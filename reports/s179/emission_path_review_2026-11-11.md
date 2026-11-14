# Answer emission-path review — 11 November 2026

Status: **AI_DRAFTED / AI_PRECHECKED / DIAGNOSTIC / NON_CITABLE / NO_HUMAN_SIGNOFF_D085**.
Scope: T0-C06-R2, read-only review at base `b76aa7ab`. Reviewer: author-only review (AI-delegated).
No frozen scorer, benchmark, preregistration, result, production code, ledger or decision was changed.

## Acceptance and interpretation

The S178 board requires the full D5 answer set, 1,000 random demo sessions, an emit-path inventory and planted
controls for four composed rules. Its zero-violation requirement is a check to perform, not an assumption.
Every baseline answer must be inspected; deliberately unconstrained baselines cannot be removed to obtain zero.
State/next-action blocks can also hallucinate chemistry and must not be excluded solely by block name.

D-085 permits labelled AI-delegated checks. D-088 forbids converting those checks into independent labels or
human verification. D-086's frozen crosswalk maps DIRECT/INTERPOLATE to `evidence_supported`, with E3/condition
caveats. It does not establish primary-source truth or applicability to a recipe's measured conditions.
An EVD identifier and a matching retention value are necessary provenance checks, not semantic entailment.

## Emission inventory

Paths are relative to the repository. Line numbers refer to the reviewed base; later edits must be rechecked.

| Path / lines | Emit path | Numeric/provenance audit requirement |
|---|---|---|
| `app/server.py:141–165` | HTTP `/api/ask` serializes `ctx.respond`; error replies have no scientific answer | Audit the JSON and its rendered fields, not only HTTP success. Socket/rate-limit tests are separate from provenance. |
| `decision/front_door.py:26–48` | Branch handler envelope; safety, malformed, unavailable, unsupported and exception refusals | Retain DEMO_ONLY/NON_CITABLE/E3 labels and `citable=False`; unknown branch/handler failure must not become an answer. |
| `decision/demo_context.py:160–185` | TRANSFORMATION: pipeline → template → evidence label; target-absence override | Match every emitted food-effect number to its cited active EVD row, value/scale, target, food/process relation and allowed precision. Presence override must emit no retention figure. |
| `decision/demo_context.py:77–89,187–195` | RELATIONSHIP: corpus co-occurrence scores, no EVD | Classify these as corpus-pattern metadata, not nutrient/effect measurements. Retain the pattern caveat and public-mode restrictions. |
| `generation/verbalize.py:68–85` | Single option: retention points/ranges or direction/conflict; row/source counts | Distinguish retention values from counts. Endpoints cite their own rows; censored bounds must not become point measurements. Direction-only/conflict answers must not gain chemistry numbers. |
| `generation/verbalize.py:88–99,102–136` | Diagnosis/recovery cookbook statements; ASK/refusal; comparisons/recommendations | Source-count metadata and potential quantities inside cookbook statements require explicit classification. Check each option's cap, not a global weakest/strongest shortcut. |
| `generation/prompts.py:31–65`; `tools/run_ladder.py:54–78` | B0/B2/B5/B5F raw LLM text, B5F+E enforcement, B5T template | Prompts are instructions, not runtime guarantees. Inspect raw and enforced arms separately; B5F+E/B7 and B5T are distinct paths. |
| `tools/s179_d5_run_rungs.py:79–95,103–130` | Frozen S block LLM answers and mapped P/C/U/X ladder answers | All saved answers remain in scope. P/C records retain decision/slots/packet IDs only for B5/B7/B5T; missing metadata in other arms is an audit limitation, not evidence of correctness. |
| `generation/claims.py:15–64`; `generation/enforce.py:20–52` | Numeric detector, packet/value check and sentence filter/fallback | Existing detector is a narrow retention-claim checker. Independently check detector coverage, value/bound meaning, citations, option scope, cap and fallback. |
| `decision/pipeline.py:159–183`; `decision/comparator.py:18–51` | Packet-derived comparator/Pareto/candidate metadata | Comparator summaries use per-group medians and censored limits; these are derived summaries, not laboratory values. Local candidate carbon/time metadata needs its own provenance. Current demo answer does not expose all pipeline internals. |
| `decision/evidence_label.py:47–91` | Answer badge from packet relations and precision | `from_data=True` requires every pooled food/process relation to be exact; mixed pools take the weakest basis. Badge does not inspect condition-axis compatibility or raw-source quality. |
| `mechanism/router_demo.py:58–65,171–260` | Per-event route and EVD summaries; optional simulation attachment | Withheld evidence belongs in `evidence_not_applied`, never applied numeric evidence. Route counts/IDs are metadata. Keep NO_CONDITIONS_CONSUMED and non-citable envelope. |
| `decision/demo_context.py:100–124,175–179` | Recipe physical layer: stated inputs and scenario estimates | Audit the recipe-bearing path separately. Global labels do not prove every numeric field has its own D-077 basis. Scenario/model-derived numbers cannot become empirical food-effect evidence. |
| `mechanism/simulate_branch.py:535–547,638–705` | Optional reduced-AA retention interval with PARAM/VAL/fit/run references and input basis | Real path must first pass its guards; preserve NOT_VALIDATED/RESEARCH_ONLY/NON_CITABLE, `physically_possible`, basis mismatch, PARAM/VAL references and SCENARIO when Layer 2 is used. No TEST_ONLY fixture may pass as REAL. |
| `mechanism/applicability.py:619–659` | Structured route decision, domain/unknown handling | UNKNOWN cannot become SIMULATE. IN_CALIBRATION_ONLY stays QUALITATIVE under the unchanged engine. No physical impossibility conclusion may rest only on an L2 scenario value. |
| `app/static/index.html:131–197` | Renders answer, evidence badge, EVD IDs, physical input/estimate fields | Verify visible and accessibility text, not only server JSON. Numeric chart axes are UI constants, not scientific outputs. Rounded estimates retain their estimate scope. |
| `decision/public_mode.py:99–130`; `app/server.py:119–139` | Filters public KGE/carbon and refuses public-looking requests in local mode | Public-mode sampling does not certify local-only carbon/duration paths. Enumerate exclusions and retain their own checks. |

