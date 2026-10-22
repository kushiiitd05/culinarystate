# STEP 07I-R -- failure analysis of the stalled identity run

Script analysed: `tools/step07i_identity.py` at commit `6acd578` (+ one uncommitted `keep`-rule edit, reconstructed byte-for-byte for the equivalence test). Line numbers below refer to that version.

## 1. What happened (facts, with provenance)

| Fact | Evidence |
|---|---|
| 612,782 recipes -> 611,714 exact-dedup representatives, **8,639,518 candidate pairs generated in 76-92 s** | printed by the dead run; transcript `0fa2d4c7...jsonl` 2026-10-22T06:49-06:56Z; reproduced exactly by the new pipeline (8,639,518; per source: title 678,114 / steps-LSH 58,612 / ingredient-LSH 7,940,499 / REC-family 716) |
| The pair-scoring stage was then running for **25 min 37 s** with a `Pool(4)` of forked workers when PID 5611 was killed by hand | transcript 07:07 UTC (`ps -o etime`: `25:37`) |
| At the moment of the kill the machine had **4,324 free 16 KB pages (~69 MB)** | `vm_stat` in the same transcript |
| Swap was saturated at the first check after reboot: 5.1 of 5.4 GB used, `sin` = 97 GB cumulative | `psutil.swap_memory()` this session |
| `/tmp/step07i_identity.log` is gone (reboot) | `ls` |
| No kernel/OOM record exists | macOS does not log a per-process OOM kill for a user process; absence of evidence is not evidence of absence |

## 2. Expected vs observed time

The scoring work itself is cheap. On the 1-in-20 sample the old script scored 201,874 pairs in ~5 s (4 workers). The new, memory-bounded implementation scores **all 8,639,518 pairs in 187 s with 3 workers (45 k pairs/s)** and the vectorised score step takes 3 s. A healthy run of the old design would therefore have finished in roughly 3-6 minutes. It ran for 25 minutes without printing `features done`. The runtime was dominated by something other than arithmetic: paging.

## 3. Memory complexity of the old design (read in full)

Everything below is O(P), P = number of candidate pairs (8.64 M), held as **Python objects** in one parent process:

| Lines | Structure | Per-pair cost (CPython) | At P = 8.64 M |
|---|---|---|---|
| 168-173 | `cand = defaultdict(int)` keyed by `i*N+j` | ~100-130 B (dict slot + int key + int value) | ~1.0 GB |
| 251 | `items = [(i, j, mask) ... sorted(cand.items())]` | ~100 B (tuple + 3 ints) + the temporary sorted `(key,mask)` list | ~1.0-2.0 GB |
| 252 | `chunks = [items[k:k+4000] ...]` (second list of references, `items` kept alive) | ~8 B | 0.07 GB |
| 51-57, 254-258 | `pair_worker` returns **every** pair as `(i, j, mask, keep, f)` with the full feature dict `f` (~22 keys) pickled through the pool pipe; `pool.imap` buffers results when the parent consumes slower than 4 workers produce | ~1.2-1.5 KB per pair in flight | unbounded in principle (up to ~10 GB if the parent lags) |
| 259 | `kept.append((i, j, mask, f))` retains the dicts of kept pairs | ~1.3 KB per kept pair | 0.3-1 GB |
| 324-330 | `pr = [dict ...]` then `pd.DataFrame(pr)` (second copy) | ~1.5 KB per kept pair | 0.5-1.5 GB |
| 60-76 `load` | `pq.read_table(...).to_pandas()` on `list<string>` columns turns every list into a Python list of Python strs; measured 1.04 GB RSS for the features alone, plus per-recipe `frozenset`/`dict`/`tuple` copies in `Store` (lines 144-166, 167) | per recipe ~3-4 KB | 2-3 GB |
| 254 | `mp.get_context("fork").Pool(4)` | CPython refcount writes defeat copy-on-write: each worker progressively privatises the parent's `Store` | up to 4 x store |
| 331-332 | `df.to_pickle` / `reps.to_pickle` of 612k-row frames with object columns | transient copy | ~1 GB |

Measured scaling of the old script (same machine, `/usr/bin/time -l`):

| Run | Recipes | Candidate pairs | Max RSS | Peak footprint |
|---|---|---|---|---|
| sample 1/20 | 30,698 | 201,874 | 1.84 GB | 3.30 GB |
| sample 1/10 | 61,367 | 513,624 | 2.48 GB | 3.62 GB |
| full | 612,782 | 8,639,518 | not completed | (>> 8 GB physical, 5.4 GB swap) |

The candidate count grows super-linearly with the corpus (x2 recipes -> x2.5 pairs; x20 -> x42.8), and the footprint is already 3.3-3.6 GB at 1/10 of the data on a machine whose practical working set is ~4-5 GB.

## 4. Verdict

**LIKELY_MEMORY_PRESSURE and LIKELY_SWAP_THRASHING.** Not proven OOM: there is no kernel record and the process was killed by hand, so "OOM" is *not* claimed.

Reasons: (i) candidate generation (cheap, pure numpy/Python) finished in 76-92 s while the stage that does only ~5 s of work per 200 k pairs ran 25 min; (ii) free memory was ~69 MB and swap was saturated; (iii) the old design keeps several O(P) Python-object structures plus the per-pair result dicts through a forked pool; (iv) the same code finishes in seconds on a sample whose pair count fits in RAM.

Ruled out: LIKELY_ALGORITHMIC_STALL (no loop depends on P^2; title blocks are capped at 60, LSH buckets at 200/50); LIKELY_SINGLE_THREAD_CPU_BOUND (4 workers were active and the arithmetic budget is ~4 min).
Not excluded: a contributing contribution from machine-wide contention (browsers, Spotify etc. were resident); this does not change the redesign.

## 5. Redesigned complexity

| Aspect | Old | New (`src/culinarystate/identity/*`) |
|---|---|---|
| Pairs in memory | all P as Python objects | a numpy `int64` key array for ONE spill bucket at a time (candidate de-dup) and ONE partition (<= `chunk_size` rows) per worker |
| Candidate generation | dict + sorted list | each generator emits `int64` key shards bucketed by the smaller index (disk), per-bucket `argsort` + `bitwise_or.reduceat`, then fixed-size input partitions |
| Per-recipe data | pandas object columns + per-row Python sets for all 611,714 recipes in every process | one integer-encoded Arrow view written **uncompressed** and memory-mapped (shared, evictable page cache); a worker materialises only the representatives its partition touches |
| Workers | forked, inherit parent heap, return every pair | `spawn` workers (nothing inherited); a worker returns a 200-byte status dict and writes its own output atomically |
| Output | one giant list -> DataFrame | per-partition parquet (components, then scores), the kept subset (<= 8.6 %) is joined once at the end |
| Failure | restart from zero | manifest of per-partition input hash / row count / content hash; resume skips only partitions that re-validate; `MEMORY_GUARD_TRIGGERED` (exit 75) checkpoints and stops |
| Peak memory | O(P) objects (> 8 GB projected) | O(chunk_size) per worker + O(N) compact arrays; **measured peak process-tree RSS 1.91 GB for the whole 8.64 M-pair run** |

See `identity_benchmark_report.md` for the measurements and `tests/unit/test_identity_pipeline.py` for the behavioural tests.
