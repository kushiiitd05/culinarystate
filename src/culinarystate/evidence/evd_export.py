"""ES-1.1: non-destructive normalised EVD export implementing the frozen MP-1 contract (registry/evd_contract_v1.csv).

Reads the append-only ledgers; writes only new files. No scientific value is invented: every numeric field is either copied from the source record or
derived by a documented deterministic formula from copied values. Anything not derivable stays null with an explicit status.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
from pathlib import Path

EXPORT_VERSION = "evd_export@1.0.0"
ROOT = Path(__file__).resolve().parents[3]
LEDGERS = ROOT / "ledgers" / "data"

DESIGN_VOCAB = ("CONTROLLED_EXPERIMENT", "OBSERVATIONAL", "DATABASE_AGGREGATE", "REVIEW", "AUTHORITY", "UNKNOWN")
VERIFICATION_VOCAB = ("UNVERIFIED", "AI_PRECHECKED", "HUMAN_VERIFIED", "HUMAN_REJECTED", "NEEDS_SOURCE", "CONFLICT")
PROVENANCE_VOCAB = ("EXPLICIT_SOURCE", "EXTERNAL_VERIFIED", "DERIVED_DETERMINISTIC", "INFERRED_LLM", "MODEL_ESTIMATED", "IMPUTED", "SIMULATED", "UNKNOWN")


def canon_json(obj) -> str:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def latest_records(name: str, root: Path = LEDGERS) -> tuple[dict, int]:
    """latest version per id (append-only ledger) and total version lines read"""
    out, n = {}, 0
    with open(root / f"{name}.jsonl", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                r = json.loads(line)
                n += 1
                out[r["id"]] = r
    return out, n


def norm_text(s):
    if s is None:
        return None
    t = re.sub(r"\s+", " ", str(s).strip().lower())
    return t or None


def matrix_key(m: dict) -> dict:
    keys = ("ingredient_id", "raw_name", "food_group", "variety", "part", "form", "prior_processing", "initial_state", "geometry", "storage_ripeness")
    return {k: (m.get(k) if k == "ingredient_id" else norm_text(m.get(k))) for k in keys}


def matrix_id(m: dict) -> str:
    return "MTX-" + sha256_text(canon_json(matrix_key(m)))[:12]


def prior_state_key(m: dict) -> dict | None:
    k = {"initial_state": norm_text(m.get("initial_state")), "prior_processing": norm_text(m.get("prior_processing"))}
    return None if not any(k.values()) else k


def prior_state_id(m: dict) -> str | None:
    k = prior_state_key(m)
    return None if k is None else "PST-" + sha256_text(canon_json(k))[:12]


def measured(x) -> float | None:
    """numeric value of a MEASURED, uncensored quantity; else None"""
    if not x or x.get("status") != "MEASURED" or x.get("censor"):
        return None
    v = x.get("value")
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
        return None
    return float(v)


def comparable(before: dict, after: dict) -> bool:
    return bool(before and after and before.get("unit") and before.get("unit") == after.get("unit"))


def derive_delta(before, after):
    """after - before when both are MEASURED, uncensored, same unit. -> (value, unit, reason_if_none)"""
    b, a = measured(before), measured(after)
    if b is None or a is None:
        return None, None, "inputs_not_measured_or_censored"
    if not comparable(before, after):
        return None, None, "unit_mismatch_or_missing"
    return a - b, before["unit"], None


def derive_log_fold_change(before, after):
    """ln(after/before) (natural log) when both MEASURED, uncensored, same unit and strictly positive"""
    b, a = measured(before), measured(after)
    if b is None or a is None:
        return None, "inputs_not_measured_or_censored"
    if not comparable(before, after):
        return None, "unit_mismatch_or_missing"
    if b <= 0 or a <= 0:
        return None, "non_positive_value"
    return math.log(a / b), None


def log_retention(rf):
    """ln(reported retention factor) when MEASURED, uncensored and > 0. Kept separate from log_fold_change: a reported retention factor may include a yield
    correction (true retention) or be apparent, so it is not assumed to equal a concentration ratio (contract conflict C4)."""
    v = measured(rf)
    if v is None:
        return None, "retention_not_measured_or_censored"
    if v <= 0:
        return None, "non_positive_value"
    return math.log(v), None


def provenance_class(rec: dict) -> tuple[str, str | None]:
    """deterministic from origin_type + provenance.method; fail-safe UNKNOWN"""
    method = (rec.get("provenance") or {}).get("method")
    origin = rec.get("origin_type")
    if method == "IMPORT" and origin in ("DATABASE_AGGREGATE", "PRIMARY_STUDY"):
        note = "SOURCE_SIDE_IMPUTATION_POSSIBLE_NOT_ROW_IDENTIFIABLE" if rec.get("source_family_id") == "USDA-RETN-R6" else None
        return "EXPLICIT_SOURCE", note
    if method == "LLM":
        return "INFERRED_LLM", None
    if method == "MODEL":
        return "MODEL_ESTIMATED", None
    return "UNKNOWN", "no_deterministic_rule_for_origin_method"


def design_strength(rec: dict) -> str:
    d = rec.get("design")
    return d if d in DESIGN_VOCAB else "UNKNOWN"


def duplicate_map(mapping_csv: Path) -> dict[str, str]:
    """duplicate SVAR id -> canonical SVAR id (registry/svar_duplicate_mapping_v1.csv, relation DUPLICATE_SAME_ANALYTE). Reversible: both ids stay in every export row."""
    import csv
    out = {}
    with open(mapping_csv, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["relation"] == "DUPLICATE_SAME_ANALYTE":
                out[r["duplicate_id"]] = r["canonical_id"]
    return out


def export_row(rec: dict, cond: dict, proc: dict, dup: dict[str, str], ledger_sha: str) -> dict:
    m, p, t = rec["matrix"], rec["process"], rec["target"]
    before, after = rec.get("before"), rec.get("after")
    d = rec.get("derived") or {}
    rf, yf, pc = d.get("retention_factor"), d.get("yield_factor"), d.get("percent_change")
    dv, du, dreason = derive_delta(before, after)
    lf, lreason = derive_log_fold_change(before, after)
    lr, lrreason = log_retention(rf)
    pclass, pnote = provenance_class(rec)
    c = cond.get(p.get("condition_id")) or {}
    mask = c.get("completeness_mask") or {}
    sv = t.get("state_variable_id")
    cens = (rf or {}).get("censor") or {}
    return {
        "evd_id": rec["id"], "ledger_version": rec["version"], "export_version": EXPORT_VERSION, "source_row_sha256": sha256_text(canon_json(rec)),
        "source_id": rec["source_id"], "source_family_id": rec["source_family_id"], "study_ids": list(rec.get("study_ids") or []), "study_id_status": rec["study_id_status"],
        "measurement_id": rec.get("measurement_method_id"),
        "ingredient_id": m.get("ingredient_id"), "matrix_id": matrix_id(m), "matrix_raw_name": m.get("raw_name"), "food_group": m.get("food_group"),
        "prior_state_id": prior_state_id(m), "prior_state_status": "UNKNOWN" if prior_state_key(m) is None else "RAW_DESCRIPTOR_HASH",
        "process_id": p.get("process_id"), "process_raw_name": p.get("raw_name"), "process_steps": list(p.get("steps") or []),
        "process_family": (proc.get(p.get("process_id")) or {}).get("family") or p.get("family"),
        "condition_id": p.get("condition_id"), "condition_completeness": {k: mask.get(k) for k in sorted(mask)},
        "target_state_variable_id": sv, "canonical_variable_id": dup.get(sv, sv), "target_raw_name": t.get("raw_name"), "target_basis": t.get("basis"),
        "before_status": (before or {}).get("status"), "before_value": (before or {}).get("value"), "before_unit": (before or {}).get("unit"),
        "after_status": (after or {}).get("status"), "after_value": (after or {}).get("value"), "after_unit": (after or {}).get("unit"),
        "delta_value": dv, "delta_unit": du, "delta_provenance": "DERIVED_DETERMINISTIC" if dv is not None else None, "delta_status": "DERIVED" if dv is not None else "UNKNOWN", "delta_reason_if_unknown": dreason,
        "direction": d.get("direction") or "UNKNOWN",
        "retention_status": (rf or {}).get("status", "ABSENT"), "retention_fraction": (rf or {}).get("value"), "retention_unit": (rf or {}).get("unit"),
        "log_fold_change": lf, "log_fold_change_provenance": "DERIVED_DETERMINISTIC" if lf is not None else None, "log_fold_change_reason_if_unknown": lreason,
        "log_retention_factor": lr, "log_retention_provenance": "DERIVED_DETERMINISTIC" if lr is not None else None, "log_retention_reason_if_unknown": lrreason,
        "percent_change": (pc or {}).get("value"), "yield_status": (yf or {}).get("status", "ABSENT"), "yield_fraction": (yf or {}).get("value"),
        "value_low": (rf or {}).get("low"), "value_high": (rf or {}).get("high"),
        "evidence_tier": rec["tier"], "provenance_class": pclass, "provenance_note": pnote, "verification_status": rec["verification"]["status"],
        "human_verified": rec["verification"]["status"] == "HUMAN_VERIFIED", "design_strength": design_strength(rec), "applicability": rec.get("applicability") or "UNKNOWN",
        "censoring_flag": bool(rec["censored"]), "censor_kind": cens.get("kind"), "censor_limit": cens.get("limit"),
        "lod": None, "loq": None, "lod_loq_status": "NOT_REPORTED_BY_SOURCE_ROW",
    }


def build_export(ledgers: Path = LEDGERS, mapping_csv: Path | None = None):
    """-> (rows, matrix_table, prior_state_table, meta). Rows are the ACTIVE latest EVD records, sorted by evd_id."""
    mapping_csv = mapping_csv or ROOT / "registry" / "svar_duplicate_mapping_v1.csv"
    evd, n_versions = latest_records("EVD", ledgers)
    cond, _ = latest_records("COND", ledgers)
    proc, _ = latest_records("PROC", ledgers)
    dup = duplicate_map(mapping_csv)
    sha = file_sha256(ledgers / "EVD.jsonl")
    active = [evd[k] for k in sorted(evd) if evd[k]["status"] == "ACTIVE"]
    rows = [export_row(r, cond, proc, dup, sha) for r in active]
    mt, pt = {}, {}
    for r in active:
        m = r["matrix"]
        mt[matrix_id(m)] = matrix_key(m)
        k = prior_state_key(m)
        if k:
            pt["PST-" + sha256_text(canon_json(k))[:12]] = k
    meta = {"ledger_file": "ledgers/data/EVD.jsonl", "ledger_sha256": sha, "ledger_version_lines": n_versions, "ledger_ids_latest": len(evd), "active_rows": len(active), "export_version": EXPORT_VERSION}
    return rows, mt, pt, meta
