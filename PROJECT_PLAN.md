# 📋 PROJECT_PLAN.md

**Project:** Automated Clinic Cancellation & Waitlist Chatbot  
**Owner:** Jonathan Ives (@dollythedog)  
**Last Updated:** October 2025

---

## 🎯 Project Overview

This document provides a detailed implementation plan for the clinic cancellation chatbot, breaking down the PROJECT_CHARTER.md into actionable milestones, tasks, and technical specifications.

---

## 🏗️ System Architecture

### Technology Stack

* **Backend:** Python 3.11+, FastAPI, APScheduler
* **Database:** PostgreSQL 14+ (existing Windows server)
* **Messaging:** Twilio Programmable SMS (HIPAA-compliant)
* **Dashboard:** Streamlit (internal LAN)
* **ORM:** SQLAlchemy / SQLModel
* **Testing:** pytest, pytest-asyncio
* **Hosting:** Windows Server (on-premises)
* **Webhook Exposure:** Cloudflare Tunnel or Tailscale Funnel

### Core Components

```
clinic_cancellation_chatbot/
├── app/
│   ├── api/
│   │   ├── cancellations.py      # POST /admin/cancel
│   │   ├── sms_webhook.py        # POST /sms/inbound (YES/NO)
│   │   ├── status_webhook.py     # POST /twilio/status
│   │   └── waitlist_api.py       # CRUD waitlist entries
│   ├── core/
│   │   ├── orchestrator.py       # Batch sends, hold timers
│   │   ├── prioritizer.py        # Priority score calculation
│   │   ├── scheduler.py          # APScheduler jobs
│   │   └── templates.py          # SMS text templates
│   ├── infra/
│   │   ├── db.py                 # SQLAlchemy engine/session
│   │   ├── models.py             # ORM models
│   │   ├── twilio_client.py      # Twilio wrapper
│   │   └── settings.py           # Config via env vars
│   └── main.py                   # FastAPI application
├── dashboard/
│   └── app.py                    # Streamlit dashboard
├── scripts/
│   ├── migrations/               # Alembic migrations
│   └── seed_data.py              # Test data generation
├── utils/
│   ├── config_loader.py
│   ├── db_utils.py
│   ├── log_utils.py
│   ├── time_utils.py
│   └── provider_utils.py
├── tests/
│   ├── test_orchestrator.py
│   ├── test_prioritizer.py
│   └── test_webhooks.py
├── configs/
│   └── .env.example
├── data/
│   ├── inbox/
│   ├── staging/
│   ├── archive/
│   └── logs/
└── docs/
    ├── DEPLOYMENT.md
    ├── RUNBOOK.md
    └── SOP.md
```

---

## 📊 Database Schema

### Tables

#### `patient_contact`
```sql
CREATE TABLE patient_contact (
    id SERIAL PRIMARY KEY,
    phone_e164 TEXT NOT NULL UNIQUE,
    display_name TEXT,
    last_contacted_at TIMESTAMP WITH TIME ZONE,
    opt_out BOOLEAN DEFAULT FALSE,
    consent_source TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX idx_patient_phone ON patient_contact(phone_e164);
CREATE INDEX idx_patient_opt_out ON patient_contact(opt_out);
```

#### `provider_reference`
```sql
CREATE TABLE provider_reference (
    id SERIAL PRIMARY KEY,
    provider_name TEXT NOT NULL,
    provider_type TEXT NOT NULL, -- 'MD/DO', 'APP', etc.
    active BOOLEAN DEFAULT TRUE,
    external_provider_id TEXT,
    tags TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### `waitlist_entry`
```sql
CREATE TABLE waitlist_entry (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patient_contact(id) ON DELETE CASCADE,
    provider_preference TEXT[],
    provider_type_preference TEXT, -- 'MD/DO', 'APP', 'Any'
    current_appt_at TIMESTAMP WITH TIME ZONE,
    urgent_flag BOOLEAN DEFAULT FALSE,
    manual_boost INTEGER DEFAULT 0 CHECK (manual_boost BETWEEN 0 AND 40),
    active BOOLEAN DEFAULT TRUE,
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    priority_score INTEGER,
    notes TEXT
);
CREATE INDEX idx_waitlist_active ON waitlist_entry(active, urgent_flag);
CREATE INDEX idx_waitlist_priority ON waitlist_entry(priority_score DESC);
```

#### `cancellation_event`
```sql
CREATE TYPE cancellation_status AS ENUM (
    'open',
    'filled',
    'expired',
    'aborted'
);

