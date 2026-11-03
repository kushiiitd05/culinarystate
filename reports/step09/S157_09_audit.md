# S157 Step 09 audit: pre-spine extraction and verification prototypes

**Status: PROVISIONAL_PENDING_09_GATE.** AI verdict by worker "ksh" (an agent, not Kush), written
under D-045. Kush and Parv review it afterwards, and their review is final. This audit does not
evaluate any G09 gate, freeze any evidence or approve any schema. All S157 outputs are synthetic-tested only.

Sources read: STEP 09 card (`docs/plan/CulinaryState_36_Step_Execution_Plan_v2.md`), spine row 09
(`registry/execution_spine_v2.csv`), D-027/D-029/D-031/D-032/D-034/D-035/D-045, the files listed below.
The protected ledgers were read only (17,978 latest-ACTIVE EVD rows: 14,108 UNVERIFIED, 3,870
AI_PRECHECKED, 0 HUMAN_VERIFIED, all tier E3).

## 1. What exists before S157

| Prototype | What it does | Tests | Distance from the card |
|---|---|---|---|
| `src/culinarystate/evidence/precheck.py` | Route A rule pre-check of one imported EVD row: before/after both MEASURED in one unit, RF inside the interval implied by 2-decimal rounding × yield (±5 %), stated T/t present in COND, matrix linked to ING. Returns a suggestion (LIKELY_CONFIRM / CHECK_VALUES / CHECK_CONDITIONS). Docstring: "Never human verification". | `test_precheck.py` | Row-level and EVD-specific. No locator, no span match, no field classes, no seeded-error suite. The ±5 % tolerance and the fixed 0.005 rounding are prototype choices. |
| `src/culinarystate/evidence/link_review.py` | Turns a filled ingredient-link review row into a decision. A decision needs a named human (`HUMANS` = Kush, Parv) and an ISO date. | `test_link_review.py` | Correct human-only rule, but only for ING links. There is no verification-queue record. |
| `tools/apply_human_review.py` | Applies `human_review_pack_v1.csv` decisions (CONFIRM / REJECT / CORRECT, verifier in HUMANS, YYYY-MM-DD date, paper locator) by writing new EVD rows (E1/E2, HUMAN_VERIFIED). | none found | Writes to `ledgers/data/EVD.jsonl`, which the 08a guard now forbids (byte-identical EVD). Nothing ties the decision to the reviewer's file: any process that can fill the CSV columns can run it. The pack has 55 rows; all `human_decision`/`verifier` cells are blank. |
| `tools/apply_link_review.py` | Has a `--sign-as Kush --date … --basis …` mode that fills EMPTY human_decision cells with the AI recommendation "on that human's explicit instruction". | none found | **Risk:** code fills a human field. It is legal under its own rule (explicit instruction), but it is a bulk-sign-off path. The S157 machinery has no equivalent entry point, and a test enforces that. |
| `tools/precheck_route_a.py` | Resolves Phenol-Explorer DOIs, rule-checks rows, writes SRC revisions and `EVD.verification = AI_PRECHECKED`, and builds the 55-row human pack. | none found | Mutates SRC/EVD (pre-08a). It cannot be re-run now without breaking the byte-identical baseline. The 3,870 AI_PRECHECKED EVD rows come from it. |
| `tools/build_verification_queue.py` | Builds `verification_queue_ranked_v1.csv` (634 rows; Route A PE papers + Route B OpenAlex candidates) with classes VERIFY_NOW / STRONG_CANDIDATE / NEEDS_SOURCE / CONFLICT / REJECT. | via `test_literature.py` (harvest/precheck helpers) | Paper-level triage and not a field-level queue. `human_status`/`verifier` are blank in all 634 rows. There is no locator, and no blind/AI-assisted mode or timing. |
| `src/culinarystate/evidence/literature.py`, `doi_resolve.py` | OpenAlex harvest, gap queries, Crossref DOI resolution with year ±1 and ≥ 85 % title-token match. Unresolved citations stay UNRESOLVED. | `test_literature.py`, `test_doi_resolve.py` | Discovery (Step 13), not extraction. Needs network access and H2 #1/#3/#4. Not reused by S157. |
| `src/culinarystate/evidence/linker.py` | PROC/ING linking with EXACT/HIGH/MEDIUM bands. `keep_linker_fields` carries verification across rebuilds. | `test_linker.py`, `test_evidence_linker_keep.py` | Linking, not extraction. Kept as is. |
| `src/culinarystate/evidence/conditions*.py`, `condition_normalizer.py` | Frozen Step 07 condition parsing. Only literally written numbers are extracted. | existing Step 07 tests | The card says to store `normalizer_fingerprint_12` with every parsed condition value. S157 stamps its own `normalizer` version on T/t normalisation and does not call the frozen normaliser (OPEN O-4). |
| `tools/make_evidence_queue.py`, `tools/infoods_transition_candidates.py` | Top-5 acquisition queue (candidates only), and an INFOODS/R2 transition-candidate classifier (COMPILED_REFERENCE, etc.). | none found | Planning artefacts. The R2 column names the 12-local parser reads are taken from `infoods_transition_candidates.py`. |
| `src/culinarystate/lineage/guard.py` | `verify_baseline`, `assert_safe_write_target` (ledgers/data, exports/evd). | lineage tests | Reused unchanged by every S157 writer. |
| `src/culinarystate/extraction/*` (S155) | Step 17 **recipe** extraction drafts (interfaces, V1–V4, invented-value auditor). | `test_step17a_*` | Different object (recipes, not documents). The card names `src/culinarystate/extraction/*` as the Step 09 output path, which **collides** with S155. S157 therefore puts the evidence machinery in `src/culinarystate/evidence/` (OPEN O-1). |

