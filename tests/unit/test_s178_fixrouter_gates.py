"""S178 FIX-ROUTER: SCI-B review findings R2, R3, R4, R5, R6 at the router gate (Rung A unchanged).

Each test is built from the reviewer's failure scenario (synthetic sentences, synthetic EVD rows and synthetic screens; no
recipe text, no real-data number except where a test says so). Every one of the R2-R6 scenario tests FAILS on the pre-fix
code (fc4c004) and passes after the fix; see reports/orchestration/S178_FIX-ROUTER_report.md for the RED run.
"""
from __future__ import annotations

import csv
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


def _ids(text: str) -> tuple[str, str]:
    it = RD.route_text(text, index=RD.EvidenceIndex.from_rows([]), target_svar=VC)["items"][0]
    return it["ingredient_id"], it["process_id"]


POTATO, BOIL = _ids("Boil the potatoes.")
_, FRY = _ids("Fry the potatoes.")
TOMATO, _ = _ids("Fry the tomatoes.")
EGG, _ = _ids("Fry the eggs.")
BEEF, ROAST = _ids("Roast the beef.")
SHRIMP, GRILL = _ids("Grill the shrimp.")
PEACH, CAN = next((i["ingredient_id"], i["process_id"]) for i in RD.route_text(
    "Mix fresh and canned peaches.", index=RD.EvidenceIndex.from_rows([]), target_svar=VC)["items"] if i["action"] == "canned")
_, MASH = _ids("Mash the potatoes.")
_, BAKE = _ids("Bake the potatoes.")
_, FREEZE = _ids("Freeze the potatoes.")
_, REHEAT = _ids("Reheat the potatoes.")
_, DRAIN = _ids("Drain the potatoes.")
ALL_FOODS = (POTATO, TOMATO, EGG, BEEF, SHRIMP, PEACH)
assert None not in ALL_FOODS and len(set(ALL_FOODS)) == len(ALL_FOODS)
assert CAN == "PROC-000132" and FREEZE == "PROC-000040" and REHEAT == EG.PRIOR_REHEAT_PROC


def _row(evd_id, ing, proc, raw_name=None):
    return {"id": evd_id, "version": 1, "status": "ACTIVE", "tier": "E3", "source_id": "SRC-1",
            "matrix": {"ingredient_id": ing}, "process": {"process_id": proc, "raw_name": raw_name},
            "target": {"state_variable_id": VC, "raw_name": "Vitamin C"},
            "derived": {"retention_factor": {"status": "MEASURED", "value": 60.0, "unit": "%", "raw": "60"}},
            "verification": {"status": "UNVERIFIED"}}


def _screen(values, *, basis="A", data_points=1):
    """values: ING -> mg per 100 g; every value gets SR derivation ``basis`` with ``data_points`` (None = no basis map)."""
    cands, vals = {}, {}
    for n, (ing, v) in enumerate(values.items()):
        cands[ing] = ((1000 + n, "HIGH", Fraction(1)),)
        if v is not None:
            vals[(1000 + n, "vitamin_c")] = Fraction(v)
    fl = {VC: EG.Floor(VC, "Vitamin C", "vitamin_c", "mg", Fraction(1), "PROPOSED_PILOT", Fraction(0))}
    b = None if basis is None else {k: (basis, data_points) for k in vals}
    return EG.TargetPresenceScreen(fl, cands, vals, {i: VEG for i in values}, basis=b)


def _gates(**kw):
    return EG.EvidenceGates(_screen({i: "20" for i in ALL_FOODS}), **kw)


ROWS = [_row("EVD-F1", POTATO, FRY), _row("EVD-F2", TOMATO, FRY), _row("EVD-F3", EGG, FRY), _row("EVD-B1", POTATO, BOIL),
        _row("EVD-R1", BEEF, ROAST), _row("EVD-G1", SHRIMP, GRILL), _row("EVD-C1", PEACH, CAN), _row("EVD-M1", POTATO, MASH),
        _row("EVD-K1", POTATO, BAKE), _row("EVD-H1", POTATO, REHEAT, "POTATO,REHEATED"),
        _row("EVD-D1", POTATO, DRAIN, "VEG,ROOTS,COOKED,DRAINED")]


def _items(text, gates=None, lines=None, **kw):
    return RD.route_text(text, index=RD.EvidenceIndex.from_rows(ROWS), target_svar=VC, gates=gates or _gates(),
                         ingredient_lines=lines, **kw)["items"]