CREATE TABLE cancellation_event (
    id SERIAL PRIMARY KEY,
    provider_id INTEGER REFERENCES provider_reference(id),
    location TEXT NOT NULL,
    slot_start_at TIMESTAMP WITH TIME ZONE NOT NULL,
    slot_end_at TIMESTAMP WITH TIME ZONE NOT NULL,
    reason TEXT,
    status cancellation_status DEFAULT 'open',
    notes TEXT,
    created_by_staff_id INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX idx_cancellation_status ON cancellation_event(status);
```

#### `offer`
```sql
CREATE TYPE offer_state AS ENUM (
    'pending',
    'accepted',
    'declined',
    'expired',
    'canceled',
    'failed'
);

CREATE TABLE offer (
    id SERIAL PRIMARY KEY,
    cancellation_id INTEGER REFERENCES cancellation_event(id) ON DELETE CASCADE,
    patient_id INTEGER REFERENCES patient_contact(id) ON DELETE CASCADE,
    batch_number INTEGER NOT NULL,
    offer_sent_at TIMESTAMP WITH TIME ZONE,
    hold_expires_at TIMESTAMP WITH TIME ZONE,
    state offer_state DEFAULT 'pending',
    lock_token UUID DEFAULT gen_random_uuid(),
    accepted_at TIMESTAMP WITH TIME ZONE,
    declined_at TIMESTAMP WITH TIME ZONE
);
CREATE INDEX idx_offer_cancellation ON offer(cancellation_id);
CREATE INDEX idx_offer_state ON offer(state);
```

#### `message_log`
```sql
CREATE TYPE message_direction AS ENUM ('outbound', 'inbound');
CREATE TYPE message_status AS ENUM (
    'queued',
    'sent',
    'delivered',
    'undelivered',
    'failed',
    'received'
);

CREATE TABLE message_log (
    id SERIAL PRIMARY KEY,
    offer_id INTEGER REFERENCES offer(id),
    direction message_direction NOT NULL,
    body TEXT NOT NULL,
    twilio_sid TEXT,
    status message_status,
    received_at TIMESTAMP WITH TIME ZONE,
    sent_at TIMESTAMP WITH TIME ZONE,
    raw_meta JSONB
);
CREATE INDEX idx_message_twilio_sid ON message_log(twilio_sid);
```

---

## 🧠 Prioritization Algorithm

```python
def calculate_priority_score(entry: WaitlistEntry) -> int:
    """
    Compute priority score for waitlist entry.
    Higher score = higher priority.
    """
    score = 0
    
    # Urgent flag: +30
    if entry.urgent_flag:
        score += 30
    
    # Manual boost: 0-40 (admin controlled)
    score += entry.manual_boost
    
    # Days until current appointment
    if entry.current_appt_at:
        days_until = (entry.current_appt_at - now_utc()).days
        if days_until >= 180:
            score += 20
        elif days_until >= 90:
            score += 10
        elif days_until >= 30:
            score += 5
    
    # Waitlist seniority: 0-10
    days_on_waitlist = (now_utc() - entry.joined_at).days
    score += min(days_on_waitlist // 30, 10)
    
    return score
```

---

## 📨 SMS Message Templates

### Initial Offer
```
TPCCC: An earlier appointment opened tomorrow at {time} at {location}. Reply YES to claim or NO to skip. This offer expires in 7 min.
```

### Acceptance (Winner)
```
TPCCC: Confirmed. You're scheduled {date} {time} at {location}. Reply STOP to opt out of future messages.
```

### Acceptance (Too Late)
```
TPCCC: Thanks—this slot has been taken. We'll keep you on the list for the next opening.
```

### Decline
```
TPCCC: No problem—we'll keep you on the list for future openings.
```

### HELP
```
HELP: TPCCC scheduling. Reply YES to claim slots; NO to skip.
```

### STOP
```
You'll no longer receive earlier-slot messages from TPCCC.
```

---

## 🚀 Implementation Milestones

### **Milestone 1: Bootstrap** (Days 1-2)

**Tasks:**
- [x] Initialize Git repository
- [ ] Create project directory structure
- [ ] Set up virtual environment and requirements.txt
- [ ] Create .env.example with all config variables
- [ ] Define database schema (schema.sql)
- [ ] Set up Alembic for migrations
- [ ] Implement time_utils.py (UTC/Central conversion)
- [ ] Create basic FastAPI skeleton with health check

**Deliverables:**
- Working development environment
- Database schema documented
- FastAPI app serving `/health` endpoint

---

### **Milestone 2: Core Logic** (Days 3-5)

**Tasks:**
- [ ] Implement ORM models (models.py)
- [ ] Build prioritizer.py with scoring algorithm
- [ ] Create orchestrator.py (batch sending, hold timers)
- [ ] Implement SMS webhook handler (/sms/inbound)
- [ ] Implement status webhook handler (/twilio/status)
- [ ] Build manual cancellation entry endpoint (/admin/cancel)
- [ ] Set up APScheduler for hold timer expiration
- [ ] Add race-safe reservation logic (SELECT FOR UPDATE)

**Deliverables:**
- Working offer orchestration engine
- SMS message handling (inbound/outbound)
- Cancellation event processing

---

### **Milestone 3: Dashboard** (Day 6)

**Tasks:**
- [ ] Create Streamlit dashboard app
- [ ] Build active cancellations view
- [ ] Add waitlist leaderboard (sorted by priority)
- [ ] Display active offers with countdown timers
- [ ] Implement message audit log viewer
- [ ] Add manual boost controls
- [ ] Add waitlist CRUD operations

**Deliverables:**
- Real-time monitoring dashboard
- Admin controls for waitlist management

---

### **Milestone 4: Hardening** (Day 7)

**Tasks:**
- [ ] Implement STOP/HELP keyword handling
- [ ] Add opt-out tracking in database
- [ ] Create audit logging system
- [ ] Add rate limiting to prevent spam
- [ ] Implement exception handling and error recovery
- [ ] Write comprehensive test suite
- [ ] Create deployment documentation
- [ ] Write staff runbook and SOP

**Deliverables:**
- HIPAA-compliant message handling
- Production-ready error handling
- Complete documentation

---

### **Milestone 5: Greenway Integration** (Future)

**Tasks:**
- [ ] Evaluate Greenway API capabilities
- [ ] Choose integration approach (webhook/polling/CSV import)
- [ ] Map Greenway fields to internal schema
- [ ] Build integration module
- [ ] Test end-to-end with production data
- [ ] Create monitoring and alerting

**Deliverables:**
- Automated cancellation ingestion from EHR

---

## 🔐 Security & Compliance Checklist

- [ ] Twilio BAA signed and active
- [ ] A2P 10DLC registration complete
- [ ] No PHI in SMS message bodies
- [ ] All timestamps stored in UTC with TZ support
- [ ] Database encryption at rest enabled
- [ ] TLS 1.2+ for all webhook connections
- [ ] Webhook signature verification implemented
- [ ] Principle of least privilege DB user created
- [ ] Audit trail for all system actions
- [ ] Data retention policy documented and implemented
- [ ] Rate limiting configured
- [ ] STOP/HELP compliance verified
- [ ] Staff training completed

---

## 🧪 Testing Strategy

### Unit Tests
- Priority score calculation
- Message template rendering
- Time zone conversions
- Provider matching logic

### Integration Tests
- Full offer orchestration flow
- Webhook handling (mocked Twilio)
- Database transactions and rollbacks
- Race condition handling

### End-to-End Tests
- Seed 3 test patients on waitlist
- Create cancellation event
- Verify 3 outbound messages sent
- Simulate YES response from patient #1
- Verify winner confirmed, others notified
- Verify dashboard updates
- Test STOP keyword

---

## 📦 Configuration Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/clinic_chatbot

# Twilio
TWILIO_ACCOUNT_SID=ACxxxx
TWILIO_AUTH_TOKEN={{TWILIO_AUTH_TOKEN}}
TWILIO_PHONE_NUMBER=+12145551234
TWILIO_MESSAGING_SERVICE_SID=MGxxxx

# Application
BATCH_SIZE=3
HOLD_MINUTES=7
CONTACT_HOURS_START=08:00
CONTACT_HOURS_END=20:00
TIMEZONE=America/Chicago

# Security
WEBHOOK_SECRET={{WEBHOOK_SECRET}}
API_KEY={{API_KEY}}

# Logging
LOG_LEVEL=INFO
LOG_FILE=data/logs/app.log
```

---

## 📞 Support & Maintenance

**Monitoring:**
- Twilio delivery rate dashboard
- Message log review (weekly)
- Fill rate metrics (daily)
- Error log review (daily)

**Maintenance Windows:**
- Database backups: Daily at 2:00 AM CT
- Log rotation: Weekly
- Dependency updates: Monthly

---

## 🎓 Training & Onboarding

**Staff Training Topics:**
1. How to log a cancellation manually
2. Using the dashboard to view active offers
3. Applying manual boost to urgent patients
4. Handling patient questions about SMS messages
5. Troubleshooting common issues

**Timeline:**
- Week 1: Demo session for leadership
- Week 2: Hands-on training for front desk
- Week 3: Shadow mode (parallel with manual process)
- Week 4: Full production launch

---

## 📈 Success Metrics

**Primary KPIs:**
- Appointment fill rate (target: ≥80%)
- Time to fill (target: <2 hours)
- Message delivery rate (target: ≥95%)
- Manual intervention rate (target: ≤5%)

**Secondary KPIs:**
- Patient response rate
- Staff time saved per week
- Provider utilization improvement
- Patient satisfaction scores

---

## 🔄 Future Enhancements

**Phase 2:**
- Direct Greenway EHR integration
- Automatic appointment confirmation in EHR
- Multi-location support
- Voice call fallback for non-responsive patients

**Phase 3:**
- Patient preference learning (ML-based)
- Multi-language support
- Integration with patient portal
- Predictive cancellation modeling

---

## 📝 Notes

This plan assumes:
- Existing PostgreSQL instance on Windows server
- Staff available for manual cancellation entry (MVP)
- Twilio account with HIPAA BAA in place
- Internal network access for dashboard
- Cloudflare or Tailscale for webhook tunneling
