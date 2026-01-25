"""Subscription service for managing user subscriptions."""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.plan import Plan
from app.models.subscription import Subscription, SubscriptionStatus


# Trial configuration
TRIAL_DURATION_DAYS = 7
TRIAL_QUOTA = 5


async def get_user_subscription(
    db: AsyncSession, user_id: UUID
) -> Subscription | None:
    """
    Get a user's current subscription.

    Args:
        db: Database session
        user_id: User's UUID

    Returns:
        Subscription if exists, None otherwise
    """
    result = await db.execute(
        select(Subscription).where(Subscription.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def create_trial_subscription(
    db: AsyncSession, user_id: UUID, plan_id: UUID
) -> Subscription:
    """
    Create a trial subscription for a new user.

    Args:
        db: Database session
        user_id: User's UUID
        plan_id: Selected plan's UUID

    Returns:
        Created Subscription object

    Raises:
        HTTPException: 400 if user already has subscription
        HTTPException: 404 if plan not found or inactive
    """
    # Check if user already has subscription
    existing = await get_user_subscription(db, user_id)
    if existing:
        raise HTTPException(
            status_code=400,
            detail={
                "error": {
                    "code": "SUBSCRIPTION_EXISTS",
                    "message": "User already has a subscription",
                }
            },
        )

    # Get plan details
    plan = await db.get(Plan, plan_id)
    if not plan or not plan.is_active:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "PLAN_NOT_FOUND",
                    "message": "Plan not found or not active",
                }
            },
        )

    now = datetime.now(timezone.utc)
    trial_ends_at = now + timedelta(days=TRIAL_DURATION_DAYS)

    subscription = Subscription(
        user_id=user_id,
        plan_id=plan_id,
        status=SubscriptionStatus.TRIAL.value,
        quota_remaining=TRIAL_QUOTA,
        quota_total=TRIAL_QUOTA,
        trial_ends_at=trial_ends_at,
        current_period_start=now,
        current_period_end=trial_ends_at,
    )

    db.add(subscription)
    await db.commit()
    await db.refresh(subscription)

    return subscription


def is_trial_expired(subscription: Subscription) -> bool:
    """
    Check if a trial subscription has expired.

    Args:
        subscription: Subscription to check

    Returns:
        True if trial is expired, False otherwise
    """
    if subscription.status != SubscriptionStatus.TRIAL.value:
        return False
    if subscription.trial_ends_at is None:
        return False
    return datetime.now(timezone.utc) > subscription.trial_ends_at


async def check_subscription_valid(db: AsyncSession, user_id: UUID) -> bool:
    """
    Check if a user has a valid subscription that allows recording.

    Args:
        db: Database session
        user_id: User's UUID

    Returns:
        True if user can record, False otherwise
    """
    subscription = await get_user_subscription(db, user_id)

    if not subscription:
        return False

    # Check status
    if subscription.status == SubscriptionStatus.EXPIRED.value:
        return False

    # Check trial expiration
    if subscription.status == SubscriptionStatus.TRIAL.value:
        if is_trial_expired(subscription):
            return False

    # Check quota
    if subscription.quota_remaining <= 0:
        return False

    return True


async def decrement_quota(db: AsyncSession, user_id: UUID) -> Subscription:
    """
    Decrement a user's remaining quota by 1.

    Args:
        db: Database session
        user_id: User's UUID

    Returns:
        Updated Subscription

    Raises:
        HTTPException: 403 if no quota remaining
        HTTPException: 404 if no subscription
    """
    subscription = await get_user_subscription(db, user_id)

    if not subscription:
        raise HTTPException(
            status_code=403,
            detail={
                "error": {
                    "code": "SUBSCRIPTION_REQUIRED",
                    "message": "Subscription required to access this feature",
                }
            },
        )

    if subscription.quota_remaining <= 0:
        raise HTTPException(
            status_code=403,
            detail={
                "error": {
                    "code": "QUOTA_EXCEEDED",
                    "message": "Monthly quota exceeded",
                    "details": {
                        "used": subscription.quota_total,
                        "limit": subscription.quota_total,
                    },
                }
            },
        )

    subscription.quota_remaining -= 1
    await db.commit()
    await db.refresh(subscription)

    return subscription


async def expire_trial_if_needed(
    db: AsyncSession, subscription: Subscription
) -> Subscription:
    """
    Mark a trial as expired if the trial period has ended.

    Args:
        db: Database session
        subscription: Subscription to check

    Returns:
        Updated Subscription (or unchanged if not expired)
    """
    if subscription.status != SubscriptionStatus.TRIAL.value:
        return subscription

    if not is_trial_expired(subscription):
        return subscription

    subscription.status = SubscriptionStatus.EXPIRED.value
    await db.commit()
    await db.refresh(subscription)

    return subscription
