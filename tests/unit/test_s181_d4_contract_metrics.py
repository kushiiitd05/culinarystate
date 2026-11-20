"""S181: D4 contract metrics (post-hoc diagnostic). Pure metric functions on small hand-built inputs."""
from __future__ import annotations

import importlib.util
import sys
from fractions import Fraction
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def _load():
    name = "s181_d4_contract_metrics"
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


M = _load()


# ------------------------------------------------------------------ Recall@K

def test_recall_at_k_known_values():
    gold, ranked = ["a", "b"], ["x", "a", "y", "b", "z"]
    assert M.recall_at_k(gold, ranked, 1) == 0.0
    assert M.recall_at_k(gold, ranked, 3) == 0.5
    assert M.recall_at_k(gold, ranked, 5) == 1.0
    assert M.recall_at_k(gold, ranked, 10) == 1.0


def test_recall_at_k_without_gold_is_none_not_zero():
    assert M.recall_at_k([], ["a"], 3) is None


def test_compat_recall_counts_only_compatible_gold_hits():
    gold, ranked = ["a", "b"], ["a", "b"]
    assert M.compat_recall_at_k(gold, ranked, 2, {"a": True, "b": False}) == 0.5
    assert M.compat_recall_at_k(gold, ranked, 2, {"a": True, "b": True}) == 1.0


def test_compat_recall_refuses_when_a_retrieved_gold_row_has_no_flag():
    with pytest.raises(M.NotComputable) as e:
        M.compat_recall_at_k(["a", "b"], ["a", "b"], 2, {"a": True})
    assert "b" in str(e.value)


def test_mean_over_questions_skips_nothing_silently():
    assert M.mean([0.0, 0.5, 1.0]) == 0.5
    assert M.mean([]) is None
    with pytest.raises(M.NotComputable):
        M.mean([0.5, None])


# ------------------------------------------------------------------ risk-coverage / AURC

def _pts(*triples):
    return [{"threshold": t, "answered": n, "errors": x, "n_total": 10} for t, x, n in triples]


def test_aurc_known_value():
    # coverage 0.5 risk 0/5 = 0; coverage 1.0 risk 5/10 = 0.5 -> trapezoid 0.5 * (0 + 0.5) / 2 = 0.125
    out = M.aurc_trapezoid(_pts(("HI", 0, 5), ("ALL", 5, 10)))
    assert out["partial_area"] == Fraction(1, 8)
    assert out["coverage_span"] == [Fraction(1, 2), Fraction(1)]
    assert out["normalized"] == Fraction(1, 4)


def test_aurc_is_monotone_in_errors():
    base = M.aurc_trapezoid(_pts(("HI", 1, 5), ("ALL", 4, 10)))["normalized"]
    worse_hi = M.aurc_trapezoid(_pts(("HI", 2, 5), ("ALL", 4, 10)))["normalized"]
    worse_all = M.aurc_trapezoid(_pts(("HI", 1, 5), ("ALL", 5, 10)))["normalized"]
    assert worse_hi > base and worse_all > base


def test_aurc_flat_curve_equals_the_flat_risk():
    assert M.aurc_trapezoid([{"threshold": t, "answered": n, "errors": x, "n_total": 20} for t, x, n in (("HI", 1, 4), ("MID", 2, 8), ("ALL", 5, 20))])["normalized"] == Fraction(1, 4)


def test_aurc_refuses_non_increasing_coverage_and_single_point():
    with pytest.raises(M.NotComputable):
        M.aurc_trapezoid(_pts(("HI", 0, 5), ("ALL", 1, 5)))
    with pytest.raises(M.NotComputable):
        M.aurc_trapezoid(_pts(("ALL", 1, 10)))


def test_aurc_does_not_extrapolate_below_the_first_observed_coverage():
    out = M.aurc_trapezoid(_pts(("HI", 0, 5), ("ALL", 5, 10)))
    assert out["coverage_span"][0] == Fraction(1, 2)          # nothing is invented for coverage < 0.5


# ------------------------------------------------------------------ unsupported-claim rate

def test_unsupported_claim_rate():
    assert M.unsupported_claim_rate(4, 34) == Fraction(4, 34)
    assert M.unsupported_claim_rate(0, 0) is None             # undefined, never coerced to 0
    with pytest.raises(ValueError):
        M.unsupported_claim_rate(5, 4)


# ------------------------------------------------------------------ ECE

def test_ece_known_value():
    # bin [0.9, 1.0): conf 0.9, acc 0.5, gap 0.4, weight 0.5; bin [0.6, 0.7): conf 0.6, acc 1.0, gap 0.4, weight 0.5
    out = M.expected_calibration_error([0.9, 0.9, 0.6, 0.6], [1, 0, 1, 1], n_bins=10)
    assert out["ece"] == pytest.approx(0.4)
    assert out["n"] == 4 and out["n_bins"] == 10 and out["binning"] == "equal-width"


def test_ece_perfectly_calibrated_is_zero():
    assert M.expected_calibration_error([1.0, 1.0, 0.0, 0.0], [1, 1, 0, 0], n_bins=10)["ece"] == 0.0


@pytest.mark.parametrize("conf", [None, [], [None, 0.5], ["QUANTITATIVE", "INTERVAL"], [1.2, 0.5], [True, False]])
def test_ece_refuses_absent_or_categorical_confidences(conf):
    with pytest.raises(M.NotComputable):
        M.expected_calibration_error(conf, [1, 0][: len(conf or [])], n_bins=10)


def test_ece_refuses_length_mismatch():
    with pytest.raises(M.NotComputable):
        M.expected_calibration_error([0.5, 0.5], [1], n_bins=10)


def test_find_numeric_confidence_fields():
    recs = [{"decision": {"precision": "QUANTITATIVE", "per_option": {"bake": {"sufficiency": "DIRECT"}}},
             "latency_s": 6.2, "checker": {"numeric_claims": 1}}]
    assert M.find_numeric_confidence_fields(recs) == []
    recs2 = [{"decision": {"confidence": 0.7}}, {"decision": {"per_option": {"a": {"probability": 0.2}}}}]
    assert M.find_numeric_confidence_fields(recs2) == ["decision.confidence", "decision.per_option.*.probability"]


def test_ece_block_reports_not_computable_for_categorical_run_records():
    recs = [{"rung": "B7", "decision": {"mode": "ANSWER", "precision": "QUANTITATIVE", "sufficiency": "DIRECT"}}]
    out = M.ece_block(recs)
    assert out["outcome"] == "NOT_COMPUTABLE"
    assert out["value"] is None
    assert "numeric" in out["missing_input"]


def test_labels_are_carried():
    for lab in ("MODEL_ASSISTED_GOLD", "NO_HUMAN_SIGNOFF_D085", "POST_HOC_DIAGNOSTIC"):
        assert lab in M.LABELS
