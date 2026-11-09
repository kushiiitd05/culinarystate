"""S175: ingredient line -> grams interval (stated mass, volume x SR density, count x SR portion, else UNKNOWN)."""
from __future__ import annotations

from types import MappingProxyType

import pytest

from culinarystate.composition import line_mass as LM
from culinarystate.composition.sr_legacy import Portion, SRFood
from culinarystate.quantity.grammar import parse_line
from culinarystate.quantity.normalize import normalize


def p(desc: str, g: float, amount: float = 1.0) -> Portion:
    return Portion(desc, g, amount, 9999, "undetermined")


ONION = SRFood(170000, "Onions, raw", 11, MappingProxyType({}), (
    p("cup, chopped", 160), p("medium (2-1/2\" dia)", 110), p("large (3\" dia)", 150), p("small", 70),
    p("tbsp chopped", 10), p("slice, large (1/4\" thick)", 38)))
GARLIC = SRFood(169230, "Garlic, raw", 11, MappingProxyType({}), (p("cup", 136), p("tsp", 2.8), p("clove", 3)))
EGG = SRFood(171287, "Egg, whole, raw, fresh", 1, MappingProxyType({}), (
    p("large", 50), p("extra large", 56), p("medium", 44), p("cup (4.86 large eggs)", 243)))
OIL = SRFood(171413, "Oil, olive, salad or cooking", 4, MappingProxyType({}), (p("tbsp", 13.5), p("cup", 216)))
NO_PORTIONS = SRFood(1, "Salt, table", 2, MappingProxyType({}), ())


def lm(line: str, food, locale="UK", **kw):
    q = parse_line(line)
    return LM.line_mass(q, normalize(q, locale), food, **kw)


def test_stated_mass_is_source_stated_point() -> None:
    r = lm("200g plain flour", None)
    assert (r.status, r.low_g, r.high_g, r.basis, r.value_type) == ("POINT", 200.0, 200.0, "TEXT_STATED_MASS",
                                                                    "SOURCE_STATED")


def test_volume_times_sr_density_interval() -> None:
    r = lm("2 tbsp olive oil", OIL)
    # UK tbsp = 15 mL; SR densities: 13.5 g / 14.787 mL and 216 g / 236.588 mL
    d_tbsp, d_cup = 13.5 / 14.78676478125, 216 / 236.5882365
    assert r.basis == "VOLUME_x_SR_DENSITY" and r.value_type == "MODEL_DERIVED" and r.fdc_id == 171413
    assert r.low_g == pytest.approx(30 * min(d_tbsp, d_cup)) and r.high_g == pytest.approx(30 * max(d_tbsp, d_cup))
    assert r.status == "INTERVAL"


def test_volume_range_and_ambiguous_locale_widen_the_interval() -> None:
    r = lm("1/2 cup olive oil", OIL, locale=None)
    d = sorted((13.5 / 14.78676478125, 216 / 236.5882365))
    assert r.low_g == pytest.approx(118.29411825 * d[0]) and r.high_g == pytest.approx(125.0 * d[1])


def test_count_uses_size_word_first_token_only() -> None:
    r = lm("2 large eggs", EGG)
    assert (r.low_g, r.high_g, r.basis) == (100.0, 100.0, "COUNT_x_SR_PORTION")
    assert r.portions == ("large",)


def test_count_uses_portion_noun_in_line() -> None:
    r = lm("3 garlic cloves", GARLIC)
    assert (r.low_g, r.high_g, r.portions) == (9.0, 9.0, ("clove",))


def test_bare_count_spans_whole_item_portions_not_slices() -> None:
    r = lm("1 onion, finely chopped", ONION)
    assert (r.low_g, r.high_g, r.status) == (70.0, 150.0, "INTERVAL")
    assert set(r.portions) == {"small", "medium (2-1/2\" dia)", "large (3\" dia)"}


def test_unknown_paths_carry_a_reason() -> None:
    assert lm("1 onion", None).reason == "NO_SR_FOOD"
    assert lm("2 tbsp salt", NO_PORTIONS).reason == "NO_SR_DENSITY"
    assert lm("1 salt", NO_PORTIONS).reason == "NO_SR_COUNT_PORTION"
    r = lm("onion", ONION)
    assert (r.status, r.reason, r.low_g) == ("UNKNOWN", "NO_AMOUNT", None)


def test_qualitative_and_units_missing() -> None:
    r = lm("a pinch of salt", NO_PORTIONS)
    assert (r.status, r.basis, r.low_g) == ("QUALITATIVE", "QUALITATIVE", None)
    r = lm("2 onion", ONION, units_missing=True)
    assert (r.status, r.basis, r.reason) == ("UNKNOWN", "UNIT_MISSING_IN_SOURCE", "UNIT_MISSING_IN_SOURCE")


def test_volume_portion_parser() -> None:
    assert LM.portion_ml(p("cup, chopped", 160)) == pytest.approx(236.5882365)
    assert LM.portion_ml(p("tbsp chopped", 10)) == pytest.approx(14.78676478125)
    assert LM.portion_ml(p("fl oz", 30, amount=2)) == pytest.approx(2 * 29.5735295625)
    assert LM.portion_ml(Portion("cup", 200, 1, 1000, "cup")) == pytest.approx(236.5882365)
    assert LM.portion_ml(p("medium", 110)) is None
