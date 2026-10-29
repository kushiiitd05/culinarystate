# Independent AI review of Step 16 rc2

2026-10-28. **AI_PRECHECK_ONLY; NOT HUMAN OR EXPERT APPROVAL.** Requested by
Parv as a separate review agent. No annotation, signature, source verification,
schema freeze or pilot gate is supplied. All examples below are synthetic.

## Scope and reproducibility

Reviewed `draft_contract.py`, both generated rc2 schemas, their 54 tests, the
rc2 contract note and the generic semantic review overlay. Read `CLAUDE.md`,
STATUS, recent WORKLOG/DECISIONS, and targeted SSOT ranges 25500–25586,
25661–25689 and 26102–26148. No raw recipe, real label/profile, ledger,
frozen/rc1 schema or external data was evaluated or changed. This agent wrote
only this report, and made no commit or push. The root agent owns fixes and
their verification; findings below describe the initial reviewed bytes.

Initial HEAD: `d3f1832832787f81f7d4906957b708cca25bf0a3`.
SHA-256 of reviewed inputs:

| File | SHA-256 |
|---|---|
| `src/culinarystate/quantity/draft_contract.py` | `84ad8bf092cbf9b3d012a52313a92ace6300c302648729aa6a94a5b9e344d1d6` |
| `src/culinarystate/annotation/schema_review.py` | `6eb22ffcca2d6727120ffb9cd25255fed56ab1e021e329268d93161c30ead75b` |
| `reports/step16/schema_drafts/QNT.draft_v2.schema.json` | `47d7f4720ff6f29de037debd71c888d3b3e5301ccc699b53c99e5a8418fc8f9f` |
| `reports/step16/schema_drafts/STATE.draft_v2.schema.json` | `99e99dc9bd034f759641cde3a4aa3b5f8e591b43660bdb612b39f73d072a6042` |
| `tests/unit/test_step16_quantity_contract.py` | `034a8928683fda0a33dba522008f416672fb6b5efe8052ccbcbd16b02e9cd56a` |
| `reports/step16/metadata_quantity_contract_v2_DRAFT.md` | `14477f15413d1cf72a6d7124a70efe4a27d16d5539ec41a9337242ade00c3975` |

Run from the takeover repository. Reproduction scripts use existing synthetic
test helpers, not production records:

```sh
PYTHONPATH=src:. OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 /Users/parvgoyal/wth/CGAS/Project/culinarystate/.venv/bin/python -m pytest tests/unit/test_step16_quantity_contract.py -q
```

Initial result: **54 passed in 0.28s**. Both JSON schemas also exactly matched
`make_record_schema` applied to their respective rc1 inputs. These passing
checks did not cover the defects below.

## Findings and proposed corrections

### R1 — medium: accepted integer-valued JSON floats crash execution

```python
from tests.unit.test_step16_quantity_contract import rat, record, schema
from culinarystate.quantity.draft_contract import validate_ast, evaluate_ast, validate_record
n = rat(1.0)  # Also reproducible with rat(1, d=1.0).
print(validate_ast(n))
evaluate_ast(n)
# []
# TypeError: both arguments should be Rational instances
r = record("QNT")
r["ast"] = n
validate_record(r, schema("QNT"))  # Same unhandled TypeError.
```

JSON Schema accepts an integral-valued float as `integer`, while the two-argument
`Fraction` constructor rejects float operands. Convert already validated integral
values deliberately to integers, or reject them with a contract issue. Cover both
numerator and denominator and ensure record validation returns issues rather
than leaking implementation exceptions. No numeric approximation is needed.

### R2 — medium: masked composites discard descendant provenance

```python
from tests.unit.test_step16_quantity_contract import rat, op, meta
from culinarystate.quantity.draft_contract import evaluate_ast
n = op("ADD", rat(2, meta=meta(origin="MODEL_ESTIMATED", route="MODEL")), rat(1))
n["meta"]["status"] = "CONFLICTING"
print(evaluate_ast(n).to_mapping())
# status UNKNOWN, reason CONFLICTING, origins ['DERIVED_DETERMINISTIC']
```

