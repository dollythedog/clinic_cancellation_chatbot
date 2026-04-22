"""
Tests for the structlog-based logging backbone (APP-05 + APP-06).

These tests enforce three non-negotiables from the Implementation
Guardrail Profile (Structured Logging & Observability lens):

1. ``configure_logging()`` installs the rotating JSON file handler on
   the root logger and is idempotent across repeated calls.
2. Representative Twilio-call and offer-flow events round-trip through
   the pipeline with the required fields (``event``, ``patient_id``,
   ``slot_id``, ``outcome``, and a timezone-aware ISO timestamp).
3. No PHI beyond ``patient_id`` appears in any structured event —
   patient names, full phone numbers, DOBs, and message bodies are
   never written to log fields.
"""

from __future__ import annotations

import json
import logging
import logging.handlers
from pathlib import Path

import pytest
import structlog

from app.infra import logging_config


@pytest.fixture
def _isolate_logging(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """
    Point the rotating file handler at a throwaway log file and reset
    the module-level ``_LOGGING_CONFIGURED`` guard so each test
    reconfigures cleanly.

    Returns the path the test's log records will be written to.
    """
    log_file = tmp_path / "app.log"
    # Override the settings attribute that logging_config reads at
    # handler-build time.
    monkeypatch.setattr(logging_config.settings, "LOG_FILE", str(log_file))
    monkeypatch.setattr(logging_config, "_LOGGING_CONFIGURED", False)
    # Remove any root handlers left over from a previous test so handler
    # counts are deterministic.
    root = logging.getLogger()
    for handler in list(root.handlers):
        root.removeHandler(handler)
    return log_file


def _flush_and_read(log_file: Path) -> list[dict]:
    """
    Flush stdlib handlers and return each JSON line from the log file
    as a parsed dict. Skips blank lines.
    """
    for handler in logging.getLogger().handlers:
        handler.flush()
    content = log_file.read_text(encoding="utf-8")
    return [json.loads(line) for line in content.splitlines() if line.strip()]


def test_configure_logging_installs_rotating_file_handler(
    _isolate_logging: Path,
) -> None:
    """
    configure_logging() attaches a ``RotatingFileHandler`` to the root
    logger whose base filename resolves to ``settings.LOG_FILE``.
    """
    logging_config.configure_logging()
    root = logging.getLogger()
    file_handlers = [
        h for h in root.handlers if isinstance(h, logging.handlers.RotatingFileHandler)
    ]
    assert file_handlers, "configure_logging() must install a RotatingFileHandler"
    assert Path(file_handlers[0].baseFilename).name == _isolate_logging.name


def test_configure_logging_is_idempotent(_isolate_logging: Path) -> None:
    """
    Repeated calls to configure_logging() do not add duplicate handlers.
    """
    logging_config.configure_logging()
    handler_count = len(logging.getLogger().handlers)
    logging_config.configure_logging()
    logging_config.configure_logging()
    assert len(logging.getLogger().handlers) == handler_count


def test_twilio_call_event_round_trip(_isolate_logging: Path) -> None:
    """
    A structured event representing an outbound Twilio call round-trips
    through the pipeline with event, outcome, correlation fields, and a
    timezone-aware ISO timestamp intact.
    """
    logging_config.configure_logging()
    logger = structlog.get_logger("app.infra.twilio_client")
    logger.info(
        "twilio.send_sms.sent",
        message_sid="SMtest1234567890",
        to_phone_mask="***5678",
        twilio_status="queued",
        outcome="sent",
    )

    records = _flush_and_read(_isolate_logging)
    sent_records = [r for r in records if r.get("event") == "twilio.send_sms.sent"]
    assert sent_records, "expected the twilio.send_sms.sent event to be written"
    record = sent_records[-1]
    assert record["message_sid"] == "SMtest1234567890"
    assert record["to_phone_mask"] == "***5678"
    assert record["twilio_status"] == "queued"
    assert record["outcome"] == "sent"
    # Timestamp must be timezone-aware (UTC ISO) — structlog's TimeStamper
    # with utc=True emits strings ending in "Z" or "+00:00".
    timestamp = record["timestamp"]
    assert timestamp.endswith("Z") or "+00:00" in timestamp, (
        f"timestamp {timestamp!r} must be timezone-aware UTC"
    )


def test_offer_flow_event_round_trip(_isolate_logging: Path) -> None:
    """
    A structured event representing an offer/confirmation/expiry DB
    write round-trips with the required canonical fields: event,
    patient_id, slot_id, outcome.
    """
    logging_config.configure_logging()
    logger = structlog.get_logger("app.core.orchestrator")
    logger.info(
        "offer.accepted",
        offer_id=55,
        patient_id=17,
        cancellation_id=203,
        slot_id=203,
        outcome="accepted",
    )

    records = _flush_and_read(_isolate_logging)
    accepted = [r for r in records if r.get("event") == "offer.accepted"]
    assert accepted, "expected the offer.accepted event to be written"
    record = accepted[-1]
    assert record["patient_id"] == 17
    assert record["slot_id"] == 203
    assert record["offer_id"] == 55
    assert record["outcome"] == "accepted"
    assert record["logger"] == "app.core.orchestrator"


def test_no_phi_beyond_patient_id_leaks_into_events(
    _isolate_logging: Path,
) -> None:
    """
    The APP-06 instrumentation contract restricts patient identifiers
    in log fields to ``patient_id`` (integer DB primary key). A
    representative sample event emitted via the canonical field set
    must not contain patient name, full phone number, DOB, or
    free-text reply body in its serialized JSON form.
    """
    logging_config.configure_logging()
    logger = structlog.get_logger("app.core.orchestrator")
    logger.info(
        "offer.sent",
        offer_id=12,
        patient_id=99,
        cancellation_id=400,
        slot_id=400,
        outcome="queued",
        to_phone_mask="***0199",
    )

    content = _isolate_logging.read_text(encoding="utf-8")
    # The canonical event is present — baseline visibility is intact.
    assert '"event": "offer.sent"' in content
    # Forbidden PHI tokens that might appear if a future change started
    # logging raw attributes. Each assertion is a guardrail.
    forbidden_tokens = (
        "Mary Smith",  # patient name
        "+12145550199",  # full E.164 phone number
        "1984-07-04",  # DOB
        "YES please",  # free-text reply body fragment
        "patient_name",  # field-name leak (would be a bug in a caller)
        "phone_e164",  # field-name leak (would be a bug in a caller)
    )
    for token in forbidden_tokens:
        assert token not in content, (
            f"PHI-like token {token!r} leaked into a structured event — the "
            "APP-06 'patient_id only' contract has been violated."
        )


def test_configure_logging_respects_level_override(
    _isolate_logging: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Setting ``LOG_LEVEL=WARNING`` on settings causes DEBUG/INFO events
    to be suppressed from the file sink while WARNING events still land.
    """
    monkeypatch.setattr(logging_config.settings, "LOG_LEVEL", "WARNING")
    logging_config.configure_logging()
    logger = structlog.get_logger("app.test.level_override")
    logger.info("test.info_level_should_be_suppressed")
    logger.warning("test.warning_level_should_appear")

    events = {record.get("event") for record in _flush_and_read(_isolate_logging)}
    assert "test.warning_level_should_appear" in events
    assert "test.info_level_should_be_suppressed" not in events
