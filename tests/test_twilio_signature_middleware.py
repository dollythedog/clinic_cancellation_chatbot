"""
Tests for the Twilio signature verification middleware (APP-03 / TST-02).

Covers the five required cases from Build Packet 2026-04-23-07:

1. Unsigned POST to ``/sms/inbound`` → 403.
2. Invalidly-signed POST to ``/sms/inbound`` → 403.
3. Validly-signed POST to ``/sms/inbound`` → middleware passes the
   request through (status code is **not** 403; the downstream handler
   is reached, verified via a monkeypatched ``twilio_client.send_sms``
   observer).
4. Unsigned POST to ``/twilio/status`` → 403 (confirms ``/twilio/*``
   prefix is protected too).
5. Unsigned GET to ``/healthz`` and ``/`` → 200 (confirms non-protected
   paths are unaffected).

Tests do not require a live database or a live Twilio account.
``twilio_client.send_sms`` is monkeypatched to a no-op observer;
``tests/conftest.py`` already seeds safe placeholder ``TWILIO_*``
env vars; ``TWILIO_WEBHOOK_BASE_URL`` is explicitly overridden inside
the ``_valid_signature_env`` fixture so the middleware's canonical-URL
computation is deterministic.

See the module docstring of ``app.api.middleware`` for the URL
strategy and PHI discipline. See DECISIONS.md 2026-04-23
"Twilio signature middleware URL strategy" for the canonical-URL
rationale.
"""

from __future__ import annotations

from collections.abc import Generator
from typing import Any

import pytest
from fastapi.testclient import TestClient
from twilio.request_validator import RequestValidator

# Test fixtures constructed against the same TWILIO_* placeholder values
# that tests/conftest.py seeds at import time.
TEST_AUTH_TOKEN = "test_auth_token_placeholder"
TEST_WEBHOOK_BASE_URL = "https://webhooks.test.example.com"
TEST_FROM = "+15551234567"
TEST_TO = "+15555550100"


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """
    Yield a ``TestClient`` whose settings are seeded with a known
    ``TWILIO_WEBHOOK_BASE_URL`` and ``TWILIO_AUTH_TOKEN`` so the
    middleware signs against a predictable canonical URL.

    The client is constructed **without** the ``with TestClient(app) as tc:``
    context-manager form so the app lifespan (scheduler startup, DB
    probe) is skipped — matching the hermetic pattern used in
    ``tests/test_health_endpoints.py``. Tests exercise routing and
    middleware behavior, not the lifespan.

    **Why ``from app.infra.settings import settings`` instead of
    ``import app.infra.settings as settings_module``.** The package
    ``app.infra/__init__.py`` re-exports the Settings instance via
    ``from app.infra.settings import settings``. That rebinds the
    attribute ``app.infra.settings`` (on the ``app.infra`` package
    object) to the Settings **instance**, shadowing the ``.settings``
    submodule attribute. Since Python's ``import a.b.c as foo``
    bytecode uses ``getattr(a.b, 'c')`` under the hood, that path
    returns the instance (not the module) — and
    ``settings_module.settings`` then triggers pydantic's
    ``__getattr__('settings')`` which raises
    ``AttributeError: 'Settings' object has no attribute 'settings'``.
    A direct ``from ... import settings`` sidesteps the shadowing by
    resolving the name through the submodule's namespace rather than
    the package attribute.

    **Why ``object.__setattr__`` for the assignment.** Pydantic 2.12's
    ``__setattr__`` runs validation-on-assignment logic that can trip
    on boundary cases for optional string fields. ``object.__setattr__``
    bypasses pydantic's validation path and writes directly through
    Python's default implementation. We save and restore the prior
    values explicitly so test isolation survives even though pytest's
    ``monkeypatch`` undo stack is bypassed.
    """
    from app.infra.settings import settings
    from app.main import app

    old_base_url = settings.TWILIO_WEBHOOK_BASE_URL
    old_auth_token = settings.TWILIO_AUTH_TOKEN

    object.__setattr__(settings, "TWILIO_WEBHOOK_BASE_URL", TEST_WEBHOOK_BASE_URL)
    object.__setattr__(settings, "TWILIO_AUTH_TOKEN", TEST_AUTH_TOKEN)

    try:
        yield TestClient(app)
    finally:
        object.__setattr__(settings, "TWILIO_WEBHOOK_BASE_URL", old_base_url)
        object.__setattr__(settings, "TWILIO_AUTH_TOKEN", old_auth_token)


@pytest.fixture
def stub_twilio_send(monkeypatch: pytest.MonkeyPatch) -> list[dict[str, Any]]:
    """
    Monkeypatch ``app.api.sms_webhook.twilio_client.send_sms`` to a
    no-op observer. Returns the list that the observer appends to, so
    tests can assert the downstream handler was reached by checking
    that the observer recorded a call.
    """
    calls: list[dict[str, Any]] = []

    def _observer(*, to: str, body: str, status_callback: str | None = None) -> str | None:
        calls.append({"to": to, "body": body, "status_callback": status_callback})
        return "SM-stubbed"

    import app.api.sms_webhook as sms_webhook_module

    monkeypatch.setattr(sms_webhook_module.twilio_client, "send_sms", _observer)
    return calls


