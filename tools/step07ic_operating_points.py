"""Step 07I-C: OP-MERGE / OP-SPLIT cut-point selection and recipe split groups.

Rules: THR-07IC-01..03, 05..09 (registry/preregistered_thresholds_v1.csv).
Selection functions see ONLY labelled pairs (score, label, stratum weight, recipe ids);
they never receive corpus size, group sizes, giant-component share or family counts (THR-07IC-09).
Writes NEW files only. Labels are never edited. Estimates are SINGLE-REVIEWER-BASIS (D-033).

  /opt/anaconda3/bin/python tools/step07ic_operating_points.py [--root .]
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

COPY_POS = frozenset({"SAME_RECIPE_COPY", "SAME_RECIPE_MINOR_VARIANT"})
DISH_POS = COPY_POS | {"SAME_DISH_DIFFERENT_RECIPE"}
MERGE_LB_MIN = 0.90  # THR-07IC-05
SPLIT_RECALL_TARGET = 0.95  # THR-07IC-06
N_FOLDS = 5
OUT_DIR = "ledgers/recipe_identity_v2"
AGREE = "annotation/duplicate_calibration/duplicate_pairs_v1_ADJUDICATED_kush_basis.csv"
KEY = "annotation/duplicate_calibration/duplicate_pairs_v1_KEY_SEALED.csv"
BASIS = "single_reviewer_basis"


def sha256_file(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def targets(label: str) -> dict | None:
    """Binary targets for a label; None for UNCERTAIN (excluded, THR-07IC-03)."""
    if label == "UNCERTAIN":
        return None
    return {
        "y_copy": int(label in COPY_POS),
        "y_dish": int(label in DISH_POS),
        "y_dish_sens": int(label in DISH_POS or label == "RELATED"),
    }


def build_pairs(labels: list[dict], key: list[dict]) -> list[dict]:
    """Join labels to the key on pair_id; drop UNCERTAIN; attach stratum weights (pool / n_stratum)."""
    kmap = {k["pair_id"]: k for k in key}
    joined = []
    for r in labels:
        t = targets(r["label"])
        if t is None:
            continue
        k = kmap[r["pair_id"]]
        joined.append({"pair_id": r["pair_id"], "a": r["a_recipe_id"], "b": r["b_recipe_id"],
                       "score": float(k["score"]), "stratum": k["stratum"],
                       "pool": float(k["stratum_pool_size"]), **t})
    n_by = {}
    for p in joined:
        n_by[p["stratum"]] = n_by.get(p["stratum"], 0) + 1
    return [{**p, "w": p["pool"] / n_by[p["stratum"]]} for p in joined]


def wilson(p: float, n_eff: float, z: float = 1.959963984540054) -> tuple[float, float]:
    if n_eff <= 0:
        return (float("nan"), float("nan"))
    d = 1 + z * z / n_eff
    c = p + z * z / (2 * n_eff)
    m = z * math.sqrt(p * (1 - p) / n_eff + z * z / (4 * n_eff * n_eff))
    return ((c - m) / d, (c + m) / d)


def _wprop(ws, ys):
    sw = sum(ws)
    if sw == 0:
        return None
    n_eff = sw * sw / sum(w * w for w in ws)  # Kish effective n
    p = sum(w * y for w, y in zip(ws, ys)) / sw
    return p, n_eff


def stats_at(pairs: list[dict], cut: float, target: str) -> dict:
    """Stratum-weighted precision / recall (Wilson on Kish n_eff) for 'score >= cut' vs target."""
    pred = [p for p in pairs if p["score"] >= cut]
    prec = _wprop([p["w"] for p in pred], [p[target] for p in pred])
    pos = [p for p in pairs if p[target] == 1]
    rec = _wprop([p["w"] for p in pos], [int(p["score"] >= cut) for p in pos])
    out = {"cut": cut, "n_pred_pos": len(pred), "n_pos": len(pos),
           "precision": None, "precision_ci95": None, "recall": None, "recall_ci95": None,
           "precision_unweighted": (sum(p[target] for p in pred) / len(pred)) if pred else None,
           "recall_unweighted": (sum(p["score"] >= cut for p in pos) / len(pos)) if pos else None}
    if prec:
        out["precision"], out["precision_ci95"] = prec[0], list(wilson(*prec))
    if rec:
        out["recall"], out["recall_ci95"] = rec[0], list(wilson(*rec))
    return out


def candidate_cuts(pairs: list[dict]) -> list[float]:
    return sorted({p["score"] for p in pairs})


def select_op_merge(pairs: list[dict], target: str = "y_copy", min_lb: float = MERGE_LB_MIN) -> dict | None:
    """THR-07IC-07: max recall s.t. Wilson95 LB(precision) >= min_lb; ties -> higher cut."""
    best = None
    for cut in candidate_cuts(pairs):
        s = stats_at(pairs, cut, target)
        if s["precision"] is None or s["recall"] is None or s["precision_ci95"][0] < min_lb:
            continue
        if best is None or s["recall"] > best["recall"] or (s["recall"] == best["recall"] and cut > best["cut"]):
            best = s
    return best


def select_op_split(pairs: list[dict], target: str = "y_dish", recall_target: float = SPLIT_RECALL_TARGET) -> dict | None:
    """THR-07IC-08: highest cut whose weighted recall point estimate >= target."""
    best = None
    for cut in candidate_cuts(pairs):
        s = stats_at(pairs, cut, target)
        if s["recall"] is not None and s["recall"] >= recall_target and (best is None or cut > best["cut"]):
            best = s
    return best


def grouped_folds(pairs: list[dict], k: int = N_FOLDS) -> list[int]:
    """Fold per pair; pairs sharing a recipe (connected components) never straddle folds. Deterministic."""
    parent: dict[str, str] = {}

    def find(x):
        parent.setdefault(x, x)
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for p in pairs:
        ra, rb = find(p["a"]), find(p["b"])
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)
    comps: dict[str, list[int]] = {}
    for i, p in enumerate(pairs):
        comps.setdefault(find(p["a"]), []).append(i)
    load = [0] * k
    fold = [0] * len(pairs)
    for root, idx in sorted(comps.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        f = min(range(k), key=lambda j: (load[j], j))
        load[f] += len(idx)
        for i in idx:
            fold[i] = f
    return fold


def nested_cv(pairs: list[dict], selector, target: str, k: int = N_FOLDS) -> dict:
    """Grouped CV check: select on k-1 folds, apply the cut to the held-out fold, pool held-out predictions."""
    fold = grouped_folds(pairs, k)
    cuts, held = [], []
    for f in range(k):
        tr = [p for p, g in zip(pairs, fold) if g != f]
        te = [p for p, g in zip(pairs, fold) if g == f]
        sel = selector(tr)
        cuts.append(None if sel is None else sel["cut"])
        held.extend([{**p, "_cut": cuts[-1]} for p in te])
    pred = [p for p in held if p["_cut"] is not None and p["score"] >= p["_cut"]]
    pos = [p for p in held if p[target] == 1]
    prec = _wprop([p["w"] for p in pred], [p[target] for p in pred])
    rec = _wprop([p["w"] for p in pos], [int(p["_cut"] is not None and p["score"] >= p["_cut"]) for p in pos])
    return {"fold_sizes": [sum(1 for g in fold if g == f) for f in range(k)], "fold_cuts": cuts,
            "oof_precision": prec[0] if prec else None,
            "oof_precision_ci95": list(wilson(*prec)) if prec else None,
            "oof_recall": rec[0] if rec else None,
            "oof_recall_ci95": list(wilson(*rec)) if rec else None}


def stratum_table(pairs: list[dict]) -> dict:
    t: dict[str, dict] = {}
    for p in pairs:
        r = t.setdefault(p["stratum"], {"n_labelled_non_uncertain": 0, "pool": p["pool"], "weight": p["w"],
                                        "n_y_copy": 0, "n_y_dish": 0})
        r["n_labelled_non_uncertain"] += 1
        r["n_y_copy"] += p["y_copy"]
        r["n_y_dish"] += p["y_dish"]
    return dict(sorted(t.items()))


def split_components(recipe_ids, group_of, edge_a, edge_b):
    """Union-find via scipy: exact duplicate groups + pair edges. Returns component label per recipe."""
    import numpy as np
    import pandas as pd
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import connected_components
    idx = pd.Index(recipe_ids)
    n = len(idx)
    gcodes, _ = pd.factorize(pd.Series(group_of))
    first = pd.Series(np.arange(n)).groupby(gcodes).transform("min").to_numpy()
    ea = idx.get_indexer(edge_a)
    eb = idx.get_indexer(edge_b)
    rows = np.concatenate([np.arange(n), ea])
    cols = np.concatenate([first, eb])
    g = coo_matrix((np.ones(len(rows), dtype=np.int8), (rows, cols)), shape=(n, n))
    return connected_components(g, directed=False)[1]


def build_groups(root: Path, split_cut: float):
    import numpy as np
    import pandas as pd
    L = root / "ledgers/recipe_identity"
    dg = pd.read_parquet(L / "duplicate_group_members_v1.parquet", columns=["recipe_id", "duplicate_group_id"])
    dg = dg.sort_values("recipe_id", kind="mergesort").reset_index(drop=True)
    cp = pd.read_parquet(L / "candidate_pairs_v1.parquet", columns=["a_recipe_id", "b_recipe_id", "score"])
    e = cp[cp["score"] >= split_cut]
    comp = split_components(dg["recipe_id"], dg["duplicate_group_id"], e["a_recipe_id"], e["b_recipe_id"])
    exact_only = split_components(dg["recipe_id"], dg["duplicate_group_id"], [], [])
    df = pd.DataFrame({"recipe_id": dg["recipe_id"], "comp": comp, "exact_comp": exact_only})
    df["_first"] = df.groupby("comp")["recipe_id"].transform("min")
    df["split_group_id"] = "SPLITGRP-REC-" + df["_first"]
    df["group_size"] = df.groupby("comp")["recipe_id"].transform("size").astype("int64")
    df["n_exact_dup_group_size"] = df.groupby("exact_comp")["recipe_id"].transform("size").astype("int64")
    df["basis_exact_duplicate"] = df["n_exact_dup_group_size"] > 1
    df["basis_op_split_edge"] = df["group_size"] > df["n_exact_dup_group_size"]
    df["calibrated"] = True
    df[BASIS] = True
    df["op_split_cut"] = float(split_cut)
    df["plane"] = "REC"
    return df[["recipe_id", "split_group_id", "group_size", "basis_exact_duplicate", "basis_op_split_edge",
               "calibrated", BASIS, "op_split_cut", "plane"]].reset_index(drop=True), int(len(e))


def size_dist(df) -> dict:
    s = df.groupby("split_group_id").size()
    q = s.quantile([0.5, 0.9, 0.99]).to_dict()
    return {"n_groups": int(len(s)), "n_recipes": int(len(df)), "largest": int(s.max()),
            "singletons": int((s == 1).sum()), "groups_ge_2": int((s >= 2).sum()),
            "largest_share_of_recipes": float(s.max() / len(df)),
            "p50": float(q[0.5]), "p90": float(q[0.9]), "p99": float(q[0.99])}


def fallback_comparison(root: Path, df) -> dict:
    """Relation to the tools/step16b_build_frame.py fallback grouping (dup+family+dish+title components). Finding only."""
    import importlib.util
    import pandas as pd
    spec = importlib.util.spec_from_file_location("s16b", root / "tools/step16b_build_frame.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    L = root / "ledgers/recipe_identity"
    fk = pd.read_parquet(L / "recipe_identity_fk_v1.parquet",
                         columns=["recipe_id", "duplicate_group_id", "recipe_family_id", "dish_family_candidate_id"])
    ft = pd.read_parquet(L / "recipe_identity_features_v1.parquet", columns=["recipe_id", "title_key"])
    f = fk.merge(ft, on="recipe_id", how="left").sort_values("recipe_id", kind="mergesort").reset_index(drop=True)
    title = f["title_key"].where(f["title_key"].fillna("") != "")
    f["fb"] = m.fallback_components(f["recipe_id"], {"dup": f["duplicate_group_id"], "fam": f["recipe_family_id"],
                                                       "dish": f["dish_family_candidate_id"], "title": title})
    j = df.merge(f[["recipe_id", "fb"]], on="recipe_id", how="inner")
    fb_size = j.groupby("fb")["recipe_id"].transform("size")
    n_sg_per_fb = j.groupby("fb")["split_group_id"].transform("nunique")
    n_fb_per_sg = j.groupby("split_group_id")["fb"].transform("nunique")
    fbs = j.groupby("fb").size()
    return {"recipes_compared": int(len(j)), "fallback_n_groups": int(len(fbs)), "fallback_largest": int(fbs.max()),
            "fallback_largest_share": float(fbs.max() / len(j)),
            "recipes_in_fallback_group_spanning_multiple_split_groups": int((n_sg_per_fb > 1).sum()),
            "recipes_in_split_group_spanning_multiple_fallback_groups": int((n_fb_per_sg > 1).sum()),
            "fallback_size_mean_per_recipe": float(fb_size.mean())}


def read_csv_rows(path: Path) -> list[dict]:
    import csv
    import io
    return list(csv.DictReader(io.StringIO(path.read_text(encoding="utf-8-sig"))))


def main(root: Path) -> None:
    import pandas as pd
    out = root / OUT_DIR
    out.mkdir(parents=True, exist_ok=True)
    key_p, adj_p = root / KEY, root / AGREE
    key_before = sha256_file(key_p)
    labels, key = read_csv_rows(adj_p), read_csv_rows(key_p)
    n_unc = sum(r["label"] == "UNCERTAIN" for r in labels)
    pairs = build_pairs(labels, key)

    merge = select_op_merge(pairs, "y_copy")
    split = select_op_split(pairs, "y_dish")
    split_sens = select_op_split(pairs, "y_dish_sens")
    merge_dish = select_op_merge(pairs, "y_dish")  # not used; shown for the Y_copy-vs-Y_dish ambiguity
    cv = {"op_merge_y_copy": nested_cv(pairs, lambda t: select_op_merge(t, "y_copy"), "y_copy"),
          "op_split_y_dish": nested_cv(pairs, lambda t: select_op_split(t, "y_dish"), "y_dish"),
          "op_split_y_dish_sens": nested_cv(pairs, lambda t: select_op_split(t, "y_dish_sens"), "y_dish_sens")}
    bounds = {}
    for tgt in ("y_copy", "y_dish"):
        pos_label = {"y_copy": COPY_POS, "y_dish": DISH_POS}[tgt]
        bounds[tgt] = {"uncertain_count": n_unc,
                       "note": "UNCERTAIN excluded from primary precision/recall (THR-07IC-03); never imputed",
                       "base_positive_rate_non_uncertain_unweighted": sum(p[tgt] for p in pairs) / len(pairs),
                       "positive_labels": sorted(pos_label)}

    groups, groups_alt = None, {}
    d = None
    if split is not None:
        groups, n_edges = build_groups(root, split["cut"])
        d = size_dist(groups)
        d["op_split_edges_applied"] = n_edges
        groups.to_parquet(out / "recipe_split_groups_v1.parquet", index=False)
        cmp_ = fallback_comparison(root, groups)
        if split_sens is not None:
            g2, e2 = build_groups(root, split_sens["cut"])
            groups_alt["related_is_1_sensitivity"] = {**size_dist(g2), "cut": split_sens["cut"], "op_split_edges_applied": e2}
    cp = pd.read_parquet(root / "ledgers/recipe_identity/candidate_pairs_v1.parquet",
                         columns=["a_recipe_id", "b_recipe_id", "score"])
    merge_edges = None
    if merge is not None:
        me = cp[cp["score"] >= merge["cut"]].reset_index(drop=True)
        me.to_parquet(out / "op_merge_pairs_v1.parquet", index=False)
        merge_edges = int(len(me))

    inputs = {AGREE: sha256_file(adj_p), KEY: key_before}
    for fp in sorted((root / "ledgers/recipe_identity").glob("*.parquet")):
        inputs[str(fp.relative_to(root))] = sha256_file(fp)
    for rel in ("registry/preregistered_thresholds_v1.csv", "tools/step16b_build_frame.py",
                "reports/step07i/step07ic_reviewer_agreement_v1.json"):
        inputs[rel] = sha256_file(root / rel)
    key_after = sha256_file(key_p)
    report = {
        "schema": "op_selection_report_v1", "basis": BASIS,
        "label_basis_caveat": "SINGLE-REVIEWER-BASIS ESTIMATES (D-033): labels are Kush's, Parv agreed after the fact; "
                              "blind-agreement evidence is below target (Y_copy kappa 0.571, Y_dish 0.588 vs 0.70). "
                              "Precision/recall carry that reviewer's bias.",
        "thresholds": {"THR-07IC-05_precision_LB_min": MERGE_LB_MIN, "THR-07IC-06_recall_target": SPLIT_RECALL_TARGET},
        "n_pairs_total": len(labels), "n_uncertain_excluded": n_unc, "n_pairs_used": len(pairs),
        "n_per_stratum": stratum_table(pairs),
        "estimator": "stratum inverse-probability weight w = pool_size/n_used_in_stratum; Wilson 95% on weighted proportion "
                     "with Kish effective n = (sum w)^2 / sum w^2. Strata treated as disjoint (pools may overlap).",
        "cut_rule": "predict positive iff score >= cut; candidate cuts = distinct observed labelled scores",
        "op_merge": {"target": "y_copy", "selected": merge, "edges_at_cut_in_candidate_pairs": merge_edges},
        "op_merge_if_y_dish_target_NOT_APPLIED": merge_dish,
        "op_split": {"target": "y_dish (RELATED=0, THR-07IC-02 primary)", "selected": split},
        "op_split_sensitivity_related_is_1_NOT_APPLIED": split_sens,
        "grouped_cv": {"folds": N_FOLDS, "grouping": "connected components of recipes across labelled pairs, "
                       "assigned greedily to folds (largest first, lowest-load fold)", "results": cv},
        "uncertain_bounds": bounds,
        "split_groups": d, "split_groups_alternate": groups_alt,
        "fallback_comparison_finding_only": cmp_ if split is not None else None,
        "contract_ambiguities": [
            "CA-1: plan silent on which binary target per operating point; used Y_copy for OP-MERGE (THR-07IC-01/05) and "
            "Y_dish primary (RELATED=0) for OP-SPLIT (THR-07IC-02/06). Alternates reported, not applied.",
            "CA-2: THR-07IC-07 names 'grouped CV, stratum-weighted calibrator' but the calibrator is a single score cut-point; "
            "folds/grouping unspecified. The cut is selected on all non-UNCERTAIN labels; grouped 5-fold nested CV "
            "(recipe-connected components) is a diagnostic only.",
            "CA-3: candidate_pairs_v1 holds only 'kept' pairs (score>=0.50, family edge, family-source, or title-source with "
            "title_token>=0.8) on duplicate-group representatives. Recall is relative to that set; if OP-SPLIT < 0.50, "
            "unretained low-score pairs cannot be linked (corpus-level recall lower than estimated). Recall on the sealed v2 "
            "probes does not exist yet.",
            "CA-4: stratum pools may overlap; weights treat strata as disjoint.",
            "CA-5: THR-07IC-06 is a target reported with CI, not a pass/fail; THR-07IC-08 uses the point estimate only.",
            "CA-6: label file reasons are 'AI draft' text; the labels are Kush's but may be anchored on them.",
            "CA-7: group edges = exact duplicate groups + candidate pairs with score >= OP-SPLIT cut (07I-S method); "
            "existing PROVISIONAL family edges are not added separately.",
        ],
        "sealed_key_sha256_before": key_before, "sealed_key_sha256_after": key_after,
        "sealed_key_unchanged": key_before == key_after,
        "input_sha256": inputs,
    }
    (out / "op_selection_report_v1.json").write_text(json.dumps(report, indent=1, sort_keys=True), encoding="utf-8")
    print(json.dumps({"merge": merge, "split": split, "groups": d, "merge_edges": merge_edges}, indent=1))


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    main(Path(ap.parse_args().root).resolve())
