# 🏥 Clinic Cancellation Chatbot

**Automated SMS-based waitlist management system for filling last-minute appointment cancellations**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-blue.svg)](https://www.postgresql.org/)
[![Twilio](https://img.shields.io/badge/Twilio-HIPAA_Compliant-red.svg)](https://www.twilio.com/)

---

## 📋 Overview

The Clinic Cancellation Chatbot is a secure, automated system that fills last-minute appointment cancellations by messaging patients from a managed waitlist via SMS. Built for Texas Pulmonary & Critical Care Consultants (TPCCC), it reduces administrative burden, improves patient access, and optimizes clinic utilization.

### Key Features

✅ **Real-time SMS outreach** via Twilio's HIPAA-compliant platform  
✅ **Intelligent prioritization** based on urgency, manual boost, and appointment proximity  
✅ **Batch messaging** with hold timers and race-safe confirmation  
✅ **Live dashboard** for monitoring active offers and waitlist management  
✅ **HIPAA-compliant** with minimal PHI in messages and comprehensive audit logging  
✅ **Manual override** for staff to promote urgent patients  

---

## 🎯 Success Metrics

* **≥80%** of canceled appointments automatically filled within 2 hours
* **≥95%** message delivery accuracy (Twilio receipts)
* **≤5%** manual intervention required for successful rescheduling
* Full HIPAA-compliant data handling

---

## 🏗️ Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Staff     │────────>│   FastAPI    │<────────│   Twilio    │
│  Dashboard  │         │   Backend    │         │  SMS API    │
└─────────────┘         └──────┬───────┘         └─────────────┘
                               │
                               │
                        ┌──────▼───────┐
                        │  PostgreSQL  │
                        │   Database   │
                        └──────────────┘
```

### Technology Stack

* **Backend:** Python 3.11+, FastAPI, APScheduler
* **Database:** PostgreSQL 14+
* **Messaging:** Twilio Programmable SMS (HIPAA BAA)
* **Dashboard:** Streamlit
* **ORM:** SQLAlchemy / SQLModel
* **Testing:** pytest, pytest-asyncio
* **Hosting:** Windows Server (on-premises)

---

## 🚀 Quick Start

### Prerequisites

* Python 3.11 or higher
* PostgreSQL 14+
* Twilio account with HIPAA BAA
* Windows Server (or compatible environment)

### Installation

1. **Clone the repository**
   ```powershell
   git clone https://github.com/dollythedog/clinic_cancellation_chatbot.git
   cd clinic_cancellation_chatbot
   ```

2. **Create virtual environment**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Set up database**
   
   **Option A: Docker (recommended for development)**
   ```powershell
   docker-compose up -d
   ```
   
   **Option B: Existing PostgreSQL server**
   ```powershell
   # Edit scripts/setup_db.py with your connection details
   python scripts/setup_db.py
   ```

5. **Configure environment**
   ```powershell
   # Copy example .env file
   cp .env.dev .env
   
   # Edit .env with your credentials:
   # - DATABASE_URL (from setup script output)
   # - TWILIO credentials (or use mock mode: USE_MOCK_TWILIO=true)
   ```

6. **Seed sample data** (optional for testing)
   ```powershell
   python scripts/seed_sample_data.py
   ```

7. **Run the application**
   ```powershell
   # Start FastAPI backend
   make run-api
   # or manually:
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   
   # In a separate terminal, start the dashboard:
   make run-dashboard
   # or manually:
   streamlit run dashboard/app.py --server.port 8502
   
   # Access:
   # - API Docs: http://localhost:8000/docs
   # - API Health: http://localhost:8000/health
   # - Dashboard: http://localhost:8502
   ```

---

## 📦 Project Structure

```
clinic_cancellation_chatbot/
├── app/
│   ├── api/              # REST API endpoints
│   ├── core/             # Business logic (orchestrator, prioritizer)
│   ├── infra/            # Infrastructure (DB, Twilio, settings)
│   └── main.py           # FastAPI application entry point
├── dashboard/
│   └── app.py            # Streamlit dashboard
├── scripts/
│   ├── migrations/       # Alembic database migrations
│   └── seed_data.py      # Test data generation
├── utils/                # Shared utilities
├── tests/                # Test suite
├── configs/
│   └── .env.example      # Environment configuration template
├── data/
│   ├── inbox/            # Incoming data staging
│   ├── staging/          # Processing area
│   ├── archive/          # Historical data
│   └── logs/             # Application logs
├── docs/
│   ├── DEPLOYMENT.md     # Deployment guide
│   ├── RUNBOOK.md        # Operations manual
│   └── SOP.md            # Staff procedures
├── PROJECT_CHARTER.md    # Project goals and scope
├── PROJECT_PLAN.md       # Implementation roadmap
├── CHANGELOG.md          # Version history
└── README.md             # This file
```

---

## 🔐 Security & Compliance

### HIPAA Compliance

* ✅ Twilio Business Associate Agreement (BAA) in place
* ✅ Minimal PHI in SMS messages (no diagnoses, limited names)
* ✅ Database encryption at rest
* ✅ TLS 1.2+ for all webhook connections
* ✅ Webhook signature verification
* ✅ Comprehensive audit logging
* ✅ Data retention policy (90-day message rotation)
* ✅ STOP/HELP keyword compliance

### Security Features

* Principle of least privilege database access
* Race-safe appointment confirmation (SELECT FOR UPDATE)
* Rate limiting to prevent spam
* Exception handling and error recovery
* Secure credential management (environment variables)

---

## 📊 Database Schema

### Core Tables

* **`patient_contact`** - Patient phone numbers and opt-out status
* **`provider_reference`** - Provider information and types
* **`waitlist_entry`** - Active waitlist with priority scoring
* **`cancellation_event`** - Canceled appointment slots
* **`offer`** - Individual SMS offers with hold timers
* **`message_log`** - SMS message audit trail

See [PROJECT_PLAN.md](PROJECT_PLAN.md) for detailed schema definitions.

---

## 🧠 Prioritization Logic

Waitlist entries are scored using the following algorithm:

```python
score = (UrgentFlag ? +30 : 0)
      + ManualBoost (0-40, admin-set)
      + DaysUntilCurrentAppt (0-20 based on proximity)
      + WaitlistSeniority (0-10 based on join date)
```

Higher scores = higher priority. Tie-breaker: earliest waitlist join time.

---

## 📨 SMS Message Flow

```mermaid
flowchart TD
    Start([Staff Logs Cancellation]) --> CreateEvent[Create Cancellation Event in DB]
    CreateEvent --> Orchestrator[Orchestrator Triggered]
    Orchestrator --> CheckWaitlist{Waitlist
Has Eligible
Patients?}
    
    CheckWaitlist -->|No| Log1[Log: No candidates available] --> End1([End])
    CheckWaitlist -->|Yes| Prioritizer[Prioritizer Calculates Scores]
    
    Prioritizer --> SelectTop[Select Top 3 by Priority Score]
    SelectTop --> CheckContactHours{Within
Contact Hours?}
    
    CheckContactHours -->|No| Schedule[Schedule for Next Contact Window] --> End2([End])
    CheckContactHours -->|Yes| CreateOffers[Create Offer Records in DB]
    
    CreateOffers --> SendBatch[Send Batch SMS via Twilio]
    SendBatch --> SetTimer[Start 7-Minute Hold Timer]
    SetTimer --> Wait[Wait for Response...]
    
    Wait --> ResponseCheck{Patient
Response?}
    
    ResponseCheck -->|"YES"| FirstYes{First YES
to Reply?}
    FirstYes -->|Yes - Race Safe Lock| ConfirmSlot[Confirm Appointment - Update DB]
    ConfirmSlot --> SendConfirm[Send Confirmation SMS]
    SendConfirm --> NotifyOthers[Notify Other Candidates Slot Taken]
    NotifyOthers --> UpdateWaitlist[Update Waitlist Entry to Matched]
    UpdateWaitlist --> LogSuccess[Log Successful Fill] --> End3([End])
    
    FirstYes -->|No - Already Taken| SendSorry[Send "Slot Already Filled" SMS] --> End4([End])
    
    ResponseCheck -->|"NO"| LogDecline[Log Decline]
    LogDecline --> CheckOthers{Other Offers
Still Pending?}
    CheckOthers -->|Yes| Wait
    CheckOthers -->|No| CheckTimer
    
    ResponseCheck -->|Timeout 7 min| CheckTimer{Any YES
Responses?}
    CheckTimer -->|No| ExpireOffers[Expire All Current Offers]
    ExpireOffers --> CheckMore{More Waitlist
Patients?}
    CheckMore -->|Yes| Prioritizer
    CheckMore -->|No| LogUnfilled[Log: Unable to Fill] --> End5([End])
    
    CheckTimer -->|Yes| SendConfirm
    
    ResponseCheck -->|"STOP"| OptOut[Mark Patient as Opted Out] --> End6([End])
    ResponseCheck -->|"HELP"| SendHelp[Send Help Message] --> Wait
    ResponseCheck -->|Unknown| SendHelp

    style Start fill:#e1f5e1
    style End1 fill:#ffe1e1
    style End2 fill:#ffe1e1
    style End3 fill:#e1f5e1
    style End4 fill:#ffe1e1
    style End5 fill:#ffe1e1
    style End6 fill:#ffe1e1
    style ConfirmSlot fill:#90ee90
    style SendBatch fill:#87ceeb
    style FirstYes fill:#ffcccb
```

### Process Steps

1. **Cancellation logged** (manual or Greenway integration)
2. **System identifies top 3 candidates** from waitlist
3. **Batch SMS sent** with 7-minute hold timer
4. **First "YES" response wins** the slot
5. **Winner confirmed**, others notified slot is taken
6. **If no response**, next batch sent after hold expires

### Sample Messages

**Initial Offer:**
```
TPCCC: An earlier appointment opened tomorrow at 10:00 AM at Main Clinic. 
Reply YES to claim or NO to skip. This offer expires in 7 min.
```

**Confirmation:**
```
TPCCC: Confirmed. You're scheduled Nov 1 at 10:00 AM at Main Clinic. 
Reply STOP to opt out of future messages.
```

---

## 🖥️ Dashboard

The Streamlit dashboard provides real-time visibility into:

* **Active Cancellations** - Open slots with countdown timers
* **Waitlist Leaderboard** - Sorted by priority score  
* **Active Offers** - Pending offers with expiration timers
* **Message Log** - SMS audit trail with filtering
* **Admin Controls** - Manual boost, add/remove patients

**Access:** `http://localhost:8501`

**Features:**
- Real-time metrics in sidebar (cancellations, waitlist size, pending offers)
- Auto-refresh option (30-second intervals)
- Multiple views: Dashboard, Waitlist, Message Log, Admin Tools
- HIPAA-compliant display (last 4 digits of phone numbers only)

---

## 🧪 Testing

```powershell
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test suite
pytest tests/test_orchestrator.py -v
```

### Test Strategy

* **Unit tests**: Priority scoring, message templates, time conversions
* **Integration tests**: Full orchestration flow, webhook handling
* **End-to-end tests**: Seed data → cancellation → SMS → confirmation

---

## 📚 Documentation

* [PROJECT_CHARTER.md](PROJECT_CHARTER.md) - Project goals, scope, and success criteria
* [PROJECT_PLAN.md](PROJECT_PLAN.md) - Detailed implementation roadmap
* [CHANGELOG.md](CHANGELOG.md) - Version history and release notes
* [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) - Deployment guide for Windows Server
* [docs/RUNBOOK.md](docs/RUNBOOK.md) - Operations manual
* [docs/SOP.md](docs/SOP.md) - Staff procedures

---

## 🛠️ Configuration

Key environment variables (see `configs/.env.example`):

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/clinic_chatbot

# Twilio
TWILIO_ACCOUNT_SID=ACxxxx
TWILIO_AUTH_TOKEN=your_token_here
TWILIO_PHONE_NUMBER=+12145551234

# Application
BATCH_SIZE=3
HOLD_MINUTES=7
CONTACT_HOURS_START=08:00
CONTACT_HOURS_END=20:00
TIMEZONE=America/Chicago
```

---

## 🔄 Future Enhancements

**Phase 2:**
* Direct Greenway EHR integration
* Automatic appointment confirmation in EHR
* Multi-location support
* Voice call fallback

**Phase 3:**
* ML-based patient preference learning
* Multi-language support
* Integration with patient portal
* Predictive cancellation modeling

---

## 🤝 Contributing

This is an internal TPCCC project. For questions or issues:

* **Project Owner:** Jonathan Ives (@dollythedog)
* **Email:** [Your email]
* **GitHub:** https://github.com/dollythedog/clinic_cancellation_chatbot

---

## 📄 License

Internal use only - Texas Pulmonary & Critical Care Consultants  
Copyright © 2025 TPCCC. All rights reserved.

---

## 🙏 Acknowledgments

* **Sponsor:** Jonathan Ives, Chief Strategy Officer
* **Department:** TPCCC Operations
* **Platform:** Twilio Programmable Messaging
* **Infrastructure:** TPCCC IT Team

---

## 📞 Support

For technical support or questions:

1. Check the [docs/RUNBOOK.md](docs/RUNBOOK.md) for troubleshooting
2. Review [PROJECT_PLAN.md](PROJECT_PLAN.md) for implementation details
3. Contact the project owner

---

**Status:** 🚧 Active Development - Milestone 3 Complete  
**Last Updated:** November 1, 2025  
**Version:** 0.3.0

**Recent Progress:**
- ✅ Milestone 1: Bootstrap (100%)
- ✅ Milestone 2: Core Logic (100%)
- ✅ Milestone 3: Dashboard (100%) - **Just Completed!**
- 🔜 Milestone 4: Hardening (Next)

**Completed:** 18/25 issues (72%)

**Latest Session (2025-11-01):**
- ✅ Fixed SQLAlchemy enum handling for Windows
- ✅ Fixed Windows date formatting issues
- ✅ Fixed dashboard infinite rerun loop  
- ✅ Created seed_sample_data.py for easy testing
- ✅ Dashboard now fully functional with sample data
- ✅ **Added ntfy.sh integration for mock SMS testing**
- ✅ Mock Twilio client now sends push notifications to phone
- ✅ Perfect for testing without real SMS costs
