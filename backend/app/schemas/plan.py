"""Pydantic schemas for Plan model."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PlanBase(BaseModel):
    """
    Base schema with common Plan fields.

    Attributes:
        name: Unique plan identifier (e.g., 'starter', 'pro')
        display_name: User-facing plan name
        price_monthly: Monthly price in cents
        quota_monthly: Number of visits allowed per month
        max_recording_minutes: Maximum recording duration in minutes
        max_notes_retention: Maximum number of notes to retain
    """

    name: str
    display_name: str = Field(..., alias="displayName")
    price_monthly: int = Field(..., alias="priceMonthly")
    quota_monthly: int = Field(..., alias="quotaMonthly")
    max_recording_minutes: int = Field(10, alias="maxRecordingMinutes")
    max_notes_retention: int = Field(10, alias="maxNotesRetention")

    model_config = ConfigDict(
        populate_by_name=True,
    )


class PlanResponse(PlanBase):
    """
    Schema for plan response in API.

    Uses camelCase for JSON serialization per project conventions.

    Attributes:
        id: Plan's UUID
        name: Unique plan identifier
        display_name: User-facing plan name
        price_monthly: Monthly price in cents
        quota_monthly: Number of visits allowed per month
        max_recording_minutes: Maximum recording duration in minutes
        max_notes_retention: Maximum number of notes to retain
        is_active: Whether the plan is currently available
    """

    id: UUID
    is_active: bool = Field(..., alias="isActive")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "starter",
                "displayName": "Starter",
                "priceMonthly": 2900,
                "quotaMonthly": 20,
                "maxRecordingMinutes": 10,
                "maxNotesRetention": 10,
                "isActive": True,
            }
        },
    )


class PlanSummary(BaseModel):
    """
    Minimal plan information for embedding in subscription responses.

    Attributes:
        name: Unique plan identifier
        display_name: User-facing plan name
        quota_monthly: Number of visits allowed per month
    """

    name: str
    display_name: str = Field(..., alias="displayName")
    quota_monthly: int = Field(..., alias="quotaMonthly")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )


class PlanList(BaseModel):
    """
    Schema for list of plans response.

    Attributes:
        plans: List of plan responses
    """

    plans: list[PlanResponse]
