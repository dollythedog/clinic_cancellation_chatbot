# Changelog

All notable changes to the Clinic Cancellation Chatbot project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

*Slice 2026-04-08-01 closed 2026-04-19 after 1 revise attempt; all 8 Build Packet acceptance checks satisfied; WBS APP-01 / APP-02 / TST-03 marked Done on the Design Schematic. 35 pre-existing ruff findings logged to ISSUES.md (3 as severity=bug, 32 as cleanup) for triage in their owning slices (APP-03 / APP-04 / APP-08 / data-layer refactor).*

### Added — Build slice 2026-04-08-01 (Config Foundation, WBS APP-01 / APP-02 / TST-03)
- Explicit `validate_settings()` startup gate in `app/infra/settings.py`,
  invoked from the FastAPI lifespan hook; missing required environment
  variables now fail loudly with a clean stderr message naming the missing
  keys and pointing at `.env.example`
- `.env.example` relocated to the repo root with exact key parity to the
  `Settings` class; legacy `configs/.env.example` removed to prevent drift
- `scripts/migrations/env.py` (Alembic) now reads the validated
  `DATABASE_URL` from `app.infra.settings` instead of ad-hoc
  `os.getenv` + `load_dotenv("configs/.env")`; closes the last
  config-read seam outside the `Settings` class
- `tests/test_settings.py` covering: required-field non-defaulted invariant,
  `ValidationError` on missing required env vars, loud stderr error from
  `validate_settings()`, clean instantiation when required env present, and
  repo-root `.env.example` ↔ `Settings` class key parity
- `tests/conftest.py` providing test-safe defaults via
  `os.environ.setdefault` so module-level `Settings()` succeeds during
  pytest collection; individual tests exercising missing-env behavior
  clear these via `monkeypatch.delenv` + `_env_file=None`
- README Configuration section updated to point at root `.env.example`,
  document the four required keys, and explain the startup validation gate;
  Project Structure tree updated to remove stale `configs/.env.example`
  entry and surface the new root-level `.env.example` and `pyproject.toml`
- `ruff>=0.6.0` added to `requirements.txt` (prerequisite for the slice's
  lint acceptance checks)
- Minimal `pyproject.toml` created with `[tool.ruff]`, `[tool.ruff.lint]`,
  `[tool.ruff.format]`, and `[tool.pytest.ini_options]` sections; build /
  packaging metadata deferred to QA-01
- `DECISIONS.md` created at repo root capturing (a) deferral of the
  Streamlit auth secret from APP-01 to APP-08, (b) deliberate redundancy
  of module-level `Settings()` with explicit `validate_settings()`, and
  (c) Windows-mount null-byte write-path mitigation

### Added — Documentation (not part of Build slice 2026-04-08-01)
*The two entries below describe prior uncommitted documentation work
that was sitting in the working tree when this slice landed. They are
listed separately so Build Packet scope attribution stays clean. Commit
them as their own change or promote them under a dated release entry
when convenient.*
- Executive presentation enhancements (docs/executive_presentation.html)
  - Table of contents slide with clickable navigation blocks
  - Fragment grey-out animation (previous items fade when new ones appear)
  - Visual system components diagram with emoji icons
  - Compact slide formatting to prevent overflow
- Presentation style guide (docs/PRESENTATION_STYLE_GUIDE.md)
  - Complete color palette documentation
  - Component library with code examples
  - Animation and transition guidelines
  - Quick start template for future presentations

### Planned
- STOP/HELP keyword handling (Milestone 4)
- Comprehensive test suite
- Greenway EHR integration (Phase 2)
- Automatic appointment confirmation in EHR
- Multi-location support
- Voice call fallback for non-responsive patients
- ML-based patient preference learning (Phase 3)
- Multi-language SMS support
- Patient portal integration

---

## [0.3.0] - 2025-11-01

### Added - Milestone 3: Dashboard Complete

**Dashboard Features:**
- Streamlit dashboard with real-time monitoring
- Active cancellations view with countdown timers
- Waitlist leaderboard sorted by priority score
- Active offers display with patient information
- Message audit log with filtering (direction, phone)
- Admin tools for manual boost and waitlist management
- Auto-refresh functionality (30-second intervals)

**Sample Data:**
- Created seed_sample_data.py script for testing
- Generates 3 providers, 5 patients, 2 cancellations with offers
- Includes sample message log entries

**Testing Features:**
- ✅ ntfy.sh integration for mock SMS notifications
- ✅ Mock Twilio client sends push notifications to phone
- ✅ Real-time testing without SMS costs
- ✅ Perfect for development and QA workflows

