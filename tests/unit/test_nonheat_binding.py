"""S176 L-NH Layer 1 (TEXT_STATED) for the non-heat families: spans, UNKNOWN, qualitative classes, census. Synthetic."""
from __future__ import annotations

import json
from fractions import Fraction

import pytest

from culinarystate.quantity import rc2_dryrun as D
from culinarystate.simulation import condition_binding as CB
from culinarystate.simulation import nonheat_binding as NB


@pytest.fixture(scope="module")
def binder():
    return NB.NonHeatBinder.load()


def ev(binder, text, role, n=0):
    return [e for e in binder.bind_text(text)["events"] if e["process_role"] == role][n]


CORPUS = [
    "Roast the chicken at 200C for 1 hour. Rest the meat for 10 minutes under foil. Cool on a wire rack.",
    "Chill the dough in the refrigerator for 2 hours. Freeze at -18C for up to 3 months. Thaw overnight in the fridge.",
    "Soak the beans overnight in cold water, then drain and rinse well. Squeeze out the water. Pat dry.",
    "Dice the onion finely. Mince the garlic and let stand 10 minutes before cooking. Fry the garlic for 2 minutes.",
    "Slice the cabbage. Grate the apple. Chop the herbs. Julienne the carrots. Crush the garlic. Halve the lemons.",
    "Brine the pork in a 5% salt solution for 12 hours. Pickle the cucumbers in vinegar for 3 days.",
    "Store in an airtight container at room temperature for up to 5 days. Dry in a 60C oven for 8 hours.",
    "Process in a boiling water bath for 10 minutes. Sterilise the jars at 120C for 15 minutes. Pasteurise at 72C.",
    "Whisk the eggs until stiff peaks form. Knead the dough for 10 minutes. Emulsify the oil slowly. Fold gently.",
    "Drain the pasta, reserving 1 cup of the cooking water. Strain the stock, discarding the solids.",
    "Marinate the chicken for 30 minutes to 1 hour in the fridge. Leave to prove for 2.5 hours in a warm place.",
    "Freeze for 4 hours. Defrost in the microwave. Refrigerate until cold. Let it cool for 1 hour 30 minutes.",
    "Chill. Cool. Rest. Soak. Dry. Store. Drain. Whisk.",
    "",
]


def test_no_input_is_bound_without_a_span_and_unknown_is_complete(binder):
    seen = 0
    for text in CORPUS:
        for e in binder.bind_text(text)["events"]:
            for name, x in e["inputs"].items():
                seen += 1
                if x["status"] == "UNKNOWN":
                    assert x["value"] is None and x["span"] is None and x["basis"] is None and x["reason"], (text, name)
                else:
                    a, b = x["span"]
                    assert 0 <= a < b <= len(text) and text[a:b].strip(), (text, name, x)
                    assert x["basis"] and x["value"] is not None
            assert 0 <= e["verb_span"][0] < e["verb_span"][1] <= len(text)
            for cue in e["cues"]:
                assert 0 <= cue["span"][0] < cue["span"][1] <= len(text)
    assert seen > 100


def test_every_record_names_a_form_candidate_class_and_only_nonheat_families(binder):
    fams = set()
    for text in CORPUS:
        for e in binder.bind_text(text)["events"]:
            assert e["nh_family"] in NB.NH_FAMILIES and e["form_candidate"] == NB.FORM_CANDIDATE[e["nh_family"]]
            assert e["family"] not in CB.HEAT and e["layer"] == "TEXT_STATED"
            fams.add(e["nh_family"])
    assert fams == set(NB.NH_FAMILIES)


def test_fridge_and_freezer_words_stay_qualitative_and_a_stated_number_is_kept_exactly(binder):
    c = ev(binder, "Chill the dough in the refrigerator for 2 hours.", "chill")
    assert c["inputs"]["environment"]["value"] == "FRIDGE" and c["inputs"]["environment"]["status"] == "QUALITATIVE"
    assert c["inputs"]["medium_temperature"]["status"] == "UNKNOWN"
    assert c["inputs"]["duration"]["value"] == 120 and c["inputs"]["duration"]["status"] == "MEASURED"
    f = ev(binder, "Freeze at -18C for 3 hours.", "freeze")
    assert f["inputs"]["medium_temperature"]["value"] == Fraction(-18)
    assert f["inputs"]["medium_temperature"]["basis"] == "TEXT_STATED"
    assert ev(binder, "Chill in a 40F fridge.", "chill")["inputs"]["medium_temperature"]["value"] == Fraction(40 - 32) * Fraction(5, 9)
    r = ev(binder, "Chill the soup in a 2-4C fridge.", "chill")["inputs"]["medium_temperature"]
    assert r["status"] == "RANGE" and r["value"] == (Fraction(2), Fraction(4))
    cooled = ev(binder, "Cool the soup to 40C.", "cool")  # S178 FIX-PHYS m4: the target is an endpoint, not an input
    assert cooled["endpoint"]["target_food_temperature"]["value"] == Fraction(40) and "target_food_temperature" not in cooled["inputs"]
    assert ev(binder, "Cool the soup to 40C.", "cool")["inputs"]["medium_temperature"]["status"] == "UNKNOWN"


