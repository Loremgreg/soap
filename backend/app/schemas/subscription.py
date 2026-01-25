"""Pydantic schemas for Subscription model."""

from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, computed_field

from app.schemas.plan import PlanSummary


class SubscriptionStatus(str, Enum):
    """
    Enum for subscription status values.

    Attributes:
        TRIAL: User is in trial period
        ACTIVE: User has active paid subscription
        CANCELLED: User cancelled subscription
        EXPIRED: Trial or subscription has expired
    """

    TRIAL = "trial"
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class SubscriptionCreate(BaseModel):
    """
    Schema for creating a new trial subscription.

    Attributes:
        plan_id: UUID of the selected plan
    """

    plan_id: UUID = Field(..., alias="planId")

    model_config = ConfigDict(
        populate_by_name=True,
    )


class SubscriptionResponse(BaseModel):
    """
    Schema for subscription response in API.

    Uses camelCase for JSON serialization per project conventions.
    Includes computed fields for trial status checking.

    Attributes:
        id: Subscription's UUID
        user_id: User's UUID
        plan_id: Plan's UUID
        plan: Plan summary information
        status: Current subscription status
        quota_remaining: Visits remaining
        quota_total: Total visits for period
        trial_ends_at: When trial ends (if applicable)
        current_period_start: Start of billing period
        current_period_end: End of billing period
        is_trial_expired: Computed field - whether trial has expired
        can_record: Computed field - whether user can record
    """

    id: UUID
    user_id: UUID = Field(..., alias="userId")
    plan_id: UUID = Field(..., alias="planId")
    plan: PlanSummary | None = None
    status: SubscriptionStatus
    quota_remaining: int = Field(..., alias="quotaRemaining")
    quota_total: int = Field(..., alias="quotaTotal")
    trial_ends_at: datetime | None = Field(None, alias="trialEndsAt")
    current_period_start: datetime | None = Field(None, alias="currentPeriodStart")
    current_period_end: datetime | None = Field(None, alias="currentPeriodEnd")
    stripe_customer_id: str | None = Field(None, alias="stripeCustomerId")
    stripe_subscription_id: str | None = Field(None, alias="stripeSubscriptionId")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")

    # These will be set by the service layer
    _is_trial_expired: bool = False
    _can_record: bool = True

    @computed_field
    @property
    def is_trial_expired(self) -> bool:
        """Check if trial has expired based on current time."""
        if self.status != SubscriptionStatus.TRIAL:
            return False
        if self.trial_ends_at is None:
            return False
        return datetime.now(self.trial_ends_at.tzinfo) > self.trial_ends_at

    @computed_field
    @property
    def can_record(self) -> bool:
        """Check if user can record based on status and quota."""
        if self.status == SubscriptionStatus.EXPIRED:
            return False
        if self.status == SubscriptionStatus.TRIAL and self.is_trial_expired:
            return False
        if self.quota_remaining <= 0:
            return False
        return True

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "userId": "660e8400-e29b-41d4-a716-446655440000",
                "planId": "770e8400-e29b-41d4-a716-446655440000",
                "plan": {
                    "name": "starter",
                    "displayName": "Starter",
                    "quotaMonthly": 20,
                },
                "status": "trial",
                "quotaRemaining": 5,
                "quotaTotal": 5,
                "trialEndsAt": "2026-02-01T14:30:00Z",
                "currentPeriodStart": "2026-01-25T14:30:00Z",
                "currentPeriodEnd": "2026-02-01T14:30:00Z",
                "stripeCustomerId": None,
                "stripeSubscriptionId": None,
                "createdAt": "2026-01-25T14:30:00Z",
                "updatedAt": "2026-01-25T14:30:00Z",
                "isTrialExpired": False,
                "canRecord": True,
            }
        },
    )


class SubscriptionStatusResponse(BaseModel):
    """
    Minimal subscription status for auth/me endpoint.

    Attributes:
        has_subscription: Whether user has any subscription
        status: Current subscription status (if exists)
        can_record: Whether user can record
        quota_remaining: Visits remaining
        quota_total: Total visits for period
    """

    has_subscription: bool = Field(..., alias="hasSubscription")
    status: SubscriptionStatus | None = None
    can_record: bool = Field(False, alias="canRecord")
    quota_remaining: int | None = Field(None, alias="quotaRemaining")
    quota_total: int | None = Field(None, alias="quotaTotal")
    trial_ends_at: datetime | None = Field(None, alias="trialEndsAt")

    model_config = ConfigDict(
        populate_by_name=True,
    )
