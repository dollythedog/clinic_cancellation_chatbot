"""
Shared pytest configuration and fixtures.

IMPORTANT: The os.environ.setdefault calls below run at import time
(before any test module is collected). They provide safe placeholder
values so that ``app.infra.settings.Settings()`` — which is instantiated
at module level — does not raise ``ValidationError`` during test
collection. Individual tests that need to assert missing-env behavior
should use ``monkeypatch.delenv`` to remove these defaults for their
duration and pass ``_env_file=None`` to ``Settings()`` to prevent
loading a real ``.env`` file.

When a new required field is added to ``Settings`` (via slice-level
work), add a matching ``setdefault`` below and update
``tests/test_settings.py``'s ``REQUIRED_KEYS`` + ``_set_all_required_env``
helpers in the same commit. The three invariants — Settings declares
the field, conftest seeds a placeholder, test_settings mirrors the
required-keys roster — must move together.
"""

import hashlib
import os

# --- Dashboard authentication (APP-08, Slice 2026-04-23-08) ------------
# The dashboard login wrapper verifies plaintext passwords against a
# SHA-256 hex digest of ``salt || plaintext``. For tests that need to
# exercise the verified-credentials path, the placeholder salt + hash
# below correspond to the plaintext password ``"testpassword"``. Tests
# that import these canonical values should prefer the constants
# exported from ``tests/test_dashboard_auth.py`` rather than re-deriving
# them.
_TEST_DASHBOARD_USERNAME = "testadmin"
_TEST_DASHBOARD_SALT = "deadbeef" * 4  # 32-char hex; matches secrets.token_hex(16) shape
_TEST_DASHBOARD_PLAINTEXT = "testpassword"
_TEST_DASHBOARD_HASH = hashlib.sha256(
    (_TEST_DASHBOARD_SALT + _TEST_DASHBOARD_PLAINTEXT).encode("utf-8")
).hexdigest()

# Test-safe defaults for required settings. setdefault ensures these
# never overwrite real env vars if a developer has them set.
os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost:5432/testdb")
os.environ.setdefault("TWILIO_ACCOUNT_SID", "ACtest000000000000000000000000test")
os.environ.setdefault("TWILIO_AUTH_TOKEN", "test_auth_token_placeholder")
os.environ.setdefault("TWILIO_PHONE_NUMBER", "+15555550100")
os.environ.setdefault("DASHBOARD_USERNAME", _TEST_DASHBOARD_USERNAME)
os.environ.setdefault("DASHBOARD_PASSWORD_SALT", _TEST_DASHBOARD_SALT)
os.environ.setdefault("DASHBOARD_PASSWORD_HASH", _TEST_DASHBOARD_HASH)
