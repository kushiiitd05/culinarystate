# CulinaryState — Master Plan v2 (ADAPTED DRAFT)

**Status: DRAFT FOR HUMAN APPROVAL. Not adopted. Does not replace SSOT v15 or `CulinaryState_Final_Master_Plan_SSOT15_v4_0.md`.**
Drafted 2026-10-22. STEP 08 NOT STARTED. No gate threshold in this file is final until recorded in `DECISIONS.md` and the threshold registry.

Inputs merged: (1) the Max/Ultra "Master Plan Research & Architecture Audit v2" (a DRAFT whose critique/revision round was skipped for usage limits; citations unchecked; the original 36-step plan was unavailable to it); (2) the Claude review of that audit; (3) an independent ChatGPT adopt/modify/reject split supplied by Kush. Where (2) and (3) differ, section 8 says so.

What I (Claude) read: audit Parts A, B/C gov summary, D (research findings), E (36-step table), the Step 07 and 08 cards in full, the key fields (status, goal, do-not, gates, fail actions) of every step card 09–36, Parts F, H, Q, R, U in full, the opening of each architecture part (M0, M, N, L, J1, J2, K), the full change log statistics and the breaking/Step 04/07/08 entries, and all 65 SSOT change-request summaries. NOT read in full: Steps 01–06 cards beyond the table, the body of the architecture parts, the 14 working notes, 10 research notes and the bibliography. Treat statements about those as unreviewed.

---

## 1. Governing principle

The original 36-step plan stays the governing spine. The audit improves HOW steps are executed (dependencies, schemas, gates, look-ahead, parallel lanes); it does not become a replacement plan. No top-level step is added, removed or renumbered (the audit agrees). Frozen artifacts stay frozen: changes are additive versions (v1.1), never retroactive "this step was never done".

## 2. Merged verdict

### GREEN — adopt
| # | Change | Where | Note |
|---|---|---|---|
| G1 | Keep all 36 top-level steps | all | |
| G2 | Evidence entity chain SRC→DOC→STUDY→SEXP→SMP→OBS→AGG/DRV with typed LIN edges (PROV-mapped), additive | 04.L, 08, 09 | EVD stays the consumer view |
| G3 | Three keys `study_id`, `lineage_root_id`, `split_group_id` + `independence_resolution`; UNKNOWN never in test sets | 04.L, 08, 15 | giant-component fallback labelled "publication-component CV", never "study-disjoint" |
| G4 | 07-DEP: Step 08 SOFT-depends on the Step-07 human condition audit; the audit stays HARD for Step 15 condition fields and Steps 23, 29–33 | 07, 08 | needs a recorded human ruling |
| G5 | Split Step 08 into 08a (existing 17,978-row corpus, CPU, Mac) and 08b (reusable lineage library called by Steps 11–14 at discovery time) | 08 | |
| G6 | Kinetic/trajectory table (+ dispersion, n, censor_kind, aggregation_level) BEFORE Step 11 | 04.K, 09 | otherwise series are flattened to endpoints |
| G7 | Namespace registry (SIM-/MODEL-/MEAS-/EXP-/CLM-/E7/D/B/T/S/H collisions) | 01.3 | cheap, do first |
| G8 | Data-plane registry + firewall rules (SOURCE / RECIPE / EVIDENCE / STATE-EPISODE / MODEL / SIMULATION; REFERENCE and GOVERNANCE layers) | 04.6 | no JSONL ledger carries a plane field today |
| G9 | Pre-registered threshold registry; a gate runs only if its threshold row predates data access | 01.6 | encodes the no-post-hoc-weakening law |
| G10 | 07I-C identity calibration from the 400-pair packet (two blind reviewers, kappa + AC1, sealed v2 test packet with recall probes) | 07 | |
| G11 | Recall-oriented `split_group_id` for recipes, separate from precision-oriented identity relations (07I-S) | 07 | families remain PROVISIONAL |
| G12 | Parallelise Steps 12 and 13 with the evidence chain | 12, 13 | |
| G13 | Start Step 21 schema/vocabulary early (no unsupported mechanism facts) | 21 | |
| G14 | Run explicit Step-35 baselines as a parallel CPU lane | 35 | |
| G15 | UNKNOWN applicability never routes to SIMULATE (retrieve / qualitative / ask / abstain) | 23, 36 | three-valued gates |
| G16 | Defer Step 28 (synthetic prior) until Step 27 passes | 28 | |
| G17 | Nine similarity notions kept separate in a typed registry; no fused scalar | 35 | |
| G18 | 09 dual independent extraction + span-match + arithmetic checks; LLM-only rows are E5 and never enter tests | 09 | |
| G19 | Condition vocabulary v1.1 additions (water:food ratio, lid, start mode, geometry, O2, tissue/medium pH, T series, condition_grid_id) as UNKNOWN for existing rows | 07.B | frozen 07H-R untouched |
| G20 | Extra agreement diagnostics for packet v4 (raw agreement, PABAK/AC1 when prevalence >0.9, positive/negative agreement, disagreement tables) | 07.A | diagnostics only |

