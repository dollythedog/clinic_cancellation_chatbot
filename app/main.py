"""
Clinic Cancellation Chatbot - FastAPI Main Application

Entry point for the FastAPI backend service.
Handles SMS webhooks, admin API, and orchestration logic.

Author: Jonathan Ives (@dollythedog)
"""

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.admin import router as admin_router
from app.api.health import router as health_router
from app.api.middleware import TwilioSignatureMiddleware
from app.api.sms_webhook import router as sms_router
from app.api.status_webhook import router as status_router
from app.core.scheduler import init_scheduler, shutdown_scheduler
from app.infra.db import check_db_connection
from app.infra.logging_config import configure_logging
from app.infra.settings import settings, validate_settings

# NOTE: Do NOT call logging.basicConfig here. The structlog-based
# backbone is installed by configure_logging(), which is invoked from
# the FastAPI lifespan hook so validation failures are emitted through
# the same structured pipeline operators will see in production.
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup/shutdown events.

    Order of operations is deliberate:
    1. ``configure_logging()`` installs the structured-logging backbone
       so every subsequent startup message is captured as JSON.
    2. ``validate_settings()`` gates startup on required env vars.
    3. DB connection probe emits a structured ``db.startup_probe`` event.
    4. Scheduler initializes and emits its own startup events.
    """
    # Install the structured logging backbone FIRST so every startup
    # message is captured in the canonical JSON form.
    configure_logging()

    logger.info("app.startup.begin", app_name=settings.APP_NAME, version=settings.APP_VERSION)

    # Explicit configuration validation gate. Raises ValidationError and
    # aborts startup if any required environment variable is missing.
    validate_settings()
    logger.info("app.startup.config_validated")

    # Check database connection
    if check_db_connection():
        logger.info("db.startup_probe", outcome="connected")
    else:
        logger.error("db.startup_probe", outcome="failed")

    # Initialize scheduler
    init_scheduler()
    logger.info("app.startup.scheduler_ready")

    logger.info("app.startup.complete")

    yield

    # Shutdown
    logger.info("app.shutdown.begin")

    # Shutdown scheduler
    shutdown_scheduler()

    logger.info("app.shutdown.complete")


# Create FastAPI application
app = FastAPI(
    title="Clinic Cancellation Chatbot",
    description="Automated SMS-based waitlist management for appointment cancellations",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enforce Twilio signature verification on /sms/* and /twilio/* paths.
# Unsigned or invalidly-signed POSTs are rejected with HTTP 403 before
# any route handler runs. All other paths (/healthz, /readyz, /health,
# /, /docs, /admin/*) pass through unmodified. See
# `app.api.middleware.TwilioSignatureMiddleware` for the full contract
# and DECISIONS.md 2026-04-23 "Twilio signature middleware URL strategy".
app.add_middleware(TwilioSignatureMiddleware)


# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    """
    return {"status": "healthy", "service": "clinic-cancellation-chatbot", "version": "0.1.0"}


@app.get("/")
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "message": "Clinic Cancellation Chatbot API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
    }


# Include API routers
app.include_router(admin_router)  # Prefix: /admin
app.include_router(sms_router)  # Prefix: /sms
app.include_router(status_router)  # Prefix: /twilio
app.include_router(health_router)  # No prefix — /healthz and /readyz are public probes

logger.info("app.routers_registered", routers=["admin", "sms", "twilio", "health"])
logger.info(
    "app.middleware_registered",
    middleware=["CORSMiddleware", "TwilioSignatureMiddleware"],
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
