# mp_part2 — Final Master Plan v4.0, lines 2451–4879 (Parts AB3 → BB), plus v2.0-vs-v4.0 diff

Reader: mp_part2 · Date 2026-10-22 · Read-only. All "MP Lxxxx" = `docs/plan/CulinaryState_Final_Master_Plan_SSOT15_v4_0.md` line numbers; "SSOT Lxxxxx" = `docs/SSOT/computational_gastronomy_master_ssot_v15_0.md`.
The 36-step Master Execution Plan v1 is NOT in the repo; every spine mapping in §8 is my reconstruction from this plan text + SSOT + repo, NOT card text.

## 0. Scope, structure and v2.0 diff (done first)

**Assigned range content (MP L2451–4879):**
- AB3–AB4 (L2440–2471) bench/lab-in-the-loop experimental contract (AB1–AB2 at L2411–2438 read for context).
- AC (L2475–2492) research stop / futility / scope rules.
- AD (L2496–2533) Definition-of-Done matrix.
- AE (L2537–2584) agent/skill layout.
- AF (L2588–2650) startup contract + mantra.
- **Everything from AG onward (L2654–4879) is labelled "v3.0"** and is the content that was added to v2.0:
  - AG verdict/lanes/status enum/authority (L2654–2753)
  - AH corrections AH1–AH15 (L2757–2984)
  - AI 8-week plan (L2988–3338)
  - AJ work packages (L3342–3399)
  - AK experiment coverage (L3403–3470)
  - AL deliverable tiers (L3474–3554)
  - AM DEL-2 contract (L3558–3632)
  - AN DEL-3 contract (L3636–3687)
  - AO DEL-4/5 contract (L3691–3776)
  - AP 10k Silver (L3780–3827)
  - AQ B03/B04/B08/B15 (L3831–3866)
  - AR compute (L3870–3916)
  - AS professor email (L3920–3947)
  - AT operating loop (L3951–3992)
  - AU Claude command (L3996–4020)
  - AV program definition (L4024–4072)
  - AW NER verdict (L4076–4349)
  - AX dataset inventory (L4353–4472)
  - AY ledger system (L4476–4596)
  - AZ program map Tracks A–K (L4600–4791)
  - BA summary (L4795–4849)
  - BB 20 principles (L4853–4879)

**Diff: v2.0 Max Master Prompt vs v4.0 (concrete result of `diff`):**
- v2.0 is a strict prefix of v4.0. There are only two differences.
  - Line 2 (subtitle): v2.0 reads "Operating system for Claude … v2.0 · built against SSOT v15.0 (6 Oct 2026)". v4.0 reads "FINAL operating system + all-inclusive master plan for Claude … v4.0 · built against SSOT v15.0 (6 Oct 2026)".
  - v4.0 appends L2651–4879 (2,229 new lines plus a separator, Parts AG–BB).
- `diff | grep -c '^<'` = 1, which is the subtitle line only. Lines 1 and 3–2650 are byte-identical.
- **v2.0 adds NOTHING that is not in v4.0.** It is fully superseded. This confirms reports/step07i/plan_authority_inventory.md.
- Corollary: the missing `…Final_Execution_Plan_v3_0.md` referenced at MP L4004 almost certainly equals "v2.0 + Parts AG–BB", because those parts are labelled "v3.0" in their headings (L2654, L2757). UNVERIFIED: the v3_0 file itself is absent, so it cannot be compared.

## 1. Definitions, entities and data contracts (field-level where given)

### 1.1 Evidence-origin contract (AH1, MP L2759–2787) — replaces "study_ids non-empty"
- `origin_type ∈ {PRIMARY_STUDY, DATABASE_AGGREGATE, REVIEW_AGGREGATE, AUTHORITY_STANDARD, PROJECT_MEASUREMENT}` (L2772–2777).
- `source_family_id` is **always required** (L2779).
- `study_ids`:
  - required for PRIMARY_STUDY-derived / literature-extracted rows "when identifiable";
  - optional for database aggregates;
  - "never fabricated merely to satisfy the schema" (L2781–2784).
- A compiled database may have a STUDY-like compilation record, but it must be typed `DATABASE_AGGREGATE` (L2787). Rationale: USDA R6 has no per-row study lineage (L2761).
- **Repo check (verified):**
  - The `ledgers/data/EVD.jsonl` keys include `origin_type`, `source_family_id`, `study_ids`, `study_id_status` and `independence_group`.
  - Across 57,280 JSONL lines, the `origin_type` counts are DATABASE_AGGREGATE 43,392 and PRIMARY_STUDY 13,888. No REVIEW_AGGREGATE, AUTHORITY_STANDARD or PROJECT_MEASUREMENT rows exist.
  - All DATABASE_AGGREGATE lines have empty study_ids, and all PRIMARY_STUDY lines have non-empty study_ids.
  - The line count (57,280) ≠ the 17,978 "active rows" in WORKLOG L887. The ledger is presumably append-only and versioned. UNVERIFIED which lines are active.

### 1.2 Ingredient identity (AH2, MP L2789–2809; AY2 L4490–4501)
- Canonicalization: raw mention → internal `ING-` → optional crosswalks (RecipeDB, FlavorDB/FlavorDB2, FoodOn, FDC, FooDB, PubChem-linked composition) (L2795–2805).
- `UNRESOLVED_EXTERNAL` is allowed while the internal concept is valid (L2807).
- AY2 IDs:
  - `ING-` concept
  - `ALIAS-` surface/regional/language alias
  - `ENTITY-` actual physical recipe/session lot
  - `MOL-` canonical molecule/InChIKey/structure
  - `IMAP-` ingredient↔molecule evidence mapping
  - `ROLE-` culinary role, optional controlled vocab (L4493–4498)
- "Never use one ID for both 'onion' the concept and 'this onion portion in this pan'" (L4501).

### 1.3 Allergen authority (AH3 L2811–2817; AX5 L4419–4425)
- An `ALLERGEN-` authority table sourced from the current authority, e.g. FSSAI for India. FlavorDB categories are never the allergen authority.
- **Repo:** 11 rows in `ledgers/data/ALLERGEN.jsonl`, with authority_source_id `SRC-000011`. In SRC.jsonl that row is `kind=AUTHORITY_STANDARD`, authors FSSAI, the 2021 Labelling & Display compendium URL, and **licence_status ASSUMED**.
- Human tick `registry/allergens/ing_allergen_review.csv` was pending per WORKLOG L146. Current status UNVERIFIED.

### 1.4 DEL-2 cell (AM1, L3560–3578)
- Course projection: C_course = (food, process, target), "with condition-completeness features/masks retained" (L3567–3570).
- Full programme cell: C = (matrix, S_in, process, Θ, target, measurement basis) (L3575).
- "Course results therefore do not imply universal condition-independent process effects" (L3578).

### 1.5 Retention-factor semantics (AM2 L3580–3595; AI4 L3061–3064)
- Preserve the source definition and **do not clip RF > 1**.
- Record before basis, after basis, yield factor, wet/dry basis, SD/range, n and source method.
- "When data are incompatible, do not merge" (L3595).

### 1.6 Study/source lineage graph (AM3 L3597–3613)
- Graph: `row → source/database → publication IDs → study families` (L3601–3605).
- Split by connected components where feasible.
- If a giant component makes the test unusable:
  - report it;
  - use publication-component CV or source-held-out analysis;
  - "do not claim a study-disjoint result that did not exist" (L3610–3613).

### 1.7 State engine (AN, L3636–3687)
- **Three mandatory identities:** canonical food concept / physical lot-entity / entity version-state, "Never collapse them" (L3640–3646).
- **Symbolic quantities first.** Example (L3652–3662): `50 g butter; reserve 1 tbsp` gives `reserved = 1 tbsp volume; rest = 50 g minus an unresolved correlated portion`. Do not invent grams.
- **Trajectory field:** `trajectory = PLANNED | OBSERVED_SESSION | PREDICTED` on every state field (L3671–3675).
  - Direct user observation overrides current belief for that observable field.
  - Prior predictions are preserved in the audit log (L3677).
- **Hidden steps:** `OMITTED_STEP_CANDIDATE` (L3681). It is not inserted as observed; it has rule/precedent/evidence; it can be accepted or rejected; it is evaluated for precision (L3683–3687).
- **DEL-3 event relations** (AI4 L3069–3072): `TRANSFORMS_INTO, MERGES_INTO, SPLITS_INTO, RESERVED_AS, DISCARDED_FROM, RECOMBINED_WITH, TRANSFERRED_TO, PART_OF, LOCATED_IN, OBSERVED_AS`.
- **Quantity grammar** (AI4 L3076–3079): exact/range/fraction/multiplier/package; locale-aware physical units; "no food-specific grams without `POR-`"; symbolic split/reserve accounting.