def _one(items, proc, ing):
    hit = [i for i in items if i["process_id"] == proc and i["ingredient_id"] == ing]
    assert len(hit) == 1, [(i["action"], i["process_id"], i["ingredient_id"]) for i in items]
    return hit[0]


# =================================================================== R2: prior processing stated as a word / a line
@pytest.mark.parametrize("text,lines,ing,kind,basis", [
    ("Fry the baked potatoes.", None, POTATO, "HEAT", EG.PB_TEXT),
    ("Fry the mashed potatoes.", None, POTATO, "PROCESSED", EG.PB_TEXT),
    ("Fry the tinned tomatoes.", None, TOMATO, "HEAT", EG.PB_TEXT),
    ("Fry the hard-boiled eggs.", None, EGG, "HEAT", EG.PB_TEXT),
    ("1 can chopped tomatoes\nFry the tomatoes.", None, TOMATO, "HEAT", EG.PB_TEXT),         # line pasted into the text
    ("2 boiled potatoes\nFry the potatoes in the oil.", None, POTATO, "HEAT", EG.PB_TEXT),
    ("Fry the tomatoes.", ["1 can chopped tomatoes"], TOMATO, "HEAT", EG.PB_LINE),            # line passed separately
    ("Fry the potatoes in the oil.", ["2 boiled potatoes", "1 tbsp oil"], POTATO, "HEAT", EG.PB_LINE),
    ("Fry the leftover potatoes.", None, POTATO, "PROCESSED", EG.PB_TEXT),
    ("Fry the frozen potatoes.", None, POTATO, "PRESERVED", EG.PB_TEXT),
])
def test_r2_stated_prior_state_withholds_direct(text, lines, ing, kind, basis):
    it = _one(_items(text, lines=lines), FRY, ing)
    assert it["route_ungated"] == "DIRECT" and it["route"] != "DIRECT"
    assert it["reasons"][0] == EG.R_PRIOR_PROCESS and kind in it["prior_process"] and basis in it["prior_basis"]
    assert it["evidence"] == [] and it["evidence_not_applied"]                       # rows stay visible, not applied


@pytest.mark.parametrize("text,lines", [("Fry the potatoes.", None), ("Fry the uncooked potatoes.", None),
                                        ("Fry the potatoes.", ["2 large potatoes", "1 cup leftover rice"]),
                                        ("Fry the non-frozen potatoes.", None)])
def test_r2_controls_keep_direct(text, lines):
    it = _one(_items(text, lines=lines), FRY, POTATO)
    assert it["route"] == "DIRECT" and it["prior_process"] == [] and it["prior_basis"] == []


def test_r2_state_cues_are_registered_words_with_spans():
    cues = EG.state_cues("2 (15 oz) cans boiled, drained and leftover; uncooked; non-frozen")
    assert [k for _, _, k in cues] == ["HEAT", "HEAT", "LEACH", "PROCESSED"]
    assert all(0 <= s < e for s, e, _ in cues)
    assert EG.STATE_WORDS["frozen"] == "PRESERVED" and EG.STATE_WORDS["canned"] == "HEAT"   # canned follows PROC can
    assert EG.state_cues("") == [] and EG.state_cues("2 large potatoes") == []


def test_r2_ingredient_line_states_counts_only():
    counts = {}
    got = RD.ingredient_line_states(["1 can chopped tomatoes", "2 large potatoes", "", "1 cup cooked rice"],
                                    RD.RungA(), counts=counts)
    assert got[TOMATO] == {"HEAT"} and POTATO not in got
    assert counts["ingredient_lines_seen"] == 3 and counts["ingredient_lines_with_state_cue"] == 2
    assert all(isinstance(v, int) for v in counts.values())


# =================================================================== R3: attributive participles / serving suggestions
@pytest.mark.parametrize("text,proc,ing,role", [
    ("Serve with roast beef.", ROAST, BEEF, EG.ATTRIBUTIVE_STATE),
    ("Spoon the sauce over grilled shrimp.", GRILL, SHRIMP, EG.ATTRIBUTIVE_STATE),
    ("Mix fresh and canned peaches.", CAN, PEACH, EG.ATTRIBUTIVE_STATE),
    ("Add mashed potatoes and stir.", MASH, POTATO, EG.ATTRIBUTIVE_STATE),
    ("Serve with rice and roast beef.", ROAST, BEEF, EG.SERVING_SUGGESTION),
])
def test_r3_attributive_and_serving_events_never_get_direct(text, proc, ing, role):
    it = _one(_items(text), proc, ing)
    assert it["route_ungated"] == "DIRECT" and it["route"] == "UNKNOWN"
    assert it["event_role"] == role and it["reasons"][0] == EG.ROLE_REASON[role]
    assert it["evidence"] == [] and [e["evd_id"] for e in it["evidence_not_applied"]]


