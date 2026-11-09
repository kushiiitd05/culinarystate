# CulinaryState: targeted related-work re-search (November 2026)

Status: **AI_DRAFTED · PROPOSED · NON_CITABLE until a human opens each source**. Board item **T0-C02-R1** (lane RELWORK, S178,
2026-11-09). This is not a human gate, signature or approval. Under D-071 an AI lane proposes; Kush and Parv decide what goes into the
report, the slides and any paper.

**Purpose.** This file feeds three things:
- the related-work section of the course report;
- the "how we differ" slide;
- any novelty sentence in a later paper.

It **adds to** `reports/master_plan/research_bibliography_v2.md` (2026-10-22, 318 entries) and does not repeat it. Works already in v2
appear here only as one-line anchors marked *(v2)*.

**Rule for every gap sentence below.** Each one is a **hypothesis about the literature**, bounded by the search described in §1. None
is a claim that nobody has done the thing. Do not write "first" anywhere until the final novelty audit (R&D plan v2 §"Novelty
boundary") has run.

---

## 0. Bottom line

The search covered 2023–2026 across six themes and about 70 queries. Every work it cited was opened on a primary page.

**No work was found that joins the chain CulinaryState builds**, which is:
1. recipe text;
2. a deterministic, replayable event log;
3. per-event *lots* (anything the state graph tracks: an ingredient, a cut piece, a mixture);
4. physical conditions that keep **text-stated** values apart from **assumed scenario** values, with missing values kept as UNKNOWN;
5. an evidence-first answer route that can ASK or ABSTAIN.

Each link has close prior work. The nearest works each cover one or two links:

| Link in the chain | Nearest works |
|---|---|
| Per-step intermediate states | PizzaCommonSense 2024; ReGraph 2026 |
| A symbolic state executor | SIMMER 2026 |
| Hand-encoded per-step temperature and duration | Kumbhakern et al. 2025 |
| Physics of one dish | Digital twins: Kannapinn et al. 2025; Cabeza-Gil et al. 2023 |
| Recipe nutrients without step conditions | Vijayakumar et al. 2024; FoodBench-QA 2026 |
| Abstention decided by the LLM, or by a learned router | Trust-Align 2025; Adaptive-RAG 2024 |
| Provenance-separated memory for chat agents | Eywa 2026 (preprint) |

The defensible contribution is therefore **the integration and its measured behaviour**, not any single component.

**Three claims we can defend** (worded as they should appear in the report):
1. **Integration (hypothesis, bounded search).** "In a targeted search of 2023–2026 work we found no system that replays recipe text
   deterministically into ingredient and mixture state, attaches physical conditions that separate text-stated from assumed values,
   and uses that state to decide whether a food-science answer is supported." Our numbers are corpus-scale:
   - 14,594,812 events;
   - 1,746,405 heat events;
   - Layer 2 trajectories for 46 % of heat events.
2. **Evidence applicability is a separate decision from evidence retrieval (AI-gated counts on a fixed sample; gates unaudited).** Prior recipe-nutrient work applies retention
   factors by a default cooking method, ignores cooking, or imputes until every profile is complete. Our target-presence and
   lot-context gates withhold a measured retention value when the food or its context does not match. On the fixed 1,000-recipe
   sample, vitamin C DIRECT routes fall from **450 to 73**; of the 377 withheld, 346 are MERGED_LOT_CONTEXT, 30 PRIOR_PROCESS_CONTEXT and
   1 TARGET_ABSENT (S177 census, three gates; `reports/step23/router_demo_census_vitc_nonBBC_1000_S177.json`, `direct_ungated_cross`).
   The S176 two-gate split (59 TARGET_ABSENT, 318 MERGED_LOT_CONTEXT) is superseded. This is a design result with counts, not yet
   validated against human gold.
3. **Recipe text under-determines physics, at scale (census counts).** Only **3.3 %** of heat events state both time and
   temperature (4.8 % counting ranges; 1,000-recipe census S172). The full non-BBC census (L1 v04,
   `reports/s178/analysis/corpus_can_say_v1.md` table 2) gives 1.77 % for Food.com, 3.07 % for Wikibooks and 0.18 % for Gutenberg. Missing values stay UNKNOWN instead of being filled in. Prior work
   either names this gap without measuring it (Kalra et al. 2020; Yun et al. 2025) or fills it silently:
   - Vijayakumar et al. 2024 use a default method per ingredient;
   - Kumbhakern et al. 2025 map "medium heat" to a °C range with no stated/assumed label.

**Three claims to avoid:**
1. "First system to track ingredient state in recipes" or "first event-sourced recipe engine". Prior work includes:
   - ProPara, OpenPI 2.0 and NPN-Cooking *(v2)*;
   - PizzaCommonSense, Bikakis et al. 2023, SIMMER, ReGraph and Toyooka 2025 *(v2)*;
   - general event-sourced agent runtimes (Nakajima 2026, Malo & Qiu 2026).
2. "A novel memory architecture." CoALA (TMLR 2024) already gives the taxonomy, MIRIX has typed stores, and Eywa has "evidence
   before belief" with deterministic retrieval. At most we can say that memory planes are **separated and enforced by firewalls**
   (`Model memory ≠ Evidence memory`, SSOT §233.7). The plan's USP map already says the taxonomy's novelty is unverified.
3. Any claim that abstention is **calibrated** or **guaranteed**, that the system **beats RAG or Self-RAG**, or that it
   **simulates or digital-twins cooking**:
   - H1 and H3 are untested;
   - there is no calibration set;
   - 0 simulators are validated;
   - Layer 2 is a bracket of scenarios, not a prediction;
   - conformal and risk-controlled RAG (C-RAG *(v2)*, Conformal-RAG 2025, TRAQ *(v2)*) already offer guarantees we do not have.

---

## 1. Method and limits

- **Scope.** There were six themes, set by the lane brief (§3.1–§3.6). The period was 2023 to 9 Nov 2026. Older work appears only
  as a marked "pre-2023 anchor" when it is the closest match.
- **Search.** Web search, about 70 queries. Four agents ran in parallel: three search lanes and this lead. Searches went through
  Google-style web search plus ACL Anthology, arXiv, OpenReview API, Crossref, Europe PMC and OpenAlex. Queries that found nothing
  relevant are listed in Appendix A, since negative searches are evidence too.
- **Verification.** Each work was opened on a primary page or an authoritative index record. That means the ACL Anthology page,
  arXiv abs page, OpenReview API record, Crossref DOI record, Europe PMC, or the publisher page.
  - **YES-2:** opened by a search lane and opened again independently by the lead in this session. The lead re-opened all 15 core
    works plus 13 others.
  - **YES-1:** opened once by a search lane or by the lead.
  - **PARTIAL:** the record exists, but one detail we would state (a number or a venue) was not confirmed from the text. Do not
    quote that detail.
  - **NO:** not opened. Nothing marked NO is cited.
- **Limits.**
  - This is not a systematic review: there was no PRISMA protocol, no second screener, and no bulk OpenAlex run (Step 13).
  - Search was in English only.
  - Paywalled full texts (ScienceDirect, MDPI, Springer) were often blocked, so some details rest on abstracts.
  - About a third of the 2026 items are recent single- or two-author arXiv preprints. They are flagged; treat them as concurrent
    work, not as established prior art.
  - The board asks a human to read for 1–2 h before any of this is cited.
- **Licence rule (law 6).** No passage of third-party text is reproduced here. Findings are paraphrased; only titles, numbers and
  two- to four-word terms (such as "evidence before belief") appear in quotation marks. Downloaded full texts stayed in the session
  scratchpad and are not committed.

---

## 2. What is being compared (CulinaryState, as built on 9 Nov 2026)

Here is what is built, so the comparisons stay honest.

**Rung A extraction (rules, no LLM).** Rules extract events from recipe text. Over 612,782 recipes this gave 14,594,812 events
(Step 17 census). Replaying the events gives a lot graph in which merges keep their parents (Step 18; `src/culinarystate/state_graph/`).

**Two physical layers, never mixed (D-077):**
- **Layer 1, TEXT_STATED:** only what the text says, plus physical definitions; anything missing is UNKNOWN. Census:
  `reports/step26/binding_census_L1_*`.
- **Layer 2, SCENARIO:** literature-default brackets GENTLE / TYPICAL / INTENSE, labelled ASSUMED_DEFAULT / MODEL_DERIVED /
  NON_CITABLE.
  - It drives core-temperature trajectories.
  - A boundary cap (`simulation/phase_change.py`, cap model 0.2.0, S177) bounds dilute water phases at about 100 °C.
  - It has non-heat families too: soak/brine, freeze/thaw, drying, rest (`reports/step26/nonheat_*`).
  - It is not validated.

**Lot composition (S175, Mac lane, `src/culinarystate/composition/`).** It uses USDA SR Legacy composition, mass intervals and
FDA pH ranges.

**Router.** Measured evidence comes first. The Step 23 router uses gates G0–G9 and Kleene logic: three-valued, so "unknown" stays
distinct from true and false. On top of it sit two new evidence gates (`mechanism/evidence_gates.py`, demo, AI_DRAFTED):
- **Target-presence:** does the food contain the nutrient at all?
- **Lot-context:** sole member, and no prior heat or leach step.

**Decision layer** (`decision/policy.py`). It returns ANSWER / ASK / ABSTAIN, with explicit reasons such as `TARGET_ABSENT`,
`CRITICAL_SLOT_MISSING` and `ABSTAIN_SAFETY`.

**Memory classes (SSOT §233.7).**
- Source memory.
- Semantic memory.
- Episode/session memory (state).
- Evidence memory.
- Model memory, which covers predictions, imputations and simulations.

The 36-step plan's USP map lists a slightly different set: source / evidence / state / model / simulation. Simulation is kept
separate there and "F-6 pending" (see §6, item 5).

**Not built or not run yet:**
- a validated simulator;
- a calibration set;
- the H1 and H3 benchmark runs;
- gold for the state graph (P1b);
- human verification of the gates.

---

## 3. Themes

Each theme gives the closest works, how CulinaryState differs, and a calibrated novelty statement (can claim / cannot claim / needs an
experiment). Numbers in brackets such as [B07] point to the bibliography table in §7.

### 3.1 Procedural and recipe state tracking

*Anchors (v2):* ProPara (Dalvi 2018), OpenPI (Tandon 2020), OpenPI 2.0 (Zhang 2024), Kim & Schuster 2023, the recipe flow graphs
(Mori 2014; Yamakata 2020), NPN (Bosselut 2018), Toyooka 2025 (ingredient-state probing), PAGED 2024 and Gajo 2026.

| Work | What it does | What CulinaryState does differently |
|---|---|---|
| **PizzaCommonSense** (Diallo et al., Findings EMNLP 2024) [B01] | 1,087 recipes cut into 13,141 single-action steps, each annotated with input, action and output (e.g. "tomato puree"). GPT-4 reaches only 26 % human preference. | Its intermediate states are free text, and annotators were told not to insert numbers. Ours are typed lots with mass intervals, composition and Layer 1 / Layer 2 conditions, built by deterministic replay. |
| **SIMMER** (Lu, Zhang & Zhang, arXiv 2026; "Accepted at COLM 2026" per arXiv) [B02] | A human-curated symbolic kitchen world model (77 actions, 262 objects). A state-machine executor finds latent failures in LLM-generated plans: at most 17 % error-free, up to 56 % with latent failures. | It is the closest *executor*, but it checks LLM plans, not real recipe text. Its state is symbolic, with no thermal or compositional quantities and no evidence routing. |
| **CaT-Bench** (Lal et al., EMNLP 2024) [B03] | Recipe step-dependency questions (must A precede B?). The best zero-shot F1 is 0.59, and LLMs lean on surface order. | It tests whether an LLM can *infer* dependencies. We *compute* lot ancestry from the event graph, so dependency is a replay output. |
| **Bikakis et al.**, graphical formalism for recipes (arXiv 2023, preprint) [B04] | Recipes as bipartite graphs of comestibles and actions, with composition, decomposition and substitution operators. | It is the closest formal analogue to the lot graph, but purely theoretical: no parser, no conditions, no QA. |
| **CREPE** (Zhang et al., Findings EACL 2023) [B05] | Links entity states to how plausible an event is. Code-style prompting with explicit entity-event chains raises F1 from about 0.35 to about 0.67. | Here entity state is a reasoning aid for an LLM; ours is a computed record. |
| **PROC2PDDL** (Zhang et al., NLRSE @ ACL 2024) [B06] | LLMs write PDDL preconditions and effects for 27 wikiHow procedures. GPT-4 succeeds about 35 % of the time. | It builds a boolean world model generated by an LLM. Ours is typed, continuous where physics allows, and UNKNOWN-preserving. |
| **Wang et al.**, "Can LMs serve as text-based world simulators?" (ACL 2024 short) [B07] | GPT-4 is judged *unreliable* at predicting state transitions in text games. | This is independent support for *not* letting an LLM produce state. |
| **ReGraph** (Liu et al., arXiv 2026, preprint) [B08] | A large recipe-graph dataset whose attributes track ingredient state, generated from food images. | Its input is images and its states are generated; no physics, no QA. It is on the watch list in R&D plan v2 [S26]. |
| **Nandy et al.**, order-based pre-training (NAACL 2024 short) [B09] | Step order used as self-supervision improves recipe entity tracking (+1.6 % on NPN-Cooking). | A learned tracker. It is a required baseline for the Step 35 representation experiments (R&D plan [S46]), not a competitor to replay. |
| Also: Kanazawa et al. 2024, robot cooking from recipes with VLM food-state recognition [B10]; Shirai et al. 2023, open-domain flow graphs [B11]; Recipe2Plan, Findings EMNLP 2025 [B12] | | Physical state is *perceived* by vision during execution [B10]; graph structure only, no lot semantics [B11]; recipe time constraints are used for scheduling, not physics [B12]. |

**Calibrated novelty (3.1).**
- **Can claim:**
  - Deterministic replay of rule-extracted events into lots with parentage, at corpus scale (14.6 M events, 0 exceptions).
  - Lots carry typed physical and compositional fields, and missing values stay UNKNOWN.
  - Contrast it with LLM-generated textual states (PizzaCommonSense, ReGraph) and LLM-written world models (PROC2PDDL). Both
    [B05] and [B07] report that LLM state prediction is unreliable.
- **Cannot claim:**
  - That this is the first state tracking for recipes.
  - That replay is more accurate than learned trackers. There is no gold comparison yet: P1b waits on a nonce, and Step 19 is not
    scored.
  - That the extracted events are correct. Extraction quality is unmeasured against gold (07.A FAILED; D-074 R1 precision 4/60).
    Only the replay's 0 exceptions is measured.
- **Needs an experiment:**
  - Score the replayed state on the P1/P1b gold against an LLM state predictor and a learned tracker (Nandy-style), at matched
    granularity.
  - Report node-aligned typed-edge F1 (R&D plan §18 scoring rules).

### 3.2 Food knowledge graphs and process-aware food QA

*Anchors (v2):* FoodKG (Haussmann 2019), FoodAtlas, FoodOn (Dooley 2018), PO2/TransformON (Weber 2023), FlavorGraph, FoodPuzzle,
FlavourBench and RecipeMind.

| Work | What it does | What CulinaryState does differently |
|---|---|---|
| **CookingSense + FoodBench** (Choi et al., LREC-COLING 2024) [B13] | A knowledgebase of culinary assertions mined from the web, papers and recipes. It improves retrieval-augmented LMs on FoodBench. | It is the closest food-science retrieval resource. But its assertions are free text, not tied to one recipe's lot state or conditions, and answers are always generated. There is no evidence tier and no abstention. |
| **Kümpel et al.**, "Everything robots need to know about cooking actions" (Frontiers in Robotics and AI 2025) [B14] | Actionable knowledge graphs map Recipe1M+ verbs onto six robot action cores (about 77 % coverage). | R&D plan v2 flags it as "must appear in the novelty audit" [S34]; now verified. Temperature has no values, "duration" is an empty slot, and food state is categorical. The authors say the action groups do not yet model cooking processes. Our Layer 1 / Layer 2 does. |
| **Haduong, Gao & Smith**, "Risks and NLP design: procedural document QA" (Findings ACL 2023) [B15] | Recipe QA where errors can injure or cause allergic reactions. A zero-shot LM matches web humans, and the paper proposes risk-oriented error analysis. | It motivates risk-aware answering but builds no abstaining system. A good citation for *why* ASK and ABSTAIN_SAFETY exist. |
| **KERL** (Mohbat & Zaki, ACL 2025) [B16] | FoodKG subgraph retrieval and an LLM produce constrained recipe recommendations plus micronutrient profiles. | Nutrition here is recipe- or ingredient-level from the KG, with no process effects and no step-wise state. |
| **NGQA** (Zhang et al., ACL 2025) [B17] | A nutrition graph-QA benchmark from NHANES/FNDDS: "is this food healthy for this user?" | It is about user health, not how cooking changes composition. |
| **FoodSky** (Zhou et al., *Patterns* 2025) [B18] | A Chinese food LLM with hierarchical topic RAG. It passes chef and dietetic exams at about 67 %. | A monolithic food LLM that always answers. |
| **FKG.in, composition** (Gupta et al., arXiv 2024; ICPR 2024 workshop per arXiv) [B19] | KG plus LLM workflow for the composition of Indian recipes (IFCT, INDB). The LLM resolves gaps. | The LLM fills gaps silently, and composition is summed over ingredients with no step replay. Indian context is relevant to the course. |
| **Kumbhakern et al.**, action-centric cooking ontology (arXiv 2025; ACM MM 2025 workshop per arXiv) [B20] | A DSL of action graphs with processes, transfers, environments and concurrency. Hand-encoded on one recipe. | See 3.3: closest *representation*, but no parser, physics or QA. |
| Also: R.E.C.I.P.E. (Zenodo 2026, not peer-reviewed) [B21]; Swiss Food KG (arXiv 2025) [B22] | | [B21] applies LLM reasoning over a recipe DAG plus functional and substitution KGs to diagnose failures, with hallucination falling from 0.42 to 0.25. It is weak as a citation and only notes intent. [B22] is a static nutrition KG with Graph-RAG and no process modelling. |

**Calibrated novelty (3.2).**
- **Can claim:**
  - Process-aware answering in which the *recipe's own* event, conditions and lot context decide which evidence applies, instead of a
    KG triple or an assertion retrieved by similarity.
  - Embedding similarity only proposes candidates (frozen rule 2), unlike CookingSense-RAG, FoodSky and KERL, where retrieval feeds
    generation directly.
- **Cannot claim:**
  - A new food KG or ontology. FoodOn and PO2 *(v2)* exist; Kumbhakern et al. and Kümpel et al. are concurrent.
  - Better food QA than CookingSense, FoodSky or KERL. No shared benchmark has been run.
- **Needs an experiment:**
  - The H1 benchmark (100 drafted questions) against a CookingSense-style assertion RAG baseline. "Strongest relevant baseline, not a
    weak generic RAG" (R&D plan §18).
  - Questions must be stratified into current-state, next-action and process-effect.

### 3.3 Cooking simulation and food-process modelling linked to recipes

*Anchors (v2):* Datta 2008, Purlis 2024 (PIML), Farkas, Singh & Rumsey 1996, Choi & Okos 1986, van Boekel 2008/2021, and Kennedy &
O'Hagan 2001.

| Work | What it does | What CulinaryState does differently |
|---|---|---|
| **Kumbhakern, Gupta, Dey & Das** (arXiv 2509.04159, 2025) [B20] | Process nodes carry temperature (with ramps) and duration. In the example, "medium heat + fry" maps to a numeric °C range. Hand-encoded on one recipe; LLM parsing and simulation are future work. | It is representationally the closest. Our version runs automatically at corpus scale and keeps the mapped range as **Layer 2 ASSUMED_DEFAULT**, separate from text-stated values. They have no such separation. |
| **Kannapinn, Dorer, Schäfer & Weeger** (J. Food Eng. 410:112918, 2026; online Dec 2025) [B23] | A digital twin of a convection oven cooking chicken fillets. A neural-ODE reduced-order model trained on FEM drives MPC on core temperature, moisture and texture. | One product and one appliance, with sensor-synchronised setpoints. Nothing comes from recipe text, and it has no nutrient output. |
| **Cabeza-Gil et al.**, crêpe digital twin (J. Food Eng. 359:111697, 2023) [B24] | A pan with a temperature sensor and a scale. A neural surrogate trained on more than 400k simulation points estimates crêpe properties in real time. | Sensor-driven, for one dish. |
| **Feyissa & Frosch**, multistage meat heat transfer (Foods 12(18):3369, 2023) [B25] | A FEM heat model chained across five industrial stages, each with its own boundary conditions, validated on plant temperature profiles. | Per-stage chaining mirrors our per-event replay. But the stage list is a fixed industrial line, not one extracted from text. |
| **Rajpal, Rajodia & Chakravorty**, robotic precision cooking with a digital twin (J. Food Sci. Technol., online 27 Apr 2026) [B26] | A conduction and convection model plus a digital twin plus robot motion planning, on gajar ka halwa. β-carotene is *measured*. | A fixed dish with no text parsing. Indian-cuisine relevant. Details are YES-1 only (lane opened the Springer page; the lead got metadata only). |
| **Cook2LTL** (Mavrogiannis et al., ICRA 2024) [B27] | NER tags Time and Temperature in recipe chunks; an LLM reduces each step to LTL robot primitives. | Temperature is extracted but used only as a symbolic argument; there is no physical model. |
| Also: Purlis 2024, digital-twin review (Curr. Nutr. Rep.) [B28]; Gil-Gaxiola et al. 2025/26, FEM plus kinetics for vitamin C retention in carrot (J. Food Eng. 411:112957) [B29, PARTIAL]; Kato & Hasegawa 2013, interactive cooking simulator [B30, PARTIAL, pre-2023] | | [B28] names real-time high-fidelity models as the bottleneck. [B29] is the physics-plus-kinetics pattern our SIMULATE route needs, for one commodity. [B30] is driven by user operations, not text. |

**Calibrated novelty (3.3).**
- **Can claim (hypothesis, bounded search):**
  - We found no work that takes free recipe text and drives a per-step physical process model at scale.
  - CulinaryState drives *scenario brackets* per heat event:
    - 810,951 heat events, 46 %, get driver trajectories;
    - evaporation cap and non-heat families included;
    - every value labelled MODEL_DERIVED.
  - Separating stated from assumed values is a design feature that the closest representation [B20] lacks.
- **Cannot claim:**
  - "Simulates cooking", "digital twin", or any validated temperature or quality prediction. 0 simulators are validated, and Layer 2
    is not compared with measurement.
  - The digital-twin literature [B23–B26] validates against sensors; we do not.
- **Needs an experiment:**
  - D-VAL: compare Layer 2 core-temperature brackets against **author-stated internal temperatures** in the corpus. Does the
    TYPICAL–INTENSE bracket contain the stated doneness temperature? This is the non-circular check REV-A proposed.
  - For SIMULATE, the Step 27 held-out validation inside the matrix domain gate.

### 3.4 Nutrient retention calculation from recipes

*Anchors (v2):* USDA retention factors Release 6 (2007), Bognár 2002, Murphy et al. 1975 (true vs apparent retention), the
Westenbrink EuroFIR overview, Naravane & Tagkopoulos 2023, Delchier 2012/2014.

| Work | What it does | What CulinaryState does differently |
|---|---|---|
| **Kalra, Batra, Diwan & Bagler** (ICDE 2020 DECOR workshop; arXiv 2004.12286) [B31] — *pre-2023 anchor, IIIT-Delhi* | NER and matching of RecipeDB ingredients to USDA SR; about 36 kcal per serving error. The full text (paraphrased) says accuracy would improve if cooking yields were accounted for, but no consolidated yield resource exists, because yields vary with ingredient, cooking time and other conditions. | This local predecessor *names* the gap we work on. We attach the recipe's own process event to each ingredient and route to retention evidence (EVD) only when it applies. |
| **Vijayakumar, Dubasi, Awasthi & Jaacks**, Indian Food Composition Database (Curr. Dev. Nutr. 8(7):103790, 2024) [B32] | An open Indian Nutrient Databank: 1,095 foods and 1,014 recipes. In a sensitivity analysis, USDA retention factors are applied using the cooking method most common for each raw food in India (paraphrased). The full text reports that only 42.62 % of recipe ingredients could be matched to a retention factor. | The factor comes from an *assumed default method* per ingredient, not from each recipe's step, and unmatched ingredients stay at raw values. We bind the factor to the recipe's event and route unmatched or mismatched cases to UNKNOWN, ASK or ABSTAIN. **The most direct comparison baseline.** |
| **Yun et al.**, cooked meat codes (Nutr. Res. Pract. 19(6):1002, 2025) [B33] | Measured grilling yields; swapping raw codes for cooked ones changes energy by −10 % to −50 % and fat by −20 % to −60 %. The authors conclude (paraphrased) that nutrient databases reflecting cooking conditions (temperature, duration, doneness) should be a priority. | It shows the need empirically. Our Layer 1 / Layer 2 records exactly these conditions per event, or marks them UNKNOWN. |
| **Sato, Inagaki, Shimamoto & Tsuji**, daycare lunches (J. Food Compos. Anal. 143:107614, 2025) [B34] | 30 dishes chemically analysed against raw and cooked recipe calculations. Cooked values agree better. Vitamin C was badly mis-estimated (lane: underestimated by more than 100 % with cooked values). | Evidence that vitamin C needs process-specific evidence rather than generic cooked codes. The vitamin C figure is YES-1 (lane-read abstract); the lead confirmed metadata only. |
| **Li et al.**, catering nutrition model (Front. Nutr. 11:1388645, 2024) [B35] | 150 Chinese dishes give raw-to-cooked ratios and per-method correction factors. | Method-category factors on structured input; no times, temperatures or text. |
| **Renard et al.**, leaching vs degradation of vitamins C and B9 (LWT 180:114694, 2023) [B36] | Separates leaching (Fick, spheres) from first-order degradation across 25–85 °C, for peas and Brussels sprouts. | The calibrated kinetics-plus-leaching model our SIMULATE route needs, for a vegetable-in-water domain. A candidate parameter source for Step 10 / M3 (newer companion to Delchier 2014 *(v2)*). |
| **FoodBench-QA** shared task (Eftimov et al., CL4Health @ LREC 2026, pp. 223–233) [B37] and **FoodyLLM** (Gjorgjevikj et al., Curr. Res. Food Sci. 12:101351, 2026) [B38] | Task 1 predicts nutrients per 100 g from recipe ingredients, scored on EU 1169/2011 tolerances. FoodyLLM fine-tunes an LLM for this task. | Ground truth is an ingredient sum. Instructions, yields and retention are not in the task, and systems always output a value. |
| **JFC-Recipe** (Shirai et al., LREC 2026, pp. 6349–6360) [B39] | Japanese recipes linked to a composition database, with amount and unit converted to grams via a weight table, plus inter-annotator agreement. | A precedent for our quantity-to-grams route (R&D plan [S47]). The abstract does not mention cooking losses. |
| **NutriBench** (Hua et al., arXiv 2407.12843; "ICLR 2025" per arXiv) [B40] | 11,857 meal descriptions; LLMs estimate carbohydrates and may answer "−1" when unsure. | The only abstention seen in this theme is a bare "−1", with no evidence routing and no cooking effects. |
| **NutriMatch** (Jankelow et al., npj Digit. Public Health 2026) [B41] | Matches items across composition databases with an LLM and *imputes* missing nutrients so every item gets a complete profile. | The explicit opposite of our UNKNOWN-is-never-0 rule. A useful contrast sentence. |

**Calibrated novelty (3.4).**
- **Can claim:**
  - Retention evidence is bound to the recipe's own process event, and applying it is gated. The gates are:
    - target presence;
    - merged-lot context;
    - prior-process context.
  - Counted on the fixed sample with the AI-drafted gates: vitamin C DIRECT goes from 450 to 73. Of the 377 withheld, 346 are
    MERGED_LOT_CONTEXT, 30 PRIOR_PROCESS_CONTEXT and 1 TARGET_ABSENT (S177 census,
    `reports/step23/router_demo_census_vitc_nonBBC_1000_S177.json`). The S176 split in `reports/orchestration/S176_L-ROUTER_report.md`
    §1 (59 / 318, two gates) is superseded.
  - The contrast with [B32] (default method, 42.62 % factor coverage, silent raw fallback) and with [B41] (complete-profile
    imputation) is factual and quotable.
- **Cannot claim:**
  - More accurate nutrient values. We emit almost no numbers: only EVD lookups, and no calibrated model.
  - That the gates are correct. They are AI_DRAFTED, with a PROPOSED_PILOT floor and no human audit.
- **Needs an experiment:**
  - On the same recipes, compute (a) the Vijayakumar-style default-method retention and (b) our gated routes. Report how often they
    disagree, and where.
  - A human audit of a random sample of TARGET_ABSENT and MERGED_LOT_CONTEXT decisions, for precision.
  - Measuring retained nutrients chemically, as in [B34], is out of scope.

### 3.5 RAG with abstention, selective answering and evidence sufficiency

*Anchors (v2):* Self-RAG, CRAG, C-RAG, TRAQ, conformal factuality (Mohri & Hashimoto 2024), conformal risk control, Sufficient
Context (Joren 2025), AbstentionBench, the Wen et al. abstention survey, and the Wang et al. 2025 conflicting-evidence paper.

*Publication-status corrections:*
- **Self-RAG** is ICLR 2024 (oral) per OpenReview, so v2's "venue not verified" can be dropped.
- **CRAG** is an **arXiv preprint**: its ICLR 2025 submission was withdrawn. Cite it as arXiv 2024, which v2 already does.

| Work | What it does | What CulinaryState does differently |
|---|---|---|
| **Adaptive-RAG** (Jeong et al., NAACL 2024) [B42] | A small learned classifier routes each query to no retrieval, single-step or iterative RAG, by predicted complexity. | The closest *router architecture*, but learned and keyed to cost and complexity. Ours is rule-based, keyed to **evidence class**, with DIRECT / INTERPOLATE / SIMULATE / QUALITATIVE / ASK / ABSTAIN outcomes. |
| **Trust-Score / Trust-Align** (Song et al., ICLR 2025 oral) [B43] | A metric for grounded answers, correct refusals and citations, plus alignment that teaches the generator to refuse. | Refusal is trained *into the generator*. Ours is decided by gates over typed evidence *before* any text is generated, and the LLM may only rephrase. |
| **ClinDet-Bench** (Watanabe et al., ACL 2026 Industry, pp. 681–703) [B44] | Clinical scoring cases with missing data, split into *determinable* (the conclusion holds under every value of the missing data) and *undeterminable*. LLMs both judge too early and abstain when they need not. | Conceptually the closest to our three-valued gates: a missing condition can still allow a determinate answer. It is an LLM benchmark; we compute determinability symbolically. |
| **KnowGuard** (Dang et al., arXiv 2509.24816; ICLR 2026 poster per the OpenReview record the lane read) [B45] | Explores a medical KG for evidence *before* abstaining, instead of relying on the model's self-assessment. | Shares the "evidence before abstention" stance, but the LLM still makes the final decision. No typed evidence classes, no validity domains. |
| **UAEval4RAG** (Peng et al., ACL 2025) [B46] | A six-category taxonomy of queries a given knowledge base cannot answer, plus automatic synthesis, scored on unanswered ratio and acceptable ratio. | An evaluation template, not a system. Use it to build the H3 ABSTAIN/ASK split. |
| **Conformal-RAG** (Feng et al., SIGIR 2025 short) [B47] | Group-conditional conformal filtering of sub-claims using RAG signals. | Offers guarantees on a calibration set. We have no calibration yet; this is the template for the H3 risk–coverage curve. |
| **CLAMBER** (Zhang et al., ACL 2024) [B48]; **MediQ** (Li et al., NeurIPS 2024) [B49] | Detecting ambiguity and asking clarifying questions; an expert agent that asks follow-up questions when unconfident. | Their ASK fires on the LLM's own sense of ambiguity or low confidence. Ours fires when a gate finds a named missing slot (`CRITICAL_SLOT_MISSING`: process, target, time or temperature). |
| **Evidence Sufficiency Benchmark** (Zhang & Wu, CMC 89(1), 2026) [B50] | A five-level evidence ladder (full / partial / irrelevant / absent / conflicting). LLMs over-answer under conflicting evidence at 65–91 %. | It parallels our evidence classes but measures LLM behaviour. Lower-tier journal. |
| Also: FLARE (EMNLP 2023) [B51]; DRAGIN (ACL 2024) [B52]; SeaKR (ACL 2025) [B53]; Wen, Howe & Wang, science-QA abstention under context perturbation (Findings EMNLP 2024) [B54]; RGB negative rejection (AAAI 2024) [B55]; QuestBench (NeurIPS 2025 D&B) [B56] | | All retrieve or abstain on the LLM's internal confidence [B51–B53]; we forbid model confidence or similarity from choosing a route. [B54] shows LLM abstention is fragile under context changes, which motivates moving the decision out of the LLM. |

**Calibrated novelty (3.5).**
- **Can claim:**
  - A design contrast: abstention and asking are decided by a deterministic, auditable router over typed evidence and explicit state.
    Every ABSTAIN or ASK carries a reason code.
  - The LLM, when used, cannot choose a route or a number.
  - This differs from reflection tokens (Self-RAG), learned routers [B42], trained refusal [B43] and LLM-final abstention [B45].
  - ClinDet-Bench [B44] gives independent, peer-reviewed support for the three-valued "determinable under missing values" logic.
- **Cannot claim:**
  - Calibrated or guaranteed abstention.
  - A lower unsupported-claim rate than any RAG baseline. H3 is untested.
  - "First rule-based abstaining QA". Rule-based QA and selective prediction are old *(v2: El-Yaniv & Wiener; Geifman & El-Yaniv)*.
- **Needs an experiment:**
  - H3: unsupported-claim rate against coverage, at **matched useful coverage** (R&D plan §18), versus text RAG, a Self-RAG-style
    reflective baseline and an LLM-judge abstention baseline.
  - Build the split with UAEval4RAG categories [B46] plus a ClinDet-style determinable/undeterminable split [B44].
  - Add a conformal filter [B47] as the guarantee-bearing comparator.

### 3.6 Agent memory architectures

*Anchors:* CoALA (Sumers, Yao, Narasimhan & Griffiths) is **TMLR 2024**, confirmed by the lead on arXiv (v3 marked "TMLR camera
ready") and by the lane on OpenReview ("Accepted by TMLR") [B57]. PROV-O and PROV-DM are in *(v2)*.

| Work | What it does | What CulinaryState does differently |
|---|---|---|
| **CoALA** (TMLR 2024) [B57] | A framework that splits language-agent memory into working, episodic, semantic and procedural memory, with structured action spaces. | It gives the taxonomy. Ours is a domain instantiation by **provenance** (source / evidence / model kept apart), not by cognitive function. |
| **MemGPT** (Packer et al., arXiv 2310.08560, preprint, no venue found) [B58] | OS-style virtual context: the LLM pages memory between tiers. | Tiers are about capacity, and the LLM decides what to write. Cite as a preprint. |
| **Generative Agents** (Park et al., UIST 2023) [B59] | A memory stream plus reflections plus retrieval. | One stream mixes observations with LLM reflections. We keep evidence immutable (protected ledgers) and separate from derived state. |
| **A-MEM** (Xu et al., NeurIPS 2025) [B60]; **Mem0** (Chhikara et al., ECAI 2025) [B61] | LLM-organised notes that "evolve" by rewriting older notes; LLM add / update / delete consolidation of facts. | Memories are mutable and LLM-curated, the opposite of byte-identical evidence ledgers. |
| **MIRIX** (Wang & Chen, arXiv 2025) [B62] | Six typed memories (core, episodic, semantic, procedural, resource, knowledge vault). | The closest *typed-store* design, but typed by function. It has no model memory with validity domains and no labels on simulation runs. |
| **Eywa** (Joshi, arXiv 2605.30771, May 2026, preprint) [B63] | "Evidence before belief": immutable source records, facts derived afterwards, extracted memories validated against sources, deterministic retrieval with zero LLM calls. | **The closest memory work.** It has no event-sourced per-entity state, no model or simulation memory, and targets conversational recall. Single-author preprint. |
| **The Log is the Agent** (Nakajima, arXiv 2026) [B64]; **PROJECTMEM** (Malo & Qiu, arXiv 2026) [B65] | An append-only event log as the source of truth, with deterministic projection, replay, forking and lineage; PROJECTMEM adds a deterministic "judgment gate". | The direct analogues of our event-sourced state memory (SSOT §233.3), for general and coding agents. No evidence typing. They make "event sourcing" itself unclaimable. |
| **Agent memory survey** (Zhang et al., ACM TOIS 43(6) art. 155, 2025) [B66]; **provenance in LLM agents survey** (Wang et al., TMLR 2026) [B67] | Framing references. [B67] separates evidence that *supports* a conclusion from execution that *influences* it. | Use [B67] next to PROV-O when describing evidence packets. |

**Calibrated novelty (3.6).**
- **Can claim:**
  - Memory planes separated by **provenance class**, enforced by firewalls in code and tests: protected byte-identical ledgers,
    `Model memory ≠ Evidence memory`, and E7 never entering EVD.
  - Model memory carries validity domains, and simulation outputs are labelled ASSUMED_DEFAULT / MODEL_DERIVED.
  - In this search, no agent-memory work had a *model* plane with validity domains or labelled *simulation* runs (hypothesis).
- **Cannot claim:**
  - A new memory architecture or taxonomy (CoALA, MIRIX).
  - The "evidence before belief" principle (Eywa).
  - Event-sourced agent memory ([B64], [B65]).
- **Needs an experiment:**
  - A leakage test: show that removing the firewall lets a Layer 2 or model value reach an answer as if it were evidence (an
    injected-default canary), and that the firewall blocks it.
  - This is the memory claim's only measurable form before 25 Nov.

---

## 4. Cross-theme map: who covers which link

| Link | Closest works (this file) | Covered by any one work together with the next link? |
|---|---|---|
| L1 recipe text → events → lot state (replay) | PizzaCommonSense [B01], Bikakis [B04], SIMMER [B02], ReGraph [B08] | No: states are textual, generated or symbolic |
| L2 lot state → per-event physical conditions (stated vs assumed) | Kumbhakern [B20] (hand-encoded), Cook2LTL [B27] (symbolic T) | No: no stated/assumed split, no scale |
| L3 conditions → physical model | Digital twins [B23–B26], Feyissa & Frosch [B25] | No: inputs come from sensors or setpoints, not text |
| L4 lot + process → nutrient evidence (applicability) | Vijayakumar [B32], Li [B35], FoodBench-QA [B37] | No: default method or ingredient sum, no gating |
| L5 evidence → answer / ASK / ABSTAIN (deterministic) | Adaptive-RAG [B42], ClinDet-Bench [B44], KnowGuard [B45] | No: routing learned or decided by the LLM |
| L6 provenance-separated memory | Eywa [B63], MIRIX [B62], The Log is the Agent [B64] | No: no model or simulation plane |

The gap sentence for the report, as a **hypothesis**: *"In a targeted 2023–2026 search (Appendix A) we did not find a system that
connects L1–L5. CulinaryState is an attempt to connect them under explicit provenance and abstention rules. Whether the connection
improves answers is what H1 and H3 test."*

---

## 5. Experiments that would turn hypotheses into claims

These are ordered by value for 25 Nov; owners and steps come from the existing plan.

| # | Claim it would support | Experiment | Plan hook |
|---|---|---|---|
| E1 | Gates are correct (3.4) | A human audit of a random 50 TARGET_ABSENT and 50 MERGED_LOT_CONTEXT decisions; report precision with an exact CI | Step 23 / L-ROUTER follow-up |
| E2 | Gating changes nutrient answers vs common practice (3.4) | On the 1,000 sample, a Vijayakumar-style default-method retention against gated routes; report counts and where they disagree | new; counts only |
| E3 | Stated-condition census is right (3.3, claim 3) | L1 extraction precision and recall against P1b gold for time and temperature spans | Step 19 P1b |
| E4 | Layer 2 brackets are physically plausible (3.3) | D-VAL: bracket coverage of author-stated internal temperatures | REV-A item; Step 31 |
| E5 | Deterministic abstention lowers unsupported claims (3.5) | H3 at matched coverage against text RAG, Self-RAG-style and LLM-judge abstention; split built with UAEval4RAG + ClinDet-style | H3 prereg |
| E6 | Replay beats LLM state (3.1) | P1/P1b gold, against LLM state prediction and a Nandy-style learned tracker | Step 19, Step 35 |
| E7 | Memory firewall matters (3.6) | An injected-default canary test | Step 36 claim enforcement |

---

## 6. Corrections and notes for other files (proposed; orchestrator decides)

1. `research_bibliography_v2.md`, Self-RAG row: the venue is now verified as ICLR 2024 (oral), via OpenReview forum hSyW5go0v8.
2. CRAG (Yan et al.) stays an arXiv preprint: ICLR 2025 shows it as a withdrawn submission. Do not upgrade it to ICLR. There is
   also a separate Meta "CRAG" benchmark with the same name; do not confuse the two.
3. MemGPT has no peer-reviewed venue found (arXiv, dblp CoRR only), so cite it as a preprint.
4. R&D plan v2 [S34] ("must appear in the novelty audit") is now verified as Kümpel et al., Frontiers in Robotics and AI 12:1682031
   (2025) [B14].
5. **Terminology mismatch:** SSOT §233.7 lists five memory classes: Source, Semantic, Episode/session, Evidence, Model (simulation
   *inside* Model). The 36-step plan USP map says source / evidence / state / model / simulation (simulation separate, "F-6
   pending"). The report and slides should use one list. **Human decision.**
6. Agent-recalled numbers: none are used here. Every number in §3 comes from a source this search opened, or from a repo report
   whose path is given.

---

## 7. Bibliography (new works; verified flag)

Flags (defined in §1):
- **YES-2:** opened twice (a lane and the lead).
- **YES-1:** opened once.
- **PARTIAL:** the record was opened, but a detail is unconfirmed.

**Core** marks the 15 works proposed for the report and slides; the board asked for 10–15. Venues stated "per arXiv" or "per
OpenReview" come from the arXiv comment field or the OpenReview record, not from a proceedings page.

| # | Core | Theme | Citation | Venue / status | Identifier | Verified |
|---|---|---|---|---|---|---|
| B01 | ★ | 3.1 | Diallo A., Bikakis A., Dickens L., Hunter A., Miller R. PizzaCommonSense: A Dataset for Commonsense Reasoning about Intermediate Steps in Cooking Recipes | Findings of EMNLP 2024, pp. 12482–12496 | 2024.findings-emnlp.728; doi:10.18653/v1/2024.findings-emnlp.728 | YES-1 (ACL Anthology, two lanes) |
| B02 | ★ | 3.1 | Lu X., Zhang R.H., Zhang R. SIMMER: Benchmarking Latent Failures in LLM Executable Planning with a World Model | arXiv 2026 (v2 9 Aug 2026); "Accepted at COLM 2026" per arXiv | arXiv:2606.14574 | YES-2 (arXiv) |
| B03 | | 3.1 | Lal Y.K., Cohen V., Chambers N., Balasubramanian N., Mooney R. CaT-Bench: Benchmarking Language Model Understanding of Causal and Temporal Dependencies in Plans | EMNLP 2024, pp. 19336–19354 | 2024.emnlp-main.1077 | YES-1 (ACL Anthology) |
| B04 | | 3.1 | Bikakis A., Diallo A., Dickens L., Hunter A., Miller R. A Graphical Formalism for Commonsense Reasoning with Recipes | arXiv preprint, 2023 (v1 only) | arXiv:2306.09042 | YES-2 (arXiv) |
| B05 | | 3.1 | Zhang L., Xu H., Yang Y., et al. Causal Reasoning of Entities and Events in Procedural Texts (CREPE) | Findings of EACL 2023, pp. 415–431 | 2023.findings-eacl.31 | YES-1 |
| B06 | | 3.1 | Zhang T., Zhang L., Hou Z., et al. PROC2PDDL: Open-Domain Planning Representations from Texts | NLRSE workshop @ ACL 2024, pp. 13–24 | 2024.nlrse-1.2; arXiv:2403.00092 | YES-1 |
| B07 | | 3.1 | Wang R., Todd G., Xiao Z., et al. Can Language Models Serve as Text-Based World Simulators? | ACL 2024 (short), pp. 1–17 | 2024.acl-short.1 | YES-1 |
| B08 | | 3.1 | Liu et al. ReGraph: Learning to Generate Recipe Graphs from Food Images | arXiv preprint, Aug 2026 | arXiv:2608.06917 | YES-1 |
| B09 | | 3.1 | Nandy A., Kulkarni Y., Goyal P., Ganguly N. Order-Based Pre-training Strategies for Procedural Text Understanding | NAACL 2024 (short), pp. 821–828 | doi:10.18653/v1/2024.naacl-short.74 | YES-1 (lead, ACL Anthology); [V] in R&D plan v2 |
| B10 | | 3.1 | Kanazawa N., Kawaharazuka K., Obinata Y., Okada K., Inaba M. Real-world cooking robot system from recipes based on food state recognition using foundation models and PDDL | Advanced Robotics 38(18):1318–1334, 2024 | doi:10.1080/01691864.2024.2407136 | YES-1 (arXiv + Crossref, two lanes) |
| B11 | | 3.1 | Shirai K., Kameko H., Mori S. Towards Flow Graph Prediction of Open-Domain Procedural Texts | RepL4NLP @ ACL 2023, pp. 87–96 | 2023.repl4nlp-1.8 | YES-1 |
| B12 | | 3.1 | Wu et al. Recipe2Plan: Evaluating Planning Abilities of LLMs for Efficient and Feasible Multitasking with Time Constraints Between Actions | Findings of EMNLP 2025, pp. 4279–4301 | 2025.findings-emnlp.229 | YES-1 |
| B13 | ★ | 3.2 | Choi D., Gim M., Park D., et al. CookingSense: A Culinary Knowledgebase with Multidisciplinary Assertions | LREC-COLING 2024, pp. 3983–3996 | 2024.lrec-main.354 | YES-2 (ACL Anthology) |
| B14 | ★ | 3.2 | Kümpel M., Scheibl M., Töberg J.-P., Hassouna V., Cimiano P., Wrede B., Beetz M. Everything robots need to know about cooking actions: creating actionable knowledge graphs to support robotic meal preparation | Frontiers in Robotics and AI 12:1682031, 2025 | doi:10.3389/frobt.2025.1682031 | YES-1 (lead, publisher full text) |
| B15 | | 3.2 | Haduong N., Gao A., Smith N.A. Risks and NLP Design: A Case Study on Procedural Document QA | Findings of ACL 2023, pp. 1248–1269 | doi:10.18653/v1/2023.findings-acl.81 | YES-1 |
| B16 | | 3.2 | Mohbat F., Zaki M.J. KERL: Knowledge-Enhanced Personalized Recipe Recommendation using Large Language Models | ACL 2025, pp. 19125–19141 | doi:10.18653/v1/2025.acl-long.938 | YES-1 |
| B17 | | 3.2 | Zhang Z., Li Y., Le N.H.L., et al. NGQA: A Nutritional Graph Question Answering Benchmark for Personalized Health-aware Nutritional Reasoning | ACL 2025, pp. 5934–5966 | doi:10.18653/v1/2025.acl-long.296 | YES-1 (two lanes) |
| B18 | | 3.2 | Zhou P., Min W., Fu C., et al. FoodSky: A food-oriented large language model that can pass the chef and dietetic examinations | Patterns 6(5):101234, 2025 | doi:10.1016/j.patter.2025.101234 | YES-1 (arXiv + Crossref) |
| B19 | | 3.2 | Gupta S.K., Dey L., Das P.P., et al. Enhancing FKG.in: automating Indian food composition analysis | arXiv 2024; ICPR 2024 workshop per arXiv | arXiv:2412.05248 | YES-1 (venue PARTIAL) |
| B20 | ★ | 3.2/3.3 | Kumbhakern A., Gupta S.K., Dey L., Das P.P. Towards an Action-Centric Ontology for Cooking Procedures Using Temporal Graphs | arXiv 2025; ACM MM 2025 Multimodal Food Computing workshop per arXiv | arXiv:2509.04159; doi:10.1145/3746264.3760499 | YES-2 (arXiv; DOI not opened) |
| B21 | | 3.2 | Nadir et al. R.E.C.I.P.E.: Retrieval-Enhanced Culinary Intelligence for Problem Evaluation and Functional Substitution | Zenodo project report 2026, not peer-reviewed | doi:10.5281/zenodo.20836036 | YES-1 |
| B22 | | 3.2 | Abdur Rahman L., Papathanail I., Mougiakakou S. Introducing the Swiss Food Knowledge Graph | arXiv preprint 2025 | arXiv:2507.10156 | YES-1 |
| B23 | ★ | 3.3 | Kannapinn M., Dorer D., Schäfer M., Weeger O. Digital twins for autonomous thermal food processing: A model predictive control study with reduced-order models of augmented neural ODE type | J. Food Eng. 410:112918 (2026 issue; online Dec 2025) | doi:10.1016/j.jfoodeng.2025.112918 | YES-2 (Crossref) |
| B24 | | 3.3 | Cabeza-Gil I., Ríos-Ruiz I., Martínez M.Á., Calvo B., Grasa J. Digital twins for monitoring and predicting the cooking of food products: A case study for a French crêpe | J. Food Eng. 359:111697, 2023 | doi:10.1016/j.jfoodeng.2023.111697 | YES-1 (Crossref + OpenAlex) |
| B25 | | 3.3 | Feyissa A.H., Frosch S. An Integrated Model of Heat Transfer in Meat Products during Multistage Operations | Foods 12(18):3369, 2023 | doi:10.3390/foods12183369 | YES-1 |
| B26 | | 3.3 | Rajpal, Rajodia A., Chakravorty A. Precision cooking with 7 DOF robotic arms: integrating digital twins for nutrient-conserving food preparation | J. Food Sci. Technol., online 27 Apr 2026 | doi:10.1007/s13197-026-06673-0 | YES-1 (lane, Springer page); lead: metadata only, so details PARTIAL |
| B27 | | 3.3 | Mavrogiannis A., Mavrogiannis C., Aloimonos Y. Cook2LTL: Translating Cooking Recipes to LTL Formulae using Large Language Models | ICRA 2024, pp. 17679–17686 | doi:10.1109/ICRA57147.2024.10611086 | YES-1 |
| B28 | | 3.3 | Purlis E. Digital Twin Methodology in Food Processing: Basic Concepts and Applications | Curr. Nutr. Rep. 13(4):914–920, 2024 | doi:10.1007/s13668-024-00584-2 | YES-1 (Europe PMC) |
| B29 | | 3.3 | Gil-Gaxiola M., Caro-Hernández O., Carrazco-Escalante M., et al. Thermokinetic parameters of vitamin C and total carotenoids in carrot: Prediction and validation of their retention via 3D finite element modelling | J. Food Eng. 411:112957 (2026 issue) | doi:10.1016/j.jfoodeng.2025.112957 | PARTIAL (metadata only) |
| B30 | | 3.3 | Kato F., Hasegawa S. Interactive cooking simulator | CEA '13 (ACM), pp. 33–38, 2013 (pre-2023) | doi:10.1145/2506023.2506030 | PARTIAL (Crossref metadata) |
| B31 | ★ | 3.4 | Kalra J., Batra D., Diwan N., Bagler G. Nutritional Profile Estimation in Cooking Recipes | ICDE 2020 DECOR workshop (pre-2023 anchor) | arXiv:2004.12286 | YES-2 (arXiv; full-text statement confirmed by lead; paraphrased here) |
| B32 | ★ | 3.4 | Vijayakumar A., Dubasi H.B., Awasthi A., Jaacks L.M. Development of an Indian Food Composition Database | Curr. Dev. Nutr. 8(7):103790, 2024 | doi:10.1016/j.cdnut.2024.103790; PMC11277795 | YES-2 (Europe PMC; 42.62 % figure confirmed in full text by lead) |
| B33 | ★ | 3.4 | Yun S.-Y., Lee H.J., Lee T., et al. Application of cooked meat codes to improve the validity of nutrient content estimation in a recipe-based food ingredient database | Nutr. Res. Pract. 19(6):1002–1010, 2025 | doi:10.4162/nrp.2025.19.6.1002; PMC12688007 | YES-2 (Crossref; full-text statement confirmed by lead; paraphrased here) |
| B34 | | 3.4 | Sato Y., Inagaki R., Shimamoto K., Tsuji H. Validating nutritional values of daycare lunches using recipe calculation based on standard tables of food composition in Japan | J. Food Compos. Anal. 143:107614, 2025 | doi:10.1016/j.jfca.2025.107614 | YES-2 for the record; vitamin C figure YES-1 (lane) |
| B35 | | 3.4 | Li N., Cong L., Wang H., et al. Establishing a nutrition calculation model for catering food according to the influencing factors of energy and nutrient content in food processing | Front. Nutr. 11:1388645, 2024 | doi:10.3389/fnut.2024.1388645 | YES-1 |
| B36 | | 3.4 | Renard C.M.G.C., Brick H., Maingonnat J.-F., Kadelka C., Delchier N. Relative role of leaching and chemical degradation in the loss of water-soluble vitamins C and B9 from frozen vegetables cooked in water | LWT 180:114694, 2023 | doi:10.1016/j.lwt.2023.114694 | YES-1 (Crossref + OpenAlex) |
| B37 | ★ | 3.4 | Eftimov T., Gjorgjevikj A., Martinc M., Cenikj G., Džeroski S., Koroušič Seljak B. FoodBench-QA: Overview of the Shared Task on Grounded Food and Nutrition Question Answering | CL4Health @ LREC 2026, pp. 223–233 | 2026.cl4health-1.20; doi:10.63317/3mtt98s2wcu7 | YES-2 (ACL Anthology) |
| B38 | | 3.4 | Gjorgjevikj A., Martinc M., Cenikj G., et al. Large language models in food and nutrition science: Opportunities, challenges, and the case of FoodyLLM | Curr. Res. Food Sci. 12:101351, 2026 | doi:10.1016/j.crfs.2026.101351 | YES-1 (Crossref + repository, two lanes) |
| B39 | | 3.4 | Shirai K., Yamakata Y., Kameko H., Sunto A., Harashima J., Mori S. JFC-Recipe: A Dataset for Nutrient Estimation from Japanese User-Generated Cooking Recipes | LREC 2026, pp. 6349–6360 | 2026.lrec-1.504 | YES-1 (lead); [V] in R&D plan v2 |
| B40 | | 3.4 | Hua A., Dhaliwal M.P., Pullela L., Burke R., Qin Y. NutriBench: A Dataset for Evaluating Large Language Models on Nutrition Estimation from Meal Descriptions | arXiv; "ICLR 2025" per arXiv (proceedings page unreachable) | arXiv:2407.12843 | YES-1 (venue PARTIAL) |
| B41 | | 3.4 | Jankelow A., Godneva A., Rein M., et al. NutriMatch: harmonizing food composition databases with large language models for enhanced nutritional prediction | npj Digit. Public Health 1:1, 2026 | doi:10.1038/s44482-025-00001-7 | YES-1 |
| B42 | ★ | 3.5 | Jeong S., Baek J., Cho S., Hwang S.J., Park J. Adaptive-RAG: Learning to Adapt Retrieval-Augmented LLMs through Question Complexity | NAACL 2024, pp. 7036–7050 | 2024.naacl-long.389 | YES-2 (ACL Anthology) |
| B43 | ★ | 3.5 | Song M., Sim S.H., Bhardwaj R., Chieu H.L., et al. Measuring and Enhancing Trustworthiness of LLMs in RAG through Grounded Attributions and Learning to Refuse | ICLR 2025 (oral) per OpenReview | arXiv:2409.11242; OR Iyrtb9EJBp | YES-1 (OpenReview API + arXiv) |
| B44 | ★ | 3.5 | Watanabe Y., Kobashi Y., Kojima T., Iwasawa Y., Okuno Y., Matsuo Y. ClinDet-Bench: Beyond Abstention, Evaluating Judgment Determinability of LLMs in Clinical Decision-Making | ACL 2026 Industry Track, pp. 681–703 | 2026.acl-industry.47; arXiv:2602.22771 | YES-2 (ACL Anthology) |
| B45 | | 3.5 | Dang X., Chen K., Su X., et al. KnowGuard: Knowledge-Driven Abstention for Multi-Round Clinical Reasoning | ICLR 2026 poster per OpenReview (lane); arXiv shows no venue | arXiv:2509.24816; OR gQRefH8upx | YES-2 for the record; venue YES-1 |
| B46 | | 3.5 | Peng X., Choubey P.K., Xiong C., Wu C.-S. Unanswerability Evaluation for Retrieval Augmented Generation | ACL 2025, pp. 8452–8472 | 2025.acl-long.415 | YES-1 |
| B47 | | 3.5 | Feng N., Sui Y., Hou S., Cresswell J.C., Wu G. Response Quality Assessment for Retrieval-Augmented Generation via Conditional Conformal Factuality | SIGIR 2025 (short), pp. 2832–2836 | doi:10.1145/3726302.3730244 | YES-1 (Crossref) |
| B48 | | 3.5 | Zhang T., Qin P., Deng Y., et al. CLAMBER: A Benchmark of Identifying and Clarifying Ambiguous Information Needs in LLMs | ACL 2024, pp. 10746–10766 | 2024.acl-long.578 | YES-1 |
| B49 | | 3.5 | Li S.S., Balachandran V., Feng S., et al. MediQ: Question-Asking LLMs and a Benchmark for Reliable Interactive Clinical Reasoning | NeurIPS 2024 (poster) per OpenReview | arXiv:2406.00922; OR W4pIBQ7bAI | YES-1 |
| B50 | | 3.5 | Zhang H., Wu W. Do LLMs Know When Evidence is Insufficient? An Evidence Sufficiency Benchmark for Answer-Abstention Calibration in RAG | Computers, Materials & Continua 89(1), 2026 | doi:10.32604/cmc.2026.086343 | YES-2 (publisher page; Crossref) |
| B51 | | 3.5 | Jiang Z., Xu F.F., Gao L., et al. Active Retrieval Augmented Generation (FLARE) | EMNLP 2023, pp. 7969–7992 | 2023.emnlp-main.495 | YES-1 |
| B52 | | 3.5 | Su W., Tang Y., Ai Q., Wu Z., Liu Y. DRAGIN: Dynamic Retrieval Augmented Generation based on the Real-time Information Needs of LLMs | ACL 2024, pp. 12991–13013 | 2024.acl-long.702 | YES-1 |
| B53 | | 3.5 | Yao Z., Qi W., Pan L., et al. SeaKR: Self-aware Knowledge Retrieval for Adaptive Retrieval Augmented Generation | ACL 2025, pp. 27022–27043 | 2025.acl-long.1312 | YES-1 |
| B54 | | 3.5 | Wen B., Howe B., Wang L.L. Characterizing LLM Abstention Behavior in Science QA with Context Perturbations | Findings of EMNLP 2024, pp. 3437–3450 | 2024.findings-emnlp.197 | YES-1 |
| B55 | | 3.5 | Chen J., Lin H., Han X., Sun L. Benchmarking Large Language Models in Retrieval-Augmented Generation (RGB) | AAAI 2024, 38(16):17754–17762 | doi:10.1609/aaai.v38i16.29728 | YES-1 (Crossref) |
| B56 | | 3.5 | Li B.Z., Kim B., Wang Z. QuestBench: Can LLMs ask the right question to acquire information in reasoning tasks? | NeurIPS 2025 Datasets & Benchmarks per arXiv journal-ref + OpenReview | arXiv:2503.22674 | YES-1 |
| B57 | ★ | 3.6 | Sumers T.R., Yao S., Narasimhan K., Griffiths T.L. Cognitive Architectures for Language Agents (CoALA) | TMLR 2024 | arXiv:2309.02427 (v3 = TMLR camera-ready); OR 1i6ZCvflQJ | YES-2 (arXiv by lead; OpenReview by lane) |
| B58 | | 3.6 | Packer C., Wooders S., Lin K., et al. MemGPT: Towards LLMs as Operating Systems | arXiv preprint 2023 (v2 Feb 2024); no venue found | arXiv:2310.08560 | YES-1 |
| B59 | | 3.6 | Park J.S., O'Brien J.C., Cai C.J., Morris M.R., Liang P., Bernstein M.S. Generative Agents: Interactive Simulacra of Human Behavior | UIST 2023, art. 2 | doi:10.1145/3586183.3606763 | YES-1 (Crossref) |
| B60 | | 3.6 | Xu W., Liang Z., Mei K., et al. A-MEM: Agentic Memory for LLM Agents | NeurIPS 2025 (poster) per OpenReview | arXiv:2502.12110; OR FiM0M8gcct | YES-1 |
| B61 | | 3.6 | Chhikara P., Khant D., Aryan S., Singh T., Yadav D. Mem0: Building Production-Ready AI Agents with Scalable Long-Term Memory | ECAI 2025 (FAIA) | doi:10.3233/FAIA251160 | YES-2 (Crossref) |
| B62 | | 3.6 | Wang Y., Chen X. MIRIX: Multi-Agent Memory System for LLM-Based Agents | arXiv preprint 2025 | arXiv:2507.07957 | YES-1 |
| B63 | ★ | 3.6 | Joshi R. Eywa: Provenance-Grounded Long-Term Memory for AI Agents | arXiv preprint, 29 May 2026 (v1; no venue) | arXiv:2605.30771 | YES-2 (arXiv) |
| B64 | | 3.6 | Nakajima Y. The Log is the Agent: Event-Sourced Reactive Graphs for Auditable, Forkable Agentic Systems | arXiv preprint, May 2026 | arXiv:2605.21997 | YES-2 (arXiv) |
| B65 | | 3.6 | Malo, Qiu. PROJECTMEM: A Local-First, Event-Sourced Memory and Judgment Layer for AI Coding Agents | arXiv preprint 2026 (v2 30 Sep 2026) | arXiv:2606.12329 | YES-1 |
| B66 | | 3.6 | Zhang Z., Dai Q., Bo X., Ma C., et al. A Survey on the Memory Mechanism of Large Language Model-based Agents | ACM TOIS 43(6), art. 155, 2025 | doi:10.1145/3748302 | YES-1 (Crossref + dblp) |
| B67 | | 3.6 | Wang et al. From Agent Traces to Trust: A Survey of Evidence Tracing and Execution Provenance in LLM Agents | TMLR 2026 per OpenReview | arXiv:2606.04990; OR iwYk6keMAM | YES-1 |

**Seen but not cited** (not opened, or too peripheral):
- **Lane one-line mentions, not core:** FABLE, ProPara-CRTS, Li/Guo/Andreas ICML 2025, Diallo 2024 recipe-graph learning,
  Takebayashi 2025, Srihari 2025, FoodGuardBench, FoodOntoRAG, Pan 2026 molecule–food benchmark, Perrignon 2026, CookBench 2025,
  Patzer 2026, Ispirova 2024 MsGEN, Cao 2026, Izzard 2026, Abstain-R1, Abdaljalil 2026, SURE-RAG, Tree of Clarifications, MIRAGE,
  Yadkori 2024, Cherian 2024, LongMemEval, Pink 2025, Hu 2025, Du 2025, PlugMem, FoodGPT (Qi 2023, a technical report with no
  results), MemoryBank (AAAI 2024).
- **Not opened** (do not cite): DietQA's quoted claim that it ignores cooking method (MDPI returned 403), MedAbstain, HealthContradict,
  NutriRAG, and arXiv 2511.17908, 2512.15068 and 2605.05244.

---

## Appendix A: searches that found nothing for the combined claim

These are the queries run by the four agents that returned nothing joining two or more links of §4. They are listed so that a reader
can judge how far the negative claims reach.

- Recipe text + physics:
  - "cooking process simulation from recipe text temperature time ingredient state"
  - "recipe instructions physics-based cooking simulation heat transfer per step"
  - "digital twin cooking recipe instructions heat transfer core temperature simulation from recipe steps" (only sensor-driven twins)
  - "recipe instructions to thermal history simulation nutrient retention kinetic model automatic pipeline"
  - "computational cooking OR in silico cooking recipe simulation physical model food"
  - "recipe flow graph simulation heating ingredients temperature estimation"
  - "LLM cooking appliance generate oven program from recipe text" (patents and one thesis only)
  - "physics-informed neural network meat cooking core temperature prediction 2024"
  - "digital twin frying OR air fryer OR sous vide"
- State + food-science QA:
  - "recipe state tracking food science question answering LLM"
  - "neuro-symbolic recipe execution simulation ingredient state graph physical properties"
  - "process-aware food question answering cooking method effect nutrient LLM knowledge graph"
  - "Maillard reaction prediction from recipe text cooking conditions"
  - "recipe text to chemical physical transformations denaturation gelatinization"
  - "event sourcing recipe steps replay ingredient state graph" (software event sourcing only)
- Nutrients + process:
  - "automatically assign nutrient retention factors cooking method extracted from recipe instructions NLP"
  - "cooking method aware nutrient estimation recipes deep learning retention factors recipe text"
  - "LLM nutrition estimation abstain uncertainty cooking method retention factors"
  - "LLM recipe nutrient estimation USDA food composition mapping retention factors cooking yield"
- Router and abstention:
  - "deterministic rule-based router abstention evidence gating LLM scientific question answering abstain ask clarify measured value"
  - "LLM question answering evidence hierarchy measured value interpolate simulate model validity domain abstain router"
  - "Kleene three-valued logic abstention gate LLM pipeline"
  - "retrieval-augmented generation nutrition food composition question answering abstain grounded LLM 2025"
  - "food question answering evidence-grounded abstain insufficient evidence nutrition LLM selective answering"
- Memory:
  - venue lookups for Zep, Eywa, The Log is the Agent, Agent Zero Memory and SURE-RAG (none found).
  - Searches for agent memory "separated by provenance (source / evidence / state / model / simulation)" found Eywa, MIRIX and Agent
    Zero Memory, but none with model or simulation planes.

## S178 FIX-GOV edits (2026-11-09)

Edited by the S178 FIX-GOV lane after the GOV review (finding GOV-9). The edits change wording and counts only; no novelty statement was added:
- Claim 2 heading "(measured)" became "(AI-gated counts on a fixed sample; gates unaudited)", and claim 3 heading "measured at scale (measured)" became "at scale (census counts)". Claim 3 gained the full non-BBC v04 shares.
- The 450 to 73 split is now quoted from the S177 1,000-sample census (three gates: 346 / 30 / 1) in claim 2 and in section 3.4. The S176 split (59 / 318) is marked superseded.
- Section 3.1 "Cannot claim" gained one sentence: extraction quality is unmeasured against gold (07.A FAILED; D-074 R1 4/60).
