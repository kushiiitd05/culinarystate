"""S178 INGCAT: inputs, ordering, outputs, the top-100 sheet, the runtime overlay and the read-only guarantees.

Synthetic ledger, registry, legacy match file, SR files, mention counts and S177 counts in a tmp repository root.
No ledger is written; the overlay is checked to leave the base screen untouched.
"""
from __future__ import annotations

import csv
import hashlib
import json
from fractions import Fraction
from pathlib import Path

import pandas as pd
import pytest

from culinarystate.mechanism import evidence_gates as EG
from tests.unit.test_s178_analysis_helpers import ROOT, load_tool

T = load_tool("s178_ingcat_propose")
VC = "SVAR-000009"
REG_COLS = ["term", "sr_description", "fdc_id", "kind", "rationale", "status", "verification"]
MATCH_COLS = ["ing_id", "canonical_name", "ing_status", "ing_category", "ledger_corpus_frequency", "rank", "fdc_id",
              "sr_description", "sr_category", "score", "confidence_band", "via", "reason", "status", "human_decision"]


def _csv(path: Path, cols, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        w.writerows(rows)


def _jsonl(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")


def _ing(i, name, cat=None, status="ACTIVE", version=1):
    r = {"id": f"ING-{i:06d}", "version": version, "status": status, "canonical_name": name}
    if cat:
        r["category"] = cat
    return r


VOCAB = ("BEVERAGE", "CEREAL", "CONDIMENT", "DAIRY", "EGG", "FAT_OIL", "FRUIT", "HERB_SPICE", "LEGUME", "MEAT", "NUT_SEED",
         "SEAFOOD", "SWEETENER", "VEGETABLE")
SR_FOODS = {200: ("Garlic, raw", "11"), 201: ("Salt, table", "2"), 202: ("Beverages, water, tap", "14"),
            203: ("Egg, whole, raw, fresh", "1"), 204: ("Leavening agents, baking powder", "18"),
            205: ("Soy sauce, made from soy", "16"), 206: ("Butter, salted", "1")}
GROUPS = {"1": "Dairy and Egg Products", "2": "Spices and Herbs", "11": "Vegetables and Vegetable Products", "14": "Beverages",
          "16": "Legumes and Legume Products", "18": "Baked Products"}
REGISTRY = [["garlic", "Garlic, raw", "200", "DIRECT"], ["salt", "Salt, table", "201", "DIRECT"],
            ["water", "Beverages, water", "202", "DIRECT"], ["egg", "Egg, whole", "203", "DEFAULT_FORM"],
            ["baking powder", "Baking powder", "204", "APPROX"], ["soy sauce", "Soy sauce", "205", "DEFAULT_FORM"],
            ["butter", "Butter, salted", "206", "DEFAULT_FORM"], ["herb", "", "", "NOT_A_FOOD"]]


@pytest.fixture
def root(tmp_path):
    r = tmp_path / "repo"
    sr = r / "sr"
    _csv(sr / "food.csv", ["fdc_id", "data_type", "description", "food_category_id", "publication_date"],
         [[f, "sr_legacy_food", d, g, "2019-04-01"] for f, (d, g) in SR_FOODS.items()])
    _csv(sr / "food_category.csv", ["id", "code", "description"], [[k, "0", v] for k, v in GROUPS.items()])
    _csv(r / "registry/ing_sr_defaults_v1.csv", REG_COLS, [[*row, "", "AGENT_PROPOSED", "UNVERIFIED"] for row in REGISTRY])
    _csv(r / "registry/ing_sr_legacy_match_draft_v1.csv", MATCH_COLS, [
        ["ING-000008", "zzfood", "ACTIVE", "", "1", "1", "206", "Butter, salted", "Dairy and Egg Products", "1.1", "LOW", "", "",
         "AI_DRAFTED", ""]])
    _jsonl(r / "ledgers/data/ING.jsonl", [
        _ing(1, "butter", "DAIRY"), _ing(2, "garlic"), _ing(3, "salt"), _ing(4, "water"), _ing(5, "egg"),
        _ing(6, "baking powder"), _ing(7, "saucepan"), _ing(8, "zzfood"), _ing(9, "old thing", status="DEPRECATED"),
        _ing(10, "soy sauce"), _ing(11, "herb"), _ing(2, "garlic", version=2), _ing(12, "olive oil", "FAT_OIL"),
        *[_ing(20 + k, f"zzname{k}", c) for k, c in enumerate(VOCAB)]])
    _jsonl(r / "ledgers/data/ALIAS.jsonl", [])
    rows = [("ING", "ING-000003", "FOODCOM", 100), ("ING", "ING-000003", "A1_BBC_GOOD_FOOD", 900),
            ("ING", "ING-000002", "FOODCOM", 60), ("ING", "ING-000005", "FOODCOM", 50), ("ING", "ING-000004", "FOODCOM", 50),
            ("ING", "ING-000004", "A1_BBC_GOOD_FOOD", 400), ("ING", "ING-000005", "A1_BBC_GOOD_FOOD", 5),
            ("ING", "ING-000006", "WIKIBOOKS", 40), ("ING", "ING-000010", "FOODCOM", 30), ("ING", "ING-000007", "FOODCOM", 5),
            ("PROC", "ING-000099", "FOODCOM", 7777), ("ING", "ING-000001", "FOODCOM", 999)]
    p = r / "ledgers/recipe_base/vocab_corpus_frequency_v1.parquet"
    p.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows, columns=["vocab_type", "vocab_id", "source_family", "mention_count"]).to_parquet(p)
    (r / "reports/step23").mkdir(parents=True)
    (r / T.S177_FULL).write_text(json.dumps({"category_blocked_items": {"ING__000005": 1000, "ING__000004": 2000,
                                                                      "ING__000010": 30, "ING__000012": 5}}), encoding="utf-8")
    table = [[ing, "1", str(f), "HIGH", "1", "vitamin_c", "mg", "0", "USDA_SR_LEGACY_2018_04", "", GROUPS[SR_FOODS[f][1]], "x", k]
             for ing, f, k in (("ING-000002", 200, "DIRECT"), ("ING-000003", 201, "DIRECT"), ("ING-000004", 202, "DIRECT"),
                               ("ING-000005", 203, "DEFAULT_FORM"), ("ING-000006", 204, "APPROX"), ("ING-000010", 205, "DEFAULT_FORM"))]
    _csv(r / "registry/ing_sr_target_content_draft_v1.csv", list(EG.TABLE_COLUMNS), table)
    return r


@pytest.fixture
def inp(root):
    return T.load_inputs(root, sr_dir=root / "sr")


def by_id(rows):
    return {r["ing_id"]: r for r in rows}


# ------------------------------------------------------------------ scope, order, columns
def test_scope_is_exactly_the_active_ing_without_a_category_in_the_latest_version(inp):
    rows = T.build_rows(inp)
    assert {r["ing_id"] for r in rows} == {f"ING-{i:06d}" for i in (2, 3, 4, 5, 6, 7, 8, 10, 11)}   # not 1, 9 (DEPRECATED), 12
    assert inp.vocabulary == VOCAB                                          # the vocabulary is read from the ledger, not hard-coded


def test_order_is_non_bbc_mentions_then_all_family_mentions_then_id(inp):
    rows = T.build_rows(inp)
    ids = [r["ing_id"] for r in rows]
    assert ids[:5] == ["ING-000003", "ING-000002", "ING-000004", "ING-000005", "ING-000006"]    # 100, 60, 50(all 450), 50(all 55), 40
    assert [r["rank"] for r in rows] == [str(i) for i in range(1, len(rows) + 1)]
    assert by_id(rows)["ING-000003"]["mention_nonbbc"] == "100" and by_id(rows)["ING-000003"]["mention_all_families"] == "1000"
    assert by_id(rows)["ING-000011"]["mention_nonbbc"] == "0"                                    # no corpus mention at all
    assert ids[-2:] == ["ING-000008", "ING-000011"]


def test_columns_and_the_empty_human_decision(inp):
    rows = T.build_rows(inp)
    assert all(tuple(r) == T.CSV_COLUMNS for r in rows)
    assert T.CSV_COLUMNS[:8] == ("ing_id", "name", "proposed_category", "basis", "confidence", "sr_food_group", "mention_items",
                                 "human_decision")
    assert all(r["human_decision"] == "" and r["status"] == "AI_DRAFTED_FOR_HUMAN_REVIEW" for r in rows)


def test_mention_items_come_from_the_s177_counts_only_where_available(inp):
    rows = by_id(T.build_rows(inp))
    assert rows["ING-000005"]["mention_items"] == "1000" and rows["ING-000004"]["mention_items"] == "2000"
    assert rows["ING-000003"]["mention_items"] == ""                       # salt is not in the S177 counts of this fixture
    assert "ING-000012" not in rows                                         # blocked in S177 but it has a category: out of scope


def test_the_brief_cases_through_the_whole_pipeline(inp):
    rows = by_id(T.build_rows(inp))
    salt, water, egg = rows["ING-000003"], rows["ING-000004"], rows["ING-000005"]
    assert (salt["proposed_category"], salt["confidence"], salt["new_category_suggestion"]) == ("HERB_SPICE", "MEDIUM", "SALT_MINERAL")
    assert salt["sr_food_group"] == "Spices and Herbs"
    assert (water["proposed_category"], water["new_category_suggestion"]) == ("BEVERAGE", "WATER")
    assert (egg["proposed_category"], egg["confidence"], egg["sr_description"]) == ("EGG", "HIGH", "Egg, whole, raw, fresh")
    bp = rows["ING-000006"]
    assert bp["proposed_category"] == "" and bp["new_category_suggestion"] == "LEAVENING_AGENT"
    assert rows["ING-000007"]["proposed_category"] == "" and rows["ING-000008"]["confidence"] == "LOW"
    assert rows["ING-000011"]["registry_kind"] == "NOT_A_FOOD"


def test_the_crosswalk_columns_say_whether_confirming_would_unlock_absent(inp):
    rows = by_id(T.build_rows(inp))
    assert rows["ING-000005"]["crosswalk_confirms"] == "YES" and rows["ING-000005"]["unlocks_absent_vitc"] == "YES"
    soy = rows["ING-000010"]                                               # CONDIMENT vs the SR group Legumes: not in the crosswalk
    assert soy["proposed_category"] == "CONDIMENT" or soy["proposed_category"] == ""
    assert soy["crosswalk_confirms"] in ("NO", "")
    assert rows["ING-000003"]["unlocks_absent_vitc"] == ""                 # no S177 count: not claimed


# ------------------------------------------------------------------ outputs, read-only guarantees
def test_write_csv_round_trips_and_refuses_to_overwrite(inp, tmp_path):
    rows = T.build_rows(inp)
    p = tmp_path / "out" / "p.csv"
    sha = T.write_csv(p, rows, overwrite=False)
    assert sha == hashlib.sha256(p.read_bytes()).hexdigest()
    back = list(csv.DictReader(p.open(newline="", encoding="utf-8")))
    assert len(back) == len(rows) and tuple(back[0]) == T.CSV_COLUMNS and back[0]["ing_id"] == rows[0]["ing_id"]
    with pytest.raises(FileExistsError):
        T.write_csv(p, rows, overwrite=False)
    assert T.write_csv(p, rows, overwrite=True) == sha                      # deterministic


def test_checked_output_refuses_ledgers_data_and_composition(root):
    for bad in ("ledgers/data/ING.jsonl", "ledgers/x.csv", "data/derived/x.csv", "src/culinarystate/composition/x.py",
                "exports/x.csv", "annotation/gold/x.csv", "../escape.csv"):
        with pytest.raises(ValueError):
            T.checked_output(root, bad)
    assert T.checked_output(root, "registry/ing_category_proposals_S178_DRAFT.csv").name.endswith("S178_DRAFT.csv")
    assert T.checked_output(root, "reports/s178/ingcat/x.md").parent.name == "ingcat"


def test_a_full_run_leaves_every_ledger_byte_identical(root):
    led = sorted((root / "ledgers").rglob("*"))
    before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in led if p.is_file()}
    rc = T.main(["--root", str(root), "--sr-dir", str(root / "sr"), "--overwrite"])
    assert rc == 0
    after = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in led if p.is_file()}
    assert before == after
    assert (root / T.OUT_CSV).exists() and (root / T.OUT_SHEET).exists() and (root / T.OUT_SUMMARY).exists()
    summ = json.loads((root / T.OUT_SUMMARY).read_text(encoding="utf-8"))
    assert summ["active_ing_without_category"] == 9 and summ["active_ing_with_category"] == 2 + len(VOCAB)
    assert sum(summ["by_confidence"].values()) == 9 and summ["counts_only"] is True


