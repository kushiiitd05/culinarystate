"""S178 PHYS2: the run-tool options (v03 -> v04 tags), the sensitivity report (T4-C05-R1), the stated-liquid before / after report and the
v03 -> v04 comparison. Synthetic records only."""
from __future__ import annotations

import copy
import importlib.util
import json
import sys
from pathlib import Path

import pytest

from culinarystate.simulation import scenario_layer as SL
from tests.unit.test_s176_phys_cap import _rec

ROOT = Path(__file__).resolve().parents[2]


def _load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / f"tools/{name}.py")
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def heat_tool():
    return _load("scenario_layer_run")


@pytest.fixture(scope="module")
def sens():
    return _load("s178_phys_sensitivity")


@pytest.fixture(scope="module")
def stated():
    return _load("s178_phys_stated_liquid_report")


@pytest.fixture(scope="module")
def cmp_tool():
    return _load("s178_phys_v04_comparison")


def _write(d: Path, recs, name="part-0.jsonl"):
    d.mkdir(parents=True, exist_ok=True)
    (d / name).write_text("".join(json.dumps(r) + "\n" for r in recs))


def _read(d: Path):
    return [json.loads(x) for f in sorted(d.glob("*.jsonl")) for x in f.read_text().splitlines()]


# ------------------------------------------------------------------------------------------------ run-tool tags
def test_heat_tool_names_the_comparison_block_by_tag_and_counts_bath_changes(heat_tool, tmp_path):
    l1 = tmp_path / "l1"
    recs = [_rec("PROC-000019", "WATER", 20, 160), _rec("PROC-000001", "OVEN_AIR", 30, 200)]
    recs[0]["inputs"]["temperature_profile"]["row"] = "CB_RULE:TEMPERATURE_OWN_CLAUSE"  # S178 FIX-PHYS: owned, but dilute (Q1)
    _write(l1, recs)
    first = tmp_path / "a.json"
    assert heat_tool.main(["--l1", str(l1), "--l2", str(tmp_path / "l2a"), "--out", str(first)]) == 0
    prev = []
    for r in _read(tmp_path / "l2a"):
        o = copy.deepcopy(r)
        o["version"] = SL.VERSION_V03
        if o["process_id"] == "PROC-000019":  # 0.3.0 had taken the oven temperature (176.7) as the boil's stated temperature
            for s in o["scenarios"].values():
                s["bath_c"] = 176.7
                s["bases"]["bath_c"] = "L1:TEXT_STATED"
        prev.append(o)
    _write(tmp_path / "prev", prev)
    second = tmp_path / "b.json"
    assert heat_tool.main(["--l1", str(l1), "--l2", str(tmp_path / "l2b"), "--out", str(second), "--compare-prev-l2", str(tmp_path / "prev"),
                           "--prev-tag", "v03", "--tag", "v04", "--prev-layer-version", SL.VERSION_V03]) == 0
    rep = json.loads(second.read_text())
    assert "v02_to_v03" not in rep and rep["v03_to_v04"]["previous_layer_version"] == SL.VERSION_V03
    c = rep["v03_to_v04"]["counts"]
    assert c["events"] == 2 and c["bath_c_changed"]["TYPICAL"] == 1 and "ALIGNMENT_ERROR" not in c
    c2 = rep["counts"]
    # S178 FIX-PHYS (Q1): an owned 160 C boil with no sugar member, syrup or pressure cue is not lifted (was lifted at 0.4.0)
    assert "stated_liquid_typical_by_stated_c_and_member" not in c2
    assert c2["fixphys_flag_typical"]["STATED_LIQUID_T_ABOVE_TBOIL_NOT_LIFTED_DILUTE"] == 1
    assert rep["layer_version"] == SL.VERSION
    for r in _read(tmp_path / "l2b"):
        assert "l1_provenance" in r


