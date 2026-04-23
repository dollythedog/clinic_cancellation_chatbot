# Decisions — Clinic Cancellation Chatbot

Architectural and design decisions made during codebase development.
Each entry records: context, decision, and consequences. Newest entries
at the top within each release section.

This file is the codebase-level decision log. Project-management-level
decisions (folder layout, deliverable scheduling, etc.) live in the
companion project-management folder at
`1 - Projects/Cancellation Chatbot/DECISIONS.md`.

---

## [Unreleased]

### 2026-04-23 — Grandfathered ruff per-file ignores as the QA-01 gate-activation discipline

**Context:** Build Slice 2026-04-23-05 (WBS QA-01) turned on the repo's ruff-check + ruff-format CI gate. At pre-execution scope-gate review, build-execution surfaced that the packet's original four-entry `[tool.ruff.lint.per-file-ignores]` plan would grandfather only 27 of the 39 baseline findings — leaving 11 unresolved and making Acceptance Check #2 (`ruff check .` reports 0 findings) unsatisfiable. Jonathan was presented with three options (grandfather all 39 / build a smarter allowlist-aware gate / defer QA-01 until the owning slices finish) and pushed back with *"why can't we just fix the errors?"* — the right question. A fourth option emerged from that pushback and was approved as the Scope Amendment: **fix what's cheap and safe in-slice; grandfather only the findings whose real fix requires feature work, DB roundtrip tests, or a blocked upstream dependency.**

**Decision:** The `[tool.ruff.lint.per-file-ignores]` block in `pyproject.toml` represents **pre-triaged, per-file, per-rule grandfather dispositions**, not blanket suppressions. Each entry observes five invariants:

1. **Pre-triaged.** The finding class is already documented in `ISSUES.md` with a named root cause and a named owning slice.
2. **Per-file, per-rule.** The ignore targets one file × one (or a small set of) rule code(s). It is never a blanket `select = [...]` rule exclusion. New violations of the same rule in any *other* file still fail the gate. New violations of *different* rules in the *same* file also still fail the gate.
3. **Owning-slice-removable.** Every entry carries a comment naming the slice whose completion removes it. When the owning slice runs, its scope **must** include deleting the ignore entry in the same commit as the underlying code fix.
4. **No behavior coupling.** Grandfathering a rule does not change runtime behavior — the flagged code keeps running exactly as it did. Grandfathering is a lint-surface decision, not a code decision.
5. **Investigation, not silencing, for anything new.** When a new finding surfaces in any file, the owning slice must investigate the underlying cause. "Add a per-file ignore" is never the first response to a new finding.

The slice's pivot to Option 4 sets a disposition-per-finding discipline that applies to every future lint-hygiene decision:

- **Cheap to fix in-slice** (no behavior change, no new test cost, no blocked dependency) → fix outright. Examples from this slice: B008 × 8 (migrate to `Annotated[..., Depends(...)]`), E712 × 15 (swap to `.is_(…)` — identical SQL on every dialect), E402 × 5 (reorder one import + `# noqa` the `sys.path` hack sites), F841 × 2 trivial deletes.
- **Risky to fix without proper coverage** (needs feature work, DB/API roundtrip tests, or a blocked upstream dependency) → grandfather. Examples from this slice: UP042 × 4 (StrEnum migration risks SQLAlchemy `Enum` column + API JSON + Python `in`-comparison MRO differences — needs roundtrip tests; owned by the data-layer cleanup slice), F821 × 3 (BUG-001 real runtime NameError needs a regression test covering three reply paths with Twilio signature middleware; owned by APP-03, blocked on Open Question 3 Twilio BAA), F841 × 2 (unused locals inside the incomplete body of `_cancel_other_offers`; the locals will be consumed once the SMS-notification send path is finished; owned by the `_cancel_other_offers` completion slice).

**Consequences:**

