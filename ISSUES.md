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

> **Grandfather note (2026-04-23, Slice 2026-04-23-05):** The three F821
> findings are now grandfathered via `pyproject.toml`
> `"app/api/sms_webhook.py" = ["F821"]` so the ruff CI gate turns on
> clean. This does **not** fix the bug — it only prevents the lint-surface
> noise from blocking the gate. The underlying runtime `NameError` still
> fires on STOP / HELP / error reply paths. **APP-03 is still required to
> fix the bug with a Twilio-signature-middleware regression test covering
> all three reply paths.** When APP-03 lands, the owning slice must
> remove the `"app/api/sms_webhook.py" = ["F821"]` entry in the same
> commit as the code fix.

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

---

### 📌 Closure Update — Slice 2026-04-23-05 (WBS QA-01)

Build Slice 2026-04-23-05 activated the ruff CI gate (`ruff check .`,
`ruff format . --check`) via `.github/workflows/lint.yml` after applying
the "fix what's cheap, grandfather what's risky" Option-4 discipline (see
DECISIONS 2026-04-23 and Build-Packets.md Packet 2026-04-23-05 Scope
Amendment). Disposition of every entry in this section at slice close:

| Rule | Count | Disposition at Slice-5 close |
|---|---|---|
| B008 | 8 | **CLOSED** — all 8 fixed via `Annotated[..., Depends(...)]` migration (`app/infra/db.py` + the 3 API modules) |
| E712 | 15 | **CLOSED** — all 15 swapped to `.is_(…)` form (`app/core/prioritizer.py` 4 + `dashboard/app.py` 11); test coverage in `tests/test_prioritizer_query_forms.py` |
| UP042 | 4 | **GRANDFATHERED** via `pyproject.toml` `"app/infra/models.py" = ["UP042"]`; owning slice (data-layer cleanup) removes the ignore when it migrates the four enums to `StrEnum` with DB + API JSON roundtrip tests |
| E402 | 5 | **CLOSED** — `app/infra/models.py:43` reordered; `scripts/test_all_messages.py:17,19,30,31` marked with trailing `# noqa: E402` (standard idiom for the `sys.path.insert(...)` hack) |
| F821 | 3 | **GRANDFATHERED** via `pyproject.toml` `"app/api/sms_webhook.py" = ["F821"]`; this is BUG-001, owned by APP-03. The ignore exits when APP-03 fixes BUG-001 with a Twilio-signature-middleware regression test |
| F841 | 4 | **PARTIAL CLOSE** — 2 of 4 fixed (`scripts/seed_test_real.py:132` delete, `dashboard/app.py:246` `created_local` delete); 2 grandfathered via `pyproject.toml` `"app/core/orchestrator.py" = ["F841"]`; the orchestrator hits exit when the `_cancel_other_offers` completion slice finishes the SMS-notification send path |

**Gate state at slice close:** `ruff check .` reports 0 findings (down
from 39); `ruff format . --check` reports 0 files need reformatting
(down from 6 at Slice 4 close, which was itself down from 23 at Slice 2
close). The CI gate is live and blocks merges on any new finding or
any new format drift in any file.

**What stays open in this section:** Only the **GRANDFATHERED** rows
above (UP042 × 4 and F841 × 2 — 6 findings total) remain live. They
survive here as reminders of the owning-slice exit paths. Every other
row is documentation-of-history only.

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

### Slice 2 baseline reconciliation (2026-04-20)

During Build Slice 2026-04-20-02 evaluation (Revise Attempt 0), the ruff-check finding count came in at **39**, not the 35 reported at Slice 1 close. No new findings were introduced by the Slice-2 code; the delta is pure counting drift in Slice 1's closeout. The per-rule corrections:

| Rule | Slice 1 count | Actual | Delta | Note |
|---|---|---|---|---|
| B008 | 8 | 8 | 0 | accurate |
| E712 | 14 | 15 | +1 | one extra hit in `dashboard/app.py` (the 11th dashboard finding) |
| UP042 | 4 | 4 | 0 | accurate |
| E402 | 5 | 4 | −1 | `scripts/test_all_messages.py` has 3 hits, not 4 — Slice 1 double-counted |
| F821 | 3 | 3 | 0 | accurate (BUG-001 cross-listed) |
| F841 | 1 | 4 | +3 | additional pre-existing hits at `app/core/orchestrator.py:528` (`patient`), `app/core/orchestrator.py:529` (`message`), and `scripts/seed_test_real.py:132` (`patients`). The two orchestrator hits are in the dangling incomplete body of `_cancel_other_offers` on HEAD; the `seed_test_real.py` hit is a trivial unused local. |
| **Total** | **35** | **39** | **+4** | |