# ------------------------------------------------------------------------------------------------ sensitivity
def _bracket(bath, dur, core, vavg, mins, cap=True, surface="SURFACE_WET_AT_TBOIL", dose=1.0):
    return {"bath_c": bath, "duration_min": dur, "initial_c": 20.0, "core_end_c": core, "volume_avg_end_c": vavg,
            "core_minutes_above_70": mins, "core_cook_value_min": dose, "zone_mean_cook_value_min": dose,
            "flags": ["EVAPORATION_CAP_APPLIED"] if cap else [], "surface_state": surface,
            "bases": {"bath_c": "SD-001", "duration_min": "KGE-000001", "initial_c": "SD-010", "k": "SD-020", "alpha": "SD-021"}}


def _l2(pid, g, t, i, status="SCENARIO_COMPUTED", **extra):
    return {"recipe_id": "R", "event_id": "E", "process_id": pid, "version": "scenario-layer-L2-0.4.0-draft", "status": status,
            "scenarios": {"GENTLE": g, "TYPICAL": t, "INTENSE": i}, **extra}


def test_verdict_and_family_flags(sens):
    assert sens.verdict([True, True, True]) == "ROBUST_YES" and sens.verdict([False] * 3) == "ROBUST_NO"
    assert sens.verdict([False, True, True]) == "FRAGILE" and sens.verdict([True, None, True]) is None and sens.verdict([True]) is None


def test_sensitivity_report_on_synthetic_records(sens, tmp_path):
    heat = tmp_path / "heat"
    recs = [  # PROC-000001 bake = DRY_HEAT, PROC-000019 boil = WET_HEAT, PROC-000031 cook = HEAT_GENERAL
        _l2("PROC-000001", _bracket(160, 20, 40, 60, 0), _bracket(200, 30, 80, 90, 10), _bracket(220, 40, 150, 140, 30)),  # fragile
        _l2("PROC-000001", _bracket(200, 30, 90, 95, 10), _bracket(200, 30, 99, 99, 20), _bracket(200, 30, 100, 100, 30)),  # robust yes
        _l2("PROC-000001", _bracket(200, 5, 20, 25, 0), _bracket(200, 5, 30, 35, 0), _bracket(200, 5, 40, 45, 0)),  # robust no
        _l2("PROC-000019", _bracket(100, 10, 100, 100, 10, cap=False), _bracket(100, 10, 100, 100, 10, cap=False),
            _bracket(100, 10, 100, 100, 10, cap=False)),
        _l2("PROC-000031", {}, {}, {}, status="SCENARIO_UNKNOWN", missing=["bath_c", "medium"]),
        _l2("PROC-000031", {}, {}, {}, status="SCENARIO_UNKNOWN", missing=["bath_c", "medium"]),
        _l2("PROC-000007", {}, {}, {}, status="UNSUPPORTED_MEDIUM", medium="MICROWAVE")]
    _write(heat, recs)
    nh = tmp_path / "nh"
    cool = lambda a, b, c: {"GENTLE": {"core_end_c": a, "duration_min": 10.0, "bases": {"duration_min": "KGE-000002"}, "flags": []},  # noqa: E731
                            "TYPICAL": {"core_end_c": b, "duration_min": 10.0, "bases": {"duration_min": "KGE-000002"}, "flags": []},
                            "INTENSE": {"core_end_c": c, "duration_min": 10.0, "bases": {"duration_min": "KGE-000002"}, "flags": []}}
    nrecs = [{"recipe_id": "R", "event_id": "E", "process_id": "PROC-000038", "nh_family": "COOLING", "version": "nonheat-scenario-L2-0.4.0-draft",
              "status": "SCENARIO_COMPUTED", "scenarios": cool(3.0, 4.0, 8.0)},
             {"recipe_id": "R", "event_id": "E", "process_id": "PROC-000038", "nh_family": "COOLING", "version": "nonheat-scenario-L2-0.4.0-draft",
              "status": "SCENARIO_COMPUTED", "scenarios": cool(70.0, 65.0, 62.0)},
             {"recipe_id": "R", "event_id": "E", "process_id": "PROC-000039", "nh_family": "COOLING", "version": "nonheat-scenario-L2-0.4.0-draft",
              "status": "SCENARIO_UNKNOWN", "scenarios": {}, "missing": ["half_thickness"]}]
    _write(nh, nrecs)
    out, md = tmp_path / "s.json", tmp_path / "s.md"
    assert sens.main(["--heat-l2", str(heat), "--nonheat-l2", str(nh), "--out", str(out), "--out-md", str(md), "--workers", "2"]) == 0
    rep = json.loads(out.read_text())
    assert rep["contains_text"] is False and rep["fragile_share_threshold_proposed"] == 0.1
    dry = rep["heat"]["DRY_HEAT"]
    assert dry["events"] == 3 and dry["computed"] == 3 and dry["core_computed"] == 3
    c70 = dry["conclusions"]["core_reaches_70c"]
    assert (c70["robust_yes"], c70["robust_no"], c70["fragile"], c70["events_evaluated"]) == (1, 1, 1, 3) and c70["flag"] == "FRAGILE"
    assert dry["conclusions"]["evaporation_cap_binds"]["flag"] == "ROBUST"
    assert dry["bracket_width"]["bath_c"]["p50"] == 0.0 and dry["bracket_width"]["bath_c"]["max"] == 60.0
    assert dry["bracket_width"]["core_end_c"]["n"] == 3 and dry["bracket_width"]["core_end_c"]["max"] == 110.0
    wet = rep["heat"]["WET_HEAT"]["conclusions"]
    assert wet["evaporation_cap_binds"]["robust_no"] == 1 and wet["core_reaches_70c"]["flag"] == "ROBUST"
    gen = rep["heat"]["HEAT_GENERAL"]
    assert gen["status"]["SCENARIO_UNKNOWN"] == 2 and gen["scenario_unknown_missing_sets"] == {"bath_c__medium": 2}
    assert gen["scenario_unknown_missing_each_input"] == {"bath_c": 2, "medium": 2}
    assert rep["heat"]["HEAT_GENERAL"]["conclusions"] == {}
    cool_r = rep["nonheat"]["COOLING"]
    assert cool_r["events"] == 3 and cool_r["computed"] == 2 and cool_r["scenario_unknown_missing_sets"] == {"half_thickness": 1}
    assert cool_r["conclusions"]["core_end_at_or_below_5c"]["fragile"] == 1 and cool_r["conclusions"]["core_end_at_or_below_5c"]["robust_no"] == 1
    assert cool_r["conclusions"]["core_end_at_or_below_60c"]["robust_no"] == 1
    assert cool_r["bracket_width"]["INPUT_duration_min"]["share_zero"] == 1.0
    assert cool_r["bracket_width"]["OUTPUT_core_end_c"]["n"] == 2 and cool_r["bracket_width"]["OUTPUT_core_end_c"]["max"] == 8.0
    text = md.read_text()
    assert "ROBUST" in text and "FRAGILE" in text and "SCENARIO_UNKNOWN" in text
    with pytest.raises(SystemExit):
        sens.main(["--heat-l2", str(heat), "--out", str(out), "--out-md", str(tmp_path / "x.md")])  # never overwrites


