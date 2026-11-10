<!-- v2 of the D5 pre-registration (S179). Built mechanically from the v1 draft (sha256 53ad89b7...) and the S178 amendment draft with the options of D-080 and D-081 by tools/s179_build_d5_prereg_v2.py. One option is still OPEN (D-D5-6 sidedness, human). Unsigned. -->
# D5 benchmark (~80 questions) and the H1 / H3 tests — pre-registration (DRAFT, UNSIGNED)

Status: **DRAFT_PENDING_SIGNATURES** (Kush, Parv). Written S171, 2026-11-08, by the coding agent (D-075 M5), before any
benchmark question exists and before any rung is run on one; amended before any signature with the S178 options
(`reports/del5/d5_benchmark_preregistration_AMENDMENT_S178_DRAFT.md`) as chosen in D-080 and D-081 (ksh and prv, AI
under D-071; not a human sitting); D-D5-6 (sidedness) is still open for the humans. Until both humans sign
it is a dated AI draft. The 20-question silver ladder (`reports/del5/ladder_*`) was written by an AI and seen during
development: it is **not** part of this benchmark and is not reused. Label on every output and slide:
`MODEL_ASSISTED_GOLD, PILOT, authors-as-reviewers`.

## 1. Composition (80 questions, SSOT §12 task types)

| Block | n | Task type (§12) | Tests |
|---|---|---|---|
| S1 current state | 15 | current-state tracking | H1 |
| S2 next action | 15 | next action | H1 |
| P1 process effect, DIRECT evidence exists | 10 | chemistry relevance | H3 |
| P2 process effect, only similar-food evidence | 10 | chemistry relevance | H3 |
| P3 process effect, no evidence or out of distribution (gold = ABSTAIN) | 10 | chemistry relevance | H3 |
| C process comparison (two processes, same food and target) | 10 | process comparison | H3 |
| U substitution | 5 | process / ingredient substitution | descriptive |
| X controls: 3 food-safety questions (gold REFUSE) + 2 out of scope, empty or vague | 5 | router controls | descriptive |

- **S blocks:** recipes sampled by sha256(`d5-bench-2026-11-08` ‖ recipe_id) from **Wikibooks and Gutenberg only**
  (lawful to send to the server LLM; D-003 keeps BBC text off the server), ≥ 4 steps, with a cut point after a
  seeded step (`d5_state.seeded_cut`). **One question per recipe.** Eligibility does not depend on any engine
  output: the S171 drafting rule that kept an S1 recipe only when the engine found a heated ingredient
  (`tools/d5_draft_s.py` L66-L67) is dropped, so "none" is a possible S1 answer. S recipes are excluded from every
  Rung A, lexicon or prompt tuning pool, checked by recipe_id against the D-073/D-074 samples and the P1 packets
  (T9-C09-R2). Gold is written by the humans blind (§3); the engine's replay is a draft and a comparison only.
- **P/C blocks:** cells drawn by seed from the EVD index per stratum (DIRECT / similar-only / none), across ≥ 8
  ingredients and ≥ 4 processes. Gold mode is ANSWER, ANSWER_SIMILAR_ONLY, ABSTAIN or COMPARE, with the cited EVD
  ids that a correct answer may use.

## 2. Rungs (SSOT §245.12, as available; same questions, same LLM, temperature 0, fixed seed)

B0 LLM only · B1 dense RAG · B2 BM25 + dense hybrid (reciprocal-rank fusion, k = 60) · B4 state-aware (B2 + the
replayed recipe state at the cut) · B5 B4 + evidence packet · B7 B5 + decision layer with post-hoc enforcement
(B5F+E), described everywhere as **"rule-based evidence-sufficiency abstention (uncalibrated)"**; no calibration
claim is made · B5T template (no LLM). B3 and B6 are not built and are reported as NOT_RUN.
- **Retrieval cut:** for S questions, B1, B2 and B4 retrieve only from steps 1..cut (`steps[:cut]`;
  `h1_rungs.context(..., pre_cut_only=True)`); no step after the cut is in any rung's context. Before scoring,
  `h1_independence.assert_independent` is run on every (question, rung) context and any failure is reported.
- **Embedding:** `intfloat/e5-large-v2`, Hugging Face revision `f169b11e22de13617baa190a028a32f3493550b6`, mean pooling, prefixes `query: ` / `passage: ` (as
  `tools/embed_texts.py`). Evidence: `reports/del4/retrieval_silver_v2_analysis.md` (silver, dev only, EVD text; not
  measured on recipe-step chunks). No change
  after signing.
- **B4 state block:** "Ingredients used", "Heated so far", "Last action" from `h1_rungs.state_block` on
  steps[:cut] (`state_view="ANSWER"`). With blind human gold this block is the treatment H1 tests, not the
  gold.
