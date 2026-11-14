"""S177 / SCIFIX-ROUTER: the ING -> SR identity adapter (mechanism/sr_identity.py) behind the presence screen.

Synthetic registry, ledgers, legacy match file and SR files for the mapping rules; the shipped table for the snapshot and
the regressions. The adapter reads ``composition.ing_sr_match`` only through ``load_registry`` and ``normalise``.
"""
from __future__ import annotations

import csv
import importlib.util
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

import pytest

from culinarystate.mechanism import evidence_gates as EG
from culinarystate.mechanism import sr_identity as SI
from culinarystate.quantity import rc2_dryrun as D

ROOT = Path(__file__).resolve().parents[2]
VC = "SVAR-000009"
REG_COLS = ["term", "sr_description", "fdc_id", "kind", "rationale", "status", "verification"]
MATCH_COLS = ["ing_id", "canonical_name", "ing_status", "ing_category", "ledger_corpus_frequency", "rank", "fdc_id",
              "sr_description", "sr_category", "score", "confidence_band", "via", "reason", "status", "human_decision"]


def _csv(path: Path, cols, rows):
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        w.writerows(rows)


def _jsonl(path: Path, rows):
    path.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")


def _ing(i, name, cat="VEGETABLE", status="ACTIVE", version=1):
    return {"id": i, "version": version, "status": status, "canonical_name": name, "category": cat or None}


def _legacy(ing, rows):
    """rows: (rank, fdc, band, score)."""
    return [[ing, "x", "ACTIVE", "", "1", str(r), str(f), "d", "g", str(sc), band, "", "", "AI_DRAFTED", ""]
            for r, f, band, sc in rows]


# SR foods: fdc -> (description, group id, vitamin C mg per 100 g or None)
SR_FOODS = {100: ("Butter, salted", "1", "0"), 101: ("Butter, without salt", "1", "0"), 102: ("Butter, whipped", "1", "5"),
            110: ("Chickpeas, canned", "16", "0.5"), 111: ("Chickpeas, raw", "16", "4"), 120: ("Apple", "9", "4.6"),
            130: ("Flour, wheat", "20", "0"), 131: ("Flour, rice", "20", None), 140: ("Sherry", "14", "0"),
            150: ("Herb tea", "14", "0"), 160: ("Custard apple", "9", "19")}
GROUPS = {"1": "Dairy and Egg Products", "9": "Fruits and Fruit Juices", "14": "Beverages", "16": "Legumes and Legume Products",
          "20": "Cereal Grains and Pasta"}