def test_sensitivity_input_basis_split(sens, tmp_path):
    heat = tmp_path / "heat"
    a = _bracket(200, 30, 90, 95, 10)
    for b in (a,):
        b["bases"]["bath_c"], b["bases"]["duration_min"] = "L1:TEXT_STATED", "L1:TEXT_STATED"
    _write(heat, [_l2("PROC-000001", copy.deepcopy(a), copy.deepcopy(a), copy.deepcopy(a))])
    rep = sens.heat_report([sens.heat_file(str(heat / "part-0.jsonl"))])
    bb = rep["DRY_HEAT"]["by_input_basis"]["bath_TEXT_STATED_duration_TEXT_STATED"]  # S178 FIX-PHYS m8: basis kinds split
    assert bb["computed"] == 1 and bb["core_reaches_70c_fragile_share"] == 0.0 and bb["core_end_c_width"]["p50"] == 0.0


# ------------------------------------------------------------------------------------------------ stated-liquid report
def _l1(rid, eid, pid, medium, temp, basis="TEXT_STATED", groups=None, note=None, ambient=False):
    r = _rec(pid, medium, 10, temp, temp_basis=basis)
    r["recipe_id"], r["event_id"] = rid, eid
    if groups:
        r["inputs"]["matrix_groups"] = {"value": groups, "status": "MEASURED", "basis": "FOOD_GROUP", "span": None}
    if note:
        r["temperature_note"] = [{"legacy_span": [1, 2], "now": note}]
    if ambient:
        r["inputs"]["ambient_temperature"] = {"value": "176", "status": "MEASURED", "basis": "TEXT_STATED", "span": None}
    return r


