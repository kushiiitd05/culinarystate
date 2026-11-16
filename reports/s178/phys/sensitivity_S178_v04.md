# Sensitivity of the GENTLE-INTENSE bracket (S178 PHYS2, T4-C05-R1)

Status: DRAFT / AI_DRAFTED, counts and quantiles only, no recipe text or ids. The brackets are scenario defaults (ASSUMED_DEFAULT, MODEL_DERIVED, NON_CITABLE). A conclusion is ROBUST for a family when at most 10% of its events change the conclusion between GENTLE, TYPICAL and INTENSE (PROPOSED threshold); ROBUST says the conclusion does not depend on where in the scenario ranges the event sits, not that it is true of food.

Input layer versions: heat L2 `scenario-layer-L2-0.4.0-draft`, non-heat L2 `nonheat-scenario-L2-0.4.0-draft`.

## Heat families

| family | events | computed | SCENARIO_UNKNOWN | conclusion | evaluated | robust yes | robust no | fragile | fragile share | flag |
|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---|
| DRY_HEAT | 401832 | 335085 | 9619 | core_reaches_70c | 31107 | 13425 | 45 | 17637 | 0.567 | FRAGILE |
| DRY_HEAT | 401832 | 335085 | 9619 | evaporation_cap_binds | 335085 | 322294 | 12784 | 7 | 0.0 | ROBUST |
| DRY_HEAT | 401832 | 335085 | 9619 | surface_state_unchanged | 335085 | 310858 | 0 | 24227 | 0.0723 | ROBUST |
| DRY_HEAT | 401832 | 335085 | 9619 | volume_average_reaches_70c | 31107 | 13514 | 45 | 17548 | 0.5641 | FRAGILE |
| FAT_HEAT | 225135 | 175864 | 49271 | core_reaches_70c | 16248 | 3832 | 70 | 12346 | 0.7598 | FRAGILE |
| FAT_HEAT | 225135 | 175864 | 49271 | evaporation_cap_binds | 175864 | 159628 | 15776 | 460 | 0.0026 | ROBUST |
| FAT_HEAT | 225135 | 175864 | 49271 | surface_state_unchanged | 175864 | 160630 | 0 | 15234 | 0.0866 | ROBUST |
| FAT_HEAT | 225135 | 175864 | 49271 | volume_average_reaches_70c | 16248 | 3886 | 10 | 12352 | 0.7602 | FRAGILE |
| HEAT_GENERAL | 707240 | 0 | 692753 | - | - | - | - | - | - | - |
| WET_HEAT | 362536 | 282507 | 80029 | core_reaches_70c | 21428 | 12528 | 15 | 8885 | 0.4146 | FRAGILE |
| WET_HEAT | 362536 | 282507 | 80029 | evaporation_cap_binds | 282507 | 6 | 282496 | 5 | 0.0 | ROBUST |
| WET_HEAT | 362536 | 282507 | 80029 | surface_state_unchanged | 282507 | 282502 | 0 | 5 | 0.0 | ROBUST |
| WET_HEAT | 362536 | 282507 | 80029 | volume_average_reaches_70c | 21428 | 12863 | 5 | 8560 | 0.3995 | FRAGILE |

### Heat families: width INTENSE - GENTLE (median [p10, p90], share of events with zero width)

