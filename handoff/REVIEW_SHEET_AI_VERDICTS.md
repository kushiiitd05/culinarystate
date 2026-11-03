# Review sheet — AI verdicts pending Kush/Parv review

Status: **AI_VERDICT_PENDING_HUMAN_REVIEW**. Nothing below is approved, signed or
recorded as a decision until Kush and Parv each reply with "ok", or with feedback,
per item or per block. Their reply is then entered into DECISIONS.md as their
decision; the coordinator acts as scribe only. This file is append-only: new
sessions add new blocks and never rewrite earlier ones.

Reply format, one line per person: `Kush: ok all` or `Parv: ok A1-A7, B2 change: ...`

Facts only a human can supply, which no verdict can cover:
- **N1 nonce (Kush):** a pilot nonce string of your own choosing.
- **N2 capacity (both):** weekly hours for Kush and for Parv.
- **N3 budget (both):** per-annotator budget B_h in hours for Kush and for Parv. The design caps the pilot at 40 h each.

## Block W — workflow (D-045 when accepted)

| ID | AI-drafted statement for your decision |
|---|---|
| W1 | Every gate and label follows the same order: an AI agent gives a verdict first, then Kush and Parv review it, and their review is final. AI verdicts are always labelled as AI. |
| W2 | Pilot and later annotations are first-pass AI labels reviewed by both humans. They are recorded as `MODEL_ASSISTED`, with the AI pass and the human edits kept separately. Agreement and timing results are reported as "human review of AI drafts", not as blind independent annotation. |
| W3 | The professor's permission for this workflow is recorded as stated by Kush; reference the written permission if there is one. |

## Block A — S154 engineering choices (`reports/step16/S154_build_note.md`)

| ID | Choice as drafted |
|---|---|
| A1 | P1 draw byte encoding:<br>- plain concatenation of frame_sha256 hex, wave and nonce;<br>- frame_sha256 taken over the frame CSV hash and the strata CSV hash;<br>- the stable shuffle is a SHA-256 rank;<br>- reserves also consume groups. |
| A2 | A P1 cell with fewer than 30 eligible recipes stops the draw instead of falling through to another source; a human chooses the reallocation. |
| A3 | The pilot start record needs both Kush and Parv as signers; the single-signer override is not accepted. |
| A4 | History variables:<br>- externally measured history (EXTERNAL_VERIFIED) stays not accepted, pending a separate ruling;<br>- only the origin/route pairs MODEL_ESTIMATED/MODEL and SIMULATED/SIMULATED are accepted. |
| A5 | POR selection:<br>- exact facet equality, where a null facet matches only another null;<br>- HUMAN_VERIFIED records only;<br>- the basis-to-Q-level map is supplied by the caller;<br>- CONVENTION is left unmapped. |
| A6 | A dual-expression conflict is an exact inequality of the two Q0 masses, with no tolerance threshold. |
| A7 | The dry-run uses the legacy source-family locale map (BBC = UK, Food.com = US). |

## Block B — Step 19 start-record choices

| ID | Choice as drafted |
|---|---|
| B1 | Instrument: `CURRENT_V0_PLUS_HANDBOOK_V1_ADDENDUM_A`, the recommended one. |
| B2 | Pilot column: `reserve_split_v2`, Parv's choice, with Kush's confirmation. |
| B3 | The AI methods and readiness recommendations PM-01..12 and PR01..10 are accepted as the method ruling, with W2 labelling. |
| B4 | Draw specification: `STEP19_P1_DRAW_SHA256_RANK_V1_DRAFT`. |
| B5 | THR-19P-01..35 signed as written in the design, Appendix A. |
| B6 | H5: authorise wave P1 once N1–N3 are supplied. |

## Block C — S155 Step 17a open items (worker ksh; details in the S155 build note)

| ID | Choice as drafted |
|---|---|
| C1 | Validator numbering follows the plan (V1 span, V2 schema, V3 vocabulary, V4 invariants), not SSOT §240.1. SSOT's arithmetic check (its V3) is covered by the rc2 validator plus the auditor. |
| C2 | Six stage functions and four failure codes, as in plan 17-M. The extra RD stages and codes are not built; RD code names are kept as reason strings. |
| C3 | Draft mappings:<br>- `ALLOWED_FAILURES`, the failure codes each stage may return;<br>- `GROUNDING_FAILURE_MAP`: grounding counts as failed unless a mass is grounded;<br>- `ROUTE_TO_ORIGIN`;<br>- an empty mention set is not a failure. |
| C4 | Offsets are Python code-point indices; `join_policy` is a literal separator string. |
| C5 | Vocabulary checks:<br>- V3 checks only the mention-label set the caller supplies;<br>- an annotation_mode outside the registry reports UNKNOWN. |
| C6 | V4 rules:<br>- order basis: text order by default, settable;<br>- only INTERMEDIATE counts as a new intermediate;<br>- split fractions are summed per parent, event and basis;<br>- disagreeing producer references give UNKNOWN;<br>- mass balance is exact, with no tolerance. |
| C7 | Auditor:<br>- registered rules only;<br>- the literal unit must appear in its span;<br>- grams and mL only through rc2 records;<br>- link scores are excluded as model diagnostics. |

## Block D — S155 Step 17b and the 17a cross-review (worker prv)

Added when prv finishes.
