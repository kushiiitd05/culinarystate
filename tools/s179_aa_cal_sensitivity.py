#!/usr/bin/env python3
"""Write a new diagnostic Model B/CAL sensitivity artifact, never the frozen fit.

Source quotes remain in ignored CAL metadata; only IDs, hashes, counts and
numerical diagnostic summaries are emitted. SIM-VAL is never read.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.simulation import aa_pilot_fit as F  # noqa: E402
from culinarystate.simulation.aa_cal_sensitivity import sensitivity_report  # noqa: E402

FIT = ROOT / "reports/step10/aa_pilot_model_a_fit_D085.json"
FIT_SHA = "b9247db03e98423f8866fa50b24e2ecd33831d907f3aace00b1f7e4f2ea9543f"
DELEGATE = "ksh+prv (AI, D-085)"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cal", required=True, type=Path)
    ap.add_argument("--metadata", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args(argv)
    if args.out.exists():
        raise SystemExit("refusing to overwrite a diagnostic output")
    started = utc_now()
    if sha(FIT) != FIT_SHA:
        raise ValueError("original frozen Model A hash changed")
    fit_doc = json.loads(FIT.read_text())
    if sha(args.cal) != fit_doc["returned_sha256"][DELEGATE]:
        raise ValueError("CAL sheet differs from the one bound by the frozen fit")
    for path, expected in fit_doc["code_sha256"].items():
        if sha(ROOT / path) != expected:
            raise ValueError("frozen code changed")
    with args.cal.open(newline="", encoding="utf-8-sig") as fh:
        cal = list(csv.DictReader(fh))
    if any(r.get("verified_by") != DELEGATE or r.get("partition") != "SIM-CAL" for r in cal):
        raise ValueError("expected the original D-085 SIM-CAL sheet")
    metadata = json.loads(args.metadata.read_text())["papers"]
    with (ROOT / "registry/evidence/aa_licence_checks_D085_v1.csv").open(newline="") as fh:
        confirmed = {r["candidate_id"] for r in csv.DictReader(fh)
                     if r["status"] == "CONFIRMED_ON_PUBLISHER_PAGE" and r["partition"] == "SIM-CAL"}
    # Preserve the frozen verdict rule. The one delegate sheet supplies both inputs;
    # it supplies no independent human agreement.
    agreed, excluded_verdict = F.agreed_rows(cal, cal)
    accepted_papers = {r["candidate_id"] for r in agreed}
    if not accepted_papers <= confirmed or not accepted_papers <= metadata.keys():
        raise ValueError("an admissible paper lacks a confirmed licence or metadata")
    for paper in accepted_papers:
        m = metadata[paper]
        pdf, text = ROOT / m["pdf_path"], ROOT / m["text_path"]
        if not pdf.resolve().is_relative_to(ROOT / "data/raw/aa_pilot"):
            raise ValueError("metadata PDF outside CAL source directory")
        if not text.resolve().is_relative_to(ROOT / "data/raw/aa_pilot"):
            raise ValueError("metadata text outside CAL source directory")
        if sha(pdf) != m["pdf_sha256"] or sha(text) != m["text_sha256"]:
            raise ValueError("CAL source hash mismatch")
        norm = " ".join(text.read_text().split())
        for proof in m["proofs"].values():
            if not proof.get("locator") or " ".join(proof["quote"].split()) not in norm:
                raise ValueError("CAL metadata proof not found in source")
        for row in (r for r in cal if r["candidate_id"] == paper and r["verdict"] == "VERIFIED"):
            if row["pdf_sha256"] != m["pdf_sha256"] or " ".join(row["span_quote"].split()) not in norm:
                raise ValueError("CAL row provenance mismatch")
            if row["row_type"] == "K_AT_T" and not row["unit"].startswith("1/min"):
                raise ValueError("rate units are not the preregistered minute basis")
    admissible = [r for r in agreed if r["row_type"] == "K_AT_T" and r["order"].lower().startswith("first")]
    rejected = sorted({r["candidate_id"] for r in cal if r["verdict"] == "REJECTED"})
    report = sensitivity_report(admissible, metadata, rejected_papers=rejected)
    if sorted(r["row_id"] for r in admissible if 60 <= r["T"] <= 100) != fit_doc["fit"]["row_ids"]:
        raise ValueError("primary inclusion IDs differ from the frozen fit")
    report.update(frozen_primary_sha256=FIT_SHA, frozen_CAL_sheet_sha256=sha(args.cal),
                  metadata_precheck_sha256=sha(args.metadata), excluded_by_verdict=excluded_verdict,
                  input_rows=len(cal), verification="AI_PRECHECKED_NOT_HUMAN",
                  sim_val_read=False, model_a_refitted=False,
                  paper_metadata={p: {k: v for k, v in m.items() if k not in ("proofs", "text_path")}
                                  for p, m in sorted(metadata.items())},
                  code_sha256={p: sha(ROOT / p) for p in
                               ("tools/s179_aa_cal_sensitivity.py",
                                "src/culinarystate/simulation/aa_cal_sensitivity.py")},
                  run_started_at_utc=started, run_completed_at_utc=utc_now(),
                  limitations=["Separate sensitivity only; original primary Model A retained.",
                               "Assay specificity is the predeclared AI interpretation, not assay validation.",
                               "Source pH dispersion is not converted to a CI or gate range.",
                               "No post-lock domain registry is supplied; no PARAM or SIMULATE gate opens.",
                               "Rejected 09/11 are excluded even from the requested all-rows arm."])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x", encoding="utf-8") as fh:
        fh.write(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print("CAL sensitivity diagnostic written; frozen Model A unchanged; no SIM-VAL access.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
