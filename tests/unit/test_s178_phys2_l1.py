"""S178 PHYS2 Layer 1 0.2.0: temperature ownership (S177 open item (a)), member groups (open item (b)), per-axis provenance
(T4-C02), endpoint cues and the leakage guard (T4-C03). Synthetic sentences only."""
from __future__ import annotations

from fractions import Fraction

import pytest

from culinarystate.simulation import condition_binding as CB
from culinarystate.simulation import endpoint_cues as EC
from culinarystate.simulation import nonheat_binding as NB
from culinarystate.simulation import phase_change as PC
from culinarystate.simulation import recipe_adapter as RA
from culinarystate.simulation import scenario_layer as SL


@pytest.fixture(scope="module")
def binder():
    return CB.Binder.load()


@pytest.fixture(scope="module")
def nh_binder(binder):
    return NB.NonHeatBinder.load(base=binder)


def ev(binder, text, pid):
    return next(e for e in binder.bind_text(text)["events"] if e["process_id"] == pid)


def temp(e):
    t = e["inputs"]["temperature_profile"]
    return None if t["status"] == "UNKNOWN" else (t["value"], t["basis"])


BOIL, SIMMER, BRAISE, BAKE, ROAST, FRY, HEAT = ("PROC-000019", "PROC-000020", "PROC-000024", "PROC-000001", "PROC-000002",
                                                 "PROC-000009", "PROC-000032")


# --------------------------------------------------------------------------------------- ownership (open item (a))
def test_boil_does_not_take_the_oven_temperature_of_a_later_roast(binder):
    text = "Boil the potatoes for 10 minutes until tender, then roast at 400 F."
    assert temp(ev(binder, text, BOIL)) == (Fraction(100), "PHYSICAL_DEFINITION")
    assert temp(ev(binder, text, ROAST)) == (Fraction(1840, 9), "TEXT_STATED")
    assert ev(binder, text, BOIL)["temperature_note"][0]["now"] == "OWNED_BY_OTHER_EVENT"  # audit trail of the 0.1.0 difference


def test_oven_temperature_of_an_unrecognised_oven_step_is_ambient_for_the_liquid_step(binder):
    e = ev(binder, "Boil the potatoes for 10 minutes until tender, then place in a 400F oven.", BOIL)
    assert temp(e) == (Fraction(100), "PHYSICAL_DEFINITION")
    amb = e["inputs"]["ambient_temperature"]
    assert amb["value"] == Fraction(1840, 9) and amb["basis"] == "TEXT_STATED" and amb["row"].startswith("CB_RULE:AMBIENT_")


def test_preheat_temperature_in_an_unsplit_sentence_is_not_the_boil_temperature(binder):
    # many corpus steps run together without punctuation
    e = ev(binder, "Preheat oven to 375°F Cook the pasta in boiling water for ten minutes", BOIL)
    assert temp(e) == (Fraction(100), "PHYSICAL_DEFINITION") and e["inputs"]["ambient_temperature"]["value"] == Fraction(1715, 9)


def test_braise_in_an_oven_keeps_the_oven_temperature_as_ambient_and_the_bake_keeps_it_as_stated(binder):
    res = binder.bind_text("Cover with foil and bake (braise) at 350°F for 2 hours.")
    bake = next(e for e in res["events"] if e["process_id"] == BAKE)
    braise = next(e for e in res["events"] if e["process_id"] == BRAISE)
    assert temp(bake) == (Fraction(530, 3), "TEXT_STATED")  # coordinated verbs share one temperature
    assert braise["inputs"]["temperature_profile"]["status"] == "UNKNOWN" and braise["inputs"]["ambient_temperature"]["value"] == Fraction(530, 3)


def test_heat_level_in_parentheses_is_not_a_liquid_temperature(binder):
    e = ev(binder, "Increase to medium heat (350°F) and let boil for 5 minutes.", BOIL)
    assert temp(e) == (Fraction(100), "PHYSICAL_DEFINITION") and e["inputs"]["ambient_temperature"]["value"] == Fraction(530, 3)


