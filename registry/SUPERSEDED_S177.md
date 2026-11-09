# What the S177 consolidation superseded (marker note)

Status: **AI_DRAFTED / PROPOSED** (S178 FIX-GOV, 2026-11-09, review finding GOV-6). This note is not a decision. The consolidation review is `reports/orchestration/S177_CONSOLIDATION_composition_vs_lotstate.md`; its proposals sit under D-079, which is **PROPOSED, not adopted**. The machine-readable list is `registry/superseded_outputs_S176.csv`, and live tools refuse its paths through `culinarystate.governance_superseded`.

## Code

| item | state | replaced by / note |
|---|---|---|
| `src/culinarystate/lotstate/` (the S176 L-LOT and L-PH lanes) | SUPERSEDED, kept with its tests | `src/culinarystate/composition/` (Mac, canonical). Marker: `src/culinarystate/lotstate/SUPERSEDED.md`. No new features may be built on it. Known bug B1: `lotstate/ph.py` drops the EXACT crosswalk rows. |

## Outputs (all rows are in `registry/superseded_outputs_S176.csv`)

| file | registry status | why |
|---|---|---|
| `reports/lotstate/lotstate_census_1000_S176_ph_provisional.json` | INVALID_SUPERSEDED_KEPT_ON_RECORD | the only lotstate census built with the pH registry (`ph_registry` PRESENT_PROVISIONAL); its pH flags are INVALID (B1: `BAND_RANK` lacks EXACT, so 147 EXACT rank-1 rows are dropped) |
| `reports/lotstate/lotstate_census_1000_S176.json` | SUPERSEDED_KEPT_ON_RECORD | lotstate superseded by composition/; holds no pH data (`ph_registry` ABSENT). Its old reason "pH flags invalid" named the wrong file and was corrected |
| `reports/lotstate/lotstate_census_600_WB_TS_S176.json` | SUPERSEDED_KEPT_ON_RECORD | the same; no pH data |
| `reports/lotstate/ing_sr_match_summary_S176.json` | SUPERSEDED_KEPT_ON_RECORD | a summary of the legacy matcher; canonical ING-to-SR identity is `registry/ing_sr_defaults_v1.csv` |

Canonical census numbers: `reports/s175/*` (BBC, Mac) and `reports/s177/*_manjot.json` (non-BBC, re-run after the fixes).

## Registries

| file | state | note |
|---|---|---|
| `registry/ing_sr_defaults_v1.csv` (490 curated terms) | canonical ING-to-SR identity | AGENT_PROPOSED / UNVERIFIED (human verification sheet, Q44) |
| `registry/ing_sr_legacy_match_draft_v1.csv` | RETAINED, non-canonical | alternates and fallback only; never enough for ABSENT |
| `registry/ing_sr_legacy_verification_queue_v1.csv` | SUPERSEDED (consolidation 5.1) | to be replaced by a sheet over the 490 canonical rows. Not registered as superseded: it is a review sheet, not a census output |
| `registry/food_ph_fda_ing_crosswalk_draft_v1.csv` | DRAFT review sheet | nothing consumes it; only EXACT and FULL rows, and only after a human check |
| `registry/lotstate_aw_constants_draft_v1.csv` | kept as a SOURCE_UNVERIFIED placeholder | nothing consumes it (SSOT 285.7) |
| FDA pH: `registry/food_ph_fda2003_v1.csv` (479 rows) vs `registry/food_ph_fda_draft_v1.csv` (488 rows) | **open**: proposed swap, not done | see below. The 2003 file is **not** registered as superseded, because `composition/food_ph.py` and `tools/s175_line_mass_census.py` still read it |

## FDA pH: 479 vs 488 (both counts are right for their own file)

- **479** = `registry/food_ph_fda2003_v1.csv`, Mac commit `03c8709`. It was built by `tools/build_food_ph_registry.py` from the FDA/CFSAN "Approximate pH of Foods and Food Products" page (Oct 2003 version, webharvest capture of 2004-10-31). Value types: INTERVAL 345, POINT 115, LOWER_BOUND_ONLY 17, UNPARSED 2. This is the file the canonical `composition/` layer reads today, and STATUS's "FDA pH registry of 479 items" means this file.
- **488** = `registry/food_ph_fda_draft_v1.csv`, server S175 lane L-PH. It was built by `tools/build_food_ph_fda_draft.py` from the April 2007 revision of the same page (Wayback capture of 2008-02-23), and keeps every table row: 480 rows with a printed pH plus 8 without one (5 group headers: Apples, Bran, Junket type Dessert:, Rice (all cooked), Soup; and 3 bare rows: Dungeness Crab Meat, Gherkin, Salsa). Parse status: PARSED 461, PARSED_OPEN_ENDED 17, PARSED_REPAIRED_WS 1, UNPARSED_REVIEW 1, NO_PH_PRINTED_GROUP_HEADER 5, NO_PH_PRINTED 3. It also has the parent context for indented rows.
- **Reconciliation:** 488 − 8 (no pH printed) − 1 = 479. The one extra row is "Pork & Beans, rts." (pH 5.70). The Mac parser drops it because its HTML row has a third, empty cell (consolidation bug A1). After whitespace normalisation, every item name in the 479-row file is also in the 488-row file. The only value difference is Tamarind: lower bound 6.00 in the 2003 file and 3.00 in the 2007 file (both checked in the CSVs; the consolidation review dates FDA's correction to the March 2005 capture).
- The consolidation (section 5.1) proposes the 488-row file as canonical, with port P5 on the Mac. Until D-079 is decided and the Mac ports it, the live file is the 479-row one. The sentence in `src/culinarystate/lotstate/SUPERSEDED.md` that calls the 488-row file "the FDA pH registry chosen as canonical" states the proposal, not the current state.
