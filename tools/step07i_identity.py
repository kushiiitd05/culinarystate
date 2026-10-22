#!/usr/bin/env python3
"""STEP 07I part 3: duplicate groups (deterministic), candidate near-duplicates, provisional recipe families (pre-registered rule), dish-family candidates, representatives, consensus profiles,
FK update of the derived recipe base, view membership, Gold firewall. Rules: reports/step07i/preregistration_v1.md (committed before this ran).
  python tools/step07i_identity.py [--sample N]   (N: deterministic 1-in-N recipe sample for testing; writes with suffix _sample)"""
import argparse
import csv
import hashlib
import json
import math
import multiprocessing as mp
import sys
import time
import zlib
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.identity import features as F  # noqa: E402
from culinarystate.identity import pairs as PS  # noqa: E402

ID = ROOT / "ledgers/recipe_identity"
REL_RANK = {"EXACT_BINARY_COPY": 3, "MIRRORED_COPY": 2, "EXACT_NORMALIZED_COPY": 1}
TIER_RANK = {"GOLD_PENDING_INDEPENDENT_IAA": 3, "SILVER_AUTO": 2, "SOURCE_RAW": 1}
USAGE_RANK = {"PUBLIC_OPEN": 5, "REDISTRIBUTABLE_WITH_ATTRIBUTION": 4, "LOCAL_RESEARCH_ONLY": 3, "LICENCE_UNVERIFIED": 2, "UNKNOWN": 1}
STATUS_RANK = {"PROCEDURALLY_RICH": 4, "PARTIAL_CONDITIONS": 3, "QUALITATIVE_ONLY": 2, "INSUFFICIENT_CONDITIONS": 1, "UNKNOWN": 0}
_S = None


class UF:
    def __init__(self, n):
        self.p = list(range(n))

    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        a, b = self.find(a), self.find(b)
        if a != b:
            self.p[max(a, b)] = min(a, b)


def pair_worker(chunk):
    out = []
    for i, j, mask in chunk:
        f = _S.features(i, j)
        keep = (f["score"] is not None and f["score"] >= 0.50) or f["family_edge"] or (mask & 8)
        out.append((i, j, mask, keep, f))
    return out


def load(sample):
    feat = pq.read_table(ID / "recipe_identity_features_v1.parquet").to_pandas()
    base = pq.read_table(ROOT / "ledgers/recipe_base/recipe_base_v1.parquet", columns=["recipe_id", "source_id", "source_record_id", "title_raw", "locale", "cuisine_if_explicit", "quality_tier", "has_instructions", "has_ingredients", "has_quantities", "has_conditions",
                                                                                         "has_gold_annotations", "recipe_family_id", "raw_recipe_pointer"]).to_pandas().rename(columns={"recipe_family_id": "legacy_family_id"})
    if sample:
        keep = feat.recipe_id.map(lambda r: zlib.crc32(r.encode()) % sample == 0)
        feat, base = feat[keep].reset_index(drop=True), base[base.recipe_id.isin(set(feat.recipe_id[keep]))].reset_index(drop=True)
    df = feat.merge(base, on="recipe_id", how="left", validate="1:1")
    usage = {r["source_id"]: r["usage_class"] for r in csv.DictReader(open(ROOT / "registry/recipe_source_usage_registry_v1.csv", encoding="utf-8"))}
    df["usage_class"] = df.source_id.map(lambda s: usage.get(s, "UNKNOWN"))
    # A1 canonical url (explicit source identifier for mirrored copies)
    a1 = {}
    for l in open(ROOT.parent / "a1" / "A1 3" / "data" / "processed" / "recipes_processed.jsonl", encoding="utf-8"):
        r = json.loads(l)
        a1[r["recipe_id"]] = r.get("canonical_url")
    df["canonical_url"] = [a1.get(s) if f == "A1_BBC_GOOD_FOOD" else None for s, f in zip(df.source_record_id, df.source_family)]
    return df


