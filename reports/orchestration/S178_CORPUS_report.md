# S178 CORPUS lane report: corpus grounding (W2)

Status: AI_DRAFTED / PROPOSED (D-071 labels apply; nothing here is a human signature or approval). Round S178, 2026-11-09, host manjot-server, tree `~/kush_work/culinarystate/.orch (worktree max/s176-orchestration)`, HEAD `e358307` with uncommitted changes from other lanes. Python `.venv312`; every run `nice -n 10`; at most 20 workers; load average 30 to 120 on 128 cores. Counts only; no third-party text in any committed file (derived name lists are in git-ignored `data/derived/s178_corpus/`).

## 1. Item status (board rows, lane_group corpus-grounding)

| item_id | status | evidence | what is left |
|---|---|---|---|
| T3-C03-R1 | DONE | `reports/s178/corpus/ing_count_reconciliation_v1.{json,md}` | board note: nothing; a human may want the stale reports edited (section 3, item 1) |
| T3-C03-R2 | DONE (unchanged, ANALYSIS lane d7cb55f) | `reports/s178/analysis/ing_alias_coverage_census_v1.*` | the queue below reproduces its numbers exactly |
| T3-C03-R3 | PARTIAL (agent part DONE) | `reports/s178/corpus/ing_review_queue_summary_v1.json`; queues in git-ignored `data/derived/s178_corpus/ing_review_queue_<FAMILY>_v1.csv` | human verified/rejected labels with reviewer ids (reviewer columns are empty); the 8 h human estimate is unchanged |
| T3-C05-R1 | DONE | `reports/s178/corpus/verb_coverage_census_v1.{json,md}`, `verb_unmapped_top200_<FAMILY>.csv` | no POS tagger on the server (rule-based slot definition); BBC not on the server; Law-6 sign-off for the single-word lists (section 3, item 6) |
| T3-C07-R1 | DONE as OPT-IN (default behaviour unchanged by design) | `src/culinarystate/quantity/prenormalize.py`, `tests/unit/test_s178_corpus_prenorm.py` (70 tests), `reports/s178/corpus/sp002_prenorm_rerun_v1.{json,md}` | the board's 'in grammar.py / parse_quantity_v2 for all callers' is NOT done (D-070: `grammar.py` untouched; the lane brief: opt-in only); wiring into `extraction/quantity_stages.py` and `rc2_dryrun` is a 2-line change left to a human decision (section 3, item 2); BBC re-run belongs to the Mac |
| T3-C07-R4 | DONE | `reports/s178/corpus/foodcom_bare_count_v1.{json,md}` | none |
| T3-C09-R1 | PARTIAL (proxy only); NER-vs-Rung A stays BLOCKED_DATA | `reports/s178/corpus/span_agreement_tasteset_v1.json` (Rung A lexicon vs human TASTEset FOOD spans, DIAGNOSTIC) | the DeBERTa-CRF span files for Food.com / Wikibooks (vinayak) or the Mac copy; Gutenberg spans were never persisted |
| T3-C09-R4 | BLOCKED_HUMAN (unchanged) | none | 200-300 hand-labelled Food.com lines (Kush + Parv, blind) |
| T3-C12-R1 | DONE | `reports/s178/corpus/replay_invariants_corpus_v1.{json,md}`, `tools/s178_corpus_replay_invariants.py`, `tests/unit/test_s178_corpus_replay.py` | the split-sum invariant is vacuous on real graphs (section 2.8); BBC on the Mac |
| T3-C23-R1 | DONE | `reports/s178/corpus/foodcom_data_card_v1.{md,json}` (8 numbered sentences, each with its source path, generated from the committed reports) | the licence sentence repeats the uploader's declaration; human licence review (H2) stays open |
| T3-C24-R1 | NOT STARTED (POST, CAPACITY) | none | Q/V conformance fixture (8-14 agent-h) has no consumer in the 25 Nov deliverables; its dependency T3-C07-R1 now exists |
| (extra) Food.com quantity/part misalignment | DONE: diagnostic + proposed rule, no behaviour change | `reports/s178/corpus/foodcom_quantity_alignment_v1.{json,md}`, `src/culinarystate/quantity/foodcom_pairing.py`, `tests/unit/test_s178_corpus_pairing.py` | adopt the rule in `recipes/corpus.py` (not my file) or consume `pair_lines`; human spot-check of aligned pairs |

## 2. Results

### 2.1 T3-C03-R1: the ING counts reconcile exactly

