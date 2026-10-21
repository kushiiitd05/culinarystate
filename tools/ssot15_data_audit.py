#!/usr/bin/env python3
"""SSOT v15 data-foundation audit (read-only, nothing is created or modified except the report files).
Measures what exists across the three data planes (recipe/semantic, physical-chemical evidence, simulation) and the state-trajectory layer.
  python tools/ssot15_data_audit.py   -> reports/ssot15/data_foundation_audit.json"""
import csv
import glob
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
L = ROOT / "ledgers/data"
OUT = ROOT / "reports/ssot15"


def latest(name):
    d = {}
    n = 0
    for line in open(L / f"{name}.jsonl"):
        if line.strip():
            r = json.loads(line)
            n += 1
            d[r["id"]] = r
    return d, n


def csv_rows(p):
    with open(p, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


led = {}
R = {"ledgers": {}}
for nm in ("SRC", "SNAP", "ING", "ALIAS", "MOL", "IMAP", "PROC", "TOOL", "UNIT", "COND", "SVAR", "MEAS", "STUDY", "EVD", "REC", "KGE", "EXP", "ALLERGEN"):
    d, n = latest(nm)
    led[nm] = d
    act = [r for r in d.values() if r.get("status") == "ACTIVE"]
    R["ledgers"][nm] = {"versions_total": n, "ids_latest": len(d), "active": len(act)}
for nm in ("INST", "EVT", "STATE", "REF", "GRAPH", "ENTITY", "QNT", "POR", "ALLOC", "RXN", "WARN", "CLM", "DATASET", "SPLIT", "MODEL", "GATE", "RQ", "RS", "API"):
    R["ledgers"][nm] = {"versions_total": 0, "ids_latest": 0, "active": 0, "file": "MISSING (schema exists)" if (ROOT / f"ledgers/schemas/{nm}.schema.json").exists() else "MISSING (no schema)"}

# ---------------- EVD ----------------
ev = [r for r in led["EVD"].values() if r.get("status") == "ACTIVE"]
sv, cond, ing, proc = led["SVAR"], led["COND"], led["ING"], led["PROC"]
E = {"n": len(ev)}
E["tier"] = dict(Counter(r.get("tier") for r in ev))
E["origin_type"] = dict(Counter(r.get("origin_type") for r in ev))
E["source_family"] = dict(Counter(r.get("source_family_id") for r in ev))
E["design"] = dict(Counter(r.get("design") for r in ev))
E["verification"] = dict(Counter((r.get("verification") or {}).get("status") for r in ev))
E["censored"] = sum(1 for r in ev if r.get("censored"))
E["study_id_status"] = dict(Counter(r.get("study_id_status") for r in ev))
E["with_ingredient_id"] = sum(1 for r in ev if (r.get("matrix") or {}).get("ingredient_id"))
E["with_process_id"] = sum(1 for r in ev if (r.get("process") or {}).get("process_id"))
E["with_condition_id"] = sum(1 for r in ev if (r.get("process") or {}).get("condition_id"))
E["svar_family"] = dict(Counter((sv.get((r.get("target") or {}).get("state_variable_id")) or {}).get("family") for r in ev))
E["target_basis"] = dict(Counter((r.get("target") or {}).get("basis") for r in ev))
dk = Counter()
for r in ev:
    for k in (r.get("derived") or {}):
        dk[k] += 1
    for k in ("before", "after"):
        if r.get(k):
            dk[k] += 1
E["derived_or_value_keys"] = dict(dk)
E["unique_ingredients"] = len({(r.get("matrix") or {}).get("ingredient_id") for r in ev} - {None})
E["unique_matrix_raw_names"] = len({(r.get("matrix") or {}).get("raw_name") for r in ev})
E["unique_processes_linked"] = len({(r.get("process") or {}).get("process_id") for r in ev} - {None})
E["unique_process_step_signatures"] = len({tuple((r.get("process") or {}).get("steps") or []) for r in ev})
E["unique_svars"] = len({(r.get("target") or {}).get("state_variable_id") for r in ev})
E["unique_studies"] = len({s for r in ev for s in (r.get("study_ids") or [])})
E["unique_food_groups"] = len({(r.get("matrix") or {}).get("food_group") for r in ev})
# condition completeness
cm = defaultdict(Counter)
for r in ev:
    c = cond.get((r.get("process") or {}).get("condition_id"))
    if c:
        for ax, v in (c.get("completeness_mask") or {}).items():
            cm[ax][v] += 1
E["condition_completeness_by_axis"] = {a: dict(c) for a, c in cm.items()}
E["rows_with_temperature_known"] = sum(1 for r in ev if ((cond.get((r.get("process") or {}).get("condition_id")) or {}).get("completeness_mask") or {}).get("temperature") not in (None, "UNKNOWN", "NOT_APPLICABLE"))
E["rows_with_duration_known"] = sum(1 for r in ev if ((cond.get((r.get("process") or {}).get("condition_id")) or {}).get("completeness_mask") or {}).get("duration") not in (None, "UNKNOWN", "NOT_APPLICABLE"))
E["eval_eligible_E1_E4"] = sum(1 for r in ev if r.get("tier") in ("E1", "E2", "E3", "E4"))
E["eval_eligible_E1_E4_ingredient_and_process_linked"] = sum(1 for r in ev if r.get("tier") in ("E1", "E2", "E3", "E4") and (r.get("matrix") or {}).get("ingredient_id") and (r.get("process") or {}).get("process_id"))
E["eval_eligible_human_verified"] = sum(1 for r in ev if (r.get("verification") or {}).get("status") not in (None, "UNVERIFIED", "AI_PRECHECKED"))
R["EVD"] = E

# ---------------- SVAR / PROC / COND / ING ----------------
R["SVAR"] = {"n": len(sv), "family": dict(Counter(r.get("family") for r in sv.values())), "observable_in_session": sum(1 for r in sv.values() if r.get("observable_in_session")),
             "svars_with_evidence": len({(r.get("target") or {}).get("state_variable_id") for r in ev})}
pf = Counter(r.get("family") for r in proc.values() if r.get("status") == "ACTIVE")
R["PROC"] = {"n_active": sum(pf.values()), "families": dict(pf), "with_mechanism_families": sum(1 for r in proc.values() if r.get("mechanism_families")), "with_evidence_coverage_gt0": sum(1 for r in proc.values() if (r.get("evidence_coverage") or 0) > 0),
             "ssot_target": ">=300 process IDs"}
R["COND"] = {"n": len(cond)}
R["ING"] = {"n_active": sum(1 for r in ing.values() if r.get("status") == "ACTIVE"), "with_parent": sum(1 for r in ing.values() if r.get("parent_ids")),
            "scientific_identity_status": dict(Counter(r.get("scientific_identity_status") for r in ing.values())), "with_facets": sum(1 for r in ing.values() if r.get("facets"))}
R["MOL"] = {"n": len(led["MOL"]), "with_smiles": sum(1 for r in led["MOL"].values() if r.get("canonical_smiles")), "with_inchikey": sum(1 for r in led["MOL"].values() if r.get("inchikey")),
            "with_pubchem_fp": sum(1 for r in led["MOL"].values() if (r.get("fingerprints") or {}).get("pubchem_cactvs_881")), "with_descriptors": sum(1 for r in led["MOL"].values() if r.get("descriptors")),
            "ecfp": sum(1 for r in led["MOL"].values() if any("ecfp" in k.lower() or "morgan" in k.lower() for k in (r.get("fingerprints") or {}))),
            "atom_level_graph_objects": 0}
R["IMAP"] = {"n": len(led["IMAP"]), "relation": dict(Counter(r.get("relation") for r in led["IMAP"].values())), "unique_ingredients": len({r.get("ingredient_id") for r in led["IMAP"].values()}),
             "unique_molecules": len({r.get("molecule_id") for r in led["IMAP"].values()})}
kp = Counter(r.get("predicate") for r in led["KGE"].values() if r.get("status") == "ACTIVE")
R["KGE"] = {"n_active": sum(kp.values()), "predicates": dict(kp)}

# ---------------- evidence coverage cube (food group x process family x svar family x tier) ----------------
pfam = lambda r: (proc.get((r.get("process") or {}).get("process_id")) or {}).get("family") or "UNMAPPED"
cube = Counter()
for r in ev:
    cube[((r.get("matrix") or {}).get("food_group") or "UNKNOWN", pfam(r), (sv.get((r.get("target") or {}).get("state_variable_id")) or {}).get("family") or "UNK", r.get("tier"))] += 1
R["coverage_cube"] = {"cells_nonempty": len(cube), "rows": sum(cube.values()),
                      "cells_ge_30": sum(1 for v in cube.values() if v >= 30), "cells_ge_100": sum(1 for v in cube.values() if v >= 100), "top_cells": [{"food_group": k[0], "process_family": k[1], "svar_family": k[2], "tier": k[3], "n": v} for k, v in cube.most_common(25)]}
# ingredient x process cells with exact EVD (ING+PROC linked)
cell = Counter()
for r in ev:
    i, p = (r.get("matrix") or {}).get("ingredient_id"), (r.get("process") or {}).get("process_id")
    if i and p:
        cell[(i, p)] += 1
R["EVD_exact_ING_PROC_cells"] = {"cells": len(cell), "cells_ge_3": sum(1 for v in cell.values() if v >= 3), "cells_ge_10": sum(1 for v in cell.values() if v >= 10), "top": [{"ING": k[0], "name": ing[k[0]]["canonical_name"], "PROC": k[1], "proc": proc[k[1]]["canonical_name"], "n": v} for k, v in cell.most_common(25)]}
ing_with = {i for i, _ in cell}
proc_with = {p for _, p in cell}
# recipe-side demand: ING_PROCESSED_BY edges (recipe plane) vs EVD exact / near
dem = [r for r in led["KGE"].values() if r.get("predicate") == "ING_PROCESSED_BY" and r.get("status") == "ACTIVE"]
exact = sum(1 for r in dem if (r["subject_id"], r["object_id"]) in cell)
near = sum(1 for r in dem if (r["subject_id"], r["object_id"]) not in cell and (r["subject_id"] in ing_with or r["object_id"] in proc_with))
wsum = lambda rs: sum((r.get("support") or {}).get("recipes", 0) for r in rs)
dex = [r for r in dem if (r["subject_id"], r["object_id"]) in cell]
R["recipe_event_to_evidence_proxy"] = {"ING_PROCESSED_BY_edges": len(dem), "edges_with_exact_EVD_cell": exact, "edges_with_only_near_evidence(ING or PROC seen elsewhere)": near, "edges_no_evidence": len(dem) - exact - near,
                                       "recipe_support_total": wsum(dem), "recipe_support_with_exact_EVD": wsum(dex), "share_recipe_support_exact": round(wsum(dex) / max(1, wsum(dem)), 4)}
top_missing = sorted((r for r in dem if (r["subject_id"], r["object_id"]) not in cell), key=lambda r: -(r.get("support") or {}).get("recipes", 0))[:30]
R["top_missing_cells_by_recipe_support"] = [{"ING": r["subject_id"], "ingredient": (ing.get(r["subject_id"]) or {}).get("canonical_name"), "PROC": r["object_id"], "process": (proc.get(r["object_id"]) or {}).get("canonical_name"), "recipes": (r.get("support") or {}).get("recipes")} for r in top_missing]

# ---------------- recipe plane ----------------
rec = [r for r in led["REC"].values() if r.get("status") == "ACTIVE"]
fam = Counter()
for r in rec:
    src = (r.get("provenance") or {}).get("source_ids") or []
    ext = (r.get("external_refs") or [""])[0].split(":")[0]
    fam[ext or "?"] += 1
R["REC"] = {"n_active": len(rec), "by_external_ref_family": dict(fam), "with_cuisine": sum(1 for r in rec if r.get("cuisine")), "median_steps": sorted(r.get("n_steps") or 0 for r in rec)[len(rec) // 2],
            "verification": dict(Counter((r.get("verification") or {}).get("status") for r in rec))}
G = {}
gold = json.load(open(ROOT / "annotation/gold/foodcom_ai_assisted_v1_1/foodcom_v1_1_joint.json"))
ev_types = Counter()
nsteps = nev = nspans = 0
for rr in gold["recipes"]:
    for st in rr["steps"]:
        nsteps += 1
        nspans += len(st["spans"])
        for e in st["events"]:
            nev += 1
            ev_types[e.get("type")] += 1
G["foodcom_ai_assisted_v1_1"] = {"recipes": len(gold["recipes"]), "steps": nsteps, "events": nev, "event_types": dict(ev_types), "step_spans": nspans, "class": "AI-assisted human-reviewed development Gold (not independent)"}
ses = glob.glob(str(ROOT / "annotation/sessions/SES-*.json"))
G["scripted_sessions"] = {"n": len(ses), "human_reviewed": 0, "provenance": "AI-drafted (STATUS: 0/30 human-reviewed)"}
G["pilot_20_manifest_rows"] = len(csv_rows(ROOT / "annotation/gold/gold_v1_1_pilot_manifest.csv"))
ef = ROOT / "annotation/gold/evidence_first_expansion"
G["evidence_first_expansion"] = {"selection_manifest_rows": len(csv_rows(ef / "selection_manifest_v1.csv")), "candidate_pool_rows": len(csv_rows(ef / "candidate_pool_local.csv")), "screening_rows": len(csv_rows(ef / "screening_log.csv")),
                                 "s116_confirmation_rows": len(csv_rows(ef / "s116_eligibility_confirmation_sheet.csv")), "s116_confirmed": sum(1 for r in csv_rows(ef / "s116_eligibility_confirmation_sheet.csv") if (r.get("kush_decision_CONFIRM_or_OVERTURN") or "").strip())}
ops = [json.loads(x) for x in open(ROOT / "data/interim/openpi/food_states.jsonl")]
attr = Counter()
nst = 0
for o in ops:
    for s in o["states"]:
        nst += 1
        attr[s.get("attribute")] += 1
G["openpi_food_states"] = {"procedures": len(ops), "state_changes": nst, "with_ING_link": sum(1 for o in ops for s in o["states"] if s.get("ingredient_id")), "top_attributes": dict(attr.most_common(15)), "role": "external DEL-3 check, free-text states, not measured physics"}
R["gold_and_state_objects"] = G
# external corpora present
ext = {}
for d in sorted(glob.glob(str(ROOT / "data/external/*"))):
    ext[Path(d).name] = sum(1 for _ in Path(d).rglob("*") if _.is_file()) if Path(d).is_dir() else 1
R["data_external_file_counts"] = ext
R["data_raw_dirs"] = sorted(Path(d).name for d in glob.glob(str(ROOT / "data/raw/*")))
R["data_interim_dirs"] = sorted(Path(d).name for d in glob.glob(str(ROOT / "data/interim/*")))

# ---------------- simulation + trajectories ----------------
sim_files = [p for p in glob.glob(str(ROOT / "**/*"), recursive=True) if any(t in Path(p).name.lower() for t in ("simulat", "sim_state")) and Path(p).is_file() and "/reports/" not in p and "/docs/" not in p and "__pycache__" not in p]
R["simulation"] = {"simulated_state_changes_csv": "MISSING", "files_matching_simulat*": [Path(p).relative_to(ROOT).as_posix() for p in sim_files][:20], "source_class_module": (ROOT / "src/culinarystate/state_graph/source_class.py").exists(), "contract_doc": (ROOT / "docs/simulator_data_contract.md").exists()}
R["trajectories"] = {"recipe_state_trajectories": "MISSING", "engine_module": (ROOT / "src/culinarystate/state_graph/engine.py").exists(), "rule_compiler_module": (ROOT / "src/culinarystate/state_graph/rule_compiler.py").exists(),
                     "EVT/STATE/GRAPH/ENTITY/REF ledgers": "schemas exist, 0 persisted rows (engine keeps in-memory event-sourced state)"}
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "data_foundation_audit.json").write_text(json.dumps(R, indent=1, default=str))
print(json.dumps({k: R[k] for k in ("ledgers", "EVD", "SVAR", "PROC", "MOL", "IMAP", "KGE", "REC", "EVD_exact_ING_PROC_cells", "recipe_event_to_evidence_proxy", "gold_and_state_objects", "simulation", "trajectories")}, indent=1, default=str)[:14000])

# ---------------- B06 priority cells (SSOT 144.3) and mechanism keywords ----------------
PRI = ["rice", "potato", "broccoli", "garlic", "beef", "wheat", "dough", "cabbage"]
def evname(r):
    m = r.get("matrix") or {}
    return ((ing.get(m.get("ingredient_id")) or {}).get("canonical_name") or "") + " | " + (m.get("raw_name") or "")
pc = {}
for k in PRI:
    rows = [r for r in ev if k in evname(r).lower()]
    pc[k] = {"evd_rows": len(rows), "tiers": dict(Counter(r["tier"] for r in rows)), "svar_family": dict(Counter((sv.get((r.get("target") or {}).get("state_variable_id")) or {}).get("family") for r in rows)),
             "linked_ING_and_PROC": sum(1 for r in rows if (r.get("matrix") or {}).get("ingredient_id") and (r.get("process") or {}).get("process_id")),
             "temperature_known": sum(1 for r in rows if ((cond.get((r.get("process") or {}).get("condition_id")) or {}).get("completeness_mask") or {}).get("temperature") not in (None, "UNKNOWN", "NOT_APPLICABLE"))}
R["B06_priority_ingredients"] = pc
MECH = ["acrylamide", "maillard", "glucose", "glycine", "ascorb", "vitamin c", "anthocyan", "chlorophyll", "pheophyt", "gelation", "ph ", "alliin", "allicin", "myrosinase", "isothiocyan", "lipoxygenase", "hydroperoxide", "polyphenol oxidase", "browning", "quercetin"]
mc = {}
for m in MECH:
    mc[m] = sum(1 for r in ev if m in ((sv.get((r.get("target") or {}).get("state_variable_id")) or {}).get("canonical_name", "") + " " + ((r.get("target") or {}).get("raw_name") or "")).lower())
R["B06_mechanism_keyword_evd_rows"] = mc
R["IMAP_PROCESS_CHANGE_examples"] = [{"ING": (ing.get(r["ingredient_id"]) or {}).get("canonical_name"), "MOL": (led["MOL"].get(r["molecule_id"]) or {}).get("preferred_name"), "state": r.get("state_id_or_form")} for r in list(led["IMAP"].values()) if r.get("relation") == "PROCESS_CHANGE"][:8]
OUT.mkdir(parents=True, exist_ok=True)
(OUT / "data_foundation_audit.json").write_text(json.dumps(R, indent=1, default=str))
print("B06 priority:", json.dumps(pc)); print("mechanism keywords:", json.dumps(mc))
