# `lotstate/` is SUPERSEDED (S177, 2026-11-09)

The consolidation review `reports/orchestration/S177_CONSOLIDATION_composition_vs_lotstate.md` chose the Mac's
`src/culinarystate/composition/` (curated `registry/ing_sr_defaults_v1.csv`, exact handling of unknown masses) as the
canonical lot-composition layer. This package is kept for the record and for its tests; do not build new features
on it. Known bug: `ph.py:36,80` drops EXACT crosswalk rows, so the provisional pH figures in
`reports/lotstate/lotstate_census_1000_S176.json` are INVALID (see `registry/superseded_outputs_S176.csv`).
Parts proposed for porting into `composition/` are listed in the review (§ port list); the Mac owns that work.
The FDA pH registry chosen as canonical is `registry/food_ph_fda_draft_v1.csv` (April 2007, 488 rows).
