# STATUS — CulinaryState (Group 17 · Kush Tokas + Parv Goyal)

**As of:** 2026-11-05, S163 full-corpus Step 17b run and auditor fixes (PR #4) plus Parv's 2026-11-04 local runs merged (PR #5), on top of S154–S162 (WORKLOG S163; DECISIONS through D-053). **Checkpoint H-A partly answered (D-053); human-only values still open.** Working order D-045: AI verdict first, then Kush and Parv review (final).
**Authoritative records:** DECISIONS.md, WORKLOG.md and the dated review artifacts.
**Repo in this session:** cloud container `/home/user/culinarystate`, branch `cloud/s161-real-data-runs` (from `cloud/s160-freeze-prep`, whose tree equals `main` after PR #2). **Data bundle present** (checksums verified 2026-11-04); real-data runs in `reports/step16/S161_real_data_runs.md`.
The previous S145 status snapshot is preserved in git history (before S150,
commit `ae5fc5a`); it contained stale pending/not-authorised wording superseded
by D-035 and later takeover decisions. No historical failed gate is erased.

## Current stage

ES-1 evidence/recipe infrastructure and unsigned representation/schema drafts.
The project is not complete. Engineering checks and AI source checks do not
supply human annotation, independent agreement, scientific validation or signatures.

| Lane | Current evidence and limits |
|---|---|
| Authority / contracts | D-027 governs. D-029 approved lineage/minimal contracts; other H4/kinetic addenda retain their own gates. Historical Steps 01–04 do not approve all later drafts. |
| Evidence / recipes | Existing 17,978-row EVD export basis and 612,782-recipe base retained. EVD/COND/SRC/MEAS/SNAP must remain byte-identical; STUDY and _ids are append-only. |
| 07.A | Returned audit's signed statistical gate FAILED. No alternative statistic is substituted to open dependent steps. |
| 07I-C | Original blind kappas 0.571 / 0.588 retained. D-033's 0.88 is Kush-stated on an adjudicated single-reviewer basis, not computed inter-reviewer agreement. Parv's own written confirmation remains pending. |
| 08a / 08b | 08a built and run, G08-3 FAIL remains; B2/B3 edges and keys provisional. D-035 authorised 08b-v0 only; v1 and downstream wiring still not authorised. Expert USDA/Bognar overlap reading remains pending. |
| Step 16 | rc2 proposals, versioned zero-preserving normaliser and conservative parsing/AST adapter implemented. S154: opt-in rc2 grounding pipeline (parse → unit resolution → exact Q0 → human-verified POR hard filters → record + invented-value audit), rc2 history-policy check and a counts-only real-data dry-run tool, all synthetic-tested. **S161 real-data dry-run:** 612,782 recipes, 4,281,956 lines, 0 exceptions, invented grams 0, rc2 mass Q0 on 33,373 lines (0.78 %), 21,172 unsupported expressions. Old grammar/normaliser/rc1/frozen schemas untouched; production migration, semantics/H4 and pilot evidence still open. |
| Step 19 | Six-stage synthetic rehearsal, v2 draft handbook, 17 synthetic cases and unsigned start record prepared. S154: real-pilot gate `tools/step19_real_pilot.py` refuses the P1 draw until every human prerequisite exists; on the current record it lists 10 blockers (signatures, H5, nonce, capacity, B_h, THR-19P rows, instrument, pilot column, method amendments, draw spec). P2 refused. No real frame/draw, human labels or timing/IAA result; P1 current-v0 instrument boundary retained. D-046: THR-19P-01..35 signed; instrument, pilot column (v2), method ruling and draw spec accepted. D-048: signed start record `pilot_start_record.SIGNED.json` (joint nonce, 15 h/week and 40 h budget each), gate ready with 0 blockers; the P1 frame must be rebuilt after the nonce commitment, then C2 draws. **Parv (2026-11-04, local, under D-048): P1 frame and strata rebuilt (byte-identical to the tracked drafts) and drawn: 21 rows, 7 strata (`deep_gold_pilot_v1/manifest_P1.csv`); packet maker built (7 tests); annotator B's 7 blank packets made. Annotator A's packets (Kush's machine) and all annotation still pending.** |
| Step 17 | S155, DRAFT_PENDING_16c: 17a interfaces, validators V1–V4 and invented-value auditor; 17b deterministic Rung A baseline. Synthetic only: invented_count 0 on 13 fixtures and 17 hard-case prompts (SYNTHETIC_NOT_GOLD). S161 real 1,000-recipe dry-run: invented_count 23 (auditor false positive on `ºF`/`ºC`, fixed test-first) → 0 after the fix; V2 5 inverted intervals. S163 full corpus (612,782 recipes, vinayak-server, CPU only): invented_count 626 → 4 → 0 after two test-first auditor fixes (`deg`/`degree` prefix before C/F, lowercase c/f); exceptions 0; V2 `INVERTED_INTERVAL` 4,511 in 3,848 texts (review pending). AI cross-review fixed R1–R7; O1–O9 await Parv (review sheet block D). G17 gates not evaluated. |
| Step 18 / 26g | S156, DRAFT: append-only event log, deterministic replay (transactions and snapshot hashes, exact bounds, issue codes) and extraction→engine adapter; 26g simulation-input contract with null sim_run_id links and a counts-only simulability census. Old engine L1–L8 left unchanged (Kush). The test_transition hang does not reproduce in the cloud. G18 gates not evaluated. Block E pending review. |
| Evidence 09/12/13a-0 | S157, PROVISIONAL: Step 09 verification-queue machinery (status only from a human review file; no code path to E4), 12.0 proposed SRC/SNAP rows in staging only, 12-local R2/Bognar parsers (raw text git-ignored; counts-only report), 13a-0 offline seed corpus with 713 exact-DOI seeds from tracked artifacts. No ledger write. S161 real runs: 12.0 3 SRC + 7 SNAP proposed (staging only); 12-local 173 R2 rows, 1,693 Bognar cells (T36 unparsed); 13a-0 715 seeds (703 DOI). Kush's review of the 12.0 file and the D-049 re-baseline are pending. |
| 04.3 / 21 / 22a / 23a | S158, DRAFT: KIN/KINPT v1.1 with a cross-record validator; MECH v1.1 with 14 expert questions (sources UNVERIFIED: hosts blocked); sign-only 22a signatures plus a case-seal helper (nothing sealed); three-valued 23a applicability engine (UNKNOWN never SIMULATE, APPDEC compatible with 26g); 23b BLOCKED. Block G pending (H4, expert answers). |
| 24a / 26a–c | S159, DRAFT and data-free: FORM/PARAM/VAL schemas; kinetic fitting and identifiability library (synthetic recovery; NOT_IDENTIFIABLE designs refused); sim_aa_1 and sim_chl_1 behind one APPDEC-gated interface with no parameter values in code; 26c verification passing; 26.0 selection template unsigned (system not chosen). D-051 signed THR-04K-01..04; scipy declared as extra step26 (D-050). Block H pending. |
| 15.0 / 15a.R / 29–34 scaffolds | S160, DRAFT: 15.0 rulings draft (RESERVED fraction UNKNOWN, needs Kush; Parv's 2026-11-04 draft `reports/step15/15_0_ruling_DRAFT_FOR_KUSH_SIGNATURE.md` proposes 1/5, STUDY_THEN_CELL, SOURCE_FAMILY and a seed hash, seed on Parv's Mac; not a decision); 15a.R seal tool refusing until a signed 15.0 exists (not run); group-disjoint split and leakage checks; NON_CITABLE 29-diag runner (refuses); Step 30 bake-off with no default margin (Parv's exploratory D0–D2 run is DIAGNOSTIC_ONLY, not pre-registered, not citable); 34a/34c scaffolds unsigned. 26.0: sim_aa_1 selected (D-052). Block I = checkpoint H-A: D-053 accepted the AI recommendations (C2-a, H-3, X-1, G-1, K-1, STUDY_THEN_CELL, SOURCE_FAMILY, Route B, R1–R4); the RESERVED fraction, seed, δ_30/ρ/c_floor, 34c values, P-1..P-5, S-1/S-2 and the Step 35 signature stay open, so 15a.R, Step 35, 29-diag and Step 30 still refuse. |
| Step 35 | S160: v2 protocol `009c9047…` + UNSIGNED record `8885a63a…` ready for Kush/Parv signature (v1 unchanged; D-041 amendments P-1..P-5 and the S-1/S-2 pre-signature conditions open); runner refuses until signed. Earlier: 35c/35d/35e synthetic-tested; existing RDKit 2026.3.6 pinned as optional step35 extra. Parv's D1–D8 review choices recorded. Protocol, mapping and new companion-bound review package remain unsigned; no real evaluations. Learned 35g deferred. |
| Cuisine | D-040 single-reviewer lookup choices applied; REGION extended to reviewed below-country terms. Coverage 12.9% cuisine, 23.7% continent; cuisine conflicts 2,643 retained/excluded from single-cuisine scoring. Expert/signatures pending. |
| Pilot column | Parv selects reserve_split_v2 and retains v1 for comparison, DRAFT_PENDING_KUSH. Strata/frame unchanged; P1 drawn by Parv under D-048 (see Step 19). |
| Expert precheck | AI source evidence explains 204 deprecated taste-edge migrations, reconstructs 307 crosswalks / 298 ING, and isolates one name collision. Human chemistry/cuisine/crosswalk verification is pending. Proposed negative-label and triplet-statistic corrections are not adopted thresholds. |
| Later steps | Evidence verification/licence gates, 07.A, 08b-v1, 16c/19 and real held-out validation still constrain completion. See the 36-step roadmap; unreviewed historical prototypes are not certified complete. |

## Review and verification entry points

- `reports/review/AI_REVIEW_2026-10-28.md`: findings, fixes, primary sources, limits and expert procedure.
- `reports/review/machine_evidence.json`: source/code hashes and per-edge checks; reproduce with `tools/review_takeover.py`.
- `reports/review/protocol_review_addendum_DRAFT.md`: exact scientific amendment proposals, awaiting review.
- `reports/review/project_completion_roadmap.md`: critical path and all 36 planning-snapshot rows.
- `reports/step35/35_0_parv_review_DRAFT.md`: Parv's answers, distinct from signatures.
- `reports/step16/parv_review_comments.md`: AI findings; Parv's own comments pending.
- `reports/step16/metadata_quantity_contract_v2_DRAFT.md`: proposed rc2 contract, API, synthetic examples, limits and remaining H4 choices.
- `reports/step16/engineering_and_pilot_lane_build_note.md`: S152 implementation, independent review dispositions, pilot artifacts and unfinished prerequisites.
- `reports/step17/S155_build_note.md` and `handoff/REVIEW_SHEET_AI_VERDICTS.md`: S155 extraction drafts and every AI verdict pending or accepted by Kush/Parv.
- `reports/step16/S154_build_note.md`: S154 grounding pipeline, history check, dry-run tool, real-pilot gate, verification and what still needs humans.
- `handoff/PARV_SESSION_NOTES.md`: append-only session record.

Full unit-suite verification now includes transition tests under scoped CPU thread
caps: `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1` before the existing
Python's `-m pytest tests/unit -q`. This is a reproducible hang workaround, not a
proven root-cause fix. Latest full unit result on the Mac: 1681 passed, 1 skipped, 1 deselected (WORKLOG S152). S161 cloud container **with** the data bundle: 3215 passed, 2 skipped, 1 deselected, 0 failed (the 12 bundle failures now pass). Earlier, S154 cloud container without the data bundle: 1797 passed, 17 skipped, 1 deselected, 1 failed + 11 errors, all missing bundle files (same as its pre-change baseline); rerun on the Mac with data before merging. The pytest config
still excludes tests marked ledgers unless explicitly requested.

## Human work and constraints

- Kush arranges a consenting chemistry reviewer; cuisine expert pending. Parv owns the unfinished crosswalk audit, including the priority collision sheet.
- Parv writes his own 07.A/07I-C confirmation after review and supplies Step 16 comments; no statement is inferred.
- Integrate accepted protocol changes, bind reviewed companion inputs, hash final bytes and obtain the required human signatures before any real Step 35 evaluation.
- H2 licence decisions and remaining source permissions are human-owned. Restricted recipe data and per-item worksheets stay local and ignored by git.
- Kush and Parv review the S161 counts-only real-data outputs (`reports/step16/S161_real_data_runs.md` section 7). The Step 19 real pilot cannot draw until the 10 blockers listed by `python tools/step19_real_pilot.py check --record reports/step19/pilot_start_record.UNSIGNED.json` are supplied by the named humans (S154 build note).
- Confirm the IIITD VPN before GPU work (Step 17/20 after their gates). No GPU job is running from this session.
- D-044 records Parv's explicit instruction to push this prepared work on a new branch in Kush's repository; remote main/merging/force-pushing remain outside scope. No signature, expert approval or failed-gate pass is supplied by this status refresh.

Presentation dates remain 25–26 November 2026 per the handoff; this review did
not independently verify that schedule. Older manual tasks and the remaining
Step 21 chemistry questions require their own review rather than blanket closure.
