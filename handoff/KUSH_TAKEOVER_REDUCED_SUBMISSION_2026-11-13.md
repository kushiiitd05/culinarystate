# Kush takeover — reduced CulinaryState submission, 13 November 2026

**Candidate status: DRAFT_CANDIDATE_NOT_AUTHOR_APPROVED.**

**Start here.** This document replaces the need to reconstruct Parv's chat history. It covers the reduced submission finish line, completed local work, the candidate bundle and the remaining actions. It does not declare author approval or scientific validation.

Labels: AI_DELEGATED_D085 · NOT_INDEPENDENT · NOT_HUMAN_VERIFIED_UNTIL_REVIEW · NO_HUMAN_SIGNOFF_D085. Human review remains pending unless explicitly recorded in an existing human decision. Parv excluded author facts and final edits; those files were preserved.

## 1. Resume safely

Use branch `kush/s179-finish-fixes` in `kushiiitd05/culinarystate`. Pull before appending shared logs/decisions and push after each coherent item. Do not merge to main from this handoff. Local source/model data remain outside the public bundle.

```sh
git pull --ff-only
git status --short
python tools/s179_gate_provenance_report.py --check
```

Use the existing compatible Python3.11 environment. The recorded dependency snapshot is `reports/s179/env_lock/parv_S179_2026-11-11.txt`. No new environment or dependency was installed during this closeout. Tests needing loopback sockets must run with local socket permission; a sandbox bind failure is not a reason to weaken or skip them.

The exact source revision and artifact hashes used for the candidate are in `reports/final/submission_candidate_2026-11-13/build_manifest_v1.json`. Subsequent documentation commits can be later than that build revision.

## 2. What is ready

| Deliverable | Result | Read this |
|---|---|---|
| Submission candidate | Curated original draft report/deck Markdown, earlier PDF/HTML exports, current technical addenda, figures, verification and this takeover document. Every member is explicitly allowlisted and hashed. Draft candidate, not author-final. | `reports/final/submission_candidate_2026-11-13/README.md`, `allowlist.json`, `build_manifest_v1.json` |
| R1 counterpart/comparison | Exact issued100-row ksh copy reconstructed from the original hash; a fresh ksh AI reviewer returned independently of prv labels. Both original returned sheets frozen and compared. | `reports/s179/r1_paired_AI_closeout_2026-11-13.json` |
| R1 resolution record |497/900 axis-code matches;400 CORRECT/N/A convention differences and3 other axis differences;3 overall differences. Proposals retain originals, with no post-adjudication rescore. Result NOT_COUNTED for human gating. | `reports/s179/reduced_submission_review_resolution_2026-11-13.{json,md}` |
| CAL counterpart/comparison | Fresh source-only ksh review and existing prv review both match16/16 numeric spans. Additional metadata qualifiers are retained separately; extraction and fit unchanged. | `reports/s179/CAL_paired_AI_closeout_2026-11-13.json`, `ksh_CAL_source_review_closeout_2026-11-13.{json,md}` |
| Demonstration | Eight authored backend scenarios execute against strict-v3. Routing, fail-closed output and numeric provenance checked; unsupported branches honestly refuse. Four earlier real-browser cases/screenshot remain separate evidence. | `reports/s179/reduced_submission_demo_2026-11-13_v2.json`, `strict_v3_browser_rehearsal_2026-11-12.json` |
| Verification | Final full-suite result, named skips, exact tested source revision, protected hashes and prior instrument-failure explanation recorded. | `reports/s179/reduced_submission_final_verification_2026-11-13.json` |
| Earlier technical results | Frozen NER agreement, D-097 first type-count result, paired D0 diagnostic contrasts, binding errors, blind claim review, branch-Gold review and source-licence findings remain available. | `reports/s179/prv_continuation_closeout_2026-11-13.md`, scope matrices v2/v3 |

The original report/deck sources and the ten-page/thirteen-slide exports are earlier drafts. The addenda supersede stale availability/review statements. They do not replace the original H1/H3 outcomes, independent-Gold limitations or source-quality qualifications. The candidate preserves both layers so authors can perform final integration explicitly.

## 3. Review conclusions requiring your attention

**R1 is not a human gate pass.** Two AI personas cannot provide independent human inter-rater evidence. The original registered scorer was reused for descriptive statistics; the public wrapper explicitly returns NOT_COUNTED / AI_PERSONAS_NOT_INTER_RATER. Original v4 FAIL remains unchanged. Do not relabel to improve AC1, rerun after proposals, sign a human prereg on behalf of either person, or promote COND verification from these AI results.

Most R1 differences are applicability-code conventions. Two further flags involve integer-second source precision versus tiny conversion drift; another concerns slash notation whose output already preserves AMBIGUOUS status. Root proposals do not establish normalizer defects. Private source/protocol-linked queues are available for expert verification. Neither reviewer independently verified opaque ontology-code meanings.

**CAL numeric matches do not validate the AA model.** Both reviewers found the same numeric spans, but source metadata need qualifications: internally conflicting time-point counts, assay specificity, measurement-location limits, leaching not measured, and a first-order alternative when another order is preferred. No new trajectory, PARAM/VAL lineage, independent lab group or eligible SIM-VAL row was created. Frozen Model A stays unchanged and not validated.

**Negative results remain visible.** H1/H3 RULE_NOT_MET, Phenol-Explorer diagnostic rungs often worse than D0, the blind claim/checker mismatch and incomplete source compatibility are results to disclose. They are not unfinished work that should be tuned until positive. D-102 and D-106 are explicitly post-hoc amendments; preserve first outputs alongside them.

