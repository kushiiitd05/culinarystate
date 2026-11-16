#!/usr/bin/env python
"""S178 (T9-C09-R2): leakage audit of the D5 benchmark draft. Counts only; refuses to overwrite.

S blocks (recipes): vs the gold recipe index and its duplicate/family groups, vs the seeded Rung A dev samples (seeds
re-derived and checked against the seed hashes recorded in committed reports), vs the J4 sample, vs NER training lines
(RecipeDB3 NER splits, TASTEset corpus lines), vs the linker concept splits, vs every tracked text file that names an
S recipe id.
P/C blocks (cells): gold EVD ids vs the DEL-2 split roles (seed 7, the 29-diag pre-seal splits), vs the retrieval silver
queries (seed 20261018, reproduced and checked against data/interim/retrieval/bm25_top100.json), vs the ladder dev
questions.
Writes reports/s178/leakage_audit_d5.json (``--out`` for a new version). Reads recipe text only to count (the recipes are
Wikibooks/Gutenberg).

S178 FIX-EVAL (SCI-B E8): the text-reference scan no longer skips all of reports/s178/. Every tracked text file is scanned;
only the files in ``ID_SCAN_ALLOW`` (the EVAL lane's own inputs and outputs, which name the ids by design) are reported
apart, each with its reason, instead of being skipped.

    python tools/s178_leakage_audit_d5.py [--out reports/s178/leakage_audit_d5_v2.json]
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import re
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from culinarystate.evaluation import leakage_audit_d5 as LA  # noqa: E402
from culinarystate.evaluation import split_registry as SR  # noqa: E402
from culinarystate.transition.dataset import cells_from_rows  # noqa: E402
from culinarystate.transition.splits import all_splits  # noqa: E402

OUT = ROOT / "reports/s178/leakage_audit_d5.json"
# Files that legitimately name S recipe ids (the D5 S draft and the EVAL lane's registry / audit outputs). They are still
# scanned and listed, under their reason, never silently skipped (SCI-B E8).
ID_SCAN_ALLOW = {
    "benchmark/d5/d5_draft_S_v1.csv": "D5_S_DRAFT_THE_IDS_THEMSELVES",
    "registry/split_registry_v1.csv": "SPLIT_REGISTRY_EVAL_OUTPUT",
    "reports/s178/split_registry_units_v1.csv": "SPLIT_REGISTRY_UNIT_LISTING_RECIPE_ID_ATTRIBUTE",
    "reports/s178/split_registry_report.json": "SPLIT_REGISTRY_EVAL_OUTPUT",
    "reports/s178/split_registry_verify_S178fix.json": "SPLIT_REGISTRY_VERIFY_EVAL_OUTPUT",
    "reports/s178/leakage_audit_d5.json": "THIS_AUDIT_EARLIER_VERSION",
    "reports/s178/leakage_audit_d5_v2.json": "THIS_AUDIT",
    "reports/s178/leakage_audit_d5_findings.md": "THIS_AUDIT_FINDINGS",
    "reports/s178/h1_gold_independence_d5_draft.json": "H1_INDEPENDENCE_EVAL_OUTPUT",
    "reports/s178/h1_gold_independence_d5_draft_v2.json": "H1_INDEPENDENCE_EVAL_OUTPUT",
}
SCAN_SKIP_DIRS = {"data", "ledgers", ".git", ".venv312", "__pycache__", "node_modules", "exports"}
SCAN_SUFFIXES = (".csv", ".json", ".jsonl", ".md", ".txt", ".py", ".yaml", ".yml", ".tsv")
S_DRAFT, PC_DRAFT = ROOT / "benchmark/d5/d5_draft_S_v1.csv", ROOT / "benchmark/d5/d5_draft_PC_v1.csv"
DEV_SETS = [  # name, seed, size, families (None = all five), where the run is recorded
    ("census_1000_all_families", "20261104", 1000, None, "binding / physical / router census samples (RUN-S172..S176)"),
    ("census_1000_non_bbc_families", "20261104", 1000, ["FOODCOM", "GUTENBERG_SEGMENT", "WIKIBOOKS", "TASTESET"],
     "manjot-server runs that cannot read BBC (RUN-S174-001, S176 lanes)"),
    ("lotstate_600_wikibooks_tasteset", "20261104", 600, ["WIKIBOOKS", "TASTESET"], "RUN-S176-LOT-003"),
    ("rung_a_dryrun_1000", "dryrun-2026-11-04", 1000, None, "reports/step17/rung_a_dryrun_counts_seed_dryrun-2026-11-04.json"),
    ("d073_exploration_400", "d073-exploration-2026-11-07", 400, None, "D-073 exploration (scratch, ksh diagnosis)"),
    ("d073_precision_400", "d073-precision-2026-11-07-r1", 400, None, "D-074 R1 precision sample (60 labelled items)"),
    ("router_demo_census_1000", "router-demo-2026-11-08", 1000, None, "RUN-S171-001/002"),
]


def read(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8-sig") as fh:
        return list(csv.DictReader(fh))


def latest(name: str) -> dict:
    out = {}
    with open(ROOT / f"ledgers/data/{name}.jsonl", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                r = json.loads(line)
                out[r["id"]] = r
    return out


def seed_in_reports(seed: str) -> int:
    """Number of committed report JSONs that record sha256(seed): the check that the seed string is the one that ran."""
    h = hashlib.sha256(seed.encode()).hexdigest()
    hits = 0
    for p in sorted((ROOT / "reports").rglob("*.json")):
        try:
            hits += h in p.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
    return hits


def s_audit(report: dict) -> set[str]:
    s_rows = read(S_DRAFT)
    by_block = {b: {r["recipe_id"] for r in s_rows if r["block"] == b} for b in ("S1", "S2")}
    s_ids = by_block["S1"] | by_block["S2"]
    dm = pd.read_parquet(ROOT / "ledgers/recipe_identity/duplicate_group_members_v1.parquet",
                         columns=["recipe_id", "source_family", "duplicate_group_id", "group_size"])
    fam_of = dict(zip(dm.recipe_id, dm.source_family))
    out: dict = {"n_questions": len(s_rows), "n_recipes": len(s_ids), "by_block": {b: len(v) for b, v in by_block.items()},
                 "by_family": dict(Counter(r["source_family"] for r in s_rows)),
                 "recipes_found_in_identity_ledger": sum(i in fam_of for i in s_ids),
                 "universe": {"n_recipes": len(fam_of), "by_family": dict(Counter(fam_of.values()))}}
    # ---- gold recipes and their duplicate / family groups
    gold = pd.read_parquet(ROOT / "ledgers/recipe_base/gold_recipe_index_v1.parquet", columns=["recipe_id"])
    gold_ids = set(gold.recipe_id)
    fm = pd.read_parquet(ROOT / "ledgers/recipe_identity/recipe_family_members_v1.parquet",
                         columns=["recipe_id", "duplicate_group_id", "recipe_family_id"])
    gold_groups = set(fm[fm.recipe_id.isin(gold_ids)].duplicate_group_id)
    gold_fams = set(fm[fm.recipe_id.isin(gold_ids)].recipe_family_id)
    sm = fm[fm.recipe_id.isin(s_ids)]
    gs = dm[dm.recipe_id.isin(s_ids)]
    s_group_counts = Counter(sm.duplicate_group_id)
    out["vs_gold"] = {**LA.overlap(s_ids, gold_ids), "n_gold_recipes": len(gold_ids),
                      "s_recipes_in_gold_duplicate_group": int(sm.duplicate_group_id.isin(gold_groups).sum()),
                      "s_recipes_in_gold_family": int(sm.recipe_family_id.isin(gold_fams).sum())}
    out["near_duplicates"] = {"s_recipes_in_non_singleton_duplicate_group": int((gs.group_size > 1).sum()),
                              "s_recipes_sharing_a_duplicate_group_with_another_s_recipe": int(sum(v > 1 for v in s_group_counts.values())),
                              "note": "recipe_identity ledger is PROVISIONAL_STAR_V1 / uncalibrated; absence of near-duplicates "
                                      "there is not proof of absence"}
    # ---- seeded Rung A dev sets
    id_family = {**fam_of}
    devs = {}
    for name, seed, size, fams, where in DEV_SETS:
        sel = LA.seeded_set(id_family, seed, size, fams)
        pop = sum(1 for f in id_family.values() if fams is None or f in fams)
        eligible = sum(1 for i in s_ids if fams is None or id_family[i] in fams)
        devs[name] = {**LA.overlap(s_ids, sel), "sample_size": size, "population": pop, "n_target_in_sampled_families": eligible,
                      "expected_overlap_if_random": LA.expected_random_overlap(eligible, size, pop),
                      "n_reports_recording_seed_sha256": seed_in_reports(seed), "recorded_in": where,
                      "overlap_by_block": {b: len(v & sel) for b, v in by_block.items()}}
    out["vs_rung_a_dev_sets"] = devs
    j4 = read(ROOT / "reports/step17/j4_inverted_interval_sample_manifest_S166.csv")
    j4h = {r["recipe_id_sha256"] for r in j4}
    out["vs_j4_sample"] = {"n_j4": len(j4h), "n_overlap": sum(hashlib.sha256(i.encode()).hexdigest() in j4h for i in s_ids)}
    # ---- full-corpus label-free runs
    out["full_corpus_runs"] = {"note": "every S recipe is inside the full-corpus census / physical-layer / NER-inference runs "
                                       "(measurement, no labels, no fitting); they are not dev sets but the engine code was "
                                       "adjusted after reading their counts (D-073, S176/S177 fixes)"}
    # ---- linker concept split (ING-level)
    s1_ing = {x for r in s_rows if r["block"] == "S1" for x in r["gold_ingredient_ids"].split("|") if x}
    pc_rows = read(PC_DRAFT)
    pc_ing = {r["ingredient_id"] for r in pc_rows if r["ingredient_id"]}
    out["vs_linker_concept_split"] = {
        "rule": "tools/build_linker_data.py: sha256('LINK-v1|ING-id') bucket, test >= 0.8, dev >= 0.7, else train (concept-grouped)",
        "s1_gold_ing_ids": dict(Counter(LA.linker_split(i) for i in s1_ing)), "n_s1_gold_ing_ids": len(s1_ing),
        "pc_question_ing_ids": dict(Counter(LA.linker_split(i) for i in pc_ing)), "n_pc_question_ing_ids": len(pc_ing),
        "reading": "the learned linker saw the aliases of train-bucket concepts; the S1 scorer links answers with the "
                   "rule-based lexicon, so this is exposure of the id space, not of recipe text"}
    report["s_blocks"] = out
    return s_ids


def corpus_lines(s_ids: set[str]) -> tuple[dict, set[str]]:
    from culinarystate.recipes import corpus
    got = {}
    for r in corpus.iter_rec_corpora(families=("WIKIBOOKS", "GUTENBERG_SEGMENT")):
        if r["recipe_id"] in s_ids:
            got[r["recipe_id"]] = r
    taste = set()
    for r in corpus.iter_tasteset():
        taste.update(LA.norm_line(x) for x in r.get("ingredient_lines") or [])
    return got, taste


def ner_audit(report: dict, s_ids: set[str]) -> None:
    got, taste = corpus_lines(s_ids)
    lines = [x for r in got.values() for x in (r.get("ingredient_lines") or [])]
    df = pd.read_csv(ROOT / "data/external/recipedb3_ner/Ingredient_Annotated_Dataset.csv").dropna()
    df = df[df.sentence.astype(str).str.strip() != ""].reset_index(drop=True)
    ok = df.apply(lambda r: len(str(r.sentence).split()) == len(str(r.tags).split()), axis=1)
    df = df[ok].reset_index(drop=True)
    spl = json.loads((ROOT / "benchmark/ner/splits/recipedb3_split_v1.json").read_text())["indices"]
    per = {}
    for role in ("train", "calibration", "dev", "test"):
        per[role] = LA.exact_line_matches(lines, {LA.norm_line(df.sentence[i]) for i in spl[role]})
    prop = {}
    text_props = Counter()
    for r in got.values():
        text_props["recipes_with_zero_ingredient_lines" if not r.get("ingredient_lines") else "recipes_with_ingredient_lines"] += 1
    prop.update(text_props)
    report["s_blocks"]["vs_ner_training_lines"] = {
        "recipes_loaded": len(got), **prop, "s_ingredient_lines": len(lines),
        "recipedb3_by_split_exact_normalised_line_matches": per,
        "tasteset_corpus_any_split_exact_normalised_line_matches": LA.exact_line_matches(lines, taste),
        "tasteset_matched_line_token_counts": sorted(len(LA.norm_line(x).split()) for x in lines if LA.norm_line(x) in taste),
        "family_overlap": {"s_recipes_in_tasteset_family": sum(r["source_family"] == "TASTESET" for r in got.values())},
        "reading": "Gutenberg segments carry steps only (no ingredient lines), so a line-overlap test has no denominator "
                   "for them; the DeBERTa-CRF NER is trained on RecipeDB3 NER + TASTEset lines and is not used by Rung A"}
    # ---- text-reference scan (every tracked text file; the allow-listed EVAL files are reported apart, not skipped)
    report["s_blocks"]["tracked_files_naming_s_recipe_ids"] = {
        **id_reference_scan(ROOT, s_ids),
        "reading": "surface-form registries list at most 3 example recipe ids per form (corpus-wide counts, not a tuning pool); "
                   "registry/recipes/*_ingredient_links_v1.csv are the ledger-build recipe->ING links for the same recipes; "
                   "allow_listed files name the ids by design (the D5 S draft and EVAL's registry / audit outputs)"}


def id_reference_scan(root: Path, s_ids: set[str], allow: dict[str, str] | None = None) -> dict:
    """Files (relative path -> number of distinct S recipe ids named) under ``root``. Allow-listed files are counted in their
    own block with the reason; nothing under reports/ is skipped (SCI-B E8)."""
    allow = ID_SCAN_ALLOW if allow is None else allow
    pat = re.compile("|".join(re.escape(i) for i in sorted(s_ids)))
    hits, allowed = {}, {}
    for p in root.rglob("*"):
        if not p.is_file() or set(p.relative_to(root).parts) & SCAN_SKIP_DIRS or p.stat().st_size > 80_000_000:
            continue
        if p.suffix.lower() not in SCAN_SUFFIXES:
            continue
        rel = p.relative_to(root).as_posix()
        try:
            n = len(set(pat.findall(p.read_text(encoding="utf-8", errors="ignore"))))
        except OSError:
            continue
        if not n:
            continue
        if rel in allow:
            allowed[rel] = {"distinct_s_ids": n, "reason": allow[rel]}
        else:
            hits[rel] = n
    return {"n_files": len(hits), "files_with_distinct_s_ids": dict(sorted(hits.items())),
            "n_allow_listed_files": len(allowed), "allow_listed_files": dict(sorted(allowed.items())),
            "n_files_under_reports_s178": sum(k.startswith("reports/s178/") for k in hits),
            "scope": "ALL_TRACKED_TEXT_FILES_EXCEPT_DATA_LEDGERS_VENV_GIT; ALLOW_LIST_REPORTED_NOT_SKIPPED"}


def pc_audit(report: dict) -> None:
    pc = read(PC_DRAFT)
    evd, cond, proc = latest("EVD"), latest("COND"), latest("PROC")
    active = [r for r in evd.values() if r["status"] == "ACTIVE"]
    gold = {}
    for r in pc:
        for k in ("gold_evd_ids", "gold_evd_ids_2"):
            for i in r[k].split("|"):
                if i:
                    gold.setdefault(r["block"], set()).add(i)
    all_gold = set().union(*gold.values())
    out: dict = {"n_cells": len(pc), "by_block": dict(Counter(r["block"] for r in pc)),
                 "gold_evd_ids": {"distinct": len(all_gold), "by_block": {b: len(v) for b, v in sorted(gold.items())},
                                  "p3_cells_without_gold_rows": sum(1 for r in pc if r["block"] == "P3")}}
    # ---- DEL-2 / 29-diag pre-seal splits (seed 7)
    role_of: dict[str, dict[str, str]] = {}
    for fam in sorted({r["source_family_id"] for r in active}):
        df = cells_from_rows(active, cond, fam).df
        if not len(df):
            continue
        splits, _ = all_splits(df, 7)
        ids = df["evd_id"].to_numpy()
        for s in splits:
            m = role_of.setdefault(s.name, {})
            for role, idx in (("train", s.train), ("cal", s.cal), ("test", s.test)):
                m.update({ids[i]: role for i in idx})
    n_cells_rows = {i for m in role_of.values() for i in m}
    out["vs_del2"] = {"del2_pool_rows": len(n_cells_rows), "gold_ids_in_del2_pool": len(all_gold & n_cells_rows),
                      "by_split": {name: dict(Counter(m.get(i, "not_in_split") for i in all_gold)) for name, m in sorted(role_of.items())},
                      "reading": "DEL-2 trained and scored on every ACTIVE retention row (random / pair / matrix / process / study "
                                 "splits, seed 7), so every D5 gold row was a DEL-2 train, calibration or test row. No D5 gold "
                                 "row was held out from DEL-2 because D5 did not exist then; a learned model fitted on DEL-2 "
                                 "rows cannot be scored on these cells without a new hold-out."}
    # ---- retrieval silver
    spec = importlib.util.spec_from_file_location("_erss", ROOT / "tools/export_retrieval_set.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    queries = LA.silver_queries(active, seed=mod.SEED, max_cells=mod.MAX_CELLS)
    from culinarystate.retrieval.retriever import EvidenceRetriever
    pfam = {p["id"]: p["family"] for p in proc.values()}
    retr = EvidenceRetriever(active, cond, pfam)
    stored = json.loads((ROOT / "data/interim/retrieval/bm25_top100.json").read_text())
    pname = {p["id"]: p["canonical_name"] for p in proc.values()}
    checked = same = 0
    for i, q in enumerate(queries[:30]):
        m_, p_, t_ = q["cell"]
        text = f"How much {t_.split(',')[0]} is left in {m_.split(',')[0]} after it is {mod.PAST.get(pname.get(p_, p_), pname.get(p_, p_))}?"
        top = [j for j, _ in retr.bm25.top(text, 100)]
        checked += 1
        same += top == stored[f"SQ-{i:04d}"]
    silver_rel = {i for q in queries for i in q["relevant"]}
    silver_cells = {q["cell"] for q in queries}
    ing_proc_silver = {((evd[i]["matrix"].get("ingredient_id")), q["cell"][1]) for q in queries for i in q["relevant"]
                       if evd[i]["matrix"].get("ingredient_id")}
    gold_cells = {LA.evd_cell(evd[i]) for i in all_gold}
    d5_pairs = {(r["ingredient_id"], r["process_id"]) for r in pc if r["ingredient_id"]} | \
               {(r["ingredient_id"], r["process_id_2"]) for r in pc if r["ingredient_id"] and r["process_id_2"]}
    out["vs_retrieval_silver"] = {
        "n_queries": len(queries), "reproduction_check": {"bm25_top100_compared": checked, "identical": same},
        "silver_relevant_rows": len(silver_rel), "gold_ids_in_silver_relevant_rows": len(all_gold & silver_rel),
        "gold_evd_cells": len(gold_cells), "gold_cells_that_are_silver_query_cells": len(gold_cells & silver_cells),
        "d5_ingredient_process_pairs": len(d5_pairs), "d5_pairs_present_in_silver_relevant_rows": len(d5_pairs & ing_proc_silver),
        "by_block_gold_ids_in_silver_relevant": {b: len(v & silver_rel) for b, v in sorted(gold.items())},
        "reading": "the silver set (600 templated cell questions, seed 20261018, >= 2 rows per cell) ranked BM25 / dense / "
                   "hybrid retrievers on these same EVD rows (dev signal for the R2 RRF choice, Hit@k on cell relevance)"}
    # ---- P3 spill: ingredient x process pairs that have rows for another target
    pair_any = {((e["matrix"].get("ingredient_id")), (e["process"] or {}).get("process_id")) for e in active
                if e["matrix"].get("ingredient_id")}
    p3 = [r for r in pc if r["block"] == "P3"]
    out["p3_spill"] = {"p3_cells": len(p3), "p3_ing_process_pairs_with_rows_for_another_target":
                       sum((r["ingredient_id"], r["process_id"]) in pair_any for r in p3)}
    # ---- ladder dev questions
    ladder_q = {LA.norm_line(json.loads(x)["question"]) for x in (ROOT / "reports/del5/ladder_v2_qwen7b.jsonl").read_text().splitlines()}
    ladder_q |= {LA.norm_line(x) for x in re.findall(r'"([^"]{15,120}\?)"', (ROOT / "tools/run_ladder.py").read_text())}
    out["vs_ladder_dev_questions"] = {"n_ladder_questions": len(ladder_q), "exact_question_matches":
                                      sum(LA.norm_line(r["question"]) in ladder_q for r in pc)}
    report["pc_blocks"] = out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args(argv)
    out_path = Path(a.out)
    if out_path.exists():
        sys.exit(f"refusing to overwrite {out_path}")
    report: dict = {"tool": "tools/s178_leakage_audit_d5.py", "module": LA.VERSION, "status": "AI_DRAFTED_COUNTS_ONLY",
                    "inputs": {"s_draft_sha256": SR.sha256_file(S_DRAFT), "pc_draft_sha256": SR.sha256_file(PC_DRAFT),
                               "evd_sha256": SR.sha256_file(ROOT / "ledgers/data/EVD.jsonl")}}
    s_ids = s_audit(report)
    ner_audit(report, s_ids)
    pc_audit(report)
    report["tool_version"] = "s178-leakage-audit-d5-0.2.0-draft"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    data = (json.dumps(report, indent=1, sort_keys=True) + "\n").encode()
    with open(out_path, "xb") as fh:
        fh.write(data)
    print(json.dumps({"out": str(out_path), "sha256": hashlib.sha256(data).hexdigest()}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
