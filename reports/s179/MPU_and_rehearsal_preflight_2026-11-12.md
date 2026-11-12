# Technical MPU and rehearsal preflight — 12 November 2026

**AI_PRECHECKED / NON_CITABLE / NO_HUMAN_SIGNOFF_D085.** Author facts and final author edits are excluded by the current user instruction. This technical preview does not claim that a future-dated event occurred.

## Current evidence, not the post-19-November assessment

| Gate | Current status | Evidence and limit |
|---|---|---|
| G16-DATA | FAIL_INDEPENDENCE_COMPONENT | `reports/del5/d5_score_v1_D085/d5_h1_after_rung_blind_check_D085.json`; Independent Deep Gold and calibrated duplicate/source controls are absent. AI_DRAFTED_GOLD is not human-blind gold. |
| G16-VOCAB | PARTIAL | `reports/s178/analysis/ing_alias_coverage_census_v1.json`; Coverage counts exist; no declared unresolved-frequency or fragmentation threshold passes. |
| G16-QTY | PARTIAL | `reports/s178/corpus/foodcom_bare_count_v1.json`; Unknown quantity is preserved; portion authority, SP-002 and interval-calibration limitations remain. |
| G16-SEM | NOT_EVALUATED_ON_INDEPENDENT_GOLD | `reports/del3/compiler_vs_gold_pooled_S179.json`; No independent Deep Gold or source-disjoint parser evaluation exists. |
| G16-GRAPH | PARTIAL | `reports/s178/corpus/replay_invariants_corpus_v2.json`; Engineering replay and consistency are distinct from semantic correctness on independent gold. |
| G16-EVID | PARTIAL | `reports/del5/d5_score_v1_D085/d5_scoring_result.json`; Frozen retrieval metrics exist; the compatible-recall inconsistency and non-independent gold remain. |
| G16-CONFLICT | PARTIAL | `src/culinarystate/retrieval/retriever.py`; A conflict regime exists in code; no independent detection rate or source-entailment certificate exists. |
| G16-CAL | NOT_MET | `reports/del5/d5_score_v1_D085/d5_scoring_result.json`; B7 is uncalibrated; there is no independent held-out gold calibrator. |
| G16-TRANS | HOLDS_BY_REFUSAL_NOT_SCIENTIFIC_PASS | `reports/step10/calibration_disposition_2026-11-11.md`; The real SIMULATE guard stays closed; code and property checks do not validate a model. |
| G16-DEC | RULE_NOT_MET | `reports/del5/d5_score_v1_D085/d5_scoring_result.json`; The original H3 conjunction fails; a secondary sign test does not repair P3 abstention. |
| G16-REC | NOT_EVALUATED | `src/culinarystate/decision/diagnosis.py`; Recovery/diagnosis wording and code are not independent efficacy evidence. |
| G16-PROV | PARTIAL | `reports/s179/emission_audit_2026-11-12_v2.json`; The original 30 frozen-answer flags remain; the strict sample has limited scope. |
| G16-OOD | PARTIAL_NEGATIVE_RESULT | `reports/s179/d5_frozen_split_leakage_v3.json`; P3 B7 abstains on 0/10 versus B2 3/10; exposure is disclosed, with no independence certificate. |
| G16-FT | NOT_RUN_BY_SCOPE | `reports/step36/step36_scope_manifest_2026-11-12.csv`; Step 35 explicit/learned rungs were not run; no FlavorTwin promotion exists. |

These 14 rows are a current evidence preview, not 14 passed gates. The companion JSON binds each source hash. The older 9 November G16 table remains historical: frozen D5 runs now exist, and H1/H3 are RULE_NOT_MET. Zero eligible SIM-VAL rows and real SIMULATE refusal remain current.

## Actual event requirements

