"""Ingest CoSyLab alignment data as KG edges.

1. MOL_HAS_TASTE edges from bittersweet (AGPL-3.0) matched molecules
2. ING_COSYLAB_CATEGORY edges for ingredients with category disagreements
"""
import csv

REG = "/Users/bournesmartasfuck_kush/Desktop/CGAS/culinarystate/registry"
KG_FILE = f"{REG}/kg/kg_edges_v1.csv"

# Find max KGE id
max_kge = 0
with open(KG_FILE) as f:
    reader = csv.DictReader(f)
    for row in reader:
        num = int(row["kge_id"].split("-")[1])
        if num > max_kge:
            max_kge = num

print(f"Current max KGE: KGE-{max_kge:06d}")

new_edges = []

# ── 1. MOL_HAS_TASTE edges (only matched molecules) ──
taste_file = f"{REG}/molecules/taste_molecule_alignment.csv"
seen = set()
taste_count = 0
with open(taste_file) as f:
    reader = csv.DictReader(f)
    for row in reader:
        mol_id = row["mol_id"]
        if mol_id == "UNMATCHED":
            continue
        taste = row["taste_class"]
        is_pos = row["is_positive"]
        source = row["source"]

        if taste in ("BITTER", "SWEET"):
            taste_label = taste.lower() if is_pos == "True" else f"not_{taste.lower()}"
        elif taste == "SWEET_QUANTIFIED":
            taste_label = "sweet_quantified" if is_pos == "True" else "not_sweet_quantified"
        else:
            continue

        key = (mol_id, taste_label)
        if key in seen:
            continue
        seen.add(key)

        max_kge += 1
        new_edges.append({
            "kge_id": f"KGE-{max_kge:06d}",
            "predicate": "MOL_HAS_TASTE",
            "subject_id": mol_id,
            "object": taste_label,
            "support": 1,
            "lift": "",
            "confidence": 0.9 if "bittersweet" in source else 0.7,
            "band": "MEDIUM",
            "p50": "",
        })
        taste_count += 1

print(f"MOL_HAS_TASTE edges: {taste_count}")

# ── 2. ING_COSYLAB_CATEGORY for disagreements ──
xwalk_file = f"{REG}/ingredients/cosylab_category_crosswalk.csv"
cat_count = 0
with open(xwalk_file) as f:
    reader = csv.DictReader(f)
    for row in reader:
        ing_id = row["ing_id"]
        if not ing_id or row["agreement"] not in ("DISAGREE", "NO_FOODON"):
            continue

        rdb2_cat = row["rdb2_category"]
        max_kge += 1
        new_edges.append({
            "kge_id": f"KGE-{max_kge:06d}",
            "predicate": "ING_COSYLAB_CATEGORY",
            "subject_id": ing_id,
            "object": rdb2_cat,
            "support": 1,
            "lift": "",
            "confidence": 0.5,
            "band": "LOW",
            "p50": "",
        })
        cat_count += 1

print(f"ING_COSYLAB_CATEGORY edges: {cat_count}")
print(f"Total new edges: {len(new_edges)}")

# Append to KG
with open(KG_FILE, "a") as f:
    for edge in new_edges:
        f.write(",".join(str(edge[k]) for k in [
            "kge_id", "predicate", "subject_id", "object",
            "support", "lift", "confidence", "band", "p50"
        ]) + "\n")

print(f"Appended to {KG_FILE}")
print(f"New max KGE: KGE-{max_kge:06d}")

# Verify
total = 0
with open(KG_FILE) as f:
    for _ in f:
        total += 1
print(f"Total KG edges now: {total - 1} (excluding header)")
