# v03 -> v04 comparison, non-BBC physical layers (S178 PHYS2)

Status: DRAFT / AI_DRAFTED, counts only, read from the run reports named in `source_report_sha256`. The heat Layer 1 was not re-run in S177, so its baseline is the S176 v02 census (Layer 1 0.1.0). Layer 2 heat 0.3.0 -> 0.4.0, non-heat Layer 2 0.3.0 -> 0.4.0, non-heat Layer 1 0.1.0 -> 0.2.0.

## FOODCOM

| quantity | before | after | delta |
|---|---:|---:|---:|
| heat L1 heat_events | 1503261 | 1503261 | 0 |
| heat L1 driver_ready_events | 56214 | 55662 | -552 |
| heat L1 driver_bounded_events | 88113 | 87139 | -974 |
| heat L1 contract_bindings | 2102847 | 2102295 | -552 |
| heat L1 temperature basis CARRIED_SETPOINT | 69839 | 70835 | 996 |
| heat L1 temperature basis PHYSICAL_DEFINITION | 99495 | 99745 | 250 |
| heat L1 temperature basis TEXT_STATED | 55364 | 48952 | -6412 |
| heat L2 status SCENARIO_COMPUTED | 667634 | 667634 | 0 |
| heat L2 status SCENARIO_UNKNOWN | 768753 | 768753 | 0 |
| heat L2 status UNSUPPORTED_MEDIUM | 66874 | 66874 | 0 |
| heat L2 stated-liquid events lifted (TYPICAL) | 430 | 182 | -248 |
| heat L2 stated-liquid lifted, stated T 100_TO_105 | 21 | 16 | -5 |
| heat L2 stated-liquid lifted, stated T 105_TO_120 | 149 | 110 | -39 |
| heat L2 stated-liquid lifted, stated T 120_TO_150 | 69 | 36 | -33 |
| heat L2 stated-liquid lifted, stated T ABOVE_150 | 191 | 20 | -171 |
| heat L2 TYPICAL core reaches 70 C = False | 2678 | 2613 | -65 |
| heat L2 TYPICAL core reaches 70 C = True | 52468 | 52533 | 65 |
| heat L2 cap flag TBOIL_CAP_LOWER_ESTIMATE_SOLUTE_RICH_MEMBER (TYPICAL) | 6869 | 142918 | 136049 |
| heat L2 cap flag ALL_MEMBERS_DRY_CLASS (TYPICAL) | 0 | 2058 | 2058 |
| heat L2 cap flag MATRIX_UNKNOWN_MOIST_ASSUMED (TYPICAL) | 486525 | 201637 | -284888 |
| heat L2 cap flag MATRIX_AMBIGUOUS_MOIST_ASSUMED (TYPICAL) | 44407 | 68274 | 23867 |
| heat L2 cap flag MATRIX_DRY_CLASS_UNCAPPED (TYPICAL) | 27409 | 29467 | 2058 |
| non-heat L1 events COOLING | 297413 | 297413 | 0 |
| non-heat L1 events FERMENT_LEAVEN | 50942 | 50942 | 0 |
| non-heat L1 events MECHANICAL_CUT | 541273 | 541273 | 0 |
| non-heat L1 events MECHANICAL_MIX | 1447067 | 1447067 | 0 |
| non-heat L1 events PRESERVATION | 66675 | 66675 | 0 |
| non-heat L1 events RESTING | 14232 | 14232 | 0 |
| non-heat L1 events SEPARATION | 269657 | 269657 | 0 |
| non-heat L1 events STORAGE | 24170 | 24170 | 0 |
| non-heat L2 computed COOLING | 23606 | 23606 | 0 |
| non-heat L2 computed FERMENT_LEAVEN | 1966 | 1966 | 0 |
| non-heat L2 computed MECHANICAL_CUT | 234186 | 234186 | 0 |
| non-heat L2 computed MECHANICAL_MIX | 0 | 0 | 0 |
| non-heat L2 computed PRESERVATION | 79 | 79 | 0 |
| non-heat L2 computed RESTING | 552 | 552 | 0 |
| non-heat L2 computed SEPARATION | 113640 | 113640 | 0 |
| non-heat L2 computed STORAGE | 0 | 0 | 0 |

