#!/usr/bin/env python3
"""STEP 07H-R finalize: integrity validators, family/leakage diagnostics, vocabulary frequency index, DATASET ledger rows, all-ledger synchronisation matrix, hash manifest, audit JSON.
Run AFTER tools/build_recipe_base.py. Never edits scientific ledgers; DATASET is the only canonical ledger appended (idempotent upsert)."""
import csv
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.evidence import condition_normalizer as N  # noqa: E402
from culinarystate.ledgers.store import LedgerStore  # noqa: E402
from culinarystate.recipes import corpus as C  # noqa: E402

RB, RS_ = ROOT / "ledgers/recipe_base", ROOT / "ledgers/recipe_semantics"
P = {"base": RB / "recipe_base_v1.parquet", "gold": RB / "gold_recipe_index_v1.parquet", "ready": RB / "recipe_simulation_readiness_v1.parquet", "freq": RB / "vocab_corpus_frequency_v1.parquet", "expr": RS_ / "recipe_expression_probe_v1.parquet",
     "cond": RS_ / "recipe_condition_mentions_v1.parquet", "ing": RS_ / "recipe_ingredient_mentions_v1.parquet", "qty": RS_ / "recipe_quantity_mentions_v1.parquet", "proc": RS_ / "recipe_process_mentions_v1.parquet"}
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
rows_of = lambda p: pq.ParquetFile(p).metadata.num_rows if Path(p).exists() else 0
jl = lambda p: sum(1 for _ in open(p, encoding="utf-8")) if Path(p).exists() else 0


def validators():
    base = pq.read_table(P["base"]).to_pandas()
    gold = pq.read_table(P["gold"]).to_pandas()
    rec = C.rec_latest()
    ids = set(base.recipe_id)
    res = {}
    res["V01_recipe_id_unique"] = bool(base.recipe_id.is_unique)
    rec_fams = ["A1_BBC_GOOD_FOOD", "WIKIBOOKS", "GUTENBERG_SEGMENT"]
    rb = base[base.source_family.isin(rec_fams)]
    res["V02_every_REC_backed_recipe_maps_to_exactly_one_REC_row"] = bool(set(rb.recipe_id) <= set(rec) and rb.recipe_id.is_unique and len(rb) == len(rec))
    comp = base[~base.source_family.isin(rec_fams)]
    res["V03_non_REC_members_documented_composites"] = bool(comp.source_family.isin(["FOODCOM", "TASTESET"]).all() and comp.source_id.str.startswith("UNREGISTERED:").all())
    res["V04_raw_content_hash_preserved_for_REC_rows"] = bool((rb.rec_content_sha256 == rb.recipe_id.map(lambda r: rec[r]["content_sha256"])).all())
    res["V05_raw_hash_and_derived_hash_present"] = bool(base.raw_hash.notna().all() and base.derived_hash.notna().all())
    res["V06_family_present_for_every_recipe"] = bool(base.recipe_family_id.notna().all())
    res["V07_gold_annotations_link_to_valid_recipe_ids"] = bool(set(gold.recipe_id) <= ids)
    ok_tier = set(base.quality_tier) <= {"SOURCE_RAW", "SILVER_AUTO", "SILVER_REVIEWED", "GOLD_LIGHT", "DEEP_GOLD", "GOLD_PENDING_INDEPENDENT_IAA", "REJECTED", "UNKNOWN"}
    res["V08_quality_tiers_in_registry"] = bool(ok_tier)
    g = base[base.quality_tier.str.startswith("GOLD") | (base.quality_tier == "DEEP_GOLD")]
    res["V09_every_gold_tier_recipe_in_gold_index_and_no_bulk_promotion"] = bool(set(g.recipe_id) <= set(gold.recipe_id) and len(g) < 100 and not (base.quality_tier == "DEEP_GOLD").any())
    res["V10_no_DEEP_GOLD_or_GOLD_LIGHT_assigned"] = bool(not base.quality_tier.isin(["DEEP_GOLD", "GOLD_LIGHT"]).any())
    for k in ("expr", "cond", "ing", "qty", "proc"):
        s = set(pq.read_table(P[k], columns=["recipe_id"]).column(0).to_pylist())
        res[f"V11_{k}_recipe_ids_valid"] = bool(s <= ids)
    ex = pq.read_table(P["expr"], columns=["expression_id", "source_plane", "observation_class"]).to_pandas()
    res["V12_expression_ids_unique"] = bool(ex.expression_id.is_unique)
    res["V13_expressions_all_TEXT_STATED_RECIPE_plane"] = bool((ex.source_plane == "RECIPE").all() and (ex.observation_class == "TEXT_STATED").all())
    cols = set(pq.ParquetFile(P["expr"]).schema.names)
    res["V14_no_evidence_tier_column_on_expressions"] = not any(c.lower() in ("tier", "evidence_tier", "e_tier") for c in cols)
    res["V15_total_base_is_not_gold"] = bool(len(g) != len(base))
    return res, base, gold