### 1.8 Retrieval packet / compatibility / claim (AO, L3691–3776)
- **Packet fields** (L3698–3708): CURRENT STATE · QUESTION/GOAL/CONSTRAINTS · DIRECT EVIDENCE · NEAR EVIDENCE · CONDITION DIFFERENCES · CONFLICTS · MODEL ESTIMATES · KNOWN UNKNOWNS · FEASIBLE ACTIONS · DISALLOWED CLAIMS · CITATION MAP. "The LLM sees a compiled packet, not raw top-k" (L3695).
- **Compatibility vector** (inspectable, L3716–3727): food/matrix, state, process, time, temperature, pH, aw/moisture, medium, geometry, target, measurement basis, source/tier. "Do not collapse immediately to an uninterpretable scalar" (L3730).
- **DEL-4 compatibility axes**, an alternative and shorter list (AI7 L3208–3217): ingredient, prior state, process, conditions, target, matrix, measurement basis, source/tier.
- "UNKNOWN is neutral, not mismatch" (L3219).
- **Evidence support cascade** (AI7 L3222–3228): DIRECT · INTERPOLATED · MODEL_ESTIMATED · QUALITATIVE · CONFLICT · UNSUPPORTED / ABSTAIN.
- **Claim ledger** (AO3 L3736–3745): `CLM-id, type, support class, EVD/source IDs, confidence/calibration output, model version if estimated, citation, scope limitation`.
  - Repo: `ledgers/schemas/CLM.schema.json` exists, but no CLM ledger data file exists in `ledgers/data/` (verified listing).
- **Decision modes** (AO4 L3749–3757; also AI8 L3257–3265): ANSWER, COMPARE, ASK, DIAGNOSE, RECOVER, RECOMMEND, ABSTAIN.
  - "ASK is selected only when the missing observation can materially alter the decision" (L3759).
- **Feasibility inputs** (AI8 L3267–3273): tools; time; dietary/allergen constraints via an authority-backed table; process prerequisites; evidence support; OOD.
- Diagnosis: "proposer and verifier separated" (L3276).
- Recovery: "recovery evidence is separate from cause evidence" (L3279).

### 1.9 Benchmark registry fields (AI6 L3169–3180)
- task type, difficulty, source family, ingredient/process family, evidence regime, answer kind, must-abstain, gold evidence, constraints.

### 1.10 Experiment registry fields (AK1 L3424–3439)
- scope_lane, dependency_ids, priority, owner, reviewer, data requirement, compute class, human requirement, course relevance, paper relevance, status, restart condition.
- **Status enum** (AG3 L2731–2739): ACTIVE_COURSE, ACTIVE_PARALLEL, BLOCKED_EXTERNAL, BLOCKED_GATE, PARKED_POST_COURSE, DROPPED_BY_EXPERIMENT, COMPLETE. AR3 adds `BLOCKED_COMPUTE` (L3915) outside this enum, which is an inconsistency.
- **Repo:** none of `registry/experiments.csv`, `gates.csv`, `research_spawns.csv`, `scope_registry.csv` or `datasets.csv` exists (find returned nothing). Present instead:
  - `ledgers/data/EXP.jsonl` (8 lines)
  - `DATASET.jsonl` (5 lines)
  - schemas `EXP/GATE/RQ/RS/DATASET/SPLIT/MODEL.schema.json`

### 1.11 Bench sample contract (AB3 L2442–2461)
- Pre-run fields: hypothesis, food matrix/lot, sample prep, replicates, controls, randomization, equipment calibration, condition schedule, measurement schedule, primary endpoint, uncertainty, analysis plan, safety plan, data schema.
- "Every measurement becomes a `SAMPLE-` + `EVD-` row with its own evidence tier" (L2461).
- Repo: **no SAMPLE.schema.json** in `ledgers/schemas/` (verified).

### 1.12 Ledger/registry system (AY, L4476–4596) — canonical object list
- **AY1** (L4483–4487): SRC- (source/database/paper identity), SNAP- (exact snapshot/version/hash/retrieval time), API- (endpoint/version/auth/rate-limit/terms), STUDY- (study design / experiment family), MEAS- (measurement method/platform/protocol).
- **AY2:** see 1.2.
- **AY3** (L4506–4512): QNT- parsed quantity expression; UNIT-; POR- ingredient/form/locale-specific portion profile; ALLOC- split/reserve/recombine allocation. "Keep symbolic values when a conversion is unsupported."
- **AY4** (L4517–4536): PROC-, TOOL-, COND- (full condition profile), SVAR- (state-variable registry).
  - COND may contain: time, temperature, pH, moisture, aw, pressure, oxygen, salt/sugar/fat, medium, geometry, particle size, agitation, biological/fermentation variables.
- **AY5** (L4541–4548): INST-, EVT- atomic event, STATE- entity version/state, REF- coreference, GRAPH- recipe/session event-state graph. "Every state transition is append-only."
- **AY6** (L4553–4559): EVD- evidence atom/before-after measurement, RXN- measured/identified reaction relation ("may be partial. Unknown networks remain unknown"), WARN- evidence-backed warning, ALLERGEN-.
- **AY7** (L4564–4577): DATASET-, SPLIT-, PROMPT-, MODEL- (trained/released model), EXP-, GATE-, RQ-, RS-, CLM-, SAMPLE- (project bench/lab sample), DEC- decision record. "No strong claim exists outside `CLM-`."
- **AY8** (L4581–4596): HIST- or a typed table. Fields: edition/publication date, recipe date interval, date basis, date confidence, region, cuisine, language, translation, source genre, lineage/duplicate family, historical-contact metadata, bias/confound fields.
- **Repo schema coverage (verified):**
  - `ledgers/schemas/` has 37 schemas, including API, ALLOC, CLM, ENTITY, EVT, GATE, GRAPH, INST, MODEL, POR, QNT, REF, RQ, RS, RXN, SPLIT, STATE and WARN.
  - **Missing schemas:** SAMPLE, DEC, PROMPT, ROLE, HIST.
  - Data files present only for ALIAS, ALLERGEN, COND, DATASET, EVD, EXP, IMAP, ING, KGE, MEAS, MOL, PROC, REC, SNAP, SRC, STUDY, SVAR, TOOL, UNIT.
  - **Not present as data:** API, QNT, POR, ALLOC, ENTITY, INST, EVT, STATE, REF, GRAPH, RXN, WARN, SPLIT, MODEL, GATE, RQ, RS, CLM.
- **Gap vs brief §18/§21:**
  - AY has no DOCUMENT, EXPERIMENT, external SAMPLE, AGGREGATE or DERIVED level.
  - STUDY- conflates "study design / experiment family" (L4486).
  - There is no mechanism ID (MECH-), formula/kinetic-model registry, parameter registry, or SIM-/KINETIC- object. MODEL- is defined as "trained/released model registry" (L4567), i.e. ML models, not mechanistic equations.

### 1.13 Project dataset releases (AX7 L4449–4472)
- Release names: DATA-SEM-GOLD, DATA-SEM-GOLDLIGHT, DATA-SEM-SILVER, DATA-EVIDENCE, DATA-STATE-GRAPH, DATA-QTY, DATA-VOCAB, DATA-RETRIEVAL-BENCH, DATA-DECISION-BENCH, DATA-TRANSITION-BENCH, DATA-HISTORICAL, DATA-FLAVORTWIN-BENCH.
- Each release has: manifest; schema version; source snapshots; licence matrix; duplicate groups; split registry; data card; hashes (L4464–4472).
- No DATA-SIM / simulation-memory release is listed, despite the brief §13 SIMULATION MEMORY plane.

### 1.14 NER label ontology (AW4 L4160–4188)
- Labels: FOOD, COMPOUND_INGREDIENT, QUANTITY, UNIT, FORM, QUALITY, STATE, PROCESS, ACTION, TOOL, MEDIUM, TIME, TEMPERATURE, ENDPOINT, INTERMEDIATE_PRODUCT, OPTIONALITY, ALTERNATIVE, REFERENCE/COREFERENCE.
- Not everything is BIO; some objects belong in span attributes / normalized fields / relations / event objects / reference edges (L4183–4188).

### 1.15 Semantic stack (AW1 L4094–4109)
- raw → source adapter/immutable snapshot → ingredient phrase parsing → span/entity recognition → canonical food/process/tool linking → quantity/unit/form/state attributes → instruction events → relations → cross-step coreference → intermediate entities → branch/optional/reserve/split/merge → ordered event/state graph → confidence/OOD routing → replayed structured recipe state.

### 1.16 Program definition (AV L4030–4062)
- Source/Evidence → Canonical Ingredient/Molecule/Process/Quantity Objects → Semantic Recipe State → Process-Conditioned Evidence/Transition → Retrieval + Confidence + Constraints → Decision/Diagnosis/Recovery.
- FlavorTwin = Target → Ingredient/Process Retrieval → Transition/Context Evaluation → Evidence/OOD Gate (L4050–4058).
- L13E is an orthogonal track (L4062).
- **L14 core object** (AZ5 L4680): z_{i,t} = F(z_i, S_t, P_t, Θ_t, H_t).

## 2. Models and baseline ladders (simple → strong → advanced)

### 2.1 DEL-2 sparsity/completion ladder (AI6 L3131–3139)
- D0 RF=1
- D1 global mean
- D2 per-process mean
- D3 hierarchical shrinkage
- D4 nearest compatible evidence
- D5 LightGBM
- D6 TabPFN "only if practical"
- D7 FM / side-information factorization
- plus a biased MF comparator