The UNKNOWN result correctly avoids a numeric point, but omits the asserted
MODEL_ESTIMATED and EXPLICIT_SOURCE inputs. CENSORED and NOT_APPLICABLE composites
take the same early-return path. A descendant RANGE likewise loses SOURCE_RANGE
tags on that path. Collect descendant provenance/tags independently of numeric
execution so a masked node retains its complete evidence classification without
needing to execute invalid or unavailable arithmetic. Add masked composite tests.

### R3 — medium: legitimate UNKNOWN state layers are rejected

```python
from tests.unit.test_step16_quantity_contract import record, schema, meta
from culinarystate.quantity.draft_contract import validate_record
for field in ("existence", "container"):
    r = record("STATE")
    r[field] = {"value": None, "raw": None, "meta": meta("UNKNOWN", "UNKNOWN")}
    print(field, validate_record(r, schema("STATE")))
# Each returns UNKNOWN_WITH_CLAIM at its field pointer.
```

The schema permits a null value with explicit UNKNOWN metadata. `_has_claim`
nevertheless treats these layer objects as known claims because they have no
embedded `status` key. Recognize their explicit null value as missing while
still rejecting a populated value with UNKNOWN metadata. Preserve raw source
text even if its normalized layer value is unknown. Test both layer types and
UNKNOWN/NOT_APPLICABLE cases.

### R4 — medium: missing schema version passes despite documented version boundary

```python
from tests.unit.test_step16_quantity_contract import record, schema
from culinarystate.quantity.draft_contract import validate_record
r = record("QNT")
del r["schema_version"]
print(validate_record(r, schema("QNT")))  # []
```

The new schemas constrain the version only when present; their required lists
do not include it. The contract note explicitly says the new schemas require
`schema_version="1.0.0-rc2"`. Add the property to the new generator's required
list, regenerate only rc2 outputs, and test absence for QNT and STATE. This
closes the documented version boundary without changing rc1 or frozen behavior.

### R5 — low: large finite integer intervals raise OverflowError

```python
from tests.unit.test_step16_quantity_contract import record, schema, meta
from culinarystate.quantity.draft_contract import validate_record
r = record("STATE")
r["quantity"] = {"status": "RANGE", "low": 10**400, "high": 10**401, "unit": "g"}
r["field_metadata"]["/quantity"] = meta()
validate_record(r, schema("STATE"))
# OverflowError: int too large to convert to float
```

The semantic review overlay calls `math.isfinite` on arbitrary integers during
interval checking. Integers are finite without float conversion. Check integer
and float types separately, or return an explicit range-policy issue if such a
limit is deliberately adopted. A synthetic large integer should not crash the
validator. This is robustness evidence, not a claim that the amount is plausible.

### R6 — review choice: UNKNOWN alternatives preserve numeric branches

An ALTERNATIVE with UNKNOWN parent metadata and two known rational children
returns ALTERNATIVE with both known branches. Arithmetic composites with UNKNOWN
parent metadata instead return UNKNOWN. This need not be a defect: a set of
explicit candidate interpretations can be known even though selection is
unknown. H4 should specify the interpretation and downstream consumers must
not select a branch or promote it to an observed amount. No automatic choice or
gold label is recommended here.

## Independent arithmetic evidence

Enumerated all nonnegative integer-bound intervals `[a,b]` with
`0 <= a <= b <= 3`. For each of the 100 ordered interval pairs, evaluated ADD
and MULTIPLY (first multiplicand dimensionless) and compared the returned exact
low/high with all four endpoint combinations. **200 checks passed**. Reproduce:

```python
from itertools import product
from tests.unit.test_step16_quantity_contract import interval, op
from culinarystate.quantity.draft_contract import evaluate_ast
intervals = [(a,b) for a in range(4) for b in range(a,4)]
for x,y in product(intervals, repeat=2):
    for kind,unit,f in (("ADD","g",lambda a,b:a+b),
                        ("MULTIPLY","1",lambda a,b:a*b)):
        r = evaluate_ast(op(kind, interval(*x, unit=unit), interval(*y)))
        values = [f(a,b) for a,b in product(x,y)]
        assert (r.low,r.high) == (min(values),max(values))
```

