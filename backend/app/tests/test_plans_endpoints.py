"""Tests for plans API endpoints."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.plan import Plan


@pytest.fixture
async def seed_plans(db_session: AsyncSession) -> list[Plan]:
    """Seed test plans in database."""
    starter_plan = Plan(
        name="starter",
        display_name="Starter",
        price_monthly=2900,
        quota_monthly=20,
        max_recording_minutes=10,
        max_notes_retention=10,
        is_active=True,
    )
    pro_plan = Plan(
        name="pro",
        display_name="Pro",
        price_monthly=4900,
        quota_monthly=50,
        max_recording_minutes=10,
        max_notes_retention=10,
        is_active=True,
    )
    inactive_plan = Plan(
        name="legacy",
        display_name="Legacy",
        price_monthly=1900,
        quota_monthly=10,
        max_recording_minutes=5,
        max_notes_retention=5,
        is_active=False,
    )
    db_session.add_all([starter_plan, pro_plan, inactive_plan])
    await db_session.commit()
    await db_session.refresh(starter_plan)
    await db_session.refresh(pro_plan)
    await db_session.refresh(inactive_plan)
    return [starter_plan, pro_plan, inactive_plan]


@pytest.mark.asyncio
async def test_get_plans_returns_active_only(
    client: AsyncClient, seed_plans: list[Plan]
) -> None:
    """Test GET /api/v1/plans returns only active plans."""
    response = await client.get("/api/v1/plans")

    assert response.status_code == 200
    plans = response.json()

    # Should only return active plans (starter, pro)
    assert len(plans) == 2

    plan_names = [p["name"] for p in plans]
    assert "starter" in plan_names
    assert "pro" in plan_names
    assert "legacy" not in plan_names


@pytest.mark.asyncio
async def test_get_plans_ordered_by_price(
    client: AsyncClient, seed_plans: list[Plan]
) -> None:
    """Test GET /api/v1/plans returns plans ordered by price ascending."""
    response = await client.get("/api/v1/plans")

    assert response.status_code == 200
    plans = response.json()

    # Starter (2900) should come before Pro (4900)
    assert plans[0]["name"] == "starter"
    assert plans[0]["priceMonthly"] == 2900
    assert plans[1]["name"] == "pro"
    assert plans[1]["priceMonthly"] == 4900


@pytest.mark.asyncio
async def test_get_plans_response_format(
    client: AsyncClient, seed_plans: list[Plan]
) -> None:
    """Test GET /api/v1/plans response uses camelCase."""
    response = await client.get("/api/v1/plans")

    assert response.status_code == 200
    plans = response.json()

    plan = plans[0]
    # Check camelCase fields
    assert "id" in plan
    assert "name" in plan
    assert "displayName" in plan
    assert "priceMonthly" in plan
    assert "quotaMonthly" in plan
    assert "maxRecordingMinutes" in plan
    assert "maxNotesRetention" in plan
    assert "isActive" in plan


@pytest.mark.asyncio
async def test_get_plan_by_id(
    client: AsyncClient, seed_plans: list[Plan]
) -> None:
    """Test GET /api/v1/plans/{plan_id} returns plan details."""
    starter_plan = seed_plans[0]

    response = await client.get(f"/api/v1/plans/{starter_plan.id}")

    assert response.status_code == 200
    plan = response.json()

    assert plan["id"] == str(starter_plan.id)
    assert plan["name"] == "starter"
    assert plan["displayName"] == "Starter"
    assert plan["priceMonthly"] == 2900
    assert plan["quotaMonthly"] == 20


@pytest.mark.asyncio
async def test_get_plan_by_id_not_found(client: AsyncClient) -> None:
    """Test GET /api/v1/plans/{plan_id} returns 404 for unknown plan."""
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = await client.get(f"/api/v1/plans/{fake_id}")

    assert response.status_code == 404
    error = response.json()["detail"]["error"]
    assert error["code"] == "PLAN_NOT_FOUND"


@pytest.mark.asyncio
async def test_get_plan_by_id_inactive_returns_404(
    client: AsyncClient, seed_plans: list[Plan]
) -> None:
    """Test GET /api/v1/plans/{plan_id} returns 404 for inactive plan."""
    inactive_plan = seed_plans[2]  # Legacy plan is inactive

    response = await client.get(f"/api/v1/plans/{inactive_plan.id}")

    assert response.status_code == 404
    error = response.json()["detail"]["error"]
    assert error["code"] == "PLAN_NOT_FOUND"


@pytest.mark.asyncio
async def test_get_plans_empty_database(client: AsyncClient) -> None:
    """Test GET /api/v1/plans returns empty list if no plans."""
    response = await client.get("/api/v1/plans")

    assert response.status_code == 200
    plans = response.json()
    assert plans == []
