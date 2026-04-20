# 🧪 SMS Testing Checklist

**Date:** November 19, 2025  
**Tester:** Jonathan Ives  
**Phone Numbers:**
- Jonathan: +18177743563
- Kylie: +18178887746

**Configuration:**
- Batch Size: 1
- Hold Timer: 30 minutes
- Twilio Mode: REAL (live SMS)
- From Number: +18173919877

---

## ✅ Pre-Test Setup

### 1. Verify Environment
```powershell
# Check .env file
cat .env | Select-String "USE_MOCK_TWILIO","BATCH_SIZE","HOLD_MINUTES"

# Expected output:
# USE_MOCK_TWILIO=false
# BATCH_SIZE=1
# HOLD_MINUTES=30
```

### 2. Verify Database Connection
```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Test database connection
python -c "from app.infra.db import check_db_connection; print('DB OK' if check_db_connection() else 'DB FAIL')"
```

### 3. Seed Test Data
```powershell
python scripts\seed_test_real.py
```

**Expected Output:**
```
🗑️  Clearing existing data...
✅ Existing data cleared

👨‍⚕️ Creating test provider...
✅ Created provider: Dr. Test Provider

👥 Creating test patients...
✅ Created patient: Jonathan (+18177743563) - Priority: 55
✅ Created patient: Kylie (+18178887746) - Priority: 20

============================================================
✅ Test database seeded successfully!
============================================================
```

---

## 🚀 Test Execution

### Phase 1: Start the Backend

```powershell
# Start FastAPI in one terminal
make run-api

# OR manually:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Verify Backend Started:**
- [ ] Check console for "Application started successfully"
- [ ] Open browser: http://localhost:8000/health
- [ ] Expected: `{"status":"healthy","service":"clinic-cancellation-chatbot","version":"0.1.0"}`

---

### Phase 2: Create Test Cancellation

**Open a NEW terminal and run:**

```powershell
# Activate environment
.\.venv\Scripts\Activate.ps1

# Create cancellation for tomorrow at 2:00 PM
python -c "
import requests
from datetime import datetime, timedelta
from utils.time_utils import now_utc

# Calculate tomorrow 2 PM Central Time (convert to UTC)
import pytz
central = pytz.timezone('America/Chicago')
tomorrow_2pm = datetime.now(central) + timedelta(days=1)
tomorrow_2pm = tomorrow_2pm.replace(hour=14, minute=0, second=0, microsecond=0)
slot_start = tomorrow_2pm.astimezone(pytz.UTC).isoformat()

# Calculate slot end (30 minutes later)
slot_end = (tomorrow_2pm + timedelta(minutes=30)).astimezone(pytz.UTC).isoformat()

# Create cancellation
response = requests.post(
    'http://localhost:8000/admin/cancel',
    json={
        'provider_id': 1,
        'location': 'Test Location',
        'slot_start_at': slot_start,
        'slot_end_at': slot_end,
        'reason': 'Test cancellation'
    }
)

print(f'Status: {response.status_code}')
print(f'Response: {response.json()}')
"
```

**Expected Response:**
```json
{
  "cancellation_id": 1,
  "offers_sent": 1,
  "message": "Cancellation created and 1 offer(s) sent"
}
```

---

### Phase 3: Verify SMS Sent

#### Check Backend Logs

**Look for in the FastAPI terminal:**
```
INFO: Offer 1 sent to patient 1 (+18177743563)
```

#### Check Your Phone (Jonathan)

**Within 30 seconds, you should receive:**
```
TPCCC: An earlier appointment opened tomorrow at 2:00 PM CT at Test Location. 
Reply YES to claim or NO to skip. This offer expires in 30 min.
```

- [ ] SMS received on Jonathan's phone (+18177743563)
- [ ] Message format is correct
- [ ] Time/location match
- [ ] Expiration time mentioned

---

### Phase 4: Database Verification

```powershell
# Query the database
python -c "
from app.infra.db import get_session
from app.infra.models import CancellationEvent, Offer, MessageLog

