# SSOT change requests v2

Generated 2026-10-22 by the CulinaryState plan-research audit (PLAN ONLY; STEP 08 NOT STARTED). Built from 9 phase drafts; the planned adversarial-critique/revision round was SKIPPED for usage-limit reasons, so treat every item as DRAFT FOR HUMAN REVIEW.

Every request: **Status: PROPOSED_ONLY**. The SSOT was not edited.

## CR-01 (G_A) — SSOT §201.7 L16651-16675 (evidence tiers E1-E6)
- **Current SSOT text / assumption:** Six tiers; E6 = heuristic/qualitative/weak inference; no simulator tier
- **New evidence:** Master Plan I1 L587-595 and repo registry/evidence_tier_provenance_map_v1.csv use E1-E7 with E6=MODEL_ESTIMATED and E7=SIMULATED; SSOT §222.9 L24044 uses class I for imputed; §223.13 L24236-24240 ranks imputed above rule labels; 'E7' also names L12 encoder rung (L8487-8511) and L13E Phase E7
- **Proposed change:** Add a tier crosswalk (SSOT E1-E6 <-> repo TIER-E1..E7 <-> class I <-> §223.13 fidelity) and either adopt E7 SIMULATED or declare it a repo extension; namespace tiers as TIER-E#
- **Scientific impact:** None to evidence ranking; prevents imputed/simulated rows being ranked or named ambiguously
- **Execution-plan impact:** Step 04.4; Steps 09, 28 tier assignment; Step 01.3 namespace
- **Status:** PROPOSED_ONLY

## CR-02 (G_A) — SSOT §239.1 L26117-26126 vs §257A.4 L28076-28093 vs §257A.14 L28298-28324
- **Current SSOT text / assumption:** Three different field provenance/status/claim vocabularies (8-value provenance; 10-value field status incl. CONFLICTING, NOT_APPLICABLE, KNOWN_*; claim classes incl. INTERPOLATED)
- **New evidence:** Repo adopted §239.1; ssot_annexA C1 shows §257A mixes them internally; W3C PROV separates derivation/origin from assertion status (r_evidence_model)
- **Proposed change:** Declare three orthogonal fields: origin_provenance (§239.1), field_status (UNKNOWN/NOT_APPLICABLE/CONFLICTING/CENSORED/NOT_REPORTED/KNOWN), claim_route (DIRECT/INTERPOLATED/MODEL_ESTIMATED/EXTRAPOLATED/SIMULATED/QUALITATIVE/UNSUPPORTED) with a crosswalk table
- **Scientific impact:** Prevents CONFLICTING/NOT_APPLICABLE being collapsed into UNKNOWN or null; correct claim language
- **Execution-plan impact:** Steps 03.1/04.5; Steps 09, 16-19, 36
- **Status:** PROPOSED_ONLY

## CR-03 (G_A) — SSOT §257C EvidenceAtom.15/.16/.22 L31100-31179 (study_id, source_id, independence_group) and §238
- **Current SSOT text / assumption:** Field names with generic boilerplate; no definition of independence group
- **New evidence:** Cochrane: study not report is the unit; von Elm 2004 covert duplicates 5.3%, 64% different authorship; repo has 127 groups with database aggregates as one group each (r_evidence_model)
- **Proposed change:** Define study_id, lineage_root_id (statistical unit), split_group_id (evaluation unit) and independence_resolution {STUDY, PUBLICATION_ONLY, SOURCE_FAMILY_ONLY, UNKNOWN}; UNKNOWN never in test sets; giant-component fallback named 'publication-component CV'
- **Scientific impact:** Valid study-disjoint evaluation, cluster bootstrap and agreement analysis
- **Execution-plan impact:** Step 04.1 contract; Step 08 compute; Step 15 freeze
- **Status:** PROPOSED_ONLY

## CR-04 (G_A) — SSOT §257C Recipe.20 duplicate_group_id vs §191.3 L14774-14801 split policy
- **Current SSOT text / assumption:** duplicate_group_id field; §191.3 requires near-duplicates and cross-source copies in one split group; §257C forbids silent reinterpretation
- **New evidence:** Repo duplicate_group_id is exact-only (07I-R Level A); families are precision-oriented (6,589 edges of 744,615 kept pairs) and uncalibrated (r_eval_splits, ssot_l13)
- **Proposed change:** Add a separate versioned split_group_id (recall-oriented, calibrated on labelled pairs) next to exact duplicate_group_id
- **Scientific impact:** Removes near-duplicate leakage without destructive merges or erasing cultural variants
- **Execution-plan impact:** Step 04.8, 07I-C, Steps 15-20, 35
- **Status:** PROPOSED_ONLY

## CR-05 (G_A) — SSOT §128 L7872-7895 (status block) and §244.3-244.4 L26542-26598 (repo layout/artifacts)
- **Current SSOT text / assumption:** 'Code written: None yet' (L7889); 'Professor API endpoints: Not yet received' (L7890); initial repo layout and first frozen artifact names
- **New evidence:** Repo has 22 packages / 14,091 LOC / 678 test functions (impl §0.1), CoSyLab use permitted per D-015, actual layout ledgers/schemas + registry/ + reports/
- **Proposed change:** Mark the stale lines [superseded by repo status; see registry/implementation_status_v2.csv] per §139 append-don't-rewrite; add a mapping table SSOT artifact name -> repo path
- **Scientific impact:** None
- **Execution-plan impact:** Steps 01/02 authority and status
- **Status:** PROPOSED_ONLY

## CR-06 (G_A) — SSOT §232.3 L25264-25273 (four evidence planes) vs §233.7 L25385-25399 (five memory classes)
- **Current SSOT text / assumption:** Planes D^recipe/D^scientific/D^estimated/D^simulated vs memory classes Source/Semantic/Episode/Evidence/Model (simulations inside Model memory)
- **New evidence:** Brief §13 requires six planes; repo mixing risks in COND/STATE/KGE/IMAP (M0 review)
- **Proposed change:** Add a crosswalk: SOURCE, RECIPE SEMANTIC, SCIENTIFIC EVIDENCE, STATE/EPISODE, MODEL, SIMULATION planes plus REFERENCE and GOVERNANCE non-memory layers; simulation stored separately while epistemically model memory
- **Scientific impact:** Stricter separation; no change to laws
- **Execution-plan impact:** Step 04.6 data-plane registry and firewalls
- **Status:** PROPOSED_ONLY

## CR-07 (G_A) — SSOT L12843 (missingness tri-state) vs L128-area four-state list (ND / below-LOD / not measured / unchanged) and L25313-25315
- **Current SSOT text / assumption:** Inconsistent missingness vocabularies across L12 and L16
- **New evidence:** Repo censoring registry lacks ROUNDED_INTERVAL, RANGE_ONLY, TRUE_ZERO; USDA rows are rounded to 5% and capped at 100 (r_evidence_model)
- **Proposed change:** One missingness/censoring superset with numeric-use rule per code
- **Scientific impact:** Correct censored-likelihood handling; UNKNOWN != 0
- **Execution-plan impact:** Step 03.2/04.2; Steps 05, 09, 30
- **Status:** PROPOSED_ONLY

