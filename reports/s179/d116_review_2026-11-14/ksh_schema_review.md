# ksh review: D-116 CompositionState / MediumState schema v1

Reviewer: ksh (AI persona, decision D-085). Status: **AI_DELEGATED**. This is not human verification and does not meet the "reviewed by Kush or Parv" gate in §3.

## Verdict: ACCEPT_WITH_CHANGES

The design holds up. C_t is additive, fractions are UNKNOWN by default (`MASS_NOT_GROUNDED`, `NO_SOURCED_PH_TABLE`), mixture pH, a_w and ionic strength are never filled, and the router hook only reuses existing enums. Four rules still break the stated laws ("no invented values; UNKNOWN valid; every field value+basis or UNKNOWN+reason"). They let a `false`, a mixture band or a role be written with no basis behind it. Changes 1, 3, 5 and 7 must land before implementation. Changes 2, 4, 6 and 8 should land before any full-corpus figure.

## Changes

1. **Stop treating absence from the marker table as `false`.** At present `salt_present`, `acid_present` and `lipid_present` become `false` whenever no member is marked, so a linked member with no marker row counts as evidence of absence. The table is AI_DRAFTED and incomplete: sea salt, kosher salt, stock cube, broth and cream are §3 seeds that are missing from `composition_markers_v1.csv`. That gap would produce invented `false` values (for example, sea salt in boiling water would give salt_present = F). Rule: `false` only when every member is linked **and** has a reviewed marker decision, with an explicit `NONE` marker row for marker-free foods. Otherwise UNKNOWN with `NO_MARKER` or `MARKER_NOT_REVIEWED`, in addition to `MEMBER_UNLINKED`.

2. **Make `marker` a set, not a single value.** Many common ingredients carry two phases or solutes: soy sauce (SALT+AQUEOUS), grape wine (ACID+AQUEOUS), stock and ham stock (AQUEOUS+SALT), salted butter (LIPID+SALT), cream and coconut milk (LIPID+AQUEOUS), Worcestershire (SALT+ACID+AQUEOUS). With one marker the table has to pick, which silently drops a true `*_present` or a phase. Two items in the marker review (bouillon, Shaoxing wine) were rejected partly because of this limit. Use a `markers` column of type set[SALT|ACID|LIPID|AQUEOUS|NONE] and derive the phase lists from it.

3. **Remove the "most acidic member" rule from `acidity_band`.** Taking the band of the most acidic member present in a "non-trace amount" is an invented mixture value. Mixture pH depends on dilution and on buffering by the food: a tablespoon of vinegar in 2 L of water with tomatoes is not "ACIDIC" just because vinegar is. "Non-trace" is also an undefined threshold. The rule also contradicts the reason `MIXTURE_PH_NOT_COMPUTED`. Split it into two fields. Member level: `member_ph_band` per member, from a cited pH table. Lot level: `acidity_band`, which stays UNKNOWN `MIXTURE_PH_NOT_COMPUTED` unless there is a cited measured pH for the mixture. Rename `LOW_ACID` to `PH_GE_4_6`: "low-acid food" is a regulatory class that also needs a_w > 0.85, and a_w is never filled.

4. **Pin down the scope, timepoint and basis of `salt_fraction` and `fat_fraction`.**
   - Scope: say whether the denominator is the food lot, the medium, or the whole pot. In a boil, salt in the water is not salt in the tomato.
   - Timepoint: as added, before the event. Evaporation and absorption are not modelled.
   - Naming: call the field `nacl_equiv_fraction`. Na × 2.54 counts every source of sodium (MSG, baking soda, soy sauce) as NaCl.
   - Basis: record the SR/FDC row id and dataset release for each member. A generic SR row standing in for a branded product (salted vs unsalted stock can differ about tenfold) is a scenario, so keep the `SCENARIO` label visible downstream.

5. **Make the food vs medium role an explicit field with a basis.** Add `role ∈ {FOOD, MEDIUM, UNKNOWN}` per member, with a basis. Today the role comes from the "marker-only" list and `phase_solid` comes from having no marker. That breaks for ingredients that can be either: butter in a roux, reduced cream, roasted lemon, tamarind pulp, wine reduced into a sauce. Put the default role in a marker-table column (`role_default`). When the event or text does not settle the role, write UNKNOWN `ROLE_AMBIGUOUS` instead of guessing. Fill `phase_solid` from role = FOOD, not from a missing marker. The §2 phrase "non-food co-members" should then refer to role = MEDIUM.

6. **Give `contact_phase` an explicit truth table.** The stated input, "the two rows above", lists only SALT and ACID solutes, so AQUEOUS cannot come from it. In variant A, AQUEOUS actually comes from `medium_type` = WATER. Spec it as a function of (`medium_type`, AQUEOUS markers in the medium, LIPID markers in the medium):
   - WATER, STEAM or LIQUID → AQUEOUS
   - OIL_IMMERSION or PAN_CONTACT_OIL → LIPID
   - OVEN_AIR → AIR
   - AQUEOUS plus a LIPID marker → AQUEOUS+LIPID
   - `medium_type` UNKNOWN → UNKNOWN, carrying the L1 reason

   Say how to handle a pan with oil plus a liquid such as wine or stock.

7. **Make the router hook handle UNKNOWN and compare both sides.** An UNKNOWN `*_present` must never yield DIRECT. Route it to CONTEXT_MISMATCH, or to the existing UNKNOWN or near-evidence path. The hook also assumes the EVD row was measured on the food alone. Record the EVD's own composition context (for example, "boiled in 1% NaCl") and compare it with the query lot, so that a salted EVD row matched to an unsalted query is not DIRECT either.

8. **Bring the marker table in line with the spec and add negative tests.**
   - The CSV has `rule, llm_acidic_7b_72b, status` but §3 specifies `basis, source`. Add `source` (citation or `NAME_RULE_V1`), the `markers` set, and `role_default`.
   - Define a status enum (`AI_DRAFTED_NOT_REVIEWED`, `AI_DELEGATED_REVIEWED`, `HUMAN_VERIFIED`) and allow only `HUMAN_VERIFIED` rows into submission figures.
   - Add the missing §3 seeds.
   - Extend the §4 acceptance tests beyond the positive cases: an unlinked member (expect UNKNOWN), a linked member with no marker (expect UNKNOWN, not F), a two-marker ingredient (salted butter), a role-ambiguous member, and one grounded-mass case whose expected `nacl_equiv_fraction` is computed from cited SR rows.

## Notes (no change requested)
- The 7B/72B agreement is used only as a flag, which is correct. In the marker table its "acidic YES" votes on chilli, truffle, walnut and basil oils are spurious, which shows why it must not serve as a basis.
- "Never filled in v1" (mixture pH, a_w, ionic strength, texture, colour) is the right scope.