This matches the SSOT canonical §209.17 D0–D7 (SSOT L18547–18596: D0 persistence, D1 global mean-delta, D2 process-conditioned mean-delta, D3 hierarchical shrinkage, D4 nearest-evidence, D5 GBDT, D6 TabPFN, D7 evidence-aware low-rank/factorization).

### 2.2 L15 ladder as written in AZ6 (L4700–4711) — INCONSISTENT with the SSOT
- AZ6 reads: D0 persistence, D1 process mean, D2 nearest evidence, D3 linear/tree, D4 neural residual, D5 conditioning, D6 multi-output, D7 sparse completion, D8 kinetics, D9 hybrid, D10/11 only if data supports.
- SSOT §209.17 (L18543–18616) reads: D8 classical kinetics, D9 hybrid mechanistic+learned residual, D10 neural multi-output/latent-state, D11 UDE/neural ODE/reaction network.
- AZ6 renumbers D1–D7 and drops hierarchical shrinkage, TabPFN and explicit GBDT. **SSOT wins (A3 conflict rule L59).** Steps 29–34 must use SSOT §209.17 numbering.
- SSOT §215.4 activation rule (L22017–22024): "dataset supervision ⇒ eligible model family"; not every dataset runs every rung.

### 2.3 Required DEL-2 splits and diagnostics (AI6 L3143–3149)
- pair holdout
- ingredient-disjoint
- feasible study/publication-component-disjoint
- random sanity
- grouped bootstrap
- propensity-weighted diagnostic
- empirical interval coverage

Programme additions (AL2 L3496–3501): larger condition-aware tensor; weighted/shift-aware conformal; mechanistic features; cold process split; active acquisition; hybrid kinetic residuals.

### 2.4 RAG/system ladder (AI9 L3289–3296)
- B0 LLM only
- B1 dense RAG
- B2 lexical+dense hybrid
- B3 + structured metadata
- B4 + reconstructed state
- B5 + evidence compatibility / routing / calibrated abstention
- B6 + transition fallback only if G16-TRANS passed
- B7 + decision/VOI only if corresponding gates passed

Comparison with the SSOT §245.12 (L26670–26677):
- SSOT B5 = "state + evidence compatibility/conflict packet"; SSOT B7 = "+ calibrated recommend/ask/abstain decision layer".
- **Plan moves calibrated abstention from B7 into B5, and redefines B7 as decision/VOI.** This is a semantic drift to flag.

Other ladder rules:
- DEL-4 retrieval components (AI6 L3157–3161): BM25; dense CPU embedding baseline; structured exact/filter; RRF; condition-compatible scorer.
- Week-6 rule (L3282): "B5 must earn itself on dev. If not, retain simpler B4/B3 and report the negative result."
- Ablations (L3299–3307): state; structured retrieval; compatibility; conflict handling; abstention; feasibility; quantity; transition fallback.
- Oracle variants (L3310–3312): oracle state / evidence / events.

### 2.5 Recipe semantic parsing ladder (AW3 L4145–4153)
- RSP0 deterministic rules + lexicons
- RSP1 recipe-domain token/entity classifier
- RSP2 entity + attribute extraction + conservative canonicalisation
- RSP3 relation + multi-action event extraction
- RSP4 coreference + intermediate entity tracking
- RSP5 ordered event/state graph + branch semantics
- RSP6 calibrated confidence/OOD routing to a stronger model or review
- RSP7 active learning / PEFT / retrieval / distillation if earned
- RSP8 end-to-end recipe-state reconstruction feeding CulinaryState-RAG

"Every rung is evaluated against the same Gold and source-safe splits" (L4156).

**Reported comparison targets to reproduce** (AW2 L4118–4129): legacy RecipeDB CRF/Stanford NER; 2024 ingredient-phrase spaCy-transformer/Stanford; RecipeDB3 ingredient DeBERTa; RecipeDB3 instruction spaCy; RecipeBERT-KA/RecipeRoBERTa-KA; DeBERTa-v3+CRF; GLiNER2/GLiNER2.5; kNN-NER; RENER; one local instruction model; one pinned frontier LLM as Silver teacher; "Jev" closed-set verifier as a separate experiment.
- These are "reported baselines… not our own verified results until rerun" (L4115).
- The exact names and versions (e.g. GLiNER2.5, RENER, RecipeBERT-KA) are UNVERIFIED here.
- Repo note: per ctx, the NER/linker block was closed in S128 (DeBERTa-base+CRF, BGE linker). Do not reopen.

### 2.6 Representation ladders
- **L12 (AZ2 L4619–4628):** molecule identity → descriptors/fingerprints → ECFP/Tanimoto → ingredient molecule-set representation → abundance/OAV where evidence exists → pretrained molecular models → learned set encoders → process-conditioned extension only after L14.
  - Required: static simple baselines first; chemistry/structure/sensory distinct; no sensory equivalence from structural similarity (L4631–4633).
- **L13 (AZ3 L4639–4649):** binary incidence → mean pooling → IDF/frequency controls → quantity/role → Deep Sets → attention/Set Transformer → interaction models → procedural/state graph → task-conditioned multiview.
  - Confounds (L4652–4657): recipe size, ingredient frequency, cuisine size, source, duplicates, language.
- **L14 (AZ5 L4686–4694):** evidence schema → condition normalization → process-event table → direct/qualitative targets → low-complexity tabular → FiLM/conditioning only if justified → cold ingredient/process/pair splits → calibrated uncertainty.
- **B04-lite (AH9 L2907–2913; AQ2 L3842–3848):** MOL- schema; resolve structures for molecules touched by DEL-1 anchor evidence and FlavorDB; RDKit fingerprints/descriptors; ingredient–molecule joins with presence/concentration provenance; no large learned molecular model.
- **B03-lite (AH8 L2896–2903; AQ1 L3835–3838):** transaction binary-membership invariant; N_s; null-cuisine tests; A2 frequency-control regression tests; frequency/size/null utilities as tested library functions; fingerprint/Tanimoto smoke test; one food-pairing replication.

### 2.7 L13E (AZ4 L4663–4671; AH12 L2947–2951)
- Sequence: historical source audit → rank/frequency + heavy-tail fitting → copy-mutate/Jain-Bagler reproductions → null lattice → recipe identity/novelty calibration → temporal/contact models → SBI only after identifiability.
- Course-bounded chain: rank-frequency/null fit → one Kinouchi/Jain reproduction → one source-safe null comparison.

### 2.8 Decision/FlavorTwin
- **Decision track** (AZ9 L4758–4767): state+goal+constraints+evidence → decision mode → candidate action/hypothesis → feasibility → transition/evidence evaluation → VOI clarification → Pareto comparison → action/diagnosis/recovery/abstention.
- **FlavorTwin V2** (AZ10 L4773–4781): target profile → static candidate baselines → ingredient/process expansion → condition refinement → recipe-role/quantity context → evidence/OOD gate → diverse Pareto candidates. "Do not expand until shared gates pass" (L4771).

## 3. Experiments / hypotheses / RQs

- **AK1 registry seeding** (L3407–3422) requires `registry/experiments.csv` to contain:
  - RQ16-01…30; E16-A…L
  - RQ13E-01…22; E13E-01…18; G13E-01…15
  - L12 T0–T9
  - L13 representation phase experiments/gates
  - L14 MVP + G14-1…12
  - L15 D0–D11 and G15 gates/tracks
  - sparsity M1–M6
  - compiler E0–E14 + subexperiments
  - JEPA J1–J5 (optional)
  - v2/v3 SX IDs
  - RS research-spawn bank
- **Repo:** that CSV does not exist (verified). Whether these IDs are seeded anywhere else (e.g. `registry/ssot15_state_experiment_map.csv`) is partially UNVERIFIED. Brief §11/44 audits should check that file.
- **AK2 course chain** (L3445–3455): schema/provenance → evidence ingestion → sparsity EDA → D0–D7 → semantic/state replay → compatible retrieval → calibration/abstention → B0–B5 ladder → locked test.
- **AK3 foundation chain** (L3459–3468): classical regression → molecule/ingredient registry → process ontology → quantity ontology → Gold semantic seed → 10k Silver → NER/scorer reproduction → representation diagnostics.
- **AW9 oracle-cascade experiment (mandatory)** (L4319–4326):
  - oracle spans → linker → graph; predicted spans → linker → graph
  - oracle links → graph; predicted links → graph
  - oracle events → replay; predicted events → replay
  - Hypothesis: the gap says whether NER is the bottleneck. "If the better NER model improves token F1 but does not improve state graph/retrieval/decision performance, it does not automatically win" (L4330).
- **AB4 state-engine validation** (L2465–2471): run the compiler blind to held-out own measurements and compare predicted direction/value, uncertainty coverage, trust-horizon behaviour and abstention.
- **AH4 conformal:**
  - empirical coverage/width under ingredient/pair/study-disjoint splits;
  - weighted/shift-aware conformal only as an experiment;
  - record failures (L2823–2826).
  - Repo precedent: WORKLOG L117 (S017) shows conformal-90 empirical coverage of 0.72–0.87 on cold splits. That is a negative result to retain.
