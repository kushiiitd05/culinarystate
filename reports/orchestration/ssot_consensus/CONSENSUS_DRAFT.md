# CulinaryState SSOT consensus audit — round 1 merged inventory (CONSENSUS_DRAFT)

Status: **DRAFT / AI_DRAFTED / PROPOSED** (synthesiser, S176, 2026-11-08). This draft does not sign, approve or decide anything (D-071). Humans or the AI personas decide the review blocks. Status values come from repo paths listed in the topic inventories. The synthesiser re-checked the numbers it relies on (below). Hours are agent estimates (UNVERIFIED).

Inputs: `topics/T0,T2..T9.json` (there is **no T1 file**; T0 covers SSOT core + Levels 7-11, so T1 appears to have been merged into T0: please confirm) and round-1 votes `votes/R-FEAS_round1.json`, `R-SCI_round1.json`, `R-SSOT_round1.json`.
Outputs: `registry/component_ledger_v1.csv` (one row per remaining canonical item, one `-DONE` row per DONE component, one `-XREF` row per component whose items were all merged elsewhere) and `contested_round1.json`.

## 1. Rules applied
- An id that no reviewer lists is **UNANIMOUS**. An AMEND by one reviewer, compatible with the project laws and not objected to by another reviewer on the same id, is **AMENDED** (proposer recorded in `notes`). Where two reviewers amended the same id compatibly (T0-C04-R1, T6-C03-R5, T5-C01-R1, T5-C02-R2, T5-C02-R4, T5-C11-R4, T3-C08-R2, T4-C06, T9-C28), the amendments were merged and the row stays AMENDED.
- **CONTESTED**: conflicting amendments (C01, C02) and 'missing' proposals that change scope or priority (C03-C09). No reviewer cast a REJECT.
- Missing proposals that only consolidate already-listed work were **adopted as AMENDED**: §128 delta -> T0-C01-R2; FDA pH registry -> T3-C22-R2; H8 scope-cut register -> T9-C07-R4; env-authorisation owner -> T9-C25-R5; human-time ledger -> T9-C26-R4 (merged with the existing MUST T0-C18-R1); prereg edit lock -> T9-C26-R5 (gathers the 10 Nov deadlines that were already adopted). R-FEAS's ids T9-C26-R3/R4/R5 and T9-C21-R2 collided with existing ids and were renumbered.
- **Duplicates**: 92 item ids were merged into a canonical id. Each canonical row lists its aliases and who proposed the merge (R-FEAS / R-SSOT / R-SCI / SYNTH). An alias has no ledger row of its own; grep the `notes` column for its id. After a merge, a canonical row's priority is the highest among its aliases, unless a reviewer amendment set the priority explicitly. Every such promotion is noted on the row as `SYNTH: priority` and is open to a round-2 vote.
- T7 `plan_steps` was normalised from string to list (R-SSOT).

## 2. Totals after merge
- Ledger rows: 493. Canonical open items: 473 (from 555 topic items + 10 new = 565, minus 92 aliases). DONE component rows: 13. XREF-only component rows: 7.
- Consensus: UNANIMOUS 414, AMENDED 67, CONTESTED 12 rows (9 contested issues).
- Priority of open items: MUST 85, SHOULD 168, COULD 110, AFTER 110. **Before the merge the topics listed 127 MUST items**; R-SSOT's double-counting finding is confirmed.
- MUST agent-hours, summed from the first range in each row: about 139-214 h (rough; rows like '0.5 per run' are counted once). Human hours are not summed here because 'each' and 'total' are mixed; T9-C26-R4 is the de-duplicated human-time ledger (R-FEAS estimate: about 16-20 h per person over 9-16 Nov, UNVERIFIED).
- MUST by topic: T0 4, T2 12, T3 5, T4 5, T5 12, T6 8, T7 1, T8 17, T9 21.

## 3. Facts the synthesiser re-verified (2026-11-08, read-only)
- `reports/step17/rung_a_dryrun_counts_full_corpus_final.json` totals.events = **9,470,190** (Rung A). 14,594,812 is the 26g census total (R-SCI correction adopted on T0-C03, T7-C17, T9-C16).
- `registry/scenario_defaults_v1.csv` = **27** data rows (not 28). `registry/scenario_defaults_nonheat_v1.csv` = 40 rows (untracked lane L-NH).
- `ledgers/data/SVAR.jsonl` = 355 lines / **224** distinct ids. `registry/state_variable_registry_v1.csv` = 254 rows (new item T2-C03-R3).
- Untracked lane files exist: `src/culinarystate/lotstate/` (values, intervals, text, ing_match, sr_legacy, linker, mention_freq), `tools/lotstate_match_ing.py`, `src/culinarystate/simulation/nonheat_drivers.py` (thaw_time_s, slab_two_stage, drying_state, f0_minutes, slab_av, cube_av), `nonheat_binding.py`, `registry/food_ph_fda_draft_v1.csv` (488 rows), `food_ph_fda_ing_crosswalk_draft_v1.csv`. Only `reports/orchestration/S176_L-PH_report.md` exists among lane reports. It records that the FDA/CFSAN page was opened through web.archive.org captures.
- SSOT anchors used by the contested proposals: L6659 = §121, L4358 = §80, L9149 = §152, L5347 = §99, L8872 = §143, L3096 = §51, L35075 = §257L, L42705 = §257P, L7872 = §128. §141 output contract text at L8846-8849 matches the brief.
- `registry/compute_runs_v1.csv` has 14 data rows. RUN claims for Rung A, rc2, NER and the replay census have no run-row id there (R-SSOT). This is not fixed in round 1 and is listed under open questions.

## 4. Contested issues (round 2 votes needed)
### C01 — T9-C16 (component status), T9-C16-R1
- Issue: Status of T9-C16 'D3 state-tracking engine VALIDATION (gold comparison)'. Topic said RUN. R-SCI: NOT_STARTED (no gold comparison exists; DEEP_GOLD 0; T3-C17 NOT_STARTED). R-SSOT: CODE (engine RUN under T3-C12, validation NOT_STARTED under T3-C17). Two different status amendments to the same id.
- Synthesiser proposal: Set T9-C16 to NOT_STARTED and give it only the D3 packaging (T9-C16-R1 MUST, unchanged), with xrefs to T3-C12 (engine, RUN) and T3-C17 (gold evaluation, NOT_STARTED). Correct the evidence to Rung A 9,470,190 events (reports/step17/rung_a_dryrun_counts_full_corpus_final.json) and 26g census 14,594,812. Both reviewers agree on the facts. NOT_STARTED is the only label for a validation component that cannot over-claim. The engine's RUN status stays in T3-C12.
### C02 — T2-C09-R1, T2-C09-R2
- Issue: Canonical owner of the AA-pilot human chain. R-FEAS makes T5-C10-R4 the canonical verification item (T0-C05-R2, T2-C09-R4, T6-C13-R1, T9-C14-R2 as aliases) and T5-C10-R2 the canonical PDF-download item. R-SSOT says T2-C09 owns evidence extraction/verification and T5-C10 owns only the fit/PARAM. The two merges conflict.
- Synthesiser proposal: Split by the freeze boundary. T2-C09 owns the pre-fit evidence chain: R1 AA prereg signature; R2 browser PDF downloads, MUST, deadline 10 Nov, Kush about 1 h; R3 CAL extraction 11-12 Nov with R-SCI's partition rule for any AAK-X addition; R4 dual blind verification, 3 h each, by 15 Nov, with R-SCI's process-based acceptance. T5-C10 owns everything that opens only after the fit freeze: R5 Model A fit and freeze on 16 Nov; R6 SIM-VAL extraction, verification and descriptive check by 18 Nov, 1.5-2 h each, SHOULD if D5 slips. All R-FEAS deadlines, budgets and alias lists are kept. Only the id that carries them changes. If either reviewer objects, fall back to R-FEAS's ids, which leaves the rest unchanged.
### C03 — T5-C22-R1 (R-SCI missing proposal)
- Issue: R-SCI proposes a new MUST component T5-C22: composed-pipeline property tests (no L2/MODEL_DERIVED input becomes evidence_supported; NOT_POSSIBLE never rests on L2; no nutrient number without EVD id or VALIDATED_HELD_OUT model; UNKNOWN never routes to SIMULATE). It is a new MUST item, so it changes scope. It overlaps T0-C06-R2, the end-to-end contract audit already adopted as MUST with R-SCI's own acceptance.
- Synthesiser proposal: Do not add a separate MUST item. Add R-SCI's four rules (a)-(d) to the acceptance of T0-C06-R2, each with one planted-violation fixture that must fail closed. Raise T0-C06-R2 agent_hours from 4-6 to 5-8. Record T5-C22-R1 as an alias of T0-C06-R2. Tests that need hypothesis run on the Mac (T5-C05-R1, T9-C25-R5).
### C04 — T9-C32-R1 (R-SCI missing proposal)
- Issue: R-SCI proposes a new MUST number-class lint: every number in the deck and report must carry an evidence-class tag, and words like 'validated', 'calibrated', 'supported' and 'beats' are blocked unless a passed gate backs them. This adds agent and human load at the end of the critical path (report/slides T9-C20-R1).
- Synthesiser proposal: Make the lint an acceptance clause of T9-C20-R1, not its own MUST item. A SHOULD script (about 2 agent h) lists every number in the deck/report with R-SCI's class tags and flags the forbidden words unless a gate id is given. Kush/Parv approve the exceptions list during the 22-23 Nov edit. If the script is not ready by 21 Nov, the agent does the check by hand on the deck only.
### C05 — T4-C26-R1 (R-SCI missing proposal)
- Issue: R-SCI proposes a new SHOULD component: a Layer 1 binder precision audit (n about 200, AI pass plus human adjudication of 1-2 h). It adds human hours in the overloaded 9-16 Nov window. Without it, Layer 1 '3.4 % stated' is a coverage figure of unknown correctness.
- Synthesiser proposal: Keep it SHOULD but run it after the 16 Nov D5 freeze. The agent checks n=100 seeded events (seed 20261104, stratified by family, non-BBC on manjot) and reports the result labelled AI_CHECKED, per field, with Wilson CI. No human hours before 16 Nov. Human adjudication of 20 events is COULD. Slides must say either 'precision AI-checked (n=100)' or 'precision unmeasured'.
### C06 — T2-C05-R7 (R-SCI missing proposal)
- Issue: R-SCI proposes planted known-wrong normalisations in the 07.A-R1 packet, to measure whether raters can detect errors (DIAGNOSTIC_ONLY). Adding it after signature voids the prereg hash. It also touches the most time-critical human task.
- Synthesiser proposal: COULD, with a hard condition: add it only if it can be written into the 07A_R1 prereg inside the 10 Nov edit lock (T9-C26-R5) and costs at most 0.3 h per rater. Otherwise drop it for 25 Nov and state the limitation in the report ('AC1 measures agreement, not error detection'). Never add it after signature.
### C07 — T9-C25-R3 (R-FEAS missing proposal, proposed id T9-C26-R5)
- Issue: R-FEAS proposes a new MUST VPN/vinayak contingency: a D5 runner dry run by 14 Nov, plus a minimal fallback (deterministic rungs on manjot CPU; LLM rungs reported not run). This raises T9-C25-R3 (SHOULD) and changes the D5 rung set conditionally.
- Synthesiser proposal: Do not add a new MUST item. (a) The 14 Nov dry run is already adopted on T8-C15-R1 through R-FEAS's T0-C11-R2 amendment. (b) Add the fallback to the T9-C26-R2 fallback levels: if vinayak is unreachable by 17 Nov, run deterministic rungs B0/B1/B2/B4/B5T on manjot CPU and report LLM rungs NOT_RUN. Because this changes the run set, the same sentence must go into the D5 prereg inside the 10 Nov edit lock. (c) T9-C25-R3 stays SHOULD.
### C08 — T9-C26-R3 (R-FEAS missing proposal, proposed id T9-C21-R2: id collision)
- Issue: R-FEAS proposes a MUST rehearsal with Q&A prep (what cannot be claimed: H2, 0 PARAM except AA pilot, 07.A failure) and a hard code/result freeze on 21 Nov. The proposed id T9-C21-R2 is already taken (demo fallback video). The existing rehearsal item T9-C26-R3 is SHOULD, so this is a priority change.
- Synthesiser proposal: Use the existing id T9-C26-R3 and raise it to MUST: a timed dry run on 24 Nov, 1.5-2 h each, plus a one-page 'cannot claim' Q&A sheet drafted by the agent (1-2 h). The 21 Nov hard freeze is already a T9-C26-R2 trigger (adopted), so it is not added twice. T9-C21-R2 (demo video) is unchanged.
### C09 — T0-C19-R1 (merges 5 R-SSOT missing proposals: T0 classical §121-§127/§80-§86/§159-§160; T0 course ontology §152-§158/§161-§170; T0 representation freeze §99-§102/§111-§120/§143/§146; T0 schemas §51/§61-§64/§72-§74; T9 §257G-§257P incl. §257L RQ flow)
- Issue: R-SSOT found 87 of 295 top-level SSOT sections that no topic anchors. It proposes owners or 'superseded' flags plus several scope decisions (which §123 null models, §99 freeze satisfied?, §257P critical-path checklist as a pass/fail table). None of the five proposals gives a priority, and together they could add a lot of scope.
- Synthesiser proposal: One SHOULD agent pass (3-5 h, 0.5 h human review) as T0-C19-R1: a coverage-map table with one row per unanchored section (with SSOT line range), each classed SUPERSEDED / OUT_OF_SCOPE_25NOV / OWNER=<existing item id> / UNCOVERED. No new build work. The §257P checklist rows go into T9-C26 as pass/fail lines. Any section classed UNCOVERED that is needed for 25 Nov comes back as a round-2 item. The §123 null-model scope is handled by the adopted T0-C15-R3 (COULD).

## 5. Critical-path view (MUST items, de-duplicated, with dates from adopted amendments)
| Date (adopted) | Item | Who | Note |
|---|---|---|---|
| 9 Nov | T3-C22-R7 Q39 lot-state decision (lean defer) | human | R-FEAS |
| 9 Nov | T2-C05-R5 07.A AC1-vs-kappa ruling before signature | human | R-FEAS + R-SCI |
| 10 Nov | T9-C26-R5 prereg edit lock (H3 reword T8-C12-R1, power note T9-C12-R1, embedding T8-C06-R2, 29-diag contrast T6-C03-R5, H1 caveat T8-C04-R2) | agent + human | R-FEAS |
| 10 Nov | T7-C01-R2 Step 35 decision (lean DESIGNED, NOT RUN) | human | R-FEAS |
| 10 Nov | T2-C09-R2 AA PDFs (5, browser) [C02] | Kush ~1 h | R-FEAS |
| 10-11 Nov | signatures: T2-C05-R1 (07.A), T2-C09-R1 (AA) [C02], T8-C20-R1 (D5), T6-C03-R1/R2 (15A-BOOT + 29-diag) | Kush, Parv | never AI (D-071) |
| 11-13 Nov | T2-C05-R2 07.A-R1 labelling (3-4 h each); else 07.A FAILED-on-record | Kush, Parv | R-FEAS trigger |
| 11-14 Nov | T6-C03-R3/R4 29-diag run on Mac + memos (after T6-C19-R1 env record) | agent | R-FEAS |
| 14 Nov | T8-C15-R1 D5 runner dry run (DRY_RUN) | agent, vinayak | R-FEAS |
| 15 Nov | T2-C09-R4 AA CAL dual verification (3 h each) [C02] | Kush, Parv | R-FEAS + R-SCI |
| 16 Nov | T8-C20-R2 D5 review incl. S-gold re-derivation (5-7 h each) -> T8-C20-R3 freeze | Kush, Parv | R-FEAS |
| 16 Nov | T5-C10-R5 Model A fit freeze (before SIM-VAL opened) | agent | R-SCI |
| 17-19 Nov | T8-C15-R1 runs, T8-C21-R1 H1, T8-C22-R1 H3, T8-C16-R1 blind manual UCR sample, T8-C01-R1 router scoring | agent + humans (UCR sample) | R-SCI MUST on T8-C16-R1 |
| 18 Nov | T5-C10-R6 SIM-VAL descriptive check (SHOULD if D5 slips) [C02] | agent + humans | R-FEAS |
| 21 Nov | code and result freeze (T9-C26-R2 trigger) | all | R-FEAS |
| 13-24 Nov | T9-C20-R1 report + deck (skeleton 13 Nov, draft 21 Nov, edit 22-23 Nov), T9-C26-R3 rehearsal 24 Nov [C08] | agent + humans | R-FEAS |

## 6. Merged inventory by topic
### T0 — SSOT core: laws, research spine, architecture, task types, MPU, router, state semantics, output contract, Levels 7-11 status
Open items 25 (MUST 4, SHOULD 10, COULD 4, AFTER 7); consensus UNANIMOUS 19, AMENDED 5, CONTESTED 1.

