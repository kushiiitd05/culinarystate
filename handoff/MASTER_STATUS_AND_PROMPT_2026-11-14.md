# CulinaryState — master status, analysis and prompts (14 Nov 2026)

One file to hand to any LLM or person. Part A is the full status; Part B analyses the UNKNOWN cells and how (and how not) to fill them with LLM / embedding support; Part C is a master prompt asking "what should be done next"; Part D is a master research prompt. Every number below comes from a committed artifact on branch `kush/s179-finish-fixes` of `kushiiitd05/culinarystate` (paths given). Labels on almost everything: AI_PRECHECKED · NON_CITABLE · NO_HUMAN_SIGNOFF_D085 unless a human decision is named.

---

## PART A — Status

### A1. The project in one paragraph
CulinaryState (Group 17: Kush Tokas, Parv Goyal; IIIT Delhi; presentation 25–26 Nov 2026) asks, per SSOT v15 §5.2: *can explicit modelling of food-state transitions and process-induced effects improve retrieval-augmented culinary guidance?* The system parses recipe steps into events that consume and produce ingredient lots, replays them as a state graph, binds stated cooking conditions (temperature, time, medium…) and physics scenarios to each heat event, and routes every ingredient × process to measured evidence (EVD retention rows), a physical formula, or UNKNOWN with a reason — then answers questions with citations or abstains.

### A2. What is LOCKED (frozen) and what is not — the source of the confusion
You did lock the best models and evaluation assets and moved on; that was correct. What was *not* done is wiring the locked NER into the step parser.

| Asset | Locked? | Evidence |
|---|---|---|
| NER v1 = DeBERTa-base + CRF (ckpt `ckpt_tasteset_base_crf_s1.pt`, sha256 582c056a…, on vinayak) | **Locked** (TEST evaluated once after freeze) | `reports/ner/culinaryner_kf_final_report.md`: TASTEset TEST micro F1 0.937; RecipeDB3 their protocol macro 0.9557 vs their 0.9543, clean grouped split 0.9504; verdict "strong system contribution without benchmark superiority" |
| Challengers (DeBERTa-v3-large+CRF, CRF top-k, Tev1-4B review head) | Tried, **not promoted** | tie ΔF1 +0.000; top-5 oracle +1.5 pp only; Tev review AUROC 0.55 vs 0.87 |
| Linker = BGE retrieval top-1 | **Locked** (D3 closeout) | `reports/ner_v2/culinary_link_decision_closeout.md`: Acc@1 0.881 on 430 fresh double-annotated items; Tev1-4B 0.872, Nimble 0.881, distilled CD-L2 0.862 rejected |
| Risk router on NER spans | Locked | accepts 59–72 % of spans at ≈2 % error |
| EVD ledger (17,978 ACTIVE rows; USDA R6, Bognár 2002, Phenol-Explorer 3.6) + 15A-BOOT freeze + 15a.R seal | **Locked** | `registry/freezes/15A-BOOT-2026-11-08.json`; seal 6/6 PASS `reports/s179/seal_integrity_check_S179_2026-11-13.json` |
| D5 benchmark (74 questions) + ladder B0–B7 results | **Locked** (D-090, D-092) | H1 RULE_NOT_MET, H3 RULE_NOT_MET |
| AA (vitamin C) Model A fit | **Locked** before SIM-VAL | Ea 64.4 kJ/mol, 7 rows, 2 papers, NOT_VALIDATED (`reports/step10/aa_pilot_model_a_fit_D085.json`) |
| qwen2.5:7b-instruct digest 845dbda0, prompt registry bc5766b7 | Pinned | RUN-S179-PIN-001 |
| Protected: EVD/COND/SRC/MEAS/SNAP rows, `grammar.py`, frozen scorers/preregs | Protected | — |
| **Step parser = Rung A (rules + lexicon)** | Current, **not** NER-based | plan step 17c "Rung B: frozen NER/linker reuse" never integrated into step parsing |
| Physics v06, router 0.4.1, strict-v3 demo | Current versions (re-runnable, not frozen) | — |