- **30 of 39 findings fixed outright** at Slice 5 close; **9 grandfathered.** `ruff check .` reports 0 findings against the baseline for the first time. `ruff format . --check` reports 0 files need reformatting for the first time.
- **Three grandfather entries** recorded in `pyproject.toml`: `app/infra/models.py = ["UP042"]`, `app/api/sms_webhook.py = ["F821"]`, `app/core/orchestrator.py = ["F841"]`. Each has a block comment naming the rule code, the finding count, the owning slice, and the ISSUES reference.
- **Project-wide ruff-version pin.** `requirements.txt` pins `ruff==0.15.9`, `.github/workflows/lint.yml` installs the same pinned version, and any future bump must update both files plus any documentation naming a version in a single commit. This prevents the version-skew failure mode that the Slice 3 5-Whys RCA on EOL drift identified as a class of problem.
- **New findings are investigated, not silenced.** The QA-01 gate will fail on any net-new finding of any rule in any file. The per-file-ignore block does not protect future code against regression — only against the known, triaged pre-existing baseline.
- **Every grandfathered entry has an exit path.** UP042 exits when the data-layer cleanup slice migrates the four enums to `StrEnum` with roundtrip tests. F821 exits when APP-03 fixes BUG-001 with a Twilio-signature-middleware regression test. F841 (orchestrator) exits when the `_cancel_other_offers` completion slice finishes the SMS-notification send path. The owning-slice discipline means the grandfather block should shrink, not grow.
- **Cross-reference:** `Build-Packets.md` Packet 2026-04-23-05 contains the Scope Amendment block recording the Option-4 decision. `CHANGELOG.md` `[Unreleased]` Slice 5 Added block records the per-finding disposition. `ISSUES.md` reflects the closed rule classes (`RUFF-B008`, `RUFF-E712`, `RUFF-E402`, `RUFF-FORMAT-BASELINE-6`) and the partial closes (`RUFF-F841`).

**Invariant added to the build-acceptance discipline:** every future slice's evaluate gate includes the check "does this slice introduce any new `[tool.ruff.lint.per-file-ignores]` entries? If yes, is each backed by an ISSUES entry with a named owning slice and a real reason the underlying code cannot be fixed in-slice?" A "yes" to the first question plus a "no" to the second is grounds for build-evaluate to return REVISE.

---

### 2026-04-23 — Renormalization is a working-tree operation, not a second commit (mental-model refinement from Slice 4 evaluate)

**Context:** Build Slice 2026-04-23-04 (WBS QA-04) was designed around the assumption that `git add --renormalize .` would stage a large diff (the 47-file RUFF-CRLF-BASELINE-47 LF-ification) and produce a second atomic commit dedicated to the renormalization. At evaluate time, `git add --renormalize .` was a **no-op** — it staged nothing. Investigation via `git ls-files --eol` showed every file already had `i/lf w/crlf`: **the index was LF; only the working tree was CRLF.**

Follow-up investigation determined that Git-for-Windows with `core.autocrlf=true` (the installer default) has been converting CRLF → LF on every `git add` throughout the project's history. The repo's committed tree has been LF for years. The "CRLF drift" documented in `ISSUES.md` § `RUFF-CRLF-BASELINE-47` / `EOL-AUTOCRLF-ROOT-CAUSE` was always a **working-tree artifact** — each `git checkout` converted the LF index content back to CRLF in the working tree via `core.autocrlf`, and `git diff` then saw CRLF-vs-LF as meaningful changes. `.gitattributes` with `eol=lf` wins over `core.autocrlf` on **new** checkouts but does not retroactively rewrite existing working-tree files.

**Decision:** The canonical recipe for "apply a newly-committed `.gitattributes` to the existing working tree" is:

```bash
git rm --cached -r .
git reset --hard
```

`git rm --cached -r .` clears the index of all tracked entries. `git reset --hard` restores the index from HEAD and overwrites every working-tree file from the restored index, applying `.gitattributes` smudge filters during the checkout step. After this, the working tree matches the policy (LF for non-`.ps1`, CRLF for `.ps1`), and future checkouts stay aligned because `.gitattributes` is now committed.

This recipe **does not produce a commit**. It is a pure working-tree side effect of the already-committed `.gitattributes` policy. It is safe to run when `git status` reports the tree clean; it is destructive (via `--hard`) if uncommitted work exists.

**Consequences:**

