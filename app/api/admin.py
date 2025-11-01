"""
Admin API - Endpoints for staff to manage cancellations and waitlist

Includes:
- Manual cancellation entry
- Waitlist management
- Provider management

Author: Jonathan Ives (@dollythedog)
"""

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.orchestrator import OfferOrchestrator
from app.core.prioritizer import boost_patient_priority, update_all_priority_scores
from app.infra.db import get_db_dependency
from app.infra.models import (
    CancellationEvent,
    CancellationStatus,
    PatientContact,
    ProviderReference,
    WaitlistEntry,
)
from utils.time_utils import now_utc, to_utc

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["Admin"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================


class CancellationCreate(BaseModel):
    """Request model for creating a cancellation"""
    provider_id: Optional[int] = Field(None, description="Provider ID")
    location: str = Field(..., description="Clinic location")
    slot_start_at: datetime = Field(..., description="Appointment start time")
    slot_end_at: datetime = Field(..., description="Appointment end time")
    reason: Optional[str] = Field(None, description="Cancellation reason")
    notes: Optional[str] = Field(None, description="Staff notes")
    created_by_staff_id: Optional[int] = Field(None, description="Staff member ID")


class CancellationResponse(BaseModel):
    """Response model for cancellation"""
    id: int
    provider_id: Optional[int]
    location: str
    slot_start_at: datetime
    slot_end_at: datetime
    status: str
    offers_sent: int
    created_at: datetime

    class Config:
        from_attributes = True


class WaitlistEntryCreate(BaseModel):
    """Request model for adding patient to waitlist"""
    patient_phone: str = Field(..., description="Patient phone (E.164)")
    patient_name: Optional[str] = Field(None, description="Patient display name")
    provider_preference: Optional[List[str]] = Field(None, description="Preferred providers")
    provider_type_preference: Optional[str] = Field("Any", description="Provider type preference")
    current_appt_at: Optional[datetime] = Field(None, description="Current appointment date")
    urgent_flag: bool = Field(False, description="Urgent priority")
    manual_boost: int = Field(0, description="Manual boost (0-40)")
    notes: Optional[str] = Field(None, description="Notes")


class PatientBoost(BaseModel):
    """Request model for boosting patient priority"""
    boost_amount: int = Field(..., ge=0, le=40, description="Boost amount (0-40)")
    reason: Optional[str] = Field(None, description="Reason for boost")


# ============================================================================
# CANCELLATION ENDPOINTS
# ============================================================================


@router.post("/cancel", response_model=CancellationResponse, status_code=status.HTTP_201_CREATED)
async def create_cancellation(
    cancellation: CancellationCreate,
    db: Session = Depends(get_db_dependency)
):
    """
    Create a new cancellation event and trigger offer orchestration.
    
    This endpoint should be called by staff when a patient cancels an appointment.
    The system will automatically send offers to eligible waitlist patients.
    
    Args:
        cancellation: Cancellation details
        db: Database session
        
    Returns:
        Created cancellation event
        
    Example:
        POST /admin/cancel
        {
            "provider_id": 1,
            "location": "Main Clinic",
            "slot_start_at": "2025-11-05T14:00:00Z",
            "slot_end_at": "2025-11-05T14:30:00Z",
            "reason": "Patient called to cancel",
            "created_by_staff_id": 1
        }
    """
    logger.info(f"Creating cancellation: {cancellation.location} at {cancellation.slot_start_at}")
    
    # Validate times
    if cancellation.slot_end_at <= cancellation.slot_start_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="slot_end_at must be after slot_start_at"
        )
    
    # Validate provider exists if provided
    if cancellation.provider_id:
        provider = db.query(ProviderReference).filter_by(id=cancellation.provider_id).first()
        if not provider:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Provider {cancellation.provider_id} not found"
            )
    
    # Create cancellation event
    event = CancellationEvent(
        provider_id=cancellation.provider_id,
        location=cancellation.location,
        slot_start_at=cancellation.slot_start_at,
        slot_end_at=cancellation.slot_end_at,
        reason=cancellation.reason,
        notes=cancellation.notes,
        created_by_staff_id=cancellation.created_by_staff_id,
        status=CancellationStatus.OPEN
    )
    
    db.add(event)
    db.commit()
    db.refresh(event)
    
    logger.info(f"✅ Cancellation {event.id} created")
    
    # Trigger offer orchestration
    orchestrator = OfferOrchestrator(db)
    offers_sent = orchestrator.process_new_cancellation(event.id)
    
    logger.info(f"📨 Sent {offers_sent} initial offers for cancellation {event.id}")
    
    return CancellationResponse(
        id=event.id,
        provider_id=event.provider_id,
        location=event.location,
        slot_start_at=event.slot_start_at,
        slot_end_at=event.slot_end_at,
        status=event.status.value,
        offers_sent=offers_sent,
        created_at=event.created_at
    )


