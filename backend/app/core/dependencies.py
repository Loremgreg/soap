"""FastAPI dependencies for authentication and authorization."""

from typing import Annotated
from uuid import UUID

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import UnauthorizedException
from app.core.security import (
    InvalidTokenError,
    TokenExpiredError,
    verify_token,
)
from app.models.user import User
from app.services import auth as auth_service

# Cookie name for authentication token
COOKIE_NAME = "access_token"


async def get_current_user(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """
    FastAPI dependency to get the current authenticated user.

    Extracts the JWT from the httpOnly cookie, verifies it,
    and returns the corresponding user from the database.

    Args:
        request: FastAPI request object containing cookies
        db: Database session

    Returns:
        The authenticated User

    Raises:
        UnauthorizedException: If not authenticated, token invalid/expired,
                               or user not found

    Usage:
        @router.get("/protected")
        async def protected_route(
            current_user: Annotated[User, Depends(get_current_user)]
        ):
            return {"user_id": current_user.id}
    """
    # Extract token from cookie
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        raise UnauthorizedException(
            message="Not authenticated",
            code="UNAUTHORIZED",
        )

    # Verify token
    try:
        payload = verify_token(token)
    except TokenExpiredError:
        raise UnauthorizedException(
            message="Token has expired",
            code="TOKEN_EXPIRED",
        )
    except InvalidTokenError:
        raise UnauthorizedException(
            message="Invalid token",
            code="INVALID_TOKEN",
        )

    # Extract user ID from payload
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise UnauthorizedException(
            message="Invalid token payload",
            code="INVALID_TOKEN",
        )

    # Parse user ID
    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise UnauthorizedException(
            message="Invalid user ID in token",
            code="INVALID_TOKEN",
        )

    # Get user from database
    user = await auth_service.get_user_by_id(db, user_id)
    if not user:
        raise UnauthorizedException(
            message="User not found",
            code="UNAUTHORIZED",
        )

    return user


async def get_current_user_optional(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User | None:
    """
    FastAPI dependency to optionally get the current user.

    Similar to get_current_user but returns None instead of
    raising an exception when not authenticated.

    Args:
        request: FastAPI request object containing cookies
        db: Database session

    Returns:
        The authenticated User or None if not authenticated

    Usage:
        @router.get("/public")
        async def public_route(
            current_user: Annotated[User | None, Depends(get_current_user_optional)]
        ):
            if current_user:
                return {"authenticated": True, "user_id": current_user.id}
            return {"authenticated": False}
    """
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None

    try:
        payload = verify_token(token)
    except (TokenExpiredError, InvalidTokenError):
        return None

    user_id_str = payload.get("sub")
    if not user_id_str:
        return None

    try:
        user_id = UUID(user_id_str)
    except ValueError:
        return None

    return await auth_service.get_user_by_id(db, user_id)


async def get_current_admin_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    FastAPI dependency to get the current user and verify admin privileges.

    Args:
        current_user: The authenticated user

    Returns:
        The authenticated admin User

    Raises:
        UnauthorizedException: If user is not an admin

    Usage:
        @router.get("/admin/dashboard")
        async def admin_dashboard(
            admin: Annotated[User, Depends(get_current_admin_user)]
        ):
            return {"admin_id": admin.id}
    """
    if not current_user.is_admin:
        raise UnauthorizedException(
            message="Admin privileges required",
            code="FORBIDDEN",
        )
    return current_user


# Type aliases for cleaner dependency injection
CurrentUser = Annotated[User, Depends(get_current_user)]
OptionalUser = Annotated[User | None, Depends(get_current_user_optional)]
AdminUser = Annotated[User, Depends(get_current_admin_user)]
