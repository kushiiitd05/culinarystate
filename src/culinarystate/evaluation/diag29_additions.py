"""29-diag additions fixed before signature (S179, D-082; `reports/step29/29diag_preregistration_DRAFT.md` §3-§4).

- ``diag29_models``: the DEL-2 ladder plus B2 (TB-V0 B-2 ingredient mean); DEL-2's ``all_models`` is unchanged.
- ``diag29_splits``: the DEL-2 splits plus S-5 food-group-disjoint, inserted before S-6 study-disjoint.
- ``contrast_d2_vs_b2`` (§4 item 3): paired loss difference D2 minus B2 on S-3, S-4, S-6 test rows, paired cluster
  bootstrap (margin 0.0, confidence 0.95, CLUSTER weighting, seed ``29diag-contrast-2026-11-10``).
- ``cap_sensitivity`` (§4 item 4): censored GT_CAP rows refitted and rescored with the bound at 0.95 / 0.975 / 1.0.
- ``duplicate_control`` (§4 item 5): imputation-duplicate groups and S-2 / S-3 rerun with each group in one fold.

Everything is DIAGNOSTIC, NON_CITABLE and deterministic; nothing here reads a ledger.
"""
from __future__ import annotations

from typing import Any, Iterable, Sequence

import numpy as np
import pandas as pd

from culinarystate.evaluation.bakeoff import BakeoffRefused, paired_cluster_bootstrap
from culinarystate.transition.baselines import (
    B2IngredientMean, D2ProcessMean, D3Hierarchical, D5Boosting, Model, all_models,
)
from culinarystate.transition.evaluate import abs_errors
from culinarystate.transition.splits import Split, _assign_groups, all_splits, food_group_disjoint

CONTRAST_SEED = "29diag-contrast-2026-11-10"
CONTRAST_SPLITS = ("matrix_disjoint", "process_disjoint", "study_disjoint")
K_MIN = 10            # PROPOSED in the prereg: fewer clusters -> DIAGNOSTIC_ONLY, no direction is read
CAPS = (0.95, 0.975, 1.0)
SIGN = "estimate = mean over clusters of (loss D2 - loss B2); > 0 means B2 lower loss"


def _key(name: str) -> str:
    return name.split("_")[0]


def _r(x) -> float | None:
    return None if x is None or (isinstance(x, float) and np.isnan(x)) else round(float(x), 4)


def diag29_models() -> list[Model]:
    return [*all_models(), B2IngredientMean()]


def usable(s: Split) -> bool:
    return len(s.train) > 0 and len(s.test) > 0


def diag29_splits(df: pd.DataFrame, seed: int = 7) -> tuple[list[Split], list[str]]:
    base, notes = all_splits(df, seed)
    notes = list(notes)
    at = next((i for i, s in enumerate(base) if s.name == "study_disjoint"), len(base))
    fg = food_group_disjoint(df, seed)
    if df["food_group"].astype(str).nunique() < 3 or not usable(fg):
        notes.append("food_group_disjoint: NOT POSSIBLE (fewer than 3 food groups or an empty fold) — not reported")
        return base, notes
    return [*base[:at], fg, *base[at:]], notes


def _fit_pred(model: Model, train: pd.DataFrame, test: pd.DataFrame) -> np.ndarray:
    model.fit(train.reset_index(drop=True))
    return model.predict(test.reset_index(drop=True))


def _losses(model_cls, df: pd.DataFrame, s: Split) -> tuple[pd.DataFrame, np.ndarray]:
    tr, te = df.iloc[s.train].reset_index(drop=True), df.iloc[s.test].reset_index(drop=True)
    return te, abs_errors(te, _fit_pred(model_cls(), tr, te))


# ------------------------------------------------------------------ item 3: contrast

def _clusters(te: pd.DataFrame) -> tuple[list[str], str]:
    if te["group"].astype(str).nunique() >= 2:
        return te["group"].astype(str).tolist(), "independence_group"
    return (te["matrix"].astype(str) + "|" + te["process"].astype(str)).tolist(), "ONE_LINEAGE_CLUSTER"


def contrast_on(df: pd.DataFrame, splits: Iterable[Split], *, n_resamples: int = 2000) -> dict:
    out: dict[str, Any] = {}
    for s in splits:
        if not usable(s):
            out[s.name] = {"refused": ["EMPTY_FOLD: train or test is empty"]}
            continue
        te, l_d2 = _losses(D2ProcessMean, df, s)
        _, l_b2 = _losses(B2IngredientMean, df, s)
        cl, ckey = _clusters(te)
        ids = te["evd_id"].astype(str).tolist()
        try:
            pc = paired_cluster_bootstrap(dict(zip(ids, l_d2)), dict(zip(ids, l_b2)), dict(zip(ids, cl)),
                                          margin=0.0, n_resamples=n_resamples, confidence=0.95, seed=CONTRAST_SEED,
                                          weighting="CLUSTER")
        except BakeoffRefused as exc:
            out[s.name] = {"refused": exc.blockers, "n_rows": int(len(te)),
                           "cluster_key": ckey}
            continue
        out[s.name] = {"n_rows": pc.n_rows, "n_clusters": pc.n_clusters, "cluster_key": ckey,
                       "estimate": _r(pc.estimate), "lower95": _r(pc.lower), "upper95": _r(pc.upper),
                       "label": "DIAGNOSTIC_ONLY" if pc.n_clusters < K_MIN else "DIAGNOSTIC"}
    return out