@pytest.fixture
def env(tmp_path):
    sr = tmp_path / "sr"
    sr.mkdir()
    _csv(sr / "food.csv", ["fdc_id", "data_type", "description", "food_category_id", "publication_date"],
         [[f, "sr_legacy_food", d, g, "2019-04-01"] for f, (d, g, _) in SR_FOODS.items()])
    _csv(sr / "food_category.csv", ["id", "code", "description"], [[k, "0", v] for k, v in GROUPS.items()])
    _csv(sr / "food_nutrient.csv", ["id", "fdc_id", "nutrient_id", "amount", "data_points", "derivation_id"],
         [[n, f, "1162", v, "1", "1"] for n, (f, (_, _, v)) in enumerate(SR_FOODS.items()) if v is not None])
    _csv(sr / "food_nutrient_derivation.csv", ["id", "code", "description", "source_id"], [["1", "A", "Analytical", "1"]])  # S178 R4
    reg = [["butter", "Butter, salted", "100", "DEFAULT_FORM", "", "AGENT_PROPOSED", "UNVERIFIED"],
           ["chickpea", "Chickpeas, canned", "110", "DEFAULT_FORM", "", "AGENT_PROPOSED", "UNVERIFIED"],
           ["apple", "Apple", "120", "DIRECT", "", "AGENT_PROPOSED", "UNVERIFIED"],
           ["plain flour", "Flour, wheat", "130", "UK_US", "", "AGENT_PROPOSED", "UNVERIFIED"],
           ["sherry", "Sherry", "140", "APPROX", "", "AGENT_PROPOSED", "UNVERIFIED"],
           ["herb", "", "", "AMBIGUOUS", "", "AGENT_PROPOSED", "UNVERIFIED"],
           ["gumbo", "", "", "NO_SR_EQUIVALENT", "", "AGENT_PROPOSED", "UNVERIFIED"],
           ["water", "", "", "NOT_A_FOOD", "", "AGENT_PROPOSED", "UNVERIFIED"]]
    _csv(tmp_path / "reg.csv", REG_COLS, reg)
    _jsonl(tmp_path / "ING.jsonl", [
        _ing("ING-1", "butter", "DAIRY"), _ing("ING-2", "chickpeas", "LEGUME"), _ing("ING-3", "apple", "FRUIT"),
        _ing("ING-4", "plain flour", "CEREAL"), _ing("ING-5", "sherry", "BEVERAGE"), _ing("ING-6", "herb", "HERB_SPICE"),
        _ing("ING-7", "gumbo", "MEAT"), _ing("ING-8", "water", ""), _ing("ING-9", "custard", "DAIRY"),
        _ing("ING-10", "scone mix", "CEREAL"), _ing("ING-11", "old name", "VEGETABLE", status="DEPRECATED"),
        _ing("ING-12", "pippin", "FRUIT"), _ing("ING-3", "apple", "FRUIT", version=2)])
    _jsonl(tmp_path / "ALIAS.jsonl", [
        {"id": "A1", "version": 1, "status": "ACTIVE", "language": "en", "ingredient_id": "ING-12", "normalized": "apple"},
        {"id": "A2", "version": 1, "status": "ACTIVE", "language": "en", "ingredient_id": "ING-13", "normalized": "butter"},
        {"id": "A3", "version": 1, "status": "ACTIVE", "language": "fr", "ingredient_id": "ING-14", "normalized": "pomme"},
        {"id": "A4", "version": 1, "status": "RETIRED", "language": "en", "ingredient_id": "ING-15", "normalized": "apple"}])
    legacy = (_legacy("ING-1", [(1, 100, "HIGH", 1.17), (2, 101, "MEDIUM", 0.89), (3, 102, "MEDIUM", 0.88)])
              + _legacy("ING-6", [(1, 150, "HIGH", 1.1)])                       # the registry says AMBIGUOUS: no fallback
              + _legacy("ING-7", [(1, 150, "HIGH", 1.1)])
              + _legacy("ING-9", [(1, 160, "HIGH", 1.1), (2, 150, "LOW", 0.3)])  # unregistered: capped at MEDIUM
              + _legacy("ING-10", [(1, 130, "LOW", 0.6)]))                       # unregistered, LOW rank 1: no identity
    _csv(tmp_path / "match.csv", MATCH_COLS, legacy)
    return dict(sr_dir=sr, registry_path=tmp_path / "reg.csv", ing_path=tmp_path / "ING.jsonl",
                alias_path=tmp_path / "ALIAS.jsonl", match_path=tmp_path / "match.csv"), tmp_path


def _build(env):
    return SI.build_identity(**env[0])


def _screen(env, idn, floor="1", margin="0.15"):
    fl = {VC: EG.Floor(VC, "Vitamin C", "vitamin_c", "mg", Fraction(floor), "PROPOSED_PILOT", Fraction(margin))}
    fdcs = {f for c in idn.cands.values() for f, _, _ in c}
    vals = EG.read_sr_values(env[0]["sr_dir"], fdcs, ["vitamin_c"])
    basis = EG.read_sr_basis(env[0]["sr_dir"], fdcs, ["vitamin_c"])                    # S178 R4
    return EG.TargetPresenceScreen(fl, idn.cands, vals, idn.categories, idn.kinds, basis)


# ------------------------------------------------------------------ kind -> band mapping
def test_kind_to_band_mapping_and_candidates(env):
    idn = _build(env)
    assert SI.MAPPED_BAND == {"DIRECT": "HIGH", "UK_US": "HIGH", "DEFAULT_FORM": "HIGH", "APPROX": "MEDIUM"}
    assert idn.cands["ING-3"] == ((120, "HIGH", Fraction(1)),)                         # DIRECT: alone
    assert idn.cands["ING-4"] == ((130, "HIGH", Fraction(1)),)                         # UK_US: alone
    assert idn.cands["ING-5"] == ((140, "MEDIUM", Fraction(1)),)                       # APPROX: MEDIUM
    assert idn.kinds == {"ING-1": "DEFAULT_FORM", "ING-2": "DEFAULT_FORM", "ING-3": "DIRECT", "ING-4": "UK_US",
                         "ING-5": "APPROX", "ING-9": "LEGACY_FALLBACK", "ING-12": "DIRECT"}     # ING-12 via its alias


