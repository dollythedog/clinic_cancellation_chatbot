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

# from app.infra.settings import settings
# from app.infra.db import init_db, close_db
# from app.api import cancellations, sms_webhook, status_webhook, waitlist_api

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
    logger.info("Starting Clinic Cancellation Chatbot...")
    # await init_db()
    logger.info("Application started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    # await close_db()
    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Clinic Cancellation Chatbot",
    description="Automated SMS-based waitlist management for appointment cancellations",
    version="0.1.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://localhost:3000"],  # Streamlit + dev
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


# TODO: Include routers when implemented
# app.include_router(cancellations.router, prefix="/api/cancellations", tags=["cancellations"])
# app.include_router(sms_webhook.router, prefix="/sms", tags=["sms"])
# app.include_router(status_webhook.router, prefix="/twilio", tags=["twilio"])
# app.include_router(waitlist_api.router, prefix="/api/waitlist", tags=["waitlist"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
