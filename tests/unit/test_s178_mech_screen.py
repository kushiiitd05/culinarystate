"""Mechanism screen (S178 lane MECH, T5-C02-R2): evaluators, layer views, member-scoped OR, edges, lineage, replay.

SYNTHETIC members (made-up SR identities and values, not USDA data) and synthetic events; the screen entries are the real
draft file. Passing says the screen keeps its K3 / layer rules, not that any verdict is true of food."""
from __future__ import annotations

import itertools
import json
import random
from fractions import Fraction as F
from types import SimpleNamespace as NS

import pytest

from culinarystate.mechanism import mech_entries as ME
from culinarystate.mechanism import mech_inputs as MI
from culinarystate.mechanism import mech_k3 as K
from culinarystate.mechanism import screen as S

# ----------------------------------------------------------------------------- synthetic catalog
FOODS = {  # fdc: (description, group, {nutrient: value})
    1: ("Garlic, raw", "Vegetables and Vegetable Products", {"protein": 6, "sugars": 1, "water": 59, "fat": 0.5,
                                                           "vitamin_c": 31, "starch": 0}),
    2: ("Sugars, granulated", "Sweets", {"protein": 0, "sugars": 99.8, "water": 0, "fat": 0, "vitamin_c": 0, "starch": 0}),
    3: ("Oil, olive, salad or cooking", "Fats and Oils", {"protein": 0, "sugars": 0, "water": 0, "fat": 100,
                                                         "vitamin_c": 0, "starch": 0}),
    4: ("Potatoes, flesh and skin, raw", "Vegetables and Vegetable Products",
        {"protein": 2, "sugars": 0.8, "water": 79, "fat": 0.1, "vitamin_c": 19, "starch": 15}),
    5: ("Chicken, broilers or fryers, meat only, raw", "Poultry Products",
        {"protein": 21, "sugars": 0, "water": 75, "fat": 3, "vitamin_c": 0, "starch": 0}),
    6: ("Spinach, raw", "Vegetables and Vegetable Products", {"protein": 2.9, "sugars": 0.4, "water": 91, "fat": 0.4,
                                                             "vitamin_c": 28, "starch": 0}),
    7: ("Lemon juice, raw", "Fruits and Fruit Juices", {"protein": 0.4, "sugars": 2.5, "water": 92, "fat": 0.2,
                                                       "vitamin_c": 39, "starch": 0}),
    8: ("Water, tap", "Beverages", {"protein": 0, "sugars": 0, "water": 100, "fat": 0, "vitamin_c": 0, "starch": 0}),
}
ING = {  # ing: (fdc, band, ING category, canonical name)
    "ING-A": (1, "HIGH", "VEGETABLE", "garlic"), "ING-B": (2, "HIGH", "SWEETENER", "sugar"),
    "ING-C": (3, "HIGH", "FAT_OIL", "olive oil"), "ING-D": (4, "HIGH", "VEGETABLE", "potato"),
    "ING-E": (5, "HIGH", "MEAT", "chicken"), "ING-G": (6, "HIGH", "VEGETABLE", "spinach"),
    "ING-H": (7, "HIGH", "FRUIT", "lemon juice"), "ING-W": (8, "HIGH", "BEVERAGE", "water"),
}
ACID = {"lemon juice"}


@pytest.fixture(scope="module")
def cat():
    return _catalog({k: ("A", 3) for k in _values()})            # every synthetic value analytical


def _values():
    return {(f, k): F(str(v)) for f, (_, _, nv) in FOODS.items() for k, v in nv.items()}


def _catalog(basis):
    cands = {i: ((f, b, F(1)),) for i, (f, b, _, _) in ING.items()}
    cats = {i: (c, FOODS[f][1]) for i, (f, _, c, _) in ING.items()}
    names = {i: n for i, (_, _, _, n) in ING.items()}
    names["ING-F"] = "mystery paste"
    return MI.MemberCatalog(cands, cats, {i: "DIRECT" for i in ING}, _values(), {f: d for f, (d, _, _) in FOODS.items()},
                            {f: g for f, (_, g, _) in FOODS.items()}, names,
                            lambda n: "ACID" if n in ACID else "LOW_ACID", basis)


