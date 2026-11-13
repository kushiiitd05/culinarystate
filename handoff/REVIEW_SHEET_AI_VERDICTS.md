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
- 2026-11-03, Kush: "block H ok by parv and me, AA selected". Recorded as D-052; signed selection record sim_aa_1 (direct selection before 11.D). Open: no-water-assay design definition, 26.0 pre-registration numbers, H5 inputs, FORM-/MODEL- prefix.

## Block I — S160, checkpoint H-A (pending review)

Source: `reports/step15/S160_build_note.md`, `pre_freeze_rulings_DRAFT.md`, `S160_ai_review.md`, `reports/step35/35_0_v2_signature_sheet.md`.

| ID | Decision or value needed |
|---|---|
| I1 | **15.0 rulings:**<br>- accept or replace the AI recommendations C2-a, H-3, X-1, G-1 and K-1;<br>- **supply the RESERVED fraction**;<br>- choose the unit (STUDY_THEN_CELL recommended) and the stratification (SOURCE_FAMILY recommended);<br>- say how the seed is generated: hard to guess, and only its sha256 published (O1).<br><br>The 15.0 entry must use the marker lines the seal expects (see the seal module). |
| I2 | **15a.R:** decide whether and when to run the seal, and where the seed file and the sealed list live (outside git). Re-sealing (O2) and pandas availability on the server (I2) are open. |
| I3 | **Step 35 v2 signature:**<br>- protocol `009c9047…`, record `8885a63a…`;<br>- answer P-1 to P-5 (D-041 amendments; P-5 also covers the unbound Food.com parquet and `pyproject.toml`, O4);<br>- conditions written into the rows "before signature": S-1, a chemistry reviewer for the taste map; S-2, a human finding on the 204 deprecated edges. Complete them, or record a deviation;<br>- choose Route A (sign the committed record: only 35a and 35e run) or Route B (regenerate on the Mac: all tasks);<br>- Q-1 to Q-4 on the signature sheet. |
| I4 | **Scaffold values only humans can set:**<br>- the Step 30 margin δ_30;<br>- ρ and c_floor for 34a, and the 34a.0 circularity check;<br>- the 34c thresholds and actions, and Kush's signature;<br>- the formats for the 15a freeze record and the 29-diag pre-registration. |
| I5 | Accept the fixes R1–R4 and decide O3 and O5. O5 is that signatures stop accidental or agent signing, not forgery: only the signer's own session commits a SIGNED file. |

## Block J — S163 cross-review: full-corpus Rung A, auditor fixes, Parv's local runs (pending review)

Source: `reports/review/S163_ai_review.md` (AI reviewers ksh and prv, read-only, cross-review). Reply per item, or `ok all`.

| ID | AI verdict | Human decision needed |
|---|---|---|
| J1 | Accept the S163 auditor fixes in `_unit_token_in` (prv P1: tests fail before each fix; risky direction probed). Regression refusals added. | ok / change. Also: is `350 degreef` (lowercase unit after a case-insensitive prefix) acceptable as a literal °F? |
| J2 | Accept the full-corpus results 626 → 4 → 0 (prv P2: the three JSONs differ only in auditor counts; every document number matches). 3.2b now states per-file provenance and evidence scope. | ok / change. Follow-up: the tool should record the code commit or auditor hash in its JSON. |
| J3 | Accept the PR #5 merge (prv P3: Parv's pre-fix file is byte-identical to `_prefix_S161`). STATUS wording corrected: 1/5 was agent-drafted, not Parv-stated. | Parv: confirm the 1/5 was not his own value, or state it is. |
| J4 | V2 `INVERTED_INTERVAL` 4,511: AI census by family and shape mask (counts only), then a human-read stratified sample: the 5 in the 1,000 sample, all A1 and Wikibooks cases, about 30 Food.com and 30 Gutenberg. Then decide whether an inverted quantity becomes UNKNOWN. | ok to run the census? Who reads the sample? |
| J5 | 15.0 draft parses in the seal and 1/5 is defensible (ksh K1). Recommended changes: Kush-generated or two-part joint seed; seal on Kush's Mac; record the pre-seal bake-off exposure; a seed reveal-or-escrow rule at 15b; D-054 from Kush's own session. | **Kush:** fraction (1/5, 1/4, …); seed source (own / joint two-part / Parv's existing); where the seal runs. |
| J6 | **Accept Parv's P1 draw as C2** (ksh K2: independent re-draw identical; gate 0 blockers; D-048 authorised). | Kush + Parv: ratify. |
| J7 | Packet "sealed" key can be rebuilt from public data (ksh K3). Recommended: a secret per-annotator salt committed by hash (or say the key is public); a git-ignore check; a one-letter-per-machine guard; build the commit/snapshot step (PV-10) before annotation; then build A on Kush's Mac. | Fix the salt now (B's packets re-issued) or accept a public key? OK to build the snapshot step? When may P1 annotation start? |
| J8 | Step 26g/30/34a records: labels honest. The Step 30 bake-off is a pre-seal exposure and is not citable (STATUS updated). The 26g census is stale (pre-fix Rung A). | Record the bake-off as a deviation in D-054? Rerun 26g on the fixed Rung A? |