## CR-08 (G_A) — SSOT §234.7 L25478 NEEDS_HUMAN_REVIEW vs §239.3 L26185 HUMAN_REVIEW; §235.3 Q0-Q6 vs §257A.2 lookup ladder L27993-27999
- **Current SSOT text / assumption:** Two names for the same review state; lookup ladder adds 'other approved national table' with no Q-level; repo POR.basis CONVENTION unmapped
- **New evidence:** ssot_l16 §9 items 1-2; ssot_annexA C4
- **Proposed change:** Single enum NEEDS_HUMAN_REVIEW; map 'approved national table' to Q1/Q2 with source-rank field; map CONVENTION explicitly
- **Scientific impact:** None (consistency)
- **Execution-plan impact:** Steps 04.5, 16, 17
- **Status:** PROPOSED_ONLY

## CR-09 (G_B) — §238 / §257C EvidenceAtom.22 independence_group (SSOT L31170-31179); EvidenceAtom.15 study_id (L31100)
- **Current SSOT text / assumption:** Field names only with generic boilerplate; no definition of what an independence group is or how it relates to study/publication/lineage
- **New evidence:** Cochrane Handbook v6.5 ch.5 (study not report), von Elm 2004 (64% of covert duplicates have different authors), PROV-DM derivation types; repo: 127 groups, PE yield factors span two publications (EVD-007019)
- **Proposed change:** Define three nested keys study_id / lineage_root_id (statistical unit) / split_group_id (evaluation unit) plus independence_resolution {STUDY, PUBLICATION_ONLY, SOURCE_FAMILY_ONLY, UNKNOWN}; UNKNOWN never in test
- **Scientific impact:** Correct counting of independent evidence; valid study-disjoint evaluation and cluster bootstrap
- **Execution-plan impact:** Step 04 addendum 04.L; Step 08 implements; Step 15 consumes
- **Status:** PROPOSED_ONLY

## CR-10 (G_B) — §257C entity list (L29336-31464) / §238 (L25745-26101)
- **Current SSOT text / assumption:** No STUDY / EXPERIMENT / SAMPLE / OBSERVATION / AGGREGATE / DERIVED / LINEAGE entities; EvidenceAtom is flat
- **New evidence:** ISA abstract model (Sansone et al. 2012), W3C SOSA/SSN, PROV-O; Cochrane ch.23.3.4 shared-control correlation; Lajeunesse 2011
- **Proposed change:** Add the SOURCE->DOCUMENT->STUDY->EXPERIMENT->SAMPLE->MEASUREMENT->AGGREGATE->DERIVED hierarchy with typed LINEAGE edges as a normative data-contract annex (semantic mapping; EvidenceAtom remains the consumer view)
- **Scientific impact:** Enables shared-control modelling, within-study-first kinetic fitting (§211.37), multi-parent derivation tracking
- **Execution-plan impact:** Steps 04, 08, 09; parts/I1_evidence_model.md
- **Status:** PROPOSED_ONLY

## CR-11 (G_B) — EvidenceAtom fields (L30958-31189) vs §257A.5 capture list (L28108-28121)
- **Current SSOT text / assumption:** EvidenceAtom lacks basis, replicates/n, dispersion type/value, censoring kind/limit, before/after or trajectory pairing, extraction_method, licence, although §257A.5 mandates capturing them
- **New evidence:** Effect-size variance requires mean/dispersion/n per arm (Hedges 1999; Lajeunesse 2011); repo: 0 of 17,978 rows have SD/n/LOD
- **Proposed change:** Add basis, statistic, dispersion_type/value, n_biological/n_technical, censor_kind/limit/resolution, pair_id/trajectory_id/time_point, extraction_method, licence_status, value_origin (incl. DIGITIZED) to EvidenceAtom
- **Scientific impact:** Weighted pooling and censored likelihoods become possible where data allow; explicit NOT_REPORTED prevents imputation
- **Execution-plan impact:** Steps 05.1, 09
- **Status:** PROPOSED_ONLY

## CR-12 (G_B) — §222.3 value statuses (L23972-23980); §201.9 censoring (L16692-16717)
- **Current SSOT text / assumption:** TRUE_ZERO / NON_DETECT / BELOW_LOD / NOT_MEASURED / UNKNOWN; no upper-cap or rounding (interval) censoring
- **New evidence:** Current corpus censoring is entirely GT_CAP (USDA '>100 reported as 100', Bognar caps) plus USDA 5% rounding; EFSA 2010 / Hwang 2023 on censored data handling
- **Proposed change:** Add GT_CAP (right-censored), ROUNDED_INTERVAL (interval-censored with resolution) and RANGE_ONLY to the status vocabulary; require a source pointer justifying each cap
- **Scientific impact:** Correct censored/interval likelihoods instead of bound substitution (DEL-2 0.975 practice)
- **Execution-plan impact:** Steps 03/04 registries, 05.4, 07.D, 29/30 training
- **Status:** PROPOSED_ONLY

## CR-13 (G_B) — G15-H (L22395) vs §201.7 (L16664) and §201.8 (L16690)
- **Current SSOT text / assumption:** G15-H covers LLM-extracted rows only; §201.8 says all held-out test values should be human verified; status of unverified E3 database-aggregate rows in test sets is ambiguous
- **New evidence:** Repo: 0 human-verified rows; all test candidates are E3 aggregates; MP-1 conflict C2 proposes 'bootstrap benchmark labelled unverified'
- **Proposed change:** State explicitly: E3 aggregate rows may form a test set only when labelled 'unverified-aggregate bootstrap benchmark' and never for G14-3/G15-6 headline claims; LLM-extracted rows require human verification (unchanged)
- **Scientific impact:** Prevents unverified data from silently counting as human-verified held-out labels
- **Execution-plan impact:** Steps 09 (E4 promotion), 15 (test eligibility), 29
- **Status:** PROPOSED_ONLY

## CR-14 (G_B) — G14-6 (L17083) and Split 6 (L16886-16891)
- **Current SSOT text / assumption:** 'Source/study-disjoint evaluation completed where study IDs exist' can pass vacuously for single-source data; Split 6 unit 'paper/study/experimental campaign' does not mention re-reports, compilations or giant components
- **New evidence:** Repo: USDA and Bognar are one cluster each; PE 125 publications; MP AM3 giant-component fallback; Roberts 2017 block-CV extrapolation caveat
- **Proposed change:** Define the Split 6 unit as the lineage component (including re-report/compilation edges); require a pre-registered minimum number of independent test clusters (PROPOSED_PILOT K=10) or label the result DIAGNOSTIC_ONLY; adopt the AM3 rule 'publication-component CV, never study-disjoint' when a giant component exists
- **Scientific impact:** No claim of study-disjoint generalisation without the required independent clusters
- **Execution-plan impact:** Steps 08 (feasibility verdicts), 15 (split registry), 29-30
- **Status:** PROPOSED_ONLY

