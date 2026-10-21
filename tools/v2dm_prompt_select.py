#!/usr/bin/env python3
"""V2-DM stage S1a: choose the prompt wording (p1/p2/p3) on an OOF TRAIN sample only (DEV never touched). Criterion fixed in advance: AUROC of P(true) from q3_exact for 'span exactly correct';
ties/near-ties (< 0.01 AUROC) -> the shorter prompt (p1 < p2 < p3). Also reports the same-row AUROC of the v1 calibrated score and the raw CRF confidence, so the decision model is read against the baselines.
  python tools/v2dm_prompt_select.py tasteset dm_p1.jsonl dm_p2.jsonl dm_p3.jsonl"""
import json
import sys
from pathlib import Path

import numpy as np
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]


def ptrue(rec, q):
    a = (rec.get("resp") or {}).get("answers", {}).get(q)
    return None if a is None else a.get("noul")


def main(ds, files):
    spans = {}
    for l in open(ROOT / "features/v2dm" / f"{ds}_spans.jsonl"):
        r = json.loads(l)
        spans[r["id"]] = r
    res = {}
    for f in files:
        recs = [json.loads(l) for l in open(f)]
        ok = [r for r in recs if ptrue(r, "q3_exact") is not None and r["rep"] == 0]
        y = np.array([spans[r["id"]]["y"] for r in ok])
        p = np.array([ptrue(r, "q3_exact") for r in ok])
        pb = np.array([ptrue(r, "q1_boundary") for r in ok])
        pc = np.clip(p, 1e-3, 1 - 1e-3)
        base_cal = np.array([spans[r["id"]]["p_cal"] for r in ok])
        base_raw = np.array([spans[r["id"]]["conf"] for r in ok])
        res[recs[0]["prompt"]] = {"n_rows": len(recs), "n_ok": len(ok), "malformed": len(recs) - len(ok), "err_rate": round(float(1 - y.mean()), 4), "auroc_q3": round(float(roc_auc_score(y, p)), 4),
                                  "auroc_q1_boundary": round(float(roc_auc_score(y, pb)), 4), "nll_raw": round(float(-np.mean(np.where(y == 1, np.log(pc), np.log(1 - pc)))), 4),
                                  "auroc_v1_calibrated_same_rows": round(float(roc_auc_score(y, base_cal)), 4), "auroc_raw_crf_same_rows": round(float(roc_auc_score(y, base_raw)), 4),
                                  "median_ms": float(np.median([r["ms"] for r in recs]))}
    best = None
    for k in sorted(res):
        if best is None or res[k]["auroc_q3"] > res[best]["auroc_q3"] + 0.01:
            best = k
    out = {"dataset": ds, "rows": "OOF TRAIN REVIEW/REJECT random sample (seed 0)", "prompts": res, "selected_prompt": best, "rule": "highest q3 AUROC; margin < 0.01 -> shorter prompt"}
    (ROOT / "reports/ner_v2" / f"_v2dm_prompt_select_{ds}.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2:])
