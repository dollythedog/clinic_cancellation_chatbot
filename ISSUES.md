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

*All tracked bugs are currently closed; see `## ✅ Closed / Resolved Issues` below for BUG-001's resolution.*

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
- **CLOSED 2026-04-23** by Build Slice 2026-04-23-07 (Packet 2026-04-23-07, WBS APP-03 + BUG-001). All three `from_phone=To` sites in `app/api/sms_webhook.py` fixed at source (replaced with `from_phone=settings.TWILIO_PHONE_NUMBER`); `"app/api/sms_webhook.py" = ["F821"]` entry removed from `pyproject.toml` `[tool.ruff.lint.per-file-ignores]` in the same commit. Regression tests in `tests/test_sms_webhook_outbound_log.py` cover all three reply paths (STOP / HELP / NO).
- See BUG-001 in the Closed / Resolved section below for the full root-cause and fix narrative.

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

### STREAMLIT-APPTEST-ASCII-ONLY-HARNESS (2026-04-23) — `AppTest.from_function` on Windows writes cp1252 but Streamlit reads UTF-8

**Finding:** `streamlit.testing.v1.AppTest.from_function(fn)` on Windows writes the harness function's source (via `inspect.getsource(fn)`) to a temp file using `open(path, "w")` without an explicit encoding. On Windows the default falls back to `locale.getpreferredencoding()` (cp1252 on US English Windows), which encodes characters like em-dash (`—`) as single bytes (0x97 for em-dash). Streamlit's script cache later reads the same temp file via `open(path, "r", encoding="utf-8")` and crashes with `UnicodeDecodeError: 'utf-8' codec can't decode byte 0x97 in position N: invalid start byte`.

**Discovery:** Build Slice 2026-04-23-08 (Packet 2026-04-23-08, WBS APP-08) Revise Attempt 1. The harness function `_auth_harness` in `tests/test_dashboard_auth.py` carried an em-dash in its docstring. Every AppTest-based test (three of them) failed at `at.run()` with the UnicodeDecodeError before any assertion could run.

**Cost:** 1 of the 3 revise attempts in Slice 8.

**Workaround (applies now):** Any function intended to be passed to `AppTest.from_function` must be **ASCII-only** in its body (including docstrings and inline comments). The discipline is two-part:

1. No non-ASCII characters (em-dashes, en-dashes, typographic quotes, unicode bullets / arrows, non-breaking spaces, etc.) anywhere in the harness function source.
2. No references to module-level names (constants, imports, variables). `AppTest.from_function` extracts only the function body and runs it as a standalone script; the surrounding module's globals are not in scope. See `STREAMLIT-APPTEST-HARNESS-SCOPE` for the sibling trap.

The `_auth_harness` docstring in `tests/test_dashboard_auth.py` documents both constraints inline so future maintainers don't re-introduce either.

**Root cause:** Upstream Streamlit bug. `AppTest.from_function`'s temp-file write should be explicit `encoding="utf-8"` to match the reader. Reproducible on any Windows machine running Python 3.11 + Streamlit 1.51.0.

**Countermeasure options:**

1. **File a Streamlit issue upstream.** Root-cause fix. Not blocking anything locally, but worth doing when there is time to spare.
2. **Lint rule.** Add a pre-commit or ruff custom rule that flags non-ASCII bytes inside any function passed to `AppTest.from_function`. Signal-to-noise is low (one slice surfaced this in 38 slices of history) and the workaround is documented, so probably not worth the custom-rule infrastructure.
3. **Test-writing guidance in `CLAUDE.md` / `WARP.md` / test-writing README.** Two-sentence note: "AppTest.from_function harness functions must be ASCII-only and must not reference module-level names. See `tests/test_dashboard_auth.py::_auth_harness` for a worked example." Lowest-effort, highest-leverage preventive.

**Owning slice / skill:** A small docs-only slice, or a passing comment in the next applicable AppTest-using slice. Not blocking Iteration 1 exit.

