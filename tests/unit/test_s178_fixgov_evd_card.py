"""S178 FIX-GOV: EVD dataset card corrections (SCI-B review B1, BLOCKER; EVD lane report item 5 / board T2-C15-R1).

RED tests built from the reviewer's scenarios, on a synthetic ledger (invented rows) shaped like the real one:
  (a) water activity is a COND schema field that no row fills: the card must say IN_SCHEMA_NEVER_POPULATED, not
      "not in the schema";
  (b) a family whose completeness mask has no pressure key (Bognar, most Phenol-Explorer rows) must appear in the
      coverage table as "not recorded", so every axis row sums to N;
  (c) missingness must count "not recorded" as missing (Bognar pressure 100 %, not 0 %); NOT_APPLICABLE is not missing;
  (d) a temperature mask RANGE that is a one-sided censored bound ("> 75 C") is not a two-sided range.
Plus checks of the committed card against the real ledger counts re-derived by this lane (17,978 rows).
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.unit.test_s178_analysis_helpers import ROOT, load_tool

T = load_tool("s178_analysis_evd_card")


def _w(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in rows), encoding="utf-8")


def _evd(i, fam, cond):
    return {"id": f"EVD-{i:06d}", "version": 1, "status": "ACTIVE", "tier": "E3", "source_family_id": fam, "source_id": "SRC-000001",
            "matrix": {"raw_name": f"food{i}", "form": None, "ingredient_id": "ING-000001", "food_group": "Veg"},
            "process": {"steps": ["boil"], "step_process_ids": ["PROC-000001"], "process_id": "PROC-000001", "condition_id": cond, "modifiers": {}},
            "target": {"state_variable_id": "SVAR-000001", "raw_name": "Calcium", "basis": "RETENTION_TR_OR_AR"},
            "derived": {"direction": "DECREASE", "retention_factor": {"status": "MEASURED", "unit": "fraction", "value": 0.8}}, "censored": False,
            "verification": {"status": "UNVERIFIED"}, "study_ids": [], "study_id_status": "NOT_IDENTIFIABLE", "independence_group": fam,
            "provenance": {"source_ids": ["SRC-000001"]}, "measurement_method_id": "MEAS-000001", "extraction_version": "x@1",
            "created_by": "t", "origin_type": "DATABASE_AGGREGATE", "design": "DATABASE_AGGREGATE", "applicability": "GENERIC"}


def _cond(i, mask, temps=(), dur=None):
    return {"id": f"COND-{i:06d}", "version": 1, "status": "ACTIVE", "completeness_mask": mask, "verification": {"status": "UNVERIFIED"},
            "duration": dur or {"status": mask["duration"], "unit": "min", "value": 10.0, "low": 10.0, "high": 20.0},
            "temperatures": [{"location": "CORE", "value": v} for v in temps]}


BASE = {"ph": "UNKNOWN", "moisture": "UNKNOWN"}


@pytest.fixture()
def root(tmp_path: Path) -> Path:
    led = tmp_path / "ledgers/data"
    conds = [
        # USDA-like: pressure NOT_APPLICABLE, nothing stated
        _cond(1, {**BASE, "temperature": "UNKNOWN", "duration": "UNKNOWN", "pressure": "NOT_APPLICABLE"}),
        # Bognar-like: no pressure key in the mask; one-sided censored core temperature "> 75 C" carried as mask RANGE
        _cond(2, {**BASE, "temperature": "RANGE", "duration": "UNKNOWN"}, temps=[{"status": "CENSORED", "unit": "degC", "censor": {"kind": "GT_STATED", "limit": 75.0}}]),
        # Bognar-like: true two-sided range, no pressure key
        _cond(3, {**BASE, "temperature": "RANGE", "duration": "UNKNOWN"}, temps=[{"status": "RANGE", "unit": "degC", "low": 160.0, "high": 180.0}]),
        # Phenol-Explorer-like: pressure measured
        _cond(4, {**BASE, "temperature": "MEASURED", "duration": "MEASURED", "pressure": "MEASURED"},
              temps=[{"status": "MEASURED", "unit": "degC", "value": 100.0}]),
    ]
    conds[3]["pressure"] = {"status": "MEASURED", "unit": "kPa", "value": 101.0}
    _w(led / "COND.jsonl", conds)
    _w(led / "EVD.jsonl", [_evd(1, "FAM-USDA", "COND-000001"), _evd(2, "FAM-BOG", "COND-000002"), _evd(3, "FAM-BOG", "COND-000002"),
                            _evd(4, "FAM-BOG", "COND-000003"), _evd(5, "FAM-PE", "COND-000004")])
    _w(led / "SRC.jsonl", [{"id": "SRC-000001", "version": 1, "status": "ACTIVE", "licence_status": "ASSUMED", "storage_rule": "DERIVED_ONLY", "kind": "DATABASE", "licence": "x"}])
    _w(led / "MEAS.jsonl", [{"id": "MEAS-000001", "version": 1, "status": "ACTIVE", "family": "CALCULATION", "basis": "UNKNOWN"}])
    _w(led / "SVAR.jsonl", [{"id": "SVAR-000001", "version": 1, "status": "ACTIVE", "family": "CHEMICAL", "canonical_name": "Calcium content"}])
    _w(led / "PROC.jsonl", [{"id": "PROC-000001", "version": 1, "status": "ACTIVE", "family": "WET_HEAT", "kind": "ACTION", "canonical_name": "boil"}])
    _w(led / "ING.jsonl", [{"id": "ING-000001", "version": 1, "status": "ACTIVE", "canonical_name": "carrot"}])
    _w(led / "STUDY.jsonl", [])
    reg = tmp_path / "registry"
    reg.mkdir()
    (reg / "state_variable_registry_v1.csv").write_text("state_variable_id,subfamily,status,canonical_variable_id\nSVAR-000001,NUTRIENT_CONTENT,ACTIVE,\n", encoding="utf-8")
    (reg / "svar_duplicate_mapping_v1.csv").write_text("duplicate_id,canonical_id\n", encoding="utf-8")
    (tmp_path / "reports/step15").mkdir(parents=True)
    (tmp_path / "reports/step15/15a_R_seal_commitment_v1.json").write_text(json.dumps(
        {"snapshot": {"active_rows": 5, "evd_sha256": "0" * 64}, "n_groups": 1, "n_reserved": 0, "n_reserved_rows": 0, "strata": {}}), encoding="utf-8")
    return tmp_path


def test_a_water_activity_is_in_the_schema_but_never_populated(root):
    wa = T.build(root)["s203_9_9_condition_coverage"]["water_activity"]
    assert wa["status"] == "IN_SCHEMA_NEVER_POPULATED" and wa["in_cond_schema"] is True and wa["rows_with_value"] == 0
    assert "NOT_IN_COND_SCHEMA" not in json.dumps(T.build(root))


def test_b_every_axis_row_sums_to_n_with_a_not_recorded_column(root):
    c = T.build(root)
    cov = c["s203_9_9_condition_coverage"]
    n = c["s203_9_1_total_rows"]["active_rows"]
    for ax in T.AXES:
        assert sum(cov[ax]["rows_by_status"].values()) == n, ax
    assert cov["pressure"]["rows_by_status"] == {"MEASURED": 1, "NOT_APPLICABLE": 1, "NOT_RECORDED": 3}
    md = T.to_markdown(c)
    row = next(line for line in md.splitlines() if line.startswith("| pressure |"))
    cells = [x.strip().replace(",", "") for x in row.strip("|").split("|")[1:]]
    assert sum(int(x) for x in cells[:-1]) == int(cells[-1]) == n            # last column is the row total


def test_c_not_recorded_counts_as_missing_and_not_applicable_does_not(root):
    m = T.build(root)["s203_9_11_missingness"]["pct_missing_by_source_and_axis"]
    assert m["FAM-BOG"]["pressure"] == 100.0                                  # was 0.0 % (only UNKNOWN was counted)
    assert m["FAM-USDA"]["pressure"] == 0.0                                    # NOT_APPLICABLE is not missing
    assert m["FAM-PE"]["pressure"] == 0.0


def test_d_one_sided_censored_temperature_is_not_a_range(root):
    c = T.build(root)
    t = c["s203_9_9_condition_coverage"]["temperature"]["rows_by_status"]
    assert t == {"CENSORED_ONE_SIDED": 2, "MEASURED": 1, "RANGE_TWO_SIDED": 1, "UNKNOWN": 1}
    rv = c["s203_9_12_condition_ranges"]["range_valued_conditions"]
    assert rv["temperature_range_rows_two_sided"] == 1 and rv["temperature_censored_one_sided_rows"] == 2 and rv["temperature_mask_RANGE_rows"] == 3


# ------------------------------------------------------------------ the committed card (real ledger)
@pytest.fixture()
def card():
    p = ROOT / "reports/s178/analysis/evd_dataset_card_v1.json"
    if not p.is_file():
        pytest.skip("card not generated in this tree")
    return json.loads(p.read_text(encoding="utf-8"))


def test_committed_card_has_the_corrected_coverage(card):
    cov = card["s203_9_9_condition_coverage"]
    n = card["s203_9_1_total_rows"]["active_rows"]
    assert n == 17978
    for ax in T.AXES:
        assert sum(cov[ax]["rows_by_status"].values()) == n, ax
    assert cov["temperature"]["rows_by_status"]["CENSORED_ONE_SIDED"] == 3369 and cov["temperature"]["rows_by_status"]["RANGE_TWO_SIDED"] == 216
    assert cov["pressure"]["rows_by_status"] == {"MEASURED": 129, "NOT_APPLICABLE": 7018, "NOT_RECORDED": 10831}
    assert cov["water_activity"]["status"] == "IN_SCHEMA_NEVER_POPULATED"
    assert card["s203_9_11_missingness"]["pct_missing_by_source_and_axis"]["BOGNAR-2002"]["pressure"] == 100.0
    assert "DRAFT" in card["status"]
