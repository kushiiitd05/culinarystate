#!/usr/bin/env python
"""Run hardcoded synthetic workflow only: no input-data option and no real pilot draw."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from culinarystate.annotation.pilot_rehearsal import RehearsalError, build_report, write_report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="New SYNTHETIC-*.json outside protected paths; omit for stdout")
    args = parser.parse_args()
    report = build_report()
    if args.output:
        try:
            write_report(args.output, report)
        except RehearsalError as exc:
            parser.error(str(exc))
        print(json.dumps({"status": report["status"], "counts_as_human_gate": False,
                          "output": str(args.output), "all_controls_detected": report["planted_controls"]["all_detected"]}))
    else:
        print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