def family_leakage(base, gold):
    norm_t = lambda t: re.sub(r"[^a-z0-9]+", " ", str(t or "").lower()).strip()
    b = base[["recipe_id", "source_family", "title_raw", "recipe_family_id", "quality_tier"]].copy()
    b["nt"] = b.title_raw.map(norm_t)
    b = b[b.nt.str.len() >= 6]
    grp = b.groupby("nt").agg(n=("recipe_id", "size"), fams=("source_family", lambda s: sorted(set(s))))
    multi = grp[grp.n > 1]
    cross = multi[multi.fams.map(len) > 1]
    a1x = cross[cross.fams.map(lambda f: "A1_BBC_GOOD_FOOD" in f)]
    fam_sz = base.groupby("recipe_family_id").size()
    by_src = {}
    for f, sub in base.groupby("source_family"):
        fs = sub.groupby("recipe_family_id").size()
        by_src[f] = {"recipes": len(sub), "families": int(len(fs)), "singleton_families": int((fs == 1).sum()), "largest_family": int(fs.max())}
    gids = set(gold[gold.gold_status == "GOLD_PENDING_INDEPENDENT_IAA"].recipe_id)
    gw = []
    for rid in sorted(gids):
        r = b[b.recipe_id == rid]
        if r.empty:
            continue
        twins = b[(b.nt == r.iloc[0].nt) & (b.recipe_id != rid)]
        twins_bulk = twins[~twins.recipe_id.isin(gids)]
        if len(twins_bulk):
            gw.append({"gold_recipe_id": rid, "twin_count": int(len(twins_bulk)), "twin_source_families": sorted(set(twins_bulk.source_family)), "twin_tiers": dict(Counter(twins_bulk.quality_tier)), "twin_examples": list(twins_bulk.recipe_id[:3])})
    return {"method": "exact normalised-title match used ONLY as a leakage-warning proxy (no family algorithm invented; no thresholds)", "unique_recipes": int(len(base)), "unique_family_ids": int(base.recipe_family_id.nunique()),
            "singleton_family_count": int((fam_sz == 1).sum()), "largest_families": [[k, int(v)] for k, v in fam_sz.sort_values(ascending=False).head(5).items()], "by_source_family": by_src,
            "same_title_groups_over_1": int(len(multi)), "cross_source_title_groups": int(len(cross)), "cross_source_group_source_pairs": dict(Counter("+".join(f) for f in cross.fams)), "a1_bbc_cross_source_title_groups": int(len(a1x)),
            "gold_leakage_warnings": gw, "gold_with_bulk_title_twin": len(gw), "gold_checked": len(gids), "splits_frozen": False, "warning": "Gold recipes with bulk-corpus relatives must be excluded/grouped when splits are built; NO split is frozen here"}


def vocab_frequency():
    ing = pq.read_table(P["ing"], columns=["source_family", "candidate_ingredient_id", "link_status"]).to_pandas()
    ing = ing[ing.candidate_ingredient_id.notna() & ing.link_status.isin(["ACCEPT", "REVIEW"])]
    f1 = ing.groupby(["candidate_ingredient_id", "source_family"]).size().reset_index(name="mention_count").assign(vocab_type="ING").rename(columns={"candidate_ingredient_id": "vocab_id"})
    pr = pq.read_table(P["proc"], columns=["recipe_id", "candidate_proc_id"]).to_pandas()
    pr = pr[pr.candidate_proc_id.notna()]
    pr["source_family"] = pr.recipe_id.map(lambda r: "FOODCOM" if r.startswith("FC") else "TASTESET" if r.startswith("TS") else None)
    base = pq.read_table(P["base"], columns=["recipe_id", "source_family"]).to_pandas().set_index("recipe_id").source_family
    pr["source_family"] = pr.recipe_id.map(base)
    f2 = pr.groupby(["candidate_proc_id", "source_family"]).size().reset_index(name="mention_count").assign(vocab_type="PROC").rename(columns={"candidate_proc_id": "vocab_id"})
    q = pq.read_table(P["qty"], columns=["source_family", "unit_key"]).to_pandas()
    q = q[q.unit_key.notna()]
    f3 = q.groupby(["unit_key", "source_family"]).size().reset_index(name="mention_count").assign(vocab_type="UNIT_KEY").rename(columns={"unit_key": "vocab_id"})
    out = pd.concat([f1, f2, f3], ignore_index=True)[["vocab_type", "vocab_id", "source_family", "mention_count"]].sort_values(["vocab_type", "vocab_id", "source_family"]).reset_index(drop=True)
    out.to_parquet(P["freq"], compression="zstd", index=False)
    return {"rows": int(len(out)), "distinct_ING_matched": int(f1.vocab_id.nunique()), "distinct_PROC_matched": int(f2.vocab_id.nunique()), "distinct_UNIT_keys": int(f3.vocab_id.nunique()),
            "top_ING": f1.groupby("vocab_id").mention_count.sum().sort_values(ascending=False).head(8).to_dict(), "top_PROC": f2.groupby("vocab_id").mention_count.sum().sort_values(ascending=False).head(8).to_dict()}


