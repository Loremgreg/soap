"""End-to-end tests for the SOAP note extraction flow.

Tests cover:
- AC1: Full transcript → SOAP note extraction
- AC2: Template-based structured output (4 sections)
- AC3: Performance < 30s (mock validation)
- AC5: Multilingual: FR/DE/EN transcripts → user language output
- AC7: Error handling: timeout, API failure, retry
"""

import json
import time
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.recording import Recording
from app.models.user import User
from app.schemas.note import NoteCreate, NoteResponse
from app.services.llm.base import SOAPNoteOutput
from app.services.soap_extraction import SOAPExtractionError, extract_soap_note


# ─── Test Data ────────────────────────────────────────────────────────────────

FRENCH_TRANSCRIPT = (
    "Bonjour, je suis venu parce que j'ai mal au genou droit depuis trois jours. "
    "La douleur est apparue après un match de tennis. C'est une douleur vive, "
    "environ 7 sur 10 quand je monte les escaliers. Au repos c'est plutôt 3 sur 10. "
    "J'ai essayé la glace mais ça ne soulage que temporairement."
)

GERMAN_TRANSCRIPT = (
    "Guten Tag, ich bin hier weil ich seit drei Tagen Schmerzen im rechten Knie habe. "
    "Der Schmerz ist nach einem Tennismatch aufgetreten."
)

ENGLISH_TRANSCRIPT = (
    "Hello, I came because I've had right knee pain for three days. "
    "The pain started after a tennis match."
)

MOCK_SOAP_FR = SOAPNoteOutput(
    subjective="Le patient rapporte une douleur au genou droit depuis 3 jours, apparue après un match de tennis. Intensité 7/10 en montant les escaliers, 3/10 au repos.",
    objective="Non documenté - examen physique requis",
    assessment="Probable syndrome fémoro-patellaire post-effort sportif",
    plan="Application de glace 3x/jour, repos relatif, réévaluation dans 48h",
)

MOCK_SOAP_DE = SOAPNoteOutput(
    subjective="Patient berichtet über Schmerzen im rechten Knie seit 3 Tagen nach einem Tennismatch",
    objective="Nicht dokumentiert",
    assessment="Verdacht auf Patellofemorales Schmerzsyndrom",
    plan="Eis 3x/Tag, relative Ruhe",
)


# ─── AC1: Full Flow Tests ────────────────────────────────────────────────────


class TestFullExtractionFlow:
    """AC1: Complete transcript → SOAP note extraction."""

    @pytest.mark.asyncio
    @patch("app.services.soap_extraction.get_llm_client")
    @patch("app.services.soap_extraction.load_soap_template")
    async def test_french_transcript_to_soap_note(
        self, mock_load_template, mock_get_client
    ):
        """Full flow: French transcript produces 4-section SOAP note."""
        mock_load_template.return_value = "## Template SOAP"
        mock_client = MagicMock()
        mock_client.extract_soap_note = AsyncMock(return_value=MOCK_SOAP_FR)
        mock_get_client.return_value = mock_client

        result = await extract_soap_note(
            transcript=FRENCH_TRANSCRIPT,
            user_language="fr",
        )

        assert result.subjective
        assert result.objective
        assert result.assessment
        assert result.plan
        assert "genou" in result.subjective.lower()


# ─── AC2: Template Structured Output Tests ────────────────────────────────────


class TestTemplateStructuredOutput:
    """AC2: Output follows 4-section SOAP format."""

    @pytest.mark.asyncio
    @patch("app.services.soap_extraction.get_llm_client")
    @patch("app.services.soap_extraction.load_soap_template")
    async def test_output_has_four_sections(
        self, mock_load_template, mock_get_client
    ):
        """SOAP note must have exactly 4 non-empty sections."""
        mock_load_template.return_value = "## Template"
        mock_client = MagicMock()
        mock_client.extract_soap_note = AsyncMock(return_value=MOCK_SOAP_FR)
        mock_get_client.return_value = mock_client

        result = await extract_soap_note(
            transcript=FRENCH_TRANSCRIPT,
            user_language="fr",
        )

        # All 4 SOAP sections must be present and non-empty
        assert len(result.subjective.strip()) > 0
        assert len(result.objective.strip()) > 0
        assert len(result.assessment.strip()) > 0
        assert len(result.plan.strip()) > 0


# ─── AC3: Performance Tests ──────────────────────────────────────────────────


class TestPerformance:
    """AC3: Performance < 30 seconds validation."""

    @pytest.mark.asyncio
    @patch("app.services.soap_extraction.get_llm_client")
    @patch("app.services.soap_extraction.load_soap_template")
    async def test_extraction_completes_within_timeout(
        self, mock_load_template, mock_get_client
    ):
        """Extraction should complete well within 30s (with mock)."""
        mock_load_template.return_value = "## Template"
        mock_client = MagicMock()
        mock_client.extract_soap_note = AsyncMock(return_value=MOCK_SOAP_FR)
        mock_get_client.return_value = mock_client

        start = time.perf_counter()
        result = await extract_soap_note(
            transcript=FRENCH_TRANSCRIPT,
            user_language="fr",
        )
        elapsed = time.perf_counter() - start

        assert result is not None
        # With mocks, should be near-instant
        assert elapsed < 1.0


# ─── AC5: Multilingual Tests ─────────────────────────────────────────────────