@pytest.fixture
def stub_sms_handlers() -> Generator[None, None, None]:
    """
    Redirect the DB dependency so ``handle_inbound_sms``'s downstream
    side effects run against a stub session instead of a live Postgres.
    ``parse_patient_response("TEST")`` returns ``None`` (no keyword
    matches), so the handler falls through to the "unparseable" branch
    which calls ``twilio_client.send_sms`` exactly once — the
    observable signal that the middleware let the request through.
    """

    class _StubQuery:
        def filter_by(self, **_kwargs: Any) -> _StubQuery:
            return self

        def first(self) -> None:
            return None

    class _StubSession:
        def add(self, _obj: Any) -> None:
            pass

        def commit(self) -> None:
            pass

        def query(self, _model: Any) -> _StubQuery:
            return _StubQuery()

    from app.infra.db import get_db_dependency
    from app.main import app

    def _override_db() -> Generator[_StubSession, None, None]:
        yield _StubSession()

    app.dependency_overrides[get_db_dependency] = _override_db
    try:
        yield
    finally:
        app.dependency_overrides.pop(get_db_dependency, None)


def _sign(
    path: str,
    params: dict[str, str],
    base_url: str = TEST_WEBHOOK_BASE_URL,
    auth_token: str = TEST_AUTH_TOKEN,
) -> tuple[str, str]:
    """Return ``(signature, canonical_url)`` for the given path + form params."""
    validator = RequestValidator(auth_token)
    canonical = base_url.rstrip("/") + path
    signature = validator.compute_signature(canonical, params)
    return signature, canonical


# ---------------------------------------------------------------------------
# The five required cases from the packet
# ---------------------------------------------------------------------------


def test_unsigned_request_rejected(client: TestClient) -> None:
    """Acceptance Check #3: POST to ``/sms/inbound`` without ``X-Twilio-Signature`` → 403."""
    response = client.post(
        "/sms/inbound",
        data={"From": TEST_FROM, "To": TEST_TO, "Body": "TEST"},
    )
    assert response.status_code == 403
    body = response.json()
    assert "signature" in body["detail"].lower()


def test_invalid_signature_rejected(client: TestClient) -> None:
    """Acceptance Check #4: POST with a bogus signature → 403."""
    response = client.post(
        "/sms/inbound",
        data={"From": TEST_FROM, "To": TEST_TO, "Body": "TEST"},
        headers={"X-Twilio-Signature": "not-a-valid-signature"},
    )
    assert response.status_code == 403
    body = response.json()
    assert "signature" in body["detail"].lower()


def test_valid_signature_passes(
    client: TestClient,
    stub_twilio_send: list[dict[str, Any]],
    stub_sms_handlers: None,
) -> None:
    """
    Acceptance Check #5: POST with a validly-computed signature reaches
    the handler. The handler falls through to the unparseable-reply
    branch on body ``"TEST"`` and invokes ``twilio_client.send_sms``
    exactly once — the presence of that call is the ground-truth signal
    that the middleware let the request through.
    """
    params = {"From": TEST_FROM, "To": TEST_TO, "Body": "TEST"}
    signature, _ = _sign("/sms/inbound", params)

    response = client.post(
        "/sms/inbound",
        data=params,
        headers={"X-Twilio-Signature": signature},
    )

    assert response.status_code != 403, (
        f"Middleware rejected a validly-signed request. Response: "
        f"{response.status_code} / {response.text}"
    )
    # Exactly one pass-through signal: the unparseable-reply branch's
    # twilio_client.send_sms observer fired. This is the strongest
    # proof the handler body was reached, not just any 2xx response.
    assert len(stub_twilio_send) == 1
    assert stub_twilio_send[0]["to"] == TEST_FROM


def test_status_webhook_protected(client: TestClient) -> None:
    """Acceptance Check #6: unsigned POST to ``/twilio/status`` → 403."""
    response = client.post(
        "/twilio/status",
        data={"MessageSid": "SM1234567890abcdef1234567890abcdef", "MessageStatus": "delivered"},
    )
    assert response.status_code == 403


def test_unprotected_paths_unaffected(client: TestClient) -> None:
    """
    Acceptance Check #7: unsigned GETs to non-Twilio paths pass through.

    ``/healthz`` and ``/`` are the canonical examples; the same
    middleware must also let ``/readyz``, ``/health``, ``/docs``, and
    ``/admin/*`` through, but those either have real side effects
    (readyz probes DB), or require admin body shape, so the two
    lightweight GETs here are the cleanest smoke.
    """
    r_healthz = client.get("/healthz")
    r_root = client.get("/")
    assert r_healthz.status_code == 200, r_healthz.text
    assert r_root.status_code == 200, r_root.text