Heat L2 per-event comparison over 1503261 events: bath temperature changed (TYPICAL) 2948; core end temperature changed 238; non-heat events whose status changed 0.

## GUTENBERG_SEGMENT

| quantity | before | after | delta |
|---|---:|---:|---:|
| heat L1 heat_events | 182049 | 182049 | 0 |
| heat L1 driver_ready_events | 1719 | 1717 | -2 |
| heat L1 driver_bounded_events | 1985 | 1983 | -2 |
| heat L1 contract_bindings | 252046 | 252044 | -2 |
| heat L1 temperature basis CARRIED_SETPOINT | 49 | 50 | 1 |
| heat L1 temperature basis PHYSICAL_DEFINITION | 53841 | 53893 | 52 |
| heat L1 temperature basis TEXT_STATED | 1042 | 932 | -110 |
| heat L2 status SCENARIO_COMPUTED | 120951 | 120951 | 0 |
| heat L2 status SCENARIO_UNKNOWN | 56765 | 56765 | 0 |
| heat L2 status UNSUPPORTED_MEDIUM | 4333 | 4333 | 0 |
| heat L2 stated-liquid events lifted (TYPICAL) | 84 | 56 | -28 |
| heat L2 stated-liquid lifted, stated T 100_TO_105 | 5 | 4 | -1 |
| heat L2 stated-liquid lifted, stated T 105_TO_120 | 51 | 36 | -15 |
| heat L2 stated-liquid lifted, stated T 120_TO_150 | 24 | 15 | -9 |
| heat L2 stated-liquid lifted, stated T ABOVE_150 | 4 | 1 | -3 |
| heat L2 TYPICAL core reaches 70 C = False | 38 | 37 | -1 |
| heat L2 TYPICAL core reaches 70 C = True | 13148 | 13149 | 1 |
| heat L2 cap flag TBOIL_CAP_LOWER_ESTIMATE_SOLUTE_RICH_MEMBER (TYPICAL) | 2247 | 18661 | 16414 |
| heat L2 cap flag ALL_MEMBERS_DRY_CLASS (TYPICAL) | 0 | 249 | 249 |
| heat L2 cap flag MATRIX_UNKNOWN_MOIST_ASSUMED (TYPICAL) | 78058 | 45697 | -32361 |
| heat L2 cap flag MATRIX_AMBIGUOUS_MOIST_ASSUMED (TYPICAL) | 9872 | 12073 | 2201 |
| heat L2 cap flag MATRIX_DRY_CLASS_UNCAPPED (TYPICAL) | 8973 | 9222 | 249 |
| non-heat L1 events COOLING | 11785 | 11785 | 0 |
| non-heat L1 events FERMENT_LEAVEN | 7100 | 7100 | 0 |
| non-heat L1 events MECHANICAL_CUT | 110806 | 110806 | 0 |
| non-heat L1 events MECHANICAL_MIX | 96148 | 96148 | 0 |
| non-heat L1 events PRESERVATION | 14653 | 14653 | 0 |
| non-heat L1 events RESTING | 2525 | 2525 | 0 |
| non-heat L1 events SEPARATION | 53329 | 53329 | 0 |
| non-heat L1 events STORAGE | 1075 | 1075 | 0 |
| non-heat L2 computed COOLING | 1367 | 1367 | 0 |
| non-heat L2 computed FERMENT_LEAVEN | 383 | 383 | 0 |
| non-heat L2 computed MECHANICAL_CUT | 47825 | 47825 | 0 |
| non-heat L2 computed MECHANICAL_MIX | 0 | 0 | 0 |
| non-heat L2 computed PRESERVATION | 42 | 42 | 0 |
| non-heat L2 computed RESTING | 87 | 87 | 0 |
| non-heat L2 computed SEPARATION | 19603 | 19603 | 0 |
| non-heat L2 computed STORAGE | 0 | 0 | 0 |