### A3. SSOT hypotheses and proposal deliverables
| ID | SSOT question | Status |
|---|---|---|
| H1 / RQ1 | state-aware beats text/RAG on current-state & next-action | tested, **RULE_NOT_MET** (B4 = B1 = B2 = 0.25, n = 24, AI-drafted gold; under-powered) |
| H2 / RQ2 | process-effect grounding helps transformation questions | diagnostic only (29-diag); full test not run (H8-02) |
| H3 / RQ3 | user constraints raise feasible-action rate | not run (H8-03) |
| H4 / RQ4 | state-distance reasoning improves recovery | not run (H8-03) |
| H5 / RQ5 | selective routing keeps quality, cuts calls | not run |
| Proposal H3 | abstention lowers unsupported claims | tested, **RULE_NOT_MET** (sign test 16–0 but P3 abstention 0/10 vs 3/10) |

| Deliverable | Status |
|---|---|
| D1 state + evidence dataset | full-corpus state dataset now filled (A6) — partial vs plan acceptance |
| D2 learned transition model | diagnostic only (29-diag, paired vs D0) |
| D3 state-graph engine + gold | built; gold 7 (P1-A, human-accepted AI drafts, not blind) + 40 dev |
| D4 evidence-aware retrieval with abstention | core built; strict-v3 demo 1,000-call audit 0 violations |
| D5 benchmark + ladder | run; H1/H3 rules not met |

### A4. 36-step plan — gate-by-gate audit (269 clauses)
`reports/orchestration/step_gate_audit_36_2026-11-13.{csv,md}`. Each pre-registered pass-gate clause checked against an existing file.

**Steps:** 0 COMPLETE · 2 run with recorded gate failure (07 condition audit κ = 0.0; 08 lineage G08-3) · 18 PARTIAL (01, 02, 04, 05, 09, 10, 12, 13, 16, 17, 18, 19, 21, 23, 24, 26, 29, 36) · 7 NOT_STARTED (03, 06, 11, 14, 22, 25, 35) · 5 BLOCKED (15, 27, 30, 31, 32; Step-07 failure keeps 29–33 gates closed; 27 has 0 eligible SIM-VAL rows) · 4 CUT (20, 28, 33, 34; H8 register D-089).
**Clauses:** 67 MET · 12 MET_AI_DELEGATED · 9 FAILED_RECORDED · 116 NOT_MET · 36 NOT_EVIDENCED · 29 N/A.
Notable audit findings: most declared output paths never created (work lives under other paths); Step 10 fit used AI_PRECHECKED rows (floor rule "no unverified extraction in calibration" breached, disclosed); router rerun not byte-identical (`gates` key); Step 36 G36-B needs a locked ≥240-item double-labelled tier (D5 has 74).

### A5. Board (252 items, 51 moved after the talk)
MUST 52 / 84 done · SHOULD 89 / 117 in scope done. Open MUST split: 12 author edits (human), 10 data-limited or partial, 7 not run / deferred, 3 calendar.

### A6. Full-corpus results, 13–14 Nov (612,782 recipes)
| Lane | Result | Artifact |
|---|---|---|
| Process → state-change map | 9,470,190 step events, 0 exceptions; Merge 24 %→10 % and Transform 48 %→76 % from first to last step; heat peaks at start and end | `reports/s179/process_state_map_full_2026-11-13.json` |
| Event typing | D-097 structural: pooled P 0.52–0.62; D-102 process-aware (post-hoc): P1-A P 0.74 / R 0.72; Transfer/Reserve now typed | `reports/s179/d10{97,2}_*` |
| **State dataset fill (D-110)** | **9,470,190 rows, 0 exceptions; 1,746,405 heat rows (18.4 %)**; every cell value+basis or UNKNOWN+reason | `reports/s179/state_dataset_fill_full_2026-11-14.json` |
| Effect map, 224 EVD targets | 600,848 non-BBC recipes, 4,118 (target × ingredient × process) rows with EVD values; 29,154 recipes (4.9 %) get ≥1 evidence-backed mineral value; biggest rows potato × boil | `reports/s179/effect_map_224_nonBBC_2026-11-14.json` |
| Vitamin-C router | 36.36 M ingredient items: DIRECT 31,278 (0.09 %), SIMULATE 0, rest UNKNOWN (`NO_FORM`, `PARAM_UNCONFIRMABLE`, …) | `reports/step23/router_demo_census_vitc_*_S179b.json` |
| AA formula per event (D-104 → D-106) | 826 heat events in domain (liquid acidic fruit, 60–100 °C, no water contact); medians are scenario-default driven | `reports/s179/formula_census_aa_*_D106_2026-11-13.json` |
| SSOT §238 column map | 146 / 210 fields have a full-corpus producer; 13 none (texture, colour, aw, pH, servings…); 19 deferred; 16 cut | `reports/s179/ssot_column_map_v2_2026-11-13.csv` |
| NER vs Rung A lexicon | frozen-ckpt FOOD spans covered by lexicon 98.4 / 95.5 / 94.6 % (Food.com / Wikibooks / TASTEset); top misses are brands (cool whip, splenda) | `reports/s179/ner_vs_runga_agreement_S179_2026-11-13.json` |
| ING attributes (AI) | qwen 7B and 72B drafts for 2,048 ingredients; agreement only 44–60 % per field; 7B errors (tomato "not acidic"); both say lemon "liquid" | `registry/ing_attributes_ai_draft{,_72b}_v1.csv` |
| 29-diag paired vs D0 | USDA rungs beat D0 on every split; Phenol-Explorer rungs mostly worse (negative kept) | `reports/step29/diag/paired_vs_d0_S179_2026-11-13.json` |

