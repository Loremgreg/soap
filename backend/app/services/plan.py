"""Plan service for managing subscription plans."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.plan import Plan


async def get_all_active_plans(db: AsyncSession) -> list[Plan]:
    """
    Get all active subscription plans.

    Args:
        db: Database session

    Returns:
        List of active Plan objects, ordered by price ascending
    """
    result = await db.execute(
        select(Plan)
        .where(Plan.is_active == True)
        .order_by(Plan.price_monthly.asc())
    )
    return list(result.scalars().all())


async def get_plan_by_id(db: AsyncSession, plan_id: UUID) -> Plan | None:
    """
    Get a plan by its UUID.

    Args:
        db: Database session
        plan_id: Plan's UUID

    Returns:
        Plan if found, None otherwise
    """
    result = await db.execute(select(Plan).where(Plan.id == plan_id))
    return result.scalar_one_or_none()


async def get_plan_by_name(db: AsyncSession, name: str) -> Plan | None:
    """
    Get a plan by its unique name.

    Args:
        db: Database session
        name: Plan's unique name (e.g., 'starter', 'pro')

    Returns:
        Plan if found, None otherwise
    """
    result = await db.execute(select(Plan).where(Plan.name == name))
    return result.scalar_one_or_none()


async def get_active_plan_by_id(db: AsyncSession, plan_id: UUID) -> Plan | None:
    """
    Get an active plan by its UUID.

    Args:
        db: Database session
        plan_id: Plan's UUID

    Returns:
        Plan if found and active, None otherwise
    """
    result = await db.execute(
        select(Plan)
        .where(Plan.id == plan_id)
        .where(Plan.is_active == True)
    )
    return result.scalar_one_or_none()