## CR-15 (G_C) — §210.29A (L19137-19163) focused kinetic anchors
- **Current SSOT text / assumption:** [SOURCE-REPORTED] acrylamide/potato frying and glucose/glycine Maillard proposed as the D-C simulator/reimplementation anchors
- **New evidence:** AA (vitamin C) has the largest independent K1/K2 literature, a low-consequence context of use and an existing E3 consumer (1,196 vitamin C rows); acrylamide is safety-critical, precursor-dependent with poorly identified degradation parameters (Knol 2009); Maillard model-system parameters transfer poorly to foods (van Boekel 2008)
- **Proposed change:** Add a note: the first focused system is chosen by a pre-registered extractability census; default candidate ascorbic-acid degradation+leaching in vegetables with chlorophyll fallback; acrylamide/Maillard retained as later RESEARCH_ONLY anchors
- **Scientific impact:** Simulator validation becomes feasible earlier on a lower-risk system; acrylamide claims deferred
- **Execution-plan impact:** Steps 10/11a/26/27/32 target AA/CHL; status PROPOSED_ONLY
- **Status:** PROPOSED_ONLY

## CR-16 (G_C) — §210.29 (L19111-19136), §211.50, §216.2 (L22800-22824) kinetic schemas
- **Current SSOT text / assumption:** Three overlapping kinetic field lists with no canonical one; no raw-timepoint origin or digitisation fields
- **New evidence:** Acquisition requires one schema carrying raw timepoints separately from fits, data_origin (table/text/figure-digitised/supplementary/author-fit-only), digitisation uncertainty, author-fit vs project-fit, lab/series/replicate ids (§257F.5 requires DIGITIZED flag)
- **Proposed change:** Declare one canonical kinetic-experiment/trajectory table (union of the three) with these fields
- **Scientific impact:** Prevents flattening series to endpoints and conflating author and project fits
- **Execution-plan impact:** Step 04.K becomes the binding contract for Steps 09-15, 24-27, 32; PROPOSED_ONLY
- **Status:** PROPOSED_ONLY

## CR-17 (G_C) — §216.1 transition-event table (L22737-22795) / §238 EvidenceAtom
- **Current SSOT text / assumption:** No replicate n, dispersion type/value, aggregation level, yield/normalisation status, lab, year, regime tag or K-rung fields
- **New evidence:** G15-1 requires yield/normalisation status; log-response-ratio variance needs mean, dispersion and n per arm (Hedges 1999; Lajeunesse 2011); FAO/INFOODS & EuroFIR require value-type/method-indicator/aggregation documentation; current EVD has none
- **Proposed change:** Add n_biological, n_technical, dispersion_type+value, statistic, aggregation_level, method_indicator, yield_normalisation_status, lab_group_id, year, regime (D-A..D-D), K_rung
- **Scientific impact:** Enables weighting, censored likelihood, cluster bootstrap and regime separation
- **Execution-plan impact:** Steps 04/05/09/12/15; PROPOSED_ONLY
- **Status:** PROPOSED_ONLY

## CR-18 (G_C) — §203.10 minimum viable data target (L17375-17385)
- **Current SSOT text / assumption:** Launch criterion 'enough support to create meaningful pair-holdout and study-disjoint test sets' with no number
- **New evidence:** Only 127 independence groups today; USDA and Bognar are one cluster each; with <20-30 clusters cluster-robust inference over-rejects (Cameron 2008); a 10 pp paired difference needs ~155 items
- **Proposed change:** Require a pre-registered minimum of independent test clusters per headline cell (proposal K=10) and a minimum verified test size per claim family; otherwise the split is DIAGNOSTIC_ONLY
- **Scientific impact:** Stops vacuous study-disjoint passes (G14-6 escape clause)
- **Execution-plan impact:** Steps 14/15 gates; PROPOSED_ONLY
- **Status:** PROPOSED_ONLY

## CR-19 (G_C) — §203.3 Priority B volatile anchors (L17213-17228) vs §144.3 curation cells vs MP AI5 anchor matrix (MP L3097-3100)
- **Current SSOT text / assumption:** Three different anchor lists; volatile Priority B before kinetic Priority C
- **New evidence:** Volatile process-effect data are LITERATURE_ONLY with absolute quantities RARE and thresholds COMMERCIAL_RESTRICTED; volatiles serve FlavorTwin (off critical path); MP AI5 warns against six-anchor bias
- **Proposed change:** Use the AI5 12-family matrix as the breadth frame for Wave-1; make volatile acquisition conditional on an H8 decision to prioritise flavour claims; keep focused kinetics (Priority C) as the depth priority
- **Scientific impact:** Acquisition aligned with validation-capable claims
- **Execution-plan impact:** Steps 11b/14; PROPOSED_ONLY
- **Status:** PROPOSED_ONLY

## CR-20 (G_C) — §224.8 active literature extraction loop (L24345-24353) / §227.11
- **Current SSOT text / assumption:** Loop current tensor -> high-value region -> acquire -> extract -> verify -> retrain; no random-acquisition stream or acquisition log mandated
- **New evidence:** Active-learning gains over random are inconsistent and selected sets transfer poorly (Lowell et al. 2019); §227.11 promotion of active learning needs a comparison against random
- **Proposed change:** Mandate an acquisition log (reason, score, model version) and a fixed random audit share (proposal >=30%) of acquisitions
- **Scientific impact:** Makes acquisition-efficiency claims testable and selection bias measurable
- **Execution-plan impact:** Steps 11/14; PROPOSED_ONLY
- **Status:** PROPOSED_ONLY

## CR-21 (G_C) — §227.8 dataset acquisition list (L24742-24758)
- **Current SSOT text / assumption:** Lists FoodAtlas and FooDB/FlavorDB as high-priority resources; omits USDA Cooking Yields, Bognar, occurrence datasets
- **New evidence:** FoodAtlas CC BY-NC since 2026-10-09; FooDB CC BY-NC; FlavorDB access blocked; PMC bulk packages retired Aug 2026; USDA Cooking Yields R2 (CC0, n/SD) available; occurrence data (EFSA, Scheijen 2016, Glycation DB) are plausibility-only
- **Proposed change:** Annotate licence status per item, add USDA Cooking Yields R2/Bognar, and mark occurrence datasets as plausibility-only (not process-effect evidence)
- **Scientific impact:** Prevents licence violations and plane mixing
- **Execution-plan impact:** Steps 06.U/12; PROPOSED_ONLY
- **Status:** PROPOSED_ONLY

## CR-22 (G_D) — SSOT §257D L31465-33895 (title 'vocabulary, quantity, entity and state parsing' Gold test catalog)
- **Current SSOT text / assumption:** 162 quantity (Q001-Q162) and 121 vocabulary (V001-V121) phrases, each with identical template bullets, no expected outputs; no entity or state cases despite the title
- **New evidence:** ssot_annexB mechanical check (uniq -c); Steps 16-19 need answer keys and entity/state/event cases
- **Proposed change:** Mark 257D as a phrase inventory; add a versioned Gold hard-case catalog with expected structures, including entity/event/state/coref cases drawn from §237.5 and §257H
- **Scientific impact:** Prevents counting 283 phrases as Gold tests; makes G16-SEM/GRAPH testable
- **Execution-plan impact:** Step 16 authors annotation/hard_case_catalog_v1.jsonl
- **Status:** PROPOSED_ONLY

