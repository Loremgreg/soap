"""Plans router for subscription plan endpoints."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.plan import PlanResponse
from app.services import plan as plan_service

router = APIRouter(prefix="/plans", tags=["plans"])


@router.get("", response_model=list[PlanResponse])
async def get_plans(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[PlanResponse]:
    """
    Get all active subscription plans.

    Returns plans ordered by price ascending (cheapest first).
    Only returns active plans that are available for purchase.

    Args:
        db: Database session

    Returns:
        List of active plans with their configuration
    """
    plans = await plan_service.get_all_active_plans(db)
    return [PlanResponse.model_validate(plan) for plan in plans]


@router.get("/{plan_id}", response_model=PlanResponse)
async def get_plan(
    plan_id: UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> PlanResponse:
    """
    Get a specific plan by ID.

    Args:
        plan_id: UUID of the plan to retrieve
        db: Database session

    Returns:
        Plan details

    Raises:
        HTTPException: 404 if plan not found or not active
    """
    plan = await plan_service.get_active_plan_by_id(db, plan_id)
    if not plan:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "PLAN_NOT_FOUND",
                    "message": "Plan not found or not active",
                }
            },
        )
    return PlanResponse.model_validate(plan)