### YELLOW — adopt with limits
| # | Change | Limit |
|---|---|---|
| Y1 | Step 19 earlier | Pilot only: 19A = DG-0, 20–50 independently annotated hard recipes with timing + IAA. 19B (100+) only if justified by measured throughput. Re-tier the 40 AI-drafted Gold as Gold-Light and remove their calibration eligibility. |
| Y2 | Step 29 earlier | TRANSITION_BOOTSTRAP_V0 on a 15a E3 freeze is DIAGNOSTIC_ONLY. No headline transition claim from unverified E3. |
| Y3 | Step 25 merged into 24 | Operationally one package; conceptually keep 25 ("can these parameters be used for this query?"). Number retained. |
| Y4 | Step 15 split into 15a/15b | 15a: diagnostics, baselines, split-feasibility, pipeline engineering. 15b: only source of headline results and verified test sets. |
| Y5 | Simulator choice | SIM-AA-1 (ascorbic acid, degradation + leaching) is candidate #1; SIM-CHL-1 the pre-registered fallback. Final choice after the Step 10/11 extractability census. Do not freeze AA now. |
| Y6 | Step 36 schema changes (PKT v2, `RCL-`, rung enum) | Design now, implement later. They are BREAKING; Step 36 is far away and Steps 08/09/23 will show what provenance really looks like. |
| Y7 | 07.A protocol amendment | Process-integrity only (see section 3). Primary gate unchanged. |
| Y8 | Steps 03/04 | Treat v1 as the frozen base and add v1.1 / 04.L / 04.K additively. A human ruling must DECLARE v1 frozen (the audit found MP-1 header "DRAFT FOR REVIEW" vs authority map "FROZEN_CONTRACT"; rulings C2–C8 unrecorded). |

### RED — do not adopt
| # | Rejected | Reason |
|---|---|---|
| R1 | Marking Steps 03/04 as failed/never complete | Additive versions instead (Y8). |
| R2 | Changing the condition gate to per-field kappa >= 0.80 | Original gate stays: pooled Cohen kappa >= 0.80 AND no systematic critical-field disagreement. The audit's Part W wording contradicts its own Step 07 card, which says "keep the existing gate verbatim". |
| R3 | Editing packet v4 (cases, labels, fields, examples) | Any edit invalidates the hash; would require v5. |
| R4 | Freezing AA as the simulator now | See Y5. |
| R5 | Launching the large Deep Gold programme now (150–375 h per person) | See Y1; hours do not fit the 25–26 Nov deadline and are UNVERIFIED estimates. |
| R6 | Executing breaking Step-36 schema changes now | See Y6. |
| R7 | Auto-adopting SSOT change requests | All 65 are `PROPOSED_ONLY`; need explicit approval (section 6). |
| R8 | Merging near-duplicate recipes, or choosing a threshold for a desired corpus size | Corpus size is a result, never a target. |
| R9 | Promoting the 605,476 provisional families to truth | They stay PROVISIONAL until 07I-C. |
| R10 | Forcing NEED_DATA branches (kinetics 32, 34b, process-conditioned 35f, FlavorTwin sensory) to execute | Correct outcome is NEED_DATA / DEFER, not a new prerequisite. |

## 3. The 07.A amendment, precisely (so it does not touch packet v4)

