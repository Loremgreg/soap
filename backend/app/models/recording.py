"""Recording model for storing transcription metadata."""

import uuid

from sqlalchemy import ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Recording(Base, TimestampMixin):
    """
    Recording model for storing transcription metadata.

    IMPORTANT: Audio data is NEVER persisted (RGPD compliance).
    Only the transcript and metadata are stored.

    Attributes:
        id: Internal UUID primary key
        user_id: Foreign key to the user who created the recording
        duration_seconds: Duration of the recording in seconds
        language_detected: Detected language code (e.g., 'fr', 'de', 'en')
        transcript_text: Full transcript text (can be null if transcription fails)
        status: Current processing status
        created_at: Timestamp when the recording was created
        updated_at: Timestamp when the recording was last updated
    """

    __tablename__ = "recordings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    duration_seconds: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    language_detected: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
    )
    transcript_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="processing",
    )

    # Relationship to user
    user: Mapped["User"] = relationship(
        "User",
        back_populates="recordings",
        lazy="selectin",
    )

    # Indexes for common queries
    __table_args__ = (
        Index("idx_recordings_user_id", "user_id"),
        Index("idx_recordings_created_at", "created_at"),
        Index("idx_recordings_status", "status"),
    )

    def __repr__(self) -> str:
        """Return string representation of Recording."""
        return f"<Recording(id={self.id}, user_id={self.user_id}, status={self.status})>"


# Import for type hints - avoid circular import
from app.models.user import User  # noqa: E402, F401
