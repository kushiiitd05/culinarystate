# prv review: should `C_t` be wired to the FDA pH bands before the freeze?

Reviewer: prv (AI persona, D-085). Status: **AI_DELEGATED**, not human verification. Instruction:
Kush, 15 Nov 2026.

## Verdict: DO NOT WIRE BEFORE THE FREEZE — and the food-science reason is stronger than the schedule one

ksh's answer is right on cost. I would refuse it even if it were free, because of what the 140 bands
actually are.

**The FDA table measures the ingredient as purchased, not the lot in the pot.** That is the whole
problem. Tomato at 4.3–4.9 is a raw tomato. By the time it is in a sauce it has been diluted by stock,
possibly acidified by wine or vinegar, possibly buffered by dairy or by the proteins and phosphates in
a meat sauce, and concentrated by reduction. The lot's pH is not the member's pH and is not a function
of the members' pH values that anyone can compute without measuring.

So a `member_ph_band` on a lot member is a **provenance-correct but situationally weak** fact: true of
the ingredient, not of the food. It is exactly right for evidence compatibility, which is matching an
evidence row's context against a query context at the ingredient level — which is where it already
is. It is wrong as a property of `C_t`, which describes the lot.

**The 8 inconclusive bands are the interesting ones and they are the ones a `C_t` field would
flatten.** Tomato straddles 4.6. So do several of the fruits and the dairy-adjacent entries. Those are
precisely the cases where cooking decides the answer and where `INCONCLUSIVE_SPANS_THRESHOLD` is the
honest output. A state field invites a downstream consumer to ask "is this lot acidic", and the only
defensible answer for a straddling ingredient in an unknown mixture is "unknown", which is what `C_t`
already says. Wiring would replace a correct UNKNOWN with a correct-but-misleading interval.

**On the 31 ACIDIC and 101 LOW_ACID.** These are safer, and for something like vinegar at 2.4–3.4 or
lemon juice at 2.0–2.6 the band is robust to everything a recipe does to it short of heavy dilution.
If there is ever a case for a member-level field it is these. But the value of knowing "vinegar is
acidic" inside `C_t` is near zero — the marker table already records `ACID` for vinegar, with a
reviewed basis, and that is what the salt/acid context cells actually use.

## Agreement and one addition

Agree with both of ksh's "required now" points and with preferring the second before 19 Nov.

One addition: **say in the report which 8 ingredients are inconclusive**, or at least say that tomato
is one of them. Tomato is the project's running example and a reader who remembers "tomato sauce is
acidic" from the earlier drafts should be able to see exactly why the system now declines to say so.
That single example explains the no-midpoints rule better than the rule does.

## On the human verification still owed

Unchanged and still owed. If one human act is spent before the freeze I would still spend it on
D-134, per my earlier review: the pH bands touch one axis in a compiler cell, D-134 touches 29.3% of
every recipe in the corpus.
