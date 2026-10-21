#!/usr/bin/env python3
"""MP-0: build registry/ssot15_state_experiment_map.csv and registry/ssot15_similarity_registry.csv.
SX experiments are parsed from the master plan v4.0 (the SSOT v15 file itself defines no SX ids; it defines RQ16/E16/G-gates, which are listed as GATE rows).
Statuses are curated from VERIFIED artifacts (see reports/h_state/ssot15_state_program_inventory.md). FILE EXISTS != EXPERIMENT COMPLETE.
  python tools/build_ssot15_experiment_map.py"""
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN = (ROOT / "docs/plan/CulinaryState_Final_Master_Plan_SSOT15_v4_0.md").read_text().splitlines()
NS = "NOT_SPECIFIED_IN_PLAN"

BLOCK = {
    "03": ("B03 classical replication (L7-L11)", "each frozen statement reproducible from code (plan B03 gate)", "B02", "SSOT 80-98,121-127,130-132"),
    "04": ("B04 molecules and ingredients (L12)", "SSOT 183.B / 183.4 Level-12 gates", "B02,B03", "SSOT 174-183,142,143"),
    "05": ("B05 process ontology", "G16-VOCAB for processes; >=95% of Gold-seed process mentions mapped or UNMAPPED+raw verb", "B02", "SSOT 25,64,107,199,203.2,234,144.1"),
    "06": ("B06 physical/chemical state-change KB", "G14-1..12 evidence spine; G15 data gates before any transition claim", "B02,B05", "SSOT 104-113,135,143-145,197-205,208-216,219-227"),
    "07": ("B07 recipe corpus factory", "SSOT 257P checklist before scaling past 10k", "B02", "SSOT 236-240,257"),
    "08": ("B08 NER / semantic engine", "G16-SEM; H6 approval before any 'beats CoSyLab' statement", "B07", "SSOT 152-155,232,245"),
    "09": ("B09 canonical vocabulary / linking", "G16-VOCAB; ACCEPT-band precision >= pre-registered budget", "B08", "SSOT 234,238,257C"),
    "10": ("B10 quantity system (CQPO)", "G16-QTY", "B09", "SSOT 235,238,257D"),
    "11": ("B11 event/state graph", "G16-GRAPH", "B07,B08,B09,B10", "SSOT 233,107"),
    "12": ("B12 process-conditioned representation (L14)", "G14-1..12", "B04,B06,B11", "SSOT 197-205 (esp. 202.16 gates, 204 MVP/defer)"),
    "13": ("B13 transition / kinetics / sparsity (L15)", "G15-1..12 + G15-H/R/I/RXN/HYB/INV", "B06,B12", "SSOT 208-216,219-227"),
    "14": ("B14 recipe/cuisine representation and similarity (L13)", "G13-0..4 (SSOT 193)", "B04,B09,B11", "SSOT 186-194,160,264-265"),
}

