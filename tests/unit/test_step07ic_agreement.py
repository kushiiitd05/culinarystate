import importlib.util
from pathlib import Path

import pytest

_spec = importlib.util.spec_from_file_location(
    "step07ic_agreement", Path(__file__).resolve().parents[2] / "tools" / "step07ic_agreement.py"
)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)


def test_perfect_agreement_kappa_one():
    a = [1, 0, 1, 0]
    assert m.cohen_kappa(a, a) == pytest.approx(1.0)
    assert m.gwet_ac1(a, a) == pytest.approx(1.0)


def test_constant_reviewer_gives_zero_kappa_but_high_raw_and_ac1():
    a = [1] * 9 + [0]
    b = [1] * 10
    assert m.cohen_kappa(a, b) == pytest.approx(0.0)
    assert m.binary_stats(a, b)["raw_agreement"] == pytest.approx(0.9)
    assert m.gwet_ac1(a, b) > 0.85  # AC1 is robust to the kappa paradox


def test_both_constant_equal_is_undefined():
    assert m.cohen_kappa([1, 1], [1, 1]) is None


def test_label_mappings():
    assert m.y_copy("SAME_RECIPE_MINOR_VARIANT") == 1
    assert m.y_copy("SAME_DISH_DIFFERENT_RECIPE") == 0
    assert m.y_dish("SAME_DISH_DIFFERENT_RECIPE") == 1
    assert m.y_dish("RELATED") == 0
    assert m.y_dish("RELATED", related_positive=True) == 1
    assert m.y_dish("DISTINCT", related_positive=True) == 0


def _packets():
    A = {f"P{i}": l for i, l in enumerate(["SAME_RECIPE_COPY", "DISTINCT", "RELATED", "UNCERTAIN", "SAME_DISH_DIFFERENT_RECIPE"])}
    B = {f"P{i}": l for i, l in enumerate(["SAME_RECIPE_COPY", "DISTINCT", "DISTINCT", "SAME_RECIPE_COPY", "RELATED"])}
    return A, B


def test_uncertain_pairs_are_excluded_and_counted():
    A, B = _packets()
    out = m.compare(A, B)
    assert out["Y_copy"]["pairs_excluded_uncertain_either"] == 1
    assert out["Y_copy"]["n"] == 4
    assert out["six_class_raw_agreement"] == pytest.approx(2 / 5)
    assert {d["pair_id"] for d in out["disagreeing_pair_ids"]} == {"P2", "P3", "P4"}


def test_rejects_labels_outside_the_six():
    A, B = _packets()
    B["P0"] = "CORRECT"
    with pytest.raises(ValueError):
        m.compare(A, B)


def test_rejects_different_pair_sets():
    A, B = _packets()
    del B["P4"]
    with pytest.raises(ValueError):
        m.compare(A, B)