## CR-23 (G_D) — SSOT §236.1 L25589-25598 and §236.5 Stage 1 L25627 (Deep Gold ~750-1,000; Gold-Light ~3-5k)
- **Current SSOT text / assumption:** Fixed target sizes without power justification; Gold-Light counted in recipes
- **New evidence:** CI arithmetic: 200 dual-annotated recipes give about +/-0.03 event F1 (effective n 540-1,050); largest public recipe flow-graph Gold is 300 (Yamakata 2020); human capacity is two people
- **Proposed change:** Stage Deep Gold DG-0 30 -> DG-1 100-200 -> DG-2 ~500 -> 750-1,000 only if CI analysis requires; define Gold-Light in units (lines/mentions/events)
- **Scientific impact:** Gold sized to the claims it supports; no fabricated precision
- **Execution-plan impact:** Steps 19/20/36 Gold budgets set from DG-0 timing
- **Status:** PROPOSED_ONLY

## CR-24 (G_D) — SSOT §237.1 L25661-25689 ('should not see the model/Silver prediction first when avoidable') vs inv. #16 L25147-25170
- **Current SSOT text / assumption:** Handbook wording permits exceptions; invariant forbids
- **New evidence:** Anchoring studies (Schroeder 2025; Choi 2024); repo Gold v1/v1.1 AI-drafted
- **Proposed change:** Deep Gold MUST be annotated blank; model-assisted review allowed only for Gold-Light with MODEL_ASSISTED_HUMAN_REVIEWED provenance; never score a model on labels it suggested
- **Scientific impact:** Restores independence of evaluation and calibration data
- **Execution-plan impact:** Step 19 protocol; tier registry v2
- **Status:** PROPOSED_ONLY

## CR-25 (G_D) — SSOT §238.151 Event L25931-25962 / §257C Event L30472-30673; §238.175 Entity; §238.189 State
- **Current SSOT text / assumption:** Event lacks event_kind, implicit arguments, alternative groups, modality, temporal relation, condition-profile link, allocation basis; Entity.quantity_state_id references an undefined type; State.timestamp vs event_index vs elapsed time undefined; no clock tag
- **New evidence:** Recipe flow-graph literature (RISeC zero anaphora; r-FG); S109 'or' lines mis-modelled; L13E two-clock law L42996-43021
- **Proposed change:** Add the listed Event fields; define Entity parentage/lifecycle and quantity state; add clock tag (TAU_PROCESS) and cumulative elapsed time
- **Scientific impact:** Graphs representable without improvisation; tau/t never mixed
- **Execution-plan impact:** Step 16 schema v1
- **Status:** PROPOSED_ONLY

## CR-26 (G_D) — SSOT §238.103 Quantity / §257C Quantity L30068-30289 vs §257A.2 step 7 L28003
- **Current SSOT text / assumption:** Only scalar normalized_mass_g/volume_ml while 257A.2 requires interval/distribution output; lookup ladder adds 'other approved national table' with no Q-level
- **New evidence:** ssot_annexA C3/C4; repo POR.basis CONVENTION unmapped
- **Proposed change:** Add normalized_mass_low_g/high_g, interval_semantics, quantity_scope, measured_state, as_purchased_vs_edible; map national tables and CONVENTION to explicit Q-levels
- **Scientific impact:** No collapse of intervals to fake point grams
- **Execution-plan impact:** Steps 16/17 CQPO
- **Status:** PROPOSED_ONLY

## CR-27 (G_D) — SSOT §257P L42705-42723 vs Master Plan v4.0 B07 L386 / AI5 L3118
- **Current SSOT text / assumption:** SSOT gates 60k-100k production; MP gates scaling past 10k and also says do not launch 10k if any item fails; P-A11 (pilot cost known) presupposes a pilot
- **New evidence:** Logical circularity of P-A11
- **Proposed change:** Run the 10k pilot with all items except P-A11; require all 15 items before exceeding 10k
- **Scientific impact:** None (governance clarity)
- **Execution-plan impact:** Step 20 gate G20.1/G20.3
- **Status:** PROPOSED_ONLY

## CR-28 (G_D) — SSOT §192.5 L15021-15030 / §191.3 L14782-14785 / §257C Recipe.20 L29532-29540 (duplicate_group_id)
- **Current SSOT text / assumption:** Split unit must include near duplicates/cross-source copies; repo duplicate_group_id is exact-only and 257C forbids silent reinterpretation
- **New evidence:** 07I-R: 1,039 exact groups vs 6,589 provisional edges; r_l13e_identity, r_eval_splits
- **Proposed change:** Keep duplicate_group_id exact; add versioned split_group_id (recall-oriented, calibrated) as the mandatory split unit
- **Scientific impact:** Leakage-safe recipe evaluation
- **Execution-plan impact:** 07I-C; Steps 16-20, 35, 36
- **Status:** PROPOSED_ONLY

## CR-29 (G_D) — SSOT §234.7 L25478 NEEDS_HUMAN_REVIEW vs §239.3 L26185 HUMAN_REVIEW; §234 vocabulary families (no endpoint family)
- **Current SSOT text / assumption:** Two spellings of the review state; endpoints mixed into process vocabulary in practice
- **New evidence:** ssot_l16 §9; repo PROC has 9 ENDPOINT rows
- **Proposed change:** Single enum value; add V_ENDPOINT (or place endpoints under V_STATE explicitly)
- **Scientific impact:** Low
- **Execution-plan impact:** Step 16 vocab registries
- **Status:** PROPOSED_ONLY

## CR-30 (G_E) — SSOT 223.5 (L24119-24121) 'validated domain'; 210.29 kinetic evidence schema (L19111-19136); 212.53 provenance graph (L20567-20581)
- **Current SSOT text / assumption:** 'Validated domain' is used as a binding limit but never defined; the kinetic schema has no domain field; calibration range and validation coverage are not distinguished
- **New evidence:** QMRF v1.2 separates goodness-of-fit from external predictivity; NASA-STD-7009B defines Domain of Validation vs M&S Limits; Sahigara 2012 shows box domains miss empty regions; Baranyi 1996 / Le Marc 2005 use the minimum convex polyhedron (r_mechanism_registry F2.1-F2.4; r_simulator_vv Q3)
- **Proposed change:** Define three distinct objects: calibration domain (design points + MCP/hull of fitted data), validated domain (derived only from study-disjoint held-out VAL records), and M&S limits (structural assumption limits); require every model-estimate output to carry domain_flag in {IN_VALIDATION_DOMAIN, IN_CALIBRATION_ONLY, EXTRAPOLATED_WITHIN_LIMITS, SIM_PROHIBITED}
- **Scientific impact:** Prevents fit statistics or calibration coverage being reported as validation; makes 223.5 enforceable
- **Execution-plan impact:** Steps 24 (FORM/PARAM/VAL schemas), 25 (domain location), 27 (VAL writes), 36 (packet domain flag); simulated_state_changes_schema validation_scope must derive from VAL
- **Status:** PROPOSED_ONLY

