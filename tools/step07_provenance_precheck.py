#!/usr/bin/env python3
"""Step 07 human gate: provenance-validity PRECHECK for the two returned v4 packets (run BEFORE tools/step07_agreement.py; read-only, never edits or fills a label).
  python tools/step07_provenance_precheck.py <Kush_completed.csv> <Parv_completed.csv> [--blank <frozen_packet.csv>] [--min-gap-seconds N]
Checks: header identical to the frozen packet; same audit_ids; every non-judgement column byte-equal to the frozen packet; sha256 + mtime of each file recorded; mtime separation; fraction of identical judgement cells; identical files.
It reports VALID / INVALID_PROVENANCE only. It does not compute agreement and does not change the gate (pooled kappa >= 0.80 AND no critical-field flag, tools/step07_agreement.py)."""
import argparse
import csv
import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JUDGEMENT_COLS = {"duration_judgement", "temperature_value_judgement", "temperature_location_judgement", "pressure_judgement", "power_judgement", "medium_judgement", "basis_judgement",
                  "retention_type_judgement", "censoring_judgement", "overall_judgement", "reason_if_not_correct"}
DEFAULT_BLANK = ROOT / "annotation/condition_audit/condition_audit_packet_100_v4_Kush.csv"
DEFAULT_MIN_GAP_SECONDS = 600  # PROPOSED parameter; recorded in the output, not a gate


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        r = csv.DictReader(f)
        return list(r.fieldnames or []), {row["audit_id"]: row for row in r}


def precheck(blank, a_path, b_path, min_gap=DEFAULT_MIN_GAP_SECONDS):
    problems = []
    hb, B = load(blank)
    ha, A = load(a_path)
    hc, C = load(b_path)
    for name, h in (("A", ha), ("B", hc)):
        if h != hb:
            problems.append(f"{name}: header differs from the frozen packet")
    for name, P in (("A", A), ("B", C)):
        if set(P) != set(B):
            problems.append(f"{name}: audit_id set differs from the frozen packet")
    fixed = [c for c in hb if c not in JUDGEMENT_COLS]
    for name, P in (("A", A), ("B", C)):
        bad = sum(1 for i in set(P) & set(B) for c in fixed if (P[i].get(c) or "") != (B[i].get(c) or ""))
        if bad:
            problems.append(f"{name}: {bad} frozen (non-judgement) cells differ from the frozen packet")
    ids = sorted(set(A) & set(C) & set(B))
    jc = [c for c in hb if c in JUDGEMENT_COLS and c != "reason_if_not_correct"]
    same = sum(1 for i in ids for c in jc if (A[i].get(c) or "").strip() == (C[i].get(c) or "").strip())
    total = len(ids) * len(jc)
    files_identical = sha256(a_path) == sha256(b_path)
    if files_identical:
        problems.append("the two returned files are byte-identical")
    gap = abs(os.path.getmtime(a_path) - os.path.getmtime(b_path))
    if gap < min_gap:
        problems.append(f"mtime separation {gap:.0f}s is below the recorded minimum {min_gap}s")
    return {"status": "INVALID_PROVENANCE" if problems else "VALID", "problems": problems, "n_cases": len(ids), "judgement_cells_compared": total,
            "identical_judgement_cells": same, "identical_judgement_fraction": (same / total) if total else None,
            "sha256": {"blank": sha256(blank), "A": sha256(a_path), "B": sha256(b_path)}, "mtime_gap_seconds": gap, "min_gap_seconds_parameter": min_gap,
            "note": "Process-integrity precheck only. Does not compute agreement and does not alter the gate."}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("kush_completed")
    ap.add_argument("parv_completed")
    ap.add_argument("--blank", default=str(DEFAULT_BLANK))
    ap.add_argument("--min-gap-seconds", type=int, default=DEFAULT_MIN_GAP_SECONDS)
    ap.add_argument("--out", default=str(ROOT / "reports/step07/step07_v4_provenance_precheck.json"))
    args = ap.parse_args(argv)
    res = precheck(args.blank, args.kush_completed, args.parv_completed, args.min_gap_seconds)
    Path(args.out).write_text(json.dumps(res, indent=1))
    print(json.dumps({k: res[k] for k in ("status", "problems", "identical_judgement_fraction", "mtime_gap_seconds")}, indent=1))
    return 0 if res["status"] == "VALID" else 2


if __name__ == "__main__":
    sys.exit(main())