- **Mental model refinement:** "EOL drift" in this codebase means working-tree drift, not index drift. Commands that operate on the index (`git add`, `git add --renormalize`, `git ls-files --eol` on the `i/` column) will show everything as LF and healthy, while `git diff` and `git ls-files --eol` on the `w/` column tell the true drift story.
- **Slice 4's "single atomic commit" constraint** was reinterpreted: Slice 4's content contribution (`.gitattributes` + docs) landed in Commit `48b49fa` (which also bundled a Slice 3 catch-up per `ISSUES.md` § `BUILD-CLOSEOUT-COMMIT-GATE`). The renormalization was not a commit at all — it was a post-commit working-tree-alignment operation. Future slices that are purely repo-hygiene changes should scope their commit count accordingly.
- **Operator recovery on new workstations:** if a contributor clones the repo fresh on Windows with `core.autocrlf=true`, the clone's checkout applies `.gitattributes` `eol=lf` and the working tree is LF from the start — no drift, no recovery needed. Drift only arises if a contributor's prior `core.autocrlf` state created CRLF files that pre-date a policy change. The recipe above handles that one-time case.
- **The earlier DECISIONS entry** (`2026-04-23 — .gitattributes + git add --renormalize . as the canonical repo EOL policy`, above in `[Unreleased]`) was slightly wrong in its consequences section — it implied `git add --renormalize .` was the operator recovery procedure. It should be read as "`git rm --cached -r . && git reset --hard` (for the one-time working-tree realignment) **plus** `.gitattributes` winning over `core.autocrlf` on all future checkouts (the durable fix)." Leaving the earlier entry in place for historical record; this entry is the corrected model.

**Entry criterion for every future slice (refined):** the working tree has no `w/crlf` on non-`.ps1` files at slice open. Verify with `git ls-files --eol | grep w/crlf | grep -v "\.ps1$"` — expect empty output.

---

### 2026-04-23 — `.gitattributes` + `git add --renormalize .` as the canonical repo EOL policy

**Context:** Build Slice 2026-04-23-04 (WBS QA-04). The repository had no
`.gitattributes` file, so working-tree EOL behavior was determined
per-contributor by each workstation's global `core.autocrlf` setting.
The solo maintainer's Git-for-Windows default (`autocrlf=true`) combined
with multi-environment contributors (Claude agents writing via a Linux
mount that produces LF) created recurring LF ↔ CRLF drift that surfaced
concretely as Slice 2026-04-21-03 Defect D2 (~2,320 spurious line-ending
changes on README / CHANGELOG / DECISIONS) and as the 47-file baseline
tracked in `ISSUES.md` § `RUFF-CRLF-BASELINE-47`. The 5-Whys diagnosis
is recorded in `ISSUES.md` § `EOL-AUTOCRLF-ROOT-CAUSE`.

**Decision:** Add a `.gitattributes` file at the repo root with two
rules and commit a repository-wide `git add --renormalize .` in the
same atomic commit. The rule set is:

1. `* text=auto eol=lf` — default for all text files. `text=auto` lets
   git detect text vs. binary via its content heuristics; `eol=lf` then
   forces LF in the working tree regardless of each contributor's
   `core.autocrlf` setting. This is the fix for the core drift.
2. `*.ps1 text eol=crlf` — explicit CRLF override for PowerShell
   scripts. Windows PowerShell can interpret LF-only `.ps1` files
   unreliably (older parser bugs around here-strings and multi-line
   `if` / `switch` blocks), so `scripts/install_service.ps1` and
   `scripts/update_server.ps1` retain CRLF deliberately.

No preemptive `*.png binary` (or similar) overrides were added. The
existing PNG assets under `docs/images/` are detected correctly by
git's `text=auto` binary heuristic; adding explicit binary markers
without evidence of misclassification would violate the packet's
"explicit overrides only with rationale" constraint. A future slice
can add them as defensive hygiene if any misclassification surfaces.

**Consequences:**

- Every future slice can assume clean EOL diffs. Cross-cutting slices
  (APP-03 Twilio signature middleware, APP-04 idempotency audit,
  DOC-03 RUNBOOK.md creation) will no longer compound the CRLF-noise
  problem that degraded the Slice 3 evaluate gate.
- If a contributor's `core.autocrlf` setting tries to flip line
  endings back on a checkout, `.gitattributes` wins — `git add
  --renormalize .` + a follow-up commit is the one-line operator
  recovery procedure (documented in `README.md` under
  `## 🤝 Contributing` § Line-ending policy).
