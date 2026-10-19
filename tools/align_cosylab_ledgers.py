"""Align downloaded CoSyLab corpus data with CulinaryState ledgers.

Three alignment tasks:
1. Bittersweet/SweetpredDB molecules → MOL_HAS_TASTE via IMAP SENSORY_ASSOCIATION
2. RecipeDB2 + SustainableFoodDB categories → ING category crosswalk
3. NER companion data → tag distribution comparison report

Output: alignment reports + new KG edge CSVs ready for ingest.
"""
import csv
import json
import os
from collections import Counter, defaultdict
from datetime import datetime, timezone

BASE_EXT = "/Users/bournesmartasfuck_kush/Desktop/CGAS/culinarystate/data/external"
REG = "/Users/bournesmartasfuck_kush/Desktop/CGAS/culinarystate/registry"
LED = "/Users/bournesmartasfuck_kush/Desktop/CGAS/culinarystate/ledgers/data"
OUT = "/Users/bournesmartasfuck_kush/Desktop/CGAS/culinarystate/registry/molecules"

# ── Load existing MOL ledger (name → mol_id, smiles → mol_id) ──
mol_by_name = {}
mol_by_smiles = {}
mol_count = 0
with open(f"{LED}/MOL.jsonl") as f:
    for line in f:
        rec = json.loads(line)
        mol_count += 1
        name = rec.get("preferred_name", "").lower().strip()
        smiles = rec.get("canonical_smiles", "").strip()
        mol_id = rec["id"]
        if name:
            mol_by_name[name] = mol_id
        if smiles:
            mol_by_smiles[smiles] = mol_id

print(f"Loaded {mol_count} MOL records ({len(mol_by_name)} by name, {len(mol_by_smiles)} by SMILES)")

