"""
SMS Webhook - Handle incoming SMS messages from Twilio

This endpoint receives inbound SMS from patients via Twilio and processes:
- YES/NO responses to offers
- STOP keyword (opt-out)
- HELP keyword

Author: Jonathan Ives (@dollythedog)
"""

import structlog
from fastapi import APIRouter, Depends, Form, Request, Response
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
from app.infra.twilio_client import _mask_phone, twilio_client
from utils.time_utils import now_utc

# PHI discipline: every structured log event on these webhook paths
# uses ``from_phone_mask`` (last-4 digits) rather than the full E.164
# number, and NEVER includes the message body. The ``message_log``
# table is the audit source of truth for the full content.
logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/sms", tags=["SMS Webhooks"])


@router.post("/inbound")
async def handle_inbound_sms(
    request: Request,
    From: str = Form(...),
    To: str = Form(...),
    Body: str = Form(...),
    MessageSid: str | None = Form(None),
    db: Session = Depends(get_db_dependency),
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

    logger.info(
        "sms.inbound.received",
        from_phone_mask=_mask_phone(from_phone),
        message_sid=MessageSid,
        body_length=len(message_body),
        outcome="received",
    )

    # Log inbound message
    log_entry = MessageLog(
        offer_id=None,  # Will be associated later if applicable
        direction=MessageDirection.INBOUND,
        from_phone=from_phone,
        to_phone=to_phone,
        body=message_body,
        twilio_sid=MessageSid,
        status=MessageStatus.RECEIVED,
        received_at=now_utc(),
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
    logger.warning(
        "sms.inbound.unparseable",
        from_phone_mask=_mask_phone(from_phone),
        message_sid=MessageSid,
        body_length=len(message_body),
        outcome="unparseable",
    )
    response_text = format_error_response()

    try:
        twilio_client.send_sms(to=from_phone, body=response_text)
    except Exception as e:
        logger.error(
            "sms.error_response.send_failed",
            from_phone_mask=_mask_phone(from_phone),
            error_type=e.__class__.__name__,
            error_message=str(e),
            outcome="send_failed",
        )

    # Return empty TwiML response
    return Response(
        content='<?xml version="1.0" encoding="UTF-8"?><Response></Response>',
        media_type="application/xml",
    )


def handle_opt_out(from_phone: str, db: Session) -> Response:
    """
    Handle STOP keyword - mark patient as opted out.

    TCPA Compliance: STOP must immediately opt patient out.
    """
    logger.info(
        "sms.opt_out.received",
        from_phone_mask=_mask_phone(from_phone),
        outcome="received",
    )

    # Find or create patient
    patient = db.query(PatientContact).filter_by(phone_e164=from_phone).first()

    if patient:
        patient.opt_out = True
        db.commit()
        logger.info(
            "sms.opt_out.patient_marked",
            patient_id=patient.id,
            from_phone_mask=_mask_phone(from_phone),
            outcome="opted_out",
        )
    else:
        # Create patient record with opt-out flag
        patient = PatientContact(phone_e164=from_phone, opt_out=True, consent_source="opt-out")
        db.add(patient)
        db.commit()
        logger.info(
            "sms.opt_out.patient_created",
            patient_id=patient.id,
            from_phone_mask=_mask_phone(from_phone),
            outcome="opted_out_new",
        )

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
            sent_at=now_utc(),
        )
        db.add(log_entry)
        db.commit()

    except Exception as e:
        logger.error(
            "sms.opt_out.confirmation_failed",
            from_phone_mask=_mask_phone(from_phone),
            error_type=e.__class__.__name__,
            error_message=str(e),
            outcome="confirmation_failed",
        )

    return Response(
        content='<?xml version="1.0" encoding="UTF-8"?><Response></Response>',
        media_type="application/xml",
    )


def handle_help_request(from_phone: str, db: Session) -> Response:
    """Handle HELP keyword - send instructions"""
    logger.info(
        "sms.help.received",
        from_phone_mask=_mask_phone(from_phone),
        outcome="received",
    )

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
            sent_at=now_utc(),
        )
        db.add(log_entry)
        db.commit()

    except Exception as e:
        logger.error(
            "sms.help.response_failed",
            from_phone_mask=_mask_phone(from_phone),
            error_type=e.__class__.__name__,
            error_message=str(e),
            outcome="response_failed",
        )

    return Response(
        content='<?xml version="1.0" encoding="UTF-8"?><Response></Response>',
        media_type="application/xml",
    )


def handle_yes_response(from_phone: str, message_body: str, db: Session) -> Response:
    """Handle YES response - attempt to claim slot"""
    logger.info(
        "sms.acceptance.received",
        from_phone_mask=_mask_phone(from_phone),
        outcome="received",
    )

    orchestrator = OfferOrchestrator(db)
    success, response_text = orchestrator.handle_patient_acceptance(from_phone, message_body)

    if success:
        logger.info(
            "sms.acceptance.claimed",
            from_phone_mask=_mask_phone(from_phone),
            outcome="claimed",
        )
    else:
        logger.info(
            "sms.acceptance.claim_failed",
            from_phone_mask=_mask_phone(from_phone),
            outcome="claim_failed",
        )

    # Response already sent by orchestrator
    return Response(
        content='<?xml version="1.0" encoding="UTF-8"?><Response></Response>',
        media_type="application/xml",
    )


def handle_no_response(from_phone: str, message_body: str, db: Session) -> Response:
    """Handle NO response - decline offer"""
    logger.info(
        "sms.decline.received",
        from_phone_mask=_mask_phone(from_phone),
        outcome="received",
    )

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
            sent_at=now_utc(),
        )
        db.add(log_entry)
        db.commit()

    except Exception as e:
        logger.error(
            "sms.decline.confirmation_failed",
            from_phone_mask=_mask_phone(from_phone),
            error_type=e.__class__.__name__,
            error_message=str(e),
            outcome="confirmation_failed",
        )

    return Response(
        content='<?xml version="1.0" encoding="UTF-8"?><Response></Response>',
        media_type="application/xml",
    )
