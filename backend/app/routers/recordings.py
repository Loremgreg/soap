"""Recordings router for audio upload and processing endpoints."""

import uuid
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.exceptions import ApiException, QuotaExceededException
from app.models.user import User
from app.schemas.recording import RecordingResponse, RecordingStatus
from app.services import subscription as subscription_service

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


@router.post("", response_model=RecordingResponse, status_code=201)
async def create_recording(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    audio: Annotated[UploadFile, File(description="WebM/Opus audio file")],
    duration: Annotated[int, Form(ge=1, le=3600, description="Duration in seconds")],
    language_detected: Annotated[
        str | None, Form(max_length=10, description="Detected language code")
    ] = None,
) -> RecordingResponse:
    """
    Upload an audio recording for processing.

    Accepts a WebM/Opus audio file and validates:
    - User has remaining quota
    - Duration is within plan limits
    - Trial is not expired

    The audio will be processed asynchronously for transcription
    (Story 2.3) and SOAP note generation (Story 3.1).

    Args:
        current_user: The authenticated user
        db: Database session
        audio: The audio file (WebM/Opus format)
        duration: Duration of the recording in seconds
        language_detected: Optional detected language code

    Returns:
        Recording ID, status, and creation timestamp

    Raises:
        QuotaExceededException: If user has no remaining quota
        AudioTooLongException: If duration exceeds plan limits
        TrialExpiredException: If user's trial has expired
    """
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

    # Generate recording ID
    recording_id = f"rec_{uuid.uuid4().hex[:12]}"

    # Read audio data (but don't store permanently - RGPD compliance)
    # In Story 2.3, this will be sent to Deepgram for transcription
    audio_data = await audio.read()
    _ = len(audio_data)  # Audio size tracked for future processing

    # Decrement quota
    subscription.quota_remaining -= 1
    await db.commit()

    # TODO: Story 2.3 - Send to Deepgram for transcription
    # TODO: Story 3.1 - Send transcript to Mistral for SOAP extraction

    # For now, return a placeholder response
    # The actual processing pipeline will be implemented in later stories
    return RecordingResponse(
        id=recording_id,
        status=RecordingStatus.PROCESSING,
        created_at=datetime.now(timezone.utc),
    )