def test_main_refuses_an_existing_output_without_overwrite(root):
    assert T.main(["--root", str(root), "--sr-dir", str(root / "sr")]) == 0
    with pytest.raises(FileExistsError):
        T.main(["--root", str(root), "--sr-dir", str(root / "sr")])


def test_the_tool_reads_the_composition_layer_only_through_the_read_only_api():
    src = (ROOT / "tools/s178_ingcat_propose.py").read_text(encoding="utf-8")
    assert "from culinarystate.composition import ing_sr_match as M" in src
    assert src.count("culinarystate.composition") == 1
    assert "M.load_registry" in src and "M.normalise" in src
    assert ".write_text(" not in src.split("def load_inputs")[0]          # nothing writes while the inputs are read


# ------------------------------------------------------------------ the top-100 sheet and the summary
def _fake_rows(n):
    return [{"rank": str(i), "ing_id": f"ING-{i:06d}", "name": f"food{i}", "proposed_category": "DAIRY" if i % 3 else "",
             "confidence": ("HIGH", "MEDIUM", "LOW")[i % 3], "sr_food_group": "Dairy and Egg Products", "mention_items": "",
             "mention_nonbbc": str(1000 - i), "alt_category": "", "new_category_suggestion": "WATER" if i == 3 else "",
             "conflicts": "NO_EXACT_FIT" if i == 3 else "", "unlocks_absent_vitc": ""} for i in range(1, n + 1)]


