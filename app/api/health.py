"""
Health & Readiness Endpoints (APP-07).

Two unauthenticated HTTP probes on the FastAPI service, intentionally
public so external monitors — Windows Task Scheduler (INF-04), NSSM
service supervision, and future uptime probes — can call them without
credentials:

- ``GET /healthz`` — **liveness** probe. Returns 200 when the process is
  alive. Consults neither the database nor any external service; its sole
  job is to prove the HTTP server is accepting requests.
- ``GET /readyz`` — **readiness** probe. Returns 200 when both (a) the
  database is reachable via a cheap, time-bounded ``SELECT 1`` and
  (b) the three required Twilio settings are present on the validated
  :mod:`app.infra.settings.settings` instance. Returns 503 with a
  structured body naming the failing sub-check(s) otherwise.

See ``DECISIONS.md`` for the rationale behind the unauthenticated
design and the liveness-vs-readiness split.

The probes must never expose secret values in their response bodies or
log events — only setting names and failure classifications. The DB
timeout guard (:data:`READYZ_DB_TIMEOUT_SECONDS`) ensures a hung
database produces a 503 rather than a hung HTTP response.

Author: Jonathan Ives (@dollythedog)
"""

from __future__ import annotations

from datetime import UTC, datetime

import anyio
import structlog
from fastapi import APIRouter, Response, status
from sqlalchemy import text

from app.infra.db import engine
from app.infra.settings import settings

logger = structlog.get_logger(__name__)

router = APIRouter(tags=["Health"])

#: Maximum wall-clock seconds the ``/readyz`` probe will spend waiting
#: on the database ping. A hung DB must produce a 503, not a hung HTTP
#: response. Tests override this via ``monkeypatch``.
READYZ_DB_TIMEOUT_SECONDS: float = 2.0

#: Required Twilio settings that must be present on the global
#: :mod:`app.infra.settings.settings` instance for ``/readyz`` to return
#: 200. Slice 1 gates startup on these via ``validate_settings()``;
#: ``/readyz`` repeats the presence check at probe time so an operator
#: can detect mid-run credential scrubbing (e.g. a restart that loaded
#: a truncated ``.env``).
_REQUIRED_TWILIO_SETTINGS: tuple[str, ...] = (
    "TWILIO_ACCOUNT_SID",
    "TWILIO_AUTH_TOKEN",
    "TWILIO_PHONE_NUMBER",
)


def _utc_now_iso() -> str:
    """Return the current time as a timezone-aware ISO-8601 string."""
    return datetime.now(UTC).isoformat()


def _check_twilio_settings_present() -> list[str]:
    """
    Return the names of required Twilio settings whose current value
    on the global :data:`settings` object is empty/missing.

    Returns:
        A list of setting names with empty values. Empty list means all
        required Twilio settings are populated.
    """
    missing: list[str] = []
    for name in _REQUIRED_TWILIO_SETTINGS:
        value = getattr(settings, name, None)
        if not value:
            missing.append(name)
    return missing


def _db_ping_sync() -> None:
    """
    Execute a cheap ``SELECT 1`` against the shared SQLAlchemy engine.

    Exists as a top-level module function (rather than an inline lambda
    or closure) so tests can replace it with ``monkeypatch.setattr``
    without constructing a real database connection.

    Raises:
        Any underlying SQLAlchemy / DB-API exception. The caller
        (:func:`_check_db_reachable`) dispatches this function via
        :func:`anyio.to_thread.run_sync` with
        ``abandon_on_cancel=True`` so a hung DB connect surfaces as a
        timeout on the HTTP response rather than a blocked request.
    """
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))


