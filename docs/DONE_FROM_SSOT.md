# DONE FROM THE SSOT — everything built, in order (S001–S096, 2026-10-18 → 2026-10-19)

Source of truth for steps: `WORKLOG.md`. Unit status: `docs/BUILD_TRACKER.md`. Live state: `STATUS.md`. Plan: `docs/plan/S093_dataset_ledger_status_and_model_plan.md`.
Tests: 2,947 default + 40 ledger tests pass. Repo is local git only (no push before H7). Commits authored as Kush.

## A. Foundations (S001–S006, S016, S023, S042) — SSOT Epic A/B, P2/P14/P15
- Repo scaffold, Bible/plan docs copied in, SSOT index (headings, ID anchors RQ16/E16/G16, boxed statements) verified against plan Appendix 1.
- WORKLOG logger, STATUS, DECISIONS D-001…D-015, CLAUDE.md. Handoff docs: SOURCE_ACCESS, API_BLOCKERS, MANUAL_NEXT_STEPS, RUNBOOK, DATASETS, NER_RUNBOOK, H1 email draft.
- Ledger system: 36 record types as JSON Schema 2020-12, ID minter (never reuses IDs), validators and cross-record laws, append-only versioned JSONL store; reusable EDA report generator (Part M).

## B. Quantity, vocabulary, registries (S008–S010, S015, S018–S021, S031–S033, S035, S041) — P3, ledger queue 1–10
- Quantity system: 74 units with cited authority (NIST, UK WMA, 21 CFR), grammar, normaliser, symbolic quantities (no invented grams), property/fuzz tests.
- ING 2,048 active / ALIAS 4,103 (A1 corpus, FoodOn: 534 linked + 287 candidates, OFF: 835 linked + 14 languages, 560 Wikidata QIDs, duplicate merge). PROC 156 (18 families), TOOL 119 (Wikibooks + Wikidata QIDs), UNIT 74, ALLERGEN 8 (FSSAI Reg 5(14)), REC ledger with near-duplicate families.
- FDC SR Legacy crosswalk candidates (CC0), 867 raw/cooked pairs.

## C. Evidence ledgers (DEL-1) (S007, S022, S025–S027, S030, S038, S052, S069) — E3, P1
- EVD 17,978 active: USDA Retention Factors R6 (7,018; censored >100% handled), Phenol-Explorer (3,870 across 125 papers, study lineage), Bognár 2002 retention + weight-yield tables (+6,594 + 496). Stated temperature bounds treated as CENSORED (D-013).
- Literature harvest (OpenAlex/Crossref) → 634-row verification queue; AI pre-check of 3,870 PE rows (temperature sign bug fixed: 266 rows).
- EVD→ING/PROC strict linking; Kush bulk-signed 389 link rows (D-014): 237 linked / 129 held / 23 concept-missing.
- MOL 1,726 + IMAP 30,294 (PubChem, FlavorGraph +1,595 MOL / 29,656 IMAP, ChemTastesDB 204 tastes).
- DEL-1 state: 4/6 clauses; 0/40 literature rows human-verified (human gate).

## D. Corpora and knowledge graph (S034, S036–S037, S043–S046, S049, S051) — X3/X4/X9/X12/X14
- REC 89,565: BBC 11,934 (A1) + Wikibooks 3,676 + Gutenberg silver (306 books, ~66–71k, D-012 silver). OpenPI food subset (7,629 state changes) as external DEL-3 check.
- KGE 48k records / 45k active, 22 predicates: co-occurrence, cuisine, units, processed-by, category, tool, followed-by, durations/temperatures, alternative-to, prep-form, optional, medium, endpoint-state, MOL_HAS_TASTE (737), ING_COSYLAB_CATEGORY (964), ING_HEALTH_ASSOCIATION (497), ING_CARBON_FOOTPRINT (134).
- Gap map: 18 resources, 15 SSOT relations mapped to predicates (docs/RESOURCE_GAP_MAP.md). FoodAtlas = manual download only (CC BY-NC, bot checkpoint — not circumvented).

## E. State engine and sessions (DEL-3) (S011, S013–S014, S055, S074) — C3/C18
- Event-sourced engine with replay, merge/split/reserve fixtures; rule compiler recipe → events; gold schema, agreement scorer, handbook; 30 AI-drafted scripted sessions (237 checks pass, **0/30 human-reviewed**); session-state updater wired into `answer()` and `ask.py`.

## F. DEL-2 transition modelling (S017, S029, S039–S040, S050)
- Cell/split generators (random, pair-holdout, matrix/process/study-disjoint), D0–D7 baselines, censor-aware eval, log-RF + median AE, experiment cards EXP-000001..4, cross-source USDA↔Bognár agreement, FDC pair check. **Verdict (negative, reported as such):** learned models win on random splits; gains vanish on cold splits; conformal coverage 0.72–0.87 under shift.

