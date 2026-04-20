"""
Tests for the application Settings class and startup configuration validation.

These tests enforce two non-negotiable invariants from the Implementation
Guardrail Profile (Secrets & Config lens):

1. Required secrets are non-defaulted fields on the Settings class.
2. Missing required environment variables cause a loud startup failure
   (pydantic ValidationError) — never a silent default.

They also enforce parity between the keys declared on the Settings class
and the keys shipped in the repo-root .env.example template.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.infra.settings import Settings, validate_settings

# The minimum set of required (non-defaulted) secrets the application
# refuses to start without. Update this set deliberately when changing
# the Settings class — the test exists to catch accidental relaxation
# of required-ness.
REQUIRED_KEYS: frozenset[str] = frozenset(
    {
        "DATABASE_URL",
        "TWILIO_ACCOUNT_SID",
        "TWILIO_AUTH_TOKEN",
        "TWILIO_PHONE_NUMBER",
    }
)


def _clear_required_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Remove every required env var from the test environment."""
    for key in REQUIRED_KEYS:
        monkeypatch.delenv(key, raising=False)


def _set_all_required_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set placeholder values for every required env var."""
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@localhost:5432/test")
    monkeypatch.setenv("TWILIO_ACCOUNT_SID", "ACtest")
    monkeypatch.setenv("TWILIO_AUTH_TOKEN", "test_token")
    monkeypatch.setenv("TWILIO_PHONE_NUMBER", "+15555550100")


def test_required_fields_are_non_defaulted() -> None:
    """
    Every key in REQUIRED_KEYS must be declared on Settings as a field
    with no default value (the pydantic ``PydanticUndefined`` sentinel).
    """
    from pydantic_core import PydanticUndefined

    for key in REQUIRED_KEYS:
        assert key in Settings.model_fields, f"Required key {key!r} is not declared on Settings"
        field = Settings.model_fields[key]
        assert field.default is PydanticUndefined, (
            f"Required key {key!r} must not have a default value"
        )


def test_missing_required_env_raises_validation_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Instantiating Settings with no required env vars set must raise a
    pydantic ValidationError that names every missing required key.
    Passing ``_env_file=None`` disables .env auto-loading so the test is
    hermetic regardless of the developer's local environment.
    """
    _clear_required_env(monkeypatch)

    with pytest.raises(ValidationError) as exc_info:
        Settings(_env_file=None)

    missing_locs = {
        str(err["loc"][0]) for err in exc_info.value.errors() if err.get("type") == "missing"
    }
    assert REQUIRED_KEYS.issubset(missing_locs), (
        f"Expected all required keys to be reported missing; "
        f"got missing={missing_locs}, expected={REQUIRED_KEYS}"
    )


def test_validate_settings_raises_loudly_when_required_missing(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """
    The explicit startup gate ``validate_settings()`` must raise
    ValidationError when required env vars are missing AND must write a
    human-readable error message to stderr that names the missing keys
    and points the operator at .env.example.
    """
    _clear_required_env(monkeypatch)
    # validate_settings() uses the class default env_file (".env"). Run
    # from the tests/ directory so no project .env file is auto-loaded.
    monkeypatch.chdir(Path(__file__).parent)
    with pytest.raises(ValidationError):
        validate_settings()

    captured = capsys.readouterr()
    assert "Configuration error" in captured.err
    assert ".env.example" in captured.err
    for key in REQUIRED_KEYS:
        assert key in captured.err, f"Expected missing key {key!r} to appear in stderr message"


def test_settings_loads_when_required_env_present(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """When all required env vars are set, Settings must instantiate cleanly."""
    _set_all_required_env(monkeypatch)
    s = Settings(_env_file=None)
    assert s.DATABASE_URL.startswith("postgresql://")
    assert s.TWILIO_ACCOUNT_SID == "ACtest"
    assert s.TWILIO_PHONE_NUMBER == "+15555550100"


def _parse_env_example_keys(path: Path) -> set[str]:
    """
    Extract the set of KEY names from a .env-style file. Lines that are
    blank or start with '#' are ignored. Only the substring before '='
    is treated as the key.
    """
    keys: set[str] = set()
    pattern = re.compile(r"^([A-Z][A-Z0-9_]*)\s*=")
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        match = pattern.match(stripped)
        if match:
            keys.add(match.group(1))
    return keys


def test_env_example_parity_with_settings_class() -> None:
    """
    The repo-root .env.example must declare exactly the same set of keys
    as the Settings class. No extras, no missing.
    """
    repo_root = Path(__file__).resolve().parent.parent
    env_example = repo_root / ".env.example"
    assert env_example.is_file(), f".env.example must exist at repo root ({env_example})"

    declared_keys: set[str] = set(Settings.model_fields.keys())
    example_keys: set[str] = _parse_env_example_keys(env_example)

    missing_in_example = declared_keys - example_keys
    extras_in_example = example_keys - declared_keys

    assert not missing_in_example, (
        f"Settings keys missing from .env.example: {sorted(missing_in_example)}"
    )
    assert not extras_in_example, (
        f".env.example has keys not declared on Settings: {sorted(extras_in_example)}"
    )
