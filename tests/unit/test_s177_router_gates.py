"""S177 / SCIFIX-ROUTER: FINAL-SCI #7 (prior-process lot context) and #6 (full ABSENT rule), synthetic screens only.

No real-data number is asserted here except structural facts about the shipped content table (every ABSENT member of the
real screen satisfies the three ABSENT conditions; the three false ABSENT cases the reviewers named are UNKNOWN).
"""
from __future__ import annotations

import csv
import json
import random
from fractions import Fraction
from pathlib import Path
from types import SimpleNamespace

import pytest

from culinarystate.mechanism import evidence_gates as EG
from culinarystate.mechanism import router_census as RC
from culinarystate.mechanism import router_demo as RD
from culinarystate.quantity import rc2_dryrun as D

ROOT = Path(__file__).resolve().parents[2]
VC = "SVAR-000009"
VEG = ("VEGETABLE", "Vegetables and Vegetable Products")


def _item_ids(text: str) -> tuple[str, str]:
    it = RD.route_text(text, index=RD.EvidenceIndex.from_rows([]), target_svar=VC)["items"][0]
    return it["ingredient_id"], it["process_id"]


POTATO, BOIL = _item_ids("Boil the potatoes for 20 minutes.")
_, FRY = _item_ids("Fry the potatoes for 5 minutes.")
_, SOAK = _item_ids("Soak the potatoes for 30 minutes.")
_, DRAIN = _item_ids("Drain the potatoes.")
_, CHOP = _item_ids("Chop the potatoes.")
CARROT, _ = _item_ids("Roast the carrots in the oven.")


def _row(evd_id, ing, proc, svar=VC):
    return {"id": evd_id, "version": 1, "status": "ACTIVE", "tier": "E3", "source_id": "SRC-1",
            "matrix": {"ingredient_id": ing}, "process": {"process_id": proc},
            "target": {"state_variable_id": svar, "raw_name": "Vitamin C"},
            "derived": {"retention_factor": {"status": "MEASURED", "value": 60.0, "unit": "%", "raw": "60"}},
            "verification": {"status": "UNVERIFIED"}}


def _screen(values, *, floor="1", margin="0", bands=None, alts=None, cats=None):
    """values: ING -> mg per 100 g (None = SR has no value). alts: ING -> [(mg or None, score, band)]."""
    cands, vals = {}, {}
    for n, (ing, v) in enumerate(values.items()):
        fdc = 1000 + 10 * n
        cs = [(fdc, (bands or {}).get(ing, "HIGH"), Fraction(1))]
        if v is not None:
            vals[(fdc, "vitamin_c")] = Fraction(v)
        for k, (av, sc, band) in enumerate((alts or {}).get(ing, ()), 1):
            cs.append((fdc + k, band, Fraction(str(sc))))
            if av is not None:
                vals[(fdc + k, "vitamin_c")] = Fraction(av)
        cands[ing] = tuple(cs)
    fl = {VC: EG.Floor(VC, "Vitamin C", "vitamin_c", "mg", Fraction(floor), "PROPOSED_PILOT", Fraction(margin))}
    cats = {ing: VEG for ing in values} if cats is None else cats
    return EG.TargetPresenceScreen(fl, cands, vals, cats, basis={k: ("A", 1) for k in vals})  # S178 R4: synthetic SR values are analytical


def _gates(values, **kw):
    gate_kw = {k: kw.pop(k) for k in ("presence", "context") if k in kw}
    return EG.EvidenceGates(_screen(values, **kw), **gate_kw)


def _items(text, gates, rows):
    out = RD.route_text(text, index=RD.EvidenceIndex.from_rows(rows), target_svar=VC, gates=gates)
    return out["items"]


def _by_action(items, action, ing=None):
    return [i for i in items if i["action"].lower() == action and (ing is None or i["ingredient_id"] == ing)]


