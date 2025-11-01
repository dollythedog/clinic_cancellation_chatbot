#!/usr/bin/env python3
"""
Seed Sample Data - Populate database with test data

Creates:
- 3 providers
- 5 patients on waitlist with varying priorities
- 2 open cancellations with offers
- Sample message log entries

Author: Jonathan Ives (@dollythedog)
"""
import sys
import os
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.infra.db import get_session
from app.infra.models import (
    PatientContact, ProviderReference, WaitlistEntry,
    CancellationEvent, CancellationStatus, Offer, OfferState,
    MessageLog, MessageDirection, MessageStatus
)
from app.core.prioritizer import calculate_priority_score
from utils.time_utils import now_utc, to_utc


def clear_existing_data(db):
    """Clear all existing data"""
    print("🗑️  Clearing existing data...")
    db.query(MessageLog).delete()
    db.query(Offer).delete()
    db.query(CancellationEvent).delete()
    db.query(WaitlistEntry).delete()
    db.query(PatientContact).delete()
    db.query(ProviderReference).delete()
    db.commit()
    print("✅ Existing data cleared")


def seed_providers(db):
    """Create sample providers"""
    print("\n👨‍⚕️ Creating providers...")
    
    providers = [
        ProviderReference(
            provider_name="Dr. Sarah Smith",
            provider_type="MD/DO",
            active=True,
            tags=["Primary Care", "Clinic"]
        ),
        ProviderReference(
            provider_name="Jennifer Davis, NP",
            provider_type="APP",
            active=True,
            tags=["Primary Care", "Tele"]
        ),
        ProviderReference(
            provider_name="Dr. Michael Johnson",
            provider_type="MD/DO",
            active=True,
            tags=["Specialty", "Clinic"]
        )
    ]
    
    for provider in providers:
        db.add(provider)
    
    db.commit()
    print(f"✅ Created {len(providers)} providers")
    return providers


def seed_patients_and_waitlist(db):
    """Create sample patients and waitlist entries"""
    print("\n👥 Creating patients and waitlist...")
    
    now = now_utc()
    
    patients_data = [
        {
            "phone": "+12145551001",
            "name": "Alice J.",
            "urgent": True,
            "manual_boost": 20,
            "current_appt": now + timedelta(days=45),
            "joined_days_ago": 5,
            "notes": "Urgent - needs follow-up for lab results"
        },
        {
            "phone": "+12145551002",
            "name": "Bob K.",
            "urgent": False,
            "manual_boost": 10,
            "current_appt": now + timedelta(days=90),
            "joined_days_ago": 15,
            "notes": "Routine check-up"
        },
        {
            "phone": "+12145551003",
            "name": "Carol M.",
            "urgent": True,
            "manual_boost": 0,
            "current_appt": now + timedelta(days=60),
            "joined_days_ago": 3,
            "notes": "High priority patient"
        },
        {
            "phone": "+12145551004",
            "name": "David P.",
            "urgent": False,
            "manual_boost": 5,
            "current_appt": now + timedelta(days=120),
            "joined_days_ago": 30,
            "notes": None
        },
        {
            "phone": "+12145551005",
            "name": "Emma R.",
            "urgent": False,
            "manual_boost": 0,
            "current_appt": None,
            "joined_days_ago": 10,
            "notes": "New patient - no current appointment"
        }
    ]
    
    patients = []
    waitlist_entries = []
    
    for data in patients_data:
        # Create patient
        patient = PatientContact(
            phone_e164=data["phone"],
            display_name=data["name"],
            consent_source="manual_entry",
            opt_out=False
        )
        db.add(patient)
        db.flush()
        
        # Create waitlist entry
        joined_at = now - timedelta(days=data["joined_days_ago"])
        entry = WaitlistEntry(
            patient_id=patient.id,
            urgent_flag=data["urgent"],
            manual_boost=data["manual_boost"],
            current_appt_at=data["current_appt"],
            provider_type_preference="Any",
            active=True,
            joined_at=joined_at,
            notes=data["notes"]
        )
        
        # Calculate priority score
        entry.priority_score = calculate_priority_score(entry)
        
        db.add(entry)
        patients.append(patient)
        waitlist_entries.append(entry)
    
    db.commit()
    print(f"✅ Created {len(patients)} patients with waitlist entries")
    return patients, waitlist_entries