Still open from block I and not covered here: δ_30, ρ, c_floor, the 34a.0 circularity check, the 34c values; Step 35 P-1..P-5, S-1, S-2 and the signature.
- 2026-11-05, Kush (for Kush and Parv): "both me and parv are okay with the verdicts of prv and ksh passed keep continuing". Block J (J1–J8) accepted as the AI verdicts state. Consequences:
  - J5 needs a seed generated by Kush, so D-054 waits for Kush's seed hash.
  - J7: packet salt, guards and commit step built in S165; B's unsalted packet list superseded, to be re-issued by Parv with his own salt.
  - J4: census run in S165.
  - J8: 26g rerun deferred, because no committed tool exists.

## Block K — S166 cross-review: PR #8 leak fix, Step 17b provenance, Step 26g census tool (prv items passed; ksh items pending)

Source: `reports/review/S166_ai_review.md`. prv items K1–K3 below were passed by Kush and Parv on 2026-11-06 (D-054). Reply to K4–K10 per item, or `ok all`.

| ID | AI verdict | Human decision needed |
|---|---|---|
| K1 | prv P1–P7: PR #8 leaked the packet→recipe map through plain hashes; fixed with salted commitments, salt checks, required issued list, re-issue note. | **Passed (D-054).** J7 re-confirmed on the fixed design. |
| K2 | Merge PR #8 (now including the fix). | **Passed (D-054).** |
| K3 | Nobody builds or re-issues packets from the superseded unsalted list; Parv re-issues B and Kush builds A only with the fixed maker. | **Passed (D-054).** |
| K4 | ksh K1/K3/K6: accept the committed 26g census tool; close J8 (census block identical to Parv's; only invented 2 → 0). | ok / change |
| K5 | ksh K2: the 2 → 0 is the S161 `º` rule, not the S163 fixes (wording corrected). | ok |
| K6 | ksh K4/K7: add stage-order, locale and sample tests; write `bindings_supplied` and `prohibited_by_construction` into the census JSON (AI remit). | ok |
| K7 | ksh K5: rerun the 1,000 census from a clean commit before citing it; mark Parv's file "superseded by S166". | ok / keep both |
| K8 | Full-corpus 26g census (612,782 recipes, seed 20261104) is running on vinayak-server, counts only. Commit its JSON when done. | ok |
| K9 | prv P8: recompute provenance after long runs; keep `.DS_Store`/`._*` out of the tree hash (AI remit). | ok |
| K10 | J4 sample (from block J): the stratified inverted-interval sample needs recipe-text excerpts in a git-ignored file. Who reads it (Kush, Parv, both)? Build the extraction on vinayak-server? | person(s) + ok |

## Block L — Annotator A's P1 packet build (pending review)

Source: `reports/review/S166_ai_review.md` (last section). Reply per item, or `ok all`.

| ID | AI verdict | Human decision needed |
|---|---|---|
| L1 | Accept A's build: all commitments verify (ksh) and nothing links a packet to a recipe from public data (prv). Kush may start annotating. | ok |
| L2 | Guard `main()` in the packet maker (AI remit, test-first). | ok |
| L3 | B's old unsalted list in `superseded_s164_unsalted/` still links B's old packets to recipes. Since B is re-issued with a new salt and order, keep it as a record, or delete it? | Parv: keep / delete |
| L4 | Before Kush's first commit step: where the question log and representability files live (non-empty, private), and the handbook version string (`v1+AddendumA`?). | Kush |
| L5 | `tests/unit/.probe` (empty, untracked, 2026-10-27): delete? | Kush |

### Block L — AI verdicts on L2–L5 and K10 (ksh and prv, read-only, 2026-11-06)

At Kush's request the AI reviewers answered the open items first; Kush and Parv review these verdicts (D-045). Reply per item, or `ok all`.

| ID | ksh (Kush side) | prv (Parv side) | Human decision needed |
|---|---|---|---|
| L2 | ACCEPT: test fails on the pre-fix maker (argparse exit on import), passes on `5580b93`; CLI unchanged. | ACCEPT: same, independent temp-tree check. | ok |
| L3 | — | KEEP `superseded_s164_unsalted/` with a README "superseded; never use to build or re-issue". The old mapping reveals only which 7 recipes B annotates (public in the manifest), nothing about the new salted order; deleting cannot remove it from git history; it is J7/D-054 evidence. | Parv: keep / delete |
| L4a | Question log and representability file in `~/.culinarystate_private/` on Kush's Mac, never in the repo; only their sha256 enters `commitments_A_P1.json`. | — | Kush ok |
| L4b | Formats from design Appendix C. Question log CSV: `entry_id,packet_id,utc_time,question,minutes_spent,answered_after_commitments`. Representability CSV: `packet_id,annotator_letter,wave,hardcase_class,rating,sp_id_if_logged,note` (rating FAITHFUL/WORKAROUND/IMPOSSIBLE; filled after labelling). No recipe text. If no questions: one line "no questions in P1". | — | Kush ok |
| L4c | `--handbook-version "v1+AddendumA"` (design 5.6; handbook v1 "Addendum A (S101)"; not v2 DRAFT, not Addendum B). | — | Kush ok |
| L5 | DELETE `tests/unit/.probe` (empty, untracked, unreferenced). | — | Kush ok |
| K10 | Both read independently, Parv first; drop the 14 P1 primary recipes (A and B) from the sample; extract on vinayak-server (VPN first), excerpts git-ignored. | Parv reads; drop any P1 recipe; extract on the server, git-ignored. | Kush + Parv: who reads |

B re-issue on Parv's Mac (prv, checked against the tool's refusals):
1. `mkdir -p ~/.culinarystate_private && chmod 700 ~/.culinarystate_private && (umask 077; /opt/anaconda3/bin/python -c "import secrets;print(secrets.token_hex(32))" > ~/.culinarystate_private/p1_salt_B.txt) && chmod 600 ~/.culinarystate_private/p1_salt_B.txt` (never print the file).
2. If B was built before: `mkdir -p ~/.culinarystate_private/superseded && mv annotation/gold/deep_gold_pilot_v1/B annotation/gold/deep_gold_pilot_v1/sealed_key_P1_B.json ~/.culinarystate_private/superseded/`.
3. `/opt/anaconda3/bin/python tools/step19_packet_maker.py --letter B --salt-file ~/.culinarystate_private/p1_salt_B.txt` (prints `"blank": true`).
4. Commit only `registry/recipe_semantics/deep_gold_pilot_v1/{packets_P1_B.csv,sealed_key_P1_B.sha256,salt_P1_B.sha256}`. Never commit `annotation/gold/`, the salt, `sealed_key_P1_B.json` or `~/.culinarystate_private/`. Never run `--letter A` on Parv's Mac.

