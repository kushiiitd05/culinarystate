#!/usr/bin/env python3
"""STEP 07I-R: phased, resumable, memory-bounded recipe identity pipeline (supersedes the single-shot 07I part-3 script, which stalled at 8.6M candidate pairs).
  python tools/step07i_identity.py --phase all --resume [--chunk-size 150000] [--threads 3] [--max-memory-gb 4.5]
phases: audit | exact | candidates | features | score | family-candidates | review-sample | statistics | all
--sample N : deterministic 1-in-N recipe subset (run name 'sample'); --run-name X : separate work dir + manifest (benchmarks); --max-pairs K : truncate candidate set (benchmarks only)
--partition PID : run a single partition ; --dry-run : report what would run ; exit code 75 = MEMORY_GUARD_TRIGGERED (checkpoint written; rerun with --resume)."""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.identity.pipeline import MemoryGuardExit, Run  # noqa: E402

PHASES = ["audit", "exact", "candidates", "features", "score", "family-candidates"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", default="all")
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--chunk-size", type=int, default=150_000)
    ap.add_argument("--partition", default=None)
    ap.add_argument("--max-memory-gb", type=float, default=4.5)
    ap.add_argument("--threads", type=int, default=3)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--max-pairs", type=int, default=0)
    ap.add_argument("--sample", type=int, default=0)
    ap.add_argument("--run-name", default=None)
    ap.add_argument("--n-buckets", type=int, default=128)
    ap.add_argument("--max-partitions", type=int, default=0, help="run at most K pending partitions this invocation (benchmarks / staged runs)")
    ap.add_argument("--watch-period", type=float, default=10.0)
    a = ap.parse_args()
    name = a.run_name or ("sample" if a.sample else "main")
    r = Run(ROOT, name, a.sample, a.chunk_size, a.n_buckets, a.max_memory_gb, a.threads, a.max_pairs, log=lambda s: print(s, flush=True))
    r.watch_period = a.watch_period
    todo = PHASES if a.phase == "all" else [a.phase]
    try:
        for ph in todo:
            if ph == "audit":
                print("audit:", r.audit()["verdict"])
            elif ph == "exact":
                r.exact(a.resume)
            elif ph == "candidates":
                r.candidates(a.resume, a.dry_run)
            elif ph == "features":
                r.features(a.resume, a.partition, a.dry_run, a.max_partitions)
            elif ph == "score":
                r.score(a.resume, a.partition, a.dry_run, a.max_partitions)
            elif ph == "family-candidates":
                r.family()
            elif ph == "review-sample":
                subprocess.check_call([sys.executable, str(ROOT / "tools/step07i_review_packet.py")])
            elif ph == "statistics":
                flag = ["--sample"] if name == "sample" else []
                for t in ("step07i_consensus.py", "step07i_audits.py", "step07i_final_stats.py"):
                    subprocess.check_call([sys.executable, str(ROOT / "tools" / t)] + (flag if t == "step07i_consensus.py" else []))
            else:
                ap.error("unknown phase " + ph)
    except MemoryGuardExit as e:
        sys.exit(int(e.code))
    finally:
        r.man.save()


if __name__ == "__main__":
    main()
