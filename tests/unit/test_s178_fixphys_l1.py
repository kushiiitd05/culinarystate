"""S178 FIX-PHYS: Layer 1 0.3.0 fixes of the SCI-A review (M1-M3, the Layer 1 part of M4, m1-m3). Synthetic sentences only.

M1: a food-probe or until-clause target is an endpoint, never the medium temperature. M2: a shared or own temperature is used only
by a medium its cue is compatible with. M3: the after-window of the cue check is cut at the next clause / verb. M4 (Layer 1):
appliance and heat-level words are ambient cues. m1: ranges, spelled-out units, "c." cups. m2: UK fan strings. m3: a water bath in
an oven. Each reviewer input is a RED test of 0.2.0.
"""
from __future__ import annotations

from fractions import Fraction

import pytest

from culinarystate.simulation import condition_binding as CB
from culinarystate.simulation import endpoint_cues as EC
from culinarystate.simulation import scenario_layer as SL

BOIL, SIMMER, POACH, BAKE, ROAST, FRY, SAUTE, STEW, BRAISE, SCALD, HEAT, COOK = (
    "PROC-000019", "PROC-000020", "PROC-000021", "PROC-000001", "PROC-000002", "PROC-000009", "PROC-000014", "PROC-000025",
    "PROC-000024", "PROC-000150", "PROC-000032", "PROC-000031")


def F(f: int) -> Fraction:
    return (Fraction(f) - 32) * Fraction(5, 9)


@pytest.fixture(scope="module")
def binder():
    return CB.Binder.load()


@pytest.fixture(scope="module")
def layer():
    return SL.ScenarioLayer.load()


def ev(binder, text, pid, k=0):
    return [e for e in binder.bind_text(text)["events"] if e["process_id"] == pid][k]


def temp(e):
    t = e["inputs"]["temperature_profile"]
    return t["value"], t["basis"]


def targets(e):
    return [Fraction(c["target_c"]) for c in e["endpoint"]["cues"] if c["class"] == EC.TARGET_CLASS]


def s_(v):
    if isinstance(v, Fraction):
        return str(v)
    if isinstance(v, tuple):
        return [s_(x) for x in v]
    return v


def l2(layer, e):
    rec = {"recipe_id": "R", "event_id": e["event_id"], "process_id": e["process_id"], "oven_setpoint_code": e.get("oven_setpoint_code"),
           "inputs": {k: {**v, "value": s_(v["value"])} for k, v in e["inputs"].items()}}
    return layer.run(rec)


# ------------------------------------------------------------------------------------------------ M1 food targets
@pytest.mark.parametrize("text, pid, f", [
    ("Bake until a thermometer inserted in the center registers 160 F.", BAKE, 160),
    ("Poach the chicken breasts until a thermometer inserted in the thickest part reads 165 F.", POACH, 165),
    ("Rub the pork with brown sugar and bake until a thermometer reads 145 F.", BAKE, 145),
    ("Roast the turkey until the thigh reaches 180 F.", ROAST, 180),
    ("Simmer the custard until it reaches 170 F.", SIMMER, 170),
])
def test_m1_food_target_is_an_endpoint_not_the_medium_temperature(binder, text, pid, f):
    e = ev(binder, text, pid)
    assert e["inputs"]["temperature_profile"]["basis"] != "TEXT_STATED", text
    assert targets(e) == [F(f)], text


@pytest.mark.parametrize("plain, cued", [
    ("Simmer the custard.", "Simmer the custard until it reaches 170 F."),
    ("Roast the turkey.", "Roast the turkey until the thigh reaches 180 F."),
    ("Bake the loaf.", "Bake the loaf until a thermometer inserted in the center registers 190 F."),
    ("Rub the pork with brown sugar and bake.", "Rub the pork with brown sugar and bake until a thermometer reads 145 F."),
])
def test_m1_reviewer_leakage_pairs_give_identical_feature_rows(binder, plain, cued):
    ra = [EC.physical_feature_row(e) for e in binder.bind_text(plain)["events"] if e["heat"]]
    rb = [EC.physical_feature_row(e) for e in binder.bind_text(cued)["events"] if e["heat"]]
    assert ra == rb, (plain, cued)