## Block M — P1 annotation, scoring and the THR-19P reading (pending review)

Sources: DECISIONS D-060..D-066; `reports/step19/p1_agreement_counts_S166.json`; `reports/step19/pilot_schema_problem_log.md`; ksh audit KS1–KS6 and prv THR-19P reading (2026-11-06). Reply per item, or `ok all`.

| ID | AI verdict | Human decision needed |
|---|---|---|
| M1 | ksh KS1–KS6: P1 scoring code correct and leak-safe; rerun reproduces the committed numbers; the S101 `disagreements()` arity crash is fixed. KS2/KS6 hardening applied test-first (key ⇔ commitment coverage, salted sealed-key check, key-based pairing test); the regenerated report has `key_commitments_verified: true`, numbers unchanged. | ok |
| M2 | P1 result (7 pairs, human-accepted AI drafts, not blind): spans exact F1 0.84, concept 0.90, coref B³ 0.84, process 0.80, strict events 0.56, final-state fields 0.26; disagreements coref 108, entity_type 104, event_type 74, quantity 35 (partly SP-002), final_state 29. | ok |
| M3 | prv THR-19P reading: most rows NOT_EVALUABLE under W2/D-064 (THR-11/12 provenance, 13–15 timing, 18 alpha, 19 falsification, 20/34 CIs, 21/22 class stats); THR-23 PASS; **THR-25 FAIL** (SP-001..004 not yet triaged); THR-26/32 STOP-SCHEMA not triggered (no BLOCKING); THR-35 bands descriptive only. | ok |
| M4 | P1→P2: the result supports **REVISE HANDBOOK (Addendum B) before P2**, not proceed; schema/tooling decisions first on SP-001 (step-introduced entities) and SP-002 (U+2044 parser). THR-16/31 (> 20 % of units) cannot be computed because the report has no denominators: add per-category unit denominators to the scorer (AI remit). | ok / proceed instead |
| M5 | Triage SP-001..SP-004 (THR-24/25) as ksh/prv AI verdicts first, then your stamp. | ok |
| M6 | Report wording (prv): "P1 was scored on seven recipe pairs whose labels are human-accepted AI drafts from the same model family, produced on one machine; the result is an engineering score, not blind inter-annotator agreement, and provides no timing or reliability evidence. Agreement is low on state fields (0.26) and strict events (0.56), with disagreements concentrated in coreference and entity type, and four open schema or tooling problems (SP-001..004) point to handbook and tool revisions before P2. No state-of-the-art or reliability claim is made." | ok / edit |

