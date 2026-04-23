# Changelog

All notable changes to the Clinic Cancellation Chatbot project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

*Slice 2026-04-23-06 closed 2026-04-23 on Revise Attempt 0; all 12 Build Packet acceptance checks satisfied; WBS TST-01 and QA-02 marked Done on the Design Schematic (Draft + Final §5.F Testing / §5.G Quality Automation tables and §9 WBS Completion Log). Iteration 1 progress: 10 / 38 WBS items closed. Two outcomes: (1) `.github/workflows/test.yml` is live, blocking merges on any non-zero exit from `pytest`; pytest is pinned to 7.4.3 via `requirements.txt` and the workflow installs the full project dependency tree because the test suite imports `app.*` modules at collection time. Together with `.github/workflows/lint.yml` from Slice 5, the Design Schematic §6 Iteration-1 exit criterion "All build acceptance checks pass: `ruff check`, `ruff format --check`, `pytest` all green" is now fully operationalized as merge-blocking CI. (2) TST-01 "confirm the environment hasn't drifted" obligation attested against the accumulated Slice-1-through-5 evidence (stable 24/24-green across two weeks, no drift encountered since the November 2025 pause). Zero scope creep: exactly 3 files touched (`.github/workflows/test.yml` created; `README.md` Continuous-Integration subsection extended; `CHANGELOG.md` Slice 6 Added block inserted). No application source, test content, `pyproject.toml`, `requirements.txt`, or `lint.yml` edits. No new ISSUES entries (the pre-existing `PYTEST-DEPRECATION-WARNINGS` tracked from Slice 5 remains open and scoped to a later slice); no new DECISIONS entries (the Slice-5 version-pin discipline already covered the parallel pytest-version case by extension).*

### Added — Build slice 2026-04-23-06 (Pytest CI Gate + Pytest Suite Baseline Attestation, WBS QA-02 / TST-01)

- `.github/workflows/test.yml` — **created.** Runs `pytest` (no flags)
  on every push to `main` and every pull request targeting `main`.
  Blocks merge on non-zero exit from the single pytest invocation.
  Installs the full project dependency tree from `requirements.txt`
  (the test suite imports `app.*` modules and requires the runtime
  dependency tree — SQLAlchemy, psycopg, pydantic-settings, structlog,
  FastAPI — at collection time, not just pytest itself). Pins Python
  to 3.11 via `actions/setup-python@v5`; pytest version is sourced from
  `requirements.txt` (`pytest==7.4.3`), matching the project-wide
  version-pin discipline established for ruff in Slice 2026-04-23-05.
