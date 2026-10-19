"""Ingest spice-disease associations as KG edges.

Creates ING_HEALTH_ASSOCIATION edges from PubMed-sourced spice-disease data.
Only for spices/foods already in our ING registry.
"""
import csv
from collections import Counter

BASE = "/Users/bournesmartasfuck_kush/Desktop/CGAS/culinarystate/data/external"
REG = "/Users/bournesmartasfuck_kush/Desktop/CGAS/culinarystate/registry"
KG_FILE = f"{REG}/kg/kg_edges_v1.csv"

# Load ING
ing_by_name = {}
with open(f"{REG}/ingredients/ingredient_registry_v1.csv") as f:
    for row in csv.DictReader(f):
        ing_by_name[row["canonical_name"].strip().lower()] = row["ing_id"]

# Find max KGE id
max_kge = 0
with open(KG_FILE) as f:
    for row in csv.DictReader(f):
        num = int(row["kge_id"].split("-")[1])
        if num > max_kge:
            max_kge = num

print(f"Current max KGE: KGE-{max_kge:06d}")

# Parse spice-disease pairs with MESH IDs
pairs = {}
with open(f"{BASE}/spice_disease/annotated-sentences.tsv") as f:
    next(f)  # header
    for line in f:
        parts = line.strip().split("\t")
        if len(parts) >= 9:
            disease_id = parts[3].strip()
            disease_text = parts[4].strip().lower()
            food_id = parts[5].strip()
            food_text = parts[6].strip().lower()
            if food_text and disease_text:
                key = (food_text, disease_text)
                if key not in pairs:
                    pairs[key] = {"count": 0, "disease_id": disease_id, "food_id": food_id}
                pairs[key]["count"] += 1

print(f"Total food-disease pairs: {len(pairs)}")

# Match to ING and create edges
new_edges = []
matched_foods = set()
for (food, disease), info in pairs.items():
    ing_id = ing_by_name.get(food)
    if not ing_id:
        continue
    matched_foods.add(food)

    # Only keep pairs with >= 2 mentions (evidence threshold)
    if info["count"] < 2:
        continue

    max_kge += 1
    new_edges.append({
        "kge_id": f"KGE-{max_kge:06d}",
        "predicate": "ING_HEALTH_ASSOCIATION",
        "subject_id": ing_id,
        "object": disease,
        "support": info["count"],
        "lift": "",
        "confidence": min(0.9, 0.3 + 0.1 * info["count"]),
        "band": "HIGH" if info["count"] >= 10 else "MEDIUM" if info["count"] >= 5 else "LOW",
        "p50": "",
    })

print(f"Foods matched to ING: {len(matched_foods)}")
print(f"New ING_HEALTH_ASSOCIATION edges (≥2 mentions): {len(new_edges)}")

# Append to KG
with open(KG_FILE, "a") as f:
    for edge in new_edges:
        f.write(",".join(str(edge[k]) for k in [
            "kge_id", "predicate", "subject_id", "object",
            "support", "lift", "confidence", "band", "p50"
        ]) + "\n")

print(f"Appended to {KG_FILE}")
print(f"New max KGE: KGE-{max_kge:06d}")

# Summary
band_counts = Counter(e["band"] for e in new_edges)
print(f"\nBy confidence band: {dict(band_counts)}")
print(f"Top associations added:")
sorted_edges = sorted(new_edges, key=lambda e: -e["support"])
for e in sorted_edges[:10]:
    food_name = [n for n, i in ing_by_name.items() if i == e["subject_id"]][0]
    print(f"  {food_name:20s} ↔ {e['object']:25s} (n={e['support']})")

# Final count
total = sum(1 for _ in open(KG_FILE)) - 1
print(f"\nTotal KG edges now: {total}")
