# Engineering and pilot preparation — AI draft, 2026-10-28

Authorisation: Parv requested both lanes and explicitly requested delegated
reviews wherever expert/human review would otherwise hold up preparation.
Agent reviews are recorded as AI prechecks. They do not supply expert identity,
human labels, signatures or independent human agreement.

## Engineering delivered

- `src/culinarystate/quantity/versioned_normalizer.py`: separate
  `CQPO_NORMALIZE_V2`, preserving the old module. Explicit zero multipliers stay
  zero. Invalid numeric inputs, unknown primary/secondary units and nonfinite
  computed channels are masked and flagged. Unit catalogue/convention semantics
  are reused, not promoted to newly verified scientific facts.
- `src/culinarystate/quantity/parse_adapter.py`: opt-in bridge from the existing
  grammar to rc2 AST, with required caller-supplied metadata and unchanged raw
  text. Exact source fractions remain exact; packages use explicit operands;
  a simple numeric "or" remains an alternative rather than a continuous range.
- Unsupported compound amounts, extra branches, unconsumed units, size-as-amount,
  dual expressions and ungrounded part yields remain UNKNOWN with review flags.
  The adapter deliberately supports a conservative subset, not arbitrary recipe
  language. `requires_review=False` is a syntax/arithmetic result, never a human
  verification, H4 verdict or eligibility for Gold.
- Compatibility normalisation remains float-based and rounded as documented in
  the legacy path. Differences from exact arithmetic are explicitly flagged.
  Long range endpoints that cannot round-trip through numeric JSON bounds are
  not silently declared exact. No density/POR is selected and no volume/count
  is converted into a guessed mass.

## Independent review and resolutions

| Review artifact | Findings and recorded action |
|---|---|
| `rc2_independent_agent_review.md` | R1–R5 reproduced: integral JSON float crash, discarded descendant provenance on masked parent, rejected null UNKNOWN layers, missing mandatory schema version and large-integer crash. Root added six failing-first cases and fixed all; reviewer independently rechecked them. |
| Same report, adapter A1–A5 | Size/count and word-fraction errors, dropped operations/branches, precision disclosure, malformed units/overflow and suffix approximations reproduced. Root added failing-first controls, fixed or conservatively masked the cases, then reviewer rechecked the exact inputs and positive controls. Original findings/hashes and later dispositions are both retained. |
| `../step19/pilot_readiness_and_ai_review.md` | Ten design/handbook inconsistencies, recommendations and exact pilot prerequisites recorded. New draft handbook and synthetic cases prepared. Frozen/current measurement instrument unchanged. |
| `../step19/pilot_methods_agent_review.md` | Twelve statistical/provenance findings with primary references and synthetic counterexamples. CI estimands, capacity/time estimands, censoring, undefined metrics, quota fall-through and exposure decisions require a reviewed amendment before actual decision reporting. No misleading interval or readiness verdict was computed. |

These reviews run alongside implementation. All reported engineering defects
have a reproduced failure and recorded correction; methodological and human
policy choices remain explicitly proposed rather than silently adopted.

## Pilot preparation delivered

`src/culinarystate/annotation/pilot_rehearsal.py` and
`tools/step19_pilot_rehearsal.py` implement six synthetic stages: grouped draw,
blank packets, simulated commitments/snapshots, integrity checks, equality
summary and report. All outputs are REHEARSAL_ONLY and
`counts_as_human_gate=false`. The CLI takes no real input-data path. Fixture IDs
and sources are checked, protected output paths and overwrites are refused.
Six planted tamper/missing-packet/hash/group/snapshot failures are detected.

The committed demonstration is
`reports/step19/synthetic_rehearsal/SYNTHETIC-rehearsal-v1.json`; it reproduces
from `build_report()`. This is not the full PV1–PV10 implementation, an actual
pilot frame/draw, a timing measurement, an IAA estimate or proof of independence.
`A` and `B` are software fixture channels; their ticks are explicitly simulated.

`annotation/annotation_handbook_v2_DRAFT.md` and
`annotation/hard_case_catalog_v2_DRAFT.jsonl` contain proposed instructions and
17 synthetic hard cases. Human/expert outcome fields are blank. These are not
Gold and must not be presented to P1 annotators as replacements for the frozen
v0 + handbook v1/Addendum A measurement instrument without a version decision.

## Concrete real-pilot start record

`reports/step19/pilot_start_record.UNSIGNED.json` binds the original pilot
design, current v0 schemas, gold schema, handbook v1/Addendum A and the two
pilot agent reviews. All 35 proposed threshold rows were structurally checked;
none was written to the threshold registry or signed. The signature guard
refuses the unsigned record.

The selected instrument, actual pre-frame nonce/supplier/commitment, weekly
capacity, per-annotator B_h and human start authorisation are null. The record
acknowledges earlier design-frame metadata exposure; it does not retroactively
claim the nonce preceded any existing frame. The nonce must precede a new
real-pilot frame build as required by the design. Missing human facts were
requested together while engineering continued.

## What remains next

1. Continue real-pilot tooling from the explicitly reviewed sampling/method
   specification; implement full provenance checks and guarded local packet
   creation after the required record is complete. No source text should enter
   an external AI review or git.
2. Resolve the scientific amendments, source/exposure and instrument decisions
   in a final version; obtain actual signatures and the pre-frame human nonce.
3. Humans annotate independently on the approved instrument. Agents may check
   software or draft recommendations; their outputs cannot stand in for those
   independent human observations. H4/16c follows measured pilot evidence.
4. Parsing/AST connection and zero-multiplier correction are implemented as
   opt-in versions; production extractor/POR integration and a frozen migration
   are separate later work. No real extraction or base recomputation occurred.

## Verification

Targeted controls: 60 rc2 contract cases, 37 quantity-pipeline cases, 13 existing
semantic-overlay cases and 22 pilot rehearsal cases pass (132 total). The agent
also rechecked 200 interval extrema and independent adapter reproductions.
Final full-suite counts and preserved-file checks are recorded in WORKLOG S152.

Final full unit result: **1681 passed, 1 skipped, 1 deselected in 76.47 s**, with
CPU thread caps and transition tests included. The existing not-ledgers marker
policy remains. Legacy grammar/normaliser/unit catalogue and protected ledger
checks pass; unsigned pilot/Step 35 companion hashes match. Additional Step 35
chemistry and cuisine review attempts were delegated after these reviews, but
both hit the service usage limit before producing reports; they remain open.