- The Slice 2026-04-21-03 per-file cosmetic normalization of three
  docs files was genuinely a stop-gap — the `.gitattributes` policy
  file is the durable fix that makes the one-off normalization
  recurrence-proof. ISSUES entries `RUFF-CRLF-BASELINE-47` and
  `EOL-AUTOCRLF-ROOT-CAUSE` are both closed by this commit.
- `*.ps1` must not be renamed to `.ps1.lf` or similar "fix this by
  renaming" pattern — the CRLF requirement is a Windows-PowerShell
  parser affordance, not a style preference. If a script genuinely
  needs LF (e.g., because it's run via WSL `pwsh-core`), give it a
  dedicated `.sh` or `.py` home and keep the `.ps1` version CRLF.

**Entry criterion for every future slice:** the working tree has no
`i/lf w/crlf` drift on files the slice will touch. If it does, run
`git add --renormalize .` before opening the slice's first commit.

---

### 2026-04-23 — `anyio.to_thread.run_sync(abandon_on_cancel=True)` for the `/readyz` DB probe timeout

**Context:** Build Slice 2026-04-21-03 Revise Attempt 1. The initial
implementation of `app.api.health._check_db_reachable` used
`asyncio.wait_for(loop.run_in_executor(None, _db_ping_sync),
timeout=...)`. The slice's time-bound acceptance test
(`tests/test_health_endpoints.py::test_readyz_db_probe_is_time_bounded`)
exposed that when the executor task was cancelled by the timeout, the
HTTP response still blocked for the full duration of the underlying
sync call (observed: 5.00 s wall-clock vs. a 0.2 s configured timeout).
`asyncio.wait_for` cancels the *waiting coroutine* but cannot interrupt
the thread running in the default executor; FastAPI's TestClient (and
starlette / uvicorn in production) waited for the worker thread to
complete before releasing the response, breaking the readiness-probe
contract that an external monitor must receive a 503 inside the
configured timeout.

**Decision:** Replace `asyncio.wait_for + loop.run_in_executor` with
`anyio.fail_after(timeout_seconds)` wrapping
`anyio.to_thread.run_sync(_db_ping_sync, abandon_on_cancel=True)`.
`anyio` is a transitive dependency of FastAPI (no new package);
`abandon_on_cancel=True` tells anyio's thread pool to release the
worker slot from the caller's perspective on cancellation rather than
wait for the blocking call to return. The HTTP response completes
within the configured timeout; the abandoned worker thread finishes in
the background — bounded by the DB driver's own network / connect
timeout — and is reclaimed by the anyio pool.

**Consequences:**

1. The `/readyz` contract now holds: external monitors receive a 503
   inside `READYZ_DB_TIMEOUT_SECONDS` even when the DB driver is hung
   on a connect or query. The
   `test_readyz_db_probe_is_time_bounded` test, which documents this
   contract, passes.
2. A hung DB can still leave an orphaned worker thread in anyio's
   pool for the duration of the driver's own timeout. This is
   acceptable at the probe's polling cadence (5 min per INF-04) —
   the pool capacity absorbs occasional orphans.
3. The module now imports `anyio` directly rather than `asyncio`.
   `anyio` is already installed as a transitive dep via FastAPI; no
   new requirement. Removing the `asyncio` import removed the only
   consumer of it in the module.
4. Future probes or background tasks that need abandon-on-hang
   semantics for a synchronous external call should follow this same
   pattern: `anyio.fail_after` for the timeout, `anyio.to_thread.run_sync`
   with `abandon_on_cancel=True` for the work.
5. The `_db_ping_sync` top-level-function seam remains unchanged, so
   the existing monkeypatch-based tests continue to work without
   modification.

---

### 2026-04-23 — Promote inline `ruff check --fix && ruff format` to an execution-checklist item

**Context:** Slice 2 Revise Attempt 1 closeout captured "RUFF-ORDER-SWAP"
as a process-improvement note: the mechanical `import logging` →
`import structlog` swap across nine files introduced ~36 auto-fixable
I-rule / UP-rule violations that `ruff check --fix` absorbed at
evaluate time. Slice 3's first evaluate pass confirmed the same
pattern held: `ruff format` on the three slice-edited files during
the pre-evaluate auto-fix step reported "1 file reformatted, 2 files
left unchanged", meaning one slice file was not format-clean at
execution handoff.

