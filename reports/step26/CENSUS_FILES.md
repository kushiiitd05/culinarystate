# Step 26g census files (D-055, review block K7)

| File | Status |
|---|---|
| `simulability_census_real_sample_counts.json` | **Superseded by the S166 file.** Parv, 2026-11-04, ad hoc chain, seed `dryrun-2026-11-04`, 1,000 recipes. Kept unchanged for the record. Its `adapter_invented_excluded` 2 predates the S161 `º` auditor rule. |
| `simulability_census_real_sample_counts_S166.json` | Current. Committed tool `tools/step26g_census.py` from a clean checkout (`code_provenance.git_dirty` false), same seed and sample. Census block and `census_sha256` `7e660634…` identical to Parv's; `adapter_invented_excluded` 0. |

All-SIM_PROHIBITED is by construction: no condition or applicability bindings exist yet (`prohibited_by_construction`). It is not a finding about the corpus.

| `simulability_census_full_corpus_S166.json` | Full corpus (612,782 recipes, seed 20261104), vinayak-server, CPU only, ~4 h single process (D-055 K8). 611,902 texts with steps, 14,594,812 engine events, SIMULATE 0, exceptions 0, invented 0, baseline PASS before and after; reasons besides the 8 MISSING_* inputs: APPLICABILITY_UNKNOWN 14,594,812, NO_CONSUMED_ENTITY 6,152,456, REPLAY_HAS_ISSUES 269,062, EVENT_REJECTED_IN_REPLAY 86,989. Ran on the tool before the K7/K9 changes (no `reading`/`prohibited_by_construction` fields, no post-run provenance check); `git_commit` null because the server copy has no `.git`; module and src-tree hashes in `code_provenance` pin the code. All-prohibited is by construction, as above. |
