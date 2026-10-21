#!/usr/bin/env python3
"""CulinarySpanDecision inventory (no chooser, no TEST): reads OOF/DEV k-best files from bench_train_v2.py --nbest-parts and reports availability, determinism vs the stored v1 OOF 1-best, differing-path counts, recoverable gold spans by label/error type, top-5 oracle F1.
  python csd_inventory.py <dataset> <runs_csd_dir> [out.json]"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import bench_train_v2 as T  # noqa: E402

ds, rd = sys.argv[1], Path(sys.argv[2])
out = Path(sys.argv[3]) if len(sys.argv) > 3 else rd / f"csd_inventory_{ds}.json"
data = str(HERE / ("TASTEset.csv" if ds == "tasteset" else "Ingredient_Annotated_Dataset.csv"))
docs = T.load_docs(ds, data)
view = T.B.VIEWS[T.PRIMARY[ds]]
gold = lambda i: {tuple(s) for s in docs[i][1] if s[2] in view}
S = lambda sp: {tuple(s) for s in sp}


def f1(tp, fp, fn):
    return 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 1.0


def kind(g, pred):
    if g in pred:
        return "present"
    ov = [p for p in pred if p[0] < g[1] and g[0] < p[1]]
    if not ov:
        return "MISSING (no overlapping predicted span)"
    if any(p[0] == g[0] and p[1] == g[1] for p in ov):
        return "LABEL (same boundary, wrong label)"
    return "BOUNDARY (overlap, different boundary)" + (" same-label" if any(p[2] == g[2] for p in ov) else " diff-label")


R = {"dataset": ds, "files": sorted(p.name for p in rd.glob(f"{ds}__*nbest_oof*.json"))}
for part in ("oof", "dev"):
    items = []  # (doc_idx, paths)
    if part == "oof":
        for f in sorted(rd.glob(f"{ds}__*_crf_oof*__seed1.nbest_oof.json")):
            d = json.load(open(f))
            items += list(zip(d["doc_indices"], d["nbest"]))
    else:
        f = rd.parent / "runs_v2dm" / f"{ds}__deberta-base_crf__seed1.nbest_dev.json"  # full-TRAIN model (DEV-protocol diagnostic); fold models also write a dev file but it is not used
        if f.exists():
            d = json.load(open(f))
            dev_idx = json.load(open(HERE / f"{ds}_split_v1.json"))["indices"]["dev"]
            items += list(zip(dev_idx, d if isinstance(d, list) else d["nbest"]))
    if not items:
        continue
    o = {"docs": len(items), "gold_spans": sum(len(gold(i)) for i, _ in items)}
    tp1 = fp1 = fn1 = tpo = fpo = fno = 0
    differ = 0
    miss, rec = 0, 0
    bylabel, bykind = Counter(), Counter()
    recl, reck = Counter(), Counter()
    ndiff_paths = Counter()
    n_k = Counter()
    for i, paths in items:
        g = gold(i)
        P = [S(p["spans"]) for p in paths]
        n_k[len(P)] += 1
        d = sum(1 for p in P[1:] if p != P[0])
        ndiff_paths[d] += 1
        differ += d > 0
        tp, fp, fn = len(g & P[0]), len(P[0] - g), len(g - P[0])
        tp1, fp1, fn1 = tp1 + tp, fp1 + fp, fn1 + fn
        best = max(P, key=lambda p: (f1(len(g & p), len(p - g), len(g - p)), p == P[0]))
        tpo, fpo, fno = tpo + len(g & best), fpo + len(best - g), fno + len(g - best)
        union = set().union(*P)
        for s in g - P[0]:
            miss += 1
            k = kind(s, P[0])
            bylabel[s[2]] += 1
            bykind[k] += 1
            if s in union:
                rec += 1
                recl[s[2]] += 1
                reck[k] += 1
    o.update({"paths_per_doc": dict(n_k), "docs_where_paths2to5_differ_from_path1": differ, "n_differing_paths_hist": dict(sorted(ndiff_paths.items())),
              "path1_micro_F1": round(f1(tp1, fp1, fn1), 4), "top5_oracle_doc_F1": round(f1(tpo, fpo, fno), 4), "oracle_gain": round(f1(tpo, fpo, fno) - f1(tp1, fp1, fn1), 4),
              "gold_spans_missed_by_path1": miss, "of_which_present_in_top5_union": rec, "recoverable_fraction": round(rec / miss, 3) if miss else None,
              "missed_by_label": dict(bylabel), "recoverable_by_label": dict(recl), "missed_by_error_type": dict(bykind), "recoverable_by_error_type": dict(reck)})
    if part == "oof":  # determinism vs stored v1 OOF 1-best
        same = tot = 0
        for f in sorted((rd.parent / "runs_conf").glob(f"{ds}__deberta-base_crf_oof*__seed1.pred.json")):
            fold = f.name.split("_oof")[1][0]
            nb = json.load(open(rd / f"{ds}__deberta-base_crf_oof{fold}__seed1.nbest_oof.json")) if (rd / f"{ds}__deberta-base_crf_oof{fold}__seed1.nbest_oof.json").exists() else None
            if not nb:
                continue
            pr = json.load(open(f)).get("oof")
            if pr is None:
                continue
            idx = dict(zip(nb["doc_indices"], nb["nbest"]))
            keys = list(pr) if isinstance(pr, dict) else range(len(pr))
            for j, di in enumerate(nb["doc_indices"]):
                v1 = pr[str(di)] if isinstance(pr, dict) and str(di) in pr else (pr[j] if not isinstance(pr, dict) else None)
                if v1 is None:
                    continue
                tot += 1
                same += S(v1) == S(idx[di][0]["spans"])
        o["determinism_vs_v1_oof_1best"] = {"docs_compared": tot, "identical": same}
    R[part] = o
out.write_text(json.dumps(R, indent=1))
print(json.dumps(R, indent=1))