Heat L2 per-event comparison over 182049 events: bath temperature changed (TYPICAL) 68; core end temperature changed 23; non-heat events whose status changed 0.

## WIKIBOOKS

| quantity | before | after | delta |
|---|---:|---:|---:|
| heat L1 heat_events | 11433 | 11433 | 0 |
| heat L1 driver_ready_events | 620 | 615 | -5 |
| heat L1 driver_bounded_events | 941 | 930 | -11 |
| heat L1 contract_bindings | 15130 | 15125 | -5 |
| heat L1 temperature basis CARRIED_SETPOINT | 492 | 496 | 4 |
| heat L1 temperature basis PHYSICAL_DEFINITION | 1155 | 1159 | 4 |
| heat L1 temperature basis TEXT_STATED | 728 | 634 | -94 |
| heat L2 status SCENARIO_COMPUTED | 4871 | 4871 | 0 |
| heat L2 status SCENARIO_UNKNOWN | 6154 | 6154 | 0 |
| heat L2 status UNSUPPORTED_MEDIUM | 408 | 408 | 0 |
| heat L2 stated-liquid events lifted (TYPICAL) | 6 | 3 | -3 |
| heat L2 stated-liquid lifted, stated T 100_TO_105 | 1 | 1 | 0 |
| heat L2 stated-liquid lifted, stated T 105_TO_120 | 2 | 2 | 0 |
| heat L2 stated-liquid lifted, stated T 120_TO_150 | 1 | 0 | -1 |
| heat L2 stated-liquid lifted, stated T ABOVE_150 | 2 | 0 | -2 |
| heat L2 TYPICAL core reaches 70 C = False | 14 | 14 | 0 |
| heat L2 TYPICAL core reaches 70 C = True | 437 | 437 | 0 |
| heat L2 cap flag TBOIL_CAP_LOWER_ESTIMATE_SOLUTE_RICH_MEMBER (TYPICAL) | 49 | 799 | 750 |
| heat L2 cap flag ALL_MEMBERS_DRY_CLASS (TYPICAL) | 0 | 17 | 17 |
| heat L2 cap flag MATRIX_UNKNOWN_MOIST_ASSUMED (TYPICAL) | 3413 | 1489 | -1924 |
| heat L2 cap flag MATRIX_AMBIGUOUS_MOIST_ASSUMED (TYPICAL) | 452 | 632 | 180 |
| heat L2 cap flag MATRIX_DRY_CLASS_UNCAPPED (TYPICAL) | 188 | 205 | 17 |
| non-heat L1 events COOLING | 1564 | 1564 | 0 |
| non-heat L1 events FERMENT_LEAVEN | 571 | 571 | 0 |
| non-heat L1 events MECHANICAL_CUT | 4125 | 4125 | 0 |
| non-heat L1 events MECHANICAL_MIX | 9459 | 9459 | 0 |
| non-heat L1 events PRESERVATION | 485 | 485 | 0 |
| non-heat L1 events RESTING | 141 | 141 | 0 |
| non-heat L1 events SEPARATION | 2403 | 2403 | 0 |
| non-heat L1 events STORAGE | 152 | 152 | 0 |
| non-heat L2 computed COOLING | 103 | 103 | 0 |
| non-heat L2 computed FERMENT_LEAVEN | 18 | 18 | 0 |
| non-heat L2 computed MECHANICAL_CUT | 1794 | 1794 | 0 |
| non-heat L2 computed MECHANICAL_MIX | 0 | 0 | 0 |
| non-heat L2 computed PRESERVATION | 1 | 1 | 0 |
| non-heat L2 computed RESTING | 3 | 3 | 0 |
| non-heat L2 computed SEPARATION | 997 | 997 | 0 |
| non-heat L2 computed STORAGE | 0 | 0 | 0 |

Heat L2 per-event comparison over 11433 events: bath temperature changed (TYPICAL) 29; core end temperature changed 2; non-heat events whose status changed 0.

## TASTESET