def test_verb_defined_classes_carry_the_verb_span(binder):
    f = ev(binder, "Freeze for 4 hours.", "freeze")
    assert f["inputs"]["environment"]["basis"] == "PROCESS_DEFINITION" and f["inputs"]["environment"]["span"] == [0, 6]
    assert ev(binder, "Refrigerate overnight.", "chill")["inputs"]["environment"]["value"] == "FRIDGE"
    assert ev(binder, "Thaw the fish.", "defrost")["inputs"]["start_state"]["value"] == "FROZEN"


def test_durations_overnight_bound_compound_and_range(binder):
    s = ev(binder, "Soak the beans overnight in cold water.", "soak")["inputs"]
    assert s["duration"]["value"] == "OVERNIGHT" and s["duration"]["status"] == "QUALITATIVE"
    assert s["medium"]["value"] == "WATER" and s["environment"]["value"] == "COLD_WATER"
    st = ev(binder, "Store for up to 3 days in the fridge.", "store")["inputs"]
    assert st["duration"]["status"] == "BOUND_UPPER" and st["duration"]["value"] == 3 * 1440
    assert st["environment"]["value"] == "FRIDGE"
    assert ev(binder, "Let it cool for 1 hour 30 minutes.", "cool")["inputs"]["duration"]["value"] == 90
    m = ev(binder, "Marinate for 30 minutes to 1 hour.", "marinate")["inputs"]["duration"]
    assert m["status"] == "RANGE" and m["value"] == (Fraction(30), Fraction(60))
    assert ev(binder, "Leave to prove for 2.5 hours.", "prove")["inputs"]["duration"]["value"] == Fraction(150)


def test_unknown_is_never_zero_or_imputed(binder):
    for role in ("chill", "cool", "soak", "dry", "store", "rest", "drain"):
        e = ev(binder, f"{role.capitalize()}.", role)
        for name, x in e["inputs"].items():
            if x["status"] != "UNKNOWN":
                assert x["basis"] == "PROCESS_DEFINITION", (role, name)  # only the verb itself may bind anything
            else:
                assert x["value"] is None
    c = ev(binder, "Chill.", "chill")["inputs"]
    assert c["duration"]["reason"] == "NO_DURATION_STATED" and c["piece_size_class"]["reason"] == "NO_CUT_HISTORY_FOR_LOT"
    assert c["start_state"]["status"] == "UNKNOWN" and c["medium_temperature"]["status"] == "UNKNOWN"


def test_preservation_media_concentrations_and_physical_definition(binder):
    b = ev(binder, "Brine the pork in a 5% salt solution for 12 hours.", "brine")["inputs"]
    assert b["medium"]["value"] == "BRINE" and b["salt_concentration_pct"]["value"] == Fraction(5)
    assert b["salt_concentration_pct"]["basis"] == "TEXT_STATED"
    p = ev(binder, "Pickle the cucumbers in 5% vinegar for 3 days.", "pickle")["inputs"]
    assert p["medium"]["value"] == "VINEGAR" and p["acid_concentration_pct"]["value"] == Fraction(5)
    assert ev(binder, "Pickle the cucumbers.", "pickle")["inputs"]["medium"]["status"] == "UNKNOWN"
    c = ev(binder, "Pasteurise the juice in a boiling water bath for 10 minutes.", "pasteurise")["inputs"]
    assert c["medium_temperature"]["value"] == Fraction(100) and c["medium_temperature"]["basis"] == "PHYSICAL_DEFINITION"
    assert c["medium_temperature"]["span"] and c["environment"]["value"] == "BOILING_WATER_BATH"
    steril = ev(binder, "Sterilise the jars at 120C for 15 minutes.", "sterilise")
    assert any(cue["name"] == "EQUIPMENT_LIKELY" for cue in steril["cues"])
    d = ev(binder, "Dry in a 60C oven for 8 hours.", "dry")["inputs"]
    assert d["environment"]["value"] == "OVEN" and d["medium_temperature"]["value"] == Fraction(60)


