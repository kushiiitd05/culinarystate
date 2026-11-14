"""S179 (D-082, 29-diag amendment C2-C5): B2 ingredient mean, S-5 food-group split, D2-vs-B2 contrast, cap
sensitivity and the imputation-duplicate control. Synthetic rows only; no EVD row is read."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from culinarystate.evaluation import diag29_additions as A
from culinarystate.transition import baselines as B
from culinarystate.transition.dataset import COLUMNS
from culinarystate.transition.splits import all_splits


def _df(n_groups: int = 12, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    for i in range(120):
        fg = f"FG{i % 4}"
        m = f"m{i % 20}"
        p = f"p{i % 6}"
        cens = i % 17 == 0
        y = float(np.clip(0.4 + 0.1 * (i % 4) + 0.05 * (i % 6) + rng.normal(0, 0.05), 0, 1.2))
        rows.append({"evd_id": f"E{i}", "matrix": m, "food_group": fg, "process": p, "target": f"t{i % 3}",
                     "y": None if cens else y, "y_lower": 0.975 if cens else None, "censored": cens,
                     "group": f"IG{i % n_groups}", "study": f"S{i % n_groups}", "basis": "b"})
    df = pd.DataFrame(rows)
    for c in COLUMNS:          # the other dataset columns D4 / D5 read, neutral values
        if c not in df:
            df[c] = 1 if c == "n_steps" else (False if c.endswith("_known") else "")
    return df


# ------------------------------------------------------------------ B2

def test_b2_is_matrix_mean_shrunk_to_food_group_then_global():
    df = pd.DataFrame({"matrix": ["a", "a", "b", "c"], "food_group": ["F", "F", "F", "G"], "y": [0.2, 0.4, 0.9, 0.5],
                       "y_lower": [None] * 4, "censored": [False] * 4})
    m = B.B2IngredientMean().fit(df)
    mu = 0.5
    fF = (0.2 + 0.4 + 0.9 + 5 * mu) / (3 + 5)
    a = (0.2 + 0.4 + 5 * fF) / (2 + 5)
    test = pd.DataFrame({"matrix": ["a", "zz", "zz"], "food_group": ["F", "F", "unknown_group"]})
    pa, unseen_m, unseen_both = m.predict(test)
    assert pa == pytest.approx(a) and unseen_m == pytest.approx(fF) and unseen_both == pytest.approx(mu)


def test_b2_empty_food_group_falls_back_to_global_and_is_not_in_del2_models():
    df = pd.DataFrame({"matrix": ["a", "b"], "food_group": ["", ""], "y": [0.2, 0.8], "y_lower": [None, None],
                       "censored": [False, False]})
    m = B.B2IngredientMean().fit(df)
    assert m.predict(pd.DataFrame({"matrix": ["zz"], "food_group": [""]}))[0] == pytest.approx(0.5)
    assert all(not isinstance(x, B.B2IngredientMean) for x in B.all_models())
    assert any(isinstance(x, B.B2IngredientMean) for x in A.diag29_models())
    assert {type(x) for x in B.all_models()} <= {type(x) for x in A.diag29_models()}


# ------------------------------------------------------------------ S-5

def test_food_group_split_is_disjoint_and_del2_splits_unchanged():
    df = _df()
    base, _ = all_splits(df, 7)
    splits, _ = A.diag29_splits(df, 7)
    fg = next(s for s in splits if s.name == "food_group_disjoint")
    assert not (set(df.iloc[fg.train]["food_group"]) & set(df.iloc[fg.test]["food_group"]))
    assert [s.name for s in splits if s.name != "food_group_disjoint"] == [s.name for s in base]


# ------------------------------------------------------------------ cap sensitivity

def test_cap_sensitivity_changes_only_censored_bounds_and_is_deterministic():
    df = _df()
    out = A.cap_sensitivity(df, 7, caps=(0.95, 0.975, 1.0))
    assert set(out) == {"0.95", "0.975", "1.0"}
    assert out == A.cap_sensitivity(df, 7, caps=(0.95, 0.975, 1.0))
    assert out["0.95"] != out["1.0"]
    assert A.with_cap(df, 0.95)["y_lower"][df["censored"]].eq(0.95).all()
    assert A.with_cap(df, 0.95)["y"].equals(df["y"])


# ------------------------------------------------------------------ duplicates

def test_duplicate_groups_need_same_process_target_value_on_two_matrices():
    df = pd.DataFrame({"evd_id": list("abcde"), "matrix": ["m1", "m2", "m3", "m3", "m4"],
                       "process": ["p", "p", "p", "q", "p"], "target": ["t"] * 5,
                       "y": [0.5, 0.5, 0.5, 0.5, 0.7], "y_lower": [None] * 5, "censored": [False] * 5})
    g = A.duplicate_groups(df)
    assert g["n_groups"] == 1 and g["rows_in_groups"] == 3
    assert len(set(g["labels"][:3])) == 1 and g["labels"][3] != g["labels"][0]


def test_duplicate_control_keeps_each_group_in_one_fold():
    df = _df()
    df.loc[[0, 6, 12], ["process", "target", "y", "censored"]] = ["p0", "t0", 0.55, False]
    labels = A.duplicate_groups(df)["labels"]
    for s in A.duplicate_aware_splits(df, 7):
        fold = np.full(len(df), "", dtype=object)
        fold[s.train], fold[s.cal], fold[s.test] = "tr", "ca", "te"
        for lab in set(labels):
            assert len(set(fold[np.asarray(labels) == lab])) == 1


# ------------------------------------------------------------------ contrast

def test_contrast_reports_sign_convention_clusters_and_diagnostic_flag():
    df = _df(n_groups=12)
    out = A.contrast_d2_vs_b2(df, 7, n_resamples=200)
    assert out["sign"] == "estimate = mean over clusters of (loss D2 - loss B2); > 0 means B2 lower loss"
    for name, row in out["splits"].items():
        assert name in {"matrix_disjoint", "process_disjoint", "study_disjoint"}
        if "refused" in row:
            continue
        assert row["n_rows"] > 0 and row["n_clusters"] >= 2
        assert row["label"] == ("DIAGNOSTIC_ONLY" if row["n_clusters"] < 10 else "DIAGNOSTIC")
        assert row["cluster_key"] in {"independence_group", "ONE_LINEAGE_CLUSTER"}


def test_contrast_one_lineage_falls_back_to_matrix_process_clusters():
    df = _df(n_groups=1)
    out = A.contrast_d2_vs_b2(df, 7, n_resamples=50)
    ok = [r for r in out["splits"].values() if "refused" not in r]
    assert ok and all(r["cluster_key"] == "ONE_LINEAGE_CLUSTER" for r in ok)


# ------------------------------------------------------------------ runner wiring

def test_runner_reports_b2_food_group_split_and_the_three_new_diagnostics():
    from culinarystate.evaluation import diag29_runner as R
    from tests.unit.test_s173_diag29_runner import PassCtx, evd_rows

    out = R.run(PassCtx(), evd_rows(), cond={}, families=["SYN"], n_resamples=100)
    fam = out["families"]["SYN"]
    assert "food_group_disjoint" in fam["splits"]
    assert all("B2" in block for block in fam["splits"].values())
    for k in ("contrast_d2_vs_b2", "cap_sensitivity", "duplicate_control"):
        assert k in fam, k
    assert set(fam["cap_sensitivity"]) == {"0.95", "0.975", "1.0"}
    assert fam["duplicate_control"]["n_groups"] >= 0


def test_degenerate_splits_are_noted_not_fitted():
    df = _df()
    df["food_group"] = "ONLY"                       # one food group: S-5 is not possible
    df["matrix"] = "m0"                             # one matrix: duplicate-safe S-3 cannot split
    splits, notes = A.diag29_splits(df, 7)
    assert "food_group_disjoint" not in [s.name for s in splits]
    assert any(n.startswith("food_group_disjoint: NOT POSSIBLE") for n in notes)
    out = A.duplicate_control(df, 7, n_resamples=50)
    assert all(v.get("duplicate_groups_in_one_fold") == "NOT_POSSIBLE" or isinstance(v, dict) for v in out["mae"].values())
