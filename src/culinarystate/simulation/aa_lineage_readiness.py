"""Read-only AA staging preparation; never grants calibration or routing permission.

Candidate rows remain source reports. Author rate summaries are not reconstructed
raw trajectories, and an empty provenance link is never filled with an invented ID.
"""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
import re

LABELS = ["AI_PRECHECKED", "NON_CITABLE", "NO_HUMAN_SIGNOFF_D085"]
SOURCE_FAMILIES = ("SRC", "DOC", "STUDY")


def normalise_doi(value):
    if not isinstance(value, str):
        return None
    value = value.strip().lower()
    for prefix in ("https://doi.org/", "http://doi.org/", "https://dx.doi.org/", "doi:"):
        if value.startswith(prefix):
            value = value[len(prefix):].strip()
            break
    return value if re.fullmatch(r"10\.\d{4,9}/\S+", value) else None


def _strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from _strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from _strings(child)


def _refs(doi, ledgers):
    return {family: sorted(r["id"] for r in ledgers.get(family, [])
                           if r.get("status") == "ACTIVE" and
                           doi in {normalise_doi(s) for s in _strings(r)})
            for family in SOURCE_FAMILIES}


def build_readiness(cal_rows, val_rows, prechecks, ledgers, licences, pdf_hashes):
    """Bind every source row and preserve exclusions; return public and private views.

    The private staging view preserves every original row verbatim as field values.
    Only a precheck-identified isothermal pH context error gets a separate corrected
    metadata field. No rate, aggregate, assay or original source value is changed.
    """
    inputs = [(r, "SIM-CAL") for r in cal_rows] + [(r, "SIM-VAL") for r in val_rows]
    ids = [r.get("row_id") for r, _ in inputs]
    if any(not isinstance(rid, str) or not rid for rid in ids) or len(set(ids)) != len(ids):
        raise ValueError("nonempty unique row IDs required")
    checks = {}
    for check in prechecks:
        rid = check.get("row_id")
        if not rid or rid in checks:
            raise ValueError("unique source-precheck row IDs required")
        checks[rid] = check
    public, private = [], []
    corrected = 0
    for original, partition in inputs:
        row = deepcopy(original)
        rid, candidate = row["row_id"], row.get("candidate_id")
        doi = normalise_doi(row.get("doi"))
        if row.get("partition") != partition or doi is None:
            raise ValueError("partition and DOI binding required")
        digest = row.get("pdf_sha256")
        if not re.fullmatch(r"[a-f0-9]{64}", str(digest)) or pdf_hashes.get(candidate) != digest:
            raise ValueError("source PDF hash mismatch")
        kind = row.get("row_type") if partition == "SIM-CAL" else row.get("row_kind")
        if not isinstance(kind, str) or not kind:
            raise ValueError("explicit source row kind required")
        check = checks.get(rid)
        if partition == "SIM-VAL" and (not check or any(check.get(k) != row.get(k) for k in
                                                       ("candidate_id", "row_kind", "pdf_sha256"))):
            raise ValueError("source precheck not bound to candidate/kind/PDF")
        refs = _refs(doi, ledgers)
        blockers = [f"MISSING_{family}_ID" for family in SOURCE_FAMILIES if not refs[family]]
        blockers += ["NO_HUMAN_VERIFICATION", "MISSING_SEXP_KIN_PARAM_FORM_CHAIN"]
        # These inputs are summaries. No time/concentration point can be inferred.
        blockers.append("NO_SOURCE_RAW_TRAJECTORY")
        if kind != "K_AT_T":
            blockers.append("AUTHOR_AGGREGATE_NOT_RAW_OBSERVATIONS" if kind.startswith("AUTHOR_") else "NOT_A_RATE_ROW")
        licensed = licences.get(candidate) == "CONFIRMED_ON_PUBLISHER_PAGE"
        if not licensed:
            blockers.append("PUBLISHER_LICENCE_UNCONFIRMED")
        if partition == "SIM-CAL" and row.get("verdict") not in ("VERIFIED", "CORRECTED"):
            blockers.append("CAL_VERDICT_EXCLUDES")
        if partition == "SIM-VAL" and (check.get("status") != "PASS" or
                                       check.get("computational_eligibility") != "ELIGIBLE"):
            blockers.append("SOURCE_PRECHECK_EXCLUDES")
        normalised = {}
        if check and check.get("reason", "").startswith("ISOTHERMAL_CONTEXT_AND_EXPONENT_SERIALIZATION"):
            if kind == "AUTHOR_FIT_K0":
                normalised = {"matrix_pH": "NOT_REPORTED_BY_SOURCE", "original_nonisothermal_pH": row.get("matrix_pH"),
                              "reason": "NONISOTHERMAL_TABLE3_PH_IS_NOT_AN_ISOTHERMAL_TABLE5_MEASUREMENT",
                              "k0_normalisation": "NOT_PERFORMED_AUTHOR_AGGREGATE_REMAINS_EXCLUDED"}
                corrected += 1
        metadata = {"row_id": rid, "candidate_id": candidate, "partition": partition, "row_kind": kind,
                    "doi": doi, "pdf_sha256": digest, "existing_source_refs": refs,
                    "blockers": sorted(set(blockers)), "production_eligible": False,
                    "declared_source_precheck": check.get("status") if check else "AI_DELEGATED_CAL_VERDICT",
                    "ph_context_staging_corrected": bool(normalised)}
        public.append(metadata)
        private.append({**metadata, "record_type": "AA_SOURCE_STAGING_CANDIDATE", "verification": "AI_PRECHECKED",
                        "labels": LABELS.copy(), "original_row": row, "source_precheck": deepcopy(check),
                        "normalised_metadata": normalised})
    totals = Counter(b for row in public for b in row["blockers"])
    report = {"record": "AA_SOURCE_BOUND_LINEAGE_STAGING_READINESS", "labels": LABELS.copy(),
              "validation_label": "NOT_VALIDATED / RESEARCH_ONLY", "rows": public,
              "n_rows": len(public), "rows_by_partition": dict(Counter(r["partition"] for r in public)),
              "rows_by_kind": dict(Counter(r["row_kind"] for r in public)), "blocker_counts": dict(sorted(totals.items())),
              "ph_context_staging_corrections": corrected, "production_eligible_rows": 0, "minted_ids": [],
              "scientific_gate_pass": False, "original_sources_or_extractions_modified": False,
              "limitations": ["Source rows are privately staged, not appended as incomplete ledger records.",
                              "Exact DOI links search active existing source ledgers only; title/fuzzy matches are not asserted.",
                              "Author rate summaries can feed the declared pilot fitter but cannot fabricate KINPT/OBS trajectories.",
                              "Separate pH context correction does not make author aggregates admissible for first-order validation.",
                              "AI_PRECHECKED is staging/source-contract review, not HUMAN_VERIFIED or production eligibility."]}
    return report, private
