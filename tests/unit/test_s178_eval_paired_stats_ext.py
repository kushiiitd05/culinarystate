"""S178: ucr_with_coverage (paired_stats) and backward compatibility of ucr."""
from __future__ import annotations

import pytest

from culinarystate.evaluation import paired_stats as PS


def test_ucr_with_coverage_distinguishes_silence_from_clean():
    silent = [(0, 0)] * 10
    clean = [(2, 0)] * 10
    assert PS.ucr(silent) == 0.0 and PS.ucr(clean) == 0.0                           # S173: indistinguishable
    a, b = PS.ucr_with_coverage(silent), PS.ucr_with_coverage(clean)
    assert a["ucr"] is None and a["claim_coverage"] == 0.0 and a["n_claims"] == 0
    assert b["ucr"] == 0.0 and b["claim_coverage"] == 1.0 and b["n_claims"] == 20


def test_ucr_with_coverage_mixed_and_empty():
    r = PS.ucr_with_coverage([(4, 1), (0, 0), (2, 2), (0, 0)])
    assert r["ucr"] == pytest.approx(3 / 6) and r["n_questions_with_claims"] == 2 and r["claim_coverage"] == 0.5
    e = PS.ucr_with_coverage([])
    assert e["ucr"] is None and e["claim_coverage"] is None and e["n_questions"] == 0