# =================================================================== #7: prior-process lot context
def test_prior_kind_classes_from_the_process_hierarchy():
    assert EG.prior_kind(BOIL) == "HEAT" and EG.prior_kind(FRY) == "HEAT"
    assert EG.prior_kind(DRAIN) == "LEACH"                        # SEPARATION family
    assert EG.prior_kind(SOAK) == "LEACH"                         # soak-like process
    assert EG.prior_kind("PROC-000133") == "HEAT"                 # dry / dehydrate
    assert EG.prior_kind(CHOP) is None                            # a cut is not a heat or leach event
    assert EG.prior_kind(None) is None and EG.prior_kind("PROC-NOPE") is None     # unresolved is not assumed heat


def _ent(eid, ing=None, parents=()):
    attrs = (SimpleNamespace(field="ingredient_id", value=ing),) if ing else ()
    return SimpleNamespace(entity_id=eid, entity_type="X", attributes=attrs, parent_entity_ids=tuple(parents))


def _ev(eid, proc, produces):
    attrs = (SimpleNamespace(field="proc_id", value=proc),) if proc else ()
    return SimpleNamespace(event_id=eid, attributes=attrs, produces=tuple(produces), consumes=(), discards=())


def test_lot_members_carry_prior_process_through_ancestry_from_events_produces():
    g = SimpleNamespace(
        entities=[_ent("N1", ing="A"), _ent("N2", parents=("N1",)), _ent("N3", parents=("N2",)),
                  _ent("N4", ing="B"), _ent("N5", parents=("N4",)), _ent("N6", parents=("N1",)),
                  _ent("N7", ing="C"), _ent("N8", parents=("N7",))],
        events=[_ev("E1", BOIL, ["N2"]), _ev("E2", CHOP, ["N5"]), _ev("E3", None, ["N6"]), _ev("E4", DRAIN, ["N8"])])
    m = EG.lot_members(g)
    assert m["N1"].prior == frozenset() and not m["N1"].prior_process          # raw root
    assert m["N2"].prior == {"HEAT"} and m["N2"].sole == "A"                   # produced by a boil
    assert m["N3"].prior == {"HEAT"}                                           # a descendant inherits it
    assert not m["N5"].prior_process                                           # a cut is not prior process
    assert m["N6"].prior == {"UNRESOLVED"}                                     # S178 R5: unresolved = unknown context (fail-closed)
    assert m["N8"].prior == {"LEACH"}
    # without events (older callers / synthetic graphs) nothing is prior
    assert not EG.lot_members(SimpleNamespace(entities=g.entities))["N2"].prior_process


TEXT_BOIL_FRY = "Boil the potatoes for 20 minutes. Fry the potatoes for 5 minutes."


def test_boil_then_fry_withholds_direct_on_the_second_process_only():
    rows = [_row("EVD-1", POTATO, BOIL), _row("EVD-2", POTATO, FRY)]
    items = _items(TEXT_BOIL_FRY, _gates({POTATO: "19.7"}), rows)
    boil, = _by_action(items, "boil", POTATO)
    fry, = _by_action(items, "fry", POTATO)
    assert boil["route"] == "DIRECT" and [e["evd_id"] for e in boil["evidence"]] == ["EVD-1"]
    assert boil["prior_process"] == [] and EG.R_PRIOR_PROCESS not in boil["reasons"]
    assert fry["route_ungated"] == "DIRECT" and fry["route"] == "UNKNOWN"      # withheld, never upgraded
    assert fry["reasons"][0] == "PRIOR_PROCESS_CONTEXT" and "EVIDENCE_PREEMPTS" not in fry["reasons"]
    assert fry["gates"] == {"presence": "PRESENT", "lot_context": "SINGLE_MEMBER"}      # the context stays SINGLE_MEMBER
    assert fry["prior_process"] == ["HEAT"]
    assert fry["evidence"] == [] and [e["evd_id"] for e in fry["evidence_not_applied"]] == ["EVD-2"]