| Component | Status | Open items | Component notes |
|---|---|---|---|
| T0-C01 Final decision, scope rule and frozen project laws | DONE | 2 |  |
| T0-C02 Field definition, literature gap and novelty claims | DRAFT | 1 |  |
| T0-C03 Shared research spine: state S_t, process P_t, transition T | RUN | 1 | R-SCI: status_evidence fix: reports/step17/rung_a_dryrun_counts_full_corpus_final.json totals.events = 9,470,190 Rung A events (re-verified by SYNTH); 14,594,812 is the Step 26g census total incl. lot-introduction events (reports/step26/simulability_census_ful |
| T0-C04 Process representation and local driver trajectories theta(x,t) | RUN | 1 |  |
| T0-C05 Hierarchical prediction targets and process-effect model T(S,P,theta) | CODE | 1 |  |
| T0-C06 Output contract: unsupported / physically_possible / evidence_supporte | CODE | 3 | R-SSOT: single owner of §141 crosswalk + no-numeric-leak audit; T8-C25 and T5-C05 reference it |
| T0-C07 Process relevance gate G(S,P,R,Q) and selective routing (RQ5/H5) | CODE | 2 |  |
| T0-C08 Query router (SSOT 39) with intent branches | CODE | 1 | R-SSOT: disambiguated: SSOT §39 QUERY router (decision/query_router.py), shared with T8-C01; T5-C05 is the 23a applicability/formula router (mechanism/applicability.py) - no shared status |
| T0-C09 System architecture (parser -> tracker -> gate -> process module -> hy | CODE | 1 |  |
| T0-C10 Decision formulation and recovery (RQ3/RQ4, feasible-action argmax, st | OUT_OF_SCOPE | 1 |  |
| T0-C11 Benchmark task types (9 tasks) and D5 benchmark | DRAFT | 2 | R-SSOT: keeps only the §12 task-crosswalk item; D5 items owned by T8-C20/T8-C15 |
| T0-C12 Metrics and statistical reporting | CODE | 0 | R-SSOT: metric spec owner T9-C12; ECE/Brier/risk-coverage on independent gold (§242.5) = T8-C12-R3 (NOT_STARTED/AFTER) |
| T0-C13 Minimum publishable unit (MPU) checklist | DRAFT | 0 | R-SSOT: xref T9-C23 (MPU table) / T9-C30 (DoD) |
| T0-C14 State semantics: sensory, physical, factorised and latent representati | CODE | 1 |  |
| T0-C15 Classical flavour-pairing replication (Levels 7-9) and similarity sens | NOT_STARTED | 3 | R-SSOT: ssot_anchor add §121-§127 L6659-7871; §80-§86 L4358-4782; §159-§160 (anchors spot-checked by SYNTH: L6659 = §121, L4358 = §80); xref T7-C06/C14 for n_ij/N_s; new item T0-C15-R3 |
| T0-C16 Levels 12-17 frozen status and legacy invariants | OUT_OF_SCOPE | 2 | R-SSOT: ssot_anchor add §131 L8136-8231, §132 L8232-8450, §135 L8541-8678; scope-out of Levels 10-11 recorded via T9-C07-R4 |
| T0-C17 Professor endpoint / API audit and external-fact items that only human | BLOCKED | 1 |  |
| T0-C18 Governance, human gates and negative-result register | BLOCKED | 1 | R-SSOT: xref only: gate registry DONE (T9-C07); executing signatures BLOCKED (T9-C13/T9-C08); human-only sheet merged into T9-C26-R4 |
| T0-C19 SSOT sections without topic anchor (coverage map) | NOT_STARTED | 1 | R-SSOT: new component proposed |

| Item | Pri | Consensus | Where | Agent h | Human h | Item (short) |
|---|---|---|---|---|---|---|
| T0-C01-R1 | SHOULD | UNANIMOUS | human | 1-2 | 0.5-1 | Decide whether to apply the v16 change set / a status addendum before 25 Nov (Q40). Agent lean: do NOT apply; ship a one-page 'SSOT v15 vs current sta _(aliases: T9-C01-R1)_ |
| T0-C01-R2 | SHOULD | AMENDED | any | 2-3 | 0 | Write the 'SSOT v15 status block vs reality' delta table (what §128 says vs what repo evidence shows) for the report appendix. |
| T0-C02-R1 | SHOULD | UNANIMOUS | any | 6-10 | 1-2 (review) | Targeted related-work re-search (state-tracking food RAG, evidence-gated abstention, process-conditioned food representations); verify each citation b |
| T0-C03-R2 | COULD | UNANIMOUS | any | 4-6 | 1 (H4 approval) | Build Step 03.3 clock registry and state_representation_contract_v1_1 (additive); add physical and history SVARs (moisture, a_w, thermal dose, time si |
| T0-C04-R1 | SHOULD | AMENDED | human | 3-5 | 2 total | Source from opened handbooks (page + range) the <=8 scenario defaults (of the 27 rows in registry/scenario_defaults_v1.csv) used by the AA/steam/boil  _(aliases: T4-C06-R1, T4-C06-R2, T5-C09-R1, T9-C27-R1)_ |
| T0-C05-R6 | AFTER | UNANIMOUS | vinayak | 40-80 | 5+ | Steps 28,31-34 (E7 prior, features at scale, hybrid, rollout) and learned heads for L2/L3. |
| T0-C06-R1 | MUST | AMENDED | human | 1-2 | 0.5-1 | Freeze the mode-to-§141 crosswalk (human-approved): DIRECT -> evidence_supported tagged E3_UNVERIFIED + COND_UNAUDITED_07A with EVD id; INTERPOLATE -> |
| T0-C06-R2 | MUST | AMENDED | any | 4-6 | 0 | End-to-end contract audit: property tests plus a corpus scan that no emitted answer contains a food-chemistry number lacking an EVD id or a frozen-mod _(aliases: T8-C25-R1)_ |
| T0-C06-R3 | SHOULD | UNANIMOUS | mac | 2-3 | 0 | Show the three-way label and basis (EVD/Layer 2/ASSUMED) on every demo claim chip. |
| T0-C07-R1 | SHOULD | UNANIMOUS | any | 3-4 | 1-2 (labels) | Build an annotated gate set (~100 queries incl. D5 X controls), measure precision/recall with false-negatives reported separately; no tuning on D5 tes |
| T0-C07-R2 | MUST | UNANIMOUS | any | 0.5 | 0.5 | Write SSOT H1-H5 to proposal H1-H4 mapping into the report. |
| T0-C08-R3 | AFTER | UNANIMOUS | vinayak | - | - | Vision/audio branch. |
| T0-C09-R2 | SHOULD | UNANIMOUS | any | 3-4 | 0 | End-to-end regression suite for the whole loop (parse -> state -> route -> packet -> answer) on 50 recipes with golden outputs. |
| T0-C10-R2 | AFTER | UNANIMOUS | vinayak | 30-50 | 10+ + expert | Recovery benchmark and state-distance model. |
| T0-C11-R3 | MUST | UNANIMOUS | any | 1 | 0 | Add a documented crosswalk SSOT Task 1-9 <-> D5 blocks <-> D-008 T1-T8, and state which tasks are not covered. |
| T0-C11-R5 | AFTER | UNANIMOUS | human | 10-15 | 55-80 split | Locked-tier benchmark (240) and Tasks 3,5,7. |
| T0-C14-R2 | AFTER | UNANIMOUS | vinayak | 20-40 | 2 | Learned encoders / embeddings of ingredient-state (GPU). |
| T0-C15-R1 | COULD | UNANIMOUS | manjot | 16-24 | 1 (review) | Implement classical layer on toy data from §80/§130 (unit tests) then on FlavorGraph/FooDB-derived profiles (licence internal-only): n_ij, N_s(R), N_s |
| T0-C15-R2 | AFTER | UNANIMOUS | manjot | 6-10 | 0 | Similarity sensitivity pass (raw/Jaccard/Ochiai/IDF/chance-adjusted) on the cuisine conclusion. |
| T0-C15-R3 | COULD | AMENDED | any | 1 | 0.5 | Decide which §123 null models (ingredient-shuffle, category-preserving, frequency-preserving) are in scope for the talk; list the rest as uncovered; x |
| T0-C16-R1 | COULD | UNANIMOUS | any | 3-4 | 0 | Map each §137 open question to a plan step or 'parked' in a one-page register (Q-P1 professor endpoint, Q-N2 licences, Q-RS1-13 extraction). |
| T0-C16-R2 | AFTER | UNANIMOUS | vinayak | 100+ | 20+ | Level 12-16 empirical programmes. |
| T0-C17-R1 | SHOULD | UNANIMOUS | human | 0.5 | 0.5-1 | Kush supplies or confirms: professor endpoint access/terms status and a written copy of permission. _(aliases: T9-C05-R1)_ |
| T0-C18-R2 | SHOULD | UNANIMOUS | human | 0.5 | 0.5 | Formalise D-071 line (AI persona decision vs human signature) in DECISIONS (Q37). |
| T0-C19-R1 | SHOULD | CONTESTED | any | 3-5 | 0.5 | SSOT coverage map for sections no topic anchors: §121-§127/§80-§86/§159-§160 classical pairing; §152-§158, §161-§170 course ontology + midsem imports; |

Topic contradictions recorded by the inventory: 7; SSOT requirements without plan coverage: 8 (see `topics/T0.json`). Resolved by round 1: Rung A count (T0/T3/T7/T9), defaults 27 rows (T4), SVAR 224 ids vs 254 rows (T0/T9), EVD lines vs ids (T2), physical % sample vs full corpus (T4/T5: use T4 full-corpus 3.4 % / 5.3 %).

### T2 — Evidence plane: EVD/COND/SVAR/STUDY ledgers, condition normalisation + 07.A, lineage 08a/08b, extraction 09, pilot 10, wave-1 11, structured DB 12, literature corpus 13, coverage 14, freeze 15, D1
Open items 64 (MUST 12, SHOULD 22, COULD 13, AFTER 17); consensus UNANIMOUS 54, AMENDED 5, CONTESTED 5.

| Component | Status | Open items | Component notes |
|---|---|---|---|
| T2-C01 EVD endpoint ledger + export v1 (process-event table, E3 plane) | DONE | 2 | R-SSOT: counting rule: EVD.jsonl 57,280 lines = 18,156 ids; 17,978 current ACTIVE ids (latest version per id); 0 human-verified; 6,148 lines carry an AI precheck block (not human verification) |
| T2-C02 Kinetic / trajectory evidence contract (KIN, KINPT, XTR, ADJ; SEXP/SMP | CODE | 2 |  |
| T2-C03 SVAR registry (state variables) and physical/history variables | DONE | 3 | R-SSOT: owner of SVAR ledger/registry (DONE for CHEMICAL only): SVAR.jsonl 355 lines / 224 distinct ids (re-verified by SYNTH) vs registry/state_variable_registry_v1.csv 254 rows - different populations; T9-C02 = xref; T3-C21 owns physical/history extension on |
| T2-C04 COND ledger and condition normaliser (07 automated part) | DONE | 3 |  |
| T2-C05 07.A human condition-audit gate (v4 FAILED, R1 redo) | BLOCKED | 7 |  |
| T2-C06 Source lineage 08a on the 17,978 EVD rows (study / lineage root / spli | RUN | 4 |  |
| T2-C07 Lineage library 08b-v0 (DOC registration, detector, keys for new evide | CODE | 2 |  |
| T2-C08 Extraction and verification machinery (Step 09) | CODE | 4 |  |
| T2-C09 Step 10 reduced pilot: ascorbic-acid kinetics rows (D-076) -> first PA | BLOCKED | 6 | R-SSOT: see T5-C10 (ownership CONTESTED C02) |
| T2-C10 Wave-1 hand-verified literature evidence (DEL-1: >=40 verified rows) a | NOT_STARTED | 6 |  |
| T2-C11 Structured database evidence (Step 12) and local-but-unregistered sour | CODE | 4 |  |
| T2-C12 Literature discovery corpus (Step 13) | CODE | 3 |  |
| T2-C13 Coverage-driven evidence growth (Step 14) and anchor-set choice | DRAFT | 3 |  |
| T2-C14 Pre-freeze rulings (15.0) and 15a.R reserved-group seal | DONE | 1 |  |
| T2-C15 Freeze 15a (bootstrap), dataset card, SPLIT registry, reproducibility  | DRAFT | 3 |  |
| T2-C16 Freeze 15b (paper-grade DATA-EVIDENCE v1) | BLOCKED | 2 |  |
| T2-C17 EVD to ingredient/process linkage (ING, PROC, prior_state) for routing | RUN | 2 |  |
| T2-C18 Source registry, licences, H2 approvals, permission emails (SRC/SNAP,  | BLOCKED | 3 |  |
| T2-C19 Evidence tiers E1-E6 mapping and conflict records | DRAFT | 2 |  |
| T2-C20 Raw-vs-cooked volatile literature anchors and platform harmonisation | OUT_OF_SCOPE | 1 |  |
| T2-C21 D1 deliverable packaging: evidence ledger for the proposal (report tex | DRAFT | 1 |  |

| Item | Pri | Consensus | Where | Agent h | Human h | Item (short) |
|---|---|---|---|---|---|---|
| T2-C01-R1 | SHOULD | UNANIMOUS | any | 3-5 | 0-0 | Field-by-field conformance table of the §203.2 process-event schema vs EVD export v1 (PRESENT / UNKNOWN-by-source / ABSENT with counts), so the D1 cla |
| T2-C01-R2 | SHOULD | UNANIMOUS | any | 0.5-1 | 0-0 | Confirm EVD export v2 (08a.7) builder output is regenerated and byte-reproducible after the last ledger state, and record hash in compute_runs _(aliases: T9-C03-R2)_ |
| T2-C02-R1 | SHOULD | UNANIMOUS | any | 4-8 | 0.5-1 | Decide the storage form for the AA pilot rows (KIN/KINPT ledger vs staged CSV) and add KIN/KINPT/XTR/ADJ schemas to ledgers/schemas |
| T2-C02-R2 | SHOULD | UNANIMOUS | any | 1-2 | 0-0 | Orchestrator-owned append of verified AA rows as new KIN/KINPT ledger (not protected EVD) with hashes |
| T2-C03-R1 | SHOULD | UNANIMOUS | human | 0.5-1 | 1-2 | Decide the physical/history SVAR v1.1 set and definitions (shared with the lot-state topic) _(aliases: T3-C21-R2, T9-C02-R1)_ |
| T2-C03-R2 | SHOULD | UNANIMOUS | any | 3-6 | 0-0 | Append additive SVAR v1.1 rows (physical/history) via orchestrator, before the 15a freeze is approved or as 15a.1 |
| T2-C03-R3 | SHOULD | AMENDED | any | 1-2 | 0 | Reconcile SVAR ledger (ledgers/data/SVAR.jsonl 355 lines / 224 distinct ids; 354 CHEMICAL, 1 PHYSICAL) vs registry/state_variable_registry_v1.csv (254 |
| T2-C04-R1 | SHOULD | UNANIMOUS | human | 0.5 | 0.5-1 | Rule whether 07.B COND v1.1 axes and 07.C platform vocabulary are adopted now (new AA/literature rows need them) or stay as raw-text SEXP optional fie |
| T2-C04-R2 | AFTER | UNANIMOUS | any | 3-6 | 1-2 | Define the condition-bucket scheme per process family (bin edges for T, t, pH, a_w; treatment of INTERVAL/QUALITATIVE) |
| T2-C04-R3 | AFTER | UNANIMOUS | any | 8-24 | 1-2 | If 07.A-R1 fails: repair normaliser as 07H.v2 with full regression and issue packet v5 |
| T2-C05-R1 | MUST | UNANIMOUS | human | 0.2 | 0.5-1 each | Kush and Parv sign the 07A_R1 pre-registration (sha-bound signature file) before opening the packet _(aliases: T9-C08-R1)_ |
| T2-C05-R2 | MUST | AMENDED | human | 0 | 3-4 each | Kush and Parv each independently label the 100-condition R1 packet (9 fields + overall), alone, blind, no external source _(aliases: T4-C02-R1, T0-C12-R1, T5-C06-R1, T6-C05-R2, T9-C13-R1)_ |
| T2-C05-R3 | MUST | UNANIMOUS | any | 0.5-1 | 0-0 | Score with tools/step07ar_agreement.py; verify freeze (step07hr_freeze.py --verify); write result JSON + diagnostics (kappa, PABAK, per-field, bootstr _(aliases: T9-C13-R2)_ |
| T2-C05-R4 | MUST | UNANIMOUS | human | 0.5 | 0.5-1 each | Joint adjudication of disagreements, DECISIONS entry (counted by orchestrator), statistic never recomputed after adjudication |
| T2-C05-R5 | MUST | AMENDED | human | 0.5 | 0.5-1 | Written ruling reconciling the plan card (R-06: AC1 diagnostic only, original kappa rule) with the R1 gating statistic, and stating what a valid 07.A  |
| T2-C05-R6 | COULD | UNANIMOUS | any | 1-2 | 0-0 | Produce the card's diagnostics annex for v4 (PABAK, AC1, specific agreement, disagreement matrix) as DIAGNOSTIC_ONLY without re-labelling the verdict |
| T2-C05-R7 | COULD | CONTESTED | any | 1-2 | 0.3 | 07.A-R1 error-detection sensitivity: optionally plant a small, prereg-disclosed set of known-wrong normalisations (hidden from raters); report detecti |
| T2-C06-R1 | SHOULD | UNANIMOUS | human | 0.5 | 0.5-2 | Expert/Kush reading of the USDA R6 vs Bognar overlap verdict (8 vs 11 references, Bognar cites USDA 1998) before cross_source_v1 is called independent |
| T2-C06-R2 | MUST | UNANIMOUS | any | 1-2 | 0.5 | Slide-level honest statement of lineage: counts, G08-3 FAIL, publication-component CV label, one-line implication for every H2 claim |
| T2-C06-R3 | AFTER | UNANIMOUS | any | 8-16 | 2-4 each | Optional detector rework and a second 150-edge human audit as a NEW version (08a.1); D-034 says no retune of v1 |
| T2-C06-R4 | AFTER | UNANIMOUS | human | 3-6 | 10-30 | Capture lab/author groups and study design for the PE 125 papers (needs reading of papers, library access) |
| T2-C07-R1 | COULD | UNANIMOUS | human | 0 | 0.5-1 | Sign THR-08B-05 or accept 08b-v0 as 'no claim' intake only; answer step08b_questions_for_kush.md |
| T2-C07-R2 | SHOULD | UNANIMOUS | mac | 1-2 | 0-0 | Register the AA pilot PDFs (7 fetched + 5 after browser download) and DOIs through register_document into scratch DOC library and run propose_edges to |
| T2-C08-R1 | SHOULD | UNANIMOUS | any | 8-16 | 1-2 | Build golden fixtures (synthetic tables with seeded fabricated values, unit/basis traps, censoring footnotes, figure-only series, empty document) and  |
| T2-C08-R2 | COULD | UNANIMOUS | vinayak | 4-8 | 0-0 | Prompt/model registry and Extractor B: run a second, different-family local model (Ollama on vinayak) blind on the AA CAL papers and diff field by fie |
| T2-C08-R3 | SHOULD | UNANIMOUS | any | 1-2 | 0.5-1 each | Pre-register the Step 10/11 accuracy gate (precision/recall LB thresholds, human-first fallback) before any further extraction counts |
| T2-C08-R4 | AFTER | UNANIMOUS | any | 6-12 | 0-0 | Figure digitisation tooling (DIGITIZED value_origin with tool/version/uncertainty) |
| T2-C09-R1 | MUST | CONTESTED | human | 0.1 | 0.3-0.5 each | Sign the AA pilot pre-registration (before any verdict is read) _(aliases: T5-C10-R1, T9-C27-R2)_ |
| T2-C09-R2 | MUST | CONTESTED | human | 0 | 0.5-1 | Browser-download the 5 PDFs that refuse scripted download (AAK-02,04,05,08,10) into data/raw/aa_pilot/ on the Mac; confirm licence on the publisher pa _(aliases: T5-C10-R2, T9-C14-R1, T0-C05-R1)_ |
| T2-C09-R3 | MUST | CONTESTED | mac | 3-5 | 0-0 | AI extraction of CAL rows from newly downloaded SIM-CAL papers with spans (SIM-VAL papers stay unopened until fit freeze) _(aliases: T5-C10-R3)_ |
| T2-C09-R4 | MUST | CONTESTED | human | 0 | 3 each | Kush and Parv each verify every CAL row (VERIFIED / CORRECTED / REJECTED) against the paper span, blind to the other _(aliases: T5-C10-R4, T0-C05-R2, T6-C13-R1, T9-C14-R2)_ |
| T2-C09-R7 | SHOULD | UNANIMOUS | any | 2-4 | 0.5 | Record what the pilot is not: n, papers, lab groups UNKNOWN, no E4 promotion, DEL-1 0/40 unaffected; kinetic_series_availability for AA (and chlorophy |
| T2-C09-R8 | AFTER | UNANIMOUS | any | 8-16 | 3-6 each | Chlorophyll (sim_chl_1) second system: extraction and comparison per R-14 |
| T2-C10-R1 | SHOULD | AMENDED | human | 1-2 | 6-12 Kush; 3-6 Parv | Strip the AI suggestion columns and have Kush verify the 40 MAIN rows against the cited papers (Parv audits a predeclared sample; RESERVE 15 as replac _(aliases: T9-C14-R3)_ |
| T2-C10-R2 | SHOULD | UNANIMOUS | human | 0 | 1-3 | Library/proxy access for the 110 non-OA Phenol-Explorer papers (human permission or institutional login) |
| T2-C10-R3 | COULD | UNANIMOUS | any | 1-2 | 0-0 | Ingest human decisions into EVD verification status (new version lines, tier stays E3 unless dual-verified) via orchestrator |
| T2-C10-R4 | COULD | UNANIMOUS | human | 1 | 3-6 | HV-003: predeclare sample size and audit 3,870 AI_PRECHECKED PE rows (Parv) _(aliases: T9-C04-R1)_ |
| T2-C10-R5 | AFTER | UNANIMOUS | human | 40-80 | 40-80 Kush; 30-60 Parv; 10-20 expert | 11b breadth: mechanism/negative/conflict rows for the 32 MECH entries (>=10 negative, >=3 conflict candidates), partition lock |
| T2-C10-R6 | COULD | UNANIMOUS | human | 0.2 | 0.2 | Record 11.D formally: AA chosen at 26.0 (D-052) before Step 11 evidence (R-14 intended choice from verified evidence); state this in the decision log |
| T2-C11-R1 | COULD | UNANIMOUS | manjot | 2-4 | 0-0 | Stage-only use of R2 yields and SR retention factors for the lot-state mass-balance (no ledger append): counts-only report |
| T2-C11-R2 | SHOULD | UNANIMOUS | human | 0.2 | 0.3 | Decision on ordering: ingest R2 + Bognar remainder into EVD before approving the 15a freeze, or defer to 15a.1 (new version) |
| T2-C11-R3 | AFTER | UNANIMOUS | any | 8-16 | 4-8 Kush; 4-8 Parv | Ingest R2 + Bognar remaining tables after audit sample >=75 rows per source with 0 transcription errors and H2 decisions |
| T2-C11-R4 | AFTER | UNANIMOUS | manjot | 3-6 | 0.5-1 | Download/stage FDC Foundation Foods, Flavonoid DB 3.3, UK CoFID after licence confirmation |
| T2-C12-R1 | COULD | UNANIMOUS | human | 0 | 0.5-1 | H2 decisions and user-created keys (OpenAlex/Crossref email, NCBI key if used) for Europe PMC, OpenAlex, Unpaywall |
| T2-C12-R2 | AFTER | UNANIMOUS | manjot | 6-12 | 3-6 each | 13a metadata-only discovery for AA and chlorophyll systems: query log, licence/OA status per DOI, 100 abstracts double-labelled |
| T2-C12-R3 | AFTER | UNANIMOUS | manjot | 20-40 | 6-12 each | Full 13a corpus with propensity universe and known-item recall >= 0.90, then triage classifier decision |
| T2-C13-R1 | SHOULD | UNANIMOUS | manjot | 4-8 | 0.5 | Counts-only coverage statement for the talk: EVD pair/cell coverage against corpus demand, per process family, with the 07.A-unaudited tag |
| T2-C13-R2 | COULD | UNANIMOUS | any | 6-12 | 1-2 | Choose the anchor set after a coverage audit and register the READY/PARTIAL/NEED_DATA readiness ledger for consumers (26/27, 29/30, 23 negatives) |
| T2-C13-R3 | AFTER | UNANIMOUS | any | 16-40 | 40-120 each | Active acquisition scheduler with random stream >= 30% and stop rules, acquisition log |
| T2-C14-R1 | SHOULD | UNANIMOUS | mac | 0.5 | 0-0 | Seal integrity check before any 15a/29-diag read (reserved list hash vs commitment, access log) |
| T2-C15-R1 | MUST | AMENDED | manjot | 8-12 total | 1-2 review | Build the dataset-card generator and publish counts-only card for the 17,978 ACTIVE E3 rows (all §203.9 outputs, COND_UNAUDITED / BOOTSTRAP_UNVERIFIED _(aliases: T4-C20-R1, T9-C14-R4)_ |
| T2-C15-R3 | COULD | UNANIMOUS | any | 4-8 | 0.5 | SPLIT schema v1.1 (add lineage-component, duplicate-group, lab, condition-OOD, matrix-OOD, platform, calibration strategies) and SPLIT.jsonl for 15a d |
| T2-C15-R4 | SHOULD | UNANIMOUS | any | 2-3 | 0-0 | Reproducibility record: seeds, versions, hashes, splits, run rows for every evidence-plane run (G15-R) |
| T2-C16-R1 | SHOULD | UNANIMOUS | any | 2-3 | 0.5 | Run the 15b readiness checklist and publish an explicit NOT_FROZEN/ BLOCKED_BY list for the report (honest negative) |
| T2-C16-R2 | AFTER | UNANIMOUS | any | 16-24 | 12-20 Kush; 6-13 Parv; 2-3 expert | Actual 15b freeze (verified test subset, sealed locked test H5, release licence matrix) |
| T2-C17-R1 | SHOULD | UNANIMOUS | human | 1 | 2-4 | Kush resolves the 129 HELD and 23 CONCEPT_MISSING ingredient links (HV-008) |
| T2-C17-R2 | COULD | UNANIMOUS | vinayak | 1-3 | 0-0 | Re-run router census with updated links to refresh the coverage numbers |
| T2-C18-R1 | SHOULD | UNANIMOUS | human | 0 | 0.5-1 | Kush rules on the H2 queue items needed before 25 Nov: #1/#3/#4 (Europe PMC, NCBI, Unpaywall), #6 (CoFID OGL), #16 (Food.com) _(aliases: T9-C05-R2, T0-C14-R3)_ |
| T2-C18-R2 | AFTER | UNANIMOUS | human | 1-2 drafting | 1-2 | Send permission/terms emails (H1 Bagler: RecipeDB/FlavorDB keys; INFOODS; IFCT; Phenol-Explorer authors; CoSyLab written confirmation) |
| T2-C18-R3 | AFTER | UNANIMOUS | any | 2-4 | 0-0 | Register local unregistered files into SRC/SNAP (12.0) with orchestrator minting ids |
| T2-C19-R1 | COULD | UNANIMOUS | human | 0.5 | 0.3 | Record the E6/E7 reconciliation in the v16 change set (decision only) |
| T2-C19-R2 | AFTER | UNANIMOUS | any | 6-10 | 1-2 review | Implement conflict-record builder with compatibility checks and human adjudication states |
| T2-C20-R1 | AFTER | UNANIMOUS | human | 20-40 | 20-40 each | Defer: curate 5-7 anchor foods (onion, garlic, potato, tomato, chicken, beef, coffee) matched raw-vs-cooked volatile studies with platform recorded |
| T2-C21-R1 | MUST | UNANIMOUS | any | 4-8 | 1-2 review | Write the D1 section and figures: sources, counts by tier/source/target, coverage (T/t/pH/a_w), lineage label, verified rows n/40, what is not claimed |

Topic contradictions recorded by the inventory: 12; SSOT requirements without plan coverage: 11 (see `topics/T2.json`). Resolved by round 1: Rung A count (T0/T3/T7/T9), defaults 27 rows (T4), SVAR 224 ids vs 254 rows (T0/T9), EVD lines vs ids (T2), physical % sample vs full corpus (T4/T5: use T4 full-corpus 3.4 % / 5.3 %).

### T3 — Recipe semantics and state tracking (steps 16-20, NER/linker deployment, quantities CQPO, vocab/ontology, identity 07I, lot-state [K])
Open items 64 (MUST 5, SHOULD 30, COULD 22, AFTER 7); consensus UNANIMOUS 55, AMENDED 9, CONTESTED 0.

| Component | Status | Open items | Component notes |
|---|---|---|---|
| T3-C01 Recipe-semantics schema contract v1 (EVT, ENTITY, STATE, QNT, POR, INS | DRAFT | 3 |  |
| T3-C02 Annotation handbook, Addendum A/B and hard-case catalog | DRAFT | 2 |  |
| T3-C03 Vocabulary: ING / ALIAS ingredient concepts and canonicalization tree | RUN | 4 | R-SSOT: ING counts 1,951 (reports/ingredient_registry_v1.md, BBC-only vocab) vs 5,387 (packet Q7) are different registries; resolution folded into T3-C03-R1 |
| T3-C04 ING to USDA SR Legacy / FDC crosswalk (feeds composition and portions) | DRAFT | 3 | SYNTH: observation (not a status change, needs round-2 vote): untracked lane code src/culinarystate/lotstate/ing_match.py, sr_legacy.py and tools/lotstate_match_ing.py exist |
| T3-C05 Process vocabulary (PROC) and process hierarchy | RUN | 2 |  |
| T3-C06 Tool vocabulary (TOOL) and tool-role registry | RUN | 1 |  |
| T3-C07 Quantity parsing and normalisation (CQPO quantity layer) | RUN | 4 |  |
| T3-C08 Portion, density and grams grounding (POR / CQPO portion ladder) | DRAFT | 4 |  |
| T3-C09 Ingredient-line NER deployment and MENTION ledger draft | RUN | 5 |  |
| T3-C10 Entity linker deployment (mention to ING) | CODE | 2 |  |
| T3-C11 Rung A deterministic instruction extraction (events, quantities in ste | RUN | 5 |  |
| T3-C12 Event-sourcing replay engine and event log | RUN | 3 |  |
| T3-C13 Quantity propagation and mass balance through merges/splits | CODE | 1 |  |
| T3-C14 Deep-Gold sampling frame, strata and hard-case sampling | RUN | 1 |  |
| T3-C15 Gold pilot P1 (7 recipes, dual annotation, counts-only scoring) | DONE | 1 |  |
| T3-C16 Gold pilot P1b (3-4 new recipes, Addendum B rule check) | BLOCKED | 2 |  |
| T3-C17 State-tracker gold evaluation (D3 claim) and held-out replay test | NOT_STARTED | 2 |  |
| T3-C18 Deep-Gold main cohort (19-S sizing, 19-M annotation N>=40, sealed test | BLOCKED | 2 |  |
| T3-C19 Scale procedural corpus (T0 weak corpus, T1 Silver 1k-10k, T2 Gold-Lig | OUT_OF_SCOPE | 4 |  |
| T3-C20 Recipe identity, duplicates, families and split groups (07I) | DONE | 2 |  |
| T3-C21 State variables for lot state: physical and history SVARs (state-field | DRAFT | 1 |  |
| T3-C22 Lot-state layer [K]: members, mass, composition, solutes, pH flags, me | CODE | 6 | R-SSOT: status NOT_STARTED->CODE: untracked lane L-LOT code src/culinarystate/lotstate/{values,intervals,text,ing_match,sr_legacy,linker,mention_freq}.py + tools/lotstate_match_ing.py exist (verified 2026-11-08), no committed tests, unreviewed; re-verify vs re |
| T3-C23 Recipe-level metadata, source/licence fields and recipe base | DONE | 1 |  |
| T3-C24 SSOT §257D gold test catalog conformance (162 Q cases, 121 V cases) | NOT_STARTED | 2 |  |
| T3-C25 Design decisions for lot-state/schema (state belief, five memory class | DRAFT | 1 |  |

| Item | Pri | Consensus | Where | Agent h | Human h | Item (short) |
|---|---|---|---|---|---|---|
| T3-C01-R1 | SHOULD | UNANIMOUS | any | 6-10 | 0 | Fold SP-001 and SP-004 plus lot-state fields into STATE/ENTITY v1.1 drafts under new ids (R-18: new versions only) with validator tests |
| T3-C01-R2 | SHOULD | UNANIMOUS | human | 1-2 (assemble packet) | 4-8 (Kush 2-4, Parv 2-4, UNVERIFIED estimate) | Step 16c freeze: Kush and Parv review contract v1, vocabulary hierarchy, handbook v2, hard-case keys and sign |
| T3-C01-R3 | COULD | UNANIMOUS | any | 3-5 | 0 | Representability check of the 20 hard-case prompts (17 synthetic + SSOT §237.5 list) against the v1.1 schemas |
| T3-C02-R1 | COULD | UNANIMOUS | human | 3-5 | 3-6 (Kush+Parv, UNVERIFIED) | Integrate Addendum B + 10 held rules into handbook v2; dual-review the hard-case catalog answer keys |
| T3-C02-R2 | AFTER | UNANIMOUS | human | 1 | 1-3 expert | Outside expert (food scientist / culinary annotator) sample check of handbook state attributes (cooked, cut, hydrated) for 10-20 events |
| T3-C03-R1 | SHOULD | AMENDED | manjot | 1-2 | 0 | Reconcile ING counts (1,951 report vs 5,387 packet vs ledgers/data/ING.jsonl rows) and publish a counts-only vocab status table |
| T3-C03-R2 | MUST | UNANIMOUS | manjot | 3-5 | 0 | Coverage census: fraction of Food.com / Wikibooks / TASTEset ingredient mentions (NER FOOD spans and Rung A links) that hit ING/ALIAS, by mention freq |
| T3-C03-R3 | SHOULD | UNANIMOUS | human | 2-3 (queue build) | 6-10 (Kush+Parv, UNVERIFIED) | Human review queue for the top-frequency unmapped / polysemous ingredients (top ~300 covering ~80 % of Food.com mentions) |
| T3-C03-R4 | COULD | UNANIMOUS | any | 3-5 | 0 | Implement §234.7 vocabulary proposal states + §234.8 growth control as a registry column and a validator |
| T3-C04-R1 | SHOULD | AMENDED | manjot | 6-10 | 0 | Deterministic scored lexical matcher ING -> SR Legacy (7,793 foods), AI-drafted, with confidence and method fields; counts-only report |
| T3-C04-R2 | SHOULD | UNANIMOUS | human | 1 | 4-8 (UNVERIFIED) | Human verification of matches for the top ingredients by corpus frequency |
| T3-C04-R3 | MUST | UNANIMOUS | human | 0.5 | 0.5 | Decision: SR Legacy as portion/composition authority under new basis codes (SR_PORTION) vs strict HUMAN_VERIFIED rule of rc2 |
| T3-C05-R1 | SHOULD | UNANIMOUS | manjot | 2-3 | 0 | Verb-coverage census of Rung A on Food.com + Gutenberg + Wikibooks steps (share of ACTION events mapped to PROC; top unmapped verbs, counts-only) |
| T3-C05-R2 | COULD | UNANIMOUS | human | 2-3 | 2-4 | Freeze PROC hierarchy v1 (parents, endpoint split) after human review |
| T3-C06-R1 | COULD | UNANIMOUS | manjot | 1-2 | 0 | Reconcile TOOL ledger (297) vs registry (119); coverage census on Food.com steps |
| T3-C07-R1 | SHOULD | UNANIMOUS | manjot | 3-5 code + 1-2 run (non-BBC; rc2 took 50 min on 4 workers) | 0.5 review | Implement SP-002 pre-normalisation in parse_quantity_v2 (versioned rc2 result beside S161), re-run grounding on non-BBC families, report before/after  _(aliases: T9-C06-R3)_ |
| T3-C07-R2 | COULD | UNANIMOUS | mac | 0.5 | 0 | BBC A1 re-run of the SP-002-fixed grounding on the Mac (BBC has only 188 U+2044 lines; low urgency) |
| T3-C07-R3 | MUST | UNANIMOUS | human | 1 (sourcing check) | 0.5-1 | Decision: how Food.com no-unit lines are treated (presence-only composition; or find original data with units; or flagged imputation) _(aliases: T0-C03-R4, T9-C28-R3)_ |
| T3-C07-R4 | SHOULD | UNANIMOUS | manjot | 1-2 | 0 | Empirical measurement: share of Food.com lines whose quantity is a bare count vs whether NER UNIT/QUANTITY ratio agrees (confirm the unit-drop mechani |
| T3-C08-R1 | SHOULD | AMENDED | manjot | 4-6 | 0 | Build POR candidate records from SR Legacy food_portion (basis SR_PORTION, interval low/high, sample_count) after the C04 decision |
| T3-C08-R2 | SHOULD | AMENDED | manjot | 2-3 | 0 | Re-run rc2 grounding with ingredient links + POR supplied; report Q-level distribution by family |
| T3-C08-R3 | COULD | UNANIMOUS | human | 1 | 2-4 | Human verification of the top ~100 portion records by usage |
| T3-C08-R4 | COULD | UNANIMOUS | manjot | 3-4 | 0 | Empirical portion distributions per ING from stated-mass lines (§235.8) for sanity cross-check of SR portions |
| T3-C09-R1 | SHOULD | UNANIMOUS | manjot | 4-6 | 0 | NER vs Rung A mention agreement diagnostic (span overlap, FOOD span in lexicon-missed lines), counts-only, labelled DIAGNOSTIC not gold |
| T3-C09-R2 | COULD | UNANIMOUS | vinayak | 3-5 | 0 | MENTION ledger DRAFT as a git-ignored derived table (mention_id, line_id, span offsets, label, model hash, confidence) plus a counts-only committed sc |
| T3-C09-R3 | COULD | UNANIMOUS | mac | 1-2 | 0 | Tag BBC ingredient lines on the Mac (CPU/MPS) for completeness, counts-only |
| T3-C09-R4 | SHOULD | UNANIMOUS | human | 2 | 3-5 (Kush+Parv, UNVERIFIED) | Small human-labelled Food.com line sample (200-300 lines) to measure NER and Rung A accuracy under no-unit shift |
| T3-C09-R5 | COULD | UNANIMOUS | human | 0.5 | 0.5 | Decide retrain vs accept (Q34): fine-tune on unit-less Food.com lines or accept |
| T3-C10-R1 | COULD | UNANIMOUS | vinayak | 6-10 | 0.5 | Decision and run: link unique normalised FOOD spans (deduped) with the frozen CD-L2 or BGE top-1 for lines Rung A failed to link; output as MODEL_DERI |
| T3-C10-R2 | COULD | UNANIMOUS | manjot | 2 | 0 | Measure how much composition coverage (mention mass) linker adds over Rung A lexicon |
| T3-C11-R1 | SHOULD | UNANIMOUS | mac | 4-6 (BBC recipes need the Mac; Food.com on manjot) | 0.5 | Diagnostic comparison of Rung A events against the P1 gold (7 recipes) and the 40 AI-assisted dev-Gold recipes using tools/eval_compiler_vs_gold.py, l _(aliases: T0-C03-R1)_ |
| T3-C11-R2 | SHOULD | UNANIMOUS | human | 3-4 (sample + prereg) | 4-6 (labelling) | Per-rule precision audit on a seeded sample for the 5 highest-volume rules (COMBINE_WITH_CURRENT, AMBIGUOUS_REFERENCE, LEXICAL_COREF_DESCENDANT, PLURA |
| T3-C11-R3 | COULD | UNANIMOUS | human | 0.5 | 1 | Review the 4,511 inverted-interval V2 cases summary and decide the rule (UNKNOWN vs swap) |
| T3-C11-R4 | COULD | UNANIMOUS | manjot | 1-2 + Mac 0.5 | 0 | Re-run Rung A after SP-002 + vocab fixes with a version bump on non-BBC families on manjot (CPU 32 workers) and BBC on Mac |
| T3-C11-R5 | AFTER | UNANIMOUS | vinayak | 40-80 | 0 | Rung B/C extraction cascade (local LLM + V1-V6 + two-model disagreement + confident learning) |
| T3-C12-R1 | SHOULD | UNANIMOUS | manjot | 4-6 | 0 | Replay-invariant property tests at corpus scale (order, consumption, split fractions sum, no resurrection of discarded lots) with counts-only violatio |
| T3-C12-R2 | COULD | UNANIMOUS | any | 2-3 | 0 | G18 gate record: replay agreement with P1/P1b gold alive-entity and process-link metrics |
| T3-C12-R3 | SHOULD | UNANIMOUS | any | 4-6 | 0 | Add §233.2 belief fields (timestamp, provenance class, unknown flag) to replay output records per lot-step |
| T3-C13-R1 | SHOULD | UNANIMOUS | manjot | 2-3 | 0 | Measure the fraction of recipes with a fully known or interval-bounded mass graph after C07/C08 fixes (counts-only) |
| T3-C14-R1 | SHOULD | UNANIMOUS | any | 4-6 | 0 | Frame update for P1b: exclude all 21 P1 manifest rows and groups; wave-scoped files and --wave P1b support in pilot_real/pilot_commit/packet maker/sco |
| T3-C15-R1 | SHOULD | UNANIMOUS | any | 2-3 | 0.5 | Write the P1 closeout: report that states the negative gate verdict, the basis caveat, SP triage and what P1b tests; include no model-generated text a |
| T3-C16-R1 | SHOULD | UNANIMOUS | human | 0 | 0.5-1 | Kush supplies size (3 or 4), writes the new nonce, signs the start-record amendment for P1b _(aliases: T9-C13-R3)_ |
| T3-C16-R2 | COULD | UNANIMOUS | human | 3-5 | 6-12 (Kush+Parv; UNVERIFIED, P1 timing not measured) | Run P1b annotation (AI first pass ksh/prv under D-060, human stamps) and score with the same scorer _(aliases: T9-C16-R2)_ |
| T3-C17-R1 | MUST | UNANIMOUS | human | 0.5 | 0.5 | Decision on the minimum gold size and wording for the D3 claim at the talk (diagnostic on 7+40 recipes versus nothing) |
| T3-C17-R2 | SHOULD | UNANIMOUS | any | 2-3 | 0 | Event-type and state-label confusion matrix of Rung A vs P1 gold, counts-only, for the slides |
| T3-C18-R1 | AFTER | UNANIMOUS | human | 1 | 1 | 19-S sizing decision from measured P1/P1b throughput (NEED_HUMAN_CAPACITY if too low) |
| T3-C18-R2 | AFTER | UNANIMOUS | human | 8-12 (tooling, packets) | 40-100 (UNVERIFIED) | Annotate Deep-Gold cohort (fallback 20 recipes at depth A2) and adjudicate |
| T3-C19-R1 | COULD | UNANIMOUS | manjot | 4-6 | 0 | Package the existing Rung A + replay outputs as a documented T0 weak corpus (counts-only manifest, per-recipe file in git-ignored data/derived) with r |
| T3-C19-R2 | AFTER | UNANIMOUS | any | 3-4 | 0 | §257P checklist status report for Step 20 gates |
| T3-C19-R3 | AFTER | UNANIMOUS | human | 0.5 | 1-2 | H2 licence decision for Food.com / TASTEset / A1 (LLM processing, training) |
| T3-C19-R4 | AFTER | UNANIMOUS | vinayak | 40-80 | 30-60 audit labels (UNVERIFIED) | T1 Silver pilot 1k -> 5k -> 10k (LLM cascade) with batch audits |
| T3-C20-R1 | SHOULD | UNANIMOUS | manjot | 2-3 | 0 | State the calibration caveat on every split used by T3 items; add a conservative union grouping check (exact U provisional family U title) for any gol |
| T3-C20-R2 | SHOULD | UNANIMOUS | human | 3-4 | 3-5 | 07I-C family threshold calibration on a human-labelled pair sample _(aliases: T7-C13-R2)_ |
| T3-C21-R1 | SHOULD | UNANIMOUS | any | 4-6 | 0 | Draft SVAR v1.1 physical/history registry (definitions, units, allowed types, UNKNOWN semantics) as additive file; no write to SVAR.jsonl |
| T3-C22-R1 | SHOULD | AMENDED | manjot | 10-16 | 0 | Step 1-2 slice: lot members + presence-only composition from ING->SR match; mass interval only where grams are known (UNKNOWN otherwise); record per l _(aliases: T0-C03-R3)_ |
| T3-C22-R2 | SHOULD | AMENDED | manjot | 4-6 | 0 | FDA pH registry (draft exists, lane L-PH): human-verify source status and parse, wire to the ING crosswalk, and record whether member pH enters Layer  |
| T3-C22-R3 | COULD | AMENDED | any | 4-6 | 0 | Solute load (g salt, g sugar per g water) and water-activity estimate as MODEL_DERIVED intervals, only where masses are known |
| T3-C22-R5 | COULD | UNANIMOUS | manjot | 20-30 | 0 | Non-heat process families feeding the same lot record (cool, drain, marinate/brine, dry, cut, mix, rest, store) as TEXT_STATED/SCENARIO records |
| T3-C22-R6 | COULD | AMENDED | manjot | 3-5 (run) + Mac 1 | 0 | Full-corpus lot-state run on manjot (non-BBC) with nice -n 10, 32 workers; BBC on the Mac; counts-only reports; outputs in data/derived |
| T3-C22-R7 | MUST | AMENDED | human | 0.5 | 0.5 | Decision Q39: is lot-state worth doing before 25 Nov versus all time on H1/H3 + first SIMULATE; fix the minimal slice |
| T3-C23-R1 | SHOULD | UNANIMOUS | any | 1-2 | 0 | Record Food.com licence/units limitations in a one-page data card (counts-only) used by every T3 report |
| T3-C24-R1 | SHOULD | UNANIMOUS | any | 8-14 | 0 | Extract the Q and V cases into a machine-readable fixture file (text only from SSOT; no third-party text) and run rc2 / vocab / link against it as a c |
| T3-C24-R2 | COULD | UNANIMOUS | human | 1 | 2-3 | Human spot review of failing cases to decide code fix vs SSOT note |
| T3-C25-R1 | SHOULD | UNANIMOUS | human | 2-3 | 1-2 | Write a short design note fixing belief fields and class tags (source/semantic/episode/evidence/model) for every lot-step field; reviewed by Kush/Parv |

Topic contradictions recorded by the inventory: 7; SSOT requirements without plan coverage: 7 (see `topics/T3.json`). Resolved by round 1: Rung A count (T0/T3/T7/T9), defaults 27 rows (T4), SVAR 224 ids vs 254 rows (T0/T9), EVD lines vs ids (T2), physical % sample vs full corpus (T4/T5: use T4 full-corpus 3.4 % / 5.3 %).

### T4 — Process conditions and physics (L14 process representation, condition schema, D-077 physical-state dataset, non-heat families, Step 31)
Open items 52 (MUST 5, SHOULD 20, COULD 14, AFTER 13); consensus UNANIMOUS 49, AMENDED 2, CONTESTED 1.

| Component | Status | Open items | Component notes |
|---|---|---|---|
| T4-C01 Process ontology and PROC representation (hierarchy family/leaf, media | DRAFT | 3 |  |
| T4-C02 Condition schema: raw-first typed condition tuple, POINT/INTERVAL/QUAL | RUN | 1 |  |
| T4-C03 Endpoint leakage and qualitative heat words ('until golden', 'medium h | CODE | 1 |  |
| T4-C04 Layer 1 TEXT_STATED binder over the full corpus (heat families) | RUN | 2 |  |
| T4-C05 Layer 2 SCENARIO driver trajectories (GENTLE/TYPICAL/INTENSE) for heat | RUN | 3 |  |
| T4-C06 Scenario defaults registry (27 rows: bath T, gas marks, h, k, alpha, h | DRAFT | 1 | R-SSOT+R-SCI: count fix: registry/scenario_defaults_v1.csv has 27 data rows (28 lines incl. header), all SOURCE_UNVERIFIED_AGENT_RECALLED (re-counted by SYNTH: 27); non-heat defaults are a separate 40-row registry |
| T4-C07 Heat-conduction physics driver (infinite slab, convective boundary) an | RUN | 2 |  |
| T4-C08 Geometry model: shape and size per cut class (slab, cylinder, sphere,  | CODE | 2 | R-SSOT: status ->CODE (partial): slab (tested) + cube A/V helper (untracked L-NH); no cylinder/sphere |
| T4-C09 Surface versus core temperature and drying-front/evaporative boundary  | CODE | 2 | R-SSOT: status ->CODE (partial: drying-only moisture state via nonheat_drivers.drying_state; SSOT L6042-6048 gap remains for heat families) |
| T4-C10 Choi-Okos thermophysical property model and Biot-based lumped-capacita | CODE | 2 |  |
| T4-C11 Non-heat Layer 1 binder and scenario registry extension (shared infras | CODE | 3 | R-SSOT: status NOT_STARTED->CODE: untracked L-NH lane registry/scenario_defaults_nonheat_v1.csv (40 rows) + src/culinarystate/simulation/nonheat_drivers.py; SYNTH also saw untracked nonheat_binding.py (census_from_records); SOURCE_UNVERIFIED defaults, no corpu |
| T4-C12 COOLING family (chill, cool, freeze, defrost): conduction with cold ba | CODE | 2 |  |
| T4-C13 SEPARATION family (drain, strain, rinse, soak-discard): leaching compa | NOT_STARTED | 2 | R-SSOT: status stays NOT_STARTED; evidence: only default row NH-080 in registry/scenario_defaults_nonheat_v1.csv, no driver function |
| T4-C14 FERMENT_LEAVEN / marinate / brine / soak: Fickian slab uptake, pH stat | CODE | 3 |  |
| T4-C15 PRESERVATION family (dry, pickle, pasteurise, sterilise, can): drying  | CODE | 2 | R-SSOT: status ->CODE (partial: drying_state + f0_minutes, defaults NH-050..054, NH-060/061; pickle/pasteurise-by-pH not covered) |
| T4-C16 MECHANICAL_CUT family: cut class to size, surface/volume, enzyme-activ | CODE | 2 | R-SSOT: status ->CODE (partial: half_thickness NH-070, cube_av/slab_av) |
| T4-C17 MECHANICAL_MIX family: qualitative flags AERATED, EMULSIFIED, DEVELOPE | NOT_STARTED | 2 |  |
| T4-C18 RESTING family: carry-over heating and moisture redistribution | NOT_STARTED | 2 |  |
| T4-C19 STORAGE family (store, refrigerated, room temperature): Arrhenius kine | NOT_STARTED | 3 |  |
| T4-C20 Physical-state dataset packaging: record schema, dataset card, provena | CODE | 1 |  |
| T4-C21 Step 26g recipe-event to simulation-input adapter and simulability cen | RUN | 1 |  |
| T4-C22 Step 31 physics/condition features (31.0 census, 31a generic features, | BLOCKED | 5 |  |
| T4-C23 Equipment, altitude and oven calibration uncertainty as Layer 2 spread | NOT_STARTED | 2 |  |
| T4-C24 Learned numerical embeddings, dense trajectory encoders, neural ODE/CD | OUT_OF_SCOPE | 1 |  |
| T4-C25 Physical-state results for talk and report: honest limits, figures, cl | NOT_STARTED | 1 |  |
| T4-C26 Layer 1 TEXT_STATED binder precision audit | NOT_STARTED | 1 | R-SCI: new component proposed |

| Item | Pri | Consensus | Where | Agent h | Human h | Item (short) |
|---|---|---|---|---|---|---|
| T4-C01-R1 | SHOULD | UNANIMOUS | any | 3-5 | 1-2 | Freeze a PROC to process-family registry (one row per PROC, one primary family, secondary flag) covering all 93 PROCs and the 8 non-heat families, wit |
| T4-C01-R2 | SHOULD | UNANIMOUS | human | 0 | 2-3 | Human review of the 27 process_medium_map rows and PROC mechanism_families for the physical families (Kush/Parv; AI personas may only propose) |
| T4-C01-R3 | AFTER | UNANIMOUS | any | 4-8 | 0 | Map PROC leaves to FoodOn/LanguaL process terms as a side table (no replacement of the custom hierarchy) |
| T4-C02-R2 | SHOULD | UNANIMOUS | any | 3-5 | 0 | Add per-axis provenance (basis code, span id, layer L1/L2) to the physical-record schema so every field is the SSOT tuple (value,unit,type,mask,proven |
| T4-C03-R1 | SHOULD | UNANIMOUS | vinayak | 4-6 | 0 | Add endpoint-cue extractor output (stopping criterion field) and a leakage unit test plus corpus count of endpoint cues per heat event |
| T4-C04-R1 | MUST | UNANIMOUS | any | 3-5 | 1 | Write 'what the corpus can say' analysis: coverage by family, source and process, share with both t and T, ranges, gas-mark-only, per-family top unbou |
| T4-C04-R2 | COULD | UNANIMOUS | any | 6-10 | 0 | Extend binder to bind lid, pressure (pressure-cooker), start mode, product vs medium temperature and water:food ratio where stated (Step 26 EVT fields |
| T4-C05-R1 | SHOULD | UNANIMOUS | any | 2-4 | 0 | Sensitivity report: bracket width (INTENSE-GENTLE) per family, share of events where bracket spread changes a qualitative conclusion (e.g. core reache |
| T4-C05-R2 | COULD | AMENDED | vinayak | 5-8 | 0 | Reduce UNKNOWN: add default durations per PROC where text lacks time (cited quantile source) and more media defaults, keeping UNKNOWN-first rule |
| T4-C05-R3 | SHOULD | UNANIMOUS | any | 3-5 | 1 | Q1 circularity control: basis masks on every Layer 2 feature plus an ablation that removes Layer 2 before any use in Steps 30-35 (lean b of packet) _(aliases: T0-C04-R4)_ |
| T4-C06-R3 | SHOULD | UNANIMOUS | any | 4-6 | 0 | Add defaults for non-heat families (cold bath T fridge/freezer, brine strength, soak durations, drying air T/RH, storage T, cut half-thickness for cub |
| T4-C07-R1 | SHOULD | UNANIMOUS | any | 3-5 | 0 | Verification pack: compare slab series with a finite-difference solve and with textbook chart values for several (Bi, Fo); report max error; add conve |
| T4-C07-R2 | COULD | UNANIMOUS | any | 4-6 | 1 | Arrhenius exposure integral Omega with representative Ea grid and temperature-trajectory input (needs literature Ea per target class, not tuned on tes |
| T4-C08-R1 | SHOULD | UNANIMOUS | any | 5-8 | 0 | Add finite-cylinder and sphere eigen-series (Bi roots, Heisler products) and a cut-class/ingredient-class to shape map, keeping slab as the stated bou _(aliases: T0-C04-R3, T5-C09-R2)_ |
| T4-C08-R2 | COULD | UNANIMOUS | any | 3-5 | 1 | Whole-item size defaults (potato, egg, chicken, joint) as ranges with source |
| T4-C09-R1 | MUST | UNANIMOUS | human | 0 | 0.5-1 | Decide scope: two-zone surface model (surface at ~100 C until dry) QUALITATIVE only, or leave as stated limitation for 25 Nov |
| T4-C09-R2 | COULD | UNANIMOUS | any | 8-14 | 1 | If built: two-zone surface/drying-front driver giving time-to-surface-dry and surface temperature bracket, flagged QUALITATIVE_ONLY |
| T4-C10-R1 | SHOULD | UNANIMOUS | any | 2-4 | 0 | Verify Choi-Okos coefficients against the 1986 paper or Rahman handbook, record page cites |
| T4-C10-R2 | COULD | UNANIMOUS | any | 4-6 | 0 | Wire Choi-Okos into Layer 2 where lot composition is known (water, fat, protein fractions), otherwise keep defaults |
| T4-C11-R1 | MUST | UNANIMOUS | vinayak | 2-4 | 0 | Census of events per non-heat family across the full corpus (counts, how many state time/T/medium/size) to size the work and rank families by volume |
| T4-C11-R2 | SHOULD | UNANIMOUS | any | 8-14 | 0 | Generalise Binder to the non-heat families (time, target T, medium, size where stated, else UNKNOWN) with tests on constructed and real samples |
| T4-C11-R3 | SHOULD | UNANIMOUS | vinayak | 2-4 | 0 | Full-corpus non-heat L1 run on non-BBC families, BBC on Mac, counts-only reports and run log rows _(aliases: T0-C04-R2)_ |
| T4-C12-R1 | SHOULD | UNANIMOUS | any | 6-12 | 0.5 | Build driver + scenario defaults + Layer 1 binding for COOLING family and unit tests |
| T4-C12-R2 | SHOULD | UNANIMOUS | vinayak | 1-2 | 0 | Full non-BBC corpus run and counts-only report for COOLING family with run-log rows |
| T4-C13-R1 | COULD | UNANIMOUS | any | 6-12 | 0.5 | Build driver + scenario defaults + Layer 1 binding for SEPARATION family and unit tests |
| T4-C13-R2 | COULD | UNANIMOUS | vinayak | 1-2 | 0 | Full non-BBC corpus run and counts-only report for SEPARATION family with run-log rows |
| T4-C14-R1 | SHOULD | UNANIMOUS | any | 6-12 | 0.5 | Build driver + scenario defaults + Layer 1 binding for FERMENT_LEAVEN family and unit tests |
| T4-C14-R2 | SHOULD | UNANIMOUS | vinayak | 1-2 | 0 | Full non-BBC corpus run and counts-only report for FERMENT_LEAVEN family with run-log rows |
| T4-C14-R3 | SHOULD | UNANIMOUS | any | 3-5 | 0 | Source diffusion coefficients (salt, acid, sugar in meat/vegetable) as ranges from handbooks |
| T4-C15-R1 | AFTER | UNANIMOUS | any | 6-12 | 0.5 | Build driver + scenario defaults + Layer 1 binding for PRESERVATION family and unit tests |
| T4-C15-R2 | AFTER | UNANIMOUS | vinayak | 1-2 | 0 | Full non-BBC corpus run and counts-only report for PRESERVATION family with run-log rows |
| T4-C16-R1 | COULD | UNANIMOUS | any | 6-12 | 0.5 | Build driver + scenario defaults + Layer 1 binding for MECHANICAL_CUT family and unit tests |
| T4-C16-R2 | COULD | UNANIMOUS | vinayak | 1-2 | 0 | Full non-BBC corpus run and counts-only report for MECHANICAL_CUT family with run-log rows |
| T4-C17-R1 | AFTER | UNANIMOUS | any | 2-4 | 0.5 | Build driver + scenario defaults + Layer 1 binding for MECHANICAL_MIX family and unit tests |
| T4-C17-R2 | AFTER | UNANIMOUS | vinayak | 1-2 | 0 | Full non-BBC corpus run and counts-only report for MECHANICAL_MIX family with run-log rows |
| T4-C18-R1 | COULD | UNANIMOUS | any | 6-12 | 0.5 | Build driver + scenario defaults + Layer 1 binding for RESTING family and unit tests |
| T4-C18-R2 | COULD | UNANIMOUS | vinayak | 1-2 | 0 | Full non-BBC corpus run and counts-only report for RESTING family with run-log rows |
| T4-C19-R1 | AFTER | UNANIMOUS | any | 6-12 | 0.5 | Build driver + scenario defaults + Layer 1 binding for STORAGE family and unit tests |
| T4-C19-R2 | AFTER | UNANIMOUS | vinayak | 1-2 | 0 | Full non-BBC corpus run and counts-only report for STORAGE family with run-log rows |
| T4-C19-R3 | AFTER | UNANIMOUS | manjot | 4-8 | 2-4 | Storage kinetics entry through Step 32 PARAM for one system (likely ascorbic acid at storage T) |
| T4-C20-R2 | SHOULD | UNANIMOUS | manjot | 3-5 (job hours ~4-8) | 0 | Reproduce FOODCOM L1/L2 on a second host (manjot, 16-32 workers) and compare counts and hashes |
| T4-C21-R1 | SHOULD | UNANIMOUS | vinayak | 4-6 | 0 | Re-run 26g census with Layer 1 bindings supplying T, t, medium and size so MISSING_* reasons drop for bound events; keep SIMULATE 0 until PARAM human  |
| T4-C22-R1 | MUST | UNANIMOUS | human | 0 | 1 | Decide how Layer 1/2 features enter Step 31: EVD-row arm only (as in plan) or add a recipe-event diagnostic arm with Layer 2 masked (Q1) _(aliases: T5-C09-R3)_ |
| T4-C22-R2 | COULD | UNANIMOUS | manjot | 3-5 | 0 | 31.0 cooking-vs-storage census of lineage components with within-study condition variation (data present in EVD/COND) |
| T4-C22-R3 | AFTER | UNANIMOUS | any | 8-12 | 0 | Build physics_feature_registry_v1.csv and 31a feature code (raw, log(1+t), 1/T_K, bounds, dose, time above threshold) inside Step 30 harness |
| T4-C22-R4 | AFTER | UNANIMOUS | manjot | 8-14 | 3 | Run condition-contribution ablation A1..A5 with paired cluster CIs; pre-registration signed by Kush |
| T4-C22-R5 | AFTER | UNANIMOUS | human | 0 | 4 | Expert review of Ea grid, temperature semantics (setpoint vs product) and heat-mode map |
| T4-C23-R1 | COULD | UNANIMOUS | human | 0 | 0.5 | Decide: add as extra Layer 2 spread or state as out of scope |
| T4-C23-R2 | AFTER | UNANIMOUS | any | 2-3 | 0 | If added: altitude-dependent boil T and oven offset parameter in scenario layer |
| T4-C24-R1 | AFTER | UNANIMOUS | human | 0 | 0.5 | Revisit after G15-2 passes and focused kinetic data exist |
| T4-C25-R1 | MUST | AMENDED | any | 3-5 | 1 each | Draft physical-layer slides/figures (coverage funnel, bracket spread, UNKNOWN reasons, non-heat families status) with wording audit against §141 |
| T4-C26-R1 | SHOULD | CONTESTED | manjot (non-BBC) + Mac (BBC) | 3-4 | 1-2 | Layer 1 binder precision audit: seeded random sample (pre-declared n, e.g. 200 bound heat events stratified by family) checked against the text span f |

Topic contradictions recorded by the inventory: 6; SSOT requirements without plan coverage: 7 (see `topics/T4.json`). Resolved by round 1: Rung A count (T0/T3/T7/T9), defaults 27 rows (T4), SVAR 224 ids vs 254 rows (T0/T9), EVD lines vs ids (T2), physical % sample vs full corpus (T4/T5: use T4 full-corpus 3.4 % / 5.3 %).

### T5 — Mechanisms, kinetics and simulation
Open items 57 (MUST 12, SHOULD 19, COULD 14, AFTER 12); consensus UNANIMOUS 44, AMENDED 11, CONTESTED 2.

| Component | Status | Open items | Component notes |
|---|---|---|---|
| T5-C01 Mechanism registry MECH (ontology, 32-entry roster, schema v1.1) | DRAFT | 7 |  |
| T5-C02 Mechanism condition-window registry, mechanism screen and interaction  | NOT_STARTED | 4 |  |
| T5-C03 Effect-type, condition-gate-type and token vocabularies | DRAFT | 1 |  |
| T5-C04 Event->effect signatures (Step 22): EFFSIG layer, shared case set, sea | CODE | 4 |  |
| T5-C05 Applicability / formula router 23a (APPDEC engine, gates G0-G9, Kleene | RUN | 6 | R-SSOT: 23a applicability/formula router, distinct from the §39 query router (T0-C08/T8-C01) |
| T5-C06 Router 23b: scientific application to real COND rows (07.A-gated) | BLOCKED | 1 |  |
| T5-C07 Formula/parameter/validation registry FORM, PARAM, VAL (Step 24) and p | CODE | 5 |  |
| T5-C08 Kinetic evidence contract KIN/KINPT v1.1, censoring, units, minimal ki | CODE | 1 |  |
| T5-C09 Counts-only physical drivers: Layer 1 TEXT_STATED binding, Layer 2 SCE | RUN | 0 | R-SSOT: xref to T4-C04/C05/C07; numeric claims dropped (T5 3.3%/4.8% = 1,000-recipe sample; T4 3.4%/5.3% = full corpus, use T4) |
| T5-C10 M3 ascorbic-acid pilot (Step 10 reduced, D-076): extraction, verificat | BLOCKED | 3 | R-SSOT: split proposed: T2-C09 owns evidence extraction/verification, T5-C10 owns fit/PARAM (ownership CONTESTED C02) |
| T5-C11 Simulator sim_aa_1 (two-compartment AA degradation + lumped leaching)  | CODE | 6 |  |
| T5-C12 Verification and synthetic-recovery harness (26c, G26-VER) and identif | CODE | 2 |  |
| T5-C13 Held-out validation of the simulator (Step 27, SIM-VAL / lockbox) | BLOCKED | 4 |  |
| T5-C14 Second system sim_chl_1 (chlorophyll to pheophytin, pH-gated) fallback | CODE | 1 |  |
| T5-C15 Focused kinetics hierarchy (Step 32) and classical kinetics baselines  | CODE | 2 |  |
| T5-C16 Hybrid mechanistic-neural models and UDE (D9, D10, D11, G15-HYB) | OUT_OF_SCOPE | 1 |  |
| T5-C17 Reaction-network learning (species graph, stoichiometric dynamics, RXN | OUT_OF_SCOPE | 1 |  |
| T5-C18 Counterfactual and inverse design (forward credibility ceiling, feasib | OUT_OF_SCOPE | 2 |  |
| T5-C19 Rollout trust horizon and open-system balance (R0-R5, constraint categ | OUT_OF_SCOPE | 1 | R-SSOT: OUT_OF_SCOPE for run; DRAFT scaffold owned by T6-C15 |
| T5-C20 E7 synthetic prior generator (Step 28) and simulator pretraining | OUT_OF_SCOPE | 1 |  |
| T5-C21 Claim-ladder enforcement, G15 gate scorecard and Level-15 decision rec | NOT_STARTED | 3 |  |
| T5-C22 Cross-layer separation and §141 emit firewall (screen, router, SIMULAT | NOT_STARTED | 1 | R-SCI: new component proposed |

| Item | Pri | Consensus | Where | Agent h | Human h | Item (short) |
|---|---|---|---|---|---|---|
| T5-C01-R1 | SHOULD | AMENDED | any | 6-8 | 0 | Author 20-32 MECH entries as JSONL from the roster, each with >=1 evidence id with document type (use EVD/SRC/DOC ids already in repo; literature DOC  |
| T5-C01-R2 | SHOULD | AMENDED | any | 4-6 | 0 | Pre-build the 32-entry screen subset needed by the lot-state mechanism screen (alliinase, onion LFS, PPO, myrosinase, Maillard, caramelisation, starch |
| T5-C01-R3 | SHOULD | UNANIMOUS | human | 0 | 12-20 (Kush 6-10, Parv 6-10) | Blind dual review of every entry (Kush, Parv) plus adjudication log with technical independence safeguards (07H provenance failures); under D-071 AI p _(aliases: T0-C05-R5)_ |
| T5-C01-R4 | SHOULD | UNANIMOUS | human | 1-2 | 1-2 | H4 decisions D21-1..D21-8 (MECH prefix, plane P-MOD, edge_semantics STATE_TRANSITION, effect-type additions, bound statuses, family tokens, directions |
| T5-C01-R5 | COULD | UNANIMOUS | human | 1-2 (prepare packet) | 4-8 expert | Food-chemistry expert answers to EQ21-01..14 (aerobic/anaerobic AA pathway, ascorbate oxidase, chlorophyllase, SBO ids, analyte-form tokens, window ne |
| T5-C01-R6 | SHOULD | UNANIMOUS | any | 3-5 | 3-6 (Parv owner, Kush reviewer) | PROC->MECH crosswalk for 156 PROC (HV-010): AI-draft all, humans verify the PROC used by the AA pilot and blanch/boil/steam/simmer (G21.7). |
| T5-C01-R7 | AFTER | UNANIMOUS | any | 4-8 | 2-3 | Mechanism xref table (SBO/GO/ChEBI/KEGG/FoodOn) with collision audit; 0 xrefs ACCEPTED without a human. |
| T5-C02-R1 | COULD | AMENDED | any | 10-18 | 0 | Build mechanism condition-window registry for ~14 screen mechanisms: window interval, matrix scope, gate type, source id (primary source opened) and r |
| T5-C02-R2 | SHOULD | AMENDED | any | 8-14 | 0 | Implement the Kleene three-valued mechanism screen (reactants present / drivers in window / inhibitors) over lot state producing POSSIBLE / NOT_POSSIB _(aliases: T3-C22-R4)_ |
| T5-C02-R3 | SHOULD | UNANIMOUS | vinayak | 1-2 (compute 1-3 h wall) | 0 | Full-corpus run of the screen on non-BBC families (Food.com 522,517; Gutenberg 73,955; Wikibooks 3,676; TASTESET 700) and BBC on Mac only. |
| T5-C02-R4 | SHOULD | AMENDED | human | 0 | 0.5-1 | Decision Q21: may POSSIBLE screens from unreviewed MECH give QUALITATIVE direction labelled AI_DRAFTED; Q15 acceptable sources for windows. |
| T5-C03-R1 | COULD | UNANIMOUS | any | 3-5 | 1 | Freeze vocabularies (drop _DRAFT suffix) after H4; add analyte-form token registry; map route enum to §214.30 evidence-class labels in a documented ta |
| T5-C04-R1 | COULD | UNANIMOUS | human | 3-5 (templates, AI-assisted drafts labelled) | 10-18 (Kush 6-10, Parv 4-8) | Author >=72 (plan card) or 250 (packet figure) shared mechanism cases (event + state -> expected candidate MECH set) BEFORE any rules; Kush authors, P |
| T5-C04-R2 | COULD | UNANIMOUS | human | 0.5 | 0.5-1 | Seal the case set with a human-held nonce (D-071: AI cannot set nonce) and record manifest; only then author rules. |
| T5-C04-R3 | AFTER | UNANIMOUS | any | 8-12 | 1 | Author signature rules from non-test cases and run G22.1-G22.5 (recall>=0.90 Wilson LB>=0.80, B1 precision>=B0, process-label permutation drop>=0.30,  |
| T5-C04-R4 | AFTER | UNANIMOUS | vinayak | 3-5 | 0.5 | Freeze EFFSIG schema and generate 22b event candidate export over the corpus (regenerable). |
| T5-C05-R1 | MUST | AMENDED | mac | 0.5 | 0 | Install hypothesis in an env where installs are allowed (Mac or vinayak) and run the >=10^4 randomised property test 'UNKNOWN/NOT_APPLICABLE never rea |
| T5-C05-R2 | SHOULD | AMENDED | vinayak | 2-4 | 0 | Router re-run on the full non-BBC corpus after lot state + mechanism screen + PARAM exist (targets beyond vitamin C where EVD has rows), counts-only;  _(aliases: T8-C08-R2)_ |
| T5-C05-R3 | SHOULD | UNANIMOUS | any | 4-8 | 0 | Extend router targets from vitamin C to every SVAR with EVD rows (folate, thiamin, carotene etc.) for the DIRECT/INTERPOLATE paths; keep SIMULATE only |
| T5-C05-R4 | MUST | UNANIMOUS | human | 0 | 1 | Decisions Q20 (is mostly-UNKNOWN a result), Q22 (what counts as bracketing), Q23 (ASK rule) for the demo. _(aliases: T6-C17-R2)_ |
| T5-C05-R5 | AFTER | UNANIMOUS | human | 3-5 | 6-10 + expert 6-10 | Pre-register false-activation tolerance and B0/B2 baselines; prepare locked test set from Step-11 verified positives/negatives labelled by someone oth |
| T5-C05-R6 | COULD | UNANIMOUS | any | 1-2 | 0 | Deliver UNKNOWN census (G23.6) on DATA-EVIDENCE v1 to Step 14 in the agreed format (reformat existing census). |
| T5-C06-R2 | SHOULD | UNANIMOUS | any | 3-5 | 0.5 | If 07.A PASS and 15b frozen: run 23b on real COND rows and report. |
| T5-C07-R1 | MUST | UNANIMOUS | human | 0.5 | 0.5-1 | DECISION: FORM- prefix (vs MODEL-), freeze FORM/PARAM/VAL schemas. |
| T5-C07-R2 | SHOULD | UNANIMOUS | any | 6-10 | 1-2 review | Mint FORM rows for first-order Arrhenius AA (reference-T form), zero-order and Weibull stubs; reproduce >=1 source figure/table within tolerance (/dC/ |
| T5-C07-R3 | MUST | UNANIMOUS | any | 2-4 | 0 | Mint PARAM rows ONLY from rows both humans VERIFIED (K>=K1, source locator, fitted_on block); automated check 0 PARAM from K0 aggregates. |
| T5-C07-R4 | COULD | UNANIMOUS | any | 10-16 | 4-6 Kush + 3-5 Parv label | Build standalone param_compat retrieval (categorical axis match vector, NO_COMPATIBLE_SET with reasons, ensemble/CONFLICT, domain location) and a >=60 |
| T5-C07-R5 | SHOULD | UNANIMOUS | any | 1-2 | 0 | Kinetic units rows (min^-1, s^-1, kJ/mol, kcal/mol) into UNIT ledger via orchestrator; wire units.py checks to ledger. |
| T5-C08-R1 | SHOULD | UNANIMOUS | any | 3-5 | 1 | Freeze KIN/KINPT after AA rows exist to test it; write AA pilot rows into KIN/KINPT form (not only a CSV packet). |
| T5-C10-R5 | MUST | AMENDED | any | 3-5 | 0.5 | Fit Model A on verified SIM-CAL rows, run Model B sensitivity, freeze fit JSON with sha256 and code hash BEFORE any SIM-VAL text is opened; ensure rep _(aliases: T2-C09-R5, T0-C05-R3, T6-C13-R2)_ |
| T5-C10-R6 | MUST | CONTESTED | any | 3-5 | 1.5-2 each (4 papers) | Then extract and verify SIM-VAL rows (AAK-12/07/03/05) and compute descriptive prediction error and interval coverage (Step 27 pilot). _(aliases: T2-C09-R6)_ |
| T5-C10-R7 | COULD | UNANIMOUS | any | 3-6 | 1-2 | Find at least one extra AA source with cooking-water/leachate assay or water-immersion design so k_L and K_p are not UNKNOWN (optional). |
| T5-C11-R1 | SHOULD | UNANIMOUS | human | 1-2 (draft) | 1-2 | Pre-register G26-VER/G26-CAL numbers and the exact no-water-assay design (O6); sign (separate files). |
| T5-C11-R2 | COULD | UNANIMOUS | human | 2-4 | 2-4 + expert 4-8 | H5 inputs: Choi-Okos coefficient check vs source, tau_h per size class, M&S limits, solver tolerances, KiSAO id check; food-engineer review of equatio |
| T5-C11-R3 | MUST | AMENDED | any | 6-10 | 1 | Calibrate sim_aa_1 with frozen Model A PARAM (26d on SIM-CAL only), produce calibration report + identifiability report on real data; issue SIMM-AA-1  |
| T5-C11-R4 | MUST | AMENDED | any | 6-10 | 0 | Wire router SIMULATE branch end-to-end: eligible AA events (steam/sealed medium) -> retention INTERVAL with PARAM id and basis; all else UNKNOWN; reco |
| T5-C11-R5 | COULD | UNANIMOUS | vinayak | 4-6 | 0 | SIM ledger writer with firewall tests and SIMLINK_v1 link table for the corpus (additive, counts-only, SIM plane). |
| T5-C11-R6 | SHOULD | UNANIMOUS | vinayak | 2-3 | 0 | Recipe simulability census v1 re-run with calibrated sim_aa_1 (counts only). |
| T5-C12-R1 | SHOULD | UNANIMOUS | manjot | 3-5 (compute ~1-2 h CPU) | 0.5 | Run the pre-registered G26-VER suite and the >=200-dataset recovery grid; write verification_report_v1.md with pass/fail per criterion. |
| T5-C12-R2 | MUST | UNANIMOUS | any | 2-3 | 0.5 | Identifiability report for the AA pilot fit (profile CI for ln k_ref and Ea; practical-identifiability test). |
| T5-C13-R1 | SHOULD | UNANIMOUS | any | 8-12 | 0 | Implement baselines (S27-B1 persistence/mean-retention, S27-B3) and negative controls NC-1..4 and cluster sign-flip inference; test on synthetic. |
| T5-C13-R2 | SHOULD | UNANIMOUS | human | 4-6 | 3-5 (Kush+Parv) + audit | Write and co-sign Step 27 pre-registration before opening SIM-VAL rows; run single confirmatory analysis; state RESEARCH_ONLY for AA (4 labs) rather t |
| T5-C13-R3 | MUST | AMENDED | human | 0 | 0.5 | Decision: does the talk accept descriptive pilot validation (D-076) in place of the plan's formal gate; record the deviation. |
| T5-C13-R4 | AFTER | UNANIMOUS | any | 10-20 | 8-12 | Collect >=5 independent lab groups of AA kinetic series for a formal VALIDATED_HELD_OUT (new sources, new verification). |
| T5-C14-R1 | AFTER | UNANIMOUS | any | 10-20 | 3-5 | Only if AA fails: 11.D record then chlorophyll literature sweep (K1/K2 series, pH-controlled). |
| T5-C15-R1 | COULD | UNANIMOUS | manjot | 6-10 | 0.5 | After PARAM exist: fit hierarchical Arrhenius, run leave-one-paper-out condition-OOD against best non-kinetic baseline (G15-5 test) only if >=2 matric |
| T5-C15-R2 | AFTER | UNANIMOUS | any | 2-4 | 0.5 | Check licence and scope of Phenol-Explorer time/temperature rows as a second K1 source (non-AA). |
| T5-C16-R1 | AFTER | UNANIMOUS | vinayak | 30-60 | 3-5 | After Step 27 VALIDATED_HELD_OUT: endpoint-residual hybrid first, three-way benchmark, residual-off ablation, //f_NN// vs //f_known//. |
| T5-C17-R1 | AFTER | UNANIMOUS | any | 20-40 | 2-4 | Known-pathway rate fitting A->B->C only if a multi-species AA series (AA, DHA, DKG) is found; randomized-topology and leave-one-reaction controls. |
| T5-C18-R1 | COULD | UNANIMOUS | any | 4-6 | 0.5 | I0 finite counterfactual comparison table over existing DIRECT/EVD retention (same ingredient, different process), with evidence class labels and abst |
| T5-C18-R2 | AFTER | UNANIMOUS | vinayak | 30-50 | 3-5 | Full inverse design (grid, random, LCB, Pareto) within safe support region. |
| T5-C19-R1 | COULD | UNANIMOUS | any | 2-3 | 0 | Report R0/R1 rollout limits honestly in talk (no trust horizon); constraint-violation counters (negative conc, balance) reported for sim_aa_1 only. |
| T5-C20-R1 | AFTER | UNANIMOUS | vinayak | 10-16 | 3-5 | Generate DATA-SIM v1 only from a VALIDATED_HELD_OUT simulator; firewall tests; C-7 span check; ablation controls spec. |
| T5-C21-R1 | MUST | UNANIMOUS | any | 3-5 | 1 | Produce an honest G15 gate scorecard for T5 gates (G15-4,5,8,11,12,HYB,RXN,INV, partial 1,6,7,H,R) with file evidence and PASS/PARTIAL/NOT_MET/NEED_DA |
| T5-C21-R2 | COULD | UNANIMOUS | any | 2-3 | 0.5 | Draft 216.13 decision record items (kinetics identifiable? simulator vs baseline? etc.) as text with NEED_DATA where applicable. |
| T5-C21-R3 | AFTER | UNANIMOUS | human | 0 | 0.5 | Add delta-compatibility type to SVAR design (state-semantics topic owns); here only request. |
| T5-C22-R1 | MUST | CONTESTED | any (Mac for hypothesis) | 4-6 | 0 | Property tests over the composed pipeline: (a) no output from an ASSUMED_DEFAULT/SCENARIO/MODEL_DERIVED input carries evidence_supported; (b) NOT_POSS |

Topic contradictions recorded by the inventory: 8; SSOT requirements without plan coverage: 10 (see `topics/T5.json`). Resolved by round 1: Rung A count (T0/T3/T7/T9), defaults 27 rows (T4), SVAR 224 ids vs 254 rows (T0/T9), EVD lines vs ids (T2), physical % sample vs full corpus (T4/T5: use T4 full-corpus 3.4 % / 5.3 %).

### T6 — Transition learning and sparsity (Steps 29-34, D2, H2)
Open items 51 (MUST 8, SHOULD 10, COULD 4, AFTER 29); consensus UNANIMOUS 48, AMENDED 3, CONTESTED 0.

| Component | Status | Open items | Component notes |
|---|---|---|---|
| T6-C01 Evidence tensor, observation mask, canonical cell definition, data aud | CODE | 3 |  |
| T6-C02 Baseline ladder D0-D5 and D7a implementation + DEL-2 results (the exis | RUN | 3 |  |
| T6-C03 29-diag: cap-stratified rerun and shortcut / D7-equals-D1 audit on the | BLOCKED | 5 |  |
| T6-C04 Hypothesis H2: process information beats food-identity-only models on  | NOT_STARTED | 3 |  |
| T6-C05 Step 29 paper-grade: TRANSITION_BOOTSTRAP_V0 on DATA-EVIDENCE v1 (T1 r | BLOCKED | 3 |  |
| T6-C06 Step 30 strong tabular / sparsity bake-off harness and models (D3-full | CODE | 4 |  |
| T6-C07 Evidence-aware sparse completion D7 (biased MF, BPMF, side-info MF/Mac | CODE | 4 |  |
| T6-C08 MNAR / observation-propensity / IPW / doubly-robust / popularity-bucke | CODE | 3 |  |
| T6-C09 Censoring, imputation, missingness-mask and anti-inflation rules (trai | CODE | 3 |  |
| T6-C10 Conformal intervals, calibration and selective abstention for transiti | CODE | 2 | R-SSOT: cross-references T9-C12 (metric spec owner) |
| T6-C11 Deliverable D2: sparsity-aware completion benchmark (density and MNAR  | NOT_STARTED | 3 |  |
| T6-C12 Step 31 (learning side): physics/condition features ablation (A3 raw T | OUT_OF_SCOPE | 2 |  |
| T6-C13 Step 32: focused kinetics (D8) fitting, identifiability, hierarchical  | CODE | 2 | R-SSOT: pointer: fitting library owner T5-C15; AA data/verification owner T2-C09/T5-C10 (see contested C02) |
| T6-C14 Step 33: mechanistic vs ML vs hybrid three-arm comparison (D9, G15-HYB | OUT_OF_SCOPE | 1 |  |
| T6-C15 Step 34 and §212: short rollout, composition consistency (34a), trust  | DRAFT | 4 | R-SSOT: status CODE->DRAFT (scaffold composition.py DRAFT_PENDING_34a_0 + unsigned spec, synthetic tests only); T5-C19 = OUT_OF_SCOPE for run, DRAFT scaffold owned here |
| T6-C16 Synthetic-data tiers and synthetic-prior pretraining (S-MECH, structur | OUT_OF_SCOPE | 2 |  |
| T6-C17 Active learning, value of information, acquisition design, inverse-des | OUT_OF_SCOPE | 1 |  |
| T6-C18 Neural / probabilistic transition models (D10, D11) and §209 state-dep | OUT_OF_SCOPE | 1 |  |
| T6-C19 Cross-cutting enablers: compute environment, reproducibility, experime | CODE | 1 | R-SSOT: xref T9-C25 for environment decision; T6-C19-R1 kept because T6-C03-R4 depends on it (R-FEAS) |
| T6-C20 Claim-boundary and reporting package for learning results (what the ta | DRAFT | 1 |  |

| Item | Pri | Consensus | Where | Agent h | Human h | Item (short) |
|---|---|---|---|---|---|---|
| T6-C01-R1 | SHOULD | UNANIMOUS | any | 3-5 | 0.5-1 | Freeze one canonical cell definition (food key, process key, target key, condition bin) and recompute density / support / cold-start-type counts per s |
| T6-C01-R2 | AFTER | UNANIMOUS | any | 4-8 | 0 | Add missing mask/weight metadata (replicate n, SD/range, yield or normalisation status RT-004 resolution, year, platform) to the EVD export view used  |
| T6-C01-R3 | AFTER | UNANIMOUS | human | 0 | 2 | Expert check of retention basis (TR vs AR, fresh vs dry weight) and the cap semantics 'values >100 reported as 100' / Bognar '1.00' for G15-1 and cens |
| T6-C02-R1 | MUST | UNANIMOUS | any | 1-2 | 0 | Write registry/transition_ladder_crosswalk_v1.csv (B-0=D0, B-1=D1, B-2=D3 matrix arm, B-3=D2, B-4=D4, B-5=D5; M0..M11 map) and fix label mismatch betw |
| T6-C02-R2 | SHOULD | UNANIMOUS | any | 1-3 | 0 | Diagnose and fix or document the test_transition hang (WORKLOG S134 deselected) so the transition suite runs in CI on every host. |
| T6-C02-R3 | SHOULD | UNANIMOUS | mac | 3-5 | 0 | Re-run DEL-2 ladder with paired tests (delta = baseline loss - challenger loss, cluster bootstrap) so every claimed gain over D0 on cold splits has a  |
| T6-C03-R1 | MUST | UNANIMOUS | human | 0 | 0.2 | Kush approves the 15A-BOOT freeze record (sets FROZEN, approved_by, approved_date). No agent or persona may set it as a signature (D-071 limits). _(aliases: T9-C08-R3, T9-C10-R1, T2-C15-R2)_ |
| T6-C03-R2 | MUST | UNANIMOUS | human | 0.5 | 0.5-1 | Kush signs the 29-diag prereg: commits reports/step29/29diag_prereg_signature.json with SHA-256 of the unchanged prereg text (agent first fixes rung-l |
| T6-C03-R3 | MUST | UNANIMOUS | mac | 0.5-1.5 | 0 | Run 29-diag twice on the Mac (CPU, minutes) and verify byte-identical outputs (G15-R). _(aliases: T0-C05-R4, T9-C15-R1)_ |
| T6-C03-R4 | MUST | AMENDED | any | 3-5 | 0.5-1 review | Write the four diag memos with every number labelled DIAGNOSTIC / BOOTSTRAP_UNVERIFIED / NON_CITABLE and no words 'supported', 'beats', 'validated'; e |
| T6-C03-R5 | MUST | AMENDED | any | 2-3 | 0 | Add paired D2-process-mean vs D3-ingredient-mean contrast (H2 shape: process info vs food-identity-only) on S-3/S-4/S-6 inside the diag memo, DIAGNOST |
| T6-C04-R1 | SHOULD | UNANIMOUS | human | 2-3 | 1-2 | Decide and pre-register the H2 operational test: which row sets, splits (S-2 pair, S-3 matrix, S-6 study), margin delta_H2, K_min, who may see test; m |
| T6-C04-R2 | AFTER | UNANIMOUS | mac | 6-10 | 2 | Run paper-grade H2 on DATA-EVIDENCE v1 (after 15b freeze + valid 07.A) with study-level bootstrap CIs; report negative result if so. |
| T6-C04-R3 | MUST | UNANIMOUS | any | 1-2 | 0.5 | For the talk: one honest H2 slide (diagnostic numbers, what cannot be concluded, prior exposure, single-study sources). |
| T6-C05-R1 | AFTER | UNANIMOUS | any | 6-10 | 0 | Draft 29.0 pre-model audit, 29.1 crosswalk, 29.2 prereg amendment (K_min, G29-A) and 29.3 engineering preconditions as DRAFT documents; SPLIT.jsonl en |
| T6-C05-R3 | AFTER | UNANIMOUS | mac | 4-6 | 1 | Run D0-D5 on S-1..S-6 on frozen DATA-EVIDENCE v1, twice, with cluster-bootstrap paired CIs; write v0_results.md and decision_record_v0.md. |
| T6-C05-R4 | AFTER | UNANIMOUS | human | 0 | 1-2 | Kush signs amendment and decision record; Parv authorises Python environment. |
| T6-C06-R1 | AFTER | UNANIMOUS | human | 2-3 | 1-2 | Pre-register Step 30.0: delta_30, K_min, bootstrap vs sign-flip cut-off, eligible splits, D6 activation rule; commit registry/phase_g_preregistration_ |
| T6-C06-R2 | AFTER | UNANIMOUS | any | 6-10 | 0 | Implement D3-full (hierarchical shrinkage over food class, process family, target class, study) as numpy/statsmodels-free partial pooling; unit tests  |
| T6-C06-R4 | AFTER | UNANIMOUS | vinayak | 6-12 | 0 | Train D5-tuned (LightGBM/XGBoost, grouped CV for hyperparameters, censored/AFT or interval objective arm) and D6 TabPFN (CPU, <=7k rows per source) or |
| T6-C06-R5 | AFTER | UNANIMOUS | any | 6-10 | 2 | Write §221.18 9-item completion audit, §222.10 anti-inflation report, G30-B/C decision records, MODEL.jsonl card drafts. |
| T6-C07-R1 | SHOULD | AMENDED | any | 2-4 | 0 | Diagnose D7a == D1 on PE (implementation vs sparsity: density 0.00267) and document; fix side-info learning if implementation. |
| T6-C07-R2 | AFTER | UNANIMOUS | any | 12-24 | 0 | Implement D7e soft-impute, D7b BPMF/Gibbs (numpy), D7d factorisation machine with side features (food group, FDC composition vector, process family, m |
| T6-C07-R3 | AFTER | UNANIMOUS | vinayak | 8-16 | 0 | Run §221.18 protocol: masked real cells, cold food, cold process, cold target (PE only), cold pair, study-disjoint (PE), frequency buckets, coverage;  |
| T6-C07-R4 | AFTER | UNANIMOUS | human | 0 | 1 | Kush signs G15-9 decision record; a REJECT is a valid outcome (R-20: negative results visible). |
| T6-C08-R1 | SHOULD | UNANIMOUS | any | 5-8 | 0 | Build propensity model with available covariates (food frequency in recipe corpus as popularity proxy, process family, target class, source), clipping |
| T6-C08-R2 | AFTER | UNANIMOUS | any | 3-5 | 0 | Frequency/support-bucket error report (does the model work only on popular cells?) and with/without mask-indicator ablation. |
| T6-C08-R3 | SHOULD | UNANIMOUS | any | 0.5-1 | 0.3 | Write MNAR claim-boundary paragraph (allowed vs forbidden wording) for the talk and paper. |
| T6-C09-R1 | AFTER | UNANIMOUS | any | 4-8 | 0 | Censored training arm (interval/Tobit objective in a small numpy fit and in AFT-capable GBDT) and cap-drop arm; compare on S-3/S-4 as DIAGNOSTIC. |
| T6-C09-R2 | SHOULD | UNANIMOUS | any | 2-3 | 0 | Add property tests: no zero/mean/half-minimum target imputation reaches dataset cells; tier I rows cannot be in test/calibration roles; E5-E7 excluded |
| T6-C09-R3 | COULD | UNANIMOUS | human | 0.2 | 0.2 | Decide TRUE_ZERO code addition to censoring registry (additive change). |
| T6-C10-R1 | AFTER | UNANIMOUS | any | 6-10 | 0 | Implement group-disjoint split-conformal (calibration roles from group_aware_split) plus weighted/Mondrian sensitivity and risk-coverage curves; study |
| T6-C10-R2 | AFTER | UNANIMOUS | any | 2-3 | 1 | Write c9_transition_fallback_spec (when the router may offer a calibrated model estimate vs ABSTAIN) consistent with section 141 contract; consumed by |
| T6-C11-R1 | SHOULD | UNANIMOUS | any | 3-4 | 0.5 | D2-lite for the talk: assemble existing DEL-2 + 29-diag numbers into a one-page density, MNAR and cold-split negative-result summary, labelled DIAGNOS |
| T6-C11-R2 | AFTER | UNANIMOUS | vinayak | 30-50 | 6-10 | Full D2: freeze FoodProc-ColdStart split manifests, run C02/C06/C07/C08/C10 stack, write D2 report with study-level CIs and negative results. |
| T6-C11-R3 | AFTER | UNANIMOUS | human | 0.5 | 1-2 | Confirm licence/terms for releasing derived non-raw benchmark manifests (USDA public domain; Bognar citation; Phenol-Explorer terms). |
| T6-C12-R1 | AFTER | UNANIMOUS | any | 4-6 | 0 | Define physics_feature_registry_v1 (log(1+t), 1/T_K, Omega with Ea grid) with source row ids; Layer 2 excluded by construction. |
| T6-C12-R2 | AFTER | UNANIMOUS | vinayak | 6-10 | 3 + expert 4 | Run A3/A4/A5 ablation on identical row sets, cooking stratum (PE conditions), paired cluster CIs; Kush signs prereg; expert reviews Ea grid and temper |
| T6-C13-R3 | COULD | UNANIMOUS | any | 3-5 | 0 | Kinetic census of Phenol-Explorer storage pseudo-series (reconcile 29 vs 8 definitions), as feasibility for KA ablation. |
| T6-C13-R4 | AFTER | UNANIMOUS | vinayak | 15-25 | 4 + expert 8-12 | KA0-KA6 model-form ablation, hierarchical fit (PyMC/NumPyro or custom), G15-4 record, expert review of forms and plausibility. |
| T6-C14-R1 | AFTER | UNANIMOUS | any | 15-25 | 4-6 | Pre-register three-arm test (M, ML, H=sequential residual) with Holm correction and physical-consistency alternative; run only after G15-4 PASS. |
| T6-C15-R1 | COULD | UNANIMOUS | any | 3-6 | 0 | 34a.0 circularity check (are USDA multi-step factors derived multiplicatively?) and, if clean, run 34a on USDA/PE with the best one-step rung from the |
| T6-C15-R2 | AFTER | UNANIMOUS | human | 0.5 | 1-2 | Kush supplies tau, eps_max, h_trust ids and STOP/DOWNGRADE actions and signs the 34c abstention spec (consumed by Step-36 tests; D4/D5 topic). |
| T6-C15-R3 | AFTER | UNANIMOUS | human | 2-4 | 1 | Search for staged cooking datasets with measured intermediates (raw -> pretreat -> dry -> fry) for 34b. |
| T6-C15-R4 | AFTER | UNANIMOUS | any | 30-60 | 0 | Broader §212 stack: semigroup and repeated-process tests on supported subsets, merge/split transitions, state-space baselines, MC/ensemble rollout, R0 |
| T6-C16-R1 | COULD | UNANIMOUS | any | 3-5 | 0.5 | Design-only: write the DATA-SIM card and ratio-sweep control spec as DRAFT so the firewall rules are fixed before any simulator output exists. |
| T6-C16-R2 | AFTER | UNANIMOUS | vinayak | 20-40 | 4 | After Step 27 PASS only: generate DATA-SIM v1, run ratio sweep and TSTR with real study-disjoint test, plus controls. |
| T6-C17-R1 | AFTER | UNANIMOUS | any | 8-14 | 0 | Simulated active-learning demo on a known kinetic system (random vs factorial vs info-gain; number of experiments to stable k, Ea), stating the simula |
| T6-C18-R1 | AFTER | UNANIMOUS | vinayak | 10-20 | 0 | After D0-D7 decision records: one residual-MLP / FiLM ablation with GPU env (vinayak A100; torch setup on manjot GPU 1 if wanted) only if gates justif |
| T6-C19-R1 | MUST | UNANIMOUS | any | 1-2 | 0.3 (Parv authorises) | Record the learning environment per host (mac pinned versions; vinayak; manjot CPU) in a lock file; run a smoke import and the transition test suite o |
| T6-C20-R1 | SHOULD | UNANIMOUS | any | 2-3 | 0.5-1 | Draft the learning claim-boundary page and slide wording (H2 diagnostic, D2-lite, negative results kept visible). |

Topic contradictions recorded by the inventory: 10; SSOT requirements without plan coverage: 14 (see `topics/T6.json`). Resolved by round 1: Rung A count (T0/T3/T7/T9), defaults 27 rows (T4), SVAR 224 ids vs 254 rows (T0/T9), EVD lines vs ids (T2), physical % sample vs full corpus (T4/T5: use T4 full-corpus 3.4 % / 5.3 %).

### T7 — Representations and similarity: Step 35 ladder, nine notions, 35e registry, RDKit toolkit, Level 12 fusion, Level 13 encoders, Level 13E evolution/identity, FlavorTwin boundary
Open items 62 (MUST 1, SHOULD 27, COULD 18, AFTER 16); consensus UNANIMOUS 57, AMENDED 5, CONTESTED 0.

| Component | Status | Open items | Component notes |
|---|---|---|---|
| T7-C01 Step 35.0 pre-registration package and G35-PRE signature gate | BLOCKED | 5 | R-SSOT: plan_steps normalised to list for all T7 components |
| T7-C02 Split families, leakage auditor and hash manifests (G35-0) | CODE | 3 |  |
| T7-C03 Molecule rung 35a: identity E0, PubChem-881 Tanimoto E1, descriptors,  | BLOCKED | 4 |  |
| T7-C04 RDKit toolkit and fingerprint rungs E2/E3 (ECFP r0-r3, SIM-06 frozen b | BLOCKED | 4 |  |
| T7-C05 Ingredient chemical profile x_ij (tiered record), coverage record and  | BLOCKED | 3 |  |
| T7-C06 Ingredient set similarity E0/E1: n_ij, Jaccard, Ochiai, IDF-overlap, C | BLOCKED | 2 |  |
| T7-C07 Ingredient E2/E3 aggregators: kernel-mean, best-match, top-k, descript | NOT_STARTED | 1 |  |
| T7-C08 Sensory and OAV-weighted similarity (separate space): odour/taste desc | NOT_STARTED | 2 |  |
| T7-C09 Nutritional similarity (separate space) and ING<->FDC crosswalk depend | BLOCKED | 1 |  |
| T7-C10 Ingredient-state representation z_{i,t}, state-dependent composition s | BLOCKED | 2 |  |
| T7-C11 Explicit lot-state-sequence representation (rung 0 of 'the state repre | NOT_STARTED | 1 |  |
| T7-C12 Recipe rungs 35c: R0 Jaccard/cosine, R2 TF-IDF, R1 mean-profile, R3 ma | CODE | 4 |  |
| T7-C13 Recipe identity/variant calibration, split_group_id (07I-C/07I-S) and  | DRAFT | 3 | R-SSOT: reduced to Step-35 split-group usage; identity ledger DONE-by-reference (T3-C20); 07I-C calibration item moved to T3-C20-R2 |
| T7-C14 Cuisine rungs 35d: C0 prevalence, C1 specificity, C2 pair/triplet moti | CODE | 3 |  |
| T7-C15 Cuisine ontology and Food.com tag-to-cuisine derivation (labels for 35 | DRAFT | 1 |  |
| T7-C16 35e typed similarity registry v2 (nine notions), lint, separation test | CODE | 3 |  |
| T7-C17 PROCEDURAL similarity (recipe process-bag Jaccard -> Levenshtein -> DT | NOT_STARTED | 1 | R-SCI: status_evidence fix: Step 17 = 9,470,190 Rung A events; 14,594,812 = 26g census |
| T7-C18 FUNCTIONAL / substitution fitness (SIM-17, SIM-18) and substitution be | NOT_STARTED | 2 |  |
| T7-C19 Mandatory confound audits and diagnostics (frequency, size, source, co | CODE | 1 |  |
| T7-C20 Level 12 learned rungs and fusion: z_m encoders (GNN, pretrained, cont | OUT_OF_SCOPE | 3 |  |
| T7-C21 Level 13 learned recipe/cuisine encoders: R4-R9, objectives O0-O7, C3- | OUT_OF_SCOPE | 2 |  |
| T7-C22 35h decision records (Level-12 §183.4, Level-13 §193.8) and Step-36 ha | NOT_STARTED | 2 |  |
| T7-C23 Level-13 data-engineering contract and representation registries (reci | DRAFT | 1 |  |
| T7-C24 Level 13E scope, data/lineage gates and nullable historical metadata ( | NOT_STARTED | 2 |  |
| T7-C25 Level 13E descriptive core: rank-frequency (Clauset protocol), null la | NOT_STARTED | 2 |  |
| T7-C26 Level 13E extended models: fitness/context fitness F_{i|c,t}, pairing- | OUT_OF_SCOPE | 2 |  |
| T7-C27 FlavorTwin boundary, cultural prior and historical RAG hooks (E13E-17/ | OUT_OF_SCOPE | 2 |  |

| Item | Pri | Consensus | Where | Agent h | Human h | Item (short) |
|---|---|---|---|---|---|---|
| T7-C01-R1 | SHOULD | UNANIMOUS | human | 0 | 2-4 (Kush ~3 h + Parv ~3 h per sheet; partly parallel) | Kush and Parv each sign the v2 package (Route B on the Mac: regenerate template, confirm sha256 009c9047..., confirm not_bound_absent_here empty, fill _(aliases: T0-C14-R1)_ |
| T7-C01-R2 | MUST | AMENDED | human | 0.5 | 0.5 | DECISION for the course: either sign and run descriptive explicit rungs (35a-lite, 35b PRESENCE arms, 35c R0/R2 descriptive, 35d descriptive, 35e regi |
| T7-C01-R3 | SHOULD | UNANIMOUS | human | 1 | 2-3 | Kush answers the open D35 checklist items not covered by Parv: D35-1 (sign THR rows), -2 (rdkit as project dependency, pin 2026.3.6; Parv already dire |
| T7-C01-R4 | SHOULD | UNANIMOUS | any | 1-2 | 0 | After signature, copy THR-35P-01..43 into registry/preregistered_thresholds_v1.csv (Step 01.6) and freeze preregistration_v1.md + sha256; orchestrator |
| T7-C01-R5 | SHOULD | UNANIMOUS | any | 0.5 | 0 | Verify on manjot (and vinayak) which bound inputs are present: ledgers/recipe_semantics/recipe_ingredient_mentions_v1.parquet and gold_firewall are NO |
| T7-C02-R1 | SHOULD | UNANIMOUS | any | 8-12 | 0 | Write molecule split auditor: InChIKey full + 14-char connectivity overlap check, tau881 cluster splits with label-free tau_cluster (99th pct over 20, |
| T7-C02-R2 | COULD | UNANIMOUS | any | 6-10 | 0 | Implement cuisine split families S-cui-src / S-cui-hold (cuisine-level) and source-stratified recipe partitions (lowest-recipe_id stratum rule THR-35P |
| T7-C02-R3 | SHOULD | UNANIMOUS | mac | 1-2 | 0 | Run splits on real data and write sha256 manifests (registry/splits/step35_split_hash_manifest_v1.json, reports/step35/output_hash_manifest_v1.json);  |
| T7-C03-R1 | SHOULD | UNANIMOUS | any | 14-22 | 0 | Write 35a scoring (no-rdkit arm): CACTVS-881 decode unit test (222 hex = 881 bits MSB-first + 7 pad), E0 identity, E1 Tanimoto, six PubChem descriptor |
| T7-C03-R2 | COULD | AMENDED | mac | 2-4 | 0 | After the 35.0 v2 signature only: run 35a no-rdkit arm on the 603 taste-labelled molecules and publish molecule_leaderboard_v1 with wide intervals and |
| T7-C03-R3 | SHOULD | UNANIMOUS | human | 1 | 4-6 (expert) + 1 (Kush to arrange) | Chemistry-aware reviewer approves taste-label normalisation map (THR-35P-04) and the scored-class support rule (THR-35P-05); establishes the reason fo |
| T7-C03-R4 | AFTER | UNANIMOUS | vinayak | 20-40 | 1-2 (licence call) | Odour-label tasks and OpenPOM-style reproduction (SSOT L11036 mandatory comparator for any molecule-level odour claim): acquire GS-LF/Keller/Pyrfume p |
| T7-C04-R1 | SHOULD | UNANIMOUS | human | 0 | 0.5 | Kush confirms (or reverses) the RDKit dependency decision D35-2 and the Open Babel stance D35-3. |
| T7-C04-R2 | COULD | UNANIMOUS | mac | 16-24 | 0 | Implement E2/E3 rung module (Morgan r0-3 bit/count 2048 and 4096 sensitivity, FCFP, MACCS, atom-pair, RDKit2D standardised, Murcko scaffold split, But |
| T7-C04-R3 | COULD | UNANIMOUS | mac | 0.5 | 0.5 | Install LightGBM (and scikit-learn) in the Mac env (and optionally manjot/vinayak venv) as pinned dependency; log in compute_runs registry. |
| T7-C04-R4 | AFTER | UNANIMOUS | mac | 3-6 | 0 | Run E2/E3 rungs on the 603 taste-labelled molecules with scaffold split; report OOD gap (random minus scaffold) vs E1 baseline. |
| T7-C05-R1 | SHOULD | UNANIMOUS | any | 6-10 | 0 | Write x_ij builder producing ingredient_profile_xij_v1 and ingredient_profile_coverage_v1 (git-ignored features/step35/) with tier, value-or-UNKNOWN,  |
| T7-C05-R2 | SHOULD | UNANIMOUS | human | 1 (prepare sheet) | 2 (Parv) | Parv audits the 50 ING<->FlavorGraph crosswalks / profile joins (D35-7). |
| T7-C05-R3 | SHOULD | UNANIMOUS | any | 3-5 | 0 | BAN-35-1 enforcement: static check that no arm, comparator or tie-breaker reads KGE ING_CO_OCCURS or any FlavorGraph/Recipe1M-derived edge/embedding ( |
| T7-C06-R1 | SHOULD | UNANIMOUS | any | 12-18 | 0 | Implement ingredient E0/E1 metrics, null percentile with B >= max(1000, ceil(20m/q)) (THR-35P-37), cardinality slope, dropout and shuffle controls, ma |
| T7-C06-R2 | COULD | UNANIMOUS | any | 2-4 | 0 | Run 35b PRESENCE arms on IMAP (descriptive then primary endpoint PE-35b incl. cold-start PE-35b-cold) and report slope/CI per arm. |
| T7-C07-R1 | COULD | UNANIMOUS | mac | 8-14 | 0 | Implement kernel-mean, symmetrised best-match, top-k mean on 881-bit Tanimoto (no-rdkit variant now, ECFP variant after C04) and descriptor-mean embed |
| T7-C08-R1 | SHOULD | UNANIMOUS | human | 1 | 0.5 | Decide and document ingredient-level SENSORY as UNSUPPORTED for 25 Nov (talk wording) and keep structural != sensory as a stated boundary. |
| T7-C08-R2 | AFTER | UNANIMOUS | manjot | 6-10 (after source chosen) | 2 (licence) | Acquire an odour/taste-threshold compilation and sensory panel labels (source and licence to be selected; none verified here) to enable OAV and ingred |
| T7-C09-R1 | COULD | UNANIMOUS | any | 6-10 | 0 | Implement NUTRITIONAL similarity (cosine/Mahalanobis on stated basis, masked) once >= N crosswalks are human-verified; basis checks and food-group str |
| T7-C10-R1 | COULD | UNANIMOUS | human | 1 | 1 | DECISION on a cheaper non-circular first version (packet Q31): similarity of mechanism-screen profiles or of EVD before/after retention vectors (vit C |
| T7-C10-R2 | AFTER | UNANIMOUS | any | 12-20 | 0 | Implement raw-vs-cooked discrimination on study-disjoint EVD with matrix-shuffled control, static vs process-response comparison on a held-out process |
| T7-C11-R1 | COULD | UNANIMOUS | vinayak | 10-16 | 1 | Define explicit per-lot-step feature vector from lot state + Layer-1/Layer-2 drivers (masked UNKNOWN, Layer 2 tagged ASSUMED_DEFAULT), with similarity |
| T7-C12-R1 | COULD | UNANIMOUS | human | 1 | 1 | Resolve the 9 build-note ambiguities (idf formula, unseen df, tf form, R3 masking, bin edges, floor equality) by registry rows or explicit confirmatio |
| T7-C12-R2 | SHOULD | UNANIMOUS | mac | 16-24 | 0 | Build 35c task harness: masked-ingredient recovery (Recall@K, MRR, nDCG), partial-recipe completion, size-matched evaluation, frequency panel (SSOT §1 |
| T7-C12-R3 | SHOULD | AMENDED | mac | 3-6 | 0 | After signature only: run R0/R2 descriptive and primary PE-35c on real recipes incl. link-coverage floor with/without masking; 1,000-recipe sample bef |
| T7-C12-R4 | COULD | UNANIMOUS | any | 3-5 | 0 | R3 quantity-weighted mass-share arm on the quantity-bearing subset (Step 16 rc2 Q0 mass lines) once coverage is audited. |
| T7-C13-R1 | SHOULD | UNANIMOUS | human | 1 | 2-3 (Parv) + 1 (Kush) | Parv writes his own 07I-C confirmation; Kush/Parv label or adjudicate any remaining calibration pairs; record the agreement figure as computed inter-r |
| T7-C13-R3 | COULD | UNANIMOUS | any | 12-20 | 0 | Identity baseline ladder on labelled pairs: title-only, ingredient Jaccard, +quantity, +role, +process (Levenshtein/DTW/graph edit), then learned comp |
| T7-C13-R4 | AFTER | UNANIMOUS | any | 8-12 | 3-6 (expert) | Novelty measure beyond rarity (set/quantity/process/density components; expert-aligned signal after rarity and source controls, G13E-08); needs a smal |
| T7-C14-R1 | SHOULD | UNANIMOUS | any | 14-22 | 0 | Implement remaining cuisine pieces: Curveball-calibrated Z / MX null path, E (era/source) null, macro-F1 classifier with minimum class support and sou |
| T7-C14-R2 | COULD | AMENDED | mac | 3-5 | 0 | After signature only: run C0-C2 descriptive on labelled recipes and pre-registered classes (>=100 recipes, >=2 source families); report class table an |
| T7-C14-R3 | AFTER | UNANIMOUS | human | 1 | 2-3 | Expert review of C1/C2 definitions (triplet NPMI generalisation, K-1 vs C-1, support thresholds 20/10). |
| T7-C15-R1 | COULD | UNANIMOUS | human | 1 | 4-6 (expert) + 0.5 (Kush) | Kush names a cuisine-aware reviewer; reviewer audits artefacts ('American/French', Jewish, Roman, New...) and approves the support rule (>=100 recipes |
| T7-C16-R1 | SHOULD | UNANIMOUS | human | 0.5 | 1 | Kush decides sim_id scheme and status mapping (D35-12), SIM-13 home (D35-11), and which statuses count as 'supported' for G35-SEP. |
| T7-C16-R2 | SHOULD | UNANIMOUS | any | 6-10 | 0 | Generate registry/similarity_registry_v2.csv and registry/representation_registry_v1.csv from the 21 v1 rows + notions, run lint, add BAN-35-1 and G35 |
| T7-C16-R3 | COULD | UNANIMOUS | any | 4-8 | 0 | Run separation tests (Spearman rank agreement and kNN-overlap@k between notions; 'structure -> taste' STRUCTURAL x SENSORY test) on whatever data exis |
| T7-C17-R1 | COULD | UNANIMOUS | any | 10-16 | 0 | Implement process-bag Jaccard and normalised Levenshtein over the canonical event sequence; step-count confound control; report extraction-error sensi |
| T7-C18-R1 | AFTER | UNANIMOUS | human | 4 (build packets) | 8-15 (expert) or Kush/Parv time | Commission 200-300 blind two-annotator substitution pairs with recipe context (needs food-literate annotators; Kush/Parv as annotators carries reviewe |
| T7-C18-R2 | AFTER | UNANIMOUS | vinayak | 8-12 | 0 | Baselines (co-occurrence-context kNN, LLM zero-shot via Ollama) on the frozen set. |
| T7-C19-R1 | SHOULD | UNANIMOUS | any | 8-12 | 0 | Build one audit module producing G35-0/COV/CIRC/NULL/SEP verdict JSON per run with negative results kept visible (law 8). |
| T7-C20-R1 | SHOULD | UNANIMOUS | human | 1 | 0.5 | Write the explicit statement 'learned rungs deferred; entry rule LR-1..LR-5' into the 35h record and talk (limitation slide). |
| T7-C20-R2 | AFTER | UNANIMOUS | vinayak | 60-120 | 4-8 | Post-course: encoder bake-off on taste task (frozen pretrained + linear probe, GNN at matched capacity, label-prior), only if an explicit rung leaves  |
| T7-C20-R3 | AFTER | UNANIMOUS | vinayak | 80-160 | 4 | Post-course: set-aggregator and multi-view fusion comparison (G7, G5, G12-DEC-3..7) after OAV/threshold data exist. |
| T7-C21-R1 | AFTER | UNANIMOUS | vinayak | 60-100 | 2-4 | Post-course: Phase 1 recipe-set encoder bake-off (mean vs Deep Sets vs attention at parameter-matched control) on licence-cleared recipes; frequency-d |
| T7-C21-R2 | AFTER | UNANIMOUS | vinayak | 80-140 | 3-5 | Post-course: objective bake-off (same-recipe multi-view contrastive, masked ingredient, cuisine supervised) with non-circular secondary evaluation (G1 |
| T7-C22-R1 | SHOULD | AMENDED | any | 2-3 | 1-2 (review) | Write decision records v1 for Level-12 and Level-13 stating per rung PROMOTED / FAILED / DATA-BLOCKED with evidence paths (expect mostly DATA-BLOCKED/ |
| T7-C22-R2 | SHOULD | UNANIMOUS | any | 2-4 | 1 | Presentation material for the representation ladder: one slide for the ladder + nine notions + current status, one slide for negative/blocked results. |
| T7-C23-R1 | SHOULD | UNANIMOUS | any | 4-6 | 0 | Create representation registry files and the output manifest writer (dataset/preprocessing/split versions, seed 20261104, code commit, sha256) used by |
| T7-C24-R1 | SHOULD | UNANIMOUS | human | 0.5 | 0.5 | DECISION: L13E = optional, parked (AH12) except one bounded descriptive null/rank-frequency chain; record 'not primary deliverable' and §279.8 first-p |
| T7-C24-R2 | COULD | UNANIMOUS | any | 6-10 | 0 | Audit dated-source coverage (Gutenberg, Wikibooks, Food.com submission dates) and write G13E-01/02 table with interval-censored dates; add nullable hi |
| T7-C25-R1 | COULD | UNANIMOUS | any | 16-26 | 0 | One bounded chain only (AH12): per-source rank-frequency with alternative-model comparison + M0 null lattice on Food.com web-era descriptors; label 'd |
| T7-C25-R2 | AFTER | UNANIMOUS | any | 20-30 | 0 | Kinouchi M1 exact copy-mutate reproduction and M2 category-constrained variant (G13E-04/05). |
| T7-C26-R1 | AFTER | UNANIMOUS | human | 0 | 0 | Park: record in the roadmap as post-course; no work before 25 Nov. Reopen only if a dated, source-diverse corpus is acquired. |
| T7-C26-R2 | AFTER | UNANIMOUS | vinayak | 80-200 | 6-12 | Post-course: acquire dated historical corpora (RELISH, Open Recipe Archive, historical cookbooks; licences unverified here) and run E3-E6. |
| T7-C27-R1 | SHOULD | UNANIMOUS | any | 1-2 | 0.5 | State the FlavorTwin boundary in one slide and in the 35h hand-off manifest (what is NOT claimed: no universal flavour scalar, no sensory equivalence  |
| T7-C27-R2 | AFTER | UNANIMOUS | vinayak | 80-160 | 4-8 | Post-course: FlavorTwin static -> process-conditioned prototype and separable cultural reranker (E13E-17). |

Topic contradictions recorded by the inventory: 11; SSOT requirements without plan coverage: 10 (see `topics/T7.json`). Resolved by round 1: Rung A count (T0/T3/T7/T9), defaults 27 rows (T4), SVAR 224 ids vs 254 rows (T0/T9), EVD lines vs ids (T2), physical % sample vs full corpus (T4/T5: use T4 full-corpus 3.4 % / 5.3 %).

### T8 — Application layer: CulinaryState-RAG (Step 36), C1-C18, router, retrieval, abstention, decision, runtime, demo, D4/D5, H1/H3
Open items 43 (MUST 17, SHOULD 9, COULD 11, AFTER 6); consensus UNANIMOUS 35, AMENDED 8, CONTESTED 0.

| Component | Status | Open items | Component notes |
|---|---|---|---|
| T8-C01 Query router (SSOT §39) + C1 query/intent parser | CODE | 1 | R-SSOT: SSOT §39 QUERY router (decision/query_router.py) = same artefact as T0-C08; owner of router scoring |
| T8-C02 Front door + branch handlers (METADATA, RELATIONSHIP, SEMANTIC, TRANSF | CODE | 2 |  |
| T8-C03 C2 entity/coreference resolver + target lexicon (question slot filling | CODE | 1 |  |
| T8-C04 State reconstruction interface for RAG (C3 state reconstructor, C4 pro | RUN | 1 |  |
| T8-C05 C5 goal/constraint parser + C11 feasibility filter | CODE | 2 |  |
| T8-C06 C6 multi-index retriever (BM25 + structured filter + dense + graph exp | RUN | 3 |  |
| T8-C07 C7 evidence compatibility vector, conflict/lineage handling, context-p | CODE | 2 |  |
| T8-C08 C8 direct transition lookup + C9 transition fallback (Level-15 model e | BLOCKED | 1 |  |
| T8-C09 C10 candidate-action generator + diagnosis/recovery (§243.6-243.7) | CODE | 1 |  |
| T8-C10 C12 outcome comparator + C15 multi-objective selector | CODE | 1 |  |
| T8-C11 C13 relevance gate (process relevance, query intent cues) | CODE | 1 |  |
| T8-C12 Confidence vector, evidence-sufficiency modes, output-precision cap, c | CODE | 2 |  |
| T8-C13 C14 uncertainty / OOD gate (evidence-support profile, cold axes) | CODE | 1 |  |
| T8-C14 Decision policy (ANSWER/COMPARE/ASK/DIAGNOSE/RECOVER/RECOMMEND/ABSTAIN | CODE | 2 |  |
| T8-C15 C16 grounded response generator + LLM backend (Ollama, template B5T) | RUN | 3 |  |
| T8-C16 C17 citation/provenance layer: claim checker + post-hoc enforcement (U | RUN | 3 |  |
| T8-C17 Runtime architecture, versioning and reproducibility artefacts | DRAFT | 1 |  |
| T8-C18 M6 demo app (local stdlib server) + hosting | CODE | 3 |  |
| T8-C19 D4 deliverable: evidence-aware retrieval with abstention (report) | RUN | 1 |  |
| T8-C20 D5 benchmark: preregistration, 100 AI-drafted questions, human review, | DRAFT | 4 | R-SSOT: owner of D5; T0-C11 keeps only the SSOT §12 task crosswalk (T0-C11-R3); T9-C17 = stats/prereg + outside check |
| T8-C21 H1 test: B0-B7 ladder on state blocks + mandatory ablations + oracle c | CODE | 4 |  |
| T8-C22 H3 test: abstention vs unsupported-claim rate + sufficiency/abstention | CODE | 1 |  |
| T8-C23 Remaining Level-16 benchmark families and robustness (SEM, LINK, QTY,  | NOT_STARTED | 2 |  |
| T8-C24 Statistics and preregistration governance for H1/H3 (and H2 diagnostic | DRAFT | 0 |  |
| T8-C25 Physical-layer / §141 output-contract integration into RAG answers | CODE | 0 | R-SSOT: references T0-C06 (owner) |

| Item | Pri | Consensus | Where | Agent h | Human h | Item (short) |
|---|---|---|---|---|---|---|
| T8-C01-R1 | MUST | AMENDED | any | 1-2 | 0 | Score router branch accuracy on the frozen D5 80 questions (never tune on them); report confusion matrix incl. X controls _(aliases: T0-C08-R1)_ |
| T8-C02-R1 | COULD | UNANIMOUS | any | 3-5 | 0 | Build METADATA handler: exact EVD/USDA SR lookup (public-domain) returning cited values or UNKNOWN _(aliases: T0-C08-R2)_ |
| T8-C02-R2 | MUST | UNANIMOUS | human | 0.2 | 0.2 | SEMANTIC branch: keep explicit abstention for 25 Nov and state it in the demo/report (decision) |
| T8-C03-R1 | SHOULD | UNANIMOUS | any | 1-2 | 0 | Measure slot extraction accuracy (ingredient/process/target) on the frozen D5 questions as a diagnostic |
| T8-C04-R2 | MUST | AMENDED | any | 1 | 0 | Report circularity caveat and an engine-vs-human-edited-gold agreement figure for S blocks |
| T8-C05-R1 | COULD | UNANIMOUS | any | 1-2 | 0 | Constraint-sensitivity robustness mini-test (oven vs pan only) as unit/property tests, no benchmark claim |
| T8-C05-R2 | AFTER | UNANIMOUS | any | 10-20 | 4-6 | H4 feasibility/recovery evaluation (§245.9, .11) |
| T8-C06-R1 | MUST | UNANIMOUS | manjot | 2-4 | 0 | Run retrieval metrics (Recall@K, MRR, condition-compatible Recall@K, source-disjoint split) on frozen D5 P/C questions as the D4 real evaluation |
| T8-C06-R2 | MUST | AMENDED | human | 0.2 | 0.3 | Resolve embedding choice for B1/B2 (bge vs e5-large-v2) before freeze and document |
| T8-C06-R3 | COULD | UNANIMOUS | any | 3-5 | 0 | Index literature passages/PARAM rows once verified (Step 10 rows) into retriever |
| T8-C07-R1 | SHOULD | UNANIMOUS | any | 3-4 | 0.5 | Decide how packets present CONFLICTING evidence (range + conflict flag) and add a small conflict test set from EVD strata |
| T8-C07-R2 | COULD | UNANIMOUS | any | 1-2 | 0 | Hard-negative evaluation of compatibility (same food/different process rows) as ablation |
| T8-C08-R1 | SHOULD | AMENDED | any | 3-5 | 0 | Wire first SIMULATE (sim_aa_1 vitamin C) into the cascade as B6 only as a RESEARCH_ONLY rung after the fit freeze and the descriptive SIM-VAL report e |
| T8-C09-R1 | AFTER | UNANIMOUS | any | 8-16 | 4-6 | Candidate Recall@K and diagnosis Recall@K benchmark (DEC/DIAG/REC families) |
| T8-C10-R1 | MUST | UNANIMOUS | any | 1 | 0 | Score C-block comparisons vs reviewed gold; report 'cannot separate' rate |
| T8-C11-R1 | COULD | UNANIMOUS | any | 0.5 | 0 | Measure relevance-gate precision/recall on X controls + S/P blocks (diagnostic) |
| T8-C12-R1 | MUST | AMENDED | human | 0.3 | 0.5 | Reword H3/B7 as 'rule-based evidence-sufficiency abstention (uncalibrated)' in prereg + deck; no calibration claim |
| T8-C12-R3 | AFTER | UNANIMOUS | manjot | 6-10 | 8-12 | Calibrated recommend/ask/abstain model (Platt/isotonic) on independently verified labels |
| T8-C13-R1 | MUST | UNANIMOUS | any | 1 | 0 | Evaluate OOD gate on P3 (gold=ABSTAIN) vs P1/P2: abstain recall/false-abstain rate |
| T8-C14-R1 | COULD | UNANIMOUS | any | 3-4 | 0 | Minimal ASK evaluation: ASK-when-missing-slot-flips-route vs NeverAsk vs AskEverything on the X/vague block (descriptive) |
| T8-C14-R2 | AFTER | UNANIMOUS | any | 10-15 | 4-6 | Full VOI benchmark |
| T8-C15-R1 | MUST | AMENDED | vinayak | 3-5 | 0 | Run B0/B1/B2/B4/B5/B7/B5T on frozen D5 benchmark with qwen2.5:7b (temp 0, seed fixed), log run in compute_runs_v1.csv _(aliases: T0-C11-R2, T9-C17-R2)_ |
| T8-C15-R2 | COULD | UNANIMOUS | vinayak | 1-2 | 0 | Sensitivity run with qwen2.5:32b on same questions (robustness only) _(aliases: T9-C17-R4)_ |
| T8-C15-R3 | SHOULD | UNANIMOUS | any | 0.5 | 0 | Pin Ollama model digest/version and prompt hash in the run record (§244.5) _(aliases: T0-C09-R3)_ |
| T8-C16-R1 | MUST | AMENDED | any | 2-3 | 1-1.5 each | Add citation precision/recall and a manual-verification sample (30 claims) to H3 reporting, so UCR is not self-graded only |
| T8-C16-R2 | MUST | UNANIMOUS | any | 1 | 0 | Report enforcement cost: sentences removed, fallback rate, answer length/coverage per rung |
| T8-C16-R3 | AFTER | UNANIMOUS | any | 4-6 | 0 | Qualitative/directional claim checker (e.g. 'leaches') against mechanism registry |
| T8-C17-R1 | SHOULD | UNANIMOUS | any | 2-3 | 0 | Create prompt_registry (prompt sha, model digest) + claim_ledger schema for D5 answers; record versions per experiment |
| T8-C18-R1 | SHOULD | UNANIMOUS | human | 0 | 0.5-1 (Kush) | Provide hosting account (or approve tunnel route) and decide LLM path (API key vs template-only) _(aliases: T9-C22-R1)_ |
| T8-C18-R2 | SHOULD | UNANIMOUS | any | 3-5 | 0.5 | Deploy hosted demo with template-only (no key) fallback; health check; DEMO_ONLY/NON_CITABLE banner _(aliases: T0-C09-R1)_ |
| T8-C18-R3 | COULD | UNANIMOUS | any | 3-4 | 0.5 | Resume demo polish after H1/H3 results (show lot state/L2 labels, examples with DIRECT evidence) |
| T8-C19-R1 | MUST | UNANIMOUS | any | 3-4 | 1 each | Write D4 section/report from frozen-benchmark P/C results + silver dev study (silver labelled) |
| T8-C20-R1 | MUST | UNANIMOUS | human | 0 | 0.3 each | Kush and Parv sign D5/H1/H3 prereg _(aliases: T9-C08-R2)_ |
| T8-C20-R2 | MUST | AMENDED | human | 1 | 5-7 each (incl. S-gold re-derivation) | Kush and Parv independently review 100 questions (KEEP/EDIT/DROP), reconcile; agent assembles benchmark _(aliases: T0-C11-R1, T9-C17-R1, T8-C04-R1)_ |
| T8-C20-R3 | MUST | UNANIMOUS | any | 0.5 | 0.3 | Freeze benchmark (sha256) and run freeze check _(aliases: T8-C17-R2)_ |
| T8-C20-R4 | SHOULD | UNANIMOUS | any | 1-2 | 0.5 each review | Author U (substitution) and X (control) blocks (5 each) which have no drafts |
| T8-C21-R1 | MUST | UNANIMOUS | vinayak | 2-3 | 0 | Execute H1 runs on frozen S1/S2 (B0,B1,B2,B4 + B5/B7), compute McNemar/Newcombe |
| T8-C21-R2 | SHOULD | UNANIMOUS | manjot | 3-5 | 0 | Cheap ablations: remove state conditioning, evidence compat, claim enforcement, OOD gate one at a time on frozen set _(aliases: T9-C12-R3)_ |
| T8-C21-R3 | COULD | UNANIMOUS | any | 2 | 0 | Oracle-state vs predicted-state cascade on S blocks using human-corrected gold state |
| T8-C21-R4 | COULD | UNANIMOUS | any | 2-3 | 0 | Build B3 (structured metadata RAG) rung |
| T8-C22-R1 | MUST | UNANIMOUS | manjot | 3-4 | 0 | Execute H3 analysis on frozen P/C blocks; decision-mode F1; handle zero-claim denominators |
| T8-C23-R1 | COULD | UNANIMOUS | any | 3-4 | 0 | Unit-invariance + paraphrase invariance mini-suite for the RAG (C<->F, kg<->g) _(aliases: T9-C12-R4, T8-C01-R2)_ |
| T8-C23-R2 | AFTER | UNANIMOUS | any | 20-40 | 8-12 | Remaining families (DEC/DIAG/REC/FT) benchmark |

Topic contradictions recorded by the inventory: 7; SSOT requirements without plan coverage: 9 (see `topics/T8.json`). Resolved by round 1: Rung A count (T0/T3/T7/T9), defaults 27 rows (T4), SVAR 224 ids vs 254 rows (T0/T9), EVD lines vs ids (T2), physical % sample vs full corpus (T4/T5: use T4 full-corpus 3.4 % / 5.3 %).

### T9 — Governance, contracts, evaluation design, deliverables, compute and timeline
Open items 55 (MUST 21, SHOULD 21, COULD 10, AFTER 3); consensus UNANIMOUS 40, AMENDED 12, CONTESTED 3.

| Component | Status | Open items | Component notes |
|---|---|---|---|
| T9-C01 Steps 01-02: project authority + implementation audit | DONE | 2 |  |
| T9-C02 Step 03: state semantics / SVAR registry / MP-1 contract | DONE | 0 | R-SSOT: xref of T2-C03 (no separate remaining items) |
| T9-C03 Step 04: evidence / provenance / similarity contracts + lineage min-co | DONE | 1 |  |
| T9-C04 Step 05: EVD normalisation (17,978 E3 rows) + EVD export view | DONE | 0 |  |
| T9-C05 Step 06: source acquisition manifest + H2 licence queue + H1 external  | BLOCKED | 1 | R-SSOT: xref of T2-C18 (licences/H2); professor email single owner T0-C17 |
| T9-C06 §238 exact data contracts (12 field dictionaries) | CODE | 2 |  |
| T9-C07 Human-gate registry H1-H8 and D-045 / D-071 delegation rules | DONE | 5 |  |
| T9-C08 Pre-registration, threshold registry, negative-results policy | CODE | 1 |  |
| T9-C09 Splits and leakage controls (source/duplicate/group-aware) | CODE | 4 |  |
| T9-C10 Step 15: DATA-EVIDENCE freeze (15.0 rulings, 15a.R seal, 15a bootstrap | DRAFT | 1 |  |
| T9-C11 Experiment registry, run log and cost accounting | CODE | 3 |  |
| T9-C12 Statistics and evaluation design (metrics, tests, ablations, power) | CODE | 2 |  |
| T9-C13 Human annotation / agreement gates (07.A-R1, 07I-C, P1b, HV queue) | BLOCKED | 2 |  |
| T9-C14 Deliverable D1: process-effect evidence ledger + data card | CODE | 0 |  |
| T9-C15 Deliverable D2 + hypothesis H2: sparsity-aware completion and cold-spl | CODE | 1 |  |
| T9-C16 Deliverable D3: state-tracking engine validation (gold comparison) | NOT_STARTED | 1 | R-SCI/R-SSOT: status CONTESTED (C01): R-SCI NOT_STARTED vs R-SSOT CODE; SYNTH compromise NOT_STARTED for the validation component, engine RUN tracked in T3-C12; evidence: Rung A 9,470,190; 26g census 14,594,812; DEEP_GOLD 0 |
| T9-C17 Deliverable D5 evaluation protocol: benchmark freeze, H1 and H3 runs | DRAFT | 1 | R-SSOT: stats/prereg only; review/runs owned by T8-C20/T8-C15 |
| T9-C18 Deliverable D4 evaluation: evidence-aware retrieval + abstention metri | CODE | 1 |  |
| T9-C19 Hypothesis H4 / feasibility filter and recovery (proposal D5 part) | OUT_OF_SCOPE | 1 |  |
| T9-C20 Final course report | DRAFT | 3 |  |
| T9-C21 Presentation slides (25-26 Nov) | NOT_STARTED | 1 |  |
| T9-C22 Working demo and demo scenarios (hosting side) | CODE | 1 |  |
| T9-C23 Paper path / SSOT §14 minimum publishable unit and §253 paper options | DRAFT | 3 |  |
| T9-C24 Reproducibility, release semantics, raw immutability, latency | CODE | 3 |  |
| T9-C25 Compute plan across Mac / vinayak / manjot (all remaining runs) | DRAFT | 4 | R-SSOT: status RUN->DRAFT (a plan, not an executed component); single owner of environment/installs authorisation (new item T9-C25-R5); T5/T6/T7 env findings reference it |
| T9-C26 Timeline and critical path to 25 Nov (human-input chain) | DRAFT | 5 |  |
| T9-C27 Step 10/M3 hand-off to governance: SIMULATE gate and verified-evidence | BLOCKED | 0 |  |
| T9-C28 Licences, redistribution, PII and release tiers | DRAFT | 2 | R-SCI+R-SSOT: status DONE->DRAFT (registries exist; licences largely owner-asserted/UNVERIFIED; Food.com training use, Q30, H2 open). Licence owner = T2-C18; T9-C05/T9-C28 reference it |
| T9-C29 SSOT §249 promotion gates G16-* and stop rules (status tracker) | DRAFT | 1 |  |
| T9-C30 SSOT §257 Definition of Done (17 items) and §257A.25 checklist (21 ite | DRAFT | 1 |  |
| T9-C31 SSOT §251 risk register controls and §247 RQ16 decision register | DRAFT | 1 |  |
| T9-C32 Number-class lint for deck/report | NOT_STARTED | 1 | R-SCI: new component proposed |

| Item | Pri | Consensus | Where | Agent h | Human h | Item (short) |
|---|---|---|---|---|---|---|
| T9-C01-R2 | COULD | UNANIMOUS | any | 1-2 | 0.25 | Materialise missing Step 01/04 v1.1 registries (authority map v1.1, namespace registry) or record that 04_9_min doc is the accepted substitute |
| T9-C01-R3 | SHOULD | UNANIMOUS | mac | 0.5 | 0 | Refresh STATUS.md to S174/S175 truth (orchestrator-only file; hand to orchestrator) |
| T9-C03-R1 | COULD | UNANIMOUS | human | 0.5 | 1-2 | Human review of similarity registry SIM-01..21 (freeze_status) - or mark 'unreviewed' in report |
| T9-C05-R3 | COULD | UNANIMOUS | any | 1 | 0 | Fix manifest DS-006 replicate_information and add v1.1 columns (UNKNOWN allowed) - append-only new file |
| T9-C06-R1 | SHOULD | UNANIMOUS | any | 2-3 | 0 | Write a §238 conformance table: each SSOT field -> schema property -> populated? (counts only) |
| T9-C06-R2 | SHOULD | UNANIMOUS | mac | 2-4 | 0.5 | Decide: materialise a counts-only CLM (claim ledger) for demo answers or declare it runtime-only for the talk |
| T9-C07-R1 | SHOULD | UNANIMOUS | human | 0.25 | 0.25 | Fill H3 compute threshold (node-hours) and record that D-077 compute (vinayak, manjot, mac) is inside it |
| T9-C07-R2 | MUST | UNANIMOUS | human | 0 | 0.25-0.5 | Obtain/record a written copy (email/screenshot) of Prof. Bagler's permission for the D-045 AI-first workflow; else keep 'as stated by Kush' wording in |
| T9-C07-R3 | MUST | UNANIMOUS | any | 1-2 | 0.5 | Report section stating exactly which gates were AI-delegated (D-071) vs human-signed, generated from DECISIONS (script, counts only) |
| T9-C07-R4 | MUST | AMENDED | human | 0.5 | 0.5 | H8 scope decision: formally drop/defer D2, H2 full test, H4, Steps 20/28/33/34, FlavorTwin before the talk _(aliases: T0-C10-R1, T9-C19-R1, T8-C24-R1)_ |
| T9-C07-R5 | SHOULD | UNANIMOUS | human | 0 | 0.25 | H7 decision: repo push/visibility for presentation (private vs public), BBC-derived counts statement |
| T9-C08-R4 | MUST | AMENDED | any | 1-2 | 0.5-1 | Add NEG rows for S171-S176 negatives (router DIRECT 0.754 %, D-074 R1 4/60, Food.com no-units, NER UNIT<<QUANTITY, SP-002 29.8 %, P1 HANDBOOK_REVISION |
| T9-C09-R1 | MUST | UNANIMOUS | any | 3-5 | 0 | Build and hash a SPLIT registry for the three evaluations that will run (D5 benchmark questions, 29-diag S-1..S-5, 07.A packet) and record in ledgers  |
| T9-C09-R2 | MUST | UNANIMOUS | manjot | 2-3 | 0 | Leakage audit: D5 S-block recipes vs NER/linker/gold training splits and vs Rung A dev sets; P/C cells vs EVD rows used in DEL-2 / retrieval silver |
| T9-C09-R3 | MUST | UNANIMOUS | any | 0.5 | 0 | Source-disjoint report line: all recipe-level results labelled source-family-disjoint or 'near-duplicate leakage not controlled' per 07I-C failure rul |
| T9-C09-R4 | AFTER | UNANIMOUS | mac | 4-6 | 0 | Study-disjoint / pair-holdout / ingredient-disjoint splits for D2 (needs 15a freeze, independence_group join) |
| T9-C10-R2 | COULD | UNANIMOUS | mac | 3-4 | 1-2 | 15b freeze (needs 07.A valid pass + AA SIM-CAL/VAL lock) |
| T9-C11-R1 | SHOULD | UNANIMOUS | any | 2-3 | 0 | Back-fill EXP rows (or a registry/experiments_S171_S175.csv) for M1..M9 runs using the SSOT §257A.20 fields _(aliases: T6-C19-R2)_ |
| T9-C11-R2 | SHOULD | UNANIMOUS | any | 0.5-1 | 0 | Complete missing start/end times and output sha256 in run log (orchestrator edits CSV); require new S176 runs to follow header |
| T9-C11-R3 | COULD | UNANIMOUS | any | 1-2 | 0.5 | Lightweight cost/time ledger: LLM tokens (H1/H3 Ollama calls), GPU hours, human review minutes per block (log from review sheets) |
| T9-C12-R1 | MUST | AMENDED | any | 1 | 0 | Power/MDE note for H1/H3 (exact McNemar at n=30, discordance assumptions) added to prereg amendment BEFORE signature _(aliases: T8-C24-R2)_ |
| T9-C12-R2 | SHOULD | AMENDED | mac | 3-5 | 0 | Add D4 metrics to prereg as descriptive: condition-compatible Recall@K on P blocks and risk-coverage curve of B7 abstention (ordinal score; no ECE/Bri |
| T9-C13-R4 | SHOULD | UNANIMOUS | human | 0 | 0.5 | Parv writes own confirmation of 07.A/07I-C statements and Step 16 comments |
| T9-C13-R5 | COULD | AMENDED | human | 1 | 3-5 | Review 30 AI-drafted scripted sessions (HV-006) as the D3 session set, or declare D3 session evaluation NOT_RUN |
| T9-C15-R2 | AFTER | UNANIMOUS | vinayak | 12-20 | 1 | Full D2 benchmark (pair-holdout, ingredient-disjoint, study-disjoint, propensity-weighted metrics, conformal) |
| T9-C16-R1 | MUST | UNANIMOUS | any | 2-3 | 0 | Report D3 as 'built + run, gold comparison limited to P1 (7 pairs, AI-drafted, human-accepted)' with intervals; add replay-consistency and merge/split |
| T9-C17-R3 | SHOULD | UNANIMOUS | human | 1 | 1-2 | Add outside check: >=1 non-author reviewer (peer or food-science student) on a 20-question subset, or declare 'author-only review' limitation _(aliases: T0-C11-R4, T8-C20-R5)_ |
| T9-C18-R1 | SHOULD | AMENDED | mac | 3-4 | 0 | Compute D4 descriptive metrics on frozen D5 benchmark: router branch accuracy, compatible Recall@K, abstention precision/recall, risk-coverage and sel _(aliases: T0-C12-R2, T8-C12-R2)_ |
| T9-C19-R2 | COULD | UNANIMOUS | mac | 4-6 | 0.5 | Optional: 5 hand-written feasibility/constraint demo cases using existing decision modules (no hypothesis test) |
| T9-C20-R1 | MUST | AMENDED | mac | 15-22 total | 4-6 each | Final report and slides (one item): skeleton with placeholders 13 Nov, fill tables from committed JSON as each result lands, full draft 21 Nov, human  _(aliases: T0-C13-R2, T9-C21-R1)_ |
| T9-C20-R2 | SHOULD | UNANIMOUS | mac | 4-6 | 0 | Figures: architecture (SSOT fig1), data tier/provenance, state-graph example, router route histogram, risk-coverage, ladder/ablation, decision registe |
| T9-C20-R3 | MUST | UNANIMOUS | human | 0 | 1 | Authors read and correct contributions section, confirm presentation date 25-26 Nov |
| T9-C21-R2 | SHOULD | UNANIMOUS | mac | 1-2 | 0.5 | Recorded demo fallback video/screens if hosting or VPN fails |
| T9-C22-R2 | SHOULD | UNANIMOUS | mac | 3-4 | 0.5 | Scenario script: pick >=5 of the 8 SSOT scenarios feasible with real data; each labelled with evidence class |
| T9-C23-R1 | COULD | UNANIMOUS | human | 2 | 1 | Choose paper angle (RAG paper §253.4 vs dataset §253.3 vs transition §253.5), outline sections and required missing evidence; record as DECISION |
| T9-C23-R2 | MUST | UNANIMOUS | any | 1 | 0 | Re-score MPU table after M1-M6 outcomes (true numbers) _(aliases: T0-C13-R1)_ |
| T9-C23-R3 | AFTER | UNANIMOUS | human | 1-2 | 2-4 expert | Food-science / chef review of a subset of answers and mechanism windows (outside expert) |
| T9-C24-R1 | SHOULD | UNANIMOUS | any | 3-4 | 0.5 | Write RELEASE_CARD.md (counts only) per §257A.16 for recipe base v1, EVD export, benchmark v1, physical L1/L2 layers, NER outputs |
| T9-C24-R2 | SHOULD | UNANIMOUS | manjot | 2-3 | 0 | Rerun-from-registry check: pick 3 run ids (router census, binding census Wikibooks, H1/H3) and reproduce on manjot; compare sha256 |
| T9-C24-R3 | COULD | UNANIMOUS | mac | 1 | 0 | Latency note for runtime RAG (query time of B5T/B7 in demo; cached assets listed) |
| T9-C25-R1 | MUST | UNANIMOUS | any | 2 | 0 | Aggregate compute ledger: remaining runs by host with agent-hours and wall-clock estimates (from all topics' inventories), VPN risk and disk budget |
| T9-C25-R3 | SHOULD | CONTESTED | human | 0 | 0.25 | VPN/route fix confirmation before server jobs (human network action) and fallback: Mac-only plan if VPN down |
| T9-C25-R4 | MUST | UNANIMOUS | any | 0.5 per run | 0 | Log every new S176 run row in compute_runs_v1.csv (orchestrator merges); counts-only outputs; sha256 _(aliases: T4-C20-R3)_ |
| T9-C25-R5 | SHOULD | AMENDED | human | 0.5-1 | 0.3-0.5 | Environment/installs authorisation decision (D-number): install sklearn/lightgbm/hypothesis/lxml/rdkit/torch on manjot vs run on Mac/vinayak; list exa _(aliases: T6-C06-R3, T9-C25-R2)_ |
| T9-C26-R1 | MUST | AMENDED | any | 1-2 | 0.5 | Publish consolidated day-by-day schedule (8-25 Nov) with human tasks front-loaded and slip triggers (e.g. no benchmark freeze by 17 Nov => H1/H3 repor |
| T9-C26-R2 | MUST | AMENDED | any | 1 | 0.5 | Declare fallback levels: (L0) full plan, (L1) H1 only, (L2) benchmark frozen but not run, (L3) results = router census + gates only; pre-write wording |
| T9-C26-R3 | SHOULD | CONTESTED | human | 0 | 2-3 each | Rehearsal and dry-run of talk including live-demo fallback (human) |
| T9-C26-R4 | MUST | AMENDED | any | 1-2 | 0.5 | Single human-time ledger + human-only items sheet: de-duplicated hours per person by task and week (approx. 16-20 h each over 9-16 Nov: signatures ~2, _(aliases: T0-C18-R1)_ |
| T9-C26-R5 | MUST | AMENDED | any | 2-3 | 0.5 | Prereg edit-lock: all pre-signature edits (07A ruling T2-C05-R5, H3/B7 reword T8-C12-R1 + H1 circularity caveat T8-C04-R2, power note T9-C12-R1, embed |
| T9-C28-R1 | MUST | UNANIMOUS | any | 1 | 0.25 | Write licence/redistribution paragraph for report + release card (what is shown: counts only; BBC never on server; Food.com CC0 unverified) |
| T9-C28-R2 | MUST | UNANIMOUS | any | 1-2 | 0 | Check slides/report/demo screenshots for recipe text leakage (automated grep of committed outputs against git-ignored text hashes) |
| T9-C29-R1 | SHOULD | UNANIMOUS | any | 2 | 0.25 | Generate G16 gate status table (14 gates: NOT_EVALUATED / FAIL / PARTIAL with path) and stop-rule check list for the report |
| T9-C30-R1 | SHOULD | UNANIMOUS | any | 2-3 | 0.25 | Produce DoD/checklist scorecard (17 + 21 items) with MET/PARTIAL/NOT_MET and evidence path; include in report appendix |
| T9-C31-R1 | COULD | UNANIMOUS | any | 3-4 | 0.5 | Build risk-control evidence table (20 risks) and RQ16 decision register for the 30 RQs (most NEED_DATA/OUT_OF_SCOPE) citing owning topic |
| T9-C32-R1 | MUST | CONTESTED | any | 3-4 | 0.5 | Number-class lint for deck/report: every number tagged EVD(E3-unverified/COND-unaudited) / TEXT_STATED / SCENARIO/ASSUMED_DEFAULT / MODEL_DERIVED/NON_ |

Topic contradictions recorded by the inventory: 12; SSOT requirements without plan coverage: 16 (see `topics/T9.json`). Resolved by round 1: Rung A count (T0/T3/T7/T9), defaults 27 rows (T4), SVAR 224 ids vs 254 rows (T0/T9), EVD lines vs ids (T2), physical % sample vs full corpus (T4/T5: use T4 full-corpus 3.4 % / 5.3 %).

## 7. Alias table (alias -> canonical [proposer])
| Alias | Canonical | Proposer |
|---|---|---|
| T0-C03-R1 | T3-C11-R1 | SYNTH |
| T0-C03-R3 | T3-C22-R1 | SYNTH |
| T0-C03-R4 | T3-C07-R3 | SYNTH |
| T0-C04-R2 | T4-C11-R3 | SYNTH |
| T0-C04-R3 | T4-C08-R1 | SYNTH (two-zone part -> T4-C09-R2) |
| T0-C04-R4 | T4-C05-R3 | SYNTH |
| T0-C05-R1 | T2-C09-R2 | SYNTH/C02 |
| T0-C05-R2 | T2-C09-R4 | R-FEAS |
| T0-C05-R3 | T5-C10-R5 | SYNTH |
| T0-C05-R4 | T6-C03-R3 | SYNTH |
| T0-C05-R5 | T5-C01-R3 | SYNTH |
| T0-C08-R1 | T8-C01-R1 | R-FEAS |
| T0-C08-R2 | T8-C02-R1 | SYNTH |
| T0-C09-R1 | T8-C18-R2 | SYNTH |
| T0-C09-R3 | T8-C15-R3 | SYNTH |
| T0-C10-R1 | T9-C07-R4 | SYNTH |
| T0-C11-R1 | T8-C20-R2 | R-SSOT (also covers T8-C20-R1 signature) |
| T0-C11-R2 | T8-C15-R1 | R-FEAS |
| T0-C11-R4 | T9-C17-R3 | SYNTH |
| T0-C12-R1 | T2-C05-R2 | SYNTH (R-SSOT T0-C12 xref) |
| T0-C12-R2 | T9-C18-R1 | SYNTH (R-SSOT T0-C12 xref) |
| T0-C13-R1 | T9-C23-R2 | R-SSOT |
| T0-C13-R2 | T9-C20-R1 | R-FEAS |
| T0-C14-R1 | T7-C01-R1 | SYNTH |
| T0-C14-R3 | T2-C18-R1 | SYNTH |
| T0-C18-R1 | T9-C26-R4 | R-SSOT xref + R-FEAS missing |
| T2-C09-R5 | T5-C10-R5 | R-SSOT |
| T2-C09-R6 | T5-C10-R6 | SYNTH/C02 |
| T2-C15-R2 | T6-C03-R1 | SYNTH |
| T3-C21-R2 | T2-C03-R1 | SYNTH |
| T3-C22-R4 | T5-C02-R2 | R-SCI (one shared rule) / SYNTH |
| T4-C02-R1 | T2-C05-R2 | R-FEAS |
| T4-C06-R1 | T0-C04-R1 | SYNTH |
| T4-C06-R2 | T0-C04-R1 | SYNTH |
| T4-C20-R1 | T2-C15-R1 | R-FEAS |
| T4-C20-R3 | T9-C25-R4 | SYNTH |
| T5-C06-R1 | T2-C05-R2 | SYNTH |
| T5-C09-R1 | T0-C04-R1 | R-SSOT |
| T5-C09-R2 | T4-C08-R1 | R-SSOT (two-zone part -> T4-C09-R2) |
| T5-C09-R3 | T4-C22-R1 | R-SSOT |
| T5-C10-R1 | T2-C09-R1 | SYNTH/C02 |
| T5-C10-R2 | T2-C09-R2 | SYNTH/C02 |
| T5-C10-R3 | T2-C09-R3 | SYNTH/C02 |
| T5-C10-R4 | T2-C09-R4 | SYNTH/C02 |
| T6-C05-R2 | T2-C05-R2 | SYNTH |
| T6-C06-R3 | T9-C25-R5 | R-SSOT |
| T6-C13-R1 | T2-C09-R4 | R-FEAS |
| T6-C13-R2 | T5-C10-R5 | R-SSOT |
| T6-C17-R2 | T5-C05-R4 | SYNTH |
| T6-C19-R2 | T9-C11-R1 | SYNTH |
| T7-C13-R2 | T3-C20-R2 | R-SSOT (T7-C13 reduce) / SYNTH |
| T8-C01-R2 | T8-C23-R1 | SYNTH |
| T8-C04-R1 | T8-C20-R2 | R-FEAS |
| T8-C08-R2 | T5-C05-R2 | SYNTH |
| T8-C12-R2 | T9-C18-R1 | SYNTH |
| T8-C17-R2 | T8-C20-R3 | SYNTH |
| T8-C20-R5 | T9-C17-R3 | SYNTH |
| T8-C24-R1 | T9-C07-R4 | SYNTH |
| T8-C24-R2 | T9-C12-R1 | SYNTH |
| T8-C25-R1 | T0-C06-R2 | R-SSOT |
| T9-C01-R1 | T0-C01-R1 | SYNTH |
| T9-C02-R1 | T2-C03-R1 | R-SSOT (reconcile part -> T2-C03-R3) |
| T9-C03-R2 | T2-C01-R2 | SYNTH |
| T9-C04-R1 | T2-C10-R4 | SYNTH |
| T9-C05-R1 | T0-C17-R1 | R-SSOT |
| T9-C05-R2 | T2-C18-R1 | R-SSOT |
| T9-C06-R3 | T3-C07-R1 | SYNTH |
| T9-C08-R1 | T2-C05-R1 | SYNTH |
| T9-C08-R2 | T8-C20-R1 | SYNTH |
| T9-C08-R3 | T6-C03-R1 | SYNTH (also covers T6-C03-R2 signature) |
| T9-C10-R1 | T6-C03-R1 | SYNTH |
| T9-C12-R3 | T8-C21-R2 | SYNTH |
| T9-C12-R4 | T8-C23-R1 | SYNTH |
| T9-C13-R1 | T2-C05-R2 | SYNTH |
| T9-C13-R2 | T2-C05-R3 | SYNTH |
| T9-C13-R3 | T3-C16-R1 | SYNTH |
| T9-C14-R1 | T2-C09-R2 | R-FEAS |
| T9-C14-R2 | T2-C09-R4 | R-FEAS |
| T9-C14-R3 | T2-C10-R1 | SYNTH |
| T9-C14-R4 | T2-C15-R1 | R-FEAS |
| T9-C15-R1 | T6-C03-R3 | SYNTH |
| T9-C16-R2 | T3-C16-R2 | SYNTH |
| T9-C17-R1 | T8-C20-R2 | R-SSOT |
| T9-C17-R2 | T8-C15-R1 | R-FEAS |
| T9-C17-R4 | T8-C15-R2 | SYNTH |
| T9-C19-R1 | T9-C07-R4 | SYNTH |
| T9-C21-R1 | T9-C20-R1 | R-FEAS |
| T9-C22-R1 | T8-C18-R1 | SYNTH |
| T9-C25-R2 | T9-C25-R5 | R-SSOT |
| T9-C27-R1 | T0-C04-R1 | SYNTH |
| T9-C27-R2 | T2-C09-R1 | SYNTH/C02 |
| T9-C28-R3 | T3-C07-R3 | SYNTH |

## 8. Open questions for round 2 (not contested by the rules, but need a vote)
- Priority promotions caused by merging (highest alias wins): T2-C01-R2, T2-C18-R1, T3-C20-R2, T9-C23-R2. R-FEAS may want some of them demoted.
- T3-C04 status: lane L-LOT has untracked matcher code (`lotstate/ing_match.py`, `sr_legacy.py`, `tools/lotstate_match_ing.py`). The component is still DRAFT in the ledger. Re-check against the S176_L-LOT report when it arrives, together with T3-C22 (now CODE), T4-C08/C09/C11/C15/C16 (now CODE partial).
- R-SSOT: every RUN status should cite a `registry/compute_runs_v1.csv` row id (only 14 rows exist). Do we add back-fill rows (T9-C11-R2) before the report?
- No T1 topic file: confirm it was merged into T0.
- T8-C16-R1 became MUST (R-SCI) and adds roughly 1-1.5 h of blind human judging per person in 17-19 Nov. It must appear in the T9-C26-R4 human-time ledger (R-FEAS load concern).
- Kush calendar constraints in T9-C26-R1 (R-FEAS) must be confirmed by Kush. They are not repo evidence.
