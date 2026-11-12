"""Synthetic-only strict-v2 context and final-render boundaries."""
from copy import deepcopy
from types import SimpleNamespace as NS

import pytest

from culinarystate.generation.strict_v2 import render, row_reasons


def fixture():
    context = {"ingredient_id": "ING-990001", "process_id": "PROC-990001", "target_id": "SVAR-990001",
               "state": "RAW", "basis": "TRUE_RETENTION", "medium": "WATER", "time_min": (5, 5),
               "temperature_c": (90, 90), "temperature_location": "CORE"}
    condition = {"id": "COND-990001", "status": "ACTIVE", "medium": "WATER",
                 "duration": {"status": "MEASURED", "value": 5, "unit": "min"},
                 "temperatures": [{"location": "CORE", "value": {"status": "MEASURED", "value": 90, "unit": "degC"}}]}
    row = {"id": "EVD-990001", "status": "ACTIVE", "tier": "E3",
           "matrix": {"ingredient_id": "ING-990001", "initial_state": "RAW"},
           "process": {"process_id": "PROC-990001", "condition_id": "COND-990001", "medium": "WATER"},
           "target": {"state_variable_id": "SVAR-990001", "basis": "TRUE_RETENTION"},
           "derived": {"retention_factor": {"status": "MEASURED", "value": .55, "unit": "fraction"}}}
    hit = NS(evd_id=row["id"], row=row, compat={"vector": {k: "MATCH" for k in ["matrix", "process", "target", "temperature", "time"]}})
    return context, condition, row, NS(direct=[hit], near=[], evidence_class="DIRECT")


def test_fully_explicit_context_only_reports_unverified_table_value():
    c, cond, row, packet = fixture()
    out = render({"mode": "ANSWER", "precision": "QUANTITATIVE"}, {"boil": packet}, {"boil": c}, {cond["id"]: cond})
    assert "0.55" in out["text"] and out["numbers"][0]["evd_id"] == row["id"]
    assert out["numbers"][0]["basis"] == "EVD_REPORTED_UNVERIFIED"
    assert out["applicability_certified"] is False and out["citable"] is False


@pytest.mark.parametrize("field", ["ingredient_id", "process_id", "target_id", "state", "basis", "medium",
                                   "time_min", "temperature_c", "temperature_location"])
def test_missing_context_never_borrows_ranking_match(field):
    c, cond, row, _ = fixture()
    c[field] = None
    assert row_reasons(row, cond, c)


@pytest.mark.parametrize("field,value", [("ingredient_id", "ING-990002"), ("process_id", "PROC-990002"),
    ("target_id", "SVAR-990002"), ("state", "COOKED"), ("basis", "APPARENT_RETENTION"), ("medium", "WATER_AND_OIL"),
    ("time_min", (4, 6)), ("temperature_c", (89, 91)), ("temperature_location", "SURFACE")])
def test_near_or_overlapping_context_is_not_exact_context(field, value):
    c, cond, row, _ = fixture()
    c[field] = value
    assert row_reasons(row, cond, c)


def test_step_membership_does_not_authorize_a_different_process():
    c, cond, row, _ = fixture()
    row["process"].update(process_id="PROC-990002", step_process_ids=[c["process_id"]])
    assert "PROCESS_ID_MISMATCH" in row_reasons(row, cond, c)


@pytest.mark.parametrize("change", ["unknown", "censored", "inactive", "ambiguous_temperature", "wrong_unit"])
def test_unknown_bound_or_inactive_source_cannot_be_a_point_claim(change):
    c, cond, row, _ = fixture()
    if change == "unknown": cond["duration"] = {"status": "UNKNOWN"}
    if change == "censored": row["derived"]["retention_factor"] = {"status": "CENSORED", "censor": {"limit": .55}}
    if change == "inactive": cond["status"] = "DEPRECATED"
    if change == "ambiguous_temperature": cond["temperatures"] *= 2
    if change == "wrong_unit": cond["duration"]["unit"] = "hours"
    assert row_reasons(row, cond, c)


def test_missing_precision_does_not_reach_a_numeric_fallback():
    c, cond, _, packet = fixture()
    out = render({"mode": "ANSWER"}, {"boil": packet}, {"boil": c}, {cond["id"]: cond},
                 fallback=lambda lines: "Retention factor 0.55 [EVD-990001].")
    assert out["mode"] == "ABSTAIN" and out["numbers"] == [] and "0.55" not in out["text"]


def test_wrong_option_or_numeric_fallback_is_rejected_after_render():
    c, cond, _, packet = fixture()
    out = render({"mode": "ANSWER", "precision": "QUANTITATIVE"}, {"boil": packet}, {"boil": c}, {cond["id"]: cond},
                 renderer=lambda lines: "fry: 0.55 [EVD-990001].", fallback=lambda lines: "0.85 [EVD-990001].")
    assert out["mode"] == "ABSTAIN" and out["numbers"] == []
    assert out["reason"] == "FINAL_RENDER_NOT_AUTHORIZED"


def test_qualitative_option_cannot_borrow_numeric_permission():
    c, cond, _, packet = fixture()
    out = render({"mode": "COMPARE", "per_option": {"boil": {"precision": "QUANTITATIVE"},
                 "fry": {"precision": "QUALITATIVE"}}}, {"boil": packet, "fry": packet},
                 {"boil": c, "fry": c}, {cond["id"]: cond})
    assert all(n["option"] == "PROC-990001" for n in out["numbers"])


def test_arbitrary_packet_label_cannot_name_a_different_process_in_the_answer():
    c, cond, _, packet = fixture()
    out = render({"mode": "ANSWER", "precision": "QUANTITATIVE"}, {"fry": packet}, {"fry": c}, {cond["id"]: cond})
    assert "fry" not in out["text"]
    assert all(n["option"] == "PROC-990001" for n in out["numbers"])


def test_input_objects_are_not_mutated():
    c, cond, row, packet = fixture()
    before = deepcopy((c, cond, row))
    render({"mode": "ANSWER", "precision": "QUANTITATIVE"}, {"boil": packet}, {"boil": c}, {cond["id"]: cond})
    assert (c, cond, row) == before