| family | quantity | n | p10 | p50 | p90 | max | share zero |
|---|---|---:|---:|---:|---:|---:|---:|
| DRY_HEAT | bath_c | 335085 | 0.0 | 60.0 | 60.0 | 83.3333 | 0.2995 |
| DRY_HEAT | core_dose_log10_ratio | 31107 | 0.457396 | 1.99923 | 3.78388 | 7.28506 | 0.0 |
| DRY_HEAT | core_end_c | 31107 | 3.499 | 45.895 | 83.825 | 196.216 | 0.0022 |
| DRY_HEAT | core_minutes_above_70 | 31107 | 6.367 | 25.396 | 117.5 | 307.518 | 0.0014 |
| DRY_HEAT | duration_min | 335085 | 0.0 | 5.0 | 110.0 | 2160.0 | 0.323 |
| DRY_HEAT | volume_avg_end_c | 31107 | 3.433 | 45.018 | 79.429 | 189.073 | 0.0022 |
| DRY_HEAT | zone_mean_dose_log10_ratio | 31107 | 0.455748 | 1.88743 | 3.64557 | 7.0337 | 0.0 |
| FAT_HEAT | bath_c | 175864 | 60.0 | 60.0 | 60.0 | 60.0 | 0.0053 |
| FAT_HEAT | core_dose_log10_ratio | 16248 | 1.30076 | 3.03333 | 4.34987 | 7.36021 | 0.0 |
| FAT_HEAT | core_end_c | 16248 | 2.536 | 49.965 | 94.679 | 194.129 | 0.0094 |
| FAT_HEAT | core_minutes_above_70 | 16248 | 2.22 | 14.73 | 59.1 | 60.788 | 0.0043 |
| FAT_HEAT | duration_min | 175864 | 0.0 | 58.0 | 58.0 | 120.0 | 0.1921 |
| FAT_HEAT | volume_avg_end_c | 16248 | 2.331 | 41.918 | 77.253 | 169.442 | 0.0094 |
| FAT_HEAT | zone_mean_dose_log10_ratio | 16248 | 1.13056 | 2.65229 | 3.56505 | 6.00837 | 0.0 |
| WET_HEAT | bath_c | 282507 | 0.0 | 0.0 | 10.0 | 20.0 | 0.5497 |
| WET_HEAT | core_dose_log10_ratio | 21428 | 0.509011 | 2.71733 | 4.70727 | 6.13484 | 0.0 |
| WET_HEAT | core_end_c | 21428 | 0.396 | 22.433 | 86.29 | 130.235 | 0.02 |
| WET_HEAT | core_minutes_above_70 | 21428 | 2.984 | 234.069 | 236.4 | 249.165 | 0.0007 |
| WET_HEAT | duration_min | 282507 | 0.0 | 236.0 | 237.0 | 840.0 | 0.232 |
| WET_HEAT | volume_avg_end_c | 21428 | 0.364 | 19.31 | 65.597 | 99.003 | 0.0201 |
| WET_HEAT | zone_mean_dose_log10_ratio | 21428 | 0.490515 | 2.24196 | 3.81115 | 4.48042 | 0.0 |

## Non-heat families

| family | events | computed | SCENARIO_UNKNOWN | conclusion | evaluated | robust yes | robust no | fragile | fragile share | flag |
|---|---:|---:|---:|---|---:|---:|---:|---:|---:|---|
| COOLING | 310762 | 25076 | 285268 | core_end_at_or_below_5c | 22619 | 19 | 12160 | 10440 | 0.4616 | FRAGILE |
| COOLING | 310762 | 25076 | 285268 | core_end_at_or_below_60c | 22619 | 8873 | 2 | 13744 | 0.6076 | FRAGILE |
| COOLING | 310762 | 25076 | 285268 | frozen_within_stated_duration | 226 | 26 | 15 | 185 | 0.8186 | FRAGILE |
| COOLING | 310762 | 25076 | 285268 | thawed_within_stated_duration | 39 | 10 | 12 | 17 | 0.4359 | FRAGILE |
| FERMENT_LEAVEN | 58613 | 2367 | 32229 | uptake_at_least_half | 2367 | 61 | 120 | 2186 | 0.9235 | FRAGILE |
| MECHANICAL_CUT | 656204 | 283805 | 165348 | - | - | - | - | - | - | - |
| MECHANICAL_MIX | 1552674 | 0 | 0 | - | - | - | - | - | - | - |
| PRESERVATION | 81813 | 122 | 71840 | time_class_unchanged | 95 | 6 | 0 | 89 | 0.9368 | FRAGILE |
| PRESERVATION | 81813 | 122 | 71840 | uptake_at_least_half | 23 | 0 | 0 | 23 | 1.0 | FRAGILE |
| RESTING | 16898 | 642 | 15806 | core_end_at_or_above_60c | 642 | 43 | 339 | 260 | 0.405 | FRAGILE |
| SEPARATION | 325389 | 134240 | 0 | - | - | - | - | - | - | - |
| STORAGE | 25397 | 0 | 13120 | - | - | - | - | - | - | - |

### Non-heat families: width INTENSE - GENTLE (median [p10, p90], share of events with zero width)

