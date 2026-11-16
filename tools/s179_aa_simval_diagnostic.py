#!/usr/bin/env python3
"""Post-extraction, frozen-model rate comparison; no fit, retention validation or routing.

Assay/basis eligibility remains unresolved. All computed comparisons are a separately
flagged diagnostic, not the preregistered same-basis comparison. Per-row source and
prediction values remain in a git-ignored private file; public output is aggregate only.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import subprocess
import sys
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.simulation.aa_pilot_fit import predict_ln_k  # noqa: E402

LABELS = ["DIAGNOSTIC", "NON_CITABLE", "AI_PRECHECKED", "NO_HUMAN_SIGNOFF_D085",
          "BASIS_UNRESOLVED_NOT_PRIMARY_COMPARISON"]


def validate_source_binding(rows, checked):
    a = {r["row_id"]: r for r in rows}
    b = {r["row_id"]: r for r in checked}
    if len(a) != len(rows) or len(b) != len(checked) or a.keys() != b.keys():
        raise ValueError("source precheck IDs differ or contain duplicates")
    for rid in a:
        for field in ("candidate_id", "row_kind", "pdf_sha256", "source_locator"):
            if not a[rid].get(field) or a[rid][field] != b[rid].get(field):
                raise ValueError(f"source precheck provenance mismatch: {rid} / {field}")


def compare_rows(rows, fit, *, source_precheck):
    ids = [r["row_id"] for r in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate extraction row IDs")
    if any(r["row_kind"] in {"RAW_POINT", "TIME_RETENTION_POINT"} for r in rows):
        raise ValueError("raw retention-point evaluation is outside this rate-only tool")
    private, excluded = [], Counter()
    for row in rows:
        reason = None
        if row["row_kind"] != "K_AT_T":
            reason = "NOT_PER_TEMPERATURE_RATE"
        elif row["candidate_id"] in fit["papers"] or row["partition"] != "SIM-VAL":
            reason = "NOT_PAPER_HELD_OUT"
        elif row["licence_status"] != "CONFIRMED_ON_PUBLISHER_PAGE_D085":
            reason = "LICENCE_UNCONFIRMED"
        elif row["reaction_order"] != "1":
            reason = "NOT_FIRST_ORDER"
        elif source_precheck.get(row["row_id"], {}).get("status") != "PASS" \
                or source_precheck.get(row["row_id"], {}).get("computational_eligibility") \
                != "ELIGIBLE_FOR_RATE_DIAGNOSTIC":
            reason = "SOURCE_PRECHECK_NOT_ELIGIBLE"
        else:
            try:
                temp = float(row["temperature_C"])
                raw, observed = Decimal(row["k_raw"]), Decimal(row["k_normalized_min_1"])
                factor = {"10^-4 min^-1": Decimal("0.0001"), "min^-1": Decimal(1)}.get(row["k_raw_unit"])
                if not math.isfinite(temp) or not 60 <= temp <= 100:
                    reason = "TEMPERATURE_OUTSIDE_MODEL_SCOPE"
                elif factor is None or not raw.is_finite() or not observed.is_finite() \
                        or raw <= 0 or observed <= 0 or raw * factor != observed:
                    reason = "INVALID_RATE_OR_UNIT_SCALING"
            except (KeyError, ValueError, InvalidOperation):
                reason = "INVALID_RATE_OR_TEMPERATURE"
        if reason:
            excluded[reason] += 1
            continue
        mid, lo, hi = predict_ln_k(fit, temp)
        actual = math.log(float(observed))
        error = mid - actual
        if not all(math.isfinite(v) for v in (mid, lo, hi, actual, error)):
            raise ValueError("nonfinite frozen-model prediction")
        private.append({"row_id": row["row_id"], "candidate_id": row["candidate_id"],
                        "temperature_C": temp, "observed_k_min_1": float(observed),
                        "predicted_ln_k": mid, "predicted_ln_k_lo95": lo, "predicted_ln_k_hi95": hi,
                        "predicted_minus_observed_ln_k": error, "inside_model_interval": lo <= actual <= hi,
                        "basis_status": "UNRESOLVED_SOURCE_BASIS", "labels": " / ".join(LABELS)})
    errors = [r["predicted_minus_observed_ln_k"] for r in private]
    n = len(errors)
    report = {"record": "AA_SIMVAL_RATE_DIAGNOSTIC", "labels": LABELS,
              "validation_status": "NOT_VALIDATED / RESEARCH_ONLY", "production_route_allowed": False,
              "primary_comparable_rows": 0, "primary_status": "NOT_RUN_BASIS_REVIEW_REQUIRED",
              "retention_observations": 0, "retention_error": None,
              "excluded": dict(sorted(excluded.items())),
              "rate_diagnostic": {"n_rows": n, "n_papers": len({r["candidate_id"] for r in private}),
                                  "mean_abs_ln_k_error": sum(map(abs, errors)) / n if n else None,
                                  "mean_signed_ln_k_error": sum(errors) / n if n else None,
                                  "inside_model_interval": sum(r["inside_model_interval"] for r in private)},
              "limitations": ["Source assay/basis comparability unresolved; no primary same-basis result.",
                              "No exact time/retention observations; no retention-error result.",
                              "No threshold, tuning, parameter update, human verification or validation gate.",
                              "Model intervals are frozen Gaussian approximations; not calibrated coverage.",
                              "No PARAM/VAL integration; this is an offline rate diagnostic only."]}
    return private, report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fit", type=Path, required=True)
    parser.add_argument("--extraction", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--source-precheck", type=Path, required=True)
    parser.add_argument("--private-out", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    for path in (args.private_out, args.out):
        if path.exists():
            parser.error("refusing existing output")
    destination = args.private_out.resolve()
    if not destination.is_relative_to((ROOT / "annotation/aa_pilot").resolve()) \
            or subprocess.run(["git", "-C", str(ROOT), "check-ignore", "-q", "--", str(destination)]).returncode:
        parser.error("per-row output must remain in git-ignored annotation/aa_pilot")
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    manifest = json.loads(args.manifest.read_text())
    if not manifest.get("status", "").startswith("FINAL_EXTRACTION") \
            or not manifest.get("extraction_completed_utc") \
            or manifest["extraction_sha256"] != sha(args.extraction) \
            or manifest["frozen_model_a_fit_sha256_received_before_extraction"] != sha(args.fit):
        parser.error("final extraction / frozen-fit manifest mismatch")
    doc = json.loads(args.fit.read_text())
    for path, expected in doc["code_sha256"].items():
        if sha(ROOT / path) != expected:
            parser.error("frozen fit code changed")
    with args.extraction.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    with args.source_precheck.open(newline="") as handle:
        checked = list(csv.DictReader(handle))
    try:
        validate_source_binding(rows, checked)
    except ValueError as exc:
        parser.error(str(exc))
    private, report = compare_rows(rows, doc["fit"], source_precheck={r["row_id"]: r for r in checked})
    report["input_sha256"] = {str(p): sha(p) for p in (args.fit, args.extraction, args.manifest, args.source_precheck)}
    report["tool_sha256"] = sha(Path(__file__))
    with args.private_out.open("x", newline="") as handle:
        if private:
            writer = csv.DictWriter(handle, fieldnames=list(private[0]))
            writer.writeheader()
            writer.writerows(private)
    report["private_output_sha256"] = sha(args.private_out)
    with args.out.open("x") as handle:
        handle.write(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n")
    print("Offline rate diagnostic written; primary comparison NOT_RUN; no route or validation gate opens.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