def dataset_ledger(base):
    store = LedgerStore(ROOT / "ledgers/data")
    A1 = ROOT.parent / "a1" / "A1 3" / "data" / "processed" / "recipes_processed.jsonl"
    src = {"A1_BBC_GOOD_FOOD": (A1, ["SRC-000002"], "RESTRICTED (third-party copyright, SRC-000002): local analysis only; no redistribution of recipe text"), "WIKIBOOKS": (ROOT / "data/interim/wikibooks/recipes.jsonl", ["SRC-000140"], "CC BY-SA 4.0: attribution + share-alike on redistribution"),
           "GUTENBERG_SEGMENT": (ROOT / "data/interim/gutenberg/recipes.jsonl", [], "public domain per Gutenberg (per-book SRC rows SRC-000144..); segmentation heuristic ~80-85% precision on a 30-sample"), "FOODCOM": (ROOT / "data/external/foodcom/recipes.parquet", [], "CC0 declared by Kaggle uploader; authority NOT verified; derived/analysis use only, NO redistribution of text; no SRC row yet (H2 approval item)"),
           "TASTESET": (ROOT / "data/raw/tasteset/TASTEset.csv", [], "third-party research dataset; terms not re-checked here; no SRC row yet (H2 approval item)")}
    out = []
    for fam, (path, sids, allowed) in src.items():
        sub = base[base.source_family == fam]
        rid = store.ids.mint("DATASET", f"recipe_base_v1:{fam}")
        rec = {"id": rid, "record_type": "DATASET", "status": "ACTIVE", "created_by": "Kush+Claude", "provenance": {"agent": "step07hr_finalize@1", "method": "DERIVED", "source_ids": sids, "locator": str(path.relative_to(ROOT)) if str(path).startswith(str(ROOT)) else "../a1/A1 3/data/processed/recipes_processed.jsonl"},
               "verification": {"status": "UNVERIFIED"}, "name": f"recipe_base_v1 member corpus: {fam}", "release": f"recipe_base_v1/{fam}", "source_ids": sids, "sha256": sha(path), "n_rows": int(len(sub)),
               "notes": f"quality tiers {dict(Counter(sub.quality_tier))}; annotation coverage: has_conditions={int(sub.has_conditions.sum())}, has_gold_annotations={int(sub.has_gold_annotations.sum())}; allowed use/redistribution: {allowed}; locale={sub.locale.iloc[0] if len(sub) else None}"}
        st, stored = store.upsert(rec)
        out.append({"dataset_id": stored["id"], "family": fam, "action": st, "n_rows": int(len(sub))})
    return out


