#!/usr/bin/env python3
"""
Simulate SMS Response - Test patient acceptance workflow

Simulates a patient replying YES/NO to an offer.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.infra.db import get_session
from app.core.orchestrator import OfferOrchestrator
from app.infra.models import MessageLog, MessageDirection, MessageStatus
from utils.time_utils import now_utc


def simulate_response(from_phone: str, response: str):
    """Simulate patient SMS response"""
    
    print(f"📱 Simulating SMS response...\n")
    print(f"   From: {from_phone}")
    print(f"   Message: {response}\n")
    
    with get_session() as db:
        orchestrator = OfferOrchestrator(db)
        
        # Log incoming message
        msg_log = MessageLog(
            direction=MessageDirection.INBOUND,
            from_phone=from_phone,
            to_phone="+18173919877",
            body=response,
            status=MessageStatus.RECEIVED,
            received_at=now_utc()
        )
        db.add(msg_log)
        db.commit()
        
        print(f"✅ Logged inbound message (ID: {msg_log.id})\n")
        
        # Process response
        if response.upper().strip() == "YES":
            print("🔄 Processing YES response...\n")
            success, reply = orchestrator.handle_patient_acceptance(from_phone, response)
            
            if success:
                print("✅ SUCCESS! Slot claimed!")
                print(f"\n📨 Confirmation message sent:")
                print(f"   '{reply}'\n")
                
                # Show database state
                from app.infra.models import CancellationEvent, Offer
                cancel = db.query(CancellationEvent).filter_by(id=14).first()
                offer = db.query(Offer).filter_by(id=46).first()
                
                print("📊 Database State:")
                print(f"   Cancellation Status: {cancel.status}")
                print(f"   Filled By Patient: {cancel.filled_by_patient_id}")
                print(f"   Offer State: {offer.state}")
                print(f"   Accepted At: {offer.accepted_at}")
                
            else:
                print(f"❌ Failed: {reply}\n")
                
        elif response.upper().strip() == "NO":
            print("🔄 Processing NO response...\n")
            success, reply = orchestrator.handle_patient_decline(from_phone, response)
            print(f"✅ Acknowledged: '{reply}'\n")
            
            from app.infra.models import Offer
            offer = db.query(Offer).filter_by(id=46).first()
            print(f"📊 Offer State: {offer.state}")
            
        else:
            print(f"⚠️  Unrecognized response: {response}")


if __name__ == "__main__":
    # Default to Jonathan's number and YES
    phone = sys.argv[1] if len(sys.argv) > 1 else "+18177743563"
    response = sys.argv[2] if len(sys.argv) > 2 else "YES"
    
    simulate_response(phone, response)