@pytest.fixture(scope="module")
def screen():
    return S.MechScreen(ME.load(ME.OUT_PATH))


def lot(cat, *members, unknown=0):
    """members: ING id or (ING id, heated_before, cut_before)."""
    rows = [(m, False, False) if isinstance(m, str) else m for m in members]
    return MI.LotCtx("ENT1", MI.members_from(cat, rows), unknown)


def l1(**axes):
    out = {}
    for k, v in axes.items():
        out[k] = {"value": None, "status": "UNKNOWN", "basis": None, "reason": "X"} if v is None else \
            {"value": v[0], "status": "MEASURED", "basis": v[1]}
    return out


def ev(family, pid="PROC-000999", inputs=None, l2=None, l2_medium=None):
    return MI.EventCtx("E1", pid, family, inputs or {}, l2 or {}, l2_medium)


BOIL = ev("WET_HEAT", "PROC-000019", l1(medium=("WATER", "PROCESS_DEFINITION"),
                                        temperature_profile=("100", "PHYSICAL_DEFINITION")))
SIMMER = ev("WET_HEAT", "PROC-000020", l1(medium=("WATER", "PROCESS_DEFINITION"), temperature_profile=None),
            {"GENTLE": {"surface_state": "SURFACE_IMMERSED_WET", "bath_c": 85.0},
             "TYPICAL": {"surface_state": "SURFACE_IMMERSED_WET", "bath_c": 90.0},
             "INTENSE": {"surface_state": "SURFACE_IMMERSED_WET", "bath_c": 100.0}}, "WATER")
CUT = ev("MECHANICAL_CUT", "PROC-000050", l1(disruption_level=("HIGH", "PROCESS_DEFINITION")))
STIR = ev("MECHANICAL_MIX", "PROC-000064", l1())
SAUTE = ev("FAT_HEAT", "PROC-000014", l1(medium=("PAN_CONTACT_OIL", "PROCESS_DEFINITION")))


def verdict(screen, lt, e, key, view="L1"):
    return screen.screen_lot(lt, e)[key][view]


# ----------------------------------------------------------------------------- classes and presence
def test_taxon_classes_need_a_raw_identity():
    assert MI.in_class("ALLIUM_FRESH", "Garlic, raw")
    assert not MI.in_class("ALLIUM_FRESH", "Spices, garlic powder")
    assert not MI.in_class("ALLIUM_FRESH", "Onions, dehydrated flakes")
    assert MI.in_class("CHLOROPHYLL_TISSUE", "Peas, green, frozen, unprepared")
    assert not MI.in_class("PPO_FRESH", "Potatoes, baked, flesh, with salt")
    assert not MI.in_class("CHLOROPHYLL_TISSUE", "Cabbage, red, raw")
    assert MI.in_class("CHLOROPHYLL_TISSUE", "Cabbage, savoy, raw")
    assert MI.in_class("PPO_FRESH", "Potatoes, flesh and skin, raw")


def test_member_facts(cat):
    assert cat.member("ING-A").classes == {"ALLIUM_FRESH"}
    assert cat.member("ING-E").classes == {"COLLAGEN_TISSUE"}
    assert cat.member("ING-C").inert and cat.member("ING-W").inert and not cat.member("ING-D").inert
    assert cat.member("ING-C").presence["starch"][0] == "ABSENT"
    assert cat.member("ING-F").presence["starch"] == ("UNKNOWN", "NO_USABLE_IDENTITY")      # no identity: never absent
    assert cat.member("ING-H").acid_class == "ACID"


