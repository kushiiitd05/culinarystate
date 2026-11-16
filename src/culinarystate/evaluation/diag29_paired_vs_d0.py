"""T6-C02-R3: every 29-diag rung vs D0 on every usable split, per source family, paired cluster bootstrap.

Same splits (``diag29_splits``, seed 7), cluster rule (``_clusters``), bootstrap (``paired_cluster_bootstrap``, margin 0,
CLUSTER weighting, 95%), contrast seed and K_MIN as the D-082 D2-vs-B2 contrast; only the pair changes (baseline D0,
challenger each other rung). These splits were already read in RUN-S179-DIAG29-001, so every number is a
PRIOR_EXPOSURE_REANALYSIS, DIAGNOSTIC (or DIAGNOSTIC_ONLY under K_MIN), never a confirmatory result.
"""
from __future__ import annotations

from typing import Any, Callable, Iterable, Mapping, Optional, Sequence

from culinarystate.evaluation import diag29_additions as ADD
from culinarystate.evaluation.bakeoff import BakeoffRefused, paired_cluster_bootstrap
from culinarystate.transition.dataset import cells_from_rows

SIGN = "estimate = mean over clusters of (loss D0 - loss rung); > 0 means the rung has lower loss than D0"
REANALYSIS = "PRIOR_EXPOSURE_REANALYSIS"
LABELS = ["DIAGNOSTIC", REANALYSIS, "NON_CITABLE", "NO_HUMAN_SIGNOFF_D085"]


def _label(n_clusters: int) -> str:
    return ("DIAGNOSTIC_ONLY" if n_clusters < ADD.K_MIN else "DIAGNOSTIC") + ";" + REANALYSIS


def paired_vs_d0(df, *, splits: Optional[Sequence] = None, models: Optional[Sequence] = None,
                 losses: Optional[Callable] = None, seed: int = 7, n_resamples: int = 2000) -> dict:
    """{split: {rung: contrast}}; ``splits``/``models``/``losses`` are injectable for tests."""
    splits = list(splits) if splits is not None else ADD.diag29_splits(df, seed)[0]
    models = list(models) if models is not None else ADD.diag29_models()
    losses = losses or (lambda m, d, s: ADD._losses(type(m), d, s))
    base = next(m for m in models if ADD._key(m.name) == "D0")
    out: dict[str, Any] = {}
    for s in splits:
        if not ADD.usable(s):
            out[s.name] = {"refused": ["EMPTY_FOLD: train or test is empty"]}
            continue
        te, l0 = losses(base, df, s)
        cl, ckey = ADD._clusters(te)
        ids = te["evd_id"].astype(str).tolist()
        per: dict[str, Any] = {}
        for m in models:
            k = ADD._key(m.name)
            if k == "D0":
                continue
            _, lm = losses(m, df, s)
            try:
                pc = paired_cluster_bootstrap(dict(zip(ids, l0)), dict(zip(ids, lm)), dict(zip(ids, cl)), margin=0.0,
                                              n_resamples=n_resamples, confidence=0.95, seed=ADD.CONTRAST_SEED,
                                              weighting="CLUSTER")
            except BakeoffRefused as exc:
                per[k] = {"refused": exc.blockers, "n_rows": int(len(te)), "cluster_key": ckey}
                continue
            per[k] = {"n_rows": pc.n_rows, "n_clusters": pc.n_clusters, "cluster_key": ckey,
                      "estimate": ADD._r(pc.estimate), "lower95": ADD._r(pc.lower), "upper95": ADD._r(pc.upper),
                      "label": _label(pc.n_clusters)}
        out[s.name] = per
    return out


def run(ctx: Any, evd_rows: Sequence[Mapping], *, cond: Mapping, families: Iterable[str], seed: int = 7,
        n_resamples: int = 2000) -> dict:
    active = [r for r in evd_rows if r.get("status") == "ACTIVE"]
    kept = ctx.filter_dev_rows(active, id_column="id", group_columns=("id",))
    out = {"labels": LABELS, "sign": SIGN, "seed": seed, "contrast_seed": ADD.CONTRAST_SEED, "k_min": ADD.K_MIN,
           "rows_before_seal": len(active), "rows_after_seal": len(kept), "families": {}}
    for fam in families:
        df = cells_from_rows(kept, dict(cond), fam).df
        if len(df):
            out["families"][fam] = {"rows": int(len(df)), "splits": paired_vs_d0(df, seed=seed, n_resamples=n_resamples)}
    return out
