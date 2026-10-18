"""Calibration / selective-prediction metrics for DEL-4 (SSOT §242.5, §201.15; plan AI8).

`conf` = predicted probability that the output is correct (or that answering is right); `correct` = 0/1 label from
independently verified data (§242.3: never labels produced by the model being calibrated).
"""
from __future__ import annotations

from collections.abc import Sequence

from sklearn.metrics import roc_auc_score


def brier(conf: Sequence[float], correct: Sequence[int]) -> float:
    return round(sum((p - y) ** 2 for p, y in zip(conf, correct)) / len(conf), 6)


def ece(conf: Sequence[float], correct: Sequence[int], n_bins: int = 10) -> dict:
    """Expected calibration error with equal-width bins; `bins` doubles as reliability-plot data."""
    bins: dict[int, list[tuple[float, int]]] = {}
    for p, y in zip(conf, correct):
        bins.setdefault(min(int(p * n_bins), n_bins - 1), []).append((p, y))
    rows, total = [], 0.0
    for b in sorted(bins):
        xs = bins[b]
        c, a = sum(p for p, _ in xs) / len(xs), sum(y for _, y in xs) / len(xs)
        total += len(xs) * abs(a - c)
        rows.append({"bin": b, "n": len(xs), "confidence": round(c, 4), "accuracy": round(a, 4)})
    return {"ece": round(total / len(conf), 6), "bins": rows}


def risk_coverage(conf: Sequence[float], correct: Sequence[int]) -> list[dict]:
    """Answer the k most confident items, k = 1..n; risk = error rate among answered (ties broken by input order)."""
    order = sorted(range(len(conf)), key=lambda i: -conf[i])
    out, errors = [], 0
    for k, i in enumerate(order, 1):
        errors += 1 - correct[i]
        out.append({"coverage": k / len(conf), "risk": errors / k, "threshold": conf[i]})
    return out


def aurc(conf: Sequence[float], correct: Sequence[int]) -> float:
    """Area under the risk–coverage curve (mean risk over coverage steps); lower is better."""
    rc = risk_coverage(conf, correct)
    return round(sum(p["risk"] for p in rc) / len(rc), 6)


def error_detection_auroc(conf: Sequence[float], correct: Sequence[int]) -> float | None:
    """How well confidence separates correct from wrong outputs; None when only one class is present."""
    if len(set(correct)) < 2:
        return None
    return round(float(roc_auc_score(correct, conf)), 6)


def unsupported_claim_rate(claims: Sequence[dict]) -> dict:
    """UCR over judged claims; `supported` is True / False / None (not yet judged — excluded, but counted)."""
    judged = [c for c in claims if c.get("supported") is not None]
    bad = sum(1 for c in judged if not c["supported"])
    return {"ucr": round(bad / len(judged), 6) if judged else None, "claims": len(claims), "judged": len(judged),
            "unjudged": len(claims) - len(judged)}
