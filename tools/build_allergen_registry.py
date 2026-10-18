#!/usr/bin/env python3
"""ALLERGEN- ledger from FSSAI (Labelling & Display) Regulations 2020, Reg. 5(14) — compendium 23-09-2021.

Authority text: data/raw/fssai/Compendium_Labelling_Display_23_09_2021.pdf (sha256 pinned in SNAP).
Group definitions are quoted from the regulation. ING membership is an AI-drafted keyword mapping
(verification UNVERIFIED) -> registry/allergens/ing_allergen_review.csv for human sign-off before DEL-5 uses
it as a hard constraint. FlavorDB is never used here (AH3).
"""
import hashlib
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.ledgers.store import LedgerStore  # noqa: E402

PDF = ROOT / "data" / "raw" / "fssai" / "Compendium_Labelling_Display_23_09_2021.pdf"
URL = "https://www.fssai.gov.in/upload/uploadfiles/files/Compendium_Labelling_Display_23_09_2021.pdf"
GROUPS = [  # (declared name, regulation item, quoted definition, member keyword regex, exceptions)
    ("Cereals containing gluten", "5(14)(i)", "wheat, rye, barley, oats, spelt or their hybridized strains and "
     "products of these (to be declared as name of the cereal); except wheat-based glucose syrups incl. dextrose, "
     "wheat-based maltodextrins, barley glucose syrups, cereals for alcoholic distillates (gluten ≤ 20 mg/kg)",
     r"\b(wheat|rye|barley|oats?|oatmeal|porridge oats?|spelt|flour|bread|breadcrumbs?|pasta|spaghetti|penne|"
     r"linguine|tagliatelle|fusilli|macaroni|lasagne|couscous|bulgur|semolina|noodles?|pastry|filo|tortillas?|"
     r"pitta|naan|chapati|roti|biscuits?|cake|digestive|brioche|croissants?|crackers?|seitan|freekeh|farro)\b",
     r"\b(rice|corn|gram|chickpea|buckwheat|almond|coconut|potato|tapioca|cassava|gluten-free)\b"),
    ("Crustacean", "5(14)(ii)", "crustacean and their products (to be declared as Crustacean)",
     r"\b(prawns?|shrimps?|crabs?|lobsters?|crayfish|langoustines?|scampi)\b", None),
    ("Milk", "5(14)(iii)", "milk & milk products (to be declared as Milk)",
     r"\b(milk|butter|buttermilk|cream|cheese|cheddar|parmesan|mozzarella|ricotta|mascarpone|feta|halloumi|"
     r"paneer|ghee|yogh?urt|kefir|curd|crème fraîche|creme fraiche|custard|quark|brie|camembert|gruyère|"
     r"gruyere|stilton|goat's cheese|labneh|khoya|condensed milk|ice cream|whey)\b",
     r"\b(coconut milk|almond milk|oat milk|soya milk|soy milk|rice milk|peanut butter|nut butter|cocoa butter|"
     r"shea|apple butter|butter bean|butternut|vegan)\b"),
    ("Egg", "5(14)(iv)", "eggs and egg products (to be declared as Egg)",
     r"\b(eggs?|egg yolks?|egg whites?|mayonnaise|meringue|aioli)\b", r"\b(eggplant|vegan mayo|chocolate (mini )?eggs?|creme eggs?|easter eggs?)\b"),
    ("Fish", "5(14)(v)", "fish and fish products (to be declared as Fish)",
     r"\b(fish|salmon|tuna|cod|haddock|anchov(y|ies)|mackerel|sardines?|trout|sea bass|bream|hake|pollock|"
     r"plaice|sole|halibut|monkfish|swordfish|kipper|fish sauce|worcestershire sauce|caviar|roe)\b", None),
    ("Nut", "5(14)(vi)", "peanuts, tree nuts (e.g. almonds, walnuts, pistachio, cashew nuts) and their products "
     "(to be declared as Nut)",
     r"\b(peanuts?|groundnuts?|almonds?|walnuts?|pistachios?|cashews?|hazelnuts?|pecans?|macadamias?|"
     r"brazil nuts?|marzipan|praline|nutella|frangipane|peanut butter|nut butter|mixed nuts|nuts?)\b",
     r"\b(nutmeg|coconut|butternut|doughnut|water chestnut|tiger nut|pine nuts?|oil)\b"),
    ("Soy", "5(14)(vii)", "soybeans and their products (to be declared as Soy)",
     r"\b(soy|soya|soybeans?|tofu|tempeh|edamame|miso|tamari|soy sauce)\b", r"\boil\b"),
    ("Sulphite", "5(14)(viii)", "sulphite in concentrations of 10 mg/kg or more (to be declared as sulphite) — "
     "depends on concentration, not identity", None, None),
]
REVIEW_ONLY = {"pine nut": "Nut (pine nuts are seeds; FSSAI 'tree nuts' list is non-exhaustive)",
               "coconut": "Nut? (not in FSSAI examples)", "wine": "Sulphite possible (concentration-dependent)",
               "dried apricot": "Sulphite possible", "vinegar": "Sulphite possible", "sultana": "Sulphite possible",
               "raisin": "Sulphite possible", "prosecco": "Sulphite possible", "cider": "Sulphite possible"}

