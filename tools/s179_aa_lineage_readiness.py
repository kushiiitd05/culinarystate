#!/usr/bin/env python3
"""Prepare source-bound AA staging candidates without minting incomplete ledger rows."""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.simulation.aa_lineage_readiness import build_readiness  # noqa: E402

CAL = ROOT / "annotation/aa_pilot/aa_pilot_verify_CAL_v1_D085.csv"
VAL = ROOT / "annotation/aa_pilot/aa_pilot_SIMVAL_extraction_2026-11-11.csv"
PRE = ROOT / "annotation/aa_pilot/aa_pilot_SIMVAL_source_precheck_2026-11-11.csv"
MANIFEST = ROOT / "data/raw/aa_pilot_simval_quarantine/aa_pilot_SIMVAL_extraction_2026-11-11.manifest.json"
FIT = ROOT / "reports/step10/aa_pilot_model_a_fit_D085.json"
LICENCE = ROOT / "registry/evidence/aa_licence_checks_D085_v1.csv"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def csv_rows(path):
    with Path(path).open(newline="") as handle:
        return list(csv.DictReader(handle))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--private-out", type=Path, required=True)
    args = parser.parse_args(argv)
    for output in [args.out, args.private_out]:
        if output.exists():
            parser.error("refusing to overwrite a prior artifact")
    private = args.private_out.resolve()
    if not private.is_relative_to(ROOT / "annotation/aa_pilot") or subprocess.run(
            ["git", "check-ignore", "-q", "--", str(private)], cwd=ROOT).returncode != 0:
        parser.error("private source staging must be inside ignored annotation/aa_pilot")
    started = datetime.now(timezone.utc).isoformat()
    cal, val, pre = csv_rows(CAL), csv_rows(VAL), csv_rows(PRE)
    frozen = json.loads(FIT.read_text())
    manifest = json.loads(MANIFEST.read_text())
    if sha(CAL) != frozen["returned_sha256"]["ksh+prv (AI, D-085)"]:
        parser.error("CAL return differs from frozen Model A")
    if sha(VAL) != manifest["extraction_sha256"]:
        parser.error("final SIM-VAL extraction hash mismatch")
    if sha(PRE) != "c5565cac24bc6a583ae08f3dcfc87a4f88df014f1df1d37da733228ec6381aa8":
        parser.error("source precheck differs from published reviewed artifact")
    licences = {r["candidate_id"]: r["status"] for r in csv_rows(LICENCE)}
    ledger_paths = {family: ROOT / "ledgers/data" / (family + ".jsonl")
                    for family in ["SRC", "DOC", "STUDY", "SEXP", "OBS", "KIN", "KINPT", "PARAM", "FORM"]}
    ledgers = {}
    for family, path in ledger_paths.items():
        latest = {}
        if path.exists():
            for line in path.read_text().splitlines():
                if line.strip():
                    row = json.loads(line)
                    latest[row["id"]] = row
        ledgers[family] = list(latest.values())
    pdf_paths = {}
    for row in cal:
        pdf_paths[row["candidate_id"]] = ROOT / "data/raw/aa_pilot" / (row["candidate_id"] + ".pdf")
    for row in val:
        pdf_paths[row["candidate_id"]] = ROOT / "data/raw/aa_pilot_simval_quarantine" / (row["candidate_id"] + ".pdf")
    pdf_hashes = {candidate: sha(path) for candidate, path in pdf_paths.items()}
    report, staging = build_readiness(cal, val, pre, ledgers, licences, pdf_hashes)
    args.private_out.parent.mkdir(parents=True, exist_ok=True)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.private_out.open("x") as handle:
        json.dump({"record": "PRIVATE_AA_SOURCE_STAGING", "labels": report["labels"], "candidates": staging}, handle,
                  indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")
    inputs = [CAL, VAL, PRE, MANIFEST, FIT, LICENCE] + list(pdf_paths.values())
    inputs += [path for path in ledger_paths.values() if path.exists()]
    input_hashes = {str(path.relative_to(ROOT)): sha(path) for path in inputs}
    code = [Path(__file__).resolve(), ROOT / "src/culinarystate/simulation/aa_lineage_readiness.py"]
    report.update(started_at_utc=started, completed_at_utc=datetime.now(timezone.utc).isoformat(),
                  base_commit=subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                  input_sha256=input_hashes, code_sha256={str(path.relative_to(ROOT)): sha(path) for path in code},
                  private_staging_path=str(private.relative_to(ROOT)), private_staging_sha256=sha(private),
                  latest_ledger_record_counts={family: len(rows) for family, rows in ledgers.items()},
                  frozen_model_a_sha256=sha(FIT), frozen_fit_row_ids=frozen["fit"]["row_ids"],
                  source_pdf_text_opened_by_tool=False, source_pdf_binary_hashes_only=True)
    if input_hashes != {path: sha(ROOT / path) for path in input_hashes}:
        raise RuntimeError("source/ledger input changed during staging")
    with args.out.open("x") as handle:
        json.dump(report, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")
    print(json.dumps({"rows": report["n_rows"], "eligible": report["production_eligible_rows"],
                      "ph_context_staging_corrections": report["ph_context_staging_corrections"],
                      "minted_ids": report["minted_ids"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
