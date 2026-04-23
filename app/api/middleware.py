"""
Twilio Signature Verification Middleware (APP-03)

Enforces cryptographic proof that inbound POSTs on Twilio-webhook-facing
paths (`/sms/*` and `/twilio/*`) actually originated from Twilio.
Unsigned or invalidly-signed requests are rejected with HTTP 403 before
any route handler runs. All other paths (``/healthz``, ``/readyz``,
``/health``, ``/``, ``/docs``, ``/admin/*``) pass through unmodified.

Signature verification uses :class:`twilio.request_validator.RequestValidator`
against ``settings.TWILIO_AUTH_TOKEN`` plus the sorted form-encoded body
parameters, matching Twilio's published signing algorithm (HMAC-SHA1 of
the canonical URL concatenated with ``key + value`` for each sorted form
field).

**URL strategy.** The URL Twilio signs is the public URL it POSTed to —
behind the Cloudflare Tunnel + NSSM deployment on the Windows server,
that URL's scheme and host differ from what FastAPI sees internally. The
middleware prefers ``settings.TWILIO_WEBHOOK_BASE_URL`` as the canonical
scheme-plus-host source and appends the request's path + query. When
``TWILIO_WEBHOOK_BASE_URL`` is unset the middleware falls back to
``request.url`` and emits a warn-level ``webhook.signature.url_fallback``
event — useful in local dev, broken for production behind a proxy. See
``DECISIONS.md`` 2026-04-23 "Twilio signature middleware URL strategy"
for the full rationale.

**PHI discipline.** This middleware never logs the raw signature, the
auth token, or full phone numbers. On verification success the event
is ``webhook.signature.verified`` with the request path only; on
rejection the event is ``webhook.signature.rejected`` with ``reason``
and ``path``. The downstream handler continues to mask phone numbers
via ``_mask_phone`` on its own structured events.

Owning work package: APP-03 (Design Schematic §5.C). Landed in Build
Slice 2026-04-23-07 (Packet 2026-04-23-07).
"""

from __future__ import annotations

from typing import Any
from urllib.parse import parse_qs

import structlog
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from twilio.request_validator import RequestValidator

from app.infra.settings import settings

logger = structlog.get_logger(__name__)

#: URL-path prefixes whose POSTs must bear a valid ``X-Twilio-Signature``.
#: ``/sms/*`` covers inbound SMS from patients; ``/twilio/*`` covers
#: delivery-status callbacks. Adding a new prefix is a deliberate act —
#: every new Twilio-facing router must be accounted for here or it
#: bypasses the gate.
PROTECTED_PREFIXES: tuple[str, ...] = ("/sms/", "/twilio/")

#: Header name Twilio uses for the request signature.
TWILIO_SIG_HEADER: str = "X-Twilio-Signature"


def _is_protected(path: str) -> bool:
    """Return ``True`` iff ``path`` starts with one of the Twilio-webhook prefixes."""
    return any(path.startswith(prefix) for prefix in PROTECTED_PREFIXES)


def _canonical_signing_url(request: Request) -> tuple[str, bool]:
    """
    Compute the URL string Twilio signed against.

    Returns a ``(canonical_url, used_fallback)`` tuple. ``used_fallback``
    is ``True`` when ``settings.TWILIO_WEBHOOK_BASE_URL`` is unset and
    the caller should emit a warn-level ``webhook.signature.url_fallback``
    event — the raw ``request.url`` is the internal FastAPI URL, which
    does not match what Twilio signed whenever the app runs behind a
    reverse proxy or tunnel.
    """
    base = settings.TWILIO_WEBHOOK_BASE_URL
    if base:
        canonical = base.rstrip("/") + request.url.path
        if request.url.query:
            canonical = canonical + "?" + request.url.query
        return canonical, False
    return str(request.url), True


def _parse_form_params(raw_body: bytes) -> dict[str, str]:
    """
    Decode a ``application/x-www-form-urlencoded`` request body to the
    single-value dict form ``RequestValidator.validate`` expects.

    Twilio's signature covers form fields by concatenating sorted
    ``key + value`` pairs. Lists are flattened to the first value for
    this purpose — which is consistent with Twilio's own signer, which
    emits scalar form parameters. Empty bodies decode to ``{}``.
    """
    # ``parse_qs`` with ``keep_blank_values=True`` round-trips empty
    # form fields rather than silently dropping them — important
    # because Twilio's signature includes empty fields.
    decoded = parse_qs(raw_body.decode("utf-8"), keep_blank_values=True)
    return {key: values[0] if values else "" for key, values in decoded.items()}


class TwilioSignatureMiddleware(BaseHTTPMiddleware):
    """
    ASGI middleware enforcing Twilio signature verification on protected paths.

    See the module docstring for the URL strategy, PHI discipline, and
    the owning work package reference.
    """

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        """
        Reject unsigned / invalid-signature requests on protected prefixes;
        pass all other requests through unmodified.
        """
        path = request.url.path

        if not _is_protected(path):
            return await call_next(request)

        signature = request.headers.get(TWILIO_SIG_HEADER)

        if not signature:
            logger.warning(
                "webhook.signature.rejected",
                path=path,
                reason="missing_signature",
                signature_present=False,
                outcome="rejected",
            )
            return JSONResponse(
                status_code=403,
                content={"detail": "Missing Twilio signature"},
            )

        # Capture the raw body once. BaseHTTPMiddleware's default
        # behavior consumes the ASGI receive stream, so we re-inject
        # the body below before handing off to the downstream handler.
        raw_body = await request.body()
        params = _parse_form_params(raw_body)

        canonical_url, used_fallback = _canonical_signing_url(request)
        if used_fallback:
            logger.warning(
                "webhook.signature.url_fallback",
                path=path,
                reason="TWILIO_WEBHOOK_BASE_URL unset; using request.url",
                outcome="fallback",
            )

        validator = RequestValidator(settings.TWILIO_AUTH_TOKEN)
        if not validator.validate(canonical_url, params, signature):
            logger.warning(
                "webhook.signature.rejected",
                path=path,
                reason="invalid_signature",
                signature_present=True,
                outcome="rejected",
            )
            return JSONResponse(
                status_code=403,
                content={"detail": "Invalid Twilio signature"},
            )

        logger.info(
            "webhook.signature.verified",
            path=path,
            signature_present=True,
            outcome="verified",
        )

        # Re-inject the raw body so the downstream handler's
        # ``request.form()`` call can re-parse it. BaseHTTPMiddleware's
        # own body read exhausts the original ASGI receive channel;
        # without this replay the handler sees an empty body and raises
        # 422 on missing Form fields.
        body_replayed = False

        async def replay_receive() -> dict[str, Any]:
            nonlocal body_replayed
            if body_replayed:
                return {"type": "http.disconnect"}
            body_replayed = True
            return {
                "type": "http.request",
                "body": raw_body,
                "more_body": False,
            }

        # ``request._receive`` replacement is the documented Starlette idiom
        # for replaying a consumed body; see starlette.requests.Request source.
        request._receive = replay_receive

        return await call_next(request)
