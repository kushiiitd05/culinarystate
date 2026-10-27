#!/usr/bin/env python3
"""Step 08a.9: two independent scratch rebuilds, gate report (G08-1..10) and freeze manifest.

  python tools/step08a_gate.py --scratch-root <dir outside the repo> [--report-dir reports/step08]

Each rebuild copies the real ledgers/data into <scratch-root>/rebuild_N/led/data, runs docs/studies, edges, keys,
feasibility and export v2 there, and compares the two runs byte for byte (G08-6). The real ledgers are only read.
The gate report is written to <scratch-root>/gate and, with --report-dir, copied to the repo.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from culinarystate.lineage import detectors, gates, guard, seeding  # noqa: E402

SEED = detectors.CUT_DETERMINATION_SEED
BASELINE = ROOT / "registry" / "baseline_ledger_hashes_08a_v1.csv"


def _run(*args: object) -> None:
    subprocess.run([sys.executable, *map(str, args)], check=True, cwd=ROOT, stdout=subprocess.DEVNULL)


def rebuild(scratch: Path, n: int) -> dict[str, Path]:
    base = scratch / f"rebuild_{n}"
    if base.exists():
        shutil.rmtree(base)
    led = base / "led"
    shutil.copytree(ROOT / "ledgers" / "data", led / "data")
    t = ROOT / "tools"
    sr = ["--scratch-root", scratch]
    _run(t / "step08a_build_docs.py", "--ledgers-root", led, "--out", base / "docs_counts.json")
    _run(t / "step08a_detect_edges.py", "--ledgers-root", led, "--out-dir", base / "edges", *sr)
    _run(t / "step08a_build_keys.py", "--ledgers-root", led, "--edges", base / "edges" / "edge_candidates.jsonl",
         "--out-dir", base / "keys", *sr)
    _run(t / "step08a_feasibility.py", "--ledgers-root", led, "--keys", base / "keys" / "keys.jsonl",
         "--out-dir", base / "feas", *sr)
    _run(t / "step08a_export_v2.py", "--ledgers", led, "--keys", base / "keys" / "keys.jsonl", "--out", base / "export_v2")
    return {"DOC.jsonl": led / "data" / "DOC.jsonl", "STUDY.jsonl": led / "data" / "STUDY.jsonl",
            "_ids.jsonl": led / "data" / "_ids.jsonl", "edge_candidates.jsonl": base / "edges" / "edge_candidates.jsonl",
            "keys.jsonl": base / "keys" / "keys.jsonl", "feasibility.json": base / "feas" / "feasibility.json",
            "evd_export_v2.jsonl": base / "export_v2" / "evd_export_v2.jsonl"}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--scratch-root", required=True, type=Path)
    ap.add_argument("--report-dir", type=Path, default=None)
    a = ap.parse_args()
    scratch = a.scratch_root.resolve()
    if ROOT in scratch.parents or scratch == ROOT:
        raise SystemExit("refused: scratch root must be outside the repo")
    guard.verify_baseline(BASELINE, ROOT)
    r1, r2 = rebuild(scratch, 1), rebuild(scratch, 2)
    guard.verify_baseline(BASELINE, ROOT)
    out = scratch / "gate"
    out.mkdir(parents=True, exist_ok=True)
    keys_counts = json.loads((r1["keys.jsonl"].parent / "counts.json").read_text())
    docs_counts = json.loads((r1["keys.jsonl"].parent.parent / "docs_counts.json").read_text())
    export_man = json.loads((r1["evd_export_v2.jsonl"].parent / "evd_export_v2.manifest.json").read_text())
    seeded = seeding.seeded_recall(seeding.generate_seeded_pairs(SEED, 100), detectors.record_b3_detects)
    overlap = json.loads((ROOT / "reports" / "step08" / "usda_bognar_overlap_v1.json").read_text())
    feas = json.loads(r1["feasibility.json"].read_text())
    report = gates.build_gate_report(
        keys_counts=keys_counts, seeded=seeded, feasibility=feas,
        largest_share=keys_counts["largest_split_group_share"], overlap=overlap,
        baseline_after=docs_counts["baseline_after"],
        export_v1_identical=bool(export_man["committed_v1"].get("v1_columns_identical_to_committed_v1")),
        rebuild=gates.compare_runs(r1, r2))
    report["step"] = "08a.9"
    report["scratch_only"] = True
    report["rule_version"] = keys_counts["rule_version"]
    manifest = {"outputs": gates.freeze_manifest(r1),
                "real_ledgers_verified": guard.verify_baseline(BASELINE, ROOT), "baseline_csv": str(BASELINE.relative_to(ROOT))}
    (out / "gate_report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    (out / "freeze_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    if a.report_dir:
        a.report_dir.mkdir(parents=True, exist_ok=True)
        for n in ("gate_report.json", "freeze_manifest.json"):
            shutil.copy2(out / n, a.report_dir / f"step08a_scratch_{n}")
    print(json.dumps({"overall": report["overall"], **{k: v["status"] for k, v in report["gates"].items()}}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
