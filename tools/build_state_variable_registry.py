#!/usr/bin/env python3
"""MP-1: registry/state_variable_registry_v1.csv from the SVAR + EVD ledgers (read-only) plus SSOT-defined FUTURE variables.
Status rules are fixed here, before any evidence acquisition:
  ACTIVE            >= 50 active EVD rows and >= 3 distinct process signatures and not a group aggregate
  PROVISIONAL       10-49 rows (or >= 50 rows but < 3 process signatures, or a group aggregate with evidence)
  MISSING_EVIDENCE  < 10 rows (variable defined; not usable for a benchmark)
  DUPLICATE         same normalised analyte as a lower-id variable (canonical_variable_id given; EVD NOT rewritten until MP-5A migration)
  FUTURE            SSOT-defined variable with no ledger record yet
No scientific variable is invented: FUTURE rows come only from SSOT 105-107 profile lists and the W3 registry in the master plan.
  python tools/build_state_variable_registry.py"""
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L = ROOT / "ledgers/data"


def latest(name):
    d = {}
    for line in open(L / f"{name}.jsonl"):
        if line.strip():
            r = json.loads(line)
            d[r["id"]] = r
    return d


sv, evd = latest("SVAR"), latest("EVD")
ev = [r for r in evd.values() if r["status"] == "ACTIVE"]
rows_by = defaultdict(list)
for r in ev:
    rows_by[r["target"]["state_variable_id"]].append(r)

AGG = re.compile(r"^(other |amino acids|organic acids|sterols|purines|carotenoids|minerals \(ash\))", re.I)


def norm(name):
    n = re.sub(r"\s+content$", "", name.strip())
    n = re.sub(r",\s*[A-Z][a-z]?$", "", n)          # drop a trailing element symbol (", Ca"); other commas are part of the analyte definition
    return re.sub(r"[\s\-]+", "", n.lower())


seen, dup_of = {}, {}
names = {k: re.sub(r"\s+content$", "", sv[k]["canonical_name"]).lower() for k in sv}
for k in sorted(sv):
    n = norm(sv[k]["canonical_name"])
    if n in seen:
        dup_of[k] = seen[n]
    else:
        seen[n] = k

SRC_FIELDS = {
    "USDA-RETN-R6": dict(before=False, after=False, delta=False, direction=True, retention=True, logfold="derivable", meas="MEAS-000001 (calculated %TR/%AR, nearest 5%)", unit="percent retention (source); fraction in ledger"),
    "BOGNAR-2002": dict(before=False, after=False, delta=False, direction=True, retention=True, logfold="derivable", meas="MEAS-000002 (true retention) / MEAS-000003 (weight yield)", unit="fraction"),
    "PHENOL-EXPLORER-3.6": dict(before=True, after=True, delta="derivable", direction=True, retention=True, logfold="derivable", meas="per-study analytical methods (MEAS ledger has 3 records only; study-level methods not captured)", unit="mg/100 g fresh weight | mg/100 mL | mg/100 g dry weight"),
}
HDR = ["state_variable_id", "name", "family", "subfamily", "definition", "datatype", "unit", "before_allowed", "after_allowed", "delta_allowed", "direction_allowed", "retention_allowed", "logfold_allowed", "measurement_family",
       "gold_eligible", "simulation_eligible", "evidence_required", "current_row_count", "current_evidence_tiers", "current_coverage_status", "SSOT_source", "status", "canonical_variable_id", "n_distinct_process_signatures", "source_families", "notes"]
