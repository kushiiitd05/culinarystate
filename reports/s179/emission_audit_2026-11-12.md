# Answer emission audit — 12 November 2026

**ENGINEERING_DIAGNOSTIC / NON_CITABLE / NO_HUMAN_SIGNOFF_D085.**

T0-C06-R2 remains **PARTIAL**. This is a separate post-hoc lexical/structural engineering scan; it does not
rescore H1/H3, establish semantic entailment, or change a scientific gate or any frozen answer.

## Scope and provenance

- Instrument revision/base: `84929a73808d155b4539a22fbfd1210e0a80115a`; source hashes and exact run times are in the JSON.
- Saved D5 answers: all 346, including unconstrained baselines and S blocks; no answer excluded to obtain zero.
- Public-mode demo: 1000 deterministic metadata-template calls, seed 20261112, sampled ACTIVE EVD rows with replacement.
- 200 calls include a clearly synthetic caller recipe; this supplies no real recipe or scientific measurement.
- No LLM, GPU, SSH, private recipe text, frozen benchmark edits, output replacement or production change.
- The base commit identifies other tracked runtime assets; explicit input hashes cover EVD and saved runs.
  This does not supply an independent snapshot of every possible private/environment-dependent runtime input.

## Saved-answer findings

| Rung | Answers | Records flagged | Numeric reference/cap findings | Review gaps |
|---|---:|---:|---|---|
| B0 | 74 | 4 | UNCITED_CHEMISTRY_NUMBER=7 | PACKET_PROVENANCE_UNRECORDED=7; UNCLASSIFIED_NUMERIC_TOKEN=2; UNIT_BEARING_QUANTITY_NOT_CHECKED=4 |
| B1 | 24 | 0 | none detected | none detected |
| B2 | 74 | 8 | UNCITED_CHEMISTRY_NUMBER=8; VALUE_NOT_IN_CITED_POINT_EVIDENCE=7 | PACKET_PROVENANCE_UNRECORDED=55; UNCLASSIFIED_NUMERIC_TOKEN=5; UNIT_BEARING_QUANTITY_NOT_CHECKED=2 |
| B4 | 24 | 0 | none detected | none detected |
| B5 | 50 | 18 | NUMERIC_CLAIM_EXCEEDS_PRECISION_CAP=16; UNCITED_CHEMISTRY_NUMBER=9; VALUE_NOT_IN_CITED_POINT_EVIDENCE=12 | UNIT_BEARING_QUANTITY_NOT_CHECKED=3 |
| B5T | 50 | 0 | none detected | none detected |
| B7 | 50 | 0 | none detected | none detected |

Thirty answers have at least one reference or precision-cap flag. Across all answers there are 24 uncited
chemistry-number tokens, 19 values not matched to cited ACTIVE MEASURED point evidence, and 16 precision-cap
flags. These token counts overlap and are not thirty independent scientific errors. 43 records have at least
one explicit review gap; 62 chemistry tokens lack recorded packet provenance. No semantic error rate is inferred.

B5T and B7 have no flags under this instrument. This is not a new H3 result, general correctness claim or
condition-applicability check. Zero detected tokens in the S arms is not evidence of correct state predictions.

## Demo findings and coverage

All 1000 calls have no detected lexical/structural issue after the instrument correction below. 147 retention
numbers align lexically with cited measured points. This does not mean those values apply to the queried food
or conditions. Full source entailment and per-number physical-basis checks remain incomplete.

| Branch | Calls |
|---|---:|
| SAFETY | 197 |
| TRANSFORMATION | 173 |
| UNKNOWN | 630 |

Modes: 126 ANSWER, 25 ABSTAIN, 197 ABSTAIN_SAFETY and 652 ASK. There are 926 distinct query hashes.
Of 200 synthetic recipe requests, 36 reached a recipe response; 51 physical steps were serialized. This is
limited branch coverage, not 1000 successful transformation answers or a sample of natural user queries.
Relationship, local-only carbon/time, full real-recipe behavior, rendered browser text and all simulation
provenance paths are not certified by this sample.

## Instrument correction and retained original run

The first run, `emission_audit_2026-11-12.json`, flagged 33 demo records because the broad detector treated
digits in recorded names (e.g. a vitamin identifier or a fat percentage in a food descriptor) as retention
claims. Three regression cases reproduced that error. The corrected detector masks whole, exact recorded
metadata names, never arbitrary numeric substrings; it still catches an incorrect retention number beside
such a name. The source-name correction was committed before the separate v2 run. The original artifact is
retained with its original source hashes; none of the production answers was changed to make flags disappear.

The saved D5 aggregate findings are unchanged by this correction. Every unit-bearing or unclassified number
outside the checked retention grammar remains an explicit gap. Censored limits cannot satisfy a point-value
claim; numeric alignment uses half a two-decimal rounding unit as a disclosed engineering setting.

## Controls and remaining requirements

Twenty-one synthetic tests cover uncited large/signed/scientific/percentage numbers, incorrect values,
out-of-packet citations, citation-only fragments, metadata counts, precision caps, censored limits,
UNKNOWN-to-SIMULATE, model/scenario-to-evidence labels, L2-based impossibility, deterministic sampling and
the recorded-name correction. Text and recipe/source excerpts are absent from the audit output.

The emit-path inventory and independent source observations are in `emission_path_review_2026-11-11.md`.
That agent supplied a draft and findings before its final turn hit a service usage limit. Root completed
the instrument and checks; no completed independent review of the new auditor is claimed.

Acceptance still needs: source-context/option-specific entailment, full quantity/unit and model/PARAM basis
checks, literal per-number physical basis coverage, all emit paths and rendered app checks, and disposition
of raw-baseline flags. Existing claim checking has detector, option-pooling and unchecked-fallback limits;
fixes must be dated/versioned, preserve frozen results and never silently redefine the old score.

Machine evidence: `emission_audit_2026-11-12_v2.json`; original run: `emission_audit_2026-11-12.json`.
Both preserve original D5 hashes. Original H1/H3 RULE_NOT_MET and all prior failed gates remain unchanged.