DESIGNED = [  # (object, path, action, reason, plane, owner)
    ("SRC", "ledgers/data/SRC.jsonl", "NO_CHANGE_REQUIRED", "488 sources unchanged; Food.com and TASTEset have NO SRC rows -> registered as UNREGISTERED:* in the recipe base; licence/ID registration is an H2 approval item (no new licence assumption)", "SOURCE", "Step 06 / H2"),
    ("REC", "ledgers/data/REC.jsonl", "REINDEXED", "immutable source memory; 89,565 unique ids indexed into recipe_base_v1 (107,760 history lines = 89,565 ids + 18,195 version-2 lines)", "RECIPE", "existing"),
    ("FAM", "ledgers/recipe_base/recipe_base_v1.parquet", "REBUILT_DERIVED", "recipe_family_id/family_method columns in recipe_base_v1: existing REC.family_id kept; Food.com/TASTEset singleton identity families (no algorithm/threshold invented)", "RECIPE", "07H-R"),
    ("ING", "ledgers/data/ING.jsonl", "VALIDATED_ONLY", "canonical ingredient vocabulary unchanged; corpus occurrence counts moved to the derived vocab_corpus_frequency_v1 index", "VOCAB", "existing"),
    ("ALIAS", "ledgers/data/ALIAS.jsonl", "VALIDATED_ONLY", "used read-only for exact alias lookup", "VOCAB", "existing"),
    ("PROC", "ledgers/data/PROC.jsonl", "VALIDATED_ONLY", "used read-only for verb-form candidates; mechanism ontology not executed", "VOCAB", "existing"),
    ("TOOL", "ledgers/data/TOOL.jsonl", "VALIDATED_ONLY", "unchanged; utensil mention extraction not run in this step", "VOCAB", "existing"),
    ("UNIT", "ledgers/data/UNIT.jsonl", "VALIDATED_ONLY", "unchanged; unit keys counted in the derived frequency index", "VOCAB", "existing"),
    ("DATASET", "ledgers/data/DATASET.jsonl", "POPULATED", "5 recipe corpus releases registered (counts, hashes, tiers, allowed use, redistribution limits)", "RECIPE", "07H-R"),
    ("recipe_base_v1", "ledgers/recipe_base/recipe_base_v1.parquet", "POPULATED", "canonical indexed view of all local recipes (pointers + hashes, no text copy)", "RECIPE", "07H-R"),
    ("gold_recipe_index_v1", "ledgers/recipe_base/gold_recipe_index_v1.parquet", "POPULATED", "existing Gold/Gold-candidate recipes linked; all AI-drafted human-reviewed -> GOLD_PENDING_INDEPENDENT_IAA", "RECIPE", "07H-R"),
    ("recipe_expression_probe_v1", "ledgers/recipe_semantics/recipe_expression_probe_v1.parquet", "POPULATED", "candidate surface expressions normalised with the final 07H parser/normalizer", "RECIPE", "07H-R"),
    ("recipe_condition_mentions_v1", "ledgers/recipe_semantics/recipe_condition_mentions_v1.parquet", "POPULATED", "TEXT_STATED procedural condition mentions (no measurements)", "RECIPE", "07H-R"),
    ("recipe_ingredient_mentions_v1", "ledgers/recipe_semantics/recipe_ingredient_mentions_v1.parquet", "POPULATED", "mentions with exact-alias link status; frozen NER/linker/router not re-run (needs GPU server run)", "RECIPE", "07H-R"),
    ("recipe_quantity_mentions_v1", "ledgers/recipe_semantics/recipe_quantity_mentions_v1.parquet", "POPULATED", "existing deterministic quantity grammar v0 per ingredient line; no CQPO preemption", "RECIPE", "07H-R"),
    ("recipe_process_mentions_v1", "ledgers/recipe_semantics/recipe_process_mentions_v1.parquet", "POPULATED", "PROC verb-form candidates (POS unchecked) + UNMAPPED leading tokens; no chemistry", "RECIPE", "07H-R"),
    ("recipe_simulation_readiness_v1", "ledgers/recipe_base/recipe_simulation_readiness_v1.parquet", "POPULATED", "text availability vector only; NOT permission to simulate", "RECIPE", "07H-R"),
    ("vocab_corpus_frequency_v1", "ledgers/recipe_base/vocab_corpus_frequency_v1.parquet", "POPULATED", "ING/PROC/UNIT occurrence counts over the recipe base by source family", "RECIPE", "07H-R"),
    ("COND", "ledgers/data/COND.jsonl", "NO_CHANGE_REQUIRED", "scientific-source conditions byte-identical; recipe text conditions live in recipe_condition_mentions_v1 (never merged)", "SCIENTIFIC", "Step 07"),
    ("EVD", "ledgers/data/EVD.jsonl", "NO_CHANGE_REQUIRED", "recipes must not create measured evidence rows; byte-identical", "SCIENTIFIC", "ES-1.1"),
    ("MEAS", "ledgers/data/MEAS.jsonl", "NO_CHANGE_REQUIRED", "scientific measurement methods; byte-identical", "SCIENTIFIC", "Step 07"),
    ("SVAR", "ledgers/data/SVAR.jsonl", "NO_CHANGE_REQUIRED", "byte-identical", "SCIENTIFIC", "MP-1"),
    ("STUDY", "ledgers/data/STUDY.jsonl", "NO_CHANGE_REQUIRED", "scientific studies; unaffected", "SCIENTIFIC", "existing"),
    ("MOL", "ledgers/data/MOL.jsonl", "NO_CHANGE_REQUIRED", "not recipe-derived", "CHEMISTRY", "existing"),
    ("IMAP", "ledgers/data/IMAP.jsonl", "NO_CHANGE_REQUIRED", "ingredient-molecule map not recipe-derived", "CHEMISTRY", "existing"),
    ("KGE", "ledgers/data/KGE.jsonl", "BLOCKED_FUTURE_STEP", "co-occurrence graph rebuild from the enlarged corpus is a separate step; occurrence index provided instead", "GRAPH", "later"),
    ("SNAP", "ledgers/data/SNAP.jsonl", "NO_CHANGE_REQUIRED", "no new scraping; snapshot ledger unchanged", "SOURCE", "existing"),
    ("EXP", "ledgers/data/EXP.jsonl", "NO_CHANGE_REQUIRED", "experiment cards unchanged", "EXPERIMENT", "existing"),
    ("ALLERGEN", "ledgers/data/ALLERGEN.jsonl", "NO_CHANGE_REQUIRED", "authority table unchanged", "VOCAB", "existing"),
    ("QNT", "ledgers/data/QNT.jsonl", "BLOCKED_FUTURE_STEP", "canonical QNT ledger belongs to the CQPO programme; syntax-level rows are in recipe_quantity_mentions_v1", "RECIPE", "CQPO"),
    ("POR", "ledgers/data/POR.jsonl", "BLOCKED_FUTURE_STEP", "portion/density evidence (CQPO); no grams invented", "SCIENTIFIC", "CQPO"),
    ("INST", "ledgers/data/INST.jsonl", "BLOCKED_FUTURE_STEP", "instruction semantic records need event extraction (Steps 16-20); raw text not copied", "RECIPE", "Steps 16-20"),
    ("ENTITY", "ledgers/data/ENTITY.jsonl", "BLOCKED_FUTURE_STEP", "no entity/state graph from this run", "RECIPE", "Steps 16-20"),
    ("EVT", "ledgers/data/EVT.jsonl", "BLOCKED_FUTURE_STEP", "no EVT rows exist; none created from a parser run (no authoritative transitions)", "RECIPE", "Steps 16-20"),
    ("STATE", "ledgers/data/STATE.jsonl", "BLOCKED_FUTURE_STEP", "no STATE rows exist; none created", "RECIPE", "Steps 16-20"),
    ("SPLIT", "ledgers/data/SPLIT.jsonl", "BLOCKED_FUTURE_STEP", "splits NOT frozen; leakage diagnostic only", "EXPERIMENT", "later"),
    ("RXN", "ledgers/data/RXN.jsonl", "BLOCKED_FUTURE_STEP", "no reaction rows from recipes", "SCIENTIFIC", "mechanism steps"),
    ("WARN", "ledgers/data/WARN.jsonl", "BLOCKED_FUTURE_STEP", "no inferred warnings", "SCIENTIFIC", "later"),
    ("HYP", "ledgers/data/HYP.jsonl", "BLOCKED_FUTURE_STEP", "no hypotheses created", "SCIENTIFIC", "later"),
    ("SIM", "ledgers/data/SIM.jsonl", "BLOCKED_FUTURE_STEP", "no simulation", "SCIENTIFIC", "later"),
    ("KINETIC", "ledgers/data/KINETIC.jsonl", "BLOCKED_FUTURE_STEP", "no kinetic parameters from recipes", "SCIENTIFIC", "later"),
    ("LOT/ENT", "ledgers/data/ENTITY.jsonl", "BLOCKED_FUTURE_STEP", "physical lot/entity layer not built", "RECIPE", "later"),
    ("GRAPH/CLM/REF/RQ/RS/GATE/MODEL/API/ALLOC", "ledgers/schemas/*.schema.json", "BLOCKED_FUTURE_STEP", "schemas designed, no data files, not recipe-derived", "META", "later"),
    ("data_source_acquisition_manifest", "registry/data_source_acquisition_manifest.csv", "NO_CHANGE_REQUIRED", "ES-1.2 manifest unchanged (no new sources)", "SOURCE", "ES-1.2"),
    ("recipe_quality_tier_registry_v1", "registry/recipe_quality_tier_registry_v1.csv", "POPULATED", "8 tiers with use/IAA rules", "RECIPE", "07H-R"),
    ("recipe_*_surface_forms_v1 (condition/quantity/temporal/process)", "registry/recipe_condition_surface_forms_v1.csv", "POPULATED", "surface-form registries from the full corpus probe", "RECIPE", "07H-R"),
]


