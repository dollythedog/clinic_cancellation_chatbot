# 🎯 ISSUES.md

**Project:** Clinic Cancellation Chatbot  
**Last Updated:** 2025-11-01  
**GitHub Project:** [Clinic Chatbot MVP](https://github.com/users/dollythedog/projects/1)

---

## 📊 Overview

Track project issues locally and sync with GitHub Issues. Use `make issues-sync` to update from GitHub.

**Current Status:** 🚧 Milestone 3 Complete - Moving to Milestone 4 (Hardening)  
**Progress:** 18/25 issues closed (72%) | 3/5 milestones complete (60%)

---

## ✅ Milestone 1: Bootstrap - COMPLETE

### 🔴 High Priority (DONE)
- [x] Initialize Git repository (@dollythedog) ✅
- [x] [#1](https://github.com/dollythedog/clinic_cancellation_chatbot/issues/1) - Create project directory structure (@dollythedog) ✅
- [x] [#2](https://github.com/dollythedog/clinic_cancellation_chatbot/issues/2) - Set up virtual environment and requirements.txt (@dollythedog) ✅
- [x] [#3](https://github.com/dollythedog/clinic_cancellation_chatbot/issues/3) - Create .env.example with all config variables (@dollythedog) ✅

### 🟡 Medium Priority (DONE)
- [x] [#4](https://github.com/dollythedog/clinic_cancellation_chatbot/issues/4) - Define database schema (schema.sql) (@dollythedog) ✅
- [x] [#5](https://github.com/dollythedog/clinic_cancellation_chatbot/issues/5) - Set up Alembic for migrations (@dollythedog) ✅
- [x] [#6](https://github.com/dollythedog/clinic_cancellation_chatbot/issues/6) - Implement time_utils.py (UTC/Central conversion) (@dollythedog) ✅
- [x] [#7](https://github.com/dollythedog/clinic_cancellation_chatbot/issues/7) - Create basic FastAPI skeleton with health check (@dollythedog) ✅

---

## 📋 Milestone 2: Core Logic - COMPLETE

### 🔴 High Priority (DONE)
- [x] [#8](https://github.com/dollythedog/clinic_cancellation_chatbot/issues/8) - Implement ORM models (models.py) (@dollythedog) ✅
- [x] [#9](https://github.com/dollythedog/clinic_cancellation_chatbot/issues/9) - Build prioritizer.py with scoring algorithm (@dollythedog) ✅
- [x] [#10](https://github.com/dollythedog/clinic_cancellation_chatbot/issues/10) - Create orchestrator.py (batch sending, hold timers) (@dollythedog) ✅
- [x] [#15](https://github.com/dollythedog/clinic_cancellation_chatbot/issues/15) - Add race-safe reservation logic (SELECT FOR UPDATE) (@dollythedog) ✅

### 🟡 Medium Priority (DONE)
- [x] [#11](https://github.com/dollythedog/clinic_cancellation_chatbot/issues/11) - Implement SMS webhook handler (/sms/inbound) (@dollythedog) ✅
- [x] [#12](https://github.com/dollythedog/clinic_cancellation_chatbot/issues/12) - Implement status webhook handler (/twilio/status) (@dollythedog) ✅
- [x] [#13](https://github.com/dollythedog/clinic_cancellation_chatbot/issues/13) - Build manual cancellation entry endpoint (/admin/cancel) (@dollythedog) ✅
- [x] [#14](https://github.com/dollythedog/clinic_cancellation_chatbot/issues/14) - Set up APScheduler for hold timer expiration (@dollythedog) ✅

---

## 📋 Milestone 3: Dashboard - COMPLETE

### 🟡 Medium Priority (DONE)
- [x] [#16](https://github.com/dollythedog/clinic_cancellation_chatbot/issues/16) - Create Streamlit dashboard app (@dollythedog) ✅
- [x] [#17](https://github.com/dollythedog/clinic_cancellation_chatbot/issues/17) - Build active cancellations view (@dollythedog) ✅
- [x] [#18](https://github.com/dollythedog/clinic_cancellation_chatbot/issues/18) - Add waitlist leaderboard (sorted by priority) (@dollythedog) ✅
- [x] Display active offers with countdown timers (@dollythedog) ✅
- [x] Implement message audit log viewer (@dollythedog) ✅
- [x] Add manual boost controls (@dollythedog) ✅
- [x] Add waitlist CRUD operations (@dollythedog) ✅

---

## 📋 Milestone 4: Hardening

### 🔴 High Priority (HIPAA Critical)
- [ ] [#19](https://github.com/dollythedog/clinic_cancellation_chatbot/issues/19) - Implement STOP/HELP keyword handling (@dollythedog)
- [ ] [#20](https://github.com/dollythedog/clinic_cancellation_chatbot/issues/20) - Add opt-out tracking in database (@dollythedog)
- [ ] [#21](https://github.com/dollythedog/clinic_cancellation_chatbot/issues/21) - Create audit logging system (@dollythedog)
- [ ] [#22](https://github.com/dollythedog/clinic_cancellation_chatbot/issues/22) - Add rate limiting to prevent spam (@dollythedog)
- [ ] Implement exception handling and error recovery (@dollythedog)

### 🟡 Medium Priority
- [ ] Write comprehensive test suite (@dollythedog)
- [ ] Create deployment documentation (@dollythedog)
- [ ] Write staff runbook and SOP (@dollythedog)

---

## 🔐 Security & Compliance Checklist

### 🔴 High Priority (Blocking Launch)
- [ ] [#23](https://github.com/dollythedog/clinic_cancellation_chatbot/issues/23) - Sign Twilio BAA (@dollythedog)
- [ ] [#24](https://github.com/dollythedog/clinic_cancellation_chatbot/issues/24) - Complete A2P 10DLC registration (@dollythedog)
- [ ] [#25](https://github.com/dollythedog/clinic_cancellation_chatbot/issues/25) - Verify no PHI in SMS message bodies (@dollythedog)
- [ ] Enable database encryption at rest (@dollythedog)
- [ ] Implement TLS 1.2+ for all webhook connections (@dollythedog)
- [ ] Implement webhook signature verification (@dollythedog)

### 🟡 Medium Priority
- [ ] Create principle of least privilege DB user (@dollythedog)
- [ ] Document data retention policy (@dollythedog)
- [ ] Complete staff training (@dollythedog)

---

## 🚀 Milestone 5: Greenway Integration (Future)

### 🟢 Low Priority / Phase 2
- [ ] Evaluate Greenway API capabilities (@dollythedog)
- [ ] Choose integration approach (webhook/polling/CSV) (@dollythedog)
- [ ] Map Greenway fields to internal schema (@dollythedog)
- [ ] Build integration module (@dollythedog)
- [ ] Test end-to-end with production data (@dollythedog)
- [ ] Create monitoring and alerting (@dollythedog)

---

## 🐛 Bugs

### BUG-001 — `To` undefined in `app/api/sms_webhook.py` outbound-log branches
- **Severity:** bug (runtime `NameError`)
- **Discovered:** 2026-04-19 by build-evaluate on Build slice 2026-04-08-01 (Packet 2026-04-08-01)
- **Symptom:** Three outbound `MessageLog` builders reference an undefined name `To`:
  - `app/api/sms_webhook.py:147` — `from_phone=To,  # Our number`
  - `app/api/sms_webhook.py:177` — `from_phone=To,  # Our number`
  - `app/api/sms_webhook.py:228` — `from_phone=To,  # Our number`
- **Impact:** Any code path that reaches these branches (STOP/HELP handlers, error responder) raises `NameError` at runtime before the log entry is written. Outbound logging is currently broken for those three reply types.
- **Diagnosis:** Function signature only declares `From: str = Form(...)` and `Body: str = Form(...)` — there is no `To` parameter. The intent is almost certainly to log our own Twilio-owned number as `from_phone` on outbound replies, pulled from `settings.TWILIO_PHONE_NUMBER`.
- **Suggested fix:** Add `To: str = Form(None)` to the signature (Twilio webhooks post this as the destination of the inbound message, which equals our `from_phone` on outbound) OR replace the three `from_phone=To` sites with `from_phone=settings.TWILIO_PHONE_NUMBER`. The latter is less coupled to Twilio's form schema.
- **Owning slice:** APP-03 (Twilio signature middleware) or INT-03 (STOP/HELP keyword handling end-to-end). Needs a regression test that exercises each of the three reply paths and asserts the `MessageLog` entry is written.

---

---

## 🧹 Ruff Baseline Findings (2026-04-19)

Discovered when `ruff>=0.6.0` was first installed during Build slice
2026-04-08-01 (Config Foundation). None were introduced by that slice —
they are pre-existing code that became visible once ruff started running
in CI. Cataloged here per the Build Acceptance Checklist ("Missing items
become open issues in ISSUES.md — they are not silently deferred").

Total: **35 findings** across 6 files. Grouped by rule + owning slice.

### RUFF-B008 (8) — FastAPI `Depends(...)` in argument defaults
- **Finding:** `B008 Do not perform function call Depends in argument defaults`
- **Files:** `app/api/admin.py` (6× at :96, :177, :207, :275, :311, :326), `app/api/sms_webhook.py` (1× at :41), `app/api/status_webhook.py` (1× at :33)
- **Classification:** Framework false positive. `Depends(...)` in the default position is the canonical FastAPI pattern; the framework introspects it at route-registration time.
- **Suggested fix:** Per-file ruff ignore in `pyproject.toml` — `[tool.ruff.lint.per-file-ignores]` mapping `"app/api/*.py" = ["B008"]`. No code changes.
- **Owning slice:** QA-01 (ruff/pytest CI configuration) or a dedicated lint-baseline micro-slice.

### RUFF-E712 (14) — SQLAlchemy `== True` / `== False` in query filters
- **Finding:** `E712 Avoid equality comparisons to True/False`
- **Files:** `app/core/prioritizer.py` (4× at :138, :176, :231, :295), `dashboard/app.py` (10× across :144 ×2, :370, :412 ×2, :563, :797, :879 ×2, :921)
- **Classification:** SQLAlchemy idiom. `Column == True` compiles to the SQL predicate `active = TRUE`; replacing with the bare column reference changes the compiled SQL. Safe fix is per-file ignore.
- **Suggested fix:** `[tool.ruff.lint.per-file-ignores]` mapping `"app/core/prioritizer.py" = ["E712"]` and `"dashboard/app.py" = ["E712"]`. Reasoning captured in a DECISIONS.md entry.
- **Owning slices:** prioritizer findings → APP-04 (idempotency audit); dashboard findings → APP-08 (Streamlit auth wrapper, where dashboard/app.py is already in scope).

### RUFF-UP042 (4) — `class X(str, enum.Enum)` should be `StrEnum`
- **Finding:** `UP042 Class X inherits from both str and enum.Enum`
- **Files:** `app/infra/models.py:46 (CancellationStatus)`, `:55 (OfferState)`, `:66 (MessageDirection)`, `:73 (MessageStatus)`
- **Classification:** Real suggestion but data-layer risky. Python 3.11+ `enum.StrEnum` is functionally equivalent for most cases, but SQLAlchemy `Enum` column storage, JSON serialization, and string `in` comparisons can observe MRO differences.
- **Suggested fix:** Either (a) migrate to `enum.StrEnum` with regression tests that round-trip each enum value through the database and through API JSON responses, or (b) per-file ignore with rationale in DECISIONS.md.
- **Owning slice:** Dedicated data-layer cleanup slice (adjacent to DAT-05) before APP-04 idempotency work begins. Do not fold into an unrelated slice.

### RUFF-E402 (5) — Module-level import not at top of file
- **Finding:** `E402 Module level import not at top of file`
- **Files:** `app/infra/models.py:43` (`import enum` after a comment block), `scripts/test_all_messages.py:17, 19, 30, 31` (imports after `sys.path.insert(...)` hack)
- **Classification:** Mixed. `app/infra/models.py:43` is a simple reorder. The `scripts/test_all_messages.py` cluster is a legitimate `sys.path` manipulation and should be `# noqa: E402` with the standard "path adjustment required before downstream imports" comment.
- **Owning slice:** `models.py` entry → data-layer cleanup slice (alongside RUFF-UP042). `test_all_messages.py` entries → QA-01 or a dedicated script-hygiene micro-slice.

### RUFF-F821 (3) — Undefined name `To`
- See **BUG-001** under the Bugs section above. These are not style issues — they are runtime defects masquerading as lint findings.

### RUFF-F841 (1) — Unused local variable
- **Finding:** `dashboard/app.py:287 — created_local is assigned to but never used`
- **Classification:** Trivial dead-code cleanup.
- **Suggested fix:** Delete the assignment.
- **Owning slice:** APP-08 (Streamlit auth / dashboard touches).

### Triage summary
| Rule | Count | Disposition | Owning slice |
|---|---|---|---|
| B008 | 8 | Per-file ignore | QA-01 |
| E712 | 14 | Per-file ignore | APP-04 (4), APP-08 (10) |
| UP042 | 4 | Migrate to StrEnum with tests | Data-layer cleanup slice |
| E402 | 5 | Reorder + noqa | Data-layer cleanup (1), QA-01 (4) |
| F821 | 3 | **Fix as bug** (see BUG-001) | APP-03 or INT-03 |
| F841 | 1 | Delete dead assignment | APP-08 |
| **Total** | **35** | | |

*The 35 findings reconcile exactly with ruff's reported count. F821 entries are cross-listed under BUG-001 above for severity-tracking purposes.*

---

## 💡 Enhancements

### 🟢 Low Priority / Phase 3
- [ ] Patient preference learning (ML-based)
- [ ] Multi-language support
- [ ] Integration with patient portal
- [ ] Predictive cancellation modeling

---

## 📝 Notes

**Labels Used:**
- `milestone-1-bootstrap`, `milestone-2-core`, `milestone-3-dashboard`, `milestone-4-hardening`, `milestone-5-greenway`
- `priority-high`, `priority-medium`, `priority-low`
- `bug`, `enhancement`, `documentation`, `security`, `hipaa-critical`

**Sync Command:**
```bash
make issues-sync
```

**Create Issue:**
```bash
gh issue create --title "Task name" --label "priority-high,milestone-1-bootstrap" --milestone "MVP"
```

---

## 🎯 Current Focus

**✅ Milestone 1 COMPLETE:** Bootstrap (Issues #1-#7) - 100% done  
**✅ Milestone 2 COMPLETE:** Core Logic (Issues #8-#15) - 100% done  
**✅ Milestone 3 COMPLETE:** Dashboard (Issues #16-#18) - 100% done  
**🔜 Next Session:** Start Milestone 4 - Hardening (Issues #19-#22)  
**Blocker:** None

**Recent Accomplishments (2025-11-01):**
- ✅ Fixed SQLAlchemy enum handling for Windows compatibility
- ✅ Fixed Windows date formatting issues (%-I format)
- ✅ Fixed dashboard infinite rerun loop
- ✅ Created seed_sample_data.py for easy testing
- ✅ **Added ntfy.sh integration for mock SMS testing**
- ✅ Mock Twilio client now sends push notifications to phone
- ✅ Dashboard fully functional with real-time monitoring
- ✅ All core logic implemented and tested

**Recent Accomplishments (2025-11-05):**
- ✅ Enhanced executive presentation with table of contents
- ✅ Added fragment grey-out animation for progressive reveals
- ✅ Replaced ASCII diagram with visual component layout
- ✅ Fixed multiple slide overflow issues with compact formatting
- ✅ Created comprehensive presentation style guide (PRESENTATION_STYLE_GUIDE.md)
- ✅ Documented color palette, components, and animation patterns

---

## 📈 Quick Stats

- **Total Issues Created:** 25
- **Open Issues:** 7
- **Closed Issues:** 18 ✅
- **Milestones Complete:** 3 of 5 (60%)
- **High Priority Remaining:** 2
- **HIPAA Critical:** 6