- **AM4 propensity/MNAR** (L3619–3624): report variables used, calibration, positivity/overlap, sensitivity to the propensity model, and unweighted beside weighted metrics.
- **10k Silver pilot staged experiment** (AP3 L3802–3810): 1k smoke → audit → prompt/schema fix → 5k → audit → 10k → freeze. Outputs listed in AP4 (L3816–3826), including "decision: scale / repair / stop".
- **Benchmark design** (AH5 L2834–2848; AI6 L3164–3167):
  - tiers: min 24 dev + 80 locked = 104; target 80 + 240 = 320; stretch 120 + 320 = 440;
  - 8 task types (MP L1252 "~80 questions × 8 task types");
  - "Every benchmark release must report the achieved tier" (L2850).
- **Demo** (L3321–3322): ≥8 course scenarios, target 12–16.
- **Human review experiment** (AH14 L2969–2973; AI9 L3314–3318): shuffled outputs; double-annotated stratified scientific-claim subset; LLM–human agreement reported; the LLM judge is supplemental.

## 4. Gates, promotion and stop rules (quoted ids/thresholds)

**Plan gates in range:**
- **Week-0 gate** (L3029): "No scraping, paid API or cluster-wide job before approvals."
- **Week-1 gate** (L3053–3056):
  - broken EvidenceRow is rejected by CI;
  - raw source hash pinned;
  - internal IDs work without RecipeDB/FlavorDB access;
  - one end-to-end fixture source → evidence row → query → citation.
- **Week-2 gate** (L3087–3090):
  - 20 Gold design recipes fit schemas without ad-hoc fields;
  - annotation disagreements produce handbook changes;
  - zero invented grams;
  - replay fixtures deterministic.
- **Week-3 gate** (L3121–3124):
  - DEL-2 cards committed;
  - no locked split result inspected;
  - evidence ledger v0 frozen;
  - Silver pilot receives GO/BLOCKED with reasons.
- **Week-4 gate** (L3183–3186):
  - test hash frozen;
  - no test-driven changes after freeze;
  - benchmark curator role recorded;
  - dev/calibration/test separation documented.
- **Week-6 gate** (L3282): "B5 must earn itself on dev. If not, retain simpler B4/B3 and report the negative result."
- **Week-7 gate** (L3325): "No final claim lacking a `CLM-`, experiment ID, artifact hash and CI/gate verdict."
- **DEL-2 promotion rule AM5** (L3628–3632): "Complexity is promoted only if it improves a predeclared primary metric with uncertainty and does not catastrophically harm: cold splits; calibration; interval coverage; interpretable error slices."
  - "catastrophically" is undefined, i.e. no threshold is given.
- **DEL-2 close** (L3191–3195): CIs; model-complexity decision; KEEP/MODIFY/DROP/NEED_DATA; "no 'process helps' claim without CI-supported comparison."
- **B6 gating** (L3295): transition fallback "only if G16-TRANS passed".
  - SSOT G16-TRANS (L27470–27471): "No Level-15 fallback is used for a target/domain until the relevant G15 gates pass."
- **10k Silver gate:**
  - AH10 (L2921): run "only after the SSOT 257P prerequisites are satisfied".
  - AI5 (L3118): "Run the 257P prerequisites. If any fail, do not launch 10k."
  - AP2 (L3798): "Exactly the SSOT 257P checklist."
  - Stop conditions (AH10 L2923–2928): schema unstable; reannotation rate too high; licence/storage unresolved; cost exceeds budget; Gold error profile unacceptable. **None of these has a numeric threshold.**
- **SSOT 257P** (SSOT L42705–42742), quoted. "Do not authorize 60k–100k production annotation until":
  - schema v1 fields/missingness documented;
  - provenance enum enforced in code;
  - raw-source checksum/manifest;
  - "at least 100–500 difficult Gold seed cases exist";
  - unit engine passes property-based tests;
  - vocab proposal/review workflow;
  - quantity lookup returns exact/interval/UNKNOWN without guessing;
  - graph represents intermediate/split/merge/reserve/recombine;
  - QA flags fabricated chemistry/conditions;
  - batch report statistics;
  - "pilot cost and reannotation rate are known";
  - "duplicate grouping runs before split assignment";
  - "Deep-Gold annotators remain independent of Silver predictions";
  - prompt/model/schema versions logged;
  - rollback/reprocess strategy.
  - Final RAG claims block (L42725–42734) and FlavorTwin V2 block (L42736–42742) are also in 257P.
- **SOTA claim gate AW10** (L4334–4343). Eight conjunctive conditions:
  1. exact protocol reproduced;
  2. strongest baselines rerun;
  3. same held-out test;
  4. source/duplicate leakage audited;
  5. uncertainty;
  6. ≥1 external/source-disjoint test;
  7. gain not only from private labels/retrieval leakage;
  8. compute cost reported.
- **Test-locking language AH13** (L2961): "After hash freeze, no training, prompt engineering, threshold setting or architecture decision uses locked-test labels/results. A designated benchmark curator may know the items but does not tune the evaluated component from them."
- **Research stop rule AC** (L2479–2483): sufficient primary evidence; two independent passes find nothing new; source class exhausted; cannot change the gate.
- **Experiment park/drop rule AC** (L2485–2490): simple baseline meets target and complexity yields no meaningful improvement; data below minimum claim regime; repeated seeds show no stable effect; leakage/unfixable confound; disproportionate compute. "New scope needs H8" (L2492). H8 is defined at MP L142: adding/dropping a Level/Block/deliverable, promoting stretch, changing the course contract.
- **DoD AD** (L2502–2520): 17 items. Source/data manifest; schema+validator; EDA; baselines; experiment cards; reproducible runs; metrics+uncertainty; ablations; error analysis; negative controls; gate verdict; artifact hashes; model/data card; claim ledger update; docs; CI/regression tests; reviewer sign-off.
  - State-change claims additionally need tier, source span, matrix/process/condition applicability, measurement method and conflict check (L2523–2527).
  - Warnings additionally need authoritative evidence for safety, severity, mitigation and false/over-warning evaluation (L2530–2533).
- **Compute gate AR2** (L3892–3897): local unit test → 1-node smoke → 10-node shard → inspect → full approved fan-out.
  - Every job must be idempotent, checkpointed, resumable, with hashed inputs, a fixed environment, a resource estimate and a manifest (L3900–3907).
  - **AR3** (L3911–3916): no GPU means `BLOCKED_COMPUTE`; "never substitute a weaker CPU result and call it SOTA".
- **Related SSOT gates referenced but outside the range, quoted for Steps 29–36:**
  - G15-1…12, R, H, I (SSOT L22380–22396). Key items:
    - G15-2 "Canonical D0–D6 are reported on all eligible headline splits before D7+ claims";
    - G15-3 process signal on a process-disjoint split with CI;
    - G15-4 kinetic fit identifiable with profile/bootstrap/posterior uncertainty;
    - G15-6 "Real, study-disjoint calibration";
    - G15-10 synthetic/imputed utility on a REAL-only study-disjoint ratio sweep, with no synthetic in test/calibration;
    - G15-11 rollout trust horizon only where true intermediate states exist;
    - G15-H "Every LLM-extracted row used in held-out test/calibration is human verified against the cited source span/table".
  - G15-RXN / G15-HYB / G15-INV (SSOT L22402–22426).
  - G16-DATA…G16-FT (SSOT L27446–27486).

## 5. Data requirements and named sources (with licence notes)

**General rule** (AX L4355): every resource needs SRC-, SNAP-, a licence/terms field, exact version/date, allowed storage/redistribution, and role. AH15 (L2977–2984) requires API/licence/pricing facts as API-/SNAP- with retrieval timestamps, reverified before execution.

**AX1 recipe/semantic** (L4359–4372, with the "never assume" column):

| Resource | Never assume |
|---|---|
| RecipeDB/2/3 | API/redistribution rights until verified |
| RecipeDB legacy NER | same scorer/splits |
| RecipeNLG | independence from ReciFine copies |
| Recipe1M+ | redistribution of raw text/images |
| ReciFine/ReciFineGold | automatic labels are Gold |
| TASTEset v1/v2 | ontology identical (ctx: licence unverified) |
| JFC-Recipe | English/general equivalence |
| English Recipe Flow Graph Corpus | chemistry truth |
| RISeC | full fit |
| ARA | independent families without audit |
| INDoRI | raw-text rights without licence audit |
| CocktailDB | direct recipe equivalence |

**AW5** additionally lists r-FG (L4210) and "other licence-approved recipe corpora" (L4213). Rule: "Never place copies/derivatives of the same recipe family in both train and test merely because they came from different public datasets" (L4215).

**AX2 ingredient/molecule** (L4376–4385): FlavorDB/FlavorDB2; FoodAtlas; FooDB "or equivalent licensed"; PubChem; USDA FDC (IDs, nutrients, household portions); FAO/INFOODS (densities); FoodOn; LanguaL/FoodEx2 "if permitted". "No database is assumed to provide state-transition chemistry merely because it provides raw composition" (L4387).

