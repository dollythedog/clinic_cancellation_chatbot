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
  provide safe defaults at import time; individual tests that exercise
  the missing-env path use `monkeypatch.delenv` plus `_env_file=None`.
