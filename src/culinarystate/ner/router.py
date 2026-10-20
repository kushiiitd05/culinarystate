"""S119 calibrator + conformal-style risk-control router + statistics (Aprilab items 4-5; master prompt P3, P10, P11). Laptop-side, sklearn/numpy.
Two scores: p_ent (is it an entity) and p_link (is the concept right). Outcomes: ACCEPT / REVIEW / NOVEL(NIL) / REJECT.
Thresholds are set on the CALIBRATION split only, per stratum, so the ACCEPT-set error is <= eps (with a finite-sample correction)."""
from __future__ import annotations

import random
from typing import Dict, List, Sequence, Tuple

import numpy as np
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold

ACCEPT, REVIEW, NOVEL, REJECT = "ACCEPT", "REVIEW", "NOVEL", "REJECT"


def fit_calibrator(X: np.ndarray, y: np.ndarray, k: int = 5, seed: int = 0, C: float = 1.0):
    """Cross-fitted logistic regression + isotonic on out-of-fold scores. Returns (model, isotonic, oof_probs).
    Fit ONLY on train-split features that were themselves built out-of-fold; never on CALIBRATION/dev/test."""
    oof = np.zeros(len(y))
    for tr, va in StratifiedKFold(k, shuffle=True, random_state=seed).split(X, y):
        oof[va] = LogisticRegression(C=C, max_iter=1000).fit(X[tr], y[tr]).predict_proba(X[va])[:, 1]
    iso = IsotonicRegression(out_of_bounds="clip", y_min=0.0, y_max=1.0).fit(oof, y)
    return LogisticRegression(C=C, max_iter=1000).fit(X, y), iso, oof


def calibrated(model, iso, X: np.ndarray) -> np.ndarray:
    return iso.predict(model.predict_proba(X)[:, 1])


def risk_control_threshold(score: np.ndarray, correct: np.ndarray, eps: float) -> float:
    """Smallest tau such that {score >= tau} has (errors + 1) / (n_accept + 1) <= eps on the calibration set (conservative finite-sample bound).
    Returns +inf if no threshold qualifies (nothing is accepted)."""
    order = np.argsort(-score)
    s, c = score[order], correct[order].astype(float)
    err = np.cumsum(1.0 - c)
    n = np.arange(1, len(s) + 1)
    ok = np.where((err + 1) / (n + 1) <= eps)[0]
    return float(s[ok.max()]) if len(ok) else float("inf")


def stratified_thresholds(score, correct, strata: Sequence[str], eps: float, min_n: int = 30) -> Dict[str, float]:
    """One tau per stratum (entity type / line length); strata with < min_n calibration items borrow the pooled tau."""
    strata = np.asarray(strata)
    pooled = risk_control_threshold(score, correct, eps)
    return {s: (risk_control_threshold(score[strata == s], correct[strata == s], eps) if (strata == s).sum() >= min_n else pooled)
            for s in sorted(set(strata))} | {"__pooled__": pooled}


def route(p_ent: float, p_link: float, tau_e: float, tau_l: float, review_bar: float, has_candidate_above_nil: bool) -> str:
    if p_ent < review_bar:
        return REJECT
    if p_ent >= tau_e:
        if p_link >= tau_l:
            return ACCEPT
        return REVIEW if has_candidate_above_nil else NOVEL
    return REVIEW


def accept_error(routes: Sequence[str], correct: Sequence[int]) -> dict:
    acc = [i for i, r in enumerate(routes) if r == ACCEPT]
    err = sum(1 - correct[i] for i in acc)
    return {"n_accept": len(acc), "accept_error": err / len(acc) if acc else None, "review_rate": sum(r == REVIEW for r in routes) / max(len(routes), 1),
            "novel_rate": sum(r == NOVEL for r in routes) / max(len(routes), 1), "coverage": len(acc) / max(len(routes), 1)}


# ------------------------------------------------------------------ statistics (P10)
def paired_grouped_bootstrap(a: Sequence[float], b: Sequence[float], groups: Sequence, n_boot: int = 1000, seed: int = 20261018) -> dict:
    """Per-group metric values a (candidate) and b (baseline); resamples whole groups. Returns mean delta, 95% CI, and a two-sided p."""
    g = sorted(set(groups), key=str)
    idx = {k: [i for i, x in enumerate(groups) if x == k] for k in g}
    d = np.array(a, float) - np.array(b, float)
    rng = random.Random(seed)
    stats = []
    for _ in range(n_boot):
        samp = [i for _ in g for i in idx[g[rng.randrange(len(g))]]]
        stats.append(d[samp].mean())
    stats = np.sort(stats)
    p = 2 * min((stats <= 0).mean(), (stats >= 0).mean())
    return {"delta": float(d.mean()), "low": float(stats[int(0.025 * n_boot)]), "high": float(stats[min(n_boot - 1, int(0.975 * n_boot))]), "p": float(max(p, 1.0 / n_boot))}


def holm(pvals: Sequence[float], alpha: float = 0.05) -> List[bool]:
    """Holm step-down: True where the hypothesis is rejected (i.e. the gain counts) at family-wise alpha."""
    order = np.argsort(pvals)
    out = [False] * len(pvals)
    for rank, i in enumerate(order):
        if pvals[i] <= alpha / (len(pvals) - rank):
            out[i] = True
        else:
            break
    return out


def promote(delta: dict, holm_ok: bool, min_effect: float = 0.003) -> bool:
    return bool(holm_ok and delta["delta"] >= min_effect and delta["low"] > 0)
