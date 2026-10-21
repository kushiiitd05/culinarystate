"""ES-1.1 tests: normalised EVD export (non-destructive, deterministic, no invented values)."""
import copy
import json
import math
from pathlib import Path

import jsonschema
import pytest

from culinarystate.evidence import evd_export as X

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = json.loads((ROOT / "registry/schemas/evd_export_v1.schema.json").read_text())


def q(value=None, unit="mg/100 g fresh weight", status="MEASURED", censor=None):
    return {"status": status, "value": value, "unit": unit, "censor": censor}


def rec(**kw):
    r = {"id": "EVD-000001", "record_type": "EVD", "version": 1, "status": "ACTIVE", "source_id": "SRC-000001", "source_family_id": "X", "study_ids": [], "study_id_status": "NOT_IDENTIFIABLE",
         "origin_type": "DATABASE_AGGREGATE", "provenance": {"method": "IMPORT", "source_ids": ["SRC-000001"]}, "verification": {"status": "UNVERIFIED"}, "tier": "E3", "design": "DATABASE_AGGREGATE", "censored": False, "applicability": "GENERIC",
         "matrix": {"ingredient_id": None, "raw_name": "Onion, RAW "}, "process": {"process_id": None, "condition_id": None, "steps": ["boil"]}, "target": {"state_variable_id": "SVAR-000001", "basis": "FRESH_WEIGHT"},
         "before": q(10.0), "after": q(5.0), "derived": {"direction": "DECREASE", "retention_factor": {"status": "MEASURED", "value": 0.5, "unit": "fraction"}}}
    r.update(kw)
    return r


def row(r, dup=None):
    return X.export_row(r, {}, {}, dup or {}, "sha")


def test_delta_and_lfc_need_measured_same_unit_positive():
    assert X.derive_delta(q(10.0), q(4.0))[0] == -6.0
    assert X.derive_delta(q(10.0), q(4.0, unit="mg/100 mL"))[0] is None
    assert X.derive_delta(q(None, status="UNKNOWN"), q(4.0))[0] is None
    assert math.isclose(X.derive_log_fold_change(q(10.0), q(5.0))[0], math.log(0.5))
    assert X.derive_log_fold_change(q(0.0), q(5.0))[0] is None
    assert X.derive_log_fold_change(q(10.0), q(0.0))[0] is None


def test_censored_inputs_never_derive():
    cen = {"kind": "GT_CAP", "limit": 97.5}
    assert X.derive_delta(q(10.0, censor=cen), q(5.0))[0] is None
    assert X.derive_log_fold_change(q(10.0), q(5.0, censor=cen))[0] is None
    assert X.log_retention({"status": "CENSORED", "value": 1.0, "censor": cen})[0] is None


def test_log_retention_is_separate_from_log_fold_change():
    r = rec(derived={"direction": "DECREASE", "retention_factor": {"status": "MEASURED", "value": 0.25, "unit": "fraction"}}, before=None, after=None)
    out = row(r)
    assert out["log_fold_change"] is None and math.isclose(out["log_retention_factor"], math.log(0.25))
    assert out["delta_value"] is None and out["lod"] is None and out["loq"] is None


def test_matrix_id_deterministic_and_normalised():
    a = X.matrix_id({"raw_name": "Onion,  RAW", "food_group": "Veg"})
    b = X.matrix_id({"raw_name": " onion, raw ", "food_group": "veg"})
    assert a == b and a.startswith("MTX-") and len(a) == 16
    assert X.matrix_id({"raw_name": "carrot"}) != a


def test_prior_state_unknown_when_absent():
    assert X.prior_state_id({"raw_name": "x"}) is None
    assert X.prior_state_id({"initial_state": "Raw"}) == X.prior_state_id({"initial_state": " raw "})


def test_provenance_rules_fail_safe():
    assert X.provenance_class(rec())[0] == "EXPLICIT_SOURCE"
    assert X.provenance_class(rec(provenance={"method": "LLM"}))[0] == "INFERRED_LLM"
    assert X.provenance_class(rec(provenance={"method": "MANUAL"}))[0] == "UNKNOWN"


def test_c1_fields_stay_separate_human_review_does_not_promote_tier():
    r = rec(verification={"status": "HUMAN_VERIFIED", "verifier": "Kush"}, design="UNKNOWN")
    out = row(r)
    assert out["evidence_tier"] == "E3" and out["human_verified"] is True and out["verification_status"] == "HUMAN_VERIFIED"
    assert out["design_strength"] == "UNKNOWN" and out["provenance_class"] == "EXPLICIT_SOURCE"


def test_export_row_valid_against_schema_and_source_hash():
    r = rec()
    out = row(r)
    jsonschema.Draft202012Validator(SCHEMA).validate(out)
    assert out["source_row_sha256"] == X.sha256_text(X.canon_json(r))
    r2 = copy.deepcopy(r)
    r2["notes"] = "changed"
    assert row(r2)["source_row_sha256"] != out["source_row_sha256"]


def test_duplicate_mapping_kept_reversible():
    out = row(rec(), dup={"SVAR-000001": "SVAR-000009"})
    assert out["target_state_variable_id"] == "SVAR-000001" and out["canonical_variable_id"] == "SVAR-000009"


def test_duplicate_map_reads_only_duplicate_relation(tmp_path):
    p = tmp_path / "m.csv"
    p.write_text("duplicate_id,canonical_id,relation\nSVAR-000002,SVAR-000001,DUPLICATE_SAME_ANALYTE\nSVAR-000005,,EQUIVALENT_CANDIDATE_NOT_MERGED\n")
    assert X.duplicate_map(p) == {"SVAR-000002": "SVAR-000001"}


@pytest.mark.ledgers
def test_full_ledger_export_accounts_for_all_rows_and_leaves_ledgers_unchanged():
    names = ("EVD", "SVAR", "COND", "PROC")
    before = {n: X.file_sha256(X.LEDGERS / f"{n}.jsonl") for n in names}
    rows, mt, pt, meta = X.build_export()
    evd, _ = X.latest_records("EVD")
    active = {k for k, v in evd.items() if v["status"] == "ACTIVE"}
    assert {r["evd_id"] for r in rows} == active and len(rows) == meta["active_rows"]
    assert {n: X.file_sha256(X.LEDGERS / f"{n}.jsonl") for n in names} == before
    rows2, *_ = X.build_export()
    assert [X.canon_json(r) for r in rows] == [X.canon_json(r) for r in rows2]
    assert all(r["evidence_tier"] == evd[r["evd_id"]]["tier"] for r in rows)  # tiers copied, never altered
