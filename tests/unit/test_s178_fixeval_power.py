"""S178 FIX-EVAL: SCI-B E7 (McNemar power / MDE wording and tables). Planning arithmetic only.

Failure scenario (review): "power is a sawtooth in delta -> conservative MDE" is wrong (at fixed n and d power is monotone in
delta; the sawtooth is in n), and the headline ranges mix discordance ranges (n = 30 covers d 0.3-0.5, n = 60 covers d 0.2-0.5).
"""
from __future__ import annotations

import inspect

import pytest

from culinarystate.evaluation import mcnemar_power as MP


@pytest.mark.parametrize("n", [15, 30, 60])
@pytest.mark.parametrize("d", [0.2, 0.3, 0.4, 0.5])
def test_power_is_monotone_in_delta_at_fixed_n_and_d(n, d):
    assert MP.power_monotone_in_delta(n, d, step=0.005)


def test_the_sawtooth_is_in_the_discordant_count_not_in_delta():
    cp = [MP.conditional_power(m, 0.3, 0.4) for m in range(1, 41)]
    assert any(b < a for a, b in zip(cp, cp[1:]))                                      # falls for some m -> m + 1 (6 -> 7)
    assert round(cp[5], 3) == 0.449 and round(cp[6], 3) == 0.393
    ps = [MP.power(n, 0.3, 0.4) for n in range(5, 81)]                                 # averaged over m: smooth in n here
    assert all(b >= a - 1e-12 for a, b in zip(ps, ps[1:]))


def test_mde_docstring_no_longer_claims_a_sawtooth_in_delta():
    doc = inspect.getdoc(MP.mde)
    assert "sawtooth in delta" not in doc and "monotone" in doc
    assert "sawtooth" not in (MP.__doc__ or "").split("S178 FIX-EVAL")[0].lower()


def test_first_crossing_equals_the_mde():
    for n in (30, 60):
        for d in (0.3, 0.4, 0.5):
            assert MP.mde(n, d) == MP.mde_first_crossing(n, d)


def test_headline_states_the_discordance_range_per_n_and_a_common_range():
    t = MP.planning_table(ns=(30, 60))
    assert t["grid_step"] == 0.005
    h = t["headline_by_n"]
    assert h["30"]["discordance_range_with_mde"] == [0.3, 0.5] and h["30"]["mde_range"] == [0.275, 0.365]
    assert h["30"]["discordances_without_mde"] == [0.2]
    assert h["60"]["discordance_range_with_mde"] == [0.2, 0.5] and h["60"]["mde_range"] == [0.165, 0.265]
    c = t["common_discordance_range"]
    assert c["discordance_range"] == [0.3, 0.5]
    assert c["mde_range_by_n"] == {"30": [0.275, 0.365], "60": [0.205, 0.265]}
