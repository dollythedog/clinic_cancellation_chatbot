"""
Status Webhook - Handle Twilio delivery status callbacks

This endpoint receives delivery status updates from Twilio for outbound messages.
Updates message_log records with delivery status, error codes, etc.

Author: Jonathan Ives (@dollythedog)
"""

import structlog
from fastapi import APIRouter, Depends, Form, Request, Response
from sqlalchemy.orm import Session

from app.infra.db import get_db_dependency
from app.infra.models import MessageLog
from app.infra.twilio_client import _mask_phone
from utils.time_utils import now_utc

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/twilio", tags=["Twilio Webhooks"])


@router.post("/status")
async def handle_status_callback(
    request: Request,
    MessageSid: str = Form(...),
    MessageStatus: str = Form(...),
    ErrorCode: str | None = Form(None),
    ErrorMessage: str | None = Form(None),
    To: str | None = Form(None),
    From: str | None = Form(None),
    db: Session = Depends(get_db_dependency),
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
    logger.info(
        "twilio.status_callback.received",
        message_sid=MessageSid,
        twilio_status=MessageStatus,
        outcome="received",
    )

    # Find message log by Twilio SID
    message_log = db.query(MessageLog).filter_by(twilio_sid=MessageSid).first()

    if not message_log:
        logger.warning(
            "twilio.status_callback.sid_not_found",
            message_sid=MessageSid,
            outcome="sid_not_found",
        )
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
            logger.info(
                "twilio.status_callback.delivered",
                message_sid=MessageSid,
                to_phone_mask=_mask_phone(To) if To else "<unknown>",
                outcome="delivered",
            )

        # Log errors
        if ErrorCode:
            message_log.error_code = int(ErrorCode)
            message_log.error_message = ErrorMessage
            logger.error(
                "twilio.status_callback.failed",
                message_sid=MessageSid,
                twilio_error_code=int(ErrorCode),
                twilio_error_message=ErrorMessage,
                outcome="failed",
            )

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
        logger.warning(
            "twilio.status_callback.unknown_status",
            message_sid=MessageSid,
            twilio_status=MessageStatus,
            outcome="unknown_status",
        )

    return Response(content="OK", status_code=200)


@router.get("/status/health")
async def status_webhook_health():
    """Health check for status webhook endpoint"""
    return {"status": "healthy", "endpoint": "status_webhook"}