out = []
for k in sorted(sv):
    r = sv[k]
    rows = rows_by.get(k, [])
    fams = Counter(x["source_family_id"] for x in rows)
    sig = len({tuple((x["process"] or {}).get("steps") or []) for x in rows})
    tiers = Counter(x["tier"] for x in rows)
    isagg = bool(AGG.match(r["canonical_name"]))
    mass = r["family"] == "PHYSICAL"
    if k in dup_of:
        status = "DUPLICATE"
    elif len(rows) < 10:
        status = "MISSING_EVIDENCE"
    elif len(rows) >= 50 and sig >= 3 and not isagg:
        status = "ACTIVE"
    else:
        status = "PROVISIONAL"
    sf = list(fams)[0] if fams else "NONE"
    f = {kk: any(SRC_FIELDS.get(s, {}).get(kk) is True for s in fams) for kk in ("before", "after", "retention", "direction")}
    delta = "derivable_when_before_after_present" if any(SRC_FIELDS.get(s, {}).get("delta") == "derivable" for s in fams) else "no"
    if mass:
        sub, dfn, unit = "MASS_YIELD", "Food mass change across a process, reported as a weight yield factor (cooked weight / raw weight) by the source; basis recorded per EVD row.", "fraction (yield factor)"
    elif isagg:
        sub, dfn, unit = "GROUP_AGGREGATE", f"Content of a reported group aggregate ('{r['canonical_name']}') as defined by the source table; not a single analyte.", "per EVD row (mass/mass or retention fraction)"
    elif "phenol-explorer" in ",".join(r.get("external_refs", [])) or "PHENOL-EXPLORER-3.6" in fams:
        sub, dfn, unit = "PHENOLIC_COMPOUND_CONTENT", f"Content of the named compound ('{r['canonical_name'].replace(' content','')}') in the food matrix as reported by the source; basis (fresh/dry weight, per volume) recorded per EVD row.", "per EVD row (mg/100 g fresh weight | mg/100 mL | mg/100 g dry weight)"
    else:
        sub, dfn, unit = "NUTRIENT_CONTENT", f"Content of the named nutrient ('{r['canonical_name'].replace(' content','')}') in the food matrix as reported by the source table; expressed as retention in the source.", "retention fraction/percent (source); mass/mass where reported"
    gold = "NO_DUPLICATE_USE_CANONICAL" if status == "DUPLICATE" else "NO_AGGREGATE_NOT_A_SINGLE_ANALYTE" if isagg else "NO_INSUFFICIENT_EVIDENCE" if status == "MISSING_EVIDENCE" else "YES_ONLY_IF_E4_HUMAN_VERIFIED_AND_NOT_CENSORED_OR_CENSOR_AWARE"
    sim = "POTENTIAL_ONLY_WITH_A_VALIDATED_MASS_BALANCE_OR_MOISTURE_SIMULATOR" if mass else "NO_BY_DEFAULT (chemical/nutrient change needs a validated mechanism or kinetic model)"
    cov = "none" if not rows else f"{len(rows)} rows, {sig} process signatures, " + ", ".join(f"{a}:{b}" for a, b in fams.items())
    notes = []
    eq = [j for j in sv if j != k and (names[j].startswith(names[k] + ",") or names[k].startswith(names[j] + ",")) and norm(sv[j]["canonical_name"]) != norm(r["canonical_name"])]
    if eq:
        notes.append("equivalent-candidate (needs human/analytical check, NOT merged): " + ",".join(eq))
    if k in dup_of:
        notes.append(f"same analyte as {dup_of[k]}; merge evidence in MP-5A migration")
    if fams.get("BOGNAR-2002") and not mass:
        notes.append("Bognar true-retention rows: ~50% censored")
    if fams.get("USDA-RETN-R6"):
        notes.append("USDA R6: %TR vs %AR not disclosed at row level; nearest 5%; many values imputed from similar foods")
    out.append([k, r["canonical_name"], r["family"], sub, dfn, r["value_type"], unit, f["before"], f["after"], delta, f["direction"], f["retention"], "derivable_from_retention_or_before_after_when_positive" if (f["retention"] or (f["before"] and f["after"])) else "no",
                "; ".join(SRC_FIELDS[s]["meas"] for s in fams if s in SRC_FIELDS) or "none", gold, sim, "E1-E4 for evaluation; E3 allowed as training prior; censoring must be carried", len(rows), ",".join(f"{a}:{b}" for a, b in tiers.items()) or "none", cov,
                "ledger SVAR + master plan W3; SSOT 105-107 (profile definitions)", status, dup_of.get(k, ""), sig, ",".join(fams), "; ".join(notes)])

