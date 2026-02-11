"""Notes router for SOAP note generation and management endpoints."""

import logging
from typing import Annotated

import sentry_sdk
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.exceptions import ApiException, NotFoundException
from app.models.recording import Recording
from app.models.user import User
from app.schemas.note import NoteCreate, NoteResponse
from app.services.soap_extraction import (
    SOAPExtractionError,
    create_note_from_transcript,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/soap-notes", tags=["soap-notes"])


class NoteGenerationFailedException(ApiException):
    """500 Note Generation Failed exception."""

    def __init__(self, reason: str) -> None:
        """
        Initialize note generation failed exception.

        Args:
            reason: Description of why generation failed
        """
        super().__init__(
            500,
            "INTERNAL_ERROR",
            "La génération de la note SOAP a échoué",
            {"reason": reason},
        )



@router.post("", response_model=NoteResponse, status_code=201)
async def create_note(
    data: NoteCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> NoteResponse:
    """
    Generate a SOAP note from a recording's transcript.

    Sends the transcript to the configured LLM provider for structured
    extraction into 4 SOAP sections, then persists the result.

    Args:
        data: Note creation request with recording ID and preferences
        current_user: The authenticated user
        db: Database session

    Returns:
        The created SOAP note with all sections

    Raises:
        NotFoundException: If the recording doesn't exist or doesn't belong to user
        NoteGenerationFailedException: If LLM extraction fails
    """
    # Find the recording and verify ownership
    result = await db.execute(
        select(Recording).where(
            Recording.id == data.recording_id,
            Recording.user_id == current_user.id,
        )
    )
    recording = result.scalar_one_or_none()

    if not recording:
        raise NotFoundException(
            message="Enregistrement non trouvé",
            details={"recordingId": str(data.recording_id)},
        )

    if not recording.transcript_text:
        raise NotFoundException(
            message="Aucune transcription disponible pour cet enregistrement",
            code="NOT_FOUND",
            details={"recordingId": str(data.recording_id)},
        )

    # Generate SOAP note via LLM
    try:
        note = await create_note_from_transcript(
            db=db,
            user_id=current_user.id,
            recording_id=recording.id,
            transcript=recording.transcript_text,
            user_language=data.language,
            note_format=data.format,
            verbosity=data.verbosity,
        )
    except SOAPExtractionError as e:
        logger.error(
            "SOAP note generation failed for recording %s: %s",
            data.recording_id,
            e,
        )
        sentry_sdk.capture_exception(e)
        raise NoteGenerationFailedException(reason=str(e))

    logger.info(
        "SOAP note generated: note_id=%s recording_id=%s user_id=%s",
        note.id,
        recording.id,
        current_user.id,
    )

    return NoteResponse.model_validate(note)
