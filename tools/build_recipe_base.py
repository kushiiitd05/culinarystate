#!/usr/bin/env python3
"""STEP 07H-R orchestrator: builds the canonical recipe base and ALL recipe-derived ledgers in one deterministic streaming pass.
Outputs (local, git-ignored parquet; manifests/hashes committed):
  ledgers/recipe_base/{recipe_base_v1,gold_recipe_index_v1,recipe_simulation_readiness_v1}.parquet
  ledgers/recipe_semantics/{recipe_expression_probe_v1,recipe_condition_mentions_v1,recipe_ingredient_mentions_v1,recipe_quantity_mentions_v1,recipe_process_mentions_v1}.parquet
  registry/recipe_{condition,quantity,temporal,process}_surface_forms_v1.csv ; reports/step07/_recipe_build_stats.json
  python tools/build_recipe_base.py [--limit N] [--out-suffix _test]"""
import argparse
import csv
import glob
import hashlib
import json
import multiprocessing as mp
import os
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.evidence import condition_normalizer as N  # noqa: E402
from culinarystate.recipes import corpus as C, ledgers as LG, probe as PR  # noqa: E402

CHUNK = 400
COND_FAMS = {"TEMPERATURE", "GAS_MARK", "QUALITATIVE_HEAT", "TIME", "TIME_QUALITATIVE", "TIME_STRUCTURED_FIELD", "ENDPOINT", "PRESSURE", "POWER", "MEDIUM"}
S, F, B, I = pa.string(), pa.float64(), pa.bool_(), pa.int64()
EXPR_SCHEMA = [("expression_id", S), ("recipe_id", S), ("recipe_family_id", S), ("source_id", S), ("source_family", S), ("source_record_id", S), ("ingredient_index", I), ("step_index", I), ("sentence_index", I), ("char_start", I), ("char_end", I),
               ("expression_family", S), ("raw_expression", S), ("raw_context_hash", S), ("text_unit", S), ("candidate_semantic_role", S), ("parser_candidate_type", S), ("normalized_variable", S), ("normalized_variable_id", S), ("normalized_value_type", S),
               ("normalized_status", S), ("canonical_value", F), ("canonical_low", F), ("canonical_high", F), ("canonical_unit", S), ("open_low", B), ("open_high", B), ("approximate", B), ("measurement_location", S), ("pressure_reference", S), ("basis", S),
               ("qualitative_value", S), ("reason_codes", S), ("mapping_id", S), ("mapping_status", S), ("compound_group_id", S), ("source_plane", S), ("observation_class", S), ("probe_version", S), ("normalizer_version", S), ("schema_version", S), ("registry_versions", S)]
ING_SCHEMA = [("mention_id", S), ("recipe_id", S), ("source_family", S), ("ingredient_index", I), ("raw_span", S), ("char_start", I), ("char_end", I), ("extraction_method", S), ("candidate_ingredient_id", S), ("link_status", S), ("link_method", S), ("link_band", S),
              ("link_confidence", F), ("router_status", S), ("quantity_raw", S), ("unit_raw", S), ("quantity_pointer", S), ("form_state_modifiers", S), ("external_label", S), ("source_plane", S)]
PROC_SCHEMA = [("recipe_id", S), ("instruction_index", I), ("sentence_index", I), ("char_start", I), ("char_end", I), ("raw_action", S), ("candidate_proc_id", S), ("proc_kind", S), ("mapping_status", S), ("modifier", S), ("endpoint_phrase", S),
               ("condition_expression_ids", S), ("source_plane", S)]