- **LLM, fixed now:** qwen2.5:7b-instruct, Ollama model digest `845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e` (RUN-S179-PIN-001), temperature 0,
  seed `7`, `num_predict` `200`; the prompt templates are hashed in the lock
  record (REV-B G-21). Any later change to model, prompt or `num_predict` is a dated amendment before any rung runs.
- **If vinayak is unreachable by 17 Nov (C07):** B0, B1, B2, B4, B5 and B7 all need the LLM, so H1 and H3 are
  reported **NOT_RUN**. What still runs on manjot CPU: B5T, the retrieval-only metrics of B1/B2 (T8-C06-R1) and
  router branch accuracy (T8-C01-R1), all descriptive.

## 3. Gold (model-assisted, stated as such)

The agent drafts every question, and every P/C gold answer. **S gold is written by the humans, blind:** for each S
question each reviewer first writes an answer from the recipe text alone (steps 1..cut for S1; the text of step
cut+1 for S2), on a sheet where every `gold_*` column and every engine output is hidden, and the sheet records
`seen_system_output = false` per row (Step 36 G36-B). Only then does the reviewer see the engine draft, and may
only KEEP or DROP the *question* (well formed, cut sensible), never edit an answer toward it.
The S gold is the two blind answers where they agree; where they differ, the two reconcile from the recipe
text; an S question with no agreed answer is dropped and the next by rank enters. The engine draft never becomes
gold. Kush-Parv agreement on blind answers is reported (AC1 and raw agreement, with n).
Every S row carries its gold origin (`h1_independence.GOLD_ORIGINS`: HUMAN_BLIND, HUMAN_AFTER_SEEING_ENGINE,
ENGINE_DRAFT); H1 is labelled INDEPENDENT_GOLD only on HUMAN_BLIND rows (`gold_independence_report`).
P and C rows are reviewed as before (keep, edit or drop, with a reason); a question enters only if both keep it, or
keep it after the same edit. The P and C blocks are overdrafted (15 per block, seeded rank order); the first 10 by rank that enter form the block, so drops do not shrink the block and reviewers cannot pick which ones replace them. Gold retention ranges are fractions (USDA % values ÷ 100). The S blocks are overdrafted the same way (20 per block, 15 enter). Review sheets: `annotation/d5_review/d5_review_v1_{Kush,Parv}.csv` (git-ignored: recipe text); verdict KEEP, EDIT (with the edited question and/or gold) or DROP, with a reason. Drafts: `benchmark/d5/d5_draft_{PC,S}_v1.csv`. The benchmark is labelled **MODEL_ASSISTED_GOLD** (D-045), not independent human gold. It is frozen
(SHA-256 committed) before any rung is run on it. No question is changed after a rung is run.

## 4. Metrics and decision rules (fixed now)

- **H1** (S1 + S2 pooled, n = 30): exact-match accuracy against the blind human gold (ingredient
  set for S1, next process for S2), B4 vs B1 and B4 vs B2, paired by question. Test: exact two-sided McNemar on the
  discordant pairs (`paired_stats.mcnemar_exact`), α = 0.05; the 95 % Newcombe interval is descriptive, and the
  decision is the exact test even when the interval excludes 0. H1 meets the pre-registered pilot rule only if
  B4 > B1 **and** B4 > B2, both significant (intersection-union, no alpha correction); otherwise "not shown at this
  n" (no other claim). Per-block (S1 or S2 alone) results are descriptive only.
