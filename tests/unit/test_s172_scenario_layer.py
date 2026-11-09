"""S172 / D-077 Layer 2 SCENARIO: fill only gaps from the registry / corpus quantiles; GENTLE <= TYPICAL <= INTENSE."""
from __future__ import annotations

import pytest

from culinarystate.simulation import scenario_layer as SL


def _rec(proc, fam, **inp):
    base = {k: {"value": None, "status": "UNKNOWN", "basis": None, "span": None}
            for k in ("duration", "temperature_profile", "medium", "lid_state", "start_mode", "piece_size_class",
                      "water_ratio", "matrix_class")}
    for k, (v, b) in inp.items():
        base[k] = {"value": v, "status": "MEASURED" if not isinstance(v, list) else "RANGE", "basis": b, "span": None}
    return {"recipe_id": "R", "event_id": "E1", "process_id": proc, "family": fam, "inputs": base,
            "oven_setpoint_code": None}


@pytest.fixture(scope="module")
def layer():
    return SL.ScenarioLayer.load()


def test_stated_values_kept_gaps_filled_with_ids(layer):
    rec = _rec("PROC-000019", "WET_HEAT", duration=("20", "TEXT_STATED"), temperature_profile=("100", "PHYSICAL_DEFINITION"),
               medium=("WATER", "PROCESS_DEFINITION"), piece_size_class=("DICED", "CUT_HISTORY"))
    out = layer.run(rec)
    t = out["scenarios"]["TYPICAL"]
    assert t["bath_c"] == 100 and t["bases"]["bath_c"] == "L1:PHYSICAL_DEFINITION"
    assert t["duration_min"] == 20 and t["bases"]["duration_min"] == "L1:TEXT_STATED"
    assert t["bases"]["h"] == "SD-030" and t["bases"]["half_thickness_m"] == "SD-052"
    assert 95 < t["core_end_c"] <= 100 and out["transition_status"] == "physically_possible"
    assert out["labels"] == ["SCENARIO", "MODEL_DERIVED", "NON_CITABLE", "ASSUMED_DEFAULT"]


def test_simmer_bath_from_registry_and_brackets_ordered(layer):
    rec = _rec("PROC-000020", "WET_HEAT", duration=("15", "TEXT_STATED"), medium=("WATER", "PROCESS_DEFINITION"),
               piece_size_class=("SLICED", "CUT_HISTORY"))
    s = layer.run(rec)["scenarios"]
    assert [s[k]["bath_c"] for k in ("GENTLE", "TYPICAL", "INTENSE")] == [85, 90, 95]
    assert s["GENTLE"]["core_end_c"] <= s["TYPICAL"]["core_end_c"] <= s["INTENSE"]["core_end_c"]
    assert s["GENTLE"]["core_cook_value_min"] <= s["INTENSE"]["core_cook_value_min"]


def test_missing_duration_from_corpus_quantiles(layer):
    rec = _rec("PROC-000001", "DRY_HEAT", medium=("OVEN_AIR", "PROCESS_DEFINITION"))
    s = layer.run(rec)["scenarios"]
    assert s["GENTLE"]["bases"]["duration_min"].startswith("KGE-")
    assert s["GENTLE"]["duration_min"] <= s["TYPICAL"]["duration_min"] <= s["INTENSE"]["duration_min"]
    assert s["TYPICAL"]["core_end_c"] is None and "CORE_UNKNOWN_NO_SIZE" in s["TYPICAL"]["flags"]
    assert s["TYPICAL"]["surface_cook_value_min"] is None  # dry heat: surface is not at bath temperature


def test_gas_mark_converted_in_layer_2_only(layer):
    rec = _rec("PROC-000001", "DRY_HEAT", duration=("30", "TEXT_STATED"), medium=("OVEN_AIR", "PROCESS_DEFINITION"))
    rec["oven_setpoint_code"] = "GAS_4"
    s = layer.run(rec)["scenarios"]["TYPICAL"]
    assert s["bath_c"] == 180 and s["bases"]["bath_c"] == "SD-020"


def test_unsupported_and_unknown(layer):
    mw = layer.run(_rec("PROC-000007", "HEAT_GENERAL", medium=("MICROWAVE", "PROCESS_DEFINITION")))
    assert mw["status"] == "UNSUPPORTED_MEDIUM" and mw["scenarios"] == {}
    cook = layer.run(_rec("PROC-000031", "HEAT_GENERAL"))
    assert cook["status"] == "SCENARIO_UNKNOWN" and cook["transition_status"] == "unsupported"


def test_no_nutrient_number_is_ever_emitted(layer):
    rec = _rec("PROC-000019", "WET_HEAT", duration=("20", "TEXT_STATED"), temperature_profile=("100", "PHYSICAL_DEFINITION"),
               medium=("WATER", "PROCESS_DEFINITION"), piece_size_class=("DICED", "CUT_HISTORY"))
    text = repr(layer.run(rec)).lower()
    assert "retention" not in text and "vitamin" not in text