# status: COMPLETE | PARTIAL | MISSING | BLOCKED_HUMAN | DONE_NEGATIVE | OBSOLETE
CUR = {
    "SX-03-01": ("MISSING", "src/culinarystate/classical/ is empty; course A2/A3 (outside repo) are assignments, not SSOT-validated reproductions", "implement n_ij / N_s / nulls as tested code (needs FlavorDB; blocked on professor access)"),
    "SX-03-02": ("MISSING", "none", "needs Indian regional recipe data + FlavorDB"),
    "SX-03-03": ("PARTIAL", "../A2/src/random_controls.py (size/frequency-controlled controls; 22/22 assignment checks); not the degree-preserving null lattice", "port into repo with exact degree-preserving controls"),
    "SX-03-04": ("MISSING", "none", "FlavorDB vs FlavorDB2 coverage; FlavorDB bulk access blocked"),
    "SX-03-05": ("PARTIAL", "../A3 copy-mutate models (624/624 assignment checks); exact Kinouchi reproduction not verified", "verify against published figures before claiming"),
    "SX-04-01": ("PARTIAL", "MOL 1,726 all with InChIKey/SMILES (PubChem); registry/molecules/unresolved_targets.csv (22 unresolved); coverage % not reported as an SX result", "compute coverage over all in-scope ingredient molecules"),
    "SX-04-02": ("MISSING", "MOL has PubChem 881-bit fp + descriptors only; no ECFP/MACCS stored; no odor/taste benchmark task", "RDKit is available in base python; needs labelled odor/taste data (blocked on FlavorDB/ChemTastesDB join)"),
    "SX-04-03": ("MISSING", "none", "depends on SX-04-02"),
    "SX-04-04": ("MISSING", "none", "depends on a molecule-set representation"),
    "SX-04-05": ("MISSING", "none", "benchmark only after SX-04-02"),
    "SX-05-01": ("PARTIAL", "reports/process_registry_v1.md: 99.3% of 39,540 BBC steps have a recognised process; 1,345 unmapped lemmas; 156 PROC (target >=300); not on a 10k-recipe sample with mapped/unmapped/ambiguous rates", "extend PROC toward >=300; report the three rates"),
    "SX-05-02": ("MISSING", "no human synonym-merge audit", "human audit (resource)"),
    "SX-05-03": ("MISSING", "hidden-step rules exist only as candidate generator; no gold missing-prerequisite set", "needs gold (pairs with SX-11-04)"),
    "SX-05-04": ("MISSING", "18 families exist; usefulness for cold-process generalisation untested", "run with cold-process split once EVD diversity grows"),
    "SX-06-01": ("MISSING", "PROC.mechanism_families on 93 PROC are AI-drafted/unverified; no evidence census by mechanism (mechanism keyword rows = 0)", "census after mechanism SVARs exist"),
    "SX-06-02": ("PARTIAL", "EVD 17,978 active, all E3 (USDA R6 7,018; Bognar 7,090; Phenol-Explorer 3,870); schema-validated; 0 human-verified", "human verification of a sample (E4 path); expand SVAR registry"),
    "SX-06-03": ("MISSING", "no volatile raw-vs-cooked rows; FDC raw/cooked pairs (867) are nutrient candidates (E6), not in EVD", "first curation cells rice/potato/broccoli/garlic/beef/wheat dough/cabbage; garlic and dough have 0 EVD rows"),
    "SX-06-04": ("MISSING", "no kinetic parameter table; acrylamide/Maillard/anthocyanin(34 rows only)/chlorophyll=0", "literature extraction + human verification"),
    "SX-06-05": ("MISSING", "pH is UNKNOWN in 100% of EVD conditions", "pH-effect evidence table"),
    "SX-06-06": ("MISSING", "alliinase/LFS, myrosinase, LOX/HPL, PPO = 0 rows", "enzymatic/cutting evidence table"),
    "SX-06-07": ("MISSING", "WARN ledger 0 rows (schema exists); troubleshooting_v1 mined statements are not evidence-backed warnings", "after SX-06-03..06"),
    "SX-06-08": ("BLOCKED_HUMAN", "verification_queue_ranked_v1.csv 634 rows; 0/40 verified", "human verification"),
    "SX-07-01": ("BLOCKED_HUMAN", "pilot_20 Gold is AI-assisted human-reviewed (not independent); Parv blind pass not done; no agreement measured", "Parv blind annotation + agreement"),
    "SX-07-02": ("MISSING", "Silver factory scaffold not built (silver/ package empty)", "after SX-07-01"),
    "SX-07-03": ("PARTIAL", "ledger schema/law validators exist (tests); Silver validators absent", "build Silver validators"),
    "SX-07-04": ("PARTIAL", "REC near-duplicate families (FAM ids, near_duplicate_pairs.csv); NER split leakage audit done in NER lane (RecipeDB3 13.5% numbers-masked family leakage); RQ16-13 not run as an experiment", "run duplicate-leakage audit across all REC sources before splits"),
    "SX-07-05": ("MISSING", "no Silver utility curve", "needs Gold held-out + Silver"),
    "SX-07-06": ("MISSING", "none", "after Silver"),
    "SX-08-01": ("COMPLETE", "reports/ner/recipedb3_matched_reproduction.md: their protocol macro 0.9543 +/- 0.0020 (5 seeds) vs published 0.9557", "none"),
    "SX-08-02": ("COMPLETE", "reports/ner/recipedb3_vulnerability_analysis.md; clean grouped split macro 0.9504; NER v1 frozen", "none"),
    "SX-08-03": ("COMPLETE", "reports/ner/span_model_bakeoff.md; tasteset_encoders_v1.md; DeBERTa-base+CRF frozen (H6-C)", "none"),
    "SX-08-04": ("DONE_NEGATIVE", "kNN-NER null; reports/ner/knowledge_augmentation_ablation.md", "none (rejected)"),
    "SX-08-05": ("MISSING", "instruction weak labels (QUANTITY, PREPROCESS, DRYFRESH, TEMPERATURE) not built", "optional; only if B11 needs instruction-level fields"),
    "SX-08-06": ("MISSING", "no Hinglish evaluation", "needs Archana's Kitchen originals"),
    "SX-08-07": ("MISSING", "position/format robustness not run", "optional"),
    "SX-08-08": ("MISSING", "LLM-Silver distillation into a small parser not run", "not justified by NER closeout; future"),
    "SX-09-01": ("MISSING", "linker is whole-string; factorized linking not tested", "future; H6-C closed NER lane"),
    "SX-09-02": ("MISSING", "no product-boundary challenge set", "future"),
    "SX-09-03": ("COMPLETE", "Recall@K + selector comparison: BGE/E5, cross-encoder, Tev1-4B, Nimble, CD-L2 on 441 and 850 human gold; BGE retained (CulinaryLinkDecision D3)", "none"),
    "SX-09-04": ("PARTIAL", "stratum (alias/NIL/long-qualified/known) results on 850 set; head/tail by frequency not computed; regional S5 unavailable", "regional data (RecipeDB API) pending"),
    "SX-09-05": ("MISSING", "ontology-drift robustness not tested", "future"),
    "SX-10-01": ("PARTIAL", "grammar coverage on BBC (116,997 lines; NUMBER 78.7%, QUALITATIVE 4.1%); no frozen gold quantity catalog exact-match", "build catalog"),
    "SX-10-02": ("COMPLETE", "tests/unit/test_quantity.py::test_no_invented_grams_for_counts_and_volumes; tests/unit/test_ledgers.py::test_no_invented_grams_from_cup", "none (keep as CI)"),
    "SX-10-03": ("MISSING", "POR ledger 0 rows; FDC portion candidates only", "after POR evidence"),
    "SX-10-04": ("MISSING", "no comparison to RecipeDB2 43.90% conversion", "needs RecipeDB2 data comparison"),
    "SX-10-05": ("MISSING", "Indian household measures interval coverage not measured", "future"),
    "SX-10-06": ("MISSING", "ALLOC/QNT ledgers 0 rows; symbolic allocation implemented in engine (symqty.py) but not evaluated as SX", "evaluate on Gold events"),
    "SX-10-07": ("MISSING", "none", "RQ16-23, far downstream"),
    "SX-11-01": ("MISSING", "no resolver comparison; compiler-vs-Gold diagnostic only (reports/del3/compiler_vs_gold_v1.md: state-field acc 0.102, alive F1 0.312, merge/split F1 0.343 on 20 AI-assisted Gold recipes)", "MP-8 on 20 Gold recipes"),
    "SX-11-02": ("MISSING", "none", "after SX-11-01"),
    "SX-11-03": ("MISSING", "108/113 coref mentions in Gold are UNKNOWN: coreference effectively unevaluated", "Gold correction"),
    "SX-11-04": ("MISSING", "OMITTED_STEP_CANDIDATE generator exists; no precision/hallucination audit", "needs gold"),
    "SX-11-05": ("PARTIAL", "engine: observation outranks prediction; sessions SES-003/011 pass; 30 sessions AI-drafted, 0 human-reviewed", "human review of sessions"),
    "SX-12-01": ("PARTIAL", "DEL-2 D0 persistence / D1 global mean / D2 process mean baselines exist on retention data (EXP-000001..4); no food-identity-only vs process-only shortcut test on state vectors", "MP-10A"),
    "SX-12-02": ("MISSING", "no thermal dose / Arrhenius features; temperature known in 33% of EVD rows", "needs condition-bearing evidence"),
    "SX-12-03": ("PARTIAL", "D5 gradient boosting on retention; TabPFN skipped; no concat/FiLM/cross-attention", "defer until G14-1..8 data gates"),
    "SX-12-04": ("MISSING", "none", "defer"),
    "SX-12-05": ("PARTIAL", "conformal coverage reported in DEL-2 (0.72-0.87 under shift); no selective-prediction on state targets", "later"),
    "SX-13-01": ("PARTIAL", "EXP-000001..4: D0-D7 on USDA R6, Phenol-Explorer, Bognar; random split gains vanish on cold splits (USDA, PE); Bognar supported incl. cold; retention only, no physical states", "extend to new evidence; D8+ only after G15-2"),
    "SX-13-02": ("MISSING", "no kinetic table or fits", "needs SX-06-04"),
    "SX-13-03": ("PARTIAL", "D7 biased MF with side info exists in DEL-2; no masked-cell/cold-pair evaluation of evidence-aware completion", "after more cells"),
    "SX-13-04": ("PARTIAL", "propensity AUC 0.81 and IPW MAE reported in DEL-2; no MNAR-corrected headline", "later"),
    "SX-13-05": ("MISSING", "no simulator data (simulated_state_changes.csv missing)", "simulation CSV path unknown; E7 never enters Gold eval"),
    "SX-13-06": ("MISSING", "needs true intermediate states", "defer"),
    "SX-13-07": ("MISSING", "none", "defer"),
    "SX-14-01": ("MISSING", "no recipe embeddings; classical A2 frequent itemsets outside repo", "defer"),
    "SX-14-02": ("MISSING", "similarity types not yet separated or tested (see similarity registry)", "MP-1 registry, then test"),
    "SX-14-03": ("MISSING", "none", "needs expert-labelled variants (shared with E13E-05)"),
    "SX-14-04": ("MISSING", "none", "defer"),
    "SX-14-05": ("MISSING", "ING_ALTERNATIVE_TO KGE (220 edges) are mined co-occurrence, not a substitution benchmark", "defer"),
}
HUMAN = {"SX-06-02", "SX-06-03", "SX-06-04", "SX-06-05", "SX-06-06", "SX-06-08", "SX-07-01", "SX-05-02", "SX-05-03", "SX-11-03", "SX-11-04", "SX-11-05", "SX-10-01"}

