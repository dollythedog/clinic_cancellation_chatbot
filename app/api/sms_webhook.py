"""
SMS Webhook - Handle incoming SMS messages from Twilio

This endpoint receives inbound SMS from patients via Twilio and processes:
- YES/NO responses to offers
- STOP keyword (opt-out)
- HELP keyword

Author: Jonathan Ives (@dollythedog)
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, Form, Request, Response, status
from sqlalchemy.orm import Session

from app.core.orchestrator import OfferOrchestrator
from app.core.templates import (
    format_error_response,
    format_help_response,
    format_stop_response,
    parse_patient_response,
)
from app.infra.db import get_db_dependency
from app.infra.models import MessageDirection, MessageLog, MessageStatus, PatientContact
from app.infra.twilio_client import twilio_client
from utils.time_utils import now_utc

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sms", tags=["SMS Webhooks"])


@router.post("/inbound")
async def handle_inbound_sms(
    request: Request,
    From: str = Form(...),
    To: str = Form(...),
    Body: str = Form(...),
    MessageSid: Optional[str] = Form(None),
    db: Session = Depends(get_db_dependency)
):
    """
    Handle inbound SMS from Twilio.
    
    This endpoint is called by Twilio when a patient sends an SMS.
    
    Args:
        From: Patient phone number (E.164)
        To: Our Twilio number
        Body: SMS message body
        MessageSid: Twilio message SID
        db: Database session
        
    Returns:
        TwiML response (empty for now)
        
    Twilio Webhook Documentation:
    https://www.twilio.com/docs/sms/twiml
    """
    from_phone = From
    to_phone = To
    message_body = Body.strip()
    
    logger.info(f"📩 Inbound SMS from {from_phone}: {message_body}")
    
    # Log inbound message
    log_entry = MessageLog(
        offer_id=None,  # Will be associated later if applicable
        direction=MessageDirection.INBOUND,
        from_phone=from_phone,
        to_phone=to_phone,
        body=message_body,
        twilio_sid=MessageSid,
        status=MessageStatus.RECEIVED,
        received_at=now_utc()
    )
    db.add(log_entry)
    db.commit()
    
    # Parse patient response
    action = parse_patient_response(message_body)
    
    # Handle STOP keyword (opt-out)
    if action == "STOP":
        return handle_opt_out(from_phone, db)
    
    # Handle HELP keyword
    if action == "HELP":
        return handle_help_request(from_phone, db)
    
    # Handle YES response
    if action == "YES":
        return handle_yes_response(from_phone, message_body, db)
    
    # Handle NO response
    if action == "NO":
        return handle_no_response(from_phone, message_body, db)
    
    # Unknown message - send error response
    logger.warning(f"Unknown message from {from_phone}: {message_body}")
    response_text = format_error_response()
    
    try:
        twilio_client.send_sms(to=from_phone, body=response_text)
    except Exception as e:
        logger.error(f"Failed to send error response to {from_phone}: {e}")
    
    # Return empty TwiML response
    return Response(
        content='<?xml version="1.0" encoding="UTF-8"?><Response></Response>',
        media_type="application/xml"
    )


def handle_opt_out(from_phone: str, db: Session) -> Response:
    """
    Handle STOP keyword - mark patient as opted out.
    
    TCPA Compliance: STOP must immediately opt patient out.
    """
    logger.info(f"🛑 STOP received from {from_phone}")
    
    # Find or create patient
    patient = db.query(PatientContact).filter_by(phone_e164=from_phone).first()
    
    if patient:
        patient.opt_out = True
        db.commit()
        logger.info(f"Patient {patient.id} opted out")
    else:
        # Create patient record with opt-out flag
        patient = PatientContact(
            phone_e164=from_phone,
            opt_out=True,
            consent_source="opt-out"
        )
        db.add(patient)
        db.commit()
        logger.info(f"Created opted-out patient record for {from_phone}")
    
    # Send confirmation
    response_text = format_stop_response()
    
    try:
        twilio_client.send_sms(to=from_phone, body=response_text)
        
        # Log outbound message
        log_entry = MessageLog(
            direction=MessageDirection.OUTBOUND,
            from_phone=To,  # Our number
            to_phone=from_phone,
            body=response_text,
            status=MessageStatus.SENT,
            sent_at=now_utc()
        )
        db.add(log_entry)
        db.commit()
        
    except Exception as e:
        logger.error(f"Failed to send STOP confirmation to {from_phone}: {e}")
    
    return Response(
        content='<?xml version="1.0" encoding="UTF-8"?><Response></Response>',
        media_type="application/xml"
    )


def handle_help_request(from_phone: str, db: Session) -> Response:
    """Handle HELP keyword - send instructions"""
    logger.info(f"❓ HELP received from {from_phone}")
    
    response_text = format_help_response()
    
    try:
        twilio_client.send_sms(to=from_phone, body=response_text)
        
        # Log outbound message
        log_entry = MessageLog(
            direction=MessageDirection.OUTBOUND,
            from_phone=To,  # Our number
            to_phone=from_phone,
            body=response_text,
            status=MessageStatus.SENT,
            sent_at=now_utc()
        )
        db.add(log_entry)
        db.commit()
        
    except Exception as e:
        logger.error(f"Failed to send HELP response to {from_phone}: {e}")
    
    return Response(
        content='<?xml version="1.0" encoding="UTF-8"?><Response></Response>',
        media_type="application/xml"
    )


def handle_yes_response(from_phone: str, message_body: str, db: Session) -> Response:
    """Handle YES response - attempt to claim slot"""
    logger.info(f"✅ YES received from {from_phone}")
    
    orchestrator = OfferOrchestrator(db)
    success, response_text = orchestrator.handle_patient_acceptance(from_phone, message_body)
    
    if success:
        logger.info(f"🎉 Slot successfully claimed by {from_phone}")
    else:
        logger.info(f"❌ Slot claim failed for {from_phone}: {response_text}")
    
    # Response already sent by orchestrator
    return Response(
        content='<?xml version="1.0" encoding="UTF-8"?><Response></Response>',
        media_type="application/xml"
    )


def handle_no_response(from_phone: str, message_body: str, db: Session) -> Response:
    """Handle NO response - decline offer"""
    logger.info(f"❌ NO received from {from_phone}")
    
    orchestrator = OfferOrchestrator(db)
    success, response_text = orchestrator.handle_patient_decline(from_phone, message_body)
    
    # Send response
    try:
        twilio_client.send_sms(to=from_phone, body=response_text)
        
        # Log outbound message
        log_entry = MessageLog(
            direction=MessageDirection.OUTBOUND,
            from_phone=To,  # Our number
            to_phone=from_phone,
            body=response_text,
            status=MessageStatus.SENT,
            sent_at=now_utc()
        )
        db.add(log_entry)
        db.commit()
        
    except Exception as e:
        logger.error(f"Failed to send NO confirmation to {from_phone}: {e}")
    
    return Response(
        content='<?xml version="1.0" encoding="UTF-8"?><Response></Response>',
        media_type="application/xml"
    )
