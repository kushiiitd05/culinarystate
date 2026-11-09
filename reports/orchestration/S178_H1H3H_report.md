# S178 lane H1H3H: D5 scoring harness, frozen-input guard, synthetic fixtures

Status: **AI_DRAFTED (D-071).** Nothing here is a decision, signature, approval or result. Host manjot-server, worktree
`~/kush_work/culinarystate/.orch` (branch `max/s176-orchestration`), 2026-11-09. Work started at HEAD `32415c4`; HEAD
moved to `9f4cebb` during the lane (other lanes' commits; none touched `src/`, these items' board rows or this lane's
files). Nothing committed by this lane. No existing file was edited.

**No scorer was run on, and no number was computed from, the D5 benchmark questions, drafts or gold.** The drafts
(`benchmark/d5/*.csv`) were not opened; their column names were read from the drafting code
(`tools/d5_draft_{pc,s}.py`, `tools/s178_evd_d5_ux_draft.py`). Every number in this lane's outputs comes from the
invented fixture in `tests/fixtures/d5_synthetic/` and is stamped `SYNTHETIC_FIXTURE_NOT_A_RESULT`.

## 1. Item statuses

All ten items are **BLOCKED_HUMAN with the agent part DONE.** The acceptance of each item is a number "on the frozen
benchmark", and that needs (a) the human freeze (T8-C20-R3, Mon 16 Nov, hard stop 17 Nov) and (b) the rung run outputs
(T8-C15-R1, 17-19 Nov). The harness for each item is built, tested on hand-computed fixtures and exercised end to
end on the synthetic fixture. What is left per item is one guarded real-mode call of `tools/s178_d5_score.py` after
the freeze, plus the extras named below.

