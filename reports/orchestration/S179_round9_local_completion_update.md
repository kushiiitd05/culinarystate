# S179 round 9 — local completion reconciliation, 12 November 2026

Status: **AI_DRAFTED / PROPOSED / AI_PRECHECKED / NON_CITABLE / NO_HUMAN_SIGNOFF_D085**.
This additive evidence review reconciles the immutable round-6 acceptance audit, round-7 private-transfer
supplement and round-8 emission-audit brief with the local artifacts now available. It does not amend the S178
board, adopt decisions, confer human verification or retroactively pass frozen scientific results.

## Accounting and acceptance updates

Recounted the round-6 CSV: **252 rows = 84 MUST + 168 SHOULD; 51 POST rows retained**. Round-6 MUST statuses
remain its historical snapshot: 24 DONE, 8 DONE_AI_DELEGATED, 8 DONE_DRAFT, 4 DONE_WITH_DEVIATION, 25 PARTIAL,
5 OPEN, 4 NOT_RUN_BY_DECISION, 2 BLOCKED_DATA, 2 BLOCKED_HUMAN, 1 DEFERRED and 1 ONGOING. The table below is
an additive reconciliation of selected MUST items, not a replacement aggregate or a project completion percentage.

| Item | Current proposed disposition | What is now evidenced; remaining acceptance boundary |
|---|---|---|
| T2-C09-R4, CAL verification | DONE_AI_DELEGATED_WITH_LIMITS (round 7 retained) | Frozen-bound CAL sheet restored and source prechecked. This is AI_PRECHECKED, not two independent human verifications. |
| T5-C10-R5, AA sensitivities | DONE_WITH_DEVIATION | Model B fits use 4 AAK-01 and 3 AAK-06 rows. Every declared arm has a disposition: below-60 and water-contact exclusions retain the primary rows without refitting; licence-rejected arm NOT_RUN; assay-clean shared-Ea arm NEED_DATA. No primary fit or source exclusion changed. |
| T5-C10-R6, SIM-VAL | PARTIAL; extraction/refusal disposition complete | 19 extracted rows, source precheck 6 PASS / 12 FLAG / 1 REJECT. Diagnostic v2 excludes 16 NOT_PER_TEMPERATURE_RATE and 3 SOURCE_PRECHECK_NOT_ELIGIBLE; zero primary-comparable rows, zero predictions and no error metric. Primary status NOT_RUN_BASIS_REVIEW_REQUIRED. This closes the unexplained missing-file/extraction gap, not the predictive-comparison requirement. |
| T5-C12-R2, identifiability | DONE_DRAFT_WITH_LIMITS | Bounded conditional OLS profiles exist; practical precision remains NOT_ASSESSED_NO_LOCKED_PRECISION_CRITERION. Source restoration does not establish useful scientific precision. |
| T5-C21-R1, G15 scorecard | DONE_DRAFT | All 13 gates mapped: 5 PARTIAL, 3 NEED_DATA, 5 NOT_MET, zero PASS. A completed assessment is not a passed gate. |
| T5-C07-R3, KIN/PARAM minting | OPEN | No complete admissible source-linked KIN/PARAM provenance. Do not invent IDs or mark AI-prechecked records HUMAN_VERIFIED. |
| T5-C11-R3/R4, calibration/REAL route | PARTIAL | Calibration disposition/model-card draft exists. FORM/PARAM/VAL/domain/human-verification requirements still close the REAL SIMULATE route; no scientific calibration pass. |
| T9-C09-R1, split registry | PARTIAL overall; frozen-D5 artifact complete | New versioned v3 registry: 8 blocks, 74 identifier-only question units and reproducible hashes. Compute/EXP recording is orchestrator work; historical private DIAG29/07.A assignment provenance is retained, not reconstructed. |
| T9-C09-R2, leakage check | Frozen-D5 audit complete with reported overlap; broader independence unestablished | Every attempted v3 section completed after tier-1 restoration. Positive overlaps and restricted denominators are explicit below. No blanket zero-overlap, near-duplicate or source-family independence certificate. |
| T9-C09-R3, result split labels | PARTIAL assembly; section refreshed | Updated only §2 of S179_licence_and_split_labels_DRAFT.md with actual frozen counts, v3 evidence and split labels. Each final table still needs the stated label; no automatic final-author approval. |
| T0-C06-R2, emissions | PARTIAL (round 8 retained) | Original 346 frozen-answer audit retains 30 flagged records: B0=4, B2=8, B5=18. New strict runtime is a separate diagnostic; it does not erase these flags or certify all semantics. |
| T9-C28-R2, source-text scan | PARTIAL | Local source-window scans are bounded by their supplied inputs and text-window method; images, short excerpts/paraphrases and later edits need separate review. No independent licence clearance. |
| T9-C20-R1/R3, report/deck | PARTIAL pending final assembly/facts | Draft sections and export work can proceed locally. Actual author contribution facts, author edits/review and slot/date/length facts cannot be inferred by an AI reviewer. |

