"""Subscriptions router for subscription management endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.plan import PlanSummary
from app.schemas.subscription import (
    SubscriptionCreate,
    SubscriptionResponse,
    SubscriptionStatus,
)
from app.services import subscription as subscription_service

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.post("/trial", response_model=SubscriptionResponse)
async def create_trial(
    data: SubscriptionCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SubscriptionResponse:
    """
    Activate a trial subscription for the current user.

    Creates a new trial subscription with 7-day duration and 5 visits quota.
    User must be authenticated and not already have a subscription.

    Args:
        data: Subscription creation data with plan ID
        current_user: The authenticated user
        db: Database session

    Returns:
        Created subscription details

    Raises:
        HTTPException: 400 if user already has subscription
        HTTPException: 404 if plan not found or inactive
    """
    subscription = await subscription_service.create_trial_subscription(
        db=db,
        user_id=current_user.id,
        plan_id=data.plan_id,
    )

    # Load plan for response
    await db.refresh(subscription, ["plan"])

    response = SubscriptionResponse.model_validate(subscription)
    if subscription.plan:
        response.plan = PlanSummary.model_validate(subscription.plan)

    return response


@router.get("/me", response_model=SubscriptionResponse)
async def get_my_subscription(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SubscriptionResponse:
    """
    Get the current user's subscription.

    Returns the user's subscription with plan details.
    Also checks and updates trial expiration status.

    Args:
        current_user: The authenticated user
        db: Database session

    Returns:
        User's subscription details

    Raises:
        HTTPException: 404 if user has no subscription
    """
    subscription = await subscription_service.get_user_subscription(
        db=db,
        user_id=current_user.id,
    )

    if not subscription:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "SUBSCRIPTION_NOT_FOUND",
                    "message": "No subscription found for this user",
                }
            },
        )

    # Check and update trial expiration
    subscription = await subscription_service.expire_trial_if_needed(db, subscription)

    # Load plan for response
    await db.refresh(subscription, ["plan"])

    response = SubscriptionResponse.model_validate(subscription)
    if subscription.plan:
        response.plan = PlanSummary.model_validate(subscription.plan)

    return response
