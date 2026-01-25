"""Tests for subscription service."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.plan import Plan
from app.models.subscription import Subscription, SubscriptionStatus
from app.models.user import User
from app.services import subscription as subscription_service


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        google_id="test_google_id_123",
        email="test@example.com",
        name="Test User",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_plan(db_session: AsyncSession) -> Plan:
    """Create a test plan."""
    plan = Plan(
        name="starter",
        display_name="Starter",
        price_monthly=2900,
        quota_monthly=20,
        is_active=True,
    )
    db_session.add(plan)
    await db_session.commit()
    await db_session.refresh(plan)
    return plan


@pytest.mark.asyncio
async def test_create_trial_subscription(
    db_session: AsyncSession, test_user: User, test_plan: Plan
) -> None:
    """Test creating a trial subscription."""
    subscription = await subscription_service.create_trial_subscription(
        db=db_session,
        user_id=test_user.id,
        plan_id=test_plan.id,
    )

    assert subscription.id is not None
    assert subscription.user_id == test_user.id
    assert subscription.plan_id == test_plan.id
    assert subscription.status == SubscriptionStatus.TRIAL.value
    assert subscription.quota_remaining == 5  # Trial quota
    assert subscription.quota_total == 5
    assert subscription.trial_ends_at is not None

    # Trial should end in 7 days
    expected_end = datetime.now(timezone.utc) + timedelta(days=7)
    assert abs((subscription.trial_ends_at - expected_end).total_seconds()) < 60


@pytest.mark.asyncio
async def test_create_trial_subscription_user_already_has_subscription(
    db_session: AsyncSession, test_user: User, test_plan: Plan
) -> None:
    """Test creating trial fails if user already has subscription."""
    # Create first subscription
    await subscription_service.create_trial_subscription(
        db=db_session,
        user_id=test_user.id,
        plan_id=test_plan.id,
    )

    # Try to create second subscription
    with pytest.raises(HTTPException) as exc_info:
        await subscription_service.create_trial_subscription(
            db=db_session,
            user_id=test_user.id,
            plan_id=test_plan.id,
        )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail["error"]["code"] == "SUBSCRIPTION_EXISTS"


@pytest.mark.asyncio
async def test_create_trial_subscription_plan_not_found(
    db_session: AsyncSession, test_user: User
) -> None:
    """Test creating trial fails if plan not found."""
    fake_plan_id = uuid4()

    with pytest.raises(HTTPException) as exc_info:
        await subscription_service.create_trial_subscription(
            db=db_session,
            user_id=test_user.id,
            plan_id=fake_plan_id,
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail["error"]["code"] == "PLAN_NOT_FOUND"


@pytest.mark.asyncio
async def test_create_trial_subscription_inactive_plan(
    db_session: AsyncSession, test_user: User
) -> None:
    """Test creating trial fails if plan is inactive."""
    inactive_plan = Plan(
        name="legacy",
        display_name="Legacy",
        price_monthly=1900,
        quota_monthly=10,
        is_active=False,
    )
    db_session.add(inactive_plan)
    await db_session.commit()
    await db_session.refresh(inactive_plan)

    with pytest.raises(HTTPException) as exc_info:
        await subscription_service.create_trial_subscription(
            db=db_session,
            user_id=test_user.id,
            plan_id=inactive_plan.id,
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail["error"]["code"] == "PLAN_NOT_FOUND"


@pytest.mark.asyncio
async def test_get_user_subscription(
    db_session: AsyncSession, test_user: User, test_plan: Plan
) -> None:
    """Test getting user subscription."""
    # No subscription initially
    subscription = await subscription_service.get_user_subscription(
        db=db_session, user_id=test_user.id
    )
    assert subscription is None

    # Create subscription
    await subscription_service.create_trial_subscription(
        db=db_session,
        user_id=test_user.id,
        plan_id=test_plan.id,
    )

    # Now should find subscription
    subscription = await subscription_service.get_user_subscription(
        db=db_session, user_id=test_user.id
    )
    assert subscription is not None
    assert subscription.user_id == test_user.id


@pytest.mark.asyncio
async def test_is_trial_expired_not_expired(
    db_session: AsyncSession, test_user: User, test_plan: Plan
) -> None:
    """Test is_trial_expired returns False for active trial."""
    subscription = await subscription_service.create_trial_subscription(
        db=db_session,
        user_id=test_user.id,
        plan_id=test_plan.id,
    )

    assert subscription_service.is_trial_expired(subscription) is False


@pytest.mark.asyncio
async def test_is_trial_expired_when_expired(
    db_session: AsyncSession, test_user: User, test_plan: Plan
) -> None:
    """Test is_trial_expired returns True for expired trial."""
    subscription = Subscription(
        user_id=test_user.id,
        plan_id=test_plan.id,
        status=SubscriptionStatus.TRIAL.value,
        quota_remaining=5,
        quota_total=5,
        trial_ends_at=datetime.now(timezone.utc) - timedelta(days=1),  # Expired
        current_period_start=datetime.now(timezone.utc) - timedelta(days=8),
        current_period_end=datetime.now(timezone.utc) - timedelta(days=1),
    )
    db_session.add(subscription)
    await db_session.commit()
    await db_session.refresh(subscription)

    assert subscription_service.is_trial_expired(subscription) is True


@pytest.mark.asyncio
async def test_is_trial_expired_non_trial_status(
    db_session: AsyncSession, test_user: User, test_plan: Plan
) -> None:
    """Test is_trial_expired returns False for non-trial subscription."""
    subscription = Subscription(
        user_id=test_user.id,
        plan_id=test_plan.id,
        status=SubscriptionStatus.ACTIVE.value,
        quota_remaining=20,
        quota_total=20,
        trial_ends_at=None,
    )
    db_session.add(subscription)
    await db_session.commit()
    await db_session.refresh(subscription)

    assert subscription_service.is_trial_expired(subscription) is False


@pytest.mark.asyncio
async def test_check_subscription_valid(
    db_session: AsyncSession, test_user: User, test_plan: Plan
) -> None:
    """Test check_subscription_valid for valid trial."""
    await subscription_service.create_trial_subscription(
        db=db_session,
        user_id=test_user.id,
        plan_id=test_plan.id,
    )

    is_valid = await subscription_service.check_subscription_valid(
        db=db_session, user_id=test_user.id
    )
    assert is_valid is True


@pytest.mark.asyncio
async def test_check_subscription_valid_no_subscription(
    db_session: AsyncSession, test_user: User
) -> None:
    """Test check_subscription_valid returns False without subscription."""
    is_valid = await subscription_service.check_subscription_valid(
        db=db_session, user_id=test_user.id
    )
    assert is_valid is False


@pytest.mark.asyncio
async def test_check_subscription_valid_expired(
    db_session: AsyncSession, test_user: User, test_plan: Plan
) -> None:
    """Test check_subscription_valid returns False for expired subscription."""
    subscription = Subscription(
        user_id=test_user.id,
        plan_id=test_plan.id,
        status=SubscriptionStatus.EXPIRED.value,
        quota_remaining=0,
        quota_total=5,
    )
    db_session.add(subscription)
    await db_session.commit()

    is_valid = await subscription_service.check_subscription_valid(
        db=db_session, user_id=test_user.id
    )
    assert is_valid is False


@pytest.mark.asyncio
async def test_check_subscription_valid_no_quota(
    db_session: AsyncSession, test_user: User, test_plan: Plan
) -> None:
    """Test check_subscription_valid returns False when quota exhausted."""
    subscription = Subscription(
        user_id=test_user.id,
        plan_id=test_plan.id,
        status=SubscriptionStatus.TRIAL.value,
        quota_remaining=0,  # No quota left
        quota_total=5,
        trial_ends_at=datetime.now(timezone.utc) + timedelta(days=7),
    )
    db_session.add(subscription)
    await db_session.commit()

    is_valid = await subscription_service.check_subscription_valid(
        db=db_session, user_id=test_user.id
    )
    assert is_valid is False


@pytest.mark.asyncio
async def test_decrement_quota(
    db_session: AsyncSession, test_user: User, test_plan: Plan
) -> None:
    """Test decrement_quota reduces quota by 1."""
    await subscription_service.create_trial_subscription(
        db=db_session,
        user_id=test_user.id,
        plan_id=test_plan.id,
    )

    subscription = await subscription_service.decrement_quota(
        db=db_session, user_id=test_user.id
    )

    assert subscription.quota_remaining == 4  # 5 - 1


@pytest.mark.asyncio
async def test_decrement_quota_no_subscription(
    db_session: AsyncSession, test_user: User
) -> None:
    """Test decrement_quota fails without subscription."""
    with pytest.raises(HTTPException) as exc_info:
        await subscription_service.decrement_quota(
            db=db_session, user_id=test_user.id
        )

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail["error"]["code"] == "SUBSCRIPTION_REQUIRED"


@pytest.mark.asyncio
async def test_decrement_quota_no_remaining(
    db_session: AsyncSession, test_user: User, test_plan: Plan
) -> None:
    """Test decrement_quota fails when no quota remaining."""
    subscription = Subscription(
        user_id=test_user.id,
        plan_id=test_plan.id,
        status=SubscriptionStatus.TRIAL.value,
        quota_remaining=0,
        quota_total=5,
        trial_ends_at=datetime.now(timezone.utc) + timedelta(days=7),
    )
    db_session.add(subscription)
    await db_session.commit()

    with pytest.raises(HTTPException) as exc_info:
        await subscription_service.decrement_quota(
            db=db_session, user_id=test_user.id
        )

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail["error"]["code"] == "QUOTA_EXCEEDED"


@pytest.mark.asyncio
async def test_expire_trial_if_needed(
    db_session: AsyncSession, test_user: User, test_plan: Plan
) -> None:
    """Test expire_trial_if_needed marks expired trial as expired."""
    subscription = Subscription(
        user_id=test_user.id,
        plan_id=test_plan.id,
        status=SubscriptionStatus.TRIAL.value,
        quota_remaining=5,
        quota_total=5,
        trial_ends_at=datetime.now(timezone.utc) - timedelta(days=1),  # Expired
    )
    db_session.add(subscription)
    await db_session.commit()
    await db_session.refresh(subscription)

    updated = await subscription_service.expire_trial_if_needed(db_session, subscription)

    assert updated.status == SubscriptionStatus.EXPIRED.value