def test_soak_or_drain_then_boil_is_withheld_as_leach():
    for first in ("Soak the potatoes for 30 minutes.", "Drain the potatoes."):
        items = _items(first + " Boil the potatoes for 20 minutes.", _gates({POTATO: "19.7"}),
                       [_row("EVD-1", POTATO, BOIL)])
        boil, = _by_action(items, "boil", POTATO)
        assert boil["route"] == "UNKNOWN" and boil["reasons"][0] == "PRIOR_PROCESS_CONTEXT", first
        assert boil["prior_process"] == ["LEACH"]


def test_a_cut_before_the_process_does_not_withhold():
    items = _items("Chop the potatoes. Boil the potatoes for 20 minutes.", _gates({POTATO: "19.7"}),
                   [_row("EVD-1", POTATO, BOIL)])
    boil, = _by_action(items, "boil", POTATO)
    assert boil["route"] == "DIRECT" and boil["prior_process"] == [] and boil["evidence_not_applied"] == []


def test_prior_process_reason_only_when_it_actually_downgrades():
    items = _items(TEXT_BOIL_FRY, _gates({POTATO: "19.7"}), [_row("EVD-1", POTATO, BOIL)])   # no row for fry
    fry, = _by_action(items, "fry", POTATO)
    assert fry["route"] == "UNKNOWN" and EG.R_PRIOR_PROCESS not in fry["reasons"]          # nothing to withhold
    assert fry["prior_process"] == ["HEAT"]                                                   # the fact is still reported


def test_context_gate_switch_turns_the_prior_process_rule_off_and_presence_still_precedes():
    rows = [_row("EVD-1", POTATO, BOIL), _row("EVD-2", POTATO, FRY)]
    off = _items(TEXT_BOIL_FRY, _gates({POTATO: "19.7"}, context=False), rows)
    assert _by_action(off, "fry", POTATO)[0]["route"] == "DIRECT"
    absent = _items(TEXT_BOIL_FRY, _gates({POTATO: "0"}), rows)                               # ABSENT beats the context rule
    fry, = _by_action(absent, "fry", POTATO)
    assert fry["route"] == EG.NOT_APPLICABLE and fry["reasons"][0] == "TARGET_ABSENT"


def test_merged_lot_reason_takes_precedence_over_prior_process():
    text = "Boil the potatoes for 10 minutes. Add the carrots to the potatoes. Fry for 5 minutes."
    rows = [_row("EVD-2", POTATO, FRY), _row("EVD-3", CARROT, FRY)]
    fry = _by_action(_items(text, _gates({POTATO: "19.7", CARROT: "5.9"}), rows), "fry")
    assert {i["ingredient_id"] for i in fry} == {POTATO, CARROT}
    for it in fry:
        assert it["gates"]["lot_context"] == "MERGED" and it["prior_process"] == ["HEAT"]
        assert it["route_ungated"] == "DIRECT" and it["route"] == "UNKNOWN"
        assert it["reasons"][0] == "MERGED_LOT_CONTEXT" and EG.R_PRIOR_PROCESS not in it["reasons"]


def test_gates_never_upgrade_a_route_with_the_prior_process_rule():
    texts = [TEXT_BOIL_FRY, "Soak the potatoes. Boil the potatoes. Fry the potatoes.",
             "Chop the potatoes. Fry the potatoes. Roast the carrots. Drain the carrots. Boil the carrots."]
    keys = [(POTATO, BOIL), (POTATO, FRY), (CARROT, BOIL), (CARROT, "PROC-000020"), (POTATO, SOAK)]
    rng = random.Random(177)
    for _ in range(30):
        rows = [_row(f"E{n}", i, p) for n, (i, p) in enumerate(rng.sample(keys, rng.randint(0, len(keys))))]
        context_on = rng.random() < 0.8
        gates = _gates({POTATO: rng.choice(["0", "5", None]), CARROT: rng.choice(["0", "5", None])},
                       presence=rng.random() < 0.8, context=context_on)
        for text in texts:
            for it in _items(text, gates, rows):
                if it["route"] == EG.NOT_APPLICABLE:
                    continue
                assert EG.ROUTE_STRENGTH[it["route"]] <= EG.ROUTE_STRENGTH[it["route_ungated"]]
                if it["route"] == "DIRECT":
                    assert it["route_ungated"] == "DIRECT" and it["evidence"]
                    assert not it["prior_process"] or not context_on          # a surviving DIRECT is never after a heat / leach


