"""STEP 07I-R phase `family-candidates`: provisional star families (pre-registered rule, DIRECT edge to centre only, no transitive chaining), cluster-consistency diagnostics,
dish-family candidates and the per-recipe identity tables. Operates on the KEPT subset of scored pairs only."""
from __future__ import annotations

import json
from collections import defaultdict
from itertools import combinations

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

from .pairwork import local_store

HETERO_SCORE = 0.60
INTERNAL_MAX_MEMBERS = 40


def collect_kept(run_dir, pids, rep_ids):
    """stream score+feature partitions -> frame of kept pairs with ids, components and score (rows in partition order)"""
    frames = []
    for pid in pids:
        s = pq.read_table(run_dir / "parts" / (pid + ".score.parquet")).to_pandas()
        keep = s.keep.to_numpy()
        if not keep.any():
            continue
        f = pq.read_table(run_dir / "parts" / (pid + ".feat.parquet")).to_pandas()
        assert (f.i.to_numpy() == s.i.to_numpy()).all() and (f.j.to_numpy() == s.j.to_numpy()).all()
        d = f[keep].copy()
        d["score"], d["features_available"], d["family_edge"] = s.score[keep].to_numpy(), s.features_available[keep].to_numpy(), s.family_edge[keep].to_numpy()
        frames.append(d)
    d = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    ids = np.asarray(rep_ids, dtype=object)
    d.insert(0, "a_recipe_id", ids[d.i.to_numpy()])
    d.insert(1, "b_recipe_id", ids[d.j.to_numpy()])
    d = d.rename(columns={"mask": "candidate_source_mask"})
    d["relation_status"] = np.where((d.candidate_source_mask == 8) & ~d.family_edge, "EXISTING_FAMILY_ONLY", "CANDIDATE_NEAR_DUPLICATE")
    d["relation_class"] = "UNCERTAIN"
    for k in ("title_token", "ingredient_idf", "instruction_shingle", "process_seq", "condition", "quantity_profile"):
        d[k + "_missing"] = d[k].isna()
    return d.sort_values(["score", "a_recipe_id", "b_recipe_id"], ascending=[False, True, True], kind="stable").reset_index(drop=True)


def star_cluster(n, ei, ej, es):
    """Deterministic star clustering. A member joins only through a DIRECT edge to its centre. Index order == recipe_id order."""
    adj = defaultdict(dict)
    for i, j, s in zip(ei.tolist(), ej.tolist(), es.tolist()):
        adj[i][j] = s
        adj[j][i] = s
    center = np.arange(n)
    conf = np.ones(n)
    done = set()
    for c in sorted(adj, key=lambda x: (-len(adj[x]), x)):
        if c in done:
            continue
        done.add(c)
        for nb in sorted(adj[c], key=lambda x: (-adj[c][x], x)):
            if nb not in done:
                done.add(nb)
                center[nb], conf[nb] = c, adj[c][nb]
    return center, conf


def consistency(view_path, idf, rep_ids, members_by_center, src_of, usage_of):
    """pairwise internal diagnostics for multi-member families (<= INTERNAL_MAX_MEMBERS members; larger ones are reported UNSCORED).
    One store is built over every member of every scored family (not one per family)."""
    plan, pair_i, pair_j, owner = [], [], [], []
    for c, mem in members_by_center.items():
        base = {"center_idx": c, "member_count": len(mem), "source_diversity": len({src_of[m] for m in mem}), "usage_class_count": len({usage_of[m] for m in mem})}
        plan.append(base)
        if len(mem) <= INTERNAL_MAX_MEMBERS:
            for a_, b_ in combinations(sorted(mem), 2):
                pair_i.append(a_), pair_j.append(b_), owner.append(len(plan) - 1)
    scores, ings, procs = defaultdict(list), defaultdict(list), defaultdict(list)
    if pair_i:
        ii, jj = np.array(pair_i, dtype=np.int64), np.array(pair_j, dtype=np.int64)
        st, li, lj = local_store(view_path, idf, ii, jj)
        for k, (a_, b_) in enumerate(zip(li.tolist(), lj.tolist())):
            f = st.finalize(st.components(a_, b_))
            o = owner[k]
            if f["score"] is not None:
                scores[o].append(f["score"])
            if f["ingredient_idf"] is not None:
                ings[o].append(f["ingredient_idf"])
            if f["process_set"] is not None:
                procs[o].append(f["process_set"])
    npairs = np.bincount(np.array(owner, dtype=np.int64), minlength=len(plan)) if owner else np.zeros(len(plan), dtype=int)
    rows = []
    for o, base in enumerate(plan):
        sc = scores[o]
        rows.append({**base, "internal_pairs_scored": int(npairs[o]), "min_internal_score": min(sc) if sc else np.nan, "mean_internal_score": float(np.mean(sc)) if sc else np.nan,
                     "max_disagreement": 1.0 - min(sc) if sc else np.nan, "ingredient_agreement": float(np.mean(ings[o])) if ings[o] else np.nan, "process_agreement": float(np.mean(procs[o])) if procs[o] else np.nan})
    return pd.DataFrame(rows)


