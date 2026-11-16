# v04 -> v05 comparison, non-BBC physical layers (S178 FIX-PHYS)

Status: DRAFT / AI_DRAFTED, counts only, read from the run reports named in `source_report_sha256`. v04 = PHYS2 (Layer 1 0.2.0, Layer 2 0.4.0); v05 = FIX-PHYS (Layer 1 0.3.0: food targets, medium-compatible temperatures, window cut, ambient cues, cue axes; Layer 2 0.5.0: the Q1 lift gate, the moist-piece boundary, the water bath; non-heat Layer 1 0.3.0, Layer 2 0.5.0).

## Record audit (SCI-A figures, all non-BBC families)

| counter | v04 | v05 | delta |
|---|---:|---:|---:|
| until_clause_bound_temperature_reviewer_method | 869 | 438 | -431 |
| until_clause_bound_temperature_clause_spans | 0 | 475 | 475 |
| until_clause_bound_temperature_clause_spans_syrup_exempt | 0 | 0 | 0 |
| oven_text_stated_below_77 | 318 | 189 | -129 |
| oven_text_stated_below_77_core_computed | 20 | 14 | -6 |
| lifted_typical | 241 | 166 | -75 |
| lifted_typical_above_150 | 21 | 5 | -16 |
| lifted_typical_with_core | 12 | 4 | -8 |
| lifted_typical_core_above_100 | 12 | 0 | -12 |
| moist_piece_core_above_tboil | 12 | 0 | -12 |
| fat_heat_temperature_from_setter | 460 | 190 | -270 |
| aqueous_above_100_from_setter | 10 | 3 | -7 |
| aqueous_above_100_all | 373 | 330 | -43 |
| l1_ambient_temperature | 1915 | 2618 | 703 |
| l1_text_stated_range | 422 | 716 | 294 |
| flag_typical_FAN_VS_CONVENTIONAL_UNRESOLVED | 0 | 19 | 19 |
| flag_typical_SALT_MEMBER_BPE_SMALL | 0 | 68558 | 68558 |
| flag_typical_STATED_LIQUID_T_ABOVE_TBOIL_NOT_LIFTED_DILUTE | 0 | 40 | 40 |
| flag_typical_STATED_LIQUID_T_NOT_APPLIED_TO_MOIST_PIECE | 0 | 4 | 4 |
| flag_typical_SUGAR_PHASE_TBOIL_LOWER_ESTIMATE | 0 | 112352 | 112352 |
| flag_typical_TBOIL_CAP_LOWER_ESTIMATE_SOLUTE_RICH_MEMBER | 162378 | 0 | -162378 |
| flag_typical_WATER_BATH_IN_OVEN | 0 | 493 | 493 |
| l1_heat_events | 1696743 | 1696743 | 0 |
| l1_pressure_cue | 0 | 1102 | 1102 |
| l1_records_with_until_clause_spans | 0 | 51121 | 51121 |
| l1_syrup_stage_cue | 0 | 50733 | 50733 |
| l1_temperature_flag_FAN_VS_CONVENTIONAL_UNRESOLVED | 0 | 53 | 53 |
| l1_temperature_flag_HEAT_LEVEL_OR_APPLIANCE_SETTING_AT_OR_BELOW_TBOIL | 0 | 35 | 35 |
| l1_text_stated_DRY_HEAT | 33579 | 34812 | 1233 |
| l1_text_stated_FAT_HEAT | 1033 | 654 | -379 |
| l1_text_stated_HEAT_GENERAL | 14772 | 14925 | 153 |
| l1_text_stated_WET_HEAT | 1134 | 730 | -404 |
| l1_water_bath_cue | 0 | 493 | 493 |
| lifted_typical_row_CB_RULE_TEMPERATURE_FROM_SETTER_STEP | 8 | 0 | -8 |
| lifted_typical_row_CB_RULE_TEMPERATURE_OWN_CLAUSE | 233 | 166 | -67 |
| lifted_typical_solute_member_NO | 123 | 2 | -121 |
| lifted_typical_solute_member_YES | 118 | 164 | 46 |
| moist_piece_core_above_tboil_medium_LIQUID | 2 | 0 | -2 |
| moist_piece_core_above_tboil_medium_WATER | 10 | 0 | -10 |

## FOODCOM