@pytest.mark.skipif(not MI.basis_supported(), reason="router presence screen without the S178 R4 basis rule")
def test_absent_needs_an_analytical_sr_zero(screen):
    """An assumed (Z) or undocumented zero, or no basis at all, never supports ABSENT, so never NOT_POSSIBLE."""
    assumed = _catalog({k: (("Z", 0) if k == (3, "starch") else ("A", 3)) for k in _values()})
    assert assumed.member("ING-C").presence["starch"] == ("UNKNOWN", "SR_ZERO_NOT_ANALYTICAL")
    assert assumed.member("ING-C").presence["protein"][0] == "ABSENT"
    assert verdict(screen, lot(assumed, "ING-C"), BOIL, "STARCH_GELATINISATION").verdict == K.UNDECIDED
    assert assumed.basis_rule == "ABSENT_NEEDS_ANALYTICAL_SR_ZERO"
    none = _catalog(None)
    assert none.basis_rule == "NO_BASIS_ABSENT_FAIL_CLOSED"
    assert none.member("ING-C").presence["starch"][0] == "UNKNOWN"
    for key in ("STARCH_GELATINISATION", "MAILLARD_STRECKER_LUMPED", "LIPID_OXIDATION", "CARAMELISATION"):
        for lt in (lot(none, "ING-C"), lot(none, "ING-B"), lot(none, "ING-B", "ING-W")):
            assert all(v.verdict != K.NOT_POSSIBLE for v in screen.screen_lot(lt, BOIL)[key].values())


# ----------------------------------------------------------------------------- cut-triggered enzymes
def test_alliinase(cat, screen):
    k = "ALLIINASE_ALLIIN_CLEAVAGE"
    v = verdict(screen, lot(cat, "ING-A"), CUT, k)
    assert v.verdict == K.POSSIBLE and v.support_layer == "L1"
    assert verdict(screen, lot(cat, "ING-A", "ING-C"), CUT, k).verdict == K.POSSIBLE          # oil is inert
    v = verdict(screen, lot(cat, "ING-A", "ING-D"), CUT, k)
    assert (v.verdict, v.reason) == (K.UNDECIDED, "FOREIGN_MEMBER_MAY_INHIBIT")
    v = verdict(screen, lot(cat, ("ING-A", True, True)), STIR, k)
    assert (v.verdict, v.reason) == (K.UNDECIDED, "PRIOR_HEAT_INACTIVATION_EXTENT_UNKNOWN")
    assert verdict(screen, lot(cat, "ING-A"), STIR, k).reason == "NO_DISRUPTION_EVIDENCE"
    assert verdict(screen, lot(cat, ("ING-A", False, True)), SAUTE, k).verdict == K.POSSIBLE     # cut earlier, raw
    v = verdict(screen, lot(cat, "ING-D"), CUT, k)
    assert (v.verdict, v.reason) == (K.UNDECIDED, "TAXON_ALLIUM_FRESH_NOT_IDENTIFIED")         # never NOT_POSSIBLE
    v = verdict(screen, lot(cat, "ING-A", unknown=1), CUT, k)
    assert (v.verdict, v.reason) == (K.UNDECIDED, "UNLINKED_MEMBER_MAY_INHIBIT")


def test_member_scope_needs_one_member_to_satisfy_all_conjuncts(cat, screen):
    """Two Allium members: one heated and uncut, one raw and cut earlier -> the second alone makes it POSSIBLE; with
    the flags split across members (heated+cut vs raw+uncut) no single member qualifies."""
    import dataclasses
    onion = dataclasses.replace(cat.member("ING-A"), ing_id="ING-A2")
    good = MI.LotCtx("E", (MI.LotMember(cat.member("ING-A"), True, False), MI.LotMember(onion, False, True)), 0)
    bad = MI.LotCtx("E", (MI.LotMember(cat.member("ING-A"), True, True), MI.LotMember(onion, False, False)), 0)
    k = "ALLIINASE_ALLIIN_CLEAVAGE"
    assert screen.screen_lot(good, STIR)[k]["L1"].verdict == K.POSSIBLE
    assert screen.screen_lot(bad, STIR)[k]["L1"].verdict == K.UNDECIDED