**AX3 process/state evidence** (L4391–4404):
1. USDA Retention Factors.
2. Phenol-Explorer retention "if legally/technically obtainable".
3. FoodAtlas.
4. Primary process/kinetics literature: raw vs processed before/after; time series; temperature series; pH/medium; moisture/aw; volatile profiles; texture/colour/physical; measured reaction systems.
5. Curated mechanistic anchor studies.
6. Approved in-house measurements.

Rule: "Every scientific row belongs to the evidence plane, not the recipe-text Gold" (L4406).
Repo (ctx): EVD origins are USDA R6 7,018; Bognár 7,090; Phenol-Explorer 3,870 / 125 papers. **Bognár (BFE-R-02-03) is not named anywhere in AX3**, so the inventory is stale relative to the repo.

**AX4 quantity/metrology** (L4410–4417): UCUM; QUDT; FDC portion weights; INFOODS density DB; JFC-Recipe quantities; validated national composition/portion tables; empirical corpus distributions after verification; Ingredient Parser only as baseline, "with unsafe generic density defaults disabled".

**AX5 allergen** (L4421–4425): FSSAI snapshot for India. Repo: licence_status ASSUMED.

**AX6 historical** (L4429–4443): RELISH or other licence-audited historical corpora; public-domain cookbook archives; historical RecipeDB-compatible sources; ingredient-introduction/trade scholarship. Per-source fields: edition year, inferred interval, date precision, language/translation, lineage, bias ledger. "Historical sources do not enter the physical chemistry evidence plane."

**Volume targets:**
- **DEL-1** (AH7 L2872–2888; AL1 L3478–3484): course min ≥1,000 public DB rows + ≥40 human-verified literature rows; course research target 5k–10k rows + 100–150 hand-verified; long-term ≥100k tiered rows, "never means 100k invented completions".
  - "Do not measure success by row count alone. Always report independent sources, targets, matrices, processes, condition completeness and tiers" (L3484).
  - Repo (WORKLOG L199, S029): 10,888 DB rows, human-verified 0/40 at that time. Current verified count UNVERIFIED in this note.
- **Anchor matrix** (AI5 L3097–3100), 12 families: allium, leafy/green vegetable, tuber, grain/starch, legume, fruit, dairy/emulsion, egg/protein, red meat, poultry, oil/frying medium, fermented food. "avoid six-anchor-only bias" (L3096).
- **Gold** (AH6 L2858–2864; AW6 L4219–4231):
  - design pilot 20 hard recipes;
  - course Deep Gold ≥40 independently double-annotated A4 recipes;
  - Gold-Light 100–160;
  - sessions 80–100 (minimum 30);
  - long term Deep Gold 750–1,000, Gold-Light 5k, Silver 60k–100k after gates.
  - Hard strata are listed at L4233–4249.
  - **Repo:** per DECISIONS.md (D-016/D-017, line ~135) there are 40 GOLD_PENDING_INDEPENDENT_IAA, "all AI-drafted + human-reviewed, NOT independent"; no DEEP_GOLD / GOLD_LIGHT. The AI4 "two annotators, no pre-fill" (L3068) contract is therefore NOT met.
- **Silver:** 10k pilot → 25k → 60k → 100k (AG2 L2715; BA L4825–4830).
- **Bench data (AB2 L2427–2436):** temperature trajectory with calibrated probe, mass loss, pH (meter/strips with uncertainty), phone/colorimeter L*a*b*, texture/force proxy, time, geometry/thickness, water loss. Exclusions: "No hazardous chemistry, microbiological challenge work, pressurized custom rigs" (L2438).
- **Access email (AS L3922–3947):** RecipeDB/RecipeDB3 + annotations, FlavorDB/FlavorDB2, cross-resource ID mappings, API auth/rate limits/derived-artifact storage terms, plus non-blocking Foodoscope endpoints. Repo: D-015 records CoSyLab use as "permitted by Prof. Bagler (reported by Kush)", i.e. licence ASSUMED/DERIVED_ONLY.

## 6. Dependencies on other levels/steps

- **Lanes (AG2 L2691–2725):**
  - Lane A: DEL-1→DEL-5.
  - Lane B: B03-lite, B04-lite, B05 process ontology, B06 evidence expansion, B07 10k Silver, B08 NER reproduction, B09 vocab, B10 CQPO, B11 event/state graph, B15 L13E.
  - Lane C: 25k→100k Silver; 10k+ ingredient concepts; 100k evidence; molecule/sensory master; advanced L12–L15 encoders; transition/kinetic hybrids; NER SOTA; full L13E; FlavorTwin V2; L17; publication.
- **Hard dependencies stated:**
  - B6 needs G16-TRANS, which needs G15 (L3295; SSOT L27471).
  - B7 needs decision/VOI gates (L3296).
  - 10k Silver needs 257P (L2921, L3118).
  - L12 process-conditioned extension needs L14 (L4627).
  - FlavorTwin needs shared gates (L4771; 257P FT block).
  - Inverse design needs model validity (L4720; G15-INV).
  - SBI (L13E) needs identifiability (L4670).
  - L17 needs a stable text/state/evidence core (L4785).
  - Week-1 gate needs internal IDs to work without external APIs (L3055).
- **Non-blocking stated:** B15 never delays DEL-1…5 (L3866; AH12 L2943). B08 off the course critical path (L2930). B03/B04 artifacts "allowed to finish… without becoming course headline claims" (L3470).
- **Week ordering:**
  - W0 approvals;
  - W1 schemas/CI/USDA ingest/process ontology/event core;
  - W2 DEL-1 v0 + 20 Gold design + quantity v0;
  - W3 DEL-2 preregistration (cell, inclusion, study graph, propensity features frozen before outcome);
  - W4 D0–D7 runs + Deep Gold + retrieval baseline + benchmark freeze;
  - W5 close DEL-2/3 + DEL-4 compatibility + 10k Silver;
  - W6 DEL-4 locked eval + decision layer;
  - W7 ladder + human review;
  - W8 buffer (AI1 L2993–3001).
  - Implied order: preregistration (W3) before any D-model runs (W4); benchmark freeze (W4) before locked evaluation (W6–W7).
- **Ownership (AJ L3348–3398):**
  - Kush K1–K17 (CI, USDA, schemas/conditions, PE ADR, evidence ingestion, canonical names, CQPO, literature evidence, DEL-1 freeze, retrieval B1–B3, compatibility/calibration, DEL-4 locked eval, DEL-5 wiring, locked API runs, B03-lite, B04-lite, Silver validators).
  - Parv P1–P15 (registries, process ontology, event core, Gold guideline, DEL-2 splits/cards/runs/gates, sessions/DEL-3 eval, decision/diagnosis/recovery, UI, vocab audit, Silver audit, B08, B15).
  - Joint J1–J8.

## 7. Risks / failure modes (as stated or implied in range)

- **Endless research / scope expansion:** AC (L2477, L2492).
- **Progress theatre:** AT3 (L3984–3992) excludes agents spawned, pages scraped, commits, parameters, Silver rows and pretty demos.
- **Fabricated study lineage** to satisfy a schema (AH1 L2784).
- **External API dependence blocking the ontology** (AH2 L2809).
- **Allergen safety from a non-authority** (AH3).
- **Nominal conformal validity claimed under shift** (AH4 L2824).
- **Count inflation:** Gold, benchmark and evidence rows (AH5 L2842, AH6 L2866, AH7 L2890).
- **Test leakage / misleading "unseen test" claims** (AH13).
- **LLM judge as sole ground truth** (AH14 L2973).
- **Stale snapshot facts** (AH15).
- **Giant connected component** destroying study-disjoint testing (AM3 L3610). Repo: USDA single source makes study-disjoint impossible (WORKLOG L117).
- **MNAR propensity treated as truth** (AM4 L3617).
- **Collapsing rich cell to (food, process, target)** gives over-general claims (AM1 L3578).
- **RF clipping / incompatible-basis merges** (AM2). Repo: Phenol-Explorer RF up to 102 dominated MAE (WORKLOG L199), so metric/target choice is a risk (log-RF adopted, S040).
- **Invented grams** (AN2, BB6).
- **Hidden steps treated as observed** (AN4).
- **Uninterpretable compatibility scalar** (AO2 L3730).
- **Uninspected 10k batch** (AP3 L3812).
- **Hammering one website/API** with the cluster (AR1 L3888).
- **Weaker CPU result labelled SOTA** (AR3 L3916).
- **Cross-dataset recipe-family leakage** (AW5 L4215; AW7 L4264–4272: augmentation, translations, LLM Silver, retrieval exemplars, kNN datastore and few-shot demos must obey splits).
- **NER token-F1 gains not translating downstream** (AW9 L4330).
- **SOTA claims from abstracts** (AW2 L4132).
- **Historical sources contaminating the chemistry plane** (AX6 L4443).
- **Structural similarity mistaken for sensory equivalence** (AZ2 L4633; BB16).
- **Historical simulators treated as causal truth** (AZ4 L4673).
- **Lab safety** (AB2 L2438); own measurements are not a substitute for broad evidence (AB1 L2421).
- **Implied, not stated:** the human-time bottleneck. The whole of W2–W7 depends on two annotators producing ≥40 independent Deep Gold plus a 104–320-item benchmark. The repo shows Parv blind passes still pending (WORKLOG L719), so this is the dominant risk.