# ── Load ING registry (name → ing_id) ──
ing_by_name = {}
ing_categories = {}
with open(f"{REG}/ingredients/ingredient_registry_v1.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        name = row["canonical_name"].strip().lower()
        ing_id = row["ing_id"]
        ing_by_name[name] = ing_id

# Load FoodOn categories
with open(f"{REG}/ingredients/foodon_crosswalk_v1.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        ing_id = row["ing_id"]
        cat = row.get("category", "").strip()
        if cat:
            ing_categories[ing_id] = cat

print(f"Loaded {len(ing_by_name)} ING records, {len(ing_categories)} with FoodOn categories")

# ═══════════════════════════════════════════════════════════
# TASK 1: Bittersweet + SweetpredDB → Taste molecule alignment
# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("TASK 1: Taste Molecule Alignment (Bittersweet + SweetpredDB)")
print("=" * 60)

taste_molecules = []  # (name, smiles, taste_class, source, is_positive)

# Bittersweet
for fname, taste in [("bitter-train.tsv", "BITTER"), ("bitter-test.tsv", "BITTER"),
                      ("sweet-train.tsv", "SWEET"), ("sweet-test.tsv", "SWEET")]:
    fpath = f"{BASE_EXT}/bittersweet/{fname}"
    with open(fpath) as f:
        header = f.readline().strip().split("\t")
        taste_col = "Bitter" if taste == "BITTER" else "Sweet"
        taste_idx = header.index(taste_col) if taste_col in header else -1
        smiles_idx = header.index("Canonical SMILES") if "Canonical SMILES" in header else header.index("SMILES")
        name_idx = header.index("Name")
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) <= max(taste_idx, smiles_idx, name_idx):
                continue
            name = parts[name_idx].strip()
            smiles = parts[smiles_idx].strip()
            is_pos = parts[taste_idx].strip().lower() == "true" if taste_idx >= 0 else None
            taste_molecules.append((name, smiles, taste, "bittersweet_AGPL3", is_pos))

# SweetpredDB
fpath = f"{BASE_EXT}/sweetpreddb/SweetpredDB.csv"
with open(fpath) as f:
    reader = csv.DictReader(f)
    for row in reader:
        name = row.get("Name", "").strip()
        smiles = row.get("Smiles", "").strip()
        sweetness = float(row.get("Sweetness", 0) or 0)
        taste_molecules.append((name, smiles, "SWEET_QUANTIFIED", "sweetpreddb", sweetness > 1))

print(f"Total taste molecule records: {len(taste_molecules)}")

# Match to existing MOL
matched_by_smiles = 0
matched_by_name = 0
unmatched = 0
taste_edges = []  # (mol_id_or_name, taste_class, source, smiles)

seen = set()
for name, smiles, taste_class, source, is_positive in taste_molecules:
    key = (smiles.lower() if smiles else name.lower(), taste_class)
    if key in seen:
        continue
    seen.add(key)

    mol_id = None
    if smiles and smiles in mol_by_smiles:
        mol_id = mol_by_smiles[smiles]
        matched_by_smiles += 1
    elif name.lower() in mol_by_name:
        mol_id = mol_by_name[name.lower()]
        matched_by_name += 1
    else:
        unmatched += 1

    taste_edges.append({
        "mol_name": name,
        "smiles": smiles,
        "mol_id": mol_id or "UNMATCHED",
        "taste_class": taste_class,
        "is_positive": is_positive,
        "source": source,
    })

print(f"  Matched by SMILES: {matched_by_smiles}")
print(f"  Matched by name:   {matched_by_name}")
print(f"  Unmatched (new):   {unmatched}")
print(f"  Unique taste edges: {len(taste_edges)}")

# Write taste alignment CSV
taste_out = f"{OUT}/taste_molecule_alignment.csv"
with open(taste_out, "w", newline="") as f:
    w = csv.DictWriter(f, ["mol_name", "smiles", "mol_id", "taste_class", "is_positive", "source"])
    w.writeheader()
    w.writerows(taste_edges)
print(f"  Written: {taste_out}")

# Stats
taste_counts = Counter(e["taste_class"] for e in taste_edges)
matched_counts = Counter(e["taste_class"] for e in taste_edges if e["mol_id"] != "UNMATCHED")
print(f"\n  By taste class (total / matched to MOL):")
for tc in sorted(taste_counts):
    print(f"    {tc:20s}: {taste_counts[tc]:5d} total / {matched_counts.get(tc, 0):5d} matched")

# ═══════════════════════════════════════════════════════════
# TASK 2: RecipeDB2 + SustainableFoodDB category crosswalk
# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("TASK 2: Ingredient Category Crosswalk (RecipeDB2 vs FoodOn)")
print("=" * 60)

# RecipeDB2 categories
rdb2_cats = {}
fpath = f"{BASE_EXT}/recipedb2/Category_manually_labelled.csv"
with open(fpath) as f:
    reader = csv.DictReader(f)
    for row in reader:
        ing = row.get("ingredient", "").strip().lower()
        cat = row.get("Dietrx_Category", "").strip()
        if ing and cat:
            rdb2_cats[ing] = cat

# SustainableFoodDB categories
sfdb_cats = {}
fpath = f"{BASE_EXT}/sustainablefooddb/RecipeDB_ingredient_category.csv"
with open(fpath) as f:
    reader = csv.DictReader(f)
    for row in reader:
        ing = row.get("ingredient", "").strip().lower()
        cat = row.get("Dietrx_Category", "").strip()
        if ing and cat:
            sfdb_cats[ing] = cat

print(f"RecipeDB2 categories: {len(rdb2_cats)} ingredients")
print(f"SustainableFoodDB categories: {len(sfdb_cats)} ingredients")

# Match to ING registry
crosswalk = []
matched = 0
unmatched_ing = 0
category_map = {
    "Vegetable": "VEGETABLE", "Fruit": "FRUIT", "Meat": "MEAT",
    "Dairy": "DAIRY", "Spice": "HERB_SPICE", "Herb": "HERB_SPICE",
    "Fish": "SEAFOOD", "Seafood": "SEAFOOD", "Cereal": "GRAIN",
    "Legume": "LEGUME", "Bakery": "BAKED_GOODS", "Beverage": "BEVERAGE",
    "Beverage-Alcoholic": "ALCOHOLIC_BEVERAGE", "Condiment": "CONDIMENT",
    "Nuts and Seeds": "NUT_SEED", "Fungi": "FUNGI",
    "Plant Derivative": "PLANT_DERIVATIVE", "Essential Oil": "ESSENTIAL_OIL",
    "Plant": "PLANT", "Additive": "ADDITIVE", "Dish": "DISH",
    "Maize": "GRAIN", "Flower": "FLOWER",
}

for ing_name, rdb2_cat in rdb2_cats.items():
    ing_id = ing_by_name.get(ing_name)
    foodon_cat = ing_categories.get(ing_id, "") if ing_id else ""
    normalized_rdb2 = category_map.get(rdb2_cat, rdb2_cat.upper())

    if ing_id:
        matched += 1
        agreement = "AGREE" if foodon_cat and normalized_rdb2 == foodon_cat else (
            "DISAGREE" if foodon_cat else "NO_FOODON"
        )
    else:
        unmatched_ing += 1
        agreement = "NO_MATCH"

    crosswalk.append({
        "ingredient": ing_name,
        "ing_id": ing_id or "",
        "rdb2_category": rdb2_cat,
        "rdb2_normalized": normalized_rdb2,
        "foodon_category": foodon_cat,
        "agreement": agreement,
        "sfdb_category": sfdb_cats.get(ing_name, ""),
    })

xwalk_out = f"{REG}/ingredients/cosylab_category_crosswalk.csv"
with open(xwalk_out, "w", newline="") as f:
    w = csv.DictWriter(f, ["ingredient", "ing_id", "rdb2_category", "rdb2_normalized",
                            "foodon_category", "agreement", "sfdb_category"])
    w.writeheader()
    w.writerows(crosswalk)

agree = sum(1 for r in crosswalk if r["agreement"] == "AGREE")
disagree = sum(1 for r in crosswalk if r["agreement"] == "DISAGREE")
no_foodon = sum(1 for r in crosswalk if r["agreement"] == "NO_FOODON")
no_match = sum(1 for r in crosswalk if r["agreement"] == "NO_MATCH")

print(f"\n  Matched to ING registry: {matched}")
print(f"  Not in ING registry:    {unmatched_ing}")
print(f"  Agreement stats (matched only):")
print(f"    AGREE:    {agree}")
print(f"    DISAGREE: {disagree}")
print(f"    NO_FOODON (ING exists, no FoodOn cat): {no_foodon}")
print(f"  Written: {xwalk_out}")

# Show disagreements
if disagree > 0:
    print(f"\n  Top disagreements:")
    disag = [r for r in crosswalk if r["agreement"] == "DISAGREE"]
    for r in disag[:20]:
        print(f"    {r['ingredient']:30s} RDB2={r['rdb2_category']:15s} FoodOn={r['foodon_category']}")

# ═══════════════════════════════════════════════════════════
# TASK 3: NER tag distribution comparison
# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("TASK 3: NER Tag Distribution Comparison")
print("=" * 60)

# Companion data (ground truth with SIZE)
for fname in ["ar_gk_train.tsv", "ar_gk_test.tsv"]:
    fpath = f"{BASE_EXT}/cosylab_companion/{fname}"
    labels = Counter()
    with open(fpath) as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) == 2 and parts[1]:
                labels[parts[1]] += 1
    total = sum(labels.values())
    print(f"\n  {fname} ({total} tokens):")
    for label, count in labels.most_common():
        print(f"    {label:10s} {count:6d} ({100*count/total:5.1f}%)")