Ownership disposition for the newly-surfaced items:
- `orchestrator.py:528-529` (F841 × 2) → APP-07 or a dedicated `_cancel_other_offers` completion slice (the function body is incomplete on HEAD; those two locals will be used once the SMS-notification send path is finished)
- `seed_test_real.py:132` (F841 × 1) → QA-01 (trivial delete)
- `dashboard/app.py` 11th E712 → APP-08 (the dashboard-findings group grows from 10 to 11; per-file ignore disposition unchanged)

### RUFF-FORMAT-BASELINE-23 → RUFF-FORMAT-BASELINE-6 → CLOSED (2026-04-23 by Slice 5)

**Status:** Closed — resolved by **Packet 2026-04-23-05 (Slice 5, WBS QA-01)** on 2026-04-23. The remaining 6 ruff-format-baseline files (`dashboard/app.py`, `scripts/create_test_cancellation.py`, `scripts/direct_test.py`, `scripts/process_latest_cancellation.py`, `scripts/seed_test_real.py`, `scripts/simulate_response.py`) were reformatted clean by `ruff format .` in the same slice that activated the CI gate. Combined with Slice 4's 17-file LF-normalization pass, this resolves the full original 23-file baseline identified at Slice 2. Post-slice verification: `ruff format . --check` reports "38 files already formatted, 0 would be reformatted."

**Update (2026-04-23 — Slice 4 / Packet 2026-04-23-04 / WBS QA-04 closeout):** The baseline has shrunk from 23 to **6** as an incidental side effect of the EOL normalization. Slice 4's forced working-tree re-checkout (`git rm --cached -r . && git reset --hard`) rewrote every tracked file with LF line endings per the new `.gitattributes` `* text=auto eol=lf` policy. Ruff's format engine evaluates line endings when computing its canonical output; with LF working-tree content now matching what ruff emits by default, 17 of the 23 previously-flagged files pass `ruff format . --check` cleanly without any explicit reformatting.

**Remaining 6 files (all Python, still pre-existing formatting drift — out of scope for any slice except a dedicated QA pass):**
`dashboard/app.py`, `scripts/create_test_cancellation.py`, `scripts/direct_test.py`, `scripts/process_latest_cancellation.py`, `scripts/seed_test_real.py`, `scripts/simulate_response.py`.

**Owning slice:** unchanged — **QA-01** (quality-automation hardening). One `ruff format` run on those 6 files closes the remainder.

**Priority:** 🟢 Low (down from 🟡 Medium pre-Slice-4 — 74% of the baseline is already resolved).

---

### RUFF-FORMAT-BASELINE-23 (2026-04-20) — original finding, preserved for history

**Finding:** `ruff format . --check` reports 23 files would be reformatted. All 23 are in files untouched by Slice 2. The ten files authored or edited by Slice 2 (`app/main.py`, `app/infra/settings.py`, `app/infra/logging_config.py`, `app/infra/twilio_client.py`, `app/core/orchestrator.py`, `app/core/scheduler.py`, `app/api/admin.py`, `app/api/sms_webhook.py`, `app/api/status_webhook.py`, `tests/test_logging_config.py`) all report as "already formatted."

**Affected files (23):**
`app/api/__init__.py`, `app/core/__init__.py`, `app/core/prioritizer.py`, `app/core/templates.py`, `app/infra/__init__.py`, `app/infra/db.py`, `app/infra/models.py`, `dashboard/app.py`, `scripts/create_test_cancellation.py`, `scripts/direct_test.py`, `scripts/log_note.py`, `scripts/migrations/env.py`, `scripts/process_latest_cancellation.py`, `scripts/seed_sample_data.py`, `scripts/seed_test_real.py`, `scripts/setup_db.py`, `scripts/simulate_response.py`, `scripts/test_all_messages.py`, `tasks.py`, `tests/conftest.py`, `tests/test_settings.py`, `utils/__init__.py`, `utils/time_utils.py`.

