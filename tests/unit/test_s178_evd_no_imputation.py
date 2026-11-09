"""S178 EVD lane, T6-C09-R2: no zero / mean / half-minimum imputation reaches a transition dataset cell.

Pure tests against ``src/culinarystate/transition`` on synthetic EVD rows (no ledger is read). Property style: many seeded
random row sets (``hypothesis`` is not installed here), each checked against invariants of the cell table builder
(``dataset.cells_from_rows``), the training-target helper (``dataset.y_train``), the cross-source aggregation
(``cross_source.prepare`` / ``prepare_groups``) and the baselines.

What the tests pin (current behaviour, not a wish):
  * a row whose retention factor is UNKNOWN / ABSENT never becomes a cell; no value is filled;
  * a MEASURED value enters as exactly ``value * scale`` (scale 0.01 for "%"); never mean-, zero- or minimum-substituted;
  * a CENSORED row keeps ``y`` empty, ``y_lower`` = its stated limit * scale, ``censored`` True (documented bound, flagged);
  * ``y_train`` returns, per row, either ``y`` or ``y_lower``: the stated bound is the only substitution there is;
  * fitting any baseline never mutates the training frame; ``fillna`` appears only where it is a prediction-time backoff;
  * the cell table carries booleans for condition knowledge, never an imputed numeric temperature or duration.

Three tests are ``xfail(strict=True)`` and document latent gaps found while writing this file (the builder is NOT changed
here; a human decides): a censored row without a limit becomes y_lower = 0; a left-censored (LT_*) row is stored as a lower
bound; the builder does not filter by evidence tier (E5-E7 rows would pass). When the builder is fixed the xfail flips to an
unexpected pass and the marker must be removed.
"""
from __future__ import annotations

import ast
import random
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from culinarystate.transition import baselines as B
from culinarystate.transition import cross_source as CS
from culinarystate.transition import dataset as DS

TRANSITION = Path(DS.__file__).resolve().parent
FAMILY = "USDA-RETN-R6"
EXPECTED_COLUMNS = ["evd_id", "matrix", "matrix_form", "food_group", "ingredient_id", "process", "process_family", "n_steps", "target", "basis",
                    "y", "y_lower", "censored", "group", "study", "duration_known", "temperature_known", "medium"]
KNOWN = ("MEASURED", "RANGE")


def evd(i, rf, *, fam=FAMILY, status="ACTIVE", tier="E3", cond_id="COND-1", steps=("boil",), matrix="carrot", target="vitamin c", form=None, ing=None):
    e = {"id": f"EVD-{i:06d}", "status": status, "source_family_id": fam, "tier": tier,
         "matrix": {"raw_name": matrix.upper(), "food_group": "Vegetables", "form": form, "ingredient_id": ing},
         "process": {"steps": list(steps), "condition_id": cond_id, "modifiers": {}},
         "target": {"raw_name": target.title(), "basis": "TRUE_RETENTION", "state_variable_id": "SVAR-000009"},
         "derived": ({"retention_factor": rf} if rf is not None else {}), "independence_group": fam, "study_ids": []}
    return e


def measured(v, unit="%"):
    return {"status": "MEASURED", "value": v, "unit": unit}


def censored(limit, unit="%", kind="GT_CAP"):
    return {"status": "CENSORED", "unit": unit, "censor": {"kind": kind, "limit": limit}}


COND = {"COND-1": {"id": "COND-1", "completeness_mask": {"temperature": "MEASURED", "duration": "UNKNOWN", "ph": "UNKNOWN"}, "medium": "water"}}