| Item | Agent part (done) | Left | Evidence |
|---|---|---|---|
| T8-C01-R1 router branch accuracy + confusion matrix incl. X | `d5_scoring.router_branch_accuracy` (accuracy with CP95, per block, confusion gold x predicted, per-branch recall, X sub-table), `predicted_branches` (rungs must agree), `live_router_branches` (frozen rule router on the question text, runs on manjot CPU under C07 fallback F1); output carries the frozen-benchmark and code sha256 from the guard | freeze; **a `gold_branch` on every row** (P/C/S drafts have no such column; rows without it are excluded and the status is `INCOMPLETE_GOLD_BRANCH`) | `test_s178_d5_scoring.py::test_router_*` |
| T8-C03-R1 slot accuracy (diagnostic) | `slot_accuracy`: ingredient id, process id **set** (both C processes), target SVAR in the gold set; per block with CP95; missing predictions counted; a target given only as a name is `UNRESOLVED`, not credited | freeze; runner must emit `slots.target_svar` | `test_slot_accuracy` |
| T8-C06-R1 retrieval Recall@K, MRR, compatible Recall@K, source-disjoint | `d4_metrics.retrieval_table`: K 1/3/5/10, per block (P1, P2, C, pooled), question-level bootstrap 95 % (10,000, seed `d5-d4-recall`), "x of n with every gold id in top K" with CP95, P3 "returned evidence anyway" share, per gold source family (DIAGNOSTIC_ONLY); MRR as EXPLORATORY; B0 = NA | freeze; runner must dump ranked EVD ids per arm and the compatibility vector of each gold row | `test_s178_d5_d4_metrics.py` |
| T8-C10-R1 C-block vs gold + 'cannot separate' rate | `gold_compare_label`, `compare_label_from_decision`, `c_block_scores`: agreement (all, among resolved), cannot-separate rate (rung and gold), wrong-order count, abstained, unresolved, confusion | freeze; a reviewed `gold_compare` per C row (else derived from the gold ranges, tagged); rung-blind human labels for LLM free-text comparisons (else `UNRESOLVED`) | `test_c_block_gold_derivation_and_scores` |
| T8-C13-R1 OOD gate: abstain recall on P3, false-abstain on P1/P2 | `ood_abstention`: text abstention (primary), decision-mode ABSTAIN and OOD-flag columns, P1, P2, P1+P2, P3 with CP95, and the F-12 caveat in every output ("B7 and B5T abstain on P3 by construction") | freeze, runs | `test_ood_abstention_recall_false_abstain` |
| T8-C16-R1 citation P/R + 30-claim manual sample | `citation_metrics` (support-based and gold-based readings, both EXPLORATORY); `audit_sample` (claim_audit, seed `d5-h3-audit`, B2 / B7 / B5T x 10 = 30 claims, rung-blind sheets, sealed key); `audit_report` (reviewer agreement, weighted checker precision / recall, design-weighted human unsupported share per rung next to scorer UCR, human-vs-scorer agreement, feeds the H3-A veto) | freeze, runs; **human labels Thu 19 - Fri 20** (Kush and Parv, 1.25 h each); real mode writes sheets with `--audit-dir` under `data/derived/` | `test_weighted_human_share_and_audit_report`; fixture run (sheets hashed, then deleted) |
| T8-C16-R2 enforcement cost per rung | `enforcement_cost`: sentences removed (total, per reason, answers touched), template-fallback rate (CP95), mode fallbacks, words / characters, coverage on answerable questions | freeze, runs (runner must store `enforce.removed` reasons and `fallback`) | `test_enforcement_cost` |
| T8-C22-R1 H3 on frozen P/C, decision-mode F1, zero-claim denominators | `h3_summaries` (h3_independent UCR + coverage + selective risk, per block, per source family), `h3_verdicts` for every registered option (H3-A / H3-B one- and two-sided, H3-C bootstrap via `paired_stats.ucr_diff_upper95`), P3 condition, H3-A veto (PENDING without labels), B5T vs B7 descriptive, `checker_ucr` printed with its label; `f1_table` / `mode_f1` (UCR None with no claim; precision None with no prediction; F1 None only when a class is absent on both sides) | freeze, runs, the lock's choice of D-D5-5 / D-D5-6 (real mode refuses without `--h3-option` and `--sidedness`) | `test_h3_*`, `test_f1_table_*`, `test_mode_f1_*` |
| T9-C18-R1 D4 descriptive metrics | `risk_coverage` (primary precision class, secondary sufficiency mode, error E1 / E2), `selective_risk_at_coverage` 50/70/90 % (EXPLORATORY), `all_answered_risk` (B5 reference), `abstention_precision_recall`; every cell carries x, n and a CP95; `NOT_REPORTED` = ECE, Brier, reliability, AUROC, area under the curve (a test fails if any such function exists) | freeze, runs, D-D4-1..3 at the lock | `test_risk_coverage_and_selective_risk_hand_computed`, `test_no_ece_or_brier` |
| T8-C21-R2 ablations (agent part) | `ablation`: §245.13 table (4 CHEAP_RUN rows: state conditioning, evidence compatibility, claim enforcement, OOD gate; 5 NOT_RUN with reasons), driver `run_ablations(rows, system)`, `table_from_records`, paired E1 discordance vs FULL with exact McNemar p (descriptive) | freeze; **the real `system(row, disabled)` adapter** wiring the toggles to the pipeline (runner lane; `EvidenceRetriever` has no switch to drop the compatibility term yet) | `test_s178_d5_ablation.py` |
| H1 exact McNemar (scoring part of T8-C21-R1) | `h1_analysis`: accuracy per rung and block, B4 vs B1 and B4 vs B2 exact two-sided McNemar + Newcombe (reused from `paired_stats` / `mcnemar_power.describe_realised`, no duplicated maths), intersection-union verdict with base and C5 wording, gold-origin label from `h1_independence`; `s1_outcome` / `s2_outcome` (UNRESOLVED on a link failure), `apply_human_resolutions` (only UNRESOLVED items can be resolved); any UNRESOLVED or missing item in a compared rung blocks the test | freeze, runs, rung-blind human check of unresolved items | `test_h1_*`, `test_s_outcomes_*` |

## 2. Frozen-input guard (`src/culinarystate/evaluation/frozen_guard.py`)

Real mode runs only if a freeze record exists with: `record` = `FREEZE_D5_BENCHMARK`, `status` = `FROZEN`; approvals by
**both** humans (`freeze_records.HUMANS`, exact names, ISO dates), with no AI marker in any approval field (agent, AI,
assistant, Claude, Anthropic, GPT, Qwen, model, the ksh / prv personas, ...); `files` with the sha256 of every input
the scorer reads (benchmark CSVs, EVD ledger, relatives file), each matching the bytes on disk; `code_sha256` for the
13 scorer files (`scorer_code_paths()`); `prereg_sha256` matching the prereg text; the record tracked and unmodified in
git (read-only `git ls-files` / `git diff --quiet`). Fixture paths in a real run, or a real output directory under
`reports/s178/d5_harness/` or `tests/`, refuse. The guard only reads and hashes; a test checks that the module has no
file-writing call, and nothing in the lane creates a freeze record. The record shape is documented in the module
docstring for the humans or the Mac scribe to write.

