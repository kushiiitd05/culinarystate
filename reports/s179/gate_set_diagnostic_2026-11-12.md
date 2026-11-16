# Prehashed AI-labelled query-gate diagnostic — 12 November 2026

**AI_LABELLED_NOT_BLIND / DIAGNOSTIC / NON_CITABLE / NO_HUMAN_SIGNOFF_D085.**

T0-C07-R1 artifact: 100 annotated queries (95 newly authored semantic cases and the exact five frozen D5 X controls). Labels and producer bytes were hashed before predictions. No D5 item, rule, threshold, scorer or frozen result changed.

The label author knew the project/rules; prehashing protects against changing these labels after this run, not against prior knowledge or subjectivity. This is not independent human gold, natural-query prevalence or a scientific gate test.

Positive process label means causal/process-effect/diagnosis/recovery reasoning is needed. Static metadata/graph lookups, navigation, multimodal requests and food-safety referral are process-negative. The safety label is evaluated separately.

Only literal True activates the relevance gate. UNKNOWN is counted as no activation operationally and also reported separately; it is not silently removed from denominators.

| Predicate | TP / FN / FP / TN | Recall (Wilson 95%) | False-negative rate (Wilson 95%) | False-positive rate (Wilson 95%) | Precision (Wilson 95%) | UNKNOWN |
|---|---|---|---|---|---|---|
| process_relevance_gate | 15 / 25 / 7 / 53 | 15/40 = 0.3750 [0.2422, 0.5297] | 25/40 = 0.6250 [0.4703, 0.7578] | 7/60 = 0.1167 [0.0577, 0.2218] | 15/22 = 0.6818 [0.4732, 0.8364] | 64 (25 process-positive, 39 process-negative) |
| router_process_activation | 28 / 12 / 0 / 60 | 28/40 = 0.7000 [0.5457, 0.8193] | 12/40 = 0.3000 [0.1807, 0.4543] | 0/60 = 0.0000 [0.0000, 0.0602] | 28/28 = 1.0000 [0.8794, 1.0000] | 0 (0 process-positive, 0 process-negative) |
| safety_gate | 12 / 1 / 0 / 87 | 12/13 = 0.9231 [0.6669, 0.9863] | 1/13 = 0.0769 [0.0137, 0.3331] | 0/87 = 0.0000 [0.0000, 0.0423] | 12/12 = 1.0000 [0.7575, 1.0000] | 0 (0 process-positive, 0 process-negative) |

Branch-label agreement: 86/100 = 0.8600 [0.7786, 0.9147]. This is authored-case agreement, not 100-query independent accuracy.

## Findings and interpretation

The legacy process-relevance predicate misses many authored causal descriptions without its cue strings. Its operational false-negative count includes UNKNOWN on positive cases. It also activates on seven static graph-lookup substitution cases, even though the downstream query router can choose RELATIONSHIP. The router process-activation predicate therefore has a different operating point; its separate counts must not be substituted for relevance-gate counts.

The safety predicate misses one known frozen D5 X control. Its identifier is retained below and was not used to retune the frozen implementation. A missed safety cue does not authorize answering a safety question: the strict adapter is a separate engineering boundary and is not a scientifically evaluated safety product. Zero false positives among this authored negative set has a nonzero Wilson upper bound.

| Predicate | False-negative case IDs | False-positive case IDs |
|---|---|---|
| process_relevance_gate | GATE-AI-001, GATE-AI-002, GATE-AI-004, GATE-AI-005, GATE-AI-006, GATE-AI-007, GATE-AI-010, GATE-AI-011, GATE-AI-012, GATE-AI-014, GATE-AI-015, GATE-AI-016, GATE-AI-017, GATE-AI-018, GATE-AI-019, GATE-AI-020, GATE-AI-027, GATE-AI-028, GATE-AI-029, GATE-AI-030, GATE-AI-034, GATE-AI-036, GATE-AI-037, GATE-AI-038, GATE-AI-040 | GATE-AI-066, GATE-AI-067, GATE-AI-068, GATE-AI-070, GATE-AI-073, GATE-AI-074, GATE-AI-075 |
| router_process_activation | GATE-AI-015, GATE-AI-016, GATE-AI-018, GATE-AI-027, GATE-AI-028, GATE-AI-029, GATE-AI-030, GATE-AI-034, GATE-AI-036, GATE-AI-037, GATE-AI-038, GATE-AI-040 | none |
| safety_gate | D5-X-001 | none |

## Provenance and rerun

- Annotation file: `benchmark/diagnostic/gate_set_2026-11-12.csv` (AI-authored query text, no third-party recipe text).
- Before-prediction manifest: `reports/s179/gate_set_manifest_2026-11-12.json`; exact annotation/tool/gate/D5-control hashes.
- Result and per-case query hashes/predictions: `reports/s179/gate_set_diagnostic_2026-11-12.json`.
- Producer: `tools/s179_gate_set_diagnostic.py`; three TDD tests cover FP/FN/UNKNOWN accounting, Wilson zero denominator/boundary behavior and prehash tamper rejection.
- Actual run: 2026-11-12T14:16:40.933692+00:00 to 2026-11-12T14:16:40.942091+00:00.

Use a NEW output path for a rerun: `python tools/s179_gate_set_diagnostic.py --annotations benchmark/diagnostic/gate_set_2026-11-12.csv --manifest reports/s179/gate_set_manifest_2026-11-12.json --out <new-report.json>`. The producer rejects changed prehashed files and existing outputs.

Gate labels, known controls and confusion counts remain a reviewable engineering diagnostic. Their Wilson intervals condition on these deliberately authored categories and cannot establish population error, calibrated confidence, source entailment or a passed H1/H3/food-safety gate.