def test_top_sheet_has_exactly_one_tickable_line_per_ing_up_to_100():
    md = T.top_sheet(_fake_rows(150))
    ticks = [ln for ln in md.splitlines() if ln.startswith("- [ ] ")]
    assert len(ticks) == 100 and ticks[0].startswith("- [ ] 1. `ING-000001`") and "`ING-000101`" not in md
    assert "[HIGH]" in md and "(none fits)" in md and "suggest NEW value WATER" in md
    assert "Suggested NEW category values" in md and "`WATER`" in md and "CATEGORY_CROSSWALK" in md
    assert len(T.top_sheet(_fake_rows(7)).split("- [ ] ")) == 8


def test_top_sheet_of_the_fixture(inp):
    md = T.top_sheet(T.build_rows(inp))
    assert md.count("- [ ] ") == 9 and "**salt**" in md and "unlocks ABSENT" in md
    assert "AI_DRAFTED" in md and "No ledger was edited" in md


def test_summary_counts_add_up(inp):
    rows = T.build_rows(inp)
    s = T.summarise(rows, inp.vocabulary, 2 + len(VOCAB), T.backtest(inp))
    assert s["active_ing_without_category"] == len(rows) == sum(s["by_confidence"].values()) == sum(s["by_proposed_category"].values())
    assert s["no_proposal"] == s["by_proposed_category"]["NONE"]
    assert s["nonbbc_mentions_total_of_uncategorised"] == sum(s["nonbbc_mentions_by_confidence"].values()) == 100 + 60 + 50 + 50 + 40 + 30 + 5
    assert s["s177_category_blocked_ing"] == 3
    assert s["new_value_suggestions_ing"] == {"LEAVENING_AGENT": 1, "SALT_MINERAL": 1, "WATER": 1}


