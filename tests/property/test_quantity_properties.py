"""SSOT §257I.2 property-based quantity tests (seeded stdlib generators; no hypothesis dependency).

Equivalent exact-unit expressions must give identical canonical results; locale-ambiguous culinary units must stay
ambiguous (no invented precision); text without a number never yields a MEASURED quantity.
"""
import random

import pytest

from culinarystate.evidence.conditions import extract_conditions
from culinarystate.quantity.grammar import parse_line
from culinarystate.quantity.normalize import normalize

RNG = random.Random(20261018)
VALUES = [round(RNG.uniform(0.05, 50), 2) for _ in range(60)] + [0.25, 0.5, 1, 2, 3, 10, 12]
FOODS = ["flour", "caster sugar", "water", "whole milk", "chicken stock", "rice"]


def _q(text, locale="UK"):
    return normalize(parse_line(text), locale=locale)


def _num(x: float) -> str:
    return f"{x:g}"


@pytest.mark.parametrize("v", VALUES)
def test_kg_equals_thousand_g(v):
    food = RNG.choice(FOODS)
    a, b = _q(f"{_num(v)} kg {food}").mass_g, _q(f"{_num(round(v * 1000, 4))} g {food}").mass_g
    assert a["status"] == b["status"] == "MEASURED" and a["value"] == pytest.approx(b["value"], rel=1e-9)


@pytest.mark.parametrize("v", VALUES)
def test_litre_equals_thousand_ml(v):
    a, b = _q(f"{_num(v)} l water").volume_ml, _q(f"{_num(round(v * 1000, 4))} ml water").volume_ml
    assert a["status"] == b["status"] == "MEASURED" and a["value"] == pytest.approx(b["value"], rel=1e-9)


@pytest.mark.parametrize("v", [1, 2, 3, 0.5, 4])
def test_pound_equals_sixteen_ounces(v):
    a, b = _q(f"{_num(v)} lb sugar").mass_g, _q(f"{_num(v * 16)} oz sugar").mass_g
    assert a["value"] == pytest.approx(b["value"], rel=1e-9)


@pytest.mark.parametrize("vulgar,dec", [("½", 0.5), ("1½", 1.5), ("¼", 0.25), ("2¾", 2.75), ("1/2", 0.5), ("3/4", 0.75)])
def test_fraction_forms_equal_decimals(vulgar, dec):
    assert _q(f"{vulgar} kg rice").mass_g["value"] == pytest.approx(_q(f"{dec} kg rice").mass_g["value"])


@pytest.mark.parametrize("lo,hi", [(1, 2), (2, 3), (100, 150)])
def test_ranges_keep_both_ends_and_scale_exactly(lo, hi):
    g = _q(f"{lo}-{hi} kg potatoes").mass_g
    assert g["status"] == "RANGE" and (g["low"], g["high"]) == (lo * 1000, hi * 1000)


@pytest.mark.parametrize("locale", ["UK", None])
def test_ambiguous_cup_never_gets_invented_precision(locale):
    v = _q("1 cup milk", locale=locale).volume_ml
    assert v["status"] == "RANGE" and v["low"] < v["high"]


def test_resolved_us_cup_is_exact():
    v = _q("2 cups milk", locale="US").volume_ml
    assert v["status"] == "MEASURED" and v["value"] == pytest.approx(2 * 236.5882365)


@pytest.mark.parametrize("text", ["salt to taste", "a handful of herbs", "some butter", "oil for frying", "pepper"])
def test_no_number_never_measured(text):
    z = _q(text)
    assert all(ch["status"] != "MEASURED" for ch in (z.mass_g, z.volume_ml, z.count))


@pytest.mark.parametrize("c", [RNG.randint(-30, 260) for _ in range(25)] + [-18, 0, 100, 180])
def test_temperature_celsius_fahrenheit_same_physical_value(c):
    f = round(c * 9 / 5 + 32, 1)
    tc = extract_conditions(f"bake at {c} °C")["temperatures"][0]["value"]
    tf = extract_conditions(f"bake at {f:g} °F")["temperatures"][0]["value"]
    assert tc["unit"] == "degC" and tf["unit"] == "degF"
    assert (tf["value"] - 32) * 5 / 9 == pytest.approx(tc["value"], abs=0.06)


@pytest.mark.parametrize("v", VALUES[:20])
def test_raw_text_is_always_preserved(v):
    t = f"{_num(v)} kg flour, sifted"
    assert _q(t).mass_g["raw"] == t