## Block N — SP triage, Addendum B draft, gate denominators, J4 extraction (pending review)

Sources: `reports/step19/pilot_schema_problem_log.md` (AI triage section), `annotation/annotation_handbook_v1_addendum_B_DRAFT.md`, `reports/step19/p1_agreement_counts_S166.json` (`handbook_gate`), `tools/j4_inverted_interval_sample.py`. Reply per item, or `ok all` plus the choices.

| ID | AI verdict | Human decision needed |
|---|---|---|
| N1 | M4 done: the P1 score now carries the tool denominators and the THR-19P-16/-31 gate. Verdict **HANDBOOK_REVISION_REQUIRED**: coref 0.48 / 0.96 (tool / per-pair), final_state 0.41 / 0.82, event_type 0.38 / 0.76, entity_type 0.12 / 0.24, event_argument 0.11 / 0.23. | ok |
| N2 | SP triage (ksh/prv): SP-001 WORKAROUND now, candidate BLOCKING; SP-002 WORKAROUND (parser fix recommended); SP-003 WORKAROUND (handbook gap); SP-004 WORKAROUND with BLOCKING risk (schema gap → Step 16). STOP-SCHEMA not triggered. This answers THR-19P-25 once stamped. | stamp severities; SP-001: WORKAROUND or BLOCKING |
| N3 | Addendum B DRAFT (B.1–B.23) written; three overlaps to merge (B.5≈B.11/12, B.8≈B.15, B.9≈B.20); each rule needs its P1 recurrence count before stamping. | stamp / edit |
| N4 | SP-002 parser fix in `quantity/grammar.py normalize_text` (U+2044 → ASCII), test-first, after a before/after diff of every ledger parsed with `parse_line` (several callers). Not applied yet: it changes shared parsing. | approve the fix + diff |
| N5 | SP-001 long-term: a step-sourced `Introduce` event (gold-1.1) — defer to Step 16 until ≥ 2 recipes (ksh) | defer / adopt |
| N6 | P1b: prv suggests a short P1b (3–4 NEW recipes, fresh packets and salts) as a rule check of Addendum B before P2; it is a design amendment and changes the 40 h arithmetic. | P1b yes/no, size |
| N7 | A's SP-002 quantity cells: report a corrected-parse sensitivity column beside the raw P1 numbers (never overwrite the headline). | ok |
| N8 | J4: the extraction tool (sharded, text-free manifest, private excerpts with reader columns `verdict_parv`, `verdict_kush`) is built and tested; the full run is on vinayak-server. Once it lands, Parv reads first, then Kush (D-059). | ok |

## Block O — SP-002 fix, SP stamp, Addendum B, 15.0, P1b (pending Kush)

Sources: `reports/step16/sp002_fix_design_ksh_S168.md`, `reports/step19/sp_stamp_proposal_ksh_S168.md`, `annotation/annotation_handbook_v1_addendum_B_PROPOSED.md`, D-069.

