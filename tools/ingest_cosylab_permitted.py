#!/usr/bin/env python3
"""CoSyLab datasets used under D-015 (permission reported by Kush; licence_status ASSUMED, DERIVED_ONLY) -> KGE via LedgerStore.

  /opt/anaconda3/bin/python tools/ingest_cosylab_permitted.py
  1. RecipeDB2 DietRx categories vs ING FoodOn category -> ING_COSYLAB_CATEGORY (disagreements, low confidence 0.5)
  2. spice-disease PubMed sentences -> ING_HEALTH_ASSOCIATION (foods in ING, >=2 mentions)
  3. SweetpredDB sweet molecules -> MOL_HAS_TASTE "Sweetness" (matched to MOL by InChIKey block 1)
Raw files stay local (gitignored). Unmatched molecules/foods are counted, not created.
"""
import csv
import sys
from collections import Counter
from pathlib import Path

from rdkit import Chem, RDLogger

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.ledgers.store import LedgerStore  # noqa: E402
from culinarystate.vocab.foodon import norm  # noqa: E402

EXT = ROOT / "data" / "external"
CB = "Kush+Claude"
LIC = "No licence file; use permitted by Prof. Bagler (reported by Kush, D-015)"


def src(st, key, title, url) -> str:
    sid = st.ids.mint("SRC", key=key)
    st.upsert({"id": sid, "record_type": "SRC", "status": "ACTIVE", "created_by": CB,
               "provenance": {"method": "MANUAL", "source_ids": []}, "verification": {"status": "UNVERIFIED"},
               "kind": "DATABASE", "title": title, "url": url, "year": 2022, "licence": LIC,
               "licence_status": "ASSUMED", "storage_rule": "DERIVED_ONLY", "primary_or_secondary": "SECONDARY",
               "source_family_id": key.split(":")[0].upper(), "notes": "written confirmation requested in H1 email"})
    return sid


def edge(st, w, sid, agent, pred, subj, val, conf, band, locator, corpus, notes="", n=0):
    kid = st.ids.mint("KGE", key=f"{pred}|{subj}|{val}|{corpus}")
    w[st.upsert({"id": kid, "record_type": "KGE", "status": "ACTIVE", "created_by": CB,
                 "provenance": {"method": "IMPORT", "source_ids": [sid], "agent": agent, "locator": locator},
                 "verification": {"status": "UNVERIFIED"}, "predicate": pred, "subject_id": subj,
                 "object_id": None, "object_value": val, "support": {"recipes": n}, "confidence": conf,
                 "confidence_band": band, "method": "EXTERNAL_SOURCE", "corpus_ids": [corpus], "notes": notes})[0]] += 1


def main() -> None:
    RDLogger.DisableLog("rdApp.*")
    st = LedgerStore()
    ings = [i for i in st.all_latest("ING") if i["status"] == "ACTIVE"]
    by_name = {norm(i["canonical_name"]): i for i in ings}
    w = Counter()
    # 1. RecipeDB2 categories
    s1 = src(st, "recipedb2:categories", "RecipeDB2 manually labelled ingredient categories (CoSyLab)",
             "https://github.com/cosylabiiit/RecipeDB2")
    for r in csv.DictReader((EXT / "recipedb2" / "Category_manually_labelled.csv").open()):
        name = norm(r.get("ingredient") or r.get("Ingredient") or list(r.values())[0])
        cat = (r.get("category") or r.get("Category") or list(r.values())[1] or "").strip()
        ing = by_name.get(name)
        if not ing or not cat:
            continue
        foodon = str(ing.get("category") or "").upper()
        if foodon and cat.upper().replace(" ", "_") == foodon:
            w["category_agree"] += 1
            continue
        edge(st, w, s1, "cosylab_permitted@0.1", "ING_COSYLAB_CATEGORY", ing["id"], cat, 0.5, "LOW",
             f"Category_manually_labelled.csv: {name}", "RECIPEDB2", f"our category: {foodon or 'none'}")
    # 2. spice-disease
    s2 = src(st, "spicedisease:pubmed", "spice-disease-associations annotated PubMed sentences (CoSyLab)",
             "https://github.com/cosylabiiit/spice-disease-associations")
    pairs = Counter()
    with (EXT / "spice_disease" / "annotated-sentences.tsv").open() as f:
        next(f)
        for line in f:
            p = line.rstrip("\n").split("\t")
            if len(p) >= 9 and p[4].strip() and p[6].strip():
                pairs[(norm(p[6]), p[4].strip().lower())] += 1
    for (food, dis), n in pairs.items():
        ing = by_name.get(food)
        if ing and n >= 2:
            edge(st, w, s2, "cosylab_permitted@0.1", "ING_HEALTH_ASSOCIATION", ing["id"], dis,
                 min(0.9, 0.3 + 0.1 * n), "HIGH" if n >= 10 else "MEDIUM" if n >= 5 else "LOW",
                 "annotated-sentences.tsv", "SPICEDISEASE", "PubMed co-mention, not causal", n)
    # 3. SweetpredDB
    s3 = src(st, "sweetpreddb:v1", "SweetpredDB sweetness database (CoSyLab)", "https://github.com/cosylabiiit/SweetpredDB")
    by_ik = {m["inchikey"][:14]: m["id"] for m in st.all_latest("MOL") if m["status"] == "ACTIVE"}
    seen = set()
    for r in csv.DictReader((EXT / "sweetpreddb" / "SweetpredDB.csv").open()):
        m = Chem.MolFromSmiles(r["Smiles"])
        mid = by_ik.get(Chem.MolToInchiKey(m)[:14]) if m else None
        if mid and mid not in seen:
            seen.add(mid)
            edge(st, w, s3, "cosylab_permitted@0.1", "MOL_HAS_TASTE", mid, "Sweetness", 0.8, "MEDIUM",
                 f"SweetpredDB {r['Test_ID']}", "SWEETPREDDB", f"relative sweetness {r['Sweetness']} (x sucrose)")
    print(dict(w))


if __name__ == "__main__":
    main()