class TestMultilingual:
    """AC5: Multilingual support - output in user's language."""

    @pytest.mark.asyncio
    @patch("app.services.soap_extraction.get_llm_client")
    @patch("app.services.soap_extraction.load_soap_template")
    async def test_french_transcript_french_output(
        self, mock_load_template, mock_get_client
    ):
        """French transcript → French output."""
        mock_load_template.return_value = "## Template"
        mock_client = MagicMock()
        mock_client.extract_soap_note = AsyncMock(return_value=MOCK_SOAP_FR)
        mock_get_client.return_value = mock_client

        result = await extract_soap_note(
            transcript=FRENCH_TRANSCRIPT,
            user_language="fr",
        )

        # Verify LLM was called with French language
        call_args = mock_client.extract_soap_note.call_args
        assert call_args[0][2] == "fr"
        assert result.subjective is not None

    @pytest.mark.asyncio
    @patch("app.services.soap_extraction.get_llm_client")
    @patch("app.services.soap_extraction.load_soap_template")
    async def test_german_transcript_german_output(
        self, mock_load_template, mock_get_client
    ):
        """German transcript → German output."""
        mock_load_template.return_value = "## Template"
        mock_client = MagicMock()
        mock_client.extract_soap_note = AsyncMock(return_value=MOCK_SOAP_DE)
        mock_get_client.return_value = mock_client

        result = await extract_soap_note(
            transcript=GERMAN_TRANSCRIPT,
            user_language="de",
        )

        call_args = mock_client.extract_soap_note.call_args
        assert call_args[0][2] == "de"
        assert result.subjective is not None

    @pytest.mark.asyncio
    @patch("app.services.soap_extraction.get_llm_client")
    @patch("app.services.soap_extraction.load_soap_template")
    async def test_english_transcript_french_output(
        self, mock_load_template, mock_get_client
    ):
        """English transcript → French output (cross-language translation)."""
        mock_load_template.return_value = "## Template"
        mock_client = MagicMock()
        mock_client.extract_soap_note = AsyncMock(return_value=MOCK_SOAP_FR)
        mock_get_client.return_value = mock_client

        result = await extract_soap_note(
            transcript=ENGLISH_TRANSCRIPT,
            user_language="fr",
        )

        # LLM should receive "fr" as target language
        call_args = mock_client.extract_soap_note.call_args
        assert call_args[0][2] == "fr"


# ─── AC7: Error Handling Tests ────────────────────────────────────────────────


class TestErrorHandling:
    """AC7: Error handling for API failures and timeouts."""

    @pytest.mark.asyncio
    @patch("app.services.soap_extraction.sentry_sdk")
    @patch("app.services.soap_extraction.get_llm_client")
    @patch("app.services.soap_extraction.load_soap_template")
    async def test_api_timeout_logged_to_sentry(
        self, mock_load_template, mock_get_client, mock_sentry
    ):
        """API timeout should be logged to Sentry."""
        mock_load_template.return_value = "## Template"
        mock_client = MagicMock()
        mock_client.extract_soap_note = AsyncMock(
            side_effect=TimeoutError("Mistral API timeout")
        )
        mock_get_client.return_value = mock_client

        with pytest.raises(SOAPExtractionError):
            await extract_soap_note(
                transcript=FRENCH_TRANSCRIPT,
                user_language="fr",
            )

        mock_sentry.capture_exception.assert_called_once()

    @pytest.mark.asyncio
    @patch("app.services.soap_extraction.sentry_sdk")
    @patch("app.services.soap_extraction.get_llm_client")
    @patch("app.services.soap_extraction.load_soap_template")
    async def test_api_failure_raises_extraction_error(
        self, mock_load_template, mock_get_client, mock_sentry
    ):
        """API failure should raise SOAPExtractionError after retries."""
        mock_load_template.return_value = "## Template"
        mock_client = MagicMock()
        mock_client.extract_soap_note = AsyncMock(
            side_effect=Exception("Connection refused")
        )
        mock_get_client.return_value = mock_client

        with pytest.raises(SOAPExtractionError, match="Failed to extract"):
            await extract_soap_note(
                transcript=FRENCH_TRANSCRIPT,
                user_language="fr",
            )

    @pytest.mark.asyncio
    @patch("app.services.soap_extraction.get_llm_client")
    @patch("app.services.soap_extraction.load_soap_template")
    async def test_transcript_preserved_on_failure(
        self, mock_load_template, mock_get_client, db_session: AsyncSession
    ):
        """Transcript should NOT be lost when extraction fails (retry possible)."""
        mock_load_template.return_value = "## Template"
        mock_client = MagicMock()
        mock_client.extract_soap_note = AsyncMock(
            side_effect=Exception("API failure")
        )
        mock_get_client.return_value = mock_client

        # Create user and recording
        user = User(
            id=uuid.uuid4(),
            google_id="google-e2e-fail",
            email="e2e-fail@example.com",
            name="Dr. Fail",
        )
        db_session.add(user)
        await db_session.flush()

        recording = Recording(
            id=uuid.uuid4(),
            user_id=user.id,
            duration_seconds=120,
            status="completed",
            transcript_text=FRENCH_TRANSCRIPT,
        )
        db_session.add(recording)
        await db_session.commit()

        # Try extraction (should fail)
        with pytest.raises(SOAPExtractionError):
            await extract_soap_note(
                transcript=recording.transcript_text,
                user_language="fr",
            )

        # Verify transcript is still intact in the recording
        await db_session.refresh(recording)
        assert recording.transcript_text == FRENCH_TRANSCRIPT
        assert recording.status == "completed"