## CR-31 (G_E) — SSOT 210.29 (L19111-19136), 211.50 (L19806-19827), 216.2 (L22800-22823), 216.3 (L22825-22845), 213.42 (L21171-21187)
- **Current SSOT text / assumption:** Five overlapping kinetic/reaction field lists with no canonical union (e.g. 'verified' only in 210.29, 'identifiability_status' only in 216.2, 'measured/inferred' only in 213.42)
- **New evidence:** Repo has none of these tables (no KINETIC/PARAM/RXN rows); FSK-ML/PMF-ML parameter metadata and SABIO-RK condition keying show the needed union; ssot_l15a C10 and ssot_l15b contradiction 5
- **Proposed change:** One canonical kinetic-parameter contract = union of the five lists plus K_level, T_ref, fit_T_range/fit_t_range, origin {AUTHOR_REPORTED, PROJECT_REFIT}, ci_method, partition, lineage ids; reaction ledger references parameters by id
- **Scientific impact:** Prevents incompatible parameters being pooled and author fits being conflated with project refits
- **Execution-plan impact:** Step 04 contract, Step 09 extraction fields, Step 24 PARAM schema, Step 32 reuse
- **Status:** PROPOSED_ONLY

## CR-32 (G_E) — SSOT 215.60 decision hierarchy (L22525-22539); G16-TRANS (~L27470); rule 12 (L18026)
- **Current SSOT text / assumption:** Decision hierarchy: direct evidence -> calibrated interpolation -> broader qualitative -> abstain; mechanism/formula/parameter applicability and competing mechanisms are not explicit preconditions of the model rung
- **New evidence:** r_mechanism_registry F6.1: brief s20 chain needs three-valued gates, competing-mechanism and input-observability gates; repo COND has 0% pH/aw/moisture so implicit applicability would silently pass on defaults
- **Proposed change:** State explicitly: the MODEL/SIMULATE rung requires mechanism applicability PASS, no unresolved competing mechanism on the target, all model inputs observed (no imputation), compatible parameters, and domain_flag IN_VALIDATION_DOMAIN; any UNKNOWN routes to QUALITATIVE/ASK/ABSTAIN
- **Scientific impact:** Hard guarantee that qualitative plausibility is never converted into a quantitative simulation automatically (brief s20)
- **Execution-plan impact:** Step 23 route rule; Step 36 cascade; G16-TRANS evaluation
- **Status:** PROPOSED_ONLY

## CR-33 (G_E) — SSOT 210.29A focused anchors (L19137-19163) [reference; owned by Phase-F drafter]
- **Current SSOT text / assumption:** Names potato/frying/acrylamide and glucose/glycine Maillard as focused simulator anchors
- **New evidence:** r_simulator_vv Q1: ascorbic acid in vegetables has the largest independent K1/K2 literature, low decision consequence, an existing E3 consumer (1,196 vitamin C rows); acrylamide is precursor-dependent, safety-critical, degradation parameter poorly identified (Knol 2009)
- **Proposed change:** Allow SIM-AA-1 (ascorbic acid) as first focused simulator with SIM-CHL-1 fallback; keep acrylamide/Maillard as RESEARCH_ONLY extension after Step 27 PASS
- **Scientific impact:** First simulator chosen by data availability and validation feasibility, not prominence
- **Execution-plan impact:** Step 24b population order; Steps 10-14 kinetic quotas; Step 26/27
- **Status:** PROPOSED_ONLY

## CR-34 (G_F) — §210.29A (L19137-19162) and §226.5 M3 (L24541-24547)
- **Current SSOT text / assumption:** Focused anchor simulators = potato/frying/acrylamide and glucose/glycine Maillard [SOURCE-REPORTED]
- **New evidence:** Acrylamide in foods needs co-reported precursors and surface T/moisture; degradation parameters poorly identified in crisps (Knol et al. 2009 [V-meta]); safety-critical COU (high V&V 40 risk). Maillard model-system parameters do not transfer to foods (van Boekel 2008 [V]). Ascorbic acid has the largest K1/K2 literature (r_acquisition) and addresses the leaching-vs-destruction question (SSOT §144.2 L8992; MP L614). Repo has 0 series for any candidate.
- **Proposed change:** First focused simulator = ascorbic acid in vegetables under water/steam heating (two-pathway: degradation + leaching), with chlorophyll->pheophytin as pre-registered fallback; acrylamide and Maillard retained as later RESEARCH_ONLY anchors (Step 32 extension) after the first simulator passes held-out validation.
- **Scientific impact:** Lower-risk first COU; explicit leaching compartment; matrix-scoped parameters; acrylamide/Maillard work deferred, not dropped
- **Execution-plan impact:** Steps 10-14 acquisition quotas target AA/CHL series; Steps 21-25 populate AA/CHL entries first; Steps 26-27 per G_F cards
- **Status:** PROPOSED_ONLY

## CR-35 (G_F) — §223 (L24064-24268) synthetic tiers; §274.2 (L44358-44360)
- **Current SSOT text / assumption:** L15 synthetic rules: ratio sweep, TSTR/TRTR, memorisation checks, hard prohibition; randomized-simulator control defined only for L13E (§274.2); 'validated model' (L24080) undefined
- **New evidence:** Simulator pretraining helped only when pretraining spanned more variability than real training (Read et al. 2019 [V-meta]); gains can reflect added volume rather than physics (§274.2 logic); calibration-study leakage into downstream tests is possible
- **Proposed change:** Add to §223 for L15: (a) matched-volume randomized/wrong-physics simulator control; (b) real-n learning curve; (c) calibration-leakage rule SIM-CAL subset DS-TRAIN, DS-TEST disjoint from SIM-CAL; (d) variability-span precondition; (e) mandatory per-row provenance (sim_version, seed, domain_flag, validation_status); (f) define 'validated model' as Step-27 VALIDATED_HELD_OUT within a declared domain of validation (NASA-STD-7009B sense).
- **Scientific impact:** Prevents spurious synthetic-prior gains and leakage
- **Execution-plan impact:** Step 28 controls C-1..C-8; executed in Steps 30/33
- **Status:** PROPOSED_ONLY

## CR-36 (G_F) — §201.7 evidence tiers E1-E6 (L16651-16661) vs MP L587-595 / repo registry E1-E7
- **Current SSOT text / assumption:** SSOT has no E7 tier; E6 = heuristic/qualitative; MP and repo define E7 = simulator output (SIMULATED); 'E7' label also used for L12 encoder rung (L8497) and L13E Phase E7 (L45417)
- **New evidence:** Repo registry/evidence_tier_provenance_map_v1.csv and simulated_state_changes_schema_v1.csv already bind E7=SIMULATED; namespace collision confuses 'Step 28 E7 prior'
- **Proposed change:** Add tier E7 = SIMULATED (never evaluation-eligible) to §201.7 or publish a crosswalk; namespace evidence tiers as TIER-E1..TIER-E7 in plan text.
- **Scientific impact:** None (clarity)
- **Execution-plan impact:** Step 04 crosswalk; Step 28 renamed
- **Status:** PROPOSED_ONLY

