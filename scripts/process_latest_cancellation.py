#!/usr/bin/env python3
"""
Process Latest Cancellation - Send offers for the most recent open cancellation

This script finds the most recent OPEN cancellation and sends offers to waitlist.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.infra.db import get_session
from app.infra.models import CancellationEvent, CancellationStatus
from app.core.orchestrator import OfferOrchestrator
from sqlalchemy import desc

def main():
    print("🔍 Finding latest open cancellation...\n")
    
    try:
        with get_session() as db:
            # Get most recent OPEN cancellation
            cancellation = db.query(CancellationEvent).filter(
                CancellationEvent.status == CancellationStatus.OPEN
            ).order_by(desc(CancellationEvent.created_at)).first()
            
            if not cancellation:
                print("❌ No open cancellations found")
                sys.exit(1)
            
            provider_name = cancellation.provider.provider_name if cancellation.provider else "Unknown"
            print(f"✅ Found cancellation:")
            print(f"   ID: {cancellation.id}")
            print(f"   Provider: {provider_name}")
            print(f"   Location: {cancellation.location}")
            print(f"   Slot: {cancellation.slot_start_at}")
            
            # Run orchestrator
            print(f"\n📨 Sending offers to waitlist...")
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