@pytest.mark.parametrize("text,proc,ing", [("Roast the beef.", ROAST, BEEF), ("Peel and boil potatoes.", BOIL, POTATO),
                                           ("Top with cheese and bake the potatoes for 10 minutes.", BAKE, POTATO),
                                           ("Grill the shrimp for 3 minutes.", GRILL, SHRIMP)])
def test_r3_real_steps_keep_direct(text, proc, ing):
    it = _one(_items(text), proc, ing)
    assert it["event_role"] == EG.PROCESS_STEP and it["route"] == "DIRECT"


def test_r3_attributive_state_feeds_the_food_prior_state():
    """"Add mashed potatoes" is a state of the potatoes: a later fry of them is no raw-to-fried case."""
    it = _one(_items("Add mashed potatoes and fry them."), FRY, POTATO)
    assert it["route"] != "DIRECT" and "PROCESSED" in it["prior_process"] and EG.PB_TEXT in it["prior_basis"]


def test_r3_presence_absent_does_not_turn_a_non_event_into_not_applicable():
    g = EG.EvidenceGates(_screen({BEEF: "0"}))
    it = _one(_items("Serve with roast beef.", g), ROAST, BEEF)
    assert it["route"] == "UNKNOWN" and it["reasons"][0] == EG.R_ATTRIBUTIVE           # no claim about a non-event


def test_r3_simulate_branch_is_not_run_for_a_non_event():
    calls = []

    class FakeSim:
        guard = SimpleNamespace(mode="TEST_ONLY", allowed=True, reasons=())

        def layer1(self, raw, locale):
            return {}

        def evaluate_item(self, item, **kw):
            calls.append(item["event_id"])
            return SimpleNamespace(simulated=False, as_item=lambda: {"status": "NOT_SIMULATED"}, record=None)
    items = _items("Serve with roast beef.", simulate=FakeSim())
    it = _one(items, ROAST, BEEF)
    assert it["simulate"]["status"] == "NOT_EVALUATED_NOT_A_PROCESS_STEP" and it["simulate"]["simulated"] is False
    assert it["event_id"] not in calls and calls                                       # the Serve step itself is evaluated


def test_r3_participle_rules():
    assert EG.is_participle("mashed") and EG.is_participle("frozen") and EG.is_participle("stir-fried")
    assert not EG.is_participle("shred") and not EG.is_participle("seed") and not EG.is_participle("boil")
    assert EG.is_attributive("roast", "Serve with ") and EG.is_attributive("roast", "Add ")
    assert not EG.is_attributive("roast", "Peel and ") and not EG.is_attributive("roast", "")
    assert not EG.is_attributive("boil", "Peel and ")


# =================================================================== R4: ABSENT needs analytical SR values
@pytest.mark.parametrize("code,points,state,blocker", [
    ("A", 3, EG.ABSENT, ""), ("AI", 1, EG.ABSENT, ""), ("AR", 2, EG.ABSENT, ""),
    ("A", 0, EG.UNKNOWN, EG.B_NOT_ANALYTICAL),            # analytical code but no data point
    ("Z", 0, EG.UNKNOWN, EG.B_NOT_ANALYTICAL),            # "Assumed zero"
    ("NONE", 0, EG.UNKNOWN, EG.B_NOT_ANALYTICAL),         # blank derivation, 0 data points (butter / olive oil / flour)
    ("NONE", 4, EG.UNKNOWN, EG.B_NOT_ANALYTICAL),
    ("PIK", 0, EG.UNKNOWN, EG.B_NOT_ANALYTICAL), ("FLA", 0, EG.UNKNOWN, EG.B_NOT_ANALYTICAL),
    ("LC", 1, EG.UNKNOWN, EG.B_NOT_ANALYTICAL), ("RA", 0, EG.UNKNOWN, EG.B_NOT_ANALYTICAL),
])
def test_r4_absent_only_on_analytical_values(code, points, state, blocker):
    sc = _screen({"ING-X": "0"}, basis=code, data_points=points)
    assert sc.member_verdict(VC, "ING-X") == (state, blocker)
    assert sc.lot_state(VC, ["ING-X"]) == (EG.ABSENT if state == EG.ABSENT else EG.UNKNOWN)