BASE_SCHEMA = [("recipe_id", S), ("source_id", S), ("source_family", S), ("source_record_id", S), ("source_version", S), ("title_raw", S), ("language", S), ("locale", S), ("cuisine_if_explicit", S), ("raw_recipe_pointer", S), ("ingredient_text_pointer", S),
               ("instruction_text_pointer", S), ("recipe_family_id", S), ("family_method", S), ("quality_tier", S), ("annotation_status", S), ("human_verification_status", S), ("independent_iaa_status", S), ("has_ingredients", B), ("has_quantities", B),
               ("has_instructions", B), ("has_conditions", B), ("has_existing_events", B), ("has_existing_states", B), ("has_gold_annotations", B), ("ner_version", S), ("linker_version", S), ("parser_version", S), ("normalizer_version", S), ("source_plane", S),
               ("licence_status", S), ("local_only", B), ("raw_hash", S), ("rec_content_sha256", S), ("derived_hash", S), ("n_ingredient_lines", I), ("n_steps", I), ("n_expressions", I)]
READY_SCHEMA = [("recipe_id", S), ("source_family", S), ("has_time", B), ("has_numeric_temperature", B), ("has_temperature_location", B), ("has_pressure", B), ("has_power", B), ("has_qualitative_heat", B), ("has_endpoint_condition", B),
                ("has_quantity_information", B), ("has_geometry_information", B), ("has_medium_information", B), ("readiness_status", S), ("note", S)]
QTY_SCHEMA = [("recipe_id", S), ("source_family", S), ("ingredient_index", I), ("mention_pointer", S), ("raw_quantity", S), ("parse_kind", S), ("number", F), ("range_low", F), ("range_high", F), ("unit_key", S), ("unit_raw", S), ("multiplier", F), ("package_key", S),
              ("qualitative_amount", S), ("qualifiers", S), ("size_word", S), ("part", S), ("locale_used", S), ("q_level", S), ("conversion_method", S), ("conversion_path", S), ("flags", S), ("mass_status", S), ("mass_value", F), ("mass_low", F), ("mass_high", F),
              ("volume_status", S), ("volume_value", F), ("volume_low", F), ("volume_high", F), ("count_status", S), ("count_value", F), ("count_low", F), ("count_high", F), ("count_unit", S), ("uncertainty", S), ("source_plane", S), ("grammar", S)]
LICENCE = {"A1_BBC_GOOD_FOOD": ("SCRAPED_PUBLIC_WEB_LICENCE_NOT_ASSUMED", True), "WIKIBOOKS": ("CC_BY_SA_PER_WIKIBOOKS_TERMS_NOT_RECHECKED_HERE", False), "GUTENBERG_SEGMENT": ("PUBLIC_DOMAIN_PER_GUTENBERG_NOT_RECHECKED_HERE", False),
           "FOODCOM": ("CC0_DECLARED_BY_UPLOADER_AUTHORITY_UNVERIFIED", True), "TASTESET": ("THIRD_PARTY_RESEARCH_DATASET_TERMS_NOT_RECHECKED_HERE", True)}
LANG = {"A1_BBC_GOOD_FOOD": ("en", "en-GB"), "WIKIBOOKS": ("en", "en"), "GUTENBERG_SEGMENT": ("en", "en-historic"), "FOODCOM": ("en", "en-US"), "TASTESET": ("en", "en")}
DIALECT_RX = {"gas_mark": re.compile(r"\bgas\s*(?:mark\s*)?\d", re.I), "fan": re.compile(r"\bfan\b", re.I), "conventional": re.compile(r"\bconventional\b", re.I), "oven_compound_180C/160C_fan/gas": re.compile(r"\d{2,3}\s*°?\s*C\s*/\s*\d{2,3}\s*°?\s*C\s*fan\s*/\s*gas", re.I),
              "fahrenheit": re.compile(r"\d\s*°?\s*F\b"), "tsp_tbsp": re.compile(r"\b(?:tsp|tbsp)\b", re.I), "until_phrase": re.compile(r"\buntil\b", re.I), "leave_to": re.compile(r"\bleave to\b", re.I), "chill": re.compile(r"\bchill\b", re.I), "cool": re.compile(r"\bcool\b", re.I),
              "level_spoon_uk": re.compile(r"\bheaped|\blevel\b", re.I), "pinch_handful": re.compile(r"\bpinch|handful\b", re.I), "g_ml_kg_unit": re.compile(r"\d\s*(?:g|ml|kg|l)\b", re.I), "range_to": re.compile(r"\d\s*(?:-|to|–)\s*\d+\s*(?:mins?|minutes|hours?)", re.I)}