def test_census_counts_prior_process_withheld_by_kind_counts_only():
    recs = [{"recipe_id": f"SYN-{i}", "source_family": "FOODCOM", "ingredient_lines": ["2 potatoes"],
             "steps": ["Boil the potatoes for 20 minutes.", "Fry the potatoes for 5 minutes.",
                       "Soak the carrots. Roast the carrots in the oven."]} for i in range(4)]
    rows = [_row("E1", POTATO, BOIL), _row("E2", POTATO, FRY), _row("E3", CARROT, "PROC-000020"),
            _row("E4", CARROT, _item_ids("Roast the carrots.")[1])]
    rep = RC.census_from_records(recs, seed="9", size=4, index=RD.EvidenceIndex.from_rows(rows), target_svar=VC,
                                 gates=_gates({POTATO: "19.7", CARROT: "5.9"}))
    D.assert_counts_only(rep)
    assert rep["prior_process_withheld"].get("HEAT", 0) == 4          # fry after boil, x4 recipes
    assert rep["prior_process_withheld"].get("LEACH", 0) == 4         # roast after soak
    assert rep["reason_counts"]["PRIOR_PROCESS_CONTEXT"] == 8
    assert sum(rep["member_presence"].values()) == rep["items"]
    assert rep["census_version"] == RC.CENSUS_VERSION and RC.CENSUS_VERSION.endswith("0.4.1-draft")   # S179: 0.4.1 adds post-food state cues (SCI #4)


# =================================================================== #6: the full ABSENT rule
def test_absent_needs_a_high_rank1_band_and_a_confirmed_category():
    sc = _screen({"HI": "0", "MED": "0", "NOCAT": "0", "WRONG": "0"}, bands={"MED": "MEDIUM"},
                 cats={"HI": VEG, "MED": VEG, "NOCAT": ("", "Vegetables and Vegetable Products"),
                       "WRONG": ("VEGETABLE", "Beverages")})
    assert sc.member_verdict(VC, "HI") == (EG.ABSENT, "")
    assert sc.member_verdict(VC, "MED") == (EG.UNKNOWN, "RANK1_NOT_HIGH")
    assert sc.member_verdict(VC, "NOCAT") == (EG.UNKNOWN, "CATEGORY_EMPTY")
    assert sc.member_verdict(VC, "WRONG") == (EG.UNKNOWN, "CATEGORY_MISMATCH")
    assert sc.member_verdict(VC, "UNMATCHED") == (EG.UNKNOWN, "NO_USABLE_IDENTITY")
    nocats = _screen({"HI": "0"}, cats={})                                    # no category information: fail closed
    assert nocats.member_state(VC, "HI") == EG.UNKNOWN


def test_low_band_alternatives_within_the_margin_block_absent():
    """The reviewers' case: LOW-band rank 2-3 alternatives used to be dropped before the margin test."""
    alts = {"A": [("127.7", "0.88", "LOW")],       # 0.12 below rank 1, holds the nutrient
            "B": [(None, "0.9", "LOW")],           # SR has no value for a plausible identity
            "C": [("0", "0.9", "LOW")],            # LOW alternative also below the floor
            "D": [("127.7", "0.5", "LOW")]}        # far below rank 1: not a plausible identity
    sc = _screen({k: "0" for k in "ABCD"}, margin="0.15", alts=alts)
    assert sc.member_verdict(VC, "A") == (EG.UNKNOWN, "IDENTITIES_DISAGREE")
    assert sc.member_verdict(VC, "B") == (EG.UNKNOWN, "SR_VALUE_MISSING")
    assert sc.member_state(VC, "C") == EG.ABSENT
    assert sc.member_state(VC, "D") == EG.ABSENT
    assert sc.with_margin(VC, 0).member_state(VC, "A") == EG.ABSENT           # margin 0 = rank 1 only
    # a LOW alternative never makes a member PRESENT: PRESENT is decided over the HIGH / MEDIUM identities
    pres = _screen({"P": "20"}, margin="0.15", alts={"P": [("0", "0.9", "LOW")]})
    assert pres.member_state(VC, "P") == EG.PRESENT