@pytest.mark.parametrize("text, pid, f", [
    ("Boil the jam until it reaches 220 F.", BOIL, 220),                   # the jam's own temperature (S177 stage rule)
    ("Boil the sugar until a candy thermometer reads 235 F.", BOIL, 235),
    ("Boil the syrup, stirring, until it reaches 240 F.", BOIL, 240),
    ("Boil to 240 F, soft ball stage.", BOIL, 240),
    ("Heat the oil until it reaches 375 F.", HEAT, 375),                    # the oil, not a food
    ("Heat the milk until it reaches 180 F.", HEAT, 180),
])
def test_m1_liquid_and_syrup_temperatures_stay_stated(binder, text, pid, f):
    e = ev(binder, text, pid)
    assert temp(e) == (F(f), "TEXT_STATED") and targets(e) == [], text


def test_m1_a_setting_in_an_until_clause_is_not_a_target(binder):
    e = ev(binder, "Bake until golden at 350 F for 20 minutes.", BAKE)
    assert temp(e) == (F(350), "TEXT_STATED") and targets(e) == []


def test_m1_sugar_outside_the_events_own_phrase_does_not_block_a_target(binder):
    e = ev(binder, "Brush the ham with the syrup and roast until a thermometer reads 140 F.", ROAST)
    assert targets(e) == [F(140)] and e["inputs"]["temperature_profile"]["basis"] != "TEXT_STATED"


def test_m1_until_clause_spans_are_stored_in_the_endpoint_block(binder):
    text = "Simmer the custard until it reaches 170 F."
    e = ev(binder, text, SIMMER)
    cl = e["endpoint"]["until_clauses"]
    assert len(cl) == 1 and text[cl[0]["span"][0]:].startswith("until")
    assert [t["role"] for t in cl[0]["temperatures"]] == ["TARGET_UNTIL_CLAUSE"]
    assert "until_clauses" not in e["inputs"] and "until_clauses" in EC.ENDPOINT_FIELDS
    jam = ev(binder, "Boil the jam until it reaches 220 F.", BOIL)
    assert [t["role"] for t in jam["endpoint"]["until_clauses"][0]["temperatures"]] == ["EXEMPT_SYRUP_OR_CANDY"]


# ------------------------------------------------------------------------------------------------ M2 medium compatibility
def test_m2_oven_preheat_is_not_the_saute_pan_temperature(binder):
    e = ev(binder, "Preheat the oven to 400 F and saute the onions in butter for 5 minutes.", SAUTE)
    assert e["inputs"]["temperature_profile"]["status"] == "UNKNOWN"


def test_m2_an_oven_cued_temperature_is_ambient_for_a_fry(binder):
    e = ev(binder, "Fry the bacon until crisp and boil the eggs, oven at 350 F.", FRY)
    assert e["inputs"]["temperature_profile"]["status"] == "UNKNOWN"
    assert e["inputs"]["ambient_temperature"]["value"] == F(350)


def test_m2_the_oil_temperature_goes_to_the_fry_not_to_the_later_bake(binder):
    text = "Heat the oil to 375 F and fry the chicken for 5 minutes, then bake for 20 minutes."
    fry = ev(binder, text, FRY)
    assert temp(fry) == (F(375), "TEXT_STATED") and fry["inputs"]["temperature_profile"]["row"] == "CB_RULE:TEMPERATURE_FROM_SETTER_STEP"
    assert ev(binder, text, BAKE)["inputs"]["temperature_profile"]["basis"] != "TEXT_STATED"


def test_m2_a_general_setter_does_not_lend_another_foods_target(binder):
    e = ev(binder, "Cook the custard to 170 F, then simmer the berries for 5 minutes.", SIMMER)
    assert e["inputs"]["temperature_profile"]["basis"] != "TEXT_STATED"


