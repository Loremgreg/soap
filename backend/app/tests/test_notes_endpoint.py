"""Integration tests for the SOAP notes API endpoint.

Tests cover:
- POST /api/v1/soap-notes - SOAP note generation
- Authentication requirements
- Recording ownership validation
- Missing transcript handling
- Error handling for LLM failures
"""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.note import Note
from app.models.recording import Recording
from app.models.user import User
from app.services.llm.base import SOAPNoteOutput
from app.services.soap_extraction import SOAPExtractionError


MOCK_SOAP_OUTPUT = SOAPNoteOutput(
    subjective="Le patient rapporte une douleur au genou droit",
    objective="Flexion limitée à 90°, gonflement visible",
    assessment="Syndrome fémoro-patellaire aigu",
    plan="Glace 3x/jour, exercices de renforcement",
)


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user for note endpoint tests."""
    user = User(
        id=uuid.uuid4(),
        google_id="google-notes-test",
        email="notes@example.com",
        name="Dr. Notes",
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest.fixture
async def test_recording(db_session: AsyncSession, test_user: User) -> Recording:
    """Create a test recording with transcript."""
    recording = Recording(
        id=uuid.uuid4(),
        user_id=test_user.id,
        duration_seconds=180,
        status="completed",
        transcript_text="Le patient rapporte une douleur au genou droit depuis 3 jours.",
        language_detected="fr",
    )
    db_session.add(recording)
    await db_session.flush()
    return recording


@pytest.fixture
async def test_recording_no_transcript(
    db_session: AsyncSession, test_user: User
) -> Recording:
    """Create a test recording without transcript."""
    recording = Recording(
        id=uuid.uuid4(),
        user_id=test_user.id,
        duration_seconds=60,
        status="failed",
        transcript_text=None,
    )
    db_session.add(recording)
    await db_session.flush()
    return recording


class TestCreateNoteEndpoint:
    """Tests for POST /api/v1/soap-notes."""

    @pytest.mark.asyncio
    @patch("app.services.soap_extraction.get_llm_client")
    @patch("app.services.soap_extraction.load_soap_template")
    async def test_successful_note_creation(
        self,
        mock_load_template,
        mock_get_client,
        db_session: AsyncSession,
        test_user: User,
        test_recording: Recording,
    ):
        """Should create a SOAP note from a recording transcript."""
        mock_load_template.return_value = "## Template"
        mock_client = MagicMock()
        mock_client.extract_soap_note = AsyncMock(return_value=MOCK_SOAP_OUTPUT)
        mock_get_client.return_value = mock_client

        from app.routers.notes import create_note
        from app.schemas.note import NoteCreate

        request_data = NoteCreate(
            recordingId=test_recording.id,
            language="fr",
            format="paragraph",
            verbosity="medium",
        )

        # Simulate calling the endpoint directly
        result = await create_note(
            data=request_data,
            current_user=test_user,
            db=db_session,
        )

        assert result.subjective == MOCK_SOAP_OUTPUT.subjective
        assert result.objective == MOCK_SOAP_OUTPUT.objective
        assert result.assessment == MOCK_SOAP_OUTPUT.assessment
        assert result.plan == MOCK_SOAP_OUTPUT.plan
        assert result.recording_id == test_recording.id
        assert result.user_id == test_user.id

    @pytest.mark.asyncio
    async def test_recording_not_found(
        self,
        db_session: AsyncSession,
        test_user: User,
    ):
        """Should return 404 if recording doesn't exist."""
        from app.routers.notes import create_note
        from app.core.exceptions import NotFoundException
        from app.schemas.note import NoteCreate

        request_data = NoteCreate(
            recordingId=uuid.uuid4(),
            language="fr",
        )

        with pytest.raises(NotFoundException):
            await create_note(
                data=request_data,
                current_user=test_user,
                db=db_session,
            )

    @pytest.mark.asyncio
    async def test_no_transcript_available(
        self,
        db_session: AsyncSession,
        test_user: User,
        test_recording_no_transcript: Recording,
    ):
        """Should return 404 if recording has no transcript."""
        from app.routers.notes import create_note
        from app.core.exceptions import NotFoundException
        from app.schemas.note import NoteCreate

        request_data = NoteCreate(
            recordingId=test_recording_no_transcript.id,
            language="fr",
        )

        with pytest.raises(NotFoundException, match="transcription"):
            await create_note(
                data=request_data,
                current_user=test_user,
                db=db_session,
            )

    @pytest.mark.asyncio
    async def test_recording_wrong_user(
        self,
        db_session: AsyncSession,
        test_recording: Recording,
    ):
        """Should return 404 if recording belongs to another user."""
        from app.routers.notes import create_note
        from app.core.exceptions import NotFoundException
        from app.schemas.note import NoteCreate

        other_user = User(
            id=uuid.uuid4(),
            google_id="google-other-user",
            email="other@example.com",
            name="Other User",
        )
        db_session.add(other_user)
        await db_session.flush()

        request_data = NoteCreate(
            recordingId=test_recording.id,
            language="fr",
        )

        with pytest.raises(NotFoundException):
            await create_note(
                data=request_data,
                current_user=other_user,
                db=db_session,
            )

    @pytest.mark.asyncio
    @patch("app.services.soap_extraction.get_llm_client")
    @patch("app.services.soap_extraction.load_soap_template")
    async def test_llm_failure_returns_500(
        self,
        mock_load_template,
        mock_get_client,
        db_session: AsyncSession,
        test_user: User,
        test_recording: Recording,
    ):
        """Should return 500 if LLM extraction fails."""
        mock_load_template.return_value = "## Template"
        mock_client = MagicMock()
        mock_client.extract_soap_note = AsyncMock(
            side_effect=Exception("Mistral API timeout")
        )
        mock_get_client.return_value = mock_client

        from app.routers.notes import create_note, NoteGenerationFailedException
        from app.schemas.note import NoteCreate

        request_data = NoteCreate(
            recordingId=test_recording.id,
            language="fr",
        )

        with pytest.raises(NoteGenerationFailedException):
            await create_note(
                data=request_data,
                current_user=test_user,
                db=db_session,
            )