### A7. Fill rates of the State columns (heat rows unless noted)
| Column | Filled | Main UNKNOWN reason |
|---|---|---|
| state type (all rows) | 87.3 % | UNMAPPED_STRUCTURE 1.20 M (parallel 2→2 events, 0-consume events) |
| process (all rows) | 99.2 % | NO_PROC 80 k |
| medium | 53.8 % | NO_MEDIUM_IN_PROCESS_MAP 0.81 M (generic "cook/heat") |
| temperature stated | 16.5 % | NO_TEMPERATURE_STATED 1.46 M |
| duration stated | 28.2 % | NO_DURATION_STATED 1.25 M |
| matrix class | 33.2 % | MULTIPLE_FOOD_GROUPS 0.65 M, NO_FOOD_GROUP 0.51 M |
| lid | 8.8 % | NO_LID_CUE |
| piece size | 9.7 % | NO_CUT_HISTORY |
| food temperature (scenario default) | 46.4 % | SCENARIO_UNKNOWN 0.86 M (mostly because medium is unknown) |
| AA retention (formula) | 826 events | MATRIX_NOT_ACIDIC_FRUIT 1.72 M |
| ingredient linked (router items) | 97.1 % | 1.01 M unlinked items |
| pH, water activity, texture, colour | 0 % | no producer |
| mass (g) per line | Wikibooks 59 %, TASTEset 64 %, **Food.com 0 %** (units dropped at source) | — |

### A8. Worked example — the four tomato variants (real pipeline output, 14 Nov)
| Variant (self-written text) | Events / state change | Lycopene | Vitamin C |
|---|---|---|---|
| A boil tomatoes 20 min | boil → Transform | DIRECT 95 % (EVD) | UNKNOWN (no tomato × boil row) |
| B + salt, same sentence | boil, 2 lots in → 2 out → unmapped | still 95 % — salt changes nothing | UNKNOWN |
| C + salt + vinegar, mixed then boiled | mix → **"salt" parsed as the verb season** → Merge(tomato, vinegar) → boil | abstains: `MERGED_LOT_CONTEXT` (tomato-alone evidence not transferred to a vinegar mixture) | UNKNOWN |
| D + salt + oil + vinegar | mix → season ("salt") → **brush ("oil")** → Merge → boil | abstains | UNKNOWN |

So: the **structure** distinguishes the variants and the evidence layer correctly refuses to reuse tomato-alone values for a mixture. The **chemistry** (pH from vinegar, salt %, fat % / lycopene bioavailability, pH-dependent vitamin-C loss) is **not represented**, and the step parser has a verb/ingredient ambiguity bug ("salt", "oil" read as actions inside ingredient lists).

