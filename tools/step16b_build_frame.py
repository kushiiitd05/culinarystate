#!/usr/bin/env python
"""Step 16b: build the Deep-Gold sampling FRAME (candidates only; nothing is drawn).

Reads (read-only): recipe_base_v1, recipe_identity_fk_v1, recipe_identity_features_v1
(title_key is used ONLY as a hash-equality edge, never emitted), gold_recipe_index_v1,
the id column of the S116 screening log, and the source usage registry.
Writes one text-free CSV of ids, structural counts and group ids.
Python: /opt/anaconda3/bin/python.  Design: reports/step16/deep_gold_frame_preregistration_v1_DRAFT.md
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

ROOT = Path(__file__).resolve().parents[1]
BASE = "ledgers/recipe_base/recipe_base_v1.parquet"
FK = "ledgers/recipe_identity/recipe_identity_fk_v1.parquet"
FEAT = "ledgers/recipe_identity/recipe_identity_features_v1.parquet"
GOLD = "ledgers/recipe_base/gold_recipe_index_v1.parquet"
POOL = "annotation/gold/evidence_first_expansion/screening_log.csv"
USAGE = "registry/recipe_source_usage_registry_v1.csv"
OUT = "registry/recipe_semantics/deep_gold_sampling_frame_v1_DRAFT.csv"

# Pre-registered design parameters (Step 19 draft THR-19P-02/-06; not tuned to outcomes).
ELIGIBLE_SOURCES = ("A1_BBC_GOOD_FOOD", "FOODCOM", "WIKIBOOKS")
ING_RANGE, STEP_RANGE = (4, 20), (2, 15)
TIER_LOW_MAX, TIER_MID_MAX = 14, 24
SIMPLE_MAX_STEPS, SIMPLE_MAX_LINES = 3, 6
INDIAN_TOKENS = {"indian", "south indian", "indic"}
COLUMNS = [
    "recipe_id", "source_family", "source_id", "usage_class", "n_ingredient_lines", "n_steps",
    "complexity_c", "complexity_tier", "stratum_simple", "stratum_indian", "stratum_random",
    "text_regex_strata_status", "split_group_id", "group_id", "group_basis", "group_size",
    "duplicate_group_id", "recipe_family_id", "dish_family_candidate_id",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fallback_components(recipe_ids: pd.Series, keys: dict[str, pd.Series]) -> np.ndarray:
    """Connected components of recipes linked by any shared non-null key (bipartite graph)."""
    n = len(recipe_ids)
    rows, cols, offset = [], [], n
    for series in keys.values():
        codes, uniques = pd.factorize(series, sort=False)
        ok = codes >= 0
        rows.append(np.flatnonzero(ok))
        cols.append(codes[ok] + offset)
        offset += len(uniques)
    r, c = np.concatenate(rows), np.concatenate(cols)
    g = coo_matrix((np.ones(len(r), dtype=np.int8), (r, c)), shape=(offset, offset))
    _, labels = connected_components(g, directed=False)
    return labels[:n]


def is_indian(label) -> bool:
    if label is None or (isinstance(label, float) and np.isnan(label)):
        return False
    return any(t.strip().lower() in INDIAN_TOKENS for t in re.split(r"[|,]", str(label)))


def build_frame(root: Path) -> tuple[pd.DataFrame, dict]:
    base = pd.read_parquet(root / BASE, columns=[
        "recipe_id", "source_id", "source_family", "cuisine_if_explicit", "has_ingredients",
        "has_instructions", "n_ingredient_lines", "n_steps"])
    fk = pd.read_parquet(root / FK, columns=[
        "recipe_id", "duplicate_group_id", "recipe_family_id", "dish_family_candidate_id",
        "representative_recipe_id"])
    feat = pd.read_parquet(root / FEAT, columns=["recipe_id", "title_key"])
    df = base.merge(fk, on="recipe_id", how="left", validate="1:1").merge(
        feat, on="recipe_id", how="left", validate="1:1")
    df = df.sort_values("recipe_id", kind="mergesort").reset_index(drop=True)
    title = df["title_key"].where(df["title_key"].fillna("") != "")
    df["comp"] = fallback_components(df["recipe_id"], {
        "dup": df["duplicate_group_id"], "fam": df["recipe_family_id"],
        "dish": df["dish_family_candidate_id"], "title": title})
    size = df.groupby("comp")["recipe_id"].transform("size")
    first = df.groupby("comp")["recipe_id"].transform("min")
    df["group_id"] = "FBG-" + first
    df["group_size"] = size

    gold = pd.read_parquet(root / GOLD, columns=["recipe_id"])["recipe_id"]
    pool = pd.read_csv(root / POOL, usecols=["source_recipe_id"])["source_recipe_id"]
    excl_ids = set(gold) | set(pool)
    excl_comp = set(df.loc[df["recipe_id"].isin(excl_ids), "comp"])
    stats = {"base_rows": len(df), "excluded_seed_ids": len(excl_ids),
             "excluded_seed_ids_in_base": int(df["recipe_id"].isin(excl_ids).sum()),
             "excluded_components": len(excl_comp),
             "max_component_size": int(size.max())}

    lo, hi = ING_RANGE; slo, shi = STEP_RANGE
    steps = [
        ("source", df["source_family"].isin(ELIGIBLE_SOURCES)),
        ("has_ingredients_and_instructions", df["has_ingredients"] & df["has_instructions"]),
        ("exact_dup_representative", df["recipe_id"] == df["representative_recipe_id"]),
        ("ingredient_lines_4_20", df["n_ingredient_lines"].between(lo, hi)),
        ("steps_2_15", df["n_steps"].between(slo, shi)),
        ("not_in_excluded_group", ~df["comp"].isin(excl_comp)),
    ]
    mask = pd.Series(True, index=df.index)
    funnel = {}
    for name, m in steps:
        mask &= m
        funnel[name] = int(mask.sum())
    stats["funnel"] = funnel
    f = df[mask].copy()

    f["complexity_c"] = f["n_ingredient_lines"] + 2 * f["n_steps"]
    f["complexity_tier"] = np.where(f["complexity_c"] <= TIER_LOW_MAX, "LOW",
                                    np.where(f["complexity_c"] <= TIER_MID_MAX, "MID", "HIGH"))
    f["stratum_simple"] = (f["n_steps"] <= SIMPLE_MAX_STEPS) & (f["n_ingredient_lines"] <= SIMPLE_MAX_LINES)
    f["stratum_indian"] = f["cuisine_if_explicit"].map(is_indian)
    f["stratum_random"] = True
    f["text_regex_strata_status"] = "NOT_COMPUTED_TEXT_NOT_READ"
    f["split_group_id"] = ""  # 07I-C recipe_split_groups_v1 does not exist: no value invented
    f["group_basis"] = "FALLBACK_COMPONENT_V1"
    usage = pd.read_csv(root / USAGE, usecols=["source_id", "usage_class"])
    f = f.merge(usage, on="source_id", how="left", validate="m:1")
    f["usage_class"] = f["usage_class"].fillna("UNKNOWN")
    out = f[COLUMNS].sort_values("recipe_id", kind="mergesort").reset_index(drop=True)
    for col in ("stratum_simple", "stratum_indian", "stratum_random"):
        out[col] = out[col].map({True: "Y", False: "N"})
    return out, stats


def write_frame(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.fillna("").to_csv(path, index=False, lineterminator="\n")


def summarise(df: pd.DataFrame) -> dict:
    return {
        "rows": len(df),
        "by_source": df["source_family"].value_counts().sort_index().to_dict(),
        "by_source_tier": {f"{s}|{t}": int(n) for (s, t), n in df.groupby(["source_family", "complexity_tier"]).size().items()},
        "simple": df[df.stratum_simple == "Y"]["source_family"].value_counts().sort_index().to_dict(),
        "indian": df[df.stratum_indian == "Y"]["source_family"].value_counts().sort_index().to_dict(),
        "group_basis": df["group_basis"].value_counts().to_dict(),
        "fallback_rows": int((df["group_basis"] == "FALLBACK_COMPONENT_V1").sum()),
        "distinct_groups": int(df["group_id"].nunique()),
        "max_group_size_full_base": int(df["group_size"].max()),
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    root = Path(a.root)
    out = Path(a.out) if a.out else root / OUT
    df, stats = build_frame(root)
    write_frame(df, out)
    print(json.dumps({"build": stats, "frame": summarise(df), "sha256": sha256_file(out)}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