## 4. Private files and transfer

The previous Parv return pack remains `data/derived/prv_return_to_kush_2026-11-13/`; its manifest is `reports/s179/prv_private_return_manifest_2026-11-13.json`. It was staged locally, not sent. New ksh AI sheets are:

- `annotation/condition_audit/ksh_R1_AI_review_closeout_2026-11-13.csv`
- `annotation/aa_pilot/ksh_CAL_source_review_closeout_2026-11-13.csv`
- `annotation/aa_pilot/ksh_CAL_source_review_closeout_2026-11-13_spans.json`

New source-linked comparison/proposal queues are under `data/derived/reduced_submission_closeout_2026-11-13/`. Public reports bind all input and private-queue hashes. These are not in Git or the public candidate. Privately copy them if you need to verify their raw source spans on another machine. No private upload or message was sent by the agent.

The user-supplied `condition_audit_packet_100_R1_Parv.csv` is blank and exactly matches issued SHA256 `f086975a2eac8531633299ff4f089da007ecc19c46c77619977ba96b925ca27d`. Its transfer issue is fully resolved. It is not a completed human review.

The exact NER checkpoint, committed seed/sealed list, accepted P1A packets and frozen7b model remain with your machines. Earlier local-absence statements were superseded by your upstream results. Do not request the seed or sealed list or substitute local3b for frozen7b. This session performed no external model inference or SSH.

## 5. Exact remaining finish-line actions

| Order | Action | What closes it |
|---|---|---|
|1| Review the paired AI summaries/source-linked proposals and record your actual acceptance or corrections | An actual human review entry. Keep the human-gate outcome NOT_COUNTED; acceptance of AI work is not independent validation. |
|2| Reconcile retained model/retrieval experiments with your latest server outputs | Check D-098 ablations, frozen7b regeneration, source-held-out retrieval and versioned D5 re-emission. Commit actual artifacts if run; otherwise retain a named NOT_RUN disposition and its limitation. Existing B0–B7 results must not be overwritten. |
|3| Integrate technical addenda into the author-final report/deck and fill person-only facts | Authors supply contributions, signatures/permission statements and final editorial choices. Preserve all negative results and AI labels. This was excluded from Parv's authorized editing scope. |
|4| Decide whether newly acquired source papers belong in this submission | AAK-04/10 attribution families confirmed but local PDF hashes/extraction remain pending; AAK-02/08 unconfirmed; AAK-05 has NC-SA licence and is excluded by the project's CC-BY/CC0 rule. No paper is silently marked acquired. New SIM-VAL extraction requires a fresh unexposed session and original partition rules. |
|5| Rebuild candidate after any author edits; run checks on that exact source revision | New versioned artifact paths, hashes, number/source-text review and required CI. Do not treat the current earlier PDF exports as final updated author documents. |
|6| Review/integrate PR stack and perform scheduled presentation events | Check live PR#11/#12 metadata, approvals, exact integration tests and conflicts; no merge performed here. MPU/freeze/rehearsal require their real dates/events. |

Experimental data constraints do not block submitting an honestly labelled reduced project if its approved scope accepts those limitations. They do block validated simulator, synthetic-prior/hybrid and multi-step chemistry claims. The separate full-corpus state/effect plan is not silently represented as completed by this submission candidate.

## 6. Commands and demonstration fallback

```sh
# Full local regression; keep named skip reasons.
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  python -m pytest -q -rs -m 'ledgers or not ledgers' -o faulthandler_timeout=120

# Reproduce backend demonstration to a NEW output path.
python tools/s179_submission_demo.py --out reports/s179/reduced_submission_demo_NEW.json

# Local browser demonstration, public-filtered by default.
python tools/run_local_demo_v3.py
```

The eight backend cases include safe refusals for unimplemented metadata/search/multimodal handlers and absent substitution edges. They do not prove those features work, that nutrient applicability is established, or that the model answers every question. The recipe/physics case demonstrates provenance-labelled engineering quantities without authorizing nutrient predictions.

Use `reports/s179/strict_v3_fallback_2026-11-12.png` and `reports/s179/prv_rehearsal_pack_2026-11-13.md` if the local application cannot run. State that these are saved technical demonstration materials. A four-case browser rehearsal or eight-case backend check is not the actual scheduled human presentation rehearsal.

To rebuild the bundle, use a new archive and external manifest path:

```sh
python tools/s179_submission_candidate.py \
  --allowlist reports/final/submission_candidate_2026-11-13/allowlist.json \
  --archive data/derived/submission_candidate_2026-11-13/CulinaryState_reduced_candidate_v2.zip \
  --manifest-out reports/final/submission_candidate_2026-11-13/build_manifest_v2.json
```

The archive contains an internal `MANIFEST.json` binding every member. The external build manifest binds the ZIP SHA256 and exact source revision. Keep source papers, corpora, private review sheets, checkpoints and seals outside this bundle. The candidate is a document/artifact package, not a self-contained model/data installation.

## 7. What must remain unchanged

EVD/COND/SRC/MEAS/SNAP source rows, frozen benchmark/question IDs, scorer/preregistration/prompt/results, original generation, quantity grammar and original negative findings. New work uses new versioned paths. Keep source observations, scenario assumptions and AI drafts distinguishable. UNKNOWN is valid; no missing scientific value is invented to make coverage look complete.

**Completion statement:** feasible local comparison, candidate assembly and handoff work is complete at its recorded revision. Reduced submission still needs the author/integration/event actions above; full scientific validation is not claimed.
