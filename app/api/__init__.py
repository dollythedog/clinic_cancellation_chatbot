"""API endpoints"""

from app.api.admin import router as admin_router
from app.api.sms_webhook import router as sms_router
from app.api.status_webhook import router as status_router

__all__ = [
    "admin_router",
    "sms_router",
    "status_router",
]