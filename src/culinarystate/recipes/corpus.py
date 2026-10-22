"""STEP 07H-R: iterate every locally present recipe corpus as a uniform record. Read-only; text is never copied into ledgers (pointers + hashes only).

Record: {recipe_id, source_family, source_record_id, source_id, title, ingredient_lines[list[str]], steps[list[str]], structured_times{field:str}, pointer, extra}
REC-backed corpora (A1/BBC, Wikibooks, Gutenberg segments) use the LATEST version per REC id. Food.com (local parquet, not in REC) and TASTEset (not in REC) are indexed members with their own id schemes.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
A1_DIR = ROOT.parent / "a1" / "A1 3" / "data" / "processed"
FOODCOM = ROOT / "data/external/foodcom/recipes.parquet"
TASTESET = ROOT / "data/raw/tasteset/TASTEset.csv"
SOURCE_FAMILIES = ("A1_BBC_GOOD_FOOD", "WIKIBOOKS", "GUTENBERG_SEGMENT", "FOODCOM", "TASTESET")


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def rec_latest() -> dict:
    out = {}
    for line in open(ROOT / "ledgers/data/REC.jsonl", encoding="utf-8"):
        if line.strip():
            r = json.loads(line)
            out[r["id"]] = r
    return out


def family_of(rec: dict) -> str:
    loc = (rec.get("raw_location") or "").split("#")[0]
    return {"data/interim/gutenberg/recipes.jsonl": "GUTENBERG_SEGMENT", "data/interim/wikibooks/recipes.jsonl": "WIKIBOOKS", "../a1/A1 3/data/processed/recipes_processed.jsonl": "A1_BBC_GOOD_FOOD"}.get(loc, "UNKNOWN")


def _ext(rec: dict, prefix: str):
    for e in rec.get("external_refs") or []:
        if e.startswith(prefix + ":"):
            return e.split(":", 1)[1]
    return None


def iter_rec_corpora(rec: dict | None = None, families=("A1_BBC_GOOD_FOOD", "WIKIBOOKS", "GUTENBERG_SEGMENT")):
    rec = rec or rec_latest()
    by_fam = {f: {} for f in SOURCE_FAMILIES}
    for r in rec.values():
        by_fam[family_of(r)] [r["id"]] = r
    if "A1_BBC_GOOD_FOOD" in families:
        idx = {_ext(r, "A1"): r for r in by_fam["A1_BBC_GOOD_FOOD"].values()}
        for line in open(A1_DIR / "recipes_processed.jsonl", encoding="utf-8"):
            a = json.loads(line)
            r = idx.get(a["recipe_id"])
            if r is None:
                continue
            yield {"recipe_id": r["id"], "source_family": "A1_BBC_GOOD_FOOD", "source_record_id": a["recipe_id"], "source_id": r["provenance"]["source_ids"][0], "title": a.get("title"), "ingredient_lines": list(a.get("ingredient_phrases_raw") or []),
                   "steps": list(a.get("instruction_steps_raw") or []), "structured_times": {"total_time_raw": a.get("total_time_raw")}, "pointer": r["raw_location"], "rec": r, "extra": {"mentions": a.get("mentions") or [], "cuisine": r.get("cuisine")}}
    if "WIKIBOOKS" in families:
        idx = {(_ext(r, "WIKIBOOKS") or "").split(":")[0]: r for r in by_fam["WIKIBOOKS"].values()}
        for line in open(ROOT / "data/interim/wikibooks/recipes.jsonl", encoding="utf-8"):
            w = json.loads(line)
            r = idx.get(str(w["pageid"]))
            if r is None:
                continue
            yield {"recipe_id": r["id"], "source_family": "WIKIBOOKS", "source_record_id": f"pageid={w['pageid']}", "source_id": r["provenance"]["source_ids"][0], "title": w.get("title"), "ingredient_lines": [i["text"] for i in w.get("ingredients") or []],
                   "steps": [s["text"] for s in w.get("steps") or []], "structured_times": {}, "pointer": r["raw_location"], "rec": r, "extra": {"equipment": [e for s in w.get("steps") or [] for e in (s.get("equipment") or [])], "cuisine": r.get("cuisine")}}
    if "GUTENBERG_SEGMENT" in families:
        seen_g = set()
        gidx = {_ext(r, "GUTENBERG"): r for r in by_fam["GUTENBERG_SEGMENT"].values()}  # key 'book:idx' (the jsonl rec_id is not reliable for every segment)
        for line in open(ROOT / "data/interim/gutenberg/recipes.jsonl", encoding="utf-8"):
            g = json.loads(line)
            r = gidx.get(f"{g['book_id']}:{g['idx']}") or rec.get(g.get("rec_id"))
            if r is None:
                continue
            seen_g.add(r["id"])
            yield {"recipe_id": r["id"], "source_family": "GUTENBERG_SEGMENT", "source_record_id": f"G{g['book_id']}_{g['idx']}", "source_id": r["provenance"]["source_ids"][0], "title": g.get("title"), "ingredient_lines": [],
                   "steps": list(g.get("steps") or []), "structured_times": {}, "pointer": r["raw_location"], "rec": r, "extra": {"legacy_ing_ids": g.get("ing_ids") or [], "legacy_processes": g.get("processes") or [], "cuisine": g.get("cuisine")}}
        yield from _gutenberg_stubs(by_fam["GUTENBERG_SEGMENT"], seen_g)


def _gutenberg_stubs(rec_by_fam, seen):
    """REC rows whose raw segment text is NOT present in the local interim file: kept as base members flagged RAW_SEGMENT_MISSING_LOCALLY (no text, no expressions)"""
    for r in rec_by_fam.values():
        if r["id"] not in seen:
            yield {"recipe_id": r["id"], "source_family": "GUTENBERG_SEGMENT", "source_record_id": (r.get("raw_location") or "").split("#")[-1], "source_id": r["provenance"]["source_ids"][0], "title": r.get("title"), "ingredient_lines": [], "steps": [],
                   "structured_times": {}, "pointer": r["raw_location"], "rec": r, "extra": {"raw_segment_missing": True, "legacy_ing_ids": [], "cuisine": r.get("cuisine")}}


def iter_foodcom(batch_size=2000, limit=None):
    import pyarrow.parquet as pq
    pf = pq.ParquetFile(FOODCOM)
    n = 0
    for b in pf.iter_batches(batch_size=batch_size, columns=["RecipeId", "Name", "PrepTime", "CookTime", "TotalTime", "RecipeIngredientQuantities", "RecipeIngredientParts", "RecipeInstructions", "RecipeCategory"]):
        for row in b.to_pylist():
            rid = int(row["RecipeId"])
            q, p = row["RecipeIngredientQuantities"] or [], row["RecipeIngredientParts"] or []
            lines = [f"{(q[i] if i < len(q) and q[i] else '')} {p[i]}".strip() for i in range(len(p))]
            yield {"recipe_id": f"FC{rid}", "source_family": "FOODCOM", "source_record_id": str(rid), "source_id": "UNREGISTERED:FOODCOM_KAGGLE_IRKAAL", "title": row["Name"], "ingredient_lines": lines, "steps": list(row["RecipeInstructions"] or []),
                   "structured_times": {"prep_time": row["PrepTime"], "cook_time": row["CookTime"], "total_time": row["TotalTime"]}, "pointer": f"data/external/foodcom/recipes.parquet#RecipeId={rid}", "rec": None, "extra": {"category": row["RecipeCategory"], "ingredient_parts": list(p), "ingredient_quantities": [(q[i] if i < len(q) else None) for i in range(len(p))]}}
            n += 1
            if limit and n >= limit:
                return


def iter_tasteset():
    for i, r in enumerate(csv.DictReader(open(TASTESET, encoding="utf-8")), 1):
        lines = [x for x in (r["ingredients"] or "").split("\n") if x.strip()]
        yield {"recipe_id": f"TS{i:04d}", "source_family": "TASTESET", "source_record_id": str(i), "source_id": "UNREGISTERED:TASTESET", "title": None, "ingredient_lines": lines, "steps": [], "structured_times": {}, "pointer": f"data/raw/tasteset/TASTEset.csv#row={i}", "rec": None, "extra": {"entities_json": r["ingredients_entities"]}}


def raw_hash(rec: dict) -> str:
    """hash of the recipe's text fields in a canonical order (does not depend on the pointer)"""
    return sha256_text(json.dumps([rec["title"], rec["ingredient_lines"], rec["steps"], rec["structured_times"]], ensure_ascii=False, sort_keys=True))