| quantity | v04 | v05 | delta |
|---|---:|---:|---:|
| heat L1 heat_events | 1503261 | 1503261 | 0 |
| heat L1 driver_ready_events | 55662 | 57417 | 1755 |
| heat L1 driver_bounded_events | 87139 | 89882 | 2743 |
| heat L1 contract_bindings | 2102295 | 2104050 | 1755 |
| heat L1 temperature basis CARRIED_SETPOINT | 70835 | 73761 | 2926 |
| heat L1 temperature basis PHYSICAL_DEFINITION | 99745 | 99786 | 41 |
| heat L1 temperature basis TEXT_STATED | 48952 | 49557 | 605 |
| heat L2 status SCENARIO_COMPUTED | 667634 | 667634 | 0 |
| heat L2 status SCENARIO_UNKNOWN | 768753 | 768753 | 0 |
| heat L2 status UNSUPPORTED_MEDIUM | 66874 | 66874 | 0 |
| heat L2 stated-liquid events lifted (TYPICAL) | 182 | 120 | -62 |
| heat L2 TYPICAL core reaches 70 C = False | 2613 | 2610 | -3 |
| heat L2 TYPICAL core reaches 70 C = True | 52533 | 52536 | 3 |
| heat L2 cap flag SALT_MEMBER_BPE_SMALL (TYPICAL) | 0 | 59495 | 59495 |
| heat L2 cap flag STATED_LIQUID_LIFT_SUGAR_PHASE_MEMBER (TYPICAL) | 0 | 76 | 76 |
| heat L2 cap flag STATED_LIQUID_LIFT_SYRUP_STAGE_CUE (TYPICAL) | 0 | 44 | 44 |
| heat L2 cap flag STATED_LIQUID_T_ABOVE_TBOIL (TYPICAL) | 182 | 120 | -62 |
| heat L2 cap flag STATED_LIQUID_T_ABOVE_TBOIL_NOT_LIFTED_DILUTE (TYPICAL) | 0 | 27 | 27 |
| heat L2 cap flag STATED_LIQUID_T_ABOVE_TBOIL_NOT_LIFTED_NOT_OWNED (TYPICAL) | 0 | 2 | 2 |
| heat L2 cap flag STATED_LIQUID_T_NOT_APPLIED_TO_MOIST_PIECE (TYPICAL) | 0 | 3 | 3 |
| heat L2 cap flag SUGAR_PHASE_TBOIL_LOWER_ESTIMATE (TYPICAL) | 0 | 97882 | 97882 |
| heat L2 cap flag TBOIL_CAP_LOWER_ESTIMATE_SOLUTE_RICH_MEMBER (TYPICAL) | 142918 | 0 | -142918 |
| heat L2 cap flag WATER_BATH_IN_OVEN (TYPICAL) | 0 | 305 | 305 |
| heat L2 cap flag WATER_BATH_TEMPERATURE_BOUNDED_BY_TBOIL_UPPER_BOUND (TYPICAL) | 0 | 305 | 305 |
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
| non-heat L2 computed PRESERVATION | 79 | 80 | 1 |
| non-heat L2 computed RESTING | 552 | 552 | 0 |
| non-heat L2 computed SEPARATION | 113640 | 113640 | 0 |
| non-heat L2 computed STORAGE | 0 | 0 | 0 |

Heat L2 per-event comparison over 1503261 events: bath temperature changed (TYPICAL) 5067; core end temperature changed 45; non-heat events whose status changed 1. FIX-PHYS flags (TYPICAL): {'FAN_VS_CONVENTIONAL_UNRESOLVED': 19, 'HEAT_LEVEL_OR_APPLIANCE_SETTING_AT_OR_BELOW_TBOIL': 8, 'STATED_LIQUID_LIFT_SUGAR_PHASE_MEMBER': 76, 'STATED_LIQUID_LIFT_SYRUP_STAGE_CUE': 44, 'STATED_LIQUID_T_ABOVE_TBOIL_NOT_LIFTED_DILUTE': 27, 'STATED_LIQUID_T_ABOVE_TBOIL_NOT_LIFTED_NOT_OWNED': 2, 'STATED_LIQUID_T_NOT_APPLIED_TO_MOIST_PIECE': 3, 'WATER_BATH_IN_OVEN': 305}. Until-clause check (Layer 1): {'EXEMPT_LIQUID_OR_MEDIUM_SUBJECT': 146, 'EXEMPT_MEDIUM_THERMOMETER': 201, 'EXEMPT_SETTING_PHRASE': 32, 'EXEMPT_SYRUP_OR_CANDY': 84}.

## GUTENBERG_SEGMENT

