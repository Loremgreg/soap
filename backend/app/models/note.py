"""Note model for storing SOAP notes generated from transcriptions."""

import uuid

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Note(Base, TimestampMixin):
    """
    SOAP note generated from a consultation transcription.

    Stores the 4 SOAP sections (Subjective, Objective, Assessment, Plan)
    along with metadata about language, format, and verbosity preferences.

    Attributes:
        id: Internal UUID primary key
        user_id: Foreign key to the user who owns the note
        recording_id: Foreign key to the source recording
        subjective: Patient's reported symptoms, history, complaints
        objective: Observable findings, measurements, examination results
        assessment: Clinical reasoning, diagnosis, contributing factors
        plan: Treatment provided, home program, follow-up plan
        language: Output language code (fr, de, en)
        format: Note format preference (paragraph or bullets)
        verbosity: Note verbosity level (concise or medium)
        created_at: Timestamp when the note was created
        updated_at: Timestamp when the note was last updated
    """

    __tablename__ = "soap_notes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    recording_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("recordings.id", ondelete="CASCADE"),
        nullable=False,
    )
    subjective: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    objective: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    assessment: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    plan: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    language: Mapped[str] = mapped_column(
        String(5),
        nullable=False,
        default="fr",
    )
    format: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="paragraph",
    )
    verbosity: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="medium",
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        lazy="selectin",
    )
    recording: Mapped["Recording"] = relationship(
        "Recording",
        lazy="selectin",
    )

    # Indexes for common queries
    __table_args__ = (
        Index("idx_soap_notes_user_id", "user_id"),
        Index("idx_soap_notes_recording_id", "recording_id"),
    )

    def __repr__(self) -> str:
        """Return string representation of Note."""
        return f"<Note(id={self.id}, user_id={self.user_id}, language={self.language})>"


# Import for type hints - avoid circular import
from app.models.recording import Recording  # noqa: E402, F401
from app.models.user import User  # noqa: E402, F401
