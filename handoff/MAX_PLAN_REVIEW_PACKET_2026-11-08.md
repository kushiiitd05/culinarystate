# CulinaryState: review packet for an external plan review (2026-11-08)

Written by the coding agent (S175) for Kush to hand to a reviewer model ("Max plan") for critique and consensus.
Sources: SSOT v15.0 (`docs/SSOT/computational_gastronomy_master_ssot_v15_0.md`), v16 change set (draft, not
applied), 36-step plan v2 (`docs/plan/CulinaryState_36_Step_Execution_Plan_v2.md`), `DECISIONS.md` (D-001…D-077),
`handoff/FINISH_PLAN_2026-11-07.md`, `handoff/PROJECT_FLOW_VERDICT_2026-11-08.md`, the proposal brief, and the run
log `registry/compute_runs_v1.csv`. Every number below is from a committed report or ledger; anything that is a
plan, a proposal or an estimate says so.

---

## 0. Prompt to give the reviewer (copy from here to the end of the file)

> You are reviewing the research and engineering plan of **CulinaryState**, a course mini-project (IIIT Delhi,
> group 17, presentation 25–26 Nov 2026) that is also meant to grow into a publishable system. Two students
> (Kush, Parv) own all human gates; a coding agent does the engineering. Read sections 1–9 below. Then:
>
> 1. **Answer every numbered doubt in section 8** (Q1–Q40). For each: give a recommendation, the reason, the
>    risk if we ignore it, and what evidence or experiment would settle it. Say "agree with the agent's lean" or
>    "disagree" explicitly. If a question is ill-posed, say how to re-pose it.
> 2. **Find what is missing** (section 9 lists what we already suspect). Look especially for: scientific validity
>    holes, circularity or leakage between layers, places where a default or an AI guess could leak into a claim,
>    missing physics or chemistry that a food scientist would expect, evaluation designs that cannot show what
>    they claim, and timeline items that cannot finish by 25 Nov.
> 3. **Rank the remaining work** (section 7) by value for (a) the 25 Nov presentation and (b) the later paper. Say
>    what to cut.
> 4. **Check the state-change representation design (section 5)** in depth: the state vector, how mixtures and
>    ingredient interactions are represented, what is computed versus learned, and whether it can support the
>    Step 35 representations without circularity.
> 5. Keep the project's frozen rules (section 2.3). If you think a frozen rule is wrong, say so separately and
>    explain; do not silently plan around it.
>
> Output format: (A) a verdict paragraph; (B) a table Q1–Q40 with columns *answer / agree? / risk / how to
> settle*; (C) missing items, each with where it goes in the 36-step plan; (D) a ranked, cut-down plan to 25 Nov;
> (E) any change you propose to the state representation, as a concrete schema.

---

## 1. What the project is

**Central question (proposal):** can a system that tracks the *state* of food through a recipe, and knows which
claims are backed by evidence, answer cooking and food-science questions better and more honestly than text RAG?

| Hypothesis | Statement (proposal brief) | Status |
|---|---|---|
| H1 | State-aware retrieval beats text-only / dense RAG on current-state and next-action questions | prereg + 100 draft questions ready; waiting on human review |
| H2 | Process information beats food-identity-only models on unseen ingredient × process pairs and unseen studies | not tested; 29-diag runner ready, waiting on human approval |
| H3 | Evidence-class routing with calibrated abstention lowers the unsupported-claim rate at a small cost in coverage | prereg ready; waiting on human review |
| H4 | Feasibility filtering and recovery reasoning respect user constraints and state divergence better than a generic chatbot | not started; out of scope before 25 Nov |

| Deliverable | Content | Status (estimate) |
|---|---|---|
| D1 evidence ledger | process-effect rows with provenance | 17,978 E3 rows (public tables), unverified; 0 of 40 hand-verified literature rows |
| D2 completion benchmark | recipe/ingredient completion with conformal intervals | not run |
| D3 state-tracking engine | recipe → event log → per-step state | built and run on the full corpus; no gold comparison yet |
| D4 retrieval with abstention | query router + evidence packets + abstain | core done on real ledgers |
| D5 end-to-end RAG + B0–B5 ladder | benchmark + ablation ladder | 20-question silver ladder only; 100-question benchmark drafted |

