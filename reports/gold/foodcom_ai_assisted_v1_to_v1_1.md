# Food.com Gold: S117 (v1) -> S118 (v1.1) repair

**Provenance v1.1: `AI_REAUTHORED_SOURCE_GROUNDED` + `HUMAN_REVIEW_PENDING`.** v1.1 events were re-authored by the AI (Claude) from the source steps. Kush's chat approval covered the v1 AI proposal (v1 = AI_ASSISTED_HUMAN_REVIEWED, batch-level), **not** v1.1. v1.1 is NOT human-verified, NOT independent, Kush and Parv files identical. It becomes AI_ASSISTED_HUMAN_REVIEWED only after Kush reviews it. S117 files are preserved unchanged (`annotation/gold/foodcom_ai_assisted/`). **Format: one joint file** `annotation/gold/foodcom_ai_assisted_v1_1/foodcom_v1_1_joint.json` (annotator `JOINT`, 20 recipes; Kush and Parv copies removed, since identical). Joint files are the convention from here on. Recipe text stays local; this report and `foodcom_dropped_event_audit_summary.csv` are text-free. Full audit (with step text): `reports/gold/foodcom_dropped_event_audit.csv` (git-ignored).

## What the audit found
- **Canonical count: 410 proposed, 126 initially dropped, 284 written/by-design** (the 407 in the master-prompt patch was wrong). S117 wrote 281 event objects; v1.1 has **310** final source-supported events.
- 62 dropped events are root rows (22 named root causes in 14 recipes, plus 21 that reference a "mixture of step N" no proposed event creates); the other 64 are cascades (BROKEN_LINEAGE) of those roots.
- **The 281 "survivors" were not trustworthy either.** The AI proposal contained wrong food inputs (e.g. "water" as the food in "soak in water" and "remove liver from water"), and output names built by mechanical concatenation ("remove water", "dried water"). So v1.1 re-authors every step of all 20 recipes rather than patching only the 126.
- Source-list omissions are widespread (unlisted foods named in steps: beans, lasagne sheets, cannelloni, stuffing, oil, salt/pepper, tomato soup, summer squash, yams, marmite ...). They become step-only entities with quantity UNKNOWN (`STEP_ONLY_ENTITY` note). Unlisted water/oil used purely as a medium is a `medium` field, not an entity.

## Outcome of the 126 dropped events
| outcome | n | meaning |
|---|---|---|
| RESTORED | 57 | v1.1 holds an event with the same canonical process in that step |
| SUPERSEDED | 36 | the AI-mechanical event is gone; the step is re-authored with source-supported events |
| REJECTED_BY_POLICY | 33 | medium-only water, serving suggestions, alternative-branch notes, vessel-heating with no tracked food |
| UNRESOLVED | 0 | |
Breakdown by repair class: `foodcom_dropped_event_audit_summary.csv`.

## v1.1 validity
| | S117 v1 | S118 v1.1 |
|---|---|---|
| events | 281 | 310 |
| files validate / replay clean / deterministic | 40/40 (20 recipes x 2) | 40/40 |
| step-only entities | 0 | see `STEP_ONLY_ENTITY` notes |
Recipes fully structurally clean (validate, replay, deterministic): **20/20**. Recipes still *semantically* uncertain (flagged in each file's `unknowns`): FC113219 ((A)/(B) groups undefined), FC438595 (stock/pan-juice composition), FC158166 (lasagne alternative not modelled), FC484761 (implicit Recombine of the lamb), FC458306 and FC175640 (reader-inferred list matches), FC464207 (marmite amount), FC100067 (bouillon cubes OR powder, wine timing alternative). Step spans (from the AI proposal) were NOT re-audited; some FOOD spans are wrong (e.g. FC464207 "water").

## H_STATE coverage, observed on repaired Gold (no 0.54 forecast multiplier used)
| | S114 pilot_20 | Food.com v1 (S117) | Food.com v1.1 (S118) |
|---|---|---|---|
| supported recipes | 8 | 8 | **15** |
| supported recipe-evidence pairs | 14 | 22 | **51** |
| unique ingredient x process cells | - | 20 | **37** |
| process families | - | 5 | 6 (DRY_HEAT, FAT_HEAT, HEAT_GENERAL, MECHANICAL_MIX, PRESERVATION, WET_HEAT) |
| evidence source families | - | 3 | 3 (BOGNAR-2002, PHENOL-EXPLORER-3.6, USDA-RETN-R6) |
| effective recipe clusters | - | 8 | 15 (each recipe its own family; no shared families) |
Detail: `reports/gold/foodcom_hstate_coverage.json`. v1 -> v1.1 more than doubles supported pairs because the dropped lineage had hidden the ingredient->process chain.

**Verdict: `H_STATE_COVERAGE_READY`** (structural coverage) but **`H_STATE_GOLD_PROVENANCE_GATE = NOT CLEARED`** until Kush reviews v1.1 and confirms the S116 eligibility screen. Coverage (51 supported pairs >= the 40-of-60 card target, 15 recipes, cap 6 per recipe). Conditions: (1) the v1.1 Gold is AI-authored and unverified by a human, so questions grounded in it inherit that caveat until Kush spot-checks; (2) Kush has not yet confirmed the AI eligibility screen (S116); (3) only 3 evidence source families, so source diversity is thin. No question authored, no B3/B4 run.
