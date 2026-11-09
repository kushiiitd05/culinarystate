"""S178 PHYS2 T4-C02-R2: the physical record schema validator (100 % of fields carry their provenance)."""
from __future__ import annotations

import copy
import importlib.util
import json
from fractions import Fraction

import pytest

from culinarystate.simulation import condition_binding as CB
from culinarystate.simulation import nonheat_binding as NB
from culinarystate.simulation import nonheat_scenario as NS
from culinarystate.simulation import physical_record_schema as PS
from culinarystate.simulation import scenario_layer as SL

ROOT = PS.EC.ROOT
TEXT = ("Preheat the oven to 200C. Dice the carrots. Boil the milk and the sugar for 10 minutes until thick. Bake the carrots for 30 "
        "minutes until golden. Roast the chicken until a thermometer reads 74C. Rest the meat for 10 minutes. Cool on a wire rack. "
        "Soak the beans overnight in cold water, then drain. Store in the fridge for 3 days.")


def _s(v):
    if isinstance(v, Fraction):
        return str(v)
    if isinstance(v, (tuple, list)):
        return [_s(x) for x in v]
    return v


@pytest.fixture(scope="module")
def l1_heat():
    b = CB.Binder.load()
    out = []
    for e in b.bind_text(TEXT)["events"]:
        if e["heat"]:
            out.append({"recipe_id": "R", "event_id": e["event_id"], "process_id": e["process_id"], "family": e["family"],
                        "oven_setpoint_code": e["oven_setpoint_code"], EC_KEY: e[EC_KEY],
                        "inputs": {k: {kk: (_s(vv) if kk == "value" else vv) for kk, vv in v.items()} for k, v in e["inputs"].items()}})
    return out


EC_KEY = PS.EC.BLOCK_KEY


@pytest.fixture(scope="module")
def l1_nh():
    nb = NB.NonHeatBinder.load()
    return [NB.row(e, "X", "R") for e in nb.bind_text(TEXT)["events"]]


def test_l1_records_are_complete(l1_heat, l1_nh):
    t = PS.Tally()
    for r in l1_heat:
        PS.check("L1_HEAT", r, t)
    for r in l1_nh:
        PS.check("L1_NONHEAT", r, t)
    s = PS.summary(t)
    assert s["problems"] == {}
    for kind in ("L1_HEAT", "L1_NONHEAT"):
        assert s["ratios"][kind]["bound_with_basis_over_bound_axes"] == 1.0
        assert s["ratios"][kind]["bound_with_span_id_over_bound_axes"] == 1.0
        assert s["ratios"][kind]["bound_with_row_over_bound_axes"] == 1.0
        assert s["ratios"][kind]["unknown_axes_with_reason_over_unknown_axes"] == 1.0
        assert s["counts"][kind]["bound_axes"] > 10 and s["counts"][kind]["unknown_axes"] > 10


def test_l2_heat_and_nonheat_records_are_complete(l1_heat, l1_nh):
    layer, nl = SL.ScenarioLayer.load(), NS.NonHeatScenario.load()
    t = PS.Tally()
    for r in l1_heat:
        out = layer.run(r)
        PS.check("L2_HEAT", out, t)
    for r in l1_nh:
        PS.check("L2_NONHEAT", nl.run({**r, "recipe_id": "R"}), t)
    s = PS.summary(t)
    assert s["problems"] == {}, s["problems"]
    r = s["ratios"]
    assert r["L2_HEAT"]["input_fields_with_basis_over_input_fields"] == 1.0
    assert r["L2_HEAT"]["output_fields_traceable_to_input_bases_over_output_fields"] == 1.0
    assert r["L2_HEAT"]["basis_entries_valid_over_basis_entries"] == 1.0
    assert r["L2_NONHEAT"]["basis_entries_valid_over_basis_entries"] == 1.0
    assert s["counts"]["L2_HEAT"]["output_fields"] > 10


def _problems(kind, rec):
    return PS.check(kind, rec).problems


def test_validator_catches_l1_defects(l1_heat):
    rec = next(r for r in l1_heat if r["process_id"] == "PROC-000001" and r["inputs"]["duration"]["status"] != "UNKNOWN")

    def mut(fn):
        c = copy.deepcopy(rec)
        fn(c)
        return _problems("L1_HEAT", c)
    assert mut(lambda c: c["inputs"]["duration"].update(basis=None))
    assert mut(lambda c: c["inputs"]["duration"].update(span_id=None))
    assert mut(lambda c: c["inputs"]["duration"].update(span_id="X:1"))
    assert mut(lambda c: c["inputs"]["duration"].update(row=None))
    assert mut(lambda c: c["inputs"]["duration"].update(basis="INVENTED"))
    assert mut(lambda c: c["inputs"]["water_ratio"].pop("reason"))
    assert mut(lambda c: c["inputs"].update(endpoint={"value": "COLOUR", "status": "QUALITATIVE", "basis": "TEXT_CUE", "span": [0, 1],
                                                    "span_id": "C:0-1", "row": "x"}))  # an endpoint field among the inputs
    assert mut(lambda c: c.pop(EC_KEY))
    assert mut(lambda c: c[EC_KEY]["cues"].append({"class": "NOT_A_CLASS", "span": [0, 1]}))
    assert not _problems("L1_HEAT", rec)


