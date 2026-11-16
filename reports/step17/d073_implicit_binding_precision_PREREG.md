# D-073 implicit-object binding: precision-check pre-registration (S170, 2026-11-07)

Status: PRE-REGISTERED before any precision-sample draw. Decided by ksh (AI) under D-071; entered by the coding agent.
Not a human gate. Exploration (below) used a different seed from the precision sample.

## Exploration (seed `d073-exploration-2026-11-07`, 400 recipes, 6,345 Rung A events; scratch, not committed)

Per unique event (the binder runs twice per text, once in `build_events` and once in `resolve_refs`):

- IMPLICIT_ARG_NONE ~303: ~282 occur before any entity exists (e.g. "Preheat the oven"): no object, and UNKNOWN is
  correct. ~19 occur when the only live entities are reserved portions; ~2 when everything was consumed.
- IMPLICIT_ARG_AMBIGUOUS ~427: ~214 with a live current mixture (`_Binder.current`). Roughly one in ten
  ambiguous ACTION mentions read like nouns tagged as verbs ("salt", "juices", "proof", "butter"); that is an
  upstream tagging issue, not a binding one.

## Rule R2 (bind the last-produced intermediate when none is live): WITHDRAWN, not tested

It fires on at most ~0.3 % of events. Where it fires, the only live candidates are reserved portions, which the
binder never binds implicitly by design ("reserved portions are never implicit"); a consumed entity cannot be
consumed again. Leave those events IMPLICIT_ARG_NONE.

## Rule R1 under test: `RA_IMPLICIT_CURRENT_V1`

At an event with no explicit argument, no reference argument and no named product, when the most-recent live tier
(`_tier(_live())`) holds two or more entities and `_Binder.current` is live, bind `[current]` as the only input
(diagnostic flag `IMPLICIT_ARG_BOUND_CURRENT`). Every other case stays as now.

## Sample

- Seed string `d073-precision-2026-11-07-r1`; recipes drawn with `seeded_sample` (smallest sha256(seed || recipe_id))
  over all five families, 400 recipes; any recipe in the exploration sample is excluded.
- Every R1 firing in those recipes is a candidate; at most one per recipe (the smallest sha256(seed || recipe_id ||
  action char offset)); the 60 candidates with the smallest recipe rank form the sample. Fewer than 60: all of them.
- Text and recipe ids go only to a git-ignored private file; the tracked output holds counts only.

## Labels (one per item, read in the action's recipe context)

- `CORRECT`: the action really acts on exactly the current mixture as described (its ingredient leaves).
- `WRONG_OBJECT`: the action acts on something else, on more or fewer entities, or on a new ingredient.
- `NO_OBJECT`: a real action with no food object (e.g. "cover the pan", "lower the heat").
- `NOT_AN_ACTION`: the ACTION mention is not a verb in context (tagging error).
- `UNCLEAR`: context does not decide.

Precision = CORRECT / all labelled items (every non-CORRECT label counts against the rule, because a wrong binding is
worse than UNKNOWN).

## Landing rule (fixed now)

LAND R1 (RULES_VERSION bump, tests first, census rerun as a new version) iff CORRECT >= 54 of 60 (point precision
>= 0.90; Wilson 95 % lower bound 0.7985). With n < 60 items, land iff the Wilson 95 % lower bound >= 0.80.
Otherwise do not land; record the label counts and leave the binder unchanged.

Labeller: ksh (AI) under D-071. A prv cross-check is welcome but not required for this engineering rule; same-model
caveat as J4 applies.

## Amendment 1 (S170, before any draw)

The first version said 54/60 gives a Wilson 95 % lower bound >= 0.80; it is 0.7985. The operative rule
(CORRECT >= 54 of 60) is unchanged; only the parenthetical was corrected. Found by the scorer's unit test.
