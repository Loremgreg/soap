"""Pydantic schemas for SOAP note endpoints."""

from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class NoteCreate(BaseModel):
    """
    Request body for generating a new SOAP note.

    Attributes:
        recording_id: UUID of the recording to extract the note from
        language: Target language for the note output (fr/de/en)
        format: Note format preference (paragraph or bullets)
        verbosity: Note verbosity level (concise or medium)
    """

    recording_id: UUID = Field(
        ...,
        alias="recordingId",
        description="UUID of the source recording",
    )
    language: Literal["fr", "de", "en"] = Field(
        "fr",
        description="Target language code (fr, de, en)",
    )
    format: Literal["paragraph", "bullets"] = Field(
        "paragraph",
        description="Note format: paragraph or bullets",
    )
    verbosity: Literal["concise", "medium"] = Field(
        "medium",
        description="Note verbosity: concise or medium",
    )

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "recordingId": "550e8400-e29b-41d4-a716-446655440000",
                "language": "fr",
                "format": "paragraph",
                "verbosity": "medium",
            }
        },
    )


class NoteResponse(BaseModel):
    """
    Response body for a SOAP note.

    Attributes:
        id: Unique identifier for the note
        user_id: Owner user UUID
        recording_id: Source recording UUID
        subjective: Patient's reported symptoms and history
        objective: Observable findings and measurements
        assessment: Clinical reasoning and diagnosis
        plan: Treatment and follow-up plan
        language: Note output language
        format: Note format (paragraph/bullets)
        verbosity: Note verbosity (concise/medium)
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    id: UUID = Field(..., description="Note UUID")
    user_id: UUID = Field(..., alias="userId", description="Owner user UUID")
    recording_id: UUID = Field(
        ..., alias="recordingId", description="Source recording UUID"
    )
    subjective: str = Field(..., description="Subjective assessment")
    objective: str = Field(..., description="Objective assessment")
    assessment: str = Field(..., description="Clinical reasoning")
    plan: str = Field(..., description="Management plan")
    language: str = Field(..., description="Note output language")
    format: str = Field(..., description="Note format")
    verbosity: str = Field(..., description="Note verbosity level")
    created_at: datetime = Field(..., alias="createdAt", description="Creation timestamp")
    updated_at: datetime = Field(..., alias="updatedAt", description="Last update timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class NoteUpdate(BaseModel):
    """
    Request body for updating an existing SOAP note.

    All fields are optional - only provided fields will be updated.

    Attributes:
        subjective: Updated subjective assessment
        objective: Updated objective assessment
        assessment: Updated clinical reasoning
        plan: Updated management plan
    """

    subjective: Optional[str] = Field(None, description="Updated subjective assessment")
    objective: Optional[str] = Field(None, description="Updated objective assessment")
    assessment: Optional[str] = Field(None, description="Updated clinical reasoning")
    plan: Optional[str] = Field(None, description="Updated management plan")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "subjective": "Updated patient history...",
            }
        },
    )
