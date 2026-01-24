"""Tests for User model."""

import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class TestUserModel:
    """Tests for User SQLAlchemy model."""

    @pytest.mark.asyncio
    async def test_create_user(self, db_session: AsyncSession) -> None:
        """
        Test creating a user with all required fields.

        Verifies:
            - User can be created with valid data
            - UUID is auto-generated
            - Timestamps are auto-set
        """
        user = User(
            google_id="123456789",
            email="test@example.com",
            name="Test User",
            avatar_url="https://example.com/avatar.jpg",
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        assert user.id is not None
        assert isinstance(user.id, uuid.UUID)
        assert user.google_id == "123456789"
        assert user.email == "test@example.com"
        assert user.name == "Test User"
        assert user.avatar_url == "https://example.com/avatar.jpg"
        assert user.is_admin is False
        assert user.created_at is not None
        assert user.updated_at is not None

    @pytest.mark.asyncio
    async def test_user_google_id_unique(self, db_session: AsyncSession) -> None:
        """
        Test that google_id must be unique.

        Verifies:
            - Duplicate google_id raises IntegrityError
        """
        user1 = User(google_id="same-id", email="user1@example.com")
        db_session.add(user1)
        await db_session.commit()

        user2 = User(google_id="same-id", email="user2@example.com")
        db_session.add(user2)

        from sqlalchemy.exc import IntegrityError

        with pytest.raises(IntegrityError):
            await db_session.commit()

    @pytest.mark.asyncio
    async def test_user_email_unique(self, db_session: AsyncSession) -> None:
        """
        Test that email must be unique.

        Verifies:
            - Duplicate email raises IntegrityError
        """
        user1 = User(google_id="id-1", email="same@example.com")
        db_session.add(user1)
        await db_session.commit()

        user2 = User(google_id="id-2", email="same@example.com")
        db_session.add(user2)

        from sqlalchemy.exc import IntegrityError

        with pytest.raises(IntegrityError):
            await db_session.commit()

    @pytest.mark.asyncio
    async def test_user_optional_fields(self, db_session: AsyncSession) -> None:
        """
        Test that name and avatar_url are optional.

        Verifies:
            - User can be created with only required fields
        """
        user = User(
            google_id="minimal-user",
            email="minimal@example.com",
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)

        assert user.name is None
        assert user.avatar_url is None

    @pytest.mark.asyncio
    async def test_query_user_by_google_id(self, db_session: AsyncSession) -> None:
        """
        Test querying user by google_id.

        Verifies:
            - User can be retrieved by google_id
        """
        user = User(google_id="query-test", email="query@example.com")
        db_session.add(user)
        await db_session.commit()

        result = await db_session.execute(
            select(User).where(User.google_id == "query-test")
        )
        found_user = result.scalar_one_or_none()

        assert found_user is not None
        assert found_user.email == "query@example.com"

    @pytest.mark.asyncio
    async def test_query_user_by_email(self, db_session: AsyncSession) -> None:
        """
        Test querying user by email.

        Verifies:
            - User can be retrieved by email
        """
        user = User(google_id="email-test", email="email-query@example.com")
        db_session.add(user)
        await db_session.commit()

        result = await db_session.execute(
            select(User).where(User.email == "email-query@example.com")
        )
        found_user = result.scalar_one_or_none()

        assert found_user is not None
        assert found_user.google_id == "email-test"
