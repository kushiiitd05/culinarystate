# Prompt-sensitivity probe: one clause decides whether the 7B answers at all

**`DIAGNOSTIC_ONLY` · not an arm · 4 prompts on 1 case.** 15 Nov 2026, found while implementing
prompt v3 under amendment A5. Recorded before any v3 arm was run.

## What happened

v3 was implemented and probed on eligible cases. The 7B returned `[]` on every one — including
*Pasta with Sausage*, whose text contains "mix in **sauce or ketchup**", a choice both arms had
previously found.

`ask_local` sets `temperature: 0`, so the arm is deterministic: the same prompt gives the same
answer. Six identical calls returned `[]` six times. The model itself is healthy — it answers
`Reply with exactly: OK` correctly, and on a two-key JSON request about "Add sauce or ketchup." it
returns well-formed JSON.

So the cause had to be in the prompt. A four-way bisection on one case (`Pasta with Sausage`,
triggers `VNEXT_ALTERNATIVE_SKIPPED`, `VNEXT_MIXTURE_COREF`):

| Prompt | Result |
|---|---|
| A — minimal: return JSON objects with `value` and `quote` for any choice | **proposals returned** |
| B — A plus `event_id` and the event-id list | **proposals returned** |
| C — A plus **"Return [] if nothing is warranted."** | **`[]`** |
| D — A plus the field constraint and the no-numbers rule | **proposals returned** |

**One sentence decides it.** Adding the abstention clause to a prompt that was answering flips the
7B to returning nothing. Removing it restores answers.

## Why this matters more than the clause itself

**That clause is in v1 and v2.** It is not a v3 artifact. It has been in every prompt this step has
used, which means the recorded arm results sit on top of an uncontrolled sensitivity of this size.

**The answers it suppresses are not good answers.** In A, B and D the 7B returns junk: `"value":
"A"` with the quote `"Bring 2 liters water to a boil, and add salt."` — it is not finding "sauce or
ketchup", it is filling the schema. So the 7B's two states on this case are **abstain** (with the
clause) or **emit a malformed label** (without it). Neither is a usable proposal, and a measure that
counted only the first state would read as caution rather than as failure.

**It confounds a v3 zero on the 7B.** If the 7B returns zero grounded proposals under v3, that zero
cannot be attributed to span grounding without this probe beside it, because the abstention clause
alone is sufficient to produce it. The 72B answered under v1, which carries the same clause, so it
appears robust to it; the 7B is not.

## What was NOT done, deliberately

**The clause was not removed to make the arms answer.** That would be tuning toward a positive
result after seeing that removal produces output, and amendment A5 registered v3 as a change to how a
choice is *located*, not to how willing a model is to offer one. v3 runs with the clause in place,
exactly as v1 and v2 did, and this probe is reported beside the result so the zero is interpretable.

## What this adds to the limitations

Single-sample arm results on a 60-case set carry an uncontrolled prompt sensitivity large enough to
move an arm between "answers" and "declines everything" on one sentence. No arm number in this step
should be read as a property of the model alone. Measuring that sensitivity properly — several
prompt variants per arm, reported as a spread rather than a point — is the right design and was not
done before the freeze.