def test_default_form_adds_the_legacy_foods_as_low_alternates_at_score_one(env):
    idn = _build(env)
    assert idn.cands["ING-1"] == ((100, "HIGH", Fraction(1)), (101, "LOW", Fraction(1)), (102, "LOW", Fraction(1)))
    assert idn.cands["ING-2"] == ((110, "HIGH", Fraction(1)),)                         # no legacy rows: the default alone


def test_unmappable_kinds_have_no_identity_and_no_fallback(env):
    idn = _build(env)
    for ing in ("ING-6", "ING-7", "ING-8"):                                            # AMBIGUOUS, NO_SR_EQUIVALENT, NOT_A_FOOD
        assert ing not in idn.cands and ing not in idn.kinds
    assert idn.diagnostics["registry_AMBIGUOUS"] == 1 and idn.diagnostics["registry_NO_SR_EQUIVALENT"] == 1
    scr = _screen(env, idn)
    assert scr.member_verdict(VC, "ING-6") == (EG.UNKNOWN, "NO_USABLE_IDENTITY")       # "herb" -> chamomile tea is gone


def test_unregistered_terms_use_the_legacy_file_capped_at_medium_and_never_absent(env):
    idn = _build(env)
    assert idn.cands["ING-9"] == ((160, "MEDIUM", Fraction("1.1")), (150, "LOW", Fraction("0.3")))   # HIGH -> MEDIUM
    assert "ING-10" not in idn.cands                                                    # LOW rank 1: no identity
    scr = _screen(env, idn)
    assert scr.member_state(VC, "ING-9") == EG.PRESENT                                  # custard-apple has vitamin C: PRESENT only
    low_only = SI.Identity({"ING-X": ((140, "MEDIUM", Fraction(1)),)}, {"ING-X": ("BEVERAGE", "Beverages")},
                           {"ING-X": SI.KIND_FALLBACK})
    assert _screen(env, low_only).member_verdict(VC, "ING-X") == (EG.UNKNOWN, "RANK1_NOT_HIGH")


def test_inactive_ing_are_skipped_and_the_latest_version_wins(env):
    idn = _build(env)
    assert "ING-11" not in idn.cands and idn.categories["ING-3"][0] == "FRUIT"


def test_aliases_only_when_active_english_and_unambiguous(env):
    idn = _build(env)
    # ING-12 'pippin' has the ACTIVE English alias 'apple' -> the DIRECT registry entry; ING-13 / 14 / 15 are not ING rows
    assert idn.cands["ING-12"] == ((120, "HIGH", Fraction(1)),) and idn.kinds["ING-12"] == "DIRECT"
    assert SI.read_aliases(env[0]["alias_path"]) == {"ING-12": ("apple",), "ING-13": ("butter",)}   # fr / RETIRED excluded


# ------------------------------------------------------------------ what can be ABSENT
def test_only_curated_direct_uk_us_and_default_form_identities_can_be_absent(env):
    scr = _screen(env, _build(env))
    states = {i: scr.member_verdict(VC, i) for i in ("ING-1", "ING-2", "ING-3", "ING-4", "ING-5", "ING-9")}
    assert states["ING-4"] == (EG.ABSENT, "")                                          # UK_US, 0 mg, category confirmed
    assert states["ING-1"] == (EG.UNKNOWN, "IDENTITIES_DISAGREE")                       # a butter form holds 5 mg
    assert states["ING-2"] == (EG.ABSENT, "")                                           # DEFAULT_FORM, no other form known, 0.5 < 1
    assert states["ING-3"][0] == EG.PRESENT                                             # apple 4.6
    assert states["ING-5"] == (EG.UNKNOWN, "RANK1_NOT_HIGH")                            # APPROX sherry: never ABSENT
    assert scr.kinds["ING-4"] == "UK_US"


def test_default_form_is_absent_only_when_every_form_is_known_and_below_the_floor(env):
    idn = _build(env)
    scr = _screen(env, idn)
    assert scr.member_state(VC, "ING-1") == EG.UNKNOWN                                  # 102 has 5 mg
    only_low_forms = SI.Identity({"I": ((100, "HIGH", Fraction(1)), (101, "LOW", Fraction(1)))},
                                 {"I": ("DAIRY", "Dairy and Egg Products")}, {"I": "DEFAULT_FORM"})
    assert _screen(env, only_low_forms).member_state(VC, "I") == EG.ABSENT
    missing = SI.Identity({"I": ((100, "HIGH", Fraction(1)), (131, "LOW", Fraction(1)))},   # 131 has no SR value
                          {"I": ("DAIRY", "Dairy and Egg Products")}, {"I": "DEFAULT_FORM"})
    assert _screen(env, missing).member_verdict(VC, "I") == (EG.UNKNOWN, "SR_VALUE_MISSING")