Existing tests additionally verify exact fractions, package multiplication,
fraction-of, conservative remainder bounds, definite/possible overrun behavior,
unknown versus zero, forbidden dimensions, alternatives, metadata conflicts,
pointer escaping and nonmutation. This review did not establish exhaustive
correctness for arbitrary trees or source-grounding correctness.

## Expert handoff and remaining boundaries

R1–R5 are reproducible engineering issues; they can be fixed and regression
tested without a consenting chemistry/cuisine expert or human annotation.
The parent agent was informed before this report was finalized. Resolution
must be recorded with changed-file hashes and post-fix tests; the initial
evidence above must remain distinguishable from later corrected behavior.

H4 still owns the semantic coverage roster, the independent metadata axes,
history policy, unit marker and wire contract, interval/overrun policy and R6.
This review supplies recommendations that an expert can independently challenge.
It does not verify provenance assertions, whether an evidence reference exists,
POR/locale choices, source spans or compatibility between AST output and the
separate normalized/mass fields. Those are explicit grounding and integration
tasks; passing this validator alone cannot certify a source claim.

Human Step 19 independent annotations, their provenance and agreement remain
required for a real pilot/freeze. Agent review does not count as an annotator,
second reviewer, chemistry/cuisine sign-off or a replacement statistical gate.
Synthetic pilot engineering and versioned adapters can continue in parallel.

## Independent post-fix verification — 2026-10-28

The root agent implemented R1–R5 after receiving the initial findings. This
review agent independently reran every original reproduction against the changed
bytes and added the following adversarial variations in an ephemeral script:

| Finding | Independently observed disposition |
|---|---|
| R1 | Both integral-float numerator and denominator evaluate exactly to 1; the corresponding QNT records validate without exceptions. |
| R2 | CONFLICTING, CENSORED and NOT_APPLICABLE composite outputs have no numeric endpoints and retain MODEL_ESTIMATED provenance and SOURCE_RANGE tags from their descendants. |
| R3 | Both existence/container with null values and retained synthetic raw text validate with UNKNOWN or NOT_APPLICABLE metadata; adding a populated normalized layer still produces an issue. |
| R4 | Missing version is rejected for both QNT and STATE; both regenerated schemas exactly equal their generator output. |
| R5 | The original large finite integer interval validates without OverflowError. This remains structural acceptance, not a scientific plausibility ruling. |

Combined existing/new contract and semantic-review tests:

```sh
PYTHONPATH=src:. OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 /Users/parvgoyal/wth/CGAS/Project/culinarystate/.venv/bin/python -m pytest tests/unit/test_step16_quantity_contract.py tests/unit/test_schema_semantic_review.py -q
```

Result: **73 passed in 0.28s** (60 contract cases, 13 semantic-review cases).
R1–R5 are resolved on the exact reviewed working-tree bytes below; no human
semantic approval is implied. R6 and the expert/human boundaries above remain.

| Changed file | Post-fix SHA-256 |
|---|---|
| `src/culinarystate/quantity/draft_contract.py` | `ce48b01ed6721d1c6a0f6472303f6bd93a24400e99175cede285015641c36bc9` |
| `src/culinarystate/annotation/schema_review.py` | `e27bc6377ed38216aa57869b33241af449dbdfdc0bd6a6f3a8188a725f738be9` |
| `reports/step16/schema_drafts/QNT.draft_v2.schema.json` | `02be26be679a70fd90d806cc05017cd02924a4342ae01c8d7d42812ec2136465` |
| `reports/step16/schema_drafts/STATE.draft_v2.schema.json` | `b15c1c587028d45a78eac188b4452711e332013621dc10d4e329c2c635016496` |
| `tests/unit/test_step16_quantity_contract.py` | `fc98c8102c974e64a1f1bcdf9b1a357f59252283c96137b3e2d3438af9c87dbe` |