with get_session() as db:
    # Check cancellation
    cancel = db.query(CancellationEvent).first()
    print(f'Cancellation ID: {cancel.id}')
    print(f'Status: {cancel.status}')
    print(f'Location: {cancel.location}')
    print()
    
    # Check offer
    offer = db.query(Offer).first()
    print(f'Offer ID: {offer.id}')
    print(f'State: {offer.state}')
    print(f'Patient ID: {offer.patient_id}')
    print(f'Batch: {offer.batch_number}')
    print()
    
    # Check message log
    msg = db.query(MessageLog).filter_by(direction='outbound').first()
    print(f'Message ID: {msg.id}')
    print(f'To: {msg.to_phone}')
    print(f'Status: {msg.status}')
    print(f'Twilio SID: {msg.twilio_sid}')
"
```

**Expected Output:**
```
Cancellation ID: 1
Status: open
Location: Test Location

Offer ID: 1
State: pending
Patient ID: 1
Batch: 1

Message ID: 1
To: +18177743563
Status: sent
Twilio SID: SMxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

---

## 📱 Test Scenarios

### Scenario A: Accept Offer (YES)

**Action:** Reply **YES** from Jonathan's phone

**Expected Backend Log:**
```
INFO: Patient 1 claimed slot 1
INFO: Offer 1 accepted by patient 1
```

**Expected SMS Response to Jonathan:**
```
TPCCC: Confirmed. You're scheduled tomorrow at 2:00 PM CT at Test Location. 
Reply STOP to opt out of future messages.
```

**Database Check:**
```powershell
python -c "
from app.infra.db import get_session
from app.infra.models import CancellationEvent, Offer

with get_session() as db:
    cancel = db.query(CancellationEvent).first()
    offer = db.query(Offer).first()
    
    print(f'Cancellation Status: {cancel.status}')  # Should be 'filled'
    print(f'Filled By: {cancel.filled_by_patient_id}')  # Should be 1
    print(f'Offer State: {offer.state}')  # Should be 'accepted'
"
```

**Verification Checklist:**
- [ ] Jonathan received confirmation SMS
- [ ] Cancellation status = "filled"
- [ ] Offer state = "accepted"
- [ ] Backend logged success

---

### Scenario B: Decline Offer (NO)

**Action:** Reply **NO** from Jonathan's phone

**Expected Backend Log:**
```
INFO: Patient 1 declined offer 1
```

**Expected SMS Response:**
```
TPCCC: No problem—we'll keep you on the list for future openings.
```

**Database Check:**
```powershell
python -c "
from app.infra.db import get_session
from app.infra.models import CancellationEvent, Offer

with get_session() as db:
    cancel = db.query(CancellationEvent).first()
    offer = db.query(Offer).first()
    
    print(f'Cancellation Status: {cancel.status}')  # Should still be 'open'
    print(f'Offer State: {offer.state}')  # Should be 'declined'
"
```

**Next Batch Test:**
Since BATCH_SIZE=1 and Jonathan declined, the system should send to Kylie after the 30-minute hold expires.

**Wait 30 minutes, then check:**
- [ ] Kylie receives SMS offer
- [ ] New offer record created with batch_number=2

---

### Scenario C: Expired Offer (No Response)

**Action:** Wait 30 minutes without responding

**Expected Backend Behavior:**
- After 30 minutes, scheduler checks expired holds
- Offer marked as "expired"
- Next batch sent to Kylie

**Database Check After 30 Minutes:**
```powershell
python -c "
from app.infra.db import get_session
from app.infra.models import Offer

with get_session() as db:
    offers = db.query(Offer).order_by(Offer.id).all()
    for offer in offers:
        print(f'Offer {offer.id}: Batch {offer.batch_number}, State: {offer.state}, Patient: {offer.patient_id}')
"
```

**Expected:**
```
Offer 1: Batch 1, State: expired, Patient: 1
Offer 2: Batch 2, State: pending, Patient: 2
```

- [ ] Jonathan's offer expired
- [ ] Kylie received new SMS

---

### Scenario D: STOP Keyword

**Action:** Reply **STOP** from Jonathan's phone

