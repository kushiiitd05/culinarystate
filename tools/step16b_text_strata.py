#!/usr/bin/env python
"""Step 16b: compute the four text-regex strata flags for every row of the 16b frame, LOCALLY.

Regexes are COPIED VERBATIM from tools/make_gold_batch.py (STRATA; that script runs argparse at import, so it
cannot be imported). Text per recipe = " ".join(steps).lower() + " " + " ".join(ingredient lines).lower(), the same
construction as make_gold_batch.py. Output holds only recipe_id + Y/N/NA flags, never text.
Sources (read-only): data/external/foodcom/recipes.parquet; BBC via ../a1/A1 3/data/{processed,raw} (source_record_id ->
source_url -> raw jsonl, as make_gold_batch.py); Wikibooks data/interim/wikibooks/recipes.jsonl (pageid).
Unreadable/missing text (or no steps and no ingredient lines) -> 'NA', never 'N'.
Python: /opt/anaconda3/bin/python.  Nothing is drawn; no network.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FRAME = "registry/recipe_semantics/deep_gold_sampling_frame_v1_DRAFT.csv"
BASE = "ledgers/recipe_base/recipe_base_v1.parquet"
OUT = "registry/recipe_semantics/deep_gold_text_strata_v1_DRAFT.csv"
FOODCOM = "data/external/foodcom/recipes.parquet"
WIKI = "data/interim/wikibooks/recipes.jsonl"
A1_RAW = "../a1/A1 3/data/raw/recipes_raw.jsonl"
A1_PROC = "../a1/A1 3/data/processed/recipes_processed.jsonl"

# Verbatim from tools/make_gold_batch.py STRATA (text-regex entries only).
STRATA = {
    "reserve_split": r"\b(reserv|set aside|remaining|the rest|divide|half the)\b",
    # D-038: corrected twin of reserve_split; v1 above stays verbatim for comparability with the old pilot.
    "reserve_split_v2": r"\b(reserv\w*|set aside|remaining|the rest|divide|half the)\b",
    "drain_discard": r"\b(drain|strain|discard)\b",
    "baking": r"\b(bake|oven)\b",
    "multi_component": r"\b(for the (sauce|dressing|topping|filling|marinade))\b",
}
FLAGS = ["baking", "drain_discard", "reserve_split", "reserve_split_v2", "multi_component"]
COLUMNS = ["recipe_id"] + FLAGS


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def flags_for(steps, ings) -> dict:
    """Y/N per stratum, or all 'NA' when no text could be read (no steps and no ingredient lines)."""
    steps, ings = [str(s) for s in (steps or [])], [str(s) for s in (ings or [])]
    if not steps and not ings:
        return {k: "NA" for k in FLAGS}
    text = " ".join(steps).lower() + " " + " ".join(ings).lower()
    return {k: "Y" if re.search(STRATA[k], text) else "N" for k in FLAGS}


def _foodcom_texts(root: Path, ids: set[str]) -> dict:
    d = pd.read_parquet(root / FOODCOM, columns=["RecipeId", "RecipeIngredientQuantities", "RecipeIngredientParts",
                                                 "RecipeInstructions"])
    out = {}
    for rid, q, parts, steps in zip(d.RecipeId, d.RecipeIngredientQuantities, d.RecipeIngredientParts, d.RecipeInstructions):
        key = f"FC{int(rid)}"
        if key not in ids:
            continue
        parts = [str(x) for x in (parts if parts is not None else [])]
        q = [str(x) for x in (q if q is not None else [])]
        lines = [f"{(q[i] if i < len(q) and q[i] != 'None' else '')} {p}".strip() for i, p in enumerate(parts)]
        out[key] = ([str(x) for x in (steps if steps is not None else [])], lines)
    return out


def _bbc_texts(root: Path, recs: pd.DataFrame) -> dict:
    url_of = {}
    with (root / A1_PROC).open() as fh:
        for line in fh:
            r = json.loads(line)
            url_of[r["recipe_id"]] = r["source_url"]
    raw = {}
    with (root / A1_RAW).open() as fh:
        for line in fh:
            r = json.loads(line)
            raw.setdefault(r["source_url"], r)
    out = {}
    for rid, srec in zip(recs.recipe_id, recs.source_record_id):
        r = raw.get(url_of.get(srec))
        if r is not None:
            out[rid] = (r.get("instruction_steps_raw") or [], r.get("ingredient_phrases_raw") or [])
    return out


def _wiki_texts(root: Path, recs: pd.DataFrame) -> dict:
    pid_to_rid = {int(s.split("=", 1)[1]): rid for rid, s in zip(recs.recipe_id, recs.source_record_id)}
    out = {}
    with (root / WIKI).open() as fh:
        for line in fh:
            r = json.loads(line)
            rid = pid_to_rid.get(r.get("pageid"))
            if rid is not None and rid not in out:
                out[rid] = ([s.get("text", "") for s in r.get("steps") or []],
                            [s.get("text", "") for s in r.get("ingredients") or []])
    return out


def compute(root: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    frame = pd.read_csv(root / FRAME, usecols=["recipe_id", "source_family"], dtype=str, keep_default_na=False)
    base = pd.read_parquet(root / BASE, columns=["recipe_id", "source_record_id"])
    f = frame.merge(base, on="recipe_id", how="left", validate="1:1")
    texts = {}
    texts.update(_foodcom_texts(root, set(f.loc[f.source_family == "FOODCOM", "recipe_id"])))
    texts.update(_bbc_texts(root, f[f.source_family == "A1_BBC_GOOD_FOOD"]))
    texts.update(_wiki_texts(root, f[f.source_family == "WIKIBOOKS"]))
    rows = []
    for rid in frame.recipe_id:
        st, ing = texts.get(rid, ([], []))
        rows.append({"recipe_id": rid, **flags_for(st, ing)})
    out = pd.DataFrame(rows, columns=COLUMNS)
    return out, frame[["recipe_id", "source_family"]]


def write(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, lineterminator="\n")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    root = Path(a.root)
    out = Path(a.out) if a.out else root / OUT
    df, fr = compute(root)
    write(df, out)
    m = df.merge(fr, on="recipe_id")
    summ = {s: {k: m[m.source_family == s][k].value_counts().to_dict() for k in FLAGS} for s in sorted(m.source_family.unique())}
    print(json.dumps({"rows": len(df), "by_source": summ, "sha256": sha256_file(out)}, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