| quantity | v04 | v05 | delta |
|---|---:|---:|---:|
| heat L1 heat_events | 182049 | 182049 | 0 |
| heat L1 driver_ready_events | 1717 | 1717 | 0 |
| heat L1 driver_bounded_events | 1983 | 1982 | -1 |
| heat L1 contract_bindings | 252044 | 252044 | 0 |
| heat L1 temperature basis CARRIED_SETPOINT | 50 | 50 | 0 |
| heat L1 temperature basis PHYSICAL_DEFINITION | 53893 | 53890 | -3 |
| heat L1 temperature basis TEXT_STATED | 932 | 952 | 20 |
| heat L2 status SCENARIO_COMPUTED | 120951 | 120951 | 0 |
| heat L2 status SCENARIO_UNKNOWN | 56765 | 56765 | 0 |
| heat L2 status UNSUPPORTED_MEDIUM | 4333 | 4333 | 0 |
| heat L2 stated-liquid events lifted (TYPICAL) | 56 | 44 | -12 |
| heat L2 TYPICAL core reaches 70 C = False | 37 | 37 | 0 |
| heat L2 TYPICAL core reaches 70 C = True | 13149 | 13149 | 0 |
| heat L2 cap flag SALT_MEMBER_BPE_SMALL (TYPICAL) | 0 | 8731 | 8731 |
| heat L2 cap flag STATED_LIQUID_LIFT_PRESSURE_CUE (TYPICAL) | 0 | 2 | 2 |
| heat L2 cap flag STATED_LIQUID_LIFT_SUGAR_PHASE_MEMBER (TYPICAL) | 0 | 11 | 11 |
| heat L2 cap flag STATED_LIQUID_LIFT_SYRUP_STAGE_CUE (TYPICAL) | 0 | 31 | 31 |
| heat L2 cap flag STATED_LIQUID_T_ABOVE_TBOIL (TYPICAL) | 56 | 44 | -12 |
| heat L2 cap flag STATED_LIQUID_T_ABOVE_TBOIL_NOT_LIFTED_DILUTE (TYPICAL) | 0 | 13 | 13 |
| heat L2 cap flag SUGAR_PHASE_TBOIL_LOWER_ESTIMATE (TYPICAL) | 0 | 13890 | 13890 |
| heat L2 cap flag TBOIL_CAP_LOWER_ESTIMATE_SOLUTE_RICH_MEMBER (TYPICAL) | 18661 | 0 | -18661 |
| heat L2 cap flag WATER_BATH_IN_OVEN (TYPICAL) | 0 | 186 | 186 |
| heat L2 cap flag WATER_BATH_TEMPERATURE_BOUNDED_BY_TBOIL_UPPER_BOUND (TYPICAL) | 0 | 186 | 186 |
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

Heat L2 per-event comparison over 182049 events: bath temperature changed (TYPICAL) 30; core end temperature changed 10; non-heat events whose status changed 0. FIX-PHYS flags (TYPICAL): {'STATED_LIQUID_LIFT_PRESSURE_CUE': 2, 'STATED_LIQUID_LIFT_SUGAR_PHASE_MEMBER': 11, 'STATED_LIQUID_LIFT_SYRUP_STAGE_CUE': 31, 'STATED_LIQUID_T_ABOVE_TBOIL_NOT_LIFTED_DILUTE': 13, 'WATER_BATH_IN_OVEN': 186}. Until-clause check (Layer 1): {'EXEMPT_LIQUID_OR_MEDIUM_SUBJECT': 4, 'EXEMPT_SYRUP_OR_CANDY': 3}.

## WIKIBOOKS

