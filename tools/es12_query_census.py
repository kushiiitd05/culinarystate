#!/usr/bin/env python3
"""ES-1.2: literature query taxonomy + metadata-only hit counts from the Europe PMC REST search (resultType=lite, pageSize=1; counts only, nothing downloaded,
no abstracts or full text stored). ~2 requests per query at <=1 request/second. Writes registry/evidence_query_matrix_v1.csv.
  python tools/es12_query_census.py"""
import csv
import json
import time
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
UA = "culinarystate-es12-census/1.0 (research; counts only; kush23296@iiitd.ac.in)"

# (id, priority_cell, matrix terms, process terms, target terms, mechanism terms, condition axes sought, state-variable families, evidence type sought)
M = lambda *t: "(" + " OR ".join(t) + ")"
Q = [
    ("Q01", "garlic", M("garlic", '"Allium sativum"'), M("crush*", "chop*", "cut", "mince*", "macerat*"), M("allicin", "alliin", "thiosulfinate*"), M("alliinase"), "time after crushing; temperature; pH", "chemical (precursor/product), kinetics", "controlled experiment"),
    ("Q02", "garlic", M("garlic", '"Allium sativum"'), M("heat*", "boil*", "cook*", "fry*", "microwav*"), M("allicin", "thiosulfinate*", "alliin"), M("alliinase", "thermal degradation"), "temperature; time; resting time before heating", "chemical, kinetics", "controlled experiment"),
    ("Q03", "onion", M("onion", '"Allium cepa"'), M("cut*", "chop*", "slic*", "crush*"), M('"lachrymatory factor"', "propanethial", "syn-propanethial-S-oxide"), M('"lachrymatory factor synthase"', "alliinase"), "time; temperature; cultivar", "chemical (volatile), sensory (tear)", "controlled experiment"),
    ("Q04", "onion", M("onion", '"Allium cepa"'), M("boil*", "fry*", "saut*", "cook*", "roast*"), M("quercetin", "flavonol*", "vitamin C", "polyphenol*"), M("leaching", "thermal degradation"), "temperature; time; medium", "chemical (retention)", "controlled experiment / database aggregate"),
    ("Q05", "potato", M("potato*", '"Solanum tuberosum"'), M("fry*", "deep-fry*", "french fries", "chips", "bak*", "roast*"), M("acrylamide"), M("Maillard", "asparagine", "reducing sugar*"), "oil temperature; time; pH; sugar content", "chemical (product formation), kinetics", "controlled experiment"),
    ("Q06", "potato", M("potato*", '"Solanum tuberosum"'), M("fry*", "deep-fry*", "french fries"), M("moisture", "oil uptake", "texture", "colour", "color", "crust"), M("water loss", "oil absorption"), "oil temperature; time; slice thickness", "physical (moisture, texture, colour, geometry)", "controlled experiment"),
    ("Q07", "potato", M("potato*", '"Solanum tuberosum"'), M("cut*", "peel*", "slic*", "shred*"), M("browning", "discolo*"), M("polyphenol oxidase", "PPO", "enzymatic browning"), "time; antioxidant/acid; temperature", "physical (colour), chemical", "controlled experiment"),
    ("Q08", "potato", M("potato*", '"Solanum tuberosum"'), M("boil*", "steam*", "cook*", "microwav*"), M('"vitamin C"', "ascorbic", "polyphenol*", "nutrient retention"), M("leaching", "thermal degradation"), "temperature; time; water volume", "chemical (retention), physical (mass)", "controlled experiment / database aggregate"),
    ("Q09", "broccoli", M("broccoli", '"Brassica oleracea"'), M("steam*", "boil*", "blanch*", "microwav*", "cook*", "chop*"), M("glucosinolate*", "sulforaphane", "isothiocyanate*"), M("myrosinase"), "temperature; time; cutting before heating", "chemical, kinetics", "controlled experiment"),
    ("Q10", "broccoli", M("broccoli"), M("steam*", "boil*", "blanch*", "cook*", "heat*"), M("chlorophyll", "pheophytin", "colour", "color"), M("pheophytinization", "pH"), "temperature; time; pH", "physical (colour), chemical (pigment)", "controlled experiment"),
    ("Q11", "cabbage", M("cabbage", '"Brassica oleracea"'), M("chop*", "shred*", "cut*", "boil*", "steam*", "cook*"), M("glucosinolate*", "isothiocyanate*", "sulforaphane"), M("myrosinase"), "temperature; time; cutting", "chemical", "controlled experiment"),
    ("Q12", "cabbage", M("cabbage", "sauerkraut", "kimchi"), M("ferment*"), M("lactic acid", "pH", "titratable acidity"), M("lactic acid bacteria"), "salt %; temperature; time", "chemical (pH/acidity), procedural", "controlled experiment"),
    ("Q13", "green vegetables", M("green vegetable*", "spinach", "broccoli", "green bean*", "peas"), M("heat*", "thermal process*", "blanch*"), M("chlorophyll", "pheophytin"), M("kinetic*", "activation energy", "Arrhenius", "first-order"), "temperature; time; pH", "kinetics, physical (colour)", "controlled experiment (kinetic)"),
    ("Q14", "apple/avocado/banana", M("apple", "avocado", "banana"), M("cut*", "slic*", "peel*", "bruis*"), M("browning", "discolo*"), M("polyphenol oxidase", "enzymatic browning"), "time; pH; temperature; antioxidant", "physical (colour), chemical", "controlled experiment"),
    ("Q15", "wheat dough", M('"wheat dough"', "bread dough"), M("mix*", "knead*", "proof*", "ferment*", "bak*"), M("moisture", "water absorption", "volume", "gluten", "starch"), M("gelatini*", "gluten network", "protein aggregation"), "temperature profile; time; water content", "physical (moisture, structure), chemical", "controlled experiment"),
    ("Q16", "wheat dough", M("sourdough", '"wheat dough"'), M("ferment*", "proof*"), M("pH", "titratable acidity", "lactic acid", "volume"), M("lactic acid bacteria", "yeast"), "temperature; time; starter", "chemical (pH), physical", "controlled experiment"),
    ("Q17", "rice", M("rice", '"Oryza sativa"'), M("soak*", "boil*", "cook*", "steam*"), M("water uptake", "hydration", "moisture", "texture", "cooking time"), M("gelatini*", "absorption"), "temperature; time; water:rice ratio", "physical (moisture, texture), phase", "controlled experiment"),
    ("Q18", "rice", M("rice", '"Oryza sativa"'), M("cook*", "cool*", "stor*", "reheat*"), M("retrogradation", "resistant starch", "hardness"), M("starch retrogradation"), "temperature; time", "physical (texture), chemical (starch)", "controlled experiment"),
    ("Q19", "beef", M("beef", "meat"), M("cook*", "roast*", "boil*", "grill*", "sous-vide", "braise*"), M("cooking loss", "yield", "weight loss", "moisture", "shear force"), M("protein denaturation", "water loss"), "core temperature; time; cut; method", "physical (mass, moisture, texture)", "controlled experiment / database aggregate"),
    ("Q20", "beef", M("beef", "meat"), M("cook*", "heat*"), M("collagen", "tenderness", "shear force"), M("collagen solubili*", "collagen denaturation"), "core temperature; time", "physical (texture), chemical", "controlled experiment"),
    ("Q21", "beef", M("beef", "meat"), M("cook*", "grill*", "fry*", "roast*", "sear*"), M("browning", "colour", "volatile*", "heterocyclic amine*"), M("Maillard", "Strecker"), "surface temperature; time", "chemical (products), physical (colour)", "controlled experiment"),
    ("Q22", "frying oils", M("frying oil*", "cooking oil*"), M("fry*", "heat*"), M("polar compounds", "lipid oxidation", "oxidation"), M("lipid oxidation", "thermal oxidation"), "temperature; time; cycles", "chemical (oxidation markers)", "controlled experiment"),
    ("Q23", "anthocyanin foods", M("red cabbage", "berry", "blueberry", "purple"), M("heat*", "thermal process*", "cook*"), M("anthocyanin*"), M("degradation", "kinetic*", "pH"), "temperature; time; pH", "chemical, colour", "controlled experiment (kinetic)"),
    ("Q24", "vegetables (vitamin C kinetics)", M("vegetable*"), M("heat*", "thermal process*", "boil*"), M('"vitamin C"', "ascorbic acid"), M("kinetic*", "Arrhenius", "activation energy", "first-order"), "temperature; time; pH", "chemical, kinetics", "controlled experiment (kinetic)"),
    ("Q25", "sugars", M("sucrose", "glucose", "sugar"), M("heat*", "caramel*"), M("hydroxymethylfurfural", "HMF", "caramel*"), M("caramelisation", "caramelization", "sugar degradation"), "temperature; time; pH", "chemical (products)", "controlled experiment"),
    ("Q26", "generic (physical properties)", M("food*"), M("heat*", "cook*", "dry*"), M("thermal conductivity", "specific heat", "thermal diffusivity", "moisture diffusivity"), M("heat transfer", "mass transfer"), "temperature; moisture", "physical properties, simulator parameters", "property measurement / model"),
    ("Q27", "generic (water activity)", M("food*"), M("dry*", "stor*"), M('"water activity"', "sorption isotherm"), M("sorption"), "temperature; aw", "physical (aw, moisture)", "property measurement"),
    ("Q28", "generic (pressure)", M("vegetable*", "meat", "legume*"), M('"pressure cooking"', "autoclav*", "high pressure"), M("nutrient retention", "texture", "vitamin"), M("pressure effect"), "pressure; temperature; time", "chemical, physical", "controlled experiment"),
    ("Q29", "generic (leaching vs destruction)", M("vegetable*"), M("boil*", "blanch*"), M("leaching", "vitamin*", "mineral*"), M("leaching", "thermal destruction"), "water:food ratio; temperature; time", "chemical (retention), mass", "controlled experiment"),
    ("Q30", "smoked/pyrolysed", M("smok*", "wood smoke"), M("smok*", "pyrolysis"), M("guaiacol", "syringol", "phenols"), M("lignin pyrolysis"), "temperature; wood type", "chemical (volatiles)", "controlled experiment"),
]


