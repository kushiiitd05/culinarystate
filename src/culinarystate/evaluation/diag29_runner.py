"""29-diag runner (reports/step29/29diag_preregistration_DRAFT.md §3-§5). DIAGNOSTIC, never a claim.

run(ctx, evd_rows, cond, families): seal filter first (ctx.filter_dev_rows, singleton components: the 15a.R seal
unit is CELL, D-068, so the seal's own cell mapping decides exclusion; grouping by independence_group would burn whole
sources such as USDA), then per source family the DEL-2 splits and ladder with errors split at the cap
(censored GT_CAP rows) vs below it, a variant trained without cap rows, a shortcut rerun of D5 with basis removed,
and the D7-vs-D1 prediction difference. Deterministic.
"""
from __future__ import annotations

from typing import Any, Mapping, Sequence

import numpy as np

from culinarystate.transition.baselines import all_models
from culinarystate.transition.dataset import cells_from_rows
from culinarystate.transition.evaluate import abs_errors
from culinarystate.transition.splits import all_splits

LABELS = ("DIAGNOSTIC", "BOOTSTRAP_UNVERIFIED", "NON_CITABLE", "PRIOR_EXPOSURE_REANALYSIS")


def _key(name: str) -> str:
    return name.split("_")[0]


def _r(x) -> float | None:
    return None if x is None or (isinstance(x, float) and np.isnan(x)) else round(float(x), 4)


def _fit_pred(model, train, test):
    model.fit(train.reset_index(drop=True))
    return model.predict(test.reset_index(drop=True))


def _split_block(df, s) -> dict:
    tr, te = df.iloc[s.train].reset_index(drop=True), df.iloc[s.test].reset_index(drop=True)
    cap = te["censored"].to_numpy()
    out = {}
    for m in all_models():
        err = abs_errors(te, _fit_pred(m, tr, te))
        tr_nc = tr[~tr["censored"]]
        err_nc = abs_errors(te, _fit_pred(type(m)(), tr_nc, te)) if len(tr_nc) else np.array([np.nan])
        out[_key(m.name)] = {"mae_all": _r(err.mean()), "mae_below_cap": _r(err[~cap].mean()) if (~cap).any() else None,
                             "mae_at_cap": _r(err[cap].mean()) if cap.any() else None,
                             "mae_cap_rows_dropped_in_training": _r(np.nanmean(err_nc)),
                             "n_test": int(len(te)), "n_test_at_cap": int(cap.sum())}
    return out


def _family(df, seed: int) -> dict:
    splits, notes = all_splits(df, seed)
    res = {"rows": int(len(df)), "censored": int(df["censored"].sum()), "notes": notes,
           "splits": {s.name: _split_block(df, s) for s in splits}}
    models = {_key(m.name): m for m in all_models()}
    s0 = splits[0]
    tr, te = df.iloc[s0.train], df.iloc[s0.test]
    if "D5" in models:
        nb = df.assign(basis="")
        e_full = abs_errors(te.reset_index(drop=True), _fit_pred(type(models["D5"])(), tr, te))
        e_nb = abs_errors(nb.iloc[s0.test].reset_index(drop=True),
                          _fit_pred(type(models["D5"])(), nb.iloc[s0.train], nb.iloc[s0.test]))
        res["shortcut_basis_removed"] = {"split": s0.name, "d5_mae": _r(e_full.mean()), "d5_mae_no_basis": _r(e_nb.mean())}
    if "D7" in models and "D1" in models:
        p7 = _fit_pred(type(models["D7"])(), tr, te)
        p1 = _fit_pred(type(models["D1"])(), tr, te)
        res["d7_vs_d1_max_abs_pred_diff"] = _r(np.max(np.abs(np.asarray(p7) - np.asarray(p1))))
    return res


def run(ctx: Any, evd_rows: Sequence[Mapping], *, cond: Mapping, families: Sequence[str], seed: int = 7,
        n_boot: int = 300) -> dict:
    active = [r for r in evd_rows if r.get("status") == "ACTIVE"]
    kept = ctx.filter_dev_rows(active, id_column="id", group_columns=("id",))
    out = {"labels": list(LABELS), "rows_before_seal": len(active), "rows_after_seal": len(kept), "seed": seed,
           "families": {}}
    for fam in families:
        df = cells_from_rows(kept, dict(cond), fam).df
        if len(df):
            out["families"][fam] = _family(df, seed)
    return out
