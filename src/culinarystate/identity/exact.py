"""STEP 07I-R phase `exact`: deterministic duplicate groups (Level A) and group representatives, computed BEFORE any pair scoring.
Rules are the pre-registered ones (reports/step07i/preregistration_v1.md section 1/6). Members are never deleted. Only scalar/hash columns are read (no list columns)."""
from __future__ import annotations

import csv
import json
import zlib
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

REL_RANK = {"EXACT_BINARY_COPY": 3, "MIRRORED_COPY": 2, "EXACT_NORMALIZED_COPY": 1}
REL_NAME = {3: "EXACT_BINARY_COPY", 2: "MIRRORED_COPY", 1: "EXACT_NORMALIZED_COPY", 0: "NONE"}
TIER_RANK = {"GOLD_PENDING_INDEPENDENT_IAA": 3, "SILVER_AUTO": 2, "SOURCE_RAW": 1}
USAGE_RANK = {"PUBLIC_OPEN": 5, "REDISTRIBUTABLE_WITH_ATTRIBUTION": 4, "LOCAL_RESEARCH_ONLY": 3, "LICENCE_UNVERIFIED": 2, "UNKNOWN": 1}
FEAT_SCALAR = ["recipe_id", "source_family", "norm_text_hash", "raw_hash", "rec_content_sha256", "n_chars", "n_ing_lines", "n_steps", "existing_family_id"]
BASE_COLS = ["recipe_id", "source_id", "source_record_id", "locale", "cuisine_if_explicit", "quality_tier", "has_instructions", "has_ingredients", "has_quantities", "has_conditions",
             "has_gold_annotations", "recipe_family_id", "raw_recipe_pointer"]


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


def sample_mask(ids, sample: int):
    return np.array([zlib.crc32(r.encode()) % sample == 0 for r in ids]) if sample else np.ones(len(ids), dtype=bool)


def load_frame(feat_path, base_path, usage_csv, a1_jsonl=None, sample: int = 0) -> pd.DataFrame:
    feat = pq.read_table(feat_path, columns=FEAT_SCALAR).to_pandas()
    base = pq.read_table(base_path, columns=BASE_COLS).to_pandas().rename(columns={"recipe_family_id": "legacy_family_id"})
    if sample:
        keep = sample_mask(feat.recipe_id.tolist(), sample)
        feat = feat[keep].reset_index(drop=True)
        base = base[base.recipe_id.isin(set(feat.recipe_id))].reset_index(drop=True)
    df = feat.merge(base, on="recipe_id", how="left", validate="1:1")
    usage = {r["source_id"]: r["usage_class"] for r in csv.DictReader(open(usage_csv, encoding="utf-8"))}
    df["usage_class"] = df.source_id.map(lambda s: usage.get(s, "UNKNOWN"))
    df["canonical_url"] = None
    if a1_jsonl and Path(a1_jsonl).exists():
        a1 = {}
        for l in open(a1_jsonl, encoding="utf-8"):
            r = json.loads(l)
            a1[r["recipe_id"]] = r.get("canonical_url")
        df["canonical_url"] = [a1.get(s) if f == "A1_BBC_GOOD_FOOD" else None for s, f in zip(df.source_record_id, df.source_family)]
    return df.sort_values("recipe_id", kind="stable").reset_index(drop=True)


def exact_groups(df: pd.DataFrame):
    n = len(df)
    valid = ((df.n_chars >= 60) & ((df.n_ing_lines + df.n_steps) > 0)).to_numpy()
    uf = UF(n)
    edge_rel = np.zeros(n, dtype=np.int8)  # best relation rank among incident deterministic edges
    stats = {}
    for key, rel in (("raw_hash", "EXACT_BINARY_COPY"), ("rec_content_sha256", "EXACT_BINARY_COPY"), ("canonical_url", "MIRRORED_COPY"), ("norm_text_hash", "EXACT_NORMALIZED_COPY")):
        col = df[key]
        m = col.notna().to_numpy() if key == "canonical_url" else (valid & col.notna().to_numpy())
        idx = np.nonzero(m)[0]
        g = pd.DataFrame({"k": col.to_numpy()[idx], "i": idx}).groupby("k").i.apply(list)
        g = g[g.map(len) > 1]
        members = 0
        for lst in g:
            members += len(lst)
            for a in lst[1:]:
                uf.union(lst[0], a)
            edge_rel[lst] = np.maximum(edge_rel[lst], REL_RANK[rel])
        stats[rel + "|" + key] = {"groups": int(len(g)), "records": int(members)}
    root = np.array([uf.find(i) for i in range(n)])
    return root, edge_rel, stats


def build_exact(df: pd.DataFrame):
    """returns (per-recipe table, stats). df must be sorted by recipe_id (load_frame does)."""
    n = len(df)
    root, edge_rel, stats = exact_groups(df)
    out = df[["recipe_id", "source_family", "source_id", "usage_class", "quality_tier", "legacy_family_id", "existing_family_id", "locale", "cuisine_if_explicit"]].copy()
    first = pd.Series(np.arange(n)).groupby(root).min()  # recipe_ids are sorted, so first index = min recipe_id
    order = first.sort_values()  # root -> first idx; sorted by min recipe_id
    gid_of_root = {r: "DG-%08d" % (k + 1) for k, r in enumerate(order.index[np.argsort(order.to_numpy(), kind="stable")])}
    out["duplicate_group_id"] = [gid_of_root[r] for r in root]
    comp = df.has_instructions.astype(int) + df.has_ingredients.astype(int) + df.has_quantities.astype(int) + df.has_conditions.astype(int)
    rk = pd.DataFrame({"g": out.duplicate_group_id.to_numpy(), "tier": df.quality_tier.map(TIER_RANK).fillna(0).to_numpy(), "usage": df.usage_class.map(USAGE_RANK).fillna(0).to_numpy(),
                       "comp": comp.to_numpy(), "ning": df.n_ing_lines.clip(upper=30).to_numpy(), "nst": df.n_steps.clip(upper=30).to_numpy(), "rid": df.recipe_id.to_numpy()})
    best = rk.sort_values(["g", "tier", "usage", "comp", "ning", "nst", "rid"], ascending=[True, False, False, False, False, False, True], kind="stable").groupby("g").head(1)
    rep_of = dict(zip(best.g, best.rid))
    out["group_representative_id"] = out.duplicate_group_id.map(rep_of)
    out["group_size"] = out.groupby("duplicate_group_id").recipe_id.transform("size")
    out["group_cross_source"] = out.groupby("duplicate_group_id").source_family.transform("nunique") > 1
    rel = np.array([REL_NAME[int(x)] for x in edge_rel])
    out["duplicate_relation"] = np.where(out.group_size == 1, "NONE", np.where(out.recipe_id == out.group_representative_id, "REPRESENTATIVE", rel))
    out["duplicate_status"] = np.where(out.group_size == 1, "SINGLETON", "DETERMINISTIC_EXACT")
    return out, stats