rows = []
SKIPPED = []
cur_block = None
for ln in PLAN:
    m = re.match(r"- \*\*(SX-(\d\d)-(\d\d))\*\* (.*)", ln)
    if not m:
        continue
    eid, b, _, q = m.groups()
    if b not in BLOCK:
        SKIPPED.append(eid)
        continue
    name, gate, dep, anchors = BLOCK[b]
    st, art, nxt = CUR.get(eid, ("MISSING", "none", NS))
    rows.append({"experiment_id": eid, "kind": "SX", "block": name, "question": q.strip(), "input": NS, "baseline": NS, "experimental_arm": NS, "metric": NS, "split": NS, "gate": gate, "dependency": dep,
                 "status": st, "existing_artifact": art, "next_action": nxt, "defined_in": "master plan v4.0 (block list)", "ssot_anchor_sections": anchors, "human_resource_needed": "YES" if eid in HUMAN else "no"})
assert len(rows) >= 60, len(rows)
print("SX outside B03-B14 skipped:", len(SKIPPED), sorted(set(x[3:5] for x in SKIPPED)))
SX_IDS = {r["experiment_id"] for r in rows}
missing_cur = set(CUR) - SX_IDS
assert not missing_cur, missing_cur

G = [
    ("G12-DEC-1..10", "Level-12 mandatory decision gates (SSOT 183.B): learned vs FP2/Morgan; single vs multi-view; mean vs learned aggregation; attention vs DeepSets; Set Transformer vs interaction graph; static vs process-conditioned; universal vs task-conditioned; frozen vs fine-tune vs PEFT; presence vs concentration/OAV; automatic vs expert validation", "B04", "MISSING", "no empirical Level-12 runs"),
    ("G12-COMPLETE (183.4)", "Level 12 empirically frozen only when registry, splits, E0-E3 baselines, z_m justified vs ECFP, aggregation ladder, confound audits, calibration/OOD, compute profile, final decision record", "B04", "MISSING", "0 of 12 items satisfied beyond MOL registry existing"),
    ("G13-0", "no learned Level-13 headline before leakage audits and explicit baselines", "B14", "MISSING", ""),
    ("G13-1", "promote a learned set aggregator only if gains exceed seed/split uncertainty on >=2 task families", "B14", "MISSING", ""),
    ("G13-2", "freeze no objective on the task it directly optimises; require transfer/non-circular secondary evaluation", "B14", "MISSING", ""),
    ("G13-3", "procedural/graph complexity promoted only if it improves process-sensitive or cross-source tasks beyond set/text baselines and survives extraction-error analysis", "B14", "MISSING", ""),
    ("G13-4", "learned z_C must add value beyond explicit cuisine fingerprints on a non-circular held-out task and be stable under matched resampling", "B14", "MISSING", ""),
]
G14 = ["Versioned process-event schema + provenance/evidence tier/missingness", "Dataset card with per-field coverage, source/study/platform distribution", "Human-verified held-out test labels", "Shortcut/null/tabular baselines completed", "Ingredient x process pair-holdout completed",
       "Source/study-disjoint evaluation completed where study IDs exist", "Condition contribution tested against label-only", "Missingness robustness reported", "Calibration / interval coverage / risk-coverage reported", "Evidence-quality stratification reported",
       "Multiple-seed / clustered uncertainty reported for learned models", "Final decision record states supported / extrapolated / abstain"]