## 8. MAPPING TO THE 36-STEP SPINE (reconstruction; the 36-step cards are missing)

- **01 Freeze project authority.**
  - Requires a single authority order. The plan has two that conflict: A3 (L50–56) vs AG4 (L2745–2751); see §9.
  - Must record that v2.0 is superseded by v4.0 (diff in §0), and that the v3_0 file referenced at L4004 is missing.
  - Inputs: AG3 status enum (L2731–2739) for every SSOT item.
  - Outputs: scope registry (L3014, L3022) and DEC- records (L4574).
  - Gate: H1–H8 human gates (MP L135–142).
- **02 Audit implementation state.**
  - Use the AD 17-item DoD (L2502–2520) as the per-block audit rubric.
  - Status labels per AG3, plus BLOCKED_COMPUTE (L3915).
  - AK1 registry fields (L3424–3439).
  - Findings so far:
    - `registry/experiments.csv`, `gates.csv`, `research_spawns.csv`, `scope_registry.csv` and `datasets.csv` are absent;
    - 18 AY object types have a schema but no data;
    - SAMPLE/DEC/PROMPT/ROLE/HIST have no schema.
  - Metric: DoD completion per block. AT3 bans count-based progress claims.
- **03 Freeze state semantics.**
  - Must freeze the AN1 three identities (L3640–3646) and the AN3 `trajectory` enum PLANNED/OBSERVED_SESSION/PREDICTED (L3671–3675), with the observation-override + audit-log rule (L3677).
  - Also: AN4 OMITTED_STEP_CANDIDATE; AY5 append-only STATE/EVT/REF/GRAPH (L4541–4548); the AI4 relation set (L3069–3072); the L14 object z_{i,t}=F(z_i,S_t,P_t,Θ_t,H_t) (L4680); and the full cell C=(matrix,S_in,process,Θ,target,measurement basis) (L3575).
  - Output: STATE/EVT schema freeze. These exist in `ledgers/schemas/` and `reports/h_state/state_representation_contract_v1.md`, which should be checked against AN.
- **04 Freeze evidence/provenance/similarity contracts.**
  - Evidence and provenance: AH1 origin_type enum and study_ids rule (L2772–2785); AH2 internal-ID-first (L2795–2807); AH3/AX5 allergen authority; AO3 CLM fields (L3736–3745); AY1 SRC/SNAP/API/STUDY/MEAS.
  - Similarity: AZ2 "chemistry/structure/sensory kept distinct" (L4632) and BB16 (L4870). There is no field-level similarity contract in range.
  - Gate: Week-1 gate items (L3053–3056).
- **05 Normalize EVD.**
  - AM2 (L3584–3593): keep RF>1; before/after basis, yield factor, wet/dry, SD/range, n, method; no merge if incompatible.
  - AI4 (L3061–3064): preserve SD/range/n/methods; DATABASE_AGGREGATE vs primary.
  - Output feeds the DEL-2 tensor.
  - Repo: ES-1.1 export S129 already has tier/verification/design/provenance separated (WORKLOG L887). Check that `origin_type` gains the REVIEW_AGGREGATE/AUTHORITY_STANDARD/PROJECT_MEASUREMENT values when relevant.
- **06 Freeze source acquisition manifest.**
  - AX's every-resource requirement (L4355: SRC, SNAP, licence/terms, version/date, storage/redistribution, role).
  - Use the AX1–AX6 lists as candidate rows, with each "never assume" note recorded.
  - AH15: API-/SNAP- timestamped and reverified.
  - Week-0 gate (L3029).
  - Email per AS (H1).
  - Repo: `registry/data_source_acquisition_manifest.csv` and the S130 64-source census exist. Cross-check them against AX (Bognár missing from AX; FoodAtlas, INFOODS, QUDT, UCUM and JFC-Recipe to verify).
- **07 Condition & measurement normalization.**
  - Must cover the AY4 COND fields (L4523–4536: time, temperature, pH, moisture, aw, pressure, oxygen, salt/sugar/fat, medium, geometry, particle size, agitation, biological/fermentation) and the AO2 compatibility axes (L3716–3727).
  - MEAS- method/platform/protocol (L4487).
  - Condition-completeness masks for the course cell (L3570).
  - Repo: ctx says the 07H human gate is NOT_COUNTED_PROVENANCE_INVALID, so this step is not cleanly closed.
- **08 Scientific source lineage.**
  - AM3 graph row→source→publication IDs→study families with connected-component split feasibility (L3599–3613).
  - AH1 study_ids/source_family_id.
  - AI5: "build source/study-family graph; assess whether publication connected components make study-disjoint split feasible" (L3106–3107).
  - G15-6 needs study-disjoint calibration (SSOT L22387).
  - Output: STUDY- and lineage edges plus a component report (giant-component statistic).
  - Missing in the plan: DOCUMENT/EXPERIMENT/SAMPLE/AGGREGATE levels (§1.12).
- **09 Evidence extraction & verification machinery.**
  - G15-H human verification of every LLM-extracted test/calibration row (SSOT L22395).
  - AD state-change claim extras: tier, source span, applicability, measurement method, conflict check (L2523–2527).
  - AH14 human-auditable claim support.
  - AW7: LLM Silver labels obey split boundaries.
  - Output: verification queue (`registry/human_verification_queue.csv` exists).
- **10 20-row mechanism pilot.**
  - Use the AI5 12-family anchor matrix (L3097–3100) so the pilot does not lock in a six-anchor bias.
  - Rows must satisfy the AD state-change claim fields.
  - No numeric pilot gate is in range.
- **11 Wave-1 verified mechanism evidence.**
  - Targets: ≥40 human-verified literature rows (course minimum, L2874); 100–150 hand-verified (target, L2881).
- **12 Structured database evidence.**
  - AX3 items 1–3 (USDA RF, Phenol-Explorer "if legally/technically obtainable", FoodAtlas); AX2 FDC/FooDB.
  - Target 5k–10k validated rows (L2880).
  - Typed DATABASE_AGGREGATE (L2787).
- **13 Large literature discovery corpus.**
  - AX3 item 4 (L4394–4402) lists the evidence classes to search: time/temperature series, pH/medium, moisture/aw, volatiles, texture/colour, reaction systems.
  - AR1 permits CPU-parallel PDF/table extraction only after licence approval (L3876).
- **14 Coverage-driven evidence growth.**
  - AL1 "coverage/VOI driven" programme (L3482), with reporting of independent sources/targets/matrices/processes/condition completeness/tiers (L3484).
  - Growth path 10k+ → 25k+ → 100k "if evidence sources genuinely support it" (L4833–4835).
- **15 Freeze DATA-EVIDENCE v1.**
  - AX7 release with manifest, schema version, source snapshots, licence matrix, duplicate groups, split registry, data card, hashes (L4464–4472).
  - Week-3 gate "evidence ledger v0 frozen" (L3123).
  - Must include the AM3 component-based SPLIT- registry.
- **16 Instruction semantic schema.**
  - AW4 label ontology (L4160–4181) and the non-BIO placement rule (L4183–4188).
  - AI4 relations; AY5 INST-; AW1 stack (L4094–4109); AN2 quantity grammar.
  - Gate: "20 Gold design recipes fit schemas without ad-hoc fields" (L3087).
- **17 Instruction-level extraction.**
  - Ladder RSP0–RSP8 (L4145–4153); comparison targets AW2.
  - Splits AW7 (L4256–4261): random sanity (not headline), source-disjoint, template/duplicate-family-disjoint, ingredient-tail/unseen-alias, process-tail, locale/language.
  - Metrics AW8 (L4276–4313): span, attribute, linking, event/graph and system layers.
  - Mandatory oracle cascade AW9; SOTA gate AW10.
  - Respect the S128 NER/linker freeze; RSP3–RSP6 are the open part.
- **18 Event-sourcing engine.**
  - Append-only transitions (L4548); replay determinism tests (L3073, L3090).
  - ALLOC- split/reserve/recombine (L4509); symbolic quantities (AN2).
  - Trajectory/override semantics (AN3); OMITTED_STEP_CANDIDATE (AN4).
  - Metrics (AI7 L3199–3204): state-field accuracy, replay consistency, merge/split edge F1, allocation accuracy, unresolved-rate, oracle-vs-built gap.
- **19 Gold state-trajectory pilot.**
  - AH6 (L2858–2864); AI4 "two annotators, no pre-fill" (L3068); "agreement before adjudication" (AI6 L3153).
  - Hard strata list (AW6 L4233–4249); disagreements → handbook changes (L3088).
  - Course minimum: 40 Deep Gold + 30 sessions.
  - Repo conflict: D-016 means the Kush set is AI-assisted, so it is NOT independent.
- **20 Scale procedural semantic corpus.**
  - AP 10k pilot: 1k→5k→10k staged, with outputs per AP4 (L3816–3826).
  - SSOT 257P prerequisites (L42707–42723), including "duplicate grouping runs before split assignment" and "Deep-Gold annotators remain independent of Silver".
  - AH10 stop reasons; then 25k→60k→100k (L4825–4830).
  - Must use the Step-07I family IDs for duplicate grouping.
