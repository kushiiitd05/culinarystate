#!/usr/bin/env python3
"""S119 E1 / E2 (laptop): span-confidence calibration and the cross-fitted metadata calibrator.

  /opt/anaconda3/bin/python tools/e1_e2_calibration.py tasteset      # reads reports/ner/_raw_conf/*, writes reports/ner/_e1e2_<ds>.json
Inputs (pulled from the A100): <ds>__<model>[_crf]__seed1.{pred,conf}.json for dev/calibration/test and <..>_oof{k}__seed1.* for the 5 out-of-fold TRAIN tables.
Span table: one row per PREDICTED span {conf, correct (exact match to gold), label, length, train-only gazetteer features}. Gazetteer for OOF rows = built without that
fold; for calibration/dev/test = full train. Calibrator fit on OOF rows only; temperature fit on OOF only; CALIBRATION/dev never fit anything here; results are reported on DEV (TEST stays untouched until the configuration is frozen).
A0 raw confidence | E1 temperature-scaled | A2 +gazetteer | A5 +frequency only | A7 all promoted combos. Metrics: ECE, Brier, AURC, precision@coverage 80/90/95."""
import glob
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))
from culinarystate.ner import benchmark as B  # noqa: E402
from culinarystate.ner import router as R  # noqa: E402
from culinarystate.ner import spans as S  # noqa: E402
from culinarystate.scoring.calibration import aurc, brier, ece  # noqa: E402
import freeze_ner_benchmark as F  # noqa: E402
import pandas as pd  # noqa: E402
from scipy.optimize import minimize_scalar  # noqa: E402

RAW = ROOT / "reports" / "ner" / "_raw_conf"


def logit(p):
    p = np.clip(np.asarray(p, float), 1e-4, 1 - 1e-4)
    return np.log(p / (1 - p))


def load(ds):
    sp = json.loads((ROOT / "benchmark/ner/splits" / f"{ds}_split_v1.json").read_text())["indices"]
    if ds == "tasteset":
        df = pd.read_csv(F.TASTE)
        docs = lambda idx: F.docs_taste(df, idx)
        labels = sorted(B.VIEWS["tasteset_native"])
    else:
        df, _ = F.load_rdb3()
        docs = lambda idx: F.docs_rdb3(df, idx)
        labels = sorted(B.VIEWS["recipedb3_published"])
    return sp, docs, labels


def table(docs_part, preds, confs, gaz_for_doc, labels, groups):
    rows = []
    for k, ((text, gold), pr, cf) in enumerate(zip(docs_part, preds, confs)):
        g = {tuple(x) for x in gold}
        gz = gaz_for_doc(k)
        for (s, e, lab, *_), c in zip(pr, cf):
            surf = text[s:e]
            f = gz.features(surf)
            rows.append({"conf": c, "y": int((s, e, lab) in g), "lab": labels.index(lab), "len": len(surf.split()), "gaz": f, "group": groups[k]})
    return rows


def X_of(rows, kind, T=1.0):
    base = [logit(r["conf"]) / T for r in rows]
    cols = [np.array(base)]
    if kind in ("A2", "A7"):
        cols += list(np.stack([r["gaz"] for r in rows]).T)
    if kind == "A5":
        cols += [np.array([r["gaz"][1::4][r["lab"]] for r in rows])]                    # log_count of the predicted label's slot
    if kind in ("A2", "A5", "A7"):
        cols += [np.array([r["len"] for r in rows], float)]
    if kind == "A7":
        cols += list(np.eye(len(rows[0]["gaz"]) // 4 + 1)[[r["lab"] for r in rows]].T)
    return np.stack(cols, axis=1)


def prec_at_cov(score, y, cov):
    k = max(1, int(round(cov * len(score))))
    idx = np.argsort(-score)[:k]
    return float(np.mean(y[idx]))


def metrics(p, y):
    p = np.clip(p, 0, 1)
    return {"ece": ece(p.tolist(), y.tolist())["ece"], "brier": brier(p.tolist(), y.tolist()), "aurc": round(aurc(p.tolist(), y.tolist()), 5),
            **{f"prec@{int(c * 100)}": round(prec_at_cov(p, y, c), 4) for c in (0.8, 0.9, 0.95)}, "n": int(len(y)), "acc": round(float(y.mean()), 4)}


def main():
    ds = sys.argv[1]
    stem = sys.argv[2] if len(sys.argv) > 2 else "deberta-base_crf"
    sp, docs, labels = load(ds)
    tr_idx = sp["train"]
    tr_docs = docs(tr_idx)
    fold = np.random.RandomState(0).permutation(len(tr_idx)) % 5
    rows_oof = []
    for k in range(5):
        pred = json.load(open(RAW / f"{ds}__{stem}_oof{k}__seed1.pred.json"))["oof"]
        conf = json.load(open(RAW / f"{ds}__{stem}_oof{k}__seed1.conf.json"))["oof"]
        held = [i for i in range(len(tr_idx)) if fold[i] == k]
        gz = S.Gazetteer.build((tr_docs[i] for i in range(len(tr_idx)) if fold[i] != k), labels)
        rows_oof += table([tr_docs[i] for i in held], pred, conf, lambda _k, gz=gz: gz, labels, held)
    full = S.Gazetteer.build(tr_docs, labels)
    parts = {}
    pred_all = json.load(open(RAW / f"{ds}__{stem}__seed1.pred.json"))
    conf_all = json.load(open(RAW / f"{ds}__{stem}__seed1.conf.json"))
    for p in ("calibration", "dev"):
        parts[p] = table(docs(sp[p]), pred_all[p], conf_all[p], lambda _k: full, labels, list(range(len(sp[p]))))
    yo = np.array([r["y"] for r in rows_oof])
    T = minimize_scalar(lambda t: -np.mean(np.log(np.clip(np.where(yo == 1, 1 / (1 + np.exp(-logit([r["conf"] for r in rows_oof]) / t)),
                                                                1 - 1 / (1 + np.exp(-logit([r["conf"] for r in rows_oof]) / t))), 1e-9, 1))), bounds=(0.2, 10), method="bounded").x
    out = {"stem": stem, "temperature_fit_on_oof": round(float(T), 4), "n_oof_spans": len(rows_oof), "results": {}}
    yt = np.array([r["y"] for r in parts["dev"]])
    sig = lambda z: 1 / (1 + np.exp(-z))
    res = {"A0_raw": metrics(np.array([r["conf"] for r in parts["dev"]]), yt),
           "E1_temperature": metrics(sig(logit([r["conf"] for r in parts["dev"]]) / T), yt)}
    for kind in ("A2", "A5", "A7"):
        model, iso, _ = R.fit_calibrator(X_of(rows_oof, kind), yo)
        res[f"E2_{kind}"] = metrics(R.calibrated(model, iso, X_of(parts["dev"], kind)), yt)
    out["results"]["dev"] = res
    # calibration-split view (what the router thresholds will be set on): same models, reported for completeness
    model, iso, _ = R.fit_calibrator(X_of(rows_oof, "A7"), yo)
    ycal = np.array([r["y"] for r in parts["calibration"]])
    out["results"]["calibration_E2_A7"] = metrics(R.calibrated(model, iso, X_of(parts["calibration"], "A7")), ycal)
    (ROOT / "reports" / "ner" / f"_e1e2_{ds}.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
