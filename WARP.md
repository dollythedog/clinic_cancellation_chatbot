# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

**Project:** Clinic Cancellation Chatbot  
**Owner:** Jonathan Ives (@dollythedog)  
**Last Updated:** 2025-10-31

---

## Project Context

This project is an **SMS-based chatbot** for Texas Pulmonary & Critical Care Consultants (TPCCC) that automatically fills last-minute appointment cancellations by messaging patients from a managed waitlist. The system prioritizes patients intelligently and handles responses in real-time.

---

## 🚀 Common Commands

**Note:** This project uses a Makefile for common workflows. Run `make help` to see all available commands.

### Development Setup
```powershell
# Create virtual environment and install dependencies
make install

# Or manually:
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Running the Application
```powershell
# Start FastAPI backend (development mode with reload)
make run-api

# Start Streamlit dashboard (separate terminal)
make run-dashboard
```

### Testing
```powershell
# Run all tests
make test

# Run with coverage report
make test-cov

# Run specific test file (manual)
pytest tests/test_orchestrator.py -v

# Run specific test function (manual)
pytest tests/test_prioritizer.py::test_priority_score_calculation -v
```

### Code Quality
```powershell
# Format code with black and isort
make format

# Lint with flake8
make lint

# Type checking with mypy
make typecheck

# Run all quality checks
make quality
```

### Database Management
```powershell
# Initialize database (when implemented)
make db-init

# Create new migration
make db-migrate MSG="Description of changes"

# Apply migrations
make db-upgrade

# Rollback one migration
make db-downgrade
```

### Git Workflow
```powershell
# Check status
make git-status

# Pull latest changes
make git-pull