def test_ppo_needs_oxygen_contact(cat, screen):
    k = "PPO_ENZYMATIC_BROWNING"
    v = verdict(screen, lot(cat, "ING-D"), CUT, k)
    assert v.verdict == K.UNDECIDED and v.reason == "OXYGEN_CONTACT_NOT_STATED"
    assert verdict(screen, lot(cat, ("ING-D", False, True), "ING-C"), SAUTE, k).verdict == K.POSSIBLE


# ----------------------------------------------------------------------------- layer views
def test_starch_gelatinisation_views(cat, screen):
    k = "STARCH_GELATINISATION"
    per = screen.screen_lot(lot(cat, "ING-D"), BOIL)[k]
    assert all(per[v].verdict == K.POSSIBLE and per[v].support_layer == "L1" for v in K.VIEWS)
    per = screen.screen_lot(lot(cat, "ING-D"), SIMMER)[k]
    assert per["L1"].verdict == K.UNDECIDED and per["L1"].reason == "TEMPERATURE_UNKNOWN_L1"
    assert per["L2:GENTLE"].verdict == per["L2:TYPICAL"].verdict == K.UNDECIDED
    assert per["L2:INTENSE"].verdict == K.POSSIBLE and per["L2:INTENSE"].support_layer == "L2"
    per = screen.screen_lot(lot(cat, "ING-C"), SIMMER)[k]                       # oil only: starch measured absent
    assert all(per[v].verdict == K.NOT_POSSIBLE and per[v].item_key == "PRE01" for v in K.VIEWS)
    per = screen.screen_lot(lot(cat, "ING-C", "ING-F"), BOIL)[k]                # unknown identity: never absent
    assert per["L1"].verdict == K.UNDECIDED
    per = screen.screen_lot(lot(cat, "ING-C", unknown=1), BOIL)[k]
    assert per["L1"].verdict == K.UNDECIDED and per["L1"].reason.endswith("UNLINKED_MEMBER")


def test_reactions_have_no_temperature_switch(cat, screen):
    v = verdict(screen, lot(cat, "ING-E", "ING-B"), STIR, "MAILLARD_STRECKER_LUMPED")
    assert v.verdict == K.POSSIBLE and "DOSE_NOT_ASSESSED" in v.flags and "NO_SWITCH_REACTION" in v.flags
    assert verdict(screen, lot(cat, "ING-B", "ING-W"), BOIL, "MAILLARD_STRECKER_LUMPED").verdict == K.NOT_POSSIBLE
    v = verdict(screen, lot(cat, "ING-E"), SAUTE, "MAILLARD_STRECKER_LUMPED")      # meat traces: never absent
    assert (v.verdict, v.reason) == (K.UNDECIDED, "CARBONYL_SOURCE_NOT_ESTABLISHED")
    assert verdict(screen, lot(cat, "ING-E"), SAUTE, "CARAMELISATION").verdict == K.UNDECIDED   # trace-exempt muscle
    assert verdict(screen, lot(cat, "ING-C"), SAUTE, "CARAMELISATION").verdict == K.NOT_POSSIBLE
    assert verdict(screen, lot(cat, "ING-B"), STIR, "CARAMELISATION").reason == "NOT_A_HEAT_EVENT_FOOD_T_UNKNOWN"


