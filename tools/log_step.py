#!/usr/bin/env python3
"""Append a timestamped, sequentially numbered step to WORKLOG.md.

Usage:
  python tools/log_step.py --who Kush+Claude --block B00 --title "Repo scaffold" \
      --did "..." --files "a.py,b.md" --verify "pytest: 12 passed" --next "..."

Step IDs are S001, S002, ... and are never reused. The log is append-only.
"""
from __future__ import annotations

import argparse
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
WORKLOG = ROOT / "WORKLOG.md"
HEADER = (
    "# WORKLOG — CulinaryState (Group 17: Kush + Parv)\n\n"
    "Append-only, sequential, timestamped (IST). One entry per step. "
    "Written by `tools/log_step.py`; never edit past entries — add a correcting step instead.\n\n"
    "Presentation: **25–26 Nov 2026**.\n\n"
)
STEP_RE = re.compile(r"^### (S\d{3,})", re.MULTILINE)


def next_step_id(text: str) -> str:
    ids = [int(m.group(1)[1:]) for m in STEP_RE.finditer(text)]
    return f"S{(max(ids) + 1 if ids else 1):03d}"


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--who", default="Kush+Claude")
    p.add_argument("--block", required=True, help="e.g. B00, B06, DEL-1")
    p.add_argument("--title", required=True)
    p.add_argument("--did", required=True)
    p.add_argument("--files", default="")
    p.add_argument("--verify", default="")
    p.add_argument("--next", default="")
    a = p.parse_args()

    text = WORKLOG.read_text() if WORKLOG.exists() else HEADER
    sid = next_step_id(text)
    ts = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M IST")
    entry = [f"### {sid} · {ts} · {a.block} · {a.title}", f"- **Who:** {a.who}", f"- **Did:** {a.did}"]
    if a.files:
        entry.append("- **Files:** " + ", ".join(f"`{f.strip()}`" for f in a.files.split(",") if f.strip()))
    if a.verify:
        entry.append(f"- **Verified:** {a.verify}")
    if a.next:
        entry.append(f"- **Next:** {a.next}")
    WORKLOG.write_text(text.rstrip("\n") + "\n\n" + "\n".join(entry) + "\n")
    print(sid, ts)


if __name__ == "__main__":
    main()