def count(q):
    url = BASE + "?" + urllib.parse.urlencode({"query": q, "format": "json", "pageSize": 1, "resultType": "lite"})
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["hitCount"]


rows = []
for (qid, cell, mat, proc, tgt, mech, cond, fam, etype) in Q:
    qs = f"{mat} AND {proc} AND {tgt}"
    qs_m = f"{qs} AND {mech}"
    out = {"query_id": qid, "priority_cell": cell, "MATRIX": mat, "PROCESS": proc, "TARGET": tgt, "MECHANISM": mech, "CONDITION_axes_sought": cond, "state_variable_families": fam, "evidence_type_sought": etype,
           "route": "Europe PMC REST search (metadata counts only)", "europepmc_query_matrix_process_target": qs, "europepmc_query_with_mechanism": qs_m}
    qs_ta = f"TITLE_ABS:{mat} AND TITLE_ABS:{proc} AND TITLE_ABS:{tgt}"
    out["europepmc_query_titleabs"] = qs_ta
    for key, q in (("hits_all", qs), ("hits_OA", qs + " AND OPEN_ACCESS:y"), ("hits_with_mechanism_all", qs_m), ("hits_with_mechanism_OA", qs_m + " AND OPEN_ACCESS:y"), ("hits_titleabs_OA", qs_ta + " AND OPEN_ACCESS:y")):
        try:
            out[key] = count(q)
        except Exception as e:  # keep going; record the failure
            out[key] = f"ERROR:{type(e).__name__}"
        time.sleep(1.0)
    out["count_date"] = str(date.today())
    out["notes"] = "counts are upper-bound candidate-discovery indicators (wildcard terms match full text); hits_titleabs_OA is a stricter lower-bound proxy; relevance, design, per-article licence and measurement quality are NOT assessed; OA flag is not a reuse-licence guarantee"
    rows.append(out)
    print(qid, cell, out["hits_all"], out["hits_OA"], out["hits_with_mechanism_all"], out["hits_with_mechanism_OA"], out["hits_titleabs_OA"], flush=True)
cols = list(rows[0].keys())
with open(ROOT / "registry/evidence_query_matrix_v1.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    w.writerows(rows)