def test_setter_shares_the_oil_temperature_with_the_fry_but_not_with_the_boil(binder):
    text = "Heat the oil to 340F for tempura and boil the water in a large pot for 5 minutes."
    assert temp(ev(binder, text, HEAT)) == (Fraction(1540, 9), "TEXT_STATED")
    assert temp(ev(binder, text, BOIL)) == (Fraction(100), "PHYSICAL_DEFINITION")
    fry = ev(binder, "Heat the oil to 350°F, then fry the chicken for 5 minutes.", FRY)
    assert temp(fry) == (Fraction(530, 3), "TEXT_STATED") and fry["inputs"]["temperature_profile"]["row"] == "CB_RULE:TEMPERATURE_FROM_SETTER_STEP"


def test_a_later_verb_does_not_lend_its_clause_cue(binder):
    # "roast" belongs to another clause: the boil's own 100 C is a liquid temperature
    for text in ("Roast the potatoes, then boil the carrots at 100C for 5 minutes.",
                 "Roast potatoes and boil carrots at 100C for 5 minutes."):
        e = ev(binder, text, BOIL)
        assert temp(e) == (Fraction(100), "TEXT_STATED") and "ambient_temperature" not in e["inputs"]


def test_sugar_syrup_temperatures_stay_liquid_temperatures(binder):
    # the S177 rule (cap never below a stated liquid temperature) is meant for candy stages
    for text in ("Boil the sugar and water to 240°F.", "Boil the syrup until it reaches 240F."):
        e = ev(binder, text, BOIL)
        assert temp(e) == (Fraction(1040, 9), "TEXT_STATED") and "ambient_temperature" not in e["inputs"]


def test_stated_temperature_of_a_simmer_without_an_oven_word_is_kept_as_stated(binder):
    # no cue, no guess: Layer 1 keeps what the text says; the flag is visible downstream, not silently dropped
    assert temp(ev(binder, "Cover and simmer for 2 hours at 325°F.", SIMMER)) == (Fraction(1465, 9), "TEXT_STATED")


def test_carried_setpoint_and_gas_mark_behaviour_is_unchanged(binder):
    assert temp(ev(binder, "Preheat the oven to 180C. Put the tray in. Bake for 30 minutes.", BAKE)) == (Fraction(180), "CARRIED_SETPOINT")
    e = ev(binder, "Preheat the oven to gas mark 4. Bake the cake for 20 minutes.", BAKE)
    assert e["inputs"]["temperature_profile"]["status"] == "UNKNOWN" and e["oven_setpoint_code"] == "GAS_4"
    assert e["inputs"]["temperature_profile"]["reason"] == "GAS_MARK_CODE_ONLY"


def test_second_temperature_of_one_verb_leads_the_next_verb(binder):
    text = "Pour mixture into cold pan and bake at 450 degrees F for 18 minutes- turn oven down to 350 degrees F and bake for another 10 minutes"
    bakes = [e for e in binder.bind_text(text)["events"] if e["process_id"] == BAKE]
    assert [temp(e) for e in bakes] == [(Fraction(2090, 9), "TEXT_STATED"), (Fraction(530, 3), "TEXT_STATED")]


def test_reduce_temperature_sets_the_temperature_of_the_roast(binder):
    e = ev(binder, "Reduce temperature to 350F and roast beef for 36 minutes longer.", ROAST)
    assert temp(e) == (Fraction(530, 3), "TEXT_STATED")


