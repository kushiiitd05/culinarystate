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

### Block D content (added 2026-11-03 after prv finished; pending Parv review)

Source: `reports/step17/S155_17a_ai_review.md` (sent to Kush for Parv).

| ID | AI verdict |
|---|---|
| D1 | Accept the fixes R1–R7 to ksh's 17a, each with a failing test committed first:<br>- R1, R2: auditor unit/number pairing and minus sign;<br>- R3: `config_hash` coverage;<br>- R4: cross-output id references;<br>- R5: V3 categorical and identifier claims;<br>- R6: `Span.of` offset types;<br>- R7: malformed V4 order. |
| D2 | Decide the open items O1–O9:<br>- O1: PASS when nothing was checked;<br>- O2: a unitless temperature or duration is accepted;<br>- O3: discard after discard is not flagged;<br>- O4: split fractions are summed per event;<br>- O5: a failed grounding can still carry a count or volume;<br>- O6: registry categoricals are checked only by V3;<br>- O7: H4 draft tables and validator numbering;<br>- O8: mutable `params`;<br>- O9: unused imports. |
| D3 | Rung A draft choices:<br>- first instruction mentions are typed as ingredient lots;<br>- "into a/an X" is the product, "into the X" the destination;<br>- an unresolved mixture word opens a new mixture;<br>- the cue, adverb and auxiliary lists;<br>- "20 C" is flagged as ambiguous, not read as a temperature;<br>- the `t`/`c` unit tokens are excluded. |
| D4 | Lexicon gaps seen in the hard cases ("liquid", "use", "hold") stay as gaps; no entries are invented. |

## Responses recorded

- 2026-11-03, Kush: "the pendings you have are okked by parv and me - kush". Blocks W, A, B1–B5 and C1–C7 accepted; recorded as D-045 and D-046. B6 waits for N1–N3.
- 2026-11-03, Kush relaying Parv: "parv said pass for the above file you gave me". Recorded as Parv's pass on the S154 bundle and branch (D-046).
- Block D: pending.
- 2026-11-03, Kush: "all given files seen and reviewed by parv ok and mine are also okay and passed". Block D (D1–D4) accepted and S155 passed; recorded as D-047. N1–N3 still needed.
- 2026-11-03, Kush: N2 weekly capacity Kush 15 h, Parv 15 h ("we can spend 15-20 hrs per week"; 15 used as the planning figure); N3 budget B_h Kush 40 h, Parv 40 h. N1 nonce not yet supplied (Kush asked what it is; explained).
- 2026-11-03, Parv: N1 string "BlindedByTheRecipes_05"; Kush: "Houdini_loves_hustin_crepes_07". Joint nonce recorded; B6/H5 recorded as D-048; signed start record written; gate check ready=true, 0 blockers.

## Block E — S156 Step 18 and 26g (pending review)

Source: `reports/step18/S156_build_note.md`, `S156_engine_audit.md`, `S156_18_ai_review.md`.

| ID | AI verdict |
|---|---|
| E1 | Accept the fixes R1–R6 to ksh's Step 18 code. |
| E2 | Decide the open items O1–O7. O2 matters most: replay PASS should account for issues the adapter reported. |
| E3 | Engine policies left open:<br>- merge/transform mass;<br>- who assigns the split/reserve basis;<br>- how to read a REMAINDER with no fraction;<br>- count-unit identity;<br>- whether a rejected event cascades;<br>- text order vs execution order. |
| E4 | 26g, all PROPOSED_PENDING_26b:<br>- the required-input lists for sim_aa_1 and sim_chl_1;<br>- the units;<br>- the name MEASURED;<br>- whether SYNTHETIC inputs are allowed;<br>- a replay issue blocks every event;<br>- the census reason codes. |

Responses:
- 2026-11-03, Kush: the old-engine defects L1–L8 are not influential and are left unchanged; work continues on the new replay.

## Block F — S157 evidence machinery (pending review)

Source: `reports/step09/S157_build_note.md`, `S157_09_audit.md`, `S157_ai_review.md`.