Packet v4 (`condition_audit_packet_100_v4_*.csv`, sha256 `533c49ba…8571`, normalizer fingerprint `e7d58913…76a5`) is frozen and its Kush/Parv copies are byte-identical before labelling. The amendment is applied to the RETURNED files, not the packet:
- keep verbatim: pooled kappa >= 0.80 AND no systematic critical-field disagreement;
- add as validity prechecks: sha256 of each completed file recorded before the other is opened; minimum mtime separation; test for identical cells/distributions across the two files; original raw/frozen fields byte-identical to the packet;
- add as diagnostics: raw agreement, PABAK/AC1, positive/negative agreement for fields with dominant-code prevalence > 0.9, full disagreement tables; every disagreement on such a field is human-adjudicated (never by an LLM);
- DROP the audit's "separate per-reviewer packet IDs" sub-item: it would require editing the packet. The two reviewer file names already separate them;
- record it as a DECISION BEFORE any v4 label exists.

## 4. Architectures (consolidated)

1. **Data planes** — SOURCE, RECIPE SEMANTIC, SCIENTIFIC EVIDENCE, STATE/EPISODE, MODEL, SIMULATION; plus REFERENCE (vocabularies) and GOVERNANCE (splits, claims, gates) as non-memory layers. Recipe text never defines measured magnitudes; model/simulation values never enter evidence, tests or citations. Enforce with validators before Step 08 (evidence firewall) and Step 16 (recipe/state firewall).
2. **Evidence model** — SRC→DOC→STUDY→SEXP→SMP→OBS→AGG/DRV + LIN. USDA R6 and Bognár rows are typed user-level AGGREGATEs and are never re-pooled with their members. OBS carries dispersion type/value, n_biological/n_technical, statistic, censor_kind {LT_LOD, LT_LOQ, ND, GT_CAP, ROUNDED_INTERVAL, RANGE_ONLY}, basis, method. Unreported dispersion is NOT_REPORTED, never imputed.
3. **Acquisition** — structured databases give endpoints only; kinetics, aw, texture and colour series are literature-only; therefore Steps 10–14 are coverage-driven and the plan must not promise broad kinetic coverage. Discovery: OpenAlex (CC0) metadata, Crossref/Unpaywall licence and OA location, Europe PMC / PMC per-file for lawful full text; the user, not the agent, creates API keys.
4. **Mechanism** — small registry (MECH-, ~20–40 entries) + three-valued applicability gates (APPLICABLE / NOT_APPLICABLE / UNKNOWN) + formula/parameter registry (FORM-/PARAM-/VAL-) populated first for one focused system. An LLM may propose, never decide.
5. **Simulation** — one deterministic simulator; lineage-disjoint calibration vs validation; one-shot lockbox; credibility record; failure => RESEARCH_ONLY. Calibration domain, validated domain and M&S limits are three different objects.
6. **Transition** — one baseline ladder (SSOT D-numbering canonical, B-to-D mapping published). Tuned GBDT, hierarchical/mixed-effects (D3+) are the floor; TabPFN v2 is a CPU comparator only (TabPFN-2.5 weights not usable). Conformal calibrated on groups held out the same way as the test split. The repo's own DEL-2 result — gains vanish on cold splits — is the decisive prior.
7. **Representation** — explicit rungs first (ECFP4 count + LightGBM reference, IDF/Jaccard, tiered ingredient profile x_ij, frequency panels, kNN memorisation baseline); learned rungs gated, default DEFER; pairing statistics are cultural descriptors with frequency-preserving nulls, never flavour compatibility.
8. **Recipe state** — ingredient identity separate from form/cut/state/preservation/brand facets; CQPO quantity intervals (no fake grams); process/tool hierarchy; corpus tiers weak 612k → Silver → Gold-Light → Deep Gold, with Deep Gold annotated blank; identity ≠ state; process clock tau ≠ historical clock t.
9. **RAG / confidence** — structured retrieval primary; BM25 + dense (RRF) fallback only; no generic cross-encoder; certainty as a profile of separate ordinal domains, never a multiplied scalar; rule cascade DIRECT / INTERPOLATE / MODEL / QUALITATIVE / ASK / ABSTAIN with conflict status orthogonal; sufficiency rule-derived; Platt/logistic calibrators with 1–6 features, no isotonic below ~1,000 labels; calibration data must be independent human Gold, never AI-assisted.

