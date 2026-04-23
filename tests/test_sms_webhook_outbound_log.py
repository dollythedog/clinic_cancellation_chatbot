"""
Regression tests for BUG-001 in ``app/api/sms_webhook.py`` (Slice 2026-04-23-07).

Prior to this slice, the three outbound-log builders in
``handle_opt_out``, ``handle_help_request``, and ``handle_no_response``
referenced an undefined name ``To`` (the function-local form parameter
from the parent ``handle_inbound_sms`` signature, not visible in the
helper scope). Any request reaching one of those reply paths raised a
``NameError`` after the ``twilio_client.send_sms`` call but before the
``MessageLog`` row was inserted — outbound logging was silently broken
for STOP, HELP, and NO replies.

The BUG-001 fix replaces ``from_phone=To`` with
``from_phone=settings.TWILIO_PHONE_NUMBER`` at lines ~188, ~230, ~306.
These tests lock the fix in against regression and also assert the
outbound ``MessageLog`` row is actually constructed with the correct
field values — covering both the ``NameError``-does-not-raise invariant
and the log-correctness invariant.

Tests do not require a live database or a live Twilio account. The
``twilio_client.send_sms`` is monkeypatched to a no-op observer; a
``_StubSession`` collects objects passed to ``db.add`` so the test can
assert on the ``MessageLog`` field values.
"""

from __future__ import annotations

from typing import Any

import pytest

from app.api.sms_webhook import (
    handle_help_request,
    handle_no_response,
    handle_opt_out,
)
from app.infra.models import MessageDirection, MessageLog, PatientContact
from app.infra.settings import settings

TEST_PATIENT_PHONE = "+15551234567"


class _StubQuery:
    """Records filter_by calls and returns a result from ``_results`` in FIFO order."""

    def __init__(self, results: list[Any]) -> None:
        self._results = results

    def filter_by(self, **_kwargs: Any) -> _StubQuery:
        return self

    def first(self) -> Any:
        return self._results.pop(0) if self._results else None


class _StubSession:
    """
    Minimal stand-in for a SQLAlchemy ``Session``. Captures ``add`` /
    ``commit`` / ``query`` calls so the test can assert on the
    ``MessageLog`` rows that ``sms_webhook`` builders insert.
    """

    def __init__(self, query_results: dict[type, list[Any]] | None = None) -> None:
        self.added: list[Any] = []
        self.commits: int = 0
        self._query_results: dict[type, list[Any]] = query_results or {}

    def add(self, obj: Any) -> None:
        self.added.append(obj)

    def commit(self) -> None:
        self.commits += 1

    def query(self, model: type) -> _StubQuery:
        return _StubQuery(self._query_results.get(model, []))


def _outbound_message_logs(added: list[Any]) -> list[MessageLog]:
    """Filter captured ``session.add`` calls down to outbound ``MessageLog`` rows."""
    return [
        obj
        for obj in added
        if isinstance(obj, MessageLog) and obj.direction == MessageDirection.OUTBOUND
    ]


@pytest.fixture
def stub_send(monkeypatch: pytest.MonkeyPatch) -> list[dict[str, Any]]:
    """Monkeypatch ``twilio_client.send_sms`` so handlers never make a real call."""
    calls: list[dict[str, Any]] = []

    def _observer(*, to: str, body: str, status_callback: str | None = None) -> str | None:
        calls.append({"to": to, "body": body, "status_callback": status_callback})
        return "SM-stubbed"

    import app.api.sms_webhook as sms_webhook_module

    monkeypatch.setattr(sms_webhook_module.twilio_client, "send_sms", _observer)
    return calls


# ---------------------------------------------------------------------------
# Acceptance Checks 9, 10, 11: one test per BUG-001 site
# ---------------------------------------------------------------------------


def test_stop_path_outbound_log(stub_send: list[dict[str, Any]]) -> None:
    """
    Acceptance Check #9: ``handle_opt_out`` writes an outbound
    ``MessageLog`` row whose ``from_phone`` is the Twilio phone number
    from settings, and does not raise ``NameError``.
    """
    # Pre-create the patient so the opt-out branch takes the "found" path
    existing = PatientContact(phone_e164=TEST_PATIENT_PHONE, opt_out=False)
    existing.id = 42  # type: ignore[assignment]
    db = _StubSession(query_results={PatientContact: [existing]})

    response = handle_opt_out(TEST_PATIENT_PHONE, db)

    assert response is not None
    outbound = _outbound_message_logs(db.added)
    assert len(outbound) == 1, f"expected exactly one outbound MessageLog, got {len(outbound)}"
    row = outbound[0]
    assert row.from_phone == settings.TWILIO_PHONE_NUMBER
    assert row.to_phone == TEST_PATIENT_PHONE
    assert row.direction == MessageDirection.OUTBOUND
    assert row.body  # non-empty STOP response body
    assert len(stub_send) == 1  # twilio_client.send_sms called exactly once


def test_help_path_outbound_log(stub_send: list[dict[str, Any]]) -> None:
    """
    Acceptance Check #10: ``handle_help_request`` writes an outbound
    ``MessageLog`` row whose ``from_phone`` is the Twilio phone number
    from settings, and does not raise ``NameError``.
    """
    db = _StubSession()

    response = handle_help_request(TEST_PATIENT_PHONE, db)

    assert response is not None
    outbound = _outbound_message_logs(db.added)
    assert len(outbound) == 1
    row = outbound[0]
    assert row.from_phone == settings.TWILIO_PHONE_NUMBER
    assert row.to_phone == TEST_PATIENT_PHONE
    assert row.direction == MessageDirection.OUTBOUND
    assert row.body
    assert len(stub_send) == 1


def test_no_reply_outbound_log(
    stub_send: list[dict[str, Any]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Acceptance Check #11: the NO-reply send path (``handle_no_response``)
    writes its outbound ``MessageLog`` row without raising
    ``NameError``, and the row's ``from_phone`` matches
    ``settings.TWILIO_PHONE_NUMBER``.

    ``OfferOrchestrator`` is stubbed to return a fixed
    ``(success, response_text)`` tuple so the test does not exercise
    the orchestrator's DB queries.
    """

    class _StubOrchestrator:
        def __init__(self, _db: Any) -> None:
            pass

        def handle_patient_decline(
            self,
            from_phone: str,
            message_body: str,
        ) -> tuple[bool, str]:
            return True, "Thanks for letting us know."

    import app.api.sms_webhook as sms_webhook_module

    monkeypatch.setattr(sms_webhook_module, "OfferOrchestrator", _StubOrchestrator)

    db = _StubSession()
    response = handle_no_response(TEST_PATIENT_PHONE, "NO", db)

    assert response is not None
    outbound = _outbound_message_logs(db.added)
    assert len(outbound) == 1
    row = outbound[0]
    assert row.from_phone == settings.TWILIO_PHONE_NUMBER
    assert row.to_phone == TEST_PATIENT_PHONE
    assert row.direction == MessageDirection.OUTBOUND
    assert "thanks" in row.body.lower()
    assert len(stub_send) == 1