## CR-37 (G_F) — §215.57 kinetic ablation K0-K6 (L22486-22501) vs §210.28 kinetic data hierarchy K0-K4 (L19089-19109)
- **Current SSOT text / assumption:** Two different 'K0..' ladders (ablation arms vs data rungs)
- **New evidence:** Both are used in Steps 26/27/32 cards and acquisition triage; collision causes mislabelled reports
- **Proposed change:** Rename ablation family to KA0-KA6 (keep K0-K4 for data rungs).
- **Scientific impact:** None (clarity)
- **Execution-plan impact:** Steps 26d, 32 reporting
- **Status:** PROPOSED_ONLY

## CR-38 (G_F) — §215.38 G15-10 (L22391) 'without unacceptable calibration damage'; G15-4 (L22385)
- **Current SSOT text / assumption:** No numeric threshold; G15-4 implicitly owned by focused-kinetics work
- **New evidence:** No-post-hoc-gate-weakening law requires pre-registered numbers; simulator calibration (Step 26d) produces the first focused identifiable fit
- **Proposed change:** Operationalise G15-10 calibration damage as PROPOSED_PILOT: real-only 90% coverage drop >0.03 absolute or interval width increase >20% on any headline study-disjoint split = unacceptable; allow G15-4 to be first evidenced by the Step-26 calibration identifiability report.
- **Scientific impact:** Gate becomes decidable
- **Execution-plan impact:** Steps 26, 28, 30, 32, 33
- **Status:** PROPOSED_ONLY

## CR-39 (G_G) — §215.38 G15-11 (L22392)
- **Current SSOT text / assumption:** 'A trust horizon is empirically established on D-C/D-D where true intermediate states exist'
- **New evidence:** D-D 'Does not directly support quantitative chemistry' (L21994-21996); procedural rollout != chemistry rollout (L19966-19970)
- **Proposed change:** State that a G15-11 pass on D-D licenses only R0/R1 procedural/qualitative rollout; R2+ requires D-C intermediates. Status PROPOSED_ONLY.
- **Scientific impact:** Prevents a recipe-Gold horizon being cited as a chemistry trust horizon
- **Execution-plan impact:** Step 34b gate wording; Step 36 rollout rung
- **Status:** PROPOSED_ONLY

## CR-40 (G_G) — §215.38 G15-1 (L22382)
- **Current SSOT text / assumption:** 'Every quantitative row has source/study ...'
- **New evidence:** 13,888-14,108 of 17,978 ACTIVE EVD rows (USDA/Bognar) have study NOT_IDENTIFIABLE; database aggregates have no study unit
- **Proposed change:** Allow independence_resolution {STUDY, PUBLICATION_ONLY, SOURCE_FAMILY_ONLY, UNKNOWN} plus lineage_root_id as the status for database aggregates. G15-1 audits status completeness, not study presence. Status PROPOSED_ONLY.
- **Scientific impact:** G15-1 becomes passable without fabricating study IDs (MP AH1)
- **Execution-plan impact:** Step 29 G29-A; Step 08 outputs
- **Status:** PROPOSED_ONLY

## CR-41 (G_G) — §216.12 minimum package (L22988-23032) and §215.28/§216.7 'D0-D4 baselines'
- **Current SSOT text / assumption:** Package lists persistence, process_mean, nearest_evidence, ridge, lightgbm, tabpfn_if_applicable; no D3 shrinkage, no D7 completion, no propensity/mask audit; MVP says D0-D4 while G15-2 says D0-D6
- **New evidence:** §226.4 M2 and G15-2/G15-9 require D3, D6, D7 and propensity sensitivity
- **Proposed change:** Align the package with §209.17 D0-D7 and §226.4 (add D3 hierarchical, D7 completion, propensity and mask audit modules); state the MVP as 'D0-D4 first, D5-D6 before any D7+ claim'. Status PROPOSED_ONLY.
- **Scientific impact:** Removes an internal inconsistency that makes G15-2 unpassable by the MVP
- **Execution-plan impact:** Steps 29-30 module list
- **Status:** PROPOSED_ONLY

## CR-42 (G_G) — §215.71 (L22707-22722) vs §216.7 DAG (L22914-22918)
- **Current SSOT text / assumption:** Physics features before kinetics in §215.71; kinetic fits before physics features in §216.7
- **New evidence:** §210.13 permits representative-Ea features without fitting (L18856); §211.49 multi-fidelity bridge uses fitted parameters (L19794-19804)
- **Proposed change:** Clarify: generic physics features (literature Ea grid) precede focused kinetics; fitted-parameter features follow them. Status PROPOSED_ONLY.
- **Scientific impact:** Both orders are valid for different feature types
- **Execution-plan impact:** Step 31 split into 31a/31b
- **Status:** PROPOSED_ONLY

## CR-43 (G_G) — §215.38 G15-5/6/9/10/11 and §215.39 G15-HYB
- **Current SSOT text / assumption:** No numeric thresholds ('acceptable', 'beats', 'meaningful', 'unacceptable calibration damage')
- **New evidence:** §202.17 pilot values are unrecoverable (656-line source report absent); the no-post-hoc-weakening law
- **Proposed change:** Add a rule: every G15 gate's numeric operationalisation (margin, cluster minimum, coverage floor, statistic) must be pre-registered in the step contract before the first locked-test read, and changes logged as decisions. Status PROPOSED_ONLY.
- **Scientific impact:** Makes the gates falsifiable
- **Execution-plan impact:** registry/phase_g_preregistration_v1.csv
- **Status:** PROPOSED_ONLY

## CR-44 (G_G) — §215.38 G15-9 (L22390)
- **Current SSOT text / assumption:** 'Evidence-aware D7 completion beats D5/D6 ... or is rejected'
- **New evidence:** §220.4 (L23590-23606): the mixed model D3 'serves the same broad purpose as factorization ... should be benchmarked before advanced completion'
- **Proposed change:** Include D3 (full hierarchical partial pooling) in the G15-9 comparator set: D7 must beat D3/D5/D6. Status PROPOSED_ONLY.
- **Scientific impact:** Prevents accepting completion that merely re-learns hierarchical means
- **Execution-plan impact:** Step 30 G30-B
- **Status:** PROPOSED_ONLY

## CR-45 (G_H) — SSOT L10671 (§175 F3)
- **Current SSOT text / assumption:** Praski et al. 2025 (pretrained encoders rarely beat ECFP) labelled [FROZEN].
- **New evidence:** arXiv 2508.06199 v4 (Feb 2026) has no peer-reviewed venue; conclusion corroborated by Deng et al. Nat Commun 2023 and MoleculeNet 2018.
- **Proposed change:** Relabel as 'preprint, corroborated by peer-reviewed Deng 2023 / MoleculeNet'.
- **Scientific impact:** None on default (fingerprint baseline stays); evidence labelling correctness.
- **Execution-plan impact:** 35a cites corroborating peer-reviewed sources.
- **Status:** PROPOSED_ONLY

