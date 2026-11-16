# Negative results S171-S177: verification of every figure (S178, T9-C08-R4)

AI_DRAFTED / PROPOSED. Each row appended to `registry/negative_results_register_v1.csv` was rebuilt from the sources below; VERIFIED_COMPUTED = recomputed from a committed JSON/CSV/code; VERIFIED_TEXT_ONLY = found verbatim in committed prose, not machine-reproducible; UNVERIFIED = could not be checked; MISMATCH = stated figure differs from the recomputed one.

Check status counts: {'VERIFIED_COMPUTED': 74, 'VERIFIED_TEXT_ONLY': 9}.

| check | figure as stated | recomputed | status | source |
|---|---|---|---|---|
| R1.direct | DIRECT 274,058 | 274058 | VERIFIED_COMPUTED | `reports/step23/router_demo_census_vitc_full_corpus_S171.json` |
| R1.items | 36,359,902 route checks | 36359902 | VERIFIED_COMPUTED | `reports/step23/router_demo_census_vitc_full_corpus_S171.json` |
| R1.pct | 0.754 % | 0.754 % | VERIFIED_COMPUTED | `reports/step23/router_demo_census_vitc_full_corpus_S171.json` |
| R1.sum | DIRECT + UNKNOWN = items | 36359902 | VERIFIED_COMPUTED | `reports/step23/router_demo_census_vitc_full_corpus_S171.json` |
| R1.recipes | recipes 612,782 | 612782 | VERIFIED_COMPUTED | `reports/step23/router_demo_census_vitc_full_corpus_S171.json` |
| R1.preempt | EVIDENCE_PREEMPTS equals DIRECT | 274058 | VERIFIED_COMPUTED | `reports/step23/router_demo_census_vitc_full_corpus_S171.json` |
| R1.reasons | NO_FORM, PARAM_UNCONFIRMABLE, NO_CANDIDATE_MECHANISM on every check | (36359902, 36359902, 36359902) | VERIFIED_COMPUTED | `reports/step23/router_demo_census_vitc_full_corpus_S171.json` |
| R1.coverage | 103 of 130,886 pairs, 115 EVD pairs, 25 ingredients | (103, 130886, 115, 25) | VERIFIED_COMPUTED | `reports/step23/router_demo_census_vitc_full_corpus_S171.json` |
| R2.ungated | ungated DIRECT 267,933 | 267933 | VERIFIED_COMPUTED | `reports/step23/router_demo_census_vitc_nonBBC_full_S176.json` |
| R2.gated | gated DIRECT 34,537 | 34537 | VERIFIED_COMPUTED | `reports/step23/router_demo_census_vitc_nonBBC_full_S176.json` |
| R2.cross_sum | gated DIRECT = PRESENT/UNKNOWN x SINGLE_MEMBER | 34537 | VERIFIED_COMPUTED | `reports/step23/router_demo_census_vitc_nonBBC_full_S176.json` |
| R2.ungated_cross_sum | ungated DIRECT = sum of the cross | 267933 | VERIFIED_COMPUTED | `reports/step23/router_demo_census_vitc_nonBBC_full_S176.json` |
| R2.items | non-BBC items 35,256,601 | 35256601 | VERIFIED_COMPUTED | `reports/step23/router_demo_census_vitc_nonBBC_full_S176.json` |
| D74.correct | CORRECT 4 of 60 | (4, 60) | VERIFIED_COMPUTED | `reports/step17/d073_r1_precision_S170.json` |
| D74.wrong_object | WRONG_OBJECT 43 | 43 | VERIFIED_COMPUTED | `reports/step17/d073_r1_precision_S170.json` |
| D74.precision | precision 0.0667 | 0.0667 | VERIFIED_COMPUTED | `reports/step17/d073_r1_precision_S170.json` |
| D74.wilson_lower | Wilson 95 % lower 0.0262 | 0.0262 | VERIFIED_COMPUTED | `reports/step17/d073_r1_precision_S170.json` recomputed upper 0.1593 |
| D74.labels_sum | labels sum to 60 | 60 | VERIFIED_COMPUTED | `reports/step17/d073_r1_precision_S170.json` |
| D74.decision | D-074 text CORRECT 4, WRONG_OBJECT 43, NOT_AN_ACTION 8, UNCLEAR 3, NO_OBJECT 2 | CORRECT 4, WRONG_OBJECT 43, NOT_AN_ACTION 8, UNCLEAR 3, NO_OBJECT 2 | VERIFIED_TEXT_ONLY | `DECISIONS.md` |
| FU.unit_tokens | 0 unit tokens in 7,950 quantity strings | (0, 7950) | VERIFIED_COMPUTED | `reports/lotstate/foodcom_units_check_S176.json` |
| FU.letters | 0 quantity strings with an ASCII letter | 0 | VERIFIED_COMPUTED | `reports/lotstate/foodcom_units_check_S176.json` |
| FU.mass_lines | 0 stated masses in 1,445 paired lines | (0, 1445) | VERIFIED_COMPUTED | `reports/lotstate/foodcom_units_check_S176.json` |
| FU.bare | 1,378 bare numbers | 1378 | VERIFIED_COMPUTED | `reports/lotstate/foodcom_units_check_S176.json` |
| FU.full_lines | S177: 4,129,433 FOODCOM lines, 0 with grams | (4129433, 0) | VERIFIED_COMPUTED | `reports/s177/line_mass_census_FOODCOM_manjot.json` |
| FU.full_status | S177: all FOODCOM lines UNIT_MISSING_IN_SOURCE | 4129433 | VERIFIED_COMPUTED | `reports/s177/line_mass_census_FOODCOM_manjot.json` |
| FQ.full_recipes | Food.com recipes 522,517 | 522517 | VERIFIED_COMPUTED | `data/external/foodcom (parquet list lengths)` |
| FQ.sample_mis | 683 of 859 recipes (79.5 %) | (683, 859, '79.5 %') | VERIFIED_COMPUTED | `reports/lotstate/foodcom_units_check_S176.json` |
| FQ.sample_split | 645 longer, 38 shorter, 176 equal | (645, 38, 176) | VERIFIED_COMPUTED | `reports/lotstate/foodcom_units_check_S176.json` |
| FQ.code | iter_foodcom pads or truncates the quantity list by index | (q[i] if i < len(q) and q[i] else '') | VERIFIED_TEXT_ONLY | `src/culinarystate/recipes/corpus.py` |
| NER.fc | Food.com UNIT 171,812 vs QUANTITY 3,937,650 | (171812, 3937650) | VERIFIED_COMPUTED | `reports/ner_v2/ner_corpus_counts_S174.json` |
| NER.wb | Wikibooks UNIT 27,207 vs QUANTITY 33,091 | (27207, 33091) | VERIFIED_COMPUTED | `reports/ner_v2/ner_corpus_counts_S174.json` |
| NER.ts | TASTEset UNIT 3,184 vs QUANTITY 3,802 | (3184, 3802) | VERIFIED_COMPUTED | `reports/ner_v2/ner_corpus_counts_S174.json` |
| NER.fc_parts_units | S176: 304 of 6,682 Food.com parts hold a count/package unit token | (304, 6682) | VERIFIED_COMPUTED | `reports/lotstate/foodcom_units_check_S176.json` |
| SP.denominator | 4,281,956 corpus ingredient lines | 4281956 | VERIFIED_COMPUTED | `reports/s177/line_mass_census_*_manjot.json + reports/s175/line_mass_census_BBC.json` |
| SP.pct | 29.8 % | 29.8 % | VERIFIED_COMPUTED | `reports/step16/sp002_fix_design_ksh_S168.md` |
| SP.text | 1,275,782 of 4,281,956 corpus ingredient lines (29.8 %) | 1,275,782 of 4,281,956 | VERIFIED_TEXT_ONLY | `reports/step16/sp002_fix_design_ksh_S168.md` |
| SP.foodcom | Food.com 1,275,153 lines with U+2044 | 1275153 | VERIFIED_COMPUTED | `reports/s178/analysis/ing_alias_coverage_census_v1.json` |
| SP.tasteset | TASTEset 441 | 441 | VERIFIED_COMPUTED | `reports/s178/analysis/ing_alias_coverage_census_v1.json` |
| SP.wikibooks | Wikibooks 0 (S177: none) | 0 | VERIFIED_COMPUTED | `reports/s178/analysis/ing_alias_coverage_census_v1.json` |
| SP.sum_with_bbc_text | 1,275,153 + 441 + 0 + BBC 188 = 1,275,782 | 1275782 | VERIFIED_COMPUTED | `reports/s178/analysis/ing_alias_coverage_census_v1.json` BBC 188 is not recomputable on this server (D-003), taken from the S168 text |
| SP.unfixed | quantity/grammar.py does not handle U+2044 | False | VERIFIED_COMPUTED | `src/culinarystate/quantity/grammar.py` grep of the source for U+2044 handling |
| P1.verdict | HANDBOOK_REVISION_REQUIRED | HANDBOOK_REVISION_REQUIRED | VERIFIED_COMPUTED | `reports/step19/p1_agreement_counts_S166.json` |
| P1.pairs | 7 pairs | 7 | VERIFIED_COMPUTED | `reports/step19/p1_agreement_counts_S166.json` |
| P1.flagged | 5 of 9 categories above 0.20 | (5, 9) | VERIFIED_COMPUTED | `reports/step19/p1_agreement_counts_S166.json` |
| P1.rates | coref 0.9558, event_type 0.7629, final_state 0.8169, entity_type 0.2361, event_argument 0.2268 | (0.9558, 0.7629, 0.8169, 0.2361, 0.2268) | VERIFIED_COMPUTED | `reports/step19/p1_agreement_counts_S166.json` |
| P1.basis | label basis HUMAN_ACCEPTED_AI_DRAFTS_NOT_BLIND | HUMAN_ACCEPTED_AI_DRAFTS_NOT_BLIND | VERIFIED_COMPUTED | `reports/step19/p1_agreement_counts_S166.json` |
| P1.addendum | Addendum B names HANDBOOK_REVISION_REQUIRED | HANDBOOK_REVISION_REQUIRED | VERIFIED_TEXT_ONLY | `annotation/annotation_handbook_v1_addendum_B.md` |
| A4.kappa | pooled kappa 0.0 | 0.0 | VERIFIED_COMPUTED | `reports/step07/step07_v4_agreement_result_run2.json` |
| A4.raw | raw agreement 0.9944 | 0.9944 | VERIFIED_COMPUTED | `reports/step07/step07_v4_agreement_result_run2.json` |
| A4.cells | 5 disagreements in 900 cells | (5, 900) | VERIFIED_COMPUTED | `reports/step07/step07_v4_agreement_result_run2.json` |
| A4.fields | duration 4 + temperature_value 1 | (4, 1) | VERIFIED_COMPUTED | `reports/step07/step07_v4_agreement_result_run2.json` |
| A4.prevalence | 5 critical fields at dominant-code prevalence 1.00 | 5 | VERIFIED_COMPUTED | `reports/step07/step07_v4_agreement_result_run2.json` also non-critical at 1.00: medium_judgement, power_judgement |
| A4.gate | gate FAIL_OR_ADJUDICATE | FAIL_OR_ADJUDICATE | VERIFIED_COMPUTED | `reports/step07/step07_v4_agreement_result_run2.json` |
| A4.adj | adjudication: kappa stays 0.0; statistical gate NOT met | the statistical gate is NOT met | VERIFIED_TEXT_ONLY | `reports/step07/step07_v4_adjudication_result.md` |
| EV.denominator | 68,783 heat events with a computed core | 68783 | VERIFIED_COMPUTED | `reports/step26/scenario_L2_{FOODCOM,GUTENBERG_SEGMENT,WIKIBOOKS}_full_S176_v02.json` |
| EV.before | 47,198 cores above 100 C before the cap (68.6 %) | (47198, '68.6 %') | VERIFIED_COMPUTED | `same` bracket INTENSE; the text does not name the bracket, this is the one that matches |
| EV.after | 1,242 after the cap (1.8 %) | (1242, '1.8 %') | VERIFIED_COMPUTED | `same` |
| EV.all_dry | every remaining core above 100 C is a dry-class matrix | True | VERIFIED_COMPUTED | `reports/step26/scenario_L2_{FOODCOM,GUTENBERG_SEGMENT,WIKIBOOKS}_full_S176_v02.json` core_gt_100 equals core_gt_100_nonpressure_dry_class per bracket and family |
| EV.median | median core cook value 341 -> 9.2 equivalent minutes | (341, 9.2) | VERIFIED_COMPUTED | `reports/step26/scenario_L2_FOODCOM_full_S176_v02.json` |
| EV.p99 | p99 37,422 -> 116 | (37422, 116) | VERIFIED_COMPUTED | `reports/step26/scenario_L2_FOODCOM_full_S176_v02.json` |
| EV.superseded | evaporation-cap superseded files recorded in the registry | 11 | VERIFIED_COMPUTED | `registry/superseded_outputs_S176.csv` 12 rows in total (the others: pH) |
| SALT.points | 13,391 salt POINT values in the 1,000-recipe census | 13391 | VERIFIED_COMPUTED | `reports/lotstate/lotstate_census_1000_S176.json` |
| SALT.arith_wrong | salted butter: 10.3 g NaCl per g water (buggy formula) | 10.3 | VERIFIED_COMPUTED | `arithmetic on the review's inputs (Na 643 mg/100 g, water 15.9 g/100 g)` |
| SALT.arith_right | true value about 0.10 | 0.1 | VERIFIED_COMPUTED | `same` |
| SALT.review | FINAL-SCI review row 1: salt load 100x too high | The salt load is 100× too high | VERIFIED_TEXT_ONLY | `reports/orchestration/review/S176_FINAL_SCI_review.md` |
| SALT.fixed_lotstate | fixed in lotstate/composition.py (test at test_lotstate_composition.py:87) | FINAL-SCI #1 (100× error) **is fixed** | VERIFIED_TEXT_ONLY | `reports/orchestration/S177_CONSOLIDATION_composition_vs_lotstate.md` |
| PH.exact_rows | 147 EXACT rank-1 rows dropped | 147 | VERIFIED_COMPUTED | `registry/food_ph_fda_ing_crosswalk_draft_v1.csv` |
| PH.no_entry | 123 ING with an EXACT row get no by_ing entry | 123 | VERIFIED_COMPUTED | `same` 145 ING have an EXACT rank-1 row; 22 also have a HIGH rank-1 row (a processed form) |
| PH.band_rank | BAND_RANK has no EXACT key | True | VERIFIED_COMPUTED | `src/culinarystate/lotstate/ph.py` regex over the dict literal |
| PH.superseded | census registered as superseded: pH flags invalid (B1) | lotstate/ph.py drops EXACT crosswalk rows | VERIFIED_TEXT_ONLY | `registry/superseded_outputs_S176.csv` |
| SD.heat | 27 heat defaults, all SOURCE_UNVERIFIED_AGENT_RECALLED | (27, 27) | VERIFIED_COMPUTED | `registry/scenario_defaults_v1.csv` |
| SD.nonheat | 40 non-heat defaults, 38 unverified + 2 retired | (40, 38, 2) | VERIFIED_COMPUTED | `registry/scenario_defaults_nonheat_v1.csv` |
| SD.review | 97 reviewed rows: 58 opened by AI, 39 unverified candidates, 0 human-verified | (97, 58, 39, 97) | VERIFIED_COMPUTED | `registry/scenario_defaults_source_review_S176.csv` |
| SD.windows | 149 mechanism windows, all QUALITATIVE_ONLY | (149, 149) | VERIFIED_COMPUTED | `registry/mechanism_condition_windows_draft_v1.csv` |
| GR.bbc | BBC 75.3 % of lines with grams | 75.3 % | VERIFIED_COMPUTED | `reports/s175/line_mass_census_BBC.json` |
| GR.wb | Wikibooks 59.0 % | 59.0 % | VERIFIED_COMPUTED | `reports/s177/line_mass_census_WIKIBOOKS_manjot.json` |
| GR.ts | TASTEset 56.7 % | 56.7 % | VERIFIED_COMPUTED | `reports/s177/line_mass_census_TASTESET_manjot.json` |
| GR.gut | Gutenberg 0 lines | 0 | VERIFIED_COMPUTED | `reports/s177/line_mass_census_GUTENBERG_SEGMENT_manjot.json` |
| GR.recipes | recipes with every quantified line in grams: BBC 17.3 %, WB 10.0 %, TS 12.9 % | ('17.3 %', '10.0 %', '12.9 %') | VERIFIED_COMPUTED | `same files` |
| GR.unverified | grams resting on an unverified SR link: BBC 60.4 %, WB 78.1 %, TS 79.0 % | ('60.4 %', '78.1 %', '79.0 %') | VERIFIED_COMPUTED | `same files` |
| TL.all | 520 events with a stated liquid temperature above T_boil | 520 | VERIFIED_COMPUTED | `reports/step26/scenario_L2_{FOODCOM,GUTENBERG_SEGMENT,WIKIBOOKS}_full_S177_v03.json` |
| TL.above150 | 197 of them state more than 150 C (191 + 4 + 2) | 197 | VERIFIED_COMPUTED | `same` |
| TL.core204 | 7 FOODCOM events with a computed core in that bucket (core up to 204 C) | core up to 204 C | VERIFIED_TEXT_ONLY | `reports/orchestration/S177_SCIFIX-PHYS_report.md` |

