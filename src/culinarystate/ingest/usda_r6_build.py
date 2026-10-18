"""Build ledger records (SRC, SNAP, MEAS, SVAR, COND, EVD) from USDA R6 rows.

EVD rows are tier E3 (database aggregate). Ingredient / process IDs are left null
here and linked later as new versions once ING-/PROC- registries exist (AH2: internal
identity first, external crosswalks optional).
"""
from __future__ import annotations

from collections import Counter

from culinarystate.ingest.acquire import Snapshot
from culinarystate.ingest.usda_r6 import ParsedDesc, R6Row, factor_qvalue, parse_desc
from culinarystate.ledgers.store import LedgerStore

EXTRACTION_VERSION = "usda_r6_parser@0.2"
CREATED_BY = "Kush+Claude"
FAMILY = "USDA-RETN-R6"

FOOD_GROUPS = {  # USDA SR food group codes present in R6
    "01": "Dairy and Egg Products", "05": "Poultry Products", "08": "Breakfast Cereals",
    "09": "Fruits and Fruit Juices", "10": "Pork Products", "11": "Vegetables and Vegetable Products",
    "12": "Nut and Seed Products", "13": "Beef Products", "14": "Beverages", "15": "Finfish and Shellfish Products",
    "16": "Legumes and Legume Products", "17": "Lamb, Veal, and Game Products", "20": "Cereal Grains and Pasta",
}


def _env(store: LedgerStore, prefix: str, key: str, src_ids: list[str], locator: str | None = None,
         method: str = "IMPORT") -> dict:
    prov = {"method": method, "source_ids": src_ids, "agent": f"rule:{EXTRACTION_VERSION}"}
    if locator:
        prov["locator"] = locator
    return {"id": store.ids.mint(prefix, key=key), "record_type": prefix, "status": "ACTIVE",
            "created_by": CREATED_BY, "provenance": prov, "verification": {"status": "UNVERIFIED"}}


def source_records(store: LedgerStore, snaps: list[Snapshot]) -> tuple[str, list[dict]]:
    src = {**_env(store, "SRC", "usda:retn06", [], method="MANUAL"),
           "kind": "DATABASE", "title": "USDA Table of Nutrient Retention Factors, Release 6",
           "authors": ["USDA ARS Nutrient Data Laboratory"], "year": 2007, "publisher": "USDA ARS BHNRC",
           "url": "https://www.ars.usda.gov/ARSUserFiles/80400525/Data/retn/retn06.pdf",
           "licence": "US federal government work (public domain, 17 U.S.C. §105)",
           "licence_status": "ASSUMED", "storage_rule": "COMMIT_OK", "primary_or_secondary": "SECONDARY",
           "source_family_id": FAMILY,
           "notes": "Mostly True Retention (%TR), some Apparent (%AR); nearest 5%; values >100 reported as 100; "
                    "all rows dated 09/1975 (placeholder)."}
    src_id = src["id"]
    recs = [src]
    for s in snaps:
        recs.append({**_env(store, "SNAP", f"sha256:{s.sha256}", [src_id]),
                     "source_id": src_id, "retrieved_at": s.retrieved_at, "retrieval_url": s.url,
                     "sha256": s.sha256, "bytes": s.bytes, "local_path": s.local_path,
                     "http_status": s.http_status, "source_version": "Release 6 (Dec 2007)"})
    return src_id, recs


def meas_record(store: LedgerStore, src_id: str) -> dict:
    return {**_env(store, "MEAS", "usda:retn06:retention_calc", [src_id], locator="retn06.pdf p.1 Methods"),
            "family": "CALCULATION", "basis": "UNKNOWN",
            "protocol": "%TR = (Nc*Gc)/(Nr*Gr)*100 (Murphy et al. 1975); %AR on dry-weight basis when weights missing",
            "comparability_notes": "Row-level TR vs AR not disclosed; many factors imputed from similar foods."}


def svar_records(store: LedgerStore, src_id: str, rows: list[R6Row]) -> dict[str, dict]:
    out = {}
    for nutr_no, desc in dict.fromkeys((r.nutr_no, r.nutr_desc) for r in rows):
        out[nutr_no] = {**_env(store, "SVAR", f"usda_nutr:{nutr_no}", [src_id]),
                        "canonical_name": f"{desc} content", "family": "CHEMICAL", "dimension": "mass/mass",
                        "value_type": "SCALAR", "observable_in_session": False,
                        "external_refs": [f"USDA-SR-NUTR:{nutr_no}"]}
    return out


