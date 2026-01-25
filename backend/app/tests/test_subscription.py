"""Tests for Subscription model."""

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.plan import Plan
from app.models.subscription import Subscription, SubscriptionStatus
from app.models.user import User


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user for subscription tests."""
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
    """Create a test plan for subscription tests."""
    plan = Plan(
        name="starter",
        display_name="Starter",
        price_monthly=2900,
        quota_monthly=20,
        max_recording_minutes=10,
        max_notes_retention=10,
        is_active=True,
    )
    db_session.add(plan)
    await db_session.commit()
    await db_session.refresh(plan)
    return plan


@pytest.mark.asyncio
async def test_subscription_creation(
    db_session: AsyncSession, test_user: User, test_plan: Plan
) -> None:
    """Test creating a subscription with all required fields."""
    now = datetime.now(timezone.utc)
    trial_ends_at = now + timedelta(days=7)

    subscription = Subscription(
        user_id=test_user.id,
        plan_id=test_plan.id,
        status=SubscriptionStatus.TRIAL.value,
        quota_remaining=5,
        quota_total=5,
        trial_ends_at=trial_ends_at,
        current_period_start=now,
        current_period_end=trial_ends_at,
    )
    db_session.add(subscription)
    await db_session.commit()
    await db_session.refresh(subscription)

    assert subscription.id is not None
    assert subscription.user_id == test_user.id
    assert subscription.plan_id == test_plan.id
    assert subscription.status == SubscriptionStatus.TRIAL.value
    assert subscription.quota_remaining == 5
    assert subscription.quota_total == 5
    assert subscription.trial_ends_at is not None
    assert subscription.created_at is not None
    assert subscription.updated_at is not None


@pytest.mark.asyncio
async def test_subscription_status_enum() -> None:
    """Test SubscriptionStatus enum values."""
    assert SubscriptionStatus.TRIAL.value == "trial"
    assert SubscriptionStatus.ACTIVE.value == "active"
    assert SubscriptionStatus.CANCELLED.value == "cancelled"
    assert SubscriptionStatus.EXPIRED.value == "expired"


@pytest.mark.asyncio
async def test_subscription_unique_user_constraint(
    db_session: AsyncSession, test_user: User, test_plan: Plan
) -> None:
    """Test that each user can only have one subscription."""
    subscription1 = Subscription(
        user_id=test_user.id,
        plan_id=test_plan.id,
        status=SubscriptionStatus.TRIAL.value,
        quota_remaining=5,
        quota_total=5,
    )
    db_session.add(subscription1)
    await db_session.commit()

    subscription2 = Subscription(
        user_id=test_user.id,
        plan_id=test_plan.id,
        status=SubscriptionStatus.ACTIVE.value,
        quota_remaining=20,
        quota_total=20,
    )
    db_session.add(subscription2)

    with pytest.raises(Exception):  # IntegrityError
        await db_session.commit()


@pytest.mark.asyncio
async def test_subscription_user_relationship(
    db_session: AsyncSession, test_user: User, test_plan: Plan
) -> None:
    """Test subscription has access to user relationship."""
    subscription = Subscription(
        user_id=test_user.id,
        plan_id=test_plan.id,
        status=SubscriptionStatus.TRIAL.value,
        quota_remaining=5,
        quota_total=5,
    )
    db_session.add(subscription)
    await db_session.commit()
    await db_session.refresh(subscription)

    # Relationship should be loaded
    assert subscription.user is not None
    assert subscription.user.email == "test@example.com"


@pytest.mark.asyncio
async def test_subscription_plan_relationship(
    db_session: AsyncSession, test_user: User, test_plan: Plan
) -> None:
    """Test subscription has access to plan relationship."""
    subscription = Subscription(
        user_id=test_user.id,
        plan_id=test_plan.id,
        status=SubscriptionStatus.TRIAL.value,
        quota_remaining=5,
        quota_total=5,
    )
    db_session.add(subscription)
    await db_session.commit()
    await db_session.refresh(subscription)

    # Relationship should be loaded
    assert subscription.plan is not None
    assert subscription.plan.name == "starter"


@pytest.mark.asyncio
async def test_subscription_trial_quota(
    db_session: AsyncSession, test_user: User, test_plan: Plan
) -> None:
    """Test trial subscription uses trial quota (5), not plan quota."""
    now = datetime.now(timezone.utc)
    subscription = Subscription(
        user_id=test_user.id,
        plan_id=test_plan.id,
        status=SubscriptionStatus.TRIAL.value,
        quota_remaining=5,  # Trial limit
        quota_total=5,  # Trial limit, not plan's 20
        trial_ends_at=now + timedelta(days=7),
        current_period_start=now,
        current_period_end=now + timedelta(days=7),
    )
    db_session.add(subscription)
    await db_session.commit()

    # Trial quota should be 5, even though plan has 20
    assert subscription.quota_total == 5
    assert subscription.plan.quota_monthly == 20


@pytest.mark.asyncio
async def test_subscription_cascade_delete(
    db_session: AsyncSession, test_user: User, test_plan: Plan
) -> None:
    """Test subscription is deleted when user is deleted."""
    subscription = Subscription(
        user_id=test_user.id,
        plan_id=test_plan.id,
        status=SubscriptionStatus.TRIAL.value,
        quota_remaining=5,
        quota_total=5,
    )
    db_session.add(subscription)
    await db_session.commit()
    await db_session.refresh(subscription)

    subscription_id = subscription.id

    # Delete user
    await db_session.delete(test_user)
    await db_session.commit()

    # Expire all cached objects to force fresh read from DB
    db_session.expire_all()

    # Subscription should be deleted too (cascade delete via FK constraint)
    result = await db_session.execute(
        select(Subscription).where(Subscription.id == subscription_id)
    )
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_subscription_repr(
    db_session: AsyncSession, test_user: User, test_plan: Plan
) -> None:
    """Test subscription string representation."""
    subscription = Subscription(
        user_id=test_user.id,
        plan_id=test_plan.id,
        status=SubscriptionStatus.TRIAL.value,
        quota_remaining=5,
        quota_total=5,
    )
    db_session.add(subscription)
    await db_session.commit()
    await db_session.refresh(subscription)

    repr_str = repr(subscription)
    assert "Subscription" in repr_str
    assert "trial" in repr_str


@pytest.mark.asyncio
async def test_subscription_stripe_fields_nullable(
    db_session: AsyncSession, test_user: User, test_plan: Plan
) -> None:
    """Test Stripe fields are nullable for trial subscriptions."""
    subscription = Subscription(
        user_id=test_user.id,
        plan_id=test_plan.id,
        status=SubscriptionStatus.TRIAL.value,
        quota_remaining=5,
        quota_total=5,
        stripe_customer_id=None,
        stripe_subscription_id=None,
    )
    db_session.add(subscription)
    await db_session.commit()
    await db_session.refresh(subscription)

    assert subscription.stripe_customer_id is None
    assert subscription.stripe_subscription_id is None


@pytest.mark.asyncio
async def test_user_subscription_relationship(
    db_session: AsyncSession, test_user: User, test_plan: Plan
) -> None:
    """Test user has access to subscription relationship."""
    subscription = Subscription(
        user_id=test_user.id,
        plan_id=test_plan.id,
        status=SubscriptionStatus.TRIAL.value,
        quota_remaining=5,
        quota_total=5,
    )
    db_session.add(subscription)
    await db_session.commit()

    # Refresh user to load relationship
    await db_session.refresh(test_user)

    assert test_user.subscription is not None
    assert test_user.subscription.status == SubscriptionStatus.TRIAL.value
