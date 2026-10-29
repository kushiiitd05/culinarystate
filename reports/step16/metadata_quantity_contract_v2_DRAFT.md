# Step 16 metadata and quantity AST contract rc2 — DRAFT_PENDING_H4

2026-10-28. Engineering proposal requested by Parv. No human label, pilot
annotation, schema freeze or scientific threshold is supplied by this document.
It closes the specified representation gaps as a tested draft, not an approved
production migration.

## Basis and version boundary

- Execution Plan v2 Step 16 Method and 16-B, especially the three independent
  metadata axes, quantity AST, separate interval types and no invented grams.
- SSOT v15 ranges read: 235 (lines 25500–25586), 237.1 (25661–25689), and
  the annotation/provenance rules in 239.1 (26102–26148). The full SSOT was not loaded.
- The prior v0 ledger schemas and all ten existing rc1 draft files are unchanged.
  New files `schema_drafts/{QNT,STATE}.draft_v2.schema.json` have distinct schema
  IDs, require `schema_version="1.0.0-rc2"`, and require `field_metadata`.
- Code: `src/culinarystate/quantity/draft_contract.py`. The existing semantic
  review overlay gains opt-in JSON Pointer output; its default path format and
  legacy behavior remain unchanged.

Records must explicitly select rc2 and supply metadata. No backfill, value
normalisation, provenance inference or migration is performed by validation.
`make_record_schema(v1_schema, kind)` deterministically generates the separate
proposals without mutating its argument; a mismatched source record type fails.

## Metadata coverage and consistency

Each present semantic claim requires the existing triple:
`origin`, `status`, `claim_route`. Enum members match the current provenance,
field-status and claim-route registries; their meanings are not newly approved.
Optional `evidence_refs` hold nonblank references, not new ledger IDs. The
validator checks syntax, not whether a source or human verification really exists.

Metadata can be inline as `meta` on a value object, or in the record's
`field_metadata` map at its exact JSON Pointer. Inline and mapped copies must
agree if both exist. There is no ancestor inheritance or default metadata.
Stale, malformed or out-of-scope pointers fail rather than being ignored.

| Record | Claim targets |
|---|---|
| QNT | Every present field in `QNT_FIELDS` in the module: raw/parsed/normalised values, mass/volume/count, qualifiers, conversion method/path, portion/Q-level/locale/ingredient link, both normalised mass bounds, scope/state/packing/multiplier/dual-expression/unit/era fields. Each `intervals` entry is its own target. |
| STATE | Present belief, quantity, location, form, existence, container, plus each individual `variables` value. |
| AST | Each node has mandatory inline metadata. The top `/ast` pointer may additionally duplicate that metadata only if identical; descendant AST nodes are covered inline, not by inherited root metadata. |

Envelope IDs/versions, timestamps, record provenance/verification, linking/order
fields, external references and notes are not reinterpreted as measured recipe
claims. This explicit coverage boundary is a proposal for H4, not a claim that
the plan's broad "every field" wording has already been adjudicated.

