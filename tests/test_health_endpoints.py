"""
Tests for the APP-07 health and readiness endpoints.

Covers the five required cases from Build Packet 2026-04-21-03:

(a) ``/healthz`` returns 200 with the expected body shape and emits a
    structured log event.
(b) ``/readyz`` returns 200 when both sub-checks pass.
(c) ``/readyz`` returns 503 when the DB ping fails (response body names
    ``db`` as the failing sub-check).
(d) ``/readyz`` returns 503 when a required Twilio setting is empty
    (response body lists the missing setting name).
(e) ``/readyz`` emits a structured event with ``event=health.ready`` and
    an ``outcome`` field, and never writes actual Twilio secret values
    into the log.

Plus two additional guardrails:

- The DB probe is time-bounded: a hung ping yields 503 well within the
  configured timeout rather than blocking the HTTP response (acceptance
  check 6).
- ``app.main.app`` registers both routes exactly once, proving the
  router is wired into the real application (acceptance check 2).

Tests do not require a live database or Twilio account; the DB ping is
stubbed via ``monkeypatch.setattr``, and ``tests/conftest.py`` provides
safe placeholder values for the required settings.
"""

from __future__ import annotations

import json
import logging
import logging.handlers
import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.api import health as health_module
from app.infra import logging_config


@pytest.fixture
def _isolated_log(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """
    Point the rotating file handler at a throwaway log file and reset
    the module-level ``_LOGGING_CONFIGURED`` guard so each test
    reconfigures cleanly.

    Mirrors the fixture in ``tests/test_logging_config.py`` so the
    logging backbone behaves identically under test.

    Returns:
        The tmp-file path the test's log records will be written to.
    """
    log_file = tmp_path / "app.log"
    monkeypatch.setattr(logging_config.settings, "LOG_FILE", str(log_file))
    monkeypatch.setattr(logging_config, "_LOGGING_CONFIGURED", False)
    root = logging.getLogger()
    for handler in list(root.handlers):
        root.removeHandler(handler)
    logging_config.configure_logging()
    return log_file


@pytest.fixture
def client(_isolated_log: Path) -> TestClient:
    """
    FastAPI TestClient bound to the real ``app.main.app`` **without**
    triggering the app lifespan.

    The scheduler and DB connection probes in
    :func:`app.main.lifespan` are explicitly skipped so tests remain
    hermetic. The ``_isolated_log`` fixture reinstalls
    :func:`configure_logging` so structlog events emitted by the
    endpoint land in the tmp log file.
    """
    from app.main import app

    return TestClient(app)


def _read_events(log_file: Path) -> list[dict]:
    """Flush stdlib handlers and parse each JSON line from the log."""
    for handler in logging.getLogger().handlers:
        handler.flush()
    content = log_file.read_text(encoding="utf-8")
    return [json.loads(line) for line in content.splitlines() if line.strip()]


def test_main_registers_health_router_once() -> None:
    """
    ``app.main.app`` includes ``/healthz`` and ``/readyz`` exactly once
    each, proving the router is wired via ``include_router``. Satisfies
    Build Packet acceptance check 2.
    """
    from app.main import app

    paths = [getattr(route, "path", None) for route in app.routes]
    assert paths.count("/healthz") == 1
    assert paths.count("/readyz") == 1


def test_healthz_returns_ok_and_emits_event(client: TestClient, _isolated_log: Path) -> None:
    """
    (a) ``/healthz`` returns 200 with the expected body shape and emits
    a ``health.check`` structured event.
    """
    response = client.get("/healthz")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"]
    assert body["version"]

    timestamp = body["timestamp"]
    assert timestamp.endswith("Z") or "+00:00" in timestamp, (
        f"timestamp {timestamp!r} must be timezone-aware UTC"
    )

    events = _read_events(_isolated_log)
    check_events = [e for e in events if e.get("event") == "health.check"]
    assert check_events, "expected the health.check event to be written"
    assert check_events[-1].get("outcome") == "ok"


def test_readyz_returns_ok_when_all_checks_pass(
    client: TestClient,
    _isolated_log: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    (b) ``/readyz`` returns 200 when the DB ping succeeds AND every
    required Twilio setting is populated.
    """
    monkeypatch.setattr(health_module, "_db_ping_sync", lambda: None)

    response = client.get("/readyz")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["checks"]["db"] == "ok"
    assert body["checks"]["twilio"] == "ok"
    assert "twilio_missing" not in body["checks"], (
        "twilio_missing must be absent from the body when the check passes"
    )


def test_readyz_returns_503_when_db_fails(
    client: TestClient,
    _isolated_log: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    (c) ``/readyz`` returns 503 when the DB ping fails. The response
    body names ``db`` as the failing sub-check and does not surface the
    raw exception message.
    """

    def _raise() -> None:
        raise RuntimeError("connection refused to secret-bearing-url")

    monkeypatch.setattr(health_module, "_db_ping_sync", _raise)

    response = client.get("/readyz")

    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "fail"
    assert body["checks"]["db"] == "fail"
    assert body["checks"]["twilio"] == "ok"
    # The raw exception message must not leak into the body.
    body_text = json.dumps(body)
    assert "connection refused" not in body_text
    assert "secret-bearing-url" not in body_text


def test_readyz_returns_503_when_twilio_setting_missing(
    client: TestClient,
    _isolated_log: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    (d) ``/readyz`` returns 503 when any required Twilio setting is
    empty. The response body lists the missing setting name(s).
    """
    monkeypatch.setattr(health_module, "_db_ping_sync", lambda: None)
    monkeypatch.setattr(health_module.settings, "TWILIO_ACCOUNT_SID", "")

    response = client.get("/readyz")

    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "fail"
    assert body["checks"]["twilio"] == "fail"
    assert "TWILIO_ACCOUNT_SID" in body["checks"]["twilio_missing"]


def test_readyz_db_probe_is_time_bounded(
    client: TestClient,
    _isolated_log: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    A hung DB ping surfaces as a 503 within the configured timeout
    rather than blocking the HTTP response.

    Sets :data:`health.READYZ_DB_TIMEOUT_SECONDS` to a short value and
    substitutes a :func:`time.sleep` so the ping would otherwise hang
    for five seconds.
    """
    monkeypatch.setattr(health_module, "READYZ_DB_TIMEOUT_SECONDS", 0.2)

    def _hang() -> None:
        time.sleep(5.0)

    monkeypatch.setattr(health_module, "_db_ping_sync", _hang)

    start = time.monotonic()
    response = client.get("/readyz")
    elapsed = time.monotonic() - start

    assert response.status_code == 503
    # Generous slack for CI / cold FastAPI stack; still well under the
    # 5 s hung call the sleep would have produced.
    assert elapsed < 2.5, f"/readyz took {elapsed:.2f}s — timeout guard did not fire"
    assert response.json()["checks"]["db"] == "fail"


def test_readyz_event_carries_outcome_and_no_secrets(
    client: TestClient,
    _isolated_log: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    (e) ``/readyz`` emits a ``health.ready`` structured event with an
    ``outcome`` field. The log file never contains the actual Twilio
    secret values from the settings object.
    """
    monkeypatch.setattr(health_module, "_db_ping_sync", lambda: None)

    client.get("/readyz")

    events = _read_events(_isolated_log)
    ready_events = [e for e in events if e.get("event") == "health.ready"]
    assert ready_events, "expected the health.ready event"
    record = ready_events[-1]
    assert record.get("outcome") in {
        "ok",
        "db_unreachable",
        "twilio_missing",
        "db_unreachable_and_twilio_missing",
    }
    assert record.get("db_status") in {"ok", "fail"}
    assert record.get("twilio_status") in {"ok", "fail"}

    log_text = _isolated_log.read_text(encoding="utf-8")
    # The real secret values seeded by tests/conftest.py must never
    # appear in log output. If any of these tokens land in the log the
    # "secrets never logged" guarantee has been violated.
    assert health_module.settings.TWILIO_AUTH_TOKEN not in log_text
    assert health_module.settings.TWILIO_ACCOUNT_SID not in log_text
    assert health_module.settings.TWILIO_PHONE_NUMBER not in log_text
