# D-116 CompositionState / MediumState — schema v1.1 (for Kush review before chemistry routing)

Supersedes `d116_composition_state_schema_v1.md`. Changes come from the ksh+prv AI-delegated review (D-085, recorded as D-118; not human review). Code: `src/culinarystate/composition/state.py` (`composition_v11`, `lot_members_v11`, `load_markers_v2`). Markers: `registry/composition_markers_v2.csv` (115 rows).

S_t = (G_t, C_t, Q_t, Y_t, P_t). This file defines **C_t** only. G (lots/events), Q (physics v06 L1/L2), Y (EVD/formula) and P (value+basis | UNKNOWN+reason) are unchanged. Additive: new derived view, new output paths, no ledger or frozen-output changes. Every field is `{"v": value, "b": basis}` or `{"v": null, "u": reason}`.

## 1. Fields (one record per heat event, over the union of consumed lots)
| Field | Values | Filled from | Basis | UNKNOWN reasons |
|---|---|---|---|---|
| food_lot | list[ING id] | linked lineage members that are not MEDIUM-role marker ingredients | RUNG_A_LOT | `NO_LINKED_MEMBERS`, `ONLY_MEDIUM_MEMBERS` |
| medium_members | list[ING id] | members with a marker and `role_default = MEDIUM` | MARKER_TABLE_V2 | `NO_LINKED_MEMBERS` |
| salt_marker_present | TRUE / NOT_DETECTED | any member with SALT | MARKER_TABLE_V2 | `MEMBER_UNLINKED`, `NO_LINKED_MEMBERS` |
| acid_marker_present | TRUE / NOT_DETECTED | any member with ACID | MARKER_TABLE_V2 | same |
| lipid_marker_present | TRUE / NOT_DETECTED | any member with LIPID, or L1 medium ∈ {OIL_IMMERSION, PAN_CONTACT_OIL} | MARKER_TABLE_V2 | same |
| contact_phase | AQUEOUS / LIPID / AQUEOUS+LIPID / AIR | truth table §2 | MARKER_TABLE_V2+PHYSICS_V06_L1 | `MEDIUM_UNKNOWN`, `NO_LINKED_MEMBERS` |
| nacl_equiv_fraction_as_added | float w/w | needs grounded masses for every member | — | always `MASS_NOT_GROUNDED` in v1.1 |
| fat_fraction_as_added | float w/w | same | — | always `MASS_NOT_GROUNDED` in v1.1 |
| lot_acidity_band | — | not computed | — | always `LOT_PH_NOT_COMPUTED` |

Presence semantics: **TRUE** means a marker was found. **NOT_DETECTED** means no marker among the linked members, which is not FALSE. If no marker was found and some INGREDIENT_LOT ancestor has no `ingredient_id`, the value is UNKNOWN `MEMBER_UNLINKED`. A mixture pH, water activity, ionic strength, texture or colour value is never filled.

## 2. contact_phase truth table
aq = any AQUEOUS member or L1 medium ∈ {WATER, STEAM, LIQUID, LIQUID_PARTIAL}; lip = lipid_marker_present is TRUE.

| aq | lip | medium ∈ {OVEN_AIR, RADIANT} | contact_phase |
|---|---|---|---|
| T | T | any | AQUEOUS+LIPID |
| T | F | any | AQUEOUS |
| F | T | any | LIPID |
| F | F | yes | AIR |
| F | F | no | UNKNOWN `MEDIUM_UNKNOWN` |

## 3. Marker table v2
Columns: `ing_id, canonical_name, marker, rule, llm_acidic_7b_72b, status, role_default, basis, source`. One row per (ingredient, marker), so an ingredient can carry a set of markers: soy sauce has SALT and AQUEOUS, wine has ACID and AQUEOUS, cream has LIPID and AQUEOUS with role FOOD. Agreed reclassifications: rice/shaoxing/shaohsing wine → AQUEOUS only, and bouillon → AQUEOUS only. Status `AI_DELEGATED_REVIEWED_KSH_PRV_D085`. Kush or Parv must verify it before any submission figure uses it. Sea salt, miso and salted butter have no ACTIVE ING rows, so no rows were minted for them.

## 4. Acceptance — tomato variants (shared BOIL PROC-000019)
| Variant | food_lot | salt / acid / lipid | contact_phase |
|---|---|---|---|
| A water | tomato | ND / ND / ND | AQUEOUS |
| B + salt | tomato | T / ND / ND | AQUEOUS |
| C + salt + vinegar | tomato | T / T / ND | AQUEOUS |
| D + salt + vinegar + oil | tomato | T / T / T | AQUEOUS+LIPID |

All four are distinct. The fractions are `MASS_NOT_GROUNDED` and the acidity band is `LOT_PH_NOT_COMPUTED`. Test: `tests/unit/test_s179_d116_composition_v11.py` (pass).

## 5. Router hook (next step, after Kush approval; existing enums only)
The router compares the query's C_t with the **evidence row's own composition** (EVD context). If the query lot has a TRUE marker that the evidence row lacks, the result is `CONTEXT_MISMATCH` (near evidence, not DIRECT). If the query has an UNKNOWN presence, the result cannot be DIRECT for composition-sensitive analytes. No new router and no new enums.

## 6. Corpus results
- BBC (Mac): `state_dataset_fill_BBC_D116v11_2026-11-14.json`.
- Non-BBC (manjot): pending VPN.
- Full merged report: produced after the merge.