`ING.jsonl` has **5,387 lines = 2,110 ids** (2,048 ACTIVE, 49 SUPERSEDED, 13 DEPRECATED) + 3,277 later versions of the same ids. Of the 2,048 ACTIVE concepts, **1,951 were first written by the A1 (BBC) registry build and 97 by the Wikibooks link import**; no Food.com or Gutenberg ING id exists. So: 1,951 (`reports/ingredient_registry_v1.md` L4, `reports/fdc_crosswalk_v0.md` L3) = the BBC-built ACTIVE concepts, **stale** as a statement about the current vocabulary; 5,387 (review packet Q7, `reports/master_plan/master_plan_research_audit_v2.md` L639) = `wc -l ledgers/data/ING.jsonl`, i.e. ledger VERSION LINES called 'rows'; 2,110 / 2,048 = ids / ACTIVE ids (S176 L-LOT). The consensus guess 'suspected Food.com-extended ING' is not supported: the file that produced 5,387 is `ledgers/data/ING.jsonl` itself. Vocabulary status: FoodOn LINKED 553 (27.0 %), USDA FDC LINKED 0 (all UNRESOLVED_EXTERNAL; packet Q7's '0 % crosswalked' is the USDA/FDC figure), parents on 315, facets on 235, scientific identity UNKNOWN for all, verification UNVERIFIED for all. All 21 ledgers are counted in the JSON; EVD/COND/SRC/MEAS/SNAP were read only and their sha256 are unchanged (EVD `5b3b1939...`).

### 2.2 T3-C07-R1: SP-002 pre-normaliser (opt-in) and the before/after counts

`culinarystate.quantity.prenormalize` (version `CQPO_SP002_PRENORM_V1_DRAFT`): rule SP002_U2044 (U+2044, U+2215, U+FF0F between digits, blanks allowed, becomes `/`), rule SP002_GLUED_REFUSE (>= 2 digits glued to the left of such a slash, e.g. `11⁄2`, is REFUSED: UNKNOWN AST, flag `AMBIGUOUS_GLUED_FRACTION`, never a guess; an ASCII `11/2` is untouched), rule SP002_HYPHEN_MIXED (D-072: `N-a/b` with N >= 1 and a/b < 1 is a mixed number, not an inverted range). Entry points: `prenormalise`, `parse_line_prenorm`, `parse_quantity_v2_prenorm`, `ground_quantity_rc2_prenorm` (swaps `rc2_grounding.parse_quantity_v2` for the duration of one call, process-local, not thread-safe). Raw text stays in every `raw` field; `rule_version` becomes `<adapter>+<prenorm>` only when a rule fired. `grammar.py`, `normalize.py`, `parse_adapter.py`, `rc2_grounding.py` are untouched (tests assert the legacy defect is still there).

Tests: 70 in `test_s178_corpus_prenorm.py`, including the byte-identity property (28 fixed + 400 seeded random lines without a trigger: `repr` of `parse_quantity_v2_prenorm` equals `parse_quantity_v2`, and the rc2 grounding record equals `ground_quantity_rc2`), glued REFUSE, ASCII twin equality for 300 random U+2044 lines, idempotence, rule independence, and the swap being undone on error.

| family | lines | touched by a rule | % | normalised amount changes | rc2 mass lines (Q0) before -> after | refused (glued) |
|---|---:|---:|---:|---:|---|---:|
| FOODCOM | 4,129,433 | 1,275,154 | 30.88 | 1,275,123 | 87 -> 127 | 0 |
| WIKIBOOKS | 32,036 | 0 | 0.0 | 0 | 3,020 -> 3,020 | 0 |
| TASTESET | 3,788 | 443 | 11.695 | 414 | 410 -> 465 | 0 |

Rules by family: FOODCOM {'SP002_HYPHEN_MIXED': 1, 'SP002_U2044': 1275153}, TASTESET {'SP002_HYPHEN_MIXED': 2, 'SP002_U2044': 441}, WIKIBOOKS none. GUTENBERG has no ingredient lines; BBC (188 U+2044 lines per S168) is not on this server. Food.com: **1,275,154 of 4,129,433 lines (30.88 %)** are touched; before, the frozen path read `1⁄2` as a count of 1 (value class transitions: exactly 1 -> below 1: 911,130; exactly 1 -> fractional above 1: 172,208; integer above 1 -> below 1: 119,827). Food.com has no units, so mass moves only 87 -> 127 lines; unsupported/UNKNOWN grows (ast_root UNKNOWN 193,715 -> 196,322; `UNSUPPORTED_COMPOUND_AMOUNT` 2,155 -> 3,280) and the frozen pipeline's own `NORMALIZATION_FLOAT_PRECISION_LIMIT` flag appears on 101,860 lines (thirds). TASTEset: 441 U+2044 lines + 2 hyphen lines; rc2 Q0 mass 410 -> 465 (+55), `unit_resolution` COUNT 1,264 -> 858. Wikibooks: 0 lines (its fractions are vulgar-fraction characters the frozen parser already handles). All 1,483,559 Food.com quantity strings with U+2044 are changed by the first rule and none has a slash outside digits. The glued REFUSE rule fires on 0 non-BBC lines (checked on all 4,583,725 Food.com quantity strings: 0 glued shapes), so it is covered by tests only. Verification: the BEFORE marginals equal the committed S161 counts (`reports/step16/rc2_grounding_dryrun_counts.json`) in all three families, 0 differences; unaffected unique lines re-run through the opt-in path were identical: FOODCOM 18,723/18,723, WIKIBOOKS 18,986/18,986, TASTESET 2,739/2,739.

Scope notes: (a) in Food.com step text only 131 of 3,468,491 step strings contain U+2044, so Rung A's in-step quantities are practically unaffected by that rule; 6,393 step strings carry an `N-a/b` shape that the hyphen rule rewrites (D-072), but Rung A only benefits once `quantity_stages.parse_quantity` calls the opt-in function. (b) The other two D-072 items ('a leading unicode fraction must not be cut from the span', 'decimals are never split') live in Rung A's span regex `extraction/rung_a.py:58` (`_NUM`), not in the quantity parser; not changed.

### 2.3 T3-C07-R4: Food.com bare counts, and the unit drop is source-level

4,882,431 quantity strings (298,706 null): **0 contain a letter**, every non-null string is an integer, decimal, fraction, mixed number or range; 1,483,559 contain U+2044. On the 4,129,433 corpus lines, 3,937,952 (95.363 %) start with a bare number; **3,929,823 lines (95.166 %) are bare counts with no unit anywhere**; the parser recognises a unit on 0.198 % of lines (from the food name), 4.244 % of name strings hold a unit word, and the S174 NER's UNIT spans (171,812) equal the number of names with a unit word (175,237) to within 2 % (ratio 0.9805); its QUANTITY spans (3,937,650) equal the lines starting with a digit to within 302 lines. NEG-0036's 4.4 % UNIT/QUANTITY ratio is therefore the share of food names that contain a unit word, not a parser or NER failure.

### 2.4 Food.com quantity/part misalignment: diagnostic and proposed rule

407,536 of 522,517 recipes (**77.995 %**) have lists of different length (385,756 quantities longer, 21,780 shorter), covering 76.823 % of part lines; the quantity lists hold 752,998 more entries than the parts lists (1.441 per recipe). A recipe with one part is equal-length in only 13 of 8,672 cases. Hypothesis (not established; the lists carry no line index): the quantity list has one entry per source line, the parts list only the lines where a food part was extracted. Positional pairing drops 779,502 quantity strings beyond the parts list and pairs the rest by index. **Proposed default `EQUAL_LENGTH_ONLY`** (`foodcom_pairing.pair_equal_length` / `pair_lines`): pair only equal-length recipes (114,981 recipes, 957,071 lines = 23.177 %), give every other part no quantity (UNKNOWN). Equal length is necessary, not sufficient. Experimental `ALIGN_MODEL` (monotone alignment scored by P(quantity bucket | food name) trained on equal-length recipes, kept at forward-backward posterior >= 0.9): in simulation on held-out equal-length recipes with k dropped parts, positional pairing is right for 50.018 % (k=1) and 33.878 % (k=2) of parts, the gated alignment pairs 44.879 % / 22.914 % of parts with precision 91.786 % / 89.554 %. That is simulation only, on a corruption the method assumes; the real mechanism is unknown and no ground truth exists, so the alignment is NOT recommended without a human spot-check of its pairs.

### 2.5 T3-C05-R1: Rung A verb coverage (non-BBC)

| family | texts | ACTION events | verb-slot candidates mapped | sentence-initial candidates mapped | ambiguous events | distinct unmapped lemmas (>= 20) |
|---|---:|---:|---:|---:|---:|---:|
| FOODCOM | 522,514 | 8,728,967 | 78.816 % | 87.355 % | 0.904 % | 2,775 |
| WIKIBOOKS | 3,676 | 62,527 | 76.271 % | 86.918 % | 0.414 % | 123 |
| GUTENBERG_SEGMENT | 73,778 | 952,392 | 62.04 % | 68.718 % | 0.184 % | 2,018 |

100 % of ACTION events map to PROC by construction (the label exists only after a PROC match; 0.02 % via the lemma guess); the informative number is how many verb-slot words are NOT mapped. No POS tagger exists on the server, so a candidate is a word in a verb slot (sentence start or after a comma, then, and, or, to, until...) that is not closed-class, food or tool. The unmapped lists (top 200 per family, with slot share and sentence-initial counts to separate verbs from adjectives and nouns) are in `verb_unmapped_top200_<FAMILY>.csv`; the first entries in Food.com are generic verbs (let, bring, make, use, allow, enjoy, continue, prepare, leave, repeat), which the process registry deliberately leaves out, plus adjectives (golden, tender, soft). Gutenberg is the weakest (62 % of slot words), as expected for 19th-century prose.

### 2.6 T3-C03-R3 (agent part): review queue

- FOODCOM: 6,086 non-exact phrases holding 735,268 mentions (17.806 % of all mentions); the top 633 phrases hold 80 % of the non-exact mentions (band A), 1,723 hold 95 %; 5,452 PARTIAL (a lexicon food is inside; the queue row carries its candidate ING id), 634 MISS.
- TASTESET: 1,165 non-exact phrases holding 1,569 mentions (41.519 % of all mentions); the top 852 phrases hold 80 % of the non-exact mentions (band A), 1,087 hold 95 %; 1,054 PARTIAL (a lexicon food is inside; the queue row carries its candidate ING id), 111 MISS.
- WIKIBOOKS: 7,017 non-exact phrases holding 11,599 mentions (36.285 % of all mentions); the top 4,698 phrases hold 80 % of the non-exact mentions (band A), 6,438 hold 95 %; 6,372 PARTIAL (a lexicon food is inside; the queue row carries its candidate ING id), 645 MISS.

Each row has rank, phrase, count, class, candidate ING ids (AI suggestion from the registry, not a decision), cumulative share, band A/B/C (C = default `LOW_CONFIDENCE_UNREVIEWED`) and empty `reviewer_id` / `verdict` / `note`. The numbers equal the ANALYSIS lane's census (6,086 / 633 for Food.com). Note the earlier row text 'top ~300 covering ~80 %' is for all mentions; for the non-exact queue it is 633.

### 2.7 T3-C09-R1 (partial): Rung A lexicon vs human TASTEset FOOD spans (DIAGNOSTIC, not gold, not NER)

4,020 gold FOOD spans: 94.776 % overlapped by a lexicon span, 68.408 % with the exact boundary, 5.224 % missed; of 4,339 lexicon spans 92.602 % overlap a gold FOOD span, 5.301 % overlap no gold span. No lexicon blocking or ACTION precedence; TASTEset also trained the NER, so this is not an NER measure. The top missed foods are in git-ignored `data/derived/s178_corpus/span_agreement_missed_gold_foods_TASTESET.csv`. The real item (NER spans vs Rung A on Food.com and Wikibooks) is still BLOCKED_DATA: the span files are on vinayak and Gutenberg spans were never persisted (a search of this server found only `features/v2dm/{tasteset,recipedb3}_spans.jsonl`).

### 2.8 T3-C12-R1: replay invariants at corpus scale

Pipeline per instruction text: Rung A -> `adapt_event_graph` -> engine `replay_events` (rejects any event that violates an invariant), plus an independent re-implementation of seven invariants (`independent_check`), compared event by event (conditioned on the engine's apply/reject decisions), plus planted violations on a 1-in-20 sample and a replay-twice determinism check on 1 in 50.

| family | texts | with events | engine events | replay PASS | UNKNOWN | FAIL | untraced issues | engine-vs-independent disagreements | determinism |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| FOODCOM | 522,517 | 522,390 | 12,543,466 | 455,613 | 55,180 | 11,721 | 0 | 0 | 10416/10416 identical |
| WIKIBOOKS | 3,676 | 3,674 | 90,224 | 3,123 | 455 | 98 | 0 | 0 | 80/80 identical |
| GUTENBERG_SEGMENT | 73,778 | 73,777 | 1,563,210 | 66,392 | 6,431 | 955 | 0 | 0 | 1550/1550 identical |

Violating events per invariant (engine / independent):

| invariant | FOODCOM | WIKIBOOKS | GUTENBERG_SEGMENT |
|---|---:|---:|---:|
| ORDER_REGRESSION | 0 / 0 | 0 / 0 | 0 / 0 |
| ENTITY_UNKNOWN | 79,206 / 79,206 | 779 / 779 | 4,957 / 4,957 |
| ENTITY_ALREADY_CONSUMED | 0 / 0 | 0 / 0 | 0 / 0 |
| ENTITY_REUSED_AFTER_DISCARD | 0 / 0 | 0 / 0 | 0 / 0 |
| ENTITY_ID_REUSED | 0 / 0 | 0 / 0 | 0 / 0 |
| EVENT_ID_REUSED | 0 / 0 | 0 / 0 | 0 / 0 |
| SPLIT_FRACTIONS_EXCEED_ONE | 0 / 0 | 0 / 0 | 0 / 0 |

Every engine issue is traced: FOODCOM {'DEPENDENCY_NOT_APPLIED__CASCADE_DEPENDENCY_REJECTED': 67627, 'ENTITY_UNKNOWN__ADAPTER_ENTITY_WITHOUT_PRODUCER': 11864, 'ENTITY_UNKNOWN__CASCADE_PRODUCER_REJECTED': 68278}; WIKIBOOKS {'DEPENDENCY_NOT_APPLIED__CASCADE_DEPENDENCY_REJECTED': 683, 'ENTITY_UNKNOWN__ADAPTER_ENTITY_WITHOUT_PRODUCER': 99, 'ENTITY_UNKNOWN__CASCADE_PRODUCER_REJECTED': 686}; GUTENBERG_SEGMENT {'DEPENDENCY_NOT_APPLIED__CASCADE_DEPENDENCY_REJECTED': 4088, 'ENTITY_UNKNOWN__ADAPTER_ENTITY_WITHOUT_PRODUCER': 956, 'ENTITY_UNKNOWN__CASCADE_PRODUCER_REJECTED': 4211}. Root cause of every replay FAIL: Rung A opens a MIXTURE entity for a mixture word with no live antecedent and no producing event (documented in `extraction/rung_a_binding.py:21`, created at `:244`, flagged `INTERMEDIATE_NEW_ENTITY`); the adapter reports `ENTITY_WITHOUT_PRODUCER` (`state_graph/event_adapter.py`, `events()`: non-lot entity with no producer) and the engine rejects the one event that consumes it (ENTITY_UNKNOWN) and, as designed, every later event that depends on it (cascade). At scale the adapter's `ENTITY_WITHOUT_PRODUCER` counts (FOODCOM 11,874, WIKIBOOKS 99, GUTENBERG_SEGMENT 956) equal exactly the `INTERMEDIATE_NEW_ENTITY` diagnostic of the committed S163 full-corpus Rung A counts (`reports/step17/rung_a_dryrun_counts_full_corpus_final.json`: 11,874 / 99 / 956), and a probe on 600 Wikibooks recipes found all 14 such entities to be MIXTURE entities consumed once. Order regression, double consumption, resurrection of a DISCARDED lot (Rung A opens a new lot after a discard), entity-id reuse and event-id reuse never occur in any family.

Power (planted violations on the sampled texts; detected by the engine / by the independent checker):

| mutation | FOODCOM | WIKIBOOKS | GUTENBERG_SEGMENT |
|---|---:|---:|---:|
| M_DOUBLE_CONSUME | 25133/25133 of 25133 | 173/173 of 173 | 3548/3548 of 3548 |
| M_ORDER_SWAP | 26120/26120 of 26120 | 180/180 of 180 | 3645/3645 of 3645 |
| M_RESURRECT_DISCARDED | 896/896 of 896 | 2/2 of 2 | 4/4 of 4 |
| M_SPLIT_OVER_ONE | 365/365 of 365 | 2/2 of 2 | 23/23 of 23 |

The split-sum invariant has nothing to check on real graphs: FOODCOM 79,220 partition groups, 79,220 with basis UNSPECIFIED, 0 with a basis and a known fraction; WIKIBOOKS 645 partition groups, 645 with basis UNSPECIFIED, 0 with a basis and a known fraction; GUTENBERG_SEGMENT 8,952 partition groups, 8,952 with basis UNSPECIFIED, 0 with a basis and a known fraction. Rung A states a fraction only for 'half' and never a basis, so the property is verified only through the planted violations. A zero count says the rule-based extraction respects the replay's structural invariants; it does not say the events are right (`NOT_CHECKED` in the replay lists span round-trip, lot-accounting completeness, merge/transform quantities, observation override).

### 2.9 T3-C23-R1: Food.com data card

`reports/s178/corpus/foodcom_data_card_v1.md` holds eight sentences (LICENCE, SHAPE, NO_UNITS, GRAMS, MISALIGNMENT, SP002, NAMES, STEPS), each with the path of the committed report it was computed from, and five rules for using Food.com in a T3 report. The generator reads the committed JSONs, so the card cannot drift from them (a test compares them).

## 3. Bugs, hazards and decisions (nothing outside my paths was changed)

1. **Stale ING numbers.** `reports/ingredient_registry_v1.md` L4 and `reports/fdc_crosswalk_v0.md` L3 say 1,951 ING concepts; the ledger now has 2,048 ACTIVE. The packet's '5,387 ING rows' means ledger lines. Suggest a one-line caveat in both reports and 'ING concepts: 2,048 ACTIVE (5,387 ledger lines)' in the final report.
2. **SP-002 is fixed only opt-in.** To make it the default for Rung A and the rc2 dry-run: `extraction/quantity_stages.py:73` `parse_quantity_v2(...)` -> `parse_quantity_v2_prenorm(...)` and `:88` `ground_quantity_rc2(...)` -> `ground_quantity_rc2_prenorm(...)`, and the same swap in `quantity/rc2_dryrun.py` `_count_recipe`; bump the report versions; re-run S161 beside the old numbers. Legacy callers (`rule_ner`, `line_link`, `rule_compiler`, gold `_base_from_text`, `recipe_quantity_mentions_v1.parquet`, KGE) keep the defect, as D-070 says. The Mac fix in `composition/line_census.py` (ticket A4) is independent.
3. **`recipes/corpus.py:98` `iter_foodcom`** pairs quantity and part by index (78.0 % of recipes unequal). Not my file; use `foodcom_pairing.pair_lines(q, p, 'EQUAL_LENGTH_ONLY')` or apply the same rule there. Anything that already consumed `ingredient_lines` for Food.com (S161 rc2 dry-run, Rung A inputs, the S175/S177 line and lot censuses) carries the mispairing.
4. **`extraction/rung_a.py:58` `_NUM`** is ASCII-only and splits decimals at the point (D-072 items 2 and 3); not changed.
5. **Tests that cannot run on this venv (pre-existing, not touched):** `hypothesis` and `lxml` are not installed (`test_step16_rc2_grounding`, `test_step17a_auditor`, `test_step18_event_log`, `test_step18_replay`, `tests/property/test_fuzz_entry_points`), and `test_step16b_text_strata` needs `registry/recipe_semantics/deep_gold_sampling_frame_v1_DRAFT.csv` (absent). The other 690 tests of the quantity/step16/17/18/property families pass with my files present.
6. **Law 6.** (a) The top-200 verb lists are single English words with counts (min 20), like the committed `registry/processes/unmapped_verbs.csv`; they are committed under `reports/s178/corpus/`: reviewer to confirm. (b) The ingredient review queues and the span-agreement lists hold short ingredient phrases, so they are in git-ignored `data/derived/s178_corpus/` (a path outside my four ownership patterns, the same Law-6 location the ANALYSIS lane used); move or delete as you see fit.
7. **Not done and why.** T3-C09-R1 real item (no NER span files here), T3-C09-R4 (human), T3-C24-R1 (POST, CAPACITY). BBC rows of every table (not on this server, D-003). I did not run the verb census on a 1,000-recipe Food.com sample before the full run (a 300-text Wikibooks smoke run and the unit tests preceded it); every other tool had a sample or smoke run first.

## 4. Decisions for the orchestrator / humans

1. Adopt `EQUAL_LENGTH_ONLY` for Food.com pairing (and where: `corpus.py` or the consumers)? ALIGN_MODEL only with a human spot-check.
2. Switch the rc2 path (quantity_stages, rc2_dryrun) to the SP-002 pre-normaliser and re-run S161 beside the old numbers (the Food.com numbers above are the expected size of the change)?
3. Should the adapter give an unproduced MIXTURE a lot-introduction event (or Rung A a producer) so a mixture word with no antecedent does not reject its consumer? Today 1.3 % (Gutenberg), 2.2 % (Food.com) and 2.7 % (Wikibooks) of texts replay as FAIL for this single reason; the invariants themselves are fine.
4. Law-6 sign-off for the committed top-200 verb lists; location of the git-ignored queues.
5. T3-C03-R3 human review: who reviews the 633 band-A Food.com phrases (and the 852 TASTEset / 4,698 Wikibooks band-A rows if those are wanted).

## 5. Tests run

`tests/unit/test_s178_corpus_{prenorm,pairing,tools,replay}.py`: **160 passed** in 3.0 s (70 + 40 + 29 + 21). Regression: `tests/unit/test_quantity*.py test_step16*.py test_step17*.py test_step18*.py tests/property`: 690 passed, 1 skipped, 10 collection/fixture errors that pre-date this lane (item 5 above); `tests/unit/test_s178_analysis_*.py` unaffected (no file of theirs was edited).

## 6. compute_runs rows (proposed; the orchestrator owns `registry/compute_runs_v1.csv`)

All: host manjot-server, tree `~/kush_work/culinarystate/.orch (worktree max/s176-orchestration)`, git_commit `e358307+uncommitted`, `nice -n 10`, `.venv312`, workers as stated, load average 30 to 120 on 128 cores.

```csv
run_id,host,tree,git_commit,families,workers,command,output_path,output_sha256,start,end,status,notes
RUN-S178-CORP-001,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),e358307+uncommitted,FOODCOM WIKIBOOKS TASTESET,16,tools/s178_corpus_prenorm_rerun.py --workers 16 --verify-unaffected 20000,reports/s178/corpus/sp002_prenorm_rerun_v1.json,168856a7226932c07f326fb1efd51bc876e85a82d0234826b5b2d8b288a05345,2026-11-09T10:31:15Z,2026-11-09T10:35:24Z,DONE,"T3-C07-R1; rc2 grounding before/after the opt-in SP-002 pre-normaliser; BEFORE equals committed S161 counts (0 differences); FOODCOM 1,275,154 of 4,129,433 lines touched; unaffected lines identical; a 1,000-recipe sample run (2026-11-09T10:18:11Z, scratch) preceded it; md sha256 f64299c35b9788d8"
RUN-S178-CORP-002,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),e358307+uncommitted,FOODCOM GUTENBERG_SEGMENT WIKIBOOKS,16,tools/s178_corpus_verb_census.py --workers 16 --batch 500,reports/s178/corpus/verb_coverage_census_v1.json,fe1735c35ab8168b5ec1a507c1173f30fe1a9f213c367830a736cf3db712e317,2026-11-09T10:36:19Z,2026-11-09T10:38:31Z,DONE,"T3-C05-R1; 8,728,967 Food.com ACTION events; csv sha256 FOODCOM 57a674c0cee48a79, GUTENBERG 3a887bf613b81bf8, WIKIBOOKS 54ed92e133d2d87c; md 2deb338a8c4a5e87"
RUN-S178-CORP-003,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),e358307+uncommitted,FOODCOM,1,tools/s178_corpus_foodcom_quantity.py,reports/s178/corpus/foodcom_bare_count_v1.json,56dcfa76678c6ace5322cf050bfc5075ab4111006109aec017caa73060ff1baa,2026-11-09T10:40:18Z,2026-11-09T10:41:02Z,DONE,"T3-C07-R4; 0 letters in 4,583,725 quantity strings; an earlier run 2026-11-09T10:36:19Z-10:37:49Z before the bare-count additions is superseded; md b015ed2205ce4128"
RUN-S178-CORP-004,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),e358307+uncommitted,FOODCOM,1,tools/s178_corpus_foodcom_alignment.py --eval-recipes 4000,reports/s178/corpus/foodcom_quantity_alignment_v1.json,f1989b4affa641050ef5489811783671c66593468c42c92d67c6ac77ed0557d4,2026-11-09T10:44:47Z,2026-11-09T10:46:37Z,DONE,"Food.com quantity/part misalignment diagnostic + rules; 407,536 of 522,517 recipes unequal; earlier run 10:37:49Z-10:39:27Z superseded by a wording fix (same numbers); md c2454989cb95a14f"
RUN-S178-CORP-005,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),e358307+uncommitted,FOODCOM WIKIBOOKS TASTESET,1,tools/s178_corpus_ing_review_queue.py,reports/s178/corpus/ing_review_queue_summary_v1.json,61caabb669bd42992d582f8072724558fcf13caf3025ac39d9b17c6464259095,2026-11-09T10:47:43Z,2026-11-09T10:48:21Z,DONE,"T3-C03-R3 agent part; queues in git-ignored data/derived/s178_corpus (sha256 FOODCOM 24b6c4626284bf1c, WIKIBOOKS 0033054252ec78f7, TASTESET 4e05aa91348d6c11)"
RUN-S178-CORP-006,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),e358307+uncommitted,TASTESET,1,tools/s178_corpus_span_agreement.py,reports/s178/corpus/span_agreement_tasteset_v1.json,8602a10de0fe90853ba0dba4975828412a78e42f1767bcf80fbc04f70d196794,2026-11-09T10:52:46Z,2026-11-09T10:52:47Z,DONE,T3-C09-R1 proxy (Rung A lexicon vs human TASTEset FOOD spans); DIAGNOSTIC_NOT_GOLD; lists in git-ignored data/derived/s178_corpus
RUN-S178-CORP-007,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),e358307+uncommitted,FOODCOM GUTENBERG_SEGMENT WIKIBOOKS,20,tools/s178_corpus_replay_invariants.py --workers 20 --batch 200,reports/s178/corpus/replay_invariants_corpus_v1.json,b7fe719c349207f2b641b6fe8f71aa17ef41e0f81859e8365c0c69ae66fd5ae4,2026-11-09T10:42:30Z,2026-11-09T10:56:20Z,DONE,"T3-C12-R1; 14,196,900 engine events; unexplained 0; Food.com 1,000-recipe sample (2026-11-09T10:39:59Z-10:40:42Z) and a Wikibooks/Gutenberg 400-recipe smoke run preceded it; a first full start at 10:41Z was killed by me within a minute to change the tool (no output); md fe412b96d18eab7a"
RUN-S178-CORP-008,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),e358307+uncommitted,—,1,tools/s178_corpus_ing_reconcile.py,reports/s178/corpus/ing_count_reconciliation_v1.json,7ddbc10a9536187d9e3d45f675a5a48dc00066a394658f60a157c15ab3142714,2026-11-09T10:52:04Z,2026-11-09T10:52:14Z,DONE,T3-C03-R1; 23 ledgers read-only; EVD/COND/SRC/MEAS/SNAP sha256 identical before and after; an earlier run 10:09:05Z-10:10:13Z is superseded by a wording fix; md 08893d2ecd6c3c8e
RUN-S178-CORP-009,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),e358307+uncommitted,—,1,tools/s178_corpus_foodcom_card.py,reports/s178/corpus/foodcom_data_card_v1.json,05ea42c4e2b5d44ac0276b1b7b3fa8834bfaa7f0a10a5d1a2aa86ab990b0cad9,,,DONE,T3-C23-R1; reads the committed JSONs; md e9590a950a008d3f; start/end not recorded (under 1 s)
RUN-S178-CORP-010,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),e358307+uncommitted,—,1,python -m pytest -q tests/unit/test_s178_corpus_prenorm.py tests/unit/test_s178_corpus_pairing.py tests/unit/test_s178_corpus_tools.py tests/unit/test_s178_corpus_replay.py,,,2026-11-09T10:57:18Z,2026-11-09T10:57:21Z,DONE,"160 passed in 3.0 s (prenorm 70, pairing 40, tools 29, replay 21); tests/unit/test_s178_analysis_*.py 26 passed"
```

Tool and module sha256 (first 16 hex): foodcom_pairing.py `8e6a739de5664c2c`, prenormalize.py `58721873c127b2a2`, s178_corpus_foodcom_alignment.py `cbcc1dc017b7eaf8`, s178_corpus_foodcom_card.py `cf5e84e507c71190`, s178_corpus_foodcom_quantity.py `3bc61d0c7469accc`, s178_corpus_ing_reconcile.py `3a2d7efa2f634f4f`, s178_corpus_ing_review_queue.py `ee1095d0aa36166c`, s178_corpus_prenorm_rerun.py `9a111fda178e70a3`, s178_corpus_replay_invariants.py `9fc8dda1ff41ae66`, s178_corpus_span_agreement.py `ffcedfb06d0a3501`, s178_corpus_verb_census.py `5406a7213d763232`.

## 7. Files

- `src/culinarystate/quantity/{prenormalize,foodcom_pairing}.py` (new, opt-in; no existing file changed)
- `tools/s178_corpus_{ing_reconcile,prenorm_rerun,verb_census,foodcom_quantity,foodcom_alignment,foodcom_card,ing_review_queue,span_agreement,replay_invariants}.py`
- `tests/unit/test_s178_corpus_{prenorm,pairing,tools,replay}.py`
- `reports/s178/corpus/`: `ing_count_reconciliation_v1`, `sp002_prenorm_rerun_v1`, `verb_coverage_census_v1` (+ `verb_unmapped_top200_{FOODCOM,GUTENBERG_SEGMENT,WIKIBOOKS}.csv`), `foodcom_bare_count_v1`, `foodcom_quantity_alignment_v1`, `foodcom_data_card_v1`, `ing_review_queue_summary_v1.json`, `span_agreement_tasteset_v1.json`, `replay_invariants_corpus_v1`
- `data/derived/s178_corpus/` (git-ignored, about 1.2 MB): review queues, span-agreement lists


## S178 correction (FIX-EVAL), 2026-11-09 (re-run completed S179)

AI_DRAFTED (D-071). Appended after the SCI-B review findings CORP-4, CORP-5 and CORP-6; the sections above are kept as
written. Run rows RUN-S179-CORP-001 (1,000 smoke) and RUN-S179-CORP-002 (full families); the S178 full re-run was
killed and is logged ABORTED.

- **CORP-4, independence.** `tools/s178_corpus_replay_invariants.py` 0.2.0 re-derives the seven invariants, every other
  structural rejection rule and its own apply / reject vector; only MASS_BALANCE_FAIL positions come from the engine
  (0 such events in the run). Result on the full families: 0 apply-decision and 0 issue-code-set disagreements
  (engine-rejected = independently rejected: Food.com 79,206, Gutenberg 4,957, Wikibooks 779). Planted mutations at a
  hash-drawn position (order swap, double consume, resurrect after discard, split over one) are detected 100 % by both
  checkers, at the planted position, mostly in interior events (Food.com order swap 24,171 interior of 26,120).
- **CORP-5, by-construction invariants.** ORDER_REGRESSION and EVENT_ID_REUSED cannot be produced by Rung A and the
  adapter (`extraction/rung_a_binding.py:211-226`, `state_graph/event_adapter.py:180-213`). Their zeros in section 2.8
  are not validation; v2 marks them BY CONSTRUCTION. The planted order swap shows the check itself works.
- **CORP-6, determinism.** v2 checks determinism in the same worker and in a second pool with a different hash seed:
  Food.com 10,416 / 10,416, Gutenberg 1,550 / 1,550, Wikibooks 80 / 80 equal in both. The verb-census denominator and
  "exhaustive" wording are corrected in `verb_coverage_census_v2` (sample, not exhaustive).
- **Full-family v2 counts** (`reports/s178/corpus/replay_invariants_corpus_v2.{json,md}`): engine events incl. lot
  introductions Food.com 12,543,466, Gutenberg 1,563,210, Wikibooks 90,224; replay FAIL texts 11,721 / 955 / 98;
  unexplained 0 in every family. The split-sum invariant still has nothing checkable on real graphs (0 partition
  groups with a basis and a known fraction). v1 is kept as history and superseded by v2.
