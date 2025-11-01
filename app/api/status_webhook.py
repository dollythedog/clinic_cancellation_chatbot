"""
Status Webhook - Handle Twilio delivery status callbacks

This endpoint receives delivery status updates from Twilio for outbound messages.
Updates message_log records with delivery status, error codes, etc.

Author: Jonathan Ives (@dollythedog)
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, Form, Request, Response
from sqlalchemy.orm import Session

from app.infra.db import get_db_dependency
from app.infra.models import MessageLog, MessageStatus
from utils.time_utils import now_utc

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/twilio", tags=["Twilio Webhooks"])


@router.post("/status")
async def handle_status_callback(
    request: Request,
    MessageSid: str = Form(...),
    MessageStatus: str = Form(...),
    ErrorCode: Optional[str] = Form(None),
    ErrorMessage: Optional[str] = Form(None),
    To: Optional[str] = Form(None),
    From: Optional[str] = Form(None),
    db: Session = Depends(get_db_dependency)
):
    """
    Handle Twilio delivery status callbacks.
    
    Twilio sends this webhook when message status changes:
    - queued: Message accepted by Twilio
    - sent: Message sent to carrier
    - delivered: Message delivered to device
    - undelivered: Message failed to deliver
    - failed: Message send failed
    
    Args:
        MessageSid: Twilio message SID
        MessageStatus: Current status
        ErrorCode: Error code if failed
        ErrorMessage: Error message if failed
        To: Recipient phone
        From: Sender phone
        db: Database session
        
    Returns:
        Empty response
        
    Twilio Documentation:
    https://www.twilio.com/docs/sms/tutorials/how-to-confirm-delivery-python
    """
    logger.info(f"📊 Status callback: {MessageSid} -> {MessageStatus}")
    
    # Find message log by Twilio SID
    message_log = db.query(MessageLog).filter_by(twilio_sid=MessageSid).first()
    
    if not message_log:
        logger.warning(f"Message log not found for SID: {MessageSid}")
        # Still return success to Twilio
        return Response(content="OK", status_code=200)
    
    # Map Twilio status to our enum
    status_mapping = {
        "queued": MessageStatus.QUEUED,
        "sent": MessageStatus.SENT,
        "delivered": MessageStatus.DELIVERED,
        "undelivered": MessageStatus.UNDELIVERED,
        "failed": MessageStatus.FAILED,
    }
    
    new_status = status_mapping.get(MessageStatus.lower())
    
    if new_status:
        message_log.status = new_status
        
        # Update delivered_at timestamp
        if new_status == MessageStatus.DELIVERED:
            message_log.delivered_at = now_utc()
            logger.info(f"✅ Message {MessageSid} delivered to {To}")
        
        # Log errors
        if ErrorCode:
            message_log.error_code = int(ErrorCode)
            message_log.error_message = ErrorMessage
            logger.error(f"❌ Message {MessageSid} failed: {ErrorCode} - {ErrorMessage}")
        
        # Store raw metadata
        if not message_log.raw_meta:
            message_log.raw_meta = {}
        
        message_log.raw_meta["last_status_update"] = {
            "status": MessageStatus,
            "timestamp": now_utc().isoformat(),
            "error_code": ErrorCode,
            "error_message": ErrorMessage,
            "to": To,
            "from": From,
        }
        
        db.commit()
    else:
        logger.warning(f"Unknown status: {MessageStatus} for SID {MessageSid}")
    
    return Response(content="OK", status_code=200)


@router.get("/status/health")
async def status_webhook_health():
    """Health check for status webhook endpoint"""
    return {"status": "healthy", "endpoint": "status_webhook"}