# Add, commit, and push all changes
make git-push MSG="Your commit message"
```

---

## 🏗️ Architecture Overview

### System Flow
The system operates on an **event-driven batch messaging model**:

1. **Cancellation occurs** → Logged manually or via future EHR integration
2. **Orchestrator activates** → Queries waitlist and calculates priority scores
3. **Batch SMS sent** → Top N patients (default 3) receive simultaneous offers with hold timer (default 7 min)
4. **Race-safe confirmation** → First "YES" wins via SELECT FOR UPDATE locking
5. **Others notified** → Remaining patients told slot is taken
6. **Next batch** → If no response, send to next priority group after hold expires

### Key Components

**Core Logic** (`app/core/`):
- **orchestrator.py** - Main coordinator; manages batch sending, hold timers, and state transitions
- **prioritizer.py** - Implements scoring algorithm (urgent flag + manual boost + appointment proximity + seniority)
- **scheduler.py** - APScheduler background jobs for timer expiration and cleanup
- **templates.py** - SMS message templates with time zone formatting

**Infrastructure** (`app/infra/`):
- **models.py** - SQLAlchemy ORM models (6 core tables: patient_contact, provider_reference, waitlist_entry, cancellation_event, offer, message_log)
- **db.py** - Database connection pooling and session management
- **twilio_client.py** - Wrapper for Twilio API with signature verification and delivery tracking
- **settings.py** - Pydantic settings loaded from environment variables

**API Endpoints** (`app/api/`):
- **cancellations.py** - POST /admin/cancel (manual cancellation entry)
- **sms_webhook.py** - POST /sms/inbound (handles YES/NO responses)
- **status_webhook.py** - POST /twilio/status (delivery receipt callbacks)
- **waitlist_api.py** - CRUD operations for waitlist management

**Utilities** (`utils/`):
- **time_utils.py** - **CRITICAL**: All timezone conversions (UTC storage ↔ Central Time display)
- Other shared utilities for config, logging, database helpers

### Database Schema Summary
See PROJECT_PLAN.md for full schema. Key relationships:
- `patient_contact` ← `waitlist_entry` (one-to-many)
- `cancellation_event` ← `offer` (one-to-many)
- `offer` → `message_log` (one-to-many)
- All tables use PostgreSQL ENUM types for state management
- **All datetime fields are TIMESTAMP WITH TIME ZONE stored in UTC**

---

## Technology Stack Rules

### Required Technologies
- **Python 3.11+** for all backend code
- **FastAPI** for REST API and webhook endpoints
- **PostgreSQL 14+** for data storage with TIMESTAMP WITH TIME ZONE
- **Twilio Programmable SMS** for HIPAA-compliant messaging
- **Streamlit** for internal dashboard
- **SQLAlchemy/SQLModel** for ORM
- **APScheduler** for hold timers and background jobs
- **pytest** for testing

### Hosting Environment
- **Windows Server** (on-premises)
- Use **PowerShell** commands, not bash
- Paths use backslashes (e.g., `C:\Projects\clinic_cancellation_chatbot\`)
- Consider Windows service deployment (NSSM or Docker Desktop)

---

## Code Style & Conventions

### Python Standards
- Follow **PEP 8** style guide
- Use **type hints** for all function signatures
- Use **docstrings** for all public functions and classes
- Prefer **async/await** for I/O operations
- Use **Pydantic** models for data validation
- Keep functions focused and single-purpose

### Naming Conventions
- **Files:** `snake_case.py`
- **Classes:** `PascalCase`
- **Functions/variables:** `snake_case`
- **Constants:** `UPPER_SNAKE_CASE`
- **Database tables:** `snake_case` (singular or plural as appropriate)
- **Enum values:** `lowercase` (for PostgreSQL compatibility)

### Project Structure
- All application code in `app/` directory
- Utilities in `utils/` (reusable across projects)
- Scripts in `scripts/` (ETL, migrations, seeding)
- Tests mirror source structure in `tests/`
- Configuration in `configs/` directory
- Data files in `data/` subdirectories (inbox, staging, archive, logs)

---

## Database Rules

### Schema Guidelines
- Use **PostgreSQL ENUM types** for status fields
- Always use **TIMESTAMP WITH TIME ZONE** for datetime fields
- Default timestamps to `NOW()` for `created_at` fields
- Add **indexes** on foreign keys and frequently queried columns
- Use **CASCADE** carefully (only where appropriate)
- Include `notes` TEXT field for flexibility

### Time Zone Handling
- **CRITICAL:** Store all timestamps in **UTC** in database
- Convert to **America/Chicago (Central Time)** for display and SMS
- Use `time_utils.py` helpers for all conversions:
  ```python
  from utils.time_utils import now_utc, to_local, to_utc
  ```
- Never perform date arithmetic without time zone awareness

### Data Retention
- Message bodies rotated after **90 days** (keep metadata)
- Archive inactive waitlist entries after **180 days**
- Keep cancellation events indefinitely (audit trail)

---

## HIPAA Compliance Rules

### SMS Message Content
- **NEVER** include diagnosis, condition, or reason for visit
- Use **initials or first name only** (no full names)
- Keep messages **generic and neutral**
- Example: "TPCCC: An earlier appointment opened tomorrow at 10:00 AM..."
- Include **STOP** keyword instructions in confirmations

### Data Handling
- Minimize PHI stored in database
- Use **least privilege** database accounts
- Log all system actions for audit trail
- Implement **webhook signature verification**
- Encrypt database backups
- Use Twilio BAA-compliant messaging service

### Audit Trail
- Log all offers sent/received in `message_log` table
- Track all manual boosts and staff actions
- Record Twilio delivery statuses
- Store raw webhook payloads in JSONB for investigation

---

## Messaging Rules

### Twilio Best Practices
- Use **Messaging Service SID** (not raw phone number)
- Always capture **status callbacks** for delivery tracking
- Verify **webhook signatures** to prevent spoofing
- Handle **STOP, UNSTOP, HELP, START** keywords automatically
- Respect **opt-out status** from database
- Use **A2P 10DLC** registered messaging service

### SMS Templates
- Keep under **160 characters** when possible
- Use **clear call-to-action** (YES/NO)
- Include **expiration time** for offers
- Always identify sender as **TPCCC**
- Format times in **12-hour format with timezone** (e.g., "10:00 AM CT")

### Contact Hours
- Default: **08:00 - 20:00 Central Time**
- Suppress overnight messages
- Make configurable via environment variable

---

## Orchestration Rules

### Batch Processing
- Default batch size: **3 patients** per round
- Hold timer: **7 minutes** default
- Both values configurable via `.env`

### Priority Scoring
- Use deterministic algorithm (no randomness in scoring)
- Components:
  - Urgent flag: +30
  - Manual boost: 0-40 (admin controlled)
  - Days until current appointment: 0-20
  - Waitlist seniority: 0-10
- Tie-breaker: earliest `joined_at` timestamp

### Race Condition Handling
- Use **SELECT FOR UPDATE** for cancellation reservation
- Atomic confirm/cancel operations in single transaction
- Lock token (UUID) for offer uniqueness
- Expire pending offers after hold window

---

## Testing Rules

### Test Coverage Requirements
- Unit tests for all business logic (prioritizer, templates)
- Integration tests for orchestration flows
- End-to-end tests with seeded data
- Webhook tests with mocked Twilio responses

### Test Data
- Use **faker** library for realistic test data
- Maintain `scripts/seed_data.py` for consistent fixtures
- Use **+1555** phone numbers for testing (Twilio test numbers)
- Never commit real patient data

---

## Configuration Rules

### Environment Variables
- **NEVER** commit `.env` file to git
- Provide `.env.example` with placeholders
- Use `{{SECRET_NAME}}` format for sensitive values
- Load config via `python-dotenv` in `settings.py`
- Validate all required variables on startup

### Secrets Management
- Store credentials in environment variables
- Use Windows Credential Manager or similar for production
- Rotate Twilio auth tokens periodically
- Never log sensitive values (mask in logs)

---

## Documentation Rules

### Maintain These Files
- **PROJECT_CHARTER.md** - High-level goals and scope
- **PROJECT_PLAN.md** - Technical roadmap and milestones
- **README.md** - Getting started and overview
- **CHANGELOG.md** - Version history (Keep a Changelog format)
- **WARP.md** - This file (project-specific AI rules)

### Code Comments
- Add docstrings to all public functions
- Comment complex business logic
- Explain "why" not "what" in comments
- Keep comments up-to-date with code changes

### Commit Messages
- Use conventional commits format:
  - `feat:` new feature
  - `fix:` bug fix
  - `docs:` documentation changes
  - `refactor:` code restructuring
  - `test:` test additions/changes
  - `chore:` maintenance tasks

---

## Development Workflow

### Git Practices
- Work in feature branches when appropriate
- Write descriptive commit messages
- Don't commit sensitive data or logs
- Use `.gitignore` for environment-specific files

### Dependency Management
- Maintain `requirements.txt` with pinned versions
- Document major dependencies in README
- Test after upgrading dependencies
- Use virtual environment for isolation

---

## Deployment Rules

### Pre-Production Checklist
- [ ] All tests passing
- [ ] Twilio BAA signed
- [ ] Database migrations applied
- [ ] Environment variables configured
- [ ] Webhook tunnel established (Cloudflare/Tailscale)
- [ ] Staff training completed
- [ ] Runbook reviewed

### Monitoring
- Review Twilio delivery rates daily
- Check error logs daily
- Monitor fill rate metrics
- Weekly message log audit
- Monthly dependency updates

---

## Integration with Other Projects

### Reusable Utilities
This project shares utility modules with other TPCCC projects:
- `utils/db_utils.py` - Database connection helpers
- `utils/log_utils.py` - Logging configuration
- `utils/config_loader.py` - Environment variable loading
- `utils/time_utils.py` - Time zone conversions

### Provider Database
- Links to existing TPCCC provider database
- Read-only access to `provider_reference` table
- Consider schema-based separation if same PostgreSQL instance

---

## Anti-Patterns to Avoid

### Do NOT:
- Store PHI unnecessarily (diagnosis, full medical record)
- Send messages outside contact hours
- Ignore opt-out status
- Use blocking I/O in FastAPI handlers
- Hard-code configuration values
- Commit secrets to git
- Use local time without explicit timezone
- Perform database queries in loops (N+1 problem)
- Ignore Twilio webhook signatures

---

## Questions to Ask Before Implementing

1. **Does this store minimal PHI?**
2. **Is this time zone-aware?**
3. **Does this respect opt-out status?**
4. **Is this race-safe for concurrent requests?**
5. **Does this handle Twilio failures gracefully?**
6. **Is this testable?**
7. **Is this documented?**
8. **Does this follow the existing project structure?**

---

## Future Considerations

### Phase 2 (Greenway Integration)
- Design for eventual EHR connectivity
- Keep manual entry path as fallback
- Maintain clean separation of concerns

### Scalability
- Current design targets single clinic with ~50 daily cancellations
- Consider message queuing if volume increases significantly
- Plan for multi-location support in schema

---

## Contact & Support

- **Project Owner:** Jonathan Ives (@dollythedog)
- **GitHub:** https://github.com/dollythedog/clinic_cancellation_chatbot
- **Documentation:** See `docs/` directory for runbooks and SOPs

---

**This file should be updated as project patterns and conventions evolve.**