async def _check_db_reachable(timeout_seconds: float) -> tuple[bool, str | None]:
    """
    Attempt a time-bounded database ping.

    Dispatches the synchronous :func:`_db_ping_sync` to anyio's worker
    thread pool with ``abandon_on_cancel=True``. An outer
    :func:`anyio.fail_after` cancels the awaiting task when the timeout
    expires; because the worker is marked abandonable, anyio releases
    the pool slot from the caller's perspective rather than waiting for
    the blocking call to return. The HTTP response therefore completes
    within ``timeout_seconds`` even when the underlying DB driver is
    hung on a connect or query. The orphaned worker thread finishes in
    the background — bounded by the DB driver's own network / connect
    timeout — and the thread is then reclaimed.

    This is the critical invariant for the readiness-probe contract:
    an external monitor polling ``/readyz`` must receive a 503 inside
    ``timeout_seconds`` regardless of how long the DB driver takes to
    notice it is unreachable. See ``DECISIONS.md`` (2026-04-23 entry)
    for the rationale behind the anyio + ``abandon_on_cancel=True``
    choice and why the earlier ``asyncio.wait_for +
    loop.run_in_executor`` pattern failed that contract.

    Args:
        timeout_seconds: Maximum wall-clock seconds the HTTP response
            will spend waiting for the ping to complete.

    Returns:
        ``(True, None)`` when the ping succeeds. ``(False, reason)``
        when it fails — ``reason`` is ``"timeout"`` for the timeout
        case and the exception class name otherwise. The reason is
        suitable for structured-log fields; it must not be echoed to
        the HTTP response body because some SQLAlchemy errors embed
        connection strings that contain credentials.
    """
    try:
        with anyio.fail_after(timeout_seconds):
            await anyio.to_thread.run_sync(_db_ping_sync, abandon_on_cancel=True)
    except TimeoutError:
        return False, "timeout"
    except Exception as exc:
        # The probe must classify every failure mode; narrower excepts
        # would leak DB driver errors as 500s. The failure reason logged
        # here is a class name only (never the exception message).
        return False, exc.__class__.__name__
    return True, None


@router.get("/healthz")
async def healthz() -> dict:
    """
    Liveness probe.

    Returns 200 with a small JSON body whenever the FastAPI process is
    alive. Does not consult the database, Twilio, or any other external
    service; a green ``/healthz`` means only that the HTTP stack is up.

    Intended callers: Windows Task Scheduler health-check job (INF-04),
    NSSM service supervision, and external uptime monitors.

    Returns:
        Dict with ``status``, ``service``, ``version``, and a
        timezone-aware ISO-8601 ``timestamp``.
    """
    payload: dict = {
        "status": "ok",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": _utc_now_iso(),
    }
    logger.info("health.check", outcome="ok")
    return payload


@router.get("/readyz")
async def readyz(response: Response) -> dict:
    """
    Readiness probe.

    Returns 200 when the service is ready to serve real traffic, 503
    otherwise. Two sub-checks:

    - ``db`` — bounded-timeout ``SELECT 1`` via the shared SQLAlchemy
      engine. Timeout is :data:`READYZ_DB_TIMEOUT_SECONDS`.
    - ``twilio`` — presence of every setting in
      :data:`_REQUIRED_TWILIO_SETTINGS` on the validated
      :data:`settings` instance (empty string or ``None`` counts as
      missing).

    The response body names each sub-check's status (``"ok"`` / ``"fail"``)
    and, when the ``twilio`` check fails, lists the missing setting
    **names** (never their values). Secret values are never included in
    the response or in structured log events.

    Args:
        response: Injected FastAPI :class:`Response`. The handler sets
            ``response.status_code`` explicitly to 200 or 503 based on
            the combined check outcome.

    Returns:
        Dict with ``status``, ``service``, ``version``, timezone-aware
        ``timestamp``, and a ``checks`` sub-dict carrying the per-check
        status.
    """
    db_ok, db_reason = await _check_db_reachable(READYZ_DB_TIMEOUT_SECONDS)
    missing_twilio = _check_twilio_settings_present()
    twilio_ok = not missing_twilio

    checks: dict = {
        "db": "ok" if db_ok else "fail",
        "twilio": "ok" if twilio_ok else "fail",
    }
    if missing_twilio:
        checks["twilio_missing"] = missing_twilio

    if db_ok and twilio_ok:
        outcome = "ok"
        status_code = status.HTTP_200_OK
    elif not db_ok and not twilio_ok:
        outcome = "db_unreachable_and_twilio_missing"
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    elif not db_ok:
        outcome = "db_unreachable"
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    else:
        outcome = "twilio_missing"
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    response.status_code = status_code
    payload: dict = {
        "status": "ok" if outcome == "ok" else "fail",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": _utc_now_iso(),
        "checks": checks,
    }

    # Structured event. Missing Twilio setting NAMES (not values) are
    # safe to log — they are the same names the response body exposes.
    # db_failure_reason is an exception class name only, never an error
    # message, because some SQLAlchemy errors embed the connection
    # string (which may contain credentials).
    logger.info(
        "health.ready",
        outcome=outcome,
        db_status=checks["db"],
        twilio_status=checks["twilio"],
        db_failure_reason=db_reason,
        twilio_missing=missing_twilio or None,
    )
    return payload
