"""S178 T2-C15-R1: EVD dataset card generator. Synthetic ledgers (invented rows, test only) plus structural checks of the committed card."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from tests.unit.test_s178_analysis_helpers import ROOT, load_tool

T = load_tool("s178_analysis_evd_card")
SECRET = "SECRETFOODNAME"


def _w(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in rows), encoding="utf-8")


def _evd(i, fam, ver=1, status="ACTIVE", cond="COND-000001", steps=("boil",), ing="ING-000001", censored=False, direction="DECREASE",
         vstatus="UNVERIFIED", target="SVAR-000001", group=None, study=()):
    rf = {"status": "CENSORED", "unit": "%", "raw": "100", "censor": {"kind": "GT_CAP", "limit": 97.5}} if censored else {"status": "MEASURED", "unit": "fraction", "value": 0.8}
    return {"id": f"EVD-{i:06d}", "version": ver, "status": status, "tier": "E3", "source_family_id": fam, "source_id": "SRC-000001",
            "matrix": {"raw_name": SECRET + str(i), "form": None, "ingredient_id": ing, "food_group": "Dairy"},
            "process": {"steps": list(steps), "step_process_ids": ["PROC-000001"], "process_id": "PROC-000001", "condition_id": cond, "modifiers": {}},
            "target": {"state_variable_id": target, "raw_name": "Calcium", "basis": "RETENTION_TR_OR_AR"},
            "derived": {"direction": direction, "retention_factor": rf}, "censored": censored, "verification": {"status": vstatus},
            "study_ids": list(study), "study_id_status": "PRESENT" if study else "NOT_IDENTIFIABLE", "independence_group": group or fam,
            "provenance": {"source_ids": ["SRC-000001"]}, "measurement_method_id": "MEAS-000001", "extraction_version": "x@1",
            "created_by": "t", "origin_type": "DATABASE_AGGREGATE", "design": "DATABASE_AGGREGATE", "applicability": "GENERIC"}


@pytest.fixture()
def fixture_root(tmp_path: Path) -> Path:
    led = tmp_path / "ledgers/data"
    _w(led / "EVD.jsonl", [
        _evd(1, "FAM-A", ver=1), _evd(1, "FAM-A", ver=2),                       # two versions, latest ACTIVE
        _evd(2, "FAM-A", cond="COND-000002", censored=True),
        _evd(3, "FAM-B", cond="COND-000002", ing=None, direction="INCREASE", vstatus="AI_PRECHECKED", study=("STUDY-000001",), group="g1"),
        _evd(4, "FAM-B", status="DEPRECATED"),
    ])
    mask1 = {"temperature": "UNKNOWN", "duration": "UNKNOWN", "ph": "UNKNOWN", "moisture": "UNKNOWN", "pressure": "NOT_APPLICABLE"}
    mask2 = {"temperature": "MEASURED", "duration": "RANGE", "ph": "UNKNOWN", "moisture": "UNKNOWN", "pressure": "NOT_APPLICABLE"}
    c = lambda i, m, **kw: {"id": f"COND-{i:06d}", "version": 1, "status": "ACTIVE", "completeness_mask": m, "verification": {"status": "UNVERIFIED"},  # noqa: E731
                            "duration": {"status": m["duration"], "unit": "min", "low": 10.0, "high": 20.0}, **kw}
    _w(led / "COND.jsonl", [c(1, mask1), c(2, mask2, temperatures=[{"location": "UNSPECIFIED", "value": {"status": "MEASURED", "value": 100.0, "unit": "degC"}}])])
    _w(led / "SRC.jsonl", [{"id": "SRC-000001", "version": 1, "status": "ACTIVE", "licence_status": "ASSUMED", "storage_rule": "DERIVED_ONLY", "kind": "DATABASE", "licence": "test licence"}])
    _w(led / "MEAS.jsonl", [{"id": "MEAS-000001", "version": 1, "status": "ACTIVE", "family": "CALCULATION", "basis": "UNKNOWN"}])
    _w(led / "SVAR.jsonl", [{"id": "SVAR-000001", "version": 1, "status": "ACTIVE", "family": "CHEMICAL", "canonical_name": "Calcium content"}])
    _w(led / "PROC.jsonl", [{"id": "PROC-000001", "version": 1, "status": "ACTIVE", "family": "WET_HEAT", "kind": "ACTION", "canonical_name": "boil"}])
    _w(led / "ING.jsonl", [{"id": "ING-000001", "version": 1, "status": "ACTIVE", "canonical_name": "butter"}])
    _w(led / "STUDY.jsonl", [{"id": "STUDY-000001", "version": 1, "status": "ACTIVE"}])
    reg = tmp_path / "registry"
    reg.mkdir()
    (reg / "state_variable_registry_v1.csv").write_text("state_variable_id,subfamily,status,canonical_variable_id\nSVAR-000001,NUTRIENT_CONTENT,ACTIVE,\n", encoding="utf-8")
    (reg / "svar_duplicate_mapping_v1.csv").write_text("duplicate_id,canonical_id\n", encoding="utf-8")
    seal = tmp_path / "reports/step15"
    seal.mkdir(parents=True)
    (seal / "15a_R_seal_commitment_v1.json").write_text(json.dumps({
        "snapshot": {"active_rows": 3, "evd_sha256": "0" * 64}, "n_groups": 2, "n_reserved": 1, "n_reserved_rows": 1,
        "strata": {"FAM-A": {"n_rows": 2, "n_groups": 1, "n_reserved": 0, "n_reserved_rows": 0}}}), encoding="utf-8")
    return tmp_path


def test_counts_and_labels(fixture_root):
    c = T.build(fixture_root)
    assert c["s203_9_1_total_rows"]["active_rows"] == 3
    assert c["s203_9_1_total_rows"]["deprecated_ids"] == 1
    assert c["s203_9_1_total_rows"]["ledger_version_lines"] == 5
    assert c["s203_9_1_total_rows"]["rows_per_source_family"] == {"FAM-A": 2, "FAM-B": 1}
    lab = c["labels"]
    assert lab["E3_UNVERIFIED"] == 3 and lab["BOOTSTRAP_UNVERIFIED"] == 3 and lab["COND_UNAUDITED"] == 3
    assert lab["human_verified_rows"] == 0 and lab["d1_verified_rows_n_of_40"] == "0/40"
    assert lab["verification_status_rows"] == {"UNVERIFIED": 2, "AI_PRECHECKED": 1}


def test_coverage_censoring_and_conflict_free(fixture_root):
    c = T.build(fixture_root)
    cov = c["s203_9_9_condition_coverage"]
    assert cov["temperature"]["rows_by_status"] == {"MEASURED": 2, "UNKNOWN": 1}
    assert cov["duration"]["rows_by_status"] == {"RANGE": 2, "UNKNOWN": 1}
    assert cov["temperature_and_duration_both_stated"]["rows"] == 2
    assert cov["water_activity"]["status"] == "NOT_IN_COND_SCHEMA"
    assert c["censoring"]["censored_rows"] == 1 and c["censoring"]["censored_rows_by_source"]["FAM-A"] == 1
    assert c["censoring"]["censor_limits"] == {"FAM-A|GT_CAP|97.5": 1}
    assert c["s203_9_2_unique_ingredients"]["unique_ing_ids_linked"] == 1
    assert c["s203_9_2_unique_ingredients"]["pct_rows_with_ing_link"] == pytest.approx(66.67)
    assert c["s203_9_13_duplicate_conflict_audit"]["conflict_candidate_cells_opposite_direction_across_groups"] == 0


def test_every_203_9_item_has_a_section(fixture_root):
    c = T.build(fixture_root)
    for n in range(1, 14):
        assert any(k.startswith(f"s203_9_{n}_") for k in c), n


def test_deterministic_and_counts_only(fixture_root, tmp_path):
    a = T.write(fixture_root, tmp_path / "o1")
    b = T.write(fixture_root, tmp_path / "o2")
    assert a == b
    js = (tmp_path / "o1/evd_dataset_card_v1.json").read_text(encoding="utf-8")
    md = (tmp_path / "o1/evd_dataset_card_v1.md").read_text(encoding="utf-8")
    assert SECRET not in js and SECRET not in md      # raw source food names never enter the card
    assert "2026-" not in js                           # no timestamp
    assert json.loads(js)["contains_text"] is False


def test_ledgers_not_modified(fixture_root, tmp_path):
    before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (fixture_root / "ledgers/data").glob("*.jsonl")}
    T.write(fixture_root, tmp_path / "o")
    after = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (fixture_root / "ledgers/data").glob("*.jsonl")}
    assert before == after


def test_committed_card_matches_current_ledger():
    card = ROOT / "reports/s178/analysis/evd_dataset_card_v1.json"
    if not card.is_file():
        pytest.skip("card not generated in this tree")
    c = json.loads(card.read_text(encoding="utf-8"))
    ev = ROOT / "ledgers/data/EVD.jsonl"
    assert c["inputs"]["ledgers/data/EVD.jsonl"] == hashlib.sha256(ev.read_bytes()).hexdigest(), "EVD ledger changed: regenerate the card"
    assert c["s203_9_1_total_rows"]["active_rows"] == 17978
    assert c["labels"]["human_verified_rows"] == 0
    assert sum(c["s203_9_1_total_rows"]["rows_per_source_family"].values()) == 17978
