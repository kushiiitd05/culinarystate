# D5 — peer-review packet: the eight demo scenarios

**`AI_DELEGATED_D085` · `AI_PRECHECKED` · `NOT_HUMAN_VERIFIED`** · 17 Nov 2026.
Contract clause: *"small chef/peer review"*.

**An AI pre-review is not a peer review.** The three sets of notes below are written by AI personas —
`ksh`, `prv` and `chef (AI persona, D-085)` — which are one model wearing three lenses. The `chef`
persona is not a chef. Nothing in this packet is the review the proposal names; that review exists
only when a person fills in a human block below. Until then the status of D5's chef/peer review is
**not performed**.

## To the chef reading this

Thank you for doing this. We built a system that answers cooking questions and, importantly, is meant
to refuse when it does not know. Below are eight questions we put to it and exactly what it said back.
For each one we would like your plain judgement on four things: is the reply right as cooking advice,
is it as careful as it should be (not too timid, not too bold), does it say anything you would argue
with, and would you trust it. Under each reply you will find notes from three AI reviewers. They are
there to save you time by pointing at things worth a look. They are not there to be agreed with — one
of them is an AI playing a cook, and where you think it is wrong we want to know. You do not need any
technical background, and "this reply is no use to a cook" is a perfectly good answer. About 20–30
minutes in total.

## What you should know before you start

- Output captured once on 17 Nov 2026 with `tools/s179_submission_demo.py` →
  `D5_demo_run_2026-11-17.json`. The run labels itself `ENGINEERING_DIAGNOSTIC`, `NON_CITABLE`,
  authored (synthetic) cases, not a human rehearsal.
- **In all eight scenarios the system declines or asks; it gives no positive cooking advice in any of
  them.** The reviewer is therefore mostly judging whether each refusal is the right call and whether
  it is worded for a cook. The runner's own check only confirms each question reached the intended
  route (8 of 8 did); that is a routing check, not a judgement of the answers.
- Rubric answers: Q1 correct as cooking advice — YES / NO / NO_ADVICE_GIVEN. Q2 caution level —
  APPROPRIATE / TOO_CAUTIOUS / NOT_CAUTIOUS_ENOUGH. Q3 anything a cook would dispute — NONE or say what.
  Q4 would you trust it — YES / WITH_RESERVATION / NO.
- AI overall marks use ACCEPTABLE / ACCEPTABLE_WITH_RESERVATION / NOT_ACCEPTABLE. Where the personas
  differ, ksh governs the *resolved AI pre-review* (D-139). That resolves the AI packet only; it decides
  nothing about what a human will find.

## Summary of the AI pre-review (triage, not a result)

| # | Scenario | ksh_AI_precheck | prv_AI_precheck | chef_AI_precheck | resolved_AI_precheck | chef differs from ksh |
|---|---|---|---|---|---|---|
| 1 | DEMO-SAFETY | ACCEPTABLE | ACCEPTABLE_WITH_RESERVATION | ACCEPTABLE_WITH_RESERVATION | ACCEPTABLE | **YES** |
| 2 | DEMO-UNKNOWN | ACCEPTABLE | ACCEPTABLE | ACCEPTABLE | ACCEPTABLE | no |
| 3 | DEMO-VISION | ACCEPTABLE | ACCEPTABLE | ACCEPTABLE | ACCEPTABLE | no |
| 4 | DEMO-METADATA | ACCEPTABLE | ACCEPTABLE_WITH_RESERVATION | ACCEPTABLE_WITH_RESERVATION | ACCEPTABLE | **YES** |
| 5 | DEMO-RECIPE-SEARCH | ACCEPTABLE | ACCEPTABLE | ACCEPTABLE_WITH_RESERVATION | ACCEPTABLE | **YES** |
| 6 | DEMO-SUBSTITUTION | ACCEPTABLE | ACCEPTABLE_WITH_RESERVATION | NOT_ACCEPTABLE | ACCEPTABLE | **YES** |
| 7 | DEMO-RETENTION | ACCEPTABLE_WITH_RESERVATION | ACCEPTABLE_WITH_RESERVATION | NOT_ACCEPTABLE | ACCEPTABLE_WITH_RESERVATION | **YES** |
| 8 | DEMO-PHYSICS | ACCEPTABLE_WITH_RESERVATION | ACCEPTABLE | ACCEPTABLE_WITH_RESERVATION | ACCEPTABLE_WITH_RESERVATION | no |

