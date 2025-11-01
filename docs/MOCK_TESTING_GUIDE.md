# 🧪 Mock Testing Guide

**Testing the Clinic Cancellation Chatbot without real SMS**

---

## 🎯 Overview

With `USE_MOCK_TWILIO=true` in your `.env` file, you can test the entire system without sending real SMS messages. This guide shows you how to test everything including using **ntfy.sh** for push notifications!

---

## 🚀 Getting Started

### 1. Start the System

**Terminal 1 - API Backend:**
```powershell
make run-api
```
Access at: http://localhost:8000/docs

**Terminal 2 - Dashboard:**
```powershell
make run-dashboard
```
Access at: http://localhost:8502

---

## 📱 Using ntfy.sh for Notifications

**ntfy.sh** is a free, simple notification service - perfect for testing! No signup required.

### Setup ntfy.sh

1. **Choose a unique topic name** (e.g., `clinic-chatbot-jives-test-123`)
2. **Subscribe on your phone:**
   - Install ntfy app: https://ntfy.sh/app
   - Or use web: https://ntfy.sh/clinic-chatbot-jives-test-123
   
3. **Update .env to use ntfy:**
```bash
# Add this to your .env file
SLACK_WEBHOOK_URL=https://ntfy.sh/clinic-chatbot-jives-test-123
```

4. **Restart the API** to load new config

### How It Works

When the mock Twilio client "sends" an SMS, it will:
- ✅ Log to console
- ✅ Save to database (message_log table)
- ✅ **Send notification to ntfy.sh** (push notification to your phone!)

You'll get **real push notifications on your phone** for each "SMS" sent! 

**Notification Format:**
```
Title: TPCCC Mock SMS
Message: 📱 Mock SMS to +12145551001

TPCCC: An earlier appointment opened tomorrow at 10:00 AM...
```

---

## 🧪 Testing Workflow

### Step 1: Add Test Data

**Option A: Use Dashboard**
1. Go to http://localhost:8502
2. Navigate to "Admin Tools" → "Add to Waitlist"
3. Add 3 test patients:
   ```
   Patient 1: +12145551001, "Alice", urgent=true
   Patient 2: +12145551002, "Bob", manual_boost=20
   Patient 3: +12145551003, "Carol", manual_boost=10
   ```

**Option B: Use Seed Script (if available)**
```powershell
python scripts/seed_data.py
```

### Step 2: Create a Cancellation

**Via API (Swagger UI):**
1. Go to http://localhost:8000/docs
2. Find `POST /admin/cancel`
3. Click "Try it out"
4. Use this payload:
```json
{
  "provider_id": 1,
  "location": "Main Clinic",
  "slot_start_at": "2025-11-02T10:00:00-06:00",
  "slot_end_at": "2025-11-02T10:30:00-06:00",
  "reason": "Patient canceled",
  "created_by_staff_id": 1
}
```
5. Execute

**What Happens:**
- System creates cancellation
- Orchestrator selects top 3 waitlist patients
- Mock SMS sent to all 3
- You get ntfy notifications!
- Dashboard updates with offers

### Step 3: Watch the Dashboard

Go to Dashboard → "Dashboard" view to see:
- 🔴 Active cancellation
- 🟡 3 pending offers
- ⏰ Countdown timers (7 minutes)

### Step 4: Simulate Patient Response

**Simulate "YES" response:**
```powershell
curl -X POST http://localhost:8000/sms/inbound \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "From=%2B12145551001&Body=YES&To=%2B12145551234"
```

Or use Swagger UI:
1. Go to http://localhost:8000/docs
2. Find `POST /sms/inbound`
3. Body: `From=+12145551001&Body=YES`

**What Happens:**
- Offer accepted by Alice
- 🟢 Dashboard shows accepted offer
- Other offers canceled
- Winner gets confirmation "SMS"
- Cancellation marked as FILLED

### Step 5: Check Message Log

Dashboard → "Message Log":
- See all mock messages
- Filter by direction
- View message bodies
- Check timing

---

## 🎭 Mock Scenarios to Test

### Scenario 1: Happy Path
1. Create cancellation
2. Top 3 patients get offers
3. Patient responds YES
4. Slot filled
5. Others notified

### Scenario 2: No Response (Hold Timer Expires)
1. Create cancellation
2. Offers sent to batch 1 (3 patients)
3. Wait 7 minutes
4. Hold timer expires
5. Batch 2 offers sent (next 3 patients)

### Scenario 3: Multiple "YES" (Race Condition)
1. Create cancellation
2. Simulate 2 patients saying YES at same time
3. First one wins
4. Second one gets "too late" message