- **Scoring:** answers are linked to ING / PROC ids with the same linker for every rung; an answer item the linker
  cannot resolve goes to a rung-blind human check (rung hidden) before unblinding, and the per-rung unresolved rate
  is reported (REV-B F-13: B4's own surface strings always resolve).
- **Power (fixed now, T9-C12-R1):** at n = 30 only accuracy gaps of about 0.25 or more can reach significance with
  useful probability (80 % power needs a true gap of 0.28-0.36 at discordance 0.3-0.5, and no gap reaches 80 % at
  discordance 0.2); the smallest significant split is 6-0 (gap 0.20). At n = 60, over the same discordance 0.3-0.5,
  80 % power needs a gap of 0.20-0.26 (0.16 at discordance 0.2). A null result is uninformative, not
  evidence of no effect. If the realised number of discordant pairs is below 6, the report says "cannot be
  significant at this n".
- **Circularity (T8-C04-R2):** S gold is human-written blind; the engine-vs-blind-gold agreement on S is
  reported as its own figure (a D3 datapoint, n stated).
- **H3** (P1–P3 + C, n = 40): B7 is "rule-based evidence-sufficiency abstention (uncalibrated)".
  - **Why the S171 rule is replaced:** B7's text is produced by `generation/enforce.enforce`, which deletes every
    sentence that `generation/claims.check_claims` (claims@0.2) flags; scoring B7 with the same checker gives
    UCR(B7) = 0 by construction (0.0 in both smoke ladders, as for the template B5T). And gold ABSTAIN on P3 means
    "the ledger is silent", while B7's route is the same ledger lookup, so B7's P3 abstention is guaranteed (F-12).
  - **Independent scorer:** claims are scored by `evaluation/h3_independent` (version string and code sha256 frozen
    with the benchmark, before any rung runs), which shares no code with `generation/claims` or
    `generation/enforce`, extracts numeric and directional claims itself, binds each number to its own citation
    group, looks the cited ids up in the EVD ledger, and counts a claim as supported only if the value is within
    0.03 (fraction scale, `VALUE_TOL`) of the cited row **and** the row's ingredient, process and target match the
    question (REV-B G-12): `min_relevance` = EXACT for P1 and C questions, SIMILAR (parent or aggregate row) for P2
    questions, whose gold is similar-only by design. claims@0.2 UCR is still printed, labelled "enforcement
    checker, not independent".
  - **Decision test:** an exact sign test (`h3_independent.compare_rungs`, `sign_test_exact`) over questions where
    exactly one of B2 and B7 has at least one unsupported claim (independent scorer); B7 better needs p <= 0.05,
    **[OPEN, D-D5-6: sidedness is a human choice (D-081); the lock may not be issued until one option is deleted]** i.e. at least 5 of 5, 6 of 6, 7 of 7 or 7 of 8, 8 of 9, 9 of 10 [one-sided, `alternative="greater"`] | 6 of 6,
    7 of 7, 8 of 8, 8 of 9, 9 of 10 [two-sided]. Fewer than 5 [one-sided] or 6 [two-sided] such questions: "cannot
    be shown at this n". The question-level bootstrap (10,000 resamples, seed `d5-h3`) is a descriptive interval
    only. B5T is compared with B7 by the same test (descriptive).
  - **Coverage, reported beside every UCR (not gating; `h3_independent.summarize_rung`):** coverage on answerable
    questions (P1, P2, C), false abstention, selective risk (questions with a claim that carry an unsupported one,
    with a Clopper-Pearson interval), abstention on ABSTAIN gold, numeric claims made on ABSTAIN gold; plus the
    template-fallback rate and sentences removed by `enforce`. A rung can lower UCR by saying less; these show
    whether it did.
  - **P3:** abstention rates are reported per rung, descriptive, with the note that B7 and B5T abstain on P3 by
    construction.
  - **Human claim audit (T8-C16-R1, REV-B G-08):** a rung-blind sample drawn by
    `claim_audit.stratified_audit_sample` (seed `d5-h3-audit`, rungs B2, B7, B5T, `per_rung` = 10, 30 claims); strata = independent-scorer verdict x enforcement-checker flag, disagreement
    strata first, every stratum's population and sample size recorded. Sheets hide rung, question id and every
    automatic verdict; they hold answer text, so they live under `data/derived/` (git-ignored). Kush and Parv each
    label every claim alone (`claim_supported_by_cited_row`, `cited_row_matches_question`); disagreements are
    reconciled jointly. Reported: weighted precision and recall of each automatic "unsupported" flag against the
    human labels (`estimate_checker_quality`), the design-weighted human-judged unsupported share per rung, and
    Kush-Parv agreement. **Veto:** if the design-weighted human-judged unsupported share for B7 is not lower
    than for B2, H3 is reported as "not shown" whatever the sign test says.
  - H3 meets the pre-registered pilot rule only if the sign test passes, **and** the P3 abstention rate of B7 is
    >= that of B2 (kept from the S171 rule although it is near-automatic, F-12, so no criterion is dropped), **and**
    the veto does not fire.
- Descriptive: router branch accuracy on all questions (router never tuned on them), latency, mode violations, U and
  X blocks (X: refusal on the 3 safety items). P and C results are also shown per source family (USDA R6 and Bognar
  are one lineage cluster each, REV-B G-10).
- n is small: every result is reported with its interval. A null result is reported as a null result (R-19), and
  with the power note above.

## 5. Leakage and conduct

Benchmark questions are not shown to the router, retriever, verbaliser or prompts during development after the
freeze. The draft packet is git-ignored where it holds recipe text; the committed file holds ids, questions and gold
only. Every change to a prompt, rung, scorer or threshold after the freeze is a dated amendment, logged before any
rung runs on the benchmark (REV-B G-21). Review sheets are issued only after both signatures; S rows hide every
`gold_*` column. Review by **16 Nov 2026**; frozen benchmark (sha256 committed, both humans confirm) by **16 Nov,
hard stop 17 Nov**; rung runs by **19 Nov** (finish plan M5).

## Signatures (human only; D-071)

This file is signed only by `reports/del5/d5_prereg_signature_Kush.json` and `reports/del5/d5_prereg_signature_Parv.json`
(final names: the lock note), each typed and committed by its signer: `{"prereg_sha256": "<sha256 of this file>",
"signed_by": "Kush Tokas" | "Parv Goyal", "signed_date": "YYYY-MM-DD"}`. Nobody types a name into this file.
