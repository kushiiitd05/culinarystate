# Gold-v1 -> v1.1: decisions applied, validation and final compiler rerun (S109)

**Gold-v1.1 created** (`annotation/gold/pilot_20_adjudicated_v1_1/`, manifest `gold_v1_1_pilot_manifest.csv`). Label: **AI-assisted, human-reviewed development Gold** (OpenAI GPT-5.6 Sol draft; corrections drafted by the coding agent; decisions by Kush after a review with ChatGPT). It is **not** independent Gold, not blind Gold, not a test set. Gold-v1 (`pilot_20_adjudicated`) is unchanged (hashes verified against the v1 manifest).

## Decisions (decision owner: Kush)
{'APPROVE': 76, 'MODIFY': 19, 'NOTED_NO_CHANGE': 1, '(info only)': 25}. 76 proposals APPROVED, 19 MODIFIED (Kush's modification rules; AI-written patches recorded in the queue with a rationale per row), GC-017 documented schema limitation (no Gold change), 25 audit flags information only. None rejected; none left in NEEDS_DISCUSSION. Rationales are in `annotation/gold/gold_v1_correction_queue.csv` (`decision_rationale`, local file with source text) and the ChatGPT recommendations file `gold_v1_1_AI_review_recommendations.csv`.
Notable modifications: separate pea and asparagus lineages with a 6 tbsp reserve from the peas only; two 1 tbsp oil uses and the chicken kept apart until returned; optional yogurt, peanuts, rice and hot sauce are not unconditional events; exact 5 tbsp cream allocation (5/6 + 1/6); lemon zest, juice and wedges kept distinct; tea-towel wrapping as a location; no invented excess-batter entity; dough outputs with null fractions (equality not explicit).

## Validation
- validate: **20/20**; replay with no issues: **20/20**; deterministic replay (identical graph hash twice): **20/20**.
- No converter-looking entity remains alive (no 'remainder', no 'or 10 dough portion N'); the one unrepresentable item (R009647, chilling a glass: a tool state) is a documented schema limitation.
- Gold-event replay scores 1.000 on every metric.
- Coreference: 78 of the 113 draft entries were removed as non-references; 28 genuine mentions stay `UNKNOWN` (ambiguous; documented, not errors).

## Final compiler rerun (the same compiler as S107/S108; `rule_compiler.py` unchanged; n=20; bootstrap CI over recipes)
| metric (raw text = P) | S107 | S108 provisional | **S109 final** | S109 O1 gold concepts | S109 O2 gold Adds | S109 G gold replay |
|---|---|---|---|---|---|---|
| state-field accuracy | 0.102 | 0.140 | **0.106** [0.04, 0.19] | 0.106 | 0.106 | 1.000 |
| alive-entity F1 | 0.312 | 0.395 | **0.294** [0.20, 0.39] | 0.308 | 0.294 | 1.000 |
| merge/split/reserve/recombine F1 | 0.343 | 0.368 | **0.351** [0.26, 0.45] | 0.339 | 0.351 | 1.000 |
| relation F1 | 0.289 | 0.327 | **0.324** [0.24, 0.41] | 0.310 | 0.324 | 1.000 |
| event F1 (loose) | 0.199 | 0.237 | **0.247** [0.17, 0.34] | 0.240 | 0.247 | 1.000 |
| event-type F1 | 0.582 | 0.629 | **0.626** [0.53, 0.72] | 0.613 | 0.626 | 1.000 |

Event counts, gold -> predicted: Merge 86 vs 60, Transform 97 vs 169, Split 21 vs 14, Transfer 22 vs 22, Discard 10 vs 10, Reserve 1 vs 8. Per-recipe scores: `compiler_vs_gold_s109_final.json`.

## What the three references say
- The conclusions are **stable across S107, S108-provisional and S109-final**: state-field accuracy 0.10-0.14, alive-entity F1 0.29-0.40, merge/split/reserve/recombine F1 0.34-0.38. Reference repair changes the numbers by a few hundredths, not the picture.
- Oracle ingredient identity (O1) and gold Add events (O2) give no gain (state-field accuracy 0.106 in all three); the bottleneck is step-event construction and state tracking.
- Over-produced: Transform (169 predicted vs 97) and Reserve (8 vs 1). Under-produced: Merge (60 vs 86) and Split (14 vs 21).
- 20 development recipes from one source: no generalisation claim.

## Oracle readiness
All gate conditions are met: 20/20 source-audited; all decided corrections applied; validate/replay 20/20 and deterministic; converter artefacts removed or documented; provenance stated honestly.
**GOLD_ORACLE_READY_FOR_H_STATE**
Caveats that travel with it: development reference only (AI-assisted, one human decision pass, audit read by one AI reader); coreference is mostly UNKNOWN; the oracle arm of EXP-000007 should be reported as 'AI-assisted human-reviewed Gold state', and any H_STATE claim needs a note that gold state quality was verified by review, not by independent annotation.