def cond_record(store: LedgerStore, src_id: str, code: str, p: ParsedDesc) -> dict:
    mask = {"temperature": "UNKNOWN", "ph": "UNKNOWN", "moisture": "UNKNOWN", "pressure": "NOT_APPLICABLE"}
    rec = {**_env(store, "COND", f"usda_r6:{code}", [src_id], locator=f"Retn_Code {code}")}
    if p.duration_min:
        lo, hi = p.duration_min
        rec["duration"] = ({"status": "MEASURED", "value": lo, "unit": "min", "raw": p.raw} if lo == hi else
                           {"status": "RANGE", "low": lo, "high": hi, "unit": "min", "raw": p.raw})
        mask["duration"] = "MEASURED" if lo == hi else "RANGE"
    else:
        rec["duration"] = {"status": "UNKNOWN", "raw": None}
        mask["duration"] = "UNKNOWN"
    medium = p.modifiers.get("medium") or ("water" if "cooking_water" in p.modifiers else None)
    if medium:
        rec["medium"] = medium
    rec["completeness_mask"] = mask
    return rec


def evd_record(store: LedgerStore, src_id: str, r: R6Row, p: ParsedDesc, cond_id: str, svar_id: str,
               meas_id: str) -> dict:
    rf = factor_qvalue(r.factor_raw)
    censored = rf["status"] == "CENSORED"
    if rf["status"] == "MEASURED":
        direction = "DECREASE" if rf["value"] < 100 else "NO_CHANGE"
    else:
        direction = "UNKNOWN"     # capped at 100 hides whether anything was lost; blank = no data
    initial = ",".join(f for f in p.forms if f in {"raw", "fresh", "frozen", "canned", "dried", "cured"}) or None
    return {
        **_env(store, "EVD", f"usda_r6:{r.retn_code}:{r.nutr_no}", [src_id],
               locator=f"retn06.txt line {r.line_no} (Retn_Code {r.retn_code}, Nutr_No {r.nutr_no})"),
        "origin_type": "DATABASE_AGGREGATE", "source_id": src_id, "source_family_id": FAMILY,
        "study_ids": [], "study_id_status": "NOT_IDENTIFIABLE", "extraction_version": EXTRACTION_VERSION,
        "matrix": {"ingredient_id": None, "raw_name": p.matrix_raw or r.desc, "initial_state": initial,
                   "form": ",".join(p.forms) or None,
                   "food_group": FOOD_GROUPS.get(r.food_group, f"food group {r.food_group}")},
        "process": {"process_id": None, "raw_name": r.desc, "steps": list(p.steps),
                    "modifiers": dict(p.modifiers), "condition_id": cond_id,
                    "medium": p.modifiers.get("medium") or ("water" if "cooking_water" in p.modifiers else None)},
        "target": {"state_variable_id": svar_id, "raw_name": r.nutr_desc, "basis": "RETENTION_TR_OR_AR"},
        "measurement_method_id": meas_id,
        "derived": {"retention_factor": rf, "direction": direction},
        "design": "DATABASE_AGGREGATE", "tier": "E3", "applicability": "GENERIC", "censored": censored,
        "independence_group": FAMILY,
    }


def build(store: LedgerStore, rows: list[R6Row], snaps: list[Snapshot]) -> Counter:
    counts: Counter = Counter()
    src_id, src_recs = source_records(store, snaps)
    meas = meas_record(store, src_id)
    svars = svar_records(store, src_id, rows)
    parsed = {code: parse_desc(desc) for code, desc in dict.fromkeys((r.retn_code, r.desc) for r in rows)}
    conds = {code: cond_record(store, src_id, code, p) for code, p in parsed.items()}
    for rec in [*src_recs, meas, *svars.values(), *conds.values()]:
        counts[(rec["record_type"], store.upsert(rec)[0])] += 1
    for r in rows:
        rec = evd_record(store, src_id, r, parsed[r.retn_code], conds[r.retn_code]["id"],
                         svars[r.nutr_no]["id"], meas["id"])
        counts[("EVD", store.upsert(rec)[0])] += 1
    return counts
