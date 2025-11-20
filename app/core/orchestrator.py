"""
Orchestrator - Core offer management logic

This module coordinates the entire cancellation offer workflow:
- Send offers in batches (3 patients at a time)
- Manage hold timers (7-minute windows)
- Handle acceptances/declines
- Prevent race conditions with SELECT FOR UPDATE
- Track message delivery

Author: Jonathan Ives (@dollythedog)
"""

import logging
from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.core.prioritizer import get_eligible_patients_for_cancellation
from app.core.templates import format_initial_offer, format_acceptance_winner, format_acceptance_too_late, format_cancellation_notification
from app.infra.models import (
    CancellationEvent,
    CancellationStatus,
    MessageDirection,
    MessageLog,
    MessageStatus,
    Offer,
    OfferState,
    PatientContact,
    WaitlistEntry,
)
from app.infra.settings import settings
from app.infra.twilio_client import twilio_client
from utils.time_utils import add_minutes, now_utc

logger = logging.getLogger(__name__)


class OfferOrchestrator:
    """
    Manages the entire offer lifecycle for cancellation events.
    
    Responsibilities:
    - Send offers in batches
    - Track hold timers
    - Handle patient responses
    - Ensure race-safe slot claiming
    """
    
    def __init__(self, session: Session):
        """
        Initialize orchestrator with database session.
        
        Args:
            session: SQLAlchemy session
        """
        self.session = session
        self.batch_size = settings.BATCH_SIZE
        self.hold_minutes = settings.HOLD_MINUTES
    
    def process_new_cancellation(self, cancellation_id: int) -> int:
        """
        Process a new cancellation event by sending initial batch of offers.
        
        Args:
            cancellation_id: ID of cancellation event
            
        Returns:
            int: Number of offers sent
            
        Example:
            >>> orchestrator = OfferOrchestrator(session)
            >>> count = orchestrator.process_new_cancellation(123)
            >>> print(f"Sent {count} offers")
        """
        cancellation = self.session.query(CancellationEvent).filter_by(id=cancellation_id).first()
        
        if not cancellation:
            logger.error(f"Cancellation {cancellation_id} not found")
            return 0
        
        if cancellation.status != CancellationStatus.OPEN:
            logger.warning(f"Cancellation {cancellation_id} is not open (status: {cancellation.status})")
            return 0
        
        logger.info(f"Processing new cancellation {cancellation_id}")
        
        # Send first batch
        return self.send_next_batch(cancellation_id)
    
    def send_next_batch(self, cancellation_id: int) -> int:
        """
        Send the next batch of offers for a cancellation.
        
        Args:
            cancellation_id: ID of cancellation event
            
        Returns:
            int: Number of offers sent
        """
        cancellation = self.session.query(CancellationEvent).filter_by(id=cancellation_id).first()
        
        if not cancellation or cancellation.status != CancellationStatus.OPEN:
            return 0
        
        # Determine next batch number
        existing_offers = self.session.query(Offer).filter_by(cancellation_id=cancellation_id).all()
        current_batch = max([o.batch_number for o in existing_offers], default=0) + 1
        
        # Get patients already offered
        already_offered_patient_ids = [o.patient_id for o in existing_offers]
        
        # Get eligible patients
        eligible_entries = get_eligible_patients_for_cancellation(
            self.session,
            cancellation_id=cancellation_id,
            provider_id=cancellation.provider_id,
            provider_type=cancellation.provider.provider_type if cancellation.provider else None,
            limit=self.batch_size,
            exclude_patient_ids=already_offered_patient_ids
        )
        
        if not eligible_entries:
            logger.info(f"No more eligible patients for cancellation {cancellation_id}")
            self._mark_cancellation_expired(cancellation_id)
            return 0
        
        logger.info(f"Sending batch {current_batch} ({len(eligible_entries)} offers) for cancellation {cancellation_id}")
        
        # Create offers and send SMS
        count = 0
        now = now_utc()
        hold_expires_at = add_minutes(now, self.hold_minutes)
        
        for entry in eligible_entries:
            patient = entry.patient
            
            # Create offer record
            offer = Offer(
                cancellation_id=cancellation_id,
                patient_id=patient.id,
                batch_number=current_batch,
                offer_sent_at=now,
                hold_expires_at=hold_expires_at,
                state=OfferState.PENDING
            )
            self.session.add(offer)
            self.session.flush()  # Get offer ID
            
            # Format SMS message
            provider_name = cancellation.provider.provider_name if cancellation.provider else "Provider"
            message_body = format_initial_offer(
                slot_time=cancellation.slot_start_at,
                location=cancellation.location,
                provider_name=provider_name,
                hold_minutes=self.hold_minutes
            )
            
            # Send SMS
            try:
                status_callback = self._get_status_callback_url() if settings.TWILIO_WEBHOOK_BASE_URL else None
                
                twilio_sid = twilio_client.send_sms(
                    to=patient.phone_e164,
                    body=message_body,
                    status_callback=status_callback
                )
                
                # Log outbound message
                self._log_message(
                    offer_id=offer.id,
                    direction=MessageDirection.OUTBOUND,
                    from_phone=settings.TWILIO_PHONE_NUMBER,
                    to_phone=patient.phone_e164,
                    body=message_body,
                    twilio_sid=twilio_sid,
                    status=MessageStatus.SENT
                )
                
                # Update patient last_contacted_at
                patient.last_contacted_at = now
                
                count += 1
                logger.info(f"Offer {offer.id} sent to patient {patient.id} ({patient.phone_e164})")
                
            except Exception as e:
                logger.error(f"Failed to send offer to patient {patient.id}: {e}")
                offer.state = OfferState.FAILED
        
        self.session.commit()
        return count
    
    def handle_patient_acceptance(self, from_phone: str, message_body: str) -> Tuple[bool, str]:
        """
        Handle a YES response from a patient.
        
        Uses SELECT FOR UPDATE to prevent race conditions.
        
        Args:
            from_phone: Patient phone number (E.164)
            message_body: SMS body for logging
            
        Returns:
            tuple: (success: bool, response_message: str)
        """
        # Find patient
        patient = self.session.query(PatientContact).filter_by(phone_e164=from_phone).first()
        
        if not patient:
            logger.warning(f"Received YES from unknown number: {from_phone}")
            return False, "Patient not found"
        
        # Find active pending offer for this patient
        # Use SELECT FOR UPDATE to lock the row
        offer = (
            self.session.query(Offer)
            .filter(
                and_(
                    Offer.patient_id == patient.id,
                    Offer.state == OfferState.PENDING
                )
            )
            .order_by(Offer.offer_sent_at.desc())
            .with_for_update()  # Race-safe locking
            .first()
        )
        
        if not offer:
            logger.warning(f"No pending offer found for patient {patient.id}")
            return False, "No active offer"
        
        # Check if offer has expired
        if now_utc() > offer.hold_expires_at:
            logger.info(f"Offer {offer.id} expired for patient {patient.id}")
            offer.state = OfferState.EXPIRED
            self.session.commit()
            return False, "Offer expired"
        
        # Load cancellation with lock
        cancellation = (
            self.session.query(CancellationEvent)
            .filter_by(id=offer.cancellation_id)
            .with_for_update()
            .first()
        )
        
        # Check if slot is still available
        if cancellation.status != CancellationStatus.OPEN:
            logger.info(f"Slot {cancellation.id} no longer available")
            offer.state = OfferState.CANCELED
            self.session.commit()
            
            # Send "too late" message
            response = format_acceptance_too_late()
            twilio_client.send_sms(to=from_phone, body=response)
            self._log_message(
                offer_id=offer.id,
                direction=MessageDirection.OUTBOUND,
                from_phone=settings.TWILIO_PHONE_NUMBER,
                to_phone=from_phone,
                body=response,
                status=MessageStatus.SENT
            )
            
            return False, response
        
        # SUCCESS - Claim the slot!
        now = now_utc()
        offer.state = OfferState.ACCEPTED
        offer.accepted_at = now
        
        cancellation.status = CancellationStatus.FILLED
        cancellation.filled_at = now
        cancellation.filled_by_patient_id = patient.id
        
        self.session.commit()
        
        logger.info(f"✅ Patient {patient.id} claimed slot {cancellation.id}")
        
        # Send confirmation message
        provider_name = cancellation.provider.provider_name if cancellation.provider else "Provider"
        response = format_acceptance_winner(
            slot_time=cancellation.slot_start_at,
            location=cancellation.location,
            provider_name=provider_name
        )
        twilio_client.send_sms(to=from_phone, body=response)
        self._log_message(
            offer_id=offer.id,
            direction=MessageDirection.OUTBOUND,
            from_phone=settings.TWILIO_PHONE_NUMBER,
            to_phone=from_phone,
            body=response,
            status=MessageStatus.SENT
        )
        
        # Cancel other pending offers for this cancellation
        self._cancel_other_offers(cancellation.id, winning_offer_id=offer.id)
        
        return True, response
    
    def handle_patient_decline(self, from_phone: str, message_body: str) -> Tuple[bool, str]:
        """
        Handle a NO response from a patient.
        
        Args:
            from_phone: Patient phone number (E.164)
            message_body: SMS body for logging
            
        Returns:
            tuple: (success: bool, response_message: str)
        """
        patient = self.session.query(PatientContact).filter_by(phone_e164=from_phone).first()
        
        if not patient:
            return False, "Patient not found"
        
        # Find active pending offer
        offer = (
            self.session.query(Offer)
            .filter(
                and_(
                    Offer.patient_id == patient.id,
                    Offer.state == OfferState.PENDING
                )
            )
            .order_by(Offer.offer_sent_at.desc())
            .first()
        )
        
        if offer:
            cancellation_id = offer.cancellation_id
            offer.state = OfferState.DECLINED
            offer.declined_at = now_utc()
            self.session.commit()
            logger.info(f"Patient {patient.id} declined offer {offer.id}")
            
            # Check if all offers in current batch are resolved
            cancellation = self.session.query(CancellationEvent).filter_by(id=cancellation_id).first()
            if cancellation and cancellation.status == CancellationStatus.OPEN:
                current_batch = max([o.batch_number for o in cancellation.offers])
                current_batch_offers = [o for o in cancellation.offers if o.batch_number == current_batch]
                
                all_resolved = all(
                    o.state in [OfferState.ACCEPTED, OfferState.DECLINED, OfferState.EXPIRED]
                    for o in current_batch_offers
                )
                
                # If all offers in batch are resolved, immediately send next batch
                if all_resolved:
                    logger.info(f"All offers in batch {current_batch} resolved, sending next batch immediately")
                    offers_sent = self.send_next_batch(cancellation_id)
                    if offers_sent > 0:
                        logger.info(f"Sent {offers_sent} offer(s) in next batch")
        
        from app.core.templates import format_decline_response
        response = format_decline_response()
        
        return True, response
    
    def check_expired_holds(self) -> int:
        """
        Check for expired hold timers and trigger next batch.
        
        This should be called periodically by the scheduler.
        
        Returns:
            int: Number of batches sent
        """
        now = now_utc()
        
        # Find cancellations with expired pending offers
        expired_offers = (
            self.session.query(Offer)
            .filter(
                and_(
                    Offer.state == OfferState.PENDING,
                    Offer.hold_expires_at <= now
                )
            )
            .all()
        )
        
        if not expired_offers:
            return 0
        
        # Mark expired offers
        for offer in expired_offers:
            offer.state = OfferState.EXPIRED
            logger.info(f"Offer {offer.id} expired")
        
        self.session.commit()
        
        # Get unique cancellation IDs with expired offers
        cancellation_ids = set(o.cancellation_id for o in expired_offers)
        
        # Send next batch for each cancellation
        batches_sent = 0
        for cancellation_id in cancellation_ids:
            cancellation = self.session.query(CancellationEvent).filter_by(id=cancellation_id).first()
            
            if cancellation and cancellation.status == CancellationStatus.OPEN:
                # Check if all offers in current batch have responded or expired
                current_batch = max([o.batch_number for o in cancellation.offers])
                current_batch_offers = [o for o in cancellation.offers if o.batch_number == current_batch]
                
                all_resolved = all(
                    o.state in [OfferState.ACCEPTED, OfferState.DECLINED, OfferState.EXPIRED]
                    for o in current_batch_offers
                )
                
                if all_resolved:
                    count = self.send_next_batch(cancellation_id)
                    if count > 0:
                        batches_sent += 1
        
        return batches_sent
    
    def _cancel_other_offers(self, cancellation_id: int, winning_offer_id: int):
        """Cancel all other pending offers for a cancellation"""
        other_offers = (
            self.session.query(Offer)
            .filter(
                and_(
                    Offer.cancellation_id == cancellation_id,
                    Offer.id != winning_offer_id,
                    Offer.state == OfferState.PENDING
                )
            )
            .all()
        )
        
        for offer in other_offers:
            offer.state = OfferState.CANCELED
            
            # Send notification SMS
            patient = offer.patient
            message = format_cancellation_notification(offer.id)
            
            try:
                twilio_client.send_sms(to=patient.phone_e164, body=message)
                self._log_message(
                    offer_id=offer.id,
                    direction=MessageDirection.OUTBOUND,
                    from_phone=settings.TWILIO_PHONE_NUMBER,
                    to_phone=patient.phone_e164,
                    body=message,
                    status=MessageStatus.SENT
                )
            except Exception as e:
                logger.error(f"Failed to send cancellation notification to patient {patient.id}: {e}")
        
        self.session.commit()
    
    def _mark_cancellation_expired(self, cancellation_id: int):
        """Mark a cancellation as expired (no more eligible patients)"""
        cancellation = self.session.query(CancellationEvent).filter_by(id=cancellation_id).first()
        if cancellation:
            cancellation.status = CancellationStatus.EXPIRED
            self.session.commit()
            logger.info(f"Cancellation {cancellation_id} marked as expired")
    
    def _log_message(
        self,
        offer_id: Optional[int],
        direction: MessageDirection,
        from_phone: str,
        to_phone: str,
        body: str,
        twilio_sid: Optional[str] = None,
        status: Optional[MessageStatus] = None,
        error_code: Optional[int] = None,
        error_message: Optional[str] = None
    ):
        """Log a message to the database"""
        log = MessageLog(
            offer_id=offer_id,
            direction=direction,
            from_phone=from_phone,
            to_phone=to_phone,
            body=body,
            twilio_sid=twilio_sid,
            status=status,
            error_code=error_code,
            error_message=error_message,
            sent_at=now_utc() if direction == MessageDirection.OUTBOUND else None,
            received_at=now_utc() if direction == MessageDirection.INBOUND else None
        )
        self.session.add(log)
    
    def _get_status_callback_url(self) -> str:
        """Generate Twilio status callback URL"""
        base_url = settings.TWILIO_WEBHOOK_BASE_URL
        return f"{base_url}/twilio/status"