**Expected:**
- Patient opt_out flag set to True
- Twilio auto-response: "You have successfully been unsubscribed..."
- No future messages sent to this number

**Database Check:**
```powershell
python -c "
from app.infra.db import get_session
from app.infra.models import PatientContact

with get_session() as db:
    patient = db.query(PatientContact).filter_by(phone_e164='+18177743563').first()
    print(f'Opt Out: {patient.opt_out}')
"
```

- [ ] opt_out = True

---

### Scenario E: HELP Keyword

**Action:** Reply **HELP** from Jonathan's phone

**Expected SMS Response:**
```
HELP: TPCCC scheduling. Reply YES to claim slots; NO to skip.
```

- [ ] HELP response received

---

## 📊 Log File Review

### Check Application Logs

```powershell
# View last 50 lines of logs
Get-Content data\logs\app.log -Tail 50
```

**Look for:**
- [ ] Twilio API calls logged
- [ ] Message delivery status
- [ ] No error messages
- [ ] Offer state transitions

### Check Twilio Console

**Visit:** https://console.twilio.com/us1/monitor/logs/sms

**Verify:**
- [ ] Message appears in Twilio logs
- [ ] Status = "delivered"
- [ ] No error codes
- [ ] Message body matches expected format

---

## 🎯 Success Criteria

### ✅ Test Passes If:

1. **SMS Delivery:**
   - [ ] Jonathan receives SMS within 30 seconds of cancellation creation
   - [ ] Message format matches template
   - [ ] Twilio reports "delivered" status

2. **Database Consistency:**
   - [ ] Cancellation record created
   - [ ] Offer record created with correct batch number
   - [ ] Message log entry exists
   - [ ] All foreign keys valid

3. **Response Handling:**
   - [ ] YES response claims slot and marks cancellation "filled"
   - [ ] NO response marks offer "declined" and sends acknowledgment
   - [ ] Expired offers trigger next batch
   - [ ] STOP keyword sets opt_out flag

4. **Backend Stability:**
   - [ ] No crashes or exceptions
   - [ ] All logs show expected flow
   - [ ] Database transactions committed properly

---

## 🐛 Troubleshooting

### SMS Not Received

**Check:**
1. Twilio account balance sufficient?
2. Phone number verified in Twilio?
3. A2P 10DLC campaign approved?
4. Check Twilio console for error codes

**Common Error Codes:**
- **30007**: Message blocked (carrier filter)
- **30008**: Unknown destination
- **30034**: Message undeliverable (invalid number)

### Database Errors

```powershell
# Check database connection
python -c "from app.infra.db import engine; print(engine.url)"

# Verify tables exist
python -c "
from app.infra.db import engine
from sqlalchemy import inspect
inspector = inspect(engine)
print('Tables:', inspector.get_table_names())
"
```

### Backend Not Starting

```powershell
# Check for port conflicts
netstat -ano | findstr :8000

# Check .env file loaded
python -c "from app.infra.settings import settings; print(settings.DATABASE_URL)"
```

---

## 📝 Test Log Template

**Test Run:** [Date/Time]  
**Tester:** Jonathan Ives  

| Scenario | Action | Expected | Actual | Pass/Fail |
|----------|--------|----------|--------|-----------|
| Setup | Seed data | Data created | | |
| Send SMS | Create cancellation | SMS received | | |
| Accept | Reply YES | Slot claimed | | |
| Decline | Reply NO | Acknowledged | | |
| Expire | Wait 30 min | Next batch | | |
| STOP | Reply STOP | Opt out | | |
| HELP | Reply HELP | Help msg | | |

**Notes:**

**Issues Found:**

**Next Steps:**

---

## 🎉 Ready to Test!

**Run these commands in order:**

```powershell
# 1. Activate environment
.\.venv\Scripts\Activate.ps1

# 2. Seed test data
python scripts\seed_test_real.py

# 3. Start backend (keep running)
make run-api

# 4. In NEW terminal, create cancellation
python scripts\create_test_cancellation.py

# 5. Check your phone!
```

Good luck! 🍀
