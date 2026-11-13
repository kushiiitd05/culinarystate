#!/usr/bin/env python
"""T9-C09-R1: re-derive the historical 15a.R reserved assignment on Kush's Mac and write a counts-only
split registry. Seed and sealed list stay outside git; outputs carry hashes and counts only and refuse
to overwrite. Refuses unless the seal integrity check passes on the same inputs.

    /opt/anaconda3/bin/python tools/s179_15a_assignment_registry.py \
        --sealed ~/.culinarystate_private/15aR_sealed_list.json --seed ~/.culinarystate_private/15aR_seed_kush.txt
"""
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.lineage import assignment_registry as AR  # noqa: E402
from culinarystate.lineage import reserved_seal as rs  # noqa: E402
from culinarystate.lineage import seal_integrity as SI  # noqa: E402

OUT_CSV = ROOT / "registry" / "split_registry_15a_v1.csv"
OUT_JSON = ROOT / "reports" / "s179" / "15a_assignment_registry_2026-11-13.json"
LABELS = ["AI_PRECHECKED", "NON_CITABLE", "NO_HUMAN_SIGNOFF_D085"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sealed", required=True)
    ap.add_argument("--seed", required=True)
    a = ap.parse_args()
    sealed, seed_path = Path(a.sealed).expanduser(), Path(a.seed).expanduser()
    for p in (sealed, seed_path):
        reason = rs.trackable_reason(p, ROOT)
        if reason:
            sys.exit(f"refusing: {reason}")
    for out in (OUT_CSV, OUT_JSON):
        if out.exists():
            sys.exit(f"refusing to overwrite {out}")
    commitment = json.loads((ROOT / rs.COMMITMENT_PATH).read_text(encoding="utf-8"))
    sealed_bytes, seed_text = sealed.read_bytes(), seed_path.read_text(encoding="utf-8")
    integrity = SI.check(root=ROOT, commitment=commitment, sealed_bytes=sealed_bytes, seed_text=seed_text)
    if integrity["verdict"] != "PASS":
        sys.exit(f"refusing: seal integrity {integrity['checks']}")
    seed = seed_text[:-1] if seed_text.endswith("\n") else seed_text
    evd = ROOT / commitment["snapshot"]["evd_path"]
    groups = rs.build_groups(rs.latest_active(rs.read_jsonl(evd)), str(commitment["unit"]))
    reserved = rs.select_reserved(groups, snapshot_sha256=rs.sha256_file(evd), seed=seed,
                                  fraction=Fraction(str(commitment["fraction"])), stratify=str(commitment["stratify"]))
    summary = AR.partition_summary(groups, reserved=reserved)
    for k in ("n_groups", "n_reserved_rows"):
        want = commitment[k if k != "n_reserved_rows" else "n_reserved_rows"]
        if summary[k] != want:
            sys.exit(f"refusing: {k} {summary[k]} != commitment {want}")
    if summary["n_reserved_groups"] != commitment["n_reserved"]:
        sys.exit("refusing: reserved count differs from commitment")
    code = Path(__file__).relative_to(ROOT).as_posix()
    rows = AR.registry_rows(summary, commitment=commitment, source_artifact=rs.COMMITMENT_PATH,
                            source_sha256=rs.sha256_file(ROOT / rs.COMMITMENT_PATH), code_artifact=code,
                            code_sha256=rs.sha256_file(Path(__file__)))
    head = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    with OUT_CSV.open("x", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=AR.REGISTRY_FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    record = {"record": "SPLIT_ASSIGNMENT_REGISTRY_15A_R", "item": "T9-C09-R1", "labels": LABELS,
              "approver": "ksh+prv (AI, D-085)", "git_commit": head,
              "checked_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
              "seal_integrity": integrity["checks"], "summary": summary,
              "registry_csv": OUT_CSV.relative_to(ROOT).as_posix(), "registry_csv_sha256": rs.sha256_file(OUT_CSV),
              "limitations": ["Counts and hashes only; group ids and seed stay in ~/.culinarystate_private.",
                              "0 groups crossing is by construction (DEV = complement); it is not source independence.",
                              "Cross-source matrix/process keys in both splits are disclosed, not resolved.",
                              "AI re-derivation; no human verification implied."],
              "scientific_gate_pass": False}
    with OUT_JSON.open("x", encoding="utf-8") as f:
        f.write(json.dumps(record, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: summary[k] for k in summary if k != "strata"}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
