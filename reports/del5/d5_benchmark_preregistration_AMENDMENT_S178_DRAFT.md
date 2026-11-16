# D5 / H1 / H3 pre-registration: pre-signature amendment draft (S178)

Status: **AI_DRAFTED / PROPOSED. Not a decision, not a signature, not an approval (D-071).** Written 2026-11-09 by the
S178 PREREG lane (an AI agent) for the 9-10 Nov decision sitting: ops pack items **#4** (T8-C06-R2), **#5**
(T8-C12-R1), **#6** (T9-C12-R1 + T8-C04-R2), **A1** (REV-B G-05..G-08, G-12, G-13) and the C07 VPN-fallback
sentence (T9-C26-R5). Nothing here edits `reports/del5/d5_benchmark_preregistration_DRAFT.md`; the Mac scribe applies
the chosen options there after the sitting.

> **Revision S178-FIX-EVAL (2026-11-09; AI_DRAFTED; wording only, no number and no option changed).** SCI-B E7
> (`reports/orchestration/review/S178_REV_SCI-B.md`): the C5 power sentence put an n = 30 range over discordance
> 0.3-0.5 next to an n = 60 range over 0.2-0.5. C5 and the §3 "smallest true gap" line now state the discordance range
> of each MDE range and the grid step. Power is monotone in the gap at fixed n and discordance, so the first grid gap
> reaching 80 % is the MDE (`evaluation/mcnemar_power.py`; the S178 EVAL text calling it a "conservative reading of a
> sawtooth in delta" was wrong; the discrete sawtooth is in the number of discordant pairs).

- Base text amended: `reports/del5/d5_benchmark_preregistration_DRAFT.md`, sha256
  `53ad89b7c13db57800e4546efb2ccfe29cdb2ef617b49c462c8b78f51415aa6b` (server worktree, 2026-11-09). Stop if the Mac
  copy differs.
- Drafts today (committed, ids and gold only): `benchmark/d5/d5_draft_S_v1.csv` 40 rows (S1 20, S2 20; 38
  Gutenberg, 2 Wikibooks; 40 distinct recipes), `benchmark/d5/d5_draft_PC_v1.csv` 60 rows (P1, P2, P3, C 15 each).
  U and X blocks: no drafts. No reviewer has opened a sheet (no signature exists).
- Power numbers: exact, computed with the project's `paired_stats.mcnemar_exact` and `scipy.stats.binom`
  (`reports/orchestration/S178_PREREG_calc/power_s178.py`, output `power_s178.json`); they reproduce REV-B Q26 (0.71 / 0.91 / 0.97 at gap 0.30).

## 0. What the sitting must decide

| Id | Question | Options here | Type | Pack rec. |
|---|---|---|---|---|
| D-D5-1 | S pool size (A1) | **S30** 15 + 15 · **S60** 30 + 30 | choice | S60 if both confirm >= 18 h free 9-16 Nov, else S30 |
| D-D5-2 | Whose answer is the S gold (H1 circularity) | **G-A** reconciled blind human answers · **G-B** engine gold reviewed after a blind pass | choice | G-A |
| D-D5-3 | What B4 is shown for S1 | **K1** full engine state block · **K2** state block without "Heated so far" | choice | K1 (with G-A) |
| D-D5-4 | B1/B2 embedding (#4) | **E5** e5-large-v2 · **BGE** a named bge model | choice | E5 |
| D-D5-5 | H3 decision test | **H3-A** sign test on an independent scorer + human audit veto · **H3-B** sign test, audit descriptive · **H3-C** draft bootstrap kept | choice | H3-A |
| D-D5-6 | Sign-test sidedness | **one-sided** alpha 0.05 (>= 5-0) · **two-sided** (>= 6-0) | choice | one-sided (direction pre-registered) |
| D-D5-7 | VPN fallback (C07) | **F1** fallback = H1 and H3 NOT_RUN, deterministic outputs only · **F2** same model digest on the Mac | choice | F1 (F2 if the Mac can run it) |
| D-D5-8 | H3/B7 wording (#5) | "rule-based evidence-sufficiency abstention (uncalibrated)" | choice | adopt |

## 1. Why this is not a post-hoc weakening

No rung has been run on any D5 benchmark question; the benchmark does not exist yet; no sheet has been opened. Every
change below makes a test harder to pass or more honest about what it measures: blind gold removes the engine's
answer from the gold; the retrieval cut removes future-step leakage; the independent scorer and the human audit
remove "UCR(B7) = 0 by construction"; the power note turns a likely null into "cannot show at this n" instead of
"no effect". The silver ladder (`reports/del5/ladder_*`) stays out of the benchmark as before.

## 2. Changes (old text -> new text)

### C1. Header (L3-L5)

```diff
-Status: **DRAFT_PENDING_SIGNATURES** (Kush, Parv). Written S171, 2026-11-08, by the coding agent (D-075 M5), before any
-benchmark question exists and before any rung is run on one. The 20-question silver ladder (`reports/del5/ladder_*`) was
-written by an AI and seen during development: it is **not** part of this benchmark and is not reused.
+Status: **DRAFT_PENDING_SIGNATURES** (Kush, Parv). Written S171, 2026-11-08, by the coding agent (D-075 M5), before any
+benchmark question exists and before any rung is run on one; amended before any signature with the S178 options the
+9-10 Nov sitting chose (`reports/del5/d5_benchmark_preregistration_AMENDMENT_S178_DRAFT.md`). Until both humans sign
+it is a dated AI draft. The 20-question silver ladder (`reports/del5/ladder_*`) was written by an AI and seen during
+development: it is **not** part of this benchmark and is not reused. Label on every output and slide:
+`MODEL_ASSISTED_GOLD, PILOT, authors-as-reviewers`.
```

### C2. §1 Composition (L9-L26)

```diff
-| S1 current state | 15 | current-state tracking | H1 |
-| S2 next action | 15 | next action | H1 |
+| S1 current state | 15 [S30] / 30 [S60] | current-state tracking | H1 |
+| S2 next action | 15 [S30] / 30 [S60] | next action | H1 |
@@
-| X controls (out of scope, multimodal, empty or vague) | 5 | router controls | descriptive |
+| X controls: 3 food-safety questions (gold REFUSE) + 2 out of scope, empty or vague | 5 | router controls | descriptive |
```
```diff
-- **S blocks:** recipes sampled by sha256(`d5-bench-2026-11-08` ‖ recipe_id) from **Wikibooks and Gutenberg only**
-  (lawful to send to the server LLM; D-003 keeps BBC text off the server), ≥ 4 steps, with a cut point after a
-  seeded step. Questions are asked at the cut; gold comes from the current engine's replay, **then reviewed and
-  corrected by the humans** (§3).
+- **S blocks:** recipes sampled by sha256(`d5-bench-2026-11-08` ‖ recipe_id) from **Wikibooks and Gutenberg only**
+  (lawful to send to the server LLM; D-003 keeps BBC text off the server), ≥ 4 steps, with a cut point after a
+  seeded step (`d5_state.seeded_cut`). **One question per recipe.** Eligibility does not depend on any engine
+  output: the S171 drafting rule that kept an S1 recipe only when the engine found a heated ingredient
+  (`tools/d5_draft_s.py` L66-L67) is dropped, so "none" is a possible S1 answer. S recipes are excluded from every
+  Rung A, lexicon or prompt tuning pool, checked by recipe_id against the D-073/D-074 samples and the P1 packets
+  (T9-C09-R2). Gold is written by the humans blind (§3); the engine's replay is a draft and a comparison only.
```

### C3. §2 Rungs (L30-L33)

```diff
-B0 LLM only · B1 dense RAG (bge embeddings over EVD texts) · B2 BM25 + dense hybrid · B4 state-aware (B2 + the
-replayed recipe state at the cut) · B5 B4 + evidence packet · B7 B5 + decision layer with post-hoc enforcement
-(B5F+E) · B5T template (no LLM). LLM: qwen2.5:7b-instruct on vinayak-server via SSH tunnel (one model fixed now).
-B3 and B6 are not built and are reported as NOT_RUN.
+B0 LLM only · B1 dense RAG · B2 BM25 + dense hybrid (reciprocal-rank fusion, k = 60) · B4 state-aware (B2 + the
+replayed recipe state at the cut) · B5 B4 + evidence packet · B7 B5 + decision layer with post-hoc enforcement
+(B5F+E), described everywhere as **"rule-based evidence-sufficiency abstention (uncalibrated)"**; no calibration
+claim is made · B5T template (no LLM). B3 and B6 are not built and are reported as NOT_RUN.
+- **Retrieval cut:** for S questions, B1, B2 and B4 retrieve only from steps 1..cut (`steps[:cut]`;
+  `h1_rungs.context(..., pre_cut_only=True)`); no step after the cut is in any rung's context. Before scoring,
+  `h1_independence.assert_independent` is run on every (question, rung) context and any failure is reported.
+- **Embedding [E5]:** `intfloat/e5-large-v2`, Hugging Face revision `<commit hash, filled from the local cache before
+  the lock; the lock may not be issued with this blank>`, mean pooling, prefixes `query: ` / `passage: ` (as
+  `tools/embed_texts.py`). Evidence: `reports/del4/retrieval_silver_v2_analysis.md` (silver, dev only, EVD text; not
+  measured on recipe-step chunks). [BGE: `BAAI/<model name>`, revision `<hash>`, CLS pooling, no prefix.] No change
+  after signing.
+- **B4 state block [K1]:** "Ingredients used", "Heated so far", "Last action" from `h1_rungs.state_block` on
+  steps[:cut] (`state_view="ANSWER"`). With blind human gold (G-A) this block is the treatment H1 tests, not the
+  gold. [K2: `state_view="PRIMITIVES"` — ingredients used, the ordered engine events with their bound ingredients,
+  last action, and no aggregate "Heated so far" line, so B4 must infer the heated set. The events are still engine
+  output; how far they determine the S1 answer is reported with `h1_independence.heated_from_primitives`.]
+- **LLM, fixed now:** qwen2.5:7b-instruct, Ollama model digest `<sha256, filled before the lock>`, temperature 0,
+  seed `<integer, fixed before the lock>`, `num_predict` `<integer>`; the prompt templates are hashed in the lock
+  record (REV-B G-21). Any later change to model, prompt or `num_predict` is a dated amendment before any rung runs.
+- **If vinayak is unreachable by 17 Nov (C07) [F1]:** B0, B1, B2, B4, B5 and B7 all need the LLM, so H1 and H3 are
+  reported **NOT_RUN**. What still runs on manjot CPU: B5T, the retrieval-only metrics of B1/B2 (T8-C06-R1) and
+  router branch accuracy (T8-C01-R1), all descriptive. [F2: the same model digest, temperature, seed and prompts
+  run on the Mac; the run log records the host; results are labelled with the host.]
```
Note for the sitting: the consensus wording of C07 ("run deterministic rungs B0/B1/B2/B4/B5T on manjot CPU")
treats B0-B4 as deterministic, but each of them is an LLM answer over a context (`h1_rungs.prompt`). Only B5T and
the retrieval rankings are deterministic. F1 states that plainly.

### C4. §3 Gold (L37-L40): blind-first S gold (H1 circularity fix)

```diff
-The agent drafts every question and gold answer. Kush and Parv each review all 80 independently (keep, edit or
-drop, with a reason), then reconcile. A question enters the benchmark only if both keep it, or keep it after the
-same edit.
+The agent drafts every question, and every P/C gold answer. **S gold is written by the humans, blind:** for each S
+question each reviewer first writes an answer from the recipe text alone (steps 1..cut for S1; the text of step
+cut+1 for S2), on a sheet where every `gold_*` column and every engine output is hidden, and the sheet records
+`seen_system_output = false` per row (Step 36 G36-B). Only then does the reviewer see the engine draft, and may
+only KEEP or DROP the *question* (well formed, cut sensible), never edit an answer toward it.
+[G-A] The S gold is the two blind answers where they agree; where they differ, the two reconcile from the recipe
+text; an S question with no agreed answer is dropped and the next by rank enters. The engine draft never becomes
+gold. Kush-Parv agreement on blind answers is reported (AC1 and raw agreement, with n).
+[G-B] The S gold is the engine draft after both reviewers KEEP or EDIT it having first answered blind; the report
+states that the gold was seen by reviewers who had seen engine output, and H1 on S is labelled ENGINE_ANCHORED.
+Every S row carries its gold origin (`h1_independence.GOLD_ORIGINS`: HUMAN_BLIND, HUMAN_AFTER_SEEING_ENGINE,
+ENGINE_DRAFT); H1 is labelled INDEPENDENT_GOLD only on HUMAN_BLIND rows (`gold_independence_report`).
+P and C rows are reviewed as before (keep, edit or drop, with a reason); a question enters only if both keep it, or
+keep it after the same edit.
```
And in the same paragraph (L39), the S overdraft follows the pool size:
```diff
-The S blocks are overdrafted the same way (20 per block, 15 enter).
+The S blocks are overdrafted the same way (20 per block, 15 enter [S30] | 40 per block, 30 enter [S60]).
```

**What the S gold must not share with the B4 context (the circularity rule, all options):**

1. **No shared generator.** The gold is not computed by `d5_state.heated_ingredient_ids`, `d5_state.next_action`
   or any Rung A graph; B4's state block is computed by exactly those (`h1_rungs.state_block`, `d5_state.graph`).
2. **No selection on engine output.** Which recipes and cuts become S questions does not depend on what the engine
   found (C2 above).
3. **No shared linker in the gold.** The gold is a set of ingredient names as written in the recipe (S1) or a verb
   plus a process chosen by the reviewer from the PROC list (S2), not ids produced by the engine's linker.
4. **No future text.** S1 gold uses steps 1..cut only; no rung sees steps after the cut (C3).
5. **No anchoring.** The reviewer writes the gold before seeing any engine output (`seen_system_output = false`).

### C5. §4 H1 (L44-L47): power note, scoring fix

```diff
-- **H1** (S1 + S2, n ≤ 30): exact-match accuracy against gold (entity set for S1, next process for S2), B4 vs B1
-  and B4 vs B2, paired by question. Test: exact two-sided McNemar on the discordant pairs, α = 0.05; report the
-  difference with a 95 % Newcombe interval. H1 is **supported** only if B4 > B1 **and** B4 > B2, both significant;
-  otherwise "not supported at this n" (no other claim).
+- **H1** (S1 + S2 pooled, n = 30 [S30] | 60 [S60]): exact-match accuracy against the blind human gold (ingredient
+  set for S1, next process for S2), B4 vs B1 and B4 vs B2, paired by question. Test: exact two-sided McNemar on the
+  discordant pairs (`paired_stats.mcnemar_exact`), α = 0.05; the 95 % Newcombe interval is descriptive, and the
+  decision is the exact test even when the interval excludes 0. H1 meets the pre-registered pilot rule only if
+  B4 > B1 **and** B4 > B2, both significant (intersection-union, no alpha correction); otherwise "not shown at this
+  n" (no other claim). Per-block (S1 or S2 alone) results are descriptive only.
+- **Scoring:** answers are linked to ING / PROC ids with the same linker for every rung; an answer item the linker
+  cannot resolve goes to a rung-blind human check (rung hidden) before unblinding, and the per-rung unresolved rate
+  is reported (REV-B F-13: B4's own surface strings always resolve).
+- **Power (fixed now, T9-C12-R1):** at n = 30 only accuracy gaps of about 0.25 or more can reach significance with
+  useful probability (80 % power needs a true gap of 0.28-0.36 at discordance 0.3-0.5, and no gap reaches 80 % at
+  discordance 0.2); the smallest significant split is 6-0 (gap 0.20). At n = 60, over the same discordance 0.3-0.5,
+  80 % power needs a gap of 0.20-0.26 (0.16 at discordance 0.2). A null result is uninformative, not
+  evidence of no effect. If the realised number of discordant pairs is below 6, the report says "cannot be
+  significant at this n".
+- **Circularity (T8-C04-R2):** S gold is human-written blind [G-A]; the engine-vs-blind-gold agreement on S is
+  reported as its own figure (a D3 datapoint, n stated). [G-B: H1 on S measures agreement with engine-anchored
+  gold and is reported as exactly that.]
```

### C6. §4 H3 (L48-L52): non-tautological scoring design

```diff
-- **H3** (P1–P3 + C, n ≤ 40): unsupported-claim rate (UCR) per rung, from the C17 checker (a numeric claim is
-  unsupported if uncited, cited to a non-evidence id, or its value lies outside the cited rows), plus the abstention
-  rate on P3 (gold ABSTAIN). H3 is **supported** only if UCR(B7) < UCR(B2) by an exact one-sided test on claims
-  clustered by question (question-level bootstrap, 10,000 resamples, seed `d5-h3`; the 95 % upper bound of the
-  difference < 0), **and** the P3 abstention rate of B7 ≥ that of B2.
```
**OPTION H3-A (recommended)**
```diff
+- **H3** (P1–P3 + C, n = 40): B7 is "rule-based evidence-sufficiency abstention (uncalibrated)".
+  - **Why the S171 rule is replaced:** B7's text is produced by `generation/enforce.enforce`, which deletes every
+    sentence that `generation/claims.check_claims` (claims@0.2) flags; scoring B7 with the same checker gives
+    UCR(B7) = 0 by construction (0.0 in both smoke ladders, as for the template B5T). And gold ABSTAIN on P3 means
+    "the ledger is silent", while B7's route is the same ledger lookup, so B7's P3 abstention is guaranteed (F-12).
+  - **Independent scorer:** claims are scored by `evaluation/h3_independent` (version string and code sha256 frozen
+    with the benchmark, before any rung runs), which shares no code with `generation/claims` or
+    `generation/enforce`, extracts numeric and directional claims itself, binds each number to its own citation
+    group, looks the cited ids up in the EVD ledger, and counts a claim as supported only if the value is within
+    0.03 (fraction scale, `VALUE_TOL`) of the cited row **and** the row's ingredient, process and target match the
+    question (REV-B G-12): `min_relevance` = EXACT for P1 and C questions, SIMILAR (parent or aggregate row) for P2
+    questions, whose gold is similar-only by design. claims@0.2 UCR is still printed, labelled "enforcement
+    checker, not independent".
+  - **Decision test:** an exact sign test (`h3_independent.compare_rungs`, `sign_test_exact`) over questions where
+    exactly one of B2 and B7 has at least one unsupported claim (independent scorer); B7 better needs p <= 0.05,
+    i.e. at least 5 of 5, 6 of 6, 7 of 7 or 7 of 8, 8 of 9, 9 of 10 [one-sided, `alternative="greater"`] | 6 of 6,
+    7 of 7, 8 of 8, 8 of 9, 9 of 10 [two-sided]. Fewer than 5 [one-sided] or 6 [two-sided] such questions: "cannot
+    be shown at this n". The question-level bootstrap (10,000 resamples, seed `d5-h3`) is a descriptive interval
+    only. B5T is compared with B7 by the same test (descriptive).
+  - **Coverage, reported beside every UCR (not gating; `h3_independent.summarize_rung`):** coverage on answerable
+    questions (P1, P2, C), false abstention, selective risk (questions with a claim that carry an unsupported one,
+    with a Clopper-Pearson interval), abstention on ABSTAIN gold, numeric claims made on ABSTAIN gold; plus the
+    template-fallback rate and sentences removed by `enforce`. A rung can lower UCR by saying less; these show
+    whether it did.
+  - **P3:** abstention rates are reported per rung, descriptive, with the note that B7 and B5T abstain on P3 by
+    construction.
+  - **Human claim audit (T8-C16-R1, REV-B G-08):** a rung-blind sample drawn by
+    `claim_audit.stratified_audit_sample` (seed `d5-h3-audit`, rungs B2, B7, B5T, `per_rung` = 10 [30 claims, the
+    consensus size] | 20 [60 claims]); strata = independent-scorer verdict x enforcement-checker flag, disagreement
+    strata first, every stratum's population and sample size recorded. Sheets hide rung, question id and every
+    automatic verdict; they hold answer text, so they live under `data/derived/` (git-ignored). Kush and Parv each
+    label every claim alone (`claim_supported_by_cited_row`, `cited_row_matches_question`); disagreements are
+    reconciled jointly. Reported: weighted precision and recall of each automatic "unsupported" flag against the
+    human labels (`estimate_checker_quality`), the design-weighted human-judged unsupported share per rung, and
+    Kush-Parv agreement. **Veto [H3-A]:** if the design-weighted human-judged unsupported share for B7 is not lower
+    than for B2, H3 is reported as "not shown" whatever the sign test says.
+  - H3 meets the pre-registered pilot rule only if the sign test passes, **and** the P3 abstention rate of B7 is
+    >= that of B2 (kept from the S171 rule although it is near-automatic, F-12, so no criterion is dropped), **and**
+    the veto does not fire.
```
**OPTION H3-B:** as H3-A without the veto (the audit is descriptive only).
**OPTION H3-C:** keep the S171 bootstrap rule. Then the report must say "UCR(B7) = 0 by construction; H3 as
registered cannot fail whenever B2 has 3 or more questions with an unsupported claim" (REV-B Q26/G-07). Not
recommended.

### C7. §4 Descriptive (L53-L55)

```diff
-- Descriptive: router branch accuracy on all 80 (router never tuned on them), latency, mode violations, U and X
-  blocks.
-- n is small: every result is reported with its interval. A null result is reported as a null result (R-19).
+- Descriptive: router branch accuracy on all questions (router never tuned on them), latency, mode violations, U and
+  X blocks (X: refusal on the 3 safety items). P and C results are also shown per source family (USDA R6 and Bognar
+  are one lineage cluster each, REV-B G-10).
+- n is small: every result is reported with its interval. A null result is reported as a null result (R-19), and
+  with the power note above.
```

### C8. §5 Leakage and conduct (L59-L61): forking-path log

```diff
 freeze. The draft packet is git-ignored where it holds recipe text; the committed file holds ids, questions and gold
-only. Review by **16 Nov 2026**; frozen benchmark and rung runs by **19 Nov** (finish plan M5).
+only. Every change to a prompt, rung, scorer or threshold after the freeze is a dated amendment, logged before any
+rung runs on the benchmark (REV-B G-21). Review sheets are issued only after both signatures; S rows hide every
+`gold_*` column. Review by **16 Nov 2026**; frozen benchmark (sha256 committed, both humans confirm) by **16 Nov,
+hard stop 17 Nov**; rung runs by **19 Nov** (finish plan M5).
```

### C9. Signatures (L63-L66)

```diff
-- Kush Tokas: ______ date ______
-- Parv Goyal: ______ date ______
+This file is signed only by `reports/del5/d5_prereg_signature_Kush.json` and `reports/del5/d5_prereg_signature_Parv.json`
+(final names: the lock note), each typed and committed by its signer: `{"prereg_sha256": "<sha256 of this file>",
+"signed_by": "Kush Tokas" | "Parv Goyal", "signed_date": "YYYY-MM-DD"}`. Nobody types a name into this file.
```

## 3. Power and MDE tables (exact; T9-C12-R1 asks for "minimum detectable discordance")

**Minimum discordant split for two-sided exact McNemar p <= 0.05** (b = B4 only right, c = other rung only right).
The split depends only on d; the accuracy gap is (b − c)/n.

| d (discordant pairs) | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 14 | 16 | 18 | 20 | 24 | 30 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| minimum split b-c | none | 6-0 | 7-0 | 8-0 | 8-1 | 9-1 | 10-1 | 10-2 | 12-2 | 13-3 | 14-4 | 15-5 | 18-6 | 21-9 |
| exact p | | 0.031 | 0.016 | 0.008 | 0.039 | 0.021 | 0.012 | 0.039 | 0.013 | 0.021 | 0.031 | 0.041 | 0.023 | 0.043 |
| gap at n = 30 | | 0.200 | 0.233 | 0.267 | 0.233 | 0.267 | 0.300 | 0.267 | 0.333 | 0.333 | 0.333 | 0.333 | 0.400 | 0.400 |
| gap at n = 60 | | 0.100 | 0.117 | 0.133 | 0.117 | 0.133 | 0.150 | 0.133 | 0.167 | 0.167 | 0.167 | 0.167 | 0.200 | 0.200 |

At n = 60 further rows: d 40 -> 27-13 (gap 0.233), d 50 -> 33-17 (0.267), d 60 -> 39-21 (0.300). The smallest
significant gap is 6-0 at any n (0.200 at n = 30, 0.100 at n = 60). With 5 or fewer discordant pairs nothing can be
significant. (Correction to the ops pack #6 text, which says the smallest results at n = 30 are "8-0, 9-1, 10-2 ...
a gap of 0.23 to 0.27": 6-0 and 7-0 also reach p <= 0.05.)

**Exact power** (two-sided alpha 0.05, correct direction). Model: each question is discordant with probability psi;
a discordant question favours B4 with probability pi = (1 + gap/psi)/2. "-" = impossible (gap > psi).

| true gap | psi 0.20 n30 / n60 | psi 0.30 n30 / n60 | psi 0.40 n30 / n60 | psi 0.50 n30 / n60 |
|---|---|---|---|---|
| 0.10 | 0.099 / 0.308 | 0.091 / 0.221 | 0.080 / 0.169 | 0.075 / 0.142 |
| 0.15 | 0.265 / 0.705 | 0.208 / 0.495 | 0.167 / 0.372 | 0.147 / 0.303 |
| 0.20 | 0.572 / 0.988 | 0.403 / 0.797 | 0.307 / 0.635 | 0.258 / 0.525 |
| 0.25 | - | 0.666 / 0.968 | 0.498 / 0.859 | 0.409 / 0.749 |
| 0.30 | - | 0.923 / 1.000 | 0.713 / 0.972 | 0.586 / 0.907 |
| 0.35 | - | - | 0.898 / 0.999 | 0.761 / 0.980 |
| 0.40 | - | - | 0.994 / 1.000 | 0.900 / 0.998 |

**Smallest true gap with 80 % power** (first gap on a 0.001 grid reaching 80 %; power is monotone in the gap):
n = 30: none at psi 0.20 (max power 0.57), 0.275 (psi 0.30), 0.322 (0.40), 0.363 (0.50). n = 60: 0.163 (psi 0.20),
0.201 (0.30), 0.235 (0.40), 0.264 (0.50). Compare n only over the same psi: over psi 0.30-0.50, n = 30 needs
0.275-0.363 and n = 60 needs 0.201-0.264. REV-B scenarios reproduced: gap 0.30 / psi 0.40 -> 0.713, 0.908,
0.972 at n = 30, 45, 60; gap 0.20 / psi 0.30 -> 0.403, 0.637, 0.797.

**H1 needs both comparisons (B4 > B1 and B4 > B2).** If each has power p, the joint power lies between max(0, 2p − 1)
and p (independence gives p²). Example gap 0.30, psi 0.40: n = 30 p = 0.713 -> joint 0.43-0.71 (0.51 if
independent); n = 60 p = 0.972 -> 0.94-0.97.

**H3 sign test, n = 40 questions.** r = share of questions where only B2 has an unsupported claim, s = share where
only B7 has one. Power (one-sided / two-sided):

| r | s = 0 | s = 0.025 | s = 0.05 |
|---|---|---|---|
| 0.05 | 0.048 / 0.014 | 0.020 / 0.006 | 0.008 / 0.002 |
| 0.10 | 0.371 / 0.206 | 0.182 / 0.097 | 0.088 / 0.045 |
| 0.15 | 0.737 / 0.567 | 0.447 / 0.318 | 0.262 / 0.172 |
| 0.20 | 0.924 / 0.839 | 0.689 / 0.570 | 0.485 / 0.364 |
| 0.30 | 0.997 / 0.991 | 0.941 / 0.891 | 0.839 / 0.741 |

On the 20-question silver ladder B2 had an unsupported claim in about 2 of 20 answers (qwen2.5:7b) and 1 of 20
(32b), i.e. r of about 0.05-0.10. At that rate the H3 test will most likely end "cannot be shown at this n"; that is
stated now so it is not read as evidence against H3.

**Human claim audit, scale of what 10 claims can show** (two-sided 95 % Clopper-Pearson interval for x
unsupported of 10, before design weights): 0 -> (0, 0.31); 1 -> (0.003, 0.45); 2 -> (0.025, 0.56); 3 -> (0.067,
0.65); 5 -> (0.19, 0.81). At 10 claims per rung the audit can show a gross failure of the scorer, not a small
difference between rungs; 20 per rung narrows each interval by roughly a third.

## 4. Code needed so every statistic is computable

Status on 2026-11-09: a parallel S178 lane on this worktree is writing the H1/H3 independence code (uncommitted,
DRAFT; **this lane did not review or run it**, so "exists" below means "file present", not "tested"). Whatever is
locked must name the version strings and code sha256 that are actually frozen.

| Item | Where | State | Option |
|---|---|---|---|
| Retrieval cut, state views | `evaluation/h1_rungs.py` `context(pre_cut_only=..., state_view=...)`, `independent_context` | present (uncommitted diff; defaults keep the S173 behaviour, so the runner must pass the arguments) | all, K1/K2 |
| Gold provenance and context-leak test | `evaluation/h1_independence.py` (`gold_origin`, `assert_independent`, `heated_from_primitives`, `gold_agreement`) | present (new file) | all |
| Independent scorer, sign test, coverage | `evaluation/h3_independent.py` (`score_answer`, `compare_rungs`, `sign_test_exact`, `summarize_rung`, `clopper_pearson`) | present (new file) | H3-A, H3-B |
| Claim-audit sample and estimates | `evaluation/claim_audit.py` | present (new file) | H3-A, H3-B |
| Per-question `min_relevance` (EXACT for P1/C, SIMILAR for P2) | caller of `h3_independent.score_answer` | to write | H3-A, H3-B |
| S drafting | `tools/d5_draft_s.py` L66-L67: drop the `if heated:` eligibility filter; overdraft 20 or 40 per block; new draft file (v2) | to write | all |
| Blind sheet | review-sheet builder: hide `gold_*` for S rows, add blind-answer and `seen_system_output` columns | to write | G-A, G-B |
| Unresolved-link queue | `h1_rungs.score_s1/score_s2` return UNRESOLVED instead of False when `link` returns None | to write | all |
| Test that pins the old behaviour | `tests/unit/test_s173_h1_rungs.py` passes the full recipe with `cut=2` | update | all |
| X safety items, U items | drafting (agent), reviewed by both | to write | all |

## 5. Hash after lock

```bash
git show <LOCK>:reports/del5/d5_benchmark_preregistration_DRAFT.md | sha256sum     # macOS: | shasum -a 256
sha256sum reports/del5/d5_benchmark_preregistration_DRAFT.md                       # must match
git diff --exit-code <LOCK> -- reports/del5/d5_benchmark_preregistration_DRAFT.md  # must print nothing
sha256sum reports/del5/d5_benchmark_preregistration_AMENDMENT_S178_DRAFT.md        # provenance, for the lock record
```
The lock record also carries the sha256 of the re-issued review sheets, the S and P/C draft files, the prompt
templates, the embedding revision and the Ollama digest. Each signer checks the prereg hash against the lock record
before typing a signature file; any mismatch: stop.

Sources: ops pack #4, #5, #6, A1, §3.2, §4.4; consensus §4 (T8-C04-R2, T8-C06-R2, T8-C12-R1, T9-C12-R1, T9-C26-R5,
C07); REV-B Q25, Q26, F-12, F-13, G-05..G-08, G-10, G-12, G-13, G-21; `h1_rungs.py`, `d5_state.py`, `paired_stats.py`,
`generation/claims.py`, `generation/enforce.py`, `tools/d5_draft_s.py`, `reports/del5/ladder_v2_*.md`.