Evidence for the AA rows: `reports/step10/aa_model_b_sensitivities_2026-11-11.{json,md}`,
`aa_SIMVAL_diagnostic_2026-11-11_v2.json`, `SIMVAL_source_precheck_2026-11-11.md`,
`aa_identifiability_profile_summary_S179.json` and `G15_T5_scorecard_2026-11-11.md`.
AA labels remain NOT_VALIDATED / RESEARCH_ONLY; no source excerpts or private observations are reproduced here.

## Frozen-D5 evidence, rechecked

Freeze D5-BENCH-2026-11-10b contains S1/S2=12 each; P1/P2/P3/C=10 each; U/X=5 each: 74 unique questions.
There are 24 distinct S recipes (22 Gutenberg, 2 Wikibooks), no S1/S2 recipe-ID overlap and 79 distinct P/C gold
EVD IDs. C/P1 shares 2 gold IDs, C/P2 shares 1 and P1/P2 shares 9. All 79 gold IDs occur in the 17,458-row DEL-2
retention pool. Retrieval-silver overlap is 2 gold IDs, 1 gold cell and 13/44 ingredient/process pairs.
No overlap was found with the 50 gold recipe IDs, the seven declared seeded Rung-A/dev samples or 68 J4 hashes.
Those exact/provisional-group checks do not establish near-duplicate control or source-family disjointness.

The restored-source exact-line check loads all 24 S recipes, but only the two Wikibooks recipes provide
ingredient lines (9 total). RecipeDB3 exact normalized matches are train=1/9, calibration=0/9, dev=0/9,
test=1/9; TASTEset any split=2/9. The 22 Gutenberg segments have no ingredient-line channel, not 22 negative
NER test outcomes. This exposure proxy is neither learned-NER accuracy nor cross-family agreement.

The v3 run was 2026-11-12T07:40:47.236728+00:00–07:40:55.230948+00:00. Source, actual dependency/tool and output
hashes are in `reports/s179/d5_frozen_split_leakage_v3.json`. v2 remains the immutable missing-input run.
The old split registry's S-5 mislabel remains historical; actual S-5 is food-group-disjoint and S-6 study-disjoint.
DIAG29/07.A provenance is RECORDED_PROVENANCE_NOT_REDERIVED; 07.A-R1 remains NOT_RUN under D-085.

## Engineering evidence and checkpoint gap

The separate strict-v2 diagnostic records 1,000 metadata-template calls (seed 17912), including 200 synthetic
recipe requests: SAFETY=186, TRANSFORMATION=176, UNKNOWN=638; ASK=659, ABSTAIN=155, ABSTAIN_SAFETY=186.
Its scoped counters are zero for citability violations, handler errors, missing numeric provenance, unknown
numeric fields and unexpected SIMULATE; 141 numeric fields and 53 physical steps were checked. It emits no
table effect numbers. `strict_http_smoke_2026-11-12.json` records PASS for its local HTTP checks, including
forwarded local-mode refusal. Both artifacts explicitly state scientific_gate_pass=false. Synthetic sampling,
declarative provenance and local HTTP checks do not certify real-world applicability or browser interaction.
The original round-8 audit's 30 D5 flags and its lexical/structural scope remain intact.

