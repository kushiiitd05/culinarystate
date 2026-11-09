"""S179: composition/ fixes from the S177 consolidation review and FULLRUN (tickets A1-A11, F1-F5, ports P1/P3/P4/P5).

Ids refer to handoff/MAC_TASKS_FROM_CONSOLIDATION_S177.md.
"""
from __future__ import annotations

import csv
import json
import math
from fractions import Fraction
from pathlib import Path
from types import MappingProxyType

import pytest

from culinarystate.composition import food_ph as PH
from culinarystate.composition import line_census as LC
from culinarystate.composition import line_mass as LM
from culinarystate.composition import lot_state as LS
from culinarystate.composition import sr_legacy as SR
from culinarystate.composition.sr_legacy import Portion, SRFood
from culinarystate.quantity.grammar import parse_line
from culinarystate.quantity.normalize import normalize

ROOT = Path(__file__).resolve().parents[2]
LPH = ROOT / "registry/food_ph_fda_draft_v1.csv"


def p(desc: str, g: float, amount: float = 1.0) -> Portion:
    return Portion(desc, g, amount, 9999, "undetermined")


ONION = SRFood(1, "Onions, raw", 11, MappingProxyType({}), (
    p("cup, chopped", 160), p("medium (2-1/2\" dia)", 110), p("large (3\" dia)", 150), p("small", 70)))
SUGAR = SRFood(2, "Sugars, granulated", 19, MappingProxyType({}), (p("cup", 200), p("tsp", 4.2)))
EGG = SRFood(3, "Egg, whole, raw, fresh", 1, MappingProxyType({}), (
    p("small", 38), p("medium", 44), p("large", 50), p("extra large", 56), p("jumbo", 63),
    p("cup (4.86 large eggs)", 243)))
OIL = SRFood(4, "Oil, olive, salad or cooking", 4, MappingProxyType({}), (p("tbsp", 13.5), p("cup", 216)))
MILK = SRFood(5, "Milk, whole", 1, MappingProxyType({}), (p("quart", 976), p("cup", 244)))
QUART_ONLY = SRFood(6, "Beverages, cola", 14, MappingProxyType({}), (p("quart", 1000),))
CHICKEN = SRFood(7, "Chicken, broilers or fryers, meat and skin, raw", 5, MappingProxyType({}), (
    p("unit (yield from 1 lb ready-to-cook chicken)", 196), p("chicken, bone removed", 920)))


def lm(line: str, food, locale="UK", **kw):
    q = parse_line(line)
    return LM.line_mass(q, normalize(q, locale), food, **kw)


def census_line(line: str, family: str, foods: dict):
    name = {1: "onion", 2: "sugar", 4: "olive oil"}
    by_name = {v: k for k, v in name.items() if k in foods}

    def find(text: str):
        return next((n for n in by_name if n.split()[-1] in text), None)

    return LC._line(line, family, find, lambda n: LC.Resolved(by_name[n], "REGISTRY_MAPPED"), foods)[1]


# --- A4 / P1 / F1: U+2044 FRACTION SLASH and U+2215 DIVISION SLASH ------------------------------------------------
def test_a4_fraction_slash_is_read_as_a_fraction() -> None:
    m = census_line("1⁄2 onion", "A1_BBC_GOOD_FOOD", {1: ONION})
    assert (m.basis, m.low_g, m.high_g) == ("COUNT_x_SR_PORTION", 35.0, 75.0)
    m = census_line("1∕2 onion", "A1_BBC_GOOD_FOOD", {1: ONION})
    assert (m.low_g, m.high_g) == (35.0, 75.0)
    v = census_line("1⁄4 cup sugar", "TASTESET", {2: SUGAR})
    assert v.basis == "VOLUME_x_SR_DENSITY"
    assert v.low_g == pytest.approx(0.25 * 236.5882365 * min(200 / 236.5882365, 4.2 / 4.92892159375))


