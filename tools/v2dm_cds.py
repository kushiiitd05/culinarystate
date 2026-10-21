#!/usr/bin/env python3
"""V2-DM: simple stronger-router baselines (no decision model needed): R0 raw CRF confidence per stratum, R1 frozen v1 (calibrated+M6) per stratum, CD-S = gradient-boosted decision model over numeric NER/linker/gazetteer features trained on OOF TRAIN spans only.
Thresholds per stratum (label x seen/unseen, n >= 30 else never accept) from CALIBRATION at eps = 0.02; evaluated on DEV (development-level evidence; v1 TEST never read).
  python tools/v2dm_cds.py tasteset|recipedb3"""
import json
import sys
from pathlib import Path

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import e2_signal_calibration as M  # noqa: E402
import router_eval as RT  # noqa: E402
import v2dm_analyze as A  # noqa: E402
from culinarystate.ner import router as R  # noqa: E402

EPS = 0.02


def thresholds(score, y, keys):
    return {k: (R.risk_control_threshold(score[keys == k], y[keys == k], EPS) if (keys == k).sum() >= 30 else np.inf) for k in set(keys)}


def route_eval(score_cal, y_cal, k_cal, score_dev, y_dev, k_dev, lab_dev, unseen_dev, review_dev):
    t = thresholds(score_cal, y_cal, k_cal)
    td = np.array([t.get(k, np.inf) for k in k_dev])
    acc = score_dev >= td
    wrong = 1 - y_dev
    per = {l: {"n": int((lab_dev == l).sum()), "accept_rate": round(float(acc[lab_dev == l].mean()), 3), "accept_error": (round(float(wrong[(lab_dev == l) & acc].mean()), 4) if ((lab_dev == l) & acc).any() else None)} for l in sorted(set(lab_dev))}
    k = int(wrong[acc].sum())
    return {"coverage": round(float(acc.mean()), 4), "accept_error": round(k / max(int(acc.sum()), 1), 4), "cp95_upper": round(A.cp_upper(k, int(acc.sum())), 4), "error_capture_nonaccept": round(float(wrong[~acc].sum() / max(wrong.sum(), 1)), 4),
            "released_from_v1_REVIEW": int((acc & review_dev).sum()), "of_v1_REVIEW": int(review_dev.sum()), "released_error": round(float(wrong[acc & review_dev].mean()), 4) if (acc & review_dev).any() else None,
            "accept_error_unseen": (round(float(wrong[acc & unseen_dev].mean()), 4) if (acc & unseen_dev).any() else None), "n_accept_unseen": int((acc & unseen_dev).sum()), "per_label": per}


def main(ds):
    oof, dev, labels = M.collect(ds)
    cal = RT.calibration_rows(ds)
    ex = json.loads((ROOT / "reports/ner/_raw_v2/linker_export__bge-large-en-v1.5_v2x__seed1.json").read_text())["scores"]
    cats, _ = M.cat_map()
    K = M.ledger_maps()
    for rs in (oof, dev, cal):
        M.add_features(rs, ds, ex, cats, K)
    spec = {"nlab": len(labels), "cats": [], "fams": []}
    kind = "C+M1+M2+M5+M6"
    X = {nm: M.design(rs, kind, spec) for nm, rs in (("oof", oof), ("dev", dev), ("cal", cal))}
    y = {nm: np.array([r["y"] for r in rs]) for nm, rs in (("oof", oof), ("dev", dev), ("cal", cal))}
    js = {nm: [json.loads(l) for l in open(ROOT / "features/v2dm" / f"{ds}_spans.jsonl") if json.loads(l)["part"] == nm] for nm in ("dev", "cal")} if False else None
    rows = [json.loads(l) for l in open(ROOT / "features/v2dm" / f"{ds}_spans.jsonl")]
    J = {nm: [r for r in rows if r["part"] == nm] for nm in ("dev", "cal")}
    for nm in ("dev", "cal"):
        assert all(int(a["y"]) == int(b) for a, b in zip(J[nm], y[nm]))
    gbm = HistGradientBoostingClassifier(max_iter=250, learning_rate=0.05, max_leaf_nodes=15, l2_regularization=1.0, random_state=0).fit(X["oof"], y["oof"])
    s = {"R0_raw_conf": {nm: np.array([r["conf"] for r in J[nm]]) for nm in J}, "R1_frozen_v1_calibrated+M6": {nm: np.array([r["p_cal"] for r in J[nm]]) for nm in J},
         "CD-S_gbm": {"dev": gbm.predict_proba(X["dev"])[:, 1], "cal": gbm.predict_proba(X["cal"])[:, 1]}}
    key = lambda js_: np.array([f"{r['label']}|{'U' if r['unseen'] else 'S'}" for r in js_])
    lab_dev = np.array([r["label"] for r in J["dev"]])
    unseen_dev = np.array([r["unseen"] for r in J["dev"]])
    review_dev = np.array([r["route"] != "ACCEPT" for r in J["dev"]])
    out = {"dataset": ds, "n_dev": len(J["dev"]), "n_review_dev": int(review_dev.sum()), "arms": {}}
    for nm, sc in s.items():
        yd = y["dev"]
        p = np.clip(sc["dev"], 1e-3, 1 - 1e-3)
        out["arms"][nm] = {"auroc_all_dev": round(float(roc_auc_score(yd, sc["dev"])), 4), "aurc_all_dev": round(M.aurc(sc["dev"], yd), 5), "auroc_in_v1_REVIEW": round(float(roc_auc_score(yd[review_dev], sc["dev"][review_dev])), 4),
                           **route_eval(sc["cal"], y["cal"], key(J["cal"]), sc["dev"], yd, key(J["dev"]), lab_dev, unseen_dev, review_dev)}
    (ROOT / "reports/ner_v2" / f"_v2dm_{ds}_simple_routers.json").write_text(json.dumps(out, indent=1))
    print("==", ds, "dev spans", out["n_dev"], "v1 REVIEW", out["n_review_dev"])
    for nm, a in out["arms"].items():
        print(f"{nm:28s} cov {a['coverage']:.3f} acc_err {a['accept_error']:.4f} (cp95 {a['cp95_upper']:.4f}) capture {a['error_capture_nonaccept']:.3f} released-from-REVIEW {a['released_from_v1_REVIEW']}/{a['of_v1_REVIEW']} err {a['released_error']} unseenAcc {a['n_accept_unseen']}@{a['accept_error_unseen']} AUROC(REVIEW) {a['auroc_in_v1_REVIEW']} AURC {a['aurc_all_dev']}")
        print("     per label:", {l: (v['accept_rate'], v['accept_error']) for l, v in a["per_label"].items()})


if __name__ == "__main__":
    main(sys.argv[1])
