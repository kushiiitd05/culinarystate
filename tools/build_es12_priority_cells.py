#!/usr/bin/env python3
"""ES-1.2: priority-cell source coverage ("where should we look?"). No numeric evidence extracted; counts come from registry/evidence_query_matrix_v1.csv (Europe PMC metadata counts)
and from the current EVD ledger (local row counts via the ES-1.1 audit)."""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
q = {r["query_id"]: r for r in csv.DictReader(open(ROOT / "registry/evidence_query_matrix_v1.csv", encoding="utf-8"))}
LOC = {"garlic": 0, "onion": 474, "potato": 840, "broccoli": 355, "cabbage": 256, "rice": 129, "wheat dough": 0, "wheat (flour/other)": 35, "beef": 1785}  # EVD rows by name (MP-0 audit + onion count from the same ledger)
# (cell, process, mechanism, state-variable family, condition types, local-key, structured sources, reference/mechanism sources, query ids, structured status, next action)
R = [
    ("garlic", "crushing / cutting / resting", "alliinase: alliin -> allicin (thiosulfinates)", "chemical (precursor depletion, product formation); sensory later", "time after crushing; temperature; pH", "garlic", "none identified", "Rhea (reaction), BRENDA (in-vitro alliinase parameters)", "Q01", "SOURCE_GAP (structured)", "ES-1.3 pilot candidate; literature route"),
    ("garlic", "heating (boil/fry/microwave), with or without resting after crushing", "thermal inactivation of alliinase; allicin degradation", "chemical, kinetics", "temperature; time; resting time", "garlic", "none identified", "BRENDA (enzyme thermal parameters, in vitro)", "Q02", "SOURCE_GAP (structured)", "literature route; kinetic extraction"),
    ("onion", "cutting / slicing", "alliinase + lachrymatory factor synthase -> propanethial S-oxide", "chemical (volatile), sensory (tear) later", "time; temperature; cultivar", "onion", "none identified", "Rhea/BRENDA (LFS entry not verified)", "Q03", "SOURCE_GAP (structured); small literature pool", "treat as high-risk: few OA papers (see counts)"),
    ("onion", "boiling / frying / roasting", "leaching, thermal degradation (flavonols, vitamin C)", "chemical retention", "temperature; time; medium", "onion", "DS-001 USDA R6; DS-002 Bognar; DS-003 Phenol-Explorer (existing); DS-016 USDA Flavonoid DB 3.3 (composition)", "-", "Q04", "STRUCTURED_AVAILABLE (E3, 474 EVD rows) + literature", "unverified E3 already present; add conditions via literature"),
    ("potato", "frying (deep/shallow), baking, roasting", "Maillard: asparagine + reducing sugars -> acrylamide", "chemical (product formation), kinetics; physical (moisture, colour, oil)", "oil/oven temperature; time; sugar content; pH; slice thickness", "potato", "DS-049 EFSA/JRC occurrence (access UNKNOWN); no controlled-kinetics database identified", "Rhea/BRENDA do not cover Maillard", "Q05; Q06", "SOURCE_GAP (structured kinetics) ; literature rich", "ES-1.3 pilot candidate; kinetic extraction"),
    ("potato", "cutting / peeling", "polyphenol oxidase enzymatic browning", "physical (colour L*a*b*), chemical", "time; antioxidant/acid; temperature", "potato", "none identified", "BRENDA (PPO in-vitro), Rhea", "Q07", "SOURCE_GAP (structured)", "literature route"),
    ("potato", "boiling / steaming", "leaching vs thermal destruction (vitamin C, polyphenols)", "chemical retention; mass", "temperature; time; water volume", "potato", "DS-001, DS-002, DS-003 (existing, 840 EVD rows); DS-009 AFCD retention; DS-008 CoFID factors", "-", "Q08", "STRUCTURED_AVAILABLE (E3) ", "already covered at E3; add condition-rich primary studies"),
    ("broccoli", "steaming / boiling / blanching / chopping", "myrosinase: glucosinolates -> isothiocyanates", "chemical, kinetics", "temperature; time; cutting before heating", "broccoli", "none identified (existing 355 EVD rows are nutrient retention, not mechanism)", "BRENDA (myrosinase in vitro)", "Q09", "SOURCE_GAP (structured mechanism)", "ES-1.3 candidate #2; literature route"),
    ("broccoli / green vegetables", "heating with pH change", "chlorophyll -> pheophytin (pheophytinization)", "physical (colour), chemical (pigment), kinetics", "temperature; time; pH", "broccoli", "none identified", "-", "Q10; Q13", "SOURCE_GAP (structured)", "literature route; Arrhenius extraction"),
    ("cabbage", "chopping / shredding / cooking", "myrosinase / glucosinolate hydrolysis", "chemical", "temperature; time; cutting", "cabbage", "none identified (existing 256 EVD rows are nutrients)", "BRENDA (myrosinase)", "Q11", "SOURCE_GAP (structured mechanism)", "literature route"),
    ("cabbage", "lactic fermentation (sauerkraut/kimchi)", "lactic acid fermentation: pH/acidity change", "chemical (pH, acidity), procedural", "salt %; temperature; time", "cabbage", "none identified", "-", "Q12", "SOURCE_GAP (structured)", "literature route; pH trajectories"),
    ("apple / avocado / banana (PPO produce)", "cutting / peeling", "polyphenol oxidase browning", "physical (colour), chemical", "time; pH; temperature; antioxidant", "none", "none identified", "BRENDA (PPO)", "Q14", "SOURCE_GAP (structured)", "literature route (generalises PPO)"),
    ("wheat dough", "mixing / kneading / proofing / baking", "starch gelatinisation; gluten network; protein aggregation; fermentation", "physical (moisture, structure, volume), chemical (pH)", "temperature profile; time; water content", "wheat dough", "none identified (existing 35 wheat rows are nutrients; dough 0 rows)", "-", "Q15; Q16", "SOURCE_GAP (structured)", "literature route; physical time series"),
    ("rice", "soaking / boiling / absorption cooking / cooling", "starch gelatinisation; hydration; retrogradation", "physical (moisture, texture), phase", "temperature; time; water:rice ratio", "rice", "DS-001/002/003 (existing 129 nutrient rows; temperature known in 0)", "-", "Q17; Q18", "SOURCE_GAP (physical/mechanism); nutrient E3 present", "literature route; moisture/texture time series"),
    ("beef", "roasting / boiling / braising / grilling", "water loss; protein denaturation; collagen changes", "physical (mass yield, moisture, texture), chemical (fat)", "core temperature; time; cut; method", "beef", "DS-006 USDA Cooking Yields for Meat & Poultry R2 (local, not ingested); DS-002 Bognar yields; DS-001; DS-009 AFCD weight-change factors", "-", "Q19; Q20", "STRUCTURED_AVAILABLE (yield/moisture/fat end-points) + literature for texture/collagen", "Wave A import of DS-006 first"),
    ("beef", "searing / grilling / frying", "Maillard / Strecker; heterocyclic amines", "chemical (products), physical (colour)", "surface temperature; time", "beef", "none identified", "-", "Q21", "SOURCE_GAP (structured)", "literature route"),
]
cols = ["cell_id", "priority_cell", "process", "mechanism_or_target", "state_variable_family", "condition_types_to_capture", "existing_local_EVD_rows_for_matrix", "structured_candidate_sources", "reference_mechanism_sources", "literature_query_ids",
        "europepmc_hits_with_mechanism_all", "europepmc_hits_with_mechanism_OA", "europepmc_hits_titleabs_OA", "discovery_status", "next_action", "note"]