- `README.md` — extended the `Continuous Integration` subsection
  introduced in Slice 2026-04-23-05 to document the new test gate:
  local reproduction command (`pytest`), the push / pull_request
  triggers, and the pytest version-pin rule. The two workflows together
  (`lint.yml` + `test.yml`) operationalize the Iteration-1 exit
  criterion from the Design Schematic §6 ("`ruff check`, `ruff format
  --check`, `pytest` all green"); a merge to `main` is now blocked
  unless all three commands exit 0.
- TST-01 attestation — the existing pytest suite has run green
  continuously across Slices 1 (10/10), 3 (18/18), 4 (18/18 in 2.59 s),
  and 5 (24/24 in 2.06 s) with no environmental drift encountered
  since the November 2025 pause. TST-01's "confirm the environment
  hasn't drifted" obligation is satisfied against the Slice 5 24-test
  baseline; `.github/workflows/test.yml` locks the invariant in for
  every subsequent merge.

No application source, test content, `pyproject.toml`, `requirements.txt`,
or `.github/workflows/lint.yml` edits in this slice — this is a
tooling + documentation slice only, completing the CI automation trio
started in Slice 2026-04-23-05.

*Slice 2026-04-23-05 closed 2026-04-23 on Revise Attempt 0; all 14 Build Packet acceptance checks satisfied; WBS QA-01 marked Done on the Design Schematic (Draft + Final §5.G Quality Automation tables and §9 WBS Completion Log). Iteration 1 progress: 8 / 38 WBS items closed. Three key outcomes: (1) `ruff check .` reports 0 findings and `ruff format . --check` reports 0 files need reformatting — both for the first time in the project's history; the Design Schematic §6 Iteration-1 exit criterion "All build acceptance checks pass: `ruff check`, `ruff format --check` … all green" is satisfied. (2) The slice pivoted mid-execution from the packet's original "grandfather-27" plan to the "fix what's cheap, grandfather what's risky" Option-4 discipline after Jonathan asked why more findings couldn't simply be fixed — 30 of 39 findings fixed outright (B008 × 8 via `Annotated[..., Depends(...)]`, E712 × 15 via `.is_(…)`, E402 × 5 via reorder + `# noqa`, F841 × 2 via dead-code delete); 9 grandfathered via `pyproject.toml` per-file-ignores (UP042 × 4 owned by data-layer cleanup, F821 × 3 owned by APP-03 / BUG-001, F841 × 2 owned by `_cancel_other_offers` completion). Each grandfather entry has a named owning-slice exit path. (3) `.github/workflows/lint.yml` is live, blocking merges on any non-zero exit from ruff check or ruff format --check; ruff is pinned to 0.15.9 across `requirements.txt` and the workflow with a project-wide bump discipline recorded in DECISIONS. One new ISSUES entry surfaced from pytest-warning inspection during evaluate: `PYTEST-DEPRECATION-WARNINGS` (pre-existing SQLAlchemy `declarative_base` + Pydantic class-based `Config` — low priority, scoped to the data-layer cleanup and a future deprecation-sweep slice).*

### Added — Build slice 2026-04-23-05 (Lint Hygiene Baseline + Ruff CI Gate, WBS QA-01)

- `.github/workflows/lint.yml` — **created.** Runs `ruff check .` and
  `ruff format . --check` on every push to `main` and every pull
  request targeting `main`. Blocks merge on non-zero exit from either
  command. Pins ruff to 0.15.9, matching the version in
  `requirements.txt` and the baseline disposition recorded in
  `pyproject.toml` `[tool.ruff.lint.per-file-ignores]`.
- `pyproject.toml` — new `[tool.ruff.lint.per-file-ignores]` block
  grandfathering **9** pre-existing findings (down from the 27
  originally proposed in the packet — the slice's "fix what's cheap,
  grandfather what's risky" Option-4 amendment fixed the other 30
  outright rather than hiding them). Grandfather entries cover only:
  `app/infra/models.py` = `["UP042"]` (4 StrEnum-migration findings,
  owned by the data-layer cleanup slice); `app/api/sms_webhook.py` =
  `["F821"]` (3 BUG-001 runtime-bug findings, owned by APP-03); and
  `app/core/orchestrator.py` = `["F841"]` (2 unused locals in the
  incomplete `_cancel_other_offers` body, owned by the
  `_cancel_other_offers` completion slice).
- `app/infra/db.py` — added
  `DbSession = Annotated[Session, Depends(get_db_dependency)]` type
  alias as the canonical modern-FastAPI form of the database-session
  dependency. The alias replaces the legacy
  `db: Session = Depends(get_db_dependency)` idiom across all three
  API modules, eliminating 8 B008 findings with zero behavior change.
- `app/api/admin.py` (6 routes), `app/api/sms_webhook.py` (1 route),
  `app/api/status_webhook.py` (1 route) — migrated to `db: DbSession`
  form; removed the now-unused `Depends`, `get_db_dependency`, and
  (in files where it was no longer referenced) `Session` imports.
- `app/core/prioritizer.py` — 4 `WaitlistEntry.active == True` filters
  swapped to `.is_(True)` (rule E712). Same compiled SQL on every
  SQLAlchemy-supported dialect; no query-result change.
- `dashboard/app.py` — 11 boolean-equality filters swapped to
  `.is_(True)` / `.is_(False)` (rule E712); **one** F841 dead-code
  finding deleted (`created_local` at the prior line 246, unused).
- `app/infra/models.py` — `import enum` moved to the top of the module
  (E402). Mechanical 1-line reorder; no behavior change.
- `scripts/test_all_messages.py` — four imports after
  `sys.path.insert(...)` annotated with trailing `# noqa: E402`
  comments (E402). The `sys.path` manipulation is the correct idiom
  for standalone scripts; suppressing at the call site is the right
  discipline.
- `scripts/seed_test_real.py` — unused `patients` local at line 132
  deleted (F841). The function still seeds both test patients via its
  side effect; only the no-op assignment is removed.
- Six ruff-format-baseline files reformatted clean by `ruff format .`
  in the same slice: `app/api/admin.py` (carried drift from this
  slice's B008 edits), `dashboard/app.py`,
  `scripts/create_test_cancellation.py`, `scripts/direct_test.py`,
  `scripts/process_latest_cancellation.py`,
  `scripts/seed_test_real.py`, `scripts/simulate_response.py`.
  Paired with Slice 4's 17-file normalization, this closes the entire
  23-file `RUFF-FORMAT-BASELINE` identified at Slice 2.
- `tests/test_prioritizer_query_forms.py` — **created.** Six tests
  locking in the E712 → `.is_()` swap equivalence on all four
  affected boolean columns (`WaitlistEntry.active`,
  `PatientContact.opt_out`, `ProviderReference.active`, and the
  `.is_(False)` forms). Compiles each predicate against the
  PostgreSQL dialect with literal binds and asserts the exact SQL
  shape.
- `requirements.txt` — `ruff` pinned from `>=0.6.0` to `==0.15.9` so
  local developer workstations evaluate the same rules as the CI gate.
- `README.md` — new **Continuous Integration** subsection under
  `## 🤝 Contributing`, documenting the two gate commands, the local
  reproduction pattern, the ruff-version-bump discipline (update in
  three places atomically), and the grandfathered-per-file-ignore
  policy with a pointer to the DECISIONS entry.
- `DECISIONS.md` — new **2026-04-23 — Grandfathered ruff per-file
  ignores as the QA-01 gate-activation discipline** entry, documenting
  the "fix what's cheap, grandfather what's risky" Option-4 discipline
  the slice pivoted to at the pre-execution scope gate, the three
  specific grandfather entries and their owning slices, and the
  invariant that new findings in any file must be investigated — never
  silently suppressed. Cross-references the Build Packet's Scope
  Amendment block.
- `ISSUES.md` — closed `RUFF-B008` (all 8 findings fixed via
  `Annotated[...]` migration); closed `RUFF-E712` (all 15 findings
  fixed via `.is_(…)` swap); closed `RUFF-E402` (1 fixed via reorder,
  4 fixed via `# noqa`); closed `RUFF-FORMAT-BASELINE-6` (the
  remaining six files reformatted clean — paired with Slice 4's
  17-file pass this resolves the full original
  `RUFF-FORMAT-BASELINE-23`). Partial update on `RUFF-F841` — the
  `seed_test_real.py` and `dashboard/app.py` hits are fixed; the two
  `orchestrator.py` hits remain grandfathered, owned by the
  `_cancel_other_offers` completion slice. `RUFF-UP042` and `BUG-001`
  remain open, now grandfathered via `pyproject.toml` rather than
  surfacing as raw ruff output, with their owning slices unchanged.

---

*Slice 2026-04-23-04 closed 2026-04-23 on Revise Attempt 0; all 13 Build Packet acceptance checks satisfied; WBS QA-04 marked Done on the Design Schematic (Draft + Final §5.G tables and §9 WBS Completion Log). Iteration 1 progress: 7 / 38 WBS items closed. Three key findings surfaced at evaluate + close: (1) the renormalization was a working-tree re-checkout (`git rm --cached -r . && git reset --hard`), not a second commit — the repo's index had been LF all along via historical `core.autocrlf=true` convert-on-add behavior, and the documented "CRLF drift" lived purely in the working tree (new DECISIONS entry "Renormalization was a working-tree operation, not a second commit" captures the refined mental model). (2) Slice 3's project-management close (2026-04-23) did not include a codebase commit, so Slice 3's code (`app/main.py`, `app/api/health.py`, `tests/test_health_endpoints.py`) sat uncommitted until Slice 4 bundled it into Commit `48b49fa` alongside Slice 4's own `.gitattributes` + docs; new ISSUES entry `BUILD-CLOSEOUT-COMMIT-GATE` scopes the build-closeout skill enhancement needed to prevent recurrence. (3) `ruff format --check` baseline shifted 23 → 6 as an incidental side effect of the LF normalization — 17 Python files were cleaned up for free; new ISSUES entry `RUFF-FORMAT-BASELINE-6` reconciles the count and lists the 6 remaining files. Two ISSUES closed by this slice: `RUFF-CRLF-BASELINE-47` and `EOL-AUTOCRLF-ROOT-CAUSE`, both resolved by the `.gitattributes` policy landing durably.*

### Added — Build slice 2026-04-23-04 (EOL Normalization, WBS QA-04)

- `.gitattributes` — **created** at repo root. Declares the canonical
  end-of-line policy for the repository: `* text=auto eol=lf` as the
  default (all text files use LF in the working tree regardless of each
  contributor's `core.autocrlf` setting) and `*.ps1 text eol=crlf` to
  preserve CRLF on PowerShell scripts (`scripts/install_service.ps1`
  and `scripts/update_server.ps1`). Header comment cross-references the
  DECISIONS 2026-04-23 entry and the ISSUES `EOL-AUTOCRLF-ROOT-CAUSE`
  5-Whys diagnosis that motivated this policy.
- Repository-wide `git add --renormalize .` applied in the same
  atomic commit to bring the existing 47-file `i/lf w/crlf` baseline
  (RUFF-CRLF-BASELINE-47) into alignment with the new policy. After
  the commit, `git ls-files --eol | grep "w/crlf"` returns only the
  two `.ps1` files.
- `README.md` — new **Line-ending policy** subsection under
  `## 🤝 Contributing`. Explains the two `.gitattributes` rules, names
  the one-time operator recovery command (`git add --renormalize .`
  + follow-up commit) for contributors who hit drift, and points at
  DECISIONS / ISSUES for the rationale.
- `DECISIONS.md` — new **2026-04-23 — `.gitattributes` +
  `git add --renormalize .`** entry documenting the rule set, the
  binary-heuristic-trust-by-default stance (no preemptive `*.png
  binary` markers — git's content detection handles the existing
  PNG assets correctly), the PowerShell-CRLF rationale, and the
  operator recovery procedure. Cross-references the 5-Whys chain.
- `ISSUES.md` — `RUFF-CRLF-BASELINE-47` and `EOL-AUTOCRLF-ROOT-CAUSE`
  moved to a new top-level `## ✅ Closed / Resolved Issues` section
  with resolution notes pointing at Packet 2026-04-23-04.
- Design Schematic `2026-04-07-Design-Schematic-workflow.md` — new
  `QA-04` row added to §5 Quality Automation (Draft + Final WBS
  tables) per the packet's Path A approval (description: "Add
  repo-wide EOL policy (`.gitattributes`) and renormalize"; effort
  1 h; deps none; iteration 1). build-closeout will append the
  completion to §9 WBS Completion Log.

No Python code changed; no tests added (repo-hygiene change, not a
behavior change — verification is `git ls-files --eol | grep "w/crlf"`
returning only `.ps1` files, which lives in the slice's validation
commands block). No new dependencies.

---

*Slice 2026-04-21-03 closed 2026-04-23 after 1 revise attempt; all 15 Build Packet acceptance checks satisfied; WBS APP-07 marked Done on the Design Schematic. Iteration 1 progress: 6 / 38 WBS items closed. Revise Attempt 1 addressed three defects: (1) `/readyz` time-bound guard was broken under the initial `asyncio.wait_for + loop.run_in_executor` pattern (HTTP response blocked for the full duration of the sync call regardless of timeout) — fixed via `anyio.fail_after` wrapping `anyio.to_thread.run_sync(..., abandon_on_cancel=True)`; (2) CRLF scope-creep on README / CHANGELOG / DECISIONS docs normalized back to LF; (3) inline `ruff check --fix && ruff format` on slice-authored `.py` files promoted from lesson-learned to an execution-checklist item via new DECISIONS entry. Two new ISSUES entries logged for cross-slice follow-up: `RUFF-CRLF-BASELINE-47` (47 text files drift from LF → CRLF on every git operation) and `EOL-AUTOCRLF-ROOT-CAUSE` (5-Whys diagnosis; countermeasure is a dedicated EOL-Normalization slice adding `.gitattributes` at repo root with `* text=auto eol=lf`).*

*Slice 2026-04-20-02 closed 2026-04-20 after 1 revise attempt; all 11 Build Packet acceptance checks satisfied; WBS APP-05 / APP-06 marked Done on the Design Schematic. Iteration 1 progress: 5 / 38 WBS items closed. 23 pre-existing `ruff format --check` failures on untouched files logged to ISSUES.md as `RUFF-FORMAT-BASELINE-23` for QA-01 attention; ruff-check baseline count reconciled from 35 (reported) to 39 (actual) during evaluation.*

*Slice 2026-04-08-01 closed 2026-04-19 after 1 revise attempt; all 8 Build Packet acceptance checks satisfied; WBS APP-01 / APP-02 / TST-03 marked Done on the Design Schematic. 35 pre-existing ruff findings logged to ISSUES.md (3 as severity=bug, 32 as cleanup) for triage in their owning slices (APP-03 / APP-04 / APP-08 / data-layer refactor).*

### Added — Build slice 2026-04-21-03 (Health & Readiness Endpoints, WBS APP-07)
- `app/api/health.py` — new FastAPI `APIRouter` exposing two
  unauthenticated probes at the root (no prefix):
  - `GET /healthz` — **liveness** probe. Returns 200 with a small
    JSON body (`status`, `service`, `version`, timezone-aware ISO
    timestamp) whenever the process is alive. No database, Twilio,
    or external I/O; liveness is strictly local.
  - `GET /readyz` — **readiness** probe. Returns 200 when both
    (a) a cheap `SELECT 1` against the shared SQLAlchemy engine
    succeeds within `READYZ_DB_TIMEOUT_SECONDS` (2 s) and
    (b) the three required Twilio settings
    (`TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`,
    `TWILIO_PHONE_NUMBER`) are non-empty on the validated settings
    object. Returns 503 with a structured body naming the failing
    sub-check(s) — and, when the Twilio sub-check fails, the missing
    setting NAMES only (never values) — otherwise.
- DB probe is time-bounded via `anyio.fail_after` wrapping
  `anyio.to_thread.run_sync(..., abandon_on_cancel=True)`, so a hung
  database produces a 503 within the configured timeout rather than a
  hung HTTP response (the abandoned worker thread finishes in the
  background, bounded by the DB driver's own timeout). The bound is a
  module-level constant (`READYZ_DB_TIMEOUT_SECONDS`) that tests
  override via `monkeypatch.setattr`. See DECISIONS.md 2026-04-23
  entry for the rationale — the initial `asyncio.wait_for +
  loop.run_in_executor` attempt could not abandon the blocking thread
  and broke the probe's timeout contract.
- Both endpoints emit structured events on every request via
  `structlog.get_logger(__name__)`:
  - `event=health.check` with `outcome=ok` for every `/healthz` call
  - `event=health.ready` with `outcome` one of `ok`,
    `db_unreachable`, `twilio_missing`, or
    `db_unreachable_and_twilio_missing`, plus `db_status`,
    `twilio_status`, `db_failure_reason` (exception class name only,
    never the message), and `twilio_missing` (setting names only,
    never values)
- `app/main.py` registers the new router via the existing
  `app.include_router(...)` pattern alongside admin / sms / status;
  `app.routers_registered` startup event now includes `health` in its
  `routers` list
- `tests/test_health_endpoints.py` — 7 new test cases covering: the
  router-registration contract, `/healthz` green path + event, the
  four-quadrant `/readyz` matrix (DB ok × Twilio ok / DB fail × Twilio
  ok / DB ok × Twilio missing / DB hang × Twilio ok), the time-bound
  guarantee on the DB probe (sleeps 5 s, must return within 2.5 s),
  and the "no secret values in logs" guardrail
- README gains a Health endpoints subsection under Logging, documenting
  both endpoints, their response shapes, and the Task Scheduler
  polling cadence
- DECISIONS.md gains an entry documenting the unauthenticated-health-
  endpoints decision and the liveness-vs-readiness split

### Added — Build slice 2026-04-20-02 (Structured Logging Backbone + Offer-Flow Instrumentation, WBS APP-05 / APP-06)
- `app/infra/logging_config.py` — central `configure_logging()` entry
  point that installs the structlog-based JSON logging backbone:
  rotating file handler at `settings.LOG_FILE`
  (`LOG_MAX_BYTES` / `LOG_BACKUP_COUNT` drive rotation), a stderr
  stream handler for dev visibility, and a conditional
  `NTEventLogHandler` for ERROR-level events on Windows hosts with
  `pywin32` available (graceful no-op elsewhere). Idempotent across
  repeated calls. Processor chain stamps every record with
  timezone-aware UTC timestamp, logger name, level, and exception info
- `app.main.lifespan` now calls `configure_logging()` as the first
  startup step so every subsequent event — including
  `validate_settings()` failures — routes through the structured JSON
  pipeline operators will see in production
- All eight previously stdlib-logging modules migrated to
  `structlog.get_logger(__name__)`: `app/main.py`, `app/infra/settings.py`,
  `app/infra/twilio_client.py`, `app/core/orchestrator.py`,
  `app/core/scheduler.py`, `app/api/sms_webhook.py`,
  `app/api/status_webhook.py`, `app/api/admin.py`
- Twilio-call path in `app/infra/twilio_client.py` emits structured
  events only — no `logger.info(f"…")` f-strings remain. Every
  `send_sms` and `get_message_status` call path (mock, disabled, sent,
  api_error, exception) logs `event`, `outcome`, `message_sid`, and
  a last-4-digit `to_phone_mask`; full phone numbers and message
  bodies never appear as log fields
- Offer / confirmation / expiry DB-write sites in
  `app/core/orchestrator.py` emit structured events with the canonical
  `event` / `patient_id` / `slot_id` / `outcome` field set
  (`offer.sent`, `offer.accepted`, `offer.declined`, `offer.expired`,
  `offer.expired_on_acceptance`, `offer.send_failed`,
  `offer.batch_dispatch`, `offer.batch_continuation`,
  `cancellation.processing`, `cancellation.not_found`,
  `cancellation.state_mismatch`, `cancellation.no_eligible_patients`,
  `acceptance.slot_unavailable`, `acceptance.unknown_sender`,
  `acceptance.no_pending_offer`)
- Scheduler tick outcomes in `app/core/scheduler.py` emit
  `scheduler.expired_holds.tick` / `.error` and
  `scheduler.priority_recalc.completed` / `.disabled` / `.error`
  events
- Inbound-SMS flow in `app/api/sms_webhook.py` emits structured events
  for received messages, STOP/HELP keywords, YES/NO responses, and
  error paths, all using `from_phone_mask` (never full E.164) and
  never carrying the message body
- Status-callback flow in `app/api/status_webhook.py` emits structured
  `twilio.status_callback.*` events for received / delivered / failed
  / sid_not_found / unknown_status
- `tests/test_logging_config.py` covering: rotating-file-handler
  installation, idempotence of `configure_logging`, round-trip of
  representative Twilio-call and offer-flow events (required fields +
  timezone-aware timestamp), a PHI-guardrail test that asserts patient
  name / full phone / DOB / reply body never leak into serialized
  events, and a log-level override test proving DEBUG/INFO are
  suppressed when `LOG_LEVEL=WARNING`
- README `Logging` section added covering log path, rotation policy,
  structured-field vocabulary, the `patient_id`-only PHI rule, and how
  to tail
- `DECISIONS.md` entry documenting the structlog + JSON + Windows
  Event Log decision and the "no PHI beyond patient_id" rule
- `pywin32; sys_platform == 'win32'` added to `requirements.txt` as a
  Windows-only conditional dependency for the Event Log sink;
  non-Windows developers install the rest of the stack unchanged

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

### Server Deployment Notes

**Successful Deployment:**
- Deployed to Windows Server (192.168.1.220)
- Services running via NSSM (win32 version for 32-bit Windows)
- API: Port 8000, Dashboard: Port 8503
- PostgreSQL database on same server

**Issues Encountered & Resolved:**
1. **Streamlit email prompt blocking startup**
   - Solution: Copy config.toml from working project (clinical_productivity)
   - Config disables telemetry: `gatherUsageStats = false`

2. **Missing psycopg2 dependency**
   - Solution: `pip install psycopg2-binary`

3. **NSSM service path issues after venv recreation**
   - Solution: Use full path to venv python.exe in service config
   - Path: `C:\projects\clinic_cancellation_chatbot\.venv\Scripts\python.exe`

**Next Steps:**
- Configure Cloudflare Tunnel for webhooks
- Test end-to-end messaging from server
- Set up automatic service restart on failure

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
- Offer orchestrator (orchestr