"""
Test All Messages Script - Send all SMS templates to NTFY for review

This script sends all programmed SMS message templates to your NTFY channel
so you can review them on your phone.

Author: Jonathan Ives (@dollythedog)
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from datetime import datetime, timezone, timedelta
from app.core.templates import (
    format_initial_offer,
    format_acceptance_winner,
    format_acceptance_too_late,
    format_decline_response,
    format_help_response,
    format_stop_response,
    format_cancellation_notification,
    format_error_response,
    format_welcome_message
)
from app.infra.twilio_client import TwilioClient
from app.infra.settings import settings

def main():
    """Send all message templates to NTFY for review."""
    
    print("=" * 70)
    print("📱 TPCCC Message Template Review")
    print("=" * 70)
    print()
    
    # Check if mock mode is enabled
    if not settings.USE_MOCK_TWILIO:
        print("⚠️  WARNING: USE_MOCK_TWILIO is False!")
        print("This script should only run in mock mode to avoid real SMS charges.")
        response = input("Continue anyway? (yes/no): ")
        if response.lower() != "yes":
            print("Aborted.")
            return
    
    # Check if NTFY is configured
    if not settings.SLACK_WEBHOOK_URL:
        print("❌ ERROR: SLACK_WEBHOOK_URL is not configured in .env")
        print("Add this line to your .env file:")
        print("SLACK_WEBHOOK_URL=https://ntfy.sh/your-topic-name")
        return
    
    print(f"✅ Mock mode enabled: {settings.USE_MOCK_TWILIO}")
    print(f"✅ NTFY webhook: {settings.SLACK_WEBHOOK_URL}")
    print()
    
    # Initialize client
    client = TwilioClient(use_mock=True)
    
    # Test phone number
    test_phone = "+12145551234"
    
    # Sample data for templates
    tomorrow_2pm = datetime.now(timezone.utc) + timedelta(days=1, hours=14)
    future_appt = datetime.now(timezone.utc) + timedelta(days=30, hours=10)
    
    messages = [
        {
            "name": "0. Welcome to Waitlist",
            "body": format_welcome_message(
                patient_name="John",
                current_appt_date=future_appt
            ),
            "notes": "Sent when patient is added to waitlist (subscription message)"
        },
        {
            "name": "1. Initial Offer",
            "body": format_initial_offer(
                slot_time=tomorrow_2pm,
                location="Main Clinic",
                provider_name="Dr. McDonald",
                hold_minutes=7
            ),
            "notes": "First message patients receive when a slot opens"
        },
        {
            "name": "2. Acceptance - Winner",
            "body": format_acceptance_winner(
                slot_time=tomorrow_2pm,
                location="Main Clinic",
                provider_name="Dr. McDonald"
            ),
            "notes": "Patient successfully claimed the slot"
        },
        {
            "name": "3. Acceptance - Too Late",
            "body": format_acceptance_too_late(),
            "notes": "Patient said YES but someone else got it first"
        },
        {
            "name": "4. Decline Response",
            "body": format_decline_response(),
            "notes": "Patient said NO to the offer"
        },
        {
            "name": "5. Cancellation Notification",
            "body": format_cancellation_notification(offer_id=123),
            "notes": "Slot filled by another patient while offer was pending"
        },
        {
            "name": "6. HELP Response",
            "body": format_help_response(),
            "notes": "Automatic response when patient texts HELP"
        },
        {
            "name": "7. STOP Response",
            "body": format_stop_response(),
            "notes": "Opt-out confirmation (required by TCPA)"
        },
        {
            "name": "8. Error Response",
            "body": format_error_response(),
            "notes": "Unrecognized message from patient"
        }
    ]
    
    print("Sending messages to NTFY...")
    print()
    
    for i, msg in enumerate(messages, 1):
        print(f"[{i}/{len(messages)}] {msg['name']}")
        print(f"    Notes: {msg['notes']}")
        print(f"    Length: {len(msg['body'])} characters")
        
        try:
            # Send via mock client (will go to NTFY)
            sid = client.send_sms(
                to=test_phone,
                body=f"[{msg['name']}]\n\n{msg['body']}\n\n---\nNotes: {msg['notes']}"
            )
            print(f"    ✅ Sent (SID: {sid})")
        except Exception as e:
            print(f"    ❌ Error: {e}")
        
        print()
    
    print("=" * 70)
    print("✅ All messages sent!")
    print()
    print("Check your NTFY app or web interface:")
    print(f"   {settings.SLACK_WEBHOOK_URL.replace('https://', 'https://ntfy.sh/')}")
    print()
    print("💬 What do you think of the messages?")
    print("   - Are they clear and professional?")
    print("   - Are they too long or too short?")
    print("   - Do they include all necessary info?")
    print("   - Do they feel urgent without being pushy?")
    print()
    print("Let me know your feedback and I'll adjust them!")
    print("=" * 70)


if __name__ == "__main__":
    main()
