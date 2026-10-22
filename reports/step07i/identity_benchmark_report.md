# STEP 07I-R -- benchmark, memory and reproducibility report

Machine: Mac M2 Pro, 8 GB, macOS, `/opt/anaconda3` (Python 3.11, pyarrow 14, pandas 2.1). Disk free ~28 GB. Machine was **not idle** (browser, Spotify, other agent session resident; swap 4.4-5.8 GB used throughout), i.e. these are worst-case numbers for the target machine.
Worker model: 3 `spawn` workers + 1 parent; ceiling `--max-memory-gb 4.5` (process-tree RSS). Tooling: pyarrow + numpy only (no DuckDB/Polars on the Mac; the identity data is integer-encoded Arrow so no SQL engine or spill directory is needed).

## 1. Staged benchmark (full 611,714-representative universe, chunk_size = 10,000)

| Stage | Pairs scored this stage | Wall | Throughput | Peak process-tree RSS (watchdog, 3 s samples) | Output bytes/pair |
|---|---|---|---|---|---|
| B1 | 10,000 (1 partition) | 2.6 s | 3.8 k/s (cold start dominated) | < 1 sample (run shorter than the 3 s period) | ~18.6 |
| B2 | 90,000 (9 partitions; 100 k cumulative) | 8.7 s | 10.3 k/s | 2.12 GB | ~18.6 |
| B3 | 400,000 (40 partitions; 500,000 cumulative) | 29 s | 13.8 k/s | 1.52 GB | ~18.6 |

Time is linear in pairs (about 0.07 ms/pair at steady state with 10 k partitions; start-up per partition dominates at this small chunk size, which is why production uses 100 k -> 45 k pairs/s). RSS does **not** grow with the number of pairs processed (2.1 GB -> 1.5 GB).

## 2. Full run (chunk_size = 100,000; 87 partitions)

| Phase | Time | Peak RSS | Notes |
|---|---|---|---|
| exact | 35 s | 1.18 GB | 612,782 -> 611,714 groups |
| candidates (view build + generation) | 126-153 s | 1.55 GB (view build); generation 0.1 GB steady | 8,639,518 pairs / 87 partitions; spill = `raw_shards/` (~140 MB, deleted afterwards) |
| features | **187 s** | **1.91 GB process-tree peak**; worker peak 0.50 GB | **45,502 pairs/s** at the end; 8.64 M pairs; 161 MB output |
| score | 3 s | < 0.3 GB | vectorised; 118 MB output |
| family-candidates + tables | 46 s | 1.90 GB | 744,615 kept pairs, 6,589 provisional edges |
| consensus (existing tool) | 67 s | 1.65 GB | |
| audits (existing tool) | 63 s | 2.05 GB (8.6 GB reported "peak memory footprint" counts compressed pages) | |

Process-tree RSS over the features phase (watchdog, 5 s): 1.05 -> 1.11 -> 1.31 -> 0.66 -> 1.25 -> 1.16 -> 1.19 GB -- **flat**; swap used moved 4.9 -> 5.8 GB only because of other tenants. Total spill/temp footprint of the run directory: 633 MB (reps view 320 MB uncompressed + parts 325 MB). Measured against the configured safe limit (4.5 GB) the peak used 42 %.

## 3. Old vs new on the same 1-in-20 sample (30,698 recipes, 201,874 pairs)

| | Old script | New pipeline |
|---|---|---|
| Max RSS | 1.84 GB | 1.02 GB (incl. view build) |
| Peak footprint | 3.30 GB | 1.13 GB |
| Result | 2,850 kept pairs, 11 family edges, 30,687 families | **identical**: same pair set, `max |delta|` = 0.0 on all 12 score components and the final score, 0 edge/mask/hint mismatches, same duplicate group ids, same family ids and roles |

Projected old-design cost at 8.64 M pairs: > 8 GB (see `identity_failure_analysis.md`). New design: 1.9 GB measured.

## 4. Recovery and reproducibility (real runs on the full data)

| Test | Result |
|---|---|
| Clean second `--phase all --resume` | exact / candidates / 87 features / 87 score partitions all **skipped as valid**; 0 pairs rescored; identical `final_hash` `963466d8f207...` |
| `SIGKILL` of the whole process tree mid-features (25 files on disk, 24 recorded DONE) | no `.tmp` files left; resume skipped 24, recomputed 63; final hashes of all five identity tables **identical** to the uninterrupted run |
| Memory guard (`--max-memory-gb 0.3`) | workers abort their partition without leaving output; process exits with code **75 (MEMORY_GUARD_TRIGGERED)**; rerun with `--resume` exits 0 |
| Unit tests (`tests/unit/test_identity_pipeline.py`) | 11 pass: resume after interruption, truncated partition, missing partition, input-hash change, atomic write, deterministic scoring, chunk bound, pair uniqueness, exact-group order independence, star clustering has no chaining, Gold/licence/provenance preserved, vectorised score == scalar score |
