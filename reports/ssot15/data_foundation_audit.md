# MILESTONE: SSOT15 H_STATE DATA FOUNDATION AUDIT

Generated from the repo by `tools/ssot15_data_audit.py` (numbers: `reports/ssot15/data_foundation_audit.json`). Read-only audit; no model run, nothing created in the ledgers. SSOT sources read: master plan v4.0 Part I (state-change KB, tiers E1-E7), B05/B06/B07, W3-W9 (SVAR, EVD record, dynamic state compiler), AN (state-engine contract), AX7/AY (data releases, ledger system), `docs/simulator_data_contract.md` (S116). `STATUS.md` is stale (2026-10-19); the live log is `WORKLOG.md` (S128).

## Verdict in one paragraph
Plane A (recipes) is large but mostly Silver/unverified with a 20-recipe AI-assisted Gold; Plane B (physical/chemical evidence) has 17,978 rows that are **all tier E3, all chemical-or-yield, none human-verified, no E1/E2/E4, almost no physical variables, and no moisture/pH/aw condition values**; Plane C (state trajectories) and the simulation plane **do not exist as data** (engine code exists; EVT/STATE/GRAPH/RXN ledgers have schemas and 0 rows). Real-recipe events meet exact EVD cells for **3.0% of recipe-process support**. A DATA-TRANSITION-BENCH can be formed today only as a thin chemical-retention benchmark from E3 aggregate data, not as a physical state-change benchmark. Training H_STATE now would train on what the ledger cannot support.

