#!/usr/bin/env python
"""Append one row to registry/compute_runs_v1.csv (D-077 tracking). Hashes the output file; never edits old rows.

    python tools/log_compute_run.py --run-id RUN-S172-001 --host mac --tree ~/Desktop/CGAS/culinarystate \
        --commit 1a2b3c4 --command "python tools/binding_census.py ..." --output reports/step26/x.json \
        --start 2026-11-08T03:10 --end 2026-11-08T03:11 --status DONE --notes "..."
"""
import argparse
import csv
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "registry/compute_runs_v1.csv"
COLS = ["run_id", "host", "tree", "git_commit", "families", "workers", "command", "output_path", "output_sha256",
        "start", "end", "status", "notes"]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    for c in COLS:
        if c != "output_sha256":
            ap.add_argument("--" + c.replace("_", "-").replace("output-path", "output").replace("git-commit", "commit"),
                            dest=c, default="")
    a = ap.parse_args(argv)
    rows = list(csv.DictReader(open(REG, newline=""))) if REG.exists() else []
    if any(r["run_id"] == a.run_id for r in rows):
        sys.exit(f"run id {a.run_id} already logged")
    out = ROOT / a.output_path if a.output_path and not Path(a.output_path).is_absolute() else Path(a.output_path or ".")
    sha = hashlib.sha256(out.read_bytes()).hexdigest() if a.output_path and out.is_file() else ""
    new = not REG.exists()
    with open(REG, "a", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS)
        if new:
            w.writeheader()
        w.writerow({**{c: getattr(a, c) for c in COLS if c != "output_sha256"}, "output_sha256": sha})
    print(a.run_id, sha[:16])
    return 0


if __name__ == "__main__":
    sys.exit(main())
