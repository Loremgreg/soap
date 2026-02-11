"""Tests for the Note model and note schemas.

Tests cover:
- Note SQLAlchemy model creation and validation
- NoteCreate, NoteResponse, NoteUpdate Pydantic schemas
- Schema serialization with camelCase aliases
"""

import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.note import Note
from app.models.recording import Recording
from app.models.user import User
from app.schemas.note import NoteCreate, NoteResponse, NoteUpdate


# ─── Note Model Tests ─────────────────────────────────────────────────────────


class TestNoteModel:
    """Tests for the Note SQLAlchemy model."""

    @pytest.mark.asyncio
    async def test_create_note(self, db_session: AsyncSession):
        """Note can be created with all required fields."""
        # Create user
        user = User(
            id=uuid.uuid4(),
            google_id="google-test-123",
            email="test@example.com",
            name="Test User",
        )
        db_session.add(user)
        await db_session.flush()

        # Create recording
        recording = Recording(
            id=uuid.uuid4(),
            user_id=user.id,
            duration_seconds=120,
            status="completed",
            transcript_text="Patient reports knee pain",
        )
        db_session.add(recording)
        await db_session.flush()

        # Create note
        note = Note(
            id=uuid.uuid4(),
            user_id=user.id,
            recording_id=recording.id,
            subjective="Douleur genou droit depuis 3 jours",
            objective="Flexion limitée à 90°, gonflement visible",
            assessment="Syndrome fémoro-patellaire aigu",
            plan="Glace 3x/jour, exercices prescrits",
            language="fr",
            format="paragraph",
            verbosity="medium",
        )
        db_session.add(note)
        await db_session.commit()

        assert note.id is not None
        assert note.user_id == user.id
        assert note.recording_id == recording.id
        assert note.subjective == "Douleur genou droit depuis 3 jours"
        assert note.language == "fr"
        assert note.format == "paragraph"
        assert note.verbosity == "medium"

    @pytest.mark.asyncio
    async def test_note_defaults(self, db_session: AsyncSession):
        """Note should use default values for language, format, verbosity."""
        user = User(
            id=uuid.uuid4(),
            google_id="google-test-456",
            email="test2@example.com",
            name="Test User 2",
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

        note = Note(
            user_id=user.id,
            recording_id=recording.id,
            subjective="Pain",
            objective="Swelling",
            assessment="Sprain",
            plan="Rest",
        )
        db_session.add(note)
        await db_session.commit()

        assert note.language == "fr"
        assert note.format == "paragraph"
        assert note.verbosity == "medium"

    def test_note_repr(self):
        """Note __repr__ should include key fields."""
        note_id = uuid.uuid4()
        user_id = uuid.uuid4()
        note = Note(id=note_id, user_id=user_id, language="fr")
        repr_str = repr(note)
        assert str(note_id) in repr_str
        assert str(user_id) in repr_str
        assert "fr" in repr_str


# ─── Schema Tests ─────────────────────────────────────────────────────────────


class TestNoteCreate:
    """Tests for the NoteCreate schema."""

    def test_valid_create(self):
        """NoteCreate should accept valid input."""
        recording_id = uuid.uuid4()
        schema = NoteCreate(recordingId=recording_id, language="de")
        assert schema.recording_id == recording_id
        assert schema.language == "de"
        assert schema.format == "paragraph"
        assert schema.verbosity == "medium"

    def test_defaults(self):
        """NoteCreate should have sensible defaults."""
        recording_id = uuid.uuid4()
        schema = NoteCreate(recordingId=recording_id)
        assert schema.language == "fr"
        assert schema.format == "paragraph"
        assert schema.verbosity == "medium"

    def test_camel_case_alias(self):
        """NoteCreate should accept camelCase field names."""
        recording_id = uuid.uuid4()
        schema = NoteCreate.model_validate(
            {"recordingId": str(recording_id)}
        )
        assert schema.recording_id == recording_id

    def test_invalid_language_rejected(self):
        """NoteCreate should reject invalid language codes."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            NoteCreate(recordingId=uuid.uuid4(), language="klingon")

    def test_invalid_format_rejected(self):
        """NoteCreate should reject invalid format values."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            NoteCreate(recordingId=uuid.uuid4(), format="xml")

    def test_invalid_verbosity_rejected(self):
        """NoteCreate should reject invalid verbosity values."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            NoteCreate(recordingId=uuid.uuid4(), verbosity="extreme")


class TestNoteResponse:
    """Tests for the NoteResponse schema."""

    def test_from_orm(self):
        """NoteResponse should serialize from ORM model attributes."""
        now = datetime.now(timezone.utc)
        note_id = uuid.uuid4()
        user_id = uuid.uuid4()
        recording_id = uuid.uuid4()

        response = NoteResponse(
            id=note_id,
            user_id=user_id,
            recording_id=recording_id,
            subjective="Pain",
            objective="Swelling",
            assessment="Sprain",
            plan="Rest",
            language="fr",
            format="paragraph",
            verbosity="medium",
            created_at=now,
            updated_at=now,
        )

        assert response.id == note_id
        assert response.user_id == user_id
        assert response.recording_id == recording_id

    def test_camel_case_serialization(self):
        """NoteResponse should serialize to camelCase."""
        now = datetime.now(timezone.utc)
        response = NoteResponse(
            id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            recording_id=uuid.uuid4(),
            subjective="Pain",
            objective="Swelling",
            assessment="Sprain",
            plan="Rest",
            language="fr",
            format="paragraph",
            verbosity="medium",
            created_at=now,
            updated_at=now,
        )

        data = response.model_dump(by_alias=True)
        assert "userId" in data
        assert "recordingId" in data
        assert "createdAt" in data
        assert "updatedAt" in data


class TestNoteUpdate:
    """Tests for the NoteUpdate schema."""

    def test_partial_update(self):
        """NoteUpdate should allow partial field updates."""
        update = NoteUpdate(subjective="Updated pain description")
        assert update.subjective == "Updated pain description"
        assert update.objective is None
        assert update.assessment is None
        assert update.plan is None

    def test_empty_update(self):
        """NoteUpdate should allow empty update (no fields)."""
        update = NoteUpdate()
        assert update.subjective is None
        assert update.objective is None