def test_backtest_hides_the_label_and_counts_by_confidence(inp):
    bt = T.backtest(inp)
    n = 2 + len(VOCAB)                                                    # the labelled ING of the fixture
    assert sum(v["n"] for v in bt.values()) == n
    assert sum(v["agree"] + v["disagree"] + v["no_proposal"] for v in bt.values()) == n
    # butter: registry + lexical agree (HIGH); olive oil: lexical only (MEDIUM); the invented names have no basis, nothing proposed
    assert (bt["HIGH"]["agree"], bt["MEDIUM"]["agree"], bt["LOW"]["no_proposal"]) == (1, 1, len(VOCAB))


# ------------------------------------------------------------------ the runtime overlay and the scenarios
def _gates():
    floors = {VC: EG.Floor(VC, "Vitamin C", "vitamin_c", "mg", Fraction(1), "PROPOSED", Fraction("0.15"))}
    cands = {"ING-A": ((1, "HIGH", Fraction(1)),), "ING-B": ((2, "HIGH", Fraction(1)),), "ING-C": ((3, "HIGH", Fraction(1)),)}
    values = {(1, "vitamin_c"): Fraction(0), (2, "vitamin_c"): Fraction(0), (3, "vitamin_c"): Fraction(0)}
    cats = {"ING-A": ("", "Dairy and Egg Products"), "ING-B": ("", "Legumes and Legume Products"), "ING-C": ("DAIRY", "Dairy and Egg Products")}
    return EG.EvidenceGates(EG.TargetPresenceScreen(floors, cands, values, cats, {}), provenance={"version": "x"})


