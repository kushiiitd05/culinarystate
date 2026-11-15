# Step 7 final: what the sealed comparison established

**`DIAGNOSTIC_ONLY` · `AI_DELEGATED_D085` · `NOT_HUMAN_VERIFIED` · `NOT_GOLD`.** 16 Nov 2026.
Governed by `step7_sealed_comparison_preregistration.md` and amendments A1–A6, each committed before
the result it governs. Sealed set unchanged throughout: 60 cases, packet SHA-256 `b926c303…15da6e7`.

## 1. The headline

| Arm | Returned | Accepted | **Grounded** | Values naming a real choice |
|---|---|---|---|---|
| 7B prompt v1 | 84 | 13¹ | **0** | 7 of 14 — 50% |
| 72B prompt v1 | 70 | 16 | **0** | 13 of 16 — 81% |
| 7B prompt v3 | 3 | 1 | **1** | — |
| **72B prompt v3** | 63 | **21** | **21** | **19 of 21 — 90%** |

¹ re-scored onto the surviving licensed field after D-135; recorded as 39 under the gate of the day.

**Two separate things were wrong, and they were found in the right order.**

1. **The field was wrong.** `condition_profile_id` was a reference with no referent, so any noun
   passed. Removed in D-135; the licensed surface became one field on one trigger.
2. **The grounding was never enforced.** The gate range-checked spans and called it grounding, so
   **every** accepted proposal across both v1 arms pointed somewhere else. Closed in D-137.
3. **The prompt asked the wrong thing.** Asking a language model for integer character offsets
   produces plausible numbers, not locations. v3 asks for the licensing *quote* and locates it in
   code.

With all three fixed: **0 → 21 grounded proposals**, and **0 of 63 quotes failed to locate**.

## 2. What scale did and did not do

**Did:** choose better. 90% of the 72B's v3 values name a choice that genuinely exists, against 50%
for the 7B under v1. The 72B found alternatives the 7B missed entirely — `clarified butter or olive
oil`, `Grill or pan-fry the fish` — and both are swaps that change the context `C_t` tracks. It never
made the 7B's worst error, reading "layer after layer of potatoes, meat **and** onions" as a choice.

**Did not:** ground anything. Under v1 both arms scored **0**. Scale moved 50% → 81% on selection and
0 → 0 on location. **Grounding was a protocol defect, and no amount of model fixed it.**

The 7B's v3 count of 1 is not a model result: its output is suppressed by an abstention clause
documented in `prompt_sensitivity_probe_2026-11-15.md`, where adding one sentence to a working prompt
flips it to returning nothing. The 72B is robust to that clause; the 7B is not.

## 3. The ksh+prv evidence pass on the 21

Verdicts: `alternatives_verification_2026-11-15/ai_verdicts_72b_v3_ksh_prv_D085.csv`.

| Verdict | n |
|---|---|
| `REAL_CHOICE`, well named | 9 |
| `REAL_CHOICE_SLOT_LABEL` — real, but labels the slot rather than the branches | 8 |
| `REAL_CHOICE_DUPLICATE` — correct, but the same group minted on a third event | 2 |
| `NOT_A_CHOICE` | **2** |

**The two failures are both instructive and neither is a comprehension failure.**

- `channa_or_choley` — *"serve hot with channa or choley (chickpea curry)"* glosses **two names for
  one dish**. An orthographic variant read as a cooking decision.
- `microwave_duration` — *"Microwave on high for 4 minutes **or a little after it stops rising**"* is
  an **endpoint condition**, not a branch. It escaped the `or until|till|when|so` filter because the
  wording is unusual. **That is a gap in our grounding rule, not in the model.** Recorded, not fixed:
  widening the filter after seeing which phrase slipped through would be fitting the rule to the
  result.

**The duplicate finding is real and unaddressed.** `butter_or_oil` was proposed on three separate
events of one recipe, correctly each time. V4 checks mutual exclusivity *within* a group; nothing
checks that one choice has been minted repeatedly across events.

## 4. What this licenses

**Does:** Layer-1, as finally specified, produces **21 grounded, contract-passing proposals** on the
60 hardest cases in the corpus, of which an AI-delegated pass judges 19 to name a real alternative.
Span grounding, not model scale, was the binding constraint. The validator caught every defect that
was found — each one was discovered **because** a check failed or a review read the output, never
because a model behaved well.

**Does not:** any accuracy claim. There is **no gold**. The pass is `AI_DELEGATED_D085` and two
personas of one model are not independent raters — this project set 07.A-R1 to NOT_RUN for exactly
that reason. **The human packet is open and owed**, and now covers 35 proposals across three arms. No
latency comparison is drawn: the 49 GB 72B does not fit a 40 GB A100 and ran on CPU.

## 5. Stated limitations, not papered over

1. **Single-sample arms.** One prompt clause moves the 7B between answering and declining everything.
   No arm number is a property of a model alone. The right design is several prompt variants per arm
   reported as a spread; not done before the freeze.
2. **The 72B v3 run is 59 cases in one pass plus 1 repaired call** (A6), never a clean 60/60. The
   repaired case (pageid 77844, *Rugelach*) took **832 s** against the main pass's 420 s timeout,
   which is what had killed it; it returned 9 proposals and **0 were accepted**, since its only
   trigger is `AMBIGUOUS_REFERENCE` and that licenses no field. The repair therefore changed the
   returned total from 54 to 63 and the gate rate from 0.3889 to 0.3333, and changed **no** accepted,
   grounded or verdict count.
3. **Recall is unmeasured.** The eligible cases with no accepted proposal remain unjudged by anyone.
4. **The endpoint filter is incomplete**, demonstrated by `microwave_duration`.
5. **Duplicate groups across events are unchecked.**
