"""
Regression tests for the ``app.infra`` package-hygiene rule (QA-05).

Locks in the invariant that ``app/infra/__init__.py`` does not re-export
``settings`` or ``twilio_client`` under names that collide with the
``app.infra.settings`` and ``app.infra.twilio_client`` submodules. The
collision would cause ``import app.infra.settings as X`` to return the
instance (not the module) because Python's bytecode resolves the final
segment via ``getattr(app.infra, 'settings')``, and the re-export had
rebound that attribute to the instance.

See ``DECISIONS.md`` 2026-04-23 "Package hygiene — ``app.infra`` must
not re-export submodule attributes under the same name as the submodule"
for the full rationale and the two-slice cost history that motivated
this rule.

Landed in Build Slice 2026-04-23-09 (Packet 2026-04-23-09, WBS QA-05).
"""

from __future__ import annotations

import types

import app.infra
import app.infra.settings
import app.infra.twilio_client


class TestSubmodulesResolveToModuleObjects:
    """``import app.infra.X as Y`` must yield a module, not a rebound instance."""

    def test_settings_submodule_is_a_module(self) -> None:
        """``app.infra.settings`` must be a module object."""
        assert isinstance(app.infra.settings, types.ModuleType), (
            "app.infra.settings must resolve to a module object, not an instance. "
            "If this fails, `app/infra/__init__.py` has likely re-introduced "
            "`from app.infra.settings import settings` which shadows the submodule."
        )
        assert app.infra.settings.__name__ == "app.infra.settings"

    def test_twilio_client_submodule_is_a_module(self) -> None:
        """``app.infra.twilio_client`` must be a module object."""
        assert isinstance(app.infra.twilio_client, types.ModuleType), (
            "app.infra.twilio_client must resolve to a module object, not an "
            "instance. If this fails, `app/infra/__init__.py` has likely "
            "re-introduced `from app.infra.twilio_client import twilio_client` "
            "which shadows the submodule."
        )
        assert app.infra.twilio_client.__name__ == "app.infra.twilio_client"


class TestPackageExportsDoNotShadowSubmodules:
    """The ``app.infra`` package's ``__all__`` must not contain shadow names."""

    def test_all_does_not_contain_settings(self) -> None:
        """``"settings"`` must not be in ``app.infra.__all__``."""
        assert "settings" not in app.infra.__all__, (
            "Re-exporting `settings` from app.infra shadows the "
            "app.infra.settings submodule. See DECISIONS.md 2026-04-23 "
            '"Package hygiene".'
        )

    def test_all_does_not_contain_twilio_client(self) -> None:
        """``"twilio_client"`` must not be in ``app.infra.__all__``."""
        assert "twilio_client" not in app.infra.__all__, (
            "Re-exporting `twilio_client` from app.infra shadows the "
            "app.infra.twilio_client submodule. See DECISIONS.md 2026-04-23 "
            '"Package hygiene".'
        )


class TestSubmoduleContentIsReachableThroughDirectImports:
    """The canonical ``from app.infra.X import Y`` imports still work.

    This confirms the deletion of the re-exports did not break the
    submodule-attribute access path — it only removed the package-level
    shorthand that nothing was using anyway (the pre-execution grep
    in Packet 2026-04-23-09 confirmed zero callers of the shadow form).
    """

    def test_settings_instance_reachable_via_direct_import(self) -> None:
        """``from app.infra.settings import settings`` must still work."""
        from app.infra.settings import settings as settings_instance

        assert settings_instance is not None
        assert hasattr(settings_instance, "DATABASE_URL")
        assert hasattr(settings_instance, "TWILIO_ACCOUNT_SID")

    def test_twilio_client_instance_reachable_via_direct_import(self) -> None:
        """``from app.infra.twilio_client import twilio_client`` must still work."""
        from app.infra.twilio_client import twilio_client as twilio_client_instance

        assert twilio_client_instance is not None