| quantity | before | after | delta |
|---|---:|---:|---:|
| heat L1 heat_events | 0 | 0 | 0 |
| heat L1 driver_ready_events | 0 | 0 | 0 |
| heat L1 driver_bounded_events | 0 | 0 | 0 |
| heat L1 contract_bindings | 0 | 0 | 0 |
| heat L2 stated-liquid events lifted (TYPICAL) | 0 | 0 | 0 |
| heat L2 stated-liquid lifted, stated T 100_TO_105 | 0 | 0 | 0 |
| heat L2 stated-liquid lifted, stated T 105_TO_120 | 0 | 0 | 0 |
| heat L2 stated-liquid lifted, stated T 120_TO_150 | 0 | 0 | 0 |
| heat L2 stated-liquid lifted, stated T ABOVE_150 | 0 | 0 | 0 |
| non-heat L1 events COOLING | 0 | 0 | 0 |
| non-heat L1 events FERMENT_LEAVEN | 0 | 0 | 0 |
| non-heat L1 events MECHANICAL_CUT | 0 | 0 | 0 |
| non-heat L1 events MECHANICAL_MIX | 0 | 0 | 0 |
| non-heat L1 events PRESERVATION | 0 | 0 | 0 |
| non-heat L1 events RESTING | 0 | 0 | 0 |
| non-heat L1 events SEPARATION | 0 | 0 | 0 |
| non-heat L1 events STORAGE | 0 | 0 | 0 |
| non-heat L2 computed COOLING | 0 | 0 | 0 |
| non-heat L2 computed FERMENT_LEAVEN | 0 | 0 | 0 |
| non-heat L2 computed MECHANICAL_CUT | 0 | 0 | 0 |
| non-heat L2 computed MECHANICAL_MIX | 0 | 0 | 0 |
| non-heat L2 computed PRESERVATION | 0 | 0 | 0 |
| non-heat L2 computed RESTING | 0 | 0 | 0 |
| non-heat L2 computed SEPARATION | 0 | 0 | 0 |
| non-heat L2 computed STORAGE | 0 | 0 | 0 |

Heat L2 per-event comparison over None events: bath temperature changed (TYPICAL) 0; core end temperature changed 0; non-heat events whose status changed 0.

## SUPERSEDED outputs

The v04 files replace these reports for the non-BBC families; the old files are kept for the audit trail and are not read by any v04 tool.

- `reports/step26/binding_census_L1_FOODCOM_full_S176_v02.json` (heat_l1)
- `reports/step26/binding_census_L1_GUTENBERG_SEGMENT_full_S176_v02.json` (heat_l1)
- `reports/step26/binding_census_L1_WIKIBOOKS_full_S176_v02.json` (heat_l1)
- `reports/step26/binding_census_L1_TASTESET_full_S176_v02.json` (heat_l1)
- `reports/step26/scenario_L2_FOODCOM_full_S177_v03.json` (heat_l2)
- `reports/step26/scenario_L2_GUTENBERG_SEGMENT_full_S177_v03.json` (heat_l2)
- `reports/step26/scenario_L2_WIKIBOOKS_full_S177_v03.json` (heat_l2)
- `reports/step26/scenario_L2_TASTESET_full_S177_v03.json` (heat_l2)
- `reports/step26/nonheat_L1_FOODCOM_full_S176.json` (nonheat_l1)
- `reports/step26/nonheat_L1_GUTENBERG_SEGMENT_full_S176.json` (nonheat_l1)
- `reports/step26/nonheat_L1_WIKIBOOKS_full_S176.json` (nonheat_l1)
- `reports/step26/nonheat_L1_TASTESET_full_S176.json` (nonheat_l1)
- `reports/step26/nonheat_L2_FOODCOM_full_S177_v03.json` (nonheat_l2)
- `reports/step26/nonheat_L2_GUTENBERG_SEGMENT_full_S177_v03.json` (nonheat_l2)
- `reports/step26/nonheat_L2_WIKIBOOKS_full_S177_v03.json` (nonheat_l2)
- `reports/step26/nonheat_L2_TASTESET_full_S177_v03.json` (nonheat_l2)
