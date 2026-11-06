# Step 26g census files (D-055, review block K7)

| File | Status |
|---|---|
| `simulability_census_real_sample_counts.json` | **Superseded by the S166 file.** Parv, 2026-11-04, ad hoc chain, seed `dryrun-2026-11-04`, 1,000 recipes. Kept unchanged for the record. Its `adapter_invented_excluded` 2 predates the S161 `º` auditor rule. |
| `simulability_census_real_sample_counts_S166.json` | Current. Committed tool `tools/step26g_census.py` from a clean checkout (`code_provenance.git_dirty` false), same seed and sample. Census block and `census_sha256` `7e660634…` identical to Parv's; `adapter_invented_excluded` 0. |

All-SIM_PROHIBITED is by construction: no condition or applicability bindings exist yet (`prohibited_by_construction`). It is not a finding about the corpus.
