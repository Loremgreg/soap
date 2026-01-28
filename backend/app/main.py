"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.config import get_settings
from app.core.exceptions import ApiException, api_exception_handler
from app.routers import auth, plans, recordings, subscriptions

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan handler for startup and shutdown events.

    Args:
        app: FastAPI application instance
    """
    # Startup
    if settings.sentry_dsn and not settings.is_development:
        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            environment=settings.app_env,
            traces_sample_rate=0.1,
        )
    yield
    # Shutdown


app = FastAPI(
    title="SOAP Notice API",
    description="API for audio transcription and SOAP note generation for physiotherapists",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
)

# Session Middleware (required for OAuth state management)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret_key,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Exception Handlers
app.add_exception_handler(ApiException, api_exception_handler)

# Routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(plans.router, prefix="/api/v1")
app.include_router(recordings.router, prefix="/api/v1")
app.include_router(subscriptions.router, prefix="/api/v1")


@app.get("/health")
async def health_check() -> dict[str, str]:
    """
    Health check endpoint for monitoring.

    Returns:
        Status indicating the service is healthy
    """
    return {"status": "healthy"}


@app.get("/api/v1/health")
async def api_health_check() -> dict[str, str]:
    """
    API health check endpoint.

    Returns:
        Status and version information
    """
    return {
        "status": "healthy",
        "version": "0.1.0",
        "environment": settings.app_env,
    }
