"""S178 / T9-C12-R1: exact McNemar power and MDE (n = 30 / 60), hand-checked values; reuses paired_stats."""
from __future__ import annotations

import math

import pytest

from culinarystate.evaluation import mcnemar_power as MP
from culinarystate.evaluation import paired_stats as PS


def test_min_discordant_and_majority_thresholds():
    assert MP.min_discordant_for_significance(0.05) == 6            # 2 * 0.5**6 = 0.03125 <= 0.05; m = 5 gives 0.0625
    assert PS.mcnemar_exact(0, 5) > 0.05 >= PS.mcnemar_exact(0, 6)
    assert MP.min_majority_for_significance(5) is None
    assert MP.min_majority_for_significance(6) == 6
    assert MP.min_majority_for_significance(10) == 9                # 9:1 -> 22/1024 = 0.0215; 8:2 -> 0.109
    assert PS.mcnemar_exact(9, 1) == pytest.approx(22 / 1024) and PS.mcnemar_exact(8, 2) > 0.05
    t = MP.rejection_table(30)
    assert t[0] is None and t[5] is None and t[6] == 6 and t[30] == 21
    assert PS.mcnemar_exact(21, 9) == pytest.approx(0.0428, abs=5e-4) and PS.mcnemar_exact(20, 10) > 0.05


def test_rejection_table_matches_the_reused_test_for_every_m():
    for m, k in MP.rejection_table(30).items():
        if k is None:
            assert all(PS.mcnemar_exact(b, m - b) > 0.05 for b in range(m + 1))
        else:
            assert PS.mcnemar_exact(k, m - k) <= 0.05 and (k - 1 <= m / 2 or PS.mcnemar_exact(k - 1, m - k + 1) > 0.05)


def test_power_hand_checked_and_properties():
    # n = 10, every discordant pair favours x, d = 0.5: m ~ Bin(10, .5), rejects iff m >= 6 -> 386 / 1024
    assert MP.power(10, 0.5, 0.5) == pytest.approx(386 / 1024)
    assert MP.power(30, 0.2, 0.4) == pytest.approx(MP.power(30, -0.2, 0.4))          # two-sided symmetry
    null = MP.power(30, 0.0, 0.4)
    assert 0 < null <= 0.05                                                         # exact test is conservative
    ps = [MP.power(30, g / 100, 0.5) for g in (10, 20, 30, 40, 50)]
    assert ps[-1] > ps[0] and ps[-1] > 0.9
    assert MP.power(60, 0.2, 0.4) > MP.power(30, 0.2, 0.4)                          # more questions, more power
    assert MP.power(30, 0.0, 0.0) == 0.0
    with pytest.raises(ValueError):
        MP.power(30, 0.5, 0.3)                                                      # gap larger than discordance
    with pytest.raises(ValueError):
        MP.power(0, 0.1, 0.3)


def test_power_matches_a_brute_force_enumeration():
    n, pb, pc = 8, 0.30, 0.10
    total = 0.0
    for b in range(n + 1):
        for c in range(n + 1 - b):
            pr = math.factorial(n) // (math.factorial(b) * math.factorial(c) * math.factorial(n - b - c))
            pr *= pb ** b * pc ** c * (1 - pb - pc) ** (n - b - c)
            if PS.mcnemar_exact(b, c) <= 0.05:
                total += pr
    assert MP.power(n, pb - pc, pb + pc) == pytest.approx(total, abs=1e-12)


def test_mde_is_conservative_and_shrinks_with_n():
    m30, m60 = MP.mde(30, 0.4), MP.mde(60, 0.4)
    assert m30 is not None and m60 is not None and m60 < m30
    for g in (m30, 0.4):                                                            # power stays >= 0.8 from the MDE up
        assert MP.power(30, g, 0.4) >= 0.8
    assert MP.mde(30, 0.05) is None                                                 # d = 0.05: never reaches 80 %
    assert 0.2 <= m30 <= 0.4                                                        # REV-B range for n = 30 is ~0.28-0.33


def test_iu_bounds_and_realised_statement():
    assert MP.iu_power_bounds(0.8, 0.8) == (pytest.approx(0.6), 0.8)
    assert MP.iu_power_bounds(0.4, 0.4) == (0.0, 0.4)
    r = MP.describe_realised(30, 4, 1)
    assert r["can_be_significant"] is False and "cannot be significant at this n" in r["statement"]
    r = MP.describe_realised(30, 12, 2)
    assert r["can_be_significant"] and r["statement"] == "significant" and r["min_majority_needed"] == 12
    r = MP.describe_realised(30, 8, 5)
    assert r["statement"] == "not significant at this n" and r["p_exact"] == pytest.approx(PS.mcnemar_exact(8, 5))


def test_design_interval_reuses_newcombe():
    di = MP.design_interval(40, 0.5, 0.3, 0.4)                                      # pi_b = 0.35, pi_c = 0.05
    a, b, c, d = di["counts_abcd"]
    assert (a + b + c + d) == 40 and (b, c) == (14, 2) and di["diff"] == 0.3
    assert di["newcombe95"] == [round(x, 4) for x in PS.newcombe_paired(a, b, c, d)]
    with pytest.raises(ValueError):
        MP.design_interval(40, 0.0, 0.3, 0.4)                                       # baseline 0 cannot host 3 only-y pairs


def test_planning_table_covers_n30_n60():
    t = MP.planning_table()
    assert {r["n"] for r in t["rows"]} == {30, 60} and t["min_discordant_for_alpha"] == 6
    by = {(r["n"], r["discordance"]): r for r in t["rows"]}
    assert by[(60, 0.4)]["mde"] < by[(30, 0.4)]["mde"]
    assert all(r["iu_power_bounds_at_mde"][0] <= r["iu_power_bounds_at_mde"][1] for r in t["rows"] if r["mde"])