## G. DEL-4 retrieval and calibration (S028, S053, S057, S068, S070, S072) — C6/C7/C8
- BM25 + 9-axis compatibility vector (UNKNOWN neutral) + Evidence Packet. Silver comparison (600 q): structured MRR 0.856 > RRF hybrid 0.704 > BM25 0.597; RRF+e5-large +0.057 paired; cross-encoders negative; R4 food-graph expansion promoted (vertical relations; siblings off); RQ16-03 pilot: structured compatibility beats CE-large on hard negatives (AUROC 0.995 oracle). Calibration metrics (ECE/Brier/AURC/UCR) + confidence vector ready; headline eval waits for human-verified labels.

## H. DEL-5 decision system (S054, S058–S067, S071, S075–S076, S086–S087, S095–S096) — C1–C18
- Relevance gate, feasibility filter (tools, time, FSSAI allergens, ingredient exclusions; allergen table awaits human sign-off), policy modes (ANSWER/COMPARE/RECOMMEND/RECOVER/ASK/ABSTAIN), OOD gate, outcome comparator (needs ≥2 independent sources), VOI-aware target asking, closed-world target lexicon, diagnosis proposer + history verifier + separate recovery index.
- C10 candidates and C15 Pareto selector now inside `answer()` (`candidates`, `pareto`): retention median + feasibility + typical duration; substitution reasons carry carbon vs original; `tools/ask.py` prints `tradeoff` and `alternatives`.
- C16 grounded generator: deterministic verbaliser promoted (0 unsupported / 0 violations); LLM rephrase (qwen2.5 7B/32B on A100) not promoted; C17 claim checker + enforcer; ladder B0/B2/B5/B5F/B5F+E/B5T on 20 AI-authored dev questions. **Benchmark ≥80 human-authored questions (D-008) still open.**

## I. NER (E16-A, X8, X10) (S047, S063, S073, S077, S083–S084)
- TASTEset test exact F1: rules 0.774 → BERT 0.919 / RoBERTa 0.925 / DeBERTa-base 0.922 → +CRF 0.929 (base+CRF 0.927 in later table) / large+CRF 0.933; CRF significant (p=0.003); kNN-NER Δ=0 (negative); FOOD F1 head 0.97 → unseen 0.69; 301-error analysis (46.5% boundary). Runtime replay on Mac MPS reproduces 0.9266.
- GLiNER zero-shot large 0.232 exact / 0.643 relaxed (FOOD 0.470/0.801): wired as fallback only (thr 0.2, conf 0.40) in `ner/pipeline.py` (rules → encoder ± CRF → GLiNER → verifier stub).
- RecipeDB3 audit (S078, S091–S092): 10 methodology vulnerabilities; verified on released data — file equals the augmented set (26,444 rows), random 80/20 split, model selected on the test set, SIZE absent from labels; 13.5% ± 0.4% numbers-masked family leakage and 5.4% ± 0.2% exact over 100 splits. **Matched reproduction + grouped clean re-evaluation harness written (`gpu/ner_recipedb3/`) but NOT yet run (VPN down).** No claim until H6.
- Mention→ING linking baseline: e5-large zero-shot Acc@1 0.607 vs char TF-IDF 0.555 (paired +0.051, CI [0.014, 0.090]); fine-tune not yet run.

## J. CoSyLab data (S078–S082, S088–S091, D-015)
- Audited 26 repos / 18 web services. Raw data downloaded to `data/external/` (gitignored). Use of unlicensed datasets permitted by Prof. Bagler per Kush (recorded D-015: licence ASSUMED, storage DERIVED_ONLY; written confirmation requested in H1 email). S080–S082 first attempt wrongly bypassed the ledger → reverted (S088) and redone through `LedgerStore` (S090).
- Ingested via ledger: bittersweet AGPL-3.0 (524 taste edges), SweetpredDB, RecipeDB2 categories (229 agree; disagreements as low-confidence edges), spice-disease co-mentions, carbon footprints.
- Not yet ledgered: SustainableFoodDB recipes (118k), companion/NER_DL NER sets, NOVA nutrients, AllerStack proteins, recipe_knowledge_mining.

## K. Tests and engineering quality (S058)
- SSOT §257I layers: property tests, 1.7k seeded fuzz cases, §257B contracts, replay, release audit, retrieval regression, e2e.

## L. Open items (nothing below is done)
1. VPN → run `gpu/ner_recipedb3/run_all.sh` (theirs ×5 vs clean ×5), then contrastive ING linker fine-tune (ING-grouped splits).
2. Human gates: 40 literature rows (DEL-1), 30 sessions (DEL-3), allergen sign-off, benchmark ≥80 Qs (D-008), H1 email send, H6 before any "beats CoSyLab" claim, H7 GitHub.
3. B0–B5 ladder on the human benchmark with oracle tests + ablations (E16-L); RQ16-01/04/09/10/21/23/24/29/30 still ⬜.
4. Ledger size watch (REC 94 MB, KGE ~60 MB) before H7 push (shard / LFS / snapshots).
5. FlavorTwin (RQ16-25/26/27, E16-K) deliberately after DEL-5.
6. Pending package approvals: hypothesis, recipe-scrapers, tabpfn (GLiNER and rdkit already approved/installed).
