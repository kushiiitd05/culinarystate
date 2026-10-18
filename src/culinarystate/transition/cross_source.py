"""Cross-source agreement / transfer for DEL-2 (SSOT split 6: source-disjoint).

Explicit harmonisation (plan AM1 forbids silent merging): nutrient names -> NUTRIENT keys; Bognár restricted to
portion A (food edible part) to match USDA's per-food basis; cells aligned on (ingredient_id, first process step,
nutrient). Censored values enter at their lower bound and the share of censored cells is reported.
"""
from __future__ import annotations

import re

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

NUTRIENT = (  # (regex on lower-case target name, key) — first match wins
    (r"vitamin c|ascorbic", "vitamin_c"), (r"thiamin|vitamin b1\b", "vitamin_b1"), (r"riboflavin|vitamin b2", "vitamin_b2"),
    (r"niacin", "niacin"), (r"vitamin b-?6", "vitamin_b6"), (r"vitamin b-?12", "vitamin_b12"),
    (r"folate|folic|folacin", "folate"), (r"pantothenic", "pantothenic_acid"), (r"retinol|vitamin a\b", "vitamin_a"),
    (r"carot", "carotenoids"), (r"vitamin e|tocopherol", "vitamin_e"), (r"calcium", "calcium"), (r"iron", "iron"),
    (r"magnesium", "magnesium"), (r"phosph", "phosphorus"), (r"potassium", "potassium"), (r"sodium", "sodium"),
    (r"zinc", "zinc"), (r"copper", "copper"))


def nutrient_key(target: str) -> str | None:
    t = target.lower()
    return next((k for pat, k in NUTRIENT if re.search(pat, t)), None)


GROUP = (  # (regex on food_group / matrix text, coarse group); first match wins
    (r"poultry", "POULTRY"), (r"offal", "OFFAL"), (r"beef|pork|lamb|veal|game|meat", "MEAT"),
    (r"fish|shellfish|crustacean|mollus", "FISH"), (r"legume", "LEGUME"), (r"mushroom", "VEGETABLE"),
    (r"vegetable|potato", "VEGETABLE"), (r"fruit", "FRUIT"), (r"cereal|grain|pasta", "CEREAL"),
    (r"dairy|milk|egg", "DAIRY_EGG"))
STEP = {"boil": "BOIL", "simmer": "BOIL", "parboil": "BOIL", "hard-boil": "BOIL", "poach": "BOIL", "steam": "STEAM",
        "stew": "STEW", "braise": "STEW", "fry": "FRY", "pan-fry": "FRY", "deep-fry": "FRY", "stir-fry": "FRY",
        "shallow-fry": "FRY", "saute": "FRY", "brown": "FRY", "roast": "DRY_HEAT", "bake": "DRY_HEAT",
        "broil": "DRY_HEAT", "grill": "DRY_HEAT", "microwave": "MICROWAVE"}


def coarse_group(text: str) -> str | None:
    t = (text or "").lower()
    return next((g for pat, g in GROUP if re.search(pat, t)), None)


def prepare_groups(df: pd.DataFrame, evd_portion: dict | None = None) -> pd.DataFrame:
    """Level 2: (coarse food group, step family, nutrient); Bognár portion A, breaded items excluded."""
    d = df.copy()
    if evd_portion is not None:
        d = d[d.evd_id.map(lambda i: evd_portion.get(i, "FOOD_EDIBLE_PART") == "FOOD_EDIBLE_PART")]
    d = d[~d.matrix_form.str.contains("breaded", na=False)]
    d["group"] = d.food_group.map(coarse_group)
    d["step"] = d.process_family.map(STEP)
    d["nutrient"] = d.target.map(nutrient_key)
    d["y_used"] = d.y.where(~d.censored, d.y_lower)
    d = d[d.group.notna() & d.step.notna() & d.nutrient.notna() & d.y_used.notna()]
    out = d.groupby(["group", "step", "nutrient"], as_index=False).agg(
        y=("y_used", "mean"), n=("y_used", "size"), censored_share=("censored", "mean"))
    return out.rename(columns={"group": "ingredient_id"})       # same key column name as level 1


def prepare(df: pd.DataFrame, portion_a_only: bool = False, evd_portion: dict | None = None) -> pd.DataFrame:
    d = df.copy()
    if portion_a_only and evd_portion is not None:
        d = d[d.evd_id.map(lambda i: evd_portion.get(i) == "FOOD_EDIBLE_PART")]
    d["nutrient"] = d.target.map(nutrient_key)
    d["step"] = d.process_family
    d["y_used"] = d.y.where(~d.censored, d.y_lower)
    d = d[d.nutrient.notna() & d.ingredient_id.notna() & d.y_used.notna()]
    return d.groupby(["ingredient_id", "step", "nutrient"], as_index=False).agg(
        y=("y_used", "mean"), n=("y_used", "size"), censored_share=("censored", "mean"))


def agreement(a: pd.DataFrame, b: pd.DataFrame) -> dict:
    m = a.merge(b, on=["ingredient_id", "step", "nutrient"], suffixes=("_a", "_b"))
    if m.empty:
        return {"overlap_cells": 0}
    diff = (m.y_a - m.y_b).abs()
    rho = spearmanr(m.y_a, m.y_b).correlation if len(m) > 2 else None
    # transfer: predict B from (i) A's same cell, (ii) A's mean for (step, nutrient), (iii) B's own global mean
    sn = a.groupby(["step", "nutrient"]).y.mean()
    pred_sn = m.apply(lambda r: sn.get((r.step, r.nutrient), np.nan), axis=1)
    return {"overlap_cells": int(len(m)), "ingredients": int(m.ingredient_id.nunique()),
            "steps": sorted(m.step.unique().tolist()), "nutrients": int(m.nutrient.nunique()),
            "mae_same_cell": round(float(diff.mean()), 4), "median_ae": round(float(diff.median()), 4),
            "share_within_0.10": round(float((diff <= 0.10).mean()), 3), "spearman": None if rho is None else round(float(rho), 3),
            "mae_from_A_step_nutrient_mean": round(float((pred_sn - m.y_b).abs().mean()), 4),
            "mae_B_global_mean": round(float((m.y_b - b.y.mean()).abs().mean()), 4),
            "censored_share_a": round(float(m.censored_share_a.mean()), 3),
            "censored_share_b": round(float(m.censored_share_b.mean()), 3),
            "largest_disagreements": m.assign(diff=diff).sort_values("diff", ascending=False)
            .head(10)[["ingredient_id", "step", "nutrient", "y_a", "y_b"]].round(3).to_dict("records")}