| family | quantity | n | p10 | p50 | p90 | max | share zero |
|---|---|---:|---:|---:|---:|---:|---:|
| COOLING | INPUT_duration_min | 22619 | 0.0 | 316.0 | 331.0 | 20160.0 | 0.1543 |
| COOLING | INPUT_h | 25076 | 10.0 | 15.0 | 15.0 | 800.0 | 0.0 |
| COOLING | INPUT_half_thickness_m | 22619 | 0.001 | 0.0025 | 0.009 | 0.009 | 0.0 |
| COOLING | INPUT_initial_c | 22619 | 21.0 | 35.0 | 35.0 | 35.0 | 0.0 |
| COOLING | INPUT_medium_c | 25076 | 6.0 | 7.0 | 7.0 | 18.0 | 0.0002 |
| COOLING | OUTPUT_core_end_c | 22619 | 7.0 | 60.11 | 75.896 | 117.313 | 0.0 |
| COOLING | OUTPUT_core_minutes_above_5c | 22619 | 4.855 | 240.0 | 331.0 | 126528.0 | 0.0799 |
| COOLING | OUTPUT_core_minutes_above_60c | 22619 | 0.0 | 5.0 | 20.0 | 6570.0 | 0.2843 |
| COOLING | OUTPUT_freezing_point_c | 2457 | 1.5 | 1.5 | 1.5 | 1.5 | 0.0 |
| COOLING | OUTPUT_freezing_time_min | 1959 | 162.813 | 435.513 | 1336.55 | 1336.55 | 0.0 |
| COOLING | OUTPUT_minutes_to_target_food_c | 3 | 212.778 | 379.488 | 506.912 | 538.768 | 0.0 |
| COOLING | OUTPUT_thaw_time_min | 498 | 365.296 | 986.064 | 3101.51 | 5582.12 | 0.0 |
| COOLING | OUTPUT_thickness_m | 2457 | 0.002 | 0.005 | 0.018 | 0.018 | 0.0 |
| FERMENT_LEAVEN | INPUT_D_eff_m2_s | 2367 | 5.5e-10 | 5.5e-10 | 9e-10 | 9e-10 | 0.0 |
| FERMENT_LEAVEN | INPUT_duration_min | 2367 | 0.0 | 465.0 | 583.0 | 5760.0 | 0.1863 |
| FERMENT_LEAVEN | INPUT_half_thickness_m | 2367 | 0.001 | 0.0025 | 0.009 | 0.009 | 0.0 |
| FERMENT_LEAVEN | OUTPUT_fourier_number | 2367 | 0.474375 | 7.67719 | 69.1 | 82022.4 | 0.0 |
| FERMENT_LEAVEN | OUTPUT_uptake_fraction | 2367 | 0.521538 | 0.940159 | 0.983662 | 0.986038 | 0.0008 |
| MECHANICAL_CUT | INPUT_half_thickness_m | 283805 | 0.001 | 0.0025 | 0.009 | 0.009 | 0.0 |
| MECHANICAL_CUT | INPUT_time_until_next_heat | 10657 | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 |
| MECHANICAL_CUT | OUTPUT_surface_to_volume_cube_per_m | 283805 | 750.0 | 1250.0 | 4000.0 | 4000.0 | 0.0 |
| MECHANICAL_CUT | OUTPUT_surface_to_volume_slab_per_m | 283805 | 250.0 | 416.667 | 1333.33 | 1333.33 | 0.0 |
| PRESERVATION | INPUT_D_eff_m2_s | 23 | 5e-10 | 5e-10 | 5e-10 | 5e-10 | 0.0 |
| PRESERVATION | INPUT_air_c | 95 | 13.8889 | 60.0 | 60.0 | 60.0 | 0.0842 |
| PRESERVATION | INPUT_duration_min | 122 | 60.0 | 1435.0 | 1435.0 | 1435.0 | 0.082 |
| PRESERVATION | INPUT_half_thickness_m | 118 | 0.001 | 0.0025 | 0.009 | 0.009 | 0.0 |
| PRESERVATION | INPUT_medium_c | 4 | 3.78 | 12.6 | 12.6 | 12.6 | 0.25 |
| PRESERVATION | OUTPUT_constant_rate_end_min | 95 | 221.952 | 590.996 | 1780.88 | 16126.9 | 0.0 |
| PRESERVATION | OUTPUT_f0_upper_bound_at_medium_t_min | 4 | 144.421 | 292.634 | 292.634 | 292.634 | 0.0 |
| PRESERVATION | OUTPUT_falling_rate_tau_min | 95 | 169.433 | 451.407 | 1357.97 | 12268.7 | 0.0 |
| PRESERVATION | OUTPUT_fourier_number | 23 | 5.75958 | 23.0362 | 207.333 | 207.333 | 0.0 |
| PRESERVATION | OUTPUT_moisture_ratio | 95 | 0.677422 | 0.995256 | 0.998419 | 0.998419 | 0.0 |
| PRESERVATION | OUTPUT_uptake_fraction | 23 | 0.815736 | 0.930901 | 0.976966 | 0.976966 | 0.0 |
| PRESERVATION | OUTPUT_water_removed_fraction | 95 | 0.667923 | 0.978695 | 0.981787 | 0.981787 | 0.0 |
| PRESERVATION | OUTPUT_wet_bulb_c | 95 | 15.0 | 15.0 | 15.0 | 15.0 | 0.0 |
| RESTING | INPUT_half_thickness_m | 642 | 0.001 | 0.0025 | 0.009 | 0.009 | 0.0 |
| RESTING | INPUT_heat_bath_c | 642 | 0.0 | 10.0 | 60.0 | 60.0 | 0.4579 |
| RESTING | INPUT_heat_duration_min | 642 | 0.0 | 13.5 | 237.0 | 237.0 | 0.3349 |
| RESTING | INPUT_rest_duration_min | 642 | 0.0 | 715.0 | 715.0 | 10080.0 | 0.3131 |
| RESTING | INPUT_t_cap_c | 616 | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 |
| RESTING | OUTPUT_boundary_c | 642 | 0.0 | 0.0 | 10.0 | 60.0 | 0.8442 |
| RESTING | OUTPUT_carryover_rise_c | 642 | 0.001 | 0.642 | 12.585 | 25.168 | 0.0919 |
| RESTING | OUTPUT_core_end_c | 642 | 5.1551 | 22.272 | 49.3077 | 135.233 | 0.0 |
| RESTING | OUTPUT_core_end_of_heat_c | 642 | 0.675 | 23.088 | 83.827 | 196.219 | 0.0078 |
| RESTING | OUTPUT_core_peak_c | 642 | 0.674 | 21.356 | 69.723 | 190.329 | 0.0093 |
| RESTING | OUTPUT_surface_end_c | 642 | 5.5604 | 21.371 | 46.5919 | 138.487 | 0.0 |
| RESTING | OUTPUT_volume_avg_end_c | 642 | 5.114 | 21.948 | 48.709 | 136.184 | 0.0 |
| RESTING | OUTPUT_volume_avg_end_of_heat_c | 642 | 0.67 | 21.115 | 68.987 | 189.071 | 0.0078 |
| SEPARATION | INPUT_liquid_removed_fraction | 134240 | 0.28 | 0.28 | 0.28 | 0.28 | 0.0 |

