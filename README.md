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
   # Copy the template at the repo root
   cp .env.example .env

   # Edit .env with your credentials. The following are REQUIRED;
   # the application will refuse to start without them:
   #   - DATABASE_URL
   #   - TWILIO_ACCOUNT_SID
   #   - TWILIO_AUTH_TOKEN
   #   - TWILIO_PHONE_NUMBER
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
├── tests/                # pytest test suite (conftest + test modules)
├── data/
│   ├── inbox/            # Incoming data staging
│   ├── staging/          # Processing area
│   ├── archive/          # Historical data
│   └── logs/             # Application logs
├── docs/
│   ├── DEPLOYMENT.md     # Deployment guide
│   ├── RUNBOOK.md        # Operations manual
│   └── SOP.md            # Staff procedures
├── .env.example          # Environment configuration template (copy to .env at repo root)
├── pyproject.toml        # Tool configuration (ruff, pytest)
├── PROJECT_CHARTER.md    # Project goals and scope
├── PROJECT_PLAN.md       # Implementation roadmap
├── CHANGELOG.md          # Version history
├── DECISIONS.md          # Architectural and design decisions
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

### Webhook authentication

All inbound Twilio webhooks are verified cryptographically by the
[`TwilioSignatureMiddleware`](app/api/middleware.py) registered on the
FastAPI application. **Protected path prefixes:**

* `/sms/*` — inbound SMS from patients
* `/twilio/*` — Twilio delivery-status callbacks

The middleware requires a valid `X-Twilio-Signature` header on every
POST to a protected path. Missing or invalid signatures are rejected
with HTTP 403 before any route handler runs — no database write, no
log of the inbound body, no chance for a forged request to impersonate
Twilio. All other paths (`/healthz`, `/readyz`, `/health`, `/`, `/docs`,
`/admin/*`) pass through unmodified.