g14st = {1: ("PARTIAL", "EVD schema + provenance + tier + censoring exist; moisture/pH/aw never populated"), 2: ("PARTIAL", "reports/DEL1_data_card.md exists; per-field coverage for new W4 fields absent"), 3: ("MISSING", "0 human-verified EVD rows"),
         4: ("PARTIAL", "DEL-2 D0-D7 done for retention"), 5: ("PARTIAL", "pair_holdout split in DEL-2"), 6: ("PARTIAL", "study-disjoint possible only for Phenol-Explorer; USDA single family"), 7: ("MISSING", ""), 8: ("MISSING", ""), 9: ("PARTIAL", "conformal coverage in DEL-2"), 10: ("MISSING", ""), 11: ("PARTIAL", "grouped CIs in DEL-2"), 12: ("MISSING", "")}
for i, t in enumerate(G14, 1):
    G.append((f"G14-{i}", t, "B12", g14st[i][0], g14st[i][1]))
G15 = {"G15-1": ("Data audit: every quantitative row has source/study, tier, units/target definition, normalization, censoring/missingness", "PARTIAL"), "G15-2": ("Canonical D0-D6 baselines on all eligible headline splits before D7+ claims", "PARTIAL"),
       "G15-3": ("Process-conditioned modelling adds value over food-identity-only on a process-disjoint split", "PARTIAL"), "G15-4": ("Identifiable kinetic fit on at least one focused dataset", "MISSING"), "G15-5": ("Condition-OOD: kinetic/hybrid beats best non-kinetic tabular on held-out temperature/condition", "MISSING"),
       "G15-6": ("Real study-disjoint calibration reported", "PARTIAL"), "G15-7": ("Abstention improves over always-answering on REAL calibration data", "MISSING"), "G15-8": ("Consistency diagnostics on valid subsets", "MISSING"), "G15-9": ("Evidence-aware D7 completion beats D5/D6 on masked-cell and cold tests or is rejected", "PARTIAL"),
       "G15-10": ("Synthetic/imputed rows improve REAL-only study-disjoint performance; no synthetic target in test/calibration", "MISSING"), "G15-11": ("Rollout trust horizon on D-C/D-D with true intermediate states", "MISSING"), "G15-12": ("Supported inverse-design case beyond nearest-evidence/random/grid", "MISSING"),
       "G15-R": ("Reproducibility: seeds, versions, hashes, splits", "PARTIAL"), "G15-H": ("Every LLM-extracted row in held-out test/calibration is human verified", "MISSING"), "G15-I": ("RAG/FlavorTwin end-to-end logs evidence class, uncertainty, abstention, provenance", "PARTIAL"),
       "G15-RXN": ("Reaction graph promoted only with evidenced species/reactions, dynamics, topology value, randomized-topology controls", "MISSING"), "G15-HYB": ("Hybrid mechanistic-neural only if it adds value beyond both parts", "MISSING"), "G15-INV": ("Inverse-design credibility ceiling", "MISSING")}
