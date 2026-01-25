"""Subscription model for user subscription management."""

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class SubscriptionStatus(str, Enum):
    """
    Enum for subscription status values.

    Attributes:
        TRIAL: User is in trial period
        ACTIVE: User has active paid subscription
        CANCELLED: User cancelled subscription (still active until period end)
        EXPIRED: Trial or subscription has expired
    """

    TRIAL = "trial"
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class Subscription(Base, TimestampMixin):
    """
    Subscription model representing user subscriptions.

    Each user can have only one subscription at a time.
    Subscriptions track the user's plan, quota, and billing status.

    Attributes:
        id: Internal UUID primary key
        user_id: Foreign key to users table
        plan_id: Foreign key to plans table
        status: Current subscription status (trial, active, cancelled, expired)
        quota_remaining: Number of visits remaining in current period
        quota_total: Total visits allocated for current period
        trial_ends_at: When the trial period ends (if in trial)
        current_period_start: Start of current billing period
        current_period_end: End of current billing period
        stripe_customer_id: Stripe customer ID (nullable until payment)
        stripe_subscription_id: Stripe subscription ID (nullable until payment)
        created_at: Timestamp when the subscription was created
        updated_at: Timestamp when the subscription was last updated
    """

    __tablename__ = "subscriptions"

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
    plan_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("plans.id"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=SubscriptionStatus.TRIAL.value,
    )
    quota_remaining: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    quota_total: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    trial_ends_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    current_period_start: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    current_period_end: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    stripe_customer_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    stripe_subscription_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        back_populates="subscription",
        lazy="selectin",
    )
    plan: Mapped["Plan"] = relationship(
        "Plan",
        back_populates="subscriptions",
        lazy="selectin",
    )

    __table_args__ = (
        UniqueConstraint("user_id", name="unique_user_subscription"),
        Index("idx_subscriptions_user_id", "user_id"),
        Index("idx_subscriptions_status", "status"),
        Index(
            "idx_subscriptions_trial_ends_at",
            "trial_ends_at",
            postgresql_where=text("status = 'trial'"),
        ),
    )

    def __repr__(self) -> str:
        """Return string representation of Subscription."""
        return f"<Subscription(id={self.id}, user_id={self.user_id}, status={self.status})>"


# Import for type hints - avoid circular import
from app.models.plan import Plan  # noqa: E402, F401
from app.models.user import User  # noqa: E402, F401
