"""Plan model for subscription plans configuration."""

import uuid

from sqlalchemy import Boolean, Index, Integer, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Plan(Base, TimestampMixin):
    """
    Plan model representing subscription plan configurations.

    Plans are database-driven configuration, allowing pricing and limits
    to be modified without code deployment.

    Attributes:
        id: Internal UUID primary key
        name: Unique plan identifier (e.g., 'starter', 'pro')
        display_name: User-facing plan name (e.g., 'Starter', 'Pro')
        price_monthly: Monthly price in cents (2900 = 29€)
        quota_monthly: Number of visits allowed per month
        max_recording_minutes: Maximum recording duration in minutes
        max_notes_retention: Maximum number of notes to retain
        is_active: Whether the plan is currently available
        created_at: Timestamp when the plan was created
        updated_at: Timestamp when the plan was last updated
    """

    __tablename__ = "plans"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
    )
    display_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    price_monthly: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    quota_monthly: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    max_recording_minutes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=10,
    )
    max_notes_retention: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=10,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # Relationship to subscriptions (one-to-many)
    subscriptions: Mapped[list["Subscription"]] = relationship(
        "Subscription",
        back_populates="plan",
        lazy="selectin",
    )

    __table_args__ = (
        Index("idx_plans_name", "name"),
        Index("idx_plans_active", "is_active", postgresql_where=text("is_active = true")),
    )

    def __repr__(self) -> str:
        """Return string representation of Plan."""
        return f"<Plan(id={self.id}, name={self.name}, price={self.price_monthly})>"


# Import at the end to avoid circular import
from app.models.subscription import Subscription  # noqa: E402, F401
