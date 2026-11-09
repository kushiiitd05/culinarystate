"""S177 SCIFIX-PHYS rows 4 and 5 (FINAL-SCI): F0 scope and acid marinades in the non-heat Layer 2.

Row 4: F0 (z = 10 C, T_ref = 121.1 C) is the low-acid canning / retort reference. Layer 2 computes it only for PROC-000132 with a
pressure canner, names the field ``f0_upper_bound_at_medium_t_min`` (no come-up time, no cold-spot lag: an upper bound on
lethality) and takes the canner temperature from the saturation rows (PC-002), not from the retired NH-010. Pasteurise, sterilise,
boiling-water-bath and oven canning are QUALITATIVE_FLAGS_ONLY with F0_NOT_APPLICABLE_LOW_ACID_RETORT_ONLY.
Row 5: vinegar and citrus-juice media are QUALITATIVE (PH_FALLS), never a Fickian uptake fraction; NH-041 is retired.
"""
from __future__ import annotations

import copy
import csv
import math
from pathlib import Path

import pytest

from culinarystate.simulation import nonheat_binding as NB
from culinarystate.simulation import nonheat_drivers as ND
from culinarystate.simulation import nonheat_scenario as NS

ROOT = Path(__file__).resolve().parents[2]
B = ("GENTLE", "TYPICAL", "INTENSE")


@pytest.fixture(scope="module")
def binder():
    return NB.NonHeatBinder.load()


@pytest.fixture(scope="module")
def layer():
    return NS.NonHeatScenario.load()


def l1(binder, text, role, n=0):
    e = [x for x in binder.bind_text(text)["events"] if x["process_role"] == role][n]
    return {**e, "recipe_id": "R"}


def f0(minutes, t):
    return minutes * 10 ** ((t - 121.1) / 10.0)


# ------------------------------------------------------------------------------------------------ F0: pressure canning only
def test_pressure_canning_gets_an_f0_upper_bound_with_the_saturation_temperatures(layer, binder):
    r = l1(binder, "Canning the beans in a pressure canner for 30 minutes.", "can")
    assert r["process_id"] == "PROC-000132" and r["inputs"]["environment"]["value"] == "PRESSURE_CANNER"
    out = layer.run(r)
    assert out["status"] == "SCENARIO_COMPUTED"
    want = {"GENTLE": 108.4, "TYPICAL": 115.2, "INTENSE": 121.0}  # PC-002 (5 / 10 / 15 psig), not NH-010's 110 / 116 / 121
    for b in B:
        s = out["scenarios"][b]
        assert s["medium_c"] == want[b] and s["bases"]["medium_c"] == "PC-002"
        assert s["f0_upper_bound_at_medium_t_min"] == pytest.approx(round(f0(30.0, want[b]), 6), abs=1e-6)
        assert "f0_min" not in s
        assert "F0_UPPER_BOUND_AT_MEDIUM_T_NO_COMEUP_NO_COLD_SPOT_LAG" in s["flags"] and "LOW_ACID_FOOD_ASSUMED_NOT_CHECKED" in s["flags"]
        assert "EQUIVALENT_MINUTES_ONLY_NO_ORGANISM_CLAIM" in s["flags"] and "F0_NOT_APPLICABLE_LOW_ACID_RETORT_ONLY" not in s["flags"]
    vals = [out["scenarios"][b]["f0_upper_bound_at_medium_t_min"] for b in B]
    assert vals == sorted(vals)  # bracket order GENTLE <= TYPICAL <= INTENSE


def test_a_stated_canner_temperature_is_kept(layer, binder):
    out = layer.run(l1(binder, "Canning the beans in a pressure canner at 118C for 30 minutes.", "can"))
    assert out["status"] == "SCENARIO_COMPUTED"
    for b in B:
        s = out["scenarios"][b]
        assert s["medium_c"] == 118.0 and s["bases"]["medium_c"] == "L1:TEXT_STATED"
        assert s["f0_upper_bound_at_medium_t_min"] == pytest.approx(round(f0(30.0, 118.0), 6), abs=1e-6)


def test_oven_canning_is_not_a_valid_process_and_gets_no_f0(layer, binder):
    r = l1(binder, "Canning the tomatoes in a 121C oven for 60 minutes.", "can")
    assert r["inputs"]["environment"]["value"] == "OVEN"
    out = layer.run(r)
    assert out["status"] == "QUALITATIVE_FLAGS_ONLY" and out["transition_status"] == "physically_possible"
    for b in B:
        s = out["scenarios"][b]
        assert "f0_upper_bound_at_medium_t_min" not in s and "f0_min" not in s
        assert "F0_NOT_APPLICABLE_LOW_ACID_RETORT_ONLY" in s["flags"] and "OVEN_CANNING_NOT_A_VALID_PROCESS" in s["flags"]
        assert s["medium_c"] == 121.0 and s["bases"]["medium_c"] == "L1:TEXT_STATED"  # the stated conditions are kept
    # the value the 0.2.0 code printed for this method: not safe, and no longer produced
    assert f0(60.0, 121.0) == pytest.approx(58.6, abs=0.1)  # FINAL-SCI row 4: 'F0 about 58 for a method that is not safe'