# --- A5 / P3: the full SR size set for unsized counts ----------------------------------------------------------------
def test_a5_unsized_count_spans_every_sr_size() -> None:
    r = lm("3 eggs", EGG)
    assert (r.low_g, r.high_g) == (114.0, 189.0)
    assert set(r.portions) == {"small", "medium", "large", "extra large", "jumbo"}


def test_a5_two_word_size_picks_its_own_portion() -> None:
    r = lm("1 extra large egg", EGG)
    assert (r.low_g, r.high_g, r.portions) == (56.0, 56.0, ("extra large",))
    r = lm("2 large eggs", EGG)
    assert (r.low_g, r.high_g, r.portions) == (100.0, 100.0, ("large",))


# --- A6 / P4: POINT only for a stated mass -------------------------------------------------------------------------
def test_a6_sr_single_portion_is_an_interval_with_a_flag() -> None:
    r = lm("2 large eggs", EGG)
    assert r.status == "INTERVAL" and "SR_SINGLE_PORTION_NO_SPREAD" in r.flags
    r = lm("200g plain flour", None)
    assert (r.status, r.flags) == ("POINT", ())
    r = lm("3 eggs", EGG)
    assert "SR_SINGLE_PORTION_NO_SPREAD" not in r.flags


# --- A6b: locale-unknown unit hull; historical units -----------------------------------------------------------------
def test_a6b_locale_unknown_volume_hull_is_flagged() -> None:
    r = lm("1 cup olive oil", OIL, locale=None, locale_known=False)
    assert r.basis == "VOLUME_x_SR_DENSITY" and "UNIT_HULL_LOCALE_UNKNOWN" in r.flags
    r = lm("100 ml olive oil", OIL, locale=None, locale_known=False)
    assert "UNIT_HULL_LOCALE_UNKNOWN" not in r.flags
    assert "UNIT_HULL_LOCALE_UNKNOWN" not in lm("1 cup olive oil", OIL).flags


def test_a6b_historical_text_volume_needs_a_unit_registry() -> None:
    r = lm("1 cup olive oil", OIL, locale=None, locale_known=False, historical_units=True)
    assert (r.status, r.reason, r.low_g) == ("UNKNOWN", "HISTORICAL_UNIT_REGISTRY_MISSING", None)
    m = census_line("1 cup olive oil", "GUTENBERG_SEGMENT", {4: OIL})
    assert m.reason == "HISTORICAL_UNIT_REGISTRY_MISSING"
    m = census_line("1 cup olive oil", "TASTESET", {4: OIL})
    assert "UNIT_HULL_LOCALE_UNKNOWN" in m.flags
    assert lm("2 eggs", EGG, locale=None, locale_known=False, historical_units=True).basis == "COUNT_x_SR_PORTION"


# --- F2: SR volume measures beyond cup/tbsp/tsp/fl oz ----------------------------------------------------------------
def test_f2_quart_pint_litre_ml_gallon_are_volumes() -> None:
    assert LM.portion_ml(p("quart", 976)) == pytest.approx(946.352946)
    assert LM.portion_ml(p("pint", 488)) == pytest.approx(473.176473)
    assert LM.portion_ml(p("gallon", 3900)) == pytest.approx(3785.411784)
    assert LM.portion_ml(p("liter", 1030)) == pytest.approx(1000.0)
    assert LM.portion_ml(p("ml", 103, amount=100)) == pytest.approx(100.0)
    assert LM.portion_ml(p("milliliter", 1.03)) == pytest.approx(1.0)
    r = lm("2 cups milk", MILK, locale="US")
    assert set(r.portions) == {"quart", "cup"}
    assert lm("1 cup cola", QUART_ONLY, locale="US").basis == "VOLUME_x_SR_DENSITY"
    assert lm("2 cola", QUART_ONLY).reason == "NO_SR_COUNT_PORTION"            # a quart is not an item


