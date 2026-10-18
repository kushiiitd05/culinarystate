"""Phenol-Explorer parsed pages -> ledger records (SRC per publication, STUDY, SVAR, COND, EVD).

Each publication value is one EVD row: origin PRIMARY_STUDY, imported from a curated database -> tier E3.
Kept apart on purpose:
  * before/after content (as published, unit + basis)  -> before / after / percent_change
  * PE retention factor = (after/before) * yield factor -> derived.retention_factor
  * the yield factor, which PE often borrows from another food (yield_food / yield_source in modifiers)
"""
from __future__ import annotations

import hashlib
import re
from collections import Counter

from culinarystate.evidence.conditions import extract_conditions, total_duration
from culinarystate.ingest.phenol_explorer import Details, FoodRow, PubValue
from culinarystate.ledgers.store import LedgerStore

EXTRACTION_VERSION = "phenol_explorer_parser@0.1"
CREATED_BY = "Kush+Claude"
FAMILY = "PHENOL-EXPLORER-3.6"

STEP_LEMMA = {
    "baked": "bake", "blanched": "blanch", "boiled": "boil", "canned": "can", "dehulled": "dehull",
    "soaked": "soak", "pressure-boiled": "pressure-boil", "dried": "dry", "extruded": "extrude",
    "freeze-dried": "freeze-dry", "fried": "fry", "frozen": "freeze", "grilled": "grill",
    "high-intensity pulsed electric fields": "pulsed-electric-field", "high-pressure processed": "high-pressure-process",
    "jam making": "make-jam", "microwaved": "microwave", "nixtamalized": "nixtamalize", "pasteurized": "pasteurize",
    "pressure-steamed": "pressure-steam", "puree making": "make-puree", "roasted": "roast", "steamed": "steam",
    "stored at room temperature": "store-ambient", "stored frozen": "store-frozen",
    "stored refrigerated": "store-refrigerated", "stewed": "stew", "sauteed": "saute", "toasted": "toast",
    "peeled": "peel", "juicing": "juice", "juice making": "juice", "cooked": "cook", "smoked": "smoke",
    "fermented": "ferment", "germinated": "germinate", "sprouted": "sprout",
}


def process_steps(process: str) -> list[str]:
    return [STEP_LEMMA.get(p.strip().lower(), p.strip().lower()) for p in process.split(",") if p.strip()]


def basis_of(units: str) -> str:
    u = units.lower()
    if "dry" in u:
        return "DRY"
    if "fresh" in u:
        return "FRESH_WEIGHT"
    return "UNKNOWN"


def pub_key(pub: PubValue) -> str:
    norm = re.sub(r"\W+", " ", pub.publication.lower()).strip()
    return "pe_pub:" + hashlib.sha1(norm.encode()).hexdigest()[:16]


def _year(citation: str) -> int | None:
    m = re.search(r"\((19|20)\d{2}\)", citation)
    return int(m.group(0)[1:-1]) if m else None


def _env(store: LedgerStore, prefix: str, key: str, src_ids: list[str], locator: str | None = None) -> dict:
    prov = {"method": "IMPORT", "source_ids": src_ids, "agent": f"rule:{EXTRACTION_VERSION}"}
    if locator:
        prov["locator"] = locator
    return {"id": store.ids.mint(prefix, key=key), "record_type": prefix, "status": "ACTIVE",
            "created_by": CREATED_BY, "provenance": prov, "verification": {"status": "UNVERIFIED"}}


def database_src(store: LedgerStore) -> dict:
    rec = _env(store, "SRC", "phenol-explorer:3.6", [])
    rec["provenance"]["method"] = "MANUAL"
    return {**rec, "kind": "DATABASE", "title": "Phenol-Explorer 3.6 — polyphenol retention factors (food processing)",
            "authors": ["Rothwell JA", "Perez-Jimenez J", "Neveu V", "et al."], "year": 2013,
            "url": "http://phenol-explorer.eu/retention-factors/polyphenols",
            "licence": "Free public resource; commercial use/redistribution requires authors' permission; "
                       "cite Phenol-Explorer and original publications",
            "licence_status": "VERIFIED", "storage_rule": "DERIVED_ONLY", "primary_or_secondary": "SECONDARY",
            "source_family_id": FAMILY,
            "notes": "RF = (content after / content before) * yield factor; yield factor may come from another food."}


def publication_records(store: LedgerStore, db_src: str, pub: PubValue) -> tuple[dict, dict]:
    key = pub_key(pub)
    src = {**_env(store, "SRC", key, [db_src]), "kind": "PAPER", "title": pub.publication or "UNKNOWN publication",
           "year": _year(pub.publication), "licence": "Publisher copyright (values cited via Phenol-Explorer)",
           "licence_status": "UNKNOWN", "storage_rule": "DERIVED_ONLY", "primary_or_secondary": "PRIMARY",
           "source_family_id": key,
           "notes": "DOI not yet resolved — candidate for Crossref resolution in verification queue."}
    study = {**_env(store, "STUDY", key, [src["id"]]), "source_id": src["id"], "design": "UNKNOWN"}
    return src, study


