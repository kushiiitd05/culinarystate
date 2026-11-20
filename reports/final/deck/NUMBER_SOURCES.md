# Deck numerical sources

This sheet applies to the 19-slide Keynote review export. Check it again after the live evidence and final deck are added. The report evidence review carries source hashes.

| Slide | Quantity or label | Source |
|---|---|---|
| 1 | Group 17; presentation dates | `docs/Group17_MDMA_Mini_Project_Proposal_Brief.pdf`; `handoff/PARV_LATEST_PROMPT_2026-11-19.md` |
| 3 | 522,517 Food.com; 11,934 BBC Good Food; 700 TASTEset; 3,676 Wikibooks; 73,955 Gutenberg; 612,782 total | `registry/recipe_source_usage_registry_v1.csv`; counted directly in the frozen recipe-base Parquet |
| 3 | 611,902 texts with steps; 612,903 index documents | `reports/step26/simulability_census_full_corpus_S166.json`; recipe-base count plus current Wikibooks substitution, documented in `reports/final/REPORT_EVIDENCE_REVIEW_2026-11-20.json` |
| 4, 18 | D1–D5 partial; 17,978 active evidence rows; zero human literature rows; 40 dev-gold recipes, 30 sessions; 74 D5 questions; H1/H3 rules not met | `reports/final/DELIVERABLE_COMPLIANCE_MATRIX_2026-11-16.md`; `reports/s181/human_audit/REPORT_WORDING.md`; `reports/del5/d5_score_v1_D085/d5_scoring_result.json` |
| 5–6 | Single licensed Layer-1 field and trigger; state fields | `DECISIONS.md` D-135/D-137; `docs/final/FINAL_STATE_SCHEMA.md` |
| 7 | 13 axes (9 implemented, 2 compiler-only, 2 schema-only) | `registry/rag/compatibility_axes_v1.csv` |
| 8 | A’s evidence report 95.0%, EVD-002765; B–D qualify and abstain by question and context | `web/public/snapshot/scenarios/tomato-{a,b,c,d}.json`; `reports/final/screens/runs/tomato-a-d.json` |
| 9 | Frozen plain-model check: unsourced 20–30% in 3/19; at least 4 cautious replies flagged | `reports/s181/snapshot_findings.md`, plain-model analysis |
| 10 | B7 4/34, B2 24/43; B7 partial AURC 0.0977 over 0.45–1.00; B2 recall 0.20/0.3417/0.375 over 20; ECE unavailable | `reports/s181/d4_contract_metrics.json`, use unrounded values |
| 11 | 60 sealed cases; 59 calls plus one repaired; 0 grounded proposals in the offset arms, 21 in the quote-first 72B arm | `reports/s180/step7_FINAL_COMPARISON_2026-11-16.md`; figure source in `reports/final/figures_s180_2026-11-16/MANIFEST.json` |
| 12 | 4.3–4.9 and 4.6 threshold; 479 source rows, 140 bands (31, 101, 8) | `reports/s179/state_inventory_FINAL_2026-11-15.md`; `docs/final/FINAL_COMPONENT_INVENTORY.md` |
| 13 | Grouped macro F1 0.9504 ± 0.0034 baseline and 0.9545 ± 0.0037 DeBERTa+CRF; 13.6% masked-family overlap and 5.4% duplicate test rows in standard protocol | `reports/ner/culinaryner_kf_final_report.md` §A |
| 14–16 | Retrieval and proposer model IDs; live model ID; screenshot and saved-run provenance | `tools/s179_d5_run_rungs.py`; `tools/s182_live_rag.py`; `reports/final/screens/MANIFEST.json` |

The review export has screenshot placeholders on slide 16. Slide 11 needs spacing between the chart labels and its caveat. Remove legacy comparison language and use the numeric sources above when preparing the delivery export.
