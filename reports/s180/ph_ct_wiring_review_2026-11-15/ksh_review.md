# ksh review: should `C_t` be wired to the FDA pH bands before the freeze?

Reviewer: ksh (AI persona, D-085). Status: **AI_DELEGATED**, not human verification. Instruction:
Kush, 15 Nov 2026, "if any needs review then use prv and ksh".

**Question.** `composition/ph_bands.py` resolves 140 ING ids to pH bands from the FDA/CFSAN 2003
table. `composition/state.py:77` still writes `acidity_band = UNKNOWN:NO_SOURCED_PH_TABLE`
unconditionally. Should it be wired before the 19 Nov freeze?

## Verdict: DO NOT WIRE BEFORE THE FREEZE

Not because the data is bad. Because wiring buys nothing where it matters and costs the one thing
that is scarce.

**It buys nothing where it matters.** The question that needs a pH band is evidence compatibility —
axis 7, "is this evidence row's acidity context compatible with the query's" — and that is **already
wired**, through `evidence_compiler.ph_axis_cell`. The compiler reads the band directly from
`ph_bands`, with basis, source and `verify_status` attached to the cell. Nothing a question-answering
path does is improved by also writing the band into `C_t`.

**It costs the fill numbers.** `acidity_band` appears in `state_dataset_fill_full_D116v1` with
257,369 `NO_SOURCED_PH_TABLE` cells, and those numbers are cited. Wiring changes them, which means a
corpus re-fill and a re-check of every artifact that quotes a coverage figure, four days before the
freeze, for no gain in answering capability. That is the wrong trade.

**And the risk is asymmetric.** A band in `C_t` is a state value. State values propagate into every
downstream artifact and into figures. The crosswalk is `UNVERIFIED_CROSSWALK_AI_DRAFTED`; under D-085
that cannot back a submission claim. A value that is correctly labelled but sitting in the state is
far more likely to be used without its label than one that is only reachable through a compiler cell
that carries the label in the same dict.

## If it is wired later, wire it as the D-116 review already specified

That review (`reports/s179/d116_review_2026-11-14/ksh_schema_review.md`, change 3) settled the shape
and it should not be re-litigated:

- **`member_ph_band`** per member, from the cited table, with basis and `verify_status`.
- **`acidity_band`** stays lot-level and stays UNKNOWN `MIXTURE_PH_NOT_COMPUTED` unless there is a
  cited measured pH **for the mixture**. Taking the band of the most acidic member is an invented
  mixture value: a tablespoon of vinegar in two litres of water with tomatoes is not ACIDIC because
  vinegar is.

Wiring `acidity_band` directly from member bands would reintroduce exactly the rule that review
removed.

## Required now, since it is not being wired

1. **Fix the reason code's premise.** `NO_SOURCED_PH_TABLE` is now false — a sourced table exists.
   The cell should say `PH_CROSSWALK_UNVERIFIED` (band exists, verification pending) or
   `ING_NOT_IN_PH_CROSSWALK` (not among the 140). A reason that states a false fact is worse than a
   blunt one, because it tells a reader to go looking for a table that is already here.
2. That change **is** a `C_t` change and re-fills the corpus, so it carries the same cost as wiring.
   Either take both costs together after the freeze, or take neither now and record the reason code
   as knowingly stale, with the correction already written in
   `reports/s179/d116_composition_state_schema_v1.md`. I prefer the second before 19 Nov.
