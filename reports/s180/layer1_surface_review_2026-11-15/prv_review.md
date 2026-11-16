# prv review: narrow the Layer-1 proposable surface to one field

Reviewer: prv (AI persona, decision D-085). Status: **AI_DELEGATED**. Not human verification; does not
meet a "reviewed by Kush or Parv" gate. Instruction: Kush, 15 Nov 2026, "if any needs review then use
prv and ksh".

Reviewing `reports/s180/layer1_proposable_surface_proposal_v1.md`.

## Verdict: ACCEPT_WITH_CHANGES

Agree with P1 and P2. I disagree with the proposal on one substantive point (change 1) and think §4
overstates its case. The cooking content is where I can add something, so most of this is about
whether the triggers being closed off are really unanswerable, and whether the one surviving field is
the right one to keep.

## Changes

1. **§4 is too strong. A coreference answer is not always an entity.** The proposal says the answer to
   `AMBIGUOUS_REFERENCE` is "an entity, so writing it means binding consumes / produces". That is true
   for most of these cases but not all. In recipe prose a large share of ambiguous references resolve
   to a **container or a medium**, not to a food lot: "return it to the pan", "pour off the liquid",
   "cover and set aside". The step-7 values show the model reaching for exactly that — `"pan"`,
   `"dish/pan"`, `"bowl_content"` were rejected as condition profiles but they are not nonsense, they
   are vessel answers to vessel questions. Those have a legitimate destination that is not
   `consumes`/`produces`: the medium and lid cells. But those cells are **already filled
   deterministically from cues** with a basis (`Q.medium`, `Q.lid_state`), so a model answer there
   would be a second opinion on a sourced cell, which ksh's change 1 rightly refuses. So P1 still
   stands — but the *reason* in §4 should be corrected to "the answer's destination is either an
   allocation, which is never proposable, or a cell the rules already fill with a basis", rather than
   claiming every answer is an entity. Getting the reason right matters because the wrong reason
   invites someone to re-open this by finding a counterexample.

2. **P2 is right, and the cooking reason is stronger than the one given.** The proposal justifies
   removing `VNEXT_FAT_STAYS` procedurally (the rule already decided). The physical reason is better:
   whether frying fat stays with the food is not a question about the *text* at all, it is a question
   about mass transfer, and it has a real answer that varies with the food, the temperature and the
   drain step — oil uptake in a fried potato is largely a surface and cooling-phase phenomenon, not a
   lineage label. A model reading one sentence cannot know it and the recipe does not state it. The
   D-132 B rule keeps the fat in the lot, which is the conservative choice and the right one for a
   lineage graph, but the honest statement is that the *quantitative* question is unanswered and
   belongs to the simulator, not to Layer-1. Put that in the record so it is not mistaken for a
   resolved physical claim.

3. **Keep `VNEXT_ALTERNATIVE_SKIPPED` but state what the label means, because the cooking cases
   differ in kind.** The 48,520 corpus flags are not one phenomenon. At least three kinds appear:
   true substitutions where either branch gives a comparable dish (butter or oil for frying,
   sugar or honey), **non-equivalent** alternatives where the choice changes the chemistry
   materially (lemon juice or vinegar is an acid swap with different pH and flavour volatiles;
   water or stock changes the salt context), and garnish-level options that barely matter. V4 only
   checks that group members are mutually exclusive. If `alternative_group` is carrying the whole
   LLM layer, the report must say it is a **grouping label, not an equivalence claim** — otherwise a
   reader will take "alternatives" to mean the branches are interchangeable, which for an acid swap
   is wrong and would propagate into the salt/acid context cells.

4. **Check the 15 `VNEXT_ALTERNATIVE_SKIPPED` cases by hand before the freeze, or say they were not
   checked.** This is now the only trigger with a licensed destination and 13 accepted proposals rest
   on it. 15 cases is a small enough number for a real human read, and it is the one place where
   human verification would change what the report can say. I cannot do it: I am an AI persona under
   D-085 and this is exactly the kind of judgement D-085 says does not substitute for Kush or Parv.
   Flag it as owed.

## On review question 1

Refuse the closed vocabulary of condition kinds, for ksh's reason and one more: a condition profile in
this project is defined per-axis with a status per axis (MEASURED / RANGE / UNKNOWN / NOT_APPLICABLE).
A flat label like `SIMMER_COVERED` collapses several axes into one token and loses the per-axis
UNKNOWN, which is the single most important property of the representation. It would be a step
backwards from the state we already compute, not a gap being filled.

## On review question 2

Acceptable. One caution: do not let "the LLM layer is small" slide into "the LLM layer is unnecessary"
in the write-up. Detection of these ambiguities is deterministic and cheap, but the *reason* the
surface is small is that the destinations do not exist yet, not that the questions are uninteresting.
`AMBIGUOUS_REFERENCE` at 15 of 60 primary triggers is a real and common phenomenon in recipe prose and
leaving it UNKNOWN is a stated limitation, not a solved problem.

## On review question 4

Agree with ksh. Recorded first, re-scored second and labelled.
