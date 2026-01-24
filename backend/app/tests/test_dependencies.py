"""Tests for authentication dependencies."""

import uuid
from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.dependencies import (
    COOKIE_NAME,
    get_current_admin_user,
    get_current_user,
    get_current_user_optional,
)
from app.core.exceptions import UnauthorizedException
from app.core.security import create_access_token
from app.models.user import User


def create_mock_request(token: str | None = None) -> MagicMock:
    """Create a mock request with optional auth cookie."""
    request = MagicMock()
    if token:
        request.cookies = {COOKIE_NAME: token}
    else:
        request.cookies = {}
    return request


def create_mock_user(
    user_id: uuid.UUID | None = None,
    is_admin: bool = False,
) -> User:
    """Create a mock user for testing."""
    user = MagicMock(spec=User)
    user.id = user_id or uuid.uuid4()
    user.google_id = "test-google-id"
    user.email = "test@example.com"
    user.name = "Test User"
    user.is_admin = is_admin
    return user


class TestGetCurrentUser:
    """Tests for get_current_user dependency."""

    @pytest.mark.asyncio
    async def test_raises_without_cookie(self) -> None:
        """Test that missing cookie raises UnauthorizedException."""
        request = create_mock_request(token=None)
        db = AsyncMock()

        with pytest.raises(UnauthorizedException) as exc_info:
            await get_current_user(request, db)

        assert exc_info.value.code == "UNAUTHORIZED"

    @pytest.mark.asyncio
    async def test_raises_with_invalid_token(self) -> None:
        """Test that invalid token raises UnauthorizedException."""
        request = create_mock_request(token="invalid.token.here")
        db = AsyncMock()

        with pytest.raises(UnauthorizedException) as exc_info:
            await get_current_user(request, db)

        assert exc_info.value.code == "INVALID_TOKEN"

    @pytest.mark.asyncio
    async def test_raises_with_expired_token(self) -> None:
        """Test that expired token raises UnauthorizedException."""
        user_id = uuid.uuid4()
        expired_token = create_access_token(
            user_id=user_id,
            email="test@example.com",
            expires_delta=timedelta(seconds=-10),
        )
        request = create_mock_request(token=expired_token)
        db = AsyncMock()

        with pytest.raises(UnauthorizedException) as exc_info:
            await get_current_user(request, db)

        assert exc_info.value.code == "TOKEN_EXPIRED"


class TestGetCurrentUserOptional:
    """Tests for get_current_user_optional dependency."""

    @pytest.mark.asyncio
    async def test_returns_none_without_cookie(self) -> None:
        """Test that missing cookie returns None."""
        request = create_mock_request(token=None)
        db = AsyncMock()

        result = await get_current_user_optional(request, db)

        assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_with_invalid_token(self) -> None:
        """Test that invalid token returns None."""
        request = create_mock_request(token="invalid.token")
        db = AsyncMock()

        result = await get_current_user_optional(request, db)

        assert result is None

    @pytest.mark.asyncio
    async def test_returns_none_with_expired_token(self) -> None:
        """Test that expired token returns None."""
        user_id = uuid.uuid4()
        expired_token = create_access_token(
            user_id=user_id,
            email="test@example.com",
            expires_delta=timedelta(seconds=-10),
        )
        request = create_mock_request(token=expired_token)
        db = AsyncMock()

        result = await get_current_user_optional(request, db)

        assert result is None


class TestGetCurrentAdminUser:
    """Tests for get_current_admin_user dependency."""

    @pytest.mark.asyncio
    async def test_returns_admin_user(self) -> None:
        """Test that admin user is returned successfully."""
        admin_user = create_mock_user(is_admin=True)

        result = await get_current_admin_user(admin_user)

        assert result == admin_user

    @pytest.mark.asyncio
    async def test_raises_for_non_admin(self) -> None:
        """Test that non-admin user raises UnauthorizedException."""
        regular_user = create_mock_user(is_admin=False)

        with pytest.raises(UnauthorizedException) as exc_info:
            await get_current_admin_user(regular_user)

        assert exc_info.value.code == "FORBIDDEN"
