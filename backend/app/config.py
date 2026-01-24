"""Application configuration using Pydantic Settings."""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    All settings can be overridden via environment variables.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_env: Literal["development", "staging", "production"] = "development"
    debug: bool = False

    # Server
    api_base_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:5173"

    # Database
    database_url: str = "postgresql+asyncpg://localhost/soap_notice"

    # Authentication
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24 * 7  # 7 days

    # Session (for OAuth state management)
    session_secret_key: str = "change-me-in-production-session"

    # Google OAuth
    google_client_id: str = ""
    google_client_secret: str = ""

    # External Services
    deepgram_api_key: str = ""
    mistral_api_key: str = ""
    llm_provider: Literal["mistral", "azure_openai"] = "mistral"

    # Azure OpenAI (alternative)
    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_deployment: str = ""

    # Stripe
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""

    # Monitoring
    sentry_dsn: str = ""

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.app_env == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Returns:
        Settings instance loaded from environment
    """
    return Settings()