def test_boiling_water_bath_canning_and_pasteurise_are_qualitative_without_the_oven_flag(layer, binder):
    bath = layer.run(l1(binder, "Canning the jam in a boiling water bath for 10 minutes.", "can"))
    assert bath["status"] == "QUALITATIVE_FLAGS_ONLY"
    s = bath["scenarios"]["TYPICAL"]
    assert s["medium_c"] == 100.0 and s["bases"]["medium_c"] == "L1:PHYSICAL_DEFINITION"
    assert "F0_NOT_APPLICABLE_LOW_ACID_RETORT_ONLY" in s["flags"] and "OVEN_CANNING_NOT_A_VALID_PROCESS" not in s["flags"]
    pas = layer.run(l1(binder, "Pasteurise the juice at 90C for 20 minutes.", "pasteurise"))
    assert pas["status"] == "QUALITATIVE_FLAGS_ONLY"
    assert all("F0_NOT_APPLICABLE_LOW_ACID_RETORT_ONLY" in pas["scenarios"][b]["flags"] for b in B)
    assert all("f0_upper_bound_at_medium_t_min" not in pas["scenarios"][b] for b in B)


def test_a_sterilise_verb_in_a_pressure_canner_is_not_the_canning_step_and_gets_no_f0(layer, binder):
    r = l1(binder, "Sterilise the beans in a pressure canner for 20 minutes.", "sterilise")
    assert r["process_id"] == "PROC-000131" and r["inputs"]["environment"]["value"] == "PRESSURE_CANNER"
    out = layer.run(r)
    assert out["status"] == "QUALITATIVE_FLAGS_ONLY"
    s = out["scenarios"]["TYPICAL"]
    assert "F0_NOT_APPLICABLE_LOW_ACID_RETORT_ONLY" in s["flags"] and "f0_upper_bound_at_medium_t_min" not in s
    assert s["bases"]["medium_c"] == "PC-002"  # the canner steam temperature is still a condition, from the saturation rows


def test_missing_conditions_stay_unknown_not_zero(layer, binder):
    out = layer.run(l1(binder, "Pasteurise the juice.", "pasteurise"))
    assert out["status"] == "SCENARIO_UNKNOWN" and "medium_temperature" in out["missing"]
    unk = copy.deepcopy(l1(binder, "Canning the beans in a pressure canner for 30 minutes.", "can"))
    unk["inputs"]["duration"] = {"value": None, "status": "UNKNOWN", "basis": None, "span": None}
    o = layer.run(unk)
    assert o["status"] in ("SCENARIO_UNKNOWN", "SCENARIO_COMPUTED")
    if o["status"] == "SCENARIO_UNKNOWN":
        assert o["missing"] == ["duration_min"]


def test_f0_function_scope_is_documented_and_unchanged():
    assert ND.f0_minutes(minutes=10.0, t_c=121.1, t_ref_c=121.1, z_c=10.0) == pytest.approx(10.0)
    assert "UPPER BOUND" in ND.f0_minutes.__doc__ and "pressure canning" in ND.f0_minutes.__doc__


def test_preservation_order_check_uses_the_new_field_name():
    assert ("f0_upper_bound_at_medium_t_min", +1) in NS.ORDER_CHECKS["PRESERVATION"]
    assert all(k != "f0_min" for k, _ in NS.ORDER_CHECKS["PRESERVATION"])
    from collections import Counter
    c = Counter()
    layer = NS.NonHeatScenario.load()
    b = NB.NonHeatBinder.load()
    NS.count_row(layer.run(l1(b, "Canning the beans in a pressure canner for 30 minutes.", "can") | {"nh_family": "PRESERVATION"}), c)
    assert c[("order", "PRESERVATION", "f0_upper_bound_at_medium_t_min", "OK")] == 1


# ------------------------------------------------------------------------------------------------ acid marinades
@pytest.mark.parametrize("text,role", [("Marinate the chicken in vinegar for 2 hours.", "marinate"),
                                       ("Dice the carrots. Soak the carrots in lemon juice for 2 hours.", "soak"),
                                       ("Slice the cucumber. Pickle the cucumber in vinegar for 24 hours.", "pickle"),
                                       ("Slice the onion. Marinate the onion in lemon juice for 30 minutes.", "marinate")])
