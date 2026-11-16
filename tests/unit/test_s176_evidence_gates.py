"""S176 / L-ROUTER: target-presence screen + lot-context gate before G0 (NON_CITABLE demo mode; 23a engine unchanged).

Synthetic screens and EVD rows only: no real-data number here. The real registry files are checked for shape and,
when SR Legacy is on disk, for agreement with the shipped derived table.
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
FLOOR = Fraction(1)


def _ids() -> dict[str, tuple[str, str]]:
    """(ING id, PROC id) of the sentences used below, found through the real linker (no hard-coded ids)."""
    idx = RD.EvidenceIndex.from_rows([])
    out = {}
    for name, text in (("potato", "Boil the potatoes for 20 minutes."), ("carrot", "Roast the carrots in the oven."),
                       ("egg", "Bake the eggs for 10 minutes."), ("potato_simmer", "Simmer the potatoes.")):
        it = RD.route_text(text, index=idx, target_svar=VC)["items"][0]
        out[name] = (it["ingredient_id"], it["process_id"])
    return out


IDS = _ids()
POTATO, CARROT, EGG = IDS["potato"][0], IDS["carrot"][0], IDS["egg"][0]
assert len({POTATO, CARROT, EGG}) == 3


def _row(evd_id, ing, proc, svar=VC, status="MEASURED"):
    return {"id": evd_id, "version": 1, "status": "ACTIVE", "tier": "E3", "source_id": "SRC-1",
            "matrix": {"ingredient_id": ing}, "process": {"process_id": proc},
            "target": {"state_variable_id": svar, "raw_name": "Vitamin C"},
            "derived": {"retention_factor": {"status": status, "value": 60.0, "unit": "%", "raw": "60"}},
            "verification": {"status": "UNVERIFIED"}}


def _floors(value=FLOOR, svar=VC, margin=Fraction(0)):
    return {svar: EG.Floor(svar, "Vitamin C", "vitamin_c", "mg", Fraction(value), "PROPOSED_PILOT", Fraction(margin))}


def _screen(values: dict[str, str | None], floor=FLOOR, bands=None, alts=None, margin=0,
            cats=None) -> EG.TargetPresenceScreen:
    """values: ING id -> mg per 100 g (None = SR has no value). Each ING gets its own synthetic SR food (score 1).
    alts: ING id -> [(mg per 100 g or None, match score)] extra HIGH / MEDIUM candidates of rank 2, 3, ...
    S177 (FINAL-SCI #6 encoded: ABSENT now needs a confirmed ING category): each ING gets a MATCHING (ING category, SR
    group) pair unless ``cats`` is given ({} = no category information at all)."""
    cands, vals = {}, {}
    for n, (ing, v) in enumerate(values.items()):
        fdc = 1000 + 10 * n
        cs = [(fdc, (bands or {}).get(ing, "HIGH"), Fraction(1))]
        if v is not None:
            vals[(fdc, "vitamin_c")] = Fraction(v)
        for k, (av, sc) in enumerate((alts or {}).get(ing, ()), 1):
            cs.append((fdc + k, "MEDIUM", Fraction(str(sc))))
            if av is not None:
                vals[(fdc + k, "vitamin_c")] = Fraction(av)
        cands[ing] = tuple(cs)
    if cats is None:
        cats = {ing: ("VEGETABLE", "Vegetables and Vegetable Products") for ing in values}
    return EG.TargetPresenceScreen(_floors(floor, margin=margin), cands, vals, cats,
                                   basis={k: ("A", 1) for k in vals})  # S178 R4: synthetic SR values are analytical


def _gates(values, **kw) -> EG.EvidenceGates:
    return EG.EvidenceGates(_screen(values), **kw)


def _items(text, gates, rows, svar=VC):
    out = RD.route_text(text, index=RD.EvidenceIndex.from_rows(rows), target_svar=svar, gates=gates)
    return out, out["items"]


# ------------------------------------------------------------------ presence screen: member and lot states
def test_member_state_floor_unknown_and_band_rules():
    sc = _screen({"A": "1", "B": "0.999", "C": None, "D": "50"}, bands={"D": "MEDIUM"})
    assert sc.member_state(VC, "A") == EG.PRESENT            # value == floor counts as present (>=)
    assert sc.member_state(VC, "B") == EG.ABSENT
    assert sc.member_state(VC, "C") == EG.UNKNOWN            # SR has no value: UNKNOWN is never 0
    assert sc.member_state(VC, "D") == EG.PRESENT            # MEDIUM is usable
    assert sc.member_state(VC, "Z") == EG.UNKNOWN            # no usable SR match
    assert sc.member_state(VC, None) == EG.UNKNOWN


def test_lot_state_present_absent_unknown_and_not_screened():
    sc = _screen({"A": "0", "B": "0", "P": "20", "U": None})
    assert sc.lot_state(VC, ["A", "B"]) == EG.ABSENT
    assert sc.lot_state(VC, ["A", "B", "P"]) == EG.PRESENT   # one present member is enough
    assert sc.lot_state(VC, ["A", "U"]) == EG.UNKNOWN        # an unknown member blocks ABSENT
    assert sc.lot_state(VC, ["A", "B"], n_unknown=1) == EG.UNKNOWN   # a root of unknown identity blocks ABSENT
    assert sc.lot_state(VC, ["A", "P"], n_unknown=1) == EG.PRESENT
    assert sc.lot_state(VC, []) == EG.UNKNOWN                # nothing known is not "absent"
    assert sc.lot_state("SVAR-NO-FLOOR", ["A"]) == EG.NOT_SCREENED
    assert sc.lot_state(None, ["A"]) == EG.NOT_SCREENED


def test_floor_sensitivity_changes_only_the_threshold():
    sc = _screen({"A": "1.6"})
    assert sc.member_state(VC, "A") == EG.PRESENT
    assert sc.with_floor(VC, "2.0").member_state(VC, "A") == EG.ABSENT
    assert sc.floors[VC].value == 1                        # the original screen is untouched


def test_candidates_are_read_from_the_match_registry(tmp_path):
    p = tmp_path / "m.csv"
    cols = ["ing_id", "rank", "fdc_id", "confidence_band", "score"]
    rows = [("I1", "1", "11", "HIGH", "1.1"), ("I1", "2", "12", "MEDIUM", "0.95"), ("I1", "3", "13", "LOW", "0.9"),
            ("I2", "1", "21", "LOW", "0.7"), ("I2", "2", "22", "MEDIUM", "0.69"),       # rank 1 unusable: no identity
            ("I3", "0", "", "NONE", ""), ("I4", "1", "41", "MEDIUM", "0.8"), ("I4", "4", "44", "MEDIUM", "0.79")]
    with p.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        w.writerows(rows)
    # S177 (FINAL-SCI #6 encoded): the LOW rank-3 row is KEPT (a plausible alternative identity the ABSENT screen must see);
    # rank 4 and an unusable rank 1 are still dropped
    assert EG.read_candidates(p) == {"I1": ((11, "HIGH", Fraction("1.1")), (12, "MEDIUM", Fraction("0.95")),
                                            (13, "LOW", Fraction("0.9"))),
                                     "I4": ((41, "MEDIUM", Fraction("0.8")),)}
    assert EG.read_top1(p) == {"I1": (11, "HIGH"), "I4": (41, "MEDIUM")}


def test_identity_ambiguity_blocks_absent_but_distant_neighbours_do_not():
    """The 'pepper' case: black pepper (0 mg) at rank 1, sweet red pepper (127.7 mg) 0.12 below."""
    alts = {"PEP": [("127.7", "0.88")], "SALT": [("57", "0.60")]}      # PEP alt is 0.12 below rank 1 (score 1); SALT's 0.40
    vals = {"PEP": "0", "SALT": "0", "ONION": "7.4"}
    narrow = _screen(vals, alts=alts, margin="0.10")
    assert narrow.member_state(VC, "PEP") == EG.ABSENT                  # margin 0.10 does not see the alternative
    wide = _screen(vals, alts=alts, margin="0.15")
    assert wide.member_state(VC, "PEP") == EG.UNKNOWN                   # plausible identities disagree: no ABSENT claim
    assert wide.member_state(VC, "SALT") == EG.ABSENT                   # a lexical neighbour far below is not plausible
    assert wide.lot_state(VC, ["PEP"]) == EG.UNKNOWN and wide.lot_state(VC, ["SALT"]) == EG.ABSENT
    assert narrow.with_margin(VC, "0.15").member_state(VC, "PEP") == EG.UNKNOWN
    assert wide.with_margin(VC, 0).member_state(VC, "PEP") == EG.ABSENT  # margin 0 = rank 1 only
    assert wide.floors[VC].margin == Fraction("0.15")                    # the original screen is untouched


def test_all_plausible_candidates_must_agree_for_present_and_a_missing_value_is_unknown():
    s = _screen({"A": "20", "B": "20", "C": "20"}, margin="0.2", alts={"A": [("30", "0.95")], "B": [("0.5", "0.95")],
                                                                      "C": [(None, "0.95")]})
    assert s.member_state(VC, "A") == EG.PRESENT                        # both >= floor
    assert s.member_state(VC, "B") == EG.UNKNOWN                        # one below the floor: ambiguous
    assert s.member_state(VC, "C") == EG.UNKNOWN                        # SR has no value for a plausible identity


def test_real_floor_file_is_unsigned_proposed_and_positive():
    fl = EG.read_floors()
    assert VC in fl and fl[VC].status == "PROPOSED_PILOT" and fl[VC].value > 0 and fl[VC].unit == "mg"
    assert fl[VC].margin == Fraction("0.15")
    with (ROOT / "registry" / "target_presence_floor_v1_PROPOSED.csv").open(newline="", encoding="utf-8") as fh:
        assert all(r["human_decision"] == "" for r in csv.DictReader(fh))     # AI never signs the floor


def test_floor_file_refuses_zero_floor_unknown_key_and_wrong_unit(tmp_path):
    head = ("target_svar_id,target_name,sr_nutrient_key,unit,basis,floor_value,identity_score_margin,status,"
            "sensitivity_values,provenance,human_decision,notes\n")
    for bad in ("S1,x,vitamin_c,mg,b,0,0.1,PROPOSED_PILOT,,,,", "S1,x,not_a_key,mg,b,1,0.1,PROPOSED_PILOT,,,,",
                "S1,x,vitamin_c,g,b,1,0.1,PROPOSED_PILOT,,,,", "S1,x,vitamin_c,mg,b,abc,0.1,PROPOSED_PILOT,,,,",
                "S1,x,vitamin_c,mg,b,1,-0.1,PROPOSED_PILOT,,,,", "S1,x,vitamin_c,mg,b,1,,PROPOSED_PILOT,,,,"):
        p = tmp_path / "f.csv"
        p.write_text(head + bad + "\n")
        with pytest.raises(EG.GateError):
            EG.read_floors(p)


# ------------------------------------------------------------------ derived content table
def test_table_round_trip_keeps_unknown_empty_and_exact_decimals(tmp_path):
    cands = {"I1": ((11, "HIGH", Fraction("1.17")), (14, "MEDIUM", Fraction("0.8968"))),
             "I2": ((12, "MEDIUM", Fraction("0.9")),)}
    values = {(11, "vitamin_c"): Fraction(8, 5), (12, "vitamin_c"): Fraction(0)}
    rows = EG.build_table_rows(cands, values, ["vitamin_c"])
    assert [(r["ing_id"], r["candidate_rank"], r["amount_per_100g"]) for r in rows] == [
        ("I1", "1", "1.6"), ("I1", "2", ""), ("I2", "1", "0")]            # 14 has no SR value: empty, not 0
    p = tmp_path / "t.csv"
    with p.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=EG.TABLE_COLUMNS)
        w.writeheader()
        w.writerows(rows)
    c2, vals = EG.read_table(p)
    assert c2 == cands and vals == values                                  # exact round trip; empty stays absent
    assert (14, "vitamin_c") not in vals
    with pytest.raises(EG.GateError):
        EG._dec(Fraction(1, 3))
    with p.open("w", newline="") as fh:                                     # an ING without its rank-1 row is refused
        w = csv.DictWriter(fh, fieldnames=EG.TABLE_COLUMNS)
        w.writeheader()
        w.writerows([r for r in rows if not (r["ing_id"] == "I1" and r["candidate_rank"] == "1")])
    with pytest.raises(EG.GateError):
        EG.read_table(p)


def test_shipped_table_matches_sr_legacy_when_present():
    from culinarystate.lotstate.sr_legacy import default_dir
    try:
        sr = default_dir(ROOT)
    except (StopIteration, FileNotFoundError):
        pytest.skip("SR Legacy is not on this machine")
    from culinarystate.mechanism import sr_identity as SI
    cands_t, vals_t = EG.read_table()
    # S177 consolidation (identity of record = ing_sr_defaults_v1 via mechanism/sr_identity): the shipped table is the
    # adapter's identity, no longer the legacy match file's (which survives only as alternates / fallback)
    assert cands_t == SI.build_identity().cands
    vals_sr = EG.read_sr_values(sr, {f for c in cands_t.values() for f, _, _ in c}, {"vitamin_c"})
    assert {k: v for k, v in vals_t.items()} == vals_sr


def test_shipped_table_screen_matches_direct_sr_screen():
    pytest.importorskip("culinarystate.lotstate.sr_legacy")
    g = EG.EvidenceGates.load()
    assert g.describe()["content_source"] == "table" and g.describe()["status"].endswith("UNSIGNED")
    assert g.screen.floors[VC].value == EG.read_floors()[VC].value


# ------------------------------------------------------------------ lot membership from a graph
def _ent(eid, etype="INGREDIENT_LOT", ing=None, parents=()):
    attrs = (SimpleNamespace(field="ingredient_id", value=ing),) if ing else ()
    return SimpleNamespace(entity_id=eid, entity_type=etype, attributes=attrs, parent_entity_ids=tuple(parents))


def test_lot_members_known_merged_and_unknown_roots():
    g = SimpleNamespace(entities=[_ent("N1", ing="ING-A"), _ent("N2", ing="ING-B"), _ent("N3", "MIXTURE"),
                                  _ent("N4", "MIXTURE", parents=("N1", "N2")),
                                  _ent("N5", "INTERMEDIATE", parents=("N1",)),
                                  _ent("N6", "INTERMEDIATE", parents=("N4", "N3")),
                                  _ent("N7", "INTERMEDIATE", parents=("GHOST",))])
    m = EG.lot_members(g)
    assert m["N1"].sole == "ING-A" and m["N5"].sole == "ING-A"          # a transform keeps the sole member
    assert m["N4"].ings == {"ING-A", "ING-B"} and m["N4"].sole is None   # merged
    assert m["N3"].ings == frozenset() and m["N3"].unknown == 1          # a named mixture nobody produced
    assert m["N6"].ings == {"ING-A", "ING-B"} and m["N6"].unknown == 1 and m["N6"].sole is None
    assert m["N7"].unknown == 1                                           # a dangling parent is unknown identity
    assert [x.sole for x in EG.lots_of(m, ["N5", "N4"], "ING-A")] == ["ING-A", None]
    assert EG.lots_of(m, ["N3"], None) == [m["N3"]]


# ------------------------------------------------------------------ route_text with gates
def test_without_gates_the_demo_is_unchanged():
    ing, proc = IDS["potato"]
    out, (it,) = _items("Boil the potatoes for 20 minutes.", None, [_row("EVD-1", ing, proc)])
    assert it["route"] == "DIRECT" and [e["evd_id"] for e in it["evidence"]] == ["EVD-1"]
    assert "gates" not in it and "route_ungated" not in it and out["gates"] == {"enabled": False}
    assert out["citable"] is False and "NON_CITABLE" in out["labels"] and out["conditions_consumed"] is False


def test_present_single_member_keeps_direct_with_evidence():
    ing, proc = IDS["potato"]
    _, (it,) = _items("Boil the potatoes for 20 minutes.", _gates({POTATO: "19.7"}), [_row("EVD-1", ing, proc)])
    assert it["route"] == "DIRECT" and it["route_ungated"] == "DIRECT"
    assert it["gates"] == {"presence": "PRESENT", "lot_context": "SINGLE_MEMBER"}
    assert [e["evd_id"] for e in it["evidence"]] == ["EVD-1"] and it["evidence_not_applied"] == []
    assert not set(it["reasons"]) & set(EG.GATE_REASONS) and "EVIDENCE_PREEMPTS" in it["reasons"]


def test_absent_target_routes_not_applicable_and_withholds_the_row():
    ing, proc = IDS["egg"]
    _, (it,) = _items("Bake the eggs for 10 minutes.", _gates({EGG: "0"}), [_row("EVD-2", ing, proc)])
    assert it["route"] == "NOT_APPLICABLE" and it["route_ungated"] == "DIRECT"
    assert it["reasons"][0] == "TARGET_ABSENT" and "EVIDENCE_PREEMPTS" not in it["reasons"]
    assert it["evidence"] == [] and [e["evd_id"] for e in it["evidence_not_applied"]] == ["EVD-2"]
    assert it["gates"]["presence"] == "ABSENT"


def test_absent_target_is_not_applicable_even_without_an_evd_row():
    _, (it,) = _items("Bake the eggs for 10 minutes.", _gates({EGG: "0"}), [])
    assert it["route"] == "NOT_APPLICABLE" and it["route_ungated"] == "UNKNOWN" and it["evidence_not_applied"] == []


def test_unknown_presence_keeps_routing_and_adds_reason():
    ing, proc = IDS["potato"]
    for values in ({}, {POTATO: None}):                       # no usable match / SR has no value
        _, (it,) = _items("Boil the potatoes for 20 minutes.", _gates(values), [_row("EVD-1", ing, proc)])
        assert it["route"] == "DIRECT" and it["gates"]["presence"] == "UNKNOWN"
        assert it["reasons"][0] == "TARGET_PRESENCE_UNKNOWN"
    _, (it,) = _items("Boil the potatoes for 20 minutes.", _gates({POTATO: "20"}, presence=False),
                      [_row("EVD-1", ing, proc)])
    assert it["gates"]["presence"] == "NOT_SCREENED" and it["route"] == "DIRECT"


MERGED_TEXT = "Add the carrots and the potatoes. Simmer for 10 minutes."


def test_merged_lot_withholds_direct_and_downgrades_to_the_engine_order():
    proc = IDS["potato_simmer"][1]
    rows = [_row("EVD-3", POTATO, proc), _row("EVD-4", CARROT, proc)]
    _, items = _items(MERGED_TEXT, _gates({POTATO: "19.7", CARROT: "5.9"}), rows)
    simmer = [i for i in items if i["action"].lower() == "simmer"]
    assert {i["ingredient_id"] for i in simmer} == {POTATO, CARROT}
    for it in simmer:
        assert it["route_ungated"] == "DIRECT" and it["route"] == "UNKNOWN"           # no mechanism in the demo
        assert it["gates"]["lot_context"] == "MERGED" and it["reasons"][0] == "MERGED_LOT_CONTEXT"
        assert it["evidence"] == [] and len(it["evidence_not_applied"]) == 1
        assert "EVIDENCE_PREEMPTS" not in it["reasons"]


def test_context_gate_can_be_switched_off_independently():
    proc = IDS["potato_simmer"][1]
    _, items = _items(MERGED_TEXT, _gates({POTATO: "19.7", CARROT: "5.9"}, context=False),
                      [_row("EVD-3", POTATO, proc)])
    it = next(i for i in items if i["action"].lower() == "simmer" and i["ingredient_id"] == POTATO)
    assert it["route"] == "DIRECT" and it["gates"]["lot_context"] == "MERGED"


def test_merged_lot_of_all_absent_members_is_absent_not_merged():
    proc = IDS["potato_simmer"][1]
    _, items = _items(MERGED_TEXT, _gates({POTATO: "0", CARROT: "0"}), [_row("EVD-3", POTATO, proc)])
    it = next(i for i in items if i["action"].lower() == "simmer" and i["ingredient_id"] == POTATO)
    assert it["route"] == "NOT_APPLICABLE" and it["reasons"][0] == "TARGET_ABSENT"      # presence precedes context


def test_target_without_a_floor_row_is_not_screened_and_unchanged():
    ing, proc = IDS["egg"]
    other = "SVAR-000001"
    rows = [_row("EVD-5", ing, proc, svar=other)]
    _, (it,) = _items("Bake the eggs for 10 minutes.", _gates({EGG: "0"}), rows, svar=other)
    assert it["gates"]["presence"] == "NOT_SCREENED" and it["route"] == "DIRECT"
    assert not set(it["reasons"]) & set(EG.GATE_REASONS)


def test_gates_never_upgrade_a_route():
    """Property: over random EVD indexes, screens and texts, a gated route is never stronger than the ungated one."""
    texts = ["Boil the potatoes for 20 minutes. Roast the carrots in the oven. Bake the eggs.", MERGED_TEXT,
             "Bake the eggs for 10 minutes. Mix the eggs and the potatoes together into a batter. Bake the mixture.",
             "Stir well. Boil the potatoes.", "Fry the carrots. Boil the water."]
    keys = [IDS["potato"], IDS["carrot"], IDS["egg"], IDS["potato_simmer"], (POTATO, "PROC-000009"),
            (CARROT, "PROC-000020"), (EGG, "PROC-000001")]
    rng = random.Random(176)
    for _ in range(40):
        rows = [_row(f"E{n}", i, p) for n, (i, p) in enumerate(rng.sample(keys, rng.randint(0, len(keys))))]
        vals = {i: rng.choice(["0", "0.5", "1", "5", None]) for i in (POTATO, CARROT, EGG)}
        gates = _gates(vals, presence=rng.random() < 0.8, context=rng.random() < 0.8)
        for text in texts:
            _, items = _items(text, gates, rows)
            for it in items:
                if it["route"] == EG.NOT_APPLICABLE:
                    continue
                assert EG.ROUTE_STRENGTH[it["route"]] <= EG.ROUTE_STRENGTH[it["route_ungated"]]
                if it["route"] == "DIRECT":
                    assert it["route_ungated"] == "DIRECT" and it["evidence"] and not it["evidence_not_applied"]


def test_deterministic_and_labels_unchanged():
    ing, proc = IDS["egg"]
    g, rows = _gates({EGG: "0"}), [_row("EVD-2", ing, proc)]
    a, _ = _items("Bake the eggs for 10 minutes.", g, rows)
    b, _ = _items("Bake the eggs for 10 minutes.", g, rows)
    assert a == b and a["labels"] == list(RD.LABELS)
    with pytest.raises(RD.DemoRefused):
        RD.assert_citable(a)


# ------------------------------------------------------------------ census with gates
def _records(n=6):
    return [{"recipe_id": f"SYN-{i}", "source_family": "FOODCOM", "ingredient_lines": ["2 eggs"],
             "steps": ["Bake the eggs for 10 minutes.", "Boil the potatoes for 20 minutes.", MERGED_TEXT]}
            for i in range(n)]


def test_census_counts_gated_and_ungated_in_one_pass_counts_only():
    rows = [_row("E1", *IDS["egg"]), _row("E2", *IDS["potato"]), _row("E3", POTATO, IDS["potato_simmer"][1])]
    gates = _gates({EGG: "0", POTATO: "19.7", CARROT: "5.9"})
    idx = RD.EvidenceIndex.from_rows(rows)
    rep = RC.census_from_records(_records(), seed="7", size=6, index=idx, target_svar=VC, gates=gates)
    D.assert_counts_only(rep)
    assert sum(rep["route"].values()) == sum(rep["route_ungated"].values()) == rep["items"]
    assert rep["route_ungated"]["DIRECT"] == 18          # egg bake, potato boil, potato simmer in the merged lot (x6)
    assert rep["route"]["DIRECT"] == 6 and rep["route"]["NOT_APPLICABLE"] >= 6
    cross = rep["direct_ungated_cross"]
    assert sum(cross.values()) == rep["route_ungated"]["DIRECT"]
    assert cross["ABSENT__SINGLE_MEMBER__NOT_APPLICABLE"] == 6        # egg x bake
    assert cross["PRESENT__SINGLE_MEMBER__DIRECT"] == 6               # potato x boil
    assert cross["PRESENT__MERGED__UNKNOWN"] == 6                     # potato x simmer in the merged lot
    assert rep["recipes_with_any_direct"] == 6 and rep["recipes_with_any_direct_ungated"] == 6
    assert rep["gates"]["enabled"] is True and rep["census_version"] == RC.CENSUS_VERSION   # S177: version bumped to 0.3.0
    assert sum(rep["gate_cross"].values()) == rep["items"]


def test_census_without_gates_has_no_gate_fields_and_old_semantics():
    rep = RC.census_from_records(_records(2), seed="7", size=2, index=RD.EvidenceIndex.from_rows([]), target_svar=VC)
    assert rep["gates"] == {"enabled": False}
    assert "route_ungated" not in rep and "direct_ungated_cross" not in rep and "NOT_APPLICABLE" not in rep["route"]


def test_census_parallel_equals_serial_with_gates():
    rows = [_row("E1", *IDS["egg"]), _row("E2", *IDS["potato"])]
    gates, idx = _gates({EGG: "0", POTATO: "19.7"}), RD.EvidenceIndex.from_rows(rows)
    one = RC.census_from_records(_records(9), seed="7", size=9, index=idx, target_svar=VC, gates=gates)
    two = RC.census_from_records(_records(9), seed="7", size=9, index=idx, target_svar=VC, gates=gates, workers=2)
    assert one == two and json.dumps(one)


def test_cli_gates_flag_and_floor_override(tmp_path):
    import importlib.util
    spec = importlib.util.spec_from_file_location("router_demo_census", ROOT / "tools/router_demo_census.py")
    tool = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tool)
    (tmp_path / "e.jsonl").write_text("")
    src = lambda families, root: iter(_records(2))  # noqa: E731
    base = ["--seed", "7", "--sample-size", "2", "--root", str(tmp_path), "--no-baseline-check",
            "--evd", str(tmp_path / "e.jsonl")]
    assert tool.main(base + ["--out", str(tmp_path / "on.json"), "--presence-floor", f"{VC}=2.5"], record_source=src) in (0, 3)
    rep = json.loads((tmp_path / "on.json").read_text())
    f = rep["gates"]["floors"]["SVAR__000009"]
    assert f["value"] == 2.5 and f["status"] == "OVERRIDE_SENSITIVITY_RUN" and "route_ungated" in rep
    assert tool.main(base + ["--out", str(tmp_path / "off.json"), "--gates", "off"], record_source=src) in (0, 3)
    assert json.loads((tmp_path / "off.json").read_text())["gates"] == {"enabled": False}
    with pytest.raises(SystemExit):
        tool.main(base + ["--out", str(tmp_path / "bad.json"), "--presence-floor", "SVAR-NOPE=1"], record_source=src)


# ------------------------------------------------------------------ shipped registries
def test_shipped_table_covers_every_floor_nutrient_for_every_usable_ing():
    cands, vals = EG.read_table()
    keys = {f.nutrient_key for f in EG.read_floors().values()}
    assert cands and keys == {"vitamin_c"}
    assert all(c[0][1] in EG.USABLE_BANDS for c in cands.values())        # S177: rank 1 usable; rank 2-3 of any band
    with (ROOT / "registry" / "ing_sr_target_content_draft_v1.csv").open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert tuple(rows[0]) == EG.TABLE_COLUMNS and len(rows) == sum(len(c) for c in cands.values()) * len(keys)
    assert all(r["amount_per_100g"] == "" or Fraction(r["amount_per_100g"]) >= 0 for r in rows)


def test_build_tool_reproduces_the_shipped_table_when_sr_is_present():
    import importlib.util
    from culinarystate.lotstate.sr_legacy import default_dir
    try:
        default_dir(ROOT)
    except (StopIteration, FileNotFoundError):
        pytest.skip("SR Legacy is not on this machine")
    spec = importlib.util.spec_from_file_location("bt", ROOT / "tools/build_target_content_table.py")
    tool = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tool)
    assert tool.build() == (ROOT / "registry" / "ing_sr_target_content_draft_v1.csv").read_text(encoding="utf-8")


def test_sensitivity_tool_runs_variants_counts_only(tmp_path):
    import importlib.util
    spec = importlib.util.spec_from_file_location("rgs", ROOT / "tools/router_gate_sensitivity.py")
    tool = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tool)
    (tmp_path / "e.jsonl").write_text("")
    recs = _records(3)
    out = tmp_path / "s.json"
    rc = tool.main(["--seed", "7", "--sample-size", "3", "--root", str(tmp_path), "--evd", str(tmp_path / "e.jsonl"),
                    "--variants", "1.0:0.15", "1.0:0", "--out", str(out)], record_source=lambda families, root: iter(recs))
    assert rc in (0, 3)
    rep = json.loads(out.read_text())
    D.assert_counts_only(rep)
    assert set(rep["by_variant"]) == {"FLOOR_1_0_MARGIN_0_15", "FLOOR_1_0_MARGIN_0"}
    v = rep["by_variant"]["FLOOR_1_0_MARGIN_0_15"]
    assert v["identity_score_margin"] == 0.15 and sum(v["route"].values()) == sum(v["route_ungated"].values()) == v["items"]
    with pytest.raises(SystemExit):
        tool.main(["--seed", "7", "--root", str(tmp_path), "--out", str(out)], record_source=lambda f, r: iter(recs))
    with pytest.raises(ValueError):
        tool.run_variants([], ["1.0"], seed="7", index=RD.EvidenceIndex.from_rows([]), gates=_gates({}))


def test_medium_band_rank1_never_absent_s175():
    """S175 interim (FINAL-SCI #6): a below-floor value on a MEDIUM-band rank-1 identity is UNKNOWN, not ABSENT."""
    scr = _screen({"ING-HIGH": "0", "ING-MED": "0"}, bands={"ING-MED": "MEDIUM"})
    svar = next(iter(scr.floors))
    assert scr.member_state(svar, "ING-HIGH") == EG.ABSENT
    assert scr.member_state(svar, "ING-MED") == EG.UNKNOWN
    assert scr.lot_state(svar, ["ING-MED"]) == EG.UNKNOWN
