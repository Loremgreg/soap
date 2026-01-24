"""Google OAuth configuration using Authlib."""

from authlib.integrations.starlette_client import OAuth, OAuthError
from starlette.config import Config

from app.config import get_settings

settings = get_settings()

# OAuth configuration
oauth = OAuth()

# Register Google OAuth provider
oauth.register(
    name="google",
    client_id=settings.google_client_id,
    client_secret=settings.google_client_secret,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid email profile",
    },
)


class GoogleUserInfo:
    """
    Structured representation of Google user information.

    Attributes:
        google_id: Unique identifier from Google (sub claim)
        email: User's email address
        email_verified: Whether Google has verified the email
        name: User's display name
        avatar_url: URL to user's profile picture
    """

    def __init__(
        self,
        google_id: str,
        email: str,
        email_verified: bool = False,
        name: str | None = None,
        avatar_url: str | None = None,
    ):
        self.google_id = google_id
        self.email = email
        self.email_verified = email_verified
        self.name = name
        self.avatar_url = avatar_url

    @classmethod
    def from_userinfo(cls, userinfo: dict) -> "GoogleUserInfo":
        """
        Create GoogleUserInfo from Google userinfo response.

        Args:
            userinfo: Dictionary from Google's userinfo endpoint

        Returns:
            GoogleUserInfo instance with extracted data
        """
        return cls(
            google_id=userinfo["sub"],
            email=userinfo["email"],
            email_verified=userinfo.get("email_verified", False),
            name=userinfo.get("name"),
            avatar_url=userinfo.get("picture"),
        )


# Re-export OAuthError for handling in routes
__all__ = ["oauth", "GoogleUserInfo", "OAuthError"]