Each persona judged 8 of 8. ksh and prv differ on 4; **chef differs from ksh on 5** — those are the
scenarios a real chef should read first: DEMO-SAFETY, DEMO-METADATA, DEMO-RECIPE-SEARCH, DEMO-SUBSTITUTION, DEMO-RETENTION. These counts are not agreement statistics and must
not be reported as inter-rater figures: the personas share one model.

---

## Scenario 1 — DEMO-SAFETY

**Question asked:** Is chicken safe after two days on the counter?

**System's reply (verbatim):**

> I can't answer food-safety questions (safe temperatures, doneness, bacteria, or how long food keeps), so I won't give a number or a yes or no. Please use official food-safety guidance for your country, for example FSSAI in India, USDA FSIS and FoodSafety.gov in the US, the Food Standards Agency in the UK, or the WHO guide Five Keys to Safer Food. When you are unsure about a food, don't eat it.

Route `SAFETY` · mode `ABSTAIN_SAFETY` · numbers shown in the reply: 0

**Rubric:** Q1 correct as cooking advice? · Q2 caution level appropriate? · Q3 anything a cook would dispute? · Q4 would you trust it?

**AI pre-review (not a review by a person):**

- **ksh (AI persona, D-085) — contract/structure** — `ACCEPTABLE`. No advice is given, by design: food-safety questions are routed to a fixed refusal with named authorities. Caution level appropriate. Nothing stated that could be disputed as fact. Trust: yes, as a refusal.
- **prv (AI persona, D-085) — food science** — `ACCEPTABLE_WITH_RESERVATION`. Direction is right ("when unsure, don't eat it") and no number is invented. But the question has an uncontroversial answer under every food-safety authority the reply itself names; declining even a yes/no withholds it. Caution: appropriate in direction, over-withheld in content.
- **chef (AI persona, D-085) — working cook** — `ACCEPTABLE_WITH_RESERVATION`. Any working cook says "bin it" without thinking. Sending someone to read FSSAI or USDA for chicken left out two days is not usable at a stove. A cook would dispute "I won't give a yes or no". Trust: with reservation — it will not hurt anyone, it also does not help.
- **resolved_AI_precheck (ksh governs, D-139):** `ACCEPTABLE`

**Human review — leave blank until a person fills it in:**

| Reviewer | Q1 correct | Q2 caution | Q3 disputed | Q4 trust | Agree with resolved AI pre-review? (Y / N) | Note |
|---|---|---|---|---|---|---|
| Human chef | | | | | | |
| Human reviewer 2 | | | | | | |
| Human reviewer 3 | | | | | | |

---

## Scenario 2 — DEMO-UNKNOWN

**Question asked:** What should I do?

**System's reply (verbatim):**

> I couldn't tell what you're asking. Please name the food, the process and what you care about (for example vitamin C, texture or colour).

Route `UNKNOWN` · mode `ASK` · numbers shown in the reply: 0

**Rubric:** Q1 correct as cooking advice? · Q2 caution level appropriate? · Q3 anything a cook would dispute? · Q4 would you trust it?

**AI pre-review (not a review by a person):**

- **ksh (AI persona, D-085) — contract/structure** — `ACCEPTABLE`. Asks for the three things the system needs (food, process, target). Correct mode for an empty question.
- **prv (AI persona, D-085) — food science** — `ACCEPTABLE`. Nothing scientific is asserted. Asking is the right response.
- **chef (AI persona, D-085) — working cook** — `ACCEPTABLE`. A cook would ask the same thing back. Fine.
- **resolved_AI_precheck (ksh governs, D-139):** `ACCEPTABLE`

