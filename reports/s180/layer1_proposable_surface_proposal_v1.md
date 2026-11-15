# Proposal: narrow the Layer-1 proposable surface to one field

**Status: PROPOSED, awaiting review.** Written 15 Nov 2026 by the coding agent from the step-7 result
(`reports/s180/step7_analysis_2026-11-15.md`). Nothing is implemented. This is a **tightening**: it
removes licensed surface from the LLM and adds no component, so it is inside the 15 Nov freeze and
maps to the existing CR-25 / owner-step 36A.3 work. No new master plan, no new architecture name.

## 1. What step 7 found

Across three runs over the same 60 sealed cases (7B prompt v1, 7B prompt v2, and the voided 20-case
72B partial), there was **zero `(event_id, field)` slot agreement in every pair**. Accepted values for
`condition_profile_id` included `"pan"`, `"dish/pan"`, `"chicken"`, `"oil"`, `"bowl_content"`,
`"dates_seeds"`, `"boiling_time"`, `"bake"`, `"fried"`, `"cooked"` — ingredient names, vessel names,
process names and duration references, all accepted as a condition profile.

The gate accepted every one of them, correctly by its own rules: the value is categorical, non-numeric,
span-grounded, trigger-licensed and introduces no new V4 issue code.

## 2. Why that happened — the real cause

`condition_profile_id` is a **reference field with no referent and no consumer.**

- Declared on `EventCandidate` (`extraction/interfaces.py:541`) as a CR-25 field, documented in
  `docs/EVENT_IR_CONTRACT.md`.
- **Nothing in `src/` reads it.** Grep finds only its own declaration, its `__post_init__` non-blank
  check, and the proposer.
- The 36-step plan (§ step 16, v2 plan L709) defines it as `condition_profile_id → 07H COND`, i.e. a
  pointer to a condition record with per-axis `MEASURED / RANGE / UNKNOWN / NOT_APPLICABLE`.
- The populated condition identity in this repo is a different, existing thing: `condition_id` on
  evidence COND records (`evidence/evd_export.py`, `evidence/condition_audit_packet.py`,
  `transition/dataset.py`). **No COND records are minted on the recipe side.**

So a *valid* value of `condition_profile_id` is an **id of an existing profile**. There are none for
recipe events. A model cannot mint a reference, and a non-blank string check cannot tell a reference
from a word lifted out of the sentence. Every accepted `condition_profile_id` in step 7 was the
latter. This is the same class of hole amendment A1 closed one level up: A1 stopped an unlicensed
*field*; nothing stopped a **non-referential value in a reference field**.

## 3. Proposal

**P1. Remove `condition_profile_id` from `PROPOSABLE_FIELDS`.** A reference may only be proposed when
the referent exists and is enumerable. New rejection code `FIELD_REQUIRES_EXISTING_REFERENT`, so the
refusal states its reason rather than looking like a vocabulary miss. The field stays on the Event IR,
declared and unpopulated, which is its honest state.

**P2. Remove `VNEXT_FAT_STAYS` from the proposable trigger set.** The flag is raised at
`extraction/rung_a_binding.py:324` *after* the rule has already decided: frying fat and food merge
into one `MIXTURE` lot. There is no open question for a model to answer. Step 7 confirms it — over 9
`VNEXT_FAT_STAYS` cases, v1 returned 2 proposals (both unlicensed, both rejected) and v2 returned 0.
Zero acceptances was the model correctly having nothing to say, not a failure.

**P3. Consequence, stated plainly.** `AMBIGUOUS_ACTION`, `AMBIGUOUS_ANTECEDENT`,
`AMBIGUOUS_CANDIDATES`, `AMBIGUOUS_OR_MISSING`, `AMBIGUOUS_REFERENCE`, `UNRESOLVED_LOT` and
`VNEXT_MIXTURE_COREF` licensed **only** `condition_profile_id`. Under P1 they license nothing, so they
become **declared-open, rules-only** flags: the ambiguity is recorded and left UNKNOWN rather than
answered by a model.

**P4. Net Layer-1 LLM surface:** one field, `alternative_group`, on one trigger,
`VNEXT_ALTERNATIVE_SKIPPED`. Everything else is rules plus an explicit UNKNOWN.

## 4. Why the coreference triggers cannot be rescued

A reviewer should expect the objection that `AMBIGUOUS_REFERENCE` and `VNEXT_MIXTURE_COREF` are
genuine *text* questions a language model is good at. They are. But their answer is **an entity**, so
writing it means binding `consumes` / `produces` / `parent_entity_ids` — and the step-7
pre-registration §4 states that `produces` / `consumes` are **never** proposable. The answer has no
licensed destination. Routing it into `condition_profile_id` instead is precisely the smuggling A1
was written to stop, one level deeper.

So the honest position is: Layer-1 can *detect* these ambiguities deterministically and must report
them as UNKNOWN with a reason. It cannot resolve them until there is a licensed, referential
destination for the answer.

## 5. Effect on the step-7 numbers

Re-scoring the **existing, unchanged** result files under P1+P2 (old results kept, per the
pre-registration):

| | accepted as recorded | accepted under P1+P2 |
|---|---|---|
| 7B prompt v1 | 39 | **13** (`alternative_group` only) |
| 7B prompt v2 | 24 | **1** |

This is a re-scoring of recorded data, not a re-run, and must be labelled as such wherever it appears.
It does not change any committed JSON.

It also makes the arms interpretable for the first time: with one field and one trigger, a 72B re-run
measures something real, because an arm can no longer earn acceptance by filling a referenceless field
with a noun from the sentence.

## 6. What this does not claim

- Not an accuracy result. There is still **no gold** on the 60 cases; §5 of the pre-registration stands.
- Not a judgement on any model. The 72B question is open, and its run is void at 20/60.
- `alternative_group` is **not** validated either. It has no closed vocabulary; it is a grouping label
  whose only requirement is that members of one group are mutually exclusive, which V4 now checks
  (`ALTERNATIVE_GROUP_TREATED_AS_CONJUNCTION`). That check is structural, not semantic.

## 7. Questions for review

1. Is P1 right, or should `condition_profile_id` instead stay proposable against a closed vocabulary
   of *condition kinds* (e.g. `OVEN_BAKE`, `OIL_FRY`, `SIMMER_COVERED`) rather than references?
2. Is P3 acceptable before the 19 Nov freeze, given it reduces the LLM's demonstrated contribution on
   this corpus to one trigger?
3. Does P2 need a decision record, or is it a defect fix inside CR-25?
4. Should the re-scored step-7 numbers enter the report, or only the recorded ones with this proposal
   cited?
