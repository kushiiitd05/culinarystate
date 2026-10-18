"""DEL-2 evaluation: censoring-aware errors, grouped bootstrap CIs, split-conformal empirical coverage,
density / MNAR propensity diagnostics (plan AM4: diagnostics, not truth; weighted beside unweighted)."""
from __future__ import annotations

import numpy as np
import pandas as pd

from culinarystate.scoring.metrics import grouped_bootstrap

from .baselines import Model
from .splits import Split


def abs_errors(df: pd.DataFrame, pred: np.ndarray) -> np.ndarray:
    """|y - pred| for observed rows; for censored rows (y ≥ y_lower) error = max(0, y_lower - pred)."""
    obs = ~df["censored"].to_numpy()
    err = np.empty(len(df))
    err[obs] = np.abs(pd.to_numeric(df["y"], errors="coerce").to_numpy(dtype=float)[obs] - pred[obs])
    err[~obs] = np.maximum(0.0, pd.to_numeric(df["y_lower"], errors="coerce").to_numpy(dtype=float)[~obs] - pred[~obs])
    return err


def conformal(cal_err: np.ndarray, test_df: pd.DataFrame, test_pred: np.ndarray, alpha: float = 0.1) -> dict:
    """Split conformal on absolute residuals. Coverage is EMPIRICAL (AH4); no validity claim under shift."""
    obs_cal = cal_err
    if len(obs_cal) == 0:
        return {"q": None, "coverage": None, "width": None}
    n = len(obs_cal)
    q = float(np.quantile(obs_cal, min(1.0, np.ceil((n + 1) * (1 - alpha)) / n), method="higher"))
    lo, hi = test_pred - q, test_pred + q
    obs = ~test_df["censored"].to_numpy()
    y = pd.to_numeric(test_df["y"], errors="coerce").to_numpy(dtype=float)
    ylow = pd.to_numeric(test_df["y_lower"], errors="coerce").to_numpy(dtype=float)
    covered = np.where(obs, (y >= lo) & (y <= hi), hi >= ylow)
    return {"nominal": 1 - alpha, "q": round(q, 4), "coverage": round(float(covered.mean()), 4),
            "width": round(2 * q, 4)}


def propensity_weights(full: pd.DataFrame, test: pd.DataFrame) -> tuple[np.ndarray, dict]:
    """P(cell observed) from marginal frequencies of matrix, process and target over the full grid
    (logistic regression). Returns inverse-propensity weights for test rows + diagnostics."""
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import roc_auc_score
    mats, procs, tgts = full["matrix"].unique(), full["process"].unique(), full["target"].unique()
    observed = set(zip(full["matrix"], full["process"], full["target"]))
    fm, fp, ft = full["matrix"].value_counts(), full["process"].value_counts(), full["target"].value_counts()
    grid = pd.MultiIndex.from_product([mats, procs, tgts], names=["matrix", "process", "target"]).to_frame(index=False)
    if len(grid) > 400_000:
        grid = grid.sample(400_000, random_state=7)
        grid = pd.concat([grid, full[["matrix", "process", "target"]]]).drop_duplicates()

    def feats(d):
        return np.column_stack([np.log1p(d["matrix"].map(fm).fillna(0)), np.log1p(d["process"].map(fp).fillna(0)),
                                np.log1p(d["target"].map(ft).fillna(0))])
    yobs = np.array([k in observed for k in zip(grid["matrix"], grid["process"], grid["target"])])
    if yobs.all() or not yobs.any():
        return np.ones(len(test)), {"grid_cells": int(len(grid)), "observed_cells": int(yobs.sum()),
                                    "density": round(float(yobs.mean()), 5), "note": "degenerate (fully observed)"}
    lr = LogisticRegression(max_iter=1000).fit(feats(grid), yobs)
    p_grid = lr.predict_proba(feats(grid))[:, 1]
    p_test = np.clip(lr.predict_proba(feats(test))[:, 1], 1e-3, 1)
    diag = {"grid_cells": int(len(grid)), "observed_cells": int(yobs.sum()),
            "density": round(float(yobs.mean()), 5), "propensity_auc": round(float(roc_auc_score(yobs, p_grid)), 4),
            "features": ["log matrix freq", "log process freq", "log target freq"],
            "test_propensity_min": round(float(p_test.min()), 5), "test_propensity_median": round(float(np.median(p_test)), 4)}
    w = 1 / p_test
    return w / w.mean(), diag


def evaluate(df: pd.DataFrame, split: Split, model: Model, n_boot: int = 300) -> dict:
    tr, ca, te = (df.iloc[i].reset_index(drop=True) for i in (split.train, split.cal, split.test))
    model.fit(tr)
    pt, pc = model.predict(te), model.predict(ca)
    err_t, err_c = abs_errors(te, pt), abs_errors(ca, pc)
    obs = ~te["censored"].to_numpy()
    groups: dict = {}
    key = split.groups_col.split("+")[0] if split.groups_col and split.groups_col in te.columns else "matrix"
    for g, e in zip(te[key].astype(str), err_t):
        groups.setdefault(g, []).append(e)
    ci = grouped_bootstrap(groups, lambda xs: float(np.mean(xs)), n_boot=n_boot)
    w, _ = propensity_weights(df, te)
    return {
        "model": model.name, "split": split.name, "n_train": len(tr), "n_cal": len(ca), "n_test": len(te),
        "mae_censor_aware": round(float(err_t.mean()), 4), "mae_ci": ci,
        "mae_observed_only": round(float(err_t[obs].mean()), 4) if obs.any() else None,
        "rmse_observed_only": round(float(np.sqrt((err_t[obs] ** 2).mean())), 4) if obs.any() else None,
        "mae_ipw": round(float(np.average(err_t, weights=w)), 4),
        "conformal_90": conformal(err_c, te, pt, 0.1),
    }