def test_r4_no_basis_is_fail_closed_and_present_is_unchanged():
    sc = _screen({"ING-X": "0", "ING-Y": "30"}, basis=None)
    assert sc.member_verdict(VC, "ING-X") == (EG.UNKNOWN, EG.B_BASIS_NOT_RECORDED)
    assert sc.member_verdict(VC, "ING-Y") == (EG.PRESENT, "")                      # PRESENT needs no basis (unchanged)


def test_r4_one_non_analytical_alternate_blocks_absent():
    fl = {VC: EG.Floor(VC, "Vitamin C", "vitamin_c", "mg", Fraction(1), "PROPOSED_PILOT", Fraction("0.2"))}
    cands = {"ING-X": ((1, "HIGH", Fraction(1)), (2, "LOW", Fraction("0.9")))}
    vals = {(1, "vitamin_c"): Fraction(0), (2, "vitamin_c"): Fraction(0)}
    sc = EG.TargetPresenceScreen(fl, cands, vals, {"ING-X": VEG}, basis={(1, "vitamin_c"): ("A", 2), (2, "vitamin_c"): ("Z", 0)})
    assert sc.member_verdict(VC, "ING-X") == (EG.UNKNOWN, EG.B_NOT_ANALYTICAL)
    b = sc.member_basis(VC, "ING-X")
    assert [(x["fdc_id"], x["sr_derivation_code"], x["sr_data_points"], x["analytical"]) for x in b] == \
           [(1, "A", 2, True), (2, "Z", 0, False)]
    assert EG.basis_summary(b) == ("A|Z", "2|0", "NO")


def test_r4_basis_is_kept_in_the_gate_output_and_review_rows():
    g = EG.EvidenceGates(_screen({POTATO: "0"}, basis="Z", data_points=0))
    it = _one(_items("Fry the potatoes.", g), FRY, POTATO)
    assert it["member_blocker"] == EG.B_NOT_ANALYTICAL and it["route"] == "DIRECT"   # UNKNOWN presence keeps routing
    assert it["member_sr_basis"] == [{"fdc_id": 1000, "band": "HIGH", "value": "0", "sr_derivation_code": "Z",
                                      "sr_data_points": 0, "analytical": False}]
    rows = EG.review_rows(g.screen, VC, {EG.code_key(POTATO): 5})
    assert set(EG.REVIEW_COLUMNS) >= {"plausible_sr_derivation_codes", "plausible_sr_data_points", "all_plausible_analytical"}
    assert (rows[0]["plausible_sr_derivation_codes"], rows[0]["plausible_sr_data_points"],
            rows[0]["all_plausible_analytical"]) == ("Z", "0", "NO")


def _csv(path, head, rows):
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(head)
        w.writerows(rows)


def test_r4_sr_records_read_derivation_and_data_points(tmp_path):
    _csv(tmp_path / "food_nutrient.csv", ["id", "fdc_id", "nutrient_id", "amount", "data_points", "derivation_id"],
         [["1", "10", "1162", "0", "3", "1"], ["2", "11", "1162", "0", "0", ""], ["3", "12", "1162", "0", "", "68"],
          ["4", "13", "1162", "", "1", "1"]])
    _csv(tmp_path / "food_nutrient_derivation.csv", ["id", "code", "description", "source_id"],
         [["1", "A", "Analytical", "1"], ["68", "Z", "Assumed zero", "5"]])
    got = EG.read_sr_records(tmp_path, {10, 11, 12, 13}, ["vitamin_c"])
    assert got == {(10, "vitamin_c"): (Fraction(0), "A", 3), (11, "vitamin_c"): (Fraction(0), EG.NO_DERIVATION_CODE, 0),
                   (12, "vitamin_c"): (Fraction(0), "Z", 0)}                             # an empty amount stays absent
    assert EG.read_sr_basis(tmp_path, {10}, ["vitamin_c"]) == {(10, "vitamin_c"): ("A", 3)}
    (tmp_path / "food_nutrient_derivation.csv").unlink()
    assert EG.read_sr_records(tmp_path, {10}, ["vitamin_c"])[(10, "vitamin_c")][1] == EG.NOT_RECORDED_CODE