## Register rows

| id | claim tested | status |
|---|---|---|
| NEG-0031 | The Step 23a router in demo mode, fed the E3 evidence ledger, returns an evidence-supported DIRECT route for a substantial share of recipe events (vitamin C, SVAR-000009) | RECORDED_AGENT_CHECKED |
| NEG-0032 | The S171 DIRECT count survives the target-presence and lot-context gates on the non-BBC families | RECORDED_AGENT_CHECKED |
| NEG-0033 | Implicit-object rule R1 (RA_IMPLICIT_CURRENT_V1: bind an action with no stated object to the current mixture when the tier is ambiguous) reaches the pre-registered landing precision and closes part of the ~7 % real binding gap | RECORDED_AGENT_CHECKED |
| NEG-0034 | Food.com ingredient quantities carry units, so line mass can be derived from Food.com lines (the largest family, 522,517 recipes) | RECORDED_AGENT_CHECKED |
| NEG-0035 | Food.com quantity and ingredient-part lists are index-aligned, so recipes.corpus.iter_foodcom pairs each quantity with its ingredient | RECORDED_AGENT_CHECKED_PARTIAL_TEXT_ONLY |
| NEG-0036 | The DeBERTa-CRF ingredient-line NER labels a UNIT wherever it labels a QUANTITY, on every family | RECORDED_AGENT_CHECKED |
| NEG-0037 | The legacy quantity parser (quantity/grammar.py normalize_text, used by rc2 and the line-mass census) reads the Unicode fractions in corpus ingredient lines | RECORDED_AGENT_CHECKED_PARTIAL_TEXT_ONLY |
| NEG-0038 | Annotation handbook v1 (with Addendum A) gives stable independent annotation: per-pair disagreement stays at or below 0.20 in every category | RECORDED_AGENT_CHECKED |
| NEG-0039 | 07.A condition-audit packet v4 passes the signed gate (pooled Cohen's kappa >= 0.80 and no systematic critical-field failure) | RECORDED_AGENT_CHECKED |
| NEG-0040 | Layer-2 scenario cores from the first heat/non-heat scenario runs (layer 0.1.0, no evaporation cap) are physically bounded | RECORDED_AGENT_CHECKED |
| NEG-0041 | The lot-state solute load 'salt_g_per_g_water' (g NaCl per g water) is computed correctly | RECORDED_AGENT_CHECKED_PARTIAL_TEXT_ONLY |
| NEG-0042 | Provisional lot pH flags (lotstate/ph.py over the FDA-2003 ING crosswalk draft) give raw-ingredient pH ranges | RECORDED_AGENT_CHECKED_PARTIAL_TEXT_ONLY |
| NEG-0043 | The Layer-2 scenario default constants (GENTLE/TYPICAL/INTENSE ranges) are sourced from the literature | RECORDED_AGENT_CHECKED |
| NEG-0044 | The BBC line-to-grams coverage (75.3 % of ingredient lines) carries over to the other corpora, so the composition layer scales to them | RECORDED_AGENT_CHECKED_PARTIAL_TEXT_ONLY |
| NEG-0045 | A temperature stated in the recipe sentence next to a water verb (boil, simmer) is the temperature of the liquid, so the evaporation cap can be lifted to it | RECORDED_AGENT_CHECKED_PARTIAL_TEXT_ONLY |

Append: {'appended': 0, 'prefix_intact': True}
