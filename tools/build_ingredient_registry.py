#!/usr/bin/env python3
"""Build ingredient registry v1 (ING-/ALIAS- ledgers + review CSVs) from the A1 mention table.

  /opt/anaconda3/bin/python tools/build_ingredient_registry.py [--min-recipes 3]
Outputs: ledgers/data/{ING,ALIAS}.jsonl, registry/ingredients/*.csv, reports/ingredient_registry_v1.md
"""
import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.ledgers.store import LedgerStore  # noqa: E402
from culinarystate.vocab.registry_build import POLYSEMOUS, build_aliases, build_concepts, coverage_curve  # noqa: E402

TAXO = {"FORM_OF", "VARIANT_OF"}   # only these become parent_ids; HEAD_NOUN is review grouping

ap = argparse.ArgumentParser()
ap.add_argument("--mentions", default=str(ROOT.parent / "a1" / "A1 3" / "data" / "processed" / "ingredient_mentions.csv"))
ap.add_argument("--min-recipes", type=int, default=3)
a = ap.parse_args()

m = pd.read_csv(a.mentions)
concepts, rejects = build_concepts(m, a.min_recipes)
known = {c.name for c in concepts}
aliases = build_aliases(m, known)
curve = coverage_curve(m, concepts)

st = LedgerStore()
CORPUS_SRC_KEY = "a1:bbcgoodfood:ingredient_mentions"
src = {"id": st.ids.mint("SRC", key=CORPUS_SRC_KEY), "record_type": "SRC", "status": "ACTIVE",
       "created_by": "Kush+Claude", "provenance": {"method": "MANUAL", "source_ids": []},
       "verification": {"status": "UNVERIFIED"}, "kind": "DATASET",
       "title": "A1 BBC Good Food corpus — ingredient mentions (11,934 recipes, spaCy NER + normalization)",
       "year": 2026, "licence": "Derived from bbcgoodfood.com pages (third-party copyright)",
       "licence_status": "RESTRICTED", "storage_rule": "DERIVED_ONLY", "primary_or_secondary": "PRIMARY",
       "source_family_id": "BBCGF-A1"}
src_id = src["id"]
counts = {"SRC": st.upsert(src)[0]}

ids = {c.name: st.ids.mint("ING", key=f"name:{c.name}") for c in concepts}
n_ing = {"created": 0, "unchanged": 0, "revised": 0}
for c in concepts:
    rec = {"id": ids[c.name], "record_type": "ING", "status": "ACTIVE", "created_by": "Kush+Claude",
           "provenance": {"method": "MODEL", "source_ids": [src_id], "agent": "a1_ner+registry_build@0.1",
                          "locator": "ingredient_mentions.csv:ingredient_canonical"},
           "verification": {"status": "UNVERIFIED"}, "canonical_name": c.name,
           "scientific_identity_status": "UNKNOWN", "parent_ids": [ids[c.parent]] if c.parent and c.relation in TAXO else [],
           "facets": {k: v for k, v in c.facets.items() if k == "form"} if "form" in c.facets else {},
           "corpus_frequency": c.recipe_freq, "ambiguity": c.ambiguity,
           "crosswalks": {k: {"status": "UNRESOLVED_EXTERNAL"} for k in ("foodon", "fdc", "flavordb", "recipedb")},
           "notes": "; ".join(x for x in (
               f"{c.relation} {c.parent}" if c.parent else "", f"modifier={c.facets['modifier']}"
               if c.facets.get("modifier") else "", f"polysemous: {POLYSEMOUS[c.name]}" if c.name in POLYSEMOUS
               else "") if x) or None}
    n_ing[st.upsert(rec)[0]] += 1

current_ing = set(ids.values())
for old in st.all_latest("ING"):                       # concepts that dropped out: deprecate, never delete
    if old["id"] not in current_ing and old["status"] == "ACTIVE":
        st.upsert({**old, "status": "DEPRECATED", "notes": "dropped from registry rebuild (see reports)"})
        n_ing["deprecated"] = n_ing.get("deprecated", 0) + 1

