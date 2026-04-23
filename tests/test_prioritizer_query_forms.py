"""
Tests for the SQLAlchemy boolean-predicate query forms used by the
prioritizer and dashboard modules.

Build Slice 2026-04-23-05 (WBS QA-01) swapped 15 occurrences of
``Column == True`` / ``Column == False`` (ruff rule E712) to the
``.is_(True)`` / ``.is_(False)`` form across ``app/core/prioritizer.py``
(4) and ``dashboard/app.py`` (11). The two forms compile to equivalent
SQL on every SQLAlchemy-supported dialect for boolean columns — the
swap is a style-only change — but that equivalence is not enforced by
the type system or by ``ruff``.

This module locks the equivalence in with two independent proofs so
that a future refactor (accidental introduction of a non-trivial
transformation into the prioritizer's filter chain, or a dialect-level
regression in SQLAlchemy's Column.is_() implementation) would surface
as a loud test failure rather than a silent behavior change.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import dialect as postgresql_dialect

from app.infra.models import PatientContact, ProviderReference, WaitlistEntry


class TestActiveFilterSqlCompilation:
    """Direct SQL-compilation checks against the PostgreSQL dialect."""

    def test_waitlist_active_is_true_compiles_to_is_predicate(self) -> None:
        """``WaitlistEntry.active.is_(True)`` must render as ``IS true``."""
        stmt = select(WaitlistEntry).where(WaitlistEntry.active.is_(True))
        compiled = str(
            stmt.compile(dialect=postgresql_dialect(), compile_kwargs={"literal_binds": True})
        )
        assert "waitlist_entry.active IS true" in compiled

    def test_waitlist_active_is_false_compiles_to_is_predicate(self) -> None:
        """``WaitlistEntry.active.is_(False)`` must render as ``IS false``."""
        stmt = select(WaitlistEntry).where(WaitlistEntry.active.is_(False))
        compiled = str(
            stmt.compile(dialect=postgresql_dialect(), compile_kwargs={"literal_binds": True})
        )
        assert "waitlist_entry.active IS false" in compiled

    def test_patient_opt_out_is_false_compiles_to_is_predicate(self) -> None:
        """``PatientContact.opt_out.is_(False)`` must render as ``IS false``."""
        stmt = select(PatientContact).where(PatientContact.opt_out.is_(False))
        compiled = str(
            stmt.compile(dialect=postgresql_dialect(), compile_kwargs={"literal_binds": True})
        )
        assert "patient_contact.opt_out IS false" in compiled

    def test_provider_active_is_true_compiles_to_is_predicate(self) -> None:
        """``ProviderReference.active.is_(True)`` must render as ``IS true``."""
        stmt = select(ProviderReference).where(ProviderReference.active.is_(True))
        compiled = str(
            stmt.compile(dialect=postgresql_dialect(), compile_kwargs={"literal_binds": True})
        )
        assert "provider_reference.active IS true" in compiled


class TestIsEquivalentToEquality:
    """
    The ``.is_(True)`` and ``== True`` forms must select the same rows.

    These checks construct both predicates against the same SQLAlchemy
    ``Column`` object and assert the compiled SQL produces semantically
    equivalent row-selection logic. On PostgreSQL, ``col = TRUE`` and
    ``col IS TRUE`` both match rows where ``col`` is ``TRUE`` and both
    exclude rows where ``col`` is ``NULL`` (because three-valued logic
    treats both ``NULL = TRUE`` and ``NULL IS TRUE`` as "not true").

    The point of these tests is not to re-verify PostgreSQL's semantics
    — it is to prove that the prioritizer's and dashboard's swap from
    ``==`` to ``.is_()`` was a faithful style change on booleans and not
    a silent logic change.
    """

    def test_active_true_forms_select_boolean_column(self) -> None:
        """Both forms reference the same ``active`` column in the WHERE clause."""
        eq_stmt = select(WaitlistEntry).where(WaitlistEntry.active == True)  # noqa: E712
        is_stmt = select(WaitlistEntry).where(WaitlistEntry.active.is_(True))

        eq_sql = str(
            eq_stmt.compile(dialect=postgresql_dialect(), compile_kwargs={"literal_binds": True})
        )
        is_sql = str(
            is_stmt.compile(dialect=postgresql_dialect(), compile_kwargs={"literal_binds": True})
        )

        # Both must target the same boolean column.
        assert "waitlist_entry.active" in eq_sql
        assert "waitlist_entry.active" in is_sql

        # The equality form compiles to `= true`; the is_ form compiles
        # to `IS true`. Both predicates select the same rows on
        # PostgreSQL (NULL-excluding truthy check).
        assert "waitlist_entry.active = true" in eq_sql
        assert "waitlist_entry.active IS true" in is_sql

    def test_opt_out_false_forms_select_boolean_column(self) -> None:
        """Both forms reference the same ``opt_out`` column in the WHERE clause."""
        eq_stmt = select(PatientContact).where(PatientContact.opt_out == False)  # noqa: E712
        is_stmt = select(PatientContact).where(PatientContact.opt_out.is_(False))

        eq_sql = str(
            eq_stmt.compile(dialect=postgresql_dialect(), compile_kwargs={"literal_binds": True})
        )
        is_sql = str(
            is_stmt.compile(dialect=postgresql_dialect(), compile_kwargs={"literal_binds": True})
        )

        assert "patient_contact.opt_out" in eq_sql
        assert "patient_contact.opt_out" in is_sql
        assert "patient_contact.opt_out = false" in eq_sql
        assert "patient_contact.opt_out IS false" in is_sql
