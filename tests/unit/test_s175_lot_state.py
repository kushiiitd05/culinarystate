"""S175: lot composition state — exact interval bounds of mixture ratios, pH flags, provenance labels."""
from __future__ import annotations

import itertools
import math
import random
from types import MappingProxyType

import pytest

from culinarystate.composition import lot_state as LS
from culinarystate.composition.food_ph import PHRange
from culinarystate.composition.line_mass import LineMass
from culinarystate.composition.sr_legacy import SRFood


def brute(terms):
    """Vertex enumeration (finite boxes only) as the reference."""
    vals = []
    for pick in itertools.product(*[(lo, hi) for lo, hi, _, _ in terms]):
        den = sum(m * d for m, (_, _, _, d) in zip(pick, terms))
        if den > 0:
            vals.append(sum(m * n for m, (_, _, n, _) in zip(pick, terms)) / den)
    return min(vals), max(vals)


def test_ratio_bounds_match_vertex_enumeration() -> None:
    rng = random.Random(7)
    for _ in range(300):
        k = rng.randint(1, 6)
        terms = []
        for _ in range(k):
            lo = rng.choice([0.0, rng.uniform(0, 50)])
            terms.append((lo, lo + rng.uniform(0, 100), rng.uniform(0, 1), rng.choice([1.0, rng.uniform(0.01, 1)])))
        lo, hi = LS.ratio_bounds(terms)
        b = brute(terms)
        assert lo == pytest.approx(b[0], abs=1e-12) and hi == pytest.approx(b[1], abs=1e-12)


def test_unbounded_member_pulls_bound_to_its_ratio() -> None:
    # 100 g at 0.10 plus an unknown amount (>= 0) at 0.80: fraction in [0.10, 0.80)
    lo, hi = LS.ratio_bounds([(100.0, 100.0, 0.10, 1.0), (0.0, None, 0.80, 1.0)])
    assert (lo, hi) == pytest.approx((0.10, 0.80))


def test_zero_denominator_member_makes_upper_unbounded() -> None:
    # salt has (almost) no water: sodium per water can be unbounded if salt mass is unbounded
    lo, hi = LS.ratio_bounds([(100.0, 100.0, 0.0, 0.9), (0.0, None, 0.39, 0.0)])
    assert lo == 0.0 and hi is None


def food(fdc, water, sodium_mg, sugars=None):
    n = {"water_g": water, "sodium_mg": sodium_mg}
    if sugars is not None:
        n["sugars_g"] = sugars
    return SRFood(fdc, f"F{fdc}", 11, MappingProxyType(n), ())


def mass(lo, hi, q="Q0", verify=False):
    st = "POINT" if lo == hi else "INTERVAL"
    return LineMass(st, lo, hi, "TEXT_STATED_MASS", "SOURCE_STATED", None, None, (), q, verify)


UNK = LineMass("UNKNOWN", None, None, "UNKNOWN", None, "NO_AMOUNT")
PH_LEMON = PHRange(2.0, 2.6, "FDA_ITEM_MATCH", ("Lemon juice",), 2.0, 2.6)
PH_ONION = PHRange(5.3, 5.85, "FDA_HEAD_UNION", ("Onions, red",), 5.3, 5.85)
PH_UNK = PHRange(None, None, "UNKNOWN", (), None, None)


def test_lot_mass_fraction_and_solute_per_water() -> None:
    members = [LS.Member("onion", food(1, 89.0, 4.0), mass(100, 100), PH_ONION, link_verified=True),
               LS.Member("lemon juice", food(2, 92.0, 1.0), mass(30, 30), PH_LEMON, link_verified=True)]
    s = LS.lot_state(members)
    w = s.composition["water_g"]
    assert w.status == "INTERVAL" and w.low == pytest.approx((89 + 0.92 * 30) / 130)
    assert w.high - w.low <= 4 * math.ulp(w.high)                  # S179 A9: outward-rounded point
    na = s.solute["sodium_mg_per_g_water"]
    assert na.low == pytest.approx((4.0 + 0.3) / (89 + 27.6))
    assert (s.total_mass_g.low, s.total_mass_g.high) == (130.0, 130.0)
    assert s.labels == ("MODEL_DERIVED", "COMPOSITION_FROM_SR_LEGACY", "AS_LISTED_NO_PROCESS_EFFECTS", "NON_CITABLE")


def test_unknown_member_composition_makes_that_component_unknown() -> None:
    members = [LS.Member("onion", food(1, 89.0, 4.0), mass(100, 100), PH_ONION),
               LS.Member("lemon juice", food(2, 92.0, 1.0, sugars=2.5), mass(30, 30), PH_LEMON)]
    s = LS.lot_state(members)
    assert s.composition["sugars_g"].status == "UNKNOWN"
    assert s.composition["sugars_g"].reason == "MEMBER_COMPOSITION_UNKNOWN"
    assert s.composition["protein_g"].status == "UNKNOWN"


def test_unknown_food_or_mass() -> None:
    s = LS.lot_state([LS.Member("onion", food(1, 89.0, 4.0), mass(100, 100), PH_ONION),
                      LS.Member("saffron", None, mass(1, 1), PH_UNK)])
    assert s.composition["water_g"].reason == "MEMBER_FOOD_UNKNOWN"
    s = LS.lot_state([LS.Member("onion", food(1, 89.0, 4.0), mass(100, 100), PH_ONION),
                      LS.Member("salt", food(3, 0.2, 38758.0), UNK, PH_UNK)])
    w = s.composition["water_g"]
    assert w.status == "INTERVAL" and w.low == pytest.approx(0.002) and w.high == pytest.approx(0.89)
    assert s.total_mass_g.high is None and s.solute["sodium_mg_per_g_water"].high is not None


def test_ph_flags_never_a_mixture_number() -> None:
    s = LS.lot_state([LS.Member("onion", food(1, 89.0, 4.0), mass(100, 100), PH_ONION),
                      LS.Member("lemon juice", food(2, 92.0, 1.0), mass(30, 30), PH_LEMON)])
    assert s.ph_flags == ("CONTAINS_ACID_MEMBER",)
    assert s.member_ph == (("onion", "LOW_ACID"), ("lemon juice", "ACID"))
    assert not hasattr(s, "ph")
    s2 = LS.lot_state([LS.Member("lemon juice", food(2, 92.0, 1.0), mass(30, 30), PH_LEMON)])
    assert s2.ph_flags == ("ALL_MEMBERS_ACID", "CONTAINS_ACID_MEMBER")
    s3 = LS.lot_state([LS.Member("x", food(2, 92.0, 1.0), mass(30, 30), PH_UNK)])
    assert s3.ph_flags == ("ANY_MEMBER_PH_UNKNOWN",)


def test_sr_link_or_portion_grams_make_the_state_provisional() -> None:
    s = LS.lot_state([LS.Member("onion", food(1, 89.0, 4.0), mass(70, 150, "Q1", True), PH_ONION)])
    assert "PROVISIONAL_SR_LINK_UNVERIFIED" in s.labels
    s = LS.lot_state([LS.Member("onion", food(1, 89.0, 4.0), mass(100, 100), PH_ONION)])   # default: unverified
    assert "PROVISIONAL_SR_LINK_UNVERIFIED" in s.labels


def test_empty_lot_rejected() -> None:
    with pytest.raises(ValueError):
        LS.lot_state([])
