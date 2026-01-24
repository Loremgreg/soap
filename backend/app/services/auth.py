"""Authentication service for user management."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate


async def get_user_by_id(db: AsyncSession, user_id: UUID) -> User | None:
    """
    Get a user by their internal UUID.

    Args:
        db: Database session
        user_id: User's UUID

    Returns:
        User if found, None otherwise
    """
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_google_id(db: AsyncSession, google_id: str) -> User | None:
    """
    Get a user by their Google OAuth ID.

    Args:
        db: Database session
        google_id: Google's unique identifier for the user

    Returns:
        User if found, None otherwise
    """
    result = await db.execute(select(User).where(User.google_id == google_id))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """
    Get a user by their email address.

    Args:
        db: Database session
        email: User's email address

    Returns:
        User if found, None otherwise
    """
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
    """
    Create a new user from OAuth data.

    Args:
        db: Database session
        user_data: User creation data from OAuth

    Returns:
        Newly created User
    """
    user = User(
        google_id=user_data.google_id,
        email=user_data.email,
        name=user_data.name,
        avatar_url=user_data.avatar_url,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_user_profile(
    db: AsyncSession,
    user: User,
    name: str | None = None,
    avatar_url: str | None = None,
) -> User:
    """
    Update a user's profile information.

    Args:
        db: Database session
        user: User to update
        name: New display name (optional)
        avatar_url: New avatar URL (optional)

    Returns:
        Updated User
    """
    if name is not None:
        user.name = name
    if avatar_url is not None:
        user.avatar_url = avatar_url

    await db.commit()
    await db.refresh(user)
    return user


async def get_or_create_user(
    db: AsyncSession,
    google_id: str,
    email: str,
    name: str | None = None,
    avatar_url: str | None = None,
) -> tuple[User, bool]:
    """
    Get an existing user or create a new one.

    This is the main function called during OAuth login flow.
    If a user with the given google_id exists, return them.
    Otherwise, create a new user with the provided information.

    Args:
        db: Database session
        google_id: Google's unique identifier
        email: User's email address
        name: User's display name
        avatar_url: URL to user's profile picture

    Returns:
        Tuple of (User, is_new) where is_new indicates if user was just created
    """
    user = await get_user_by_google_id(db, google_id)

    if user:
        # Update profile if info changed
        updated = False
        if name and user.name != name:
            user.name = name
            updated = True
        if avatar_url and user.avatar_url != avatar_url:
            user.avatar_url = avatar_url
            updated = True

        if updated:
            await db.commit()
            await db.refresh(user)

        return user, False

    # Create new user
    user_data = UserCreate(
        google_id=google_id,
        email=email,
        name=name,
        avatar_url=avatar_url,
    )
    user = await create_user(db, user_data)
    return user, True