Fixture mode reads only `tests/fixtures/d5_synthetic/` (each file hashed in `manifest.json`, `synthetic: true`), and
refuses any `D5-` qid, any row not drafted by `SYNTHETIC_FIXTURE`, and any EVD id below `EVD-990000`. Every output
is stamped at the top level and in every section, and the file names start with `SYNTHETIC_FIXTURE_`.

## 3. Files (all new)

| File | sha256 |
|---|---|
| `src/culinarystate/evaluation/frozen_guard.py` | `cae6e69569beb687db5e72efef2d70e32f44d6bf3dae757791af3f1a4a62cf51` |
| `src/culinarystate/evaluation/d5_scoring.py` | `dc44088c8c3638434cf27349ac029144520d841686d641613ffc8d9e1b453a27` |
| `src/culinarystate/evaluation/d4_metrics.py` | `36f009806552eedfdecddf070feb95abb42ab283c02d7f6c4d511067d7d4e4d7` |
| `src/culinarystate/evaluation/ablation.py` | `b464ab0ac42465305daa328357e3c534e0e2b9f89f71ee21971e5b7daf2a8a8f` |
| `tools/s178_d5_score.py` (CLI: `--fixture` or guarded real mode) | `cc9be3a136a3dcbb15b8654e5a218af3665098f3d955d8c2e93bd263a5687fa1` |
| `tools/s178_d5_fixture.py` (builds / `--check`s the synthetic fixture) | `4bac0034d71f1a16ec7f7db9e64f87c3be1a18818a149e6152e2dfed63de869b` |
| `tests/fixtures/d5_synthetic/` (6 files; `manifest.json`) | `dc1c503e9b05838ed28477fcd23f5015fa9a5de57d43e2a850a6124c2878c86a` |
| `tests/unit/test_s178_d5_{guard,scoring,d4_metrics,ablation,fixture_run}.py` | 69 tests |
| `reports/s178/d5_harness/SYNTHETIC_FIXTURE_d5_scoring_result.json` | `cab6a228e92af11e0af33cdbbf797142e0908eb961c119983b847a8f78dba1c0` |
| `reports/s178/d5_harness/SYNTHETIC_FIXTURE_d5_scoring_result.md` | `1b8e7b535d5f4afe3baf6c69dfeffdbadcba2551eab42cc8d72623e83c59930e` |

The fixture is 16 invented questions (S1 3, S2 3, P1 2, P2 1, P3 2, C 2, U 1, X 2) with invented foods, ids
(ING / PROC / SVAR / EVD 99xxxx), answers and retention values chosen so every metric can be checked by hand; it is not
a food-chemistry statement. The fixture output is counts and rates only; the audit sheets (they hold synthetic answer
text) are written to a temporary directory, hashed into the JSON and deleted.

## 4. Pre-registration mapping (every output section carries `prereg_status`)

| Status | Metrics |
|---|---|
| BASE text (S171 prereg §4) | router branch accuracy; H1 McNemar rule; UCR; P3 abstention; mode violations; latency; U and X blocks |
| PROPOSED amendment S178 (C5, C6, C7) | H1 wording and power statement; H3-A / H3-B sign test, coverage, false abstention, selective risk (h3_independent), template-fallback rate and sentences removed, checker precision / recall against human labels, per-source-family breakdown |
| PROPOSED amendment S178 D4 (M1, M2) | Recall@K and condition-compatible Recall@K with bootstrap and CP counts; risk-coverage points with CP; no ECE / Brier |
| **EXPLORATORY_NOT_IN_PREREG** | router confusion matrix; slot accuracy; MRR; C-block agreement and 'cannot separate' rate; decision-mode F1; citation precision / recall (both readings); answer length; selective risk at 50/70/90 %; abstention precision; ablation table |

The board asks for several metrics the prereg does not name. Unless the 10 Nov lock adds them (human decision H-4
below), they must stay labelled EXPLORATORY in every report and slide.

## 5. Ambiguities and the conservative reading implemented

1. **Gold branch.** Router accuracy needs a gold branch per row; P/C/S drafts have none. Not imputed (P/C are not
   assumed TRANSFORMATION); missing rows are excluded, counted and the status says `INCOMPLETE_GOLD_BRANCH`.
2. **What "abstained" means.** Text abstention from the independent scorer (`h3_independent.is_abstention`) is the
   primary signal everywhere (H3 P3 rate, OOD recall, D4 error (b), binary mode F1), so the system's self-reported
   mode does not grade itself; decision-mode ABSTAIN and the OOD flag are secondary columns.
3. **Which claims count.** The H3 sign test counts questions with an unsupported **numeric** claim
   (`h3_independent.compare_rungs`, the function the amendment names); D4 error E1 counts any non-SUPPORTED claim,
   directional and uncited directional sentences included (the M2 text says "numeric or directional").