def test_m2_a_general_setter_shares_when_the_receiver_cooks_in_it(binder):
    e = ev(binder, "Heat the milk to 180 F, then simmer the rice in it for 20 minutes.", SIMMER)
    assert temp(e) == (F(180), "TEXT_STATED")


def test_m2_legitimate_oven_sharing_is_kept(binder):
    assert temp(ev(binder, "Preheat the oven to 350 F and bake for 30 minutes.", BAKE)) == (F(350), "TEXT_STATED")
    bakes = [e for e in binder.bind_text("Bake at 350 F for 30 minutes, uncover and bake 15 more minutes.")["events"]
             if e["process_id"] == BAKE]
    assert [temp(e) for e in bakes] == [(F(350), "TEXT_STATED")] * 2


# ------------------------------------------------------------------------------------------------ M3 after-window cut
@pytest.mark.parametrize("text, pid, f", [
    ("Boil the syrup to 240 F and bake the cake for 30 minutes.", BOIL, 240),
    ("Scald the milk to 180 F before baking the custard.", SCALD, 180),
    ("Poach the eggs at 180 F and bake the muffins for 20 minutes.", POACH, 180),
])
def test_m3_a_later_clause_oven_word_does_not_take_the_liquids_own_temperature(binder, text, pid, f):
    e = ev(binder, text, pid)
    assert temp(e) == (F(f), "TEXT_STATED") and "ambient_temperature" not in e["inputs"], text


# ------------------------------------------------------------------------------------------------ M4 (Layer 1) ambient cues
@pytest.mark.parametrize("text, pid, f", [
    ("Reduce heat to 325 F and simmer for 1 hour.", SIMMER, 325),
    ("Simmer over medium heat, about 300 F, for 20 minutes.", SIMMER, 300),
    ("Simmer in an electric skillet at 300 F for 20 minutes.", SIMMER, 300),
    ("Stew in a slow cooker on high (300 F) for 4 hours.", STEW, 300),
    ("Braise in an electric frying pan set to 325 F for 1 hour.", BRAISE, 325),
])
def test_m4_appliance_and_heat_level_settings_are_ambient_for_a_liquid(binder, text, pid, f):
    e = ev(binder, text, pid)
    assert e["inputs"]["temperature_profile"]["basis"] != "TEXT_STATED", text
    assert e["inputs"]["ambient_temperature"]["value"] == F(f), text


def test_m4_a_heat_setting_at_or_below_the_boil_is_kept_as_the_liquid_temperature(binder):
    e = ev(binder, "Bring the water to a boil, reduce heat to 180 F and poach the eggs for 4 minutes.", POACH)
    assert temp(e) == (F(180), "TEXT_STATED")
    assert "HEAT_LEVEL_OR_APPLIANCE_SETTING_AT_OR_BELOW_TBOIL" in e["inputs"]["temperature_profile"]["flags"]


def test_m4_layer1_emits_syrup_and_pressure_cues_with_spans(binder):
    text = "Boil the syrup to 240 F."
    e = ev(binder, text, BOIL)
    c = e["inputs"]["syrup_stage_cue"]
    assert c["basis"] == "CUE" and text[c["span"][0]:c["span"][1]].lower() == "syrup" and c["span_id"] == EC.span_id(c["span"])
    p = ev(binder, "Boil in a pressure cooker at 15 psi (250 F) for 10 minutes.", BOIL)
    assert p["inputs"]["pressure_cue"]["basis"] == "CUE" and temp(p) == (F(250), "TEXT_STATED")
    plain = ev(binder, "Simmer 10 minutes at 350 F.", SIMMER)
    assert "syrup_stage_cue" not in plain["inputs"] and "pressure_cue" not in plain["inputs"]


# ------------------------------------------------------------------------------------------------ m1 parsing
@pytest.mark.parametrize("text", ["Bake at 350 to 375 F for 30 minutes.", "Bake at 350°-375°F for 30 minutes."])
def test_m1minor_ranges_are_ranges(binder, text):
    t = ev(binder, text, BAKE)["inputs"]["temperature_profile"]
    assert t["status"] == "RANGE" and tuple(t["value"]) == (F(350), F(375)), text


