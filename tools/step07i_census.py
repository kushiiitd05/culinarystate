#!/usr/bin/env python3
"""STEP 07I part 1: local recipe-asset census + source usage registry (read-only; no scraping).
  -> reports/step07i/local_recipe_asset_inventory.csv, registry/recipe_source_usage_registry_v1.csv, reports/step07i/census_notes.json"""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
csv.field_size_limit(10**9)
A1 = ROOT.parent / "a1" / "A1 3" / "data"
jl = lambda p: sum(1 for _ in open(p, encoding="utf-8", errors="replace"))
H = ["dataset_source_name", "path", "format", "rows", "unique_recipe_ids", "source_version", "acquisition_provenance", "raw_text_availability", "ingredient_availability", "instruction_availability", "quantity_availability", "locale_language",
     "licence_status", "redistribution_status", "step06_source_id", "asset_class", "already_in_recipe_base", "reason_if_not_included"]


def main():
    rec_lat = {}
    for l in open(ROOT / "ledgers/data/REC.jsonl", encoding="utf-8"):
        r = json.loads(l)
        rec_lat[r["id"]] = r
    fam = Counter()
    for r in rec_lat.values():
        loc = (r.get("raw_location") or "").split("#")[0]
        fam[{"data/interim/gutenberg/recipes.jsonl": "G", "data/interim/wikibooks/recipes.jsonl": "W", "../a1/A1 3/data/processed/recipes_processed.jsonl": "A"}.get(loc, "?")] += 1
    raw = [json.loads(l) for l in open(A1 / "raw/recipes_raw.jsonl", encoding="utf-8")]
    proc_urls = {json.loads(l)["source_url"] for l in open(A1 / "processed/recipes_processed.jsonl", encoding="utf-8")}
    extra = [r for r in raw if r["source_url"] not in proc_urls]
    extra_rich = [r for r in extra if len(r.get("ingredient_phrases_raw") or []) >= 3 and len(r.get("instruction_steps_raw") or []) >= 1]
    canon = Counter(r.get("canonical_url") for r in raw)
    fc = pq.ParquetFile(ROOT / "data/external/foodcom/recipes.parquet").metadata.num_rows
    ts = sum(1 for _ in csv.DictReader(open(ROOT / "data/raw/tasteset/TASTEset.csv", encoding="utf-8")))
    r3i = Counter(r["Recipe_ID"] for r in csv.DictReader(open(ROOT / "data/external/recipedb3_ner/Instructions_Annotated_Dataset.csv", encoding="utf-8")))
    gk = Counter(row[0] for row in csv.reader(open(ROOT / "data/external/recipe_knowledge_mining/gk_ingredient_phrases.csv", encoding="utf-8")))
    X = lambda *a: dict(zip(H, a))
    rows = [
        X("A1 BBC Good Food (REC-backed, processed)", "../a1/A1 3/data/processed/recipes_processed.jsonl", "jsonl", len(proc_urls), len(proc_urls), "A1 course scrape 2026-09", "a1_scraper@1.0 (BBC Good Food pages)", "yes", "yes", "yes", "yes (raw phrases)", "en-GB", "RESTRICTED (third-party copyright; SRC-000002)", "NO raw redistribution", "SRC-000002", "RECIPE_FULL", "yes", ""),
        X("A1 BBC Good Food (raw scrape)", "../a1/A1 3/data/raw/recipes_raw.jsonl", "jsonl", len(raw), len(set(r['source_url'] for r in raw)), "A1 course scrape 2026-09", "a1 scraper", "yes", "yes", "yes", "yes", "en-GB", "RESTRICTED", "NO raw redistribution", "SRC-000002", "RECIPE_FULL", "partly (11,934 of 11,983 rows)",
          f"{len(extra)} raw rows were filtered out by the A1 processing step and have no REC id ({len(extra_rich)} of them have >=3 ingredient lines and >=1 step; others are 1-ingredient pages); no REC ids minted in this step (REC immutable); listed for a later decision"),
        X("A1 raw copy in outputs", "../a1/A1 3/outputs/Q1/Q1a_raw_recipes.jsonl", "jsonl", jl(A1.parent / "outputs/Q1/Q1a_raw_recipes.jsonl"), len(raw), "A1 Q1a output", "copy of recipes_raw.jsonl", "yes", "yes", "yes", "yes", "en-GB", "RESTRICTED", "NO", "SRC-000002", "RECIPE_FULL_COPY", "no (exact copy of the raw scrape)", "duplicate artifact of the A1 raw scrape; not a separate corpus"),
        X("Wikibooks Cookbook (REC-backed)", "data/interim/wikibooks/recipes.jsonl", "jsonl", jl(ROOT / "data/interim/wikibooks/recipes.jsonl"), fam["W"], "MediaWiki API 2026-04-12 revisions", "wikibooks_api@0.1", "yes", "yes", "yes", "yes", "en", "CC BY-SA 4.0 VERIFIED (SRC-000140)", "REDISTRIBUTABLE_WITH_ATTRIBUTION (share-alike)", "SRC-000140", "RECIPE_FULL", "yes", ""),
        X("Project Gutenberg cookbook segments (REC-backed)", "data/interim/gutenberg/recipes.jsonl", "jsonl", jl(ROOT / "data/interim/gutenberg/recipes.jsonl"), fam["G"], "Gutenberg 338 cookbook titles", "old_recipes@0.1 heuristic segmentation (~80-85% precision on 30-sample)", "yes (177 REC ids have no local segment)", "mentions only (no ingredient lines)", "yes (free-text steps)", "rare", "en (historic)", "Public domain in the USA VERIFIED (SRC-000144..)", "PUBLIC_OPEN", "SRC-000144..SRC-000481", "RECIPE_SEGMENT_HEURISTIC", "yes", ""),
        X("Food.com recipes (Kaggle irkaal)", "data/external/foodcom/recipes.parquet", "parquet", fc, fc, "downloaded 2026-10-20", "kaggle CLI", "yes", "yes", "yes", "yes (no units in extract)", "en-US", "CC0 declared by uploader; authority NOT verified", "NO raw redistribution until reviewed; local/derived analysis only", "none (UNREGISTERED:FOODCOM_KAGGLE_IRKAAL)", "RECIPE_FULL", "yes", ""),
        X("TASTEset", "data/raw/tasteset/TASTEset.csv", "csv", ts, ts, "TASTEset release (local copy 2026-10-18)", "download", "ingredient lines only", "yes", "no", "yes", "en", "LICENCE_UNVERIFIED", "UNVERIFIED", "none (UNREGISTERED:TASTESET)", "RECIPE_INGREDIENT_LINES_ONLY", "yes", ""),
        X("RecipeDB3 instruction NER annotated sample", "data/external/recipedb3_ner/Instructions_Annotated_Dataset.csv", "csv", sum(r3i.values()), len(r3i), "CoSyLab RecipeDB3_NER_Research_Paper", "github download 2026-10-19", "instruction sentences only", "no", "yes (annotated sentences)", "yes (annotated)", "en", "NONE declared (LICENCE_UNVERIFIED)", "UNVERIFIED", "none", "RECIPE_FRAGMENT_NER", "no", "annotation dataset of instruction sentences with Recipe_IDs, no ingredient lines, partial recipes, licence NONE; used for NER research only; not a full-recipe corpus"),
        X("RecipeDB3 ingredient NER annotated phrases", "data/external/recipedb3_ner/Ingredient_Annotated_Dataset.csv", "csv", jl(ROOT / "data/external/recipedb3_ner/Ingredient_Annotated_Dataset.csv") - 1, "", "CoSyLab", "github download", "ingredient phrases only", "yes", "no", "yes", "en", "NONE declared", "UNVERIFIED", "none", "PHRASE_NER_DATASET", "no", "phrase-level, no recipe ids"),
        X("Recipe_NER_DL train/test/augmented", "data/external/recipe_ner_dl/*.csv", "csv", jl(ROOT / "data/external/recipe_ner_dl/final_train.csv") + jl(ROOT / "data/external/recipe_ner_dl/final_test.csv") - 2, "", "CoSyLab", "github download", "ingredient phrases only", "yes", "no", "yes", "en", "NONE declared", "UNVERIFIED", "none", "PHRASE_NER_DATASET", "no", "phrase-level, no recipe ids"),
        X("CoSyLab recipe-knowledge-mining (AllRecipes + FOOD.com phrases)", "data/external/recipe_knowledge_mining/gk_ingredient_phrases.csv", "csv", sum(gk.values()), len(gk), "CoSyLab", "github download", "ingredient phrases (recipe-id keyed)", "yes", "no", "yes", "en", "NONE declared", "UNVERIFIED", "none", "RECIPE_FRAGMENT_PHRASES", "no", "ingredient phrases of ~23k AllRecipes/FOOD.com recipes without instructions; overlaps Food.com; licence none declared; not a full-recipe corpus"),
        X("CoSyLab ar/gk tagged datasets", "data/external/recipe_knowledge_mining/*.tsv; data/external/cosylab_companion/*.tsv", "tsv", "", "", "CoSyLab", "github download", "token-tagged phrases", "yes", "no", "yes", "en", "NONE declared", "UNVERIFIED", "none", "PHRASE_NER_DATASET", "no", "tagged-token datasets, no recipe ids"),
        X("RecipeDB2 ingredient categories", "data/external/recipedb2/Category_manually_labelled.csv", "csv", 19019, "", "CoSyLab", "github download", "no", "ingredient names", "no", "no", "en", "NONE declared", "UNVERIFIED", "none", "VOCAB_ONLY", "no", "ingredient category labels, not recipes"),
        X("Legacy REC registry (A1 REC/FAM/links)", "registry/recipes/recipe_registry_v1.csv; *_ingredient_links_v1.csv; near_duplicate_pairs.csv", "csv", 11934, 11934, "derived 2026-10-18", "tools/build_recipe_registry.py", "no", "links", "no", "no", "en", "derived", "derived", "SRC-000002", "DERIVED_REGISTRY", "n/a (used as a signal: existing family_id, 7 near-duplicate pairs at word-5-shingle Jaccard>=0.8)", "existing family algorithm is a candidate signal, not a deterministic identity"),
        X("A1/A3 recipe-ingredient incidence (course outputs)", "../A3/data/Q1c_recipe_ingredient.csv; ../a1/A1 3/outputs/extensions/recipe_ingredient_incidence.npz", "csv/npz", "", "", "A1/A3 outputs", "course pipeline", "no", "ingredient sets", "no", "no", "en", "derived from A1", "derived", "SRC-000002", "DERIVED_INCIDENCE", "n/a", "derivative of the A1 corpus, no new recipes"),
        X("FlavorGraph nodes/edges (Recipe1M-derived graph)", "data/raw/flavorgraph/*.csv", "csv", "", "", "FlavorGraph 191120", "download", "no", "co-occurrence edges", "no", "no", "en", "see SRC", "graph only", "see SRC", "GRAPH_ONLY", "no", "no recipe records (graph edges only); Recipe1M+ itself NOT locally present"),
        X("OpenPI procedural states", "data/raw/openpi/*.json", "json", "", "", "OpenPI", "download", "procedures (not recipes)", "no", "yes", "no", "en", "see SRC", "see SRC", "see SRC", "PROCEDURE_NOT_RECIPE", "no", "wikiHow-style procedures, not a recipe corpus"),
    ]
    out = ROOT / "reports/step07i/local_recipe_asset_inventory.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, H)
        w.writeheader()
        w.writerows(rows)
    # ---------- usage registry ----------
    src = {}
    for l in open(ROOT / "ledgers/data/SRC.jsonl", encoding="utf-8"):
        r = json.loads(l)
        src[r["id"]] = r
    sids = {}
    for r in rec_lat.values():
        sids.setdefault(r["provenance"]["source_ids"][0], 0)
        sids[r["provenance"]["source_ids"][0]] += 1
    UH = ["source_id", "source_family", "name", "usage_class", "training_allowed", "local_analysis_allowed", "derived_statistics_allowed", "raw_redistribution_allowed", "derived_redistribution_allowed", "citation_required", "H2_required", "licence_basis", "src_licence_status", "recipes_in_base", "note"]
    ur = []
    for sid, n in sorted(sids.items()):
        s = src[sid]
        if sid == "SRC-000002":
            ur.append(dict(zip(UH, [sid, "A1_BBC_GOOD_FOOD", s["title"][:70], "LOCAL_RESEARCH_ONLY", "UNKNOWN", "YES", "YES", "NO", "UNKNOWN", "YES", "YES", s.get("licence"), s.get("licence_status"), n, "third-party copyright; scraped; training/redistribution need H2"])))
        elif sid == "SRC-000140":
            ur.append(dict(zip(UH, [sid, "WIKIBOOKS", s["title"][:70], "REDISTRIBUTABLE_WITH_ATTRIBUTION", "CONDITIONAL", "YES", "YES", "CONDITIONAL", "CONDITIONAL", "YES", "YES", s.get("licence"), s.get("licence_status"), n, "CC BY-SA: attribution + share-alike obligations; training/release use needs H2 review"])))
        else:
            ur.append(dict(zip(UH, [sid, "GUTENBERG_SEGMENT", s["title"][:70], "PUBLIC_OPEN", "YES", "YES", "YES", "YES", "YES", "NO", "NO", s.get("licence"), s.get("licence_status"), n, "public domain in the USA per Project Gutenberg licence (non-US status not assessed); segmentation is heuristic"])))
    ur.append(dict(zip(UH, ["UNREGISTERED:FOODCOM_KAGGLE_IRKAAL", "FOODCOM", "Food.com recipes (Kaggle irkaal)", "LICENCE_UNVERIFIED", "UNKNOWN", "YES", "YES", "NO", "UNKNOWN", "YES", "YES", "CC0 declared by uploader; authority not verified", "NO_SRC_ROW", fc, "keep local/derived; no text redistribution until H2; SRC registration pending (not invented)"])))
    ur.append(dict(zip(UH, ["UNREGISTERED:TASTESET", "TASTESET", "TASTEset", "LICENCE_UNVERIFIED", "UNKNOWN", "YES", "YES", "NO", "UNKNOWN", "YES", "YES", "licence not verified", "NO_SRC_ROW", ts, "keep local; SRC registration pending (not invented)"])))
    with open(ROOT / "registry/recipe_source_usage_registry_v1.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, UH)
        w.writeheader()
        w.writerows(ur)
    notes = {"rec_unique_ids": len(rec_lat), "a1_raw_rows": len(raw), "a1_raw_not_in_processed": len(extra), "a1_raw_extra_with_3plus_ingredients_and_steps": len(extra_rich), "a1_canonical_url_duplicate_pairs": sum(1 for v in canon.values() if v > 1),
             "usage_registry_rows": len(ur), "usage_class_counts": dict(Counter(r["usage_class"] for r in ur)), "recipes_by_usage_class": dict(Counter({c: sum(r["recipes_in_base"] for r in ur if r["usage_class"] == c) for c in set(r["usage_class"] for r in ur)})),
             "newly_discovered_full_recipe_corpora": 0, "newly_discovered_fragment_datasets": 5}
    (ROOT / "reports/step07i/census_notes.json").write_text(json.dumps(notes, indent=1))
    print(json.dumps(notes, indent=1))


main()