The signature is computed by Twilio as the HMAC-SHA1 of the canonical
webhook URL concatenated with the sorted form-encoded body parameters,
keyed with the account's auth token. The middleware uses
[`twilio.request_validator.RequestValidator`](https://www.twilio.com/docs/usage/webhooks/webhooks-security)
to re-compute the expected signature against `settings.TWILIO_AUTH_TOKEN`
and compares in constant time.

**Canonical-URL strategy.** Twilio signs against the public URL it
POSTed to. Behind the Cloudflare Tunnel + NSSM deployment on the
Windows server, that public URL's scheme and host differ from what
FastAPI sees internally. Set `TWILIO_WEBHOOK_BASE_URL` in `.env` to the
public base (e.g. `https://webhooks.tpccc.example.com`) and the
middleware will concatenate it with the request's path + query to
reconstruct the exact URL Twilio signed. If `TWILIO_WEBHOOK_BASE_URL`
is unset the middleware falls back to the internal `request.url` and
emits a warn-level `webhook.signature.url_fallback` event — fine for
local development, but every public deployment must set the base URL
or every signature verification will fail. See
[`DECISIONS.md`](DECISIONS.md) 2026-04-23 "Twilio signature middleware
URL strategy" for the full rationale.

Local reproduction (using the `twilio` Python package the project
already pins in `requirements.txt`):

```python
from twilio.request_validator import RequestValidator
validator = RequestValidator(settings.TWILIO_AUTH_TOKEN)
signature = validator.compute_signature(url, params)
```

### Dashboard authentication

The Streamlit dashboard gates access behind a single-admin username +
password check implemented in
[`dashboard/auth.py`](dashboard/auth.py). Every session must sign in
before any dashboard content renders. Three invariants hold:

* **Localhost bind.** `STREAMLIT_SERVER_ADDRESS` defaults to
  `127.0.0.1` — the Streamlit server is unreachable from the clinic
  LAN. The only ingress is operators sitting at the Windows server's
  console (or RDC'd in with existing Windows creds). Override to
  `0.0.0.0` only behind a reverse proxy that's filtering inbound
  traffic.
* **Session-scoped login.** The login form wrapper, rendered as the
  first content on every request, blocks the dashboard until the
  operator supplies valid credentials. Auth persists for the current
  browser session; closing the tab or restarting the NSSM service
  ends the session and requires a fresh login. No persistent cookies,
  no remember-me, no expiry timer.
* **SHA-256 salted hash, constant-time comparison.** Credentials live
  in `.env` as `DASHBOARD_USERNAME`, `DASHBOARD_PASSWORD_HASH`, and
  `DASHBOARD_PASSWORD_SALT`. The hash is SHA-256 of `salt || plaintext`
  and comparison uses `hmac.compare_digest` to defeat timing-attack
  observers. Plaintext passwords are never logged, never committed,
  never stored outside `.env`. The interpretation of "HTTP basic-auth
  wrapper" (session-scoped in-app login vs. literal WWW-Authenticate
  401 basic-auth) plus the credential-rotation procedure — generating
  a fresh salt + hash pair and restarting the NSSM Streamlit service —
  are documented in [`DECISIONS.md`](DECISIONS.md) 2026-04-23
  *"Streamlit dashboard authentication — session-scoped login wrapper
  + localhost bind + SHA-256 salted hash"*.

Why not a reverse proxy or a full auth library? COA 1 (Minimal
Hardening / Single-Service Monolith) explicitly rules out reverse
proxies, and the single-admin threat model does not warrant
`bcrypt` / `argon2` / `streamlit-authenticator` — the Solo-Maintainer
Fit guardrail lens prices every extra dependency. If the threat model
grows (multi-user access, LAN-external exposure), the upgrade path is
named at the bottom of the same `DECISIONS.md` entry.

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
    Start([Cancellation: Nov 1 at 10:00 AM]) --> Batch[Send to Top 3 Waitlist Patients]
    
    Batch --> P1["Patient A receives:<br/>TPCCC: An earlier appointment<br/>opened Nov 1 at 10:00 AM<br/>at Main Clinic. Reply YES<br/>to claim or NO to skip.<br/>Expires in 7 min."]
    
    Batch --> P2["Patient B receives:<br/>TPCCC: An earlier appointment<br/>opened Nov 1 at 10:00 AM<br/>at Main Clinic. Reply YES<br/>to claim or NO to skip.<br/>Expires in 7 min."]
    
    Batch --> P3["Patient C receives:<br/>TPCCC: An earlier appointment<br/>opened Nov 1 at 10:00 AM<br/>at Main Clinic. Reply YES<br/>to claim or NO to skip.<br/>Expires in 7 min."]
    
    P1 --> Wait[7-Minute Hold Timer Active]
    P2 --> Wait
    P3 --> Wait
    
    Wait --> Response{Patient Response}
    
    Response -->|Patient B replies YES first| Winner["Patient B receives:<br/>TPCCC: Confirmed. You are<br/>scheduled Nov 1 at 10:00 AM<br/>at Main Clinic. Reply STOP<br/>to opt out of future messages."]
    
    Winner --> Others["Patients A & C receive:<br/>TPCCC: The Nov 1 10:00 AM<br/>appointment has been filled.<br/>You remain on the waitlist."]
    
    Others --> Success([Slot Filled Successfully])
    
    Response -->|Patient replies NO| Decline["Patient receives:<br/>TPCCC: Understood. You remain<br/>on the waitlist for future<br/>openings."]
    
    Decline --> CheckOthers{Other patients<br/>still pending?}
    CheckOthers -->|Yes| Wait
    CheckOthers -->|No| NextBatch
    
    Response -->|7 minutes - no replies| NextBatch[Send to Next 3 Patients]
    NextBatch --> Batch
    
    Response -->|Patient replies STOP| OptOut["Patient receives:<br/>TPCCC: You have been removed<br/>from the waitlist. Text START<br/>to rejoin."]
    OptOut --> Removed([Patient Opted Out])
    
    Response -->|Patient replies HELP| Help["Patient receives:<br/>TPCCC: Reply YES to accept<br/>an offer, NO to decline, or<br/>STOP to opt out. Questions?<br/>Call 214-555-1234."]
    Help --> Wait
    
    Response -->|Unknown reply| Help
    
    style Start fill:#e1f5e1
    style Success fill:#90ee90
    style Removed fill:#ffcccb
    style Winner fill:#87ceeb
    style P1 fill:#fff4e6
    style P2 fill:#fff4e6
    style P3 fill:#fff4e6
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

## 📝 Logging

The application uses **structlog** layered on Python's stdlib `logging`
to emit structured JSON events. Every module obtains its logger the
same way:

```python
import structlog
logger = structlog.get_logger(__name__)
```

The logging backbone is installed exactly once at FastAPI startup by
`configure_logging()` in `app/infra/logging_config.py` (invoked from
the lifespan hook). Do not call `logging.basicConfig` or configure
per-module handlers elsewhere.

### Destinations

| Sink | Purpose | Level |
|---|---|---|
| Rotating JSON file (`LOG_FILE`, default `data/logs/app.log`) | Audit of record; rotates at `LOG_MAX_BYTES` with `LOG_BACKUP_COUNT` backups | `LOG_LEVEL` |
| `stderr` stream | Developer visibility during local runs | `LOG_LEVEL` |
| Windows Event Log (`NTEventLogHandler` via `pywin32`) | Error-level alerts on the production Windows server | `ERROR` |

On non-Windows hosts (and Windows hosts without `pywin32`), the Event
Log sink is a graceful no-op and the rest of the pipeline is unchanged.

For the production server, set in `.env`:

```
LOG_LEVEL=INFO
LOG_FILE=C:\ProgramData\CancellationBot\logs\app.log
LOG_MAX_BYTES=52428800          # 50 MB per the Design Schematic
LOG_BACKUP_COUNT=10
```

### Structured fields

Every event is a JSON object with at minimum a timezone-aware UTC
`timestamp`, a `level`, a `logger` name, and a short `event` key.
Offer-flow and Twilio-call events additionally carry a canonical set
of identifiers and an `outcome`:

| Field | Meaning |
|---|---|
| `event` | Short dotted event name, e.g. `offer.accepted`, `twilio.send_sms.sent` |
| `patient_id` | Integer patient primary key (see PHI rule below) |
| `slot_id` / `cancellation_id` | The cancellation / slot being offered |
| `offer_id` | The individual offer row |
| `message_sid` | Twilio message SID (for Twilio-call and status-callback events) |
| `to_phone_mask` / `from_phone_mask` | Last-4-digit mask of a phone number, e.g. `***0199` |
| `outcome` | Short keyword summarizing the result: `sent`, `accepted`, `declined`, `expired`, `api_error`, … |

### PHI rule

Log fields carry **`patient_id` only** as a patient identifier. Patient
names, full E.164 phone numbers, dates of birth, and free-text reply
bodies are **never** written to log fields. The `message_log` database
table is the audit source of truth for full message content. This rule
is enforced both by code convention (`_mask_phone()` helper in
`app/infra/twilio_client.py`) and by a dedicated test in
`tests/test_logging_config.py`.

See `DECISIONS.md` for the full rationale.

### Tailing the log

On the production Windows server:

```powershell
Get-Content C:\ProgramData\CancellationBot\logs\app.log -Tail 50 -Wait
```

Or pipe to `jq` on any system with a Python-capable terminal:

```powershell
Get-Content C:\ProgramData\CancellationBot\logs\app.log -Tail 200 | `
    ForEach-Object { $_ | python -c "import sys,json; print(json.loads(sys.stdin.read())['event'])" }
```

### Health endpoints

Two unauthenticated HTTP probes complement the structured log so
external monitors — Windows Task Scheduler (INF-04), NSSM service
supervision, and future uptime probes — can answer liveness and
readiness questions without credentials.

| Endpoint | Purpose | 200 response body | 503 response body |
|---|---|---|---|
| `GET /healthz` | **Liveness** — the FastAPI process is alive. No database or Twilio calls. | `{"status": "ok", "service", "version", "timestamp"}` | — (never 503 on a live process) |
| `GET /readyz` | **Readiness** — DB reachable (`SELECT 1` with a 2-second timeout) AND required Twilio settings populated. | `{"status": "ok", "checks": {"db": "ok", "twilio": "ok"}, …}` | `{"status": "fail", "checks": {"db": "fail"\|"ok", "twilio": "fail"\|"ok", "twilio_missing": ["NAMES_ONLY"]}, …}` |

Both endpoints emit a structured event on every request (`event=health.check`
for `/healthz`, `event=health.ready` for `/readyz`) carrying the outcome
and per-sub-check status so the audit log can reconstruct probe history
from `app.log` alone. Secret values are never included in response
bodies or log events — only setting names.

The Windows Task Scheduler health-check job polls `/healthz` every
5 minutes per Design Schematic INF-04. Only a 503 (or no response)
triggers the email + ntfy.sh alert path; `/readyz` is polled at the
same cadence for richer status in the log stream.

See `DECISIONS.md` for the unauthenticated-probes decision and the
liveness-vs-readiness split rationale.

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

## 🚀 Production Deployment

### Windows Server Setup with NSSM

The system runs as 3 Windows services managed by NSSM (Non-Sucking Service Manager):

**1. FastAPI Backend Service**
```powershell
nssm install CancellationChatbotAPI "C:\Python311\python.exe" "-m uvicorn app.api.main:app --host 0.0.0.0 --port 8000"
nssm set CancellationChatbotAPI AppDirectory "C:\Projects\clinic_cancellation_chatbot"
nssm set CancellationChatbotAPI AppStdout "C:\Projects\clinic_cancellation_chatbot\data\logs\api.log"
nssm set CancellationChatbotAPI AppStderr "C:\Projects\clinic_cancellation_chatbot\data\logs\api_error.log"
nssm start CancellationChatbotAPI
```

**2. Streamlit Dashboard Service**
```powershell
nssm install CancellationChatbotDashboard "C:\Python311\python.exe" "-m streamlit run dashboard\app.py --server.port 8501 --server.address 0.0.0.0"
nssm set CancellationChatbotDashboard AppDirectory "C:\Projects\clinic_cancellation_chatbot"
nssm set CancellationChatbotDashboard AppStdout "C:\Projects\clinic_cancellation_chatbot\data\logs\dashboard.log"
nssm set CancellationChatbotDashboard AppStderr "C:\Projects\clinic_cancellation_chatbot\data\logs\dashboard_error.log"
nssm start CancellationChatbotDashboard
```

**3. Cloudflare Tunnel Service (for webhooks)**
```powershell
nssm install CancellationChatbotTunnel "C:\Program Files\cloudflared\cloudflared.exe" "tunnel --url http://localhost:8000"
nssm set CancellationChatbotTunnel AppDirectory "C:\Projects\clinic_cancellation_chatbot"
nssm set CancellationChatbotTunnel AppStdout "C:\Projects\clinic_cancellation_chatbot\data\logs\tunnel.log"
nssm set CancellationChatbotTunnel AppStderr "C:\Projects\clinic_cancellation_chatbot\data\logs\tunnel_error.log"
nssm start CancellationChatbotTunnel
```

### Deployment Workflow

```powershell
# On server (via RDC):
cd C:\Projects\clinic_cancellation_chatbot
git pull origin main
# Restart services to pick up changes:
C:\NSSM\nssm-2.24\win32\nssm.exe restart CancellationChatbotAPI
C:\NSSM\nssm-2.24\win32\nssm.exe restart CancellationChatbotDashboard
```

### Troubleshooting

**Streamlit email prompt blocking startup:**
- Copy config from working project: `Copy-Item C:\Projects\clinical_productivity\.streamlit\config.toml C:\projects\clinic_cancellation_chatbot\.streamlit\config.toml -Force`
- Or create manually with `gatherUsageStats = false`

**Service won't start:**
- Check logs: `Get-Content C:\projects\clinic_cancellation_chatbot\data\logs\*.log -Tail 50`
- Check service status: `C:\NSSM\nssm-2.24\win32\nssm.exe status ServiceName`
- Verify ports: `netstat -ano | findstr "8000"`

**Missing dependencies:**
- Reinstall: `pip install -r requirements.txt`
- Common missing: `pip install psycopg2-binary`

### Access Points

- **Dashboard:** http://192.168.1.220:8501 (internal LAN)
- **API Docs:** http://192.168.1.220:8000/docs (internal LAN)
- **Twilio Webhooks:** via Cloudflare Tunnel URL

---

## 📚 Documentation

* [PROJECT_CHARTER.md](PROJECT_CHARTER.md) - Project goals, scope, and success criteria
* [PROJECT_PLAN.md](PROJECT_PLAN.md) - Detailed implementation roadmap
* [CHANGELOG.md](CHANGELOG.md) - Version history and release notes
* [docs/executive_presentation.html](docs/executive_presentation.html) - Executive presentation (Reveal.js)
* [docs/PRESENTATION_STYLE_GUIDE.md](docs/PRESENTATION_STYLE_GUIDE.md) - Presentation design system and templates
* [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) - Deployment guide for Windows Server
* [docs/RUNBOOK.md](docs/RUNBOOK.md) - Operations manual
* [docs/SOP.md](docs/SOP.md) - Staff procedures

---

## 🛠️ Configuration

All application configuration flows through a single
[`Settings`](app/infra/settings.py) class (pydantic-settings). The full
list of supported keys lives in [`.env.example`](.env.example) at the
repo root — copy it to `.env` and fill in your values.

Required keys (the app fails loudly at startup if any are missing):

- `DATABASE_URL`
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN`
- `TWILIO_PHONE_NUMBER`

Configuration validation runs explicitly in the FastAPI lifespan startup
hook via `validate_settings()`. Missing required keys produce a
`pydantic.ValidationError` and a clean stderr message naming what's
missing. Selected highlights below:

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

### Line-ending policy

The repository declares a canonical end-of-line policy in
[`.gitattributes`](.gitattributes) at the repo root:

- `* text=auto eol=lf` — all text files use **LF** in the working tree
  regardless of each contributor's global `core.autocrlf` setting.
- `*.ps1 text eol=crlf` — PowerShell scripts retain **CRLF** (Windows
  PowerShell interprets LF-only `.ps1` files unreliably).

If you ever see a large cosmetic CRLF diff on a file you didn't mean to
change, run the one-time recovery command once from the repo root:

```bash
git add --renormalize .
git commit -m "Renormalize EOL per .gitattributes"
```

This brings the index and working tree back into agreement with the
policy. See [`DECISIONS.md`](DECISIONS.md) (2026-04-23 entry) and
[`ISSUES.md`](ISSUES.md) § `EOL-AUTOCRLF-ROOT-CAUSE` for the rationale
and the 5-Whys diagnosis that motivated this policy.

### Continuous Integration

Pushes to `main` and pull requests targeting `main` trigger the
[`lint`](.github/workflows/lint.yml) GitHub Actions workflow, which
runs the following two commands and blocks merge on any non-zero exit:

```bash
ruff check .
ruff format . --check
```

Reproduce locally — from the repository root — with the exact same two
commands. Both are expected to exit 0 on a clean working tree.

The CI job pins ruff to the same version declared in
[`requirements.txt`](requirements.txt) (currently `ruff==0.15.9`).
Bumping ruff is a deliberate multi-file change: update the version in
both `requirements.txt` and
[`.github/workflows/lint.yml`](.github/workflows/lint.yml) (and any
documentation that names a version) in a single commit so the gate,
the developer workstations, and the baseline disposition recorded in
[`pyproject.toml`](pyproject.toml) `[tool.ruff.lint.per-file-ignores]`
all move together.

If a lint finding is pre-existing and owned by a future work package,
the disposition is captured in [`ISSUES.md`](ISSUES.md) and
grandfathered via a per-file-ignore entry in
[`pyproject.toml`](pyproject.toml) — never silently suppressed
globally. New findings in files that have grandfathered ignores still
fail the gate; the ignore covers only the specific rule code on the
specific file, not the rule set as a whole. See the 2026-04-23
`DECISIONS.md` entry titled *"Grandfathered ruff per-file ignores as
the QA-01 gate-activation discipline"* for the full policy.

Pushes and pull requests also trigger the
[`test`](.github/workflows/test.yml) GitHub Actions workflow, which
installs the full project dependency tree from
[`requirements.txt`](requirements.txt) and runs:

```bash
pytest
```

Reproduce locally — from the repository root — with the exact same
command. Expected to exit 0 with the current 24-test suite on a clean
working tree.

The CI job pins pytest to the version declared in
[`requirements.txt`](requirements.txt) (currently `pytest==7.4.3`).
Bumping pytest follows the same multi-file discipline ruff uses: update
the version in `requirements.txt` and in any developer documentation
that names a version in a single commit so the gate, developer
workstations, and the test suite all move together. The workflow
installs the full dependency tree (not just pytest) because the test
suite imports `app.*` modules and needs SQLAlchemy, psycopg,
pydantic-settings, structlog, and FastAPI at collection time.

Together with the [`lint`](.github/workflows/lint.yml) workflow, the
[`test`](.github/workflows/test.yml) workflow operationalizes the
Iteration-1 exit criterion recorded in the Design Schematic §6: *"All
build acceptance checks pass: `ruff check`, `ruff format --check`,
`pytest` all green."* A merge to `main` is now blocked unless all
three commands exit 0.

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

**Status:** ✅ Production Ready - End-to-End Tested  
**Last Updated:** November 20, 2025  
**Version:** 0.4.0

**Recent Progress:**
- ✅ Milestone 1: Bootstrap (100%)
- ✅ Milestone 2: Core Logic (100%)
- ✅ Milestone 3: Dashboard (100%)
- ✅ Production Testing Complete (100%)
- 🚀 Ready for Server Deployment

**Latest Session (2025-11-20):**
- ✅ End-to-end production testing with real Twilio SMS
- ✅ Full YES/NO workflow validated
- ✅ Automatic next-batch triggering on decline
- ✅ Cloudflare Tunnel webhook integration tested
- ✅ Comprehensive admin controls added to dashboard
- ✅ Delete, void, edit, deactivate functions
- ✅ Bulk operations and system cleanup tools
- ✅ Fixed import errors and enum compatibility
- ✅ Created process_latest_cancellation.py helper script
- 🎯 **System validated and ready for Windows Server deployment**