def test_separation_fate_and_soak_chain(binder):
    r = binder.bind_text("Drain the pasta, reserving 1 cup of the cooking water. Strain the stock, discarding the solids.")
    drain = next(e for e in r["events"] if e["process_role"] == "drain")
    assert drain["inputs"]["liquid_fate"]["value"] == "RETAINED"
    disc = next(e for e in r["events"] if e["process_role"] == "discard")
    assert disc["inputs"]["removed_phase"]["value"] == "SOLID" and disc["inputs"]["removed_phase"]["basis"] == "TEXT_CUE"
    d2 = ev(binder, "Soak the beans overnight, then drain and discard the soaking water.", "drain")["inputs"]
    assert d2["liquid_fate"]["value"] == "DISCARDED" and d2["follows_soak_or_brine"]["value"] == "SOAK"
    rinse = ev(binder, "Rinse under cold running water.", "rinse")["inputs"]
    assert rinse["rinse_medium"]["value"] == "WATER" and rinse["rinse_temperature_class"]["value"] == "COLD"
    assert ev(binder, "Drain the pasta.", "drain")["inputs"]["liquid_fate"]["status"] == "UNKNOWN"


def test_cut_class_enzyme_flag_and_time_until_next_heat(binder):
    e = ev(binder, "Mince the garlic and let stand 10 minutes before cooking.", "mince")["inputs"]
    assert e["cut_class"]["value"] == "MINCED" and e["disruption_level"]["value"] == "HIGH"
    assert e["enzyme_system"]["value"] == "ALLIINASE_FAMILY" and e["enzyme_system"]["basis"] == "TEXT_CUE"
    assert e["time_until_next_heat"]["status"] == "BOUND_LOWER" and e["time_until_next_heat"]["value"] == 10
    dice = ev(binder, "Dice the carrots. Boil the carrots for 5 minutes.", "dice")["inputs"]
    assert dice["time_until_next_heat"]["value"] == "NEXT_HEAT_NO_TIMED_STEP_BETWEEN"
    assert dice["time_until_next_heat"]["status"] == "QUALITATIVE"  # not 0: the text gives no time
    raw = ev(binder, "Dice the carrots. Toss with the dressing.", "dice")["inputs"]
    assert raw["time_until_next_heat"]["status"] == "UNKNOWN"
    assert ev(binder, "Dice the carrots.", "dice")["inputs"]["enzyme_system"]["status"] == "UNKNOWN"


def test_mix_flags_only_and_verb_versus_text_basis(binder):
    w = ev(binder, "Whisk the eggs until stiff peaks form.", "whisk")["inputs"]
    assert w["aerated"]["basis"] == "TEXT_CUE" and w["emulsified"]["status"] == "UNKNOWN"
    k = ev(binder, "Knead the dough for 10 minutes.", "knead")["inputs"]
    assert k["developed"]["basis"] == "PROCESS_DEFINITION" and k["duration"]["value"] == 10
    s = ev(binder, "Stir the soup.", "stir")["inputs"]
    assert all(s[n]["status"] == "UNKNOWN" for n in ("aerated", "emulsified", "developed"))
    assert not any(isinstance(x["value"], (int, float, Fraction)) and not isinstance(x["value"], bool)
                   for x in w.values() if x["status"] != "UNKNOWN")


def test_rest_history_links_the_prior_heat_step_with_its_heat_layer_inputs(binder):
    r = binder.bind_text("Roast the chicken at 200C for 1 hour. Rest the meat for 10 minutes under foil.")
    rest = next(e for e in r["events"] if e["process_role"] == "rest")
    assert rest["inputs"]["prior_heat_link"]["basis"] in ("LINEAGE", "ORDER_ADJACENT")
    ph = rest["history"]["prior_heat"]
    heat = CB.Binder.load().bind_text("Roast the chicken at 200C for 1 hour. Rest the meat for 10 minutes under foil.")
    roast = next(e for e in heat["events"] if e["action"].lower() == "roast")
    assert ph["inputs"]["temperature_profile"]["value"] == str(roast["inputs"]["temperature_profile"]["value"])
    assert ph["inputs"]["duration"]["value"] == str(roast["inputs"]["duration"]["value"])
    assert rest["inputs"]["cover_state"]["value"] == "FOIL_TENTED"
    assert ev(binder, "Rest the dough for 10 minutes.", "rest")["inputs"]["prior_heat_link"]["status"] == "UNKNOWN"


def test_storage_environment_container_and_bound(binder):
    s = ev(binder, "Store in an airtight container in the freezer for up to 3 months.", "store")["inputs"]
    assert s["environment"]["value"] == "FREEZER" and s["container"]["value"] == "AIRTIGHT_OR_SEALED"
    assert s["duration"]["status"] == "BOUND_UPPER" and s["duration"]["value"] == 3 * 43200
    assert s["duration"]["unit_convention"] == "MONTH_30D"
    assert s["medium_temperature"]["status"] == "UNKNOWN"


