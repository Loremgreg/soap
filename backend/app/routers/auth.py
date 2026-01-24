"""Authentication router for Google OAuth flow."""

from typing import Annotated
from urllib.parse import quote

from authlib.integrations.starlette_client import OAuthError
from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.database import get_db
from app.core.dependencies import get_current_user as get_current_user_dep
from app.core.oauth import GoogleUserInfo, oauth
from app.core.security import create_access_token
from app.models.user import User
from app.schemas.user import UserResponse
from app.services import auth as auth_service

settings = get_settings()

router = APIRouter(prefix="/auth", tags=["authentication"])

# Cookie configuration
COOKIE_NAME = "access_token"
COOKIE_MAX_AGE = 60 * 60 * 24 * 7  # 7 days


def set_auth_cookie(response: Response, token: str) -> None:
    """
    Set the authentication cookie on the response.

    Args:
        response: FastAPI response object
        token: JWT token to store in cookie
    """
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        httponly=True,
        secure=settings.is_production,
        samesite="lax",
        max_age=COOKIE_MAX_AGE,
        path="/",
    )


def clear_auth_cookie(response: Response) -> None:
    """
    Clear the authentication cookie from the response.

    Args:
        response: FastAPI response object
    """
    response.delete_cookie(
        key=COOKIE_NAME,
        path="/",
        httponly=True,
        secure=settings.is_production,
        samesite="lax",
    )


@router.get("/google")
async def google_login(request: Request) -> RedirectResponse:
    """
    Initiate Google OAuth login flow.

    Redirects the user to Google's OAuth consent screen.

    Args:
        request: FastAPI request object (needed for OAuth redirect URI)

    Returns:
        Redirect to Google OAuth consent screen
    """
    redirect_uri = request.url_for("google_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def google_callback(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> RedirectResponse:
    """
    Handle Google OAuth callback.

    Exchanges the authorization code for tokens, extracts user info,
    creates or updates the user, and sets the authentication cookie.

    On error, redirects to /login with error query params for user-friendly display.

    Args:
        request: FastAPI request object with OAuth callback params
        db: Database session

    Returns:
        Redirect to frontend (plan-selection for new users, home for existing,
        or /login with error params if OAuth fails)
    """
    try:
        token = await oauth.google.authorize_access_token(request)
    except OAuthError as e:
        error_code = "OAUTH_CANCELLED" if "cancelled" in str(e).lower() else "OAUTH_FAILED"
        error_description = quote(e.description or str(e))
        redirect_url = f"{settings.frontend_url}/login?error={error_code}&error_description={error_description}"
        return RedirectResponse(url=redirect_url, status_code=302)

    # Extract user info from token
    userinfo = token.get("userinfo")
    if not userinfo:
        error_description = quote("Failed to retrieve user information from Google")
        redirect_url = f"{settings.frontend_url}/login?error=OAUTH_FAILED&error_description={error_description}"
        return RedirectResponse(url=redirect_url, status_code=302)

    # Parse user info
    google_user = GoogleUserInfo.from_userinfo(userinfo)

    # Verify email is confirmed by Google
    if not google_user.email_verified:
        error_description = quote("Email address not verified by Google")
        redirect_url = f"{settings.frontend_url}/login?error=EMAIL_NOT_VERIFIED&error_description={error_description}"
        return RedirectResponse(url=redirect_url, status_code=302)

    # Get or create user in database
    user, is_new = await auth_service.get_or_create_user(
        db=db,
        google_id=google_user.google_id,
        email=google_user.email,
        name=google_user.name,
        avatar_url=google_user.avatar_url,
    )

    # Create JWT token
    jwt_token = create_access_token(user_id=user.id, email=user.email)

    # Determine redirect destination
    redirect_path = "/plan-selection" if is_new else "/"
    redirect_url = f"{settings.frontend_url}{redirect_path}"

    # Create response with redirect
    response = RedirectResponse(url=redirect_url, status_code=302)
    set_auth_cookie(response, jwt_token)

    return response


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: Annotated[User, Depends(get_current_user_dep)],
) -> UserResponse:
    """
    Get the currently authenticated user.

    Uses the get_current_user dependency to extract and validate
    the JWT from the httpOnly cookie.

    Args:
        current_user: The authenticated user (injected by dependency)

    Returns:
        Current user's information

    Raises:
        UnauthorizedException: If not authenticated or token invalid
    """
    return UserResponse.model_validate(current_user)


@router.post("/logout")
async def logout(response: Response) -> dict[str, str]:
    """
    Log out the current user.

    Clears the authentication cookie.

    Args:
        response: FastAPI response object

    Returns:
        Success message
    """
    clear_auth_cookie(response)
    return {"message": "Successfully logged out"}
