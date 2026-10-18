#!/usr/bin/env python3
"""REC- ledger (11,934 A1 BBC recipes): metadata + content hash + near-duplicate family. Raw text stays local.

  /opt/anaconda3/bin/python tools/build_recipe_registry.py
"""
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.ingest.recipe_families import families  # noqa: E402
from culinarystate.ledgers.store import LedgerStore  # noqa: E402

PROC = ROOT.parent / "a1" / "A1 3" / "data" / "processed" / "recipes_processed.jsonl"
recs = [json.loads(line) for line in PROC.open()]
docs = {r["recipe_id"]: " ".join(r.get("instruction_steps_raw") or []) for r in recs}
fam, pairs = families(docs)

st = LedgerStore()
src_id = st.ids.mint("SRC", key="a1:bbcgoodfood:ingredient_mentions")
counts = Counter()
rows = []
for r in recs:
    content = json.dumps({"title": r["title"], "ingredients": r.get("ingredient_phrases_raw") or [],
                          "steps": r.get("instruction_steps_raw") or []}, ensure_ascii=False, sort_keys=True)
    sha = hashlib.sha256(content.encode()).hexdigest()
    rid = st.ids.mint("REC", key=f"bbcgf:{r['recipe_id']}")
    rec = {"id": rid, "record_type": "REC", "status": "ACTIVE", "created_by": "Kush+Claude",
           "provenance": {"method": "SCRAPE", "source_ids": [src_id], "agent": "a1_scraper@1.0",
                          "locator": r["source_url"]},
           "verification": {"status": "UNVERIFIED"}, "title": r["title"], "source_url": r["source_url"],
           "content_sha256": sha, "family_id": fam[r["recipe_id"]], "cuisine": r.get("cuisine_raw") or None,
           "n_ingredient_lines": int(r.get("n_ingredient_phrases") or 0), "n_steps": int(r.get("n_instruction_steps") or 0),
           "raw_location": f"../a1/A1 3/data/processed/recipes_processed.jsonl#{r['recipe_id']}",
           "external_refs": [f"A1:{r['recipe_id']}"]}
    counts[st.upsert(rec)[0]] += 1
    rows.append({"rec_id": rid, "a1_recipe_id": r["recipe_id"], "family_id": fam[r["recipe_id"]],
                 "cuisine": rec["cuisine"], "n_ingredient_lines": rec["n_ingredient_lines"], "n_steps": rec["n_steps"]})
df = pd.DataFrame(rows)
out = ROOT / "registry" / "recipes"
out.mkdir(parents=True, exist_ok=True)
df.to_csv(out / "recipe_registry_v1.csv", index=False)
pd.DataFrame(pairs, columns=["a1_a", "a1_b", "jaccard"]).to_csv(out / "near_duplicate_pairs.csv", index=False)
fsize = df["family_id"].value_counts()
lines = ["# Recipe registry v1 (REC)", "", f"- recipes: {len(df):,}; ledger writes {dict(counts)}",
         f"- near-duplicate pairs (word-5-shingle Jaccard ≥ 0.8): {len(pairs):,}",
         f"- families with >1 recipe: {(fsize > 1).sum():,} covering {fsize[fsize > 1].sum():,} recipes; largest {fsize.iloc[0]}",
         f"- cuisines (top): {df['cuisine'].value_counts().head(10).to_dict()}",
         f"- steps per recipe median {df['n_steps'].median():.0f}; ingredient lines median {df['n_ingredient_lines'].median():.0f}",
         "- raw text local only (D-003); REC holds metadata + sha256 + family for leakage-safe splits"]
(ROOT / "reports" / "recipe_registry_v1.md").write_text("\n".join(lines) + "\n")
print("\n".join(lines))

# recipe -> ingredient concept links (REC ↔ ING), from A1 mentions
ment = pd.read_csv(ROOT.parent / "a1" / "A1 3" / "data" / "processed" / "ingredient_mentions.csv",
                   usecols=["recipe_id", "ingredient_index", "ingredient_canonical", "is_primary_alternative"])
ing = {r["canonical_name"]: r["id"] for r in st.all_latest("ING") if r["status"] == "ACTIVE"}
rec_id = dict(zip(df["a1_recipe_id"], df["rec_id"]))
ment["rec_id"] = ment["recipe_id"].map(rec_id)
ment["ing_id"] = ment["ingredient_canonical"].map(ing)
ment[["rec_id", "ingredient_index", "ingredient_canonical", "ing_id", "is_primary_alternative"]] \
    .to_csv(out / "recipe_ingredient_links_v1.csv", index=False)
linked = ment["ing_id"].notna().mean()
msg = f"- REC↔ING links: {len(ment):,} mention rows; linked to an ING concept: {linked:.1%}"
(ROOT / "reports" / "recipe_registry_v1.md").open("a").write(msg + "\n")
print(msg)
