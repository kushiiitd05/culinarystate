# D5 benchmark (~80 questions) and the H1 / H3 tests — pre-registration (DRAFT, UNSIGNED)

Status: **DRAFT_PENDING_SIGNATURES** (Kush, Parv). Written S171, 2026-11-08, by the coding agent (D-075 M5), before any
benchmark question exists and before any rung is run on one. The 20-question silver ladder (`reports/del5/ladder_*`) was
written by an AI and seen during development: it is **not** part of this benchmark and is not reused.

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
| X controls (out of scope, multimodal, empty or vague) | 5 | router controls | descriptive |

- **S blocks:** recipes sampled by sha256(`d5-bench-2026-11-08` ‖ recipe_id) from **Wikibooks and Gutenberg only**
  (lawful to send to the server LLM; D-003 keeps BBC text off the server), ≥ 4 steps, with a cut point after a
  seeded step. Questions are asked at the cut; gold comes from the current engine's replay, **then reviewed and
  corrected by the humans** (§3).
- **P/C blocks:** cells drawn by seed from the EVD index per stratum (DIRECT / similar-only / none), across ≥ 8
  ingredients and ≥ 4 processes. Gold mode is ANSWER, ANSWER_SIMILAR_ONLY, ABSTAIN or COMPARE, with the cited EVD
  ids that a correct answer may use.

## 2. Rungs (SSOT §245.12, as available; same questions, same LLM, temperature 0, fixed seed)

B0 LLM only · B1 dense RAG (bge embeddings over EVD texts) · B2 BM25 + dense hybrid · B4 state-aware (B2 + the
replayed recipe state at the cut) · B5 B4 + evidence packet · B7 B5 + decision layer with post-hoc enforcement
(B5F+E) · B5T template (no LLM). LLM: qwen2.5:7b-instruct on vinayak-server via SSH tunnel (one model fixed now).
B3 and B6 are not built and are reported as NOT_RUN.

## 3. Gold (model-assisted, stated as such)

The agent drafts every question and gold answer. Kush and Parv each review all 80 independently (keep, edit or
drop, with a reason), then reconcile. A question enters the benchmark only if both keep it, or keep it after the
same edit. The P and C blocks are overdrafted (15 per block, seeded rank order); the first 10 by rank that enter form the block, so drops do not shrink the block and reviewers cannot pick which ones replace them. Gold retention ranges are fractions (USDA % values ÷ 100). The benchmark is labelled **MODEL_ASSISTED_GOLD** (D-045), not independent human gold. It is frozen
(SHA-256 committed) before any rung is run on it. No question is changed after a rung is run.

## 4. Metrics and decision rules (fixed now)

- **H1** (S1 + S2, n ≤ 30): exact-match accuracy against gold (entity set for S1, next process for S2), B4 vs B1
  and B4 vs B2, paired by question. Test: exact two-sided McNemar on the discordant pairs, α = 0.05; report the
  difference with a 95 % Newcombe interval. H1 is **supported** only if B4 > B1 **and** B4 > B2, both significant;
  otherwise "not supported at this n" (no other claim).
- **H3** (P1–P3 + C, n ≤ 40): unsupported-claim rate (UCR) per rung, from the C17 checker (a numeric claim is
  unsupported if uncited, cited to a non-evidence id, or its value lies outside the cited rows), plus the abstention
  rate on P3 (gold ABSTAIN). H3 is **supported** only if UCR(B7) < UCR(B2) by an exact one-sided test on claims
  clustered by question (question-level bootstrap, 10,000 resamples, seed `d5-h3`; the 95 % upper bound of the
  difference < 0), **and** the P3 abstention rate of B7 ≥ that of B2.
- Descriptive: router branch accuracy on all 80 (router never tuned on them), latency, mode violations, U and X
  blocks.
- n is small: every result is reported with its interval. A null result is reported as a null result (R-19).

## 5. Leakage and conduct

Benchmark questions are not shown to the router, retriever, verbaliser or prompts during development after the
freeze. The draft packet is git-ignored where it holds recipe text; the committed file holds ids, questions and gold
only. Review by **16 Nov 2026**; frozen benchmark and rung runs by **19 Nov** (finish plan M5).

## Signatures (human only; D-071)

- Kush Tokas: ______ date ______
- Parv Goyal: ______ date ______