out = []
for i, (cell, proc, mech, fam, cond, lk, struct, ref, qids, st, nxt) in enumerate(R, 1):
    ids = [x.strip() for x in qids.split(";")]
    sm = lambda key: "; ".join(f"{k}:{q[k][key]}" for k in ids if k in q)
    out.append({"cell_id": f"PC-{i:02d}", "priority_cell": cell, "process": proc, "mechanism_or_target": mech, "state_variable_family": fam, "condition_types_to_capture": cond,
                "existing_local_EVD_rows_for_matrix": LOC.get(lk, "n/a (no EVD rows by this name)"), "structured_candidate_sources": struct, "reference_mechanism_sources": ref, "literature_query_ids": ";".join(ids),
                "europepmc_hits_with_mechanism_all": sm("hits_with_mechanism_all"), "europepmc_hits_with_mechanism_OA": sm("hits_with_mechanism_OA"), "europepmc_hits_titleabs_OA": sm("hits_titleabs_OA"),
                "discovery_status": st, "next_action": nxt, "note": "counts are Europe PMC metadata hit counts (upper-bound, unverified relevance); no values extracted; existing EVD rows are E3 nutrient/phenolic retention, not mechanism evidence"})
with open(ROOT / "reports/h_state/es_1_2_priority_cell_source_coverage.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    w.writerows(out)
print(len(out), "priority-cell rows;", sum("SOURCE_GAP" in r["discovery_status"] for r in out), "with a structured-source gap")
