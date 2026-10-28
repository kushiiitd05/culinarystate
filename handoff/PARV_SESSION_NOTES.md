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