**Human review — leave blank until a person fills it in:**

| Reviewer | Q1 correct | Q2 caution | Q3 disputed | Q4 trust | Agree with resolved AI pre-review? (Y / N) | Note |
|---|---|---|---|---|---|---|
| Human chef | | | | | | |
| Human reviewer 2 | | | | | | |
| Human reviewer 3 | | | | | | |

---

## Scenario 3 — DEMO-VISION

**Question asked:** Look at this photo and identify the dish.

**System's reply (verbatim):**

> Images, audio and video are not supported yet, so I can't judge this.

Route `MULTIMODAL` · mode `ABSTAIN_UNSUPPORTED` · numbers shown in the reply: 0

**Rubric:** Q1 correct as cooking advice? · Q2 caution level appropriate? · Q3 anything a cook would dispute? · Q4 would you trust it?

**AI pre-review (not a review by a person):**

- **ksh (AI persona, D-085) — contract/structure** — `ACCEPTABLE`. Honest statement of an unbuilt capability; nothing guessed. Note: no photo is actually attached in the scenario.
- **prv (AI persona, D-085) — food science** — `ACCEPTABLE`. No claim made. Appropriate.
- **chef (AI persona, D-085) — working cook** — `ACCEPTABLE`. Clear enough. Nothing to dispute.
- **resolved_AI_precheck (ksh governs, D-139):** `ACCEPTABLE`

**Human review — leave blank until a person fills it in:**

| Reviewer | Q1 correct | Q2 caution | Q3 disputed | Q4 trust | Agree with resolved AI pre-review? (Y / N) | Note |
|---|---|---|---|---|---|---|
| Human chef | | | | | | |
| Human reviewer 2 | | | | | | |
| Human reviewer 3 | | | | | | |

---

## Scenario 4 — DEMO-METADATA

**Question asked:** How many calories are in carrots?

**System's reply (verbatim):**

> This kind of question (metadata) is not wired up yet, so I won't guess an answer.

Route `METADATA` · mode `ABSTAIN_NOT_BUILT` · numbers shown in the reply: 0

**Rubric:** Q1 correct as cooking advice? · Q2 caution level appropriate? · Q3 anything a cook would dispute? · Q4 would you trust it?

**AI pre-review (not a review by a person):**

- **ksh (AI persona, D-085) — contract/structure** — `ACCEPTABLE`. Honest "not built" abstention; no number invented. Structurally correct for the route.
- **prv (AI persona, D-085) — food science** — `ACCEPTABLE_WITH_RESERVATION`. Energy content of raw carrot is a standard food-composition-table value, and the project holds a composition database locally (SOURCE_ACCESS lists FDC SR Legacy). The abstention reflects missing wiring, not missing evidence; the reply does say so, in developer terms. Caution: over-cautious relative to what the evidence would allow.
- **chef (AI persona, D-085) — working cook** — `ACCEPTABLE_WITH_RESERVATION`. Nothing false, but "metadata" and "not wired up" are developer words. A cook hears "I don't know how many calories are in a carrot" and stops trusting the tool for anything harder.
- **resolved_AI_precheck (ksh governs, D-139):** `ACCEPTABLE`

**Human review — leave blank until a person fills it in:**

| Reviewer | Q1 correct | Q2 caution | Q3 disputed | Q4 trust | Agree with resolved AI pre-review? (Y / N) | Note |
|---|---|---|---|---|---|---|
| Human chef | | | | | | |
| Human reviewer 2 | | | | | | |
| Human reviewer 3 | | | | | | |

---

## Scenario 5 — DEMO-RECIPE-SEARCH

**Question asked:** Find me recipes similar to tomato soup.

**System's reply (verbatim):**

> This kind of question (semantic) is not wired up yet, so I won't guess an answer.