n_alias = {"created": 0, "unchanged": 0, "revised": 0}
for al in aliases:
    rec = {"id": st.ids.mint("ALIAS", key=f"en:{al.surface}"), "record_type": "ALIAS", "status": "ACTIVE",
           "created_by": "Kush+Claude",
           "provenance": {"method": "MODEL", "source_ids": [src_id], "agent": "a1_ner+registry_build@0.1"},
           "verification": {"status": "UNVERIFIED"}, "surface": al.surface, "normalized": al.surface,
           "ingredient_id": ids[al.canonical] if al.canonical else None,
           "candidate_ingredient_ids": [ids[c] for c in al.candidates],
           "language": "en", "region": "GB", "alias_type": al.alias_type, "link_band": al.link_band,
           "corpus_frequency": al.count}
    n_alias[st.upsert(rec)[0]] += 1
current_alias = {st.ids.lookup("ALIAS", f"en:{al.surface}") for al in aliases}
for old in st.all_latest("ALIAS"):
    if old["id"] not in current_alias and old["status"] == "ACTIVE":
        st.upsert({**old, "status": "DEPRECATED", "notes": "dropped from registry rebuild"})
        n_alias["deprecated"] = n_alias.get("deprecated", 0) + 1

out = ROOT / "registry" / "ingredients"
out.mkdir(parents=True, exist_ok=True)
pd.DataFrame([{"ing_id": ids[c.name], "canonical_name": c.name, "recipe_freq": c.recipe_freq,
               "mention_freq": c.mention_freq, "parent": c.parent, "relation": c.relation,
               "form": c.facets.get("form"), "modifier": c.facets.get("modifier"), "ambiguity": c.ambiguity}
              for c in concepts]).to_csv(out / "ingredient_registry_v1.csv", index=False)
pd.DataFrame([{"surface": x.surface, "canonical": x.canonical, "alias_type": x.alias_type, "link_band": x.link_band,
               "count": x.count, "candidates": "|".join(x.candidates)} for x in aliases]) \
    .to_csv(out / "alias_registry_v1.csv", index=False)
coll = [x for x in aliases if x.alias_type == "AMBIGUOUS"]
coll_rows = [{"surface": x.surface, "kind": "SURFACE_COLLISION", "count": x.count, "detail": "|".join(x.candidates)}
             for x in coll]
freq = {c.name: c.recipe_freq for c in concepts}
coll_rows += [{"surface": k, "kind": "SEMANTIC_POLYSEMY", "count": freq.get(k, 0), "detail": v}
              for k, v in POLYSEMOUS.items()]
pd.DataFrame(coll_rows, columns=["surface", "kind", "count", "detail"]).sort_values("count", ascending=False) \
    .to_csv(out / "alias_collision_report.csv", index=False)
rejects.to_csv(out / "unresolved_high_frequency.csv", index=False)
curve.to_csv(out / "coverage_curve.csv", index=False)

share_reg = m["ingredient_canonical"].isin(known).mean()
k_at = {k: float(curve.loc[curve["rank"] == k, "cum_share"].iloc[0]) for k in (50, 100, 500, 1000, 2000)
        if k <= len(curve)}
lines = [f"# Ingredient registry v1 (min recipe freq {a.min_recipes})", "",
         f"- mentions: {len(m):,}; unique A1 canonicals: {m['ingredient_canonical'].nunique():,}",
         f"- ING concepts: {len(concepts):,} (with parent link: {sum(1 for c in concepts if c.parent):,})",
         f"- ALIAS rows: {len(aliases):,}; surface collisions: {len(coll):,} (A1 normalization is deterministic); "
         f"curated polysemous concepts: {len(POLYSEMOUS)} (AI-drafted, needs human review)",
         f"- taxonomy parents (FORM_OF/VARIANT_OF): {sum(1 for c in concepts if c.relation in TAXO):,}; "
         f"head-noun groups (review only): {sum(1 for c in concepts if c.relation == 'HEAD_NOUN'):,}",
         f"- rejected/unresolved high-frequency candidates: {len(rejects):,} (human review)",
         f"- mention coverage by registry concepts: {share_reg:.1%}",
         "- coverage by top-k canonicals: " + ", ".join(f"top{k}={v:.1%}" for k, v in k_at.items()),
         "- crosswalks (FoodOn/FDC/FlavorDB/RecipeDB): all UNRESOLVED_EXTERNAL in v1; scientific identity UNKNOWN",
         f"- ledger writes: ING {n_ing}, ALIAS {n_alias}"]
(ROOT / "reports" / "ingredient_registry_v1.md").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
print("rejects by reason:", rejects["reason"].value_counts().to_dict() if len(rejects) else {})
