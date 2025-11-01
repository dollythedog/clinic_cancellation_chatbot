"""
Clinic Cancellation Chatbot - FastAPI Main Application

Entry point for the FastAPI backend service.
Handles SMS webhooks, admin API, and orchestration logic.

Author: Jonathan Ives (@dollythedog)
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.infra.settings import settings
from app.infra.db import check_db_connection
from app.core.scheduler import init_scheduler, shutdown_scheduler
from app.api.admin import router as admin_router
from app.api.sms_webhook import router as sms_router
from app.api.status_webhook import router as status_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup/shutdown events.
    """
    # Startup
    logger.info("🚀 Starting Clinic Cancellation Chatbot...")
    
    # Check database connection
    if check_db_connection():
        logger.info("✅ Database connection successful")
    else:
        logger.error("❌ Database connection failed")
    
    # Initialize scheduler
    init_scheduler()
    logger.info("✅ Scheduler initialized")
    
    logger.info("✅ Application started successfully")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down application...")
    
    # Shutdown scheduler
    shutdown_scheduler()
    
    logger.info("✅ Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Clinic Cancellation Chatbot",
    description="Automated SMS-based waitlist management for appointment cancellations",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.
    """
    return {
        "status": "healthy",
        "service": "clinic-cancellation-chatbot",
        "version": "0.1.0"
    }


@app.get("/")
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "message": "Clinic Cancellation Chatbot API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health"
    }


# Include API routers
app.include_router(admin_router)  # Prefix: /admin
app.include_router(sms_router)    # Prefix: /sms
app.include_router(status_router) # Prefix: /twilio

logger.info("✅ API routers registered")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