Missing entirely (card 09.1–09.7): XTR/ADJ/KIN/KINPT schemas (namespaces are reserved only, 04.9-min;
KIN/KINPT exist as `registry/schemas/*.draft_v1.schema.json` DRAFT_PENDING_H4),
`registry/extraction_field_class_registry_v1.csv`, `registry/prompt_registry_v1.csv`,
`tests/fixtures/extraction_golden/`, adjudication packets with per-row timing, the K-level classifier,
the Step 10/11 accuracy pre-registration, 08b detector integration, and every `reports/step09/*` gate file.

## 2. What S157 consolidated (PROVISIONAL_PENDING_09_GATE)

`src/culinarystate/evidence/machinery.py` is the single import surface. It re-exports
`evidence/extraction_fields.py`, which holds the field classes, locators, proposals and validators and
contains no review or status code. Tests: `tests/unit/test_step09_machinery.py`, 55 synthetic cases.

- **Field classes (09.2, in code):** the card's 15 classes. Critical marks are an AI proposal
  (`CRITICAL_STATUS = PROPOSED_PENDING_09_GATE`): numeric value, unit, basis, censoring, T, t, matrix,
  process, kinetic parameter.
- **Locators:** SPAN (char range), TABLE_CELL (table/row/column), FIGURE (figure id, plus a digitisation
  tool/version or a flag).
- **Proposals:** an extractor (AI_MODEL, RULE or HUMAN_EXTRACTOR, the last only Kush/Parv) proposes one
  raw string. A proposal cannot carry reviewer, verifier or status attributes.
- **Validators (09.3 shape, flag-only):**
  - value-in-span with token boundaries (catches every seeded fabricated value in the fixture set);
  - numeric / decimal-comma / zero-needs-TRUE_ZERO;
  - unit, basis and location against the registries;
  - n ≥ 1 integer; dispersion type and sign; censoring tokens;
  - temperature with unit, 0 K hard bound and the registry's plausibility bound;
  - time with unit, ≥ 0, month/year NOT_CONVERTED;
  - food:medium ratio; K0–K4; kinetic parameter AUTHOR_REPORTED (09.5);
  - retention and percent-change arithmetic under rounding intervals (precheck logic, generalised);
  - prompt-injection patterns.

  Raw strings are kept, and normalisation goes in a new column as exact decimals.
- **Queue record:** `QueueItem` (one field, ≥ 1 proposals, validator flags, `EXTRACTOR_DISAGREEMENT`).
  Span text is hashed and never stored. Schema:
  `registry/schemas/evidence_verification_queue_item.provisional_v1.schema.json`.