def test_decimal_point_does_not_split_the_clause_window(binder):
    e = ev(binder, "Chill for 2.5 hours in the fridge.", "chill")["inputs"]
    assert e["environment"]["value"] == "FRIDGE" and e["duration"]["value"] == Fraction(150)


def test_missing_core_driver_groups(binder):
    assert NB.missing_core(ev(binder, "Freeze at -18C for 3 hours.", "freeze")) == ["piece_size_class"]
    sized = binder.bind_text("Dice the pork. Freeze the pork at -18C for 3 hours.")["events"]
    assert NB.missing_core(next(e for e in sized if e["process_role"] == "freeze")) == []
    assert NB.missing_core(ev(binder, "Whisk the eggs until frothy.", "whisk")) == []
    assert NB.missing_core(ev(binder, "Stir the soup.", "stir")) == ["aerated|emulsified|developed"]


# ------------------------------------------------------------------------------------------------ census
SENT = "ZQXSENTINEL"


def records(n=6):
    return [{"recipe_id": f"SYN-{SENT}-{i}", "source_family": "WIKIBOOKS",
             "steps": [f"Dice the carrots {SENT}.", "Boil the carrots for 20 minutes.", "Chill in the fridge for 2 hours.",
                       "Soak the beans overnight, then drain and rinse.", "Whisk the eggs until frothy."] if i != 2 else []}
            for i in range(n)]


def test_census_counts_only_and_adds_up(binder):
    rep = NB.census_from_records(records(), seed="7", size=6, binder=binder)
    D.assert_counts_only(rep)
    assert SENT not in json.dumps(rep) and rep["contains_ids"] is False and rep["texts_with_steps"] == 5
    assert sum(rep["events_by_family"].values()) == rep["nonheat_events"] > 0
    for fam, n in rep["events_by_family"].items():
        for name, st in rep["input_status"].get(fam, {}).items():
            assert sum(st.values()) == n, (fam, name)
        assert rep["driver_ready_events_by_family"][fam] <= rep["any_l1_value_by_family"][fam] <= n
        assert rep["any_text_value_by_family"][fam] <= rep["any_l1_value_by_family"][fam]


def test_census_workers_identical_and_records_have_no_text(binder, tmp_path):
    a = NB.census_from_records(records(9), seed="7", size=9, binder=binder)
    b = NB.census_from_records(records(9), seed="7", size=9, workers=2, binder=binder, records_dir=tmp_path)
    assert a == b
    rows = [json.loads(l) for f in sorted(tmp_path.glob("*.jsonl")) for l in f.read_text().splitlines()]
    assert len(rows) == a["nonheat_events"]
    blob = json.dumps(rows)
    assert SENT not in blob.replace("SYN-" + SENT, "")  # the recipe id is data, the step text is not
    r = rows[0]
    assert {"recipe_id", "event_id", "process_id", "nh_family", "form_candidate", "inputs", "layer", "verb_span"} <= set(r)
    assert r["layer"] == "TEXT_STATED"


def test_range_whose_unit_follows_the_upper_number_only(binder):
    d = ev(binder, "Put the rye bread to soak in beer for 6&ndash;12 hours.", "soak")["inputs"]["duration"]
    assert d["status"] == "RANGE" and d["value"] == (Fraction(360), Fraction(720)) and d["compound"] == "RANGE_LOW_FROM_TEXT"
    d2 = ev(binder, "Soak the tapioca for 4 or 5 hours.", "soak")["inputs"]["duration"]
    assert d2["value"] == (Fraction(240), Fraction(300))
    text = "Put the rye bread to soak in beer for 6&ndash;12 hours."
    assert text[d["span"][0]:d["span"][1]] == "6&ndash;12 hours"


def test_overnight_is_not_attached_to_untimed_families(binder):
    drain = ev(binder, "Refrigerate in the bowl, and then drain the water overnight.", "drain")["inputs"]
    assert drain["duration"]["status"] == "UNKNOWN"
    assert ev(binder, "Chill overnight.", "chill")["inputs"]["duration"]["value"] == "OVERNIGHT"


def test_noun_and_adjective_surfaces_are_marked(binder):
    e = ev(binder, "Remove shrimp from marinade, and discard marinade.", "marinate")
    assert any(c["name"] == "NON_VERB_SURFACE" for c in e["cues"]) and "verb_surface" in NB.missing_core(e)
    assert not any(c["name"] == "NON_VERB_SURFACE" for c in ev(binder, "Marinate the salmon for 1 hour.", "marinate")["cues"])