- **21 Effect/mechanism ontology.**
  - Only RXN- "may be partial. Unknown networks remain unknown" (L4559) and G15-RXN (SSOT L22404–22410).
  - The plan in range has NO mechanism-ontology content and no MECH- ID. This is a gap.
- **22 Event→effect signatures.**
  - AZ5 execution: process-event table → direct/qualitative targets (L4688–4689).
  - The DEL-4 compatibility axes link events to evidence.
  - No signature schema in range (gap).
- **23 Mechanism applicability engine.**
  - AO2 compatibility vector and "UNKNOWN is neutral, not mismatch" (L3219).
  - The cascade's QUALITATIVE level (L3226).
  - No applicability-condition schema (activation ranges, inhibitors) in range (gap).
- **24 Formula/model registry.**
  - Not covered in range. MODEL- is an ML-model registry (L4567). AZ6 mentions "kinetic identifiability" (L4717). G15-4 needs profile/bootstrap/posterior uncertainty.
  - A new registry object is needed. Following the anti-scope-creep rule, it belongs inside Step 24.
- **25 Parameter-compatibility retrieval.**
  - The AO2 axes (time/temp/pH/aw/medium/geometry/basis) and the MODEL_ESTIMATED/INTERPOLATED cascade levels apply. Packet field "CONDITION DIFFERENCES" (L3702).
  - No parameter-registry fields in range.
- **26 Implement one focused deterministic simulator.**
  - Nothing explicit in range except AZ6 "reaction network only for data-supported systems" (L4719) and BB4/BB5.
  - AR1 lists "kinetic parameter fitting" as a CPU job (L3882).
- **27 Validate simulator on real held-out evidence.**
  - AB4 is the only validation protocol in range: blind prediction vs own held-out measurements; direction/value, uncertainty coverage, trust horizon, abstention (L2465–2471). AB3 sample contract fields.
  - G15-4/G15-5/G15-HYB apply (SSOT).
- **28 Generate controlled E7 synthetic prior.**
  - BB5 "Imputed/synthetic targets never enter final real test/calibration" (L4859); AZ6 "real-only final test/calibration" (L4716).
  - Gate: G15-10 ratio sweep (SSOT L22391).
- **29 TRANSITION_BOOTSTRAP_V0.**
  - DEL-2 D0–D4 floor (L3131–3135) with AM1 cell projection and AM4 MNAR diagnostics.
  - Preregistration before any test metric (L3103–3110).
  - G15-1 data audit.
  - Repo has `reports/h_state/transition_bootstrap_v0_contract.md` (to be read by another agent).
- **30 Strong tabular/sparsity bake-off.**
  - D5 LightGBM, D6 TabPFN "only if practical", D7 FM, biased MF (L3136–3139).
  - Splits L3143–3149.
  - Promotion AM5. Gates: G15-2 (D0–D6 before D7+), G15-9 completion.
  - Repo precedent (WORKLOG L117, L262): D5 ≈ D0 on cold-food splits. A negative result to carry forward.
- **31 Physics/condition features.**
  - AL2 "mechanistic features" (L3499); AZ5 "FiLM/conditioning only if justified" (L4691).
  - G15-3 process signal on a process-disjoint split with CI.
- **32 Focused kinetics.**
  - D8 (SSOT §209.17); AL2 "hybrid kinetic residuals" (L3501); AZ6 kinetic identifiability (L4717).
  - Gates: G15-4, G15-5. CPU fitting is permitted (AR1 L3882).
- **33 Mechanistic vs ML vs hybrid.**
  - D9; G15-HYB (SSOT L22414); AC park rule (L2486).
- **34 Short rollout.**
  - AZ6 "rollout trust horizon" (L4718); AB4 trust-horizon behaviour.
  - G15-11 requires true intermediate states (D-C/D-D datasets).
- **35 Representation ladder.**
  - AZ2 L12 and AZ3 L13 sequences + confounds; AH8/AQ1 B03-lite regression tests (N_s, A2 frequency controls, null-cuisine); AH9/AQ2 B04-lite (MOL-/InChIKey, canonical SMILES, RDKit fingerprints, IMAP with presence/concentration provenance).
  - L13E outputs feed "recipe identity/novelty calibration" (AZ4 L4668).
  - Gate: no sensory-equivalence claim (L4633). The plan has no per-similarity-type registry fields (gap vs brief §24).
- **36 Evidence compiler → selective RAG → FlavorTwin.**
  - Packet: AO1 (L3698–3708). Compatibility: AO2. Claims: AO3. Decision modes: AO4 + ASK rule.
  - Metrics: AO5 (L3766–3775) and AI8 (L3247–3254).
  - Retrieval components (L3157–3161). Ladder B0–B7 (L3289–3296) with B6/B7 gated. Ablations/oracles (L3299–3312).
  - Benchmark tiers 104/320/440 (AH5); benchmark registry fields (L3170–3180); test lock (AH13).
  - Human claim review (AH14); feasibility via the allergen authority (L3270).
  - Diagnosis proposer/verifier and recovery-evidence separation (L3276, L3279).
  - Demo ≥8 / 12–16 scenarios. Gates: 257P RAG and FT blocks; G16-*.
  - FlavorTwin: AZ10; AV formula.
  - Repo: a DEL-4/DEL-5 implementation exists (WORKLOG S054–S076: relevance gate, feasibility, decision policy, ask tool, Pareto selector; ladder smoke with a negative result S065–S066). It must be re-evaluated under these gates and its B-ladder semantics.
- **L13E (no spine step).** AH12, AQ4, AX6, AY8, AZ4 place it as a parallel track that must not block. Brief §25 asks where it belongs. The plan text supports a parallel lane attached to Step 35 (identity/novelty calibration) and Step 06 (historical source manifest), not a spine step.

## 9. Contradictions, stale items, underspecified parts, open questions

**Contradictions**
1. **Two authority orders inside v4.0.**
   - A3 (L50–56): 1 SSOT; 2 course proposal; 3 Recipe_Compiler_FINAL_MERGED_PLAN v1.2; 4 this master prompt; 5 human chat, which "can override 2–4".
   - AG4 (L2745–2751): 1 SSOT; 2 course proposal; 3 adjudicated schema/annotation contracts; 4 detailed compiler/R&D plan; 5 this master prompt; 6 experiment results; 7 live human decisions.
   - Human decisions move from overriding 2–4 to last place. A new rank appears (adjudicated contracts). The compiler plan changes name (FINAL_MERGED_PLAN v1.2 vs "Detailed compiler/R&D plan", the latter present as `CulinaryState_Detailed_RnD_Execution_Plan_v2.md`, written against SSOT v14 numbering per ctx).
   - Both differ from the brief §2 order, which has no course-proposal rank and adds 36-step contracts/freeze manifests and "empirical results override old expectations".
   - Step 01 must resolve this.
2. **L15 D-ladder in AZ6 (L4700–4711) contradicts the SSOT §209.17 (L18543–18616)** and the plan's own AI6 (L3131–3139); see §2.2.
3. **B-ladder semantics differ from the SSOT §245.12** (L26670–26677): calibrated abstention is moved into B5, and B7 becomes "decision/VOI".
4. **257P scope.**
   - The SSOT 257P governs "60k–100k production annotation" (SSOT L42707).
   - Plan AH10/AI5/AP2 (L2921, L3118, L3798) apply it before **10k**.
   - Plan L386 (part 1) says "§257P checklist fully ticked before scaling past 10k".
   - Internally inconsistent. Applying 257P to the 10k pilot also requires "100–500 difficult Gold seed cases" before the pilot that is supposed to measure Silver-vs-Gold error.
5. **Evidence cascade lists differ.**
   - AI7 (L3223–3228): DIRECT / INTERPOLATED / MODEL_ESTIMATED / QUALITATIVE / CONFLICT / UNSUPPORTED-ABSTAIN.
   - AZ8 (L4751): DIRECT / INTERPOLATED / MODEL / QUALITATIVE / ABSTAIN, with no CONFLICT.
   - Brief §28: DIRECT → INTERPOLATE → MODEL → QUALITATIVE → ASK → ABSTAIN, with ASK added.
   - CONFLICT is a status orthogonal to support level and should not be a rung. Step 36 needs one canonical enum.
6. **Compatibility axes differ:** AI7 (8 axes, L3208–3217) vs AO2 (12 axes, L3716–3727). AI7 has "ingredient" and "prior state" plus "conditions" bundled; AO2 has "food/matrix", "state", and unbundled time/temperature/pH/aw/medium/geometry.
7. **Packet fields differ:** AO1 (11 fields) vs brief §27 (15 fields). The brief adds QUERY, HISTORY, DIRECT FACTS vs DIRECT EXPERIMENTAL EVIDENCE, and MECHANISTIC BACKGROUND. AO1 has CONDITION DIFFERENCES, which the brief lacks. Merge both.
8. **Status enum:** AG3 (7 values) lacks BLOCKED_COMPUTE, which AR3 uses (L3915).
9. **Gold independence:** AI4 "two annotators, no pre-fill" (L3068) and 257P "Deep-Gold annotators remain independent" vs repo D-016/D-017 (AI-drafted, human-reviewed). The plan's agreement/IAA gates cannot currently be met.
10. **AU (L4001–4004) instructs loading the v3_0 file**, which is not in the repo. v4.0 is the file actually present. The command text is stale relative to v4.0 naming.

