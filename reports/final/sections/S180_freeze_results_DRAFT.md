# S180 — results of the 15 Nov architecture freeze

**DRAFT section for the final report.** Written 15 Nov 2026 by the coding agent. Every number cites a
committed artifact. Figures: `reports/final/figures_s180_2026-11-15/`, manifest carries the sha256 of
each source.

The 15 Nov freeze fixed the pipeline as: recipe semantic understanding → Typed Event IR →
event-sourced `S_t=(G,C,Q,Y,P)` → invariant validator → query-specific evidence compiler → claim
packet → LLM verbalizer → claim verifier with template fallback. Nothing new was designed. Every
adopt-now item already had an SSOT-v16 change request, and the work below is the implementation of
those, mapped to owner step 36A.3.

## 1. The validator decides, and on this evidence it has to

The strongest result of the freeze is negative and it is the one worth leading with.

Over the 60 hardest cases in the corpus, three model runs — 7B prompt v1, 7B prompt v2, and a voided
20-case 72B partial — produced **zero `(event_id, field)` slot agreement in every pair**. Not
disagreement about answers: the runs did not choose the same event to answer about, even once
(1 of 10 shared cases shared any `event_id`).

The cause was not the models. All 108 recorded returns were schema-valid, every accepted span lay
inside the raw text, and **no run attempted a single numeric value**. The cause was that
`condition_profile_id` is a reference field with no referent and no consumer: the plan defines it as a
pointer to a 07H COND record, nothing reads it, and no COND records are minted on the recipe side. A
non-blank string check cannot tell a reference from a noun lifted out of the sentence, so `pan`,
`chicken`, `bowl_content` and `boiling_time` were all accepted as condition profiles.

**D-135** removed it from the proposable set. With `VNEXT_FAT_STAYS` (already resolved by the rule
before its flag is raised) and the coreference triggers (whose answers have no licensed destination)
also closed, the LLM's entire licensed surface is **one field, `alternative_group`, on one trigger,
`VNEXT_ALTERNATIVE_SKIPPED`**.

> **Layer-1's measured contribution: on the 60 hardest cases, the LLM layer's licensed surface is one
> field on one trigger, and it produced 13 accepted proposals, none of them graded, because there is
> no gold.**

That is what "rules first, LLM proposes only on ambiguity triggers, validator decides" is supposed to
converge to. The surface is small because the destinations for the other answers do not exist yet,
not because the questions are uninteresting: `AMBIGUOUS_REFERENCE` is the primary trigger on 12 of 60
cases and is left UNKNOWN by design.

*Figure: `fig_s180_2_layer1_surface`.*

### What this does not say

There is **no gold** on the sealed set. No arm is correct, better or more accurate; acceptance
measures contract compliance only. `alternative_group` itself has no closed vocabulary — V4 checks
only that group members are mutually exclusive, which is structural, not semantic — and it is a
**grouping label, not an equivalence claim**. A 20-row human packet
(`reports/s180/alternatives_verification_2026-11-15/`) is open for Kush and Parv; a completed packet
is the only route to a correctness number for this layer.

## 2. State retrieval carries information the text does not

Three retrieval views over the same 5,181 states and 40 queries: BM25 over step text, a process
signature, and block-weighted cosine over the masked state vector.

| pair | V0 (51 dims) | V1 (60 dims) |
|---|---|---|
| TEXT vs PROCESS | 0.1164 | 0.1164 |
| TEXT vs COMPOSITION | 0.1018 | 0.0966 |
| PROCESS vs COMPOSITION | 0.0455 | 0.0502 |

Chance Jaccard@10 on this corpus is **0.001**, so these overlaps are 45–116× chance and still small.
Nothing was shared by all three views on 34 of 40 queries (V0). The views are not redundant: a
state-aware retriever is retrieving different neighbours from BM25, not the same ones more slowly.

V1 exposes the physics history State v2 already computed — thermal dose, cumulative dose, hot-aqueous
and hot-fat minutes, food temperature, moisture cap, lid state, oxygen proxy — which V0 omitted,
carrying only `temperature_C` and `duration_min` in its Q block. V0 is left untouched because the
committed diagnostic was measured on it.