for k, (t, s) in G15.items():
    G.append((k, t, "B13", s, ""))
for k, t, s in [("G16-DATA", "Deep Gold independently annotated/adjudicated; Silver quality + duplicate controls", "MISSING"), ("G16-VOCAB", "high mention coverage; unresolved/ambiguous below threshold; fragmentation audited", "PARTIAL"), ("G16-QTY", "deterministic units correct; provenance for conversions; no fabricated quantities", "PARTIAL"),
                ("G16-SEM", "ingredient/action/state/coreference parsers meet Deep-Gold thresholds source-disjoint", "PARTIAL"), ("G16-GRAPH", "graph temporal integrity, merge/split/coref metrics", "MISSING"), ("G16-EVID", "evidence retrieval compatible Recall@K / citation support", "PARTIAL"),
                ("G16-CONFLICT", "conflicts detected/qualified", "PARTIAL"), ("G16-CAL", "confidence/abstention calibrated on held-out independent gold", "MISSING"), ("G16-TRANS", "no Level-15 fallback until G15 gates pass", "PARTIAL"), ("G16-PROV", "every claim traceable", "PARTIAL")]:
    G.append((k, t, "B16/B11", s, ""))
for gid, t, blk, st, art in G:
    rows.append({"experiment_id": gid, "kind": "GATE", "block": blk, "question": t, "input": NS, "baseline": NS, "experimental_arm": NS, "metric": NS, "split": NS, "gate": gid, "dependency": "see block", "status": st,
                 "existing_artifact": art or "none", "next_action": "see block", "defined_in": "SSOT v15 file", "ssot_anchor_sections": "SSOT 183.B/193/202.16/215.38/249", "human_resource_needed": "YES" if gid in ("G14-3", "G15-H", "G16-DATA", "G16-CAL") else "no"})