Pointers follow [RFC 6901](https://www.rfc-editor.org/rfc/rfc6901): slash and
tilde in member names are escaped, array indices are explicit, and the empty
pointer denotes the document root. No URI fragment syntax or Unicode name
normalisation is applied. The rc2 validator returns pointer paths; the older
review API keeps its prior display paths unless `pointer_paths=True` is requested.

UNKNOWN and NOT_APPLICABLE metadata cannot carry a known numeric, categorical
or qualitative claim. An explicitly unknown quantity may retain a declared unit
without inventing its amount. KNOWN zero is valid and distinct from UNKNOWN.
CONFLICTING/CENSORED evidence is retained; arithmetic will not treat it as an
exact point. MODEL_ESTIMATED/INFERRED_LLM/SIMULATED origins remain visible in
results and are never changed to observed or human-verified evidence.

## Typed AST payloads

All nodes require `node_type` and metadata. Unknown payload fields are rejected;
optional raw text is preserved verbatim.

| Node | Payload and arithmetic rule |
|---|---|
| RATIONAL | Nonnegative integer numerator, positive integer denominator, explicit nonblank unit. No floating-point literal or hidden unit conversion. |
| RANGE | Finite nonnegative low/high with low <= high, explicit unit. This AST node represents SOURCE_RANGE, not conversion uncertainty or empirical quantiles. |
| ADD | At least two children; identical declared units. Preserve interval bounds. |
| MULTIPLY | Exactly two children; at least one has explicit dimensionless unit `1`. Do not infer density or multiply two physical dimensions. |
| FRACTION_OF | Exactly two children: dimensionless factor in [0,1], then the whole quantity. |
| REMAINDER_OF | First child is the total; remaining children are explicit allocations in the same unit. Subtract interval bounds conservatively. |
| PACKAGE_CONTENT | Exactly two children: explicit dimensionless package count, then explicit per-package quantity. Counts may be fractional when stated. |
| ALTERNATIVE | At least two children. Preserve separate outcomes, even across units; never select, sum or multiply branches. |
| QUALITATIVE | Nonblank raw expression, no numeric payload; never substitute grams. |
| OPEN_AMOUNT | Nonblank raw expression, no numeric payload; preserves an open amount. |
| UNKNOWN | No numeric payload; metadata status UNKNOWN or NOT_APPLICABLE; a declared unit may be retained. |

Possible allocation overrun (interval crosses below zero) gives UNKNOWN with
`POSSIBLE_OVERALLOCATION`; a definite overrun is an error. Neither is clipped or
repaired. An unresolved alternative inside arithmetic is an error. Unknown or
qualitative operands mask numeric arithmetic rather than contributing zero.

The arithmetic result retains source interval tags and provenance classes. Its
`to_mapping()` method serialises exact endpoints as numerator/denominator pairs,
with unknown endpoints as null and alternatives kept as a list. This result is
not a QNT ledger record, a source annotation, or an observed/human-verified value.

## API and synthetic demonstrations

```python
import json
from pathlib import Path
from culinarystate.quantity.draft_contract import validate_record, evaluate_ast

schema = json.loads(Path("reports/step16/schema_drafts/QNT.draft_v2.schema.json").read_text())
issues = validate_record(candidate_record, schema)
if not issues and "ast" in candidate_record:
    arithmetic_result = evaluate_ast(candidate_record["ast"]).to_mapping()
```

`validate_record` combines structural schema checks, per-claim metadata checks,
cross-field interval checks, and AST arithmetic checks. Passing JSON Schema
alone is insufficient. `validate_ast` checks typed payload/local metadata;
`evaluate_ast` additionally checks composition and arithmetic. Neither function
reads files or real recipes, writes ledgers, or chooses evidence on the caller's
behalf. Unit equality is literal: `kg + g` is rejected even though a separate
approved physical conversion could reconcile them.

`quantity_contract_synthetic_examples.json` contains seven computed demonstrations
labelled AI_DRAFT_SYNTHETIC_ONLY_PENDING_H4. Independent known-answer tests cover
exact fractions, 2 x 400 g, range addition, fractions/remainders, alternatives,
unknowns, invalid dimensions, metadata gaps/conflicts, escaped paths, version
selection, provenance retention and JSON serialisation. These are not Gold
labels or a pilot packet. The test file contains 54 cases.

Verification: 54 new synthetic cases pass; the full unit suite gives **1,616
passed, 1 skipped, 1 deselected** with CPU thread caps, including transition
tests. The existing `not ledgers` marker policy accounts for the deselection.
Existing rc1/frozen schemas, ledger baselines, strata, threshold registry and
Step 35 signed-document candidates are unchanged. Generation of both rc2 schemas
is deterministic, and all seven stored examples reproduce from their ASTs.

## Boundaries and decisions still needed

1. H4 reviews the metadata coverage roster, sidecar/inline policy, node payloads,
   dimensionless marker, interval/overrun policy and wire representation.
2. This does not parse source text into the new AST, certify metadata assertions,
   resolve a locale or select/verify POR records. No cup/count-to-mass default,
   density, midpoint, model estimate or Q-level is generated by the evaluator.
3. Conversion uncertainty and empirical intervals stay separate QNT entries with
   their own metadata. Their combination/calibration and full linkage to
   `mass_g`/POR evidence remain later grounding/invented-value-auditor work.
4. The rc1 history-field MODEL/SIMULATED restriction is inherited unchanged.
   Externally measured history and full source/claim-route policy still need
   an explicit reviewed decision. This proposal does not freeze them.
5. Step 19 pilot authorisation/annotations and H4 are still required before 16c.
   No real recipe, pilot selection or human annotation was processed here.

### Legacy issue and versioned engineering resolution

A synthetic check of the existing v0 parser/normaliser with
`0 x 400g cans synthetic ingredient` parses multiplier 0, but its
`p.multiplier or 1.0` default produces mass 400 g and count 1. The new AST
represents a stated zero correctly; it is not automatically wired into that
legacy normaliser. Preserve the historical/frozen path and fix this in an
explicitly versioned normaliser/adapter with regression coverage before that
path is used for new extraction. S152 now supplies that separate normaliser and
an opt-in parsing bridge, with zero/invalid-input/precision controls. The frozen
legacy path remains unchanged and no real recipe base was recomputed; incidence
in real data was not measured. See `engineering_and_pilot_lane_build_note.md`.

Independent S152 review also fixed integral-JSON-float handling, null UNKNOWN
layers, descendant provenance retention, mandatory schema-version presence and
large integer robustness. Original findings and final dispositions are retained
in `rc2_independent_agent_review.md`. The earlier 54-case count is historical;
the contract test file now contains 60 cases.