**Decision:** Promote inline `ruff check --fix` and `ruff format`
on slice-authored / slice-edited Python files from "lesson learned"
to an explicit execution-checklist item for every subsequent Build
slice. Build-execution's Suggested Validation Commands block must
include, as its first commands, a `ruff check --fix` + `ruff format`
run scoped to the slice-authored / slice-edited `.py` files.
Build-execution's Slice Self-Check must not be ticked until those
commands were actually run — in the host environment that owns the
files — or until it is explicitly noted that they were deferred to
evaluate because execution happened in a sandbox without ruff.

**Consequences:**

1. Future build-evaluate reports should not see "N files reformatted"
   on slice-authored files at evaluate time.
2. Slice commits carry only intended content changes, not ruff
   auto-fix drive-bys introduced by evaluate-time runs.
3. When execution happens in an environment that does not have ruff
   available (e.g., a Claude sandbox that writes code for Jonathan to
   commit from a Windows host), the orchestrator's pre-evaluate
   message to Jonathan must surface the inline ruff step explicitly so
   it is run before build-evaluate proceeds, and the Execution Summary
   must flag "inline ruff deferred" so the status is explicit rather
   than implicit.
4. This is a process rule, not an architectural change. It does not
   change any acceptance check in the Build Packet template.

---

### 2026-04-21 — Unauthenticated `/healthz` + `/readyz`; liveness vs. readiness split

**Context:** Build Slice 2026-04-21-03 (WBS APP-07) added two HTTP
probes to the FastAPI service. Two design questions needed an
architectural answer: (1) should the probes require authentication and
(2) should liveness and readiness be combined into a single endpoint or
split into two? The Design Schematic §4 Observability lens names
`/healthz` and `/readyz` directly and §5 INF-04 assumes external
polling via Windows Task Scheduler, but it does not prescribe the
authentication stance or the split.

**Decision:**

1. **Public, unauthenticated probes.** Both `/healthz` and `/readyz`
   are reachable without credentials. The Twilio signature middleware
   (APP-03, not yet landed) applies only to `/twilio/*` routes; the
   future Streamlit basic-auth wrapper (APP-08) applies only to the
   Streamlit dashboard. Health endpoints are deliberately outside both
   auth boundaries. Rationale: the callers are the Windows Task
   Scheduler health-check job, NSSM service supervision, and external
   uptime monitors — all of which benefit from zero-credential probing.
   The endpoints carry no PHI and disclose only presence/absence of
   configuration, not values, so the attack surface is limited. The
   FastAPI service itself is not directly exposed to the public internet
   (Twilio webhooks arrive via a publicly-resolvable hostname but the
   architecture anticipates TLS termination and firewalling per SEC-02).

2. **Split liveness and readiness.** `/healthz` consults nothing
   external — a green `/healthz` means only that the HTTP server is
   accepting requests. `/readyz` probes the database (bounded-timeout
   `SELECT 1`) and the presence of required Twilio settings. The split
   mirrors the Kubernetes liveness/readiness convention and keeps the
   Task Scheduler alert loop cheap: a single failed `/healthz` is a
   hard-down signal; a failed `/readyz` with green `/healthz` indicates
   a dependency problem (DB down, credentials scrubbed) worth a
   distinct alert path. Rationale for not combining them: a combined
   probe that hits the DB on every poll would either (a) mask true
   process-alive failures behind DB latency spikes or (b) cause the
   Task Scheduler job to hammer the DB with a pool of connection
   attempts unrelated to real user traffic.

3. **Bounded DB timeout, no credential disclosure.** The `/readyz`
   DB probe wraps a synchronous `SELECT 1` in `asyncio.wait_for` with a
   2-second budget (`READYZ_DB_TIMEOUT_SECONDS`). A hung DB produces a
   503 within the budget rather than a hung HTTP response. The 503
   response body names which sub-check failed and — for a missing
   Twilio setting — lists the setting NAMES only. Raw exception
   messages are never included in the response because some
   SQLAlchemy errors embed the connection string (which contains
   credentials); the log event records the exception class name only
   for the same reason.

**Consequences:**

- The FastAPI app's existing `/health` endpoint (defined inline in
  `app/main.py` since Milestone 1) is left in place for backward
  compatibility with any pre-existing callers. New monitoring integrations
  should target `/healthz` / `/readyz` and may eventually allow `/health`
  to be retired in a later cleanup slice.
