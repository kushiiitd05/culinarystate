# Parv session notes (append-only)

## 2026-10-28 — S147
- Baseline: 1510 passed, 1 skipped, 8 deselected; final: 1512 passed, 1 skipped, 8 deselected (`not test_transition`).
- Fixed duplicate CSV headers overwriting 35e fields; two synthetic regression cases failed first, then passed; targeted suite 147 passed.
- Tests/code commits: e675949, 6ba4725; build-note/guard-doc commits: 87fc30e, 9c66a25.
- Step 16 technical review: reports/step16/parv_review_comments.md (a3f55eb); explicitly AI review, Parv comments pending.
- Step 16 before freeze: settle FAM: roots versus PROC family IDs, required per-field metadata, AST payloads/history routes; validate QNT/POR bound ordering.
- Hierarchy references/cycles and CSV widths checked; no vocabulary or schema changed. Historical STUDY-size failure note is stale; current test passes.
- D1 choice (a) preserved as review only in reports/step35/35_0_parv_review_DRAFT.md (890d532); no signature.
- Unsigned current-draft hash template (21d0196) is correctly refused by G35-PRE; regenerate after protocol edits.
- All remaining review questions requested together; D2-D8 unanswered (D5 reserved to Kush), cuisine rulings and pilot-column choice pending.
- No new human decisions for Kush to confirm yet. Parv's own 07.A/07I-C written confirmation and Step 16 comments still pending.
- Kush: review S146's six 35e conventions/open points; rdkit and H2 licence choices; sign 35.0 or record his single-signer reason.
- EVD/COND/SRC/MEAS/SNAP full hashes match baseline; STUDY/_ids baseline prefixes match; D-038 strata hash matches.
- WORKLOG S147 commit: 97cffaf; this session-note file is committed separately under the one-file rule.
- No real Step 35 evaluation, sample draw, signature, human-label change, dependency install, GPU work or push.
## 2026-10-28 — S148 (D-039)
- Parv approved D2/D3/D4/D6/D7/D8 rules and explicitly instructed D5 go; existing RDKit 2026.3.6 pinned as optional step35 extra, no install. Cuisine mappings/continents/conflicts/coverage, reviewers, crosswalk owner, pilot column and own adjudication statement remain pending; follow-up batch sent. No signatures, real evaluation, ledger changes or push.
- Synthetic Morgan/Murcko checks and TOML/version check pass; guard/registry 43 passed; prior full suite 1512 passed. Draft hash unchanged, record unsigned. Commits dc0701b (pin), 6cc8760 (environment), cd0c204 (review), bb1a245 (D-039), a2abe94 (S148); notes committed separately.
## 2026-10-28 — S149 (D-040)
- Applied exactly Parv's 15 cuisine rulings, expanded REGION to below-country terms, refreshed unsigned aggregate map; conflicts excluded/count retained. Cuisine coverage/conflicts remain 12.9%/2643; continent coverage/conflicts now 23.7%/3386. Single-reviewer only; chemistry reviewer (Kush to arrange) and cuisine expert pending. Pilot reserve_split_v2 selected, v1 comparison retained, DRAFT_PENDING_KUSH; no draw. Parv owns unfinished crosswalk audit; own 07.A/07I-C statement and Step16 comments pending.
- Census tests 9 passed; full suite 1512 passed, 1 skipped, 8 deselected. Counts/statuses unchanged per tag; protocol unsigned/hash, strata hash, ledger checks pass. Commits a3e9e39 tests; 632f812 lookup; dd8a49d map; 2e5b61f README; 0cc2cf7 pilot; e7949b8 review; 76f7bf1 checklist; 64fa442 D-040; WORKLOG and these notes committed separately. No scoring, signature or push.
## 2026-10-28 — S150 (D-041, AI review; expert acceptance pending)
- Review/evidence/proposals/36-step roadmap: reports/review/. All204 deprecated taste edges source-explained as free-text-to-class migration; no taste-validity approval. Crosswalk reconstruction307 nodes/298 ING agrees with29656 active PRESENCE rows; one collision flagged. Local features/step35/ai_review/ holds50-row and supplemental priority worksheets, human fields blank, overwrites refused after human entry.
- Tests-first fixes: duplicate rankings, invalid mass/profile/NPMI support, draft EVT FAM namespace; added pure semantic review overlay and companion-file signature binding. Proposed molecule-level negative rule and triplet convention await expert decision; AST/metadata/history/cuisine scope remain open. Old protocol/thresholds/labels/ledgers unchanged; packages unsigned.
- Full suite1562 passed,1 skipped,1 deselected in76.89s with OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=MKL_NUM_THREADS=1; transition tests included, existing not-ledgers marker retained.43 added synthetic controls; audit byte-identical on rerun; source/code hashes, protected ledger baseline/prefixes and package hashes pass.
- Commits4dd70ed..74cce11 (26 commits, one file each, Parv author); this note committed separately. STATUS refreshed. Expert/human reviews, signatures, H5 pilot/16c and other roadmap gates still open. No real scoring, pilot draw, human labels, GPU work or push.
## 2026-10-28 — S151 (D-042, rc2 draft; H4 pending)
- Built separate QNT/STATE rc2 schemas, per-claim metadata, all11 typed AST nodes, exact interval/fraction/package/remainder arithmetic and rational JSON results. No metadata backfill, hidden unit conversions, branch selection or grams inferred. Spec and seven synthetic examples: reports/step16/metadata_quantity_contract_v2_DRAFT.md and quantity_contract_synthetic_examples.json.
-54 new synthetic cases pass; full unit suite1616 passed,1 skipped,1 deselected in76.69s with CPU thread caps, transition tests included. Schemas regenerate identically; examples reproduce; old rc1/frozen schemas, ledger checks and Step35 unsigned/hash checks pass. Review overlay JSON Pointer mode is opt-in.
- Recorded legacy zero-package multiplier bug (old normaliser defaults0 to1); new AST zero is correct, old path unchanged. Versioned normaliser/adapter fix and parsing/POR/source integration remain next engineering work; H4 conventions/history and Step19 pilot/16c still pending.
- Commits a6016bd..163ba4a (12 single-file commits, Parv author), notes committed separately. STATUS/roadmap updated. No real recipe processing, pilot draw, ledger labels, signatures, expert acceptance, GPU work or push.
