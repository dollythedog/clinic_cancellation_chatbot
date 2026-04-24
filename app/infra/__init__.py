"""Infrastructure layer — database, settings, external services.

**Package-hygiene rule (do not re-export submodule-shadowing names).**
This package deliberately does NOT re-export ``settings`` (from
``app.infra.settings``) or ``twilio_client`` (from
``app.infra.twilio_client``). Re-exporting an attribute under the same
name as a submodule rebinds the package's attribute for that submodule
to the re-exported object. Python's ``import app.infra.settings as X``
bytecode resolves the final segment via ``getattr(app.infra, 'settings')``,
so the shadow returns the instance (not the submodule) and downstream
``X.settings`` or ``X.Settings`` lookups fail mysteriously. Removing
these two re-exports fixes a trap that cost revise attempts in Build
Slices 2026-04-23-07 and 2026-04-23-08.

Callers should always import singletons via the submodule:

    from app.infra.settings import settings
    from app.infra.twilio_client import twilio_client

See ``DECISIONS.md`` 2026-04-23 "Package hygiene — ``app.infra`` must not
re-export submodule attributes under the same name as the submodule"
for the full rule and the regression test locking it in
(``tests/test_infra_package_imports.py``).
"""

from app.infra.db import get_db_dependency, get_session, session_scope
from app.infra.models import (
    Base,
    CancellationEvent,
    CancellationStatus,
    MessageDirection,
    MessageLog,
    MessageStatus,
    Offer,
    OfferState,
    PatientContact,
    ProviderReference,
    StaffUser,
    WaitlistEntry,
)

__all__ = [
    "get_session",
    "session_scope",
    "get_db_dependency",
    "Base",
    "PatientContact",
    "ProviderReference",
    "WaitlistEntry",
    "CancellationEvent",
    "Offer",
    "MessageLog",
    "StaffUser",
    "CancellationStatus",
    "OfferState",
    "MessageDirection",
    "MessageStatus",
]
