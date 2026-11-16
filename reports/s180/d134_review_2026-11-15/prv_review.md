# prv review: D-134, lineage vNext promoted for State v2

Reviewer: prv (AI persona, decision D-085). Status: **AI_DELEGATED**. Not human verification.
Instruction: Kush, 15 Nov 2026, "if any needs review then use prv and ksh".

## Verdict: APPROVE_AS_DIAGNOSTIC

Agree with ksh. Adding the cooking-side reasoning, because the three behaviours are not equally safe
and the record should say so.

## Where I agree without reservation

`VNEXT_MIXTURE_COREF` and `VNEXT_ALTERNATIVE_SKIPPED` are straightforward corrections. Reading "or"
as "and" is wrong in every cuisine, and binding "the mixture" to one of its components is wrong
regardless of what the mixture is. Neither needs a gold set to justify; they fix statements that were
false on the text.

## Where I want the record to be more careful

`VNEXT_FAT_STAYS` is the right lineage choice but it is the one with a physical claim hiding behind
it, and 68,868 recipes carry it.

Keeping frying fat in the food's lot is conservative **for lineage** — it stops asserting a
separation the text never states. But downstream it means the lot's composition now includes the
whole frying medium, and `lipid_present` rises (82.5% → 83.2% is consistent with that). For a deep
fry that is physically wrong in the other direction: a battered item leaving a fryer carries a few
percent of oil by mass, not the bath. Oil uptake is largely a surface and cooling-phase phenomenon,
and the drain or rest step matters more than the fry itself.

So the correct reading is: **`lipid_present = true` after a fry is a contact fact, not a quantity
claim.** The fat fraction stays UNKNOWN `MASS_NOT_GROUNDED`, which it does, and that is what keeps
this honest. My concern is only that a reader of the report will see "fat stays in the lot" and infer
the system thinks the food absorbed the oil. One sentence in the report prevents that.

## Changes

1. **State that `VNEXT_FAT_STAYS` changes contact, not quantity.** `lipid_present` becomes true;
   `fat_fraction` stays UNKNOWN. Without that sentence the 82.5% → 83.2% delta invites the wrong
   reading.

2. **Do not use the 29.3% figure without the word DIAGNOSTIC in the same sentence.** It is the most
   quotable number in the project and the most likely to be lifted into a slide on its own.

3. **Spot checks should be named as Wikibooks-only and unsampled.** If a later reader wants to know
   how much to trust the 29.3%, "spot checks consistent with the intended fixes" is not enough on its
   own; say how many and from where, or say they were informal.

## On the human gate

I cannot close it. Under D-085 I am an AI persona and this decision governs the submission headline
rerun. If one human act is bought before 19 Nov, I would spend it here rather than on the pH
crosswalk: the pH bands touch one axis, this touches 29.3% of every recipe in the corpus.
