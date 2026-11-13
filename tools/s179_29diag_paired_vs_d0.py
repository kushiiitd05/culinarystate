#!/usr/bin/env python
"""T6-C02-R3: every 29-diag rung vs D0 per family per split (paired cluster bootstrap), under the 15a.R seal.
Mac only (sealed list outside git). Runs twice and requires byte-identical output (G15-R), refuses to overwrite.
PRIOR_EXPOSURE_REANALYSIS: these splits were read in RUN-S179-DIAG29-001.

    /opt/anaconda3/bin/python tools/s179_29diag_paired_vs_d0.py --sealed ~/.culinarystate_private/15aR_sealed_list.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))
from culinarystate.evaluation import bootstrap_diag as BD  # noqa: E402
from culinarystate.evaluation import diag29_paired_vs_d0 as P  # noqa: E402
import run_29diag as base  # noqa: E402  (same snapshot, families, ledger loader)

OUT = ROOT / "reports" / "step29" / "diag" / "paired_vs_d0_S179_2026-11-13.json"


def once(sealed: Path) -> bytes:
    evd = list(base._latest(ROOT / "ledgers/data/EVD.jsonl").values())
    cond = base._latest(ROOT / "ledgers/data/COND.jsonl")
    res = BD.run_bootstrap_diag(base.SNAPSHOT, lambda ctx: P.run(ctx, evd, cond=cond, families=base.FAMILIES),
                                root=ROOT, sealed_list_path=sealed)
    res = {**res, "item": "T6-C02-R3", "approver": "ksh+prv (AI, D-085)"}
    return (json.dumps(res, indent=1, sort_keys=True, default=str) + "\n").encode("utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sealed", required=True)
    a = ap.parse_args()
    if OUT.exists():
        sys.exit(f"refusing to overwrite {OUT}")
    s = Path(a.sealed).expanduser()
    b1, b2 = once(s), once(s)
    h1, h2 = hashlib.sha256(b1).hexdigest(), hashlib.sha256(b2).hexdigest()
    if h1 != h2:
        sys.exit(f"G15-R FAIL: runs differ {h1} {h2}")
    OUT.write_bytes(b1)
    print("G15-R PASS (two runs byte-identical)", h1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
