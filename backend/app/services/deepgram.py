"""Deepgram transcription service for audio-to-text conversion.

Uses the pre-recorded API since the frontend sends the complete audio
file after recording stops (not real-time streaming).
"""

import asyncio
import logging
import time
from typing import NamedTuple

import sentry_sdk
from deepgram import DeepgramClient
from deepgram.core.api_error import ApiError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_fixed,
)

from app.config import get_settings

logger = logging.getLogger(__name__)

# Singleton Deepgram client - reused across requests
_client: DeepgramClient | None = None

# Timeout for Deepgram API calls (seconds)
DEEPGRAM_TIMEOUT_SECONDS = 30


def _get_client() -> DeepgramClient:
    """
    Get or create a singleton DeepgramClient instance.

    Returns:
        DeepgramClient instance configured with API key

    Raises:
        DeepgramTranscriptionError: If API key is not configured
    """
    global _client
    if _client is None:
        settings = get_settings()
        if not settings.deepgram_api_key or not settings.deepgram_api_key.strip():
            raise DeepgramTranscriptionError(
                "Deepgram API key not configured or empty"
            )
        _client = DeepgramClient(api_key=settings.deepgram_api_key)
    return _client


class DeepgramTranscriptionError(Exception):
    """Custom exception for Deepgram transcription failures."""

    pass


class TranscriptionResult(NamedTuple):
    """
    Result of a transcription operation.

    Attributes:
        transcript: The transcribed text
        language_detected: The detected language code (e.g., 'fr', 'de', 'en')
        duration_seconds: Duration of the audio in seconds (from Deepgram)
        latency_ms: Time taken for transcription in milliseconds
    """

    transcript: str
    language_detected: str | None
    duration_seconds: float | None
    latency_ms: float


@retry(
    stop=stop_after_attempt(2),
    wait=wait_fixed(1),
    retry=retry_if_exception_type((ApiError, ConnectionError, TimeoutError)),
    reraise=True,
)
def _transcribe_with_retry(
    client: DeepgramClient,
    audio_data: bytes,
    model: str,
    language: str,
) -> object:
    """
    Internal function to transcribe audio with retry logic.

    Limited to 1 retry with 1s wait to stay within the 5s latency target.
    Only retries on transient errors (API errors, connection issues, timeouts).

    Args:
        client: Deepgram client instance
        audio_data: Raw audio bytes
        model: Deepgram model to use (e.g., 'nova-3')
        language: Language code or 'multi' for auto-detection

    Returns:
        Deepgram API response object

    Raises:
        ApiError: If Deepgram returns an API error after retries
        ConnectionError: If connection to Deepgram fails after retries
        TimeoutError: If request times out after retries
    """
    response = client.listen.v1.media.transcribe_file(
        request=audio_data,
        model=model,
        language=language if language != "multi" else None,
        detect_language=language == "multi",
        smart_format=True,
        punctuate=True,
        request_options={"timeout_in_seconds": DEEPGRAM_TIMEOUT_SECONDS},
    )
    return response


async def transcribe_audio(
    audio_data: bytes,
    language: str = "multi",
) -> TranscriptionResult:
    """
    Transcribe audio using Deepgram Nova-3 pre-recorded API.

    Sends the complete audio file to Deepgram for transcription.
    Uses the pre-recorded API since the frontend sends complete audio
    after recording stops (not real-time streaming).

    The synchronous Deepgram SDK call is offloaded to a thread pool
    via asyncio.to_thread() to avoid blocking the FastAPI event loop.

    Args:
        audio_data: Raw audio bytes (WebM/Opus format)
        language: Language code or "multi" for auto-detection (default: "multi")

    Returns:
        TranscriptionResult with transcript, detected language, and latency

    Raises:
        DeepgramTranscriptionError: If transcription fails after retries

    Example:
        >>> audio_bytes = await audio_file.read()
        >>> result = await transcribe_audio(audio_bytes)
        >>> print(result.transcript)
        "Le patient présente des douleurs lombaires..."
    """
    settings = get_settings()

    if not settings.deepgram_api_key or not settings.deepgram_api_key.strip():
        logger.error("DEEPGRAM_API_KEY not configured")
        raise DeepgramTranscriptionError("Deepgram API key not configured or empty")

    start_time = time.time()

    try:
        client = _get_client()
        model = settings.deepgram_model

        # Offload synchronous SDK call to thread pool to avoid blocking event loop
        response = await asyncio.to_thread(
            _transcribe_with_retry, client, audio_data, model, language
        )

        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000

        # Extract transcript from response
        channels = response.results.channels
        if not channels:
            raise DeepgramTranscriptionError("No channels in Deepgram response")

        alternatives = channels[0].alternatives
        if not alternatives:
            raise DeepgramTranscriptionError("No alternatives in Deepgram response")

        transcript = alternatives[0].transcript or ""

        # Extract detected language
        language_detected = getattr(channels[0], "detected_language", None)

        # Extract duration from metadata
        duration_seconds = getattr(response.metadata, "duration", None)

        # Log transcription metrics
        logger.info(
            "Transcription completed",
            extra={
                "latency_ms": round(latency_ms, 2),
                "transcript_length": len(transcript),
                "language_detected": language_detected,
                "duration_seconds": duration_seconds,
                "audio_size_bytes": len(audio_data),
            },
        )

        # Warn if latency exceeds target (5 seconds)
        if latency_ms > 5000:
            logger.warning(
                "Transcription latency exceeded target",
                extra={
                    "latency_ms": round(latency_ms, 2),
                    "target_ms": 5000,
                },
            )

        return TranscriptionResult(
            transcript=transcript,
            language_detected=language_detected,
            duration_seconds=duration_seconds,
            latency_ms=latency_ms,
        )

    except DeepgramTranscriptionError:
        # Re-raise our custom errors
        raise
    except (ApiError, ConnectionError, TimeoutError) as e:
        latency_ms = (time.time() - start_time) * 1000

        logger.error(
            "Deepgram transcription failed",
            extra={
                "error": str(e),
                "error_type": type(e).__name__,
                "latency_ms": round(latency_ms, 2),
                "audio_size_bytes": len(audio_data),
            },
            exc_info=True,
        )

        sentry_sdk.capture_exception(e)
        raise DeepgramTranscriptionError(f"Transcription failed: {str(e)}") from e
    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000

        logger.error(
            "Unexpected error during transcription",
            extra={
                "error": str(e),
                "error_type": type(e).__name__,
                "latency_ms": round(latency_ms, 2),
                "audio_size_bytes": len(audio_data),
            },
            exc_info=True,
        )

        sentry_sdk.capture_exception(e)
        raise DeepgramTranscriptionError(f"Transcription failed: {str(e)}") from e
