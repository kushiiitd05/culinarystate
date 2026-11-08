"""S173 / M5: paired statistics for H1 (exact McNemar; Newcombe 1998 method 10 interval). Hand-checked values."""
from __future__ import annotations

import pytest

from culinarystate.evaluation import paired_stats as PS


def test_mcnemar_exact_known_values():
    # b=0, c=6: two-sided exact p = 2 * 0.5**6 = 0.03125
    assert PS.mcnemar_exact(0, 6) == pytest.approx(0.03125)
    assert PS.mcnemar_exact(3, 3) == pytest.approx(1.0)
    assert PS.mcnemar_exact(0, 0) == 1.0
    # b=1, c=9: 2 * (C(10,0)+C(10,1)) / 2**10 = 22/1024
    assert PS.mcnemar_exact(1, 9) == pytest.approx(22 / 1024)


def test_wilson_matches_textbook():
    lo, hi = PS.wilson(19, 20)
    assert lo == pytest.approx(0.7639, abs=1e-3) and hi == pytest.approx(0.9911, abs=1e-3)


def test_newcombe_interval_properties():
    lo, hi = PS.newcombe_paired(a=10, b=8, c=2, d=10)
    diff = (8 - 2) / 30
    assert -1 <= lo < diff < hi <= 1
    lo2, hi2 = PS.newcombe_paired(a=10, b=4, c=4, d=12)
    assert lo2 < 0 < hi2 and lo2 == pytest.approx(-hi2, abs=1e-9)


def test_paired_counts_from_vectors():
    assert PS.paired_counts([1, 1, 0, 0, 1], [1, 0, 1, 0, 0]) == (1, 2, 1, 1)
    with pytest.raises(ValueError):
        PS.paired_counts([1], [1, 0])