- Future slices that add new required configuration (e.g. APP-08's
  Streamlit auth credentials) must decide whether the new setting is
  readiness-relevant. If yes, add the name to
  `app.api.health._REQUIRED_TWILIO_SETTINGS` or create a new
  sub-check tuple; update `test_health_endpoints.py` accordingly.
- The bounded DB timeout (2 s) is a ceiling, not a target. Operators
  investigating readiness flakes should look at the log's
  `db_failure_reason` field (exception class name) and correlate with
  DB-side metrics rather than adjusting the probe timeout first.
- The Windows Task Scheduler health-check job (INF-04) will poll
  `/healthz` every 5 minutes and fire email + ntfy.sh alerts only on
  non-200 responses. `/readyz` is polled at the same cadence for log
  stream enrichment; a red `/readyz` with a green `/healthz` is not an
  alert-worthy condition on its own but is visible in `app.log`.

### 2026-04-20 — structlog + JSON file + Windows Event Log as the logging backbone; "patient_id only" PHI rule for log fields

**Context:** Build Slice 2026-04-20-02 (WBS APP-05 + APP-06) needed a
concrete implementation for the Structured Logging & Observability
guardrail lens from the Design Schematic §4. The Design Schematic's
non-negotiable is: *"A maintainer must be able to reconstruct any
incident from `app.log` alone."* Three concrete decisions were
required: (1) which structured-logging library, (2) which log
destinations, and (3) which PHI-bearing identifiers are permitted in
log fields.

**Decision:**

1. **Library: `structlog` on top of stdlib `logging`.** `structlog`
   was already listed in `requirements.txt` and pairs cleanly with
   stdlib handlers via `structlog.stdlib.ProcessorFormatter`. Other
   candidates (`loguru`, Python's built-in `logging.Formatter` with a
   JSON formatter) were rejected: `loguru` would introduce a second
   logging framework without a commensurate benefit; a hand-rolled
   JSON formatter would make contextvars and processor chaining more
   brittle.

2. **Destinations: rotating JSON file + stderr + conditional Windows
   Event Log.** The rotating file handler at `settings.LOG_FILE` is
   the audit-of-record; its rotation thresholds are `LOG_MAX_BYTES`
   and `LOG_BACKUP_COUNT` (Design Schematic caller: 50 MB / 10
   backups). The stderr stream handler exists for developer
   visibility during local runs. The Windows Event Log sink
   (`logging.handlers.NTEventLogHandler` via `pywin32`) attaches at
   ERROR level on Windows production hosts and is a graceful no-op on
   non-Windows dev machines — the design choice avoids making
   `pywin32` a blocking dependency for every contributor.

3. **PHI rule for log fields: `patient_id` only.** Structured log
   events may carry the integer `patient_id` (database primary key),
   `slot_id`, `offer_id`, `cancellation_id`, `message_sid`, and phone
   last-4-digit masks (`from_phone_mask`, `to_phone_mask`). Log fields
   must **never** contain patient names, full E.164 phone numbers,
   dates of birth, or free-text reply bodies. The `message_log`
   database table remains the single audit source of truth for full
   message content. This rule is enforced both by code convention (the
   `_mask_phone()` helper in `app/infra/twilio_client.py`, used by
   every PHI-adjacent call site) and by
   `tests/test_logging_config.py::test_no_phi_beyond_patient_id_leaks_into_events`
   which asserts that representative events do not contain the
   forbidden tokens.

**Consequences:**

- Every application module now obtains its logger via
  `structlog.get_logger(__name__)`; `configure_logging()` is the only
  place that touches handlers or `logging.basicConfig`. Future slices
  must not add `logging.basicConfig` calls or per-module handler
  configuration.
- The `pywin32; sys_platform == 'win32'` entry in `requirements.txt`
  is a Windows-only install; `pip install -r requirements.txt` on
  Linux/macOS installs the rest of the stack unchanged and the Event
  Log sink self-disables.
- Future work that needs to log a new patient-adjacent value must
  either use `patient_id` (preferred) or document why a masked variant
  is sufficient; full phone numbers / names / bodies are always
  forbidden in log fields. BUG-001's eventual fix in the APP-03 /
  INT-03 slice must conform.
