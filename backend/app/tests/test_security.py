"""Tests for JWT security utilities."""

import uuid
from datetime import timedelta

import pytest
from freezegun import freeze_time

from app.core.security import (
    InvalidTokenError,
    TokenExpiredError,
    create_access_token,
    get_token_payload,
    get_user_id_from_token,
    verify_token,
)


class TestCreateAccessToken:
    """Tests for create_access_token function."""

    def test_creates_valid_token(self) -> None:
        """Test that a valid JWT token is created."""
        user_id = uuid.uuid4()
        email = "test@example.com"

        token = create_access_token(user_id=user_id, email=email)

        assert isinstance(token, str)
        assert len(token) > 0
        # Token should have 3 parts separated by dots
        assert len(token.split(".")) == 3

    def test_token_contains_correct_claims(self) -> None:
        """Test that token contains correct user claims."""
        user_id = uuid.uuid4()
        email = "test@example.com"

        token = create_access_token(user_id=user_id, email=email)
        payload = get_token_payload(token)

        assert payload["sub"] == str(user_id)
        assert payload["email"] == email
        assert "iat" in payload
        assert "exp" in payload

    def test_custom_expiration(self) -> None:
        """Test token with custom expiration time."""
        user_id = uuid.uuid4()
        email = "test@example.com"
        expires_delta = timedelta(hours=1)

        token = create_access_token(
            user_id=user_id,
            email=email,
            expires_delta=expires_delta,
        )
        payload = get_token_payload(token)

        # Expiration should be approximately 1 hour from issuance
        exp_diff = payload["exp"] - payload["iat"]
        assert 3590 <= exp_diff <= 3610  # Allow small variance


class TestVerifyToken:
    """Tests for verify_token function."""

    def test_verifies_valid_token(self) -> None:
        """Test successful verification of valid token."""
        user_id = uuid.uuid4()
        email = "test@example.com"
        token = create_access_token(user_id=user_id, email=email)

        payload = verify_token(token)

        assert payload["sub"] == str(user_id)
        assert payload["email"] == email

    def test_raises_on_invalid_token(self) -> None:
        """Test that invalid token raises InvalidTokenError."""
        with pytest.raises(InvalidTokenError):
            verify_token("invalid.token.here")

    def test_raises_on_malformed_token(self) -> None:
        """Test that malformed token raises InvalidTokenError."""
        with pytest.raises(InvalidTokenError):
            verify_token("not-a-jwt")

    @freeze_time("2026-01-22 12:00:00")
    def test_raises_on_expired_token(self) -> None:
        """Test that expired token raises TokenExpiredError."""
        user_id = uuid.uuid4()
        email = "test@example.com"

        # Create token that expires in 1 second
        token = create_access_token(
            user_id=user_id,
            email=email,
            expires_delta=timedelta(seconds=1),
        )

        # Move time forward
        with freeze_time("2026-01-22 12:01:00"):
            with pytest.raises(TokenExpiredError):
                verify_token(token)

    def test_raises_on_tampered_token(self) -> None:
        """Test that tampered token raises InvalidTokenError."""
        user_id = uuid.uuid4()
        email = "test@example.com"
        token = create_access_token(user_id=user_id, email=email)

        # Tamper with token payload
        parts = token.split(".")
        tampered_token = parts[0] + ".tampered." + parts[2]

        with pytest.raises(InvalidTokenError):
            verify_token(tampered_token)


class TestGetUserIdFromToken:
    """Tests for get_user_id_from_token function."""

    def test_extracts_user_id(self) -> None:
        """Test successful extraction of user ID."""
        user_id = uuid.uuid4()
        email = "test@example.com"
        token = create_access_token(user_id=user_id, email=email)

        extracted_id = get_user_id_from_token(token)

        assert extracted_id == user_id
        assert isinstance(extracted_id, uuid.UUID)

    def test_raises_on_invalid_token(self) -> None:
        """Test that invalid token raises error."""
        with pytest.raises(InvalidTokenError):
            get_user_id_from_token("invalid.token")


class TestGetTokenPayload:
    """Tests for get_token_payload function."""

    def test_gets_payload_from_valid_token(self) -> None:
        """Test getting payload from valid token."""
        user_id = uuid.uuid4()
        email = "test@example.com"
        token = create_access_token(user_id=user_id, email=email)

        payload = get_token_payload(token)

        assert payload["sub"] == str(user_id)
        assert payload["email"] == email

    @freeze_time("2026-01-22 12:00:00")
    def test_gets_payload_from_expired_token(self) -> None:
        """Test that payload can be extracted from expired token."""
        user_id = uuid.uuid4()
        email = "test@example.com"

        # Create token that expires immediately
        token = create_access_token(
            user_id=user_id,
            email=email,
            expires_delta=timedelta(seconds=1),
        )

        # Move time forward
        with freeze_time("2026-01-22 12:01:00"):
            # Should not raise even though token is expired
            payload = get_token_payload(token)
            assert payload["sub"] == str(user_id)

    def test_raises_on_malformed_token(self) -> None:
        """Test that malformed token raises InvalidTokenError."""
        with pytest.raises(InvalidTokenError):
            get_token_payload("not-a-valid-jwt")