## Independent adapter review — 2026-10-28

Reviewed the subsequently added `parse_adapter.py`, `versioned_normalizer.py`,
their 16 synthetic tests, and their interactions with the untouched v0 grammar,
normalizer and unit helpers. Initial targeted tests: **16 passed in 0.14s**.
Initial reviewed hashes:

| File | SHA-256 |
|---|---|
| `src/culinarystate/quantity/parse_adapter.py` | `70116f51c4a828ecae73d288a870b0d45c5216ed162c658fa6a50e7f317f7e62` |
| `src/culinarystate/quantity/versioned_normalizer.py` | `97800b3fa20b3f33b6cb282b051a7e5db99871f1c4b3f0be0bd9ac48cad8df0f` |
| `tests/unit/test_quantity_v2_pipeline.py` | `db24ec5fd86d0a15d6793be96cb20bfeafab560fe8312b67d016c263edaf75da` |

The tests passed despite the following integration defects. All were reported
promptly to the parent agent. These are engineering findings from artificial
ingredient strings; they supply no human labels or measured quantities.

### A1 — high: source size and word fractions become different amounts

Use `parse_quantity_v2(raw, source_metadata=META)` with META from
`tests.unit.test_quantity_v2_pipeline`:

| Synthetic raw | Initial arithmetic output | Evidence and recommendation |
|---|---|---|
| `5cm piece synthetic ingredient` | KNOWN 5 piece, no flags, review false | Grammar intentionally represents length as size and sets count to 1; adapter incorrectly reuses the leading 5 as count. Reject unsupported length/size interpretation or use a reviewed explicit representation. |
| `1/2 inch piece synthetic ingredient` | KNOWN 1/2 piece, no flags | Same length-as-count error. |
| `a half cup synthetic ingredient` | KNOWN 1 cup | Grammar parses 0.5, but adapter picks WORD_COUNT `a` rather than the full phrase `a half`. Match the complete quantity phrase or flag UNKNOWN. |
| `half a cup synthetic ingredient` | KNOWN 1/2 item, no flags | Grammar leaves `cup` in its unparsed remainder; adapter presents a bare item quantity without review. Explicitly support the unit-bearing phrase or flag incomplete integration. |

### A2 — high: unsupported operators and alternatives are silently truncated

| Synthetic raw | Initial arithmetic output |
|---|---|
| `2.5 x 400g cans synthetic ingredient` | KNOWN 5/2 item; no flags/review |
| `1/2 x 400g cans synthetic ingredient` | KNOWN 1/2 item; no flags/review |
| `2×400g cans synthetic ingredient` | KNOWN 2 item; no flags/review |
| `about 2 x 400g cans synthetic ingredient` | KNOWN 2 item, only APPROXIMATE_SOURCE_AMOUNT |
| `1 or 2 or 3g synthetic ingredient` | ALTERNATIVE with only branches 1 and 2; third omitted |
| `1 or 2g or 1 cup synthetic ingredient` | ALTERNATIVE with only first two gram branches; cup omitted |
| `1g plus 2g synthetic ingredient` | KNOWN 1 g; no flags/review |
| `1g + 2g synthetic ingredient` | KNOWN 1 g; no flags/review |
| `1g and 2g synthetic ingredient` | KNOWN 1 g; no flags/review |

Validate that the complete source quantity expression is consumed before
exposing KNOWN/RANGE. Unsupported multiplication/addition syntax and additional
alternative branches should become UNKNOWN with a specific flag, or be parsed
fully into a supported AST. Preserve the complete raw string. A known result
for the consumed prefix must not stand for the full source expression.

### A3 — medium: precision losses are not consistently disclosed

`0.123456789123456789-0.223456789123456789g synthetic ingredient` produces
RANGE endpoints reconstructed from binary floats, different from the exact
decimal source endpoints, with no flag. A denominator containing only 2 and 5
does not guarantee a decimal can round-trip through a Python float. Compare
`Fraction(str(float(endpoint)))` to the exact endpoint before constructing the
current RANGE payload; otherwise retain UNKNOWN or extend the draft payload
deliberately to exact rational bounds.

