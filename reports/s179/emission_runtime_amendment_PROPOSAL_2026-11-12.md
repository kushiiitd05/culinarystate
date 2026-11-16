# Runtime emission hardening — dated proposal, 12 November 2026

**AI_DRAFTED / PROPOSED_NOT_IMPLEMENTED / NON_CITABLE / NO_HUMAN_SIGNOFF_D085.**
The current audit does not modify production generation, frozen prompts, scoring or benchmark outputs.
This is a concrete implementation specification for the next engineering batch, not a gate approval.

Evidence: `emission_path_review_2026-11-11.md`, `emission_audit_2026-11-12.md` and the retained v1/v2 audit JSONs.
The 30 saved-answer flags are not a new H3 score. The absence of demo flags is limited to the disclosed scan.

## Versioned implementation requirements

1. Create a separately versioned generation policy/output path before evaluation. Preserve the current
   template, enforcement behavior and frozen results for reproducibility. Bind new source, prompts, reference
   files, mode/precision schema and any evaluation amendment in a new freeze before a scientific rerun.
2. Missing mode, precision, packet or required basis must fail closed with an explicit reason. An old template
   fallback cannot bypass the final numeric cap; check the actual final rendered text after any fallback.
3. Bind each scientific claim to an option, target and declared source context. Unioning all option packets
   must not let one option borrow another option's numeric evidence. Unknown condition applicability stays unknown.
4. Preserve raw quantity/unit and bound meaning. A censored limit does not become an observed point, a percentage
   is not an absolute nutrient amount, and matching a number to some EVD row is not source entailment.
5. Carry a basis for each emitted structured number. Distinguish a recorded food descriptor, source/count
   metadata, TEXT_STATED input, corpus pattern, EVD result and SCENARIO/MODEL_DERIVED estimate. Scenario values
   must not become `evidence_supported`; UNKNOWN must not route to SIMULATE; L2 cannot establish NOT_POSSIBLE.
6. Keep MODEL_DERIVED scientific estimates behind their PARAM/fit/VAL/provenance rules. Retain the existing
   NOT_VALIDATED/RESEARCH_ONLY refusal boundary. No AI flag becomes HUMAN_VERIFIED to make a guard pass.

## Required regression controls

- Missing precision → enforcement removes a number → fallback attempts a number: final output must refuse it.
- A valid figure for option A attached to qualitative option B: reject or retain UNKNOWN with reason.
- Correct value but wrong food/process/target; unknown conditions; incorrect censor direction: do not certify.
- Uncited integer, signed/scientific notation, percentage, absolute nutrient amount and temperature/duration:
  classify each and require its own admissible source/basis rather than using a retention-only detector.
- Whole source names containing digits remain metadata; an actual wrong retention figure beside them still fails.
- Every app JSON field and visible browser number retains the same basis/cap; include relationship and recipe
  branches, local/public modes and failures. Use synthetic controls before implementation and preserve raw text.

Report a separate new engineering run beside the existing audit. Reusing already inspected D5 questions is
post-hoc and non-citable. No tightening or bug fix may retroactively convert D-092 into a successful hypothesis
test, supply independent labels or erase a prior failed gate.