**Classification:** Pre-existing formatting drift. Slice 1's closeout claimed "31 files already formatted" — that claim was either mistaken or the ruff version drifted between sessions. Slice 2 did not introduce any of these failures; they are all in files Slice 2 did not edit.

**Suggested fix (original):** One line — `ruff format .` — in a scoped QA slice. Not appropriate to carry in a behavior slice.

**Partial resolution 2026-04-23:** 17 of the 23 files closed by Slice 4's LF normalization side effect — see the RUFF-FORMAT-BASELINE-6 update above.

**Owning slice:** **QA-01** (quality-automation hardening) for the remaining 6.

### RUFF-ORDER-SWAP (2026-04-20) — import-order sensitivity of mechanical logger swaps

**Finding:** Slice 2 swapped `import logging` → `import structlog` across 8 files. The initial `ruff check .` at Stage 3 reported 75 errors; after `ruff check --fix` it reported 39 (back to the Slice-1 baseline). The 36-error delta that `--fix` absorbed was almost certainly auto-fixable I-rule (import ordering) and UP-rule (pyupgrade) violations introduced by the mechanical swaps.

**Classification:** Process improvement, not a code defect. Acceptance check 8 (`ruff check .` passes with no new violations) is evaluated against the post-fix state and passed.

**Suggested fix:** Add a note to `DECISIONS.md` or to the build-execution skill that future mechanical-swap slices (import replacements, library migrations) should run `ruff check --fix && ruff format .` during execution rather than leaving the cleanup for the evaluate gate.

**Owning slice:** Optional — may be folded into QA-01 or a DECISIONS.md addition with the other Slice-2 baseline reconciliations. Not blocking.

**Resolution:** Closed by Slice 3 DECISIONS.md entry `2026-04-23 — Promote inline ruff check --fix && ruff format to an execution-checklist item`. Build-execution's Suggested Validation Commands block now leads with inline ruff; Slice 3's Revise Attempt 1 honored the new rule (pre-handoff ruff reported "All checks passed! 3 files left unchanged").

---

### PYTEST-DEPRECATION-WARNINGS (2026-04-23) — two pre-existing deprecation warnings emitted on every pytest run

**Discovered:** Surfaced formally during Slice 5 (Packet 2026-04-23-05) evaluate; present in every pytest run since at least Slice 4 and mentioned casually in the Slice 4 CHANGELOG closure note. Slice 5 captures them as a proper ISSUES entry for the first time.

**Finding:** Every `pytest` invocation on the suite emits the same two `warnings summary` entries:

1. `app/infra/models.py:38 MovedIn20Warning: The declarative_base() function is now available as sqlalchemy.orm.declarative_base(). (deprecated since: 2.0)` — the legacy `from sqlalchemy.ext.declarative import declarative_base` import site at `app/infra/models.py:34`. Fix is a one-line import swap to `from sqlalchemy.orm import declarative_base`.
2. `app/api/admin.py:52 PydanticDeprecatedSince20: Support for class-based config is deprecated, use ConfigDict instead.` — the `class CancellationResponse(BaseModel)` inner `class Config:` block at `app/api/admin.py:64-65`. Fix is replacing the inner class with `model_config = ConfigDict(from_attributes=True)`.

**Classification:** Low-priority quality debt. Neither warning affects correctness today. Both name upstream APIs that WILL be removed in a future major version of their respective libraries (SQLAlchemy 3.0 and Pydantic V3) — the warnings are the libraries giving early notice that silent breakage is scheduled. Both fixes are mechanical and safe; what holds them off is purely slice-ownership discipline.

**Owning slices:**