for rq, t, st, art in [("RQ16-01", "Semantic state value (B4 vs B3 ladder)", "MISSING", "EXP-000007 PLANNED, BLOCKED_HUMAN (80 questions unwritten; supported stratum n=14)"), ("RQ16-14", "State memory ablation", "MISSING", "engine exists; ablation not run"),
                       ("RQ16-15", "Direct observation override", "PARTIAL", "engine + 2 sessions"), ("RQ16-24", "Recipe graph downstream", "MISSING", ""), ("RQ16-13", "Duplicate leakage", "PARTIAL", "near-dup families"), ("RQ16-20", "Transition fallback", "PARTIAL", "DEL-2 negative cold result")]:
    rows.append({"experiment_id": rq, "kind": "RQ", "block": "state programme", "question": t, "input": NS, "baseline": NS, "experimental_arm": NS, "metric": NS, "split": NS, "gate": "G16-*", "dependency": "see blocks", "status": st,
                 "existing_artifact": art or "none", "next_action": "see MP plan", "defined_in": "SSOT v15 file 247", "ssot_anchor_sections": "SSOT 247", "human_resource_needed": "YES" if rq in ("RQ16-01",) else "no"})

cols = ["experiment_id", "kind", "block", "question", "input", "baseline", "experimental_arm", "metric", "split", "gate", "dependency", "status", "existing_artifact", "next_action", "defined_in", "ssot_anchor_sections", "human_resource_needed"]
out = ROOT / "registry/ssot15_state_experiment_map.csv"
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    w.writerows(rows)
from collections import Counter
print(len(rows), "rows;", Counter((r["kind"], r["status"]) for r in rows))
