#!/usr/bin/env python3
"""Step 08a real run: publish a verified scratch rebuild (from step08a_gate.py) into the real ledgers.

  python tools/step08a_publish.py --rebuild <scratch-root>/rebuild_1 [--apply]

Without --apply it only prints the plan. Writes: new ledger files, appends to STUDY.jsonl and _ids.jsonl (D-032);
lineage outputs go to exports/lineage/step08a_v1/ (new files).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from culinarystate.lineage import guard, publish  # noqa: E402

BASELINE = ROOT / "registry" / "baseline_ledger_hashes_08a_v1.csv"
REAL = ROOT / "ledgers" / "data"
OUT = ROOT / "exports" / "lineage" / "step08a_v1"
OUTPUTS = {"edges/edge_candidates.jsonl": "edge_candidates.jsonl", "edges/edge_counts.json": "edge_counts.json",
           "keys/keys.jsonl": "keys.jsonl", "keys/counts.json": "keys_counts.json",
           "feas/feasibility.json": "feasibility.json", "feas/feasibility_report.txt": "feasibility_report.txt",
           "export_v2/evd_export_v2.jsonl": "evd_export_v2.jsonl",
           "export_v2/evd_export_v2.manifest.json": "evd_export_v2.manifest.json",
           "docs_counts.json": "docs_counts.json"}


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--rebuild", required=True, type=Path)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    scratch = a.rebuild.resolve() / "led" / "data"
    print("baseline verified (before):", guard.verify_baseline(BASELINE, ROOT), "files")
    plan = publish.plan_publish(REAL, scratch)
    print(json.dumps(plan, indent=2))
    if not a.apply:
        return 0
    if OUT.exists():
        raise SystemExit(f"refused: {OUT} exists")
    publish.apply_publish(REAL, scratch, plan)
    for name in plan["new"] + plan["append"]:
        if _sha(REAL / name) != _sha(scratch / name):
            raise SystemExit(f"MISMATCH after publish: {name}")
    OUT.mkdir(parents=True)
    for rel, dest in OUTPUTS.items():
        shutil.copy2(a.rebuild / rel, OUT / dest)
    manifest = {n: {"sha256": _sha(OUT / n), "bytes": (OUT / n).stat().st_size} for n in sorted(p.name for p in OUT.iterdir())}
    for n in plan["new"] + plan["append"]:
        manifest[f"ledgers/data/{n}"] = {"sha256": _sha(REAL / n), "bytes": (REAL / n).stat().st_size}
    (OUT / "freeze_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print("published; ledgers now match scratch for", plan)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