## 5. Step-by-step plan (07 → 36), adapted

Legend: [H] human gate · [D] data-blocked · [P] pre-registration needed first.

| Step | Adapted plan | Key gates / limits |
|---|---|---|
| 07 | Frozen automated parts stay. 07.A human audit on packet v4 with section-3 amendment [H]. 07.B/07.C additive COND/MEAS v1.1 vocab. 07I-C identity calibration [H]. 07I-S `split_group_id`. 07R: declare 07H-R/07I-R as recipe-plane lane deliverables kept under Step 07 numbering. | pooled kappa >= 0.80 + no critical-field failure (unchanged). 07I-C PROPOSED: binary kappa >= 0.70 and precision Wilson LB >= 0.90 at the merge operating point — needs human approval. |
| 08a | Lineage on existing corpus: DOC/LIN/SEXP/SMP/OBS schemas, STUDY append versions, detector ladder B0–B3, USDA↔Bognár overlap verdict, independence registry, DRV parent-union merge, component-feasibility report, EVD export v2. Extracts no new values. CPU, minutes. [P] 08.0 pre-registration | PROPOSED: 100% rows have non-null keys; 0 DRV rows span unmerged groups; edge precision Wilson LB >= 0.90 (~150 audited edges); seeded-copy recall >= 0.95; canonical ledgers byte-identical; deterministic double rebuild. Giant-component threshold PROPOSED 40%. |
| 08b | Same detector as `src/culinarystate/lineage/` library, called at discovery time by Steps 11–14. | |
| 09 | Dual extraction machinery + trajectory table; golden fixtures only (no real documents until Step 10). | AI_PRECHECKED is never verification. No licensed text to external LLM APIs without an H2 ruling. |
| 10 | 20-row pilot as a protocol shake-down and extractability census; not a gate for E4 promotion. [H] [P] | 95% observed accuracy on n=20 has CI [0.76, 0.99]. |
| 11 | Wave-1 human-verified evidence (largest human block). | G11 shortfalls => NEED_DATA, reported honestly. |
| 12 / 13 | Structured DB ingestion / literature discovery, in parallel. | Park unlicensed sources; no scraping; no paywalled TDM. |
| 14 | Coverage-driven growth with stop rules and a >= 30% random audit stream. | Do not optimise row count. |
| 15 | 15a bootstrap E3 freeze (diagnostics only); 15b full DATA-EVIDENCE v1. | No re-split after test metrics; no E5/E6/E7 in tests. |
| 16 | Instruction schema v1 + vocabulary hierarchy; DG-0 pilot design [H]. | Schema is additive to the v0 schemas. |
| 17 | B0–B5 ladder with a mandatory oracle cascade; frozen NER/linker not reopened. | |
| 18 | Keep; wire to EVT/ENTITY/STATE ledgers once schema v1 lands. | |
| 19 | 19A pilot (20–50 recipes) only; 19B gated on measured throughput [H]. | Deep Gold annotated blank. |
| 20 | Tiered scale; T0 deterministic over the 611,714 exact representatives; Silver pilot only if utility shown. | Needs 257P items; training use now covered by D-026 for project use. |
| 21–25 | MECH registry; EFFSIG signatures; applicability engine; FORM/PARAM/VAL; parameter-compatibility within the 24 package. | Any UNKNOWN => no SIMULATE route. |
| 26–28 | Data-free 26a–c can start early; 26d calibration waits for the 15b partitions; 27 one-shot lockbox; 28 deferred. | Simulator pass needs >= 5 independent validation lab groups else DIAGNOSTIC_ONLY. |
| 29–31 | 29 diagnostic on 15a; 30 bake-off on frozen splits; 31 only after the condition audit validly passes. | Cold-split collapse => lookup + hierarchical fallback stays the estimator. |
| 32–34 | 32 NEED_DATA; 33 gated on 32; 34a feasible (composition test), 34b NEED_DATA, 34c spec. | |
| 35 | 35.0 pre-registration; 35a–e explicit rungs in parallel; 35f late; 35g default DEFER; optional 35-E lane. | Sensory/OAV notions NEED_DATA. |
| 36 | 36.0 prototype audit; 36A compiler (design now); 36B human benchmark (start early) [H]; 36C selective RAG; 36D FlavorTwin DEFER. | No performance claim without human benchmark. |