def norm_pattern(raw: str) -> str:
    return re.sub(r"\d+(?:[.,]\d+)?", "#", re.sub(r"\s+", " ", raw.lower())).strip()[:60]


def load_state():
    gold = json.load(open(ROOT / "reports/step07/_gold_membership.json")) if (ROOT / "reports/step07/_gold_membership.json").exists() else {}
    return gold


def work(chunk):
    """chunk of corpus records -> aggregate rows + stats (runs in a worker process; deterministic)"""
    units_rx = PR._units()
    out = {"expr": [], "ing": [], "qty": [], "proc": [], "ready": [], "base": [], "surf": defaultdict(lambda: [0, set(), [], Counter(), None]), "dialect": Counter(), "cov": Counter(), "reasons": Counter()}
    for rec in chunk:
        gm = _GOLD.get(rec["recipe_id"], {})
        rows = PR.probe_recipe(dict(rec, family_id=rec.get("family_id")))
        for r in rows:
            r["recipe_family_id"] = rec.get("family_id")
            r["normalizer_version"] = N.NORMALIZER_VERSION
            r["schema_version"] = "condition_value_v1"
            r["registry_versions"] = "condition_variable_registry_v1;bounds_v1;notation_v1;dialect_v1;location_cues_v1"
        ing = LG.ingredient_mentions(rec, units_rx)
        eb = defaultdict(list)
        for r in rows:
            if r["step_index"] is not None:
                eb[(r["step_index"], r["sentence_index"])].append(r["expression_id"])
        proc = LG.process_mentions(rec, eb)
        rd = LG.readiness(rec, rows)
        fam_ = rec["source_family"]
        # surface forms
        for r in rows:
            k = (r["expression_family"], norm_pattern(r["raw_expression"]))
            e = out["surf"][k]
            e[0] += 1
            e[1].add(fam_)
            if len(e[2]) < 3:
                e[2].append(rec["recipe_id"])
            e[3][r["mapping_status"] or "NONE"] += 1
            e[4] = r["normalized_variable"]
            out["cov"][(fam_, r["expression_family"], r["normalized_status"])] += 1
            for code in (r["reason_codes"] or "").split(","):
                if code:
                    out["reasons"][(fam_, r["expression_family"], code)] += 1
        if fam_ == "A1_BBC_GOOD_FOOD":
            for st in rec["steps"] + rec["ingredient_lines"]:
                for k, rx in DIALECT_RX.items():
                    if rx.search(st):
                        out["dialect"][k] += 1
        derived = hashlib.sha256(json.dumps([sorted(r["expression_id"] for r in rows), N.NORMALIZER_VERSION, PR.PROBE_VERSION], sort_keys=True).encode()).hexdigest()
        cond = any(r["expression_family"] in COND_FAMS for r in rows)
        tier = gm.get("tier") or ("SILVER_AUTO" if fam_ == "A1_BBC_GOOD_FOOD" else "SOURCE_RAW")
        base = {"recipe_id": rec["recipe_id"], "source_id": rec["source_id"], "source_family": fam_, "source_record_id": rec["source_record_id"], "source_version": str((rec.get("rec") or {}).get("version") or "snapshot"), "title_raw": rec.get("title"),
                "language": LANG[fam_][0], "locale": LANG[fam_][1], "cuisine_if_explicit": rec["extra"].get("cuisine"), "raw_recipe_pointer": rec["pointer"], "ingredient_text_pointer": rec["pointer"] + "/ingredients", "instruction_text_pointer": rec["pointer"] + "/instructions",
                "recipe_family_id": rec.get("family_id"), "family_method": rec.get("family_method"), "quality_tier": tier, "annotation_status": gm.get("annotation_status") or ("RAW_SEGMENT_MISSING_LOCALLY" if rec["extra"].get("raw_segment_missing") else None) or ("MODEL_RULE_DERIVED_UNVERIFIED" if fam_ == "A1_BBC_GOOD_FOOD" else ("EXTERNAL_HUMAN_NER_BENCHMARK_THIRD_PARTY" if fam_ == "TASTESET" else "NONE")),
                "human_verification_status": gm.get("human_status") or "UNVERIFIED", "independent_iaa_status": gm.get("iaa") or "NOT_AVAILABLE", "has_ingredients": bool(rec["ingredient_lines"]) or fam_ == "GUTENBERG_SEGMENT" and bool(rec["extra"].get("legacy_ing_ids")),
                "has_quantities": any(r["expression_family"] == "QUANTITY" and r["normalized_status"] == "VALID" for r in rows), "has_instructions": bool(rec["steps"]), "has_conditions": cond, "has_existing_events": fam_ == "A1_BBC_GOOD_FOOD" or bool(gm.get("has_events")),
                "has_existing_states": bool(gm.get("has_states")), "has_gold_annotations": bool(gm), "ner_version": "A1_COURSE_NER_UNVERIFIED" if fam_ == "A1_BBC_GOOD_FOOD" else None, "linker_version": "ALIAS_EXACT_LOOKUP@1 (frozen BGE linker not re-run)", "parser_version": PR.PROBE_VERSION,
                "normalizer_version": N.NORMALIZER_VERSION, "source_plane": "RECIPE", "licence_status": LICENCE[fam_][0], "local_only": LICENCE[fam_][1], "raw_hash": C.raw_hash(rec), "rec_content_sha256": (rec.get("rec") or {}).get("content_sha256"), "derived_hash": derived, "n_ingredient_lines": len(rec["ingredient_lines"]), "n_steps": len(rec["steps"]), "n_expressions": len(rows)}
        out["base"].append(base)
        rd.update(recipe_id=rec["recipe_id"], source_family=fam_, note="readiness of the TEXT only; NOT permission to simulate")
        out["ready"].append(rd)
        out["expr"].extend(rows)
        out["ing"].extend(ing)
        out["qty"].extend(LG.quantity_mentions(rec))
        out["proc"].extend(proc)
    out["surf"] = {k: [v[0], sorted(v[1]), v[2], dict(v[3]), v[4]] for k, v in out["surf"].items()}
    return out