**DIAGNOSTIC_ONLY: there is no relevance gold for this corpus, so overlap is not precision and no view
is better.** The measurement is of disagreement, not of ranking.

*Figure: `fig_s180_1_retrieval_views`.*

## 3. The compatibility schema carries all 13 axes

The directive required the canonical schema not be limited to salt/acid/lipid. The registry
`registry/rag/compatibility_axes_v1.csv` was created (it was referenced but did not exist) and merges
SSOT §241.3, MP AO2 and the repo's nine implemented axes.

**9 implemented · 2 implemented in the compiler · 2 schema only.** An unavailable axis stays UNKNOWN
with a stated reason and is never dropped, which is what lets the compiler select question-relevant
axes before retrieval instead of assuming a fixed triple.

- **Axis 7 (pH)** left SCHEMA_ONLY when the FDA/CFSAN 2003 table was found already in the repo.
- **Axis 9 (geometry)** was wired from `Q.piece_size_class`, which State v2 derives from cut history.
  Evidence rows carry no geometry field, so a known query size is reported `QUERY_ONLY` — not
  EVALUABLE. Treating a one-sided axis as a match would breach the freeze invariant that an UNKNOWN
  evidence context must not be treated as a MATCH.
- **Axis 8 (a_w / moisture)** has no producer and **axis 12 (measurement method)** has no data.

*Figure: `fig_s180_3_axis_status`.*

## 4. Ingredient pH bands, sourced and unverified

`registry/food_ph_fda2003_v1.csv` — 479 rows, FDA/CFSAN *Approximate pH of Foods and Food Products*
(Oct 2003), public domain, per-row source sha256 — joins to **140 ING ids** through EXACT/FULL
crosswalk rows only: 113 intervals, 25 points, 2 lower-bound-only. Against the 4.6 threshold:
**31 acidic · 101 low-acid · 8 inconclusive**.

Bands are reported as the intervals they are. There are **no midpoints and no clipping** (D-013), so
vinegar at 2.4–3.4 and lemon juice at 2.0–2.6 are `ACIDIC`, while the eight bands that straddle 4.6
are `INCONCLUSIVE_SPANS_THRESHOLD` rather than forced to a side:

| ING | item | band |
|---|---|---|
| ING-000154 | Apricots | 3.3–4.8 |
| ING-000042 | Tomatoes, Paste | 3.5–4.7 |
| ING-000653 | Mustard | 3.55–6.0 |
| ING-000010 | Tomatoes | 4.3–4.9 |
| ING-001885 | Pimiento | 4.4–4.9 |
| ING-000053 | Soy Sauce | 4.4–5.4 |
| ING-000187 | Buttermilk | 4.41–4.83 |
| ING-000116 | Bananas | 4.5–5.2 |

**Tomato is the project's running example and it is one of the eight.** An earlier draft recorded the
limitation as "no sourced pH table, so tomato sauce is not yet acidic". The table is now here, and the
system still declines to call tomato acidic — because 4.3–4.9 straddles the threshold and taking a
midpoint would be inventing a value. That single example is the clearest statement of the
no-midpoints rule.

### Why `C_t` is not wired to these bands

Reviewed by ksh and prv (`reports/s180/ph_ct_wiring_review_2026-11-15/`), both DO_NOT_WIRE before the
freeze. The band is already where it is needed — the evidence compiler's axis-7 cell, carrying basis,
source and `verify_status`. Wiring `C_t` would re-fill the corpus and move cited coverage numbers for
no gain in answering capability, and would place an unverified value where it propagates into figures.

The food-science reason is the stronger one: **the FDA table measures the ingredient as purchased, not
the lot in the pot.** A tomato in a sauce has been diluted by stock, possibly acidified by wine,
possibly buffered by dairy or by the proteins and phosphates of a meat sauce, and concentrated by
reduction. The lot's pH is not a computable function of its members' pH values. A member band is
provenance-correct but situationally weak: right for ingredient-level evidence matching, wrong as a
property of the lot. Wiring it would replace a correct UNKNOWN with a correct-but-misleading interval,
exactly on the eight ingredients where cooking decides the answer.

The reason code `NO_SOURCED_PH_TABLE` that `C_t` still writes is therefore **knowingly stale**: its
premise is false, and the correction is recorded in `reports/s179/d116_composition_state_schema_v1.md`
rather than applied, because fixing it is itself a `C_t` change that re-fills the corpus.

