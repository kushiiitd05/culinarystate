# Non-blocking documentation backlog

Items here never interrupt the current execution step. Add, do not reorder, without a scope-change decision.

| Item | Added | Source of request | Notes |
|---|---|---|---|
| `reports/ner/ner_program_closeout.md` -- NER programme closeout (sections A-N: frozen v1 architecture, final TEST, H6-C, promoted/rejected/inconclusive components, V2-LINK result, DISTILL-A, CSD-C, external-validation limitation, claims we may / must not make, remaining items, why further NER tuning is unjustified) | 2026-10-22 (ES-1.2) | user instruction: add to the non-blocking backlog, do not write during ES-1.2 | synthesis only; no model reruns |

## Added during Step 07H (2026-10-22, per Kush's question)
- Read-only closed-world inventory of unique raw terms across ALL ledgers (PROC / SVAR / MEAS / EVD names, quantity forms, process names) vs. what the normaliser/registries recognise. No web access. Run after the 07 human gate.
- USDA abbreviation expansions (CKD, BKD, BLD, DRND, BKD/SIMMRD, `+`): targeted lookup in authoritative USDA documentation = H2 approval item (verification, not scraping). Until then they stay UNVERIFIED.
- No scraping/acquisition for new terms before Step 08+ approval.