### Fixed
- SQLAlchemy enum handling (added values_callable for Windows compatibility)
- Windows date formatting issues (removed %-I format specifier)
- Dashboard infinite rerun loop (auto-refresh now works correctly)
- Database enum queries now use .value instead of .name

### Changed
- Auto-refresh default changed to OFF (manual opt-in)
- Added time.sleep(30) to prevent immediate reruns

### Issues Closed
- #16 - Create Streamlit dashboard app
- #17 - Build active cancellations view
- #18 - Add waitlist leaderboard
- Fixed database enum compatibility bug
- Fixed Windows datetime formatting bug

**Milestone Progress:** 18/25 issues complete (72%)

---

## [0.2.0] - 2025-10-31

### Added - Milestone 2: Core Logic Complete

**Core Infrastructure:**
- SQLAlchemy ORM models for all 7 database tables
- Database connection and session management (db.py)
- Pydantic settings with environment variable configuration
- Twilio SMS API wrapper with mock mode support

**Business Logic:**
- Priority scoring algorithm (prioritizer.py) with 4-component calculation
- Offer orchestrator (orchestrator.py) with batch sending and hold timers
- SMS message templates (HIPAA-compliant, no PHI)
- APScheduler for background jobs (hold timer checks, priority recalc)

**API Endpoints:**
- Admin API: Manual cancellation entry, waitlist management
- SMS webhook: Inbound message handler (YES/NO/STOP/HELP)
- Status webhook: Twilio delivery status callbacks

**Features:**
- Race-safe slot reservation using SELECT FOR UPDATE
- Batch offering: 3 patients per batch with 7-minute hold timers
- Automatic priority recalculation (hourly background job)
- TCPA-compliant keyword handling (STOP, HELP)
- Comprehensive message audit logging
- Database setup script for existing PostgreSQL servers
- Docker Compose configuration for local development

### Fixed
- Pydantic v2 compatibility (added `extra="ignore"` to Config)
- SQLAlchemy 2.0 text() wrapper for raw SQL queries
- FastAPI Form data support (added python-multipart dependency)

### Documentation
- Updated README with database setup instructions
- Added database setup script (setup_db.py)
- Created .env.dev template for development
- Added run.py for easy server startup

### Issues Closed
- #8 - Implement ORM models
- #9 - Build prioritizer with scoring algorithm  
- #10 - Create orchestrator (batch sending, hold timers)
- #11 - Implement SMS webhook handler
- #12 - Implement status webhook handler
- #13 - Build manual cancellation entry endpoint
- #14 - Set up APScheduler
- #15 - Add race-safe reservation logic

**Milestone Progress:** 15/25 issues complete (60%)

---

## [0.1.0] - 2025-10-31

### Added - Initial Project Setup
- Created project repository and directory structure
- Initialized Git repository
- Created PROJECT_CHARTER.md with goals, scope, and success criteria
- Created PROJECT_PLAN.md with detailed implementation roadmap
- Created README.md with project overview and quick start guide
- Created CHANGELOG.md for version tracking
- Defined database schema for MVP:
  - `patient_contact` table
  - `provider_reference` table
  - `waitlist_entry` table
  - `cancellation_event` table
  - `offer` table
  - `message_log` table
- Documented prioritization algorithm
- Defined SMS message templates
- Outlined security and HIPAA compliance requirements

### Project Milestones Defined
1. **Milestone 1: Bootstrap** - Development environment setup
2. **Milestone 2: Core Logic** - Orchestration engine and webhooks
3. **Milestone 3: Dashboard** - Streamlit monitoring interface
4. **Milestone 4: Hardening** - HIPAA compliance and production readiness
5. **Milestone 5: Greenway Integration** - Future EHR connectivity

### Documentation
- Created comprehensive project charter
- Documented system architecture
- Defined technology stack (Python, FastAPI, PostgreSQL, Twilio, Streamlit)
- Outlined testing strategy
- Created configuration template

---

## Notes

### Version Numbering
- **Major version** (X.0.0): Breaking changes, major feature releases
- **Minor version** (0.X.0): New features, non-breaking changes
- **Patch version** (0.0.X): Bug fixes, minor improvements

### Release Schedule
- **MVP Target:** February 2026
- **Production Launch:** March 2026
- **Phase 2 (Greenway):** Q2 2026

---

## Legend

- `Added` - New features
- `Changed` - Changes in existing functionality
- `Deprecated` - Soon-to-be removed features
- `Removed` - Removed features
- `Fixed` - Bug fixes
- `Security` - Security-related changes
- `Performance` - Performance improvements
- `Documentation` - Documentation updates

---

[Unreleased]: https://github.com/dollythedog/clinic_cancellation_chatbot/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/dollythedog/clinic_cancellation_chatbot/releases/tag/v0.1.0
