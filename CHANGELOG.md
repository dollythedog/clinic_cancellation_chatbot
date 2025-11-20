# Changelog

All notable changes to the Clinic Cancellation Chatbot project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

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

## [0.4.0] - 2025-11-20

### Added - Production Testing & Admin Controls

**Production Testing Complete:**
- ✅ End-to-end testing with real Twilio SMS
- ✅ Full YES/NO response workflow validated
- ✅ Automatic next-batch triggering on patient decline
- ✅ Race-safe slot claiming confirmed working
- ✅ Cloudflare Tunnel webhook integration tested
- ✅ Message audit logging verified
- ✅ Dashboard real-time updates confirmed

**Comprehensive Admin Controls:**

*Quick Action Buttons (Dashboard View):*
- Delete button: Permanently remove cancellation and related offers
- Void button: Mark cancellation as aborted, expire pending offers
- Cancel Offer button: Cancel individual pending offers

*Quick Action Buttons (Waitlist View):*
- Edit button: Opens edit form for patient details
- Deactivate button: Remove patient from active waitlist
- Delete button: Permanently delete patient (if no offers exist)

*Enhanced Admin Tools Tab (5 sections):*
1. Manual Boost: Adjust patient priority (0-40 points)
2. Remove from Waitlist: Deactivate patients
3. Bulk Operations:
   - Expire old pending offers (by hours)
   - Reactivate all inactive patients
4. Cancellation Management:
   - View/filter all cancellations by status
   - Delete or void cancellations in bulk
5. System Cleanup:
   - Clear all test data (cancellations, offers, messages)
   - Delete old message logs (by days)

*Patient Edit Form:*
- Edit display name, urgent flag, manual boost, notes
- Form validation and error handling

**Helper Scripts:**
- Created `scripts/process_latest_cancellation.py` for manual orchestrator triggering
- Useful for development and troubleshooting

**Deployment Documentation:**
- Added production deployment section to README
- NSSM service installation commands for 3 services
- Deployment workflow with git pull
- Access points documentation

### Fixed
- Dashboard import error: `local_to_utc` → `make_aware()` + `to_utc()`
- Streamlit form button error: Moved button outside form
- CancellationStatus enum: Changed `CANCELLED` → `ABORTED` (3 locations)
- Dashboard enum filter: Updated to use valid status values

### Changed
- Dashboard now handles timezone conversion properly for cancellation creation
- Admin Tools tab expanded from 2 to 5 sections
- Waitlist patient cards now include action buttons

### Testing Results
- ✅ SMS delivery: 100% success rate via Twilio
- ✅ Webhook processing: Cloudflare Tunnel working
- ✅ YES response: Confirmation + slot filled correctly
- ✅ NO response: Immediate next batch (no 30min wait)
- ✅ Dashboard updates: Real-time display working
- ✅ Admin functions: Delete, void, edit all working

**Status:** 🚀 Production Ready - Validated on Windows laptop, ready for server deployment

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
