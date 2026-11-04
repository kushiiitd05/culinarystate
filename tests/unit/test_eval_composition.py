"""DRAFT_PENDING_34a_0 -- tests for the Step 34a composition-consistency scaffold.

Synthetic composite rows only. rho and c_floor are test inputs; the plan's values are
PROPOSED_PILOT and are never defaulted in code.
"""
from __future__ import annotations

import inspect

import pytest

from culinarystate.evaluation import composition as cp


def _codes(exc) -> set[str]:
    return {b.split(":", 1)[0] for b in exc.value.blockers}


ONE_STEP = {"blanch": 0.9, "freeze": 0.8, "boil": 0.5}


def _comp(i: int, steps, observed, source="SYN-LIT", component=None, interval=None):
    return cp.CompositeRow(row_id=f"C{i}", source_family=source, steps=tuple(steps), observed=observed,
                           component=component or f"LC{i}", interval=interval)


def _rows(noise: float = 0.0, interval_halfwidth: float = 0.2):
    rows = []
    for i in range(10):
        steps = ("blanch", "freeze") if i % 2 else ("blanch", "boil")
        chain = ONE_STEP[steps[0]] * ONE_STEP[steps[1]]
        obs = chain + (noise if i % 3 else -noise)
        rows.append(_comp(i, steps, obs, interval=(chain - interval_halfwidth, chain + interval_halfwidth)))
    return rows


def test_chain_is_the_product_of_one_step_factors():
    assert cp.chain_prediction(("blanch", "freeze"), ONE_STEP.__getitem__) == pytest.approx(0.72)
    with pytest.raises(cp.CompositionRefused) as exc:
        cp.chain_prediction(("blanch",), ONE_STEP.__getitem__)
    assert "NOT_MULTI_STEP" in _codes(exc)


def test_rho_and_c_floor_have_no_defaults():
    params = inspect.signature(cp.composition_consistency).parameters
    for name in ("rho", "c_floor", "circularity"):
        assert params[name].default is inspect.Parameter.empty, name


def _run(rows, **over):
    kw = dict(one_step=ONE_STEP.__getitem__, lookup=lambda r: r.observed + 0.05, rho=0.5, c_floor=0.5,
              circularity={"SYN-LIT": "CHECKED_NOT_DERIVED"})
    kw.update(over)
    return cp.composition_consistency(rows, **kw)


def test_exact_chain_is_consistent():
    out = _run(_rows())
    assert out["verdict"] == "CHAIN_CONSISTENT"
    assert out["e_chain"] == pytest.approx(0.0) and out["coverage"] == pytest.approx(1.0)
    assert "DIAGNOSTIC_ONLY" in out["labels"] and "STEP_INDEPENDENCE_ASSUMED" in out["labels"]
    assert out["n_rows"] == 10 and out["n_components"] == 10


def test_bad_chain_is_inconsistent_and_that_is_a_valid_outcome():
    out = _run(_rows(noise=0.3))
    assert out["verdict"] == "CHAIN_INCONSISTENT"


def test_missing_intervals_give_unknown_not_a_verdict():
    rows = [cp.CompositeRow(**{**r.__dict__, "interval": None}) for r in _rows()]
    out = _run(rows)
    assert out["verdict"] == "UNKNOWN" and out["coverage"] is None


def test_unchecked_source_is_refused_and_derived_source_excluded():
    rows = _rows() + [_comp(99, ("blanch", "boil"), 0.45, source="SYN-DB")]
    with pytest.raises(cp.CompositionRefused) as exc:
        _run(rows, circularity={"SYN-LIT": "CHECKED_NOT_DERIVED"})
    assert "CIRCULARITY_UNCHECKED" in _codes(exc)
    with pytest.raises(cp.CompositionRefused) as exc:
        _run(rows, circularity={"SYN-LIT": "CHECKED_NOT_DERIVED", "SYN-DB": "UNKNOWN"})
    assert "CIRCULARITY_UNCHECKED" in _codes(exc)
    out = _run(rows, circularity={"SYN-LIT": "CHECKED_NOT_DERIVED", "SYN-DB": "DERIVED_MULTIPLICATIVE"})
    assert out["n_rows"] == 10 and out["excluded_sources"] == ["SYN-DB"]


def test_invalid_rho_or_c_floor_refused():
    for over, code in (({"rho": -0.1}, "RHO_INVALID"), ({"c_floor": 1.5}, "C_FLOOR_INVALID"),
                       ({"rho": None}, "RHO_INVALID")):
        with pytest.raises(cp.CompositionRefused) as exc:
            _run(_rows(), **over)
        assert code in _codes(exc)


def test_fold_integrity_refuses_constituents_of_test_composites_in_train():
    composites = [_comp(1, ("blanch", "boil"), 0.45, component="LC-A")]
    singles = [cp.SingleStepRow("S1", "blanch", "LC-A"), cp.SingleStepRow("S2", "boil", "LC-B")]
    ok = {"C1": "test", "S1": "test", "S2": "train"}
    assert cp.check_fold_integrity(composites, singles, ok) == []
    bad = {"C1": "test", "S1": "train", "S2": "train"}
    blockers = cp.check_fold_integrity(composites, singles, bad)
    assert blockers and blockers[0].startswith("CONSTITUENT_IN_OTHER_FOLD")
    with pytest.raises(cp.CompositionRefused):
        cp.assert_fold_integrity(composites, singles, bad)


def test_empty_input_refused():
    with pytest.raises(cp.CompositionRefused) as exc:
        _run([])
    assert "NO_COMPOSITE_ROWS" in _codes(exc)
