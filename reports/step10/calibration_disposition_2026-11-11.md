# AA calibration and held-out disposition — 11 November 2026

**AI_DRAFTED / AI_PRECHECKED / DIAGNOSTIC / NON_CITABLE / NO_HUMAN_SIGNOFF_D085.**
The frozen Model A remains **NOT_VALIDATED / RESEARCH_ONLY**. This is a disposition report, not a calibration
success or a gate approval. It records what the restored private sources allow and what they do not.

## Restored evidence and completed analysis

Fifteen transferred files matched the supplied SHA-256 manifest and were copied to their expected git-ignored
paths. Originals were retained. The D-085 CAL sheet exactly matches the hash bound by the frozen Model A.
Files named for human reviewers do not constitute evidence that a human performed a new review.

The CAL source precheck and separate-paper Model B diagnostic are complete. See
`aa_model_b_sensitivities_2026-11-11.md` and its JSON for exact estimates, source/producer hashes and assumptions.
All admissible-temperature and explicitly-water-contact exclusion arms retain the original included rows;
they do not count as additional robustness results. Removing the predeclared non-AA-specific assay leaves
one paper and yields NEED_DATA under the unchanged two-paper Model A rule. Licence-rejected papers remain out.

The primary pools HPLC reduced-AA and iodine-titration data. That assay-basis limitation remains visible.
No source pH dispersion is converted to a gate interval, no medium is inferred from a missing description,
and no missing kinetics or independent laboratory group is invented.

## Held-out extraction and refusal outcome

A separate agent context received only the frozen fit hash before completing extraction. It did not read fit
estimates or CAL material. A second source-precheck context also remained unexposed to the estimates.
This is process/context separation, not independent human verification or inter-rater agreement.

The finalized extraction has 19 rows: 3 per-temperature rate constants, 8 author activation-energy aggregates,
7 pre-exponential aggregates and 1 licence exclusion. There are no exact raw time/retention observations.
AAK-12's publisher licence could not be confirmed (HTTP 403), so its PDF text remains unopened. AAK-05 was not supplied.
Author aggregates never become raw kinetics or per-temperature rates.

Source precheck: **6 PASS, 12 FLAG, 1 REJECT; computationally eligible rows = 0**.
PASS concerns source fidelity only. The three rate rows retain unresolved assay-basis flags; the printed numbers
and units matching the source does not remove those flags. The finalized extraction is not edited after review.

The guarded diagnostic runs after extraction and source precheck. Latest output:
`aa_SIMVAL_diagnostic_2026-11-11_v2.json`. It verifies extraction/fit hashes, the final-extraction manifest and
the precheck's row IDs, candidate IDs, row kinds, PDF hashes and source locators. FLAG, REJECT or absent
computational permission excludes a row before prediction. Per-row output paths must be git-ignored.

**Actual outcome: no predictions emitted; primary comparison NOT_RUN_BASIS_REVIEW_REQUIRED.**
Rate-error means are null, retention error is null, and no coverage percentage is calculated from zero eligible
observations. No retention error could be computed from author aggregate parameters in place of observed points.
The earlier build output `aa_SIMVAL_diagnostic_2026-11-11.json` is retained; v2 strengthens source binding and
uses a new output path. Neither output contains per-row source kinetics or grants validation/routing permission.

## PARAM and production calibration

T5-C07-R3 and T5-C11-R3 remain incomplete. No PARAM, KIN, SEXP or lineage ID is fabricated from a source filename.
The restored CSV extraction is not a complete source-linked KIN/PARAM ledger. The frozen PARAM schema admits
AI_PRECHECKED as a record status, but its calibration eligibility rule still requires HUMAN_VERIFIED.
Schema validity and production eligibility are separate checks.

The current router loader does not recognize the D-085 fit filename. Adding a file alias alone would still
fail its separate-human-return, FORM, PARAM, held-out VAL and domain requirements. The descriptive pilot cannot
define IN_VALIDATION_DOMAIN under the unchanged applicability rules. No guard is loosened or bypassed here.
Full reasons and source paths appear in `G15_T5_scorecard_2026-11-11.md`.

The accompanying draft SIMM-AA-1 card records NOT_VALIDATED, empty PARAM/VAL references and route refusal.
It is metadata about the research pilot, not a minted scientific model record or an operational simulator card.

## Remaining work

- Resolve source/assay eligibility with source-supported evidence, or retain the held-out comparison as NOT_RUN.
  A new admissible row set requires a new versioned review/output; no retroactive tuning of Model A.
- Acquire the blocked sources through the authorized human browser route and confirm licences before use.
- Complete real source-linked KIN/PARAM provenance without changing verification labels or reusing IDs.
- Preserve the failed and unmet gates. A later integration amendment must be explicit, dated and compatible with
  the existing no-loosening rule; it cannot manufacture independent labels, human verification or validation.

No updated statistical threshold, model fit, domain whitelist, production SIMULATE output or scientific pass
is supplied by this work. Original Model A, frozen code, preregistration and D5 results remain unchanged.
