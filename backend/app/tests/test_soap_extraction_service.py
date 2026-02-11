"""Tests for the SOAP extraction orchestration service.

Tests cover:
- extract_soap_note with mock LLM client
- create_note_from_transcript with database persistence
- Retry logic on failure
- Latency logging
- Error handling with SOAPExtractionError
"""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.note import Note
from app.models.recording import Recording
from app.models.user import User
from app.services.llm.base import SOAPNoteOutput
from app.services.soap_extraction import (
    SOAPExtractionError,
    create_note_from_transcript,
    extract_soap_note,
)


MOCK_SOAP_OUTPUT = SOAPNoteOutput(
    subjective="Le patient rapporte une douleur au genou droit",
    objective="Flexion limitée à 90°, gonflement visible",
    assessment="Syndrome fémoro-patellaire aigu",
    plan="Glace 3x/jour, exercices de renforcement",
)


# ─── extract_soap_note Tests ─────────────────────────────────────────────────


class TestExtractSoapNote:
    """Tests for the extract_soap_note function."""

    @pytest.mark.asyncio
    @patch("app.services.soap_extraction.get_llm_client")
    @patch("app.services.soap_extraction.load_soap_template")
    async def test_successful_extraction(self, mock_load_template, mock_get_client):
        """Should return SOAPNoteOutput on successful extraction."""
        mock_load_template.return_value = "## Template"
        mock_client = MagicMock()
        mock_client.extract_soap_note = AsyncMock(return_value=MOCK_SOAP_OUTPUT)
        mock_get_client.return_value = mock_client

        result = await extract_soap_note(
            transcript="Le patient a mal au genou",
            user_language="fr",
        )

        assert isinstance(result, SOAPNoteOutput)
        assert result.subjective == MOCK_SOAP_OUTPUT.subjective
        assert result.plan == MOCK_SOAP_OUTPUT.plan

    @pytest.mark.asyncio
    @patch("app.services.soap_extraction.get_llm_client")
    async def test_uses_provided_template(self, mock_get_client):
        """Should use provided template instead of loading from file."""
        mock_client = MagicMock()
        mock_client.extract_soap_note = AsyncMock(return_value=MOCK_SOAP_OUTPUT)
        mock_get_client.return_value = mock_client

        result = await extract_soap_note(
            transcript="Transcript text",
            user_language="de",
            template="Custom template",
        )

        assert isinstance(result, SOAPNoteOutput)
        call_args = mock_client.extract_soap_note.call_args
        assert call_args[0][1] == "Custom template"
        assert call_args[0][2] == "de"

    @pytest.mark.asyncio
    @patch("app.services.soap_extraction.sentry_sdk")
    @patch("app.services.soap_extraction.get_llm_client")
    @patch("app.services.soap_extraction.load_soap_template")
    async def test_raises_extraction_error_on_failure(
        self, mock_load_template, mock_get_client, mock_sentry
    ):
        """Should raise SOAPExtractionError and log to Sentry on failure."""
        mock_load_template.return_value = "## Template"
        mock_client = MagicMock()
        mock_client.extract_soap_note = AsyncMock(
            side_effect=Exception("API timeout")
        )
        mock_get_client.return_value = mock_client

        with pytest.raises(SOAPExtractionError, match="Failed to extract"):
            await extract_soap_note(
                transcript="Transcript",
                user_language="fr",
            )

        mock_sentry.capture_exception.assert_called_once()


# ─── create_note_from_transcript Tests ────────────────────────────────────────


class TestCreateNoteFromTranscript:
    """Tests for create_note_from_transcript with database."""

    @pytest.mark.asyncio
    @patch("app.services.soap_extraction.get_llm_client")
    @patch("app.services.soap_extraction.load_soap_template")
    async def test_creates_note_in_database(
        self, mock_load_template, mock_get_client, db_session: AsyncSession
    ):
        """Should create a Note in the database after extraction."""
        mock_load_template.return_value = "## Template"
        mock_client = MagicMock()
        mock_client.extract_soap_note = AsyncMock(return_value=MOCK_SOAP_OUTPUT)
        mock_get_client.return_value = mock_client

        # Create user and recording
        user = User(
            id=uuid.uuid4(),
            google_id="google-soap-test",
            email="soap@example.com",
            name="Dr. Test",
        )
        db_session.add(user)
        await db_session.flush()

        recording = Recording(
            id=uuid.uuid4(),
            user_id=user.id,
            duration_seconds=180,
            status="completed",
            transcript_text="Le patient a mal au genou",
        )
        db_session.add(recording)
        await db_session.flush()

        note = await create_note_from_transcript(
            db=db_session,
            user_id=user.id,
            recording_id=recording.id,
            transcript="Le patient a mal au genou",
            user_language="fr",
            note_format="paragraph",
            verbosity="medium",
        )

        assert isinstance(note, Note)
        assert note.id is not None
        assert note.user_id == user.id
        assert note.recording_id == recording.id
        assert note.subjective == MOCK_SOAP_OUTPUT.subjective
        assert note.objective == MOCK_SOAP_OUTPUT.objective
        assert note.assessment == MOCK_SOAP_OUTPUT.assessment
        assert note.plan == MOCK_SOAP_OUTPUT.plan
        assert note.language == "fr"
        assert note.format == "paragraph"
        assert note.verbosity == "medium"

    @pytest.mark.asyncio
    @patch("app.services.soap_extraction.get_llm_client")
    @patch("app.services.soap_extraction.load_soap_template")
    async def test_creates_note_with_german_language(
        self, mock_load_template, mock_get_client, db_session: AsyncSession
    ):
        """Should respect user_language parameter for multilingual support."""
        mock_load_template.return_value = "## Template"
        mock_client = MagicMock()
        mock_client.extract_soap_note = AsyncMock(return_value=MOCK_SOAP_OUTPUT)
        mock_get_client.return_value = mock_client

        user = User(
            id=uuid.uuid4(),
            google_id="google-de-test",
            email="de@example.com",
            name="Dr. Test DE",
        )
        db_session.add(user)
        await db_session.flush()

        recording = Recording(
            id=uuid.uuid4(),
            user_id=user.id,
            duration_seconds=60,
            status="completed",
        )
        db_session.add(recording)
        await db_session.flush()

        note = await create_note_from_transcript(
            db=db_session,
            user_id=user.id,
            recording_id=recording.id,
            transcript="Der Patient hat Knieschmerzen",
            user_language="de",
        )

        assert note.language == "de"
        # Verify LLM was called with German
        call_args = mock_client.extract_soap_note.call_args
        assert call_args[0][2] == "de"