4. **P3 relevance.** The amendment sets EXACT for P1 and C, SIMILAR for P2 and is silent on P3; P3, U and X use EXACT.
5. **C cell.** The cell holds both processes, so a claim citing either arm's row is cell-relevant; the scorer does not
   check that a number is attributed to the right arm (stated, not fixed).
6. **C recall.** A C question's recall is the mean over its arms with gold ids (each question weighs once).
7. **Missing compatibility vector** for a gold id in the top K: not credited, counted.
8. **Risk-coverage score.** A COMPARE answer takes its lowest option level; ABSTAIN, ASK or a missing level is the
   lowest level. Selective risk at 50/70/90 % is the strictest level whose coverage reaches the target; no interpolation.
9. **Gold comparison.** A reviewed `gold_compare` wins; else the label is derived from the two gold ranges (disjoint ->
   ordered, overlapping or touching -> CANNOT_SEPARATE) and tagged `DERIVED_FROM_GOLD_RANGES`.
10. **Predicted comparison.** Explicit label, else the decision verdict (SEPARATED ordered by process id;
    OVERLAPPING / INSUFFICIENT -> CANNOT_SEPARATE), else abstained, else UNRESOLVED (never counted as agreement).
11. **Decision mode.** ANSWER maps to ANSWER only with a DIRECT basis, to ANSWER_SIMILAR_ONLY with a SIMILAR_ONLY basis
    or NEAR_PARTIAL sufficiency; BROAD_QUALITATIVE / CONFLICTING without a recorded basis is `OTHER` (not credited).
    Text-only rungs get no 4-class F1 (NOT_DEFINED), only the binary abstain F1.
12. **Slots.** Exact; the process slot is set equality (both C processes); the target needs an SVAR id.
13. **H1.** Any UNRESOLVED or missing item in B4, B1 or B2 blocks the test until the rung-blind human check.
14. **Freeze.** Both humans must approve (amendment C8 "both humans confirm"); EVD ledger, relatives file, scorer code
    and prereg bytes must be pinned; the record must be committed. A single approver passes only if the guard is
    called with an explicit one-human policy.