| ID | Decision needed |
|---|---|
| F1 | **Re-baseline SRC/SNAP.** Appending the proposed 12.0 rows changes the byte-identical protected ledgers. Approve a re-baseline after reviewing `registry/staging/step12_0_src_snap_proposed_v1.jsonl` from a local run, or keep them proposed only. |
| F2 | **Licences (H2).** INFOODS (#9) stays LOCAL_ONLY. Re-check the Bognar licence before its 11 tables are ingested. Should catalog-reported CC0/PD count as ASSUMED or stay UNKNOWN? |
| F3 | **E4 under D-045.** E4 needs a blind second review, and AI-draft-then-human-review is not blind, so as built no item can reach E4. Keep that, or name which review counts as blind. |
| F4 | **Old tools that let code fill human fields.** `apply_link_review.py --sign-as` fills a human decision field; `apply_human_review.py` writes to EVD. Restrict, retire or keep them. |
| F5 | **Review-file authenticity (O-1).** How does a review CSV prove it came from Kush or Parv? (Signed commit, separate account, or attestation.) |
| F6 | **Bognar values above 1.00.** MEASURED in the new parser, CENSORED in the old v1. Choose one at the G12 audit. Also decide the method-label rule (O-4) and the R2 "nearest 5%" censoring rule. |
| F7 | Accept the R1–R4 fixes and the ksh audit open items O-1 to O-6: field classes, unit list and prompt-injection patterns as AI proposals; whether the T/t validators call the frozen Step 07 normaliser. |
- 2026-11-03, Kush: "block F all ok by parv and me, keep going". Recorded as D-049 with the as-built conservative default for each option item (F1 re-baseline approved in principle, executed only after a real local run is reviewed).

## Block G — S158 kinetic contract, mechanism schema, 22a and 23a (pending review)

Source: `reports/step21/S158_build_note.md`, `S158_ai_review.md`, `S158_expert_questions.md`, `reports/step23/applicability_engine_23a_DRAFT.md`.

| ID | Decision needed |
|---|---|
| G1 | H4 for 04.3 KIN/KINPT v1.1 as a whole. Step 09 must not freeze KIN/KINPT before it. |
| G2 | Kinetic readings:<br>- THR-04K-01..04 are still unsigned;<br>- does a same-reader repeat count as an independent read? (currently UNKNOWN);<br>- does a missing inter-read SD give UNKNOWN or NOT_ELIGIBLE?;<br>- R1's choice of UNKNOWN vs NOT_ELIGIBLE for unverified series;<br>- review open items O-1 to O-3. |
| G3 | MECH v1.1:<br>- `target_class` as a schema field departs from ontology §3.2;<br>- the class mismatch for STRUCTURE_ALTERED, DENATURED, AGGREGATED and GELATINIZED;<br>- where the analyte-form token registry lives and who approves it;<br>- the EQ21 id collision check. |
| G4 | Chemistry expert: answer EQ21-01..14. Kush and Parv then close each answer with a decision. |
| G5 | 22a:<br>- seal the shared 22c case set before any rule is coded (the helper exists);<br>- author real signature rules;<br>- approve a modifier vocabulary. |
| G6 | 23a:<br>- the 8 AI readings in §4 of the 23a note;<br>- the 45 AI-draft reason codes;<br>- whether ASK and RESEARCH_ONLY belong in the route enum;<br>- pre-register the G22/G23 thresholds. |
| G7 | Accept the R1–R6 fixes. |
- 2026-11-03, Kush: "block G and scipy ok by parv and me". Recorded as D-050. G4 (expert answers) and G5 sealing (no case set yet) stay open; scipy declared as optional extra step26.

## Block H — S159 simulator core (pending review)

Source: `reports/step26/S159_build_note.md`, `S159_ai_review.md`.

| ID | Decision needed |
|---|---|
| H1 | **26.0 system selection:** AA (leading) or chlorophyll (fallback). Write and sign the selection record (template provided) and the pre-registration, including an exact definition of the "no-water-assay" design (O6). This is a Kush+Parv / 11.D decision. |
| H2 | 24a:<br>- FORM- vs MODEL- prefix;<br>- H4 approval of the FORM/PARAM/VAL v1 drafts;<br>- AI proposals: the `FITRUN-` namespace, `lifecycle_status`, "MEASURED" meaning a point value, `PENDING_15B`, the slot roles, the VAL verdicts and the draft calibration rules;<br>- the Weibull parameterisation (α scale, β shape). |
| H3 | sim_aa_1 model questions (H4 or expert):<br>- the K_p dimension (m³/kg because r is in mL/g);<br>- k_L does not depend on temperature;<br>- k_dw is first order. |
| H4 | sim_chl_1:<br>- the functional form of g(pH);<br>- whether one g is shared by Chl a and Chl b. |
| H5 | Inputs only humans or sources can give:<br>- Choi–Okos coefficients, plus a check of the mixing rules (AI recollection);<br>- τ_h per size class;<br>- the M&S limits (26e);<br>- solver tolerances and G26-VER numbers;<br>- a check of the KiSAO ids (AI-recalled, UNVERIFIED). |
| H6 | Accept the fixes R1–R5 and decide O1–O5 and O7. |
