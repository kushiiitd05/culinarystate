#!/usr/bin/env python
"""Step 12-local (S157): stage USDA R2 yields and the 11 remaining Bognar tables; diff against EVD.

Status: PROVISIONAL_PENDING_G12_AUDIT. Parses the local files, writes the parsed rows (raw
third-party text) to a git-ignored staging directory, computes a read-only diff against the latest
ACTIVE EVD versions (overlap = G08-9 context, reported and never resolved or merged) and writes ONE
counts/hashes-only JSON report, the only output meant for git. No ledger is written; the 08a ledger
baseline is checked before and after when the repository root is used.

Run locally where the data bundle is present:
    pdftotext -layout data/raw/bognar/bognar_2002.pdf data/raw/bognar/bognar_2002.txt   # if the .txt is absent
    python tools/step12_local_stage.py --defaults
    python tools/step12_local_stage.py --r2-csv <csv> --bognar-txt <txt> \
        --staging-dir data/interim/<dir> --report <json>
Defaults: R2 data/external/usda_yields/cooking_yields_meat_poultry_r2.csv, Bognar text
data/raw/bognar/bognar_2002.txt, staging data/interim/step12_local_staging_v1, report
reports/step12/step12_local_counts_v1.json (both refuse overwrite).
Exit 0 written, 2 refused / missing input / unreadable layout, 3 ledger baseline mismatch.
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from culinarystate.evidence import step12_local as S  # noqa: E402
from culinarystate.ingest import bognar_remaining as B  # noqa: E402
from culinarystate.ingest import usda_yields_r2 as Y  # noqa: E402
from culinarystate.lineage.guard import LedgerBaselineMismatch, verify_baseline  # noqa: E402

BASELINE = "registry/baseline_ledger_hashes_08a_v1.csv"
DEFAULT_R2 = "data/external/usda_yields/cooking_yields_meat_poultry_r2.csv"
DEFAULT_BOGNAR_TXT = "data/raw/bognar/bognar_2002.txt"
DEFAULT_REPORT = "reports/step12/step12_local_counts_v1.json"


def _fact(path: Path, root: Path) -> dict:
    h, n = hashlib.sha256(), 0
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
            n += len(block)
    try:
        loc = path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        loc = "OUTSIDE_REPO_ROOT"
    return {"locator": loc, "sha256": h.hexdigest(), "bytes": n}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--defaults", action="store_true", help="use the default R2 CSV and Bognar text paths")
    ap.add_argument("--r2-csv", type=Path, default=None)
    ap.add_argument("--bognar-txt", type=Path, default=None)
    ap.add_argument("--evd", type=Path, default=None)
    ap.add_argument("--staging-dir", type=Path, default=None)
    ap.add_argument("--report", type=Path, default=None)
    a = ap.parse_args(argv)
    root = a.root.resolve()
    r2_path = a.r2_csv or (root / DEFAULT_R2 if a.defaults else None)
    bog_path = a.bognar_txt or (root / DEFAULT_BOGNAR_TXT if a.defaults else None)
    evd = a.evd or root / "ledgers/data/EVD.jsonl"
    stage = a.staging_dir or root / S.DEFAULT_STAGING_DIR
    report = a.report or root / DEFAULT_REPORT
    if r2_path is None and bog_path is None:
        print("give --r2-csv and/or --bognar-txt (or --defaults)", file=sys.stderr)
        return 2
    missing = [str(p) for p in (r2_path, bog_path, evd) if p is not None and not p.is_file()]
    if missing:
        print(f"missing input file(s): {missing}", file=sys.stderr)
        return 2
    check_baseline = root == ROOT.resolve()
    try:
        if check_baseline:
            verify_baseline(root / BASELINE, root)
        S.guard_staging_dir(stage, root=root)
        r2 = Y.parse_r2_file(r2_path) if r2_path else None
        bog = B.parse_remaining_file(bog_path) if bog_path else None
        inputs = {"evd": _fact(evd, root)}
        if r2_path:
            inputs["r2_csv"] = _fact(r2_path, root)
        if bog_path:
            inputs["bognar_txt"] = _fact(bog_path, root)
        rep = S.counts_report(r2=r2, bognar=bog, diff=S.diff_against_evd(evd, r2=r2, bognar=bog), inputs=inputs)
        S.guard_report_path(report, root)
        S.write_staging(stage, r2=r2, bognar=bog, root=root)
        out = S.write_report(rep, report, root=root)
        if check_baseline:
            verify_baseline(root / BASELINE, root)
    except (S.StagingError, Y.R2ParseError, B.BognarParseError, UnicodeDecodeError) as e:
        print(f"refused: {e}", file=sys.stderr)
        return 2
    except LedgerBaselineMismatch as e:
        print(f"ledger baseline mismatch: {e}", file=sys.stderr)
        return 3
    print(f"staged in {stage}; counts report {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
