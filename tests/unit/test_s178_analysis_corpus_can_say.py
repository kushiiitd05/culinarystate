"""S178 T4-C04-R1: corpus 'can say' analysis. Synthetic events (invented codes) for the keys; committed output checked against committed censuses."""
from __future__ import annotations

import json
import xml.dom.minidom
from collections import Counter

import pytest

from tests.unit.test_s178_analysis_helpers import ROOT, load_tool

T = load_tool("s178_analysis_corpus_can_say")
R = load_tool("s178_analysis_corpus_can_say_render")


def _inp(status="UNKNOWN", basis=None):
    return {"value": None, "status": status, "basis": basis, "span": None}


def _heat(dur=("UNKNOWN", None), temp=("UNKNOWN", None), gas=None, medium=("MEASURED", "PROCESS_DEFINITION")):
    return {"recipe_id": "R1", "source_family": "FOODCOM", "event_id": "E1", "process_id": "PROC-000001", "family": "DRY_HEAT", "oven_setpoint_code": gas,
            "inputs": {"duration": _inp(*dur), "temperature_profile": _inp(*temp), "medium": _inp(*medium), "lid_state": _inp(), "start_mode": _inp(),
                       "piece_size_class": _inp(), "water_ratio": _inp(), "matrix_class": _inp()}}


def test_heat_keys_joint_and_gas_mark():
    k = Counter(T.heat_event_keys(_heat(dur=("MEASURED", "TEXT_STATED"), temp=("MEASURED", "TEXT_STATED")), None))
    assert k["FOODCOM|DRY_HEAT|PROC-000001|joint|tS|T:TEXT_STATED"] == 1
    k = Counter(T.heat_event_keys(_heat(dur=("RANGE", "TEXT_STATED"), temp=("MEASURED", "CARRIED_SETPOINT")), None))
    assert k["FOODCOM|DRY_HEAT|PROC-000001|dur_range|-"] == 1 and k["FOODCOM|DRY_HEAT|PROC-000001|joint|tS|T:CARRIED_SETPOINT"] == 1
    k = Counter(T.heat_event_keys(_heat(gas="GM4"), None))
    assert k["FOODCOM|DRY_HEAT|PROC-000001|gas_mark|T:UNKNOWN"] == 1 and k["FOODCOM|DRY_HEAT|PROC-000001|joint|tU|T:UNKNOWN"] == 1


def test_heat_keys_l2_unknown_reasons():
    l2 = {"status": "SCENARIO_UNKNOWN", "missing": ["medium", "bath_c"]}
    k = Counter(T.heat_event_keys(_heat(), l2))
    assert k["FOODCOM|DRY_HEAT|PROC-000001|l2missing|medium"] == 1 and k["FOODCOM|DRY_HEAT|PROC-000001|l2missing_set|bath_c+medium"] == 1
    k = Counter(T.heat_event_keys(_heat(), {"status": "SCENARIO_COMPUTED"}))
    assert not [x for x in k if "l2missing" in x]


def test_nonheat_keys():
    r = {"source_family": "FOODCOM", "nh_family": "COOLING", "process_role": "chill", "inputs": {
        "duration": {"status": "BOUND_LOWER", "reason": None}, "medium_temperature": {"status": "UNKNOWN", "reason": "NO_TEMPERATURE_STATED"},
        "piece_size_class": {"status": "UNKNOWN", "reason": "NO_CUT_HISTORY_FOR_LOT"}}}
    k = Counter(T.nh_event_keys(r))
    base = "FOODCOM|COOLING|chill|"
    assert k[base + "joint|tS|T:U"] == 1 and k[base + "temp|UNKNOWN"] == 1
    assert k[base + "reason:medium_temperature|NO_TEMPERATURE_STATED"] == 1 and k[base + "reason:piece_size_class|NO_CUT_HISTORY_FOR_LOT"] == 1


def test_reconciliation_detects_a_mismatch():
    c = Counter({("n", "-"): 3, ("dur", "MEASURED"): 2, ("dur", "UNKNOWN"): 1})
    census = {"heat_events": 3, "input_status": {"duration": {"MEASURED": 2, "UNKNOWN": 1}}}
    assert T.reconcile_heat("X", c, census) == []
    census_bad = {"heat_events": 4, "input_status": {"duration": {"MEASURED": 2, "UNKNOWN": 1}}}
    assert any("heat events" in e for e in T.reconcile_heat("X", c, census_bad))


def test_joint_classes_sum_to_events():
    c = Counter({("n", "-"): 10, ("joint", "tS", "T:TEXT_STATED"): 1, ("joint", "tS", "T:CARRIED_SETPOINT"): 2, ("joint", "tS", "T:UNKNOWN"): 3,
                 ("joint", "tU", "T:PHYSICAL_DEFINITION"): 1, ("joint", "tU", "T:UNKNOWN"): 3})
    j = R.joint_classes(c)
    assert (j["t_and_T_text"], j["t_and_T_carried_or_definition_only"], j["t_only_T_unknown"], j["T_known_t_unknown"], j["neither"]) == (1, 2, 3, 1, 3)


@pytest.mark.parametrize("svg", [
    lambda: R.stacked_bars("t", "s", [("A", [50, 30, 20, 0, 0], "n")], list("abcde"), R.BLUE_RAMP + [R.NEUTRAL]),
    lambda: R.grouped_bars("t", "s", [("m", [10, 20, 30, 40])], list("abcd"), R.CAT),
    lambda: R.hbars("t", "s", [("G", "label", 12.5), ("G", "other", 3.0)]),
])
def test_svg_is_well_formed(svg):
    doc = xml.dom.minidom.parseString(svg())
    assert doc.documentElement.tagName == "svg"
    assert doc.getElementsByTagName("title")[0].firstChild.data == "t"


def test_committed_outputs_reconcile_with_committed_censuses():
    p = ROOT / "reports/s178/analysis/corpus_can_say_v1.json"
    if not p.is_file():
        pytest.skip("analysis not generated in this tree")
    d = json.loads(p.read_text(encoding="utf-8"))
    assert d["reconciliation"]["status"] == "PASS" and not d["reconciliation"]["errors"]
    assert d["contains_text"] is False and d["citable"] is False
    for s, row in d["heat"]["source_level_from_committed_census"].items():
        census = json.loads((ROOT / row["census_path"]).read_text(encoding="utf-8"))
        assert row["heat_events"] == census["heat_events"], s
    fc = d["heat"]["derived_by_source"]["FOODCOM"]
    assert fc["events"] == d["heat"]["source_level_from_committed_census"]["FOODCOM"]["heat_events"] == 1503261
    j = d["heat"]["joint_exclusive_classes_by_source"]["FOODCOM"]
    assert j["n"] == 1503261 and sum(v for k, v in j.items() if k != "n") == j["n"]
    for f in d["figures"]:
        assert (ROOT / f["svg"]).is_file() and (ROOT / f["csv"]).is_file()