def test_a_later_oven_step_of_the_same_sentence_keeps_the_oven_temperature(binder):
    bakes = [e for e in binder.bind_text("Cover loosely with foil and bake in 350F oven for 30 minutes, uncover and bake a further 15 minutes.")["events"]
             if e["process_id"] == BAKE]
    assert [temp(e) for e in bakes] == [(Fraction(530, 3), "TEXT_STATED")] * 2
    assert bakes[1]["inputs"]["temperature_profile"]["row"] == "CB_RULE:TEMPERATURE_FROM_SETTER_STEP"
    # the nearest preceding temperature wins when the oven is turned down in between
    b2 = [e for e in binder.bind_text("Bake at 450F for 10 minutes, then reduce heat to 350F and bake 20 more minutes.")["events"] if e["process_id"] == BAKE]
    assert [temp(e)[0] for e in b2] == [Fraction(2090, 9), Fraction(530, 3)]  # 450 F, 350 F


def test_food_target_cue_edge_cases(binder):
    # "at least" is not a medium phrase; a deep-fat thermometer reads the oil, a candy thermometer the syrup
    e = ev(binder, "Reduce oven to 375F and cook chicken for 45 minutes or until temperature in the thickest part of thigh reads at least 170°F.", "PROC-000031")
    assert [c["class"] for c in e["endpoint"]["cues"]].count(EC.TARGET_CLASS) == 1
    assert temp(e) == (Fraction(1715, 9), "TEXT_STATED")  # the cook uses the 375 F oven the reduce step set, not the 170 F target
    oil = ev(binder, "Heat the oil in a saucepan until it registers 375°F on a deep-fat thermometer.", HEAT)
    assert EC.TARGET_CLASS not in [c["class"] for c in oil["endpoint"]["cues"]]
    assert temp(oil) == (Fraction(1715, 9), "TEXT_STATED") or temp(oil)[0] == (375 - 32) * Fraction(5, 9)


def test_liquid_media_equal_the_cap_aqueous_media():
    assert set(CB.LIQUID_MEDIA) == set(PC.AQUEOUS_LIQUID_MEDIA)


# --------------------------------------------------------------------------------------- member groups (open item (b))
def test_matrix_groups_lists_all_members_and_matrix_class_stays_single_group(binder):
    e = ev(binder, "Boil the milk and the sugar.", BOIL)
    assert e["inputs"]["matrix_groups"]["value"] == ["DAIRY", "SWEETENER"] and e["inputs"]["matrix_groups"]["basis"] == "FOOD_GROUP"
    assert e["inputs"]["matrix_class"]["status"] == "UNKNOWN" and e["inputs"]["matrix_class"]["reason"] == "MULTIPLE_FOOD_GROUPS"
    one = ev(binder, "Boil the potatoes for 20 minutes.", BOIL)
    assert one["inputs"]["matrix_class"]["value"] == "VEGETABLE" and one["inputs"]["matrix_groups"]["value"] == ["VEGETABLE"]
    none = ev(binder, "Boil for 5 minutes.", BOIL)
    assert "matrix_groups" not in none["inputs"] and none["inputs"]["matrix_class"]["reason"] == "NO_FOOD_GROUP"


def _l1_record(binder, text, pid):
    e = ev(binder, text, pid)
    return {"recipe_id": "R", "event_id": e["event_id"], "process_id": pid, "family": e["family"], "oven_setpoint_code": None,
            "inputs": {k: {**v, "value": v["value"] if not isinstance(v["value"], (Fraction, tuple)) else
                           (str(v["value"]) if isinstance(v["value"], Fraction) else [str(x) for x in v["value"]])}
                       for k, v in e["inputs"].items()}}


def test_member_groups_reach_the_cap_through_the_layer_2_reader(binder):
    layer = SL.ScenarioLayer.load()
    rec = _l1_record(binder, "Boil the milk and the sugar for 20 minutes.", BOIL)
    assert SL.member_groups(rec["inputs"]) == ("DAIRY", "SWEETENER")
    out = layer.run(rec)
    flags = out["scenarios"]["TYPICAL"]["flags"]
    assert "SUGAR_PHASE_TBOIL_LOWER_ESTIMATE" in flags  # a multi-member lot with a sugar member (was invisible at 0.3.0); S178 FIX-PHYS m10: renamed from TBOIL_CAP_LOWER_ESTIMATE_SOLUTE_RICH_MEMBER
    # every member a dry class: the lot is uncapped (multi-member), flagged
    rec2 = {**rec, "inputs": {**rec["inputs"], "matrix_groups": {"value": ["NUT_SEED", "SWEETENER"], "status": "MEASURED",
                                                                 "basis": "FOOD_GROUP", "span": None}}}
    f2 = layer.run(rec2)["scenarios"]["TYPICAL"]["flags"]
    assert "ALL_MEMBERS_DRY_CLASS" in f2 and "MATRIX_DRY_CLASS_UNCAPPED" in f2


