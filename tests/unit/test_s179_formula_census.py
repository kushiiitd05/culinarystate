"""D-100 Lane S / D-104: AA formula census gate and retention (counts only)."""
from __future__ import annotations

import importlib.util
import math
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("fc", ROOT / "tools" / "s179_formula_census.py")
fc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fc)

FIT = {"n_papers": 2, "papers": ["A", "B"], "intercepts": {"A": -4.0, "B": -3.0}, "Ea_J_per_mol": 64000.0,
       "cov": [[0.01, 0, 0], [0, 0.01, 0], [0, 0, 1e8]], "sigma_between": 0.8, "residual_sd": 0.2, "T_ref_K": 363.15}


def l1(mc="FRUIT", groups=("FRUIT",), medium="PAN_CONTACT_OIL"):
    return {"inputs": {"matrix_class": {"value": mc}, "matrix_groups": {"value": list(groups)},
                       "medium": {"value": medium}}}


def l2(status="SCENARIO_COMPUTED", bath=95.0, cap=100.0, dur=20.0):
    sc = {"bath_c": bath, "t_cap_c": cap, "duration_min": dur}
    return {"status": status, "scenarios": {"GENTLE": dict(sc), "TYPICAL": dict(sc), "INTENSE": dict(sc)}}


def test_in_domain_fruit_jam_like_event():
    assert fc.gate(l1(), l2(), "TYPICAL") == (True, "IN_DOMAIN", 95.0, 20.0)


@pytest.mark.parametrize("a,b,reason", [
    (l1(mc="VEGETABLE", groups=("VEGETABLE",)), l2(), "MATRIX_NOT_ACIDIC_FRUIT"),
    (l1(medium="WATER"), l2(), "WATER_CONTACT"),
    (l1(medium=None), l2(), "MEDIUM_UNKNOWN"),
    (l1(), l2(status="SCENARIO_UNKNOWN"), "SCENARIO_NOT_COMPUTED"),
    (l1(), l2(bath=180.0, cap=None), "T_OUT_OF_RANGE"),
    (l1(), l2(bath=40.0), "T_OUT_OF_RANGE"),
    (l1(), l2(dur=0), "NO_DURATION"),
])
def test_out_of_domain_reasons(a, b, reason):
    ok, why, *_ = fc.gate(a, b, "TYPICAL")
    assert not ok and why == reason


def test_mixed_fruit_sweetener_allowed_but_needs_fruit():
    assert fc.gate(l1(mc=None, groups=("FRUIT", "SWEETENER")), l2(), "GENTLE")[0]
    assert not fc.gate(l1(mc=None, groups=("SWEETENER",)), l2(), "GENTLE")[0]


def test_food_temperature_is_capped():
    ok, _, T, _ = fc.gate(l1(), l2(bath=180.0, cap=100.0), "TYPICAL")
    assert ok and T == 100.0


def test_retention_bounds_and_order():
    mid, lo, hi = fc.retention(FIT, 95.0, 20.0)
    assert 0 < lo <= mid <= hi <= 1
    # a longer time lowers retention
    assert fc.retention(FIT, 95.0, 60.0)[0] < mid


def test_retention_matches_first_order():
    mid, _, _ = fc.retention(FIT, 90.0, 10.0)
    lnk = (-4.0 - 3.0) / 2 - (1 / (90 + 273.15) - 1 / 363.15) * 64000.0 / 8.314462618
    assert mid == pytest.approx(math.exp(-math.exp(lnk) * 10.0), rel=1e-6)