# --- F3: yield rows are not item weights ------------------------------------------------------------------------------
def test_f3_yield_rows_never_stand_in_for_an_item() -> None:
    r = lm("1 chicken", CHICKEN)
    assert r.portions == ("chicken, bone removed",)
    only_yield = SRFood(8, "Chicken, broilers or fryers, meat and skin, raw", 5, MappingProxyType({}), (
        p("unit (yield from 1 lb ready-to-cook chicken)", 196),))
    assert lm("1 chicken", only_yield).reason == "NO_SR_COUNT_PORTION"


# --- A7: zero-amount SR portion rows -------------------------------------------------------------------------------
def _write(path: Path, header: list[str], rows: list[list[object]]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, quoting=csv.QUOTE_ALL)
        w.writerow(header)
        w.writerows(rows)


def test_a7_zero_amount_portion_rows_are_skipped(tmp_path: Path) -> None:
    _write(tmp_path / "food.csv", ["fdc_id", "data_type", "description", "food_category_id", "publication_date"],
           [[171062, "sr_legacy_food", "Chicken, broilers or fryers, back, meat and skin, raw", 5, "2019-04-01"]])
    _write(tmp_path / "food_nutrient.csv", ["id", "fdc_id", "nutrient_id", "amount", "data_points", "derivation_id",
                                            "min", "max", "median", "footnote", "min_year_acquired"],
           [[1, 171062, 1051, "60", "", "", "", "", "", "", ""]])
    _write(tmp_path / "food_portion.csv", ["id", "fdc_id", "seq_num", "amount", "measure_unit_id",
                                           "portion_description", "modifier", "gram_weight", "data_points",
                                           "footnote", "min_year_acquired"],
           [[1, 171062, 1, "0", 9999, "", "chicken, bone removed", "171", "", "", ""],
            [2, 171062, 2, "1", 9999, "", "back, bone removed", "99", "", "", ""]])
    _write(tmp_path / "measure_unit.csv", ["id", "name"], [[9999, "undetermined"]])
    food = SR.load_sr(tmp_path)[171062]
    assert [x.description for x in food.portions] == ["back, bone removed"]
    assert lm("1 chicken", food).reason == "NO_SR_COUNT_PORTION"                  # no ZeroDivisionError


# --- A1: three-cell FDA rows -------------------------------------------------------------------------------------------
def test_a1_three_cell_row_with_empty_tail_is_kept() -> None:
    html = ("<table><tr><td>Pork &amp; Beans, rts.</td><td>5.70</td><td></td></tr>"
            "<tr><td>Odd</td><td>5.0</td><td>note</td></tr><tr><td>Plain</td><td>6.0</td></tr></table>")
    assert [r.item for r in PH.parse_fda_html(html)] == ["Pork & Beans, rts.", "Plain"]


# --- A2 / A3 / P5: the L-PH registry with parent context --------------------------------------------------------------
def test_p5_lph_registry_loads_with_parent_context() -> None:
    rows = PH.load_registry_lph(LPH)
    valued = [r for r in rows if r.low is not None]
    assert len(rows) == 488 and len(valued) == 479            # 8 NONE rows + "Cheese, Snippy" kept UNPARSED
    by = {r.item: r for r in rows}
    assert (by["pork & beans, rts"].low, by["pork & beans, rts"].value_type) == (5.70, "POINT")
    assert (by["tamarind"].low, by["tamarind"].high, by["tamarind"].value_type) == (3.0, None, "LOWER_BOUND_ONLY")
    assert by["cheese, snippy"].value_type == "UNPARSED" and by["cheese, snippy"].low is None
    assert by["guava, canned"].high == 4.10                    # documented whitespace repair


def test_a2_child_rows_keep_their_parent() -> None:
    t = PH.PHTable(PH.load_registry_lph(LPH))
    e = t.lookup("egg white")
    assert (e.basis, e.low, e.high) == ("FDA_ITEM_MATCH", 7.96, 7.96)
    r = t.lookup("white rice")
    assert r.basis == "FDA_ITEM_MATCH" and r.low <= 6.00 and r.high >= 6.70
    a = t.lookup("apple juice")
    assert (a.low, a.high, PH.acid_class(a)) == (3.35, 4.00, "ACID")
    rice = t.lookup("rice")                                    # head union now holds the cooked-rice children
    assert rice.low <= 5.40 and rice.high >= 6.80