- Log-level drift between environments is controlled via
  `settings.LOG_LEVEL` alone; `configure_logging()` honors whatever
  level is set on the validated settings object. Tests cover the
  override behavior.

### 2026-04-19 — Null-byte mitigation for Windows-mounted filesystem writes

**Context:** During Build Slice 2026-04-08-01 Revise Attempt 1, the
evaluate gate detected trailing null bytes in `app/infra/settings.py`
that caused `ruff format . --check` and `pytest` collection to fail
with `ValueError: source code string cannot contain null bytes`. A
second invocation of the same commands succeeded with no intervening
edit visible in the transcript. This is the same failure mode the
project-manager skill's Phase 3 procedure warns about for README
`## Log` section edits — the Windows-mounted filesystem can leave
trailing null bytes when a writer does not flush/close cleanly.

**Decision:** Any file written by a build skill on a mounted Windows
path must be post-processed with a null-byte scrub before the write is
considered complete:

```bash
tr -d '\0' < FILEPATH > /tmp/clean && cat /tmp/clean > FILEPATH && rm /tmp/clean
```

Python source files are particularly sensitive because the parser
rejects null bytes outright. Markdown, JSON, and config files are less
sensitive but the same scrub applies.

**Consequences:**
- `build-execution` should invoke the scrub after any `Write`/`Edit`
  tool call on this repo going forward.
- If a `ruff` or `pytest` run fails with a parse error at the final
  line of a recently-written file, suspect null bytes first.
- `app/infra/settings.py` was re-scrubbed during Revise Attempt 1 as a
  defensive measure; null-byte count at that time was zero.

### 2026-04-19 — Defer Streamlit auth secret from APP-01 to APP-08

**Context:** Build Packet 2026-04-08-01 (Config Foundation) listed five
required-at-minimum secrets on the `Settings` class: Twilio account
SID, Twilio auth token, Twilio from-number, database URL, and
**Streamlit auth secret**. The Design Schematic §4 Secrets & Config
lens echoes this. However, the Streamlit auth secret's consumer is the
HTTP basic-auth wrapper in WBS item APP-08, which has not yet landed.
Declaring the field now would ship a required secret with no use-site,
forcing operators to set a placeholder in `.env` with no functional
effect and no validation that the placeholder is even in the right
shape (single secret vs. username + password).

**Decision:** Defer the Streamlit auth credential field(s) from APP-01
to APP-08. `Settings` currently declares four required fields
(`DATABASE_URL`, `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`,
`TWILIO_PHONE_NUMBER`). APP-08 will add `STREAMLIT_AUTH_USERNAME` and
`STREAMLIT_AUTH_PASSWORD` (or an equivalent shape chosen by the auth
wrapper's implementation — single HMAC secret, bcrypt hash, etc.) as
required non-defaulted fields, update `.env.example` (the
`test_env_example_parity_with_settings_class` test will catch drift
automatically), and document the credential rotation procedure in the
RUNBOOK.

**Consequences:**
- The slice's parity test reflects four required keys, not five. This
  is the intended state until APP-08 lands.
- When APP-08 work begins, it must (a) add the required field(s) on
  `Settings`, (b) add corresponding line(s) to `.env.example`,
  (c) update this DECISIONS.md entry with a pointer to the implementing
  slice's commit, and (d) confirm the startup-validation test still
  covers the new required keys.

### 2026-04-19 — Retain module-level `settings = Settings()` alongside explicit `validate_settings()`

**Context:** `app/infra/settings.py` instantiates `settings = Settings()`
at module import time AND exposes an explicit `validate_settings()`
function that the FastAPI lifespan hook calls at startup. The two
patterns are deliberately redundant.

**Decision:** Keep both. Module-level instantiation fails loudly at
import time if required env vars are missing, giving a consistent error
regardless of how the app is entered (pytest, alembic env.py, direct
CLI). The explicit `validate_settings()` is the audit-visible startup
gate invoked from the FastAPI lifespan so that configuration validation
appears in structured startup logs as a named step, not a side effect
of import.

**Consequences:**
- Existing `from app.infra.settings import settings` call sites
  (including the Alembic `scripts/migrations/env.py`) continue to work
  without modification.
- Future maintainers who see both and suspect dead code should read
  this entry before removing either.
- Tests use `tests/conftest.py` with `os.environ.setdefault(...)` to
  provide safe defaults at import time; 