def test_r4_content_table_round_trip_and_old_table_is_fail_closed(tmp_path):
    cands = {"ING-X": ((10, "HIGH", Fraction(1)),), "ING-Y": ((11, "HIGH", Fraction(1)),)}
    vals = {(10, "vitamin_c"): Fraction(0), (11, "vitamin_c"): Fraction(0)}
    rows = EG.build_table_rows(cands, vals, ["vitamin_c"], {"ING-X": VEG, "ING-Y": VEG},
                               {(10, "vitamin_c"): ("A", 2), (11, "vitamin_c"): ("Z", 0)})
    p = tmp_path / "t.csv"
    with p.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=EG.TABLE_COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    assert EG.read_table_basis(p) == {(10, "vitamin_c"): ("A", 2), (11, "vitamin_c"): ("Z", 0)}
    old = tmp_path / "old.csv"
    old_cols = [c for c in EG.TABLE_COLUMNS if not c.startswith("sr_d")]
    with old.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=old_cols, lineterminator="\n", extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    assert EG.read_table_basis(old) is None


def test_r4_shipped_table_carries_the_basis_and_every_absent_member_is_analytical():
    """Real shipped table (structural facts only): the basis columns are filled and every ABSENT member is analytical."""
    g = EG.EvidenceGates.load()
    sc = g.screen
    assert sc.basis is not None and len(sc.basis) == len(sc.values)
    assert g.describe()["analytical_derivation_codes"] == ["A", "AI", "AR"]
    for i in sc.cands:
        if sc.member_state(VC, i) == EG.ABSENT:
            assert all(b["analytical"] for b in sc.member_basis(VC, i)), i


def test_r4_wording_measured_composition_is_gone():
    for rel in ("src/culinarystate/mechanism/evidence_gates.py", "src/culinarystate/decision/demo_context.py"):
        text = (ROOT / rel).read_text(encoding="utf-8").lower()
        assert "measured composition" not in text and "measured sr legacy composition" not in text, rel


# =================================================================== R5: fail-closed context
def _ent(eid, ing=None, parents=()):
    attrs = (SimpleNamespace(field="ingredient_id", value=ing),) if ing else ()
    return SimpleNamespace(entity_id=eid, entity_type="X", attributes=attrs, parent_entity_ids=tuple(parents), span=None)


def _ev(eid, proc, produces):
    attrs = (SimpleNamespace(field="proc_id", value=proc),) if proc else ()
    return SimpleNamespace(event_id=eid, attributes=attrs, produces=tuple(produces), consumes=(), discards=(), span=None)


def test_r5a_unresolved_ancestor_event_withholds_direct():
    graph = SimpleNamespace(entities=[_ent("N1", ing=POTATO), _ent("N2", parents=("N1",))],
                            events=[_ev("E1", None, ["N2"])])
    m = EG.lot_members(graph)
    assert m["N2"].prior == {"UNRESOLVED"} and m["N2"].prior_basis == {EG.PB_UNRESOLVED}
    r = _gates().evaluate(svar_id=VC, ing=POTATO, raw_precheck="DIRECT", lots=[m["N2"]])
    assert r.final_precheck == "NONE" and r.withheld and r.reasons[0] == EG.R_PRIOR_UNRESOLVED
    assert EG.R_PRIOR_PROCESS not in r.reasons
    graph.events = [_ev("E1", "PROC-999999", ["N2"])]                                  # a process the hierarchy lacks
    assert EG.lot_members(graph)["N2"].prior == {"UNRESOLVED"}


def test_r5b_no_lot_cannot_keep_a_raw_direct():
    r = _gates().evaluate(svar_id=VC, ing=POTATO, raw_precheck="DIRECT", lots=[])
    assert r.lot_context == EG.NO_LOT and r.final_precheck == "NONE" and r.withheld
    assert r.reasons[0] == EG.R_LOT_UNKNOWN
    r = _gates().evaluate(svar_id=VC, ing=None, raw_precheck="NONE", lots=[])
    assert r.final_precheck == "NONE" and not r.withheld                               # nothing to withhold


