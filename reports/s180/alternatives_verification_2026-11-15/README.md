# Human verification packet: `alternative_group` proposals

**For Kush and Parv. This is the one human act that would let step 7 say anything about correctness.**
Created 15 Nov 2026. 20 rows of reading in total.

## Why this packet exists

After the Layer-1 surface was narrowed (`reports/s180/layer1_proposable_surface_proposal_v1.md`,
reviewed ACCEPT_WITH_CHANGES by ksh and prv), the LLM's entire licensed surface is **one field**,
`alternative_group`, on **one trigger**, `VNEXT_ALTERNATIVE_SKIPPED`. On the 60 sealed cases, 18 have
that trigger among those fired and 15 have it as primary.

`alternative_group` has **no closed vocabulary**. V4 checks only that members of one group are
mutually exclusive (`ALTERNATIVE_GROUP_TREATED_AS_CONJUNCTION`) — a structural check, not a semantic
one. So the gate cannot tell a real choice from a label that merely looks like one, which is the same
class of gap that `condition_profile_id` had, now confined to one field.

There is **no gold** on these cases. Without this packet, nothing in step 7 can be called correct.

## The two files

**`alternatives_to_verify.csv`** — 14 accepted proposals (13 from prompt v1, 1 from v2). For each:
pageid, revid, url, event id, proposed value, span. Fill `ksh_verdict` and `prv_verdict` with one of:

| Verdict | Meaning |
|---|---|
| `REAL_CHOICE` | the text offers A or B and this value names that choice |
| `NOT_A_CHOICE` | the value names an object, a time or a process, not an alternative |
| `REAL_CHOICE_WRONG_LABEL` | there is a choice here, but this value misnames it |
| `UNCLEAR` | the text does not settle it |

**`alternatives_cases_with_no_proposal.csv`** — 6 eligible cases where no proposal was accepted. Fill
`ksh_is_there_a_real_choice` / `prv_is_there_a_real_choice` with `YES` / `NO` / `UNCLEAR`. This
measures the other error direction: a decline on a case that did contain a choice.

## What the agent already noticed, and why it is not a result

Reading the 14 values, they appear to fall into two groups:

- plausibly real choices: `cooking_or_freezing`, `fat_or_butter`, `pan_or_wok`,
  `potatoes_or_meat_onions`, `sauce_or_ketchup`, `smooth_or_coarse`, `baking_soda_or_yeast`
- apparently not choices at all: `flaky_pie_crust`, `egg sauce`, `marinade_time` (×2), `niter_qibe`,
  `simmer_time`, `fish_stock_cube`

**This is the coding agent's inspection, not a measurement, and it is not gold.** It is recorded so
the packet is honest about prior expectation, and so a verdict that disagrees with it is visibly a
disagreement rather than a surprise. Do not treat the `_or_` substring as a scorer: it is a surface
pattern, it would pass `marinade_or_time`, and using it would make the result circular.

## What a completed packet licenses, and what it does not

**Licenses:** a stated per-proposal correctness rate on this one field, with the denominator (14
proposals, 18 eligible cases, 60 sealed cases). That is a real, reportable number for the LLM layer.

**Does not license:** calling any arm "better", comparing 7B against 72B on accuracy, or extending
the verdict to the triggers that now license nothing. Those remain DIAGNOSTIC and ungraded, per §5 of
`step7_sealed_comparison_preregistration.md`.

## Independence

ksh and prv must fill their columns **without reading each other's**, and disagreements are kept
rather than resolved by the agent. If both columns are completed by the same person, say so in `note`:
it is still worth more than nothing, but it is one reader, not two.