@router.get("/cancellations/active")
async def get_active_cancellations(db: Session = Depends(get_db_dependency)):
    """Get all active (open) cancellations"""
    cancellations = (
        db.query(CancellationEvent)
        .filter(CancellationEvent.status == CancellationStatus.OPEN)
        .order_by(CancellationEvent.slot_start_at.asc())
        .all()
    )
    
    return {
        "count": len(cancellations),
        "cancellations": [
            {
                "id": c.id,
                "location": c.location,
                "slot_start_at": c.slot_start_at,
                "provider_name": c.provider.provider_name if c.provider else None,
                "created_at": c.created_at,
            }
            for c in cancellations
        ]
    }


# ============================================================================
# WAITLIST ENDPOINTS
# ============================================================================


@router.post("/waitlist", status_code=status.HTTP_201_CREATED)
async def add_to_waitlist(
    entry: WaitlistEntryCreate,
    db: Session = Depends(get_db_dependency)
):
    """
    Add a patient to the waitlist.
    
    Args:
        entry: Waitlist entry details
        db: Database session
        
    Returns:
        Created waitlist entry
    """
    # Find or create patient
    patient = db.query(PatientContact).filter_by(phone_e164=entry.patient_phone).first()
    
    if not patient:
        patient = PatientContact(
            phone_e164=entry.patient_phone,
            display_name=entry.patient_name,
            consent_source="staff_entry"
        )
        db.add(patient)
        db.flush()
        logger.info(f"Created new patient: {patient.id}")
    
    # Check if already on waitlist
    existing = (
        db.query(WaitlistEntry)
        .filter_by(patient_id=patient.id, active=True)
        .first()
    )
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Patient already on active waitlist (entry ID: {existing.id})"
        )
    
    # Create waitlist entry
    waitlist_entry = WaitlistEntry(
        patient_id=patient.id,
        provider_preference=entry.provider_preference,
        provider_type_preference=entry.provider_type_preference,
        current_appt_at=entry.current_appt_at,
        urgent_flag=entry.urgent_flag,
        manual_boost=entry.manual_boost,
        notes=entry.notes,
        active=True
    )
    
    db.add(waitlist_entry)
    db.commit()
    db.refresh(waitlist_entry)
    
    # Calculate initial priority score
    from app.core.prioritizer import update_priority_score
    update_priority_score(waitlist_entry, db)
    db.commit()
    
    logger.info(f"✅ Added patient {patient.id} to waitlist (entry {waitlist_entry.id})")
    
    return {
        "id": waitlist_entry.id,
        "patient_id": patient.id,
        "patient_phone": patient.phone_e164,
        "priority_score": waitlist_entry.priority_score,
        "joined_at": waitlist_entry.joined_at
    }


@router.post("/waitlist/{patient_id}/boost")
async def boost_priority(
    patient_id: int,
    boost: PatientBoost,
    db: Session = Depends(get_db_dependency)
):
    """
    Manually boost a patient's priority on the waitlist.
    
    Args:
        patient_id: Patient ID
        boost: Boost details
        db: Database session
        
    Returns:
        Updated waitlist entry
    """
    entry = boost_patient_priority(
        session=db,
        patient_id=patient_id,
        boost_amount=boost.boost_amount,
        reason=boost.reason
    )
    
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Active waitlist entry not found for patient {patient_id}"
        )
    
    db.commit()
    
    logger.info(f"✅ Boosted patient {patient_id} priority to {entry.priority_score}")
    
    return {
        "patient_id": patient_id,
        "manual_boost": entry.manual_boost,
        "priority_score": entry.priority_score,
        "reason": boost.reason
    }


@router.post("/waitlist/recalculate-priorities")
async def recalculate_priorities(db: Session = Depends(get_db_dependency)):
    """
    Recalculate priority scores for all active waitlist entries.
    
    This is called periodically by the scheduler but can be manually triggered.
    """
    count = update_all_priority_scores(db, active_only=True)
    db.commit()
    
    logger.info(f"✅ Recalculated {count} priority scores")
    
    return {
        "updated_count": count,
        "timestamp": now_utc()
    }


@router.get("/waitlist")
async def get_waitlist(
    limit: int = 50,
    db: Session = Depends(get_db_dependency)
):
    """Get prioritized waitlist (top patients)"""
    from app.core.prioritizer import get_prioritized_waitlist
    
    entries = get_prioritized_waitlist(db, limit=limit, active_only=True)
    
    return {
        "count": len(entries),
        "entries": [
            {
                "id": e.id,
                "patient_id": e.patient_id,
                "patient_name": e.patient.display_name,
                "patient_phone": e.patient.phone_e164,
                "priority_score": e.priority_score,
                "urgent_flag": e.urgent_flag,
                "manual_boost": e.manual_boost,
                "joined_at": e.joined_at,
            }
            for e in entries
        ]
    }


# ============================================================================
# HEALTH CHECK
# ============================================================================


@router.get("/health")
async def admin_health():
    """Health check for admin API"""
    return {"status": "healthy", "endpoint": "admin"}
