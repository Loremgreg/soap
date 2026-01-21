"""Standardized exception handling and error responses."""

from typing import Any

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


class ApiException(HTTPException):
    """
    Base API exception with standardized error format.

    Args:
        status_code: HTTP status code
        code: Error code string (e.g., "VALIDATION_ERROR")
        message: Human-readable error message
        details: Optional additional error details
    """

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.code = code
        self.message = message
        self.details = details
        super().__init__(status_code=status_code, detail=message)


class BadRequestException(ApiException):
    """400 Bad Request exception."""

    def __init__(
        self,
        message: str = "Invalid request",
        code: str = "INVALID_REQUEST",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(400, code, message, details)


class UnauthorizedException(ApiException):
    """401 Unauthorized exception."""

    def __init__(
        self,
        message: str = "Authentication required",
        code: str = "UNAUTHORIZED",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(401, code, message, details)


class ForbiddenException(ApiException):
    """403 Forbidden exception."""

    def __init__(
        self,
        message: str = "Access denied",
        code: str = "FORBIDDEN",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(403, code, message, details)


class NotFoundException(ApiException):
    """404 Not Found exception."""

    def __init__(
        self,
        message: str = "Resource not found",
        code: str = "NOT_FOUND",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(404, code, message, details)


class QuotaExceededException(ApiException):
    """403 Quota Exceeded exception."""

    def __init__(
        self,
        message: str = "Monthly quota exceeded",
        used: int = 0,
        limit: int = 0,
    ) -> None:
        super().__init__(
            403,
            "QUOTA_EXCEEDED",
            message,
            {"used": used, "limit": limit},
        )


class TrialExpiredException(ApiException):
    """403 Trial Expired exception."""

    def __init__(
        self,
        message: str = "Trial period has expired",
    ) -> None:
        super().__init__(403, "TRIAL_EXPIRED", message)


class RateLimitedException(ApiException):
    """429 Rate Limited exception."""

    def __init__(
        self,
        message: str = "Too many requests",
        retry_after: int = 60,
    ) -> None:
        super().__init__(
            429,
            "RATE_LIMITED",
            message,
            {"retry_after": retry_after},
        )


async def api_exception_handler(request: Request, exc: ApiException) -> JSONResponse:
    """
    Handle ApiException and return standardized error response.

    Args:
        request: FastAPI request object
        exc: The raised ApiException

    Returns:
        JSONResponse with standardized error format
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )
