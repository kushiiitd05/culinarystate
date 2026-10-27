import importlib.util
import inspect
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("step07ic_op", ROOT / "tools" / "step07ic_operating_points.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)


def P(i, score, y, stratum="S", w=1.0, ydish=None):
    return {"pair_id": f"P{i}", "a": f"A{i}", "b": f"B{i}", "score": score, "stratum": stratum, "pool": w,
            "w": w, "y_copy": y, "y_dish": y if ydish is None else ydish, "y_dish_sens": y if ydish is None else ydish}


def synthetic():
    # 40 clean positives at high scores, negatives below; one stray negative at 0.95 would break LB
    pos = [P(i, 0.90 + i * 0.001, 1) for i in range(40)]
    neg = [P(100 + i, 0.30 + i * 0.01, 0) for i in range(40)]
    return pos + neg


def test_merge_max_recall_subject_to_wilson_lb():
    s = m.select_op_merge(synthetic())
    assert s["recall"] == pytest.approx(1.0)
    assert s["precision_ci95"][0] >= 0.90
    assert s["cut"] == pytest.approx(0.90)  # lowest cut that still has full recall and clean precision


def test_merge_infeasible_returns_none():
    pairs = [P(i, 0.5 + i * 0.01, i % 2) for i in range(20)]
    assert m.select_op_merge(pairs) is None


def test_merge_tie_goes_to_higher_cut():
    pairs = synthetic() + [P(500, 0.20, 0)]
    # cuts 0.20..0.30 all give recall 1 but fail LB; among feasible equal-recall cuts the higher wins
    s = m.select_op_merge(pairs)
    assert s["cut"] == pytest.approx(0.90)
    lo = m.stats_at(pairs, 0.90, "y_copy")
    hi = m.stats_at(pairs, 0.91, "y_copy")
    assert hi["recall"] < lo["recall"]


def test_split_highest_cut_meeting_recall_target():
    pairs = [P(i, 0.1 * (i + 1), 1) for i in range(10)]  # scores .1..1.0 all positive
    s = m.select_op_split(pairs, recall_target=0.9)
    assert s["cut"] == pytest.approx(0.2)  # 9/10 positives at >=0.2
    assert m.select_op_split(pairs, recall_target=1.0)["cut"] == pytest.approx(0.1)


def test_split_tie_prefers_higher_cut():
    pairs = [P(0, 0.2, 0), P(1, 0.4, 1), P(2, 0.6, 1)]
    assert m.select_op_split(pairs, recall_target=1.0)["cut"] == pytest.approx(0.4)


def test_uncertain_excluded_and_never_imputed():
    labels = [{"pair_id": "1", "a_recipe_id": "a", "b_recipe_id": "b", "label": "UNCERTAIN"},
              {"pair_id": "2", "a_recipe_id": "c", "b_recipe_id": "d", "label": "SAME_RECIPE_COPY"},
              {"pair_id": "3", "a_recipe_id": "e", "b_recipe_id": "f", "label": "RELATED"}]
    key = [{"pair_id": str(i), "score": "0.9", "stratum": "S1", "stratum_pool_size": "100"} for i in (1, 2, 3)]
    pairs = m.build_pairs(labels, key)
    assert [p["pair_id"] for p in pairs] == ["2", "3"]
    assert pairs[0]["w"] == 50.0
    assert (pairs[1]["y_copy"], pairs[1]["y_dish"], pairs[1]["y_dish_sens"]) == (0, 0, 1)
    assert m.targets("UNCERTAIN") is None


def test_stratum_weighting_changes_estimate():
    pairs = [P(0, 0.9, 1, "A", 1.0), P(1, 0.9, 0, "B", 99.0)]
    assert m.stats_at(pairs, 0.9, "y_copy")["precision"] == pytest.approx(0.01)


def test_selection_ignores_group_size_and_corpus_info():
    for fn in (m.select_op_merge, m.select_op_split, m.stats_at, m.grouped_folds):
        src = inspect.getsource(fn).lower()
        assert "group_size" not in src and "giant" not in src and "corpus" not in src
    base = synthetic()
    extra = [{**p, "group_size": 10**6, "corpus_n": 612782} for p in base]
    assert m.select_op_merge(base)["cut"] == m.select_op_merge(extra)["cut"]


def test_determinism_and_grouped_folds_keep_components_together():
    pairs = synthetic()
    pairs.append({**P(900, 0.5, 0), "a": "A0", "b": "B1"})  # links pair 0 and pair 1
    f = m.grouped_folds(pairs)
    assert f == m.grouped_folds(list(pairs))
    assert f[0] == f[1] == f[-1]
    assert m.select_op_merge(pairs) == m.select_op_merge(list(pairs))
    assert m.nested_cv(pairs, m.select_op_merge, "y_copy") == m.nested_cv(pairs, m.select_op_merge, "y_copy")


def test_wilson_known_value():
    lo, hi = m.wilson(0.5, 100)
    assert lo == pytest.approx(0.4038, abs=1e-3) and hi == pytest.approx(0.5962, abs=1e-3)


def test_split_components_union_find():
    ids = ["r1", "r2", "r3", "r4", "r5"]
    comp = m.split_components(ids, ["g1", "g1", "g2", "g3", "g4"], ["r3"], ["r4"])
    assert comp[0] == comp[1] and comp[2] == comp[3]
    assert len({comp[0], comp[2], comp[4]}) == 3


@pytest.mark.skipif(not (ROOT / m.KEY).exists(), reason="local sealed key absent")
def test_sealed_key_and_recipe_identity_unchanged():
    import json
    rep = ROOT / m.OUT_DIR / "op_selection_report_v1.json"
    if not rep.exists():
        pytest.skip("report not generated")
    r = json.loads(rep.read_text())
    assert r["sealed_key_unchanged"] is True
    assert m.sha256_file(ROOT / m.KEY) == r["input_sha256"][m.KEY]
    for rel, h in r["input_sha256"].items():
        if rel.startswith("ledgers/recipe_identity/"):
            assert m.sha256_file(ROOT / rel) == h, rel