- **Human-only status:** `verification_status` has no setter and no constructor argument. It is derived
  in one function from a `HumanReview`:
  - the reviewer must be Kush or Parv; AI names and "ksh"/"prv" are refused;
  - the decision must be one of CONFIRM / REJECT / CORRECT / UNSURE;
  - `review_mode` is one of INDEPENDENT_BLIND / AI_ASSISTED / JOINT, with a `seen_model_output` flag;
  - the record carries minutes and the sha256 of the review file.

  Reviews enter only through `read_human_reviews` (a human-filled CSV). `write_queue_jsonl` re-reads
  that file and refuses a review missing from it or different from it. This blocks forged or upgraded
  reviews in code.
- **Proof that code cannot mark VERIFIED:** an AST test shows the literal `HUMAN_VERIFIED` appears only
  in the derivation function and the vocabulary. Further tests show:
  - no sign/approve/autofill entry point exists;
  - no combination of AI, rule and human-extractor proposals reaches a HUMAN_* status;
  - `from_dict` rejects a stored HUMAN_VERIFIED without a review;
  - the writer rejects reviews whose file is not given.
- **Tier:** never E4. `E4_ELIGIBLE_PENDING_ADJ` requires all of the following: a blind CONFIRM with a
  checked locator, ≥ 2 extractor families and no blocking flag. Otherwise the tier is E5. Promotion
  needs the 09.1 ADJ record, which does not exist yet.
- **Writers:** a new file only. They refuse `ledgers/`, `exports/`, `annotation/gold/` and ledger-like
  file names. The review sheet is blind by default (proposed values hidden).

## 3. Gaps against the card (still open after S157)

| Card item | State after S157 |
|---|---|
| 09.1 XTR/ADJ/KIN/KINPT schemas; finalised SEXP/SMP/OBS | Not done: needs the approved 04.3 (H4). The queue item is not XTR/ADJ. |
| 09.2 field-class registry CSV | In code only. Writing `registry/extraction_field_class_registry_v1.csv` waits for the critical-class ruling. |
| 09.3 golden fixtures `tests/fixtures/extraction_golden/` | Synthetic unit fixtures only. Kush authors the fixture set (card: 3–4 h). G09-1 not evaluated. |
| 09.4 adjudication packets with 07.A provenance controls | Review-sheet / queue mechanics and timing fields exist. The packet design and provenance precheck reuse are not done. |
| 09.5 kinetic capture subset | AUTHOR_REPORTED validator only. No KIN round-trip (G09-6). |
| 09.6 Step 10/11 accuracy pre-registration | Not done (THR rows need human signature). |
| 09.7 08b detector before extraction | Not wired (08b v1 not authorised, D-035). |
| G09-2 catch rate | 100 % on the seeded fabricated values in the unit tests. Not a gate measurement: no registered seeded-error suite exists. |
| G09-3 replay determinism | Builds are deterministic for given proposals. No cached-model replay exists, because no model is called. |
| G09-5 no E5→E4 without human ADJ | Satisfied by construction for this module (unit-tested). The ADJ record itself is missing. |

## 4. OPEN for Kush and Parv

- **O-1** Output path: the card names `src/culinarystate/extraction/*`, which S155 uses for Step 17. Do you accept `src/culinarystate/evidence/{machinery,extraction_fields}.py`?
- **O-2** Critical field classes, scientific unit list, prompt-injection patterns: AI proposals.
- **O-3** E4 eligibility requires INDEPENDENT_BLIND. Under D-045 W2 (humans review AI drafts) no item can reach `E4_ELIGIBLE_PENDING_ADJ`. Decide whether the card's blind-adjudication rule stands for evidence, or a MODEL_ASSISTED route is defined.
- **O-4** Whether T/t validators must call the frozen Step 07 normaliser and store `normalizer_fingerprint_12` (card input).
- **O-5** Disposition of `tools/apply_link_review.py --sign-as` and `tools/apply_human_review.py` (writes EVD) now that EVD is byte-identical-protected.
- **O-6** H2 provider/licence policy and H3 compute threshold before any real document or model call (card human gate).