**Stale items**
- The whole 8-week calendar (AI L2993–3338; BA). The repo has moved to a 36-step spine. STATUS dates W1–W6 to 25–26 Nov (WORKLOG L33). DEL-1…5 week assignments do not match the step order (e.g. DEL-5 decision layer already built in S054–S076 before Step 08 evidence lineage).
- AX3 lacks Bognár, which is now ~7,090 EVD rows.
- AS email: D-015 suggests access was granted verbally. It still needs a SNAP- of the terms.
- AR1 "100 CPU nodes" does not match the compute reality in ctx (Mac CPU, a 128-core shared Linux server, A100 over a slow VPN). Existence of a 100-node cluster is UNVERIFIED.
- AR3 "GPU absence" contradicts the ctx (an RTX-class GPU and an A100 exist; NER ran on GPU).
- AW2 comparison list predates the S128 NER freeze.

**Underspecified**
- No numeric thresholds for:
  - AM5 "catastrophically harm";
  - AH10 "reannotation rate too high" / "Gold error profile unacceptable";
  - G16 "declared thresholds";
  - Week-6 "earn itself";
  - IAA (no kappa/F1 target in range; ctx mentions kappa ≥0.8 for the condition audit only).
- The 8 benchmark task types are referenced (L1252, L2835) but not enumerated in range (D-008 in DECISIONS.md is the probable source; UNVERIFIED here).
- "Substantial double-annotated stratified subset" (L2971) has no size.
- Mechanism ontology, formula/model registry, parameter registry, simulator V&V and synthetic-prior generation are essentially absent from Parts AB–BB. Only AB4 and the BB principles touch them. Steps 21–28 must be built from the SSOT (L14/L15 parts), not this plan.
- Similarity-type separation (brief §24) has no registry design. Only `registry/ssot15_similarity_registry.csv` exists in the repo, contents UNVERIFIED by me.
- SIMULATION MEMORY plane (brief §13): no SIM- object, no DATA-SIM release.
- Evidence hierarchy (brief §18): no DOCUMENT/EXPERIMENT/external SAMPLE/AGGREGATE/DERIVED objects.

**Open questions needing external research**
- Q1: Availability and licence for FoodAtlas, INFOODS density DB, QUDT/UCUM, FoodEx2/LanguaL access terms, JFC-Recipe, ReciFine, English Recipe Flow Graph Corpus, RISeC, ARA, INDoRI, RELISH, TASTEset (licence UNVERIFIED per ctx). Note: research must not send project data.
- Q2: Status and reproducibility of GLiNER2/2.5, RENER and RecipeBERT-KA as reported baselines (verify publication status and dates).
- Q3: Shift-aware/weighted conformal for grouped/study-disjoint splits (e.g. weighted conformal, group-conditional / Mondrian conformal) to inform AH4.
- Q4: IAA standards for recipe event/flow-graph annotation, to set the missing Gold thresholds.
- Q5: Sample size for a selective-prediction/RAG benchmark: is 80 locked items per tier enough for AURC/ECE CIs at 8 task types?
- Q6: Evidence/provenance models (PROV-O, ISA-Tab, the FoodOn/OBI measurement model) for the missing DOCUMENT→EXPERIMENT→SAMPLE levels.

## 10. LOOK-AHEAD — fields earlier steps must capture for this material to be usable later

**Step 03 (state semantics)**
- `concept_id` / `entity_id` / `state_version_id` as three separate keys (AN1).
- `trajectory ∈ {PLANNED, OBSERVED_SESSION, PREDICTED}` per field, with an `observed_at`/session id and a pointer to the superseded prediction (AN3 L3677).
- `omitted_step_candidate` with rule/precedent/evidence id and accept/reject status (AN4).
- Prior-state reference `S_in` on every transition (cell L3575).
- H_t history pointer (AZ5 L4680).

**Step 04 (contracts)**
- `origin_type` with all 5 values, including PROJECT_MEASUREMENT for AB bench rows and AUTHORITY_STANDARD; `source_family_id` mandatory; `study_id_status`.
- `support_class` vocabulary matching the final cascade (one enum; fix the conflict noted in §9 item 5).
- CLM- fields (AO3).
- A `similarity_type` enum separating structural/chemical/sensory/... (AZ2, BB16).
- `UNRESOLVED_EXTERNAL` crosswalk status (AH2).
- `licence_status` on every derived object so DATA-* release licence matrices can be computed (AX7).

**Step 05 (EVD normalize)**
- RF raw (unclipped), before_basis, after_basis, yield_factor, wet/dry, SD/range, n, method_id (AM2).
- `censored` + censoring type (exists).
- A condition-completeness mask per row (L3570). Needed for the DEL-2 course projection and Step 29.

**Step 06 (manifest)**
- Per source: SRC-, SNAP- (hash, retrieval timestamp), API- (endpoint/version/auth/rate-limit/terms), licence/terms, allowed storage/redistribution, role, plus the "never assume" note from AX1 (AH15, AX).
- For historical sources: edition year, date precision, language/translation, lineage, bias ledger (AX6), so L13E is not blocked later.

**Step 07 (conditions/measurement)**
- All AY4 COND variables, even if mostly UNKNOWN: time, temperature (with location: core/surface/medium; repo has `measurement_location_registry_v1.csv`), pH, moisture, aw, pressure, oxygen, salt/sugar/fat, medium, geometry/thickness, particle size, agitation, fermentation variables.
- Measurement platform/protocol (MEAS-).
- Steps 23/25 compatibility (AO2) and Steps 31–32 kinetics need these as explicit fields, not free text. They also need numeric series structure (time-series id, time-point index) so D-C/D-D trajectory datasets (G15-4, G15-11) can be recognized.

**Step 08 (lineage)**
- publication_id (DOI/PMID), study_family_id, source/database id, compilation-from-publication edges (for DATABASE_AGGREGATE rows citing primary studies), and lab/author group if available, all for the AM3 connected-component splits.
- A component-size report is needed to pre-decide whether study-disjoint (G15-6) is feasible.
- Add experiment/sample-level ids (lot, cultivar, replicate) so independence groups are not just publications.

**Step 09 (verification)**
- Source span/table locator, extractor model/prompt version (PROMPT-), human verifier id + timestamp (G15-H), and a conflict-check flag (AD L2527).
- A flag marking whether a row is eligible for test/calibration (human-verified only).

**Steps 10–14 (acquisition)**
- Coverage keys for reporting per AL1 (L3484): independent source count, target, matrix, process, condition completeness, tier. Track them per the 12-family anchor matrix (L3097–3100).
- Capture time/temperature series rather than endpoints wherever the paper has them (needed for Steps 32/34).
- Record whether intermediate states were measured (G15-11).
- Capture volatiles/texture/colour targets with SVAR- ids (AX3 item 4).
- Capture ingredient–molecule concentration and basis for IMAP (AH9), needed by Step 35 abundance/OAV (AZ2 L4624).

**Step 15 (freeze)**
- The release must ship duplicate groups, the split registry (study-component, pair-holdout, ingredient-disjoint, process-disjoint, condition-OOD), licence matrix, hashes and data card (AX7 L4464–4472), plus the condition-completeness distribution.

**Steps 16–20 (procedure/state)**
- AW4 labels, including ENDPOINT ("until …"), MEDIUM, INTERMEDIATE_PRODUCT, OPTIONALITY/ALTERNATIVE and REFERENCE edges.
- QNT- symbolic quantity with POR- provenance; ALLOC- for reserve/split (AN2, AY3).
- `tool` and `heat_transfer_mode` (repo registry exists) for feasibility (AI8 L3268).
- Per-recipe `source_id`, Step-07I `family_id`/`dish_candidate_id`, locale/language and template id. Needed for the AW7 splits and "duplicate grouping before split assignment" (257P).
- Annotator provenance class (independent / AI-assisted, per D-016) so Deep Gold independence can be audited.
- Model/prompt/schema version per Silver record (257P).
- Explicit COND surface mentions (time/temperature/doneness endpoint) linked to the Step-07 COND schema. Step 22 event→effect signatures and Step 36 compatibility need the instruction-level Θ, not only the process label (BB8 L4862).

**For Step 36 (backward propagation)**
- Benchmark items need: task type, difficulty, source family, ingredient/process family, evidence regime, answer kind, must-abstain, gold evidence ids, constraints (L3170–3180), and curator id (L3185).
- Evidence rows must carry the IDs these refer to. Allergen links (ALLERGEN→ING) must exist and be human-ticked before hard constraints are used.

**For L13E (parallel)**
- AY8 HIST fields: edition date, recipe interval, date basis/confidence, region, cuisine, language, translation, genre, lineage/duplicate family, contact metadata, bias fields.
- Ideally attach these at Step 06/07H-R recipe-base time so that identity families (07I) can be reused for novelty calibration.
