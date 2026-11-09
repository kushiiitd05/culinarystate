"""S176 L-NH Layer 2 SCENARIO for the non-heat families: registry rules, L1 kept, gaps filled with ids, UNKNOWN kept."""
from __future__ import annotations

import copy
import csv
import json
import math
from fractions import Fraction
from pathlib import Path

import pytest

from culinarystate.simulation import nonheat_binding as NB
from culinarystate.simulation import nonheat_drivers as ND
from culinarystate.simulation import nonheat_scenario as NS
from culinarystate.simulation import physics_drivers as PD

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


def reg(path):
    with open(ROOT / path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


# ------------------------------------------------------------------------------------------------ registry
def test_registry_rules():
    heat, nh = reg("registry/scenario_defaults_v1.csv"), reg("registry/scenario_defaults_nonheat_v1.csv")
    assert list(heat[0]) == list(nh[0])  # same columns as the heat registry
    ids = [r["default_id"] for r in nh]
    assert len(set(ids)) == len(ids) and all(i.startswith("NH-") for i in ids)
    assert not set(ids) & {r["default_id"] for r in heat}
    for r in nh:
        if r["source_status"].startswith("RETIRED_S177"):  # S177: kept for the audit trail (IDs never reused), never read
            assert "RETIRED S177" in r["source_hint"], r["default_id"]
            continue
        assert r["source_status"] == "SOURCE_UNVERIFIED_AGENT_RECALLED", r["default_id"]
        assert "needs_source" in r["source_hint"], r["default_id"]
        lo, mid, hi = (float(r[k]) for k in ("low", "mid", "high"))
        assert lo <= mid <= hi, r["default_id"]
        assert r["unit"] and r["quantity"] and r["applies_to"]


def test_l2_labels(layer, binder):
    out = layer.run(l1(binder, "Dice the pork. Freeze the pork for 4 hours.", "freeze"))
    assert out["labels"] == ["SCENARIO", "MODEL_DERIVED", "NON_CITABLE", "ASSUMED_DEFAULT"] and out["layer"] == "SCENARIO"
    assert out["form_candidate"] == NB.FORM_CANDIDATE["COOLING"]


# ------------------------------------------------------------------------------------------------ L2 never writes into L1
def test_layer_1_record_is_not_modified_and_stated_values_are_kept(layer, binder):
    e = l1(binder, "Dice the pork. Freeze the pork at -18C for 4 hours.", "freeze")
    before = copy.deepcopy(e)
    out = layer.run(e)
    assert e == before
    assert out["layer"] == "SCENARIO" and "inputs" not in out
    for name in B:
        sc = out["scenarios"][name]
        assert sc["medium_c"] == -18.0 and sc["bases"]["medium_c"] == "L1:TEXT_STATED"
        assert sc["bases"]["half_thickness_m"].startswith("L1:CUT_HISTORY|SD-")
        assert sc["frozen_within_stated_duration"] in (True, False) and sc["bases"]["stated_duration_min"] == "L1:TEXT_STATED"


def test_gaps_are_never_labelled_as_layer_1(layer, binder):
    out = layer.run(l1(binder, "Dice the pork. Chill the pork in the refrigerator.", "chill"))
    t = out["scenarios"]["TYPICAL"]
    assert t["bases"]["environment"] == "L1:TEXT_CUE"  # the fridge word is Layer 1; its temperature is not
    assert t["bases"]["medium_c"] == "NH-001" and t["medium_c"] == 5.0
    assert t["bases"]["duration_min"].startswith("KGE-")  # nothing stated: corpus quantiles, never L1
    assert t["bases"]["initial_c"].startswith("SD-") and t["bases"]["h"].startswith("NH-")
    assert t["bases"]["half_thickness_m"].startswith("L1:CUT_HISTORY|")
    assert "START_UNKNOWN_AMBIENT_ASSUMED" in t["flags"]
    for name in B:
        assert not any(v.startswith("L1:") for k, v in out["scenarios"][name]["bases"].items()
                       if k in ("duration_min", "initial_c", "h"))


def test_unknown_stays_unknown_and_sizes_are_never_invented(layer, binder):
    assert layer.run(l1(binder, "Chill the soup in the fridge for 2 hours.", "chill"))["status"] == "SCENARIO_UNKNOWN"
    out = layer.run(l1(binder, "Chill the soup in the fridge for 2 hours.", "chill"))
    assert "half_thickness" in out["missing"] and out["scenarios"] == {} and out["transition_status"] == "unsupported"
    assert layer.run(l1(binder, "Pickle the cucumbers.", "pickle"))["missing"] == ["medium"]
    assert layer.run(l1(binder, "Rest the dough for 10 minutes.", "rest"))["missing"] == ["prior_heat_link"]
    assert layer.run(l1(binder, "Dry the herbs.", "dry"))["status"] == "SCENARIO_UNKNOWN"
    assert layer.run(l1(binder, "Marinate the chicken.", "marinate"))["status"] == "SCENARIO_UNKNOWN"
    cut = layer.run(l1(binder, "Cut the cake.", "cut"))
    assert cut["status"] == "SCENARIO_UNKNOWN" and cut["missing"] == ["cut_class"]


def test_unsupported_media(layer, binder):
    assert layer.run(l1(binder, "Dice the fish. Defrost the fish in the microwave.", "defrost"))["status"] == "UNSUPPORTED_MEDIUM"
    assert layer.run(l1(binder, "Dry in the microwave for 5 minutes.", "dry"))["status"] == "UNSUPPORTED_MEDIUM"
    eq = layer.run(l1(binder, "Sterilise the jars at 120C for 15 minutes.", "sterilise"))
    assert eq["status"] == "UNSUPPORTED_TARGET_EQUIPMENT" and eq["scenarios"] == {}


# ------------------------------------------------------------------------------------------------ drivers through L2
def test_plank_through_layer_2_matches_the_formula_with_registry_values(layer, binder):
    out = layer.run(l1(binder, "Dice the pork. Freeze the pork at -18C for 4 hours.", "freeze"))
    t = out["scenarios"]["TYPICAL"]
    nh = {r["quantity"] + "/" + r["applies_to"]: r for r in reg("registry/scenario_defaults_nonheat_v1.csv")}
    mid = lambda q: float(nh[q]["mid"])  # noqa: E731
    expect = PD.plank_freezing_time_s(rho=mid("density_food/FOOD_HIGH_MOISTURE"),
                                      latent_j_kg=mid("latent_heat_freezing/FOOD_HIGH_MOISTURE"),
                                      t_freeze_c=mid("freezing_point/FOOD_HIGH_MOISTURE"), t_air_c=-18.0,
                                      thickness_m=2 * 0.005, h_w_m2k=mid("h/FREEZER"),
                                      k_frozen_w_mk=mid("k_frozen/FOOD_HIGH_MOISTURE")) / 60
    assert t["freezing_time_min"] == pytest.approx(expect, abs=1e-3)
    ft = [out["scenarios"][b]["freezing_time_min"] for b in B]
    assert ft[0] > ft[1] > ft[2]  # GENTLE is the slowest freezing


def test_freezing_with_a_medium_that_cannot_freeze_is_unknown(layer, binder):
    e = l1(binder, "Dice the pork. Freeze the pork in an ice bath.", "freeze")
    out = layer.run(e)
    assert out["status"] == "SCENARIO_UNKNOWN" and out["missing"] == ["MEDIUM_NOT_BELOW_FREEZING_POINT"]


def test_thaw_reverse_plank_and_ordering(layer, binder):
    out = layer.run(l1(binder, "Dice the pork. Thaw the pork in the fridge.", "defrost"))
    tt = [out["scenarios"][b]["thaw_time_min"] for b in B]
    assert tt[0] > tt[1] > tt[2] and "THAW_AS_REVERSE_PLANK" in out["scenarios"]["TYPICAL"]["flags"]


def test_cooling_trajectory_ordering_and_target_time(layer, binder):
    out = layer.run(l1(binder, "Dice the carrots. Boil the carrots for 10 minutes. Chill the carrots in the fridge for 3 hours "
                       "to 8C.", "chill"))
    assert out["status"] == "SCENARIO_COMPUTED", out
    ends = [out["scenarios"][b]["core_end_c"] for b in B]
    assert ends[0] >= ends[1] >= ends[2]
    assert out["scenarios"]["TYPICAL"]["initial_c"] == 80.0 and "START_POST_HEAT" in out["scenarios"]["TYPICAL"]["flags"]
    assert out["scenarios"]["TYPICAL"]["bases"]["target_food_c"] == "L1:TEXT_STATED"
    t = out["scenarios"]["TYPICAL"]["minutes_to_target_food_c"]
    assert t is not None and 0 < t < 24 * 60
    # the time-to-target agrees with the series at that time
    sc = out["scenarios"]["TYPICAL"]
    core = PD.core_temperature(t0_c=sc["initial_c"], bath_c=sc["medium_c"], time_s=60 * t, half_thickness_m=sc["half_thickness_m"],
                               alpha_m2_s=1.4e-7, h_w_m2k=sc["h"], k_w_mk=0.5)
    assert core == pytest.approx(8.0, abs=0.01)


def test_fickian_uptake_through_layer_2_matches_the_series(layer, binder):
    out = layer.run(l1(binder, "Slice the carrots. Soak the carrots for 2 hours in water.", "soak"))
    assert out["status"] == "SCENARIO_COMPUTED"
    t = out["scenarios"]["TYPICAL"]
    assert t["duration_min"] == 120 and t["bases"]["duration_min"] == "L1:TEXT_STATED"
    assert t["uptake_fraction"] == pytest.approx(PD.slab_uptake_fraction(d_m2_s=3e-10, half_thickness_m=0.0025,
                                                                         time_s=7200.0), abs=1e-6)
    assert t["fourier_number"] == pytest.approx(3e-10 * 7200 / 0.0025 ** 2, rel=1e-4)
    up = [out["scenarios"][b]["uptake_fraction"] for b in B]
    assert up == sorted(up) and "UPTAKE_FRACTION_OF_EQUILIBRIUM_NOT_A_CONCENTRATION" in out["scenarios"]["TYPICAL"]["flags"]


def test_overnight_and_bound_durations_fill_from_registry_and_kge_without_claiming_l1_numbers(layer, binder):
    o = layer.run(l1(binder, "Slice the carrots. Soak the carrots overnight in water.", "soak"))
    t = o["scenarios"]["TYPICAL"]
    assert t["duration_min"] == 600 and t["bases"]["duration_min"].startswith("NH-") and \
        "DURATION_FROM_OVERNIGHT_WORD" in t["flags"]
    b = layer.run(l1(binder, "Slice the carrots. Soak the carrots in water for up to 30 minutes.", "soak"))
    assert all(b["scenarios"][n]["duration_min"] <= 30 for n in B) and "DURATION_CLIPPED_TO_STATED_BOUND" in \
        b["scenarios"]["TYPICAL"]["flags"]


def test_f0_only_for_pressure_canning_and_qualitative_otherwise(layer, binder):
    # S177 (FINAL-SCI row 4): F0 is the low-acid pressure-canning reference. Pasteurise is outside its scope: conditions only.
    out = layer.run(l1(binder, "Pasteurise the juice at 120C for 15 minutes.", "pasteurise"))
    assert out["status"] == "QUALITATIVE_FLAGS_ONLY"
    for n in B:
        sc = out["scenarios"][n]
        assert "f0_min" not in sc and "f0_upper_bound_at_medium_t_min" not in sc
        assert "F0_NOT_APPLICABLE_LOW_ACID_RETORT_ONLY" in sc["flags"]
        assert sc["medium_c"] == 120.0 and sc["bases"]["medium_c"] == "L1:TEXT_STATED"
    assert layer.run(l1(binder, "Pasteurise the juice.", "pasteurise"))["status"] == "SCENARIO_UNKNOWN"
    bath = layer.run(l1(binder, "Pasteurise the juice in a boiling water bath for 10 minutes.", "pasteurise"))
    assert bath["status"] == "QUALITATIVE_FLAGS_ONLY"
    assert bath["scenarios"]["TYPICAL"]["medium_c"] == 100.0
    assert bath["scenarios"]["TYPICAL"]["bases"]["medium_c"] == "L1:PHYSICAL_DEFINITION"
    assert "f0_upper_bound_at_medium_t_min" not in bath["scenarios"]["TYPICAL"]


def test_drying_uses_stated_temperature_and_orders_the_brackets(layer, binder):
    out = layer.run(l1(binder, "Dice the apple. Dry the apple in a 60C oven for 8 hours.", "dry"))
    assert out["status"] == "SCENARIO_COMPUTED"
    assert all(out["scenarios"][n]["air_c"] == 60.0 for n in B)
    rem = [out["scenarios"][n]["water_removed_fraction"] for n in B]
    assert rem[0] <= rem[1] <= rem[2]
    assert {out["scenarios"][n]["time_class"] for n in B} <= {"CONSTANT_RATE_ONLY", "FALLING_RATE_REACHED"}
    assert "WATER_CONTENT_IS_A_DRYING_STATE_NOT_A_NUTRIENT" in out["scenarios"]["TYPICAL"]["flags"]


def test_cut_geometry_and_flags(layer, binder):
    out = layer.run(l1(binder, "Mince the garlic and let stand 10 minutes before cooking.", "mince"))
    hs = [out["scenarios"][n]["half_thickness_m"] for n in B]
    assert hs[0] > hs[1] > hs[2]  # thickest = GENTLE
    t = out["scenarios"]["TYPICAL"]
    assert t["surface_to_volume_slab_per_m"] == pytest.approx(1 / t["half_thickness_m"], rel=1e-3)
    assert t["surface_to_volume_cube_per_m"] == pytest.approx(3 / t["half_thickness_m"], rel=1e-3)
    assert t["enzyme_system_candidate"] == "ALLIINASE_FAMILY" and t["time_until_next_heat"] == 10.0
    assert t["time_until_next_heat_status"] == "BOUND_LOWER"
    halved = layer.run(l1(binder, "Halve the lemons.", "halve"))
    assert halved["status"] == "QUALITATIVE_FLAGS_ONLY" and "half_thickness_m" not in halved["scenarios"]["TYPICAL"]


def test_mix_is_flags_only_with_no_number(layer, binder):
    out = layer.run(l1(binder, "Whisk the eggs until stiff peaks form.", "whisk"))
    assert out["status"] == "QUALITATIVE_FLAGS_ONLY"
    for n in B:
        sc = out["scenarios"][n]
        assert sc["state_flags"] == ["AERATED"]
        assert not [v for v in sc.values() if isinstance(v, (int, float)) and not isinstance(v, bool)]
    assert layer.run(l1(binder, "Stir the soup.", "stir"))["status"] == "NO_FLAG_APPLICABLE"


def test_separation_handoff_codes(layer, binder):
    out = layer.run(l1(binder, "Soak the beans overnight, then drain and discard the soaking water.", "drain"))
    t = out["scenarios"]["TYPICAL"]
    assert t["handoff"] == "AQUEOUS_PHASE_REMOVED_AND_DISCARDED" and "SOAK_DISCARD_CHAIN_CANDIDATE" in t["flags"]
    fr = [out["scenarios"][n]["liquid_removed_fraction"] for n in B]
    assert fr == sorted(fr) and 0 < fr[0] and fr[-1] < 1
    assert layer.run(l1(binder, "Drain the pasta.", "drain"))["scenarios"]["TYPICAL"]["handoff"] == \
        "AQUEOUS_PHASE_REMOVED_FATE_UNKNOWN"
    kept = layer.run(l1(binder, "Drain the pasta, reserving 1 cup of the cooking water.", "drain"))
    assert kept["scenarios"]["TYPICAL"]["handoff"] == "AQUEOUS_PHASE_REMOVED_RETAINED_AS_SEPARATE_LOT"


def test_prove_and_ferment_are_flags_only(layer, binder):
    out = layer.run(l1(binder, "Leave the dough to prove for 1 hour.", "prove"))
    assert out["status"] == "QUALITATIVE_FLAGS_ONLY" and out["scenarios"]["TYPICAL"]["state_flags"] == ["VOLUME_RISES"]
    assert out["scenarios"]["TYPICAL"]["duration_min"] == 60 and out["scenarios"]["TYPICAL"]["bases"]["duration_min"] == "L1:TEXT_STATED"
    assert layer.run(l1(binder, "Ferment the cabbage for 3 days.", "ferment"))["scenarios"]["GENTLE"]["state_flags"] == ["PH_FALLS"]


def test_rest_carryover_through_layer_2(layer, binder):
    e = l1(binder, "Dice the potatoes. Roast the potatoes at 200C for 30 minutes. Rest the potatoes for 10 minutes.", "rest")
    out = layer.run(e)
    assert out["status"] == "SCENARIO_COMPUTED", out
    rises = [out["scenarios"][n]["carryover_rise_c"] for n in B]
    assert all(r >= 0 for r in rises)  # the rise itself is not monotone in the heat dose, by physics
    for key in ("core_end_of_heat_c", "core_peak_c"):  # the bracket order is the heat dose
        vals = [out["scenarios"][n][key] for n in B]
        assert vals[0] <= vals[1] <= vals[2], key
    t = out["scenarios"]["TYPICAL"]
    assert t["core_peak_c"] >= t["core_end_of_heat_c"] and t["core_end_c"] <= t["core_peak_c"]
    assert t["bases"]["heat_bath_c"] == "L1:TEXT_STATED" and t["bases"]["rest_duration_min"] == "L1:TEXT_STATED"
    assert "BRACKETS_ORDERED_BY_HEAT_DOSE_CARRYOVER_RISE_NOT_MONOTONE" in t["flags"]


def test_storage_conditions_only_kinetics_unknown(layer, binder):
    out = layer.run(l1(binder, "Store in the fridge for up to 3 days.", "store"))
    assert out["status"] == "CONDITIONS_ONLY_KINETICS_UNKNOWN" and out["transition_status"] == "unsupported"
    for n in B:
        sc = out["scenarios"][n]
        assert sc["kinetics"] == "UNKNOWN_PENDING_PARAM" and sc["duration_bound_min"] == 3 * 1440
    temps = [out["scenarios"][n]["storage_c"] for n in B]
    assert temps == [2.0, 5.0, 8.0]
    assert layer.run(l1(binder, "Store the jam.", "store"))["status"] == "SCENARIO_UNKNOWN"


def test_json_roundtrip_gives_the_same_layer_2(layer, binder):
    e = l1(binder, "Dice the carrots. Boil the carrots for 10 minutes. Chill the carrots in the fridge for 2-3 hours.", "chill")
    row = NB.row(e, "WIKIBOOKS", "R")
    a = layer.run(json.loads(json.dumps(row)))
    b = layer.run(e)
    assert a == b
    assert a["scenarios"]["GENTLE"]["duration_min"] == 120 and a["scenarios"]["INTENSE"]["duration_min"] == 180


def test_no_compound_or_nutrient_number_in_any_output(layer, binder):
    texts = ["Dice the pork. Freeze the pork at -18C.", "Slice the carrots. Soak the carrots for 2 hours in water.",
             "Dry the apple in a 60C oven for 8 hours.", "Sterilise at 120C for 15 minutes.", "Store in the fridge."]
    roles = ["freeze", "soak", "dry", "sterilise", "store"]
    for t, r in zip(texts, roles):
        text = repr(layer.run(l1(binder, t, r))).lower()
        for bad in ("vitamin", "retention", "nutrient", "mg", "ascorb", "carotene", "yield", "safe"):
            assert bad not in text.replace("mg ", "").replace("_not_a_nutrient", ""), (t, bad)


def test_count_row_and_order_checks(layer, binder):
    from collections import Counter
    c = Counter()
    NS.count_row(layer.run(l1(binder, "Dice the pork. Freeze the pork at -18C.", "freeze")), c)
    assert c[("n", "COOLING")] == 1 and c[("status", "COOLING", "SCENARIO_COMPUTED")] == 1
    assert c[("order", "COOLING", "freezing_time_min", "OK")] == 1
    assert not any(k[0] == "order" and k[-1] == "VIOLATION" for k in c)


def test_noun_surface_is_not_simulated(layer, binder):
    out = layer.run(l1(binder, "Remove shrimp from marinade, and discard marinade.", "marinate"))
    assert out["status"] == "UNSUPPORTED_NON_VERB_SURFACE" and out["scenarios"] == {} and out["transition_status"] == "unsupported"