- **MovedIn20Warning** → the dedicated **data-layer cleanup slice** (the same slice that will migrate UP042 `class X(str, enum.Enum)` → `StrEnum` in `app/infra/models.py`). Fold the `declarative_base` import swap into that slice so the data-layer file gets one coherent pass.
- **PydanticDeprecatedSince20** → a **Pydantic-V2-idiom sweep** slice. The project likely has multiple class-based `Config` sites (admin.py is only the one surfaced by pytest's warning filter). A sweep slice should find all `class Config:` inner classes inside `BaseModel` subclasses across `app/` and migrate them to `model_config = ConfigDict(...)` in a single pass, plus any other Pydantic-V1 idioms (e.g., `@validator` → `@field_validator`, `BaseSettings(env_file=...)` → `SettingsConfigDict(...)`). This is not an existing WBS item; it will surface as a new ISSUES-driven slice proposal when the data-layer cleanup slice runs or shortly thereafter.

**Suggested fix (per warning):**

1. In `app/infra/models.py`, replace the line `from sqlalchemy.ext.declarative import declarative_base` with `from sqlalchemy.orm import declarative_base`.
2. In `app/api/admin.py`, in the `CancellationResponse(BaseModel)` class, replace:
   ```python
   class Config:
       from_attributes = True
   ```
   with:
   ```python
   from pydantic import ConfigDict
   model_config = ConfigDict(from_attributes=True)
   ```
   (and sweep the rest of the codebase for matching `class Config:` blocks; expect 1–5 call sites given the project's size).

**Priority:** 🟢 Low. Neither fix is runtime-critical. Both should land inside their respective owning slices to preserve slice-coherence discipline. Do NOT fold into QA-01 or any other lint-hygiene slice — these are real code edits on application files, not lint-surface decisions.

**Cross-reference:** Both warnings are visible in any Slice 5 or later pytest run. Slice 5 evaluate paste-back shows them at the tail of the "warnings summary" section (2 warnings, 0 failures, 24 passed).

---

## 📐 EOL & Repository Hygiene

*No open issues in this category — the two entries previously listed here (`RUFF-CRLF-BASELINE-47` and `EOL-AUTOCRLF-ROOT-CAUSE`) were resolved by Build Slice 2026-04-23-04 (WBS QA-04). Their closed forms live under `## ✅ Closed / Resolved Issues` below.*

---

## 🔧 Build-System & Skill-Level Follow-Ups

### BUILD-CLOSEOUT-COMMIT-GATE (2026-04-23) — build-closeout should verify codebase commit state before close

**Finding:** Slice 3 (Packet 2026-04-21-03, WBS APP-07) closed on 2026-04-23 in project-management state — Design Schematic marked `APP-07 ✓`, README `## Build State` advanced to Closed, this ISSUES.md file gained the two Slice-3-discovered EOL entries (which Slice 4 subsequently closed), and Build-Packets.md got its Closeout Result block. But the actual codebase commit was never made. Slice 3's new code (`app/main.py` router wiring, `app/api/health.py`, `tests/test_health_endpoints.py`) sat in the working tree as uncommitted changes for the entire duration of Slice 4 (three days), and was only captured in git when Slice 4's evaluate gate discovered the state inconsistency and routed the bundled Commit 1 (`48b49fa`) in lieu of the pristine Slice 4 atomic commit the packet had intended.

**Impact:**

- **Slice 4's "single atomic commit" constraint** was reinterpreted rather than satisfied literally. Slice 4's content contribution did land in one commit, but it was bundled with Slice 3's catch-up rather than standing alone.
- **Evaluate-gate rework.** Build-evaluate had to diagnose the bundled state, reroute Jonathan through a two-commit + re-checkout sequence (Commit 1 = bundled content; "Commit 2" degenerated to a `git rm --cached -r . && git reset --hard` because the index was already LF), and reinterpret AC4. Each step introduced extra round-trip latency and cognitive overhead.
- **Historical attribution.** Git log now shows Slice 3's code under Commit `48b49fa` ("Slice 3 codebase catch-up + Slice 4 pre-normalization") rather than a dedicated Slice 3 commit. A reader looking at Slice 3's scope in Build-Packets.md will not find a matching commit in `git log --grep "APP-07"` — the attribution bridge is the commit message body, not the subject line.

**Root cause:** The current build-closeout skill updates project-management state (Design Schematic, README, ISSUES, CHANGELOG, Build-Packets.md) but does not verify that the codebase itself is in a clean committed state matching the claimed closure. There is no commit-verification gate between "slice closed in docs" and "slice's code in git."

**Countermeasure (proposed — owning slice: a dedicated skill-edit pass on build-closeout):** Add a Step 1.5 "Commit Verification" between Step 1 (verify PASS) and Step 2 (mark WBS items Done). At Step 1.5, build-closeout should:

1. Run `git -C <codebase-path> status --porcelain=v1 -uall` and parse the output.
2. If the output is non-empty — i.e., any file listed as staged, modified, or untracked under the codebase path — stop and escalate. Do NOT mark WBS items Done, do NOT advance the README state, do NOT write the Closeout Result block. Return with a message like: *"Codebase has uncommitted work: [list]. Close operation blocked. Jonathan must commit (or explicitly stash with rationale) before the slice can close."*
3. Optionally: if Jonathan acknowledges the uncommitted state as intentional scope for a future slice, allow close with an explicit flag like `--allow-uncommitted "Rationale..."` which writes the rationale into the Closeout Result block.

**Secondary countermeasure (tactical, applies now):** Project-manager's Phase 2 status-read should read `git status` output for each App Development project in Executing → Build and flag projects whose working tree disagrees with their README Build State. This catches the Slice-3 kind of discrepancy at the next portfolio-briefing boundary rather than waiting for the next slice's evaluate gate.

**Owning slice / skill:** A dedicated `skill-creator`-driven edit pass on the build-closeout SKILL.md. Not blocking Iteration 1 exit. Not a code defect in the Cancellation Chatbot codebase itself — this is a Department-5 (skill system) process issue, tagged here only because Slice 4 surfaced it.

**Priority:** 🟡 Medium — no immediate runtime risk, but repeated occurrence will erode the slice-attribution integrity of the git history and compound evaluate-gate overhead on future slices.

---

## ✅ Closed / Resolved Issues

### RUFF-CRLF-BASELINE-47 (2026-04-23) — 47 text files drift LF → CRLF on every git operation

**Status:** Closed — resolved by **Packet 2026-04-23-04 (Slice 4, WBS QA-04)** on 2026-04-23. The repo-wide `.gitattributes` + `git add --renormalize .` commit brought all 47 affected files into `i/lf w/lf` alignment. Post-commit verification: `git ls-files --eol | grep "w/crlf"` returns only the two deliberately-CRLF `.ps1` files (`scripts/install_service.ps1`, `scripts/update_server.ps1`).

**Finding:** `git ls-files --eol` during Slice 3 Revise Attempt 1 identified **47 text files** with `i/lf w/crlf` drift in the working tree (repo index stored LF; working tree contained CRLF). Final `git diff --stat` on the four Slice-3-edited files surfaced the git warning: *"LF will be replaced by CRLF the next time Git touches it."* The warning confirmed the drift would recur on any `git checkout`, `git reset`, `git stash pop`, or similar operation that writes the file from index to working tree — making cosmetic one-off normalization insufficient.

**Affected files (47):** `.env.dev`, `.env.example`, `.gitignore`, `ISSUES.md`, `Makefile`, `PROJECT_CHARTER.md`, `PROJECT_PLAN.md`, `WARP.md`, `alembic.ini`, `app/api/__init__.py`, `app/core/__init__.py`, `app/core/prioritizer.py`, `app/core/templates.py`, `app/infra/__init__.py`, `app/infra/db.py`, `app/infra/models.py`, `docker-compose.yml`, `docs/DASHBOARD_TESTING.md`, `docs/DEPLOYMENT.md`, `docs/MOCK_TESTING_GUIDE.md`, `docs/PRESENTATION_STYLE_GUIDE.md`, `docs/SESSION_SUMMARY.md`, `docs/TESTING_CHECKLIST.md`, `docs/executive_presentation.html`, `docs/images/README.md`, `pyproject.toml`, `requirements.txt`, `scripts/create_test_cancellation.py`, `scripts/direct_test.py`, `scripts/install_service.ps1`, `scripts/log_note.py`, `scripts/migrations/env.py`, `scripts/migrations/script.py.mako`, `scripts/process_latest_cancellation.py`, `scripts/quick_setup.sql`, `scripts/schema.sql`, `scripts/seed_sample_data.py`, `scripts/seed_test_real.py`, `scripts/setup_db.py`, `scripts/simulate_response.py`, `scripts/test_all_messages.py`, `scripts/update_server.ps1`, `tasks.py`, `tests/conftest.py`, `tests/test_settings.py`, `utils/__init__.py`, `utils/time_utils.py`.

**Classification (at close):** Pre-existing repository-wide EOL drift exposed by Slice 3's large docs diffs. Not introduced by any single slice. Root cause diagnosed in companion entry `EOL-AUTOCRLF-ROOT-CAUSE` (also closed by this packet).

**Resolution mechanism:** One-line repo-level policy file (`.gitattributes`) plus `git add --renormalize .` in a single atomic commit — exactly the countermeasure proposed in `EOL-AUTOCRLF-ROOT-CAUSE`. Per-file `dos2unix` was explicitly not the chosen approach (cosmetic only; does not survive subsequent git operations).

---

### EOL-AUTOCRLF-ROOT-CAUSE (2026-04-23) — 5-Whys diagnosis of recurring CRLF drift

**Status:** Closed — resolved by **Packet 2026-04-23-04 (Slice 4, WBS QA-04)** on 2026-04-23. The proposed countermeasure (`.gitattributes` with `* text=auto eol=lf` + `*.ps1 text eol=crlf`, plus `git add --renormalize .`) was implemented verbatim. Recurrence is prevented by `.gitattributes` winning over each contributor's global `core.autocrlf` setting on every future checkout. The slice's DECISIONS.md entry documents the operator recovery procedure for any contributor who hits drift on a new workstation.

**Finding:** 5-Whys RCA conducted during Slice 3 Revise Attempt 1 (see `1 - Projects/Cancellation Chatbot/` session notes for full worksheet). Diagnosis walked from the observable symptom (`git diff` showing spurious CRLF changes) to the systemic root cause (repo had no explicit EOL policy).

**5-Whys chain (abbreviated):**

1. *Why did `git diff` report EOL conversion as meaningful changes?* Because files were LF in the index but CRLF in the working tree.
2. *Why was the working tree CRLF when the index was LF?* Because Windows git with `core.autocrlf=true` converts LF → CRLF on every checkout.
3. *Why is `core.autocrlf=true` in effect?* Because the Git-for-Windows installer sets it as the global default, and the setting was never reconciled with the repo's implicit LF convention.
4. *Why does the repo have no defense against each contributor's personal autocrlf?* Because there is no `.gitattributes` file declaring a canonical EOL policy.
5. *Why was `.gitattributes` never added?* Because the repo was scaffolded as a solo Windows project; every contributor (of one) had identical autocrlf settings so drift was invisible, and EOL policy only became visible once diffs grew large (Slice 3) and multi-environment contributors (Claude agents writing via a Linux mount producing LF) joined.

**Root cause statement:** *The repository lacks a `.gitattributes` file declaring a canonical EOL policy (`* text=auto eol=lf`), so working-tree EOL behavior is determined per-contributor by global `core.autocrlf` settings. Combined with Git-for-Windows' `autocrlf=true` default on the solo maintainer's workstation and multi-environment contributors writing with different EOL conventions, this produces recurring LF↔CRLF drift that pollutes `git diff` for any file the working tree has touched since its last LF-normalizing event.*

**Countermeasure (implemented):** Added `.gitattributes` at the repo root containing `* text=auto eol=lf` plus `*.ps1 text eol=crlf` (for PowerShell scripts that genuinely need CRLF). Committed `.gitattributes` and immediately ran `git add --renormalize .` to bring the existing index in line. Measurable success: `git ls-files --eol | grep "w/crlf"` returns zero non-PS1 lines after the normalization commit — verified at evaluate time.

**Entry criterion for every future slice (now enforced):** working tree has no `i/lf w/crlf` drift on files the slice will touch. If drift recurs on a new workstation, `git add --renormalize .` + a follow-up commit is the one-line operator recovery procedure (documented in `README.md` § Line-ending policy).

**Why previous implicit "fixes" failed:** Slice 3's per-file dos2unix normalization was cosmetic — it corrected the working tree but survived only until the next `git checkout` (the `git diff --stat` warning *"LF will be replaced by CRLF the next time Git touches it"* was git telling us exactly this). A repo-level policy file was the only durable fix.

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
