#!/usr/bin/env python3
"""S127: where does M6 (train-gazetteer agreement) help? Analysis only (P0 = Platt+isotonic on span conf, +M6 = same plus exact/fuzzy). DEV, per stratum, paired doc bootstrap."""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import e1_e2_calibration as E  # noqa: E402
import e2_signal_calibration as M  # noqa: E402
from culinarystate.ner import router as R  # noqa: E402


def err_types(ds, dev_rows):
    sp, docs, _ = E.load(ds)
    pred = json.load(open(E.RAW / f"{ds}__deberta-base_crf__seed1.pred.json"))["dev"]
    out = []
    for (text, gold), pr in zip(docs(sp["dev"]), pred):
        g = [tuple(x) for x in gold]
        for (s, e, lab, *_) in pr:
            if (s, e, lab) in set(g):
                out.append("correct")
            elif any(gs == s and ge == e for gs, ge, _ in g):
                out.append("type")
            elif any(max(s, gs) < min(e, ge) and gl == lab for gs, ge, gl in g):
                out.append("boundary")
            else:
                out.append("spurious")
    assert len(out) == len(dev_rows)
    return np.array(out)


def run(ds, nb=300):
    oof, dev, labels = M.collect(ds)
    spec = {"nlab": len(labels), "cats": [], "fams": []}
    yo, yd = np.array([r["y"] for r in oof]), np.array([r["y"] for r in dev])
    gd = np.array([r["group"] for r in dev])
    P, S = {}, {}
    for k in ("P0", "P0+M6"):
        Xo, Xd = M.design(oof, k, spec), M.design(dev, k, spec)
        sc = M.scaler(Xo)
        m, iso, _ = R.fit_calibrator(sc(Xo), yo)
        P[k], S[k] = R.calibrated(m, iso, sc(Xd)), m.predict_proba(sc(Xd))[:, 1]
    n = np.array([r["n"] for r in dev])
    et = err_types(ds, dev)
    lab = np.array([r["lab_s"] for r in dev])
    strata = {"all": np.ones(len(dev), bool), "seen (n>=1)": n >= 1, "unseen (n=0)": n == 0, "tail (n=1-2)": (n >= 1) & (n <= 2), "head (n>=5)": n >= 5,
              "gazetteer exact match": np.array([r["exact"] > 0 for r in dev]), "no exact match": np.array([r["exact"] == 0 for r in dev]),
              "no exact, fuzzy>=0.6": np.array([r["exact"] == 0 and r["fuzzy"] >= 0.6 for r in dev]), "no exact, fuzzy<0.6": np.array([r["exact"] == 0 and r["fuzzy"] < 0.6 for r in dev])}
    for l in sorted(set(lab)):
        strata[f"label {l}"] = lab == l
    for t in ("correct", "boundary", "type", "spurious"):
        strata[f"outcome {t}"] = et == t
    rows = {}
    for nm, m_ in strata.items():
        if m_.sum() < 30:
            continue
        y = yd[m_]
        a, b = M.fm(P["P0"][m_], S["P0"][m_], y), M.fm(P["P0+M6"][m_], S["P0+M6"][m_], y)
        rows[nm] = {"n": int(m_.sum()), "err_rate": round(float(1 - y.mean()), 4), "nll_P0": a["nll"], "nll_M6": b["nll"], "dNLL": round(b["nll"] - a["nll"], 4), "dECE": round(b["ece"] - a["ece"], 4),
                    "dBrier": round(b["brier"] - a["brier"], 5), "mean_p_P0": round(float(P["P0"][m_].mean()), 4), "mean_p_M6": round(float(P["P0+M6"][m_].mean()), 4)}
        if nm in ("all", "unseen (n=0)", "tail (n=1-2)", "head (n>=5)", "gazetteer exact match", "no exact match"):
            bt = M.boot(P["P0+M6"][m_], S["P0+M6"][m_], P["P0"][m_], S["P0"][m_], y, gd[m_], nb)
            rows[nm]["dNLL_ci"] = [round(bt["nll"]["lo"], 4), round(bt["nll"]["hi"], 4)]
    (ROOT / f"reports/ner/_m6_analysis_{ds}.json").write_text(json.dumps(rows, indent=1))
    print("==", ds)
    for nm, r in rows.items():
        print(f"{nm:26s} n={r['n']:5d} err={r['err_rate']:.3f} dNLL {r['dNLL']:+.4f} {r.get('dNLL_ci', '')} dECE {r['dECE']:+.4f} meanp {r['mean_p_P0']:.3f}->{r['mean_p_M6']:.3f}")


if __name__ == "__main__":
    for ds in ("tasteset", "recipedb3"):
        run(ds)