15. **Intervals.** Clopper-Pearson 95 % for every proportion (the amendments name CP; the base text says only "with
    its interval"); bootstrap quantiles are nearest-rank with the `paired_stats` sha256 seeding.

## 6. Contract for the D5 runner (T8-C15-R1), so the harness is complete on the real run

One JSON line per (qid, rung) with `qid`, `rung`, `answer`; plus, where the rung has them: `route.branch`; `slots`
{`ingredient_id`, `process_ids`, `target`, `target_svar`}; `retrieval` {`arm1`, `arm2`: ranked EVD ids}; `gold_compat`
{gold EVD id: `retrieval.compatibility` vector}; `query_states_condition`; `packet_ids`; `decision` {`mode`,
`precision`, `sufficiency` / `reason`, `evidence_basis` (DIRECT / SIMILAR_ONLY), `per_option` {name: precision,
sufficiency, process_id, support}, `comparison`, `ood`}; `predicted_compare` (rung-blind human label for LLM rungs);
`enforce` {`removed` [{reason}], `fallback`, `mode_fallback`}; `s_outcome` (from `s1_outcome` / `s2_outcome` with the
same linker for every rung); `checker` {numeric_claims, unsupported} (claims@0.2); `mode_violation`; `latency_s`.
Unknown fields are refused (`RUN_RECORD_FIELDS`). For ablations, the same records with `config`.

## 7. Tests

- New: 69 tests in `tests/unit/test_s178_d5_{guard,scoring,d4_metrics,ablation,fixture_run}.py`, **69 passed** (2.9 s).
  They include hand-computed values for every metric and the edge cases (zero claims -> UCR None; class absent on both
  sides -> F1 None and excluded from macro; precision with no prediction -> None; all-abstain rung; empty block ->
  rate None; missing level; tied levels; unresolved H1 items), CP checked against `scipy.stats.beta`, the bootstrap
  against an independent re-implementation, the H3-C bound against `paired_stats.ucr_diff_upper95`, every guard
  refusal (missing record, unreadable, wrong type, hash mismatch, missing file, unlisted input, AI-signed approval in
  9 spellings, AI marker in another field, non-exact name, bad date, single human, not frozen, code not pinned / changed,
  prereg not pinned / changed, not committed, fixture input in real mode, tampered fixture, `D5-` qid in a fixture),
  "the guard never writes", "no scoring module imports `culinarystate.generation`", byte-identical re-runs, refusal to
  overwrite a different output, and equality of the committed fixture output with a fresh run.
- Existing tests of the modules the harness imports (`test_s178_eval_{h3_independent,claim_audit,mcnemar_power,
  h1_independence}`, `test_s173_paired_stats`, `test_s173_freeze_records`): 53 passed.

## 8. compute_runs rows (header of `registry/compute_runs_v1.csv`; the orchestrator merges)

```csv
run_id,host,tree,git_commit,families,workers,command,output_path,output_sha256,start,end,status,notes
RUN-S178-H1H3H-001,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),9f4cebb+uncommitted,none (SYNTHETIC fixture only; no ledger / benchmark / recipe read),1,nice -n 10 .venv312/bin/python tools/s178_d5_fixture.py,tests/fixtures/d5_synthetic/manifest.json,dc1c503e9b05838ed28477fcd23f5015fa9a5de57d43e2a850a6124c2878c86a,2026-11-09T13:53:29Z,2026-11-09T13:53:29Z,DONE,"deterministic rebuild (same bytes as the first build earlier in the lane, whose clock time was not captured); 6 files; --check OK; invented ids / foods / answers / values"
RUN-S178-H1H3H-002,manjot-server,~/kush_work/culinarystate/.orch (worktree max/s176-orchestration),9f4cebb+uncommitted,none (SYNTHETIC fixture only),1,nice -n 10 .venv312/bin/python tools/s178_d5_score.py --fixture,reports/s178/d5_harness/SYNTHETIC_FIXTURE_d5_scoring_result.json,cab6a228e92af11e0af33cdbbf797142e0908eb961c119983b847a8f78dba1c0,2026-11-09T13:52:19Z,2026-11-09T13:52:20Z,DONE,"SYNTHETIC_FIXTURE_NOT_A_RESULT; md sha256 1b8e7b535d5f4afe3baf6c69dfeffdbadcba2551eab42cc8d72623e83c59930e; 10,000 bootstrap resamples; audit sheets written to a temp dir, hashed, deleted; earlier trial runs went to the session scratchpad only (deleted)"
```

No real-mode run was made. Load average 23-67 during the lane; all runs single process, under 2 s; disk < 1 MB.

## 9. Findings in other code (not fixed; files not mine)

1. `src/culinarystate/evaluation/h3_independent.py` L362: `compare_rungs` returns `can_be_significant: b + c >= 6`,
   which is the **two-sided** floor; under the recommended one-sided test (amendment C6) 5 discordant questions can be
   significant (5 of 5, p = 0.031). The harness computes its own floor per sidedness (`d5_scoring._sign_test`).
   Fix: rename the field `can_be_significant_two_sided` or take the sidedness as an argument.
2. The S171 drafting tools write P/C/S rows without `gold_branch`, `gold_compare` and `gold_origin` columns (U/X rows
   carry `gold_branch`). The frozen benchmark needs them for router accuracy, the C block and the H1 gold label.
3. `paired_stats.ucr` returns 0.0 for a resample with no numeric claim (documented S173 behaviour). Under H3-C this
   makes an empty B7 resample look perfect; it is the registered S171 rule, so it is reproduced, with the mandated
   caveat printed next to the H3-C result.

## 10. Human decisions (all PROPOSED)

- **H-1 (Kush + Parv, at the freeze).** Write the D5 freeze record in the documented shape (both approvals, files,
  13 code hashes, prereg hash) and commit it; the agent never writes it. Pin the scorer code **after** the lock edits
  are final, because any later code change refuses the run (T8-C01-R1 "no code change after freeze").
- **H-2 (review, by 16 Nov).** Add `gold_branch` to every row (the prereg says router accuracy "on all 80"), a reviewed
  `gold_compare` to every C row (or accept the range-derived label), and `gold_origin` / `seen_system_output` to S rows.
- **H-3 (lock, 10 Nov).** D-D5-5 / D-D5-6 (H3 option and sidedness), D-D4-1..3 (D4 metrics, score, error); the real
  mode refuses without an explicit `--h3-option` and `--sidedness`.
- **H-4 (lock).** Add to the prereg, or leave EXPLORATORY: slot accuracy, MRR, router confusion matrix, C-block
  agreement / cannot-separate rate, decision-mode F1, citation precision / recall, answer length, selective risk at
  50/70/90 %, abstention precision, the ablation table.
- **H-5.** Accept or change the conservative readings in section 5 before the lock (each is a single constant or rule).
- **H-6 (19-20 Nov).** Label the 30-claim rung-blind sheets; until then the H3-A veto is PENDING and H3-A cannot be met.