def test_acid_media_are_qualitative_ph_falls_with_no_number(layer, binder, text, role):
    r = l1(binder, text, role)
    assert r["inputs"]["medium"]["value"] in ("VINEGAR", "CITRUS_JUICE")
    out = layer.run(r)
    assert out["status"] == "QUALITATIVE_FLAGS_ONLY" and out["transition_status"] == "physically_possible"
    for b in B:
        s = out["scenarios"][b]
        assert s["state_flags"] == ["PH_FALLS"] and "ACID_UPTAKE_REACTION_DIFFUSION_QUALITATIVE_ONLY" in s["flags"]
        for k in ("uptake_fraction", "fourier_number", "D_eff_m2_s", "half_thickness_m"):
            assert k not in s
        assert not any(isinstance(v, float) and k not in ("duration_min",) for k, v in s.items())  # no numeric output but the stated time
        assert "D_eff_m2_s" not in s["bases"] and s["bases"]["medium"].startswith("L1:")


def test_acid_marinade_needs_no_size_and_keeps_the_stated_duration(layer, binder):
    out = layer.run(l1(binder, "Marinate the chicken in vinegar for 2 hours.", "marinate"))
    assert out["status"] == "QUALITATIVE_FLAGS_ONLY"  # no cut size is needed for a qualitative pH flag
    assert out["scenarios"]["TYPICAL"]["duration_min"] == 120.0 and out["scenarios"]["TYPICAL"]["bases"]["duration_min"] == "L1:TEXT_STATED"


def test_unknown_medium_stays_unknown(layer, binder):
    r = l1(binder, "Marinate the chicken.", "marinate")
    assert layer.run(r)["status"] == "SCENARIO_UNKNOWN"


@pytest.mark.parametrize("text,role", [("Dice the pork. Brine the pork in a 5% brine for 6 hours.", "brine"),
                                       ("Dice the pork. Marinate the pork in soy sauce for 6 hours.", "marinate"),
                                       ("Slice the carrots. Soak the carrots for 2 hours in water.", "soak")])
def test_salt_water_and_other_media_keep_their_fickian_bound(layer, binder, text, role):
    out = layer.run(l1(binder, text, role))
    assert out["status"] == "SCENARIO_COMPUTED"
    s = out["scenarios"]["TYPICAL"]
    assert 0.0 < s["uptake_fraction"] < 1.0 and "FICKIAN_SLAB_BI_INFINITY" in s["flags"]


# ------------------------------------------------------------------------------------------------ registry retirement
def _rows():
    with open(ROOT / NS.REGISTRY, newline="", encoding="utf-8") as fh:
        return {r["default_id"]: r for r in csv.DictReader(fh)}


def test_nh_041_and_nh_010_are_retired_kept_and_never_read(layer):
    rows = _rows()
    for rid in ("NH-041", "NH-010"):
        assert rid in rows and rows[rid]["source_status"].startswith("RETIRED_S177") and "RETIRED S177" in rows[rid]["source_hint"]
    assert layer.row("D_eff", "ACID") is None  # NH-041 is not loaded
    assert layer.row("medium_temperature", "PRESSURE_CANNER") is None  # NH-010 is not loaded
    reg = NS.load_registry(ROOT / NS.REGISTRY)
    assert "ACID" not in reg["D_eff"] and "PRESSURE_CANNER" not in reg["medium_temperature"]
    assert {"BRINE", "WATER", "MARINADE_OTHER"} <= set(reg["D_eff"])  # the other diffusivities are loaded
    assert len({r for r in rows}) == len(rows) == 40 and all(i.startswith("NH-") for i in rows)  # no row removed, no id reused


def test_every_remaining_row_is_still_an_unverified_recall():
    for rid, r in _rows().items():
        if rid not in ("NH-041", "NH-010"):
            assert r["source_status"] == "SOURCE_UNVERIFIED_AGENT_RECALLED" and "needs_source" in r["source_hint"]


def test_canner_rows_in_the_saturation_registry_match_the_layer():
    with open(ROOT / "registry/phase_change_v1.csv", newline="", encoding="utf-8") as fh:
        pc = {r["default_id"]: r for r in csv.DictReader(fh)}
    assert [float(pc["PC-002"][k]) for k in ("low", "mid", "high")] == [108.4, 115.2, 121.0]
    assert [float(pc[i]["mid"]) for i in ("PC-031", "PC-032", "PC-033")] == [108.4, 115.2, 121.0]
    assert math.isclose(float(pc["PC-034"]["mid"]), 121.54)


# ------------------------------------------------------------------------------------------------ versions
def test_versions_are_bumped():
    assert NS.VERSION == "nonheat-scenario-L2-0.3.0-draft" and NS.VERSION_V02 == "nonheat-scenario-L2-0.2.0-draft"
    assert NS.NonHeatScenario.load().run(l1(NB.NonHeatBinder.load(), "Whisk the eggs until frothy.", "whisk"))["version"] == NS.VERSION
