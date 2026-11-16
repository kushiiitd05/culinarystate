import itertools
import random
from fractions import Fraction as F

import pytest

from culinarystate.lotstate import values as V
from culinarystate.lotstate.intervals import float_hi, float_lo, ratio_bounds


def brute(members, grid=5):
    """min / max of sum(m a) / sum(m b) over a grid of the box (vertices included)."""
    axes = []
    for lo, hi, a, b in members:
        axes.append([lo + (hi - lo) * F(i, grid - 1) for i in range(grid)])
    best_lo = best_hi = None
    for combo in itertools.product(*axes):
        den = sum(m * b for m, (_, _, _, b) in zip(combo, members))
        if den <= 0:
            continue
        r = sum(m * a for m, (_, _, a, _) in zip(combo, members)) / den
        best_lo = r if best_lo is None or r < best_lo else best_lo
        best_hi = r if best_hi is None or r > best_hi else best_hi
    return best_lo, best_hi


def test_two_member_hand_check():
    # m1 in [0,10] a=5 ; m2 in [10,20] a=1 ; b=1 : fraction (5 m1 + m2)/(m1 + m2)
    lo, hi, st = ratio_bounds([(F(0), F(10), F(5), F(1)), (F(10), F(20), F(1), F(1))])
    assert (lo, hi, st) == (F(1), F(3), "EXACT")


def test_point_masses_give_the_weighted_average():
    lo, hi, st = ratio_bounds([(F(100), F(100), F(10), F(1)), (F(300), F(300), F(2), F(1))])
    assert lo == hi == F(1600, 400)


@pytest.mark.parametrize("seed", range(40))
def test_matches_brute_force_on_random_boxes(seed):
    rnd = random.Random(seed)
    n = rnd.randint(1, 4)
    members = []
    for _ in range(n):
        lo = F(rnd.randint(0, 5))
        hi = lo + F(rnd.randint(0, 6))
        members.append((lo, hi, F(rnd.randint(0, 9), rnd.randint(1, 3)), F(rnd.randint(0, 4), rnd.randint(1, 2))))
    lo, hi, st = ratio_bounds(members)
    blo, bhi = brute(members)
    if st == "UNDEFINED":
        assert blo is None
    elif st == "UNBOUNDED_ABOVE":
        assert hi is None and lo is not None and lo <= blo
    else:
        # the exact bound is at least as wide as any grid value and is attained at a vertex
        assert lo <= blo and hi >= bhi
        vlo, vhi = brute(members, grid=2)
        assert (lo, hi) == (vlo, vhi)


def test_unbounded_when_no_water_member_can_hold_the_solute():
    # salt member (b = 0 water) with an oil member: g salt per g water is unbounded above
    lo, hi, st = ratio_bounds([(F(1), F(2), F(5), F(0)), (F(1), F(2), F(0), F(0))])
    assert st == "UNDEFINED" or hi is None


def test_undefined_without_live_members():
    assert ratio_bounds([(F(0), F(0), F(1), F(1))])[2] == "UNDEFINED"


def test_float_bounds_round_outward():
    x = F(1, 3)
    assert float_lo(x) <= x <= float_hi(x)
    assert F(float_lo(x)) <= x and F(float_hi(x)) >= x


def test_value_record_contract():
    prov = V.provenance("TEST")
    rec = V.numeric(F(1), F(2), "g", basis="X", prov=prov)
    V.check_record(rec)
    assert rec["type"] == "INTERVAL" and rec["mask"] == 1
    pt = V.numeric(F(3), F(3), "g", basis="X", prov=prov)
    assert pt["type"] == "POINT"
    unk = V.unknown("g", "WHY")
    V.check_record(unk)
    assert unk["mask"] == 0 and "value" not in unk
    bad = dict(rec)
    bad["provenance"] = {"labels": []}
    with pytest.raises(ValueError):
        V.check_record(bad)
