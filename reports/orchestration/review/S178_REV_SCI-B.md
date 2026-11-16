# S178 review SCI-B: evidence routing, evaluation statistics, corpus methods

Status: **AI_DRAFTED / PROPOSED.** This review is not a human gate, signature, approval or nonce (D-071). It may tighten, defer or refuse; it closes and signs nothing.

- Reviewer: SCI-B.
- Branch: `max/s176-orchestration`.
- Lanes reviewed: SCIFIX-ROUTER `b2ba3c0`, EVAL `42c01bf`, PREREG `3da963d`, ANALYSIS `d7cb55f`, CORPUS `2d45f68`, EVD `4b8e5fc`, INGCAT `e60b581`, FULLRUN `7f586e4`, GOVDOC `e358307`.
- Method:
  - I read the code and ran the tests.
  - I ran synthetic adversarial queries through `router_demo.route_text`, the gates and the screen.
  - I re-derived numbers from committed JSON, CSV and ledgers (read-only), and ran one 308-recipe spread sample (counts only).
- Nothing in the repo was changed except this file. There were no git writes and no full-corpus runs.
- No recipe text is quoted below; the example sentences are my own.

## 1. Verdict

**1 BLOCKER / 6 MAJOR / 23 MINOR.**

- **The router is honest at the screen level.**
  - UNKNOWN never becomes ABSENT or 0 inside the screen.
  - Merged lots and explicit prior-process events withhold DIRECT.
  - The census numbers re-derive exactly.