# --- F4: lookup memo --------------------------------------------------------------------------------------------------
def test_f4_lookup_is_memoised() -> None:
    t = PH.PHTable(PH.load_registry_lph(LPH))
    assert t.lookup("lemon juice") is t.lookup("lemon juice")
    assert t.lookup("Lemon Juice") is t.lookup("lemon juice")


# --- A8 / F5 / A9 / A11: lot-state reasons, signed zero, outward rounding, labels ------------------------------------
def food(fdc, water, sodium_mg, sugars=None):
    n = {"water_g": water, "sodium_mg": sodium_mg}
    if sugars is not None:
        n["sugars_g"] = sugars
    return SRFood(fdc, f"F{fdc}", 11, MappingProxyType(n), ())


def mass(lo, hi):
    return LM.LineMass("POINT" if lo == hi else "INTERVAL", lo, hi, "TEXT_STATED_MASS", "SOURCE_STATED")


UNK_PH = PH.PHRange(None, None, "UNKNOWN", (), None, None)


def test_a8_f5_no_water_in_lot_and_no_negative_zero() -> None:
    s = LS.lot_state([LS.Member("sugar", food(1, 0.0, 1.0, sugars=99.8), mass(100, 100), UNK_PH)])
    w = s.composition["water_g"]
    assert w.low == 0.0 and math.copysign(1.0, w.low) == 1.0
    assert s.solute["sodium_mg_per_g_water"].reason == "NO_WATER_IN_LOT"
    s = LS.lot_state([LS.Member("x", food(1, 50.0, 1.0), mass(0, 0), UNK_PH)])
    assert s.solute["sodium_mg_per_g_water"].reason == "NO_POSITIVE_MASS"


def test_a9_bounds_are_rounded_outward() -> None:
    s = LS.lot_state([LS.Member("onion", food(1, 89.0, 4.0), mass(100, 100), UNK_PH),
                      LS.Member("lemon", food(2, 92.0, 1.0), mass(30, 30), UNK_PH)])
    w = s.composition["water_g"]
    exact = (Fraction(100) * Fraction(0.89) + Fraction(30) * Fraction(0.92)) / Fraction(130)
    assert Fraction(w.low) <= exact <= Fraction(w.high)
    assert w.high - w.low <= 4 * math.ulp(w.high)
    lo, hi = LS.ratio_bounds([(1.0, 1.0, 0.5, 1.0)])                          # exact values stay exact
    assert (lo, hi) == (0.5, 0.5)


def test_a11_labels_say_as_listed_and_non_citable() -> None:
    s = LS.lot_state([LS.Member("onion", food(1, 89.0, 4.0), mass(100, 100), UNK_PH, link_verified=True)])
    assert {"AS_LISTED_NO_PROCESS_EFFECTS", "NON_CITABLE"} <= set(s.labels)


# --- A10: registry terms are ACTIVE ING canonical names ---------------------------------------------------------------
def test_a10_every_registry_term_is_an_active_ing_name() -> None:
    latest = {}
    with open(ROOT / "ledgers/data/ING.jsonl", encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            latest[r["id"]] = r
    active = {r["canonical_name"] for r in latest.values() if r["status"] == "ACTIVE"}
    with open(ROOT / "registry/ing_sr_defaults_v1.csv", newline="", encoding="utf-8") as fh:
        terms = [r["term"] for r in csv.DictReader(fh)]
    assert [t for t in terms if t not in active] == []


# --- the census tool reads the L-PH registry -------------------------------------------------------------------------
def test_census_tool_uses_the_lph_registry() -> None:
    src = (ROOT / "tools/s175_line_mass_census.py").read_text(encoding="utf-8")
    assert "food_ph_fda_draft_v1.csv" in src and "load_registry_lph" in src
