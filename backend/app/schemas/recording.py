"""Pydantic schemas for audio recording endpoints."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class RecordingStatus(str, Enum):
    """Status of a recording in the processing pipeline."""

    UPLOADED = "uploaded"
    PROCESSING = "processing"
    TRANSCRIBING = "transcribing"
    COMPLETED = "completed"
    FAILED = "failed"


class TranscriptionStatus(str, Enum):
    """
    Status of the transcription process.

    Used to track transcription-specific states.
    """

    PENDING = "pending"
    TRANSCRIBING = "transcribing"
    COMPLETED = "completed"
    FAILED = "failed"


class RecordingCreate(BaseModel):
    """
    Request body for creating a new recording.

    The audio file is sent as multipart form-data, not in the JSON body.
    This schema is used to validate the additional metadata.

    Attributes:
        duration: Duration of the recording in seconds
        language_detected: Optional detected language code (for Story 2.3)
    """

    duration: int = Field(
        ...,
        ge=1,
        le=3600,
        description="Duration of the recording in seconds (max 60 min)",
    )
    language_detected: Optional[str] = Field(
        None,
        max_length=10,
        description="Detected language code (e.g., 'fr', 'de', 'en')",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "duration": 300,
                "language_detected": "fr",
            }
        }
    )


class RecordingResponse(BaseModel):
    """
    Response body for a created recording.

    Attributes:
        id: Unique identifier for the recording
        status: Current processing status
        created_at: Timestamp when the recording was created
    """

    id: str = Field(..., description="Unique recording identifier")
    status: RecordingStatus = Field(..., description="Current processing status")
    created_at: datetime = Field(
        ..., alias="createdAt", description="Creation timestamp"
    )

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "id": "rec_abc123",
                "status": "processing",
                "createdAt": "2026-01-27T10:30:00Z",
            }
        },
    )


class RecordingWithTranscript(BaseModel):
    """
    Recording response with full transcript (after transcription completes).

    Used when the full recording details are needed, including transcript.

    Attributes:
        id: Unique identifier for the recording
        status: Current processing status
        duration_seconds: Duration of the recording in seconds
        language_detected: Detected language code (e.g., 'fr', 'de', 'en')
        transcript_text: Full transcript text (null if transcription failed or pending)
        created_at: Timestamp when the recording was created
    """

    id: str = Field(..., description="Unique recording identifier")
    status: RecordingStatus = Field(..., description="Current processing status")
    duration_seconds: int = Field(..., alias="durationSeconds", ge=1)
    language_detected: Optional[str] = Field(
        None,
        alias="languageDetected",
        max_length=10,
        description="Detected language code",
    )
    transcript_text: Optional[str] = Field(
        None,
        alias="transcriptText",
        description="Full transcript text",
    )
    created_at: datetime = Field(
        ..., alias="createdAt", description="Creation timestamp"
    )

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "id": "rec_abc123",
                "status": "completed",
                "durationSeconds": 180,
                "languageDetected": "fr",
                "transcriptText": "Le patient présente des douleurs lombaires depuis deux semaines...",
                "createdAt": "2026-01-27T10:30:00Z",
            }
        },
    )


class AudioTooLongError(BaseModel):
    """
    Error response for audio that exceeds duration limit.

    Attributes:
        code: Error code
        message: Human-readable error message
        details: Additional details about the error
    """

    code: str = "AUDIO_TOO_LONG"
    message: str = "La durée d'enregistrement dépasse la limite"
    details: dict = Field(
        default_factory=dict,
        description="Contains 'duration' and 'maxDuration' fields",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": "AUDIO_TOO_LONG",
                "message": "La durée d'enregistrement dépasse la limite",
                "details": {"duration": 720, "maxDuration": 600},
            }
        }
    )


class TranscriptionFailedError(BaseModel):
    """
    Error response when transcription fails.

    Attributes:
        code: Error code
        message: Human-readable error message
        details: Additional details about the failure
    """

    code: str = "TRANSCRIPTION_FAILED"
    message: str = "La transcription a échoué"
    details: dict = Field(
        default_factory=dict,
        description="Contains 'reason' field with failure details",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": "TRANSCRIPTION_FAILED",
                "message": "La transcription a échoué",
                "details": {"reason": "Deepgram service unavailable"},
            }
        }
    )
