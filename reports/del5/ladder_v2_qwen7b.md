# Ladder v2_qwen7b (qwen2.5:7b-instruct; 20 dev questions, AI-authored, silver)

| rung | numeric claims | unsupported (uncited / wrong value) | UCR | fabricated cites | `[n]` cites | mode violations | mean latency s |
|---|---|---|---|---|---|---|---|
| B0 | 1 | 1 (1 / 0) | 1.0 | 0 | 0 | 2 | 1.19 |
| B2 | 13 | 2 (0 / 2) | 0.154 | 3 | 0 | 4 | 1.48 |
| B5 | 24 | 1 (1 / 0) | 0.042 | 0 | 3 | 3 | 1.79 |
| B5F | 20 | 8 (7 / 1) | 0.4 | 0 | 0 | 2 | 1.34 |
| B5F+E | 16 | 0 (0 / 0) | 0.0 | 0 | 0 | 0 | 1.34 |
| B5T | 24 | 0 (0 / 0) | 0.0 | 0 | 0 | 0 | 0.0 |

B5F+E: fallback to template 4/20; sentences removed 16 (reasons: ['NON_EVIDENCE_CITATION', 'UNSUPPORTED_NUMBER']).
