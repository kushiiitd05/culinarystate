"""Bognár (2002) retention rows -> SRC, SNAP, MEAS, SVAR, COND, EVD (source family BOGNAR-2002, tier E3, X5).

Food-group-level aggregates (ingredient_id stays None until the linker maps the matrix text). A value of 1.00 is
stored CENSORED (GT_CAP 0.995): the report caps at 1.00 and uses 1.00 as its "preliminary recommended" default.
"""
from __future__ import annotations

from collections import Counter

from culinarystate.evidence.conditions import extract_conditions, mask_status
from culinarystate.evidence.linker import keep_linker_fields
from culinarystate.ingest.acquire import Snapshot
from culinarystate.ledgers.store import LedgerStore

from .bognar import RetRow

FAMILY, CB, VERSION = "BOGNAR-2002", "Kush+Claude", "bognar_parser@0.1"
STEPS = {"boil": ["boil"], "steam": ["steam"], "stew, braise": ["stew"], "stew": ["stew"], "fry in pan": ["pan-fry"],
         "frying in pan": ["pan-fry"], "fry in oven": ["roast"], "in oven": ["roast"], "bake in oven": ["bake"],
         "deep fry": ["deep-fry"]}
MEDIUM = {"boil": "water", "steam": "steam", "deep fry": "oil"}
PORTION = {"A": "FOOD_EDIBLE_PART", "B": "TOTAL_DISH_INCL_COOKING_LIQUID"}


def _env(st: LedgerStore, prefix: str, key: str, src: list[str], locator: str | None = None) -> dict:
    prov = {"method": "IMPORT", "source_ids": src, "agent": f"rule:{VERSION}"}
    if locator:
        prov["locator"] = locator
    return {"id": st.ids.mint(prefix, key=key), "record_type": prefix, "status": "ACTIVE", "created_by": CB,
            "provenance": prov, "verification": {"status": "UNVERIFIED"}}


def source_records(st: LedgerStore, snap: Snapshot) -> tuple[str, list[dict]]:
    src = {**_env(st, "SRC", "bognar:bfe-r-02-03", []), "provenance": {"method": "MANUAL", "source_ids": []},
           "kind": "DATABASE", "title": "Bognár A. (2002) Tables on weight yield of food and retention factors of food "
           "constituents for the calculation of nutrient composition of cooked foods (dishes). BFE-R--02-03, "
           "Bundesforschungsanstalt für Ernährung, Karlsruhe", "authors": ["Antal Bognár"], "year": 2002,
           "url": snap.url, "publisher": "Bundesforschungsanstalt für Ernährung (via KIT repository)",
           "licence": "Institutional report, open access in KIT repository; values cited, text not redistributed",
           "licence_status": "ASSUMED", "storage_rule": "DERIVED_ONLY", "primary_or_secondary": "SECONDARY",
           "source_family_id": FAMILY,
           "notes": "Part 2 average retention factors (literature [5-9] + unpublished analyses [11]); partly overlaps "
                    "USDA literature, so independence from USDA-RETN-R6 is not guaranteed."}
    snp = {**_env(st, "SNAP", f"sha256:{snap.sha256}", [src["id"]]), "source_id": src["id"],
           "retrieved_at": snap.retrieved_at, "retrieval_url": snap.url, "sha256": snap.sha256, "bytes": snap.bytes,
           "local_path": snap.local_path, "http_status": snap.http_status, "source_version": "BFE-R--02-03 (2002)"}
    meas = {**_env(st, "MEAS", "bognar:true_retention", [src["id"]], locator="Part 2 I. Determination"),
            "family": "CALCULATION", "basis": "UNKNOWN",
            "protocol": "true retention per Bognár formula (nutrient in cooked × yield / nutrient in raw); averages",
            "comparability_notes": "A = food edible part, B = total dish incl. cooking liquid; estimated values marked "
                                   "grey in PDF (not recoverable from text) -> preface list used."}
    return src["id"], [src, snp, meas]


def build(st: LedgerStore, rows: list[RetRow], snap: Snapshot) -> Counter:
    counts: Counter = Counter()
    src_id, recs = source_records(st, snap)
    meas_id = recs[2]["id"]
    svars, conds = {}, {}
    for r in rows:
        if r.constituent not in svars:
            svars[r.constituent] = {**_env(st, "SVAR", f"bognar:{r.constituent.lower()}", [src_id]),
                                    "canonical_name": f"{r.constituent} content", "family": "CHEMICAL",
                                    "dimension": "mass/mass", "value_type": "SCALAR", "observable_in_session": False}
        ck = (r.table, r.method)
        if ck not in conds:
            c = extract_conditions(r.description)
            temps = [{**t, "location": "CORE"} for t in c["temperatures"]] if "core temperature" in r.description else \
                c["temperatures"]
            rec = {**_env(st, "COND", f"bognar:T{r.table}:{r.method}", [src_id], locator=f"Part 2 table {r.table}"),
                   "duration": {"status": "UNKNOWN", "raw": None},
                   "completeness_mask": {"duration": "UNKNOWN", "ph": "UNKNOWN", "moisture": "UNKNOWN",
                                         "temperature": mask_status(temps[0]["value"]) if temps else "UNKNOWN"}}
            if temps:
                rec["temperatures"] = temps
            if MEDIUM.get(r.method):
                rec["medium"] = MEDIUM[r.method]
            conds[ck] = rec
    for rec in [*recs, *svars.values(), *conds.values()]:
        counts[(rec["record_type"], st.upsert(rec)[0])] += 1
    for r in rows:
        if r.value == "-":
            continue
        v = float(r.value)
        rf = ({"status": "CENSORED", "raw": r.value, "unit": "fraction", "censor": {"kind": "GT_CAP", "limit": 0.995}}
              if v >= 1.0 else {"status": "MEASURED", "value": v, "unit": "fraction", "raw": r.value})
        rec = {**_env(st, "EVD", f"bognar:T{r.table}:{r.method}:{r.basis}:{r.constituent.lower()}", [src_id],
                      locator=f"bognar_2002.txt line {r.line} (Part 2 table {r.table}, {r.method}, {r.basis})"),
               "origin_type": "DATABASE_AGGREGATE", "source_id": src_id, "source_family_id": FAMILY, "study_ids": [],
               "study_id_status": "NOT_IDENTIFIABLE", "extraction_version": VERSION,
               "matrix": {"ingredient_id": None, "raw_name": r.description or r.food_group, "initial_state": "raw",
                          "form": "breaded" if "breaded" in r.description.lower() else None, "food_group": r.food_group},
               "process": {"process_id": None, "raw_name": r.method, "steps": STEPS.get(r.method, [r.method]),
                           "modifiers": {"portion": PORTION[r.basis], "estimated": r.estimated},
                           "condition_id": conds[(r.table, r.method)]["id"], "medium": MEDIUM.get(r.method)},
               "target": {"state_variable_id": svars[r.constituent]["id"], "raw_name": r.constituent,
                          "basis": "TRUE_RETENTION"},
               "measurement_method_id": meas_id,
               "derived": {"retention_factor": rf, "direction": "DECREASE" if v < 1.0 else "UNKNOWN"},
               "design": "DATABASE_AGGREGATE", "tier": "E3", "applicability": "GENERIC", "censored": v >= 1.0,
               "independence_group": FAMILY}
        counts[("EVD", st.upsert(keep_linker_fields(st.latest(rec["id"]), rec))[0])] += 1
    return counts
