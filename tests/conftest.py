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
"""

import os

# Test-safe defaults for required settings. setdefault ensures these
# never overwrite real env vars if a developer has them set.
os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost:5432/testdb")
os.environ.setdefault("TWILIO_ACCOUNT_SID", "ACtest000000000000000000000000test")
os.environ.setdefault("TWILIO_AUTH_TOKEN", "test_auth_token_placeholder")
os.environ.setdefault("TWILIO_PHONE_NUMBER", "+15555550100")
