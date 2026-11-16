# CulinaryState reduced-submission candidate

**DRAFT_CANDIDATE_NOT_AUTHOR_APPROVED**

AI_DELEGATED_D085 · NOT_INDEPENDENT · NOT_HUMAN_VERIFIED_UNTIL_REVIEW · NO_HUMAN_SIGNOFF_D085

This is a curated artifact bundle for the reduced submission and Kush's takeover. It preserves the original report/deck drafts and exports alongside later technical addenda. It is not final author approval, a scientific validation result, a main-branch merge or a completed rehearsal.

## Reading order

1. `handoff/KUSH_TAKEOVER_REDUCED_SUBMISSION_2026-11-13.md`.
2. The newest paired-review closeout summaries, then `reports/final/drafts_2026-11-13/prv_technical_results_update_DRAFT.md` and the separate D5 caveat insert.
3. Original report/deck Markdown and exported PDF/HTML under `reports/final/exports_2026-11-12/`.
4. Frozen D5 results, diagnostic summaries, source-licence follow-up, figure manifests and verification evidence as needed.

The exported report is the earlier ten-page draft and the deck is the earlier thirteen-slide draft. Newer addenda supersede stale statements about artifact availability or pending local reviews; they do not silently edit the original drafts or change frozen results. Original H1/H3 RULE_NOT_MET outcomes and all source/independence limitations remain visible. Claims from AI-labelled Gold and scientific pilot outputs retain their stated diagnostic limits.

Author facts, signatures, final editorial edits and final approval remain outside this candidate. Any placeholder must be resolved by the actual authors before final submission. A planned run sheet is not proof that a timed rehearsal occurred.

## Build and verify

Run from the project repository using its existing Python environment:

```sh
python tools/s179_submission_candidate.py \
  --allowlist reports/final/submission_candidate_2026-11-13/allowlist.json \
  --archive data/derived/submission_candidate_2026-11-13/CulinaryState_reduced_candidate_v1.zip \
  --manifest-out reports/final/submission_candidate_2026-11-13/build_manifest_v1.json
```

The explicit member list includes the paired-review summaries and takeover document. No directory recursion or glob expansion is used by the packager. Both output paths must be new; rebuilding uses new versioned paths. The archive stays local in a git-ignored directory. Its hash is recorded in the external build manifest; `MANIFEST.json` inside the archive binds every included member's exact bytes and source revision. Verify the ZIP hash against the external manifest and member hashes against the internal manifest before transfer. Public hash manifests do not constitute scientific validation or redistribution clearance.

## Repository and local demonstration

Repository: https://github.com/kushiiitd05/culinarystate

Use the exact source revision from the final build manifest, rather than an unpinned moving branch:

```sh
git clone https://github.com/kushiiitd05/culinarystate.git
cd culinarystate
git checkout <source_revision_from_build_manifest>
python tools/run_local_demo_v3.py
```

Use the project's compatible, already established Python environment; the recorded Python3.11 dependency snapshot is `reports/s179/env_lock/parv_S179_2026-11-11.txt`, with metadata in the matching JSON. This candidate does not install dependencies or include private corpora, checkpoint weights or a complete executable environment. The loopback demo defaults to port8765. If the required local data is unavailable, use the saved screenshot and technical run sheet, explicitly identifying them as saved demonstration material. No external model call or hosting is needed for the saved fallback.

## Data boundary

Only explicitly listed report, figure and handoff artifact files may enter the archive. The packager rejects absolute/traversal paths, symlinks, raw/private directories, secret/model filenames and unsupported extensions. It never copies `data/`, `annotation/`, source-paper PDFs, recipe text, private review sheets, ledgers, model weights or seals. The separate private return pack is not part of this candidate and has not been sent by this build.

The allowlist is human-reviewable scope, not a general content-entailment auditor. Review any newly added public artifact for source-text and privacy limits before building. A working archive proves packaging and byte identity; scientific source validity, human independence and author approval remain separate requirements.
