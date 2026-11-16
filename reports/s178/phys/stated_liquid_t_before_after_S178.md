# Stated-liquid temperature lift: diagnosis and before / after (S178 PHYS2, S177 open item (a))

Status: DRAFT / AI_DRAFTED, counts only. Before = Layer 1 0.1.0 (nearest temperature of the sentence) with Layer 2 0.3.0; after = Layer 1 0.2.0 (temperature ownership, oven / heat-level cue guard, food-target diversion) with Layer 2 0.4.0.

## FOODCOM

Aqueous-medium heat events with a stated temperature above 100 C (Layer 1, before): 560.

| stated T before | NOW_BOIL_BY_PHYSICAL_DEFINITION | NOW_UNKNOWN_TEMPERATURE | STILL_STATED_AQUEOUS_ABOVE_100 |
|---|---:|---:|---:|
| 100_TO_105 | 3 | 3 | 22 |
| 105_TO_120 | 41 | 5 | 175 |
| 120_TO_150 | 21 | 16 | 62 |
| ABOVE_150 | 101 | 83 | 28 |

- Layer 2 0.3.0 (before): events lifted by stated T bucket {'100_TO_105': 21, '105_TO_120': 149, '120_TO_150': 69, 'ABOVE_150': 191}; with a computed core {'100_TO_105': 3, '105_TO_120': 8, '120_TO_150': 8, 'ABOVE_150': 7}; highest core of a lifted event {'100_TO_105': 104.4, '105_TO_120': 117.6, '120_TO_150': 150.0, 'ABOVE_150': 204.4}.
- Layer 2 0.4.0 (after): events lifted by stated T bucket {'100_TO_105': 16, '105_TO_120': 110, '120_TO_150': 36, 'ABOVE_150': 20}; with a computed core {'100_TO_105': 2, '105_TO_120': 4, '120_TO_150': 2, 'ABOVE_150': 2}; highest core of a lifted event {'100_TO_105': 104.4, '105_TO_120': 115.6, '120_TO_150': 148.7, 'ABOVE_150': 176.7}.

## GUTENBERG_SEGMENT

Aqueous-medium heat events with a stated temperature above 100 C (Layer 1, before): 121.

| stated T before | NOW_BOIL_BY_PHYSICAL_DEFINITION | NOW_UNKNOWN_TEMPERATURE | STILL_STATED_AQUEOUS_ABOVE_100 |
|---|---:|---:|---:|
| 100_TO_105 | 2 | 0 | 5 |
| 105_TO_120 | 23 | 0 | 51 |
| 120_TO_150 | 7 | 3 | 23 |
| ABOVE_150 | 2 | 3 | 2 |

- Layer 2 0.3.0 (before): events lifted by stated T bucket {'100_TO_105': 5, '105_TO_120': 51, '120_TO_150': 24, 'ABOVE_150': 4}; with a computed core {}; highest core of a lifted event {}.
- Layer 2 0.4.0 (after): events lifted by stated T bucket {'100_TO_105': 4, '105_TO_120': 36, '120_TO_150': 15, 'ABOVE_150': 1}; with a computed core {}; highest core of a lifted event {}.

## WIKIBOOKS

Aqueous-medium heat events with a stated temperature above 100 C (Layer 1, before): 8.

| stated T before | NOW_BOIL_BY_PHYSICAL_DEFINITION | STILL_STATED_AQUEOUS_ABOVE_100 |
|---|---:|---:|
| 100_TO_105 | 0 | 1 |
| 105_TO_120 | 0 | 3 |
| 120_TO_150 | 1 | 1 |
| ABOVE_150 | 2 | 0 |

- Layer 2 0.3.0 (before): events lifted by stated T bucket {'100_TO_105': 1, '105_TO_120': 2, '120_TO_150': 1, 'ABOVE_150': 2}; with a computed core {'100_TO_105': 1, '105_TO_120': 1}; highest core of a lifted event {'100_TO_105': 104.3, '105_TO_120': 112.2}.
- Layer 2 0.4.0 (after): events lifted by stated T bucket {'100_TO_105': 1, '105_TO_120': 2}; with a computed core {'100_TO_105': 1, '105_TO_120': 1}; highest core of a lifted event {'100_TO_105': 104.3, '105_TO_120': 112.2}.