def test_collagen_and_protein(cat, screen):
    assert verdict(screen, lot(cat, "ING-E"), BOIL, "COLLAGEN_SOLUBILISATION").verdict == K.POSSIBLE
    v = verdict(screen, lot(cat, "ING-B", "ING-C"), BOIL, "COLLAGEN_SOLUBILISATION")
    assert v.verdict == K.NOT_POSSIBLE and v.reason == "COLLAGEN_ABSENT_PROTEIN_SR_ZERO_ALL_MEMBERS"
    aerated = ev("MECHANICAL_MIX", "PROC-000066", l1(aerated=(True, "PROCESS_DEFINITION")))
    assert verdict(screen, lot(cat, "ING-E"), aerated, "PROTEIN_DENATURATION_AGGREGATION").verdict == K.POSSIBLE
    assert verdict(screen, lot(cat, "ING-E"), STIR, "PROTEIN_DENATURATION_AGGREGATION").verdict == K.UNDECIDED


def test_leaching_and_ascorbate(cat, screen):
    assert verdict(screen, lot(cat, "ING-D"), BOIL, "LEACHING").verdict == K.POSSIBLE
    assert verdict(screen, lot(cat, "ING-D"), SAUTE, "LEACHING").verdict == K.UNDECIDED
    assert verdict(screen, lot(cat, "ING-E"), BOIL, "LEACHING").verdict == K.NOT_POSSIBLE          # no vitamin C
    assert verdict(screen, lot(cat, "ING-D"), SAUTE, "ASCORBATE_TO_DHA_OXIDATION").verdict == K.POSSIBLE
    assert verdict(screen, lot(cat, "ING-D"), BOIL, "ASCORBATE_TO_DHA_OXIDATION").verdict == K.UNDECIDED


# ----------------------------------------------------------------------------- properties
def _random_cases(cat, n=400, seed=20261104):
    rnd = random.Random(seed)
    ings = list(ING) + ["ING-F"]
    media = [None, "WATER", "STEAM", "OVEN_AIR", "PAN_CONTACT_OIL", "LIQUID", "WATER_BATH_SEALED"]
    fams = ["WET_HEAT", "DRY_HEAT", "FAT_HEAT", "HEAT_GENERAL", "MECHANICAL_CUT", "MECHANICAL_MIX", "COOLING"]
    states = [None, "SURFACE_IMMERSED_WET", "SURFACE_WET_AT_TBOIL", "SURFACE_DRYING_POSSIBLE",
              "SURFACE_STATE_UNKNOWN_CORE_NOT_COMPUTED"]
    for _ in range(n):
        ms = [(i, rnd.random() < 0.3, rnd.random() < 0.3) for i in rnd.sample(ings, rnd.randint(1, 4))]
        med = rnd.choice(media)
        t = rnd.choice([None, ("100", "PHYSICAL_DEFINITION"), ("85", "TEXT_STATED"), ("180", "CARRIED_SETPOINT")])
        inp = l1(medium=(med, "PROCESS_DEFINITION") if med else None, temperature_profile=t,
                 lid_state=rnd.choice([None, ("UNCOVERED", "CUE"), ("COVERED", "CUE")]),
                 aerated=rnd.choice([None, (True, "TEXT_CUE")]))
        l2 = {b: {"surface_state": rnd.choice(states), "bath_c": rnd.choice([80.0, 95.0, 100.0, 180.0])}
              for b in K.BRACKETS}
        yield lot(cat, *ms, unknown=rnd.choice([0, 0, 0, 1])), ev(rnd.choice(fams), "PROC-000999", inp, l2, med)


def test_view_invariants_on_random_cases(cat, screen):
    for lt, e in _random_cases(cat):
        for key, per in screen.screen_lot(lt, e).items():
            l1v = per["L1"]
            for view, v in per.items():
                assert v.view == view
                if view != "L1":
                    assert not (v.verdict == K.NOT_POSSIBLE and l1v.verdict != K.NOT_POSSIBLE)   # L2 never excludes
                    assert not (l1v.verdict == K.POSSIBLE and v.verdict != K.POSSIBLE)            # L2 only adds
                if v.verdict == K.POSSIBLE:
                    assert v.reason == K.R_ALL_TRUE and v.item_key is None
                if v.verdict == K.NOT_POSSIBLE:
                    b = next(x for kk, _, x in screen.entries if kk == key)
                    assert b["items"][v.item_key]["evaluator"] in MI.MAY_EXCLUDE


