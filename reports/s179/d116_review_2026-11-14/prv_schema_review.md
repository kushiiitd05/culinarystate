# prv review — D-116 CompositionState / MediumState schema v1

Reviewer: prv (AI persona under D-085). Verdict status: **AI_DELEGATED**. This is not human verification and does not count as the "Kush or Parv" review that §3 requires.

## Verdict: ACCEPT_WITH_CHANGES

The cell model (`{"v","b"}` / `{"v":null,"u"}`), additivity, defaulting `acidity_band` to UNKNOWN, and leaving pH, a_w and ionic strength unfilled all fit the stated laws. Two parts break them. The scope of the presence fields contradicts the acceptance table. The acidity rule and the boolean semantics bring in values that have no source.

## Required changes

1. **Lot vs medium scope is contradictory.** §1 computes `salt_present`, `acid_present` and `lipid_present` over the lot's `members`. In §4, though, the food lot is only `tomato` while `salt_present = T`, so the salt has to come from the medium. Pick one scope. Either compute the presence flags and fractions per phase (food lot, medium) or state that CompositionState covers the merged lot plus its medium. `salt_fraction` and `fat_fraction` need their denominator named (food mass, liquid mass, or total). For BOIL, the relevant quantity is medium salinity (g NaCl / g liquid), not a w/w figure over the lot.

2. **A single marker per ingredient is chemically wrong for common items.** Salted butter is LIPID+SALT. Ham, bouillon and commercial stock are AQUEOUS+SALT. Wine is AQUEOUS+ACID, so §2 `contact_phase` misses AQUEOUS for wine-braised foods. Cream is an O/W emulsion, LIPID+AQUEOUS. Make `marker` a set. Add a `role_default` column (MEDIUM_ONLY / FOOD_OR_MEDIUM), because the §2 "marker-only ingredient" list is prose that the §3 table cannot express. Lemon, butter, cream and tamarind can each be the food.

3. **Booleans state more than the evidence supports.** FALSE with basis MARKER_TABLE_V1 only means "no linked member carries a marker". It does not mean "no salt": it misses intrinsic salt (cheese, bacon, canned tomato), and it misses salt added as an ACTION ("salt the water", "season", "oil the pan"), which the coord_food_guard leaves as events. Rename the fields to `*_marker_present`, or add event-derived markers from ACTION verbs. Either way, the basis has to carry the table version and its review status (AI_DRAFTED_NOT_REVIEWED). That status must carry through to every derived row, and submission figures stay blocked until a human reviews the table.

4. **Remove the `acidity_band` heuristic "band of the most acidic member when present in non-trace amount".** It is an invented rule. "Non-trace" has no threshold, and mixture pH is not the minimum of its members: dilution and food buffering both shift it. Allow ACIDIC only from a sourced mixture pH, or from a sourced pH of the bulk medium liquid itself. Otherwise the value is UNKNOWN `MIXTURE_PH_NOT_COMPUTED`. Also note that 4.6 is a food-safety boundary (C. botulinum). The schema has to justify it as a chemistry routing cut-off for each analyte, or label it as a safety band.

5. **The `salt_fraction` definition needs explicit limits.** Na × 2.54 counts all sodium as NaCl, including MSG, bicarbonate and sodium intrinsic to the food. Rename the field `sodium_as_NaCl_equiv`. State that it is *as added*, not *as retained* (draining and leaching are not modelled). Fix the units (g/g, with SR in mg/100 g) and the SR release/version in the basis. Apply the same as-added caveat to `fat_fraction`, since oil left in the pan or drained is not in the food.

6. **`phase_solid` cannot be derived.** The marker table has no SOLID marker, and `NO_MARKER` is listed as an UNKNOWN reason. The booleans, however, treat a missing marker as "not salt/acid/lipid". Define the rule explicitly, for example: a FOOD_MENTION with no marker goes to phase_solid with basis `DEFAULT_RULE_V1`. Or leave the field UNKNOWN. The same missing marker cannot count as UNKNOWN in one field and FALSE in another.

7. **Temporal ordering and guard error are not modelled.** "One per lot × event" does not say that only members added *before or during* the heat event count. Salt added at serving must not mark the BOIL row. Add an `added_at_event` constraint and an acceptance case for it. Rung A also depends on coord_food_guard, whose precision in prv's 50-item audit is 0.915 (Wilson 95% 0.80–0.97). About 1 in 12 promoted members can be verbs (fry, sprinkle) or modifiers ("dried", "salt cod", "seasoning salt"). Add acceptance cases for these negatives. Also record `member_source = GUARD_PROMOTED` so the router can tell these members apart.

8. **The router hook is asymmetric.** "DIRECT only when the query lot has no added SALT/ACID/LIPID" makes variant B CONTEXT_MISMATCH even against EVD rows measured in salted water, which is a common literature protocol. Compare the query composition with the EVD row's composition, which must be stored in the same fields. Mark DIRECT only when they match. Use CONTEXT_MISMATCH when they differ or when the EVD composition is UNKNOWN. Include the identity of the AQUEOUS medium (water vs stock vs wine) in that comparison.

## Minor (non-blocking)
- §3 lists columns `basis, source`. The delivered `composition_markers_v1.csv` has `rule, llm_acidic_7b_72b` instead, with no `source`, so the table does not match its schema.
- Seed items named in §3 are absent from the table: sea salt, kosher salt, stock cube, broth, cream.
- `canonical_name` "glass red wine" shows a unit leaking into the ING name during normalisation.
- The LLM "acidic" drafts flag several oils YES/YES (chilli, crispy chilli). Agreement between the drafts is no evidence of correctness, so keep it as a flag only.