# Recipe_NER_DL data (predecessor)
for fname in ["final_train.csv", "final_test.csv"]:
    fpath = f"{BASE_EXT}/recipe_ner_dl/{fname}"
    labels = Counter()
    with open(fpath) as f:
        reader = csv.reader(f)
        next(reader)  # header
        for row in reader:
            if len(row) >= 2:
                for tag in row[1].split():
                    labels[tag] += 1
    total = sum(labels.values())
    print(f"\n  Recipe_NER_DL {fname} ({total} tokens):")
    for label, count in labels.most_common():
        print(f"    {label:10s} {count:6d} ({100*count/total:5.1f}%)")

# RecipeDB3 label_dict (what they ACTUALLY use — 6 labels, no SIZE)
rdb3_labels = {"NAME": 1, "QUANTITY": 2, "UNIT": 3, "STATE": 4, "DF": 5, "TEMP": 6}
print(f"\n  RecipeDB3 DeBERTa label_dict: {list(rdb3_labels.keys())}")
print(f"  MISSING from RecipeDB3: SIZE (exists in companion data with 473 tokens)")
print(f"  Those 473 SIZE tokens silently map to O via label_dict.get(label, 0)")

# ═══════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════
print("\n" + "=" * 60)
print("ALIGNMENT SUMMARY")
print("=" * 60)
print(f"""
Files produced:
  1. {taste_out}
     - {len(taste_edges)} taste molecule edges
     - {matched_by_smiles + matched_by_name} matched to existing MOL ledger
     - {unmatched} new molecules (not yet in MOL)

  2. {xwalk_out}
     - {len(crosswalk)} ingredient category crosswalks
     - {matched} matched to ING registry ({agree} agree, {disagree} disagree)
     - {unmatched_ing} RecipeDB2 ingredients not in our registry

  3. NER tag comparison (stdout above)
     - Companion data has 7 labels including SIZE
     - RecipeDB3 drops SIZE (473 tokens → O)
     - Recipe_NER_DL predecessor has SIZE tag

Next steps:
  - Ingest bittersweet matched molecules as IMAP SENSORY_ASSOCIATION
  - Add COSYLAB_CATEGORY edges to KG for disagreement ingredients
  - Use disagreements as vulnerability evidence for presentation
""")