Overall progress (agent's estimate, `PROGRESS_AUDIT_2026-11-07.md`): about 35–40 % of the 36-step plan; about
25 % of the proposal deliverables; 0 of 4 hypotheses tested.

---

## 2. Architecture and frozen rules

### 2.1 Flow of one recipe

```
recipe text ─► [A] Rung A extraction (rules)       ─► entities, quantities, events, process ids, spans
            ─► [A'] NER (DeBERTa-v3 + CRF)          ─► ingredient mentions (second opinion; never gold)
            ─► [B] event replay / state graph       ─► lots: what exists, what was done to it, merges, order
            ─► [C] condition binding (Layer 1)      ─► per event: time, T, medium, lid, start, size, matrix
            ─► [C'] scenario layer (Layer 2)        ─► GENTLE / TYPICAL / INTENSE brackets from cited defaults
            ─► [D] physics drivers θ(t)             ─► core T trajectory, time above T, equivalent dose
            ─► [K] lot state (NEW, section 5)       ─► composition, pH flags, solutes, mechanism screen, interactions
            ─► [E] formula router (gates G0–G9)     ─► DIRECT / INTERPOLATE / SIMULATE / QUALITATIVE / ASK / UNKNOWN
            ─► [F] process-effect model T(S,P,θ)    ─► numbers only from measurement or a calibrated model
            ─► S_{t+1}
question    ─► [G] query router (SSOT §39) ─► [H] evidence packets + decision layer ─► cited answer / ASK / ABSTAIN
learning    ─► [I] transition models (Steps 29–33) on EVD + θ features ─► generic behaviour
            ─► [J] representations (Step 35): molecule → ingredient → ingredient-state → recipe → cuisine
```

### 2.2 State, process, transition (SSOT §4)

- State of an entity or lot: S_t = [I composition, F form, C cookedness / chemical-process state, T temperature,
  X texture, M molecular / sensory, N nutrition, V visual]. Not every field must exist; missingness is explicit.
- Process: P_t = [method, medium, temperature, duration, pressure, humidity, pH, size, surface area, fat, mixing].
- Transition: S_{t+1} = T(S_t, P_t, θ_t). Prediction levels: L1 physical, L2 sensory, L3 mechanism class,
  L4 specific molecules (only with strong evidence; direction always scoped to a driver window).
- Every condition value is (value, unit, type ∈ {POINT, INTERVAL, QUALITATIVE, UNKNOWN}, mask, provenance) (§199.5,
  §199.7).

### 2.3 Frozen rules the plan must respect

1. **Output contract (§141):** a transition is `unsupported`, `physically_possible` or `evidence_supported`. A number
   is emitted only from a measurement (EVD) or a calibrated, held-out-validated model. UNKNOWN is never 0.
2. **Router order:** measured evidence first; semantic or embedding similarity may only *find* candidates, never
   choose a route or a number. UNKNOWN never routes to SIMULATE (property-tested).
3. **Recipes are not chemistry truth (§199.6, line 72):** chemistry, pH trajectories, kinetic parameters and sensory
   causality are separately evidenced layers; co-occurrence never trains chemistry targets.
4. **Learned interaction weights are not reactions (§213.12).**
5. Two physical layers (D-077): Layer 1 TEXT_STATED and Layer 2 SCENARIO are never mixed; Layer 2 is labelled
   ASSUMED_DEFAULT / MODEL_DERIVED / NON_CITABLE.
6. Protected ledgers (EVD, COND, SRC, MEAS, SNAP) stay byte-identical; failed gates are never erased (R-20);
   23b (scientific application of the router to real COND rows) stays blocked until the 07.A gate passes (R-05).
7. Human gates: signatures, approvals and nonces are human only. (Note: D-071 lets AI personas "ksh"/"prv" decide
   some review blocks; see Q37.)
8. Licences: BBC Good Food text stays on the Mac only (D-003); third-party text is git-ignored; committed outputs
   are counts only.

---

## 3. The 36 steps: purpose, technique, status

Status words: DONE, RUN (run on the full corpus), CODE (built and tested on synthetic or constructed cases),
DRAFT, BLOCKED, NOT STARTED.

| Step | Purpose | Technique | Status | Next |
|---|---|---|---|---|
| 01 Freeze authority | SSOT v15 as authority | document control | DONE | v16 change set not applied |
| 02 Audit state | inventory | scripts | DONE | — |
| 03 State semantics | S_t fields, SVAR registry | registry (355 SVAR: 354 chemical, 1 physical) [S178 erratum: 224 distinct SVAR ids (223 CHEMICAL + 1 PHYSICAL); 355 / 354 / 1 are ledger version lines (reports/s178/evd/svar_reconciliation_v1.md)] | DONE | physical/history SVARs missing (Q11) |
| 04 Evidence / provenance contracts | EVD/COND/SRC/MEAS schemas | JSON Schema | DONE | — |
| 05 Normalise EVD | retention rows | parsers (USDA R6, Bognár) | DONE | — |
| 06 Source manifest | licences | registry | DONE | Food.com training licence open |
| 07 Condition normalisation | COND ledger (4,746 rows) | rule normaliser | **07.A FAILED** (kappa); R1 redo with Gwet AC1 ready | humans label 100 conditions |
| 08 Source lineage | study/independence groups | lineage graph | **G08-3 FAILED** (on record) | — |
| 09 Extraction machinery | AI extract + human verify | span-anchored extraction | CODE | — |
| 10 20-row mechanism pilot | first kinetic rows (vitamin C) | AI extraction with spans, dual human verification | 16 CAL rows ready to verify; 5 PDFs need browser download | humans verify by 15 Nov |
| 11 Wave-1 verified evidence | 40+ verified literature rows | as 10 | NOT STARTED | — |
| 12 Structured DB evidence | FDC/FooDB/Phenol-Explorer joins | crosswalks | partial | ING→FDC crosswalk 0 % resolved (new work, section 5) |
| 13 Literature discovery corpus | OpenAlex search | retrieval | partial | — |
| 14 Coverage-driven growth | fill gaps | active acquisition | NOT STARTED | — |
| 15 Freeze DATA-EVIDENCE v1 | snapshot + seal | hashing, 15a.R seal | 15a.R seal DONE; 15b not frozen | freeze record awaits human approval |
| 16 Instruction schema | event schema | JSON Schema | DRAFT | — |
| 17 Instruction extraction | Rung A rules | lexicon + rules, invented values 0 | RUN: 14,594,812 events | gold comparison needs P1b |
| 18 Event-sourcing engine | replay → lots | state graph | RUN | — |
| 19 Gold trajectory pilot | gold state labels | dual annotation | P1 done; P1b waiting on nonce | — |
| 20 Scale procedural corpus | silver at scale | — | NOT STARTED (out of scope before 25 Nov) | — |
| 21 Mechanism ontology | MECH registry (20–40 entries) | flat registry, three-valued gates | 32 entries DRAFTED, 0 reviewed | blind dual review (G21.6) |
| 22 Event → effect signatures | candidate mechanisms per event | rules (no learned classifier) | DRAFT | 250-case sealed case set |
| 23 Applicability engine (router) | route per event × target | gates G0–G9, Kleene logic | 23a CODE + demo RUN: 36,359,902 checks, DIRECT 274,058 (0.754 %) | 23b BLOCKED by 07.A |
| 24 Formula registry | FORM rows | registry + fitting library | CODE, no data | — |
| 25 Parameter compatibility | PARAM domain match | retrieval over PARAM | CODE, **0 PARAM rows** | needs Step 10 |
| 26 One deterministic simulator | sim_aa_1 (vitamin C) | two-compartment kinetics + leaching | CODE, no parameters | fit after M3 |
| 27 Held-out validation | SIM-VAL split | pre-registered split | BLOCKED by 26 | — |
| 28 E7 synthetic prior | controlled synthetic data | — | deferred (R-13) | — |
| 29 Transition bootstrap | baselines D0–D5 on EVD | HistGB, shrinkage means, grouped splits | 29-diag runner CODE | human approves freeze + signs prereg |
| 30 Tabular bake-off | strong tabular models | LightGBM etc. | one exploratory run (prior exposure) | — |
| 31 Physics / condition features | θ features | physics drivers | heating layers RUN (section 4) | non-heat families, lot state |
| 32 Focused kinetics | hierarchical Arrhenius | OLS Model A (shared Ea, per-paper intercept) | CODE | needs PARAM |
| 33 Mechanistic vs ML vs hybrid | comparison | — | NOT STARTED | — |
| 34 Short rollout | multi-step trust horizon | — | NOT STARTED | — |
| 35 Representation ladder | molecule → … → cuisine | explicit rungs first, learned gated | CODE (synthetic); signature pending | Step 35 signature |
| 36 Evidence compiler → selective RAG | D4/D5 | router + retriever + claim enforcement | core CODE on real ledgers | benchmark runs |

---

## 4. What has run at full scale (numbers)

| Item | Result | Where |
|---|---|---|
| Corpus | 612,782 recipes: Food.com 522,517 · Gutenberg 73,955 · BBC 11,934 · Wikibooks 3,676 · TASTESET 700 | recipe base v1 |
| Rung A events | 14,594,812 events, exceptions 0 | Step 17 census |
| Heat events | 1,746,405 | `reports/step26/binding_census_L1_*` |
| Layer 1 (text only) | both time and T stated for 3.3 % of heat events (4.8 % with ranges) | 1,000-recipe census S172 |
| Layer 2 (scenario) | 810,951 heat events (46 %) get driver trajectories | `reports/step26/scenario_L2_*` |
| Router census (vitamin C) | 36,359,902 checks; DIRECT 274,058 (0.754 %); every UNKNOWN names NO_FORM / PARAM_UNCONFIRMABLE / NO_CANDIDATE_MECHANISM | `reports/step23/router_demo_census_vitc_full_corpus_S171.json` |
| Evidence coverage | EVD vitamin C: 115 (ingredient, process) pairs over 25 ingredients; corpus has 130,886 distinct pairs | same |
| NER | 4.16 M ingredient lines tagged (Food.com 4.13 M); model DEV F1 0.940 on TASTEset | `reports/ner_v2/ner_corpus_counts_S174.json` |
| Compute | vinayak (A100 ×2, 128 cores), manjot (A100 GPU 1, CPUs), Mac (BBC only); 14 runs logged | `registry/compute_runs_v1.csv` |

**New finding (S175):** the Food.com source (Kaggle "irkaal" dump) stores quantities and ingredient names
separately and **drops the unit** ("4 blueberries" was "4 cups blueberries"). This explains the NER finding (UNIT
tags far below QUANTITY on Food.com) and means grams cannot be computed for 85 % of the corpus without another
source of units (Q8).

---

## 5. The state-change layer being built now (lot state, [K])

Kush's requirement: model not only heat but **pH, composition, molecular and structural change, and how
ingredients affect each other** inside a recipe. The SSOT already defines the fields; what is missing is the
*mixture-level* state. Design (agent proposal, not frozen):

### 5.1 Unit of state

A **lot** is anything the state graph tracks (a raw ingredient, a cut ingredient, a mixture such as a batter or a
sauce). Merges create a new lot whose parents are kept. State is recorded **per lot per event**.

### 5.2 Fields per lot-step (each as value, unit, type, mask, basis, provenance)

| Field | How it is obtained | Type allowed | Source |
|---|---|---|---|
| members | state-graph lineage (ING ids of all parents) | POINT | Rung A + replay |
| mass per member | ingredient-line quantity → grams (mass stated; volume × SR portion density; count × SR portion weight) | POINT / INTERVAL / UNKNOWN | rc2 quantity parser; USDA SR Legacy `food_portion.csv` |
| composition | mass-weighted water, protein, fat, carbohydrate, sugars, starch, fibre, ash, sodium, vitamin C per member; exact interval bounds of the mixture fractions when every member's mass is known; otherwise presence only | INTERVAL / QUALITATIVE (presence) | USDA SR Legacy (public domain), ING→SR match |
| solute load | g salt and g sugar per g water in the lot | INTERVAL / UNKNOWN | arithmetic on composition |
| water activity | from solute load (Norrish / Ross equations) | INTERVAL, MODEL_DERIVED | constants need a cited source |
| pH | per member pH range; lot gets flags CONTAINS_ACID_MEMBER (range ≤ 4.6), CONTAINS_ALKALINE_MEMBER, ALL_MEMBERS_ACID; **no mixture pH number** (buffering unknown) | QUALITATIVE + member ranges | FDA/CFSAN "Approximate pH of Foods and Food Products" (Oct 2003, archived on webharvest.gov; US government work) |
| temperature | core-temperature trajectory from Layer 1 / Layer 2 | INTERVAL per bracket | physics drivers |
| form | cut history (diced, sliced, crushed …), mixing flags (whisked, kneaded, emulsified) | QUALITATIVE | Rung A + cues |
| mechanism screen | for each of the 32 MECH entries: reactants present? (composition), drivers in window? (T, time, pH flags, water, medium), inhibitors present? → POSSIBLE / NOT_POSSIBLE / UNKNOWN (Kleene) | three-valued | MECH roster + condition-window registry (to be sourced) |
| interaction edges | when a POSSIBLE mechanism needs reactants or conditions supplied by **different members** (acid from lemon + protein from fish → acid denaturation; baking soda + onion → faster browning/softening; tomato acid + beans → slower softening; salt + aubergine → osmotic water loss; sugar → lower water activity, delayed gelatinisation; egg yolk + oil + whisking → emulsion; acid + green vegetable + heat → chlorophyll → pheophytin; acid + vitamin C → slower loss) | edge (member_i, member_j, mechanism, direction, driver window) | mechanism-mediated only; never a learned co-occurrence weight |
| nutrition | retention via the router (DIRECT / SIMULATE when calibrated) | per §141 | EVD, sim_aa_1 |

### 5.3 What is computed versus learned

- Computed (deterministic, traceable): members, masses, composition, solute load, pH flags, temperature, mechanism
  screen, interaction edges. All MODEL_DERIVED / NON_CITABLE unless a measurement backs them.
- Learned (later, gated): transition magnitudes (Steps 29–33) on EVD rows using these as features; representations
  (Step 35) over sequences of lot-step states. The learned models never feed back into the computed layer.

### 5.4 Build order

1. ING → SR Legacy match (lexical, deterministic, scored; AI-drafted, human verification queue by corpus frequency).
2. Ingredient line → (ING, grams interval, basis).
3. Lot composition with exact interval bounds.
4. FDA pH registry + member pH ranges + lot flags.
5. Mechanism condition-window registry (sourced) + mechanism screen + interaction edges.
6. Non-heat families (cooling/freezing, soak/marinate/brine, drain, drying/preservation, cut, mix, rest, storage)
   feeding the same record.
7. Full-corpus run (manjot / vinayak for non-BBC, Mac for BBC), counts-only reports, run log.

---

## 6. Data and licences

| Data | Size | Licence / constraint |
|---|---|---|
| BBC Good Food (A1) | 11,934 recipes | RESTRICTED, Mac only (D-003), analysis only |
| Food.com (Kaggle) | 522,517 recipes | uploader-declared CC0, UNVERIFIED; units missing in source |
| Gutenberg segments | 73,955 | public domain; the only `training_allowed=YES` recipe set |
| Wikibooks | 3,676 | CC BY-SA |
| TASTESET | 700 | research dataset (ingredient lists only) |
| USDA SR Legacy (FDC, 2018-04) | 7,793 foods, nutrients, portions, retention factors | public domain |
| USDA R6 retention, Bognár | retention tables → EVD | public / citation |
| FDA approximate pH list | ≈ 488 items | US government work |
| FlavorGraph, FooDB, FlavorDB, Phenol-Explorer, ChemTastesDB | molecules and links | mixed (NC, BY-NC-SA, unclear) → internal analysis only |
| MOL ledger | 1,726 molecules | per source |

---

## 7. Remaining work to 25–26 Nov (agent's ranking)

| # | Item | Owner | Depends on | Value (talk / paper) |
|---|---|---|---|---|
| 1 | Lot-state layer [K] full corpus (section 5) | agent | — | high / high |
| 2 | Non-heat process families | agent | 1 | medium / high |
| 3 | 07.A-R1 labels → score (opens 23b) | Kush + Parv | prereg signatures | high / high |
| 4 | AA pilot: verify 16 CAL rows, 5 PDF downloads → fit → freeze → SIM-VAL (first SIMULATE) | Kush + Parv, then agent | — | high / high |
| 5 | D5 review → freeze benchmark → H1 / H3 runs (Ollama on vinayak) | Kush + Parv, then agent | — | high / high |
| 6 | 29-diag (H2 diagnostic) | Kush approves freeze + signs | — | medium / medium |
| 7 | NER vs Rung A agreement; MENTION ledger draft | agent | — | low / medium |
| 8 | Router re-run with lot state + PARAM | agent | 1, 4 | high / high |
| 9 | Step 35 explicit rungs over lot-state sequences | agent | signature, 1 | medium / high |
| 10 | Report + slides from real results | agent draft, humans edit | 3–8 | high / — |

Not before 25 Nov: H4, D2, Steps 20, 28, 33, 34, FlavorTwin, multimodal, learned representation rungs.

---

## 8. Doubts, open questions and R&D blockers (please answer each)

Each item: the question, why it matters, the options, and the agent's current lean.

### A. Physical layers and defaults

- **Q1 Layer 2 circularity.** Every heat event is run at GENTLE / TYPICAL / INTENSE values from a 28-row defaults
  registry. If these drivers become features for Steps 30–35, models may learn our defaults table rather than the
  recipe. Options: (a) keep Layer 2 out of learned features; (b) include with basis masks and an ablation that
  removes it; (c) use only as a sensitivity band. *Lean: (b) with a mandatory ablation.*
- **Q2 Sources for defaults.** The 28 default rows (bath T per process, oven gas marks, h by medium, k/α, half-
  thickness by cut class, T0) are `SOURCE_UNVERIFIED_AGENT_RECALLED`. Which references are acceptable (Singh &
  Heldman, Rahman *Food Properties Handbook*, ASHRAE Refrigeration, Choi–Okos 1986)? Is a handbook value with a
  range enough, or do we need primary measurements? *Lean: handbook with range, page cited, human-verified.*
- **Q3 Surface versus core.** The slab model gives core temperature. Maillard, crust and drying happen at the
  surface, which sits near 100 °C until it dries. Do we need a surface/drying-front model (two-zone, or an
  evaporative boundary) before any browning claim? *Lean: yes, a simple two-zone surface model, QUALITATIVE only.*
- **Q4 Geometry.** Pieces are treated as infinite slabs with half-thickness from cut class. Is slab acceptable for
  diced (cube) or whole (sphere/cylinder) items, or should the shape factor change? *Lean: add sphere and cylinder
  series; map cut class to shape.*
- **Q5 Non-heat formulas.** Proposed: Plank (freezing time), Fickian slab uptake (marinade/brine), constant + falling
  rate drying, F-value (z = 10 °C, T_ref 121.1 °C), qualitative flags for mixing. Adequate for a first pass?
  Which parameter sources (D for salt/acid in meat and vegetables)?
- **Q6 Equipment and altitude.** Oven calibration error and altitude (boiling point) are ignored. Add as Layer 2
  uncertainty, or out of scope?

### B. Composition, quantities, pH, interactions (section 5)

- **Q7 ING → USDA match.** 5,387 ING rows, 0 % crosswalked. A lexical matcher will be AI-drafted. How much must be
  human-verified before composition can be used even as MODEL_DERIVED? *Lean: verify the top ingredients covering
  80 % of corpus mentions (a few hundred), the rest flagged LOW confidence.*
- **Q8 Food.com has no units.** For 522,517 recipes, grams are unknown. Options: (a) presence-only composition for
  Food.com; (b) find the original Food.com data with units (licence and availability unknown); (c) infer units with
  a model (an imputation, would need a flag and validation). *Lean: (a), and ask whether (b) is possible.*
- **Q9 Volume and count to grams.** Using SR portion weights (for example "1 cup chopped onion = 160 g", "1 medium
  onion = 110 g") conflicts with the strict rc2 rule that a portion record must be HUMAN_VERIFIED. Is SR Legacy an
  acceptable portion authority under a new basis code (`SR_PORTION`, Q-level lower than stated mass)?
- **Q10 Mixture pH.** We will not compute a mixture pH (buffer capacity unknown). Are member pH ranges plus lot flags
  (contains acid member, contains alkaline member) enough to gate chlorophyll, pectin, anthocyanin and protein-acid
  mechanisms? Is there a defensible mixture model (titratable acidity, buffer capacity) with available data?
- **Q11 Missing state variables.** SVAR has 354 nutrient variables and 1 physical. The lot state needs physical and
  history variables (moisture fraction, water activity, cell integrity, enzyme activity state, time since
  disruption, thermal dose, emulsion/aeration state, gluten development). Step 21/22 already ask for these under H4.
  Which set, and with what definitions?
- **Q12 Interaction definition.** Interactions are only mechanism-mediated edges between members of the same lot.
  Is that sufficient? Should physical interactions count (one ingredient's water is the medium for another;
  oil as the heat medium; flavour partitioning into fat)? How can interactions be validated when measured mixture
  data are almost absent?
- **Q13 Mixture factorisation.** Represent a sauce as (component states) + (mixture-level properties: pH flags,
  solute load, water, fat, solids)? Or as one merged composition? *Lean: both, components kept, mixture fields
  added.*
- **Q14 Order effects.** "Salt the aubergine, then rinse" versus "add salt at the end" differ. The event order is
  kept, but solute uptake needs time and contact. Model contact time per lot pair?
- **Q15 Mechanism condition windows.** The SSOT warns there is no universal switch (gelatinisation, denaturation,
  enzyme inactivation vary by matrix). Windows will be stored as matrix-scoped intervals with evidence ids,
  NECESSARY / MODULATING / INHIBITING. Which sources are acceptable (review papers are context only; numbers need a
  primary source)? Is the screen useful while all 32 MECH entries are unreviewed (G21.6)?

### C. Kinetics and evidence

- **Q16 One calibrated system.** PARAM has 0 rows; the AA (vitamin C) pilot has 16 CAL rows and a 4-paper SIM-VAL
  split; 5 papers need a browser download. Is one system enough to show SIMULATE works? Should chlorophyll
  (sim_chl_1, pH-gated) be the second?
- **Q17 Evidence quality.** The 17,978 E3 rows come from public tables (USDA R6, Bognár), unverified, with imputed
  factors in the source. D1 also asks for 40 hand-verified literature rows (0 so far). Minimum acceptable for the
  talk?
- **Q18 Censoring.** Retention capped at 0.975 (GT_CAP) in DEL-2 training. 29-diag stratifies by cap. Enough?
- **Q19 Prior exposure.** DEL-2 and an S160 Step 30 run already read the E3 rows. 29-diag is labelled
  PRIOR_EXPOSURE_REANALYSIS. Is any H2 claim possible from these rows, or only diagnostics?

### D. Router and answering

- **Q20 Router usefulness.** DIRECT is 0.754 %; nearly everything else is UNKNOWN. Is a mostly-UNKNOWN router a
  result (honest abstention) or a failure? What coverage target is reasonable once lot state and one calibrated
  model exist?
- **Q21 QUALITATIVE from unreviewed mechanisms.** Should a POSSIBLE mechanism screen (from unreviewed MECH entries)
  be allowed to give a QUALITATIVE direction labelled AI_DRAFTED, or must it wait for review?
- **Q22 Similar-food evidence (INTERPOLATE).** P2 questions have only similar-food evidence. What counts as
  bracketing across foods (same food group? same composition class?) without letting similarity decide?
- **Q23 ASK branch.** Value of information is not computed. Is a simple rule (ask when the missing input flips the
  route) enough for H3?

### E. Evaluation and statistics

- **Q24 07.A redo.** Kappa failed partly through the kappa paradox (skewed categories). R1 uses Gwet AC1 ≥ 0.80
  pooled + a critical-field rule, pre-registered before new labels, kappa reported. Is switching the statistic
  defensible?
- **Q25 Benchmark independence.** 100 questions are AI-drafted; the only reviewers (Kush, Parv) are also the system
  authors. How to argue independence? Add an outside reviewer for a subset?
- **Q26 Power.** H1 has n ≤ 30 per block with an exact McNemar test; only large differences can show. Accept as a
  pilot with Newcombe intervals, or enlarge?
- **Q27 H2 and H4.** H2 is diagnostic only; H4 is not started. Is it acceptable to present only H1 and H3 as tested,
  with H2 as diagnostic?
- **Q28 Gold for D3.** The P1b pilot waits on a human nonce; no gold comparison of the state tracker yet. Minimum
  gold size for a D3 claim?

### F. Representations (Step 35) and learning

- **Q29 What is "the state representation"?** Proposed: the explicit lot-step state vector (section 5.2) as rung 0,
  sequence encoders over it as later rungs. What is a non-circular supervised target? The SSOT allows few:
  measured retention (EVD), held-out recipe steps, completion.
- **Q30 Training licence.** Only Gutenberg (73,955) is training-allowed; Food.com is uploader-declared CC0. Can
  learned rungs use Food.com?
- **Q31 Process-response similarity (35f).** It needs Steps 15, 27, 30, 33. Is there a cheaper first version
  (similarity of mechanism-screen profiles) that is still non-circular?
- **Q32 Generic behaviour.** The goal "learn that heating in water leaches and degrades vitamin C; acid speeds
  chlorophyll loss" — is that a model output, or a mechanism-registry fact that the model should be tested
  against? *Lean: registry fact; models are tested for consistency with it.*

### G. NER and extraction

- **Q33 NER role.** NER is a second opinion to fill unlinked lots. How to use it without letting a model output
  become gold? Agreement with Rung A as a diagnostic only?
- **Q34 Domain shift.** The NER model is trained on TASTEset (with units); Food.com lines lack units. Retrain or
  accept?

### H. Compute, reproducibility, governance, timeline

- **Q35 Reproducibility.** Data bundles are not in git; servers get tracked files only; runs are logged with code
  and input hashes. Enough for a paper?
- **Q36 BBC.** BBC is processed on the Mac only. Its numbers enter counts-only reports. Any licence risk in
  reporting BBC-derived counts?
- **Q37 Governance.** D-071 lets AI personas "ksh"/"prv" decide some review blocks, while signatures and approvals
  are human only. Where exactly is the line? Can an AI-persona decision ever close a human gate?
- **Q38 Timeline.** Human items (07.A labels by 13 Nov, AA verification by 15 Nov, benchmark review by 16 Nov) are
  the critical path to H1/H3 results on 19 Nov and slides on 22–24 Nov. What is the fallback if they slip?
- **Q39 Scope.** Is the lot-state layer worth doing before 25 Nov, or should all agent time go to H1/H3 and the
  first SIMULATE?
- **Q40 SSOT v16.** The v16 change set is drafted, not applied. Should it be applied before the talk?

---

## 9. What may be missing from the plan (agent's suspicion; please extend)

1. **Mass balance and cooking yield:** USDA cooking-yield factors (SR `retention_factor.csv`, USDA cooking yields
   table) would tie composition to water and fat change and to retention arithmetic.
2. **Surface / drying-front model** for browning and crust (Q3).
3. **Food-safety layer:** core temperature and time for pathogen lethality; the router has a "safety" input
   that nothing fills yet.
4. **Allergen propagation** through lots (ALLERGEN ledger exists, not wired to lots).
5. **Uncertainty propagation** across steps: intervals compound through a recipe; no method is chosen.
6. **Salt and acid uptake** into foods (brining, marinating) as a state change, not only a flag.
7. **Enzyme history** (cut → rest → heat) for alliinase, myrosinase, PPO: time since disruption and inactivation.
8. **Oil uptake and fat exchange** in frying as a composition change.
9. **Sensory layer:** out of scope, but section 5 should leave fields for it with UNKNOWN.
10. **Physical and history SVARs** (Q11) as an additive SVAR v1.1 under H4.
11. **External validation:** an outside food scientist for a subset of mechanism windows and benchmark answers.

---

## 10. Failures and negative results on record (must stay visible)

- 07.A condition-normalisation gate FAILED (kappa); redo is pre-registered, not a rewrite.
- G08-3 lineage gate FAILED.
- D-074: implicit-object rule R1 scored 4/60 CORRECT and was not landed; R2 withdrawn.
- DEL-2 D7a matched D1 to four decimals on Phenol-Explorer (shortcut suspicion; 29-diag reviews it).
- Demo stopped (S173) because it showed almost only "no measured data": core first.

## 11. Addendum, 9 Nov (S175): lot composition layer built; first numbers

Built (tests first; `src/culinarystate/composition/`, 54 unit tests):

| Piece | What it does | Status |
|---|---|---|
| `sr_legacy.py` | USDA SR Legacy 2018-04: 11 roster nutrients per 100 g, portions; missing nutrient = UNKNOWN, never 0 | done |
| `ing_sr_match.py` + `registry/ing_sr_defaults_v1.csv` | ING name -> SR food: curated registry first (490 terms, kinds DIRECT / UK_US / DEFAULT_FORM / APPROX / NO_SR_EQUIVALENT / NOT_A_FOOD / AMBIGUOUS), lexical fallback; all AGENT_PROPOSED, UNVERIFIED | done; needs human check |
| `line_mass.py` | line -> grams interval: stated mass (Q0), count x SR portion (Q1), volume x SR density (Q2), else UNKNOWN with reason; SR-based grams flagged until the link is human-verified | done |
| `food_ph.py` + `registry/food_ph_fda2003_v1.csv` | FDA/CFSAN approximate pH list, 479 items; 2 source typos kept UNPARSED; acid class at the 21 CFR 113/114 4.6 boundary | done |
| `lot_state.py` | exact bounds of lot mass fractions and solute per g water (linear-fractional; unknown grams = [0, inf)); pH as member classes + flags, never a mixture pH; PROVISIONAL while SR links unverified | done |

BBC results (Mac, counts only, `reports/s175/`):

- Lines with grams: 75.3% (was 33.7% in `fdc_crosswalk_v0`); 53,069 of those rest on unverified SR links.
- Recipes with every quantified line in grams: 2,064 / 11,934 (17.3%).
- Whole-recipe lots (RECIPE_POOL): water fraction bounded in 15.9%; one unmapped member makes it UNKNOWN.
- 45.5% of recipes contain an acid member (pH <= 4.6); 99.4% have at least one member with no FDA pH (oils, salt,
  sugar, spices are not in the FDA list).

New questions from this work:

- Q41. Anhydrous members (oils, sugar, salt; SR water near 0) have no meaningful pH. May the lot layer mark them
  PH_NOT_APPLICABLE, and what water cut-off is defensible (and from which source)?
- Q42. Lots: is the event-level lot (router lineage) the right unit, with RECIPE_POOL only as an envelope? Should
  NER fragments (registry NOT_A_FOOD) be dropped as non-members?
- Q43. Registry default forms that change composition materially: UK "milk" (whole vs semi-skimmed), double cream
  (~48% fat) mapped to SR heavy whipping (~36%), UK bacon. Keep APPROX with a flag, or leave UNKNOWN?
- Q44. Who verifies the 490 registry rows (Kush / Parv), and is a sample audit (e.g. top 100 by mentions)
  enough to lift PROVISIONAL for those rows?