def test_stated_liquid_report_joins_before_and_after(stated, heat_tool, tmp_path):
    before = [_l1("A", "E1", "PROC-000019", "WATER", 176), _l1("B", "E1", "PROC-000019", "WATER", 204), _l1("C", "E1", "PROC-000019", "WATER", 116),
              _l1("D", "E1", "PROC-000019", "WATER", 116), _l1("E", "E1", "PROC-000001", "OVEN_AIR", 200)]
    after = [_l1("A", "E1", "PROC-000019", "WATER", 100, "PHYSICAL_DEFINITION", note="OWNED_BY_OTHER_EVENT"),
             _l1("B", "E1", "PROC-000019", "WATER", None, note="OVEN_OIL_OR_HEAT_LEVEL_CUE_TEMPERATURE_OF_LIQUID_STEP", ambient=True),
             _l1("C", "E1", "PROC-000019", "WATER", 116, groups=["SWEETENER"]),
             _l1("D", "E1", "PROC-000019", "WATER", 116, groups=["VEGETABLE"]), _l1("E", "E1", "PROC-000001", "OVEN_AIR", 200)]
    d = {n: tmp_path / n for n in ("b1", "a1", "b2", "a2")}
    _write(d["b1"], before)
    _write(d["a1"], after)
    assert heat_tool.main(["--l1", str(d["b1"]), "--l2", str(d["b2"]), "--out", str(tmp_path / "x.json")]) == 0
    assert heat_tool.main(["--l1", str(d["a1"]), "--l2", str(d["a2"]), "--out", str(tmp_path / "y.json")]) == 0
    out, md = tmp_path / "o.json", tmp_path / "o.md"
    assert stated.main(["--family", "TEST", "--l1-before", str(d["b1"]), "--l1-after", str(d["a1"]), "--l2-before", str(d["b2"]),
                        "--l2-after", str(d["a2"]), "--out", str(out), "--out-md", str(md)]) == 0
    rep = json.loads(out.read_text())["families"]["TEST"]
    assert rep["l1_events_before"] == 4  # the oven event is not aqueous
    t = rep["l1_old_to_new"]["old_bucket_by_new_category"]
    assert t["ABOVE_150"] == {"NOW_BOIL_BY_PHYSICAL_DEFINITION": 1, "NOW_UNKNOWN_TEMPERATURE": 1}
    assert t["105_TO_120"] == {"STILL_STATED_AQUEOUS_ABOVE_100": 2}
    assert rep["l1_old_to_new"]["remaining_by_solute_rich_member"]["105_TO_120"] == {"SOLUTE_RICH_MEMBER": 1, "NO_SOLUTE_RICH_MEMBER": 1}
    assert rep["l1_old_to_new"]["reason_of_change"]["ABOVE_150"]["OWNED_BY_OTHER_EVENT"] == 1
    assert rep["l1_old_to_new"]["ambient_temperature_kept"]["ABOVE_150"] == 1
    l2 = rep["l2"]
    # S178 FIX-PHYS: both blocks are now produced by Layer 2 0.5.0 (the Q1 gate): the synthetic records carry no Layer 1 row, so a
    # stated value is not OWNED and lifts nothing; the SWEETENER-only lot is uncapped (dry class)
    assert l2["before_l2_0_3_0"]["counts"]["not_lifted"]["ABOVE_150"] == {"STATED_LIQUID_T_ABOVE_TBOIL_NOT_LIFTED_NOT_OWNED": 2}
    assert "lifted" not in l2["after_l2_0_4_0"]["counts"]
    assert l2["after_l2_0_4_0"]["counts"]["not_lifted"] == {"105_TO_120": {"STATED_LIQUID_T_ABOVE_TBOIL_NOT_LIFTED_NOT_OWNED": 1}}
    assert l2["before_l2_0_3_0"]["max_core_end_c_of_a_lifted_event_by_bucket"] == {}
    assert "diagnosis" in md.read_text().lower() or "Stated-liquid" in md.read_text()


