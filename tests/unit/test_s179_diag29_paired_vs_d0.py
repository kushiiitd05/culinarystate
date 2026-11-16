"""T6-C02-R3: every 29-diag rung vs D0, paired cluster bootstrap per split (DIAGNOSTIC / PRIOR_EXPOSURE_REANALYSIS)."""
from __future__ import annotations

from types import SimpleNamespace as NS

import numpy as np
import pandas as pd

from culinarystate.evaluation import diag29_paired_vs_d0 as P


def _df(n=40, groups=12):
    return pd.DataFrame({"evd_id": [f"E{i}" for i in range(n)], "group": [f"G{i % groups}" for i in range(n)],
                         "matrix": "m", "process": "p", "y": np.linspace(0, 1, n)})


class Const:
    def __init__(self, name, c):
        self.name, self.c = name, c

    def __call__(self):
        return self


def _loss_fn(model, df, split):
    te = df.iloc[split.test].reset_index(drop=True)
    return te, np.abs(te["y"].to_numpy() - model.c)


def test_each_non_d0_model_contrasted_on_each_usable_split():
    df = _df()
    splits = [NS(name="random", train=list(range(20)), test=list(range(20, 40))),
              NS(name="empty", train=[], test=list(range(5)))]
    models = [Const("D0_global", 0.0), Const("D1_x", 0.5), Const("B2_y", 0.9)]
    out = P.paired_vs_d0(df, splits=splits, models=models, losses=_loss_fn, n_resamples=200)
    assert set(out) == {"random", "empty"}
    assert out["empty"] == {"refused": ["EMPTY_FOLD: train or test is empty"]}
    assert set(out["random"]) == {"D1", "B2"}
    d1 = out["random"]["D1"]
    # test y in [0.51, 1]: D0 predicts 0 (loss ~0.76), D1 predicts 0.5 (loss ~0.26) -> estimate > 0 (D1 lower loss)
    assert d1["estimate"] > 0 and d1["lower95"] <= d1["estimate"] <= d1["upper95"]
    assert d1["n_clusters"] == 12 and d1["label"] == "DIAGNOSTIC;PRIOR_EXPOSURE_REANALYSIS"


def test_few_clusters_labelled_diagnostic_only():
    df = _df(groups=3)
    splits = [NS(name="random", train=list(range(20)), test=list(range(20, 40)))]
    out = P.paired_vs_d0(df, splits=splits, models=[Const("D0_g", 0.0), Const("D1_x", 0.5)],
                         losses=_loss_fn, n_resamples=100)
    assert out["random"]["D1"]["label"] == "DIAGNOSTIC_ONLY;PRIOR_EXPOSURE_REANALYSIS"


def test_deterministic():
    df = _df()
    splits = [NS(name="random", train=list(range(20)), test=list(range(20, 40)))]
    kw = dict(splits=splits, models=[Const("D0_g", 0.0), Const("D1_x", 0.5)], losses=_loss_fn, n_resamples=100)
    assert P.paired_vs_d0(df, **kw) == P.paired_vs_d0(df, **kw)


def test_sign_documented():
    assert "D0" in P.SIGN and "> 0" in P.SIGN