def count(path):
    p = ROOT / path
    if "*" in path:
        return len(list((ROOT).glob(path)))
    if p.suffix == ".parquet":
        return rows_of(p)
    if p.suffix == ".csv":
        return max(0, jl(p) - 1) if p.exists() else 0
    return jl(p)


def sync_matrix(before):
    rows = []
    for obj, path, action, reason, plane, owner in DESIGNED:
        after = count(path)
        rows.append({"object": obj, "canonical_path": path, "exists": (ROOT / path).exists() or "*" in path, "row_count_before": before.get(obj, 0), "row_count_after": after, "action": action, "reason": reason, "source_plane": plane, "step_ownership": owner})
    with open(ROOT / "reports/step07/step07h_ledger_sync_matrix.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    return rows


def main():
    before = {"DATASET": jl(ROOT / "ledgers/data/DATASET.jsonl")}
    for o, pth, *_ in DESIGNED:
        if o not in before and o in ("SRC", "REC", "ING", "ALIAS", "PROC", "TOOL", "UNIT", "COND", "EVD", "MEAS", "SVAR", "STUDY", "MOL", "IMAP", "KGE", "SNAP", "EXP", "ALLERGEN"):
            before[o] = jl(ROOT / pth)
    sci_before = {n: sha(ROOT / f"ledgers/data/{n}.jsonl") for n in ("EVD", "COND", "MEAS", "SVAR", "REC", "SRC", "ING", "ALIAS", "PROC", "TOOL", "UNIT")}
    val, base, gold = validators()
    fl = family_leakage(base, gold)
    vf = vocab_frequency()
    ds = dataset_ledger(base)
    sci_after = {n: sha(ROOT / f"ledgers/data/{n}.jsonl") for n in sci_before}
    sm = sync_matrix(before)
    tiers = base.groupby(["source_family", "quality_tier"]).size().unstack(fill_value=0)
    ready = pq.read_table(P["ready"]).to_pandas()
    cov = {fam: {c: float(sub[c].mean()) for c in ("has_ingredients", "has_quantities", "has_instructions", "has_conditions", "has_existing_events", "has_gold_annotations")} for fam, sub in base.groupby("source_family")}
    ing = pq.read_table(P["ing"], columns=["source_family", "link_status"]).to_pandas()
    out = {"validators": val, "validators_all_pass": all(val.values()), "totals": {"recipe_base": int(len(base)), "by_source_family": base.source_family.value_counts().to_dict(), "unique_recipe_families": int(base.recipe_family_id.nunique()), "tiers_by_source_family": {k: {c: int(v) for c, v in r.items()} for k, r in tiers.iterrows()},
           "tier_totals": base.quality_tier.value_counts().to_dict(), "gold_index_rows": int(len(gold)), "gold_index_status": gold.gold_status.value_counts().to_dict()}, "coverage_by_source_family": cov, "family_leakage": fl,
           "readiness": {f: ready[ready.source_family == f].readiness_status.value_counts().to_dict() for f in sorted(ready.source_family.unique())}, "readiness_total": ready.readiness_status.value_counts().to_dict(),
           "ingredient_link_status": {f: ing[ing.source_family == f].link_status.value_counts().to_dict() for f in sorted(ing.source_family.unique())}, "vocab_frequency": vf, "dataset_ledger": ds,
           "scientific_and_vocab_ledgers_byte_identical": {k: sci_before[k] == sci_after[k] for k in sci_before}, "row_counts": {k: rows_of(P[k]) for k in P}, "sync_matrix_rows": len(sm)}
    out["hashes"] = {k: sha(P[k]) for k in P}
    out["normalizer_fingerprint"] = N.fingerprint()
    (ROOT / "reports/step07/step07h_full_recipe_base_audit.json").write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str))
    print(json.dumps({k: out[k] for k in ("validators", "validators_all_pass", "totals", "readiness_total", "scientific_and_vocab_ledgers_byte_identical", "row_counts")}, indent=1, default=str))


if __name__ == "__main__":
    main()