## CR-46 (G_H) — SSOT L10690 (§175.3 FlavorDB2 row)
- **Current SSOT text / assumption:** FlavorDB2 = 25,595 molecules; 2,254 linked to 936 ingredients, 34 categories.
- **New evidence:** These are the FlavorDB 2018 counts (Garg et al. NAR 46:D1210); FlavorDB2 (arXiv 2205.05451) counts not stated in abstract (UNVERIFIED).
- **Proposed change:** Attribute counts to FlavorDB 2018; mark FlavorDB2 counts and licence UNVERIFIED (licence also inconsistent: L10685 'Free web' vs RESOURCE_GAP_MAP CC BY-NC-SA vs manifest DS-024 UNKNOWN).
- **Scientific impact:** Coverage audits and novelty statements depend on correct source counts.
- **Execution-plan impact:** Step 06/12 licence row; 35b coverage report.
- **Status:** PROPOSED_ONLY

## CR-47 (G_H) — SSOT L15106 (§193 Phase 0 prerequisite)
- **Current SSOT text / assumption:** Phase 0 requires Level-12 ingredient representations available.
- **New evidence:** R0, R2-explicit, C0-C2, motif tables and confound audits do not use z_i; L12 is 0/12 complete.
- **Proposed change:** Phase 0 explicit baselines require only canonical identity tables; Level-12 z_i required only for R1-pooled/R2-pooled/R3-R7.
- **Scientific impact:** None (explicit baselines unchanged).
- **Execution-plan impact:** Enables 35c/35d in parallel lane.
- **Status:** PROPOSED_ONLY

## CR-48 (G_H) — SSOT L13782 vs L14738 (R2)
- **Current SSOT text / assumption:** R2 = frequency/IDF-weighted pooling of z_i; §191.1 lists an IDF-weighted explicit vector.
- **New evidence:** Ambiguity blocks Phase 0 ordering.
- **Proposed change:** Define R2-explicit (TF-IDF incidence) and R2-pooled (IDF-weighted pooling of z_i) as separate rungs.
- **Scientific impact:** Clarifies baseline identity.
- **Execution-plan impact:** 35c rung list.
- **Status:** PROPOSED_ONLY

## CR-49 (G_H) — SSOT §191.3 L14782-14785 / §192.5 L15021-15030 / §257C Recipe.20 L29532-29540
- **Current SSOT text / assumption:** duplicate_group_id is the split unit and includes near-duplicates/cross-source copies.
- **New evidence:** Repo duplicate_group_id is exact-only (07I-R preregistration); §257C forbids silent reinterpretation.
- **Proposed change:** Add versioned split_group_id (recall-oriented, calibrated in 07I-C) as the split unit; keep duplicate_group_id = exact.
- **Scientific impact:** Correct leakage control on recipe plane.
- **Execution-plan impact:** 07I-C output; 35c/35d/16-20/36 consume it.
- **Status:** PROPOSED_ONLY

## CR-50 (G_H) — SSOT L12200, L12454, L12518, L13148 ('FP2')
- **Current SSOT text / assumption:** Baseline fingerprint named FP2 in several places; G2 expects ECFP4 counts + LightGBM.
- **New evidence:** Repo SIM-06 freezes Morgan r2 2048 binary; MOL stores only CACTVS-881.
- **Proposed change:** Freeze reference = ECFP4/Morgan r2 (2048, bit and count reported) + LightGBM; FP2 only as historical comparator.
- **Scientific impact:** Single comparator across gates.
- **Execution-plan impact:** 35a reference.
- **Status:** PROPOSED_ONLY

## CR-51 (G_H) — SSOT L12843 vs L128
- **Current SSOT text / assumption:** Tri-state missingness {known, unknown, not applicable} vs four distinct states ND / below-LOD / not measured / unchanged.
- **New evidence:** Tables E/G and x_ij need both.
- **Proposed change:** Superset enum {MEASURED, QUALITATIVE_PRESENT, ND, BELOW_LOD(+LOD), NOT_MEASURED, NOT_APPLICABLE, UNCHANGED, UNKNOWN}.
- **Scientific impact:** Prevents UNKNOWN=0 coercion.
- **Execution-plan impact:** Step 03/04 enum; 35b schema.
- **Status:** PROPOSED_ONLY

## CR-52 (G_H) — SSOT L11217 vs L8506-8508
- **Current SSOT text / assumption:** §12.3.4 lists process-response similarity as contrastive positive pairs; §133.3 says raw->processed supervises a transition vector, not invariance.
- **New evidence:** Internal contradiction.
- **Proposed change:** Raw->processed pairs never used as invariance positives; process-response similarity only for z^process-specific spaces with that label.
- **Scientific impact:** Avoids erasing process effects from static encoders.
- **Execution-plan impact:** 35g objective constraints; 35f.
- **Status:** PROPOSED_ONLY

## CR-53 (G_H) — SSOT G3/G4/G7 (L10796-10900)
- **Current SSOT text / assumption:** Gates evaluable only on GS-LF, Keller and ingredient-level sensory labels.
- **New evidence:** No such labels in repo; RESOURCE_GAP_MAP L19 marks them out of scope; no public ingredient-level sensory labels found; GS-LF licence UNVERIFIED.
- **Proposed change:** Keep gates verbatim but add explicit DATA-BLOCKED status and allow decision records to report it; define available-task variants (taste classes, structural retrieval, held-out co-occurrence) as separate pre-registered gates.
- **Scientific impact:** No weakening: sensory claims remain blocked.
- **Execution-plan impact:** 35a/35b gates; FlavorTwin sensory wording.
- **Status:** PROPOSED_ONLY

## CR-54 (G_H) — SSOT L13874 vs L14129; L13836 vs L14161
- **Current SSOT text / assumption:** Relative prevalence uses (C-1) vs (K-1); IDF_i used for recipe-level and cuisine-level quantities.
- **New evidence:** Notation collision.
- **Proposed change:** One definition; name recipe-IDF and cuisine-IDF distinctly.
- **Scientific impact:** Reproducibility.
- **Execution-plan impact:** 35d reference implementation.
- **Status:** PROPOSED_ONLY

## CR-55 (G_H) — SSOT §270.1 date_basis enum (L44035-44047)
- **Current SSOT text / assumption:** {exact_publication, edition, archive_estimate, first_attestation, inferred, unknown}.
- **New evidence:** Repo era uses AUTHOR_BORN_* (Gutenberg) and Food.com upload year; Gutenberg Issued = eBook release date.
- **Proposed change:** Add AUTHOR_BIRTH_PROXY (or map to inferred with low confidence) and DOCUMENT_UPLOAD_DATE; forbid treating them as recipe-origin dates.
- **Scientific impact:** Blocks spurious temporal claims (G13E-01).
- **Execution-plan impact:** 35-E 35E.0; Step 06/07 metadata.
- **Status:** PROPOSED_ONLY