def test_layer_2_carries_the_layer_1_provenance_and_the_ambient_flag(binder):
    layer = SL.ScenarioLayer.load()
    rec = _l1_record(binder, "Boil the potatoes for 10 minutes until tender, then place in a 400F oven.", BOIL)
    out = layer.run(rec)
    prov = out["l1_provenance"]
    assert prov["temperature_profile"]["basis"] == "PHYSICAL_DEFINITION" and prov["temperature_profile"]["row"] == f"process_medium_map_v1:{BOIL}"
    assert prov["duration"]["span_id"].startswith("C:") and prov["ambient_temperature"]["row"].startswith("CB_RULE:AMBIENT_")
    assert "OVEN_OR_AMBIENT_TEMPERATURE_STATED_NOT_USED_AS_LIQUID_T" in out["scenarios"]["TYPICAL"]["flags"]
    assert out["scenarios"]["TYPICAL"]["bath_c"] == 100.0 and out["version"] == SL.VERSION


# --------------------------------------------------------------------------------------- provenance (T4-C02)
SENTENCES = ["Bake at 400F for 25 mins.", "Preheat the oven to 180C. Put the tray in. Bake for 30 minutes.",
             "Boil the potatoes for 20 minutes. Fry the onions. Cover and simmer the beans for 10 minutes.",
             "Dice the carrots. Boil them in boiling water for 10 minutes.", "Melt the butter in a pan.",
             "Simmer the sauce until reduced by half; bake at 375 degrees F for 30 minutes.",
             "Bake the chicken until a thermometer reads 165°F."]


def test_every_axis_carries_a_basis_span_id_and_row_or_a_reason(binder):
    seen = {"bound": 0, "unknown": 0}
    for text in SENTENCES:
        for e in binder.bind_text(text)["events"]:
            if not e["heat"]:
                continue
            for axis, x in e["inputs"].items():
                if x["status"] == "UNKNOWN":
                    assert x["reason"] and x["basis"] is None, (text, axis)
                    seen["unknown"] += 1
                else:
                    assert x["basis"] and x["span_id"] and x["row"], (text, axis, x)
                    assert x["span_id"].split(":")[0] in ("C", "E", "L")
                    if x["span"] is not None:
                        assert x["span_id"] == f"C:{x['span'][0]}-{x['span'][1]}"
                    seen["bound"] += 1
    assert seen["bound"] > 20 and seen["unknown"] > 10


def test_nonheat_records_carry_span_id_and_row(nh_binder):
    for e in nh_binder.bind_text("Roast the chicken at 200C for 1 hour. Rest the meat for 10 minutes under foil. Cool on a wire rack.")["events"]:
        for axis, x in e["inputs"].items():
            if x["status"] == "UNKNOWN":
                assert x["reason"]
            else:
                assert x["basis"] and x["span_id"] and x["row"], (axis, x)


def test_nonheat_heat_link_uses_the_same_temperature_ownership(nh_binder):
    res = nh_binder.bind_text("Boil the potatoes for 10 minutes until tender, then roast at 400 F. Rest the meat for 10 minutes.")
    rest = next(e for e in res["events"] if e["nh_family"] == "RESTING")
    link = rest["history"]["prior_heat"]
    assert link["process_id"] == ROAST and link["inputs"]["temperature_profile"]["basis"] == "TEXT_STATED"


