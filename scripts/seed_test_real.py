#!/usr/bin/env python3
"""
Seed Real Test Data - Testing with Jonathan and Kylie's phone numbers

Creates:
- 1 test provider (Dr. Test Provider)
- 2 patients (Jonathan and Kylie) on waitlist
- Ready to create test cancellation

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
    CancellationEvent, CancellationStatus
)
from app.core.prioritizer import calculate_priority_score
from utils.time_utils import now_utc, to_utc


def clear_existing_data(db):
    """Clear all existing data"""
    print("🗑️  Clearing existing data...")
    from app.infra.models import MessageLog, Offer
    db.query(MessageLog).delete()
    db.query(Offer).delete()
    db.query(CancellationEvent).delete()
    db.query(WaitlistEntry).delete()
    db.query(PatientContact).delete()
    db.query(ProviderReference).delete()
    db.commit()
    print("✅ Existing data cleared")


def seed_test_provider(db):
    """Create test provider"""
    print("\n👨‍⚕️ Creating test provider...")
    
    provider = ProviderReference(
        provider_name="Dr. Test Provider",
        provider_type="MD/DO",
        active=True,
        tags=["Test", "Clinic"]
    )
    
    db.add(provider)
    db.commit()
    print(f"✅ Created provider: {provider.provider_name}")
    return provider


def seed_test_patients(db):
    """Create Jonathan and Kylie as test patients"""
    print("\n👥 Creating test patients...")
    
    now = now_utc()
    
    # Jonathan
    jonathan = PatientContact(
        phone_e164="+18177743563",
        display_name="Jonathan I.",
        consent_source="test",
        opt_out=False
    )
    db.add(jonathan)
    db.flush()
    
    jonathan_waitlist = WaitlistEntry(
        patient_id=jonathan.id,
        urgent_flag=True,
        manual_boost=20,
        current_appt_at=now + timedelta(days=60),
        provider_type_preference="Any",
        active=True,
        joined_at=now - timedelta(days=5),
        notes="Test patient - Jonathan"
    )
    jonathan_waitlist.priority_score = calculate_priority_score(jonathan_waitlist)
    db.add(jonathan_waitlist)
    
    # Kylie
    kylie = PatientContact(
        phone_e164="+18178887746",
        display_name="Kylie I.",
        consent_source="test",
        opt_out=False
    )
    db.add(kylie)
    db.flush()
    
    kylie_waitlist = WaitlistEntry(
        patient_id=kylie.id,
        urgent_flag=False,
        manual_boost=10,
        current_appt_at=now + timedelta(days=90),
        provider_type_preference="Any",
        active=True,
        joined_at=now - timedelta(days=3),
        notes="Test patient - Kylie"
    )
    kylie_waitlist.priority_score = calculate_priority_score(kylie_waitlist)
    db.add(kylie_waitlist)
    
    db.commit()
    
    print(f"✅ Created patient: Jonathan (+18177743563) - Priority: {jonathan_waitlist.priority_score}")
    print(f"✅ Created patient: Kylie (+18178887746) - Priority: {kylie_waitlist.priority_score}")
    
    return [jonathan, kylie]


def main():
    """Main seed function"""
    print("🌱 Starting test database seed...\n")
    
    try:
        with get_session() as db:
            # Clear existing data
            clear_existing_data(db)
            
            # Seed test data
            provider = seed_test_provider(db)
            patients = seed_test_patients(db)
            
            print("\n" + "="*60)
            print("✅ Test database seeded successfully!")
            print("="*60)
            print("\nSummary:")
            print(f"  • Provider: Dr. Test Provider (ID: {provider.id})")
            print(f"  • Jonathan: +18177743563")
            print(f"  • Kylie: +18178887746")
            print("\n📋 Next Steps:")
            print("  1. Start the API: make run-api")
            print("  2. Create a test cancellation via API")
            print("  3. Check your phone for SMS!")
            
    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