**The ingredient crosswalk was drafted by AI and is not human-verified**
(`UNVERIFIED_CROSSWALK_AI_DRAFTED`). Under D-085, AI review is not human verification, so no band may
back a submission claim until the rows it rests on are verified. The bands are available to the
evidence compiler; `C_t` is **not** wired to them, so every recorded corpus fill number stands as
measured and the 257,369 `NO_SOURCED_PH_TABLE` cells in the November state fill remain accurate.

*Figure: `fig_s180_4_ph_bands`.*

## 5. Lineage vNext

Promoted for State v2, RAG packet v2 and the submission headline rerun (D-134). The differential over
611,902 recipes **raised no exceptions** and changed **29.3% of recipes** — `VNEXT_MIXTURE_COREF`
140,828, `VNEXT_FAT_STAYS` 68,868, `VNEXT_ALTERNATIVE_SKIPPED` 48,520.

**This is DIAGNOSTIC.** Aggregate behaviour is consistent with the intended corrections and with
nothing else having been checked: there is **no gold regression set**, so no part of that 29.3% is
known to be an improvement. Spot checks were Wikibooks-only and informal. It is not clean, not
validated and not verified. "Raised no exceptions" means no process threw, not that no recipe was
parsed wrongly.

`VNEXT_FAT_STAYS` changes **contact, not quantity**. Keeping frying fat in the food's lot makes
`lipid_present` true (82.5% → 83.2%) while `fat_fraction` stays UNKNOWN `MASS_NOT_GROUNDED`. It is not
a claim that the food absorbed the frying medium; oil uptake is a surface and cooling-phase
phenomenon and the quantitative question belongs to the simulator.

## 6. Provenance of the decisions behind this section

115 decisions: **HUMAN 80 · AI_DELEGATED_D085 21 · AI_PERSONA_D071 6 · MIXED 1 · AI_AGENT_PROVISIONAL
7 · NO_APPROVER_LINE 0**. D-134 and D-135 are AI-delegated (ksh+prv personas under D-085, on Kush's
instruction) and both still owe a human sign-off before submission.

## 7. Open, and owed

| Item | Blocker |
|---|---|
| `alternative_group` correctness rate | human packet, 20 rows, Kush + Parv |
| pH bands in any claim | human verification of the crosswalk rows used |
| D-134, D-135 for a submitted artifact | human sign-off |
| 72B arm over the 18 eligible cases | VPN; run void at 20/60 |
| `C_t` wired to pH bands | decision: may an unverified-but-sourced band enter the state? |
| axes 8 and 12 | no producer, no data — post-submission |

---

## 8. The 72B arm, and the finding that supersedes §1

Added 15 Nov 2026 after the 72B run completed. §1–§7 stand; this extends them. Full detail:
`reports/s180/step7_72b_result_2026-11-15.md`.

**The run is valid:** 60/60 answered, 0 failures, schema 1.000. Gated under the D-135 surface but
before D-137 grounding, declared in advance by pre-registration amendment A4.

**Scale helps at choosing. It does not help at grounding.**

| | 7B v1 | 72B v1 |
|---|---|---|
| Accepted on the licensed field | 13 | **16** |
| Values naming a real choice (AI-delegated pass) | 7 of 14 — **50%** | 13 of 16 — **81%** |
| Spans that ground their value | **0 of 13** | **0 of 16** |

The 72B avoided every failure mode the 7B showed — including reading "layer after layer of potatoes,
meat **and** onions" as a choice, which is the inverse of the error the trigger exists to fix — and it
found two alternatives the 7B missed entirely, one of them a **lipid swap that changes the context
`C_t` tracks**. Its three failures are milder; the most interesting is `channa or choley`, which
glosses two names for one dish, so an orthographic variant was read as a cooking decision.

But **neither arm produced a single span that supports its value.** The models read the recipe
correctly and then emit offsets pointing somewhere else: `frying_fat_or_butter` carries the span
`'out 5 mm).\nHeat t'`. Nothing in the prompt makes a model compute an offset rather than produce a
plausible-looking number.

