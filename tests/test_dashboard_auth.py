"""
Tests for the Streamlit dashboard authentication wrapper (APP-08).

Covers three concerns from Build Packet 2026-04-23-08:

1. Purity of ``hash_password`` (deterministic, salt-sensitive).
2. Correctness of ``verify_password`` (accepts matching inputs;
   rejects wrong password OR wrong salt; uses ``hmac.compare_digest``
   for constant-time comparison).
3. Gate semantics of ``require_auth`` (blocks without session;
   accepts valid credentials; rejects invalid credentials) — verified
   via ``streamlit.testing.v1.AppTest`` which renders the harness
   script in-process and exposes widget state for assertion.

The AppTest tests rely on the Settings singleton being populated with
the conftest.py placeholder values — ``_TEST_DASHBOARD_USERNAME`` /
``_TEST_DASHBOARD_SALT`` / the hash computed from ``_TEST_DASHBOARD_PLAINTEXT``.
Those constants are re-exported here for clarity.
"""

from __future__ import annotations

import hashlib
import hmac
from typing import Any

import pytest
from streamlit.testing.v1 import AppTest

from dashboard.auth import (
    AUTH_SESSION_KEY,
    hash_password,
    verify_password,
)

# Canonical test credentials. These match the values seeded in
# tests/conftest.py; any drift here breaks the AppTest fixtures that
# assume the Settings singleton already holds these exact values.
TEST_USERNAME = "testadmin"
TEST_PLAINTEXT = "testpassword"
TEST_SALT = "deadbeef" * 4  # 32-char hex, matches secrets.token_hex(16) shape
TEST_HASH = hashlib.sha256((TEST_SALT + TEST_PLAINTEXT).encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# hash_password — purity
# ---------------------------------------------------------------------------


def test_hash_password_deterministic() -> None:
    """Same plaintext + salt produce the same hex digest on every call."""
    digest_a = hash_password(TEST_PLAINTEXT, TEST_SALT)
    digest_b = hash_password(TEST_PLAINTEXT, TEST_SALT)
    assert digest_a == digest_b
    assert digest_a == TEST_HASH
    assert len(digest_a) == 64
    assert all(c in "0123456789abcdef" for c in digest_a)


def test_hash_password_salt_sensitive() -> None:
    """Changing the salt changes the digest, even if the plaintext is identical."""
    salt_a = "deadbeef" * 4
    salt_b = "cafebabe" * 4
    assert hash_password(TEST_PLAINTEXT, salt_a) != hash_password(TEST_PLAINTEXT, salt_b)


# ---------------------------------------------------------------------------
# verify_password — correctness
# ---------------------------------------------------------------------------


def test_verify_password_correct_credentials() -> None:
    """The matching salt + plaintext + hash triple verifies True."""
    assert verify_password(TEST_PLAINTEXT, TEST_SALT, TEST_HASH) is True


def test_verify_password_wrong_password() -> None:
    """A wrong plaintext against the right salt + hash verifies False."""
    assert verify_password("wrong-password", TEST_SALT, TEST_HASH) is False


def test_verify_password_wrong_salt() -> None:
    """
    The right plaintext against a wrong salt verifies False. Defends
    against the footgun of reusing a single global salt across installs —
    swapping the salt must invalidate every verification.
    """
    wrong_salt = "cafebabe" * 4
    assert verify_password(TEST_PLAINTEXT, wrong_salt, TEST_HASH) is False


def test_verify_password_uses_constant_time_comparison(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    ``verify_password`` must delegate to ``hmac.compare_digest`` rather
    than Python's ``==`` for the final comparison. Defeats timing-attack
    observers that would otherwise measure short-circuit differences.
    """
    calls: list[tuple[Any, Any]] = []
    original = hmac.compare_digest

    def _recording(a: Any, b: Any) -> bool:
        calls.append((a, b))
        return original(a, b)

    # Patch the reference the dashboard.auth module uses. The module
    # imports hmac at module scope, so we patch on that module's own
    # hmac symbol, not the stdlib's.
    from dashboard import auth as auth_module

    monkeypatch.setattr(auth_module.hmac, "compare_digest", _recording)

    verify_password(TEST_PLAINTEXT, TEST_SALT, TEST_HASH)

    assert len(calls) == 1, "verify_password must delegate exactly one call to hmac.compare_digest"


# ---------------------------------------------------------------------------
# require_auth — gate semantics via streamlit.testing.v1.AppTest
# ---------------------------------------------------------------------------
#
# Each AppTest case runs a tiny harness function that imports
# ``require_auth`` and, if it returns, renders a sentinel marker. The
# marker's presence (or absence) lets the test assert on whether the
# auth gate let execution through.


PROTECTED_MARKER = "PROTECTED_CONTENT_MARKER"


def _auth_harness() -> None:
    """Harness for AppTest: invoke require_auth then render a marker.

    If require_auth blocks via st.stop(), the marker never reaches the
    script output. Two discipline constraints apply inside this function
    body (they do NOT apply to the surrounding module):

    1. ASCII-only. AppTest.from_function writes the source to a Windows
       temp file via locale encoding (cp1252) and Streamlit then reads
       it as UTF-8; any non-ASCII byte crashes the script cache with
       UnicodeDecodeError.
    2. No references to names defined at module scope. AppTest extracts
       only the function body and runs it as a standalone script, so
       module-level constants (e.g. PROTECTED_MARKER) are out of scope.
       The marker is written as an inline string literal that matches
       the PROTECTED_MARKER constant's value.
    """
    import streamlit as st

    from dashboard.auth import require_auth

    require_auth()
    # Inline literal, intentionally not PROTECTED_MARKER (see docstring).
    st.write("PROTECTED_CONTENT_MARKER")


def test_require_auth_blocks_without_session() -> None:
    """
    A fresh session (no AUTH_SESSION_KEY) must render the login form
    and short-circuit via st.stop() before any protected content.
    """
    at = AppTest.from_function(_auth_harness)
    at.run()

    # No protected content leaked.
    rendered_text = " ".join(str(m.value) for m in at.markdown)
    rendered_writes = " ".join(str(m.value) for m in at.get("markdown"))
    combined = rendered_text + " " + rendered_writes
    assert PROTECTED_MARKER not in combined, (
        "Protected content must not render before authentication succeeds"
    )

    # Login form widgets are present.
    assert len(at.text_input) >= 2, (
        f"Expected username + password inputs; got {len(at.text_input)} text_input widgets"
    )

    # The session flag stays absent. AppTest's session_state has no
    # .get() method — attribute access routes through __getattr__ and
    # tries to look up the literal key "get". Use the `in` + `[]`
    # idiom instead.
    assert AUTH_SESSION_KEY not in at.session_state or not at.session_state[AUTH_SESSION_KEY], (
        "Auth session flag must not be set before the user submits valid credentials"
    )


def test_require_auth_accepts_valid_credentials() -> None:
    """
    Submitting the correct username + password via the login form must
    flip the session flag to True. The Settings singleton's
    ``DASHBOARD_USERNAME`` / ``DASHBOARD_PASSWORD_HASH`` /
    ``DASHBOARD_PASSWORD_SALT`` are seeded by conftest.py to the
    canonical test values, so the harness can submit ``TEST_USERNAME``
    + ``TEST_PLAINTEXT`` and expect success.
    """
    at = AppTest.from_function(_auth_harness)
    at.run()

    # Fill in the form with valid credentials.
    at.text_input(key="_login_username").set_value(TEST_USERNAME)
    at.text_input(key="_login_password").set_value(TEST_PLAINTEXT)

    # Click the form's submit button. AppTest exposes form submit
    # buttons via the `button` collection by label.
    submit_buttons = [b for b in at.button if b.label == "Sign in"]
    assert submit_buttons, "Expected a 'Sign in' submit button in the login form"
    submit_buttons[0].click()

    at.run()

    # The session flag flipped to True on the post-submit rerun.
    # AppTest session_state requires `in` + `[]`; no .get() method.
    assert AUTH_SESSION_KEY in at.session_state, (
        "Valid credentials must set the auth session flag (key missing)"
    )
    assert at.session_state[AUTH_SESSION_KEY] is True, (
        "Valid credentials must set the auth session flag to True"
    )


def test_require_auth_rejects_invalid_credentials() -> None:
    """
    Submitting wrong credentials must leave the session flag unset and
    render an "Invalid credentials" error. The error text must not
    reveal which half (username or password) was wrong.
    """
    at = AppTest.from_function(_auth_harness)
    at.run()

    at.text_input(key="_login_username").set_value(TEST_USERNAME)
    at.text_input(key="_login_password").set_value("definitely-not-the-password")

    submit_buttons = [b for b in at.button if b.label == "Sign in"]
    submit_buttons[0].click()

    at.run()

    # Session flag is NOT set. AppTest session_state requires `in` +
    # `[]`; no .get() method.
    assert AUTH_SESSION_KEY not in at.session_state or not at.session_state[AUTH_SESSION_KEY], (
        "Invalid credentials must leave the session unauthenticated"
    )

    # Generic error rendered.
    error_text = " ".join(str(e.value) for e in at.error)
    assert "Invalid credentials" in error_text
    # Error does NOT disclose which half was wrong.
    assert "username" not in error_text.lower()
    assert "password" not in error_text.lower()