def build(exact: pd.DataFrame, rep_ids, rep_title_key, kept: pd.DataFrame, view_path, idf):
    """returns dict of output frames: members(df per recipe), reps, families(registry+consistency), dish"""
    n = len(rep_ids)
    fe = kept[kept.family_edge]
    center, conf = star_cluster(n, fe.i.to_numpy(), fe.j.to_numpy(), fe.score.to_numpy())
    fam_order = np.unique(center)  # centre indices ascending == recipe_id ascending
    fid_of_center = {int(c): "RF-%08d" % (k + 1) for k, c in enumerate(fam_order)}
    reps = pd.DataFrame({"recipe_id": rep_ids, "recipe_family_id": [fid_of_center[int(c)] for c in center], "family_center_id": np.asarray(rep_ids, dtype=object)[center], "edge_confidence": conf})
    size = reps.groupby("recipe_family_id").recipe_id.transform("size")
    minconf = reps.groupby("recipe_family_id").edge_confidence.transform("min")
    reps["family_role"] = np.where(size == 1, "SINGLETON", np.where(reps.recipe_id == reps.family_center_id, "CENTER", "MEMBER"))
    reps["heterogeneous"] = (size > 1) & (minconf < HETERO_SCORE)
    # cluster consistency (additive diagnostics; membership is not altered by them)
    src_of = exact.drop_duplicates("group_representative_id").set_index("group_representative_id")
    srcm = src_of.source_family.reindex(rep_ids).tolist()
    usgm = src_of.usage_class.reindex(rep_ids).tolist()
    mem_by_center = defaultdict(list)
    for i, c in enumerate(center.tolist()):
        mem_by_center[c].append(i)
    multi = {c: m for c, m in mem_by_center.items() if len(m) > 1}
    cons = consistency(view_path, idf, rep_ids, multi, srcm, usgm) if multi else pd.DataFrame(columns=["center_idx"])
    if len(cons):
        cons["recipe_family_id"] = cons.center_idx.map(lambda c: fid_of_center[int(c)])
        cons["family_center_id"] = cons.center_idx.map(lambda c: rep_ids[int(c)])
        cons["family_review_status"] = np.where((cons.min_internal_score < HETERO_SCORE) | (cons.usage_class_count > 2) | cons.min_internal_score.isna(), "FAMILY_CANDIDATE_REVIEW", "FAMILY_CANDIDATE_CONSISTENT")
        cons = cons.drop(columns="center_idx")
    # dish-family candidates: families whose CENTRE title key is identical (>=4 chars, >=2 families)
    tk = pd.Series(rep_title_key, index=rep_ids)
    cen = reps[reps.family_role.isin(["CENTER", "SINGLETON"])]
    cen = cen.assign(_tk=tk.reindex(cen.recipe_id).fillna("").to_numpy())
    kk = cen[cen._tk.str.len() >= 4]
    grp = kk.groupby("_tk").recipe_family_id.apply(list)
    grp = grp[grp.map(len) >= 2].sort_index()
    dish_of, dish_rows = {}, []
    members = exact.merge(reps[["recipe_id", "recipe_family_id", "family_center_id", "edge_confidence", "heterogeneous"]].rename(columns={"recipe_id": "group_representative_id"}), on="group_representative_id", how="left")
    fam_recipe_count = members.groupby("recipe_family_id").recipe_id.transform("size")
    members["family_role"] = np.where(fam_recipe_count == 1, "SINGLETON", np.where(members.group_representative_id == members.family_center_id, "CENTER_GROUP", "MEMBER_GROUP"))
    members["representative_recipe_id"] = members.family_center_id
    in_dish = {f for fams in grp for f in fams}
    sub = members.loc[members.recipe_family_id.isin(in_dish), ["recipe_family_id", "source_family", "locale"]]
    fam_cnt = sub.groupby("recipe_family_id").size().to_dict()
    fam_src = sub.groupby("recipe_family_id").source_family.agg(lambda x: set(x)).to_dict()
    fam_loc = sub.dropna(subset=["locale"]).groupby("recipe_family_id").locale.agg(lambda x: set(x)).to_dict()
    for k, (key, fams) in enumerate(grp.items(), 1):
        did = "DF-%07d" % k
        for f in fams:
            dish_of[f] = did
        dish_rows.append({"dish_family_candidate_id": did, "dish_key": key, "family_count": len(fams), "recipe_count": int(sum(fam_cnt[f] for f in fams)),
                          "source_families": json.dumps(sorted(set().union(*(fam_src[f] for f in fams)))), "locales": json.dumps(sorted(set().union(*(fam_loc.get(f, set()) for f in fams)))),
                          "evidence": "TITLE_HEAD_KEY", "provenance_class": "INFERRED_CANDIDATE", "member_family_ids": json.dumps(fams)})
    members["dish_family_candidate_id"] = members.recipe_family_id.map(dish_of)
    reps["dish_family_candidate_id"] = reps.recipe_family_id.map(dish_of)
    return {"members": members, "reps": reps, "consistency": cons, "dish": pd.DataFrame(dish_rows), "n_families": len(fam_order)}
