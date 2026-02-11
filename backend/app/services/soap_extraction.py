"""SOAP note extraction orchestration service.

Orchestrates the process of extracting a structured SOAP note from a
consultation transcript, including LLM interaction, timing, and persistence.
"""

import logging
import time
import uuid
from pathlib import Path

import sentry_sdk
from sqlalchemy.ext.asyncio import AsyncSession
from tenacity import retry, stop_after_attempt, wait_exponential

from app.models.note import Note
from app.services.llm.base import BaseLLMClient, SOAPNoteOutput
from app.services.llm.factory import get_llm_client
from app.services.llm.prompts.soap_extraction import load_soap_template

logger = logging.getLogger(__name__)

# Project root for template loading
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent


class SOAPExtractionError(Exception):
    """Raised when SOAP extraction fails after retries."""

    pass


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True,
)
async def _extract_with_retry(
    client: "BaseLLMClient", transcript: str, template: str, language: str
) -> SOAPNoteOutput:
    """Extract SOAP note with automatic retry on failure.

    Args:
        client: LLM client instance (reused across retries)
        transcript: Consultation transcript text
        template: SOAP template content
        language: Output language code (fr/de/en)

    Returns:
        SOAPNoteOutput with the 4 SOAP sections

    Raises:
        Exception: Re-raised after 3 failed attempts
    """
    return await client.extract_soap_note(transcript, template, language)


async def extract_soap_note(
    transcript: str,
    user_language: str,
    template: str | None = None,
) -> SOAPNoteOutput:
    """Extract a structured SOAP note from a consultation transcript.

    Handles template loading, LLM invocation with retry logic,
    performance timing, and error handling with Sentry logging.

    Args:
        transcript: Transcribed text from the consultation
        user_language: User's app language setting (fr/de/en)
        template: Optional pre-loaded template content

    Returns:
        SOAPNoteOutput with the 4 SOAP sections

    Raises:
        SOAPExtractionError: If extraction fails after all retries
    """
    # Load template if not provided
    if template is None:
        template = load_soap_template(PROJECT_ROOT)

    # Create client once, reused across retries
    client = get_llm_client()

    # Measure latency for NFR11 monitoring
    start_time = time.perf_counter()

    try:
        result = await _extract_with_retry(client, transcript, template, user_language)
    except Exception as e:
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        logger.error(
            "SOAP extraction failed after retries: %s (%.0fms)", e, elapsed_ms
        )
        sentry_sdk.capture_exception(e)
        raise SOAPExtractionError(
            f"Failed to extract SOAP note: {e}"
        ) from e

    elapsed_ms = (time.perf_counter() - start_time) * 1000
    logger.info("SOAP extraction completed in %.0fms", elapsed_ms)

    if elapsed_ms > 25000:
        logger.warning(
            "SOAP extraction latency %.0fms exceeds 25s threshold (NFR11)",
            elapsed_ms,
        )

    return result


async def create_note_from_transcript(
    db: AsyncSession,
    user_id: uuid.UUID,
    recording_id: uuid.UUID,
    transcript: str,
    user_language: str = "fr",
    note_format: str = "paragraph",
    verbosity: str = "medium",
) -> Note:
    """Extract SOAP note and persist to database.

    Full orchestration: extract SOAP sections via LLM, create Note
    model instance, and save to database.

    Args:
        db: Async database session
        user_id: UUID of the note owner
        recording_id: UUID of the source recording
        transcript: Transcribed consultation text
        user_language: Target output language (fr/de/en)
        note_format: Note format preference (paragraph/bullets)
        verbosity: Note verbosity level (concise/medium)

    Returns:
        Created Note model instance with database-generated timestamps

    Raises:
        SOAPExtractionError: If LLM extraction fails
    """
    soap_output = await extract_soap_note(transcript, user_language)

    note = Note(
        user_id=user_id,
        recording_id=recording_id,
        subjective=soap_output.subjective,
        objective=soap_output.objective,
        assessment=soap_output.assessment,
        plan=soap_output.plan,
        language=user_language,
        format=note_format,
        verbosity=verbosity,
    )

    db.add(note)
    await db.commit()
    await db.refresh(note)

    logger.info(
        "Created note %s for user %s from recording %s",
        note.id,
        user_id,
        recording_id,
    )

    return note
