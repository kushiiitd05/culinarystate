#!/usr/bin/env python3
"""V2-DM analysis (laptop). D0/D1 baselines always; decision-model arms when result files exist. DEV-level evidence only (v1 TEST never read).
  python tools/v2dm_analyze.py tasteset|recipedb3 [--dm results.jsonl ...]"""
import json
import sys
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import e2_signal_calibration as M  # noqa: E402
from culinarystate.ner import router as R  # noqa: E402

EPS = 0.02


def load(ds):
    return [json.loads(l) for l in open(ROOT / "features/v2dm" / f"{ds}_spans.jsonl")]


def cp_upper(k, n, a=0.05):
    from scipy.stats import beta
    return 1.0 if k >= n else float(beta.ppf(1 - a, k + 1, n - k)) if n else 1.0


def score_report(rows, s, name):
    y = np.array([r["y"] for r in rows])
    if len(set(y)) < 2:
        return {"name": name, "n": len(y)}
    p = np.clip(s, 1e-3, 1 - 1e-3)
    return {"name": name, "n": int(len(y)), "err_rate": round(float(1 - y.mean()), 4), "auroc": round(float(roc_auc_score(y, s)), 4), "aurc": round(M.aurc(np.asarray(s), y), 5),
            "nll": round(float(-np.mean(np.where(y == 1, np.log(p), np.log(1 - p)))), 4), "brier": round(float(np.mean((p - y) ** 2)), 4)}


def stratum(r):
    return f"{r['label']}|{'U' if r['unseen'] else 'S'}"


def promote(cal_rows, s_cal, dev_rows, s_dev):
    """label x seen/unseen thresholds on CALIBRATION REVIEW rows at eps (finite-sample rule; strata with < 30 calibration rows never promote: no pooling across labels); newly accepted on DEV."""
    ycal = np.array([r["y"] for r in cal_rows])
    sc, kc = np.asarray(s_cal), np.array([stratum(r) for r in cal_rows])
    taus = {k: (R.risk_control_threshold(sc[kc == k], ycal[kc == k], EPS) if (kc == k).sum() >= 30 else np.inf) for k in set(kc)}
    yd = np.array([r["y"] for r in dev_rows])
    td = np.array([taus.get(stratum(r), np.inf) for r in dev_rows])
    acc = np.asarray(s_dev) >= td
    k = int((1 - yd[acc]).sum())
    per = {}
    for st in sorted(set(stratum(r) for r in dev_rows)):
        m = np.array([stratum(r) == st for r in dev_rows]) & acc
        if m.any():
            per[st] = {"n": int(m.sum()), "error": round(float((1 - yd[m]).mean()), 4)}
    return {"taus": {k_: (None if np.isinf(v) else round(float(v), 4)) for k_, v in taus.items()}, "newly_accepted": int(acc.sum()), "of_review": int(len(yd)), "reduction": round(float(acc.mean()), 4),
            "damage_wrong_accepted": k, "newly_accepted_error": round(k / max(int(acc.sum()), 1), 4), "cp95_upper": round(cp_upper(k, int(acc.sum())), 4), "correct_newly_accepted": int(yd[acc].sum()), "per_stratum": per}


def main(ds, dm_files):
    rows = load(ds)
    sel = lambda part: [r for r in rows if r["part"] == part and r["route"] in ("REVIEW", "REJECT")]
    dev, cal = sel("dev"), sel("cal")
    out = {"dataset": ds, "n_review_dev": len(dev), "n_review_cal": len(cal), "arms": {}}
    out["arms"]["D0_frozen_R6 (no promotion)"] = {"newly_accepted": 0, "note": "REVIEW stays REVIEW"}
    out["arms"]["D1_calibrated_conf_in_REVIEW"] = {**score_report(dev, [r["p_cal"] for r in dev], "D1 p_cal"), "promotion": promote(cal, [r["p_cal"] for r in cal], dev, [r["p_cal"] for r in dev])}
    out["arms"]["D1b_raw_crf_conf_in_REVIEW"] = {**score_report(dev, [r["conf"] for r in dev], "D1b raw conf"), "promotion": promote(cal, [r["conf"] for r in cal], dev, [r["conf"] for r in dev])}
    for f in dm_files:                                                    # decision-model arms (parser filled in after the smoke test fixes the response schema)
        raise SystemExit("decision-model result parsing is enabled after the smoke test records the response schema")
    (ROOT / "reports/ner_v2" / f"_v2dm_{ds}_baselines.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[3:] if len(sys.argv) > 2 and sys.argv[2] == "--dm" else [])
