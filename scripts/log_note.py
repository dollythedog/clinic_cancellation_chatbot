"""
log_note.py
===========
Quick-entry script to append a timestamped note to the activity log.

Usage::

    python scripts/log_note.py "Fixed the chart label bug"
    python scripts/log_note.py "Started Q2 dataset analysis"
    python scripts/log_note.py   # interactive prompt if no argument given

    inv log -m "Fixed the chart label bug"   # via invoke task runner

All entries go to ``logs/activity.log`` in the project root.
"""

import sys
from datetime import datetime
from pathlib import Path

LOG_FILE = Path(__file__).resolve().parent.parent / "logs" / "activity.log"


def main() -> None:
    if len(sys.argv) > 1:
        note = " ".join(sys.argv[1:])
    else:
        note = input("Note: ").strip()
        if not note:
            print("Empty note — nothing logged.")
            return

    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{timestamp} | INFO     | [note] message={note}\n"

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line)

    print(f"OK  Logged: {note}")


if __name__ == "__main__":
    main()
