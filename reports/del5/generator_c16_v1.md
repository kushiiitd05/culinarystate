# C16 grounded generator — ablation v1 (2026-10-18)

SSOT §257B.16: "verbalize; do not invent second analysis"; promotion only against the strongest simpler baseline.
20 AI-authored dev questions (8 demo + 12 across routes: direct/near answers, compare, recommend, diagnose, recover,
out-of-scope, OOD). Silver dev smoke; the locked benchmark (D-008, humans) is the evaluation. Ollama on A100 GPU 0
(private `ollama serve`, read-only shared model store; the shared system service was running on CPU), temperature 0,
seed 7, num_ctx 4096. Per-run tables: `ladder_v2_qwen7b.md`, `ladder_v2_qwen32b.md` (jsonl stores decisions,
packet row ids and answers for replay; `--rescore` re-scores without LLM calls).

| rung | qwen2.5-7B unsupported / claims | 7B mode violations | qwen2.5-32B unsupported / claims | 32B mode violations |
|---|---|---|---|---|
| B0 LLM only | 1 / 1 | 2 | 1 / 1 | 2 |
| B2 hybrid-RAG rows | 2 / 13 (+3 fabricated ids) | 4 | 1 / 13 | 3 |
| B5 rows + decision (v1 prompt) | 1 / 24 (+3 `[n]` cites) | 3 | 2 / 22 | 3 |
| B5F per-route fact prompt | 8 / 20 (7 uncited) | 2 | 4 / 22 (4 uncited) | 2 |
| **B5F+E** B5F + post-hoc enforcement | **0 / 16** | **0** | **0 / 18** | **0** |
| **B5T** deterministic template | **0 / 24** | **0** | (same) | **0** |

Mode violation = a number where the decision's precision cap forbids numbers, or an ASK without a question.

## Reading
- The v1 smoke (B5 UCR 0.71) was mostly checker error: multi-id brackets, bare "1" counted as a claim, citations
  placed after the full stop. Fixed (claims@0.2) with regression tests; v1 numbers are superseded.
- B5 (rows prompt) has few wrong values but ignores the precision cap: "≈80% thiamin" on a QUALITATIVE okra route,
  narrating cause numbers on RECOVER. Prompting alone does not enforce the decision.
- B5F's unsupported claims are almost all citation placement (ids pooled in a later sentence), not wrong values
  (7B: 1 wrong value; 32B: 0). Strict per-sentence attribution is kept on purpose.
- Enforcement (enforce@0.1) gets both models to 0 unsupported / 0 violations, at a cost: 4/20 answers fall back to
  the template and 6–8 of 24 template facts are dropped from the LLM wording.
- 32B vs 7B: fewer uncited claims, ~2.5× latency; no difference after enforcement.

## Decision (promotion rule)
- **B5T (template verbaliser) is the promoted C16 generator**: 0 unsupported, 0 violations, all facts, no GPU.
- B5F+E (LLM rephrase + enforcement) stays an optional surface layer, unpromoted: on these metrics it never beats
  the template; its only possible gain is readability, which needs human judgement (benchmark / user study).
- B5 rows prompt is retired as a generator; kept as a ladder rung.

## Fixes found by this run (all with tests)
- Miner v1.1: "separately", "if preferred", doneness signals, medical text; "unless"/"less liable" -> PREVENTION.
- Diagnosis: no session history -> UNVERIFIABLE (was INCONSISTENT).
- Relevance: jokes/poems/stories -> OUT_OF_SCOPE -> ABSTAIN (was ASK "which process?").
- Enforcer: malformed ids like `[EVD-1]` removed; an ASK that does not ask falls back to the template.
- Template: short food labels (no "such as …" group tails), short prevention statements, no censored limits as values.