`0.0000001g synthetic ingredient` keeps exact AST amount 1/10000000 but reports
normalized mass 0.0 with no precision flag. Likewise a long terminating decimal
scalar is rounded to six decimal places without a flag. `2 x 1/3g cans synthetic
ingredient` gives exact AST 2/3 but normalized 0.666667 without a precision flag.
Separate compatibility-channel output must explicitly disclose material rounding
or avoid presenting an unqualified zero. Check all arithmetic source operands,
not only standalone nonterminating scalar fractions.

### A4 — medium: incomplete input/output validation in versioned normalizer

Construct `QuantityParse` directly (public function accepts it):

```python
from culinarystate.quantity.grammar import QuantityParse
from culinarystate.quantity.versioned_normalizer import normalize_v2
normalize_v2(QuantityParse("synthetic", "NUMBER", value=2, unit_key="g",
                           alt=(3, "not_a_unit")))
# KeyError: 'not_a_unit'
normalize_v2(QuantityParse("synthetic", "NUMBER", value=2, unit_key="g",
                           alt=(float("nan"), "g")))
# MEASURED 2 g; invalid alternative is ignored without a flag.
normalize_v2(QuantityParse("synthetic", "NUMBER", value=2, unit_key="not_a_unit"))
# MEASURED count 2 item; unknown explicit unit silently treated as absent.
normalize_v2(QuantityParse("synthetic", "NUMBER", value=1e308, unit_key="kg"))
# MEASURED mass inf g; no flags.
```

Validate the primary and alternative unit keys, all alternative numeric input,
and finite computed channel output. Return UNKNOWN with a specific review flag
instead of a runtime exception, silently ignored invalid evidence or infinity.

### A5 — medium: approximation after the amount is not flagged

`1g approximately synthetic ingredient` initially returns KNOWN 1 g with no
flags/review. Approximation detection covers the leading phrase only. Recognize
supported modifier positions conservatively; make the draft uncertainty visible.
`up to 2g synthetic ingredient` at least raises APPROXIMATE_SOURCE_AMOUNT, but
its upper-bound meaning remains an H4/open-amount modeling question. No exact
source amount should be claimed from an upper bound without that qualification.

### Correctly handled examples and review boundary

Initial adapter preserved exact 1/3 scalar ASTs, flagged nonterminating range
bounds, kept simple two-way OR as alternatives, rejected cross-unit OR and
dual expressions as UNKNOWN, masked invalid numbers, and handled explicit zero
packages. Implicit `large can ...` remained UNKNOWN rather than inventing an
AST count. These positives do not close A1–A5.

No root fixes were applied by this review agent. Post-fix dispositions, when
independently rerun, must follow below without erasing this initial evidence.

### First independent adapter retest — 2026-10-28

After root's first adapter fixes, combined pipeline/contract/semantic tests
passed: **105 passed in 0.34s** (32 pipeline, 60 contract, 13 semantic).
Ten separate positive/boundary controls also passed: exact 1/3 scalar, 800 g
package result, zero package, `a half cup` = 1/2 cup, source-range endpoints,
two-way alternatives, malformed division, nonterminating range, cross-unit OR
and unstated quantities. Exact raw strings remained preserved in scalar/package
checks.

The initial length/count, numeric compound/multiplier, extra OR, decimal-range,
rounding, normalizer invalid-input/overflow, and approximation examples were
independently rerun. A3–A5's exact reproductions now have the expected review
flags or UNKNOWN output; the initial A1 `a half cup` error is corrected. The
following A1/A2 cases remained unresolved at this first retest and were reported
to root immediately:

| Synthetic raw | First retest result |
|---|---|
| `half a cup synthetic ingredient` | KNOWN 1/2 item; no flags/review (original A1 reproduction). |
| `1g plus two g synthetic ingredient` | KNOWN 1 g; no flags/review (word-number variant of A2). |
| `1 and a half g synthetic ingredient` | KNOWN 1 item; no flags/review. |
| `2 x 400g/14oz cans synthetic ingredient` | KNOWN 800 g; no flags/review (grammar discards the secondary unit). |
| `1-2-3g synthetic ingredient` | RANGE 1–2 item; no flags/review (third term omitted). |

These show why the full-consumption recommendation matters. Conservatively
mask an unconsumed quantity-bearing suffix/operator rather than treating the
consumed prefix as a complete source expression. No scientific judgment or
real recipe inference is needed to implement this guard.

First-retest working-tree SHA-256:

| File | SHA-256 |
|---|---|
| `src/culinarystate/quantity/parse_adapter.py` | `05ac1d874ce7fec7ddf36e4dce650e00a336b8c706fb5b5e1e683a5d1e5305b3` |
| `src/culinarystate/quantity/versioned_normalizer.py` | `5deba6a0385217e113dd27a84246b0c32920aab93b6bbd1c14046fa1a3ddc54f` |
| `tests/unit/test_quantity_v2_pipeline.py` | `0ac8150ac5cf54d5f7b82d6cddbba983c8a510a4082662c2159f49a0cc2ba4bb` |

### Final independent adapter disposition — 2026-10-28

Root added expression-consumption guards and five additional regression cases.
This review agent reran the original and follow-up reproductions against the
stable changed modules. All reported A1–A5 engineering reproductions are now
resolved by exact supported parsing, explicit UNKNOWN masking, or required
review flags as appropriate. In particular, `half a cup` is conservatively
UNKNOWN with UNCONSUMED_UNIT; it is not reported as a bare item quantity.

Independent ephemeral-script results:

- **17 unsupported-expression checks passed:** both length examples, half-a-cup,
  all unsupported package multiplication forms, extra alternatives, numeric and
  word additions, imprecise decimal range, approximation-prefixed package,
  package dual units and repeated range separator. Each returned UNKNOWN with
  flags and `requires_review=True`.
- **5 precision/approximation checks passed:** tiny and long-decimal masses,
  fractional package mass and suffix/upper-bound approximation each retained
  the appropriate explicit review flag.
- **6 positive controls passed:** exact 1/3 scalar, 800 g package, zero package,
  a-half-cup, source range and two-way alternatives. Scalar/package checks also
  preserved exact input raw strings.
- **4 normalizer robustness checks passed:** unknown primary/alternative units,
  nonfinite alternative and overflowing derived mass were masked with flags.

Combined regression command:

```sh
PYTHONPATH=src:. OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 /Users/parvgoyal/wth/CGAS/Project/culinarystate/.venv/bin/python -m pytest tests/unit/test_quantity_v2_pipeline.py tests/unit/test_step16_quantity_contract.py tests/unit/test_schema_semantic_review.py tests/unit/test_step19_pilot_rehearsal.py -q
```

Result: **132 passed in 0.35s** (37 pipeline, 60 contract, 13 semantic, 22 pilot
rehearsal). The rehearsal count records successful execution of its tests; this
agent's substantive review scope remains the quantity contract/adapter.

| Final reviewed file | SHA-256 |
|---|---|
| `src/culinarystate/quantity/parse_adapter.py` | `ad52c055d19d229d012c7de0a6d91329ebe3ff43512c98df58d6fcb23cda9275` |
| `src/culinarystate/quantity/versioned_normalizer.py` | `5deba6a0385217e113dd27a84246b0c32920aab93b6bbd1c14046fa1a3ddc54f` |
| `tests/unit/test_quantity_v2_pipeline.py` | `23c09f8e00a0eff3ee9791e049a329c99c9ca4b00b224333627b090d2c4e1fec` |

This closes the reported engineering findings for these bytes, not every
possible source expression. Callers must inspect arithmetic status and review
flags; the compatibility normalization channels retain their separately named
v0 conventions and cannot override an UNKNOWN AST or a review requirement.
R6, H4 semantic decisions, source grounding and the independent human pilot
remain pending as described above. No human or expert certification is supplied.
