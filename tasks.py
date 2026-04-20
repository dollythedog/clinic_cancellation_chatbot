"""
tasks.py
========
Invoke task runner.

Install invoke once:
    pip install invoke

List all available commands:
    inv --list
"""

from __future__ import annotations

from pathlib import Path

from invoke import task

ROOT = Path(__file__).parent


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------


@task
def log(c, message=""):
    """Append a quick note to the activity log.

    Usage:
        inv log -m "Fixed the chart label bug"
        inv log --message "Started Q2 analysis"
    """
    if message:
        c.run(f'python scripts/log_note.py "{message}"', pty=False)
    else:
        c.run("python scripts/log_note.py", pty=False)
