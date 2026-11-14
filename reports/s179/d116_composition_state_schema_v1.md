# D-116 CompositionState / MediumState — schema v1 (PROPOSED, for Kush review before chemistry routing)

S_t = (G_t, C_t, Q_t, Y_t, P_t). This file defines **C_t** only; G (lots/events/state type), Q (physics v06 L1/L2), Y (EVD/formula per analyte) and P (value+basis | UNKNOWN+reason) are unchanged. Every field is a cell `{"v": value, "b": basis}` or `{"v": null, "u": reason}`. Additive: new derived view and new output paths; no ledger or frozen output changes.

## 1. CompositionState (one per lot version, i.e. per lot × event)
| Field | Type | Filled from | Basis label | UNKNOWN reasons |
|---|---|---|---|---|
| lot_id, event_id, recipe_id | id | Rung A (coord_food_guard on) + engine | RUNG_A | — |
| members | list[ING id] | lots merged into this lot (engine), linked mentions | RUNG_A_LOT | `MEMBER_UNLINKED` per unlinked mention |
| phase_solid / phase_aqueous / phase_lipid | list[ING id] | member → phase via marker table §3 | MARKER_TABLE_V1 | `NO_MARKER` |
| salt_present | bool | any member with marker SALT | MARKER_TABLE_V1 | `MEMBER_UNLINKED` (only if no member is SALT and some member is unlinked) |
| acid_present | bool | any member with marker ACID | MARKER_TABLE_V1 | same |
| lipid_present | bool | any member with marker LIPID | MARKER_TABLE_V1 | same |
| salt_fraction | float (w/w) | NaCl-equivalent = Na (SR, mg/100 g) × 2.54 over grounded member masses | SR_COMPOSITION_SCENARIO | `MASS_NOT_GROUNDED` (any member without grams; all Food.com), `NO_SR_ROW` |
| fat_fraction | float (w/w) | SR total lipid × grounded masses | SR_COMPOSITION_SCENARIO | same |
| acidity_band | enum ACIDIC (pH < 4.6) / LOW_ACID / UNKNOWN | only from a cited pH table per member; band of the most acidic member when present in non-trace amount | SOURCED_PH_TABLE | `NO_SOURCED_PH_TABLE` (v1 default until a table is verified), `MIXTURE_PH_NOT_COMPUTED` |

Never filled in v1: mixture pH value, water activity, ionic strength, texture, colour.

## 2. MediumState (one per heat event; the contact medium around the food lot)
| Field | Filled from | Basis |
|---|---|---|
| medium_type | physics v06 L1 `medium` (WATER, STEAM, OIL_IMMERSION, PAN_CONTACT_OIL, OVEN_AIR, LIQUID, …) | PHYSICS_V06_L1 or UNKNOWN reason from L1 |
| food_lot | the consumed lot whose analytes are routed | RUNG_A_LOT |
| aqueous_solutes | markers SALT / ACID among non-food co-members or the cooking liquid lot | MARKER_TABLE_V1 |
| lipid_phase_present | LIPID marker in the medium or co-members, or medium_type ∈ oil classes | MARKER_TABLE_V1 / PHYSICS_V06_L1 |
| contact_phase | AQUEOUS / LIPID / AQUEOUS+LIPID / AIR / UNKNOWN | derived from the two rows above |

Food vs medium rule: a member is the **food lot** if it is a FOOD_MENTION consumed by the heat event and not a marker-only ingredient (salt, vinegar, oil, water, stock); marker-only members form the medium. Merged lots keep both roles explicit instead of collapsing to one product.

## 3. Marker table `registry/composition_markers_v1.csv` (to build; AI_DRAFTED until reviewed)
Columns: `ing_id, canonical_name, marker (SALT|ACID|LIPID|AQUEOUS), basis, source, status`. Seeds: SALT — salt, sea salt, kosher salt, soy sauce, fish sauce, stock cube; ACID — vinegar (all), lemon juice, lime juice, wine, citric acid, tamarind; LIPID — oils, butter, ghee, lard, shortening, margarine, cream; AQUEOUS — water, stock, broth. Built deterministically from ING names, cross-checked with the 7B/72B attribute drafts (agreement used only as a flag), and reviewed by Kush or Parv before any submission figure uses it.

## 4. Acceptance — tomato variants (shared process BOIL, 20 min)
| Variant | members (food lot) | medium aqueous_solutes | lipid_phase | salt / acid / lipid present | contact_phase |
|---|---|---|---|---|---|
| A water | tomato | — | no | F / F / F | AQUEOUS |
| B + salt | tomato | SALT | no | T / F / F | AQUEOUS |
| C + salt + vinegar | tomato | SALT, ACID | no | T / T / F | AQUEOUS |
| D + salt + vinegar + oil | tomato | SALT, ACID | yes (oil) | T / T / T | AQUEOUS+LIPID |
salt_fraction / fat_fraction: UNKNOWN `MASS_NOT_GROUNDED` unless quantities are given; acidity_band: UNKNOWN `NO_SOURCED_PH_TABLE` in v1.

## 5. Full-corpus report (after implementation)
Per family: heat events and boil events with salt_present, acid_present, lipid_present and each combination; share of lots with grounded salt/fat fractions; reasons for UNKNOWN. Counts only committed; rows git-ignored.

## 6. Router hook (next step, after approval)
Composition axes join the existing compatibility check: an EVD row measured on the food alone is DIRECT only when the query lot has no added SALT/ACID/LIPID markers; otherwise it is CONTEXT_MISMATCH (near evidence, not direct). Existing enums only.
