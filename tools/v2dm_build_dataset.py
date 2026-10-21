#!/usr/bin/env python3
"""V2-DM: leakage-safe span dataset for decision-model REVIEW adjudication (protocol reports/ner_v2/v2dm_protocol.md). NEVER reads TEST.
Rows for 5-fold OOF TRAIN spans (cross-fitted calibrated scores), DEV and CALIBRATION spans (final frozen calibrator + frozen R6 label x unseen thresholds from CALIBRATION).
  python tools/v2dm_build_dataset.py tasteset|recipedb3   ->  features/v2dm/<ds>_spans.jsonl  (git-ignored; contains recipe text, local/lab-server only)"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import e1_e2_calibration as E  # noqa: E402
import e2_signal_calibration as M  # noqa: E402
import router_eval as RT  # noqa: E402
from culinarystate.ner import router as R  # noqa: E402


def attach_text(ds, parts):
    """texts/offsets in the same order as M.rows(): OOF folds (held docs), then dev, then calibration."""
    sp, docs, _ = E.load(ds)
    tr_docs = docs(sp["train"])
    fold = np.random.RandomState(0).permutation(len(sp["train"])) % 5
    out = {"oof": [], "dev": [], "cal": []}
    for k in range(5):
        held = [i for i in range(len(sp["train"])) if fold[i] == k]
        pred = json.load(open(E.RAW / f"{ds}__deberta-base_crf_oof{k}__seed1.pred.json"))["oof"]
        out["oof"] += _rows([tr_docs[i] for i in held], pred, held, k)
    pa = json.load(open(E.RAW / f"{ds}__deberta-base_crf__seed1.pred.json"))
    out["dev"] = _rows(docs(sp["dev"]), pa["dev"], list(range(len(sp["dev"]))), -1)
    out["cal"] = _rows(docs(sp["calibration"]), pa["calibration"], list(range(len(sp["calibration"]))), -1)
    return out


def _rows(docs_part, preds, groups, fold):
    out = []
    for g, ((text, gold), pr) in zip(groups, zip(docs_part, preds)):
        gs = [tuple(x) for x in gold]
        gset = set(gs)
        for (s, e, lab, *_) in pr:
            if (s, e, lab) in gset:
                et = "correct"
            elif any(a == s and b == e for a, b, _ in gs):
                et = "type"
            elif any(max(s, a) < min(e, b) and c == lab for a, b, c in gs):
                et = "boundary"
            else:
                et = "spurious"
            out.append({"text": text, "s": s, "e": e, "span": text[s:e], "label": lab, "doc": g, "fold": fold, "err_type": et})
    return out


def main(ds):
    oof, dev, labels = M.collect(ds)
    cal = RT.calibration_rows(ds)
    for r in oof + dev + cal:
        r.setdefault("lf", {}), r.setdefault("pf", "NA")
    spec = {"nlab": len(labels), "cats": [], "fams": []}
    kind = "P0+M6"
    X = {nm: M.design(rs, kind, spec) for nm, rs in (("oof", oof), ("dev", dev), ("cal", cal))}
    y = {nm: np.array([r["y"] for r in rs]) for nm, rs in (("oof", oof), ("dev", dev), ("cal", cal))}
    fold = np.array([int(r["part"][3:]) for r in oof])
    p_oof = np.zeros(len(oof))
    for k in range(5):                                           # cross-fitted calibrated score for TRAIN spans
        tr, te = fold != k, fold == k
        sc = M.scaler(X["oof"][tr])
        m, iso, _ = R.fit_calibrator(sc(X["oof"][tr]), y["oof"][tr])
        p_oof[te] = R.calibrated(m, iso, sc(X["oof"][te]))
    sc = M.scaler(X["oof"])
    m, iso, _ = R.fit_calibrator(sc(X["oof"]), y["oof"])
    p = {"oof": p_oof, "dev": R.calibrated(m, iso, sc(X["dev"])), "cal": R.calibrated(m, iso, sc(X["cal"]))}
    key = lambda rs: np.array([f"{r['lab_s']}|{'U' if r['n'] == 0 else 'S'}" for r in rs])
    taus = R.stratified_thresholds(p["cal"], y["cal"], key(cal), RT.EPS)
    bar = RT.COSTS["c_review"] / RT.COSTS["c_lost"]
    txt = attach_text(ds, None)
    outdir = ROOT / "features" / "v2dm"
    outdir.mkdir(parents=True, exist_ok=True)
    n = 0
    with open(outdir / f"{ds}_spans.jsonl", "w") as f:
        for nm, rs in (("oof", oof), ("dev", dev), ("cal", cal)):
            assert len(rs) == len(txt[nm]), (nm, len(rs), len(txt[nm]))
            for i, (r, t) in enumerate(zip(rs, txt[nm])):
                assert r["lab_s"] == t["label"], (nm, i)
                tau = taus.get(key([r])[0], taus["__pooled__"])
                route = "REJECT" if p[nm][i] < bar else ("ACCEPT" if p[nm][i] >= tau else "REVIEW")
                f.write(json.dumps({"id": f"{ds}-{nm}-{i}", "ds": ds, "part": nm, "y": int(r["y"]), "conf": float(r["conf"]), "p_cal": float(p[nm][i]), "route": route, "unseen": bool(r["n"] == 0),
                                    "exact_gaz": float(r["exact"]), "fuzzy_gaz": float(r["fuzzy"]), **t}) + "\n")
                n += 1
    print(ds, n, "rows;", {nm: {rt: int(sum(1 for i in range(len(rs)) if True)) for rt in ()} for nm, rs in ()} or "ok")


if __name__ == "__main__":
    main(sys.argv[1])