def test_overlay_flips_empty_category_to_absent_only_when_the_crosswalk_confirms():
    base = _gates()
    assert base.screen.member_verdict(VC, "ING-A") == (EG.UNKNOWN, "CATEGORY_EMPTY")
    g, applied = T.overlay_gates(base, {"ING-A": "EGG", "ING-B": "CONDIMENT", "ING-NOIDENTITY": "DAIRY"})
    assert applied == 2                                                    # an ING with no router identity cannot change a verdict
    assert g.screen.member_verdict(VC, "ING-A") == (EG.ABSENT, "")
    assert g.screen.member_verdict(VC, "ING-B") == (EG.UNKNOWN, "CATEGORY_MISMATCH")   # CONDIMENT is not confirmed against Legumes
    assert g.screen.member_verdict(VC, "ING-C") == (EG.ABSENT, "")


def test_overlay_does_not_touch_the_base_screen_or_the_shipped_tables():
    base = _gates()
    snapshot = dict(base.screen.categories)
    T.overlay_gates(base, {"ING-A": "EGG"})
    assert base.screen.categories == snapshot and base.screen.member_verdict(VC, "ING-A")[1] == "CATEGORY_EMPTY"
    assert (ROOT / "registry/ing_sr_target_content_draft_v1.csv").exists()


def _scenario_rows():
    rows = []
    for i in range(1, 251):
        rows.append({"ing_id": f"ING-{i:06d}", "proposed_category": "" if i % 11 == 0 else "DAIRY",
                     "confidence": "HIGH" if i % 2 == 0 else ("MEDIUM" if i % 3 == 0 else "LOW")})
    return rows


def test_scenarios_select_only_proposed_values_by_confidence():
    rows = _scenario_rows()
    sc = T.scenarios(rows)
    a, b, c, d, e = (sc[k] for k in ("A_top100_sheet_HIGH_only", "B_first100_HIGH_proposals", "C_all_HIGH",
                                      "D_top100_sheet_HIGH_and_MEDIUM", "E_all_HIGH_and_MEDIUM"))
    conf = {r["ing_id"]: r["confidence"] for r in rows}
    assert all(conf[i] == "HIGH" for i in a) and all(int(i[4:]) <= 100 for i in a)
    assert len(b) == 100 and all(conf[i] == "HIGH" for i in b)
    assert set(a) <= set(c) and set(b) <= set(c)
    assert all(conf[i] in ("HIGH", "MEDIUM") for i in d) and set(a) <= set(d) and set(d) <= set(e)
    assert all(v for sc_ in sc.values() for v in sc_.values())              # no empty category is ever overlaid
    assert not any(int(i[4:]) % 11 == 0 for i in e)


