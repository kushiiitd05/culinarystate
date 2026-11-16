# ksh and prv as separate raters: where they disagree is the finding

**`AI_DELEGATED_D085` · `NOT_INTER_RATER` · `NOT_GOLD` · personas, not people.** 16 Nov 2026, on
Kush's instruction *"use ksh and prv for those packets"*. Verdicts:
`ai_dual_verdicts_72b_v3_D085.csv`, 21 rows, the grounded 72B v3 set.

**Column naming is deliberate.** The verdicts are in `ksh_AI_persona_verdict` and
`prv_AI_persona_verdict`. The human columns are `kush_HUMAN_verdict` and `parv_HUMAN_verdict` and
they are **empty**. The original packet's `ksh_verdict` / `prv_verdict` columns were left untouched.
Writing an AI verdict into a column a reader would take for a person's is the provenance failure this
project's laws exist to prevent, and the shared "ksh/prv" shorthand makes it easy to commit by
accident.

## The two lenses

- **ksh — contract and structure.** Is this a well-formed alternative *group*, correctly labelled,
  not a duplicate?
- **prv — cooking and chemistry.** Is this a real culinary choice, and **does the branch change
  anything** in the process or the resulting food?

## They agree on 12 of 21 (57%)

| | REAL_CHOICE | SLOT_LABEL | NOT_A_CHOICE | DUPLICATE |
|---|---|---|---|---|
| **ksh** | 9 | 8 | 2 | 2 |
| **prv** | 15 | — | 5 | 1 |

**57% is not inter-rater reliability and must never be reported as such.** Two personas of one model
share a prior; this project set 07.A-R1 to NOT_RUN for exactly that reason. The number is reported
because the *pattern* of divergence is informative, not because the rate is.

## The disagreement is not noise — it exposes a missing distinction

Every one of the 9 divergences sits on ksh's `SLOT_LABEL` (or a duplicate call), and prv splits that
same set in two directions:

**prv says REAL_CHOICE where the branch changes the cooking:**

| Row | Value | prv's reason |
|---|---|---|
| V3-014 | `salad_type` | lettuce vs cabbage changes water release into the dressing |
| V3-020 | `blend_texture` | smooth vs coarse changes surface area, so the sauce reduces differently |
| V3-008 | `sauce_choice` | egg sauce / palm oil / pepper sauce are different accompaniments, not one slot |
| V3-016 | `butter_or_oil` | the niter qibe sentence is a separate conditional, not a repeat |
| V3-003, V3-004 | garnish / bread | real branches, slot-naming is acceptable shorthand |

**prv says NOT_A_CHOICE where nothing in the process changes:**

| Row | Value | prv's reason |
|---|---|---|
| V3-007 | `serving_options` | "honey, jam, tea, or savoury" is a serving suggestion; no step changes |
| V3-013, V3-019 | garnish | parsley or cilantro: no process consequence |

**The finding: "is this an alternative?" and "does the alternative matter?" are different questions,
and `alternative_group` has one field for both.** A garnish choice and a leavening swap are
structurally identical to the schema and nothing downstream can tell them apart — yet
`yeast_or_baking_soda` changes the chemistry (biological and slow versus chemical and immediate)
while `parsley_or_cilantro` changes nothing the state tracks.

This is recorded, **not fixed**. Adding a consequence flag would be a schema change three days before
the freeze, driven by an AI-delegated reading with no human verdict behind it.

## What this does for the human packet

**It cuts the work from 21 rows to 9.** The 12 rows where both personas agree need a spot-check at
most. The 9 divergent rows are where a human judgement actually decides something, and they are
listed above.

That is the honest value of this pass: it is **triage**, not verification. It tells Kush and Parv
where to look. It does not tell anyone what is true, and the report may not quote 57%, 15/21 or 9/21
as a correctness figure.
