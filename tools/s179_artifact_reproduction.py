#!/usr/bin/env python3
"""Reproduce two recorded census runs and deterministic D5 template components.

No model call, scoring, tuning, frozen-file mutation or scientific rerun.
"""
from __future__ import annotations
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
METADATA = {"code_provenance", "code_unchanged_during_run", "records_written"}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def compare(old, new):
    keys = old.keys() | new.keys()
    differences = sorted(k for k in keys if old.get(k) != new.get(k))
    return {"raw_json_equal": old == new, "metrics_equal": all(k in METADATA for k in differences),
            "metric_difference_keys": [k for k in differences if k not in METADATA],
            "metadata_difference_keys": [k for k in differences if k in METADATA],
            "old_core_sha256": digest({k: v for k, v in old.items() if k not in METADATA}),
            "new_core_sha256": digest({k: v for k, v in new.items() if k not in METADATA})}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.out_dir.exists():
        parser.error("new output directory required")
    args.out_dir.mkdir(parents=True)
    started = datetime.now(timezone.utc).isoformat()
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    producer = {str(p.relative_to(ROOT)): sha(p) for p in ROOT.glob("src/**/*.py")}
    producer[str(Path(__file__).relative_to(ROOT))] = sha(__file__)
    jobs = [
        ("RUN-S179-ROUTER-005", "reports/step23/router_demo_census_vitc_nonBBC_1000_S179b.json", "router.json",
         ["tools/router_demo_census.py", "--seed", "20261104", "--sample-size", "1000", "--workers", "2", "--families", "WIKIBOOKS", "GUTENBERG_SEGMENT", "FOODCOM", "TASTESET", "--gates", "on"]),
        ("RUN-S179-PHYS6-004", "reports/step26/binding_census_L1_WIKIBOOKS_full_S179_v06.json", "binding_wikibooks.json",
         ["tools/binding_census.py", "--seed", "20261104", "--sample-size", "600000", "--workers", "2", "--families", "WIKIBOOKS",
          "--records-dir", "data/derived/" + args.out_dir.name + "_WIKIBOOKS"])]
    results = []
    for run_id, original, name, command in jobs:
        new_path = args.out_dir / name
        command = [sys.executable] + command + ["--out", str(new_path)]
        stamp = datetime.now(timezone.utc).isoformat()
        done = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
        result = {"original_run_id": run_id, "original_artifact": original, "original_sha256": sha(ROOT / original),
                  "new_artifact": str(new_path), "command": command, "started_at_utc": stamp,
                  "completed_at_utc": datetime.now(timezone.utc).isoformat(), "exit_code": done.returncode}
        if done.returncode == 0:
            result.update(compare(json.loads((ROOT / original).read_text()), json.loads(new_path.read_text())))
            result["new_sha256"] = sha(new_path)
        else:
            result["status"] = "FAILED_RUN_REVIEW_REQUIRED"
            result["stderr_sha256"] = hashlib.sha256(done.stderr.encode()).hexdigest()
        results.append(result)
        print(run_id, result.get("metrics_equal", "FAILED"), flush=True)
    # Recreate only deterministic template text; never invoke the frozen scorer or LLM.
    from culinarystate.decision.demo_context import DemoContext
    from culinarystate.decision.pipeline import answer
    from culinarystate.generation.verbalize import verbalize
    ctx = DemoContext.load(public=False, host="127.0.0.1")
    stored_path = ROOT / "reports/del5/d5_runs_v1_D085.jsonl"
    stored = {(r["qid"], r["rung"]): r for r in map(json.loads, stored_path.read_text().splitlines())}
    questions = list(csv.DictReader((ROOT / "benchmark/d5/d5_benchmark_v1_D085_PC.csv").open()))
    checks = []
    for row in questions:
        result = answer(row["question"], ctx.lex, ctx.retriever, ctx.req, ctx.family, support_index=ctx.sup, troubleshoot=ctx.ts)
        rendered = verbalize(row["question"], result["decision"], result["packets"])
        original = stored[(row["qid"], "B5T")]["answer"]
        checks.append({"qid": row["qid"], "rung": "B5T", "text_equal": rendered == original,
                       "original_sha256": hashlib.sha256(original.encode()).hexdigest(),
                       "new_sha256": hashlib.sha256(rendered.encode()).hexdigest()})
    if producer != {p: sha(ROOT / p) for p in producer} or head != subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip():
        raise RuntimeError("source/commit changed during reproduction")
    report = {"record": "LOCAL_ARTIFACT_REPRODUCTION", "started_at_utc": started,
              "completed_at_utc": datetime.now(timezone.utc).isoformat(), "base_commit": head,
              "source_sha256": producer, "source_and_commit_unchanged": True, "census_reruns": results,
              "deterministic_D5_component": {"original_run_id": "RUN-S179-D5-001", "rung": "B5T", "questions": len(checks),
                                             "exact_text_matches": sum(c["text_equal"] for c in checks), "checks": checks,
                                             "stored_run_sha256": sha(stored_path)},
              "labels": ["ENGINEERING_DIAGNOSTIC", "NON_CITABLE", "NO_HUMAN_SIGNOFF_D085"], "scientific_gate_pass": False,
              "limitations": ["New code/commit provenance and omitted per-event raw record export explain full-file differences; every metric difference remains listed.",
                              "D5 B5T P/C text only; H1 LLM outputs and B7 generator/enforcement inputs are not regenerated.",
                              "No rescore or new hypothesis test. Original frozen outputs and failed H1/H3 remain unchanged.",
                              "This does not impersonate the scheduled post-19-Nov/server rerun; work ran locally on 12 November."]}
    with (args.out_dir / "comparison.json").open("x") as handle:
        handle.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print("D5 B5T exact", report["deterministic_D5_component"]["exact_text_matches"], "/", len(checks))


if __name__ == "__main__":
    main()