## Reasons for SCENARIO_UNKNOWN (counts by missing-input set)

- heat DRY_HEAT: bath_c__duration_min__medium = 8167; duration_min__medium = 775; bath_c__medium = 576; medium = 79; duration_min = 22
- heat FAT_HEAT: duration_min = 47837; bath_c__duration_min__medium = 1384; bath_c__medium = 48; duration_min__medium = 2
- heat HEAT_GENERAL: bath_c__medium = 669257; medium = 14541; bath_c__duration_min__medium = 8789; duration_min__medium = 166
- heat WET_HEAT: bath_c__medium = 69516; duration_min = 7416; bath_c__duration_min__medium = 2473; medium = 614; bath_c__duration_min = 7; bath_c = 2
- nonheat COOLING: half_thickness = 285232; MEDIUM_NOT_BELOW_FREEZING_POINT = 26; MEDIUM_NOT_ABOVE_FREEZING_POINT = 10
- nonheat FERMENT_LEAVEN: half_thickness = 32229
- nonheat MECHANICAL_CUT: cut_class = 165348
- nonheat PRESERVATION: environment = 65338; medium = 2822; medium_temperature = 2178; half_thickness = 1312; duration_min__half_thickness = 170; AIR_NOT_WARMER_THAN_WET_BULB = 17
- nonheat RESTING: prior_heat_link = 8392; half_thickness = 3648; half_thickness__prior_heat_bath_c__prior_heat_h = 2800; prior_heat_bath_c__prior_heat_h = 480; half_thickness__prior_heat_duration_min = 124; half_thickness__prior_heat_h = 105
- nonheat STORAGE: storage_temperature = 13120