| quantity | v04 | v05 | delta |
|---|---:|---:|---:|
| heat L1 heat_events | 11433 | 11433 | 0 |
| heat L1 driver_ready_events | 615 | 611 | -4 |
| heat L1 driver_bounded_events | 930 | 926 | -4 |
| heat L1 contract_bindings | 15125 | 15121 | -4 |
| heat L1 temperature basis CARRIED_SETPOINT | 496 | 497 | 1 |
| heat L1 temperature basis PHYSICAL_DEFINITION | 1159 | 1160 | 1 |
| heat L1 temperature basis TEXT_STATED | 634 | 612 | -22 |
| heat L2 status SCENARIO_COMPUTED | 4871 | 4871 | 0 |
| heat L2 status SCENARIO_UNKNOWN | 6154 | 6154 | 0 |
| heat L2 status UNSUPPORTED_MEDIUM | 408 | 408 | 0 |
| heat L2 stated-liquid events lifted (TYPICAL) | 3 | 2 | -1 |
| heat L2 TYPICAL core reaches 70 C = False | 14 | 14 | 0 |
| heat L2 TYPICAL core reaches 70 C = True | 437 | 437 | 0 |
| heat L2 cap flag SALT_MEMBER_BPE_SMALL (TYPICAL) | 0 | 332 | 332 |
| heat L2 cap flag STATED_LIQUID_LIFT_SUGAR_PHASE_MEMBER (TYPICAL) | 0 | 2 | 2 |
| heat L2 cap flag STATED_LIQUID_T_ABOVE_TBOIL (TYPICAL) | 3 | 2 | -1 |
| heat L2 cap flag STATED_LIQUID_T_NOT_APPLIED_TO_MOIST_PIECE (TYPICAL) | 0 | 1 | 1 |
| heat L2 cap flag SUGAR_PHASE_TBOIL_LOWER_ESTIMATE (TYPICAL) | 0 | 580 | 580 |
| heat L2 cap flag TBOIL_CAP_LOWER_ESTIMATE_SOLUTE_RICH_MEMBER (TYPICAL) | 799 | 0 | -799 |
| heat L2 cap flag WATER_BATH_IN_OVEN (TYPICAL) | 0 | 2 | 2 |
| heat L2 cap flag WATER_BATH_TEMPERATURE_BOUNDED_BY_TBOIL_UPPER_BOUND (TYPICAL) | 0 | 2 | 2 |
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

Heat L2 per-event comparison over 11433 events: bath temperature changed (TYPICAL) 11; core end temperature changed 2; non-heat events whose status changed 0. FIX-PHYS flags (TYPICAL): {'STATED_LIQUID_LIFT_SUGAR_PHASE_MEMBER': 2, 'STATED_LIQUID_T_NOT_APPLIED_TO_MOIST_PIECE': 1, 'WATER_BATH_IN_OVEN': 2}. Until-clause check (Layer 1): {'EXEMPT_LIQUID_OR_MEDIUM_SUBJECT': 3, 'EXEMPT_SYRUP_OR_CANDY': 2}.

## TASTESET

| quantity | v04 | v05 | delta |
|---|---:|---:|---:|
| heat L1 heat_events | 0 | 0 | 0 |
| heat L1 driver_ready_events | 0 | 0 | 0 |
| heat L1 driver_bounded_events | 0 | 0 | 0 |
| heat L1 contract_bindings | 0 | 0 | 0 |
| heat L2 stated-liquid events lifted (TYPICAL) | 0 | 0 | 0 |
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

Heat L2 per-event comparison over None events: bath temperature changed (TYPICAL) 0; core end temperature changed 0; non-heat events whose status changed 0. FIX-PHYS flags (TYPICAL): {}. Until-clause check (Layer 1): {}.

## SUPERSEDED outputs

The v05 reports replace these v04 reports for the non-BBC families (kept for the audit trail).

- `reports/step26/binding_census_L1_FOODCOM_full_S178_v04.json` (heat_l1)
- `reports/step26/binding_census_L1_GUTENBERG_SEGMENT_full_S178_v04.json` (heat_l1)
- `reports/step26/binding_census_L1_WIKIBOOKS_full_S178_v04.json` (heat_l1)
- `reports/step26/binding_census_L1_TASTESET_full_S178_v04.json` (heat_l1)
- `reports/step26/scenario_L2_FOODCOM_full_S178_v04.json` (heat_l2)
- `reports/step26/scenario_L2_GUTENBERG_SEGMENT_full_S178_v04.json` (heat_l2)
- `reports/step26/scenario_L2_WIKIBOOKS_full_S178_v04.json` (heat_l2)
- `reports/step26/scenario_L2_TASTESET_full_S178_v04.json` (heat_l2)
- `reports/step26/nonheat_L1_FOODCOM_full_S178_v04.json` (nonheat_l1)
- `reports/step26/nonheat_L1_GUTENBERG_SEGMENT_full_S178_v04.json` (nonheat_l1)
- `reports/step26/nonheat_L1_WIKIBOOKS_full_S178_v04.json` (nonheat_l1)
- `reports/step26/nonheat_L1_TASTESET_full_S178_v04.json` (nonheat_l1)
- `reports/step26/nonheat_L2_FOODCOM_full_S178_v04.json` (nonheat_l2)
- `reports/step26/nonheat_L2_GUTENBERG_SEGMENT_full_S178_v04.json` (nonheat_l2)
- `reports/step26/nonheat_L2_WIKIBOOKS_full_S178_v04.json` (nonheat_l2)
- `reports/step26/nonheat_L2_TASTESET_full_S178_v04.json` (nonheat_l2)