_GOLD = {}


def init(gold):
    global _GOLD
    _GOLD = gold
    PR._units()
    LG.vocab()


def table(rows, schema, extra=()):
    cols = {n: [r.get(n) for r in rows] for n, _ in list(schema) + list(extra)}
    return pa.table({n: pa.array(cols[n], type=t) for n, t in list(schema) + list(extra)})


def records(families, rec_all, limit, fam_of):
    for f in families:
        it = {"A1_BBC_GOOD_FOOD": lambda: C.iter_rec_corpora(rec_all, ("A1_BBC_GOOD_FOOD",)), "WIKIBOOKS": lambda: C.iter_rec_corpora(rec_all, ("WIKIBOOKS",)), "GUTENBERG_SEGMENT": lambda: C.iter_rec_corpora(rec_all, ("GUTENBERG_SEGMENT",)),
              "FOODCOM": lambda: C.iter_foodcom(), "TASTESET": lambda: C.iter_tasteset()}[f]()
        n = 0
        for rec in it:
            if limit and n >= limit:
                break
            fid, fm = fam_of(rec)
            rec["family_id"], rec["family_method"] = fid, fm
            yield rec
            n += 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="per-corpus recipe limit (test runs)")
    ap.add_argument("--suffix", default="", help="output file suffix, e.g. _test")
    ap.add_argument("--families", default="A1_BBC_GOOD_FOOD,WIKIBOOKS,GUTENBERG_SEGMENT,FOODCOM,TASTESET")
    ap.add_argument("--procs", type=int, default=4)
    a = ap.parse_args()
    t0 = time.time()
    gold = json.load(open(ROOT / "reports/step07/_gold_membership.json")) if (ROOT / "reports/step07/_gold_membership.json").exists() else {}
    sel_fam = gold.get("_family_override", {})
    rec_all = C.rec_latest()
    fam_of = lambda r: ((r["rec"]["family_id"], "REC_FAMILY_FIELD_EXISTING") if r.get("rec") else (sel_fam.get(r["recipe_id"]) or f"FAM-{r['recipe_id']}", "EXISTING_SELECTION_MANIFEST" if r["recipe_id"] in sel_fam else "SINGLETON_IDENTITY_NO_ALGORITHM"))
    members = {k: v for k, v in gold.items() if not k.startswith("_")}
    (ROOT / "ledgers/recipe_base").mkdir(parents=True, exist_ok=True)
    (ROOT / "ledgers/recipe_semantics").mkdir(parents=True, exist_ok=True)
    W = {}
    paths = {"base": ROOT / f"ledgers/recipe_base/recipe_base_v1{a.suffix}.parquet", "ready": ROOT / f"ledgers/recipe_base/recipe_simulation_readiness_v1{a.suffix}.parquet", "expr": ROOT / f"ledgers/recipe_semantics/recipe_expression_probe_v1{a.suffix}.parquet",
             "cond": ROOT / f"ledgers/recipe_semantics/recipe_condition_mentions_v1{a.suffix}.parquet", "ing": ROOT / f"ledgers/recipe_semantics/recipe_ingredient_mentions_v1{a.suffix}.parquet",
             "qty": ROOT / f"ledgers/recipe_semantics/recipe_quantity_mentions_v1{a.suffix}.parquet", "proc": ROOT / f"ledgers/recipe_semantics/recipe_process_mentions_v1{a.suffix}.parquet"}
    schemas = {"base": BASE_SCHEMA, "ready": READY_SCHEMA, "expr": EXPR_SCHEMA, "cond": EXPR_SCHEMA + [("derived_observation_class_check", S)], "ing": ING_SCHEMA, "qty": QTY_SCHEMA, "proc": PROC_SCHEMA}
    surf, dialect, cov, reasons, counts = {}, Counter(), Counter(), Counter(), Counter()
    pcount = {}
    vocab_units = LG.vocab().units
    pool = mp.get_context("spawn").Pool(a.procs, initializer=init, initargs=(members,))
    fams = a.families.split(",")

    def chunks():
        buf = []
        for rec in records(fams, rec_all, a.limit, fam_of):
            buf.append(rec)
            if len(buf) >= CHUNK:
                yield buf
                buf = []
        if buf:
            yield buf

    n_chunks = 0
    for res in pool.imap(work, chunks(), chunksize=1):
        n_chunks += 1
        ex = res["expr"]
        qrows = res["qty"]
        crows = [dict(r, derived_observation_class_check="TEXT_STATED_PROCEDURAL_OBSERVATION") for r in ex if r["expression_family"] in COND_FAMS]
        for key, rows, sch in (("base", res["base"], BASE_SCHEMA), ("ready", res["ready"], READY_SCHEMA), ("expr", ex, EXPR_SCHEMA), ("cond", crows, schemas["cond"]), ("ing", res["ing"], ING_SCHEMA), ("qty", qrows, QTY_SCHEMA), ("proc", res["proc"], PROC_SCHEMA)):
            if not rows:
                continue
            t = table(rows, sch)
            if key not in W:
                W[key] = pq.ParquetWriter(paths[key], t.schema, compression="zstd")
            W[key].write_table(t)
            counts[key] += len(rows)
        for k, v in res["surf"].items():
            e = surf.setdefault(k, [0, set(), [], Counter(), None])
            e[0] += v[0]
            e[1].update(v[1])
            if len(e[2]) < 3:
                e[2].extend(v[2][: 3 - len(e[2])])
            e[3].update(v[3])
            e[4] = v[4]
        for r in res["proc"]:
            e = pcount.setdefault((r["raw_action"].lower(), r["candidate_proc_id"], r["mapping_status"]), [0, set(), []])
            e[0] += 1
            e[1].add(r["recipe_id"].split('-')[0][:3])
            if len(e[2]) < 3:
                e[2].append(r["recipe_id"])
        dialect.update(res["dialect"])
        cov.update(res["cov"])
        reasons.update(res["reasons"])
        if n_chunks % 25 == 0:
            print(f"chunks={n_chunks} recipes={counts['base']} expr={counts['expr']} t={time.time() - t0:.0f}s", flush=True)
    pool.close()
    pool.join()
    for w in W.values():
        w.close()
    # surface-form registries
    def write_surf(name, fams_):
        rows = [(f, p, e) for (f, p), e in surf.items() if f in fams_]
        rows.sort(key=lambda x: (-x[2][0], x[0], x[1]))
        with open(ROOT / f"registry/{name}{a.suffix}.csv", "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["expression_family", "surface_form", "normalized_form", "count", "source_breadth", "source_families", "example_recipe_ids", "mapping_status", "canonical_mapping", "scope", "version"])
            for f, p, e in rows[:20000]:
                ms = e[3].most_common(1)[0][0]
                w.writerow([f, p, p, e[0], len(e[1]), ";".join(sorted(e[1])), ";".join(e[2]), ms, e[4] or "", "RECIPE_TEXT_ONLY", 1])
        return len(rows)
    n_reg = {"condition": write_surf("recipe_condition_surface_forms_v1", {"TEMPERATURE", "GAS_MARK", "QUALITATIVE_HEAT", "PRESSURE", "POWER", "MEDIUM", "ENDPOINT"}), "quantity": write_surf("recipe_quantity_surface_forms_v1", {"QUANTITY", "GEOMETRY"}),
             "temporal": write_surf("recipe_temporal_surface_forms_v1", {"TIME", "TIME_QUALITATIVE", "TIME_STRUCTURED_FIELD"})}
    prow = sorted(pcount.items(), key=lambda kv: -kv[1][0])
    with open(ROOT / f"registry/recipe_process_surface_forms_v1{a.suffix}.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["surface_form", "normalized_form", "count", "source_breadth", "example_recipe_ids", "mapping_status", "canonical_mapping", "scope", "version"])
        for (sf, pid, ms), e in prow[:20000]:
            w.writerow([sf, sf, e[0], len(e[1]), ";".join(e[2]), ms, pid or "", "RECIPE_TEXT_ONLY", 1])
    n_reg["process"] = len(prow)
    stats = {"counts": dict(counts), "elapsed_s": round(time.time() - t0), "coverage": {f"{a_}|{b}|{c}": n for (a_, b, c), n in sorted(cov.items())}, "reason_counts": {f"{a_}|{b}|{c}": n for (a_, b, c), n in reasons.most_common(400)},
             "bbc_dialect_recipe_unit_counts": dict(dialect), "surface_registry_sizes": n_reg, "paths": {k: str(v.relative_to(ROOT)) for k, v in paths.items()}}
    (ROOT / f"reports/step07/_recipe_build_stats{a.suffix}.json").write_text(json.dumps(stats, indent=1))
    print(json.dumps({k: stats[k] for k in ("counts", "elapsed_s", "surface_registry_sizes")}, indent=1))


if __name__ == "__main__":
    main()