## RECIPE DATASETS (Plane A, DATA-SEM-*)
| Object | State | Size / note |
|---|---|---|
| REC ledger | EXISTS, 100% UNVERIFIED | 89,565 active: BBC Good Food 11,934 (A1), Wikibooks 3,676, Gutenberg silver 73,955; 60,144 with cuisine; median 6 steps. Near-duplicate families built (leakage-safe grouping). |
| DATA-SEM-GOLD (Deep Gold, target 750-1000) | PARTIAL | 20 recipes (Food.com), AI-assisted human-reviewed development Gold, **not independent**: 157 steps, 310 events (Transform 155, Merge 114, Transfer 17, Split 13, Reserve 8, Recombine 2, Discard 1), 989 step spans. Independent double annotation of events: NOT done (Parv's blind pass blocked on human). |
| Gold-Light (3-5k) | MISSING | none |
| Silver (10k pilot -> 100k) | PARTIAL / OBSOLETE-ish | Gutenberg/Wikibooks silver REC rows exist (D-012 silver) but **no semantic Silver** (INST/EVT per recipe): Silver factory scaffold not built; EXP for RQ16-09/11 not run. |
| NER spans for ingredient lines | EXISTS (closed) | CulinaryNER-KF v1 (frozen); TASTEset, RecipeDB3 benchmark gold; RecipeDB3 API/licence still pending. |
| Food.com evidence-first expansion | PARTIAL, BLOCKED_HUMAN | 210 screened candidates, 54 selected, 84-row S116 sheet: **0/84 confirmed by Kush**. Food.com cannot enter Gold until confirmed. |
| Scripted sessions | PARTIAL | 30 AI-drafted, 0 human-reviewed. |

## PHYSICAL/CHEMICAL DATASETS (Plane B, DATA-EVIDENCE)
EVD: 18,156 ids, **17,978 active**. All **E3**. Origin: DATABASE_AGGREGATE 14,108 (USDA R6 7,018; Bognar 2002 7,090 incl. 496 physical weight-yield rows) + PRIMARY_STUDY 3,870 (Phenol-Explorer; 125 studies). Verification: UNVERIFIED 14,108, AI_PRECHECKED 3,870, **human-verified 0**. Censored 5,894 (33%).
- Linked: ingredient_id 11,569 (64%); process_id 17,821 (99%); condition_id 100%; 165 distinct ingredients, 619 raw matrix names, 76 food groups, **36 distinct processes** of 156, 70 process-step signatures, 224 SVARs, 125 studies.
- SVAR families: CHEMICAL 223, **PHYSICAL 1**; SENSORY/PROCEDURAL/SAFETY: 0. EVD rows: chemical 17,482 / physical 496 / other 0.
- Values: `retention_factor` 17,482 rows, `yield_factor` 4,366, `percent_change` 3,859, explicit `before`/`after` values only **3,870** (Phenol-Explorer). No LOD/LOQ columns (censoring encoded in derived), no `prior_state_id`, no `matrix_id`.
- Condition completeness: temperature known 6,015 (33%), duration known 3,083 (17%), **moisture UNKNOWN 100%, pH UNKNOWN 100%**, pressure measured 129.
- Mechanism evidence: acrylamide, Maillard, glycine, chlorophyll, gelation, pH, alliinase/allicin, myrosinase, isothiocyanate, LOX, PPO/browning = **0 rows**; vitamin C ~423, quercetin 381, anthocyanin 34.
- B06 priority cells (E3 rows; ING+PROC linked; temperature known): beef 1,785 (939; 1,261), potato 840 (838; 94), broccoli 355 (49; 6), cabbage 256 (46; 12), rice 129 (24; 0), wheat 35 (35; 1), **garlic 0, wheat dough 0**.
- Molecules: MOL 1,726 (SMILES/InChIKey/descriptors/PubChem 881-bit fp all 100%; **no ECFP stored, no atom/bond graph objects**); IMAP 30,294: PRESENCE 29,656, MEASURED_CONCENTRATION 219, **PROCESS_CHANGE 419**; 313 ingredients, 1,659 molecules. **RXN: 0 rows.**
- KG layer (KGE): 45,201 active, 22 predicates (ING_PROCESSED_BY 2,132, PROC_USES_TOOL 543, PROC_ENDPOINT_STATE 47, ...). Recipe-derived, not chemistry.

## SIMULATION DATASETS (Plane, E7)
**MISSING.** No `simulated_state_changes.csv` or any simulator output exists in this repo or in ~/Desktop, ~/Downloads, ~/Documents (searched by name). Only the contract (`docs/simulator_data_contract.md`, commit 74c41cf) and `state_graph/source_class.py` (STRUCTURAL_RECIPE / COMPOSITION / MEASURED_TRANSITION / COMPILED_RETENTION / KINETIC / MOLECULAR_PRIOR / SENSORY_PRIOR / MODEL_GENERATED / SYNTHETIC) exist; `TransitionInput` enforces that recipe text cannot carry a magnitude. **If a physical-simulation CSV was produced elsewhere (another machine/session/Parv), I need its path; I will not recreate it from memory.**

## STATE/EVENT DATASETS (Plane C)
| Object | State |
|---|---|
| INST / EVT / STATE / REF / GRAPH / ENTITY / QNT / POR / ALLOC ledgers | schemas exist, **0 persisted rows** (NEEDS MIGRATION from the in-memory engine) |
| `recipe_state_trajectories` | MISSING |
| Engine (`state_graph/engine.py`, `rule_compiler.py`, `symqty.py`, `source_class.py`) | EXISTS: event-sourced, replay verified; compiler on Gold: state-field acc 0.106, alive F1 0.294 (S109) |
| OpenPI food states | EXISTS (external, free-text): 197 procedures, 7,629 state changes (3,898 with ING link); attributes: location 1,475, temperature 823, weight 602, cleanness 600, composition 362, moisture 295, texture 249... Not measured physics. |
| H_STATE (EXP-000007) | PLANNED / BLOCKED_HUMAN: authoring pack built; 80 questions not written; supported stratum max n=14 (S114). |

## COVERAGE
CURRENT ROW COUNTS: ledgers table in the JSON (REC 89,565; EVD 17,978; KGE 45,201; IMAP 30,294; ALIAS 4,103; COND 4,414; PROC 156; ING 2,048; TOOL 119; MOL 1,726; SVAR 224; STUDY 125; MEAS 3; EXP 7).
INGREDIENT COVERAGE: 2,048 ING; EVD touches 165 (8%); IMAP 313.
PROCESS COVERAGE: 156 PROC (SSOT target >= 300); 18 families; 93 with mechanism families (AI-drafted, unverified); EVD touches 36 (23%).
STATE VARIABLE COVERAGE: 224 SVAR, 1 physical; no moisture, aw, texture, colour L*a*b*, phase, temperature profile, geometry SVARs.
EVIDENCE TIER DISTRIBUTION: E1 0 | E2 0 | E3 17,978 | E4 0 | E5 0 | E6 (FDC pairs 867 / 16,365 ratios exist as candidates, not in EVD) | E7 0.
COVERAGE CUBE (food group x process family x svar family x tier): 245 non-empty cells, 108 with >= 30 rows, 58 with >= 100; all CHEMICAL (except 496 yield rows). ING x PROC exact cells: 485, of which 306 have >= 3 rows and 220 >= 10 (top: strawberry/chill 273, pork/simmer 260, potato/boil 224, pork/brown 208).
RECIPE -> EVENT COVERAGE: the corpus yields 2,132 ING_PROCESSED_BY edges (259,027 recipe-support).
EVENT -> EVIDENCE COVERAGE: exact EVD cell for 24 of 2,132 edges (3.0% of recipe support); only near evidence (ING or PROC seen elsewhere) 738; **no evidence 1,370**. On the 20 Gold recipes: 8 recipes / 14 supported (recipe, cell) pairs.
EVENT -> SIMULATION COVERAGE: 0 (no simulation data).
UNKNOWN RATE: moisture 100%, pH 100%; temperature 67%; duration 83% of EVD rows.
TOP MISSING (by recipe support): salt/season 20,293; cream/beat 14,019; pepper/season 11,497; butter/melt 7,293; onion/chop 4,077; baking powder/bake 3,935; parsley/chop; flour/sift; yolk/beat; water/soak. Many are mechanical or seasoning events where the honest answer is a physical (geometry/phase/emulsion/foam) state variable that no ledger row currently represents.

## EXISTING vs MISSING CSVs
EXISTING: registry/{evidence,ingredients,processes,recipes,molecules,kg,tools,units,allergens}/*.csv (incl. `fdc_raw_cooked_pairs_v1.csv` 867 pairs E6-candidates, `verification_queue_ranked_v1.csv` 634 literature rows 0 verified, `evd_ingredient_link_decisions.csv`), `reports/h_state/hstate_missing_evidence_cells_ranked.csv` (58 real targets), coverage-lift forecasts, annotation Gold JSON.
MISSING: `simulated_state_changes.csv`; canonical `evd` export with the W4 columns; SVAR physical/sensory/procedural/safety expansion; RXN rows; `recipe_state_trajectories`; DATA-* release manifests (DATASET/SPLIT ledgers empty); molecule similarity hierarchy tables; Gold-Light; semantic Silver.

## SCHEMA CONFLICTS (current EVD vs SSOT W4 / the requested canonical table)
| Requested/SSOT field | Current | Action |
|---|---|---|
| evidence_tier | `tier` | rename in export, keep ledger name |
| provenance_class | `origin_type` + `provenance.method` | map, add explicit class |
| measurement_id / method | `measurement_method_id` (3 MEAS only) | expand MEAS (3 -> per-platform) |
| matrix_id, prior_state_id | `matrix.{ingredient_id, raw_name, form, initial_state}` (ingredient_id 64%) | add matrix_id + prior_state vocabulary |
| before/after/delta/log_fold_change/value_low/high | `before/after` only for 3,870 PE rows; `derived.retention_factor/percent_change/yield_factor` | derive log-fold-change; fill from retention where defined; keep UNKNOWN |
| LOD/LOQ | encoded as `censor` inside derived | explicit columns |
| condition_completeness | COND completeness_mask | OK, but moisture/pH/aw never populated |
| state_variable_id | SVAR (223 chemical, 1 physical) | register W3 families before ingesting any physical evidence |

## PROVENANCE GAPS
0 human-verified EVD; 14,108 UNVERIFIED; PE rows AI_PRECHECKED only; 5,894 censored; study lineage NOT_IDENTIFIABLE for all database aggregates; process mechanism families AI-drafted; ING scientific identity UNKNOWN for most; Gold is AI-assisted not independent; sessions AI-drafted; Silver `UNVERIFIED`.

## WHAT CAN FORM DATA-TRANSITION-BENCH TODAY
Chemical retention/yield transitions from E3 aggregates (USDA R6 + Bognar + Phenol-Explorer) for ING+PROC-linked rows: **11,413 rows** (306 ING x PROC cells with >= 3 rows, 220 with >= 10), splittable by matrix/process/study with the existing DEL-2 generators (which already report cold-split failure). Use as a *retention benchmark*, labelled E3, unverified, not Gold. Optional external check: OpenPI.
WHAT CANNOT: any physical-state transition (moisture, texture, colour, phase, temperature profile); any mechanism-level chemistry (Maillard, acrylamide, alliinase...); any E1/E2/E4 Gold evidence; any simulator-backed row; recipe-event -> state trajectories at scale; the priority cells garlic and wheat dough (0 rows).

## TOP 20 HIGH-VALUE MISSING CELLS (from the B06 priority list and measured recipe demand)
1 garlic x cut/crush (alliinase->allicin; 0 rows) 2 garlic x fry/boil/simmer 3 onion x chop (LFS; PPO/flavour) 4 onion x simmer (vitamin C/polyphenols) 5 wheat dough x knead/proof/bake (gluten, gelatinization; 0 rows) 6 potato x fry/bake (acrylamide; 0 mechanism rows) 7 potato x cut/store (PPO browning) 8 broccoli x boil/steam/cut (myrosinase, chlorophyll->pheophytin) 9 cabbage x boil/cut (myrosinase/glucosinolates) 10 rice x boil/steam (gelatinization, water uptake; temperature known 0) 11 beef x sear/roast/braise (Maillard, protein denaturation, mass loss; E3 yield only) 12 cream x beat/whip (foam/phase) 13 butter x melt (phase) 14 egg yolk x beat/heat (emulsion/gelation) 15 sugar x heat/caramelise (caramelisation) 16 carrot x roast/boil 17 pea x steam 18 ginger x fry/simmer 19 salt/season (dissolution, osmotic moisture loss) 20 baking powder/flour x bake (leavening, starch gelatinization). Items 1-11 are SSOT B06 priorities; 12-20 are the highest recipe-support events with no evidence cell.
