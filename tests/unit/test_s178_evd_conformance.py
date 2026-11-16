"""S178 EVD lane, T2-C01-R1: the 203.2 conformance classifier on synthetic rows (no ledger read)."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
_spec = importlib.util.spec_from_file_location("s178_evd_conformance", ROOT / "tools/s178_evd_conformance.py")
CF = importlib.util.module_from_spec(_spec)
sys.modules["s178_evd_conformance"] = CF
_spec.loader.exec_module(CF)
P, C, U, N, A = CF.STATUSES


def temp(status, loc="UNSPECIFIED", **kw):
    return {"location": loc, "value": {"status": status, "unit": "degC", **kw}}


def make(*, temps=(), dur="UNKNOWN", rf=None, before_after=False, ing="ING-000001", proc="PROC-000001", censored=False, family="USDA-RETN-R6", extra_cond=None, direction="UNKNOWN"):
    d = {"direction": direction}
    if rf is not None:
        d["retention_factor"] = rf
    e = {"id": "EVD-000001", "censored": censored, "tier": "E3", "extraction_version": "x@1", "provenance": {"source_ids": ["SRC-1"]},
         "matrix": {"ingredient_id": ing, "raw_name": "X"}, "process": {"process_id": proc, "steps": ["boil"]},
         "target": {"state_variable_id": "SVAR-000009", "raw_name": "Vit C", "basis": "X"}, "derived": d, "study_ids": [], "verification": {"status": "UNVERIFIED"}}
    if before_after:
        e["before"] = {"status": "MEASURED", "value": 1.0, "unit": "mg"}
        e["after"] = {"status": "MEASURED", "value": 0.5, "unit": "mg"}
    cond = {"completeness_mask": {}, "duration": {"status": dur, **({"value": 5.0, "unit": "min"} if dur == "MEASURED" else {}), **({"low": 1.0, "high": 2.0, "unit": "min"} if dur == "RANGE" else {})}}
    if temps:
        cond["temperatures"] = list(temps)
    cond.update(extra_cond or {})
    x = {"source_family_id": family, "process_family": "WET_HEAT", "provenance_class": "EXPLICIT_SOURCE"}
    return CF.Row(x, e, cond, {"SRC-1": {}}, {"SVAR-000009": {"family": "CHEMICAL"}}, None)


def status(field, row):
    rule = next(f[5] for f in CF.FIELDS if f[1] == field)
    return rule(row)[0]


def test_every_field_has_exactly_one_status_and_counts_sum_to_row_count():
    rows = [make(), make(temps=[temp("MEASURED")], dur="MEASURED", rf={"status": "MEASURED", "value": 0.5, "unit": "fraction"}),
            make(temps=[temp("RANGE", low=1.0, high=2.0)], dur="RANGE", rf={"status": "CENSORED", "unit": "%", "censor": {"kind": "GT_CAP", "limit": 97.5}}, censored=True)]
    table = CF.classify(rows)
    assert len(table) == len(CF.FIELDS) == 55
    for t in table:
        assert sum(t["counts"].values()) == t["total"] == 3
        assert set(t["counts"]) == set(CF.STATUSES)


def test_temperature_forms_are_not_mixed():
    assert status("T_value", make(temps=[temp("MEASURED")])) == P
    assert status("T_lo", make(temps=[temp("MEASURED")])) == N                       # a point value makes lo / hi moot
    assert status("T_value", make(temps=[temp("RANGE", low=1.0, high=2.0)])) == N
    assert status("T_lo", make(temps=[temp("RANGE", low=1.0, high=2.0)])) == P
    one_sided = make(temps=[temp("CENSORED", "CORE", censor={"kind": "GT_STATED", "limit": 75.0})])
    assert status("T_value", one_sided) == C and status("T_lo", one_sided) == N       # "> 75 C" is a bound, not a range and not a value
    assert status("T_value", make()) == U and status("T_lo", make()) == U             # nothing stated: UNKNOWN, never 0
    assert status("T_type", make(temps=[temp("MEASURED", "SETPOINT")])) == P
    assert status("T_type", make(temps=[temp("MEASURED", "UNSPECIFIED")])) == U


def test_duration_and_absent_type_fields():
    assert status("t_value", make(dur="MEASURED")) == P and status("t_lo", make(dur="MEASURED")) == N
    assert status("t_lo", make(dur="RANGE")) == P and status("t_value", make(dur="RANGE")) == N
    assert status("t_value", make(dur="UNKNOWN")) == U
    for f in ("t_type", "ingredient_state_out", "moisture_type", "water_activity_type", "pressure_type", "ordinal_band", "platform", "split_id"):
        assert status(f, make()) == A


def test_target_value_censored_unknown_and_yield():
    assert status("target_value", make(rf={"status": "MEASURED", "value": 0.0, "unit": "fraction"})) == P         # a measured zero is a value
    assert status("target_value", make(rf={"status": "CENSORED", "unit": "%", "censor": {"kind": "GT_CAP", "limit": 97.5}}, censored=True)) == C
    assert status("target_lo", make(rf={"status": "CENSORED", "unit": "%", "censor": {"kind": "GT_CAP", "limit": 97.5}}, censored=True)) == C
    assert status("target_hi", make(rf={"status": "CENSORED", "unit": "%", "censor": {"kind": "GT_CAP", "limit": 97.5}}, censored=True)) == N
    assert status("target_value", make(rf={"status": "UNKNOWN", "unit": "%"})) == U and status("unit", make(rf={"status": "UNKNOWN"})) == U
    y = make(); y.e["derived"]["yield_factor"] = {"status": "MEASURED", "value": 0.9}
    assert status("target_value", y) == P
    assert status("target_value", make(before_after=True)) == P


def test_condition_fields_never_populated_are_unknown_and_pressure_na_follows_the_mask():
    for f in ("tool", "geometry", "moisture_value", "water_activity_value", "pH_value", "oxygen_value", "mixing"):
        assert status(f, make()) == U
    r = make(); r.c["completeness_mask"]["pressure"] = "NOT_APPLICABLE"
    assert status("pressure_value", r) == N
    assert status("pressure_value", make(extra_cond={"pressure": {"status": "MEASURED", "value": 15.0, "unit": "psi"}})) == P
    assert status("pressure_value", make()) == U


def test_identity_and_provenance_fields():
    assert status("ingredient_id", make(ing=None)) == U and status("ingredient_id", make()) == P
    assert status("process_leaf", make(proc=None)) == U
    assert status("verified_by", make()) == U                       # no human verifier on any E3 row
    assert status("notes", make()) == U
    assert status("LOD", make()) == U
    assert status("doi_or_citation", make()) == U
    r = make(); r.src["SRC-1"] = {"doi": "10.x/y"}
    assert status("doi_or_citation", r) == P
    assert status("study_id", make()) == U


def test_md_and_csv_render_with_totals():
    rows = [make(), make(temps=[temp("MEASURED")])]
    table = CF.classify(rows)
    d = {"scope": {"rows": 2, "rows_by_source_family": {"USDA-RETN-R6": 2}}, "table": table,
         "summary": {"fields_total": len(table), "ssot_203_2_lines": 45, "carried_on_every_row": 1, "populated_on_some_rows": 1, "in_schema_but_never_populated": 1, "no_field_exists": 1, "other": 0,
                     "lists": {"carried_on_every_row": ["a"], "populated_on_some_rows": ["b"], "in_schema_but_never_populated": ["c"], "no_field_exists": ["d"], "other": []}},
         "export_v2_lineage": {"split_group_id_present": 2, "rows_with_v2_key_record": 2, "distinct_split_group_ids": 1, "assignment_status": {}, "study_id_present_v2": 0,
                               "lineage_study_id_status": {}, "independence_resolution": {}}}
    csv_text = CF.render_csv(d)
    assert csv_text.splitlines()[0].startswith("ssot_203_2_line,field,group,carrier,match,PRESENT")
    assert len(csv_text.splitlines()) == 1 + len(table)
    assert "Findings that change other documents" in CF.render_md(d)