def random_rows(seed, n=200):
    rng = random.Random(seed)
    rows, truth = [], {}
    steps_pool = [("boil",), ("bake",), ("fry",), ("steam",), ("boil", "drain")]
    for i in range(n):
        kind = rng.choice(["M", "M", "M", "C", "U", "A", "NONE", "X"])
        unit = rng.choice(["%", "fraction"])
        if kind == "M":
            v = round(rng.choice([0.0, rng.uniform(0.01, 1.4)]), 6) if unit == "fraction" else round(rng.choice([0.0, rng.uniform(1, 140)]), 3)
            rf = measured(v, unit)
        elif kind == "C":
            lim = 97.5 if unit == "%" else 0.975
            rf = censored(lim, unit)
        elif kind == "U":
            rf = {"status": "UNKNOWN", "unit": unit}
        elif kind == "A":
            rf = {"status": "ABSENT"}
        elif kind == "NONE":
            rf = None
        else:  # a row of another family or not ACTIVE; must never appear
            rf = measured(50.0)
        e = evd(i, rf, steps=rng.choice(steps_pool), matrix=rng.choice(["carrot", "pea", "beef", "milk"]), target=rng.choice(["vitamin c", "folate", "thiamin"]),
                fam=FAMILY if kind != "X" else "OTHER-FAM", status="ACTIVE" if kind != "X" or rng.random() < 0.5 else "DEPRECATED")
        rows.append(e)
        truth[e["id"]] = (kind, rf)
    return rows, truth


# ---------------------------------------------------------------------------------------------------------- builder properties
@pytest.mark.parametrize("seed", range(40))
def test_cells_contain_only_measured_or_censored_source_values(seed):
    rows, truth = random_rows(seed)
    df = DS.cells_from_rows(rows, COND, FAMILY).df
    in_scope = {i for i, (k, _) in truth.items() if k in ("M", "C")}
    assert set(df["evd_id"]) == in_scope                      # UNKNOWN / ABSENT / no-retention rows are dropped, not filled
    for _, r in df.iterrows():
        kind, rf = truth[r["evd_id"]]
        scale = 0.01 if rf["unit"] == "%" else 1.0
        if kind == "M":
            assert r["y"] == rf["value"] * scale               # bit-exact: no mean / zero / minimum substitution
            assert pd.isna(r["y_lower"]) and not r["censored"]
        else:
            assert pd.isna(r["y"]) and r["censored"]           # nothing is filled in for the censored value
            assert r["y_lower"] == rf["censor"]["limit"] * scale


@pytest.mark.parametrize("seed", range(20))
def test_y_train_is_the_value_or_the_stated_bound_for_every_row(seed):
    rows, truth = random_rows(seed)
    df = DS.cells_from_rows(rows, COND, FAMILY).df
    before = df.copy(deep=True)
    yt = DS.y_train(df)
    pd.testing.assert_frame_equal(df, before)                  # y_train does not mutate
    assert len(yt) == len(df) and not yt.isna().any()
    for (_, r), v in zip(df.iterrows(), yt):
        assert v == (r["y_lower"] if r["censored"] else r["y"])
    # the only substitution is censored -> its own bound; a measured 0.0 stays 0.0 and no unknown row was turned into 0
    unknown_ids = {i for i, (k, _) in truth.items() if k in ("U", "A", "NONE")}
    assert not unknown_ids & set(df["evd_id"])


def test_measured_zero_is_kept_and_unknown_is_not_turned_into_zero():
    rows = [evd(1, measured(0.0)), evd(2, {"status": "UNKNOWN", "unit": "%"}), evd(3, None), evd(4, measured(80.0))]
    df = DS.cells_from_rows(rows, COND, FAMILY).df
    assert sorted(df["evd_id"]) == ["EVD-000001", "EVD-000004"]
    assert df.loc[df.evd_id == "EVD-000001", "y"].iloc[0] == 0.0       # a real measured zero is data
    assert sorted(df["y"]) == [0.0, 0.8]                               # and the 0.4 mean of the two values appears nowhere


def test_unknown_status_with_a_numeric_value_still_gives_no_cell():
    """A stray number on a non-MEASURED status is not read as a value."""
    rows = [evd(1, {"status": "UNKNOWN", "value": 55.0, "unit": "%"}), evd(2, {"status": "ABSENT", "value": 12.0, "unit": "%"})]
    assert len(DS.cells_from_rows(rows, COND, FAMILY).df) == 0


def test_inactive_and_other_family_rows_are_excluded():
    rows = [evd(1, measured(50.0), status="DEPRECATED"), evd(2, measured(60.0), fam="OTHER"), evd(3, measured(70.0))]
    assert list(DS.cells_from_rows(rows, COND, FAMILY).df["evd_id"]) == ["EVD-000003"]