st = LedgerStore()
raw = PDF.read_bytes()
sha = hashlib.sha256(raw).hexdigest()
src_id = st.ids.mint("SRC", key="fssai:labelling_display_2020:compendium_2021-09-23")
counts = Counter()
counts[("SRC", st.upsert({
    "id": src_id, "record_type": "SRC", "status": "ACTIVE", "created_by": "Kush+Claude",
    "provenance": {"method": "MANUAL", "source_ids": [], "locator": URL},
    "verification": {"status": "AI_PRECHECKED", "ai_reviewer": "claude-opus-5-5",
                     "notes": "Reg 5(14) text extracted verbatim with pdftotext; human to confirm"},
    "kind": "AUTHORITY_STANDARD", "title": "Food Safety and Standards (Labelling and Display) Regulations, 2020 — "
    "Compendium Version-I (23.09.2021)", "authors": ["FSSAI"], "year": 2021, "url": URL, "publisher": "FSSAI",
    "licence": "Government of India publication", "licence_status": "ASSUMED", "storage_rule": "COMMIT_OK",
    "primary_or_secondary": "PRIMARY", "source_family_id": "FSSAI-LD-2020"})[0])] += 1
snap_id = st.ids.mint("SNAP", key=f"sha256:{sha}")
counts[("SNAP", st.upsert({"id": snap_id, "record_type": "SNAP", "status": "ACTIVE", "created_by": "Kush+Claude",
                           "provenance": {"method": "IMPORT", "source_ids": [src_id]},
                           "verification": {"status": "UNVERIFIED"}, "source_id": src_id,
                           "retrieved_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
                           "retrieval_url": URL, "sha256": sha, "bytes": len(raw), "local_path": str(PDF.relative_to(ROOT)),
                           "source_version": "Version-I 23.09.2021"})[0])] += 1

ings = [r for r in st.all_latest("ING") if r["status"] == "ACTIVE"]
review = []
for name, item, definition, member_rx, except_rx in GROUPS:
    members = []
    if member_rx:
        for r in ings:
            n = r["canonical_name"]
            if re.search(member_rx, n) and not (except_rx and re.search(except_rx, n)):
                members.append(r["id"])
                review.append({"allergen": name, "ing_id": r["id"], "ingredient": n, "rule": "keyword",
                               "corpus_freq": r.get("corpus_frequency"), "human_decision": ""})
    rid = st.ids.mint("ALLERGEN", key=f"fssai:{item}")
    rec = {"id": rid, "record_type": "ALLERGEN", "status": "ACTIVE", "created_by": "Kush+Claude",
           "provenance": {"method": "MANUAL", "source_ids": [src_id], "snapshot_ids": [snap_id],
                          "locator": f"Regulation {item}", "agent": "allergen_builder@1.0"},
           "verification": {"status": "UNVERIFIED",
                            "notes": "group text from FSSAI; ING membership AI-drafted keyword mapping — review"},
           "allergen_name": name, "jurisdiction": "IN", "authority_source_id": src_id,
           "ingredient_ids": members, "legal_reference": f"FSS (Labelling & Display) Regs 2020, {item}: {definition}",
           "cross_contact_notes": "Cross-contamination declared as 'May contain …'; not required for oils/distilled "
                                  "alcoholic beverages derived from these, or where the product itself is the allergen; "
                                  "raw agricultural commodities exempt."}
    counts[("ALLERGEN", st.upsert(rec)[0])] += 1
for r in ings:
    for key, note in REVIEW_ONLY.items():
        if key in r["canonical_name"]:
            review.append({"allergen": note, "ing_id": r["id"], "ingredient": r["canonical_name"], "rule": "review_only",
                           "corpus_freq": r.get("corpus_frequency"), "human_decision": ""})
out = ROOT / "registry" / "allergens"
out.mkdir(parents=True, exist_ok=True)
df = pd.DataFrame(review).sort_values(["allergen", "corpus_freq"], ascending=[True, False])
df.to_csv(out / "ing_allergen_review.csv", index=False)
print(dict(counts))
print(df.groupby("allergen").size().to_string())