- **DIRECT still stands for a wrong state** when the earlier processing is *stated as a word* rather than as an event. It also stands for participles that Rung A turns into events (R2, R3).
- **ABSENT mostly rests on SR zeros that are not analytical** (R4).
- **Public mode leaks BBC-derived typical durations** through the scenario layer on both the API and the page (R1).
- **The statistics are right**: exact McNemar power, Clopper–Pearson and AC1 all recompute. Two logic problems sit in EVAL and PREREG (E1, P1).
- **The ANALYSIS EVD dataset card has wrong coverage numbers** (B1, BLOCKER under the brief's "committed number wrong" rule).

## 2. Findings

| id | sev | lane | file:line | finding | failure scenario | fix |
|---|---|---|---|---|---|---|
| R1 | MAJOR (blocks a hosted deploy) | SCIFIX-ROUTER | `src/culinarystate/simulation/scenario_layer.py:136-143`; `src/culinarystate/decision/demo_context.py:156` (`layer=SL.ScenarioLayer.load()`), `:99-121`, `:178`; `src/culinarystate/app/static/index.html:161` | Public mode filters KGE only inside `load_lexicon` and `load_requirements`. `ScenarioLayer.load()` reads `ledgers/data/KGE.jsonl` directly and keeps every ACTIVE `PROC_TYPICAL_DURATION` edge: 39 of 39, all BBC-derived by `public_mode.is_bbc_derived`. The mode is never passed to the layer. `physics_summary` returns `typical_duration_min` (and the core temperatures computed from it) with basis `KGE-0075xx`, and the page prints "Typical heat … for N min". The report's claim that "every BBC-derived KGE edge is dropped before any … duration candidate is built" is therefore false on this path. | Public mode (`CS_DEMO_PUBLIC=1`), `/api/ask` with recipe text "Boil the potatoes. Drain and fry the potatoes in oil." gives `recipe.physics.steps[0].scenario.typical_duration_min = 15.0` with `bases.duration_min = KGE-007576` (boil) and 5.0 with `KGE-007582` (fry). Both are BBC aggregates, and the page shows them. Verified with `physics_summary` and `ScenarioLayer.load()` as `DemoContext.load` builds them. | Give `ScenarioLayer.load` a `public: bool` parameter that drops every duration edge for which `PM.is_bbc_derived(e)` is true; call it with `public=mode.public` in `DemoContext.load`. In public mode an unstated duration becomes `SCENARIO_UNKNOWN` with `missing: ["duration_min"]`, and `index.html:161` must handle a missing `typical_duration_min`. Add a test: in public mode, walk the whole `/api/ask` response for every `KGE-\d+` id and assert that none is BBC-derived and none is `ING_CARBON_FOOTPRINT`. Correct the report sentence. |
| R2 | MAJOR | SCIFIX-ROUTER | `src/culinarystate/mechanism/evidence_gates.py:496-509` (prior kind comes only from `events[].produces`), `:627`; `src/culinarystate/mechanism/router_census.py:66` (the census routes steps only, so ingredient lines are never seen) | FINAL-SCI #7 is fixed for prior processing stated as an event. It is not fixed for the same fact stated as a word on the food mention ("boiled", "baked", "mashed", "tinned", "canned", "hard-boiled", "leftover", "frozen"). It is also not fixed for an ingredient line: the census never routes those lines, and the demo does not parse them for state. A raw-to-cooked EVD row then stays DIRECT for a food the text says is already processed. That is the wrong state under §286.2 G0-C, and it is Layer 1 TEXT_STATED information that the gate ignores. | My synthetic queries (vitamin C, real ledgers, shipped gates):<br>• "Fry the baked potatoes." → DIRECT (EVD-002349, EVD-002453)<br>• "Fry the mashed potatoes." → DIRECT<br>• "Fry the tinned tomatoes." → DIRECT (EVD-002791)<br>• "Fry the hard-boiled eggs." → DIRECT (EVD-000139)<br>• An ingredient line "1 can chopped tomatoes" and then "Fry the tomatoes" → DIRECT<br>• An ingredient line "2 boiled potatoes" and then "Fry the potatoes in the oil." → DIRECT<br>Control: "Boil the potatoes. Drain… Fry…" → fry is withheld with `PRIOR_PROCESS_CONTEXT`. | Add a `STATED_PRIOR_STATE` source to `lot_members`: a root entity whose own mention, or its matched ingredient line, carries a processed-state modifier gets prior kind HEAT, LEACH or PRESERVED from a small registered word list with spans (Layer 1, never inferred). Route the ingredient lines in the census, or pass each line's state flag in with the steps. Withhold DIRECT with `PRIOR_PROCESS_CONTEXT` and basis `TEXT_STATED_STATE`. Add the six queries above as tests. Re-run the census and report how many DIRECT items move. |
| R3 | MAJOR | SCIFIX-ROUTER (Rung A, pre-existing; it affects the committed 40,308) | `src/culinarystate/extraction/rung_a_binding.py:224-228` (every ACTION mention becomes an event); `src/culinarystate/mechanism/router_demo.py:136-141` | Attributive participles and serving suggestions ("roast" or "grilled" or "canned" or "mashed" + food) become heat or preservation events of their own. Each one gets DIRECT from the EVD row for that process, although the recipe never performs the process. | In a spread sample of 308 Food.com recipes (every 1,700th, steps only, shipped gates), **5 of 24 DIRECT items (4 recipes; Wilson 95 % CI 9–40 %) were of this kind**:<br>• a serving-suggestion "roast \<meat\>" → DIRECT roast, twice<br>• "over grilled \<seafood\>" → DIRECT grill<br>• "fresh and canned \<fruit\>" → DIRECT can<br>• "add mashed \<potato\>" → DIRECT mash<br>So the 40,308 full-census DIRECT likely includes a material share of processes that were never performed. | In the router, treat an ACTION whose surface is a past participle or attributive (it is followed directly by its own FOOD_MENTION object and governs no verb phrase) as a state of that food, not as an event. It then feeds R2's `STATED_PRIOR_STATE` and gets no DIRECT of its own (reason `ATTRIBUTIVE_STATE_NOT_EVENT`). Measure the share on the 1,000-sample before and after the change, and state it in the S177 report next to 40,308. |
| R4 | MAJOR | SCIFIX-ROUTER | `evidence_gates.py:29` ("a screen on MEASURED composition"), `:201-224` (`read_sr_values` reads `amount` only), `:341-363`; `tools/build_target_content_table.py`; `reports/s177/absent_top50_for_human_review.csv` (no basis column) | ABSENT is a negative claim; it routes 813,547 items to NOT_APPLICABLE. It mostly rests on SR zeros that are not analytical. `food_nutrient.csv` carries `derivation_id` and `data_points`, but the table drops both. | Over the plausible candidates of the 52 shipped ABSENT ING (vitamin C), only **13 of 52** ING have every value analytical (A, AI or AR). The others rest on:<br>• `Z` "Assumed zero": 9 values<br>• blank derivation with 0 data points: 40 values (e.g. butter fdc 173410, olive oil 171413 and flour 169761 are all 0 mg, 0 data points, no derivation)<br>• imputed, formulation, recipe or label-claim codes (PIK, FLA, FLC, O, RA, LC)<br>Of the 67 category-blocked ING, only 17 have every value analytical. A human checking the top-50 sheet sees "0" and reads it as measured. | Carry `sr_derivation_code` and `sr_data_points` per candidate into the content table, and into both review CSVs and the top-100 INGCAT sheet. ABSENT should need every plausible value to be analytical with `data_points ≥ 1`. Otherwise either return UNKNOWN with blocker `SR_ZERO_NOT_ANALYTICAL`, or, if a human so decides, return a separate state `ABSENT_SR_ASSUMED` with its own reason code. Reword the docstring at `:29` to "SR Legacy composition (analytical, imputed or assumed; basis recorded)". |
| E1 | MAJOR | EVAL | `src/culinarystate/evaluation/h1_independence.py:61-67`; the test at `tests/unit/test_s178_eval_h1_independence.py:35` pins the bug | `gold_origin` returns HUMAN_BLIND for any verdict KEEP or EDIT with `seen_system_output=false`, even when the gold value is the engine draft. An explicit `gold_origin` column also wins with no evidence, and `drafted_by=AI_AGENT_*` is ignored. | Under D5 option G-B (a human KEEPs or EDITs an engine draft after a blind pass), a row {drafted_by AI_AGENT_S171, KEEP, seen false, gold = engine output} becomes HUMAN_BLIND, and the set is labelled INDEPENDENT_GOLD. The amendment itself calls G-B engine-anchored. | Return HUMAN_BLIND only when the scored gold comes from a filled blind-answer column (`gold_source=BLIND_HUMAN`) and `seen=false`. KEEP or EDIT of an engine-drafted gold → HUMAN_AFTER_SEEING_ENGINE. An explicit HUMAN_BLIND on an AI-drafted row with empty blind columns → refuse. Flip the test at :35. |
| P1 | MAJOR (D-071) | PREREG | `reports/step07/07A_R1_preregistration_AMENDMENT_S178_DRAFT.md:21, 31-52, 141, 158-163` | **(i)** "IDENTICAL_JUDGEMENTS … replaced by three stronger copy checks" is false: none of the three catches a judgement-only copy. **(ii)** §1 says the options are "not a post-hoc weakening", but it compares Option A only with the unsigned S171 draft. Against the signed R-06, A passes patterns that R-06 fails (the kappa-paradox region), yet A, not A-keep, is the AI recommendation. An AI may not recommend loosening a signed gate as if it were not a loosening. | **(i)** Reviewer 2 copies reviewer 1's 10 judgement columns and blanks the reasons. The old rule gives NOT_COUNTED; all three new checks pass. **(ii)** Synthetic run: reviewer 1 all CORRECT; reviewer 2 marks SBA on 5 conditions in 5 fields; adjudicated to 0 defects. R-06 pooled kappa is 0.0 → FAIL. Option A: bootstrap AC1 lower bound 0.989, co-gate 0 → PASS. | Make the recommendation "A-keep", or "no AI recommendation (HUMAN)". Replace "stronger" with "different; does not catch a judgement-only copy". Add to §1: "A passes some patterns R-06 fails; choosing it is a human loosening of R-06, recorded in the human's own D-0NN", with the counterexample. |
| B1 | **BLOCKER** (committed numbers wrong; the fork rated it MAJOR) | ANALYSIS | `tools/s178_analysis_evd_card.py:270`, `:266-268`, `:278`; output `reports/s178/analysis/evd_dataset_card_v1.md:91-100` | The EVD dataset card (the 15a candidate) misstates condition coverage. I verified this myself:<br>**(a)** It hard-codes water activity as `NOT_IN_COND_SCHEMA`, but the COND schema has `water_activity` (`src/culinarystate/ledgers/registry.py:195`); the field is just never filled.<br>**(b)** The md table drops the `ABSENT_FROM_MASK` status. The pressure row (129 / 0 / 0 / 7,018) sums to 7,147 of 17,978, so 10,831 rows vanish.<br>**(c)** Missingness counts only `UNKNOWN`, so Bognar pressure shows 0.0 % missing although it is 100 % unrecorded.<br>**(d)** Temperature "RANGE 3,585" is 3,369 one-sided CENSORED bounds plus 216 true ranges. | A reader concludes that pressure is never missing, that a_w cannot be recorded and that 3,585 rows have a temperature range. All three are false. | Report a_w as `IN_SCHEMA_NEVER_POPULATED (0 rows)`. Add a "not recorded" column. Count `ABSENT_FROM_MASK` as missing in `s203_9_11`. Split temperature into CENSORED_ONE_SIDED and RANGE using `cond.temperatures[].value.status`. Add a test that each axis row sums to N. Regenerate the card and re-run RUN-S178-EVD-007, whose hashes will change. |
| R5 | MINOR | SCIFIX-ROUTER | `evidence_gates.py:476-480`, `:611-613` | **(a)** An ancestor event with no resolved `proc_id` counts as "no prior process". That is fail-open: 305,077 items come from unresolved events (EVENT_UNRESOLVED in the full census), and a lot that passed through one keeps DIRECT. **(b)** `evaluate` with `NO_LOT` keeps a raw DIRECT. This is unreachable from `route_text` today but unguarded. | **(a)** A lot touched by an unresolved event, then fried → DIRECT, and the census reports nothing about it. **(b)** A future caller passes `lots=[]` with a DIRECT pre-check, and DIRECT stands. | **(a)** Count `prior_unresolved` per item in the census. Withhold with `PRIOR_PROCESS_UNRESOLVED`, or at least report it next to the DIRECT count. **(b)** In `evaluate`, `NO_LOT` with `raw_precheck != "NONE"` → `final="NONE"`, withheld. |
| R6 | MINOR | SCIFIX-ROUTER | `evidence_gates.py:107-112` (PRIOR_* classes) | The prior-process classes are coarse in both directions:<br>• They withhold EVD rows that presuppose prior cooking: "Boil … Reheat the potatoes" → reheat is withheld, although the reheat row is about cooked food. Drain after boil is withheld too.<br>• Freeze and thaw are not prior processes at all: "Freeze the potatoes. Fry…" → DIRECT. | Over-withholding is the safe direction, but the census overstates the cost of #7. Freeze → fry applies a raw-to-fried retention row to frozen food. | Hand this to a human (Q1). If accepted: add a `presupposes_prior_heat` flag for reheat (PROC-000033) and drain-after-boil EVD rows, and add freeze and thaw as a PRESERVED kind. Count each kind separately in the census. |
| R7 | MINOR | INGCAT | `tools/s178_ingcat_propose.py:707`; `reports/s178/ingcat/top100_for_human_confirmation.md` (e.g. lines for water, salt, egg) | The confirmation sheet tags rows "unlocks ABSENT" and shows the SR group right next to each proposal. That steers the human towards accepting, and it hides that the ABSENT being unlocked mostly rests on non-analytical SR zeros (R4). Confirming a REGISTRY_SR + LEXICAL proposal makes ABSENT condition (c) a check of AI lexical rules against the SR group. **No proposal is consumed today** (see §3). | A human ticks "water → BEVERAGE [MEDIUM] … unlocks ABSENT" for its impact (1,427,479 items), not on its merits. | Replace "unlocks ABSENT" with a neutral "affects ABSENT screen (n items)". Add the SR derivation and data-points basis (R4). Add one line: "Judge the category from the food itself; the SR group shown is the router's identity, not evidence for the category." |
| E2 | MINOR | EVAL | `src/culinarystate/evaluation/h3_independent.py:362`; `S178_EVAL_report.md` §2 | `can_be_significant = b + c >= 6` hard-codes the two-sided floor. The recommended D-D5-6 test is one-sided, with floor 5. | A 5-0 split gives one-sided p = 0.03125, yet the function returns `can_be_significant=False`. | Use floor 5 for one-sided and 6 for two-sided, return both flags, and correct the report sentence. |
| E3 | MINOR | EVAL | `h3_independent.py:204` | The SIMILAR regex `\b{name}` has no trailing boundary. | Question "pea" against row "Peanuts, raw" → SIMILAR (verified by the fork). | `rf"\b{re.escape(n)}(?:e?s)?\b"` |
| E4 | MINOR | EVAL | `h3_independent.py:185-186, 245, 258-260` | Fail-open: with `cell=None`, relevance is NOT_CHECKED and the claim counts as SUPPORTED. | A D5 runner that omits `cell` silently falls back to "value matches any cited row" (WRONG_CELL). | Add `require_cell=True` in the D5 path; `summarize_rung` counts NOT_CHECKED separately. |
| E5 | MINOR | EVAL | `src/culinarystate/evaluation/split_registry.py:116-128` | The verifier accepts either hash convention and never checks `unit_ids_sha256`. The 16 DIAG29 rows are skipped silently. | Editing REC-012022 → REC-999999 in `split_registry_units_v1.csv` gives `verify_registry` → []. | Check `unit_ids_sha256` from `attributes`, name one hash convention per row, and emit NOT_VERIFIABLE_FROM_LISTING for DIAG29. |
| E6 | MINOR | EVAL | `src/culinarystate/evaluation/h1_rungs.py` (`state_block` docstring, `context` defaults) | The docstring says "no parent-lot walk", but the code walks `parent_entity_ids`. `context()` defaults to the leaky S173 settings. | A D5 runner that calls `context()` with defaults re-leaks the S1 gold (20/20 contexts). | Correct the docstring. Make the D5 runner use `independent_context` and `assert_independent`, or make `context` raise for D5 qids with legacy defaults. |
| E7 | MINOR | EVAL, PREREG | `src/culinarystate/evaluation/mcnemar_power.py:86-89`; EVAL report §2; D5 amendment C5 | "Power is a sawtooth in delta → conservative MDE" is wrong: at fixed n and d, power is monotone in delta (the sawtooth is in n). The headline ranges also mix discordance ranges: n=30 covers d 0.3–0.5, n=60 covers d 0.2–0.5. | A reader compares "n=60 0.165–0.265" with n=30 as if both covered the same d range. | Drop the sawtooth claim, state the grid step, and give the d range per n (n=60, d 0.3–0.5: 0.205–0.265; d 0.2: 0.165). |
| E8 | MINOR | EVAL | `tools/s178_leakage_audit_d5.py:184` | The id scan skips all of `reports/s178/`, not just EVAL's own outputs. | S recipe ids named in the ANALYSIS, CORPUS or EVD outputs go unscanned. | Exclude only an explicit list of EVAL output paths. |
| P2 | MINOR | PREREG | `07A_R1_..._AMENDMENT_S178_DRAFT.md:172-174` | "at most 1 of 100" and "at most 4 of 100" hold only for n=100. | Under U2 (120 conditions), X_any 0.90 admits 6 of 120. | State the counts per n, or define the co-gate by the CP bound alone. |
| CORP-1 | MINOR | CORPUS, ANALYSIS | `tools/s178_analysis_coverage_census.py:21, 439` → `reports/s178/analysis/ing_alias_coverage_census_v1.md:214`, `.json:1381` | **The 78.0 % vs 79.5 % discrepancy: both numbers are right.**<br>• 78.0 % = 407,536 of 522,517, the full corpus (re-derived from the parquet).<br>• 79.5 % = 683 of 859, the S176 seeded sample; it is within about 1.1 SE of 78.0 %.<br>Only the coverage census quotes 79.5 % bare, as if it were the corpus rate. | A reader quotes 79.5 % as the Food.com misalignment rate. | Write "78.0 % (407,536 / 522,517, full corpus; S176 sample 79.5 %)" and regenerate. |
| CORP-2 | MINOR | CORPUS | `src/culinarystate/quantity/prenormalize.py:63, 114-118` | The hyphen-mixed rule handles ASCII `N-a/b` only. `1-½`, `1–1/2` (en dash) and `2 - 1/2` still parse as RANGE with low > high: 2 of 32,036 Wikibooks lines after pre-normalisation. | `"1-½ cups"` → RANGE(1, 0.5), with no flag. | In the opt-in path: RANGE with low > high → UNKNOWN with flag `INVERTED_RANGE`. Optionally extend the rule to U+2013 and to a vulgar-fraction right-hand side. Add tests. |
| CORP-3 | MINOR | CORPUS | `src/culinarystate/quantity/foodcom_pairing.py:239-256` | `pair_lines`, offered as the drop-in for `iter_foodcom`, returns bare strings and so loses `QUANTITY_UNKNOWN_LENGTH_MISMATCH`. | A consumer can no longer tell "misaligned" from "the source says nothing". | Return `(line, status)` (or add `pair_lines_with_status`) and point report §3.3 at it. |
| CORP-4 | MINOR | CORPUS | `tools/s178_corpus_replay_invariants.py:73-125`; report `S178_CORPUS_report.md:96, 107` | The "independent" replay check:<br>• inherits the engine's applied vector instead of re-deriving it (67,627 Food.com cascade rejections are taken as given);<br>• imports `LIFECYCLE_BY_TYPE` and `PARTITION_KINDS` from the engine;<br>• plants every mutation at a trivial position;<br>• says "six invariants" in its docstring but checks seven. | A wrong engine rejection or lifecycle mapping still shows 0 disagreements. | Compute the applied vector independently; copy the constants locally with an equality test; plant mutations mid-graph at random positions; fix the count. |
| CORP-5 | MINOR | CORPUS | `S178_CORPUS_report.md:96, 107`; `src/culinarystate/extraction/rung_a_binding.py:213-226` | ORDER_REGRESSION and EVENT_ID_REUSED hold by construction: ids are sequential `E{n}` and the loops run in order. "0 over 14.2 M events" is a tautology, not validation. | A reader reads it as corpus-scale validation of extraction. | Mark them `HOLDS_BY_CONSTRUCTION` with the citation, and say that only ENTITY_UNKNOWN carries information. |
| CORP-6 | MINOR | CORPUS | `tools/s178_corpus_replay_invariants.py:310-313`; `tools/s178_corpus_verb_census.py:95-140`; `reports/s178/corpus/sp002_prenorm_rerun_v1.md:50` | Three gaps:<br>• The determinism check runs in one process.<br>• The verb census does not filter mapped tokens with the food/tool/closed-class filter, so the denominator depends on the outcome.<br>• "18,723 identical of 18,723" is a capped sample of 79,196 lines. | The claims read as cross-run reproducibility, unbiased coverage and an exhaustive check. | Re-run determinism in a subprocess with a different `PYTHONHASHSEED`; apply the filter before the ACTION branch; write "18,723 sampled of 79,196". |
| B2 | MINOR | ANALYSIS, GOVDOC | `registry/negative_results_register_v1.csv` (NEG-0032, NEG-0045); `STATUS.md` (M1 row); `reports/s178/g16_gate_status.md` §2; `reports/s178/analysis/corpus_can_say_v1.*` | Several numbers are stale against later committed outputs:<br>• NEG-0032 and STATUS M1 quote the S176 gated DIRECT 34,537. The S177 census gives 40,308 of 35,256,601 (0.114 %), re-derived.<br>• G16 cites the ungated S171 0.754 %.<br>• NEG-0045 says 197 liquid-T > 150 °C events; v04 says 21.<br>• The can-say tables use the v02/v03 censuses. | A slide quotes 34,537 or 0.754 % as the current router result. | Append new NEG rows (do not edit the old ones). Update STATUS M1 with its path. Quote 0.114 % next to 0.754 % in G16. Label the can-say outputs "v02/v03; v04 rebuild pending". |
| B3 | MINOR | GOVDOC, FULLRUN | `STATUS.md`, `registry/compute_runs_v1.csv` (e358307); `handoff/MAC_TASKS_FROM_CONSOLIDATION_S177.md` (7f586e4) | Lanes wrote orchestrator-only files; the orchestrator adopted the edits. Some GOVDOC edits landed in the router commit `b2ba3c0` and in PHYS2 `32415c4`. | `git show e358307` does not contain what the GOVDOC report lists. | Add an orchestrator WORKLOG note mapping files to their real commits. In future, lanes hand these edits back instead. |
| B4 | MINOR | GOVDOC, ANALYSIS, EVAL, PREREG | `registry/compute_runs_v1.csv` | Run rows are missing for GOV-001, ANA-001..007, the 3 PREREG runs and the 5 EVAL runs. | NEG-0031..0045 and `reports/s178/analysis/*` have no run record. | The orchestrator merges the rows already printed in each lane report. |
| B5 | MINOR | EVD | `tools/s178_evd_transition_audit.py:47-49, 62-66` | The `violations` block omits two invariants. The y = 0 check compares totals, not rows. Some paths are vacuous on real data; they are pinned as xfail, honestly. | One imputed 0 plus one dropped measured 0 cancel out, and "0 violations" still shows. | Add both booleans to `violations`. Check y = 0 per row by joining to the EVD id. |
| B6 | MINOR | FULLRUN | `reports/orchestration/S177_FULLRUN_report.md` §1 bullet 3 | "ANY_MEMBER_PH_UNKNOWN 98–99 % in every family" is wrong for Food.com, which is 96.7 % (502,903 / 520,298) in the report's own table. | The headline misstates the Food.com share. | Write "96.7–99.4 %". |
| B7 | MINOR | EVD (orchestrator files) | `handoff/MAX_PLAN_REVIEW_PACKET_2026-11-08.md:123`; `registry/component_ledger_v1.csv:436`; `reports/orchestration/ssot_consensus/CONSENSUS_PLAN_2026-11-08.md:53, 60` | Four lines still say "355 SVAR". | Someone quotes 355 as the number of variables. | Write "355 version lines = 224 ids (223 CHEMICAL + 1 PHYSICAL)". |

## 3. Checked and correct

**Router honesty (SCIFIX-ROUTER).**

*Synthetic queries, run on the real ledgers with the shipped gates, target vitamin C:*
- **Merged lot.** "Mix the potatoes and the tomatoes. Fry the mixture." → fry is UNKNOWN with `MERGED_LOT_CONTEXT`; ungated DIRECT is withheld.
- **Boiled, then fried.** "Boil … Drain … Fry the potatoes" → boil DIRECT, drain UNKNOWN, fry UNKNOWN with `PRIOR_PROCESS_CONTEXT` (HEAT + LEACH). Microwave, parboil, blanch, char, sous-vide and "nuke" before frying also withhold.
- **ING with no SR match.**
  - All 111 ING of registry kind NO_SR_EQUIVALENT, NOT_A_FOOD or AMBIGUOUS → UNKNOWN with `NO_USABLE_IDENTITY`.
  - An id not in the table → UNKNOWN; `None` → UNKNOWN.
  - None of them is ABSENT.
- **AI category that disagrees with the SR group.**
  - Overlaying the 53 INGCAT proposals that the crosswalk rejects gives only PRESENT, `CATEGORY_MISMATCH` or `RANK1_NOT_HIGH`. Never ABSENT.
  - Live (no overlay), the same ING are `CATEGORY_EMPTY`, PRESENT or `RANK1_NOT_HIGH`.
- **All candidates UNKNOWN.**
  - No SR value for any candidate → UNKNOWN with `SR_VALUE_MISSING`, and the lot is UNKNOWN.
  - Rank 1 = 0 with a LOW alternate missing → UNKNOWN with `SR_VALUE_MISSING`.
  - An ABSENT member plus a root of unknown identity → UNKNOWN.
  - An unscreened target → NOT_SCREENED.

*Code reading:*
- An empty SR amount stays missing at `evidence_gates.py:215`, in `build_table_rows` and in `read_table_full`. UNKNOWN is never 0 inside the router.
- ABSENT wins only through `lot_state`, which needs every member ABSENT and 0 unknown roots.
- The gates only narrow routes (never-upgrade).

**Census re-derived from `reports/step23/router_demo_census_vitc_nonBBC_full_S177.json`.**
- DIRECT ungated is 267,933 → 40,308 gated.
- `PRIOR_PROCESS_CONTEXT` is 11,861 = HEAT 8,012 + HEAT_LEACH 2,188 + LEACH 1,661 = 6,397 + 5,464 in the cross-tab.
- Routes sum to 35,256,601 = items, and the ungated cross-tab sums to 267,933.
- The UNKNOWN member blockers sum to 20,178,675 = UNKNOWN members.
- 52 ABSENT ING hold 4,191,765 items; 63 category-blocked ING hold 5,544,505 items.
- ABSENT among ungated-DIRECT items: 36,328 (13.6 %) → 1,666 (0.6 %).
- All 19 code hashes in `code_provenance` equal the files at `b2ba3c0`, so the run is reproducible from the commit despite `code_unchanged_during_run=false`. Only `router_demo.py` changed since, in AASIM.

**SR identity adapter (`mechanism/sr_identity.py`).**
- Kind → band mapping:
  - DIRECT and UK_US → HIGH alone.
  - DEFAULT_FORM → HIGH, plus the legacy rank 1–3 as LOW alternates at the anchor score, so every form must agree.
  - APPROX → MEDIUM, and the legacy fallback is capped at MEDIUM; neither can support ABSENT.
- The unmappable kinds get no fallback.
- `composition/` is read only through `load_registry` and `normalise`; it is unmodified (the diff is empty).
- The router no longer imports `lotstate/`.

**Public mode, apart from R1.**
- The KGE before/after counts re-derive exactly: ALTERNATIVE 220 → 4, FOLLOWED_BY 63 → 4, PROCESSED_BY 2,132 → 367, DURATION 39 → 0, USES_TOOL 543 → 13, CARBON 134 → 0.
- Mode resolution behaves as documented: fail-closed on an unreadable value; ON for non-loopback hosts and hosted markers.
- `demo_mode` is on every `respond` output, and `/api/health` reports the mode.
- The troubleshooting registry has 0 BBC rows (Gutenberg / Wikibooks only).
- Carbon is emptied in the only reader (`pipeline.load_lexicon`).

**INGCAT.**
- **No proposed category is consumed by the router.**
  - The router takes `ing_category` from the shipped content table. Its categories equal the ING ledger's for all 876 ING (0 mismatches).
  - No proposal ING has a non-empty category in the table.
  - No module under `src/` reads `registry/ing_category_proposals_S178_DRAFT.csv`.
  - All 1,417 `human_decision` values are empty.
  - The ledger diff `a0a5b49..HEAD -- ledgers/` is empty.
- Every HIGH proposal has a lexical basis as well as an SR basis; none rests on the SR group alone.
- Counts re-derived: 2,048 ACTIVE ING = 631 with a category + 1,417 without; HIGH 193, MEDIUM 914, LOW 310.

**Statistics (EVAL, PREREG).**
- My independent scipy `binomtest` exact conditional McNemar power reproduces every MDE: n=30 none / 0.275 / 0.325 / 0.365; n=60 0.165 / 0.205 / 0.235 / 0.265. Two cells:
  - n30, g0.30, d0.40 = 0.7131
  - n60, g0.20, d0.40 = 0.6349
- The EVAL and PREREG grids agree.
- Clopper–Pearson matches scipy beta to 4e-16, including k=0 and k=n, with α/2 per tail.
- Gwet AC1 recomputes to 0.9944 with kappa 0.0.
- **H3 scorer independence.** Its only culinarystate import is `evaluation.paired_stats`; it imports no decision, mechanism, simulation or generation code.
- **H1 circularity.** All 40 S gold rows are ENGINE_DRAFT, and the source sha256 matches. The report reads H1 as self-consistency only.
- **Leakage audit.** The role counts sum to 101 per split, and the conclusions are hedged.
- **Split registry.** Hashes are sorted and newline-joined (order-stable), and S1∩S2 = 0.
- **Option design.** The planted-errors design can fail, and the co-gate can fail. The one-sided H3 sign test is not a loosening.

**CORPUS.**
- The SP-002 pre-normaliser is opt-in: no module under `src/` imports it, and only the lane's tools and tests do.
- It is versioned (`CQPO_SP002_PRENORM_V1_DRAFT`, with a `+PRENORM` suffix only when a rule fired). Raw text is preserved.
- Existing outputs are unchanged: 0 differences against S161 in all three families. The only file the commit edited rather than added is `compute_runs` (rows appended).
- The equal-length pairing rule reproduces `iter_foodcom`. It is stated as necessary, not sufficient.
- 14,196,900 replay events re-derive.

**ANALYSIS, EVD, GOVDOC, FULLRUN.**
- The protected ledgers and the Mac tool are unchanged.
- The 8 FULLRUN sha256 values match.
- SVAR is 355 lines = 224 ids.
- The glibc `log` last-digit finding holds: 31 of 100,000 values on this host.
- NEG-0031..0045 are append-only.
- G16 is 0 PASS / 1 FAIL / 8 PARTIAL / 5 NOT_EVALUATED, and no gate was passed by AI.
- §238 field counts and 5 populated counts recompute.

**Headline numbers verified against their committed sources (10).**
1. Router DIRECT 267,933 → 40,308.
2. `PRIOR_PROCESS_CONTEXT` 11,861.
3. ABSENT ING 52 / 4,191,765 items.
4. Public-mode KGE counts.
5. INGCAT 1,417 / 193 / 914 / 310.
6. Food.com misalignment 407,536 / 522,517 = 78.0 %.
7. The McNemar MDE ranges.
8. SVAR 355 lines = 224 ids.
9. Food.com exact ING/ALIAS coverage 82.19 %.
10. FULLRUN Food.com pH-unknown share 96.7 %, which contradicts the report's prose "98–99 %" (B6).

**Tests.**
- The union of the lanes' test files ran with `nice -n 10`:
  - router: `test_s176_demo_honesty`, `test_s176_evidence_gates`, `test_s177_router_{gates,public_mode}`, `test_s177_sr_identity_adapter`
  - S178 lanes: `test_s178_{eval,analysis,corpus,evd,ingcat}_*`, `ladder_crosswalk`, `prompt_registry`, `ssot238_conformance`, `ssot_coverage_map`
- Result: **566 passed, 1 skipped (no sklearn), 3 xfailed (strict, expected), 2 deselected (`-m ledgers`)**.
- PREREG has no pytest files; its calc scripts were recomputed independently. FULLRUN is a data lane with no tests.

## 4. Questions for a human

1. **Prior-process classes (R6).**
   - Should EVD rows that presuppose a prior cook be exempt from `PRIOR_PROCESS_CONTEXT`? These are reheat, and drain after boil.
   - Should freeze and thaw count as a prior state?
2. **Basis of ABSENT (R4).**
   - May ABSENT rest on an SR "assumed zero" (`Z`) or on a 0-data-point zero with no derivation code?
   - If yes, the route should carry a distinct reason, so the claim is not read as resting on measurement.
3. **07.A option choice (P1).**
   - Option A would pass some patterns that the signed R-06 fails. Choosing it is a human loosening and needs the human's own D-0NN.
   - The accuracy co-gate is adjudicated by the same two reviewers. Should a third person adjudicate?

| id | sev | lane | file:line | finding (short) |
|---|---|---|---|---|
| B1 | BLOCKER | ANALYSIS | tools/s178_analysis_evd_card.py:266-278 | EVD card: a_w "not in schema" (it is), pressure row loses 10,831 rows, Bognar pressure 0 % missing, RANGE mixes CENSORED |
| R1 | MAJOR | SCIFIX-ROUTER | scenario_layer.py:136-143; demo_context.py:156; index.html:161 | Public mode leaks 39 BBC-derived typical durations through the scenario layer (API + page) |
| R2 | MAJOR | SCIFIX-ROUTER | evidence_gates.py:496-509; router_census.py:66 | Pre-processing stated as a word or an ingredient line ("baked/tinned/hard-boiled", "1 can …") still gets DIRECT |
| R3 | MAJOR | SCIFIX-ROUTER (Rung A) | rung_a_binding.py:224-228 | Attributive participles and serving suggestions become events with DIRECT: 5/24 DIRECT in a 308-recipe sample |
| R4 | MAJOR | SCIFIX-ROUTER | evidence_gates.py:29, 201-224, 341-363 | ABSENT rests on non-analytical SR zeros (only 13/52 ING all-analytical); derivation dropped; "measured" claim false |
| E1 | MAJOR | EVAL | h1_independence.py:61-67 | KEEP + seen=false → HUMAN_BLIND even when gold = engine draft |
| P1 | MAJOR | PREREG | 07A amendment :21, 31-52, 141, 158-163 | Recommended Option A loosens R-06 (counterexample); "stronger copy checks" false (D-071) |
| R5 | MINOR | SCIFIX-ROUTER | evidence_gates.py:476-480, 611-613 | Unresolved ancestor event = "no prior process" (fail-open); NO_LOT keeps a raw DIRECT |
| R6 | MINOR | SCIFIX-ROUTER | evidence_gates.py:107-112 | Classes withhold reheat/drain rows that presuppose cooking; freeze → fry stays DIRECT |
| R7 | MINOR | INGCAT | s178_ingcat_propose.py:707; top100 sheet | "unlocks ABSENT" tag steers confirmation and hides the SR-zero basis; no proposal is consumed (correct) |
| E2 | MINOR | EVAL | h3_independent.py:362 | `can_be_significant` uses the two-sided floor under a one-sided test |
| E3 | MINOR | EVAL | h3_independent.py:204 | "pea" matches "peanut" as SIMILAR |
| E4 | MINOR | EVAL | h3_independent.py:185, 245 | cell=None → NOT_CHECKED counted SUPPORTED |
| E5 | MINOR | EVAL | split_registry.py:116-128 | Recipe swap undetected; DIAG29 rows unverified |
| E6 | MINOR | EVAL | h1_rungs.py | Wrong docstring; leaky `context()` defaults |
| E7 | MINOR | EVAL, PREREG | mcnemar_power.py:86-89 | "Sawtooth / conservative" is wrong; MDE ranges mix d ranges |
| E8 | MINOR | EVAL | s178_leakage_audit_d5.py:184 | Scan skips all of reports/s178/ |
| P2 | MINOR | PREREG | 07A amendment :172-174 | ≤1/≤4 counts hold for n=100 only |
| CORP-1 | MINOR | CORPUS, ANALYSIS | coverage_census md:214 | 79.5 % (sample) quoted bare; the corpus rate is 78.0 %; both are correct |
| CORP-2 | MINOR | CORPUS | prenormalize.py:63, 114-118 | Inverted RANGE survives (`1-½`, en dash) |
| CORP-3 | MINOR | CORPUS | foodcom_pairing.py:239-256 | `pair_lines` drops the mismatch status |
| CORP-4 | MINOR | CORPUS | s178_corpus_replay_invariants.py:73-125 | Replay check not independent; trivial mutations |
| CORP-5 | MINOR | CORPUS | CORPUS report :96, 107 | Two invariants hold by construction (tautology) |
| CORP-6 | MINOR | CORPUS | replay :310-313; verb census :95-140 | Single-process determinism; biased verb denominator; sample called exhaustive |
| B2 | MINOR | ANALYSIS, GOVDOC | NEG-0032/0045; STATUS M1; G16 | Stale 34,537 / 0.754 % / 197 numbers |
| B3 | MINOR | GOVDOC, FULLRUN | STATUS.md; compute_runs; handoff | Orchestrator-only files written by lanes; edits in other commits |
| B4 | MINOR | several | compute_runs_v1.csv | Missing run rows (GOV-001, ANA, PREREG, EVAL) |
| B5 | MINOR | EVD | s178_evd_transition_audit.py:47-66 | Violations block incomplete; y=0 check by totals |
| B6 | MINOR | FULLRUN | FULLRUN report §1 | "98–99 %" vs 96.7 % for Food.com |
| B7 | MINOR | EVD (orchestrator files) | 4 files | "355 SVAR" still quoted |