def test_unknown_inputs_never_become_false(cat):
    """Every evaluator on a lot of unknown identity and an event with no inputs gives UNKNOWN (never FALSE)."""
    lt = lot(cat, "ING-F", unknown=1)
    empty = ev(None, None, {})
    args = {"nutrient_present": {"key": "starch"}, "taxon_present": {"cls": "ALLIUM_FRESH"},
            "tboil_surface": {"excess_water": True}, "inhibiting_agent_absent": {"cls": "ALLIUM_FRESH"}}
    for name in MI.EVALUATORS:
        for view in K.VIEWS:
            for member in (None, lt.members[0]):
                c = MI.evaluate(name, lt, member, empty, view, args.get(name, {}), "PRE01", "PRECONDITION")
                assert c.value == K.UNKNOWN, (name, view, c)


def test_evaluate_guards(cat):
    lt = lot(cat, "ING-C")
    bad = dict(MI.EVALUATORS)
    try:
        MI.EVALUATORS["heat_applied"] = lambda *a, **k: K.Conjunct("_", "_", K.FALSE, "X", "PROCESS_DEFINITION")
        with pytest.raises(K.K3Error):
            MI.evaluate("heat_applied", lt, None, STIR, "L1", {}, "PRE01", "PRECONDITION")
        MI.EVALUATORS["heat_applied"] = lambda *a, **k: K.Conjunct("_", "_", K.TRUE, "X", "SCENARIO")
        with pytest.raises(K.K3Error):
            MI.evaluate("heat_applied", lt, None, STIR, "L1", {}, "PRE01", "PRECONDITION")
    finally:
        MI.EVALUATORS.clear()
        MI.EVALUATORS.update(bad)
    with pytest.raises(K.K3Error):
        MI._basis("SD-001")                                          # an unknown basis is an error, never guessed


# ----------------------------------------------------------------------------- edges
def test_edges_only_between_distinct_members_of_the_same_lot(cat, screen):
    lt = lot(cat, "ING-E", "ING-B", "ING-D")
    edges = screen.edges(lt, screen.screen_lot(lt, SAUTE))
    pairs = {(e.supplier, e.receiver) for e in edges if e.kind == "REACTANT_PAIR" and e.view == "L1"}
    assert pairs == {("ING-D", "ING-B"), ("ING-E", "ING-B"), ("ING-E", "ING-D")}
    assert all(e.supplier != e.receiver and e.mechanism_key and e.tier == "T6_AI_DRAFTED" for e in edges)
    single = lot(cat, "ING-D")
    assert [e for e in screen.edges(single, screen.screen_lot(single, SAUTE)) if e.kind == "REACTANT_PAIR"] == []
    green = lot(cat, "ING-G", "ING-H")
    ce = [e for e in screen.edges(green, screen.screen_lot(green, BOIL)) if e.kind == "CONDITION_SUPPLIER"]
    assert {(e.supplier, e.receiver, e.direction) for e in ce} == {("ING-H", "ING-G", "INCREASES")}
    plain = lot(cat, "ING-G")
    assert not [e for e in screen.edges(plain, screen.screen_lot(plain, BOIL)) if e.kind == "CONDITION_SUPPLIER"]


# ----------------------------------------------------------------------------- lineage and the recipe path
def _claim(field, value):
    return NS(field=field, value=value)


