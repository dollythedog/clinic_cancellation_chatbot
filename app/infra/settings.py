"""
Settings - Application configuration from environment variables

This module loads configuration from environment variables (.env file).
Uses Pydantic for type validation and defaults.

Author: Jonathan Ives (@dollythedog)
"""

import os
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    See configs/.env.example for all available settings and descriptions.
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
    TWILIO_MESSAGING_SERVICE_SID: Optional[str] = Field(None, description="Twilio Messaging Service SID")
    TWILIO_WEBHOOK_BASE_URL: Optional[str] = Field(None, description="Public webhook base URL")
    TWILIO_WEBHOOK_SECRET: Optional[str] = Field(None, description="Webhook signature secret")
    
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
    API_KEY: Optional[str] = Field(None, description="API key for admin endpoints")
    JWT_SECRET: Optional[str] = Field(None, description="JWT secret for sessions")
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
    STREAMLIT_SERVER_ADDRESS: str = Field("0.0.0.0", description="Streamlit host")
    STREAMLIT_SERVER_HEADLESS: bool = Field(True, description="Streamlit headless mode")
    
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
    SLACK_WEBHOOK_URL: Optional[str] = Field(None, description="Slack webhook for alerts")
    ALERT_EMAIL: Optional[str] = Field(None, description="Email for alerts")
    SMTP_HOST: Optional[str] = Field(None, description="SMTP host")
    SMTP_PORT: int = Field(587, description="SMTP port")
    SMTP_USER: Optional[str] = Field(None, description="SMTP username")
    SMTP_PASSWORD: Optional[str] = Field(None, description="SMTP password")
    SMTP_USE_TLS: bool = Field(True, description="Use TLS for SMTP")
    
    # ========================================================================
    # EXTERNAL INTEGRATIONS (future)
    # ========================================================================
    GREENWAY_API_URL: Optional[str] = Field(None, description="Greenway API URL")
    GREENWAY_API_KEY: Optional[str] = Field(None, description="Greenway API key")
    PROVIDER_DB_URL: Optional[str] = Field(None, description="Provider database URL")
    
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
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # Allow extra fields from .env
    
    def get_cors_origins(self) -> List[str]:
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


# Global settings instance
settings = Settings()