### Scenario 4: Urgent Patient Priority
1. Add normal patient (priority ~10)
2. Add urgent patient (priority ~40)
3. Create cancellation
4. Urgent patient gets offer first

### Scenario 5: Manual Boost
1. Patient low on waitlist
2. Admin boosts +40 points
3. Create cancellation
4. Boosted patient now in top 3

---

## 📊 Monitoring During Tests

### Console Logs
API terminal shows:
```
[INFO] Mock SMS would be sent to +12145551001
[INFO] Message: "TPCCC: An earlier appointment opened..."
```

### Database Queries
```sql
-- See all messages
SELECT * FROM message_log ORDER BY created_at DESC LIMIT 10;

-- See all offers
SELECT o.id, p.phone_e164, o.state, o.hold_expires_at
FROM offer o
JOIN patient_contact p ON o.patient_id = p.id
ORDER BY o.created_at DESC;

-- See active cancellations
SELECT * FROM cancellation_event WHERE status = 'open';
```

### ntfy.sh Web Interface
Open https://ntfy.sh/your-topic-name in browser to see message history

---

## 🔧 Advanced Testing

### Test STOP/HELP Keywords (Future)
```bash
# STOP keyword
curl -X POST http://localhost:8000/sms/inbound \
  -d "From=%2B12145551001&Body=STOP"

# HELP keyword  
curl -X POST http://localhost:8000/sms/inbound \
  -d "From=%2B12145551001&Body=HELP"
```

### Test Edge Cases
1. **Empty waitlist**: Create cancellation → should log "no eligible patients"
2. **All opted out**: Set opt_out=true for all → no offers sent
3. **Outside contact hours**: Change CONTACT_HOURS_END to past time → no messages sent
4. **Expired hold timer**: Wait 7+ minutes → offers expire automatically

---

## 🐛 Troubleshooting

### Issue: Dashboard shows "Database error"
**Solution:** Check PostgreSQL is running and .env DATABASE_URL is correct
```powershell
python -c "from app.infra.db import check_db_connection; print(check_db_connection())"
```

### Issue: No notifications to ntfy
**Solution:** 
- Verify SLACK_WEBHOOK_URL in .env
- Check API logs for errors
- Test ntfy directly: 
  ```powershell
  curl -d "test message" https://ntfy.sh/your-topic-name
  ```

### Issue: Offers not being created
**Solution:**
- Check waitlist has active entries
- Verify patients have opt_out=false
- Check orchestrator logs in API console

### Issue: Can't simulate SMS response
**Solution:**
- Use exact phone format: +12145551001
- Body must be "YES" or "NO" (case insensitive)
- Check offer exists and is pending

---

## 📱 ntfy.sh Pro Tips

### Custom Message Format
Edit the Twilio mock client to send rich notifications:

```python
# In app/infra/twilio_client.py (mock mode)
import requests

def send_mock_sms(to, body):
    # Log to console
    logger.info(f"Mock SMS to {to}: {body}")
    
    # Send to ntfy
    if settings.SLACK_WEBHOOK_URL:
        requests.post(
            settings.SLACK_WEBHOOK_URL,
            data=body,
            headers={
                "Title": f"SMS to {to[-4:]}",
                "Priority": "high",
                "Tags": "phone,hospital"
            }
        )
```

### Multiple Topics
Use different topics for different message types:
- `clinic-chatbot-offers` - Offer messages
- `clinic-chatbot-confirmations` - Acceptances
- `clinic-chatbot-errors` - System errors

---

## ✅ Testing Checklist

Before declaring success, verify:

- [ ] Dashboard loads and shows stats
- [ ] Can add patient via dashboard
- [ ] Can create cancellation via API
- [ ] Offers appear in dashboard
- [ ] Countdown timers work
- [ ] Can simulate YES response
- [ ] Winner marked correctly
- [ ] Message log shows all activity
- [ ] ntfy notifications received (if configured)
- [ ] Database updates correctly

---

## 🎉 Success!

If all tests pass, your system is ready for:
1. Real Twilio integration (next week)
2. Production testing with staff
3. User acceptance testing

Just change `.env`:
```bash
USE_MOCK_TWILIO=false
TWILIO_ACCOUNT_SID=<real_sid>
TWILIO_AUTH_TOKEN=<real_token>
```

---

## 📚 Resources

- **ntfy.sh**: https://ntfy.sh
- **Swagger API Docs**: http://localhost:8000/docs
- **Dashboard**: http://localhost:8502
- **PostgreSQL**: Use pgAdmin or DBeaver to inspect tables

---

**Happy Testing! 🧪**
