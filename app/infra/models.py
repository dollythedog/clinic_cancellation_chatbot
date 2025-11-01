"""
ORM Models - SQLAlchemy models for Clinic Cancellation Chatbot

This module defines all database tables as SQLAlchemy ORM models, including:
- patient_contact
- provider_reference
- waitlist_entry
- cancellation_event
- offer
- message_log
- staff_user

All timestamps are stored in UTC. Use utils.time_utils for timezone conversions.

Author: Jonathan Ives (@dollythedog)
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID as PG_UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

# Base class for all models
Base = declarative_base()

# ============================================================================
# ENUMS
# ============================================================================

import enum


class CancellationStatus(str, enum.Enum):
    """Status of a cancellation event"""
    OPEN = "open"
    FILLED = "filled"
    EXPIRED = "expired"
    ABORTED = "aborted"


class OfferState(str, enum.Enum):
    """State of an individual offer"""
    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"
    EXPIRED = "expired"
    CANCELED = "canceled"
    FAILED = "failed"


class MessageDirection(str, enum.Enum):
    """Direction of SMS message"""
    OUTBOUND = "outbound"
    INBOUND = "inbound"


class MessageStatus(str, enum.Enum):
    """Twilio message delivery status"""
    QUEUED = "queued"
    SENT = "sent"
    DELIVERED = "delivered"
    UNDELIVERED = "undelivered"
    FAILED = "failed"
    RECEIVED = "received"


# ============================================================================
# MODELS
# ============================================================================


class PatientContact(Base):
    """
    Minimal patient contact information for SMS communication.
    
    HIPAA Note: Store only essential data, no diagnoses or full medical records.
    """
    __tablename__ = "patient_contact"

    id = Column(Integer, primary_key=True)
    phone_e164 = Column(Text, nullable=False, unique=True, index=True)
    display_name = Column(Text)
    last_contacted_at = Column(DateTime(timezone=True))
    opt_out = Column(Boolean, default=False, nullable=False)
    consent_source = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    waitlist_entries = relationship("WaitlistEntry", back_populates="patient", cascade="all, delete-orphan")
    offers = relationship("Offer", back_populates="patient", cascade="all, delete-orphan")
    filled_cancellations = relationship("CancellationEvent", back_populates="filled_by_patient", foreign_keys="CancellationEvent.filled_by_patient_id")

    def __repr__(self):
        return f"<PatientContact(id={self.id}, phone={self.phone_e164}, opt_out={self.opt_out})>"


class ProviderReference(Base):
    """
    Provider information for matching appointments to waitlist preferences.
    Can link to existing TPCCC provider database via external_provider_id.
    """
    __tablename__ = "provider_reference"

    id = Column(Integer, primary_key=True)
    provider_name = Column(Text, nullable=False)
    provider_type = Column(Text, nullable=False, index=True)
    active = Column(Boolean, default=True, nullable=False)
    external_provider_id = Column(Text)
    tags = Column(ARRAY(Text))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    cancellation_events = relationship("CancellationEvent", back_populates="provider")

    def __repr__(self):
        return f"<ProviderReference(id={self.id}, name={self.provider_name}, type={self.provider_type})>"


class WaitlistEntry(Base):
    """
    Active waitlist entries with priority scoring and provider preferences.
    Priority score is recalculated periodically based on urgency, seniority, and appointment distance.
    """
    __tablename__ = "waitlist_entry"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patient_contact.id", ondelete="CASCADE"), nullable=False, index=True)
    provider_preference = Column(ARRAY(Text))
    provider_type_preference = Column(Text)
    current_appt_at = Column(DateTime(timezone=True))
    urgent_flag = Column(Boolean, default=False, nullable=False)
    manual_boost = Column(Integer, default=0, nullable=False)
    active = Column(Boolean, default=True, nullable=False)
    joined_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    priority_score = Column(Integer)
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Constraints
    __table_args__ = (
        CheckConstraint("manual_boost BETWEEN 0 AND 40", name="check_manual_boost_range"),
    )

    # Relationships
    patient = relationship("PatientContact", back_populates="waitlist_entries")

    def __repr__(self):
        return f"<WaitlistEntry(id={self.id}, patient_id={self.patient_id}, priority={self.priority_score}, active={self.active})>"


class CancellationEvent(Base):
    """
    Tracks canceled appointment slots and their fill status.
    Triggers offer orchestration when created.
    """
    __tablename__ = "cancellation_event"

    id = Column(Integer, primary_key=True)
    provider_id = Column(Integer, ForeignKey("provider_reference.id", ondelete="SET NULL"), index=True)
    location = Column(Text, nullable=False)
    slot_start_at = Column(DateTime(timezone=True), nullable=False, index=True)
    slot_end_at = Column(DateTime(timezone=True), nullable=False)
    reason = Column(Text)
    status = Column(Enum(CancellationStatus, name="cancellation_status"), default=CancellationStatus.OPEN, nullable=False, index=True)
    notes = Column(Text)
    created_by_staff_id = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    filled_at = Column(DateTime(timezone=True))
    filled_by_patient_id = Column(Integer, ForeignKey("patient_contact.id", ondelete="SET NULL"))

    # Constraints
    __table_args__ = (
        CheckConstraint("slot_end_at > slot_start_at", name="valid_slot_times"),
    )

    # Relationships
    provider = relationship("ProviderReference", back_populates="cancellation_events")
    offers = relationship("Offer", back_populates="cancellation", cascade="all, delete-orphan")
    filled_by_patient = relationship("PatientContact", back_populates="filled_cancellations", foreign_keys=[filled_by_patient_id])

    def __repr__(self):
        return f"<CancellationEvent(id={self.id}, status={self.status}, slot_start={self.slot_start_at})>"


class Offer(Base):
    """
    Individual SMS offers sent to waitlist patients.
    Tracks batch number, hold timers, and response status.
    Uses lock_token for race-safe confirmation (SELECT FOR UPDATE).
    """
    __tablename__ = "offer"

    id = Column(Integer, primary_key=True)
    cancellation_id = Column(Integer, ForeignKey("cancellation_event.id", ondelete="CASCADE"), nullable=False, index=True)
    patient_id = Column(Integer, ForeignKey("patient_contact.id", ondelete="CASCADE"), nullable=False, index=True)
    batch_number = Column(Integer, nullable=False)
    offer_sent_at = Column(DateTime(timezone=True))
    hold_expires_at = Column(DateTime(timezone=True), index=True)
    state = Column(Enum(OfferState, name="offer_state"), default=OfferState.PENDING, nullable=False, index=True)
    lock_token = Column(PG_UUID(as_uuid=True), default=uuid4, nullable=False, unique=True)
    accepted_at = Column(DateTime(timezone=True))
    declined_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    cancellation = relationship("CancellationEvent", back_populates="offers")
    patient = relationship("PatientContact", back_populates="offers")
    messages = relationship("MessageLog", back_populates="offer")

    def __repr__(self):
        return f"<Offer(id={self.id}, state={self.state}, batch={self.batch_number}, patient_id={self.patient_id})>"


class MessageLog(Base):
    """
    Complete audit trail of all SMS messages (inbound and outbound).
    Stores Twilio delivery status and raw webhook payloads.
    
    HIPAA Note: Avoid including PHI in message bodies.
    """
    __tablename__ = "message_log"

    id = Column(Integer, primary_key=True)
    offer_id = Column(Integer, ForeignKey("offer.id", ondelete="SET NULL"), index=True)
    direction = Column(Enum(MessageDirection, name="message_direction"), nullable=False, index=True)
    from_phone = Column(Text, nullable=False, index=True)
    to_phone = Column(Text, nullable=False, index=True)
    body = Column(Text, nullable=False)
    twilio_sid = Column(Text, index=True)
    status = Column(Enum(MessageStatus, name="message_status"))
    error_code = Column(Integer)
    error_message = Column(Text)
    received_at = Column(DateTime(timezone=True))
    sent_at = Column(DateTime(timezone=True))
    delivered_at = Column(DateTime(timezone=True))
    raw_meta = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Relationships
    offer = relationship("Offer", back_populates="messages")

    def __repr__(self):
        return f"<MessageLog(id={self.id}, direction={self.direction}, status={self.status}, twilio_sid={self.twilio_sid})>"


class StaffUser(Base):
    """
    Staff users for admin dashboard access.
    Future: Add authentication and role-based access control.
    """
    __tablename__ = "staff_user"

    id = Column(Integer, primary_key=True)
    email = Column(Text, nullable=False, unique=True, index=True)
    role = Column(Text, default="staff", nullable=False)
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<StaffUser(id={self.id}, email={self.email}, role={self.role})>"


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def create_all_tables(engine):
    """
    Create all tables defined in this module.
    
    Args:
        engine: SQLAlchemy engine instance
        
    Example:
        >>> from sqlalchemy import create_engine
        >>> engine = create_engine("postgresql://...")
        >>> create_all_tables(engine)
    """
    Base.metadata.create_all(bind=engine)


def drop_all_tables(engine):
    """
    Drop all tables defined in this module.
    
    WARNING: This will delete all data!
    
    Args:
        engine: SQLAlchemy engine instance
    """
    Base.metadata.drop_all(bind=engine)