# --------------------------------------------------------------------------------------- endpoint cues (T4-C03)
def _cues(binder, text, pid):
    return ev(binder, text, pid)["endpoint"]


def test_until_clause_gives_qualitative_cues_with_spans(binder):
    text = "Bake for 20 minutes until golden brown and set."
    b = _cues(binder, text, BAKE)
    assert [c["class"] for c in b["cues"]] == ["COLOUR", "SET_FIRM"] and b["n_cues"] == 2
    sc = b["stopping_criterion"]
    assert sc["status"] == "QUALITATIVE" and sc["basis"] == "TEXT_CUE" and sc["value"] == "COLOUR" and sc["role"] == EC.ROLE
    for c in b["cues"]:
        assert text[c["span"][0]:c["span"][1]].strip() and 0 <= c["span"][0] < c["span"][1] <= len(text)
    assert text[sc["span"][0]:sc["span"][1]].lower() == "golden brown"


def test_cue_goes_to_the_nearest_preceding_heat_event(binder):
    text = "Boil the potatoes for 10 minutes until tender, then roast until golden."
    assert [c["class"] for c in _cues(binder, text, BOIL)["cues"]] == ["SOFTEN"]
    assert [c["class"] for c in _cues(binder, text, ROAST)["cues"]] == ["COLOUR"]


def test_reduced_by_half_phrase_and_unclassified_until_clause(binder):
    assert [c["class"] for c in _cues(binder, "Simmer the sauce until reduced by half.", SIMMER)["cues"]] == ["EVAPORATE_REDUCE"]
    # the phrase belongs to the nearest preceding heat event: here the verb "reduce" (PROC-000028, WET_HEAT) itself
    assert [c["class"] for c in _cues(binder, "Simmer to reduce by half.", "PROC-000028")["cues"]] == ["EVAPORATE_REDUCE"]
    b = _cues(binder, "Fry the onions until they sing.", FRY)
    assert [c["class"] for c in b["cues"]] == [EC.UNCLASSIFIED] and b["stopping_criterion"]["value"] == EC.UNCLASSIFIED


def test_no_cue_is_unknown_with_a_reason(binder):
    b = _cues(binder, "Boil the potatoes for 20 minutes.", BOIL)
    assert b["cues"] == [] and b["stopping_criterion"]["status"] == "UNKNOWN" and b["stopping_criterion"]["reason"] == "NO_ENDPOINT_CUE"


def test_food_target_temperature_is_an_endpoint_not_the_oven_temperature(binder):
    text = "Bake the chicken until a thermometer reads 165°F."
    e = ev(binder, text, BAKE)
    assert e["inputs"]["temperature_profile"]["status"] == "UNKNOWN"  # 0.1.0 bound 165 F as the oven temperature
    tgt = [c for c in e["endpoint"]["cues"] if c["class"] == EC.TARGET_CLASS]
    assert len(tgt) == 1 and Fraction(tgt[0]["target_c"]) == (165 - 32) * Fraction(5, 9)
    assert text[tgt[0]["span"][0]:tgt[0]["span"][1]] == "165°F"
    assert e["temperature_note"][0]["now"] == "TARGET_FOOD_TEMPERATURE"
    # "until the oven reaches" is the oven, and a candy thermometer reads the syrup: neither is a food target
    assert EC.TARGET_CLASS not in [c["class"] for c in ev(binder, "Boil the sugar with a candy thermometer to 240F.", BOIL)["endpoint"]["cues"]]