def test_a_usable_alternative_that_holds_the_nutrient_still_blocks_absent():
    sc = _screen({"PEP": "0"}, margin="0.15", alts={"PEP": [("127.7", "0.88", "MEDIUM")]})
    assert sc.member_state(VC, "PEP") == EG.UNKNOWN


def test_lot_absent_needs_every_member_absent_with_the_full_rule():
    sc = _screen({"A": "0", "B": "0", "M": "0"}, bands={"M": "MEDIUM"})
    assert sc.lot_state(VC, ["A", "B"]) == EG.ABSENT
    assert sc.lot_state(VC, ["A", "M"]) == EG.UNKNOWN                         # one MEDIUM member: no negative claim
    assert sc.lot_state(VC, ["A", "B"], n_unknown=1) == EG.UNKNOWN


def test_route_text_member_presence_and_blocker_fields():
    gates = _gates({POTATO: "0"}, cats={POTATO: ("", "Vegetables and Vegetable Products")})
    it, = _by_action(_items("Boil the potatoes for 20 minutes.", gates, [_row("EVD-1", POTATO, BOIL)]), "boil")
    assert it["member_presence"] == EG.UNKNOWN and it["member_blocker"] == "CATEGORY_EMPTY"
    assert it["route"] == "DIRECT" and it["gates"]["presence"] == "UNKNOWN"   # UNKNOWN keeps routing, never ABSENT
    assert it["reasons"][0] == "TARGET_PRESENCE_UNKNOWN"


def test_census_counts_category_blocked_and_absent_members():
    recs = [{"recipe_id": f"SYN-{i}", "source_family": "FOODCOM", "ingredient_lines": [],
             "steps": ["Boil the potatoes for 20 minutes.", "Roast the carrots in the oven."]} for i in range(3)]
    gates = _gates({POTATO: "0", CARROT: "0"}, cats={POTATO: VEG, CARROT: ("", "Vegetables and Vegetable Products")})
    rep = RC.census_from_records(recs, seed="9", size=3, index=RD.EvidenceIndex.from_rows([]), target_svar=VC, gates=gates)
    D.assert_counts_only(rep)
    pot = POTATO.replace("-", "__")
    assert rep["member_absent_items"] == {pot: 3}
    assert rep["category_blocked_items"] == {CARROT.replace("-", "__"): 3}
    assert rep["member_blocker"] == {"CATEGORY_EMPTY": 3}


# ------------------------------------------------------------------ the crosswalk
def test_crosswalk_is_explicit_strict_and_drafted():
    assert EG.CATEGORY_CROSSWALK_STATUS == "AI_DRAFTED_UNSIGNED"
    assert EG.category_matches("DAIRY", "Dairy and Egg Products") and EG.category_matches("EGG", "Dairy and Egg Products")
    assert EG.category_matches("MEAT", "Pork Products") and not EG.category_matches("MEAT", "Finfish and Shellfish Products")
    assert not EG.category_matches("", "Dairy and Egg Products")               # an empty ING category is never confirmed
    assert not EG.category_matches("HERB_SPICE", "Beverages")                  # "herb" -> chamomile tea
    assert not EG.category_matches("VEGETABLE", "Fats and Oils")               # "coleslaw" -> coleslaw dressing
    assert not EG.category_matches("UNKNOWN_CATEGORY", "Dairy and Egg Products")
    assert not EG.category_matches("DAIRY", None)
    with (ROOT / "registry" / "ing_sr_legacy_match_draft_v1.csv").open(newline="", encoding="utf-8") as fh:
        cats = {r["ing_category"] for r in csv.DictReader(fh)}
    assert cats - {""} <= set(EG.CATEGORY_CROSSWALK)                           # every real ING category has a crosswalk row


