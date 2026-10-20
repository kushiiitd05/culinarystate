#!/usr/bin/env python3
"""S127: one small calibration-method robustness comparison on span correctness (DEV, OOF-fit). Not a tuning loop: 7 pre-listed methods, 2 datasets.
Choose the SIMPLEST method whose NLL is not significantly worse than the best on either dataset (paired document bootstrap; tie -> fewer parameters)."""
import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import minimize_scalar
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import e1_e2_calibration as E  # noqa: E402
import e2_signal_calibration as M  # noqa: E402
from culinarystate.ner import router as R  # noqa: E402

METHODS = [  # name, design kind, post, n_params (rough)
    ("T", "P0", "T", 1), ("Platt", "P0", "platt", 2), ("Iso", "P0", "iso", 0), ("Platt+M6", "P0+M6", "platt", 4), ("Platt+label", "C", "platt", 12),
    ("Platt+Iso+M6", "P0+M6", "pi", 0), ("Platt+label+M6", "C+M6", "platt", 14)]


def fit_predict(oof, dev, spec, kind, post):
    Xo, Xd = M.design(oof, kind, spec), M.design(dev, kind, spec)
    yo = np.array([r["y"] for r in oof])
    sc = M.scaler(Xo)
    if post == "T":
        z = Xo[:, 0]
        nl = lambda t: -np.mean(np.where(yo == 1, -np.logaddexp(0, -z / t), -np.logaddexp(0, z / t)))
        t = minimize_scalar(lambda t: -nl(t), bounds=(0.2, 10), method="bounded").x
        s = Xd[:, 0] / t
        return 1 / (1 + np.exp(-s)), s
    if post == "iso":
        iso = IsotonicRegression(out_of_bounds="clip", y_min=0, y_max=1).fit(Xo[:, 0], yo)
        return iso.predict(Xd[:, 0]), Xd[:, 0]
    if post == "platt":
        m = LogisticRegression(max_iter=1000).fit(sc(Xo), yo)
        p = m.predict_proba(sc(Xd))[:, 1]
        return p, p
    m, iso, _ = R.fit_calibrator(sc(Xo), yo)
    return R.calibrated(m, iso, sc(Xd)), m.predict_proba(sc(Xd))[:, 1]


def run(ds, nb):
    oof, dev, labels = M.collect(ds)
    spec = {"nlab": len(labels), "cats": [], "fams": []}
    for r in oof + dev:                                         # lf/lg/r7 not needed for these blocks, set to avoid KeyError in unrelated blocks
        r.setdefault("lf", {}), r.setdefault("pf", "NA")
    yd, gd = np.array([r["y"] for r in dev]), np.array([r["group"] for r in dev])
    P, S = {}, {}
    for name, kind, post, _ in METHODS:
        P[name], S[name] = fit_predict(oof, dev, spec, kind, post)
    out = {"dataset": ds, "n_dev": len(dev), "metrics": {n: M.fm(P[n], S[n], yd) for n in P}, "vs_current": {}}
    best = min(out["metrics"], key=lambda n: out["metrics"][n]["nll"])
    out["best_nll"] = best
    for n in P:
        if n != best:
            b = M.boot(P[n], S[n], P[best], S[best], yd, gd, nb)
            out["vs_current"][n] = {"vs": best, "dNLL": b["nll"], "dECE": b["ece"], "dAURC": b["aurc"]}
    return out


if __name__ == "__main__":
    res = {ds: run(ds, 300) for ds in ("tasteset", "recipedb3")}
    (ROOT / "reports/ner/_calibrator_robustness.json").write_text(json.dumps(res, indent=1))
    for ds, o in res.items():
        print("==", ds, "best NLL:", o["best_nll"])
        for n, m in o["metrics"].items():
            v = o["vs_current"].get(n)
            print(f"{n:16s} nll {m['nll']:.4f} brier {m['brier']:.4f} ece {m['ece']:.4f} aurc {m['aurc']:.5f} p90 {m['prec@90']:.4f}" + (f" | dNLL vs best {v['dNLL']['delta']:+.4f} [{v['dNLL']['lo']:+.4f},{v['dNLL']['hi']:+.4f}]" if v else " | best"))
