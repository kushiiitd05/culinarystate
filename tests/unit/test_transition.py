import numpy as np
import pandas as pd

from culinarystate.transition.baselines import all_models, D3Hierarchical
from culinarystate.transition.evaluate import abs_errors, conformal, evaluate
from culinarystate.transition.splits import all_splits, grouped_split, leakage, study_disjoint


def toy(n_mat=12, seed=0):
    rng = np.random.default_rng(seed)
    rows = []
    procs = {"boil": 0.6, "bake": 0.85, "fry": 0.75, "steam": 0.9}
    for m in range(n_mat):
        mb = rng.normal(0, 0.05)
        for p, pv in procs.items():
            for t, tb in (("vitamin c", -0.1), ("calcium", 0.1)):
                y = float(np.clip(pv + mb + tb + rng.normal(0, 0.02), 0, 1.2))
                cens = y >= 0.975
                rows.append({"evd_id": f"E{len(rows)}", "matrix": f"food{m}", "matrix_form": "", "food_group": f"g{m % 3}",
                             "ingredient_id": None, "process": p, "process_family": p, "n_steps": 1, "target": t,
                             "basis": "X", "y": None if cens else y, "y_lower": 0.975 if cens else None,
                             "censored": cens, "group": f"study{m % 6}", "study": f"study{m % 6}",
                             "duration_known": False, "temperature_known": False, "medium": ""})
    return pd.DataFrame(rows)


def test_grouped_splits_have_no_leakage():
    df = toy()
    for cols, name in ((["matrix"], "matrix_disjoint"), (["process"], "process_disjoint")):
        s = grouped_split(df, cols, name)
        assert leakage(df, s, cols)[cols[0]] == 0.0
        assert len(set(s.train) & set(s.test)) == 0 and len(set(s.cal) & set(s.test)) == 0
    pair = grouped_split(df, ["matrix", "process"], "pair_holdout")
    tr = set(zip(df.iloc[pair.train].matrix, df.iloc[pair.train].process))
    te = set(zip(df.iloc[pair.test].matrix, df.iloc[pair.test].process))
    assert not tr & te


def test_study_disjoint_refuses_single_source():
    df = toy().assign(group="USDA", study=None)
    assert study_disjoint(df) is None
    splits, notes = all_splits(df)
    assert "study_disjoint" not in [s.name for s in splits] and "NOT POSSIBLE" in notes[0]


def test_study_disjoint_when_possible():
    s = study_disjoint(toy())
    assert s is not None and leakage(toy(), s, ["study"])["study"] == 0.0


def test_censor_aware_error():
    df = pd.DataFrame({"y": [0.5, None], "y_lower": [None, 0.975], "censored": [False, True]})
    e = abs_errors(df, np.array([0.6, 0.99]))
    assert np.allclose(e, [0.1, 0.0])
    assert np.allclose(abs_errors(df, np.array([0.5, 0.9])), [0.0, 0.075])


def test_conformal_empirical_coverage():
    df = pd.DataFrame({"y": np.linspace(0, 1, 50), "y_lower": None, "censored": False})
    c = conformal(np.full(30, 0.1), df, df["y"].to_numpy())
    assert c["coverage"] == 1.0 and c["width"] == 0.2


def test_baselines_run_and_beat_persistence_on_toy():
    df = toy()
    split = grouped_split(df, ["matrix"], "matrix_disjoint")
    res = {m.name: evaluate(df, split, m, n_boot=50)["mae_censor_aware"] for m in all_models()}
    assert res["D3_hierarchical_shrinkage"] < res["D0_persistence"]
    assert res["D2_process_mean"] < res["D1_global_mean"]


def test_d3_backoff_unseen_process():
    df = toy()
    m = D3Hierarchical().fit(df[df.process != "steam"])
    pred = m.predict(df[df.process == "steam"])
    assert np.isfinite(pred).all()
