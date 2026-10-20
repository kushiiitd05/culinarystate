# Food.com evidence-first Gold — AI-assisted human review (S117)

**Provenance:** AI_ASSISTED_HUMAN_REVIEWED. NOT independent annotation.
- Proposals: AI reviewer, Pass 1 (partly schema-mechanical; cross-step lineage, alternatives, reserve/remainder, malformed steps, omitted ingredients, implicit intermediates not deeply audited).
- Review: Kush stated in chat "reviewed it all, all good", accepting the proposals on Parv's rubric plus his own analysis. Batch-level approval; `Kush_Rem` / `Parv_Rem` / `Final_Decision` are empty in all 402 rows (225 ingredient, 157 step, 20 recipe-check). Parv's approval is relayed by Kush.
- Kush and Parv sets are identical (same proposal) -> agreement is trivially 1.0 and **non-informative**; do not report as IAA.
- The frozen blank independent bundles (`Kush_all_20.json`, `Parv_all_20.json`, `freeze_hashes.json`) are untouched.

**Conversion:** `tools/convert_foodcom_sheet.py` (reuses `convert_ai_review.py` rules) -> `annotation/gold/foodcom_ai_assisted/{Kush,Parv}/` (local only, recipe text), log `conversion_log.csv`.
- 40/40 files validate + replay clean (status DONE); 20 recipes, 281 events written.
- **126 proposed events NOT written** (UNRESOLVED_REFERENCE: input not an ingredient or earlier output; worst FC100067 22, FC113219 13, FC438863 12). Cause: recipe-check notes say some ingredients are missing from the lists (e.g. beans in FC100067). These are Gold gaps, not verified absences.
- Other review-worthy: 46 multi-input Transform->Merge, 58 single-input Merge->Transform, 25 unresolved coref -> UNKNOWN, 4 operations unmapped, 1 unknown concept.

**Use:** development Gold for the evidence-first expansion. Not valid as independent held-out evaluation. Recommended Pass 2: audit the 126 dropped events and the 5 SPLIT_REVIEW rows before relying on lineage metrics.
