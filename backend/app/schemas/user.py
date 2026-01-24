"""Pydantic schemas for User model."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """
    Base schema with common User fields.

    Attributes:
        email: User's email address
        name: User's display name (optional)
        avatar_url: URL to user's profile picture (optional)
    """

    email: EmailStr
    name: str | None = None
    avatar_url: str | None = Field(None, alias="avatarUrl")

    model_config = ConfigDict(
        populate_by_name=True,
    )


class UserCreate(UserBase):
    """
    Schema for creating a new user from Google OAuth data.

    Attributes:
        google_id: Unique identifier from Google OAuth
        email: User's email address
        name: User's display name (optional)
        avatar_url: URL to user's profile picture (optional)
    """

    google_id: str = Field(..., alias="googleId")


class UserUpdate(BaseModel):
    """
    Schema for updating user fields.

    All fields are optional to allow partial updates.

    Attributes:
        name: User's display name
        avatar_url: URL to user's profile picture
    """

    name: str | None = None
    avatar_url: str | None = Field(None, alias="avatarUrl")

    model_config = ConfigDict(
        populate_by_name=True,
    )


class UserResponse(UserBase):
    """
    Schema for user response in API.

    Uses camelCase for JSON serialization per project conventions.

    Attributes:
        id: User's UUID
        email: User's email address
        name: User's display name
        avatar_url: URL to user's profile picture
        is_admin: Whether user has admin privileges
        created_at: When the user was created
        updated_at: When the user was last updated
    """

    id: UUID
    is_admin: bool = Field(..., alias="isAdmin")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "name": "Jean Dupont",
                "avatarUrl": "https://example.com/avatar.jpg",
                "isAdmin": False,
                "createdAt": "2026-01-22T10:30:00Z",
                "updatedAt": "2026-01-22T10:30:00Z",
            }
        },
    )


class UserInDB(UserBase):
    """
    Schema for user as stored in database.

    Includes all database fields including google_id.

    Attributes:
        id: User's UUID
        google_id: Google OAuth identifier
        email: User's email address
        name: User's display name
        avatar_url: URL to user's profile picture
        is_admin: Whether user has admin privileges
        created_at: When the user was created
        updated_at: When the user was last updated
    """

    id: UUID
    google_id: str = Field(..., alias="googleId")
    is_admin: bool = Field(..., alias="isAdmin")
    created_at: datetime = Field(..., alias="createdAt")
    updated_at: datetime = Field(..., alias="updatedAt")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )
