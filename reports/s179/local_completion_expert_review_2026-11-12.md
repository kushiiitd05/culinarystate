# Local completion and strict runtime review — 12 November 2026

Status: **AI_DRAFTED / AI_PRECHECKED / DIAGNOSTIC / NON_CITABLE / NO_HUMAN_SIGNOFF_D085**.
Reviewer: author-only review (AI-delegated). This is an engineering/source-contract precheck, not independent
human verification, a scientific gate approval or an adoption signature. Frozen v1 artifacts are unchanged.

The earlier `emission_path_review_2026-11-11.md` is retained as the inventory/reproduction record. This dated
follow-up addresses the proposed separate strict-v2 runtime and the limits of locally completing MUST work.

## Strict admissibility must be independent of retrieval rank

The existing `retrieval/compatibility.py` vector was built for ranking. It cannot be used as a scientific
eligibility certificate. The current `decision/pipeline.py:159–167` constructs only ingredient/process/target
text for retrieval; state, time, temperature, medium and basis stay absent. A new adapter must preserve
explicitly supplied context and make unavailable fields UNKNOWN rather than silently supplying defaults.

| Axis | Existing behavior requiring care | Conservative strict-v2 criterion |
|---|---|---|
| Matrix | Exact ING ID, parent/other relations, group-name substring and broad food-group routes can all retrieve rows | Require an explicit active ingredient ID equal to the row's ingredient ID for a question-specific numeric effect. Parent/child/group transfers require their own named rule; otherwise they are background only. |
| Process | `STEP` and exact process both produce vector MATCH | Require the exact requested process ID. A row describing a multistep sequence is not automatically a measurement of one component step; reject implicit STEP transfer unless separately declared. |
| Target | Bidirectional raw-name substring; an empty row target name can satisfy substring logic | Link to a unique canonical SVAR identifier through an explicit registry mapping and require the same target ID. If linking or duplicate resolution is ambiguous, preserve UNKNOWN. Do not compare total vitamin C with reduced AA by string overlap. |
| Initial state/form | Substring comparison; nonmatching known states become NEAR | Require an explicit canonical state/form match under a declared vocabulary. Raw/cooked/canned/previously processed states are not interchangeable. Unknown is not a favourable match. |
| Measurement basis | Mismatching nonempty bases become NEAR | Require the same explicit quantity basis, analyte basis and denominator/reference definition. Fraction versus percent is a scale conversion, not a conversion between true/apparent retention, dry/wet basis or AA versus AA+DHA. |
| Duration | Any interval overlap produces MATCH | For the first conservative strict version, require equal typed reported/query intervals in the same exactly converted unit. Mere overlap or interval containment is not an experimentally justified interpolation. Never choose a midpoint or change a one-sided bound into a point. |
| Temperature | Any interval overlap produces MATCH; only the first degC entry is used | Require explicit equal typed bounds plus the same temperature location/meaning (product/core, bath, oven, etc.). Multiple source temperatures require disambiguation; equality to an unrelated sensor does not suffice. |
| Medium/contact | Substring matching between free-text fields | Require a declared canonical medium/contact match. Do not match water/oil by arbitrary substring, infer no water contact from an omitted phrase or replace missing medium by a scenario default. |
| Evidence/condition status | Retrieval DIRECT checks food/process/target only | Require an active row and active referenced COND record, valid typed finite values/units and the declared source class. Retain E3_UNVERIFIED/COND_UNAUDITED provenance; this does not repair G08-3 or certify the primary source. |

For interval checks, validate finite ordered endpoints and exact unit semantics before comparison. Where a field
is genuinely NOT_APPLICABLE, that status must come from an explicit contract/source interpretation; absence alone
is UNKNOWN. Do not require an invented numeric value for an inapplicable axis.

If the query axis is unknown, ASK is appropriate only if an answer to that question could change admissibility.
If the source axis itself is unknown, obtaining a value from the user does not fill the source's missing value.
No admissible row means no question-specific effect answer; it does not mean the compound/effect is experimentally
absent. Related evidence can be identified as background only, without becoming an answerability grant.

## Binding and output contract

1. Filter each option's evidence separately. Never union packets before authorizing values; bind each claim to
   one named option and that option's admissible row set. Retain the requested target/food/process/context in
   the claim's structured metadata so the audit can verify it independently.
2. Prefer deterministic fact construction from admissible row objects. A free-form sentence containing a valid
   EVD ID and a similar number can still assign that number to the wrong food, process, target, option or unit.
   Unknown free-form chemistry assertions should not be certified by citation presence alone.
3. A censored limit is not a measured point. Retain inequality direction, censor type and unit. Do not authorize
   an exact value or reversed inequality merely because its magnitude equals the source limit.
4. Numeric ranges require provenance for each endpoint. Aggregates/medians require an explicit computation
   provenance record and correct source set; they do not become raw measurements or independent observations.
5. Missing/invalid decision mode or precision is a refusal, not permission to print. Recheck deterministic
   fallback through the same strict claim contract. If fallback also fails, return a fixed nonnumeric refusal.
6. Preserve conflict rows and uncertainty. Do not select only the favourable direction to manufacture an
   answer. Provisional lineage keys and repeated rows do not establish independent experimental corroboration.
7. Keep physical input provenance per quantity. TEXT_STATED versus PHYSICAL_DEFINITION, CARRIED_SETPOINT,
   ASSUMED_DEFAULT, SCENARIO and MODEL_DERIVED are different bases. Scenario-derived temperature/time cannot
   silently provide empirical applicability for a nutrient effect or establish physical impossibility.
8. A model number needs the actual frozen fit/model/PARAM/VAL chain and its allowed scope, not merely an ID-like
   string. The unchanged AA production guards remain closed. RESEARCH_ONLY pilot output cannot be relabelled
   VALIDATED_HELD_OUT or empirical EVD evidence; TEST_ONLY outputs cannot be supplied as REAL.

The schema/claim map should distinguish chemistry values, stated physical inputs, scenario estimates,
corpus-pattern scores, source/row counts and UI axis constants. Excluding a category from one detector is not
permission to omit its own provenance/label checks. Rendered browser text and accessibility labels also count
as emissions; checking only server JSON is insufficient for a final UI-level assertion.

## Versioning and evaluation boundary

The P3 boundary proposal dated 11 November remains a proposal until a dated decision adopts an exact policy.
If strict-v2 is adopted as a tightening, write new code/adapter paths, an explicit policy record and fresh
output paths. Do not change frozen scorer, benchmark, prompt, original runner or original output bytes.
Existing frozen D5 results remain H1/H3 RULE_NOT_MET. The old inspected questions are not fresh confirmatory
data; any strict-v2 rerun on them is EXPLORATORY_POST_HOC / NON_CITABLE.

The old lexical audit has its own disclosed scope. It should retain raw baseline violations and unresolved
unit/context cases. A new runtime closing a defect does not retroactively turn the old audit into zero failures.
Likewise, a zero-violation run on deterministic synthetic query templates is an engineering diagnostic on that
sample; it is not a representative user distribution or a semantic certification of the entire system.

## Controls expected before calling the runtime complete

- Exact positive row; wrong matrix; wrong process; multistep-only match; wrong/empty/ambiguous target; known basis
  mismatch; unknown query/source basis; initial-state mismatch; all unknowns explicitly retained.
- Disjoint, overlapping and reversed intervals; nonfinite values; mismatched temperature location; multiple
  temperatures; different media whose words overlap; explicit NOT_APPLICABLE versus absent metadata.
- Exact cited value assigned to another option; range endpoints from different source sets; censored bound
  asserted as exact/opposite inequality; numeric value beyond the old C17 detector's domain.
- Missing precision; generated-text rejection; fallback rejection; fixed nonnumeric terminal refusal.
- Model/scenario input tagged as empirical evidence; L2-only NOT_POSSIBLE; UNKNOWN→SIMULATE; missing PARAM/VAL
  chain; research-only output falsely labelled validated; TEST_ONLY supplied in REAL mode.
- Recipe-bearing sessions, including absent duration-basis metadata, alongside query-only and relationship
  branches. A 1,000-session sample must state its sampling frame, seed and branch/recipe coverage.

## Remaining MUST acceptance limits

| Item | What can be completed locally | What must remain explicit |
|---|---|---|
| T0-C06-R2 | Standalone all-answer/sample audit, emit-path inventory, synthetic controls, strict-v2 engineering diagnostic | Literal zero violations is not satisfied by hiding baseline failures, unclassified numbers or semantic scope gaps. Keep v1 findings and v2 outcome separate. |
| T5-C07-R3 | Source-linked candidate/staging dossier and validator refusal report | Existing G24.4 requires HUMAN_VERIFIED; AI_PRECHECKED cannot satisfy it by relabelling. Do not invent KIN/SEXP/lineage IDs. |
| T5-C11-R3/R4 | Draft calibration/card metadata and guarded code-tested diagnostic | No real validated-domain route or PARAM-calibration pass follows from the descriptive AA pilot or zero eligible SIM-VAL rows. |
| T9-C09-R1 | New actual-frozen-D5 registry/supplement with IDs, seeds, group keys and hashes | Retain the old registry and actual 29-diag split semantics; do not invent absent memberships, an unperformed disjointness check or private reserved-list access. |
| T9-C23-R2 | Evidence map or preview | Acceptance explicitly requires a post-19-Nov date. A 12-Nov artifact cannot complete that temporal condition. |
| T9-C26-R3 | Q&A sheet and rehearsal plan | An actual timed 24-Nov rehearsal cannot be reported as performed now. |
| T9-C28-R2 | Source-window scan on supplied local sources/current artifacts | Missing corpora, images, short excerpts/paraphrases and later final edits remain outside that scan; no release clearance from zero supplied-source matches alone. |
| T9-C20-R1/R3 | Assemble and check reviewable report/deck drafts | Human contribution facts, date/slot/length and actual author edit/review cannot be inferred or supplied by a persona. |

## Review status

This report reviews the existing proposal/contracts and defines concrete checks for new code. It does not
pre-approve an implementation that has not yet been inspected. Any implementation follow-up should record
actual module/test paths and reproducible findings, preserving this initial design assessment as written.

## Implementation review, first pass

Reviewed the new `src/culinarystate/generation/strict_v2.py` and its initial 29 synthetic tests. The explicit
raw-field checks, per-option precision, strict canonical rendering/fallback equality and no-mutation handling
address the earlier ranking/citation/fallback gaps within the declared table-report scope. This is not an
implementation pass: independent probes exposed the defects below.

New reviewer regression file: `tests/unit/test_s179_strict_emission_reviewer.py`.
Command: `python -m pytest -q tests/unit/test_s179_strict_emission_reviewer.py` with one-thread numeric settings.
Initial result: **11 failed, 1 passed**; every row/source object is synthetic.

- Four false-authorizations: missing tier or tier E5/E6/E7 was accepted while every output was labelled
  EVIDENCE_E3_UNVERIFIED. For the current E3-only release, a conservative fix is to refuse every non-E3 source;
  otherwise source-tier-specific labels and an explicit source-class policy are required.
- Two malformed-temperature inputs (`None` and an integer instead of an array) raised TypeError rather than
  returning a refusal. A temperature list containing a non-object item already refused correctly.
- Unhashable source EVD ID and condition reference raised TypeError before validation.
- Three unrepresentable integer inputs (rate, source duration and requested duration) raised OverflowError in
  `math.isfinite`. Numeric validation must not assume every Python integer converts to a finite machine float.

An additional interface limitation is the unbound human-readable option label: a caller can name an option
"fry" while supplying a context whose process ID and matching row are both for boiling. The field checks then
pass, and canonical text inherits the incorrect option name. Bind display names to the exact process ID through
an explicit mapping, or render source process identifiers instead of arbitrary display names. This is distinct
from rechecking the final renderer, because the wrong label can already occur in the canonical authorization.

The current module verifies declared string equality, not active-entity registry membership or every identifier's
syntax. Its `EXACT_DECLARED_FIELDS_ONLY` limit should remain explicit; do not advertise it as full registry or
scientific verification. Callback-generated prose is rejected correctly if it differs from canonical output.

No production/frozen file was changed by this reviewer. Root owns the fixes; the original failed probes and
later regression disposition must remain traceable. Final acceptance is pending rerun after those fixes.

## Implementation follow-up: reported defects closed

Root patched only the new strict-v2 module. Independent rerun of
`tests/unit/test_s179_strict_emission_reviewer.py` and `tests/unit/test_s179_strict_emission_v2.py` completed:
**42 passed in 0.10 s** (12 reviewer cases plus 30 root cases).

- The current E3-only scope explicitly refuses non-E3/missing tiers.
- Malformed temperature arrays normalize to an empty candidate set and return a refusal.
- Invalid/unhashable source IDs and condition references are checked before set/map lookup.
- Unrepresentable numeric inputs return a refusal rather than raising OverflowError.
- Canonical text no longer inherits the arbitrary packet-option name. Numeric records bind option/process,
  ingredient and target identifiers to the exact source row. The additional root test checks a misleading
  "fry" packet key against a boiling context and confirms no falsely named process appears in the output.

The first-pass defects are closed within this module's declared table-report scope. The 11-red initial result
above is retained as the reproducible regression record. No legacy/frozen source or result was changed.
The separate demo adapter, sampled runtime outcomes and wider scientific acceptance remain distinct checks;
these 42 synthetic passes do not establish empirical applicability or a scientific gate pass.