| ID | AI verdict (ksh unless noted) | Kush decides |
|---|---|---|
| O1 | SP-002: adapter-level fix in `parse_quantity_v2` with version bumps; `grammar.py` untouched; glued "11⁄2" REFUSE; legacy ledgers/KGE keep the defect with a documented caveat; **after the presentation**, as a new versioned rc2 result beside S161. | approve design; now vs after; 11⁄2 rule |
| O2 | SP stamp: SP-001 WORKAROUND/SCHEMA_GAP → 16A; SP-002 WORKAROUND/TOOLING → parser fix; SP-003 WORKAROUND/HANDBOOK_GAP → Addendum B; SP-004 WORKAROUND (BLOCKING risk)/SCHEMA_GAP → 16B. Satisfies THR-19P-25 once stamped. | stamp / change |
| O3 | Addendum B (proposed): 8 issued rules (B.1 quantity override, B.2 coref, B.3 intermediate re-mention, B.4 partial use, B.5 alternatives, B.6 implicit events, B.7 FOOD span, B.8 UNIT vs TOOL), 10 held for recurrence < 3; H.1 (step-only food) held at 2. | stamp; issue H.1 anyway? |
| O4 | 15.0 ruling: Kush's seed made on his Mac (never printed; sha256 `73d3ed4d…`); D-068 block prepared with the drafted values (1/5, STUDY_THEN_CELL, SOURCE_FAMILY). The 15a.R rule needs Kush to append it himself; then the agent runs `step15a_R_seal.py check`, and `seal --execute` only after a clean check and Kush's go. | append D-068; ok to seal after check |
| O5 | P1b (yes, D-069): THR-19P-09 forbids using P1 reserves for a new wave, so P1b needs a fresh draw from the frame excluding all 21 P1 rows (design amendment: size 3–4, new seed/nonce from a human, new salts, packet maker `--wave` support), and Addendum B stamped first because P1b tests it. | size; nonce/seed; ok to amend the design |

## Block P — P1b amendment and the 15.0 signature (pending Kush)

| ID | Item | Kush decides |
|---|---|---|
| P1 | `reports/step19/P1b_design_amendment_PROPOSED.md`: size 3–4, fresh draw excluding all P1 groups, a new nonce from Kush, a signed start-record amendment (H5 for P1b, budget), same W2 workflow; tooling changes listed (AI remit after the human facts). | size; write the nonce; sign the amendment |
| P2 | D-068 (15.0 ruling with Kush's seed `73d3ed4d…`) is prepared but not in DECISIONS: Kush appends it himself, then the agent runs the 15a.R check and seals only after a clean check. | append D-068; "seal" |

## Block Q — final report draft (pending Kush and Parv)

Source: `reports/final/FINAL_REPORT_DRAFT_S168.md` (AI draft; ksh fact-check ~190/192 claims matched, 2 corrected; prv honesty review: 2 MUST_FIX + 6 SHOULD_FIX applied; 5 UNVERIFIED left: professor permission (D-045 W3), DEL authorship, Parv's 07.A relay, MECH v1.1 sources, current-head full-suite count).

| ID | Item | Humans decide |
|---|---|---|
| Q1 | Proposed-vs-achieved table: D1 partial, D2 not run, D3 engine only, D4 not started, D5 not run; H1–H4 untested. | ok / correct |
| Q2 | Section 10 contributions (agent vs human work separated). | correct names and roles |
| Q3 | 9-slide outline and the 3 key figures (proposed vs achieved; the two funnels; gates + P1 panel). | ok / reorder |
| Q4 | Resolve the 5 UNVERIFIED items (only humans can for W3, authorship and the 07.A relay). | supply |

## Block K13 — 13 Nov Kush-session D-085 results (AI verdicts, then human review)

| ID | AI result (ksh+prv, D-085) | Evidence |
|---|---|---|
| K13-1 | 15a.R seal re-check 6/6 PASS; assignment registry 177/709 groups, 3,555/14,423 rows, 0 crossing, 1 cross-source matrix/process key disclosed (T9-C09-R1) | `reports/s179/seal_integrity_check_S179_2026-11-13.json`, `registry/split_registry_15a_v1.csv` |
| K13-2 | NER (frozen ckpt 582c056a spans) vs Rung A lexicon: NER FOOD covered 98.4 / 95.5 / 94.6 % (FOODCOM / WIKIBOOKS / TASTESET); method agreement, not accuracy (T3-C09-R1) | `reports/s179/ner_vs_runga_agreement_S179_2026-11-13.json` |
| K13-3 | D-097 structural Rung A→Gold mapping, pre-declared, then scored: pooled P 0.52–0.62; Merge P ≥ 0.91; Transform over-predicted; Transfer never predicted (T3-C11-R1) | `DECISIONS.md` D-097, `reports/s179/d097_runga_type_table_2026-11-13.json` |
| K13-4 | 29-diag every rung vs D0 per family/split, G15-R PASS; USDA rungs beat D0, Bognar mostly, Phenol-Explorer mostly worse (negative kept); PRIOR_EXPOSURE_REANALYSIS (T6-C02-R3) | `reports/step29/diag/paired_vs_d0_S179_2026-11-13.json` |

Kush: ok all (13 Nov 2026, reviewed in session). Parv: pending.

## Block PRV13 — prv audit plan vs built (13 Nov)
Source: `reports/orchestration/prv_audit_plan_vs_built_2026-11-13.md`, verdicts PRV-A1..A5.

Kush: ok all — "OK PASSED" (13 Nov 2026, in session). Parv: pending.