Tier-1 restoration removed the missing identity/source-input barrier. The unresolved learned-NER/Rung-A
cross-family diagnostic still needs the **actual frozen DeBERTa-base+CRF checkpoint**, recorded SHA-256 prefix
`582c056ac20625ac`, plus its exact inference/tokenization configuration, or provenance-bound persisted
Food.com/Wikibooks inference spans. The optional 2,035,667,491-byte tier-2 bundle instead supplies metadata for
`deberta-v3-base_crf` / `DebertaV2ForTokenClassification` (`model_type=deberta-v2`). It is not the recorded
frozen-base checkpoint. `optional_model_bundle_check_2026-11-12.json` records exact_frozen_model_available=false,
substitution_performed=false and inference_performed=false. No architecture substitution or accuracy claim is
made. The earlier NER artifact inventory is historically scoped to its inspected roots; bundle inspection does
not prove the required checkpoint absent everywhere. Archived TASTEset-only predictions and procedural evidence
spans are not a substitute for the missing frozen cross-family inference artifacts.

## What still requires evidence, rather than more local drafting

- Independent human source verification and named reviewer decisions retain their literal requirements; AI
  review can prepare checkable records but cannot supply human consent, identity, contribution facts or IAA.
- Real AA basis/assay-compatible held-out observations and admissible FORM/PARAM/VAL/domain provenance are
  needed for scientific calibration and REAL SIMULATE. A zero-eligible-row refusal is the correct current result.
- T9-C23-R2 requires a post-19-Nov assessment; T9-C26-R3 requires the actual timed 24-Nov rehearsal. Neither
  future-date condition is satisfied by an artifact on 12 November.
- The required frozen checkpoint or bound inference outputs are needed for the unperformed learned-NER
  diagnostic. A GPU/VPN is not itself the acceptance requirement; exact artifacts and provenance are.
- Final authored report/deck checks, source-scan scope and orchestration logs must reflect the final bytes.
  This supplement does not pre-count a currently running full suite, final export or unrecorded compute entry.

All 51 POST rows remain POST; scope cuts and H1/H3 RULE_NOT_MET remain unchanged. Remaining barriers do not
prevent engineering, descriptive artifact assembly or an honestly labelled local demonstration from proceeding.

## Artifact hashes at review

- `reports/orchestration/S179_round6_acceptance_audit.csv`: `2da5441e54308a0dbd6f2c9d14dcb7b0f77a869229fb58fcf2e759a22377c7a8`.
- `reports/orchestration/S179_round7_private_transfer_update.md`: `35babe811050fdd98d2bdd2fbc4d70d55569995410268e236d080be922acf024`.
- `registry/d5_frozen_split_registry_v3.csv`: `4dc1329a7d9fdb8a4edaecada6526a997169d39235c043b6d1403229df9c0d8e`.
- `reports/s179/d5_frozen_split_units_v3.csv`: `bc4764a447d066942ee3ca57aadce3b2aafdd61b59f8acebdfd865a63a0a50bc`.
- `reports/s179/d5_frozen_split_leakage_v3.json`: `abfb62d3fa8e08dd5e17abf11b31c9112110aa030635bf0889e658f4f227e46f`.
- `reports/step10/aa_SIMVAL_diagnostic_2026-11-11_v2.json`: `697b3fc2c0cf3edd205339b6494cf7e73faa73ab04d9237553d81c8272477fbb`.
- `reports/step10/G15_T5_scorecard_2026-11-11.md`: `8cb0b9c98bcf29fe7cb8a5d745f7be1011e8381f374ceed0391e9606040677a1`.
- `reports/s179/strict_runtime_audit_2026-11-12.json`: `7fcf396cc51ed41f9307736e397e98716438e59876657a4b4de14d534abe6274`.
- `reports/s179/strict_http_smoke_2026-11-12.json`: `cf90fc1c126e46f20a82e261d096b4a4b9075b6c32fa48724ffe486dc7d9f89c`.
- `reports/s179/optional_model_bundle_check_2026-11-12.json`: `0b18b63a0e020496e2f5a07fc858b3cca589fa9123dbdf464c8250740f04c393`.


## Orchestrator recording supplement

All local runs are now appended in `registry/compute_runs_v1.csv` (IMPORT002, MODEL001, LEAK004..007, EMIT003, HTTP001, TEST014..016, EXPORT001). `registry/experiments_S179_local_2026-11-12.csv` records M5/M6/M8 artifacts without minting EXP ledger IDs. The actualD5 registry/exposure artifact and recording gap is closed. Overall T9-C09-R1 remains PARTIAL because its broader historical assignment/independence acceptance is not rederived; no zero-overlap or independence certificate is claimed. See root closeout for 8085-pass full suite, 75-pass targeted check, export/text-scan scope and remaining dependencies.