def exact_groups(df):
    n = len(df)
    pos = {r: i for i, r in enumerate(df.recipe_id)}
    valid = ((df.n_chars >= 60) & ((df.n_ing_lines + df.n_steps) > 0)).to_numpy()
    uf = UF(n)
    edge_rel = defaultdict(int)  # recipe idx -> best relation rank among incident deterministic edges
    stats = {}
    for key, rel in (("raw_hash", "EXACT_BINARY_COPY"), ("rec_content_sha256", "EXACT_BINARY_COPY"), ("canonical_url", "MIRRORED_COPY"), ("norm_text_hash", "EXACT_NORMALIZED_COPY")):
        col = df[key]
        m = valid & col.notna().to_numpy()
        if key == "canonical_url":
            m = col.notna().to_numpy()
        g = pd.DataFrame({"k": col[m].to_numpy(), "i": np.nonzero(m)[0]}).groupby("k").i.apply(list)
        g = g[g.map(len) > 1]
        groups, members = 0, 0
        for lst in g:
            groups += 1
            members += len(lst)
            for a in lst[1:]:
                uf.union(lst[0], a)
            for a in lst:
                edge_rel[a] = max(edge_rel[a], REL_RANK[rel])
        stats[rel + "|" + key] = {"groups": groups, "records": members}
    root = np.array([uf.find(i) for i in range(n)])
    return root, edge_rel, stats, valid


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", type=int, default=0)
    a = ap.parse_args()
    suf = "_sample" if a.sample else ""
    t0 = time.time()
    df = load(a.sample)
    n = len(df)
    print("recipes", n, flush=True)
    # ---------------- Level A: deterministic duplicate groups ----------------
    root, edge_rel, estats, valid = exact_groups(df)
    df["_root"] = root
    order = df.groupby("_root").recipe_id.min().sort_values()
    gid_of_root = {r: f"DG-{k + 1:08d}" for k, r in enumerate(order.index)}
    df["duplicate_group_id"] = df._root.map(gid_of_root)
    rel_name = {3: "EXACT_BINARY_COPY", 2: "MIRRORED_COPY", 1: "EXACT_NORMALIZED_COPY", 0: "NONE"}
    df["_rel"] = [rel_name[edge_rel.get(i, 0)] for i in range(n)]
    # representative per group
    comp = (df.has_instructions.astype(int) + df.has_ingredients.astype(int) + df.has_quantities.astype(int) + df.has_conditions.astype(int))
    df["_rep_key"] = list(zip(df.quality_tier.map(TIER_RANK).fillna(0), df.usage_class.map(USAGE_RANK).fillna(0), comp, df.n_ing_lines.clip(upper=30), df.n_steps.clip(upper=30)))
    rep_idx = {}
    for i, (g, k, r) in enumerate(zip(df.duplicate_group_id, df._rep_key, df.recipe_id)):
        cur = rep_idx.get(g)
        if cur is None or (k, -0) > (df._rep_key[cur], -0) or (k == df._rep_key[cur] and r < df.recipe_id[cur]):
            rep_idx[g] = i
    df["group_representative_id"] = df.duplicate_group_id.map(lambda g: df.recipe_id[rep_idx[g]])
    gsize = df.groupby("duplicate_group_id").recipe_id.transform("size")
    df["group_size"] = gsize
    gsrc = df.groupby("duplicate_group_id").source_family.transform("nunique")
    df["duplicate_relation"] = np.where(df.group_size == 1, "NONE", np.where(df.recipe_id == df.group_representative_id, "REPRESENTATIVE", df._rel))
    df["duplicate_status"] = np.where(df.group_size == 1, "SINGLETON", "DETERMINISTIC_EXACT")
    df["group_cross_source"] = gsrc > 1
    reps = df[df.recipe_id == df.group_representative_id].reset_index(drop=True)
    print(f"groups {len(reps)} (exact dedup logical recipes), t={time.time() - t0:.0f}s", flush=True)
    # ---------------- candidate generation on representatives ----------------
    # token ids, idf
    vocab = {}
    for lst in reps.ing_toks:
        for t in lst:
            vocab.setdefault(t, 0)
    for k, t in enumerate(sorted(vocab)):
        vocab[t] = k
    reps["toks_list"] = [sorted(vocab[t] for t in l) for l in reps.ing_toks]
    reps["toks_set"] = [frozenset(l) for l in reps.toks_list]
    dfc = Counter(t for s in reps.toks_set for t in s)
    N = len(reps)
    idf = {t: math.log((N + 1) / (c + 1)) + 1.0 for t, c in dfc.items()}
    reps["ids_set"] = [frozenset(l) for l in reps.ing_ids]
    reps["proc_seq"] = reps.proc_seq.map(list)
    reps["title_key"] = reps.title_key.fillna("")
    reps["title_norm"] = reps.title_norm.fillna("")
    # cond signatures
    condsig = defaultdict(set)
    cm = pq.read_table(ROOT / "ledgers/recipe_semantics/recipe_condition_mentions_v1.parquet", columns=["recipe_id", "expression_family", "canonical_value", "normalized_status"], filters=[("expression_family", "in", ["TEMPERATURE", "TIME"])]).to_pandas()
    cm = cm[cm.canonical_value.notna() & cm.recipe_id.isin(set(reps.recipe_id))]
    for r, f, v in zip(cm.recipe_id, cm.expression_family, cm.canonical_value):
        condsig[r].add(("T%d" % round(v)) if f == "TEMPERATURE" else ("t%d" % round(v / 60)))
    reps["cond_set"] = reps.recipe_id.map(lambda r: frozenset(condsig.get(r, ())))
    reps["mass_dict"] = [dict(zip(a, b)) if len(a) else {} for a, b in zip(reps.mass_ing, reps.mass_g)]
    reps["mh_steps"] = reps.mh_steps.map(lambda x: x if x is not None and not (isinstance(x, float)) else None)
    reps["mh_ing"] = reps.mh_ing.map(lambda x: x if x is not None and not (isinstance(x, float)) else None)
    store = PS.Store(reps, idf)
    cand = defaultdict(int)
    diag = Counter()

    def add(i, j, bit):
        if i != j:
            cand[(i * N + j) if i < j else (j * N + i)] |= bit
    # (a) title blocks
    by_title = defaultdict(list)
    for i, t in enumerate(store.title_norm):
        if len(t) >= 6:
            by_title[t].append(i)
    rare = {}
    for i in range(N):
        tk = store.toks[i]
        rare[i] = min(set(tk), key=lambda t: (dfc.get(t, 0), t)) if tk else None
    for t, lst in by_title.items():
        if len(lst) < 2:
            continue
        blocks = [lst] if len(lst) <= 60 else None
        if blocks is None:
            sub = defaultdict(list)
            for i in lst:
                if rare[i] is not None:
                    sub[rare[i]].append(i)
            blocks = [s for s in sub.values() if len(s) >= 2]
            diag["title_blocks_subblocked"] += 1
        for b in blocks:
            if len(b) > 60:
                diag["title_subblocks_skipped_over_60"] += 1
                continue
            for x in range(len(b)):
                for y in range(x + 1, len(b)):
                    add(b[x], b[y], 1)
    diag["pairs_after_title"] = len(cand)

    # (b)(c) LSH
    def lsh(col, rows, nb, bit, name, cap=200, allow=None):
        sigs = [(i, np.frombuffer(s, dtype=np.uint32)) for i, s in enumerate(col) if s is not None and (allow is None or allow[i])]
        if not sigs:
            return
        idx = np.array([i for i, _ in sigs])
        M = np.stack([s for _, s in sigs]).astype(np.uint64)
        for b in range(nb):
            blk = M[:, b * rows:(b + 1) * rows]
            key = np.zeros(len(blk), dtype=np.uint64)
            for c in range(rows):
                key = key * np.uint64(1000003) ^ blk[:, c]
            o = np.argsort(key, kind="stable")
            ks = key[o]
            starts = np.nonzero(np.r_[True, ks[1:] != ks[:-1]])[0]
            ends = np.r_[starts[1:], len(ks)]
            for s, e in zip(starts, ends):
                sz = e - s
                if sz < 2:
                    continue
                if sz > cap:
                    diag[name + "_buckets_skipped_over_cap"] += 1
                    diag[name + "_records_in_skipped_buckets"] += int(sz)
                    continue
                mem = idx[o[s:e]]
                for x in range(sz):
                    for y in range(x + 1, sz):
                        add(int(mem[x]), int(mem[y]), bit)
    lsh(store.mh_steps, 4, 16, 2, "steps_lsh")
    diag["pairs_after_steps_lsh"] = len(cand)
    lsh(reps.mh_ing.tolist(), 4, 8, 4, "ing_lsh", cap=50, allow=[len(t) >= 4 for t in store.tokset])
    diag["pairs_after_ing_lsh"] = len(cand)
    # (d) existing REC family co-membership
    ef = defaultdict(list)
    for i, f in enumerate(reps.existing_family_id):
        if isinstance(f, str) and not f.startswith("FAM-FC") and not f.startswith("FAM-TS"):
            ef[f].append(i)
    for f, lst in ef.items():
        if 2 <= len(lst) <= 30:
            for x in range(len(lst)):
                for y in range(x + 1, len(lst)):
                    add(lst[x], lst[y], 8)
    diag["pairs_total_candidates"] = len(cand)
    diag["pairs_by_source_bit"] = {str(b): sum(1 for m in cand.values() if m & b) for b in (1, 2, 4, 8)}
    print(f"candidates {len(cand)} t={time.time() - t0:.0f}s diag={dict(diag)}", flush=True)
    # ---------------- pair features (fork pool shares the store) ----------------
    global _S
    _S = store
    items = [(k // N, k % N, m) for k, m in sorted(cand.items())]
    chunks = [items[k:k + 4000] for k in range(0, len(items), 4000)]
    kept, n_edges, comp_n = [], 0, 0
    with mp.get_context("fork").Pool(4) as pool:
        for res in pool.imap(pair_worker, chunks):
            for i, j, mask, keep, f in res:
                comp_n += 1
                if keep:
                    kept.append((i, j, mask, f))
                    n_edges += int(f["family_edge"])
    diag["pairs_features_computed"] = comp_n
    diag["pairs_kept_score_ge_0.5_or_family_edge_or_existing_family"] = len(kept)
    diag["provisional_family_edges"] = n_edges
    print(f"features done kept={len(kept)} edges={n_edges} t={time.time() - t0:.0f}s", flush=True)
    # ---------------- Level B: star clustering on family edges ----------------
    adj = defaultdict(dict)
    for i, j, m, f in kept:
        if f["family_edge"]:
            adj[i][j] = f["score"]
            adj[j][i] = f["score"]
    centers = sorted(adj, key=lambda x: (-len(adj[x]), store.id[x]))
    fam_of, center_of, conf = {}, {}, {}
    for c in centers:
        if c in fam_of:
            continue
        fam_of[c], center_of[c], conf[c] = c, c, 1.0
        for nb in sorted(adj[c], key=lambda x: (-adj[c][x], store.id[x])):
            if nb not in fam_of:
                fam_of[nb], center_of[nb], conf[nb] = c, c, adj[c][nb]
    for i in range(N):
        if i not in fam_of:
            fam_of[i], center_of[i], conf[i] = i, i, 1.0
    fam_order = sorted({fam_of[i] for i in range(N)}, key=lambda c: store.id[c])
    fid = {c: f"RF-{k + 1:08d}" for k, c in enumerate(fam_order)}
    reps["recipe_family_id"] = [fid[fam_of[i]] for i in range(N)]
    reps["family_center_id"] = [store.id[center_of[i]] for i in range(N)]
    reps["edge_confidence"] = [conf[i] for i in range(N)]
    fam_size = reps.groupby("recipe_family_id").recipe_id.transform("size")
    reps["family_role"] = np.where(fam_size == 1, "SINGLETON", np.where(reps.recipe_id == reps.family_center_id, "CENTER", "MEMBER"))
    minconf = reps.groupby("recipe_family_id").edge_confidence.transform("min")
    reps["heterogeneous"] = (fam_size > 1) & (minconf < 0.60)
    diag["families_multi_rep"] = int((reps.groupby("recipe_family_id").size() > 1).sum())
    print(f"families {len(fam_order)} t={time.time() - t0:.0f}s", flush=True)
    # ---------------- tables ----------------
    df = df.merge(reps[["duplicate_group_id", "recipe_family_id", "family_center_id", "edge_confidence", "heterogeneous"]].rename(columns={"duplicate_group_id": "duplicate_group_id"}), on="duplicate_group_id", how="left")
    # family representative: the group representative of the family-center group
    center_group_rep = dict(zip(reps.recipe_id, reps.group_representative_id))
    df["representative_recipe_id"] = df.family_center_id.map(center_group_rep)
    df["family_role"] = np.where(df.recipe_family_id.map(df.groupby("recipe_family_id").size()) == 1, "SINGLETON", np.where(df.group_representative_id == df.family_center_id, "CENTER_GROUP", "MEMBER_GROUP"))
    # dish-family candidates
    fam_key = df.merge(reps[["recipe_id", "title_key"]].rename(columns={"recipe_id": "group_representative_id", "title_key": "_tk"}), on="group_representative_id", how="left")
    fk = fam_key.groupby("recipe_family_id")._tk.first()
    kk = fk[fk.fillna("").str.len() >= 4]
    dsh = kk.groupby(kk).apply(lambda s: list(s.index))
    dsh = dsh[dsh.map(len) >= 2].sort_index()
    dish_rows, dish_of = [], {}
    for k, (key, fams) in enumerate(dsh.items(), 1):
        did = f"DF-{k:07d}"
        for f_ in fams:
            dish_of[f_] = did
        sub = df[df.recipe_family_id.isin(fams)]
        dish_rows.append({"dish_family_candidate_id": did, "dish_key": key, "family_count": len(fams), "recipe_count": int(len(sub)), "source_families": json.dumps(sorted(sub.source_family.unique())), "locales": json.dumps(sorted(set(sub.locale.dropna()))),
                          "evidence": "TITLE_HEAD_KEY", "provenance_class": "INFERRED_CANDIDATE", "member_family_ids": json.dumps(fams)})
    df["dish_family_candidate_id"] = df.recipe_family_id.map(dish_of)
    # write
    def wr(name, d):
        pq.write_table(pa.Table.from_pandas(d, preserve_index=False), ID / f"{name}{suf}.parquet", compression="zstd")
    dg = df[["duplicate_group_id", "recipe_id", "source_family", "source_id", "group_representative_id", "duplicate_relation", "duplicate_status", "group_size", "group_cross_source"]].sort_values(["duplicate_group_id", "recipe_id"])
    wr("duplicate_group_members_v1", dg)
    fm = df[["recipe_family_id", "recipe_id", "duplicate_group_id", "source_family", "source_id", "family_role", "edge_confidence", "representative_recipe_id", "dish_family_candidate_id"]].assign(family_method="PROVISIONAL_STAR_V1", calibrated=False).sort_values(["recipe_family_id", "recipe_id"])
    wr("recipe_family_members_v1", fm)
    wr("dish_family_candidates_v1", pd.DataFrame(dish_rows))
    # pairs table
    pr = []
    for i, j, m, f in kept:
        pr.append({"a_recipe_id": store.id[i], "b_recipe_id": store.id[j], "candidate_source_mask": m, "relation_status": "CANDIDATE_NEAR_DUPLICATE" if not (m == 8 and not f["family_edge"]) else "EXISTING_FAMILY_ONLY", "relation_class": "UNCERTAIN", "family_edge": f["family_edge"],
                   **{k: v for k, v in f.items() if k not in ("family_edge",)}, **{k + "_missing": f.get(k) is None for k in ("title_token", "ingredient_idf", "instruction_shingle", "process_seq", "condition", "quantity_profile")}})
    pdf = pd.DataFrame(pr)
    pdf = pdf.sort_values(["score", "a_recipe_id", "b_recipe_id"], ascending=[False, True, True])
    wr("candidate_pairs_v1", pdf)
    df.to_pickle(ROOT / f"ledgers/recipe_identity/_identity_work{suf}.pkl")
    reps.drop(columns=["ing_toks", "toks_list", "toks_set", "ids_set", "cond_set", "mass_dict", "mh_steps", "mh_ing"], errors="ignore").to_pickle(ROOT / f"ledgers/recipe_identity/_reps_work{suf}.pkl")
    summary = {"recipes": n, "exact_duplicate_groups": int((df.groupby("duplicate_group_id").size() > 1).sum()), "records_in_multi_member_groups": int((df.group_size > 1).sum()), "logical_recipes_exact_dedup": int(len(reps)), "exact_stats": estats, "diagnostics": dict(diag),
               "families": len(fam_order), "multi_member_families_over_reps": int((reps.groupby("recipe_family_id").size() > 1).sum()), "dish_family_candidates": len(dish_rows), "elapsed_s": round(time.time() - t0)}
    (ROOT / f"reports/step07i/_identity_summary{suf}.json").write_text(json.dumps(summary, indent=1, default=str))
    print(json.dumps(summary, indent=1, default=str)[:3000])


if __name__ == "__main__":
    main()