# ------------------------------------------------------------------------------------------------ comparison
def test_comparison_helpers(cmp_tool):
    a = {"recipes_sampled": 10, "heat_events": 100, "driver_ready_events": 5, "driver_bounded_events": 6, "contract_bindings": 9,
         "gas_mark_only_events": 0, "input_basis": {"temperature_profile": {"TEXT_STATED": 10, "PHYSICAL_DEFINITION": 20}},
         "input_status": {"matrix_class": {"MEASURED": 4, "UNKNOWN": 96}}}
    b = {**a, "driver_ready_events": 4, "input_basis": {"temperature_profile": {"TEXT_STATED": 7, "PHYSICAL_DEFINITION": 23, "CARRIED_SETPOINT": 1}},
         "matrix_groups": {"events_by_member_group_count": {"1": 3}, "events_without_any_food_group": 2}}
    r = cmp_tool.heat_l1(a, b)
    assert r["driver_ready_events"] == {"before": 5, "after": 4, "delta": -1}
    tb = r["input_basis"]["temperature_profile"]
    assert tb["TEXT_STATED"]["delta"] == -3 and tb["CARRIED_SETPOINT"] == {"before": 0, "after": 1, "delta": 1}
    assert r["new_in_v04"]["matrix_groups_events_by_member_count"] == {"1": 3}
    assert cmp_tool._pair("x", "y")["delta"] is None
    sup = cmp_tool.superseded()
    assert all(s["status"] == "SUPERSEDED_BY_S178_v04" for s in sup)


def test_comparison_helpers_accept_a_family_without_events(cmp_tool):
    """TASTESET has no step lists: its reports hold empty count blocks."""
    empty_l2 = {"layer_version": "x", "counts": {}, "v03_to_v04": {"counts": {}}}
    r = cmp_tool.heat_l2(empty_l2, empty_l2)
    assert r["status"] == {} and r["stated_liquid_lifted_typical"] == {"before": 0, "after": 0, "delta": 0}
    n2 = {"layer_version": "x", "counts": {"events_by_family": {}, "l2_driver_computed_by_family": {}, "l2_qualitative_or_conditions_by_family": {}},
          "v03_to_v04": {"counts": {}}}
    assert cmp_tool.nonheat_l2(n2, n2)["events_whose_status_changed_by_family"] == {}


def test_comparison_tool_runs_on_the_committed_reports_when_present(cmp_tool, tmp_path):
    needed = [ROOT / "reports/step26" / n.format(f=f) for pair in cmp_tool.SOURCES.values() for n in pair for f in cmp_tool.FAMILIES]
    if not all(p.exists() for p in needed):
        pytest.skip("the S178 v04 run reports are not present")
    out, md = tmp_path / "c.json", tmp_path / "c.md"
    assert cmp_tool.main(["--out", str(out), "--out-md", str(md)]) == 0
    rep = json.loads(out.read_text())
    assert set(rep["families"]) == set(cmp_tool.FAMILIES) and rep["contains_text"] is False
    assert "SUPERSEDED outputs" in md.read_text()


