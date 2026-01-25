"""Tests for Plan model."""

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.plan import Plan


@pytest.mark.asyncio
async def test_plan_creation(db_session: AsyncSession) -> None:
    """Test creating a plan with all required fields."""
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

    assert plan.id is not None
    assert plan.name == "starter"
    assert plan.display_name == "Starter"
    assert plan.price_monthly == 2900
    assert plan.quota_monthly == 20
    assert plan.max_recording_minutes == 10
    assert plan.max_notes_retention == 10
    assert plan.is_active is True
    assert plan.created_at is not None
    assert plan.updated_at is not None


@pytest.mark.asyncio
async def test_plan_default_values(db_session: AsyncSession) -> None:
    """Test plan creation with default values."""
    plan = Plan(
        name="basic",
        display_name="Basic",
        price_monthly=1900,
        quota_monthly=10,
    )
    db_session.add(plan)
    await db_session.commit()
    await db_session.refresh(plan)

    assert plan.max_recording_minutes == 10
    assert plan.max_notes_retention == 10
    assert plan.is_active is True


@pytest.mark.asyncio
async def test_plan_unique_name_constraint(db_session: AsyncSession) -> None:
    """Test that plan names must be unique."""
    plan1 = Plan(
        name="starter",
        display_name="Starter",
        price_monthly=2900,
        quota_monthly=20,
    )
    db_session.add(plan1)
    await db_session.commit()

    plan2 = Plan(
        name="starter",
        display_name="Starter Duplicate",
        price_monthly=3900,
        quota_monthly=25,
    )
    db_session.add(plan2)

    with pytest.raises(Exception):  # IntegrityError
        await db_session.commit()


@pytest.mark.asyncio
async def test_plan_query_active_only(db_session: AsyncSession) -> None:
    """Test querying only active plans."""
    active_plan = Plan(
        name="active_plan",
        display_name="Active Plan",
        price_monthly=2900,
        quota_monthly=20,
        is_active=True,
    )
    inactive_plan = Plan(
        name="inactive_plan",
        display_name="Inactive Plan",
        price_monthly=1900,
        quota_monthly=10,
        is_active=False,
    )
    db_session.add_all([active_plan, inactive_plan])
    await db_session.commit()

    result = await db_session.execute(
        select(Plan).where(Plan.is_active == True)
    )
    active_plans = result.scalars().all()

    assert len(active_plans) == 1
    assert active_plans[0].name == "active_plan"


@pytest.mark.asyncio
async def test_plan_repr(db_session: AsyncSession) -> None:
    """Test plan string representation."""
    plan = Plan(
        name="pro",
        display_name="Pro",
        price_monthly=4900,
        quota_monthly=50,
    )
    db_session.add(plan)
    await db_session.commit()
    await db_session.refresh(plan)

    repr_str = repr(plan)
    assert "Plan" in repr_str
    assert "pro" in repr_str
    assert "4900" in repr_str


@pytest.mark.asyncio
async def test_plan_price_in_cents(db_session: AsyncSession) -> None:
    """Test that price is stored in cents (29€ = 2900 cents)."""
    plan = Plan(
        name="test_plan",
        display_name="Test Plan",
        price_monthly=2900,  # 29€
        quota_monthly=20,
    )
    db_session.add(plan)
    await db_session.commit()
    await db_session.refresh(plan)

    # Price should be 2900 (cents), not 29
    assert plan.price_monthly == 2900
    # Convert to euros for display
    price_euros = plan.price_monthly / 100
    assert price_euros == 29.0
