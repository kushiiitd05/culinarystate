# Local run record, 2026-11-04 (Mac, real data present; counts and hashes only)

Branch `parv/local-real-runs-2026-11-04` on top of `cloud/s160-freeze-prep` (8759550). Nothing signed, no ledger row written, no human gate supplied.

| # | Job | Estimate | Actual | Result | File |
|---|---|---|---|---|---|
| 1 | Full unit suite | 2 min | 114 s | 3212 passed, 2 skipped, 1 deselected, 0 failed | this record |
| 2 | Step 16 rc2 grounding dry-run, 612,782 recipes | 30-60 min | 28.9 min | 4,281,956 lines, 33,373 with rc2 mass, 0 exceptions | reports/step16/rc2_grounding_dryrun_counts.json |
| 3 | Step 17b Rung A dry-run, 1,000 seeded recipes | 1-3 min | 15 s each | seed `dryrun-2026-11-04`: 4 invented values in 2 texts; **seed 20261104 (requested): 23 invented values in 9 texts**, all UNIT_NOT_IN_SPAN, 0 exceptions | reports/step17/rung_a_dryrun_counts.json (seed 20261104), rung_a_dryrun_counts_seed_dryrun-2026-11-04.json |
| 8 | 26g simulability census via RungA -> event adapter -> replay -> sim_aa_1, same 1,000-recipe sample (seed `dryrun-2026-11-04`) | 2-5 min | 15 s | 998 texts, 23,943 engine events, all SIM_PROHIBITED (0 SIMULATE), 0 exceptions, 2 invented values excluded by the adapter | reports/step26/simulability_census_real_sample_counts.json |
| 4 | Step 19 P1 frame, strata, draw | 5-10 min | about 1 min | 21 rows, 7 strata; frame and strata byte-identical to tracked drafts | registry/recipe_semantics/deep_gold_pilot_v1/manifest_P1.csv |
| 5 | Step 13a-0 seed corpus with local OpenAlex | 1 min | under 1 s | 715 seeds (703 with DOI) | registry/evidence/seed_corpus_13a0_full_v0.jsonl, reports/step13/ |
| 6 | Step 12-local staging | 1 min | under 1 s | 173 R2 rows, 1,693 Bognar cells, T36 unparsed, 0 ledger writes | reports/step12/step12_local_counts_v1.json |
| 7 | Step 12.0 SRC/SNAP proposals | 1 min | under 1 s | 3 SRC + 7 SNAP proposed, staging only | registry/staging/step12_0_src_snap_proposed_v1.jsonl |

Reproduced unchanged: cuisine census (`tools/step35_foodcom_tag_census.py`) and `tools/review_takeover.py` regenerated their tracked outputs with no diff.

## Attempted and refused (by design)
- 15a.R seal: blockers NO_15_0_DECISION_ID, SEED_FILE_MISSING, SEALED_OUT_MISSING.
- 29-diag: SNAPSHOT_NOT_FROZEN, NO_SIGNED_15_0, SEAL_COMMITMENT_MISSING, SEALED_LIST_MISSING, DIAG_PREREG_UNSIGNED.
- Step 35 explicit baselines: PreregNotSigned (no `preregistration_35_0_v2_package.sha256.SIGNED.json`).

## Attempted and refused (continued)
- Step 34c abstention spec: SPEC_NOT_SIGNED, SIGNER_NOT_KUSH, SIGNED_AT_INVALID (status DRAFT_PENDING_34c_KUSH_SIGNATURE).
- Step 35 tasks 35a-35e: all five PreregNotSigned (v2 package SIGNED record missing).
- Step 30 bake-off: library only; no frozen 15a snapshot, no frozen model registry, no pre-registered margin; nothing to run on.

## Not runnable locally
- Step 19 packet maker and annotation: packet tools not built; annotation is human work.
- Step 30 bake-off, 34a/34c: need frozen data and signed pre-registrations.
- GPU and evidence-extraction jobs: VPN and human gates.

## Final attempts and why the rest stops here
- 15a.R seal, `check` with a seed-file and sealed-out path outside git: still refuses. The 15.0 decision must carry `15.0 RESERVED_FRACTION`, `RESERVED_UNIT`, `RESERVED_STRATIFY` and `15a.R SEED_SHA256` lines (none exist; a human writes them) and the seed file must be human-supplied. Running `seal --execute` would need an agent-chosen fraction and seed, so it was not run.
- 29-diag: same 15.0 and seal dependency, plus a signed 29-diag pre-registration (Kush) and a frozen 15a snapshot (`frozen snapshots: []`). Not run.
- Step 30 bake-off: `ModelRegistry` holds 0 models and is unfrozen; `GroupSplit` needs the frozen 15a assignment; `paired_cluster_bootstrap` requires a pre-registered `margin` with no default. An agent-built split and margin would be a post-hoc rule choice, so no bake-off was run.
- Step 34a/34c, Step 35 a-e: signature gates, refused as recorded above.
- Step 19 packet maker: no tool exists (`tools/` has only the Step 07/08a packet builders). Building it is new engineering, not a run; annotation itself is human work.