# ------------------------------------------------------------------------------------------------ endpoint report
def test_endpoint_report_sums_census_blocks(tmp_path):
    ep = _load("s178_phys_endpoint_report")

    def block(n, w, cls):
        return {"extractor_version": "x", "heat_events": n, "heat_events_with_cue": w, "cues_per_event": {"0": n - w, "1": w},
                "events_with_cue_by_family": {"DRY_HEAT": w}, "stopping_criterion_class": {"COLOUR": w}, "cue_class": cls, "cue_trigger": {"UNTIL": w},
                "cue_class_by_family": {"DRY_HEAT": cls}, "cue_and_duration_by_family": {"DRY_HEAT": 1},
                "cue_without_duration_by_family": {"DRY_HEAT": w - 1}, "cue_without_temperature_by_family": {"DRY_HEAT": 0}, "stored_outside_inputs": True}
    paths = []
    for fam, b in (("A", block(10, 4, {"COLOUR": 3, "UNTIL_CLAUSE_UNCLASSIFIED": 1})), ("B", block(30, 6, {"COLOUR": 6}))):
        p = tmp_path / f"{fam}.json"
        p.write_text(json.dumps({"endpoint_cues": b}))
        paths.append(f"{fam}={p}")
    out, md = tmp_path / "o.json", tmp_path / "o.md"
    assert ep.main(["--census", *paths, "--out", str(out), "--out-md", str(md)]) == 0
    rep = json.loads(out.read_text())["summary"]
    assert rep["all_non_bbc_families"]["heat_events"] == 40 and rep["all_non_bbc_families"]["heat_events_with_cue"] == 10
    assert rep["all_non_bbc_families"]["share_with_cue"] == 0.25 and rep["all_non_bbc_families"]["cue_class"] == {"COLOUR": 9, "UNTIL_CLAUSE_UNCLASSIFIED": 1}
    assert rep["by_source_family"]["A"]["unclassified_until_clause_share_of_cues"] == 0.25
    assert "10 with at least one endpoint cue" in md.read_text()
    with pytest.raises(SystemExit):
        ep.main(["--census", *paths, "--out", str(out), "--out-md", str(md)])


# ------------------------------------------------------------------------------------------------ non-heat tool tags
def test_nonheat_tool_names_the_comparison_block_by_tag_and_records_validate(tmp_path):
    from culinarystate.simulation import physical_record_schema as PS
    nh = _load("nonheat_layer_run")

    def source(families, root):
        for i in range(4):
            yield {"recipe_id": f"SYN-{i}", "source_family": families[0],
                   "steps": ["Dice the carrots.", "Boil the carrots for 10 minutes.", "Rest the carrots for 5 minutes. Cool on a wire rack.",
                             "Marinate the chicken in vinegar for 2 hours.", "Slice the cucumber. Brine the cucumber in a 5% brine for 6 hours.",
                             "Prove the dough for 2 hours."]}
    argv = ["--seed", "7", "--sample-size", "4", "--workers", "1", "--families", "WIKIBOOKS", "--no-baseline-check", "--root", str(ROOT),
            "--l1-out", str(tmp_path / "a_l1.json"), "--l2-out", str(tmp_path / "a_l2.json"),
            "--l1-records-dir", str(tmp_path / "r1"), "--l2-records-dir", str(tmp_path / "r2")]
    assert nh.main(argv, record_source=source) == 0
    t = PS.Tally()
    for f in sorted((tmp_path / "r1").glob("*.jsonl")):
        for line in f.read_text().splitlines():
            PS.check("L1_NONHEAT", json.loads(line), t)
    for f in sorted((tmp_path / "r2").glob("*.jsonl")):
        for line in f.read_text().splitlines():
            PS.check("L2_NONHEAT", json.loads(line), t)
    assert t.problems == {} and t[("L1_NONHEAT", "bound_axes")] > 0 and t[("L2_NONHEAT", "records")] > 0
    argv2 = ["--seed", "7", "--l2-only", "--workers", "1", "--families", "WIKIBOOKS", "--no-baseline-check", "--root", str(ROOT),
             "--l2-out", str(tmp_path / "b_l2.json"), "--l1-records-dir", str(tmp_path / "r1"), "--l2-records-dir", str(tmp_path / "r2b"),
             "--compare-prev-l2", str(tmp_path / "r2"), "--prev-tag", "v03", "--tag", "v04", "--prev-layer-version", "nonheat-scenario-L2-0.3.0-draft"]
    assert nh.main(argv2) == 0
    rep = json.loads((tmp_path / "b_l2.json").read_text())
    assert "v02_to_v03" not in rep and rep["v03_to_v04"]["previous_layer_version"] == "nonheat-scenario-L2-0.3.0-draft"
    c = rep["v03_to_v04"]["counts"]
    assert "ALIGNMENT_ERROR" not in c and all(k.split("__TO__")[0] == k.split("__TO__")[1] for d in c["status"].values() for k in d)