def test_validator_catches_l2_defects(l1_heat):
    layer = SL.ScenarioLayer.load()
    out = next(o for o in (layer.run(r) for r in l1_heat) if o["status"] == "SCENARIO_COMPUTED"
               and o["scenarios"]["TYPICAL"]["core_end_c"] is not None)
    assert not _problems("L2_HEAT", out)

    def mut(fn):
        c = copy.deepcopy(out)
        fn(c)
        return _problems("L2_HEAT", c)
    assert mut(lambda c: c["scenarios"]["TYPICAL"]["bases"].pop("bath_c"))
    assert mut(lambda c: c["scenarios"]["TYPICAL"]["bases"].update(initial_c="MADE_UP"))
    assert mut(lambda c: c["scenarios"]["TYPICAL"]["bases"].pop("k"))
    assert mut(lambda c: c["scenarios"]["TYPICAL"].update(invented_field=1.0))
    assert mut(lambda c: c.pop("l1_provenance"))
    assert mut(lambda c: c.update(labels=["SCENARIO"]))
    assert mut(lambda c: c["l1_provenance"].pop("duration", None) or c["l1_provenance"].pop("temperature_profile"))


def test_unknown_and_unsupported_l2_records_still_carry_the_provenance_block(l1_heat):
    layer = SL.ScenarioLayer.load()
    base = next(r for r in l1_heat if r["process_id"] == "PROC-000001")
    micro = copy.deepcopy(base)
    micro["inputs"]["medium"] = {**micro["inputs"]["medium"], "value": "MICROWAVE"}
    nomedium = copy.deepcopy(base)
    nomedium["inputs"]["medium"] = {"value": None, "status": "UNKNOWN", "basis": None, "span": None, "reason": "NO_MEDIUM_IN_PROCESS_MAP"}
    outs = [layer.run(micro), layer.run(nomedium)]
    assert [o["status"] for o in outs] == ["UNSUPPORTED_MEDIUM", "SCENARIO_UNKNOWN"]
    t = PS.Tally()
    for o in outs:
        assert o["l1_provenance"]["duration"]["span_id"]  # what was read is on record even when nothing was computed
        PS.check("L2_HEAT", o, t)
    assert t.problems == {}


def test_tool_counts_only_report_and_exit_code(tmp_path, l1_heat):
    spec = importlib.util.spec_from_file_location("s178_phys_schema_validate", ROOT / "tools/s178_phys_schema_validate.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    d = tmp_path / "L1"
    d.mkdir()
    (d / "part-00000.jsonl").write_text("\n".join(json.dumps(r) for r in l1_heat) + "\n", encoding="utf-8")
    out = tmp_path / "rep.json"
    assert mod.main(["--kind", "L1_HEAT", "--out", str(out), str(d)]) == 0
    rep = json.loads(out.read_text())
    assert rep["problems"] == {} and rep["contains_text"] is False and rep["counts"]["L1_HEAT"]["records"] == len(l1_heat)
    with pytest.raises(SystemExit):
        mod.main(["--kind", "L1_HEAT", "--out", str(out), str(d)])  # never overwrites
    bad = copy.deepcopy(l1_heat)
    bad[0]["inputs"]["duration"]["basis"] = None
    bad[0]["inputs"]["duration"]["status"] = "MEASURED"
    bad[0]["inputs"]["duration"]["value"] = "1"
    (d / "part-00000.jsonl").write_text("\n".join(json.dumps(r) for r in bad) + "\n", encoding="utf-8")
    out2 = tmp_path / "rep2.json"
    assert mod.main(["--kind", "L1_HEAT", "--out", str(out2), str(d)]) == 1


def test_schema_constants_match_the_binders():
    assert set(PS.L1_BASES) >= {"TEXT_STATED", "CARRIED_SETPOINT", "PHYSICAL_DEFINITION", "PROCESS_DEFINITION", "CUE", "CUT_HISTORY",
                                "FOOD_GROUP", "TEXT_CUE", "LINEAGE", "ORDER_ADJACENT", "LINEAGE_AND_STATED_DURATIONS"}
    assert set(NS.BRACKETS) == {"GENTLE", "TYPICAL", "INTENSE"}
    assert set(PS.NONHEAT_OUTPUTS) == set(NB.NH_FAMILIES) - {"STORAGE"} | {"STORAGE"}