### A9. Parv's reduced-submission candidate (13 Nov)
`reports/final/submission_candidate_2026-11-13/` (README, allowlist, build manifest): draft report + 13-slide deck, technical addenda, figures, verification; **DRAFT_CANDIDATE_NOT_AUTHOR_APPROVED**. Done there: 07.A-R1 paired AI review (497/900 axis-code matches; result NOT_COUNTED for human gating, v4 FAIL unchanged); CAL paired AI review (16/16 numeric spans match; Model A still not validated); 8-case strict-v3 backend demo; full suite 8,182 passed. Not in it yet: the 13–14 Nov full-corpus results (A6). His remaining actions: (1) Kush's real review entry; (2) D-098 ablations, frozen-7B H1/B7 regeneration, source-held-out retrieval, versioned D5 re-emission; (3) author integration + person-only facts; (4) decide AAK-04/10 (usable, not acquired), AAK-02/08 unconfirmed, AAK-05 excluded (NC-SA); (5) rebuild candidate on the exact revision; (6) PR #11/#12, MPU, 21 Nov freeze, 24 Nov rehearsal.

### A10. Our plan (`handoff/PLAN_2026-11-14_finalise_and_deploy.md`) — completion
| Plan part | Status |
|---|---|
| §1 scope freeze D-112 | drafted, awaiting Kush |
| §2 lanes: L2 fill, L4 non-BBC, 72B attributes | **done** |
| §2 L4 BBC leg, D-108 lot formula, formula-vs-EVD check, candidate v2 | open |
| §3 D-098 ablations, H1/B7 regen, source-held-out retrieval, router replay gap | open |
| §4 cheap gate closes (steps 01, 02, 08, 14, 36) | open |
| §5 SSOT crosswalk + state-representation figure + worked example | worked example done (A8); figure/crosswalk open |
| §6 deployed app | design ready; needs `vercel login` and architecture choice A (Vercel UI + container backend) or B (Vercel only, slim data pack; ledgers ≈300 MB > 250 MB limit) |
| new: verb/ingredient parser bug | found 14 Nov; not yet measured or fixed |
| new: D-116 composition-aware lot state (pH, salt %, fat %) | proposed |

