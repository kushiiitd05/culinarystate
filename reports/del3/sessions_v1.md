# DEL-3 scripted sessions v1

- sessions: 30
- invalid: {}
- passed: 30
- checks: 237
- deterministic_replay: True
- by_status: {'AI_DRAFTED': 30}
- by_scenario: {'MERGE': 2, 'RESERVE_RECOMBINE': 3, 'OBSERVATION_OVERRIDE': 4, 'SPLIT_PORTION': 4, 'SUBSTITUTION': 2, 'MISTAKE': 5, 'TRANSFER': 3, 'PARTIAL_USE': 2, 'MULTI_COMPONENT': 2, 'DISCARD': 3}
- contract_count_reviewed_and_passing: 0

Contract (≥ 30 reviewed): 0/30 — AI_DRAFTED sessions need human review (`provenance.status` = HUMAN_REVIEWED, `reviewed_by` = name) before they count.

| session | scenario | status | pass | checks | engine issues |
|---|---|---|---|---|---|
| SES-001 | MERGE | AI_DRAFTED | ✅ | 11 | 0 |
| SES-002 | RESERVE_RECOMBINE | AI_DRAFTED | ✅ | 11 | 0 |
| SES-003 | OBSERVATION_OVERRIDE | AI_DRAFTED | ✅ | 7 | 0 |
| SES-004 | SPLIT_PORTION | AI_DRAFTED | ✅ | 12 | 0 |
| SES-005 | SUBSTITUTION | AI_DRAFTED | ✅ | 8 | 0 |
| SES-006 | MISTAKE | AI_DRAFTED | ✅ | 7 | 0 |
| SES-007 | TRANSFER | AI_DRAFTED | ✅ | 6 | 0 |
| SES-008 | PARTIAL_USE | AI_DRAFTED | ✅ | 8 | 0 |
| SES-009 | SPLIT_PORTION | AI_DRAFTED | ✅ | 11 | 0 |
| SES-010 | MULTI_COMPONENT | AI_DRAFTED | ✅ | 11 | 0 |
| SES-011 | OBSERVATION_OVERRIDE | AI_DRAFTED | ✅ | 5 | 0 |
| SES-012 | MISTAKE | AI_DRAFTED | ✅ | 7 | 0 |
| SES-013 | RESERVE_RECOMBINE | AI_DRAFTED | ✅ | 7 | 0 |
| SES-014 | DISCARD | AI_DRAFTED | ✅ | 7 | 0 |
| SES-015 | TRANSFER | AI_DRAFTED | ✅ | 8 | 0 |
| SES-016 | SUBSTITUTION | AI_DRAFTED | ✅ | 7 | 0 |
| SES-017 | PARTIAL_USE | AI_DRAFTED | ✅ | 8 | 0 |
| SES-018 | MISTAKE | AI_DRAFTED | ✅ | 5 | 1 |
| SES-019 | OBSERVATION_OVERRIDE | AI_DRAFTED | ✅ | 6 | 0 |
| SES-020 | SPLIT_PORTION | AI_DRAFTED | ✅ | 9 | 0 |
| SES-021 | DISCARD | AI_DRAFTED | ✅ | 8 | 0 |
| SES-022 | TRANSFER | AI_DRAFTED | ✅ | 7 | 0 |
| SES-023 | MISTAKE | AI_DRAFTED | ✅ | 8 | 0 |
| SES-024 | MULTI_COMPONENT | AI_DRAFTED | ✅ | 12 | 0 |
| SES-025 | MERGE | AI_DRAFTED | ✅ | 7 | 0 |
| SES-026 | RESERVE_RECOMBINE | AI_DRAFTED | ✅ | 9 | 0 |
| SES-027 | OBSERVATION_OVERRIDE | AI_DRAFTED | ✅ | 6 | 0 |
| SES-028 | DISCARD | AI_DRAFTED | ✅ | 5 | 0 |
| SES-029 | SPLIT_PORTION | AI_DRAFTED | ✅ | 9 | 0 |
| SES-030 | MISTAKE | AI_DRAFTED | ✅ | 5 | 1 |