def contrast_d2_vs_b2(df: pd.DataFrame, seed: int = 7, *, n_resamples: int = 2000) -> dict:
    splits, _ = diag29_splits(df, seed)
    chosen = [s for s in splits if s.name in CONTRAST_SPLITS]
    return {"sign": SIGN, "seed": CONTRAST_SEED, "k_min": K_MIN,
            "note": "lopsided by construction: S-3 favours D2, S-4 favours B2; only S-6 compares them on equal terms",
            "splits": contrast_on(df, chosen, n_resamples=n_resamples)}


# ------------------------------------------------------------------ item 4: cap sensitivity

def with_cap(df: pd.DataFrame, cap: float) -> pd.DataFrame:
    """A copy with every censored row's lower bound set to ``cap`` (fit and scoring both read ``y_lower``)."""
    out = df.copy()
    out.loc[out["censored"].astype(bool), "y_lower"] = float(cap)
    return out


def cap_sensitivity(df: pd.DataFrame, seed: int = 7, *, caps: Sequence[float] = CAPS) -> dict:
    splits, _ = diag29_splits(df, seed)
    res: dict[str, Any] = {}
    for c in caps:
        d = with_cap(df, c)
        per: dict[str, Any] = {}
        for s in (x for x in splits if usable(x)):
            te_cap = d.iloc[s.test]["censored"].to_numpy(dtype=bool)
            row = {}
            for m in diag29_models():
                _, err = _losses(type(m), d, s)
                row[_key(m.name)] = {"mae_all": _r(err.mean()),
                                     "mae_below_cap": _r(err[~te_cap].mean()) if (~te_cap).any() else None,
                                     "mae_at_cap": _r(err[te_cap].mean()) if te_cap.any() else None}
            per[s.name] = row
        res[str(c)] = per
    return res


# ------------------------------------------------------------------ item 5: imputation duplicates

def _value_key(df: pd.DataFrame) -> pd.Series:
    obs = df["y"].where(~df["censored"].astype(bool))
    return np.where(df["censored"].astype(bool), "GE:" + df["y_lower"].astype(str),
                    "EQ:" + pd.to_numeric(obs, errors="coerce").round(6).astype(str))


def duplicate_groups(df: pd.DataFrame) -> dict:
    """Groups of >= 2 rows (one source family per call) with the same process, target and retention value at the
    reported precision, on >= 2 distinct matrices. ``labels``: group id per row (singleton id when not duplicated)."""
    key = df["process"].astype(str) + "||" + df["target"].astype(str) + "||" + pd.Series(_value_key(df), index=df.index)
    n_mat = df.groupby(key)["matrix"].transform("nunique")
    size = key.map(key.value_counts())
    dup = (size >= 2) & (n_mat >= 2)
    labels = [f"DUP:{k}" if d else f"ROW:{i}" for i, (k, d) in enumerate(zip(key, dup))]
    return {"n_groups": int(key[dup].nunique()), "rows_in_groups": int(dup.sum()),
            "share_of_rows": _r(dup.mean()) if len(df) else None, "labels": labels}


def _components(a: Sequence[str], b: Sequence[str]) -> pd.Series:
    parent: dict[str, str] = {}

    def find(x):
        while parent.setdefault(x, x) != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for x, y in zip(a, b):
        ra, rb = find(f"k:{x}"), find(f"d:{y}")
        if ra != rb:
            parent[ra] = rb
    return pd.Series([find(f"k:{x}") for x in a])


def duplicate_aware_splits(df: pd.DataFrame, seed: int = 7, cal: float = 0.15, test: float = 0.2) -> list[Split]:
    labels = duplicate_groups(df)["labels"]
    out = []
    for name, cols in (("pair_holdout", ["matrix", "process"]), ("matrix_disjoint", ["matrix"])):
        keys = df[cols].astype(str).agg("||".join, axis=1).tolist()
        comp = _components(keys, labels)
        tr, ca, te = _assign_groups(comp, (cal, test), seed)
        out.append(Split(f"{name}_dupsafe", tr, ca, te, "+".join(cols) + "+duplicate_group",
                         f"{comp.nunique()} components"))
    return out


def duplicate_control(df: pd.DataFrame, seed: int = 7, *, n_resamples: int = 2000) -> dict:
    g = duplicate_groups(df)
    base = {s.name: s for s in all_splits(df, seed)[0]}
    names = (("D2", D2ProcessMean), ("D3", D3Hierarchical), ("B2", B2IngredientMean), ("D5", D5Boosting))
    rows: dict[str, Any] = {}
    for s in duplicate_aware_splits(df, seed):
        plain = base[s.name.replace("_dupsafe", "")]
        rows[plain.name] = {way: ({k: _r(_losses(cls, df, sp)[1].mean()) for k, cls in names} if usable(sp)
                                  else "NOT_POSSIBLE")
                            for way, sp in (("as_split", plain), ("duplicate_groups_in_one_fold", s))}
    safe_s3 = [s for s in duplicate_aware_splits(df, seed) if s.name == "matrix_disjoint_dupsafe" and usable(s)]
    return {"n_groups": g["n_groups"], "rows_in_groups": g["rows_in_groups"], "share_of_rows": g["share_of_rows"],
            "mae": rows, "contrast_matrix_disjoint_dupsafe": contrast_on(df, safe_s3, n_resamples=n_resamples)}