### A11. Infrastructure
vinayak (2× A100 40 GB, 128 cores): system ollama runs **CPU-only**; a user-space ollama on GPU works (ports 11500/11501; 7B and 72B tested). manjot (A100s shared with another user's FedLLM job; disk 93 % full, ≈746 GB free). Mac 8 GB: BBC-only work (D-003). VPN drops intermittently; long jobs use setsid/nohup.

---

## PART B — UNKNOWN cells: what can be filled, how, and what must stay UNKNOWN

### B1. Laws that do not move
No invented scientific values; UNKNOWN is a valid answer; AI output is AI_DRAFTED until verified; agreement of two AI models is triage, not validation; scenario defaults are labelled SCENARIO_DEFAULT and never shown as observations; BBC and paper text never leave the Mac or go to an external service.

### B2. Column-by-column
| Gap | Can it be filled? | Method | Label |
|---|---|---|---|
| state type UNMAPPED 1.2 M | **Yes, partly** | (1) structural rules for parallel 2→2 events (split into per-lot Transforms); (2) put frozen NER FOOD spans into step parsing (Rung B) to stop "salt/oil as verb"; (3) optional qwen-72B typing on hard events, scored against the 47 gold recipes before any use | DERIVED / AI_DRAFTED |
| medium unknown 0.81 M | **Yes, mostly** | extend `process_medium_map` for generic processes using context cues (pan, pot, oven, tray) — deterministic rules; LLM may draft map rows, human-reviewed; this also unlocks scenario food-T for most of the 0.86 M SCENARIO_UNKNOWN | DERIVED (rules) |
| temperature / duration not stated (83 % / 72 %) | **No as text**; yes as scenario | the text does not say it. Keep TEXT UNKNOWN; scenario defaults (process-typical, GENTLE/TYPICAL/INTENSE bracket) already exist and should cover more once medium improves | SCENARIO_DEFAULT |
| matrix class "multiple groups" | Yes, by design change | compute per **lot**, not per event (D-116) | DERIVED |
| pH, salt %, fat % | **Yes, as scenario**, with a sourced table | ingredient pH table from a public, citable source (e.g. US FDA/USDA approximate-pH lists — check licence), SR composition for NaCl and fat × parsed quantities; lot value = mass-weighted (or "acidic present" flag when masses unknown) | SCENARIO (sourced constants) |
| water activity, texture, colour | **No** (no producer, no defensible constants) | keep UNKNOWN; name as limitation | — |
| Food.com mass 0 % | **No** at line level | units dropped at source; Food.com's own per-recipe nutrition columns (if present in `recipes.parquet`) could give recipe-level sodium / fat as a separate, labelled field — check first | SOURCE_RECIPE_LEVEL |
| 1.01 M unlinked ingredient items | **Yes, partly** | frozen BGE linker (embeddings) as fallback for lexicon misses; accept only above the frozen operating point; queue the rest | AI_LINKED |
| EVD DIRECT 0.09 % (vitamin C) | **No by AI** | coverage is limited by measured evidence; only new licensed sources add rows (AAK-04/10, more USDA/Phenol-Explorer tables) | — |
| SIMULATE 0 / formula reach 826 | Only with data | lot-level gate (D-108) raises reach; a pH-aware vitamin-C formula needs ≥2 papers with pH-varied kinetic series | RESEARCH_ONLY |

### B3. Where LLMs, embeddings and APIs fit (and where they must not)
| Role | Allowed? | Design |
|---|---|---|
| Extraction drafting (conditions, quantities, event typing) | Yes, as AI_DRAFTED | JSON-mode, temperature 0, pinned digest, prompt registered first; **every value must string-match a source span** (validator rejects otherwise — Step 17a invented-value audit exists); scored on gold before deployment |
| Formatting / schema conversion | Yes | deterministic JSON schemas; validators decide, not the model |
| Linking / normalisation | Yes | embeddings for candidate retrieval (frozen BGE); LLM rerank was tested and rejected (Tev1-4B) — do not reintroduce without a new sealed eval |
| Attribute drafting (form, acidity, vitamin-C bearing) | Yes, as triage | two models (7B, 72B) + agreement; only agreed values used, labelled; human spot check of a sample |
| Review assistance | Yes | produce queues with spans and reasons for humans |
| Filling scientific values (retention, k, pH of a lot) | **No** | only from EVD, a frozen formula, or a cited constant table |
| External hosted APIs (Claude/OpenAI) | Only for public or self-written text | never BBC, paper full text or private sheets; local GPU ollama is the default |
| Embedding index for evidence retrieval (D4) | Yes | existing retriever; dense similarity ≠ experimental compatibility (Step 25 ruling), so it ranks, it does not decide |

Infrastructure for this: user-space GPU ollama on vinayak (7B ≈ 13 s / 25 items; 72B ≈ 115 s / 25 items on 2× A100), batch scripts with per-row parse status, outputs as AI_DRAFTED registries plus agreement tables.

---

## PART C — Master prompt: "what should be done next?"

> **Role.** You are a senior research advisor and technical lead for an academic computational-gastronomy project with a hard deadline (code/result freeze 21 Nov 2026, rehearsal 24 Nov, presentation 25–26 Nov). You are rigorous about scientific claims and pragmatic about scope.
>
> **Context.** Read the attached document "CulinaryState — master status, analysis and prompts (14 Nov 2026)" Parts A and B in full. Treat its numbers as the current record. Laws you must respect: no invented scientific values; UNKNOWN is valid; AI output is AI_DRAFTED until verified; agreement between AI models is not validation; negative results stay visible; frozen assets (NER v1, BGE linker, EVD/15a freeze, D5 benchmark and results, AA Model A) are not retuned; third-party text never goes to external services.
>
> **Questions — answer each, numbered:**
> 1. Is the status assessment internally consistent? Flag any number or claim that looks wrong or over-stated.
> 2. Is a **reduced, honestly labelled submission** defensible against SSOT v15 and the proposal? Write the exact scope statement you would freeze (what is claimed, what is a limitation, what is out of scope).
> 3. Given 6 working days and two people plus an AI agent with 2 GPU servers, produce a **prioritised task list** (must / should / skip) with effort estimates, choosing among: verb/ingredient parser fix with NER in step parsing; process-medium map extension; lot-level composition state (pH, salt %, fat %); lot-level vitamin-C formula; formula-vs-EVD external check; D-098 ablations; frozen-7B H1/B7 regeneration; cheap gate closes; deployed demo app (Vercel UI + container backend vs Vercel-only); author report/deck integration.
> 4. For the **state-aware representation**: is the five-layer design (lots → events → state change → physical state → evidence state, every cell value+basis or UNKNOWN+reason) a sound and presentable contribution? What is the single most convincing figure or demo for an examiner? How should the tomato example (A8) be presented — including its failures?
> 5. For **UNKNOWN filling**: review Part B. Which fills are scientifically acceptable, which are risky, and what label must each carry? Propose the minimum validation (sample size, metric) before each fill is shown.
> 6. For **LLM / embedding support**: is the Part B3 design correct? What would you change? What is the cheapest experiment that shows LLM-drafted extraction is safe to use (with grounding validators) on this corpus?
> 7. For the **NER**: our model ties the lab's published RecipeDB3 result rather than beating it. How should this be framed? Is integrating it into step parsing worth doing before the freeze?
> 8. Top 5 **risks** to the presentation and how to mitigate each.
> 9. A **day-by-day plan** 15–25 Nov, split agent / Kush / Parv.
>
> **Output format.** Markdown. Numbered answers 1–9. Tables where useful. Every recommendation names its acceptance check. Say "insufficient information" rather than guess. Keep it under 2,500 words.

---

## PART D — Master research prompt (literature and methods)

> **Role.** You are a research assistant doing a focused, citation-backed survey for a computational-gastronomy system that models food-state transitions during cooking and their effects on nutrients. Prefer primary sources (peer-reviewed papers, official datasets); give full citations with DOI/URL, year, and licence/access status where data are involved. Mark anything you cannot verify as UNVERIFIED. Do not invent numbers.
>
> **Research questions:**
> 1. **State representation of procedural text (SOTA).** Entity/state tracking in procedural text and recipes: ProPara and successors, recipe flow graphs (e.g. Yamakata et al.), cooking-procedure graph parsers, LLM-based entity-state tracking. What representations (lots/entities, actions, state attributes) and evaluation metrics are standard? Where would a lot-based event-sourced graph with typed state changes (Merge / Split / Transform / Transfer / Reserve / Discard) sit?
> 2. **Recipe NER and linking (SOTA).** Best reported results on TASTEset and RecipeDB-style corpora (F1, protocols, splits); food entity linking to ontologies (FoodOn, FoodKG). Is "tie with published SOTA under a clean grouped split + calibrated risk routing" a recognised contribution?
> 3. **Condition-dependent nutrient kinetics.** Ascorbic acid thermal degradation vs pH, oxygen and matrix (first-order / Weibull, Arrhenius parameters with pH terms); lycopene thermal stability, isomerisation and bioaccessibility with oil; effects of salt and acid on vegetable nutrient retention and leaching during boiling. For each: open-access sources with **raw time-course data** (needed for calibration) and their licences.
> 4. **Retention-factor databases.** USDA retention factors (Release 6) coverage and successors; Bognár 2002; Phenol-Explorer retention; any newer open retention or processing-effect datasets (EU, FAO/INFOODS) with licence terms.
> 5. **Food pH / composition constants.** Citable, redistributable tables of approximate food pH and of salt and fat content (USDA FoodData Central, FDA lists) suitable for deriving lot-level pH / salt % / fat % in recipes; known pitfalls of mixing-rule estimates for pH.
> 6. **LLM-assisted information extraction with grounding.** Methods that force span-grounded extraction (citation/attribution checks, constrained decoding, validators), measured error rates for numeric extraction from scientific papers, and accepted human-verification sample sizes.
> 7. **Evaluation design under small gold.** How to report a state-aware system when the hypothesis test is under-powered (n = 24): equivalence/power analysis, what can honestly be concluded, recommended minimum benchmark sizes.
> 8. **Demo deployment.** Practical patterns for deploying a Python research backend (≈300 MB data) with a web UI: Vercel serverless limits vs container hosts (Hugging Face Spaces, Render, Railway), cold start, free-tier limits (state dates checked).
>
> **Output format.** One section per question: 5–10 key sources (citation, one-line finding, data/licence note), a short synthesis, and "implications for CulinaryState" (concrete, testable). End with a ranked list of the 5 sources most worth acquiring before 21 Nov and why.