def test_categories_come_from_the_ing_ledger_and_the_sr_food_group(env):
    idn = _build(env)
    assert idn.categories["ING-1"] == ("DAIRY", "Dairy and Egg Products")
    assert idn.categories["ING-4"] == ("CEREAL", "Cereal Grains and Pasta")
    assert SI.sr_food_groups(env[0]["sr_dir"], [100, 120, 999]) == {100: "Dairy and Egg Products",
                                                                    120: "Fruits and Fruit Juices"}
    # an ING with no category in the ledger is never confirmed: UNKNOWN (CATEGORY_EMPTY), whatever the SR value
    no_cat = SI.Identity({"I": ((130, "HIGH", Fraction(1)),)}, {"I": ("", "Cereal Grains and Pasta")}, {"I": "UK_US"})
    assert _screen(env, no_cat).member_verdict(VC, "I") == (EG.UNKNOWN, "CATEGORY_EMPTY")


def test_table_rows_carry_the_identity_source_and_registry_kind(env):
    idn = _build(env)
    vals = EG.read_sr_values(env[0]["sr_dir"], {f for c in idn.cands.values() for f, _, _ in c}, ["vitamin_c"])
    rows = SI.table_rows(idn, vals, ["vitamin_c"])
    assert tuple(rows[0]) == EG.TABLE_COLUMNS
    assert {r["identity_source"] for r in rows} == {SI.IDENTITY_SOURCE}
    by = {(r["ing_id"], r["candidate_rank"]): r for r in rows}
    assert by[("ING-1", "1")]["registry_kind"] == "DEFAULT_FORM" and by[("ING-1", "2")]["confidence_band"] == "LOW"
    assert by[("ING-9", "1")]["registry_kind"] == "LEGACY_FALLBACK" and by[("ING-9", "1")]["confidence_band"] == "MEDIUM"
    assert by[("ING-4", "1")]["amount_per_100g"] == "0" and by[("ING-1", "3")]["amount_per_100g"] == "5"
    assert D is not None and "ING-6" not in {r["ing_id"] for r in rows}


# ------------------------------------------------------------------ the nutrient list and the dependency
def test_nutrient_keys_come_from_the_composition_roster():
    assert SI.NUTRIENT_IDS["vitamin_c"] == ((1162,), "mg") and SI.NUTRIENT_UNITS["vitamin_c"] == "mg"
    assert {"water", "sodium", "calcium"} <= set(SI.NUTRIENT_IDS)
    assert EG.read_floors()[VC].nutrient_key in SI.NUTRIENT_IDS


def test_the_router_no_longer_imports_the_superseded_lotstate_package():
    for rel in ("src/culinarystate/mechanism/evidence_gates.py", "src/culinarystate/mechanism/sr_identity.py",
                "tools/build_target_content_table.py"):
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert "lotstate" not in text.replace("lotstate era", "").replace("lotstate-era", ""), rel
    text = (ROOT / "src/culinarystate/mechanism/sr_identity.py").read_text(encoding="utf-8")
    assert "from culinarystate.composition import ing_sr_match as M" in text and "M.load_registry" in text
    assert "M.normalise" in text


# ------------------------------------------------------------------ the shipped table (snapshot and regressions)
def _real():
    g = EG.EvidenceGates.load()
    return g, g.screen, SI.read_ing()


def test_snapshot_of_the_presence_states_over_the_active_ing():
    """Consolidation review 5.3 simulation: ABSENT 52 (14.1 % of mentions), PRESENT 317, UNKNOWN 1,679. This build: 52 / 318 /
    1,678 (one ING differs on the PRESENT / UNKNOWN side; ABSENT is identical). AI sizing numbers, not results.
    S178 (FIX-ROUTER, SCI-B R4): ABSENT also needs every plausible SR value to be analytical; 39 of the 52 rest on an
    assumed, imputed or undocumented zero and are UNKNOWN (SR_ZERO_NOT_ANALYTICAL): 13 / 318 / 1,717."""
    _, sc, ing = _real()
    c = Counter(sc.member_state(VC, i) for i in ing)
    assert len(ing) == 2048 and c == {EG.ABSENT: 13, EG.PRESENT: 318, EG.UNKNOWN: 1717}
    assert sum(sc.member_verdict(VC, i)[1] == EG.B_NOT_ANALYTICAL for i in ing) >= 39