## CR-56 (G_H) — SSOT §278.8 L45436 vs G13E-02 L45279
- **Current SSOT text / assumption:** Identity calibration placed after reproductions; lineage groups must be frozen before any split.
- **New evidence:** Every recipe split depends on calibrated groups.
- **Proposed change:** Split E13E-05 into 05a near-duplicate/lineage calibration (core, 07I-C) and 05b multiview variant labels (L13E Phase E3).
- **Scientific impact:** Leakage control precedes temporal work.
- **Execution-plan impact:** 07I-C owns 05a; 35-E keeps 05b optional.
- **Status:** PROPOSED_ONLY

## CR-57 (G_I) — §242.8 L26434-26446; §242.6 L26411-26422; §215.60 L22525-22540
- **Current SSOT text / assumption:** Cascade DIRECT -> interpolation -> L15 model -> qualitative -> abstain; no ASK; CONFLICTING listed as a sufficiency mode; MP AI7/AZ8 disagree
- **New evidence:** Four incompatible cascade lists (SSOT, MP AI7, MP AZ8, brief §28); §243.8 VOI ASK; §257M.10 critical-unknown -> ASK; conflict is orthogonal to support level
- **Proposed change:** Canonical rung enum DIRECT/INTERPOLATE/MODEL/QUALITATIVE/ASK/ABSTAIN with VOI-pre-emptive ASK; conflict_status orthogonal forcing REPORT_CONFLICT; one crosswalk to §214.30, §246.6, §257A.14
- **Scientific impact:** Unambiguous mode labels for RQ16-06 / mode-F1 evaluation
- **Execution-plan impact:** 36A crosswalk registry; Step 04 enum freeze
- **Status:** PROPOSED_ONLY

## CR-58 (G_I) — §242.4 L26403-26406; §242.5 L26407-26410
- **Current SSOT text / assumption:** Logistic/Platt/isotonic/small trees; ECE unspecified
- **New evidence:** Isotonic overfits below ~1,000 labels (scikit-learn docs); binned ECE biased (Kumar et al. NeurIPS 2019); AURC/E-AURC (Geifman et al. ICLR 2019)
- **Proposed change:** Isotonic only with >=~1,000 labels per decision; ECE equal-mass + debiased + bootstrap CI; add AURC/E-AURC
- **Scientific impact:** Avoids overfit calibration on 10^2-scale label sets
- **Execution-plan impact:** 36C calibration protocol
- **Status:** PROPOSED_ONLY

## CR-59 (G_I) — §241.1 R5 L26330
- **Current SSOT text / assumption:** Cross-encoder reranking as a default retrieval stage
- **New evidence:** Repo negative result bge-reranker-large dMRR -0.056 [-0.091,-0.017]; topical rerankers lack scientific hard negatives
- **Proposed change:** Generic CE is a control; R5 slot is a compatibility classifier trained on scientific hard negatives, promoted only if it beats structured retrieval on human labels
- **Scientific impact:** Retains negative result; aligns with RQ16-03
- **Execution-plan impact:** 36C retrieval ladder
- **Status:** PROPOSED_ONLY

## CR-60 (G_I) — §257M mandatory fields (L42164ff)
- **Current SSOT text / assumption:** Query ID, state version, packet version, evidence class, known unknowns, claim/citation map, model version, confidence features, response mode
- **New evidence:** Auditability of precision cap, lineage independence, conflicts and licence requires more fields (research/r_rag_confidence.md §3.4)
- **Proposed change:** Add certainty profile, evidence status, conflict clusters + trace, rejected candidates, independence summary, model-estimate block, assumptions/conversions, answerability/VOI, claim route, licence flags, snapshot hashes
- **Scientific impact:** Makes G16-PROV/CONFLICT/OOD measurable
- **Execution-plan impact:** PKT v2 schema (36A)
- **Status:** PROPOSED_ONLY

## CR-61 (G_I) — §249.1 G16-* L27446-27487
- **Current SSOT text / assumption:** Gates use 'declared threshold' / 'acceptable' with no numbers
- **New evidence:** Law: no post-hoc gate weakening; numberless gates invite post-hoc setting
- **Proposed change:** Require pre-registered operational thresholds per G16 gate in the experiment card before test access; G36-* as first instantiation
- **Scientific impact:** Falsifiable system claims
- **Execution-plan impact:** 36B/36C pre-registration
- **Status:** PROPOSED_ONLY

## CR-62 (G_I) — §232.3 L25268 vs §233.7 L25387-25391
- **Current SSOT text / assumption:** D^simulated a separate plane vs simulations merged into Model memory
- **New evidence:** Brief §13 requires a SIMULATION plane; Step 28 E7 prior must never be surfaced as an answer
- **Proposed change:** Keep SIMULATION memory a separate plane in all contracts
- **Scientific impact:** Prevents simulated values entering evidence sections
- **Execution-plan impact:** Packet MODEL ESTIMATES split into MODEL and SIMULATION sub-blocks
- **Status:** PROPOSED_ONLY

## CR-63 (G_I) — §247 RQ16-14 L27045-27047
- **Current SSOT text / assumption:** Data: simulated/real multi-turn sessions
- **New evidence:** Invariant #15: synthetic data never in final test; repo has 30 AI-drafted sessions, 0 reviewed
- **Proposed change:** Simulated sessions are development-only; headline claims require real held-out sessions
- **Scientific impact:** Valid session-memory claims
- **Execution-plan impact:** 36B session items must be real
- **Status:** PROPOSED_ONLY

## CR-64 (G_I) — §242.3 L26399-26402 (vs repo registry/recipe_quality_tier_registry_v1.csv)
- **Current SSOT text / assumption:** Independently verified calibration data required; repo tier GOLD_PENDING_INDEPENDENT_IAA permits calibration use
- **New evidence:** D-016/D-017: existing Gold AI-drafted, batch-approved; anchoring literature (Choi 2024; Schroeder 2025)
- **Proposed change:** State explicitly that AI-assisted/joint Gold cannot support G16-CAL; calibration partition independent and lineage-disjoint
- **Scientific impact:** Prevents circular calibration
- **Execution-plan impact:** 36B/36C partition rules; Step 19 Deep Gold dependency
- **Status:** PROPOSED_ONLY

## CR-65 (G_I) — §246.8 L26775-26778
- **Current SSOT text / assumption:** Static baselines random/category/ECFP/descriptors/static embeddings/multiview
- **New evidence:** FoodPuzzle (KDD 2025), FlavourBench (2026 preprint), GISMo (2023), LLM-DPO substitution (2025); Jain, Rakhi & Bagler 2015 frequency confound
- **Proposed change:** Add LLM zero-shot/RAG and contextual-substitution baselines; frequency-preserving/Curveball null for any pairing statement
- **Scientific impact:** Non-trivial FlavorTwin comparisons
- **Execution-plan impact:** 36D baseline set
- **Status:** PROPOSED_ONLY