> **This is the result of the sealed comparison. Span grounding, not model scale, is the binding
> constraint on Layer-1. After applying the grounding requirement the directive always demanded,
> both arms accept nothing.**

A zero was registered in advance by amendment A4 as a reportable result rather than a failed run, and
it is reported as one: it is a statement about the task and the prompt, not about either model. The
likely remedy is a prompt that requires the model to **quote** the licensing text, with the quote
located deterministically afterwards — a prompt change, not a gate change. It was not made before the
freeze.

**No latency comparison is drawn between the arms:** the 49 GB 72B does not fit a single 40 GB A100
and ran on CPU.

### What this adds to limitations

- Both model arms are at **zero accepted proposals** under the span-grounding requirement. The LLM
  layer currently contributes nothing that survives the full contract, and that is the honest state.
- The AI-delegated evidence pass now covers **30** proposals across both arms. It is
  `AI_DELEGATED_D085`, not gold, and the human packet is still open and still owed.
- Duplicate alternative groups across events are unchecked: the 72B proposed one group twice on one
  recipe and V4 did not object, because it checks exclusivity within a group, not duplication across
  them.


---

## 9. Final: asking for a quote instead of an offset

Added 16 Nov 2026. Full detail: `reports/s180/step7_FINAL_COMPARISON_2026-11-16.md`. This supersedes
§8's conclusion that Layer-1 contributes nothing; §1–§8 stand as recorded.

**Three defects, found in order, each closed with a decision record.**

1. **D-135** — `condition_profile_id` was a reference field with no referent, so any noun passed.
2. **D-137** — the gate range-checked spans and reported it as grounding, which the directive had
   always required. **Every** accepted proposal across both v1 arms pointed somewhere else.
3. **A5 / prompt v3** — asking a language model for integer character offsets yields plausible
   numbers, not locations. v3 asks for the licensing **quote** and locates it in code.

| Arm | Accepted on the licensed field | **Span grounds the value** |
|---|---|---|
| 7B v1 | 13 | **0** |
| 7B v3 | 1 | **1** |
| 72B v1 | 16 | **0** |
| **72B v3** | **21** | **21** |

**0 → 21 grounded proposals, and 0 of 63 quotes failed to locate.**

**Scale improved selection and did nothing for grounding.** The 72B names a real choice in 90% of its
v3 proposals against the 7B's 50% under v1, and found alternatives the 7B missed entirely — including
a `clarified butter or olive oil` swap that changes the context `C_t` tracks. But under v1 both arms
grounded **zero**. Grounding was a protocol defect and no model size touched it.

The 7B's v3 count of 1 is **not** a model result: a single clause, "Return [] if nothing is
warranted", flips it from answering to declining everything
(`reports/s180/prompt_sensitivity_probe_2026-11-15.md`). The 72B is robust to that clause.

**AI-delegated verdicts on the 21** (`AI_DELEGATED_D085`, not gold): 9 well-named real choices, 8
real but labelling the slot rather than the branches, 2 duplicates of a correct group, and **2 not
choices** — a `channa or choley` gloss of two names for one dish, and "4 minutes **or a little after
it stops rising**", an endpoint construction that escaped the `or until` filter. **That second one is
a gap in our rule, not the model's error**, and the filter was deliberately not widened after seeing
which phrase slipped through.

*Figure: `fig_s180_2_layer1_surface` in `figures_s180_2026-11-16/`.*

### Final limitations for this layer

- **No gold.** 19 of 21 is an AI-delegated reading; two personas of one model are not independent
  raters. The human packet covers 35 proposals and is **open**.
- **Single-sample arms** with a prompt sensitivity large enough to move an arm between answering and
  silence on one sentence.
- The 72B v3 run is **59 cases in one pass plus 1 repaired call** (A6). The repaired case needed
  832 s against a 420 s timeout and contributed no accepted proposal.
- **Recall unmeasured**; **duplicate groups across events unchecked**; **the endpoint filter is
  incomplete**.

## Submission note, 20 Nov 2026

The architecture comparison in this section predates the signed Explorer and local console. The report now incorporates those interfaces with the same D-134–D-139 interpretation. Guarded answer and source-state demonstrations are diagnostic. The frozen hypotheses, the development-gold limit and the outstanding human checks remain as recorded.