def test_every_absent_ing_rests_on_a_curated_direct_uk_us_or_default_form_identity():
    _, sc, ing = _real()
    absent = [i for i in ing if sc.member_state(VC, i) == EG.ABSENT]
    assert absent and {sc.kinds[i] for i in absent} <= {"DIRECT", "UK_US", "DEFAULT_FORM"}
    for i in absent:                                                         # and the three S177 conditions still hold
        assert sc.cands[i][0][1] == "HIGH" and sc.category_ok(i)


def test_regressions_herb_lemongrass_coleslaw_custard_are_never_absent():
    _, sc, ing = _real()
    by_name = {n: i for i, (n, _) in ing.items()}
    seen = 0
    for name in ("herb", "lemongrass", "coleslaw", "custard"):
        if name in by_name:
            seen += 1
            assert sc.member_state(VC, by_name[name]) != EG.ABSENT, name
    assert seen >= 3
    for i in ("ING-000195", "ING-001013", "ING-000250"):                       # the reviewers' three ids
        assert sc.member_state(VC, i) != EG.ABSENT


def test_milk_sugar_cream_vinegar_bread_leave_absent_as_the_review_predicts():
    """Alternates disagree or lack a value (milk, sugar), the registry calls the name AMBIGUOUS (cream, vinegar, bread)."""
    _, sc, ing = _real()
    by_name = {n: i for i, (n, _) in ing.items()}
    for name in ("milk", "sugar", "cream", "vinegar", "bread"):
        assert sc.member_state(VC, by_name[name]) != EG.ABSENT, name
    for name in ("butter", "olive oil", "rice", "pasta"):                     # S177: ABSENT; S178 R4: their SR zeros have
        assert sc.member_verdict(VC, by_name[name]) == (EG.UNKNOWN, EG.B_NOT_ANALYTICAL), name   # no derivation, 0 points


def test_provenance_names_the_identity_source_and_is_counts_only():
    g, sc, _ = _real()
    d = g.describe()
    assert d["identity_source"] == SI.IDENTITY_SOURCE and d["version"] == EG.VERSION
    assert d["identity_registry_sha256"] == EG._sha(SI.REGISTRY_PATH)
    assert d["identity_kinds"] == dict(sorted(Counter(sc.kinds.values()).items())) and "DIRECT" in d["identity_kinds"]
    D.assert_counts_only(d)


def test_legacy_identity_rebuild_reproduces_the_previous_absent_count(tmp_path):
    """Section 5.3: with the legacy match file alone the same rule gave 86 ABSENT ING (and the adapter gives 52)."""
    try:
        SI.default_dir(ROOT)
    except (StopIteration, FileNotFoundError):
        pytest.skip("SR Legacy is not on this machine")
    spec = importlib.util.spec_from_file_location("bt177i", ROOT / "tools/build_target_content_table.py")
    tool = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tool)
    p = tmp_path / "legacy.csv"
    p.write_text(tool.build("legacy"), encoding="utf-8")
    assert {r["identity_source"] for r in csv.DictReader(p.open(newline="", encoding="utf-8"))} == {SI.LEGACY_SOURCE}
    cands, vals, cats = EG.read_table_full(p)
    fl = EG.read_floors()
    sc = EG.TargetPresenceScreen(fl, cands, vals, cats)
    assert sum(sc.member_state(VC, i) == EG.ABSENT for i in cands) == 0      # S178 R4: no basis given -> fail-closed
    sc = EG.TargetPresenceScreen(fl, cands, vals, cats, basis=EG.read_table_basis(p))
    assert sum(sc.member_state(VC, i) == EG.ABSENT for i in cands) == 12     # S177: 86; S178 R4 analytical only: 12
    with pytest.raises(ValueError):
        tool.build("nope")
    assert tool.main(["--check"]) == 0                                       # the shipped (adapter) table still matches


def test_gates_load_from_sr_directly_builds_the_same_screen_as_the_shipped_table():
    try:
        SI.default_dir(ROOT)
    except (StopIteration, FileNotFoundError):
        pytest.skip("SR Legacy is not on this machine")
    direct = EG.EvidenceGates.load(source="sr")
    shipped = EG.EvidenceGates.load()
    assert direct.screen.cands == shipped.screen.cands and direct.screen.categories == shipped.screen.categories
    assert direct.screen.kinds == shipped.screen.kinds
    assert direct.describe()["identity_source"] == SI.IDENTITY_SOURCE