| Acceptance | Earliest valid execution | Technical action to record later | Current state |
|---|---|---|---|
| T9-C23-R2, post-19-November MPU | 20 November 2026 or later | Re-read all 14 evidence paths, hash current artifacts, record the actual timestamp and outcomes. Delegation cannot convert PARTIAL/FAIL into PASS. | NOT_YET_DUE; preview prepared |
| T9-C26-R2, code/result freeze | 21 November 2026 under the current plan | Check protected ledgers, original D5 freeze, code version, output hashes and forbidden claims. Write a new dated manifest and preserve originals. | NOT_YET_DUE |
| T9-C26-R3, timed rehearsal | 24 November 2026 under the current plan | Run the actual local demo/fallback sequence; record start/end/elapsed time, observed failures and Q&A answers. | NOT_YET_DUE; no elapsed time invented |

## Reproducible technical checklist

1. Use the existing project Python. Run `python tools/s179_gate_provenance_report.py --check` and the strict/frozen/source audit tests named in `local_completion_verification_2026-11-12.json`. Record actual commands/results at a NEW output path and append a compute run row.
2. Check original `registry/freezes/D5-BENCH-2026-11-10b.json` and engineering snapshots against exact source hashes. Freeze revisions must use new versioned files.
3. Launch `python tools/run_local_demo_v2.py` on loopback. Use public-filtered mode. No BBC text, third-party recipe example, cloud model, API key or external tunnel is needed.
4. Exercise the branches: an authored process-effect query with missing context (nonnumeric refusal), explicit food safety (referral/no answer), static relationship lookup (unverified pattern or no recorded edge), recipe similarity (unbuilt-branch refusal), and empty/malformed input (ASK or HTTP validation).
5. Check that each displayed physical number keeps its TEXT_STATED/SCENARIO/MODEL_DERIVED/UNKNOWN basis. Do not interpret legacy DIRECT chips as conditional applicability.
6. Open the existing local HTML/PDF draft fallbacks if the app fails. They are technical draft assets; no hosted or video demonstration is implied. Author-facing final edits are excluded.
7. Re-run the text scanner against then-current bytes and bind extracted PDF text to PDF hashes. Disclose missing raw segments, images/OCR, paraphrases and short excerpts.
8. Record elapsed time only after an actual run. Do not fill presentation length, contributions or author availability from AI assumptions.

## Technical Q&A for later verification

| Question | Current evidence-based answer |
|---|---|
| Did H1/H3 pass? | No. Both recorded rules are RULE_NOT_MET. H1 uses 24 AI-gold questions and is circular self-consistency only. Original raw H1 NOT_COMPUTED and its separate resolution supplement both remain. |
| Does the strict demo answer retention? | The default sample had zero effect numbers without exact context. It protects a narrow table-report contract and does not demonstrate useful answer coverage. |
| Is SIMULATE validated? | No. The AA fit is NOT_VALIDATED/RESEARCH_ONLY. SIM-VAL has zero eligible comparison rows and no genuine accepted PARAM chain. |
| Is Layer 2 measured physics? | No. Scenario brackets use unverified defaults/corpus quantiles. Structural provenance and schema conformance are not scientific accuracy. |
| Did the query-gate audit pass? | No pass criterion was locked. The 100-case AI-labelled diagnostic reports separate FN/FP rates and Wilson intervals. Safety has one known D5 X miss; no rule was tuned to that control. |
| Are models independent of D5? | No blanket claim. All 79 P/C gold EVD IDs already occur in DEL-2. Positive overlap and limited recipe-ID/exact-line surface checks are disclosed. |
| Is ingredient SENSORY available? | UNSUPPORTED. Molecular taste classes or structure do not establish ingredient/recipe sensory equivalence. Step 35 is designed, not run, with learned rungs deferred. |
| Is a future MPU/rehearsal done? | No. Current preparation does not meet actual post-19-November/24-November acceptance. |

Sources: companion MPU JSON; `gate_set_diagnostic_2026-11-12.md`; `physical_layer_technical_brief_2026-11-12.md`; `reports/step36/step36_scope_manifest_2026-11-12.md`; `local_completion_closeout_2026-11-12.md`.
