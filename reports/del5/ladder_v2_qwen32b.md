# Ladder v2_qwen32b (qwen2.5:32b; 20 dev questions, AI-authored, silver)

| rung | numeric claims | unsupported (uncited / wrong value) | UCR | fabricated cites | `[n]` cites | mode violations | mean latency s |
|---|---|---|---|---|---|---|---|
| B0 | 1 | 1 (1 / 0) | 1.0 | 0 | 0 | 2 | 9.36 |
| B2 | 13 | 1 (0 / 1) | 0.077 | 0 | 0 | 3 | 3.99 |
| B5 | 22 | 2 (2 / 0) | 0.091 | 0 | 0 | 3 | 4.48 |
| B5F | 22 | 4 (4 / 0) | 0.182 | 0 | 0 | 2 | 3.36 |
| B5F+E | 18 | 0 (0 / 0) | 0.0 | 0 | 0 | 0 | 3.36 |
| B5T | 24 | 0 (0 / 0) | 0.0 | 0 | 0 | 0 | 0.0 |

B5F+E: fallback to template 4/20; sentences removed 14 (reasons: ['NON_EVIDENCE_CITATION', 'UNSUPPORTED_NUMBER']).