def _graph():
    ents = [NS(entity_id="X1", attributes=[_claim("ingredient_id", "ING-A")], parent_entity_ids=()),
            NS(entity_id="X2", attributes=[_claim("ingredient_id", "ING-D")], parent_entity_ids=()),
            NS(entity_id="X3", attributes=[], parent_entity_ids=()),                  # unlinked root
            NS(entity_id="Y1", attributes=[], parent_entity_ids=("X1",)),             # minced garlic
            NS(entity_id="Y2", attributes=[], parent_entity_ids=("X2",)),             # boiled potato
            NS(entity_id="Z", attributes=[], parent_entity_ids=("Y1", "Y2", "X3"))]   # merged
    evs = [NS(event_id="E1", attributes=[_claim("proc_id", "PROC-000050")], consumes=("X1",), produces=("Y1",)),
           NS(event_id="E2", attributes=[_claim("proc_id", "PROC-000019")], consumes=("X2",), produces=("Y2",)),
           NS(event_id="E3", attributes=[_claim("proc_id", "PROC-000014")], consumes=("Z",), produces=())]
    return NS(entities=ents, events=evs)


def test_lineage_flags_follow_each_member_path():
    fams = MI.read_proc_families()
    lin = S.lineage(_graph(), fams)
    assert lin["Y1"] == ({"ING-A": (False, True)}, 0)
    assert lin["Y2"] == ({"ING-D": (True, False)}, 0)
    mem, unknown = lin["Z"]
    assert mem == {"ING-A": (False, True), "ING-D": (True, False)} and unknown == 1


def test_screen_graph_counts_rows_and_replay(cat, screen):
    fams = MI.read_proc_families()
    recs = {"L1": {"E2": {"process_id": "PROC-000019", "inputs": BOIL.l1}, "E3": {"process_id": "PROC-000014",
                                                                                     "inputs": SAUTE.l1}},
            "NH_L1": {"E1": {"process_id": "PROC-000050", "inputs": CUT.l1}}, "L2": {}, "NH_L2": {}}
    a = S.screen_graph("R1", "SYNTH", _graph(), screen=screen, catalog=cat, families=fams, records=recs)
    b = S.screen_graph("R1", "SYNTH", _graph(), screen=screen, catalog=cat, families=fams, records=recs)
    assert a.counts == b.counts and json.dumps(a.rows, sort_keys=True) == json.dumps(b.rows, sort_keys=True)
    assert a.counts[("events", "screened_heat")] == 2 and a.counts[("events", "screened_nonheat")] == 1
    assert a.counts[("lots", "screened")] == 3 and a.counts[("lots", "with_unlinked_member")] == 1
    assert not [k for k in a.counts if k[0] in ("invariant_violation", "exceptions")]
    row = next(r for r in a.rows if r["e"] == "E1")
    assert set(row["v"]) == {S.view_key(v) for v in K.VIEWS} and len(row["v"]["L1"]) == len(screen.keys)
    assert "r" in row and not any(isinstance(v, str) and " " in v for v in row.values())       # codes only
    bad = {**recs, "L1": {**recs["L1"], "E2": {"process_id": "PROC-000020", "inputs": {}}}}
    c = S.screen_graph("R1", "SYNTH", _graph(), screen=screen, catalog=cat, families=fams, records=bad)
    assert c.counts[("exceptions", "PROCESS_ID_MISMATCH")] == 1
    nested = S.nest(a.counts, "verdict")
    from culinarystate.quantity import rc2_dryrun as D
    D.assert_counts_only(nested)


def test_read_part_and_alignment(tmp_path):
    p = tmp_path / "part-00000.jsonl"
    p.write_text("".join(json.dumps({"recipe_id": r, "event_id": e}) + "\n" for r, e in
                         itertools.product(("R1", "R2"), ("E1", "E2"))), encoding="utf-8")
    got, seen = S.read_part(p, {"R2"})
    assert set(got) == {"R2"} and set(got["R2"]) == {"E1", "E2"} and seen == {"R1", "R2"}
    assert S.n_parts(tmp_path) == 1 and S.read_part(tmp_path / "missing.jsonl", {"R1"}) == ({}, set())