def test_full_member_projection_sums_only_ing_the_crosswalk_clears():
    rows = [{"ing_id": "ING-1", "proposed_category": "EGG", "confidence": "HIGH", "mention_items": "1000", "unlocks_absent_vitc": "YES"},
            {"ing_id": "ING-2", "proposed_category": "CONDIMENT", "confidence": "HIGH", "mention_items": "50", "unlocks_absent_vitc": "NO"},
            {"ing_id": "ING-3", "proposed_category": "DAIRY", "confidence": "MEDIUM", "mention_items": "7", "unlocks_absent_vitc": "YES"},
            {"ing_id": "ING-4", "proposed_category": "DAIRY", "confidence": "HIGH", "mention_items": "", "unlocks_absent_vitc": ""}]
    pr = T.full_member_projection(rows)
    assert pr["A_top100_sheet_HIGH_only"] == {"ing_confirmed": 3, "ing_clearing_the_s177_category_block": 1,
                                              "s177_full_items_member_unknown_to_absent": 1000}
    assert pr["D_top100_sheet_HIGH_and_MEDIUM"]["s177_full_items_member_unknown_to_absent"] == 1007
    assert pr["C_all_HIGH"]["ing_confirmed"] == 3 and pr["E_all_HIGH_and_MEDIUM"]["ing_confirmed"] == 4


def test_delta_and_slice_helpers():
    assert T._delta({"a": 5, "b": 2}, {"a": 3, "b": 2, "c": 4}) == {"a": -2, "c": 4}
    rep = {"items": 3, "route": {"DIRECT": 1}, "extra": 9}
    assert T._slice(rep) == {"items": 3, "route": {"DIRECT": 1}}


# ------------------------------------------------------------------ the shipped outputs (real ledgers; run with -m ledgers)
@pytest.mark.ledgers
def test_shipped_proposals_match_the_real_ledger():
    path = ROOT / T.OUT_CSV
    assert path.exists()
    rows = list(csv.DictReader(path.open(newline="", encoding="utf-8")))
    ing = T.read_ing_ledger(ROOT / T.ING_LEDGER)
    vocab = {r["category"] for r in ing.values() if r["category"]}
    assert {r["ing_id"] for r in rows} == {i for i, r in ing.items() if not r["category"]}
    assert len(rows) == len({r["ing_id"] for r in rows})
    assert all(r["proposed_category"] in vocab | {""} and r["alt_category"] in vocab | {""} for r in rows)
    assert all(r["human_decision"] == "" for r in rows) and tuple(rows[0]) == T.CSV_COLUMNS
    nb = [int(r["mention_nonbbc"]) for r in rows]
    assert nb == sorted(nb, reverse=True)
    top = {r["name"]: r for r in rows[:100]}
    assert top["salt"]["new_category_suggestion"] == "SALT_MINERAL" and top["water"]["new_category_suggestion"] == "WATER"


@pytest.mark.ledgers
def test_shipped_simulation_is_counts_only_runtime_only_and_reproduces_s177():
    sim = json.loads((ROOT / T.OUT_SIM).read_text(encoding="utf-8"))
    assert sim["overlay_is_runtime_only"] is True and sim["ledger_written"] is False
    assert sim["ing_ledger_unchanged"] is True and sim["protected_ledger_baseline_before"] == sim["protected_ledger_baseline_after"] == "PASS"
    assert sim["baseline_reproduces_s177_1000"] is True                      # the no-overlay pass equals the published S177 sample run
    a = sim["scenarios"]["A_top100_sheet_HIGH_only"]
    assert sum(a["delta_route"].values()) == 0                                # a category overlay moves items between routes, never creates any
    assert all(v >= 0 for v in a["delta_member_absent_items"].values())       # a confirmed category only adds ABSENT members
    from culinarystate.quantity import rc2_dryrun as D
    D.assert_counts_only(sim)
