#!/usr/bin/env python3
"""STEP 07H-R preflight: read-only inventory of every local recipe-related artifact (no assumption that REC==107,760).
  python tools/recipe_preflight.py -> reports/step07/recipe_corpus_preflight_inventory.json"""
import csv
import hashlib
import json
import glob
from collections import Counter, defaultdict
from pathlib import Path

import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
A1 = ROOT.parent / "a1" / "A1 3" / "data" / "processed"
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    rec = defaultdict(lambda: Counter())
    lat, lines, status = {}, 0, Counter()
    for line in open(ROOT / "ledgers/data/REC.jsonl", encoding="utf-8"):
        r = json.loads(line)
        lines += 1
        lat[r["id"]] = r  # append-only ledger: latest version per id
    ver_hist = Counter()
    for line in open(ROOT / "ledgers/data/REC.jsonl", encoding="utf-8"):
        ver_hist[json.loads(line)["version"]] += 1
    fam = Counter()
    ids = set(lat)
    for r in lat.values():
        status[r["status"]] += 1
        if r["status"] != "ACTIVE":
            continue
        loc = (r.get("raw_location") or "").split("#")[0]
        key = {"data/interim/gutenberg/recipes.jsonl": "GUTENBERG_SEGMENTS", "data/interim/wikibooks/recipes.jsonl": "WIKIBOOKS", "../a1/A1 3/data/processed/recipes_processed.jsonl": "A1_BBC_GOOD_FOOD"}.get(loc, "OTHER:" + loc)
        c = rec[key]
        c["recipes"] += 1
        c["with_ingredient_lines"] += r["n_ingredient_lines"] > 0
        c["with_steps"] += r["n_steps"] > 0
        c["n_distinct_source_ids"] += 0
        fam[r["family_id"]] += 1
    dup_ids = lines - len(ids)
    famsz = Counter(fam.values())
    fc = pq.ParquetFile(ROOT / "data/external/foodcom/recipes.parquet")
    tas = list(csv.DictReader(open(ROOT / "data/raw/tasteset/TASTEset.csv", encoding="utf-8")))
    gold = {}
    for name, pat in {"pilot_20_adjudicated(A1 ids)": "annotation/gold/pilot_20_adjudicated/*.json", "pilot_20_adjudicated_v1_1": "annotation/gold/pilot_20_adjudicated_v1_1/*.json", "foodcom_ai_assisted_Kush": "annotation/gold/foodcom_ai_assisted/Kush/*.json",
                      "foodcom_ai_assisted_Parv": "annotation/gold/foodcom_ai_assisted/Parv/*.json", "evidence_first_expansion_Kush_all": "annotation/gold/evidence_first_expansion/Kush_all_20.json"}.items():
        gold[name] = len(glob.glob(str(ROOT / pat)))
    out = {"rec_ledger": {"history_lines": lines, "unique_recipe_ids_latest": len(ids), "extra_version_lines": dup_ids, "version_histogram_lines": dict(ver_hist), "latest_status_counts": dict(status), "by_source_corpus": {k: dict(v) for k, v in rec.items()}, "families": {"unique_family_ids": len(fam), "family_size_distribution": dict(sorted(famsz.items())[:8]), "largest": fam.most_common(3)},
                         "field_family_id_present": True, "note": "REC.family_id exists on every row; no standalone FAM ledger file in ledgers/data"},
           "a1_processed": {"recipes": sum(1 for _ in open(A1 / "recipes_processed.jsonl", encoding="utf-8")), "instruction_events_rows": sum(1 for _ in open(A1 / "instruction_events.jsonl", encoding="utf-8")), "ingredient_mentions_rows": sum(1 for _ in open(A1 / "ingredient_mentions.csv", encoding="utf-8")) - 1,
                            "sha256_recipes_processed": sha(A1 / "recipes_processed.jsonl")},
           "foodcom_local_parquet": {"path": "data/external/foodcom/recipes.parquet", "rows": fc.metadata.num_rows, "in_REC": False, "licence": "CC0 declared by Kaggle uploader; authority NOT verified; local/derived use only", "sha256": json.load(open(ROOT / "data/external/foodcom/PROVENANCE.json"))["files"]["recipes.parquet"]},
           "tasteset": {"path": "data/raw/tasteset/TASTEset.csv", "recipes": len(tas), "in_REC": False, "annotation": "third-party human NER entity spans (ingredient-line level)"},
           "recipe1m_plus": {"locally_present": bool(glob.glob(str(ROOT / "data/**/*ecipe1M*"), recursive=True))}, "recipedb": {"locally_present_as_recipe_corpus": False, "note": "only referenced via ING crosswalk fields / RECIPEDB2 KGE edges (964), no recipe text"},
           "gold_annotation_file_counts": gold, "existing_annotation_artifacts": {"A1_ingredient_mentions_csv": "NER+rule extraction on 11,934 A1 recipes (course project, AI/model-produced, not human-verified)", "A1_instruction_events_jsonl": "rule-based action/utensil/duration/temperature per step (course project)",
                                                                                "foodcom_ai_assisted_gold": "AI-assisted event/state annotation, Kush/Parv labels not independently produced -> GOLD_PENDING_INDEPENDENT_IAA", "pilot_20_adjudicated": "20 A1 recipes adjudicated Kush+Parv (v1, v1.1)",
                                                                                "final_link_set/fresh_linker_set": "linker evaluation gold (ingredient spans); SEALED test sets - not recipe-level gold, never used for tuning"},
           "evt_state_ledgers": {"EVT_exists": (ROOT / "ledgers/data/EVT.jsonl").exists(), "STATE_exists": (ROOT / "ledgers/data/STATE.jsonl").exists(), "RXN_exists": (ROOT / "ledgers/data/RXN.jsonl").exists()},
           "disk_note": "derived parquet outputs are local, git-ignored (REC text is third-party); manifests/hashes are committed"}
    (ROOT / "reports/step07/recipe_corpus_preflight_inventory.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
    print(json.dumps(out, indent=1, ensure_ascii=False)[:3500])


main()
