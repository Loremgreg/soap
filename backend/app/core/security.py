"""JWT token creation and verification utilities."""

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from jose import JWTError, jwt

from app.config import get_settings

settings = get_settings()


class TokenError(Exception):
    """Base exception for token-related errors."""

    pass


class TokenExpiredError(TokenError):
    """Raised when a token has expired."""

    pass


class InvalidTokenError(TokenError):
    """Raised when a token is invalid or malformed."""

    pass


def create_access_token(
    user_id: UUID,
    email: str,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Create a JWT access token for a user.

    Args:
        user_id: The user's UUID
        email: The user's email address
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token string
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.jwt_expire_minutes)

    now = datetime.now(timezone.utc)
    expire = now + expires_delta

    payload: dict[str, Any] = {
        "sub": str(user_id),
        "email": email,
        "iat": now,
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )


def verify_token(token: str) -> dict[str, Any]:
    """
    Verify and decode a JWT token.

    Args:
        token: The JWT token string to verify

    Returns:
        Decoded token payload as dictionary

    Raises:
        TokenExpiredError: If the token has expired
        InvalidTokenError: If the token is invalid or malformed
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except jwt.ExpiredSignatureError as e:
        raise TokenExpiredError("Token has expired") from e
    except JWTError as e:
        raise InvalidTokenError("Invalid token") from e


def get_token_payload(token: str) -> dict[str, Any]:
    """
    Get the payload from a JWT token without verification.

    Useful for extracting claims from potentially expired tokens.

    Args:
        token: The JWT token string

    Returns:
        Decoded token payload as dictionary

    Raises:
        InvalidTokenError: If the token is malformed
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
            options={"verify_exp": False},
        )
        return payload
    except JWTError as e:
        raise InvalidTokenError("Invalid token") from e


def get_user_id_from_token(token: str) -> UUID:
    """
    Extract the user ID from a verified JWT token.

    Args:
        token: The JWT token string

    Returns:
        User's UUID

    Raises:
        TokenExpiredError: If the token has expired
        InvalidTokenError: If the token is invalid or missing user ID
    """
    payload = verify_token(token)
    user_id_str = payload.get("sub")

    if not user_id_str:
        raise InvalidTokenError("Token missing user ID")

    try:
        return UUID(user_id_str)
    except ValueError as e:
        raise InvalidTokenError("Invalid user ID in token") from e
