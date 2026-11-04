# Local run record, 2026-11-04 (Mac, real data present; counts and hashes only)

Branch `parv/local-real-runs-2026-11-04` on top of `cloud/s160-freeze-prep` (8759550). Nothing signed, no ledger row written, no human gate supplied.

| # | Job | Estimate | Actual | Result | File |
|---|---|---|---|---|---|
| 1 | Full unit suite | 2 min | 114 s | 3212 passed, 2 skipped, 1 deselected, 0 failed | this record |
| 2 | Step 16 rc2 grounding dry-run, 612,782 recipes | 30-60 min | 28.9 min | 4,281,956 lines, 33,373 with rc2 mass, 0 exceptions | reports/step16/rc2_grounding_dryrun_counts.json |
| 3 | Step 17b Rung A dry-run, 1,000 seeded recipes | 1-3 min | 15 s | 4 invented values (UNIT_NOT_IN_SPAN, 2 Food.com texts), 0 exceptions | reports/step17/rung_a_dryrun_counts.json |
| 4 | Step 19 P1 frame, strata, draw | 5-10 min | about 1 min | 21 rows, 7 strata; frame and strata byte-identical to tracked drafts | registry/recipe_semantics/deep_gold_pilot_v1/manifest_P1.csv |
| 5 | Step 13a-0 seed corpus with local OpenAlex | 1 min | under 1 s | 715 seeds (703 with DOI) | registry/evidence/seed_corpus_13a0_full_v0.jsonl, reports/step13/ |
| 6 | Step 12-local staging | 1 min | under 1 s | 173 R2 rows, 1,693 Bognar cells, T36 unparsed, 0 ledger writes | reports/step12/step12_local_counts_v1.json |
| 7 | Step 12.0 SRC/SNAP proposals | 1 min | under 1 s | 3 SRC + 7 SNAP proposed, staging only | registry/staging/step12_0_src_snap_proposed_v1.jsonl |

Reproduced unchanged: cuisine census (`tools/step35_foodcom_tag_census.py`) and `tools/review_takeover.py` regenerated their tracked outputs with no diff.

## Attempted and refused (by design)
- 15a.R seal: blockers NO_15_0_DECISION_ID, SEED_FILE_MISSING, SEALED_OUT_MISSING.
- 29-diag: SNAPSHOT_NOT_FROZEN, NO_SIGNED_15_0, SEAL_COMMITMENT_MISSING, SEALED_LIST_MISSING, DIAG_PREREG_UNSIGNED.
- Step 35 explicit baselines: PreregNotSigned (no `preregistration_35_0_v2_package.sha256.SIGNED.json`).

## Not runnable locally
- 26g simulability census: needs extracted events (Step 17 extraction not done).
- Step 19 packet maker and annotation: packet tools not built; annotation is human work.
- Step 30 bake-off, 34a/34c: need frozen data and signed pre-registrations.
- GPU and evidence-extraction jobs: VPN and human gates.