## Concrete findings and reproducible controls

1. **The existing numeric detector is incomplete for the board's broader chemistry-number wording.**
   `generation/claims.py:17–18` recognizes percentages and decimal fractions beginning with 0 or 1; it deliberately
   excludes duration/temperature/quantity contexts. In a synthetic check, a sentence containing retention 2.5
   and nutrient content 10 mg produced `numeric_claims=0`. A separate detector must cover relevant integers,
   values above two, signed/scientific notation and units, without mistaking IDs/counts/chart constants for claims.

2. **Citation/value alignment does not check semantic scope.** `claims.py:46–60` receives no ingredient/process/
   target query and checks whether any cited row value lies within tolerance. A synthetic sentence assigning a
   matching percentage to a different food had zero checker errors. Audit matrix/process/target/context separately;
   if a required relation cannot be established, record indeterminate rather than an entailment pass.

3. **Censor direction is not checked.** `row_value` returns a censored limit (`claims.py:24–28`) and the checker
   compares numerical distance only. It does not verify ≥/≤ or prevent a bound becoming an exact value. Template
   `_line` restricts its numeric range to MEASURED rows, but raw/enforced LLM paths still need this control.

4. **Enforcement pools evidence and applies a global cap.** `_union` combines all option rows and `number_cap`
   allows numbers if any COMPARE/RECOMMEND option is numeric (`enforce.py:20–43`). A value from one option can
   therefore satisfy the lexical check for a different option; the checker does not bind statements to options.

5. **Fallback is not rechecked.** `enforce.py:48–52` sends the template fallback directly. A synthetic malformed
   ANSWER decision with missing precision had `number_cap=True`; enforcement removed its bad sentence, then
   fallback emitted one numeric retention claim. This is a fail-closed robustness defect, not an assertion that
   a valid current policy decision necessarily takes that path. Missing precision must not be treated as permission.

6. **Badges have narrower semantics than full condition applicability.** `evidence_label.py:50–65` checks food/
   process and precision; it never checks condition axes or the source's human verification. Exact-row existence
   must not silently become a claim about this particular recipe context.

7. **Per-number physical basis coverage is incomplete in the demo summary.** `physics_summary` retains a
   temperature basis but does not export a corresponding explicit basis for `stated.duration_min`
   (`demo_context.py:114–117`). Scenario values have a bases map and global layer labels. The browser renders the
   duration and rounded scenario values (`index.html:139–167`). If literal per-number D-077 basis is required,
   the audit must flag/describe this gap instead of accepting global labels as proof.

8. **A query-only sample cannot cover the full app contract.** `DemoContext._transform` invokes recipe routing/
   physics only when `recipe_text` is provided. Include reproducible recipe-bearing synthetic sessions for the
   physical-layer checks, or mark that branch untested. No LLM/GPU is needed for the current public template demo.

## Suggested planted controls

- Uncited nutrient amount and a value outside the old detector's range; unknown/deprecated EVD ID; a correct ID
  with wrong value/scale; an unrelated food/process/target row; bound-as-point and wrong inequality.
- Mixed option caps with a number attached to the qualitative option; missing precision followed by fallback;
  a precision-capped direction answer gaining a number; a non-evidence citation that looks syntactically valid.
- ASSUMED_DEFAULT/SCENARIO/MODEL_DERIVED input with `evidence_supported`; NOT_POSSIBLE derived only from L2;
  UNKNOWN required input with SIMULATE; RESEARCH_ONLY AA with absent PARAM/fit or missing basis labels.
- A missing physical duration basis; a synthetic recipe-bearing call alongside query-only calls; corpus-pattern
  confidence correctly distinguished from a food-chemistry amount; public-mode restriction retained on every reply.

Each planted violation should have an independent expected finding and fail closed. Code that merely calls the
same narrow existing detector on both sides is not an independent control for detector omissions.

## Read-only verification performed

- Reviewed the paths/lines above and the T0-C06-R2 acceptance; no whole SSOT load or scientific recomputation.
- Three synthetic checker/enforcer probes confirmed detector omission, wrong-food value alignment and missing-
  precision fallback behavior. Probe outputs were flags/counts only, not recipe or paper text.
- Loaded `DemoContext.load(public=True)` locally and inspected schema/counts for three synthetic/template queries:
  a transformation query, a relationship query and a recipe-bearing transformation query. No LLM, network, SSH,
  socket server or third-party recipe input was used. All three returned expected branch envelopes; the recipe-
  bearing call exposed physical fields including duration without a separate duration-basis field.
- No claim is made here about the yet-to-be-run full 346-answer/1,000-session audit or scientific gate completion.
