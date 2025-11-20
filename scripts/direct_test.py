#!/usr/bin/env python3
"""
Direct Test - Bypass API and test orchestration directly

This bypasses the FastAPI layer to test orchestration directly.
"""
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.infra.db import get_session
from app.infra.models import CancellationEvent, CancellationStatus
from app.core.orchestrator import OfferOrchestrator
from utils.time_utils import now_utc
import pytz

def main():
    print("🧪 Running direct orchestration test...\n")
    
    try:
        with get_session() as db:
            # Calculate tomorrow at 2 PM Central
            central = pytz.timezone('America/Chicago')
            tomorrow_2pm = datetime.now(central) + timedelta(days=1)
            tomorrow_2pm = tomorrow_2pm.replace(hour=14, minute=0, second=0, microsecond=0)
            slot_start_utc = tomorrow_2pm.astimezone(pytz.UTC)
            slot_end_utc = slot_start_utc + timedelta(minutes=30)
            
            print(f"📅 Slot Time: {tomorrow_2pm.strftime('%A, %B %d at %I:%M %p %Z')}\n")
            
            # Create cancellation
            cancellation = CancellationEvent(
                provider_id=14,
                location="Test Location",
                slot_start_at=slot_start_utc,
                slot_end_at=slot_end_utc,
                reason="Direct test",
                status=CancellationStatus.OPEN
            )
            
            db.add(cancellation)
            db.commit()
            db.refresh(cancellation)
            
            print(f"✅ Cancellation created: ID={cancellation.id}")
            
            # Run orchestrator
            print("\n📨 Running orchestrator...")
            orchestrator = OfferOrchestrator(db)
            offers_sent = orchestrator.process_new_cancellation(cancellation.id)
            
            print(f"\n✅ Orchestration complete!")
            print(f"   Offers sent: {offers_sent}")
            print(f"\n📱 CHECK YOUR PHONE for SMS from +18173919877")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
