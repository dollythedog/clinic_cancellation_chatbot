"""
Prioritizer - Priority score calculation for waitlist entries

This module implements the priority scoring algorithm that determines
which patients should receive cancellation offers first.

Scoring Components:
- Urgent flag: +30 points
- Manual boost: 0-40 points (admin controlled)
- Days until current appointment: 0-20 points
- Waitlist seniority: 0-10 points

Higher score = higher priority

Author: Jonathan Ives (@dollythedog)
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.infra.models import WaitlistEntry
from utils.time_utils import now_utc


def calculate_priority_score(entry: WaitlistEntry, current_time: Optional[datetime] = None) -> int:
    """
    Compute priority score for a waitlist entry.
    
    Higher score = higher priority for receiving cancellation offers.
    
    Scoring breakdown:
    - Urgent flag: +30 points
    - Manual boost: 0-40 points (staff override)
    - Days until current appointment:
        - 180+ days: +20 points
        - 90-179 days: +10 points
        - 30-89 days: +5 points
        - <30 days: 0 points
    - Waitlist seniority: +1 point per 30 days (max 10 points)
    
    Args:
        entry: WaitlistEntry ORM object
        current_time: Override current time (for testing)
        
    Returns:
        int: Priority score (0-100 range typically)
        
    Example:
        >>> entry = WaitlistEntry(
        ...     urgent_flag=True,
        ...     manual_boost=10,
        ...     current_appt_at=datetime(...),  # 6 months out
        ...     joined_at=datetime(...)  # 2 months ago
        ... )
        >>> score = calculate_priority_score(entry)
        >>> print(score)
        62  # 30 (urgent) + 10 (boost) + 20 (appt distance) + 2 (seniority)
    """
    score = 0
    now = current_time or now_utc()
    
    # Component 1: Urgent flag (+30)
    if entry.urgent_flag:
        score += 30
    
    # Component 2: Manual boost (0-40)
    score += entry.manual_boost
    
    # Component 3: Days until current appointment (0-20)
    if entry.current_appt_at:
        days_until = (entry.current_appt_at - now).days
        
        if days_until >= 180:
            score += 20
        elif days_until >= 90:
            score += 10
        elif days_until >= 30:
            score += 5
        # else: 0 points
    
    # Component 4: Waitlist seniority (0-10)
    days_on_waitlist = (now - entry.joined_at).days
    seniority_points = min(days_on_waitlist // 30, 10)
    score += seniority_points
    
    return score


def update_priority_score(entry: WaitlistEntry, session: Session, current_time: Optional[datetime] = None) -> int:
    """
    Calculate and update the priority score for a single waitlist entry.
    
    Args:
        entry: WaitlistEntry ORM object
        session: SQLAlchemy session
        current_time: Override current time (for testing)
        
    Returns:
        int: New priority score
        
    Example:
        >>> session = get_session()
        >>> entry = session.query(WaitlistEntry).filter_by(id=123).first()
        >>> new_score = update_priority_score(entry, session)
        >>> session.commit()
    """
    new_score = calculate_priority_score(entry, current_time)
    entry.priority_score = new_score
    return new_score


def update_all_priority_scores(session: Session, active_only: bool = True) -> int:
    """
    Recalculate priority scores for all waitlist entries.
    
    This should be run periodically (e.g., hourly) to keep scores current.
    
    Args:
        session: SQLAlchemy session
        active_only: Only update active entries (default: True)
        
    Returns:
        int: Number of entries updated
        
    Example:
        >>> session = get_session()
        >>> count = update_all_priority_scores(session)
        >>> session.commit()
        >>> print(f"Updated {count} waitlist entries")
    """
    query = session.query(WaitlistEntry)
    
    if active_only:
        query = query.filter(WaitlistEntry.active == True)
    
    entries = query.all()
    current_time = now_utc()
    
    for entry in entries:
        entry.priority_score = calculate_priority_score(entry, current_time)
    
    return len(entries)


def get_prioritized_waitlist(
    session: Session,
    limit: Optional[int] = None,
    active_only: bool = True,
    exclude_patient_ids: Optional[List[int]] = None,
) -> List[WaitlistEntry]:
    """
    Get waitlist entries sorted by priority score (highest first).
    
    Args:
        session: SQLAlchemy session
        limit: Maximum number of entries to return
        active_only: Only return active entries (default: True)
        exclude_patient_ids: Patient IDs to exclude (e.g., already offered)
        
    Returns:
        List[WaitlistEntry]: Sorted waitlist entries
        
    Example:
        >>> session = get_session()
        >>> top_patients = get_prioritized_waitlist(session, limit=10)
        >>> for entry in top_patients:
        ...     print(f"{entry.patient.display_name}: {entry.priority_score}")
    """
    query = session.query(WaitlistEntry)
    
    if active_only:
        query = query.filter(WaitlistEntry.active == True)
    
    if exclude_patient_ids:
        query = query.filter(WaitlistEntry.patient_id.notin_(exclude_patient_ids))
    
    # Order by priority score (highest first), then by joined_at (oldest first)
    query = query.order_by(
        WaitlistEntry.priority_score.desc().nulls_last(),
        WaitlistEntry.joined_at.asc()
    )
    
    if limit:
        query = query.limit(limit)
    
    return query.all()


def get_eligible_patients_for_cancellation(
    session: Session,
    cancellation_id: int,
    provider_id: Optional[int] = None,
    provider_type: Optional[str] = None,
    limit: Optional[int] = None,
    exclude_patient_ids: Optional[List[int]] = None,
) -> List[WaitlistEntry]:
    """
    Get eligible waitlist entries for a specific cancellation, filtered by preferences.
    
    This function applies provider matching logic:
    - If patient has provider_preference, match against provider_id
    - If patient has provider_type_preference, match against provider_type
    - If patient has "Any" preference, include them
    
    Args:
        session: SQLAlchemy session
        cancellation_id: ID of the cancellation event
        provider_id: Provider ID of the canceled appointment
        provider_type: Provider type (e.g., "MD/DO", "APP")
        limit: Maximum number of entries to return
        exclude_patient_ids: Patient IDs to exclude
        
    Returns:
        List[WaitlistEntry]: Eligible patients sorted by priority
        
    Example:
        >>> session = get_session()
        >>> eligible = get_eligible_patients_for_cancellation(
        ...     session,
        ...     cancellation_id=123,
        ...     provider_id=5,
        ...     provider_type="MD/DO",
        ...     limit=10
        ... )
    """
    from app.infra.models import ProviderReference
    
    query = session.query(WaitlistEntry).filter(WaitlistEntry.active == True)
    
    # Exclude opted-out patients
    query = query.join(WaitlistEntry.patient).filter(
        WaitlistEntry.patient.has(opt_out=False)
    )
    
    if exclude_patient_ids:
        query = query.filter(WaitlistEntry.patient_id.notin_(exclude_patient_ids))
    
    # Provider preference matching logic
    # This is simplified - in production, you might want more sophisticated matching
    if provider_id:
        provider = session.query(ProviderReference).filter_by(id=provider_id).first()
        if provider:
            # Include patients who:
            # 1. Have "Any" type preference
            # 2. Match provider type preference
            # 3. Have provider in their preference list
            # 4. Have no preferences set
            query = query.filter(
                (WaitlistEntry.provider_type_preference == "Any") |
                (WaitlistEntry.provider_type_preference == provider.provider_type) |
                (WaitlistEntry.provider_type_preference.is_(None)) |
                (WaitlistEntry.provider_preference.contains([provider.provider_name]))
            )
    
    # Order by priority
    query = query.order_by(
        WaitlistEntry.priority_score.desc().nulls_last(),
        WaitlistEntry.joined_at.asc()
    )
    
    if limit:
        query = query.limit(limit)
    
    return query.all()


def boost_patient_priority(
    session: Session,
    patient_id: int,
    boost_amount: int,
    reason: Optional[str] = None
) -> Optional[WaitlistEntry]:
    """
    Apply a manual boost to a patient's priority score.
    
    Args:
        session: SQLAlchemy session
        patient_id: Patient ID
        boost_amount: Amount to boost (0-40)
        reason: Optional reason for audit trail
        
    Returns:
        WaitlistEntry: Updated entry, or None if not found
        
    Raises:
        ValueError: If boost_amount is out of range
        
    Example:
        >>> session = get_session()
        >>> entry = boost_patient_priority(session, patient_id=123, boost_amount=20)
        >>> session.commit()
    """
    if not (0 <= boost_amount <= 40):
        raise ValueError("Boost amount must be between 0 and 40")
    
    entry = session.query(WaitlistEntry).filter(
        and_(
            WaitlistEntry.patient_id == patient_id,
            WaitlistEntry.active == True
        )
    ).first()
    
    if not entry:
        return None
    
    entry.manual_boost = boost_amount
    
    if reason:
        # Append to notes
        timestamp = now_utc().strftime("%Y-%m-%d %H:%M UTC")
        note = f"[{timestamp}] Manual boost: {boost_amount} - {reason}"
        if entry.notes:
            entry.notes += f"\n{note}"
        else:
            entry.notes = note
    
    # Recalculate priority score
    update_priority_score(entry, session)
    
    return entry
