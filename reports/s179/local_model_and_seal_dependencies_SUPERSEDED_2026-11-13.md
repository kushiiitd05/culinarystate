# Dependency record supersession — 13 November 2026

AI_DELEGATED_D085 · NOT_INDEPENDENT · NOT_HUMAN_VERIFIED_UNTIL_REVIEW · NO_HUMAN_SIGNOFF_D085. AI_VERDICT_PENDING_HUMAN_REVIEW.

The original `local_model_and_seal_dependencies_2026-11-13.json` is retained unchanged. It describes searches on Parv's Mac only. It was insufficient as a project-wide availability statement: Kush's artifacts were on his Mac/server, outside that search. They have not been transferred to Parv's checkout; do not rerun a local seal or substitute model files and do not request the seed/sealed list.

Kush's handoff and committed results now provide these narrower, reviewable outcomes:

| Dependency | Upstream verification/result | What is and is not established |
|---|---|---|
| Frozen NER checkpoint `ckpt_tasteset_base_crf_s1.pt`, SHA256 prefix582c056ac20625ac | `reports/s179/ner_vs_runga_agreement_S179_2026-11-13.json` | Bound frozen spans compared with lexicon on available channels. Method agreement, not human-labelled NER accuracy; GUT input empty. No local model receipt/inference claimed. |
| Original15a seed/sealed list | `reports/s179/seal_integrity_check_S179_2026-11-13.json`; `registry/split_registry_15a_v1.csv`; `reports/s179/15a_assignment_registry_2026-11-13.json` | Upstream6/6 checks PASS,177 reserved/709 dev groups. Counts/hash-only record; seed and sealed list stay private. No local rederivation claimed. |
| Accepted P1 annotator-A packets | `reports/s179/d097_runga_type_table_2026-11-13.json` | D-097 explicitly declares structural Rung A→Gold map before scoring; seven P1A and two20-recipe dev sets scored by count match. Not aligned event semantics/state accuracy or independent Gold. Original unmapped diagnostic remains historically valid for its earlier contract. |
| Frozen7b model | `handoff/BRIEF_2026-11-13_KUSH_TO_PARV.md` | Available upstream per Kush. Model regeneration/ablations remain his lane; presence does not imply those tasks have finished. No substitution with local3b. |
| Matched diagnostics vs D0 | `reports/step29/diag/paired_vs_d0_S179_2026-11-13.json` | Upstream diagnostic contrasts now available; Phenol-Explorer negative outcomes retained. PRIOR_EXPOSURE_REANALYSIS, not a new held-out D2/H2 result. |

D-097a records Kush's acceptance of K13-1..4 as AI results; Parv review remains pending. Original scientific failures, non-independence labels and zero eligible SIM-VAL are unchanged. This supersedes the dependency list, not the scientific guards. Content hashes are bound in the new scope matrix and transfer receipt manifest.