FUT = [
    ("physical", "moisture content", "PHYSICAL", "MOISTURE_WATER", "Water content of the food/matrix with stated basis (wet/dry)", "SCALAR", "g/100 g (basis required)"),
    ("physical", "water activity (aw)", "PHYSICAL", "MOISTURE_WATER", "Water activity of the matrix", "SCALAR", "dimensionless"),
    ("physical", "volume", "PHYSICAL", "GEOMETRY", "Volume of the entity", "SCALAR", "mL"),
    ("physical", "density", "PHYSICAL", "GEOMETRY", "Mass per volume of the entity", "SCALAR", "g/mL"),
    ("physical", "phase", "PHYSICAL", "PHASE", "Physical phase/phase-change status (e.g. melt, gelatinize, denature, crystallize)", "CATEGORY", "category"),
    ("physical", "viscosity", "PHYSICAL", "RHEOLOGY", "Viscosity with stated protocol", "SCALAR", "Pa.s"),
    ("physical", "texture / force / rheology", "PHYSICAL", "TEXTURE", "Instrumental texture/force/rheology measure with stated protocol", "SCALAR_OR_VECTOR", "protocol-specific"),
    ("physical", "colour L*a*b*", "PHYSICAL", "COLOUR", "CIE L*a*b* colour", "VECTOR", "L*a*b*"),
    ("physical", "browning index", "PHYSICAL", "COLOUR", "Browning index with stated definition", "SCALAR", "protocol-specific"),
    ("physical", "particle size", "PHYSICAL", "GEOMETRY", "Particle/cut size of the entity", "SCALAR_OR_DISTRIBUTION", "mm"),
    ("physical", "microstructure", "PHYSICAL", "MICROSTRUCTURE", "Microstructure descriptor with stated method", "CATEGORY_OR_VECTOR", "method-specific"),
    ("physical", "surface/core temperature", "PHYSICAL", "TEMPERATURE_PROFILE", "Surface and core temperature (trajectory) of the entity", "TRAJECTORY", "degC"),
    ("chemical", "pH / acidity", "CHEMICAL", "ACIDITY", "pH or titratable acidity of the matrix", "SCALAR", "pH units"),
    ("chemical", "precursor concentration", "CHEMICAL", "REACTION_PROGRESS", "Concentration of a named precursor", "SCALAR", "mass/mass or molar"),
    ("chemical", "product concentration", "CHEMICAL", "REACTION_PROGRESS", "Concentration of a named reaction product", "SCALAR", "mass/mass or molar"),
    ("chemical", "volatile abundance", "CHEMICAL", "VOLATILE", "Volatile compound abundance with stated sampling method", "SCALAR", "method-specific"),
    ("chemical", "oxidation markers", "CHEMICAL", "OXIDATION", "Named oxidation marker concentration", "SCALAR", "method-specific"),
    ("chemical", "reaction progress", "CHEMICAL", "REACTION_PROGRESS", "Extent of a named reaction", "SCALAR", "dimensionless"),
    ("chemical", "kinetic parameter", "CHEMICAL", "KINETICS", "Rate constant/activation energy etc. for a named reaction in a stated matrix", "SCALAR_WITH_UNCERTAINTY", "parameter-specific"),
    ("sensory", "odor/taste/texture descriptor", "SENSORY", "DESCRIPTOR", "Sensory descriptor with panel method", "CATEGORY", "category"),
    ("sensory", "sensory intensity", "SENSORY", "INTENSITY", "Intensity rating with panel method", "SCALAR", "scale-specific"),
    ("sensory", "threshold / OAV", "SENSORY", "THRESHOLD", "Odor threshold/OAV only when actually supported", "SCALAR", "mass/volume"),
    ("procedural", "form", "PROCEDURAL", "FORM", "Culinary form of the entity (whole, sliced, minced...)", "CATEGORY", "category"),
    ("procedural", "cut", "PROCEDURAL", "FORM", "Cut applied", "CATEGORY", "category"),
    ("procedural", "location", "PROCEDURAL", "LOCATION", "Where the entity is (bowl, pan, reserved...)", "CATEGORY", "category"),
    ("procedural", "mixture / intermediate identity", "PROCEDURAL", "IDENTITY", "Identity of a mixture or intermediate", "ENTITY_REF", "id"),
    ("procedural", "cooked/raw/fermented status", "PROCEDURAL", "COOKING_STATUS", "Cooked, raw, fermented status", "CATEGORY", "category"),
    ("safety", "pathogen-control condition", "SAFETY", "PATHOGEN", "Pathogen-control condition (authoritative sources only)", "CATEGORY_OR_SCALAR", "authority-specific"),
    ("safety", "allergen / cross-contact state", "SAFETY", "ALLERGEN", "Allergen presence/cross-contact state", "CATEGORY", "category"),
    ("safety", "hazardous degradation marker", "SAFETY", "HAZARD_MARKER", "Hazard marker where evidence supports it", "SCALAR", "marker-specific"),
]
for i, (fam_key, name, fam, sub, dfn, dt, unit) in enumerate(FUT, 1):
    out.append([f"SVAR-FUT-{i:03d}", name, fam, sub, dfn, dt, unit, "not_applicable_yet", "not_applicable_yet", "not_applicable_yet", "not_applicable_yet", "not_applicable_yet", "not_applicable_yet", "none yet",
                "NO_UNTIL_EVIDENCE", "NO_BY_DEFAULT" if fam in ("CHEMICAL", "SENSORY", "SAFETY") else "POTENTIAL_ONLY_WITH_A_VALIDATED_SIMULATOR", "E1-E4 for evaluation", 0, "none", "none",
                "master plan v4.0 W3; SSOT 105-107 (physical/chemical/sensory profile lists)", "FUTURE", "", 0, "", "id is provisional; no ledger record yet"])
with open(ROOT / "registry/state_variable_registry_v1.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(HDR)
    w.writerows(out)
c = Counter(o[HDR.index("status")] for o in out)
print(len(out), dict(c))
print("DUPLICATE pairs:", [(k, v, sv[k]["canonical_name"], sv[v]["canonical_name"]) for k, v in dup_of.items()])
print("ACTIVE by subfamily:", Counter(o[3] for o in out if o[HDR.index("status")] == "ACTIVE"))