def svar_record(store: LedgerStore, db_src: str, compound: str, compound_path: str) -> dict:
    return {**_env(store, "SVAR", f"pe_compound:{compound_path or compound}", [db_src]),
            "canonical_name": f"{compound} content", "family": "CHEMICAL", "dimension": "mass/mass",
            "value_type": "SCALAR", "observable_in_session": False,
            "external_refs": [f"phenol-explorer:{compound_path}"] if compound_path else []}


def cond_record(store: LedgerStore, db_src: str, key: str, food_after: str, process: str) -> dict:
    c = extract_conditions(food_after)
    mask = {"duration": "UNKNOWN", "temperature": "UNKNOWN", "ph": "UNKNOWN", "moisture": "UNKNOWN"}
    rec = {**_env(store, "COND", key, [db_src], locator=f"food after processing: {food_after}")}
    dur = total_duration(c["durations"])
    rec["duration"] = dur
    mask["duration"] = dur["status"]
    if c["temperatures"]:
        rec["temperatures"] = c["temperatures"]
        mask["temperature"] = c["temperatures"][0]["value"]["status"]
    if c["power"]:
        rec["power"] = c["power"][0]
        mask["power"] = c["power"][0]["status"]
    if c["pressure"]:
        rec["pressure"] = c["pressure"][0]
        mask["pressure"] = c["pressure"][0]["status"]
    if "boil" in process or "blanch" in process:
        rec["medium"] = "water"
    elif "steam" in process:
        rec["medium"] = "steam"
    elif "fried" in process:
        rec["medium"] = "oil"
    rec["completeness_mask"] = mask
    return rec


def evd_record(store: LedgerStore, db_src: str, pub_src: dict, study: dict, food: FoodRow, det: Details,
               v: PubValue, idx: int, svar_id: str, cond_id: str) -> dict:
    basis = basis_of(v.units)
    before = ({"status": "MEASURED", "value": v.content_before, "unit": v.units}
              if v.content_before is not None else {"status": "UNKNOWN", "unit": v.units})
    after = ({"status": "MEASURED", "value": v.content_after, "unit": v.units}
             if v.content_after is not None else {"status": "UNKNOWN", "unit": v.units})
    derived: dict = {}
    if v.rf is not None:
        derived["retention_factor"] = {"status": "MEASURED", "value": v.rf, "unit": "fraction"}
        derived["direction"] = "DECREASE" if v.rf < 1 else ("INCREASE" if v.rf > 1 else "NO_CHANGE")
    else:
        derived["retention_factor"] = {"status": "UNKNOWN"}
        derived["direction"] = "UNKNOWN"
    if v.content_before not in (None, 0) and v.content_after is not None:
        pc = round((v.content_after - v.content_before) / v.content_before * 100, 4)
        derived["percent_change"] = {"status": "MEASURED", "value": pc, "unit": "%"}
    derived["yield_factor"] = ({"status": "MEASURED", "value": det.yield_factor, "unit": "fraction"}
                               if det.yield_factor is not None else {"status": "UNKNOWN"})
    mods = {"food_after_raw": v.food_after, "yield_food": det.yield_food, "yield_source": det.yield_source,
            "process_definition": det.process_definition or None}
    rec = _env(store, "EVD", f"pe:{food.details_path}:{idx}", [db_src, pub_src["id"]],
               locator=f"phenol-explorer.eu{food.details_path} value #{idx}")
    return {
        **rec,
        "origin_type": "PRIMARY_STUDY", "source_id": db_src, "source_family_id": FAMILY,
        "study_ids": [study["id"]], "study_id_status": "PRESENT", "extraction_version": EXTRACTION_VERSION,
        "matrix": {"ingredient_id": None, "raw_name": det.food or food.food,
                   "food_group": f"{food.food_group} / {food.food_subgroup}", "initial_state": v.food_before},
        "process": {"process_id": None, "raw_name": det.process, "steps": process_steps(det.process),
                    "modifiers": mods, "condition_id": cond_id},
        "target": {"state_variable_id": svar_id, "raw_name": det.compound or food.compound, "basis": basis},
        "before": before, "after": after, "derived": derived,
        "design": "UNKNOWN", "tier": "E3", "applicability": "EXACT", "censored": False,
        "independence_group": pub_src["source_family_id"],
    }


def build(store: LedgerStore, items: list[tuple[FoodRow, Details]]) -> Counter:
    counts: Counter = Counter()
    db = database_src(store)
    counts[("SRC", store.upsert(db)[0])] += 1
    seen: set[str] = set()
    for food, det in items:
        svar = svar_record(store, db["id"], det.compound or food.compound, food.compound_path)
        if svar["id"] not in seen:
            counts[("SVAR", store.upsert(svar)[0])] += 1
            seen.add(svar["id"])
        for idx, v in enumerate(det.values, 1):
            src, study = publication_records(store, db["id"], v)
            for r in (src, study):
                if r["id"] not in seen:
                    counts[(r["record_type"], store.upsert(r)[0])] += 1
                    seen.add(r["id"])
            cond = cond_record(store, db["id"], f"pe:{food.details_path}:{idx}", v.food_after, det.process)
            counts[("COND", store.upsert(cond)[0])] += 1
            evd = evd_record(store, db["id"], src, study, food, det, v, idx, svar["id"], cond["id"])
            counts[("EVD", store.upsert(evd)[0])] += 1
    return counts