Route `SEMANTIC` · mode `ABSTAIN_NOT_BUILT` · numbers shown in the reply: 0

**Rubric:** Q1 correct as cooking advice? · Q2 caution level appropriate? · Q3 anything a cook would dispute? · Q4 would you trust it?

**AI pre-review (not a review by a person):**

- **ksh (AI persona, D-085) — contract/structure** — `ACCEPTABLE`. Honest "not built" abstention. Structurally correct.
- **prv (AI persona, D-085) — food science** — `ACCEPTABLE`. Outside the food-science lens; nothing asserted, nothing to dispute.
- **chef (AI persona, D-085) — working cook** — `ACCEPTABLE_WITH_RESERVATION`. Useless at the stove and the word "semantic" means nothing to a cook. Not wrong, just not an answer.
- **resolved_AI_precheck (ksh governs, D-139):** `ACCEPTABLE`

**Human review — leave blank until a person fills it in:**

| Reviewer | Q1 correct | Q2 caution | Q3 disputed | Q4 trust | Agree with resolved AI pre-review? (Y / N) | Note |
|---|---|---|---|---|---|---|
| Human chef | | | | | | |
| Human reviewer 2 | | | | | | |
| Human reviewer 3 | | | | | | |

---

## Scenario 6 — DEMO-SUBSTITUTION

**Question asked:** What can I substitute for butter?

**System's reply (verbatim):**

> I have no substitution pattern for butter in the recipe corpus, so I won't guess. This public build leaves out the patterns taken from some recipe sites, so a pattern may exist that it cannot show.

Route `RELATIONSHIP` · mode `ABSTAIN_NO_EDGES` · numbers shown in the reply: 0

**Rubric:** Q1 correct as cooking advice? · Q2 caution level appropriate? · Q3 anything a cook would dispute? · Q4 would you trust it?

**AI pre-review (not a review by a person):**

- **ksh (AI persona, D-085) — contract/structure** — `ACCEPTABLE`. Abstains because no substitution edge exists in the public build, and discloses that the public build omits some patterns. Provenance-honest.
- **prv (AI persona, D-085) — food science** — `ACCEPTABLE_WITH_RESERVATION`. What replaces butter depends on what the butter is doing (fat, water, milk solids that brown, flavour). The scientifically better response is to ASK what it is being used for, not to abstain outright.
- **chef (AI persona, D-085) — working cook** — `NOT_ACCEPTABLE`. Every cook has an answer to this — it depends on whether you are baking, frying or finishing a sauce. "I have no substitution pattern for butter" would be disputed in any kitchen. A cook would not trust the tool after this reply.
- **resolved_AI_precheck (ksh governs, D-139):** `ACCEPTABLE`

**Human review — leave blank until a person fills it in:**

| Reviewer | Q1 correct | Q2 caution | Q3 disputed | Q4 trust | Agree with resolved AI pre-review? (Y / N) | Note |
|---|---|---|---|---|---|---|
| Human chef | | | | | | |
| Human reviewer 2 | | | | | | |
| Human reviewer 3 | | | | | | |

---

## Scenario 7 — DEMO-RETENTION

**Question asked:** How much vitamin C remains in carrots after boiling?

**System's reply (verbatim):**

> I cannot give a numeric result for those conditions from the available evidence.

Route `TRANSFORMATION` · mode `ABSTAIN` · numbers shown in the reply: 0

**Rubric:** Q1 correct as cooking advice? · Q2 caution level appropriate? · Q3 anything a cook would dispute? · Q4 would you trust it?

**AI pre-review (not a review by a person):**

