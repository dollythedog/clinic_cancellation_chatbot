#!/usr/bin/env python3
"""
Create Test Cancellation - Trigger SMS workflow for testing

This script creates a test cancellation for tomorrow at 2:00 PM
and triggers the orchestration workflow.

Author: Jonathan Ives (@dollythedog)
"""
import sys
import os
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests
import pytz
from utils.time_utils import now_utc


def create_test_cancellation():
    """Create a test cancellation via API"""
    
    print("🏥 Creating test cancellation...\n")
    
    # Calculate tomorrow at 2:00 PM Central Time
    central = pytz.timezone('America/Chicago')
    tomorrow_2pm = datetime.now(central) + timedelta(days=1)
    tomorrow_2pm = tomorrow_2pm.replace(hour=14, minute=0, second=0, microsecond=0)
    
    # Convert to UTC for API
    slot_start_utc = tomorrow_2pm.astimezone(pytz.UTC)
    slot_end_utc = slot_start_utc + timedelta(minutes=30)
    
    print(f"📅 Slot Time (Central): {tomorrow_2pm.strftime('%A, %B %d at %I:%M %p %Z')}")
    print(f"📅 Slot Time (UTC): {slot_start_utc.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print()
    
    # Prepare API request
    api_url = "http://localhost:8000/admin/cancel"
    payload = {
        "provider_id": 14,  # Dr. Test Provider (from seed script)
        "location": "Test Location",
        "slot_start_at": slot_start_utc.isoformat(),
        "slot_end_at": slot_end_utc.isoformat(),
        "reason": "Test cancellation for SMS verification"
    }
    
    try:
        print("📤 Sending request to API...")
        response = requests.post(api_url, json=payload, timeout=10)
        
        print(f"📥 Response Status: {response.status_code}\n")
        
        if response.status_code in [200, 201]:
            data = response.json()
            print("✅ Cancellation created successfully!")
            print()
            print(f"   Cancellation ID: {data.get('cancellation_id')}")
            print(f"   Offers Sent: {data.get('offers_sent')}")
            print(f"   Message: {data.get('message')}")
            print()
            print("📱 Check your phone for SMS!")
            print("   Expected recipient: Jonathan (+18177743563)")
            print("   Expected message format:")
            print("      'TPCCC: An earlier appointment opened tomorrow at 2:00 PM CT")
            print("       at Test Location. Reply YES to claim or NO to skip.")
            print("       This offer expires in 30 min.'")
            print()
            print("🔍 Next Steps:")
            print("   1. Check backend logs for: 'Offer sent to patient'")
            print("   2. Verify SMS received on phone")
            print("   3. Reply YES/NO to test workflow")
            print("   4. Check database to verify state changes")
            
        else:
            print(f"❌ Error creating cancellation:")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error!")
        print("   Is the FastAPI backend running?")
        print("   Start it with: make run-api")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    create_test_cancellation()