# ------------------------------------------------------------------ the shipped table
def test_shipped_table_has_low_band_rows_and_category_columns():
    rows = list(csv.DictReader((ROOT / "registry" / "ing_sr_target_content_draft_v1.csv").open(newline="", encoding="utf-8")))
    assert tuple(rows[0]) == EG.TABLE_COLUMNS and {"ing_category", "sr_category"} <= set(rows[0])
    assert {r["confidence_band"] for r in rows if r["candidate_rank"] != "1"} >= {"MEDIUM", "LOW"}
    assert {r["confidence_band"] for r in rows if r["candidate_rank"] == "1"} <= set(EG.USABLE_BANDS)
    cands, vals, cats = EG.read_table_full()
    assert set(cats) == set(cands)
    kinds, sources = EG.read_table_meta()
    assert set(kinds) == set(cands) and sources == {"ing_sr_defaults_v1|legacy_match_alternates"}


def test_every_absent_member_of_the_shipped_screen_satisfies_all_three_conditions():
    g = EG.EvidenceGates.load()
    sc = g.screen
    fl = sc.floors[VC]
    absent = [i for i in sc.cands if sc.member_state(VC, i) == EG.ABSENT]
    assert absent                                                           # the screen still screens something
    for i in absent:
        assert sc.cands[i][0][1] == "HIGH" and sc.category_ok(i)
        vals = [sc.values.get((f, fl.nutrient_key)) for f, _ in sc.plausible_all(VC, i)]
        assert vals and all(v is not None and v < fl.value for v in vals)
    assert g.describe()["absent_rule"].startswith("RANK1_HIGH") and g.describe()["version"] == EG.VERSION


def test_the_three_reviewer_false_absent_cases_are_now_unknown():
    """FINAL-SCI #6: ING 'herb' (chamomile tea), 'coleslaw' (coleslaw dressing), 'lemongrass' (a branded soup)."""
    sc = EG.EvidenceGates.load().screen
    for ing in ("ING-000195", "ING-001013", "ING-000250"):
        assert sc.member_state(VC, ing) != EG.ABSENT, ing


def test_absent_never_exceeds_the_s175_high_only_screen_on_the_shipped_table():
    """The full rule only removes ABSENT claims relative to the S175 interim (HIGH rank 1 + usable identities below the floor)."""
    sc = EG.EvidenceGates.load().screen
    fl = sc.floors[VC]
    for i, cs in sc.cands.items():
        interim = cs[0][1] == "HIGH" and all(
            (v := sc.values.get((f, fl.nutrient_key))) is not None and v < fl.value for f in sc.plausible(VC, i))
        if sc.member_state(VC, i) == EG.ABSENT:
            assert interim


def test_build_tool_check_passes_when_sr_is_present():
    import importlib.util
    from culinarystate.mechanism.sr_identity import default_dir
    try:
        default_dir(ROOT)
    except (StopIteration, FileNotFoundError):
        pytest.skip("SR Legacy is not on this machine")
    spec = importlib.util.spec_from_file_location("bt177", ROOT / "tools/build_target_content_table.py")
    tool = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tool)
    assert tool.main(["--check"]) == 0


