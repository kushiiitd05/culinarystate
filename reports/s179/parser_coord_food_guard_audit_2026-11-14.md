# Parser audit — coordinated-list food guard (D-116 prerequisite), 14 Nov 2026

Rung A, all 612,782 recipes, guard off (frozen, `process_state_map_full_2026-11-13.json`) vs on (`process_state_map_full_guard_2026-11-14.json`). Rule: a food word right after `,` / `and` / `or` that follows a FOOD_MENTION and is not followed by an object word stays an ingredient (`src/culinarystate/extraction/rung_a.py`, opt-in `coord_food_guard`). Tests: `tests/unit/test_s179_coord_food_guard.py` (7), existing Rung A tests 144 pass with the default off.

| Measure | Before (off) | After (on) |
|---|---|---|
| step events | 9,470,190 | 9,194,463 (−275,727; −2.9 %) |
| guard triggers (food word that was parsed as a verb) | — | **275,710 in 190,461 recipes (31.1 %)** |
| exceptions | 0 | 0 |
| COMBINATION-family events (spurious "season" etc.) | 2,192,184 | 2,011,059 (−181,125) |
| FAT_HEAT-family events (spurious "oil"/"butter" verbs) | 230,451 | 210,357 (−20,094) |
| Merge share | 18.69 % | 18.29 % |
| Transform share | 64.86 % | 64.49 % |
| UNMAPPED share | 16.16 % | 16.91 % |

Reading: about 1 in 34 parsed steps was a spurious action created from an ingredient word in a list; removing them folds those ingredients into the real Merge instead of a fake "season"/"brush" event, so Merge count falls while lot membership becomes correct (tomato A–D acceptance, `tests/unit/test_s179_d116_composition.py`).

Precision: an AI spot check of Wikibooks contexts found the guarded words to be list ingredients (salt, butter, oil, pepper); a formal precision is **not measured**. A 50-context human spot check (Kush/Parv) is needed before the number is quoted as accurate. Labels: DIAGNOSTIC · AI_PRECHECKED · NO_HUMAN_SIGNOFF_D085.