def test_missing_condition_record_gives_false_flags_and_empty_medium_not_defaults():
    rows = [evd(1, measured(50.0), cond_id="COND-MISSING"), evd(2, measured(60.0))]
    df = DS.cells_from_rows(rows, COND, FAMILY).df.set_index("evd_id")
    a, b = df.loc["EVD-000001"], df.loc["EVD-000002"]
    assert (a["duration_known"], a["temperature_known"], a["medium"]) == (False, False, "")
    assert (b["duration_known"], b["temperature_known"], b["medium"]) == (False, True, "water")


def test_cell_table_has_no_numeric_condition_column():
    df = DS.cells_from_rows([evd(1, measured(50.0))], COND, FAMILY).df
    assert list(df.columns) == EXPECTED_COLUMNS                         # a new numeric T / t / pH column must be added here on purpose
    assert df["duration_known"].dtype == bool and df["temperature_known"].dtype == bool


# ---------------------------------------------------------------------------------------------------------- baselines and aggregation
def _frame(seed=0, n=150):
    rows, _ = random_rows(seed, n)
    for k, e in enumerate(rows):
        e["matrix"]["raw_name"] = f"FOOD{k % 11}"
    return DS.cells_from_rows(rows, COND, FAMILY).df.reset_index(drop=True)


@pytest.mark.parametrize("model", [B.D0Persistence, B.D1GlobalMean, B.D2ProcessMean, B.D3Hierarchical, B.D4NearestEvidence, B.D7BiasedMF])
def test_fit_and_predict_do_not_mutate_the_frame_or_emit_nan(model):
    df = _frame()
    before = df.copy(deep=True)
    m = model().fit(df)
    pred = m.predict(df)
    pd.testing.assert_frame_equal(df, before)
    assert np.isfinite(np.asarray(pred, dtype=float)).all()


def test_d5_fit_does_not_mutate_the_frame():
    pytest.importorskip("sklearn")
    df = _frame()
    before = df.copy(deep=True)
    B.D5Boosting().fit(df).predict(df)
    pd.testing.assert_frame_equal(df, before)


def test_global_mean_baseline_is_the_mean_of_y_train_only():
    df = _frame()
    m = B.D1GlobalMean().fit(df)
    assert m.mu == float(DS.y_train(df).mean())                         # the mean is a model, fitted on stated values and bounds; it never fills a cell


def test_log_target_wrapper_floors_but_does_not_fill():
    df = _frame()
    d = df.copy()
    d["y"] = pd.to_numeric(d["y"], errors="coerce")
    seen = {}

    class Spy(B.Model):
        name = "spy"

        def fit(self, df):
            seen["y"], seen["y_lower"] = df["y"].copy(), df["y_lower"].copy()
            return self

        def predict(self, df):
            return np.zeros(len(df))
    B.LogTarget(Spy()).fit(d)
    y0 = d["y"]
    ok = y0 > B.EPS
    assert np.allclose(seen["y"][ok], np.log(y0[ok]))                   # values above the floor are exactly log(value)
    assert seen["y"][y0.isna()].isna().all()                            # missing stays missing (no zero / mean fill)


def test_cross_source_prepare_aggregates_real_values_and_drops_valueless_rows():
    df = pd.DataFrame({"evd_id": list("abcdef"), "target": ["vitamin c"] * 6, "ingredient_id": ["ING-1"] * 6, "process_family": ["boil"] * 6,
                       "y": [0.5, 0.7, None, None, 0.9, 0.3], "y_lower": [None, None, 0.975, None, None, None],
                       "censored": [False, False, True, False, False, False]})
    # row d: neither a value nor a bound -> must be dropped, not filled; row e is a measured 0.9; row f a measured 0.3
    out = CS.prepare(df)
    assert len(out) == 1 and int(out["n"].iloc[0]) == 5
    vals = [0.5, 0.7, 0.975, 0.9, 0.3]
    assert out["y"].iloc[0] == pytest.approx(sum(vals) / 5)
    assert min(vals) <= out["y"].iloc[0] <= max(vals)
    assert out["censored_share"].iloc[0] == pytest.approx(1 / 5)         # the bound-substituted share stays reported