def test_m1minor_spelled_out_units_and_cups(binder):
    assert temp(ev(binder, "Bake at 400 degrees Fahrenheit for 30 minutes.", BAKE)) == (F(400), "TEXT_STATED")
    assert temp(ev(binder, "Bake at 200 degrees Celsius for 30 minutes.", BAKE)) == (Fraction(200), "TEXT_STATED")
    e = ev(binder, "Simmer the stock with 250 c. of water for 20 minutes.", SIMMER)
    assert e["inputs"]["temperature_profile"]["basis"] != "TEXT_STATED"
    assert temp(ev(binder, "Preheat the oven to 180 c. Grease a tin. Bake for 30 minutes.", BAKE)) == (Fraction(180), "CARRIED_SETPOINT")


def test_m1minor_a_from_to_change_is_the_new_setting(binder):
    t = ev(binder, "Turn the oven from 450 to 350 F and bake for 20 minutes.", BAKE)["inputs"]["temperature_profile"]
    assert t["status"] == "MEASURED" and t["value"] == F(350)


def test_m1minor_endpoint_regex_is_the_binder_regex():
    assert EC.TEMP_RE is CB._T


# ------------------------------------------------------------------------------------------------ m2 fan strings, m3 water bath
def test_m2minor_uk_fan_string_is_a_range_with_a_flag(binder):
    t = ev(binder, "Bake at 200C/180C fan/gas 6 for 30 minutes.", BAKE)["inputs"]["temperature_profile"]
    assert t["status"] == "RANGE" and tuple(t["value"]) == (Fraction(180), Fraction(200))
    assert t["flags"] == ["FAN_VS_CONVENTIONAL_UNRESOLVED"]
    t2 = ev(binder, "Bake at 180C fan / 200C for 30 minutes.", BAKE)["inputs"]["temperature_profile"]
    assert tuple(t2["value"]) == (Fraction(180), Fraction(200)) and "FAN_VS_CONVENTIONAL_UNRESOLVED" in t2["flags"]


def test_m3minor_water_bath_in_an_oven_is_a_water_medium_bounded_by_the_boil(binder, layer):
    text = "Dice the pears. Bake the pears in a water bath at 325 F for 50 minutes."
    e = ev(binder, text, BAKE)
    assert e["inputs"]["water_bath_cue"]["basis"] == "CUE" and temp(e) == (F(325), "TEXT_STATED")
    out = l2(layer, e)
    for i, (b, sc) in enumerate(out["scenarios"].items()):
        assert "WATER_BATH_IN_OVEN" in sc["flags"] and sc["boundary_c"] <= 100.0 and sc["h"] == layer.d["h"]["WATER"][i]
        assert sc["core_end_c"] <= 100.0 + 0.5
        assert "STATED_LIQUID_T_ABOVE_TBOIL" not in sc["flags"]
    assert out["medium"] == "WATER" and out["medium_rule"] == "WATER_BATH_IN_OVEN"


def test_layer1_version_is_0_3_0():
    assert CB.VERSION == "condition-binding-L1-0.3.1-draft" and CB.VERSION_V02 == "condition-binding-L1-0.2.0-draft"
    assert EC.VERSION == "endpoint-cues-0.3.0-draft"   # S179 SCI #1


def test_m1minor_nonheat_binder_reads_a_spaced_unit_and_refuses_cups():
    from culinarystate.simulation import nonheat_binding as NB
    nb = NB.NonHeatBinder.load()
    cool = next(e for e in nb.bind_text("Chill the custard to 40 F for 2 hours.")["events"] if e["nh_family"] == "COOLING")
    assert cool["endpoint"]["target_food_temperature"]["value"] == F(40)
    cups = next(e for e in nb.bind_text("Add 1 C sugar and chill for 1 hour.")["events"] if e["nh_family"] == "COOLING")
    assert cups["inputs"]["medium_temperature"]["status"] == "UNKNOWN"
    assert cups["endpoint"]["target_food_temperature"]["status"] == "UNKNOWN"
