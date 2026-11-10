#!/usr/bin/env python
"""Run 29-diag (D-082 prereg; D-085 delegated lock) twice on the Mac and require byte-identical output (G15-R).

    python tools/run_29diag.py --sealed ~/.culinarystate_private/15aR_sealed_list.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.evaluation import bootstrap_diag as BD  # noqa: E402
from culinarystate.evaluation import diag29_runner as R  # noqa: E402

SNAPSHOT = "15A-BOOT-2026-11-08"
FAMILIES = ("USDA-RETN-R6", "BOGNAR-2002", "PHENOL-EXPLORER-3.6")
OUT = ROOT / "reports" / "step29" / "diag" / "diag_results_S179.json"


def _latest(path: Path) -> dict:
    out = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            out[r["id"]] = r
    return out


def once(sealed: Path) -> bytes:
    evd = list(_latest(ROOT / "ledgers/data/EVD.jsonl").values())
    cond = _latest(ROOT / "ledgers/data/COND.jsonl")
    res = BD.run_bootstrap_diag(SNAPSHOT, lambda ctx: R.run(ctx, evd, cond=cond, families=FAMILIES),
                                root=ROOT, sealed_list_path=sealed)
    return (json.dumps(res, indent=1, sort_keys=True, default=str) + "\n").encode("utf-8")


if __name__ == "__main__":
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
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(b1)
    print("G15-R PASS (two runs byte-identical)", h1)
