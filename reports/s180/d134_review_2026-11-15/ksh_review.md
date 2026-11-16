# ksh review: D-134, lineage vNext promoted for State v2

Reviewer: ksh (AI persona, decision D-085). Status: **AI_DELEGATED**. Not human verification.
Instruction: Kush, 15 Nov 2026, "if any needs review then use prv and ksh".

D-134 (2026-11-14) promoted `RungA(coord_food_guard=True, lineage_vnext=True)` for State v2, RAG
packet v2 and the submission headline rerun. It was entered by the coding agent as scribe with **no
approver line**, which `tools/s179_gate_provenance_report.py` classes `NO_APPROVER_LINE` — the only
such entry in 115 decisions.

## Verdict: APPROVE_AS_DIAGNOSTIC, with the wording constraint below

The promotion is sound as an engineering default and must not be described as validated.

**Why approve.** The three vNext behaviours each correct a defect that is demonstrable on the text,
independent of any aggregate:

1. `VNEXT_FAT_STAYS` (68,868) — frying fat was being split into its own lot, so the food's lot lost
   the fat it is cooked in. Keeping one `MIXTURE` lot is the conservative choice: it does not claim
   how much fat transfers, it only stops asserting a separation the recipe never states.
2. `VNEXT_MIXTURE_COREF` (140,828) — a later reference to a mixture was binding to a component
   instead of the mixture. That is a lineage error with a wrong answer, not a judgement call.
3. `VNEXT_ALTERNATIVE_SKIPPED` (48,520) — "A or B" was being read as both, which V4 now refuses
   outright as `ALTERNATIVE_GROUP_TREATED_AS_CONJUNCTION`. Promoting vNext and keeping the old
   behaviour would leave the pipeline in a state the validator rejects.

Point 3 is the decisive one: with the invariant in place, not promoting vNext is not a neutral
option.

**Why it is not validated.** 29.3% of recipes change and the run completed corpus-wide with 0
exceptions, but there is **no gold regression set**, so no part of that 29.3% is known to be an
improvement. The aggregate deltas (events −0.10%, produced lots −1.11%, heat food-events +1.00%,
salt-context 66.9% → 66.3%) are consistent with the intended corrections and consistent with nothing
else being checked. Spot checks were on Wikibooks only and were not sampled to a protocol.

## Required wording constraint

Anywhere this promotion is reported, the three words "clean", "validated" and "verified" must not be
used of it. Permitted form: **DIAGNOSTIC, with aggregate behaviour consistent with the intended
corrections, no gold regression set.** This repeats Kush's 15 Nov standing instruction and is recorded
here so the constraint travels with the approval rather than sitting only in the directive.

## Changes

1. **The approver line must say what kind of approval this is.** Record it as
   `ksh+prv (AI, D-085) on Kush's instruction of 15 Nov 2026` — not as Kush or Parv. The gate
   provenance report will then class it `AI_DELEGATED_D085` and the count will read HUMAN 80 /
   AI_DELEGATED 21, which is the true state. An approval that reads as human when it is not would
   defeat the purpose of the report.

2. **A human sign-off is still owed before submission and must stay on the open list.** This approval
   unblocks the test and the build; it does not close the gate for a submitted artifact. D-085 is
   explicit that AI review is not human verification, and this decision governs the headline rerun.

3. **Add the 0-exception claim's scope.** "Completed corpus-wide without exceptions" means no
   process raised an exception over 611,902 recipes. It does not mean no recipe was parsed wrongly.
   Say "no exceptions raised" rather than "without exceptions", which reads as "nothing went wrong".
