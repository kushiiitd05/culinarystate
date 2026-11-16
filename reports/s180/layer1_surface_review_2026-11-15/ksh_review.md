# ksh review: narrow the Layer-1 proposable surface to one field

Reviewer: ksh (AI persona, decision D-085). Status: **AI_DELEGATED**. This is not human verification
and does not meet a "reviewed by Kush or Parv" gate. Instruction: Kush, 15 Nov 2026, "if any needs
review then use prv and ksh".

Reviewing `reports/s180/layer1_proposable_surface_proposal_v1.md`.

## Verdict: ACCEPT_WITH_CHANGES

P1 and P2 are correct and should land before the 19 Nov freeze. The diagnosis in §2 is the strongest
part of the document: a reference field with no referent and no consumer cannot be validated by a
non-blank string check, and the step-7 values prove the hole was live rather than theoretical. P3 is
the right consequence and must not be softened. Four changes below; changes 1 and 2 must land with
the implementation, 3 and 4 before any figure or deck slide uses these numbers.

## Changes

1. **Do not answer review question 1 with a closed vocabulary of condition kinds.** The proposal
   offers that as an alternative and it must be refused explicitly, not left open. A vocabulary like
   `{OVEN_BAKE, OIL_FRY, SIMMER_COVERED}` would duplicate information the rules already derive
   deterministically and better: `Q.medium`, `Q.lid_state`, `G.family`, `G.process` and
   `Q.start_mode` are all populated from cues, with a basis on each cell. Asking a model for
   `OIL_FRY` when `Q.medium` already says `OIL` from a cue span is not a Layer-1 proposal, it is a
   second, unsourced opinion about a cell that already has a provenance. That is a second
   implementation of state in all but name, which the freeze forbids. State the refusal in the
   decision record so it is not revisited.

2. **`FIELD_REQUIRES_EXISTING_REFERENT` must be checked before field licensing, for the same reason
   the numeric prohibition is.** The proposal does not say where in `_reject` the new code goes.
   Precedent is already set at `layer1_proposer.py:115-118`: the absolute prohibition is checked
   first so the refusal reports the real cause rather than an incidental one. A proposal of
   `condition_profile_id` under a trigger that no longer licenses it would otherwise be reported as
   `FIELD_NOT_LICENSED_BY_TRIGGER`, which is now a misleading code — it implies some other trigger
   could license it, and none can. Order: not-proposable, numeric, requires-referent, licensing,
   event-in-graph.

3. **The re-scored 39 → 13 and 24 → 1 figures need a stated denominator, or they will read as a
   regression.** As written they look like the arm got worse. They are not comparable to the recorded
   numbers, because the recorded numbers counted a field that should never have been on offer. Report
   them as "accepted proposals on the surface that remains licensed", give the returned count on that
   same surface, and keep the recorded 39 and 24 visible beside them with the reason for the
   difference. A single arrow with no denominator is the kind of number that ends up on a slide
   without its caveat.

4. **Say what Layer-1's measured contribution now is, in one sentence, in the report.** Under P4 the
   LLM's licensed surface is one field on one trigger, and on the sealed set that produced 13 accepted
   proposals from 60 hard cases with no gold to score them against. That is the honest headline for
   the LLM layer and it should be written down plainly rather than inferred by a reader from two
   tables. It is also a defensible result: it is what "rules first, LLM proposes only on ambiguity,
   validator decides" is supposed to converge to.

## On review question 2

Acceptable, and preferable to the alternative. Shipping a frozen architecture whose LLM layer earns
its acceptance rate by writing nouns into a referenceless field would be the worse outcome by a
distance, because the number would survive into the report as evidence of something it is not. A
small honest surface is defensible at a viva; a large unvalidated one is not.

## On review question 3

P2 does not need its own decision record. The flag is raised after the rule has already committed the
merge, so licensing it was a defect in the CR-25 licensing table, not a change of policy. Note it in
the CR-25 entry and in the worklog. P1 and P3 together **do** need a decision record, because P3
changes what the system will claim it can do.

## On review question 4

Both, in this order: recorded numbers first as the registered result, then the re-scored numbers
labelled as a re-scoring of recorded data with this proposal cited. Dropping the recorded numbers
would breach the pre-registration rule that old results are kept.

## Not in scope but flagged

`alternative_group` has no closed vocabulary either, and §6 admits it. The V4 check is structural
(mutual exclusivity), so two runs can label the same group `"filling"` and `"sugar_or_milk"` and both
pass. With the surface reduced to this one field, that is now the **only** place a semantic gap
remains, and it carries the whole LLM layer. It needs a stated position before the freeze even if the
position is "accepted as a free label, never used as an identifier".