def seed_cancellations_and_offers(db, providers, patients):
    """Create sample cancellations with offers"""
    print("\n📅 Creating cancellations and offers...")
    
    now = now_utc()
    
    # Cancellation 1: Tomorrow afternoon with active offers
    cancel1 = CancellationEvent(
        provider_id=providers[0].id,
        location="Main Clinic",
        slot_start_at=now + timedelta(days=1, hours=2),
        slot_end_at=now + timedelta(days=1, hours=2, minutes=30),
        reason="Patient called to cancel",
        status=CancellationStatus.OPEN,
        notes="Urgent slot - try to fill quickly"
    )
    db.add(cancel1)
    db.flush()
    
    # Create offers for cancellation 1 (batch 1 - pending)
    for i in range(3):
        offer = Offer(
            cancellation_id=cancel1.id,
            patient_id=patients[i].id,
            batch_number=1,
            offer_sent_at=now - timedelta(minutes=10),
            hold_expires_at=now + timedelta(minutes=20),
            state=OfferState.PENDING
        )
        db.add(offer)
        
        # Add message log for each offer
        msg = MessageLog(
            offer_id=None,  # Will be set after flush
            direction=MessageDirection.OUTBOUND,
            from_phone="+12145550000",
            to_phone=patients[i].phone_e164,
            body=f"Appointment available tomorrow at 2:00 PM with {providers[0].provider_name}. Reply YES to claim or NO to decline.",
            status=MessageStatus.DELIVERED,
            sent_at=now - timedelta(minutes=10),
            delivered_at=now - timedelta(minutes=9)
        )
        db.add(msg)
    
    # Cancellation 2: Next week with mixed responses
    cancel2 = CancellationEvent(
        provider_id=providers[1].id,
        location="North Clinic",
        slot_start_at=now + timedelta(days=5, hours=10),
        slot_end_at=now + timedelta(days=5, hours=10, minutes=30),
        reason="Provider schedule change",
        status=CancellationStatus.OPEN,
        notes=None
    )
    db.add(cancel2)
    db.flush()
    
    # Batch 1 - all declined
    for i in range(3):
        offer = Offer(
            cancellation_id=cancel2.id,
            patient_id=patients[i].id,
            batch_number=1,
            offer_sent_at=now - timedelta(hours=2),
            hold_expires_at=now - timedelta(hours=1, minutes=30),
            state=OfferState.DECLINED,
            declined_at=now - timedelta(hours=1, minutes=45)
        )
        db.add(offer)
    
    # Batch 2 - currently pending
    if len(patients) >= 5:
        for i in range(3, 5):
            offer = Offer(
                cancellation_id=cancel2.id,
                patient_id=patients[i].id,
                batch_number=2,
                offer_sent_at=now - timedelta(minutes=5),
                hold_expires_at=now + timedelta(minutes=25),
                state=OfferState.PENDING
            )
            db.add(offer)
    
    db.commit()
    print(f"✅ Created 2 cancellations with offers")


def seed_message_log(db, patients):
    """Create sample message log entries"""
    print("\n📨 Creating message log entries...")
    
    now = now_utc()
    
    messages = [
        # Outbound offer
        MessageLog(
            direction=MessageDirection.OUTBOUND,
            from_phone="+12145550000",
            to_phone=patients[0].phone_e164,
            body="Appointment available tomorrow at 2:00 PM. Reply YES to claim.",
            status=MessageStatus.DELIVERED,
            sent_at=now - timedelta(minutes=10),
            delivered_at=now - timedelta(minutes=9)
        ),
        # Inbound response
        MessageLog(
            direction=MessageDirection.INBOUND,
            from_phone=patients[1].phone_e164,
            to_phone="+12145550000",
            body="NO",
            status=MessageStatus.RECEIVED,
            received_at=now - timedelta(minutes=5)
        ),
        # Another outbound
        MessageLog(
            direction=MessageDirection.OUTBOUND,
            from_phone="+12145550000",
            to_phone=patients[2].phone_e164,
            body="Thank you. You're still on our waitlist.",
            status=MessageStatus.DELIVERED,
            sent_at=now - timedelta(minutes=3),
            delivered_at=now - timedelta(minutes=2)
        )
    ]
    
    for msg in messages:
        db.add(msg)
    
    db.commit()
    print(f"✅ Created {len(messages)} message log entries")


def main():
    """Main seed function"""
    print("🌱 Starting database seed...\n")
    
    try:
        with get_session() as db:
            # Clear existing data
            clear_existing_data(db)
            
            # Seed all data
            providers = seed_providers(db)
            patients, waitlist_entries = seed_patients_and_waitlist(db)
            seed_cancellations_and_offers(db, providers, patients)
            seed_message_log(db, patients)
            
            print("\n" + "="*60)
            print("✅ Database seeded successfully!")
            print("="*60)
            print("\nSummary:")
            print(f"  • {len(providers)} providers")
            print(f"  • {len(patients)} patients")
            print(f"  • {len(waitlist_entries)} waitlist entries")
            print(f"  • 2 open cancellations")
            print(f"  • Multiple offers (pending and declined)")
            print(f"  • Sample message logs")
            print("\n🎉 Dashboard is ready to view!")
            print("   Run: make run-dashboard")
            
    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
