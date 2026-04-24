"""
Settings - Application configuration from environment variables.

This module defines the single `Settings` class used by the entire
application for configuration. All configuration flows through this class.
Required secrets are declared as non-defaulted fields; missing required
values cause a **loud startup failure** (pydantic ``ValidationError``)
rather than silently falling back to a default.

See ``.env.example`` at the repo root for the full list of keys. At
application startup, call :func:`validate_settings` from the FastAPI
lifespan hook to make configuration validation explicit and to emit a
clean error message naming the missing keys.

Author: Jonathan Ives (@dollythedog)
"""

import sys

import structlog
from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

# NOTE: This module is imported very early in the startup sequence —
# before ``configure_logging()`` has installed the structured backbone.
# structlog.get_logger() is safe to call at import time; any events
# emitted before configure_logging runs pass through structlog's
# default stderr factory. After configure_logging runs, subsequent
# events route through the full JSON pipeline.
logger = structlog.get_logger(__name__)


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    See .env.example at the repo root for all available settings and descriptions.
    """

    # ========================================================================
    # DATABASE
    # ========================================================================
    DATABASE_URL: str = Field(..., description="PostgreSQL connection string")
    DB_POOL_SIZE: int = Field(5, description="Connection pool size")
    DB_MAX_OVERFLOW: int = Field(10, description="Max overflow connections")

    # ========================================================================
    # TWILIO
    # ========================================================================
    TWILIO_ACCOUNT_SID: str = Field(..., description="Twilio Account SID")
    TWILIO_AUTH_TOKEN: str = Field(..., description="Twilio Auth Token")
    TWILIO_PHONE_NUMBER: str = Field(..., description="Twilio phone number (E.164)")
    TWILIO_MESSAGING_SERVICE_SID: str | None = Field(
        None, description="Twilio Messaging Service SID"
    )
    TWILIO_WEBHOOK_BASE_URL: str | None = Field(None, description="Public webhook base URL")
    TWILIO_WEBHOOK_SECRET: str | None = Field(None, description="Webhook signature secret")

    # ========================================================================
    # APPLICATION
    # ========================================================================
    BATCH_SIZE: int = Field(3, description="Number of patients per offer batch")
    HOLD_MINUTES: int = Field(7, description="Minutes to hold slot before next batch")
    CONTACT_HOURS_START: str = Field("08:00", description="Contact hours start time (HH:MM)")
    CONTACT_HOURS_END: str = Field("20:00", description="Contact hours end time (HH:MM)")
    TIMEZONE: str = Field("America/Chicago", description="Default timezone")

    # ========================================================================
    # SECURITY
    # ========================================================================
    API_KEY: str | None = Field(None, description="API key for admin endpoints")
    JWT_SECRET: str | None = Field(None, description="JWT secret for sessions")
    WEBHOOK_SIGNATURE_ENABLED: bool = Field(True, description="Verify Twilio webhook signatures")

    # ========================================================================
    # LOGGING
    # ========================================================================
    LOG_LEVEL: str = Field("INFO", description="Logging level")
    LOG_FILE: str = Field("data/logs/app.log", description="Log file path")
    LOG_MAX_BYTES: int = Field(10485760, description="Max log file size (10MB)")
    LOG_BACKUP_COUNT: int = Field(5, description="Number of log backups")

    # ========================================================================
    # FASTAPI
    # ========================================================================
    APP_NAME: str = Field("Clinic Cancellation Chatbot", description="Application name")
    APP_VERSION: str = Field("0.1.0", description="Application version")
    APP_HOST: str = Field("0.0.0.0", description="FastAPI host")
    APP_PORT: int = Field(8000, description="FastAPI port")
    DEBUG: bool = Field(False, description="Debug mode")
    CORS_ORIGINS: str = Field("http://localhost:8501", description="CORS origins (comma-separated)")

    # ========================================================================
    # STREAMLIT
    # ========================================================================
    STREAMLIT_SERVER_PORT: int = Field(8501, description="Streamlit port")
    STREAMLIT_SERVER_ADDRESS: str = Field(
        "127.0.0.1",
        description=(
            "Streamlit host bind address. Defaults to loopback so the dashboard is "
            "unreachable from the clinic LAN; the HTTP basic-auth-style login "
            "wrapper in dashboard/auth.py adds a second layer of defense for "
            "on-host access. Set to 0.0.0.0 only when you have verified an "
            "upstream reverse proxy is filtering inbound traffic."
        ),
    )
    STREAMLIT_SERVER_HEADLESS: bool = Field(True, description="Streamlit headless mode")

    # ========================================================================
    # DASHBOARD AUTHENTICATION
    # ========================================================================
    # Three required fields. Missing values cause startup to fail loudly via
    # pydantic's ValidationError — the same discipline APP-01 established for
    # every required secret. Generation procedure (run once per install, then
    # copy the output into `.env`) is documented in DECISIONS.md under the
    # 2026-04-23 entry "Streamlit dashboard authentication". The short form:
    #
    #     python -c "import secrets, hashlib, getpass; \
    #       salt = secrets.token_hex(16); \
    #       pw = getpass.getpass('Password: '); \
    #       print(f'DASHBOARD_PASSWORD_SALT={salt}'); \
    #       print(f'DASHBOARD_PASSWORD_HASH={hashlib.sha256((salt + pw).encode(\"utf-8\")).hexdigest()}')"
    #
    # The stored hash is SHA-256 of ``salt || plaintext``; verification uses
    # ``hmac.compare_digest`` for constant-time comparison. Plaintext passwords
    # are never logged, never committed, and never stored outside ``.env``.
    DASHBOARD_USERNAME: str = Field(
        ..., description="Admin username for the Streamlit dashboard login wrapper"
    )
    DASHBOARD_PASSWORD_HASH: str = Field(
        ...,
        description=(
            "SHA-256 hex digest of salt || plaintext. See DECISIONS.md "
            "2026-04-23 'Streamlit dashboard authentication' for the "
            "generation + rotation procedure."
        ),
    )
    DASHBOARD_PASSWORD_SALT: str = Field(
        ...,
        description=(
            "Hex-encoded per-install salt (32 chars minimum, e.g. "
            "``secrets.token_hex(16)``). Rotate together with the hash; "
            "never reuse a salt across installs."
        ),
    )

    # ========================================================================
    # DATA RETENTION
    # ========================================================================
    MESSAGE_BODY_RETENTION_DAYS: int = Field(90, description="Days to keep message bodies")
    WAITLIST_RETENTION_DAYS: int = Field(180, description="Days to keep inactive waitlist")

    # ========================================================================
    # RATE LIMITING
    # ========================================================================
    MAX_SMS_PER_HOUR: int = Field(100, description="Max SMS per hour")
    API_RATE_LIMIT: int = Field(60, description="API requests per minute")

    # ========================================================================
    # SCHEDULER
    # ========================================================================
    HOLD_TIMER_CHECK_INTERVAL: int = Field(30, description="Hold timer check interval (seconds)")
    PRIORITY_RECALC_INTERVAL: int = Field(60, description="Priority recalc interval (minutes)")

    # ========================================================================
    # MONITORING (optional)
    # ========================================================================
    SLACK_WEBHOOK_URL: str | None = Field(None, description="Slack webhook for alerts")
    ALERT_EMAIL: str | None = Field(None, description="Email for alerts")
    SMTP_HOST: str | None = Field(None, description="SMTP host")
    SMTP_PORT: int = Field(587, description="SMTP port")
    SMTP_USER: str | None = Field(None, description="SMTP username")
    SMTP_PASSWORD: str | None = Field(None, description="SMTP password")
    SMTP_USE_TLS: bool = Field(True, description="Use TLS for SMTP")

    # ========================================================================
    # EXTERNAL INTEGRATIONS (future)
    # ========================================================================
    GREENWAY_API_URL: str | None = Field(None, description="Greenway API URL")
    GREENWAY_API_KEY: str | None = Field(None, description="Greenway API key")
    PROVIDER_DB_URL: str | None = Field(None, description="Provider database URL")

    # ========================================================================
    # FEATURE FLAGS
    # ========================================================================
    ENABLE_SMS_SENDING: bool = Field(True, description="Enable SMS sending")
    ENABLE_WEBHOOKS: bool = Field(True, description="Enable webhooks")
    ENABLE_AUTO_CONFIRMATION: bool = Field(True, description="Enable auto confirmation")
    ENABLE_PRIORITY_RECALC: bool = Field(True, description="Enable priority recalc")

    # ========================================================================
    # DEVELOPMENT
    # ========================================================================
    USE_MOCK_TWILIO: bool = Field(False, description="Use mock Twilio client")
    SEED_TEST_DATA: bool = Field(False, description="Seed test data on startup")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    def get_cors_origins(self) -> list[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    def get_contact_hours(self) -> tuple[int, int]:
        """
        Parse contact hours start and end times.

        Returns:
            tuple: (start_hour, end_hour) as integers (0-23)
        """
        start_parts = self.CONTACT_HOURS_START.split(":")
        end_parts = self.CONTACT_HOURS_END.split(":")

        start_hour = int(start_parts[0])
        end_hour = int(end_parts[0])

        return start_hour, end_hour


def _format_missing_error(exc: ValidationError) -> str:
    """
    Build a human-readable error summary for missing required settings.

    Args:
        exc: The pydantic ``ValidationError`` raised when instantiating
            :class:`Settings`.

    Returns:
        A multi-line string listing the missing required env vars and
        pointing the reader at ``.env.example``.
    """
    missing = [str(err["loc"][0]) for err in exc.errors() if err.get("type") == "missing"]
    lines = ["Configuration error: cannot start application."]
    if missing:
        lines.append("Missing required environment variables: " + ", ".join(missing))
    lines.append("See .env.example at the repository root for the full list of keys.")
    return "\n".join(lines)


def validate_settings() -> "Settings":
    """
    Explicitly validate application settings.

    Intended to be called from the FastAPI lifespan startup hook so that
    configuration validation is an explicit, logged step rather than a
    side effect of module import. Returns the validated :class:`Settings`
    instance. If any required environment variable is missing or invalid,
    raises :class:`pydantic.ValidationError` after logging a clean,
    operator-friendly error message.

    Returns:
        Settings: A freshly validated settings instance.

    Raises:
        pydantic.ValidationError: If any required setting is missing or
            fails validation.
    """
    try:
        return Settings()
    except ValidationError as exc:
        message = _format_missing_error(exc)
        missing_keys = [str(err["loc"][0]) for err in exc.errors() if err.get("type") == "missing"]
        logger.error(
            "settings.validation_failed",
            missing_required=missing_keys,
            message=message,
        )
        # Also write to stderr so the failure is visible even before
        # logging handlers are fully configured.
        sys.stderr.write("\n" + message + "\n\n")
        raise


# Global settings instance. Instantiation happens at import time so that
# any missing required configuration fails loudly as early as possible.
# The explicit validate_settings() call in the FastAPI lifespan hook is
# the audit-visible startup gate; this module-level instance exists for
# backward compatibility with existing ``from app.infra.settings import settings``
# call sites.
try:
    settings: "Settings" = Settings()
except ValidationError as _exc:
    sys.stderr.write("\n" + _format_missing_error(_exc) + "\n\n")
    raise