def test_table_round_trip_carries_categories(tmp_path):
    cands = {"I1": ((11, "HIGH", Fraction("1.17")), (14, "LOW", Fraction("0.8")))}
    rows = EG.build_table_rows(cands, {(11, "vitamin_c"): Fraction(0), (14, "vitamin_c"): Fraction(3)}, ["vitamin_c"],
                               {"I1": ("DAIRY", "Dairy and Egg Products")})
    assert [(r["candidate_rank"], r["confidence_band"], r["ing_category"], r["sr_category"]) for r in rows] == [
        ("1", "HIGH", "DAIRY", "Dairy and Egg Products"), ("2", "LOW", "DAIRY", "Dairy and Egg Products")]
    p = tmp_path / "t.csv"
    with p.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=EG.TABLE_COLUMNS)
        w.writeheader()
        w.writerows(rows)
    c2, v2, k2 = EG.read_table_full(p)
    assert c2 == cands and k2 == {"I1": ("DAIRY", "Dairy and Egg Products")} and v2[(14, "vitamin_c")] == 3
    bad = [dict(r, confidence_band="LOW") if r["candidate_rank"] == "1" else r for r in rows]
    with p.open("w", newline="") as fh:                                       # a LOW rank-1 ING does not belong in the table
        w = csv.DictWriter(fh, fieldnames=EG.TABLE_COLUMNS)
        w.writeheader()
        w.writerows(bad)
    with pytest.raises(EG.GateError):
        EG.read_table_full(p)


# ------------------------------------------------------------------ the human-review lists
def test_review_rows_rank_by_item_count_and_carry_counts_and_registry_names_only():
    sc = _screen({"A": "0", "B": "0", "C": "7"}, cats={"A": VEG, "B": ("", VEG[1]), "C": VEG})
    rows = EG.review_rows(sc, VC, {"B": 9, "A": 40, "C": 5}, top=2)
    assert tuple(rows[0]) == EG.REVIEW_COLUMNS and [r["ing_id"] for r in rows] == ["A", "B"]
    assert [r["items"] for r in rows] == ["40", "9"] and [r["rank"] for r in rows] == ["1", "2"]
    assert rows[0]["member_verdict"] == "ABSENT" and rows[0]["blocker"] == ""
    assert rows[1]["member_verdict"] == "UNKNOWN" and rows[1]["blocker"] == "CATEGORY_EMPTY"
    assert rows[0]["floor_mg_per_100g"] == "1" and rows[0]["rank1_sr_value_mg_per_100g"] == "0"
    assert rows[0]["status"] == "AI_DRAFTED_FOR_HUMAN_REVIEW" and rows[0]["human_verdict"] == "" == rows[0]["human_note"]
    # report keys are code(ING id): ING__000123 maps back to ING-000123, ties break on the id
    tie = EG.review_rows(sc, VC, {"ING__000002": 3, "ING__000001": 3}, top=5)
    assert [r["ing_id"] for r in tie] == ["ING-000001", "ING-000002"]


def test_cli_review_from_report_writes_both_csvs_and_refuses_to_overwrite(tmp_path):
    import importlib.util
    spec = importlib.util.spec_from_file_location("rdc177", ROOT / "tools/router_demo_census.py")
    tool = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tool)
    ing_abs = next(i for i in EG.EvidenceGates.load().screen.cands
                   if EG.EvidenceGates.load().screen.member_state(VC, i) == EG.ABSENT)
    rep = {"target_svar": VC, "member_absent_items": {ing_abs.replace("-", "__"): 12},
           "category_blocked_items": {ing_abs.replace("-", "__"): 3}}
    (tmp_path / "r.json").write_text(json.dumps(rep))
    a, b = tmp_path / "abs.csv", tmp_path / "blk.csv"
    argv = ["--review-from", str(tmp_path / "r.json"), "--absent-review-csv", str(a), "--category-blocked-csv", str(b)]
    assert tool.main(argv) == 0
    rows = list(csv.DictReader(a.open(newline="", encoding="utf-8")))
    assert tuple(rows[0]) == EG.REVIEW_COLUMNS and rows[0]["ing_id"] == ing_abs and rows[0]["items"] == "12"
    assert rows[0]["ing_canonical_name"] != "" and rows[0]["rank1_sr_description"] != ""
    assert list(csv.DictReader(b.open(newline="", encoding="utf-8")))[0]["items"] == "3"
    with pytest.raises(SystemExit):
        tool.main(argv)                                                    # a review file is never overwritten
    with pytest.raises(SystemExit):
        tool.main(["--review-from", str(tmp_path / "r.json")])             # needs at least one CSV path