# =================================================================== R6: prior-process classes
def test_r6_freeze_then_fry_is_a_prior_process():
    it = _one(_items("Freeze the potatoes. Fry the potatoes."), FRY, POTATO)
    assert it["route"] != "DIRECT" and it["prior_process"] == ["PRESERVED"] and it["prior_basis"] == [EG.PB_EVENT]
    assert EG.prior_kind(FREEZE) == "PRESERVED" and EG.prior_kind("PROC-000041") == "PRESERVED"


def test_r6_reheat_and_drain_of_cooked_rows_stay_withheld_until_a_human_decides():
    """The exemption would LOOSEN the S177 rule (D-071): OFF by default, only counted; a human may switch it on."""
    for text, proc in (("Boil the potatoes. Reheat the potatoes.", REHEAT), ("Boil the potatoes. Drain the potatoes.", DRAIN)):
        it = _one(_items(text), proc, POTATO)
        assert it["route"] != "DIRECT" and it["prior_presupposed"] is True and EG.R_PRIOR_PROCESS in it["reasons"]
        on = _one(_items(text, EG.EvidenceGates(_gates().screen, exempt_presupposed=True)), proc, POTATO)
        assert on["route"] == "DIRECT"                                                 # what the human switch would do
    fry = _one(_items("Boil the potatoes. Fry the potatoes."), FRY, POTATO)
    assert fry["prior_presupposed"] is False                                           # a raw-to-fried row presupposes nothing
    assert EG.presupposes_prior_heat(REHEAT, None) and EG.presupposes_prior_heat(DRAIN, "VEG,CKD FROM FRZN,DRAINED")
    assert not EG.presupposes_prior_heat(DRAIN, "BEANS,CANNED,DRAINED") and not EG.presupposes_prior_heat(FRY, "COOKED")
    assert _gates().describe()["presupposed_prior_heat_exemption_applied"] is False


# =================================================================== census
def test_census_v040_passes_ingredient_lines_and_counts_new_codes_only():
    recs = [{"recipe_id": f"R{i}", "source_family": "WIKIBOOKS", "steps": [s], "ingredient_lines": lines}
            for i, (s, lines) in enumerate([("Fry the potatoes.", ["2 boiled potatoes"]),
                                            ("Serve with roast beef.", ["1 lb beef"]),
                                            ("Freeze the potatoes. Fry the potatoes.", []),
                                            ("Fry the potatoes.", ["2 potatoes"])])]
    rep = RC.census_from_records(recs, seed="t", size=10, index=RD.EvidenceIndex.from_rows(ROWS), target_svar=VC,
                                 gates=_gates())
    assert RC.CENSUS_VERSION == "router-demo-census-0.4.0-draft"
    assert rep["route"].get("DIRECT") == 1 and rep["route_ungated"]["DIRECT"] == 4
    assert rep["prior_process_withheld_by_basis"] == {"EVENT": 1, "INGREDIENT_LINE": 1}
    assert rep["event_role"].get("ATTRIBUTIVE_STATE") == 1
    assert rep["direct_ungated_by_role"].get("ATTRIBUTIVE_STATE__UNKNOWN", rep["direct_ungated_by_role"].get(
        "ATTRIBUTIVE_STATE|UNKNOWN")) == 1
    assert rep["ingredient_lines"]["ingredient_lines_seen"] == 3 and rep["ingredient_lines"]["ingredient_lines_with_state_cue"] == 1
    assert isinstance(rep["prior_presupposed_would_release"], int) and "sr_not_analytical_items" in rep
    D.assert_counts_only(rep)


def test_r3_share_counter_marks_non_events_that_would_otherwise_be_direct():
    it = _one(_items("Serve with roast beef."), ROAST, BEEF)
    assert it["direct_if_process_step"] is True                                    # only the role rule withholds it
    absent = _one(_items("Serve with roast beef.", EG.EvidenceGates(_screen({BEEF: "0"}))), ROAST, BEEF)
    assert absent["direct_if_process_step"] is False                               # ABSENT would have taken it anyway
    rec = [{"recipe_id": "R1", "source_family": "WIKIBOOKS", "steps": ["Serve with roast beef."], "ingredient_lines": []}]
    rep = RC.census_from_records(rec, seed="t", size=5, index=RD.EvidenceIndex.from_rows(ROWS), target_svar=VC, gates=_gates())
    assert rep["non_step_direct_withheld_only_by_role"] == {"ATTRIBUTIVE_STATE": 1}