def test_a_list_of_food_target_temperatures_is_all_endpoint(binder):
    text = "Cook, turning often, until internal temperature reaches 140°F for medium rare, 155°F for medium, and 165°F for well done."
    e = ev(binder, text, "PROC-000031")
    assert e["inputs"]["temperature_profile"]["status"] == "UNKNOWN"
    tgt = [c for c in e["endpoint"]["cues"] if c["class"] == EC.TARGET_CLASS]
    assert len(tgt) == 3 and [text[c["span"][0]:c["span"][1]] for c in tgt] == ["140°F", "155°F", "165°F"]
    e2 = ev(binder, "Cook until internal temperature reaches 165°F in the breast and 170°F for the dark meat.", "PROC-000031")
    assert len([c for c in e2["endpoint"]["cues"] if c["class"] == EC.TARGET_CLASS]) == 2
    # a temperature after a verb or a medium word is not part of the list
    e3 = ev(binder, "Cook until internal temperature reaches 165°F, then bake at 350°F.", "PROC-000031")
    assert len([c for c in e3["endpoint"]["cues"] if c["class"] == EC.TARGET_CLASS]) == 1


def test_lexicon_is_well_formed_and_keyed_to_the_ledger_endpoint_procs():
    import csv
    import re
    from culinarystate.simulation import proc_family_registry as PR
    rows = list(csv.DictReader(open(EC.ROOT / EC.LEXICON, newline="", encoding="utf-8")))
    assert len({r["class_code"] for r in rows}) == len(rows) and len({int(r["priority"]) for r in rows}) == len(rows)
    for r in rows:
        re.compile(r["pattern"])
        assert r["status"].startswith("AI_DRAFTED")
    endpoint = {p for p, r in PR.latest_proc().items() if r["family"] == "ENDPOINT"}
    assert endpoint <= {r["ledger_proc_id"] for r in rows}  # every ledger ENDPOINT PROC has a cue class
    assert set(EC.classes()) >= {r["class_code"] for r in rows}


# --------------------------------------------------------------------------------------- leakage guard (T4-C03)
def test_endpoint_fields_are_not_input_axes_and_not_contract_bindings(binder):
    assert not set(CB.INPUTS) & EC.ENDPOINT_FIELDS
    res = binder.bind_text("Bake the chicken at 200C for 40 minutes until golden and a thermometer reads 74C.")
    for e in res["events"]:
        assert not set(e["inputs"]) & EC.ENDPOINT_FIELDS
    assert not {b.input_name for b in res["bindings"]} & EC.ENDPOINT_FIELDS
    assert {b.input_name for b in res["bindings"]} <= set(RA.INPUT_SPECS)


def test_endpoint_phrase_does_not_change_the_feature_row(binder):
    """Two texts that differ only in the endpoint phrase give identical feature rows (no endpoint cue in the feature matrix)."""
    pairs = [("Bake at 200C for 40 minutes.", "Bake at 200C for 40 minutes until golden brown."),
             ("Fry the onions in oil for 5 minutes.", "Fry the onions in oil for 5 minutes until soft and translucent."),
             ("Simmer the sauce for 15 minutes.", "Simmer the sauce for 15 minutes until reduced by half."),
             ("Roast at 220C for 30 minutes.", "Roast at 220C for 30 minutes until a thermometer reads 74C.")]
    for plain, cued in pairs:
        a, b = binder.bind_text(plain), binder.bind_text(cued)
        ra = [EC.physical_feature_row(e) for e in a["events"] if e["heat"]]
        rb = [EC.physical_feature_row(e) for e in b["events"] if e["heat"]]
        assert ra == rb, (plain, cued)
        assert any(e["endpoint"]["cues"] for e in b["events"] if e["heat"]) and not any(e["endpoint"]["cues"] for e in a["events"] if e["heat"])
        for row in rb:
            EC.assert_no_endpoint_fields(row)


def test_guard_rejects_an_endpoint_column(binder):
    with pytest.raises(AssertionError):
        EC.assert_no_endpoint_fields(["l1.duration.value", "l1.endpoint.value"])
    with pytest.raises(AssertionError):
        EC.assert_no_endpoint_fields(["process_id"], axes=["stopping_criterion"])
    e = ev(binder, "Bake for 20 minutes until golden.", BAKE)
    row = EC.physical_feature_row(e)
    assert not any("endpoint" in c or "stopping" in c or "cues" in c for c in row)
    EC.assert_no_endpoint_fields(row, axes=e["inputs"])
