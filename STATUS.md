# STATUS — CulinaryState (Group 17 · Kush Tokas + Parv Goyal)

**As of:** 2026-10-28, Step 16 rc2 draft implementation (WORKLOG S151; DECISIONS through D-042).
**Authoritative records:** DECISIONS.md, WORKLOG.md and the dated review artifacts.
**Repo in this session:** `/Users/parvgoyal/wth/CGAS/takeover/culinarystate`.
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
| Step 16 | Draft registries/frame/strata retained. Separate QNT/STATE rc2 proposals now implement claim metadata, all eleven AST payloads, exact arithmetic and combined validation. Earlier drafts/frozen schemas unchanged. Coverage/convention acceptance, grounding/integration and history policy still need review; 16c waits for Step 19 and H4. Legacy zero-multiplier defect recorded for versioned correction. |
| Step 19 | Design exists; no new start/seal approval or sample draw. Human annotations/representability/IAA evidence not replaced by AI review. |
| Step 35 | 35c/35d/35e synthetic-tested; existing RDKit 2026.3.6 pinned as optional step35 extra. Parv's D1–D8 review choices recorded. Protocol, mapping and new companion-bound review package remain unsigned; no real evaluations. Learned 35g deferred. |
| Cuisine | D-040 single-reviewer lookup choices applied; REGION extended to reviewed below-country terms. Coverage 12.9% cuisine, 23.7% continent; cuisine conflicts 2,643 retained/excluded from single-cuisine scoring. Expert/signatures pending. |
| Pilot column | Parv selects reserve_split_v2 and retains v1 for comparison, DRAFT_PENDING_KUSH. Strata/frame unchanged; no draw. |
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
- `handoff/PARV_SESSION_NOTES.md`: append-only session record.

Full unit-suite verification now includes transition tests under scoped CPU thread
caps: `OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1` before the existing
Python's `-m pytest tests/unit -q`. This is a reproducible hang workaround, not a
proven root-cause fix. Exact final counts are in WORKLOG S151. The pytest config
still excludes tests marked ledgers unless explicitly requested.

## Human work and constraints

- Kush arranges a consenting chemistry reviewer; cuisine expert pending. Parv owns the unfinished crosswalk audit, including the priority collision sheet.
- Parv writes his own 07.A/07I-C confirmation after review and supplies Step 16 comments; no statement is inferred.
- Integrate accepted protocol changes, bind reviewed companion inputs, hash final bytes and obtain the required human signatures before any real Step 35 evaluation.
- H2 licence decisions and remaining source permissions are human-owned. Restricted recipe data and per-item worksheets stay local and ignored by git.
- Confirm the IIITD VPN before GPU work (Step 17/20 after their gates). No GPU job is running from this session.
- No push without Kush's explicit session approval. No signature, expert approval or failed-gate pass is supplied by this status refresh.

Presentation dates remain 25–26 November 2026 per the handoff; this review did
not independently verify that schedule. Older manual tasks and the remaining
Step 21 chemistry questions require their own review rather than blanket closure.
