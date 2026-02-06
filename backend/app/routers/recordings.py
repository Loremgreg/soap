"""Recordings router for audio upload and processing endpoints."""

import logging
import time
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.exceptions import ApiException, QuotaExceededException
from app.models.recording import Recording
from app.models.user import User
from app.schemas.recording import RecordingStatus, RecordingWithTranscript
from app.services import subscription as subscription_service
from app.services.deepgram import (
    DeepgramTranscriptionError,
    transcribe_audio,
)

logger = logging.getLogger(__name__)

# Valid MIME types for audio uploads
ALLOWED_AUDIO_TYPES = {
    "audio/webm",
    "audio/ogg",
    "audio/mp4",
    "audio/mpeg",
}

router = APIRouter(prefix="/recordings", tags=["recordings"])

# Maximum recording duration in seconds (10 minutes default)
# TODO: Get from plan configuration
MAX_RECORDING_SECONDS = 600


class AudioTooLongException(ApiException):
    """413 Audio Too Long exception."""

    def __init__(
        self,
        duration: int,
        max_duration: int,
    ) -> None:
        """
        Initialize audio too long exception.

        Args:
            duration: Actual duration of the audio in seconds
            max_duration: Maximum allowed duration in seconds
        """
        super().__init__(
            413,
            "AUDIO_TOO_LONG",
            "La durée d'enregistrement dépasse la limite",
            {"duration": duration, "maxDuration": max_duration},
        )


class InvalidAudioTypeException(ApiException):
    """415 Unsupported Media Type exception."""

    def __init__(self, content_type: str | None) -> None:
        """
        Initialize invalid audio type exception.

        Args:
            content_type: The content type that was rejected
        """
        super().__init__(
            415,
            "INVALID_AUDIO_TYPE",
            "Type de fichier audio non supporté",
            {"contentType": content_type, "allowedTypes": list(ALLOWED_AUDIO_TYPES)},
        )


class TranscriptionFailedException(ApiException):
    """500 Transcription Failed exception."""

    def __init__(self, reason: str) -> None:
        """
        Initialize transcription failed exception.

        Args:
            reason: Description of why transcription failed
        """
        super().__init__(
            500,
            "TRANSCRIPTION_FAILED",
            "La transcription a échoué",
            {"reason": reason},
        )


@router.post("", response_model=RecordingWithTranscript, status_code=201)
async def create_recording(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    audio: Annotated[UploadFile, File(description="WebM/Opus audio file")],
    duration: Annotated[int, Form(ge=1, le=3600, description="Duration in seconds")],
    language_detected: Annotated[
        str | None, Form(max_length=10, description="Detected language code")
    ] = None,
) -> RecordingWithTranscript:
    """
    Upload an audio recording for transcription.

    Accepts a WebM/Opus audio file and:
    1. Validates user quota and trial status
    2. Validates audio format and duration
    3. Sends audio to Deepgram pre-recorded API for transcription
    4. Stores transcript in database (audio is NOT stored - RGPD)
    5. Decrements quota only on successful transcription
    6. Returns recording with transcript

    Args:
        current_user: The authenticated user
        db: Database session
        audio: The audio file (WebM/Opus format)
        duration: Duration of the recording in seconds
        language_detected: Optional detected language code (overridden by Deepgram)

    Returns:
        Recording with transcript, status, and metadata

    Raises:
        QuotaExceededException: If user has no remaining quota
        AudioTooLongException: If duration exceeds plan limits
        TranscriptionFailedException: If Deepgram transcription fails
    """
    start_time = time.time()

    # Get user's subscription and check quota
    subscription = await subscription_service.get_user_subscription(
        db=db,
        user_id=current_user.id,
    )

    if not subscription:
        raise QuotaExceededException(
            message="Aucun abonnement actif",
            used=0,
            limit=0,
        )

    # Check if trial expired
    subscription = await subscription_service.expire_trial_if_needed(db, subscription)

    if subscription.status == "expired":
        raise QuotaExceededException(
            message="Votre période d'essai a expiré",
            used=subscription.quota_total - subscription.quota_remaining,
            limit=subscription.quota_total,
        )

    # Check quota
    if subscription.quota_remaining <= 0:
        raise QuotaExceededException(
            message="Vous avez atteint votre quota mensuel",
            used=subscription.quota_total - subscription.quota_remaining,
            limit=subscription.quota_total,
        )

    # Check duration against plan limits
    # TODO: Get max_recording_minutes from plan
    max_duration = MAX_RECORDING_SECONDS
    if duration > max_duration:
        raise AudioTooLongException(
            duration=duration,
            max_duration=max_duration,
        )

    # Validate MIME type
    content_type = audio.content_type
    if content_type:
        # Extract base MIME type (without codecs parameter)
        base_type = content_type.split(";")[0].strip()
        if base_type not in ALLOWED_AUDIO_TYPES:
            raise InvalidAudioTypeException(content_type)
    else:
        raise InvalidAudioTypeException(None)

    # Read audio data into memory (RGPD: never persisted to disk)
    audio_data = await audio.read()

    # Create recording record with TRANSCRIBING status (before transcription)
    recording = Recording(
        user_id=current_user.id,
        duration_seconds=duration,
        language_detected=language_detected,
        status=RecordingStatus.TRANSCRIBING.value,
    )
    db.add(recording)
    await db.commit()
    await db.refresh(recording)

    # Transcribe audio with Deepgram
    try:
        result = await transcribe_audio(audio_data)

        # Success: update recording with transcript AND decrement quota atomically
        recording.transcript_text = result.transcript
        recording.language_detected = result.language_detected or language_detected
        recording.status = RecordingStatus.COMPLETED.value
        subscription.quota_remaining -= 1
        await db.commit()
        await db.refresh(recording)

        # Log latency for monitoring
        total_latency_ms = (time.time() - start_time) * 1000
        logger.info(
            "Recording processed successfully",
            extra={
                "recording_id": str(recording.id),
                "user_id": str(current_user.id),
                "duration_seconds": duration,
                "transcription_latency_ms": round(result.latency_ms, 2),
                "total_latency_ms": round(total_latency_ms, 2),
                "transcript_length": len(result.transcript),
                "language_detected": result.language_detected,
            },
        )

        # Warn if total latency exceeds target (5 seconds)
        if total_latency_ms > 5000:
            logger.warning(
                "Recording processing latency exceeded target",
                extra={
                    "recording_id": str(recording.id),
                    "total_latency_ms": round(total_latency_ms, 2),
                    "target_ms": 5000,
                },
            )

    except DeepgramTranscriptionError as e:
        # Failure: mark recording as failed, do NOT decrement quota
        recording.status = RecordingStatus.FAILED.value
        await db.commit()

        logger.error(
            "Transcription failed",
            extra={
                "recording_id": str(recording.id),
                "user_id": str(current_user.id),
                "error": str(e),
            },
        )

        raise TranscriptionFailedException(reason=str(e))

    # Return response with transcript
    # TODO: Story 3.1 - Send transcript to Mistral for SOAP extraction
    return RecordingWithTranscript(
        id=str(recording.id),
        status=RecordingStatus(recording.status),
        duration_seconds=recording.duration_seconds,
        language_detected=recording.language_detected,
        transcript_text=recording.transcript_text,
        created_at=recording.created_at,
    )
