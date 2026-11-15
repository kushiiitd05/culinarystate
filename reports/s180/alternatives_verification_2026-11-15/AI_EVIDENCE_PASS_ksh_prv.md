# ksh + prv evidence pass on the 14 `alternative_group` proposals

**Status: `AI_DELEGATED_D085` · `NOT_HUMAN_VERIFIED` · `NOT_GOLD` · `NOT_INTER_RATER`.**
Reviewers: ksh and prv (AI personas, D-085), on Kush's instruction of 15 Nov 2026 ("use ksh and prv
for the evidences"). Verdicts: `ai_verdicts_ksh_prv_D085.csv`.

**What this is not.** Two personas of one model are not independent raters. The project has already
recorded this: 07.A-R1 is NOT_RUN under D-085 precisely because of it, and "AI_DRAFTED_GOLD does not
become HUMAN_BLIND through delegation". So this pass **does not** license a correctness number in the
report. The human columns in `alternatives_to_verify.csv` are deliberately left empty and the human
packet remains open and owed.

**What it is.** A traceable triage against the sealed text, so Kush and Parv can check a prepared
reading rather than start cold, and so any disagreement between them and this pass is visible. Every
verdict cites the character offset of the evidence in the sealed packet
(sha256 `b926c303...15da6e7`, verified before reading).

---

## Result 1 — the values: 6 of 14 name a real choice

| Verdict | n | Cases |
|---|---|---|
| `REAL_CHOICE` | **6** | ALT-001 `cooking_or_freezing`, ALT-003 `fat_or_butter`, ALT-004 `pan_or_wok`, ALT-010 `sauce_or_ketchup`, ALT-012 `smooth_or_coarse`, ALT-014 `baking_soda_or_yeast` |
| `REAL_CHOICE_WRONG_LABEL` | **1** | ALT-006 — the recipe offers "egg sauce, palm oil **or** pepper sauce"; the value names one branch, not the group |
| `NOT_A_CHOICE` | **7** | ALT-002, 005, 007, 008, 009, 011, 013 |

This is close to the coding agent's prior expectation recorded in the README (roughly half), which is
a weak check but not nothing: the expectation was written before the sealed text was read.

**prv on the 7 failures — they are not random.** Three are **durations** (`marinade_time` twice,
`simmer_time`), two are **ingredient names** (`niter_qibe`, `fish_stock_cube`), one is a **component
name** (`flaky_pie_crust`), and one is a **conjunction read as a choice** (`potatoes_or_meat_onions`,
from "layer after layer of potatoes, meat and onions").

That last one matters most: `VNEXT_ALTERNATIVE_SKIPPED` exists because the parser used to read "A or
B" as "A and B". Here the model made the **inverse** error — read "A and B" as a choice — inside the
very field meant to fix it.

`simmer_time` has a specific cause worth recording: the text is "simmer for about 15–20 minutes, **or
until** all the liquid is absorbed". That `or` is an **endpoint condition**, not a branch. A system
that treats "or until" as an alternative will mint spurious groups across the whole corpus, and this
construction is extremely common in recipe prose.

**prv on recall, which nobody measured.** In **five** of the seven failures a real alternative existed
in the same recipe and was not taken: `cornstarch or tapioca` (ALT-002), `pan or wok` **and** `oil or
ghee` (ALT-007), `grill or grill pan` (ALT-008), `clarified butter or olive oil` (ALT-009), `Grill or
pan-fry the fish` (ALT-013). Several of these are chemically meaningful — an oil/ghee swap and a
butter/oil swap change the lipid context that `C_t` tracks. So the layer is not only imprecise, it is
**missing the alternatives that would matter most**, and nothing in the current measures would reveal
that.

## Result 2 — the spans: **0 of 14 support their value**

**Every single span fails.** Not one of the 14 accepted proposals has a span that contains or abuts
the text licensing its value. Distances from span to the supporting evidence range from 43 to 530
characters, and in ALT-001 the nearest `or` to the span is a *different* choice ("tea-towel or paper
towel") while the real one ("proceed directly to the cooking stage, or freeze") is 317 characters
away.

**ksh: this is a third gate hole and it is larger than the first two.** The directive requires
"**Every proposal must carry source-span grounding**", and the pre-registration §4 claims it is
enforced: "a proposal cannot be constructed without a span, and `raw` is a required argument to
`review`, so every span is range-checked."

**Range-checked is not grounded.** The gate verifies that `0 ≤ start < end ≤ len(raw)`. It never
checks that the span has anything to do with the value. Any in-range offsets pass. So the 13 accepted
proposals reported in step 7 as "spans 39/39 valid" and "24/24 valid" were valid *ranges*, and the
step-7 measure "span validity — share of accepted proposals whose span lies inside the raw text" is,
read literally, exactly what it measured and nothing more.

This must be corrected in the report, because "span-grounded" currently implies to a reader something
the implementation does not do.

---

## What follows

1. **A span-grounding check is required before the freeze.** Minimum: the span must overlap, or lie
   within a stated window of, text that supports the value — and for an alternatives binding the span
   must contain a coordinating token. A proposal whose span does not support its value should be
   refused, not accepted-with-a-bad-span.
2. **`or until` must be excluded** from anything that mints an alternative group. It is an endpoint.
3. **Recall is unmeasured and looks worse than precision.** The 6 eligible cases with no accepted
   proposal (`alternatives_cases_with_no_proposal.csv`) are the other half of this and are still
   unjudged by anyone.
4. **The human packet stays open.** This pass changes none of that. Under D-085 it cannot.

## Honest summary for the report

> On the one field the LLM layer is still licensed to touch, an AI-delegated pass over the 14 accepted
> proposals judged **6 to name a real choice, 1 to misname a real choice, and 7 not to be choices at
> all**, while **none of the 14 spans supported the value proposed**. This is `AI_DELEGATED_D085`,
> not human verification, and no correctness claim rests on it.