**Priority:** 🟡 Medium — the workaround is trivial once known, but the failure mode is confusing on first encounter (the UnicodeDecodeError points at a temp-file path the developer never wrote, which makes the trail cold). Documentation + a working example (this slice's `_auth_harness`) is the primary mitigation.

---

### STREAMLIT-APPTEST-SESSIONSTATE-NO-GET (2026-04-23) — `AppTest.session_state` has no `.get()` method; attribute access routes to key lookup

**Finding:** `streamlit.testing.v1.AppTest.session_state` is a `streamlit.runtime.state.session_state.SessionState` instance (or a close wrapper). It exposes `__getitem__` and `__contains__` but does **not** expose a `.get()` method. Calling `at.session_state.get(key)` routes through `SessionState.__getattr__` which interprets the attribute name as a session-state key and tries to look it up — i.e. `at.session_state.get("dashboard_authenticated")` literally tries to look up the key `"get"`, not the key `"dashboard_authenticated"`. The lookup of `"get"` fails and `AttributeError: get not found in session_state.` is raised.

**Discovery:** Build Slice 2026-04-23-08 (Packet 2026-04-23-08, WBS APP-08) Revise Attempt 2. Three AppTest-based tests in `tests/test_dashboard_auth.py` used `at.session_state.get(AUTH_SESSION_KEY)` as a convenient "exists-and-is-truthy?" check. All three failed at that line.

**Cost:** 1 of the 3 revise attempts in Slice 8.

**Workaround (applies now):** Use the `in` + `__getitem__` idiom explicitly:

```python
# Instead of: at.session_state.get(KEY)
# Use:
if KEY in at.session_state and at.session_state[KEY]:
    ...

# Or for a presence-only check:
assert KEY in at.session_state
```

All three AppTest tests in `tests/test_dashboard_auth.py` now use this idiom with inline comments explaining why.

**Root cause:** `SessionState` overrides `__getattr__` to support the `st.session_state.some_key` access pattern that Streamlit apps use idiomatically. The override treats every attribute access as a key lookup, which collides with dict-like methods (`.get`, `.setdefault`, `.keys`, `.items`, etc.). Streamlit's public documentation for `st.session_state` names `__getitem__` and `__contains__` as the supported operations; `.get` and friends are not documented as supported.

This is *by design* in Streamlit rather than a bug, but the failure mode (an `AttributeError` for `get` that looks like a naive dict would support it) is confusing.

**Countermeasure options:**

1. **Test-writing guidance in `CLAUDE.md` / `WARP.md` / test-writing README.** Paired with the `STREAMLIT-APPTEST-ASCII-ONLY-HARNESS` guidance above as a two-line "AppTest gotchas" section. Lowest-effort.
2. **Helper function.** Add `tests/_streamlit_helpers.py` with a `session_get(at, key, default=None)` shim that does the `in` + `[]` dance, and recommend it in the guidance. Might be overengineering for a single slice's worth of traps.

**Owning slice / skill:** Same as `STREAMLIT-APPTEST-ASCII-ONLY-HARNESS` — a small docs-only slice or a passing comment in the next AppTest-using slice.

**Priority:** 🟢 Low — workaround is trivial; the surprise is a one-time tax per developer learning AppTest.

---

### INFRA-NAMESPACE-SHADOWING (2026-04-23) — `app.infra/__init__.py` re-export shadows the `app.infra.settings` submodule attribute

**Finding:** During Build Slice 2026-04-23-07 (Packet 2026-04-23-07, WBS APP-03 / TST-02), the new middleware test fixture used the idiom `import app.infra.settings as settings_module; settings = settings_module.settings` to obtain the Settings singleton for test-time override. This raised `AttributeError: 'Settings' object has no attribute 'settings'` on every test's setup, consuming **2 of the 3 available revise attempts** before the real root cause was identified.

**Root cause:** `app/infra/__init__.py` contains `from app.infra.settings import settings`, which imports the Settings **instance** into the `app.infra` package's namespace under the name `settings`. This rebinds the attribute `app.infra.settings` (on the `app.infra` package object) to point at the instance rather than the submodule. Python's `import app.infra.settings as X` bytecode resolves the final segment via `getattr(app.infra, 'settings')` — which after the `__init__.py` re-export returns the **instance**, not the module. `X.settings` then triggers pydantic's `__getattr__('settings')` on the instance, which has no field by that name, and raises `AttributeError`.

**Impact:**

- **Cost 2 of 3 revise attempts** in Slice 7. Attempt 1 misdiagnosed the error as a pytest-monkeypatch + pydantic-setattr incompatibility and replaced `monkeypatch.setattr` with `object.__setattr__` (did not help — the real failure was one line upstream, in argument evaluation). Attempt 2 correctly diagnosed the namespace shadow and switched the fixture to `from app.infra.settings import settings` which resolves the name through the submodule's own namespace rather than via the shadowed package attribute.
- **Latent footgun for every future test** that wants to reach into `app.infra.settings` the module (as opposed to the Settings instance). Any test using `import app.infra.settings as X` will hit the same shadow. The recommended idiom `from app.infra.settings import settings` happens to sidestep it by accident — but a future contributor may try other forms and hit this.

**Workaround (applies now):** Use `from app.infra.settings import settings` in tests and other consumers. Do not use `import app.infra.settings as X` followed by `X.settings`. If you really need the submodule object (rare), use `import sys; sys.modules["app.infra.settings"]` which bypasses the package-attribute path entirely.

**Countermeasure options (for a future cleanup slice):**

1. **Remove the re-export from `app/infra/__init__.py`.** Drop `from app.infra.settings import settings` and its entry in `__all__`. Downstream callers already import `from app.infra.settings import settings` directly; the re-export is a convenience that creates the shadow. Low-risk change, but touches every call site that used `from app.infra import settings` (if any exist — grep first).
2. **Rename the submodule to avoid the collision.** E.g., `app/infra/config.py` with the Settings class, and keep `from app.infra.config import settings` in `__init__.py`. Higher-cost but eliminates the ambiguity at the source.
3. **Document the trap in CLAUDE.md / WARP.md / test-writing guidelines.** Accept the shadow as a fact of life; just warn future contributors not to use the `import ... as X` form on `app.infra.settings`.

**Owning slice / skill:** A dedicated `app/infra/` hygiene slice. Not blocking Iteration 1 exit — the workaround is trivial once known. Captured here so the trap is visible to the next person who writes a test importing `app.infra.settings`.

**Priority:** 🟢 Low — workaround is trivial; no runtime risk; only costs time when a contributor first hits it.

---

### NULL-BYTE-SCRUB-AUTOMATION (2026-04-23) — null bytes appear in source files after Edit-tool operations on Windows-mounted filesystem, blocking pytest collection

**Finding:** During Build Slice 2026-04-23-07 Revise Attempt 2, `tests/test_twilio_signature_middleware.py` accumulated 2 null (`\0`) bytes after an Edit-tool operation on the Windows-mounted workspace. Pytest collection then failed with `ValueError: source code string cannot contain null bytes`, blocking the entire middleware test suite until a manual `tr -d '\0'` scrub restored parseability.

**Symptoms:**

- `pytest tests/...` reports `ERROR ... - ValueError: source code string cannot contain null bytes`; 1 error during collection; no tests run.
- `cat` and `Read` on the file display content normally — null bytes are invisible in most text renderers.
- Detection command: `tr -cd '\0' < path/to/file | wc -c` returns a non-zero count.

**Pattern:** The agent's Edit tool writes to files via the Windows-mount bridge. Under some conditions (exact trigger not fully characterized — correlates with edits near file-end regions or after rapid successive edits), the mount layer introduces spurious null bytes in the written file. The project has seen this before at the README `## Log` tail — the project-manager and build-orchestrator skills already document a mandatory `tr -d '\0' < FILE > /tmp/tmp && cat /tmp/tmp > FILE` scrub after every edit that touches a file's trailing bytes.

**Impact:**

- **Cost at least 1 round trip** in Slice 7 Revise Attempt 2 to diagnose and scrub. Jonathan's initial pytest run failed with an error message (`ValueError: source code string cannot contain null bytes`) that doesn't obviously point to null-byte contamination — the agent had to recognize the symptom from prior experience with the README `## Log` case.
- **Silent risk:** a null-byte-contaminated Python source file that somehow slips past `pytest` collection (e.g., if the null bytes land in a comment region that CPython tolerates) would be a time bomb — it would survive `ruff check` but fail in any CPython context that actually parses the bytes.

**Root cause:** Windows-mount file-write behavior in the agent's sandboxed environment. Not a codebase defect — an agent-infrastructure defect at the tool-mount interface layer.

**Countermeasure (proposed — related to and extends `BUILD-CLOSEOUT-COMMIT-GATE`):** Add a Step 1.6 "Null-Byte Scrub" to the build-closeout procedure (and potentially to build-execution's file-write discipline):

1. For every file in the slice's touched-file list (from `git status --porcelain`), run `tr -cd '\0' < FILE | wc -c`.
2. If any file reports >0 null bytes, scrub via `tr -d '\0' < FILE > /tmp/clean && cat /tmp/clean > FILE` and emit a structured log event naming the file and the number of bytes scrubbed.
3. Fail the slice close (or return with an explicit warning) if scrubbing changed the file's line count by more than 0 — that would indicate the null bytes were within a line and the scrub collapsed structure (e.g., removed a newline pair).

**Workaround (applies now):** After any multi-edit sequence on files via the Edit tool, run the scrub pattern before considering the file "done." The project-manager and build-orchestrator skills already carry this discipline for README `## Log` edits; extend it tacitly to test files and any other file where the agent touches trailing regions.

**Owning slice / skill:** A dedicated `skill-creator`-driven edit pass on build-closeout (and possibly build-execution) to institutionalize the scrub. Related to `BUILD-CLOSEOUT-COMMIT-GATE` — both are in the same "closeout should have more gates before declaring done" family.

**Priority:** 🟡 Medium — silent-corruption risk even if the immediate pytest-collection case is loud; the invariant is worth automating.

---

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

### BUG-001 (2026-04-23) — `To` undefined in `app/api/sms_webhook.py` outbound-log branches

**Status:** Closed — resolved by **Packet 2026-04-23-07 (Slice 7, WBS APP-03 + TST-02)** on 2026-04-23. All three `from_phone=To` sites in `handle_opt_out`, `handle_help_request`, and `handle_no_response` replaced with `from_phone=settings.TWILIO_PHONE_NUMBER`; `from app.infra.settings import settings` added at the top of the module. The `"app/api/sms_webhook.py" = ["F821"]` per-file-ignore entry removed from `pyproject.toml` in the same commit per the Slice-5 owning-slice-removable invariant.

**Originally discovered:** 2026-04-19 by build-evaluate on Build slice 2026-04-08-01 (Packet 2026-04-08-01).

**Symptom (pre-fix):** Three outbound `MessageLog` builders referenced an undefined name `To`:

- `app/api/sms_webhook.py:182` in `handle_opt_out` (STOP reply)
- `app/api/sms_webhook.py:222` in `handle_help_request` (HELP reply)
- `app/api/sms_webhook.py:295` in `handle_no_response` (NO reply)

Any code path that reached one of these branches raised `NameError` at runtime after the `twilio_client.send_sms` call but before the `MessageLog` row was inserted — outbound logging was silently broken for STOP, HELP, and NO replies.

**Root cause:** The helper functions `handle_opt_out(from_phone, db)`, `handle_help_request(from_phone, db)`, and `handle_no_response(from_phone, message_body, db)` do not receive the inbound `To` form parameter that the parent `handle_inbound_sms` extracts. The outbound-log builders should have sourced our own Twilio-owned number from `settings.TWILIO_PHONE_NUMBER`, not referenced a name that was never in scope.

**Resolution mechanism:** Replace `from_phone=To` with `from_phone=settings.TWILIO_PHONE_NUMBER` at the three sites. New regression test suite `tests/test_sms_webhook_outbound_log.py` covers all three reply paths (STOP / HELP / NO) and asserts (a) no `NameError` is raised and (b) the outbound `MessageLog` row is constructed with the correct `from_phone`. The fix lands in the same slice as the new `TwilioSignatureMiddleware` (APP-03) — those handlers are now reachable only via a validly-signed Twilio webhook, so the regression has both a unit-test-level guard and a request-path-level guard against re-introduction.

**Grandfather-note history (now historical):** Between Slice 5 (2026-04-23) and Slice 7 (2026-04-23) the three F821 findings were grandfathered via `pyproject.toml` `"app/api/sms_webhook.py" = ["F821"]` so that the ruff CI gate from QA-01 could turn on clean. That grandfather was explicitly temporary and tied to this slice as the named owning-slice exit path — and it was removed in the same commit as the code fix, exactly as the Slice-5 discipline requires.

---

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