def test_cross_source_prepare_groups_never_fabricates_a_cell():
    df = pd.DataFrame({"evd_id": list("abc"), "target": ["vitamin c"] * 3, "food_group": ["Vegetables"] * 3, "matrix_form": [""] * 3,
                       "process_family": ["boil"] * 3, "y": [None, None, None], "y_lower": [None, None, None], "censored": [False] * 3})
    assert len(CS.prepare_groups(df)) == 0


# ---------------------------------------------------------------------------------------------------------- static guard on the source
def _calls(path: Path, attr: str) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    hits: set[str] = set()

    def walk(node, scope):
        for ch in ast.iter_child_nodes(node):
            name = scope
            if isinstance(ch, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                name = f"{scope}.{ch.name}" if scope else ch.name
            if isinstance(ch, ast.Call) and isinstance(ch.func, ast.Attribute) and ch.func.attr == attr:
                hits.add(scope)
            walk(ch, name)
    walk(tree, "")
    return hits


def test_fillna_appears_only_as_prediction_or_feature_backoff():
    assert _calls(TRANSITION / "dataset.py", "fillna") == set()
    assert _calls(TRANSITION / "cross_source.py", "fillna") == set()
    assert _calls(TRANSITION / "splits.py", "fillna") == set()
    # prediction-time backoff to the fitted mean / an unseen-category code; not dataset cells
    assert _calls(TRANSITION / "baselines.py", "fillna") == {"D2ProcessMean.predict", "D5Boosting._X"}
    # frequency of an unseen category = 0 inside the propensity diagnostic (a count, not a measurement)
    assert _calls(TRANSITION / "evaluate.py", "fillna") == {"propensity_weights.feats"}


def test_no_imputer_or_interpolation_in_dataset_builders():
    for f in ("dataset.py", "cross_source.py", "splits.py"):
        src = (TRANSITION / f).read_text(encoding="utf-8")
        for bad in ("SimpleImputer", "IterativeImputer", "KNNImputer", ".interpolate(", ".ffill(", ".bfill(", "fillna", "np.nan_to_num", "min() / 2", "min()/2"):
            assert bad not in src, (f, bad)


# ---------------------------------------------------------------------------------------------------------- latent gaps (xfail, strict)
@pytest.mark.xfail(strict=True, reason="LATENT: dataset._rf reads censor.limit with default 0, so a CENSORED row whose censor object has no 'limit' key "
                                       "becomes y_lower = 0.0 (a zero imputation). Not reachable from the real ledger (all 5,894 censored rows carry a limit); reported, builder unchanged.")
def test_censored_row_without_a_limit_must_not_become_a_zero_lower_bound():
    rf = {"status": "CENSORED", "unit": "%", "censor": {"kind": "GT_CAP"}}
    df = DS.cells_from_rows([evd(1, rf)], COND, FAMILY).df
    assert len(df) == 0 or not (df["y_lower"] == 0.0).any()


@pytest.mark.xfail(strict=True, reason="LATENT: dataset._rf ignores censor.kind, so a left-censored (LT_LOD / LT_STATED) value is stored as y_lower = its limit "
                                       "(an upper bound read as a lower bound). The real ledger has only GT_CAP; reported, builder unchanged.")
def test_left_censored_row_must_not_be_stored_as_a_lower_bound():
    df = DS.cells_from_rows([evd(1, censored(5.0, kind="LT_LOD"))], COND, FAMILY).df
    assert len(df) == 0 or not df["y_lower"].notna().any()


@pytest.mark.xfail(strict=True, reason="GAP vs the T6-C09 firewall text: cells_from_rows filters by source family and ACTIVE status only, not by evidence tier, "
                                       "so an E5-E7 (simulated / assumed) row would enter a cell table. Reported, builder unchanged.")
def test_e5_to_e7_rows_must_not_enter_the_cell_table():
    rows = [evd(1, measured(50.0), tier="E3"), evd(2, measured(60.0), tier="E7")]
    df = DS.cells_from_rows(rows, COND, FAMILY).df
    assert list(df["evd_id"]) == ["EVD-000001"]
