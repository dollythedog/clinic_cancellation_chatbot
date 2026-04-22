"""
Logging Configuration — Central structlog-based logging backbone.

This module defines :func:`configure_logging`, the single entry point for
initializing the application's structured-logging stack. It is invoked
exactly once from the FastAPI lifespan hook, before routers register.

Handlers installed
------------------
- ``RotatingFileHandler`` writing newline-delimited JSON records to
  ``settings.LOG_FILE`` (default ``data/logs/app.log``). Size-based
  rotation at ``settings.LOG_MAX_BYTES`` with ``settings.LOG_BACKUP_COUNT``
  backups. Directory is created if missing.
- ``NTEventLogHandler`` attached at level ``ERROR`` on Windows hosts with
  ``pywin32`` available. Non-Windows hosts (and Windows hosts without
  ``pywin32``) see a graceful no-op so dev environments remain
  frictionless.
- ``StreamHandler`` on ``stderr`` for local development visibility.

Processor chain (applied to every record)
-----------------------------------------
- ``contextvars.merge_contextvars`` — carry correlation context across
  async boundaries.
- ``stdlib.add_logger_name`` — stamp module path (``logger``).
- ``stdlib.add_log_level`` — stamp level name (``level``).
- ``TimeStamper(fmt="iso", utc=True)`` — timezone-aware UTC timestamp.
- ``StackInfoRenderer`` + ``format_exc_info`` — render exception info.
- ``JSONRenderer`` — final serialization.

Usage
-----
Every module obtains its logger the same way::

    import structlog
    logger = structlog.get_logger(__name__)

Never configure handlers outside this module. Never call
``logging.basicConfig``.

PHI Logging Guardrail
---------------------
The codebase treats ``patient_id`` (integer DB primary key) as the only
permitted patient identifier in structured log fields. Names, phone
numbers, dates of birth, and free-text reply bodies must not appear in
log fields. Full message bodies live in the ``message_log`` table only.
See ``DECISIONS.md`` for rationale.

Author: Jonathan Ives (@dollythedog)
"""

from __future__ import annotations

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Any

import structlog

from app.infra.settings import settings

#: Module-level flag so repeated calls to :func:`configure_logging` are
#: no-ops. Tests reset this via monkeypatch.
_LOGGING_CONFIGURED: bool = False

#: Third-party loggers whose default INFO-level chatter drowns the
#: application signal. Their levels are raised to WARNING at configure
#: time; emitting ERROR from them is still preserved.
_NOISY_LOGGERS: tuple[str, ...] = (
    "urllib3",
    "twilio.http_client",
    "apscheduler",
    "apscheduler.scheduler",
    "apscheduler.executors.default",
)


def _coerce_log_level(level_name: str) -> int:
    """
    Translate a case-insensitive level name (``"info"``, ``"DEBUG"``, …)
    into the stdlib integer value.

    Unknown names fall back to ``logging.INFO`` rather than raising, so
    a typo in ``.env`` cannot block application startup.
    """
    return logging.getLevelNamesMapping().get(level_name.upper(), logging.INFO)


def _build_file_handler() -> logging.handlers.RotatingFileHandler:
    """
    Build a size-rotated file handler writing to ``settings.LOG_FILE``.

    Creates the parent directory if it does not exist so the first run
    on a fresh deployment succeeds without a separate provisioning step.
    """
    log_path = Path(settings.LOG_FILE)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    handler = logging.handlers.RotatingFileHandler(
        filename=str(log_path),
        maxBytes=settings.LOG_MAX_BYTES,
        backupCount=settings.LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    return handler


def _build_windows_event_log_handler() -> logging.Handler | None:
    """
    Return a Windows Event Log handler when available, else ``None``.

    The handler is only attached on Windows hosts with ``pywin32``
    installed. On non-Windows platforms or when ``pywin32`` is missing,
    this returns ``None`` and the caller skips the sink. A short notice
    is written to stderr so the operator knows the sink was skipped.
    """
    if sys.platform != "win32":
        return None
    try:
        from logging.handlers import NTEventLogHandler
    except ImportError:
        return None
    try:
        handler = NTEventLogHandler(appname="CancellationBot")
    except Exception as exc:  # pywin32 import errors surface at handler construction
        sys.stderr.write(
            "Windows Event Log sink unavailable "
            f"({exc.__class__.__name__}: {exc}); continuing with file + stream handlers.\n"
        )
        return None
    handler.setLevel(logging.ERROR)
    return handler


def _shared_processors() -> list[Any]:
    """
    The processor chain applied to both structlog-native events and
    foreign stdlib-logging records routed through ``ProcessorFormatter``.
    """
    return [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]


def configure_logging() -> None:
    """
    Configure the application-wide logging backbone.

    This function is idempotent: the first call wires the root logger,
    and subsequent calls return immediately. It must be invoked exactly
    once at FastAPI startup (see ``app.main.lifespan``).

    Side effects
    ------------
    - Root logger level set to ``settings.LOG_LEVEL``.
    - Existing root-logger handlers are removed so no duplicate,
      unstructured output survives from earlier ``logging.basicConfig``
      calls or autoloaded stdlib defaults.
    - One ``RotatingFileHandler``, one ``StreamHandler(stderr)``, and
      (on Windows with ``pywin32``) one ``NTEventLogHandler`` are
      attached, each using a structlog ``ProcessorFormatter`` with a
      ``JSONRenderer`` terminator.
    - Noisy third-party loggers are clamped to ``WARNING``.

    Raises
    ------
    OSError
        If the log directory cannot be created or the log file cannot be
        opened for append. Loud failure is the intended behavior.
    """
    global _LOGGING_CONFIGURED
    if _LOGGING_CONFIGURED:
        return

    log_level = _coerce_log_level(settings.LOG_LEVEL)
    shared = _shared_processors()

    structlog.configure(
        processors=[
            *shared,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    json_formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared,
        processor=structlog.processors.JSONRenderer(),
    )

    root = logging.getLogger()
    for existing in list(root.handlers):
        root.removeHandler(existing)
    root.setLevel(log_level)

    file_handler = _build_file_handler()
    file_handler.setFormatter(json_formatter)
    file_handler.setLevel(log_level)
    root.addHandler(file_handler)

    stream_handler = logging.StreamHandler(sys.stderr)
    stream_handler.setFormatter(json_formatter)
    stream_handler.setLevel(log_level)
    root.addHandler(stream_handler)

    event_log_handler = _build_windows_event_log_handler()
    if event_log_handler is not None:
        event_log_handler.setFormatter(json_formatter)
        root.addHandler(event_log_handler)

    for noisy in _NOISY_LOGGERS:
        logging.getLogger(noisy).setLevel(logging.WARNING)

    _LOGGING_CONFIGURED = True

    # Emit the first structured event so operators can confirm the
    # backbone is live and see which handlers are attached.
    startup_logger = structlog.get_logger(__name__)
    startup_logger.info(
        "logging.configured",
        log_file=str(Path(settings.LOG_FILE).resolve()),
        max_bytes=settings.LOG_MAX_BYTES,
        backup_count=settings.LOG_BACKUP_COUNT,
        level=settings.LOG_LEVEL.upper(),
        windows_event_log=event_log_handler is not None,
        stream_sink=True,
    )