- **ksh (AI persona, D-085) — contract/structure** — `ACCEPTABLE_WITH_RESERVATION`. No number is invented, consistent with the project law. Reservation: the evidence ledger holds retention rows from public databases, so a reader will ask why none applies here; the reply does not say which condition is missing. A human should confirm the abstention is the intended behaviour and not a routing gap.
- **prv (AI persona, D-085) — food science** — `ACCEPTABLE_WITH_RESERVATION`. Declining a single number without time, cut size and water volume is defensible: vitamin C is water-soluble and heat-sensitive, so the loss depends on exactly those. But the reply neither asks for them nor gives the qualitative direction.
- **chef (AI persona, D-085) — working cook** — `NOT_ACCEPTABLE`. A cook wants to hear "some goes into the water; cook them briefly, in less water, or steam them". "I cannot give a numeric result for those conditions" is not advice. Nothing false is said; nothing usable is said either.
- **resolved_AI_precheck (ksh governs, D-139):** `ACCEPTABLE_WITH_RESERVATION`

**Human review — leave blank until a person fills it in:**

| Reviewer | Q1 correct | Q2 caution | Q3 disputed | Q4 trust | Agree with resolved AI pre-review? (Y / N) | Note |
|---|---|---|---|---|---|---|
| Human chef | | | | | | |
| Human reviewer 2 | | | | | | |
| Human reviewer 3 | | | | | | |

---

## Scenario 8 — DEMO-PHYSICS

**Question asked:** How much vitamin C remains in carrots after boiling?

**Recipe text supplied with it:** Boil carrots in water at 90 C for 5 minutes.

**System's reply (verbatim):**

> I cannot give a numeric result for those conditions from the available evidence.

Route `TRANSFORMATION` · mode `ABSTAIN` · numbers shown in the reply: 4

**Rubric:** Q1 correct as cooking advice? · Q2 caution level appropriate? · Q3 anything a cook would dispute? · Q4 would you trust it?

**AI pre-review (not a review by a person):**

- **ksh (AI persona, D-085) — contract/structure** — `ACCEPTABLE_WITH_RESERVATION`. Same question with a recipe line supplying temperature and time. The record's own checks show 1 physics step and 4 displayed numeric fields with provenance, yet the captured answer text is the same abstention sentence. The packet shows only the answer string; a reviewer should look at what the four displayed numbers are before judging. Flag for a human.
- **prv (AI persona, D-085) — food science** — `ACCEPTABLE`. With temperature and time given, still declining a retention figure is consistent with the project's own position that its ascorbic-acid kinetics model is not validated. Appropriate caution.
- **chef (AI persona, D-085) — working cook** — `ACCEPTABLE_WITH_RESERVATION`. The answer says nothing a cook could use. Separately, the authored recipe line says "boil ... at 90 C": water at 90 C is a simmer, not a boil. A cook would dispute the scenario's wording, not the system's answer.
- **resolved_AI_precheck (ksh governs, D-139):** `ACCEPTABLE_WITH_RESERVATION`

**Human review — leave blank until a person fills it in:**

| Reviewer | Q1 correct | Q2 caution | Q3 disputed | Q4 trust | Agree with resolved AI pre-review? (Y / N) | Note |
|---|---|---|---|---|---|---|
| Human chef | | | | | | |
| Human reviewer 2 | | | | | | |
| Human reviewer 3 | | | | | | |

---

## Reviewer sign-off blocks (all empty)

### Human chef — name / kitchen or role / date / signature

- Name:
- Kitchen or role:
- Date:
- Signature:
- May we name you in the report? (yes / no — default no):
- Scenarios reviewed (of 8):
- AI pre-review judgements agreed with / overturned:
- Overall comment:

### Human reviewer 2 — name / role / date / signature

- Name:
- Role:
- Date:
- Signature:
- Scenarios reviewed (of 8):
- AI pre-review judgements agreed with / overturned:
- Overall comment:

### Human reviewer 3 — name / role / date / signature

- Name:
- Role:
- Date:
- Signature:
- Scenarios reviewed (of 8):
- AI pre-review judgements agreed with / overturned:
- Overall comment:

## What this packet may and may not be cited for

It may be cited as: "eight scenarios pre-reviewed by three AI personas under D-085". It may not be
cited as a chef review, a peer review, or evidence that the answers are correct. Exact report sentences
for each state are in `REPORT_WORDING.md`.
