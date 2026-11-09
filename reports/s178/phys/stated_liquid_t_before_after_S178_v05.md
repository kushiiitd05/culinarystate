# Stated-liquid temperature lift: diagnosis and before / after (S178 PHYS2, S177 open item (a))

Status: DRAFT / AI_DRAFTED, counts only. The two Layer 2 blocks are named by their labels (PHYS2: before = Layer 1 0.1.0 with Layer 2 0.3.0, after = Layer 1 0.2.0 with Layer 2 0.4.0; FIX-PHYS v05: before = 0.2.0 / 0.4.0, after = Layer 1 0.3.0 with Layer 2 0.5.0, the Q1 lift gate and the moist-piece boundary).

## FOODCOM

Aqueous-medium heat events with a stated temperature above 100 C (Layer 1, before): 287.

| stated T before | NOW_BOIL_BY_PHYSICAL_DEFINITION | NOW_UNKNOWN_TEMPERATURE | STILL_STATED_AQUEOUS_ABOVE_100 |
|---|---:|---:|---:|
| 100_TO_105 | 3 | 1 | 18 |
| 105_TO_120 | 23 | 2 | 150 |
| 120_TO_150 | 13 | 2 | 47 |
| ABOVE_150 | 3 | 3 | 22 |

- before_v04: events lifted by stated T bucket {'100_TO_105': 16, '105_TO_120': 110, '120_TO_150': 36, 'ABOVE_150': 20}; with a computed core {'100_TO_105': 2, '105_TO_120': 4, '120_TO_150': 2, 'ABOVE_150': 2}; highest core of a lifted event {'100_TO_105': 104.4, '105_TO_120': 115.6, '120_TO_150': 148.7, 'ABOVE_150': 176.7}.
- after_v05: events lifted by stated T bucket {'100_TO_105': 9, '105_TO_120': 85, '120_TO_150': 22, 'ABOVE_150': 4}; with a computed core {'105_TO_120': 3}; highest core of a lifted event {'105_TO_120': 100.0}; not lifted (Q1 gate) {'100_TO_105': {'STATED_LIQUID_T_ABOVE_TBOIL_NOT_LIFTED_DILUTE': 5}, '105_TO_120': {'STATED_LIQUID_T_ABOVE_TBOIL_NOT_LIFTED_DILUTE': 6, 'STATED_LIQUID_T_ABOVE_TBOIL_NOT_LIFTED_NOT_OWNED': 1}, '120_TO_150': {'STATED_LIQUID_T_ABOVE_TBOIL_NOT_LIFTED_DILUTE': 4, 'STATED_LIQUID_T_ABOVE_TBOIL_NOT_LIFTED_NOT_OWNED': 1}, 'ABOVE_150': {'STATED_LIQUID_T_ABOVE_TBOIL_NOT_LIFTED_DILUTE': 12}}; lift reasons {'100_TO_105': {'STATED_LIQUID_LIFT_SUGAR_PHASE_MEMBER': 5, 'STATED_LIQUID_LIFT_SYRUP_STAGE_CUE': 4}, '105_TO_120': {'STATED_LIQUID_LIFT_SUGAR_PHASE_MEMBER': 55, 'STATED_LIQUID_LIFT_SYRUP_STAGE_CUE': 30}, '120_TO_150': {'STATED_LIQUID_LIFT_SUGAR_PHASE_MEMBER': 12, 'STATED_LIQUID_LIFT_SYRUP_STAGE_CUE': 10}, 'ABOVE_150': {'STATED_LIQUID_LIFT_SUGAR_PHASE_MEMBER': 4}}; moist piece bounded by T_boil {'105_TO_120': 3}.

## GUTENBERG_SEGMENT

Aqueous-medium heat events with a stated temperature above 100 C (Layer 1, before): 81.

| stated T before | NOW_BOIL_BY_PHYSICAL_DEFINITION | STILL_STATED_AQUEOUS_ABOVE_100 |
|---|---:|---:|
| 100_TO_105 | 0 | 5 |
| 105_TO_120 | 0 | 51 |
| 120_TO_150 | 1 | 22 |
| ABOVE_150 | 0 | 2 |

- before_v04: events lifted by stated T bucket {'100_TO_105': 4, '105_TO_120': 36, '120_TO_150': 15, 'ABOVE_150': 1}; with a computed core {}; highest core of a lifted event {}.
- after_v05: events lifted by stated T bucket {'100_TO_105': 3, '105_TO_120': 32, '120_TO_150': 8, 'ABOVE_150': 1}; with a computed core {}; highest core of a lifted event {}; not lifted (Q1 gate) {'100_TO_105': {'STATED_LIQUID_T_ABOVE_TBOIL_NOT_LIFTED_DILUTE': 1}, '105_TO_120': {'STATED_LIQUID_T_ABOVE_TBOIL_NOT_LIFTED_DILUTE': 5}, '120_TO_150': {'STATED_LIQUID_T_ABOVE_TBOIL_NOT_LIFTED_DILUTE': 7}}; lift reasons {'100_TO_105': {'STATED_LIQUID_LIFT_SUGAR_PHASE_MEMBER': 1, 'STATED_LIQUID_LIFT_SYRUP_STAGE_CUE': 2}, '105_TO_120': {'STATED_LIQUID_LIFT_PRESSURE_CUE': 2, 'STATED_LIQUID_LIFT_SUGAR_PHASE_MEMBER': 9, 'STATED_LIQUID_LIFT_SYRUP_STAGE_CUE': 21}, '120_TO_150': {'STATED_LIQUID_LIFT_SUGAR_PHASE_MEMBER': 1, 'STATED_LIQUID_LIFT_SYRUP_STAGE_CUE': 7}, 'ABOVE_150': {'STATED_LIQUID_LIFT_SYRUP_STAGE_CUE': 1}}.

## WIKIBOOKS

Aqueous-medium heat events with a stated temperature above 100 C (Layer 1, before): 5.

| stated T before | NOW_BOIL_BY_PHYSICAL_DEFINITION | STILL_STATED_AQUEOUS_ABOVE_100 |
|---|---:|---:|
| 100_TO_105 | 1 | 0 |
| 105_TO_120 | 0 | 3 |
| 120_TO_150 | 0 | 1 |

- before_v04: events lifted by stated T bucket {'100_TO_105': 1, '105_TO_120': 2}; with a computed core {'100_TO_105': 1, '105_TO_120': 1}; highest core of a lifted event {'100_TO_105': 104.3, '105_TO_120': 112.2}.
- after_v05: events lifted by stated T bucket {'105_TO_120': 2}; with a computed core {'105_TO_120': 1}; highest core of a lifted event {'105_TO_120': 100.0}; lift reasons {'105_TO_120': {'STATED_LIQUID_LIFT_SUGAR_PHASE_MEMBER': 2}}; moist piece bounded by T_boil {'105_TO_120': 1}.
