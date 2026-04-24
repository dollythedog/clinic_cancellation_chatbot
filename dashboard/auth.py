"""
Dashboard authentication (APP-08).

Session-scoped login wrapper for the Streamlit dashboard. Blocks all
dashboard content behind a username + password check; credentials are
sourced from :mod:`app.infra.settings` and verified against a SHA-256
salted hash in constant time via :func:`hmac.compare_digest`.

**Interpretation of "HTTP basic-auth wrapper."** Streamlit runs its own
Tornado server and cannot emit a browser-native WWW-Authenticate 401
challenge without a reverse proxy in front. COA 1 explicitly rules out
reverse proxies, so this module implements the functionally-equivalent
pattern: a session-scoped login form rendered as the first content on
every request. ``st.stop()`` at the end of the unauthenticated path
guarantees no downstream content renders until authentication succeeds.
See ``DECISIONS.md`` 2026-04-23 "Streamlit dashboard authentication"
for the full trade-off narrative and the operator rotation procedure.

**PHI discipline.** This module never logs (at any level) the entered
plaintext password, the entered username, the stored hash, or the
salt. The error message shown on failed login is the generic
"Invalid credentials" string — it does not reveal which half (username
vs. password) was wrong, to resist credential enumeration.

Owning work package: APP-08 (Design Schematic §5.C). Landed in Build
Slice 2026-04-23-08 (Packet 2026-04-23-08).
"""

from __future__ import annotations

import hashlib
import hmac

import streamlit as st

from app.infra.settings import settings

#: Streamlit ``session_state`` key used to persist the authentication
#: flag across reruns within a single browser session. Session state
#: is per-tab; closing the browser tab or restarting the Streamlit
#: service ends the session and requires a fresh login.
AUTH_SESSION_KEY = "dashboard_authenticated"


def hash_password(plaintext: str, salt: str) -> str:
    """
    Compute the SHA-256 hex digest of ``salt || plaintext``.

    The concatenation order (salt-first) matches the ``DECISIONS.md``
    rotation procedure so operators and verifiers produce the same
    digest from the same inputs.

    Args:
        plaintext: The password to hash.
        salt: The per-install hex-encoded salt.

    Returns:
        The 64-character lowercase SHA-256 hex digest.
    """
    return hashlib.sha256((salt + plaintext).encode("utf-8")).hexdigest()


def verify_password(plaintext: str, salt: str, expected_hash: str) -> bool:
    """
    Verify a plaintext password against the stored salt + hash.

    Uses :func:`hmac.compare_digest` for constant-time comparison so
    that a local observer with a timer cannot distinguish correct from
    incorrect password attempts by measuring response latency.

    Args:
        plaintext: The password the operator typed.
        salt: The per-install salt (from ``settings.DASHBOARD_PASSWORD_SALT``).
        expected_hash: The stored SHA-256 hex digest (from
            ``settings.DASHBOARD_PASSWORD_HASH``).

    Returns:
        ``True`` iff ``hash_password(plaintext, salt) == expected_hash``
        under constant-time comparison; ``False`` otherwise.
    """
    computed = hash_password(plaintext, salt)
    return hmac.compare_digest(computed, expected_hash)


def require_auth() -> None:
    """
    Gate the current Streamlit session behind a login wrapper.

    Idempotent in the authenticated case: if
    ``st.session_state[AUTH_SESSION_KEY]`` is truthy, returns
    immediately and lets the rest of the dashboard render. Otherwise
    renders a username + password form; on submit, validates against
    the Settings-sourced credentials and either sets the session flag
    (on success, then reruns the script) or shows a generic "Invalid
    credentials" error. Calls :func:`streamlit.stop` at the end of the
    unauthenticated path so no dashboard content leaks before auth
    succeeds.

    The function has no parameters — it reads credentials directly
    from the module-level ``settings`` singleton so callers cannot
    accidentally wire the wrong names. Callers must invoke it after
    :func:`streamlit.set_page_config` but before any other Streamlit
    rendering.

    Returns:
        ``None``. Either returns normally (authenticated) or calls
        ``st.stop()`` (unauthenticated) which short-circuits the
        Streamlit script executor.
    """
    if st.session_state.get(AUTH_SESSION_KEY):
        return

    st.title("🏥 TPCCC Cancellation Chatbot — Sign in")
    st.markdown(
        "This dashboard displays protected health information. "
        "Sign in with your authorized admin credentials to continue."
    )

    with st.form("dashboard_login", clear_on_submit=False):
        username = st.text_input("Username", key="_login_username")
        password = st.text_input("Password", type="password", key="_login_password")
        submitted = st.form_submit_button("Sign in")

    if submitted:
        if username == settings.DASHBOARD_USERNAME and verify_password(
            password,
            settings.DASHBOARD_PASSWORD_SALT,
            settings.DASHBOARD_PASSWORD_HASH,
        ):
            st.session_state[AUTH_SESSION_KEY] = True
            st.rerun()
        else:
            # Generic error — does NOT reveal which half was wrong.
            # Resists credential enumeration against the username.
            st.error("Invalid credentials")

    st.stop()
