#!/usr/bin/env python
"""S179 (T2-C14-R1): 15a.R seal integrity check before any 15a / 29-diag read. Mac only (sealed list and seed are
outside git on Kush's Mac). Read-only on the seal; writes one counts-only JSON (refuses to overwrite) and appends one
line to the private access log beside the sealed list.

    /opt/anaconda3/bin/python tools/s179_seal_integrity_check.py \
        --sealed ~/.culinarystate_private/15aR_sealed_list.json --seed ~/.culinarystate_private/15aR_seed_kush.txt
"""
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.lineage import reserved_seal as rs  # noqa: E402
from culinarystate.lineage import seal_integrity as SI  # noqa: E402

OUT = ROOT / "reports" / "s179" / "seal_integrity_check_S179.json"
LOG_FIELDS = ("accessed_at_utc", "tool", "git_commit", "purpose", "verdict")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sealed", required=True)
    ap.add_argument("--seed", required=True)
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--purpose", default="T2-C14-R1 seal integrity check before 29-diag")
    a = ap.parse_args()
    sealed, seed, out = Path(a.sealed).expanduser(), Path(a.seed).expanduser(), Path(a.out)
    for p in (sealed, seed):
        reason = rs.trackable_reason(p, ROOT)
        if reason:
            sys.exit(f"refusing: {reason}")
    if out.exists():
        sys.exit(f"refusing to overwrite {out}")
    commitment = json.loads((ROOT / rs.COMMITMENT_PATH).read_text(encoding="utf-8"))
    result = SI.check(root=ROOT, commitment=commitment, sealed_bytes=sealed.read_bytes(),
                      seed_text=seed.read_text(encoding="utf-8"))
    head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    result |= {"checked_at_utc": now, "git_commit": head, "commitment_path": rs.COMMITMENT_PATH,
               "sealed_list_location": "NOT_RECORDED (outside git)",
               "dev_filter": "29-diag runner (evaluation/bootstrap_diag.py) refuses without a sealed list that verifies"}
    log = sealed.parent / "15aR_access_log.csv"
    new = not log.exists()
    with log.open("a", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        if new:
            w.writerow(LOG_FIELDS)
        w.writerow((now, "tools/s179_seal_integrity_check.py", head, a.purpose, result["verdict"]))
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("x") as f:
        f.write(json.dumps(result, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"verdict": result["verdict"], "checks": result["checks"]}, indent=1))
    return 0 if result["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