## 6. Human work is the critical path

Pending human items today: Step-07 condition audit v4 (0 judgements), 400-pair identity packet (0 labels), H2 licence items, Step 04 rulings. Audit estimates (UNVERIFIED): Kush/Parv hours Step 07 6–14 each, Step 08 3–8, Step 10 10–20, Step 11 30–80, Step 14 40–120, Step 19 150–375, Step 36B 40–55. The course presentation is 25–26 Nov 2026. These do not all fit. The honest scope for the deadline is: 07.A, 07I-C, 08a, 09 machinery, 10, 15a diagnostics, 29/30 diagnostics on E3, 16 schema, 19A pilot, 35 explicit baselines, 36A/36B design; everything else is reported NEED_DATA/DEFER. Replace every hours estimate with logged timings from the Step 07 and Step 10 work.

## 7. Critiques of the audit (what could be wrong)

1. **Draft quality:** critique, DAG-consistency and citation-check rounds never ran; Parts F, H, Q, R, U were merged mechanically; phase cards are authoritative for their own edges.
2. **Reconstruction risk:** if the original 36-step plan resurfaces with different card-level gates, Phase A must be re-diffed.
3. **Internal inconsistencies seen:** Part W says "per-field kappa >= 0.8" while the Step 07 card says keep the gate verbatim; step counts differ between Part A (36 steps) and the 49-row ratings table (substeps counted); an audit-proposed D-026 collides with the actual D-026 (usage decision) — the audit's authority ruling becomes D-027.
4. **Environment claims to verify:** the audit says pandas/pyarrow are absent "on this Linux server"; manjot-server runs a conda base Python, so recheck before concluding anything is BLOCKED_ENV.
5. **Capacity:** only two humans exist; the same hours serve 07.A, 07I-C, Steps 09–11 verification and Deep Gold.
6. **Prior exposure:** all current E3 rows were inspected by DEL-2, so no fresh confirmatory test exists until Step 15b sealed rows. 15a must stay diagnostic.
7. **Step 08 feasibility unknowns:** component structure (giant component), USDA↔Bognár overlap, and whether the R6/Bognár bibliographies exist locally are all UNVERIFIED.
8. **Numeric thresholds** (40% giant component, 0.90 edge precision, 0.95 seeded recall, K=10 clusters, alpha 0.80/0.667, kappa 0.70) are design proposals, not literature constants.
9. **Licence:** external-LLM extraction of licensed text, digitised closed-access figures, Phenol-Explorer redistribution and FlavorGraph NC terms remain open H2 items; D-026 covers project use of the recipe base only.

## 8. Where Claude and the ChatGPT split differ

- ChatGPT: "Steps 03 and 04 were already frozen". Fact: the audit found the freeze status ambiguous and rulings C2–C8 unrecorded. Agreement on the additive approach; one recorded human ruling is needed to settle it (Y8).
- ChatGPT rejects editing packet v4. Agreed; the amendment is therefore applied to returned files only (section 3), and one sub-item of the audit is dropped.
- ChatGPT keeps Step 25 conceptually; the audit keeps the number too ("MERGE ... number retained"). Effectively the same.
- ChatGPT's Gold pilot (20–50) is consistent with the audit's DG-0 (30) → DG-1 (200, fallback 100); the difference is only that DG-1 is gated here.

## 9. Immediate actions (each needs Kush's go-ahead)

1. Record D-027: 07-DEP ruling + declare Step 03/04 v1 as the frozen base + additive 04.L/04.K.
2. Approve (or edit) the section-3 amendment before anyone labels packet v4.
3. Pre-register Step 08 thresholds in the threshold registry (01.6).
4. Authorise Step 08a (CPU, Mac) once 1 and 3 are done.
5. Schedule the human tracks: v4 audit and the 400-pair labels (blind, technically independent), then the 19A pilot.

*End of draft.*
