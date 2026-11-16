#!/usr/bin/env python
"""S179 (T3-C17-R2): per-event-type counts, rule compiler (level P) vs the P1 gold and the 40 dev-gold recipes, with
recipe-cluster bootstrap intervals. Counts only; Mac only (BBC gold, D-003); refuses to overwrite. NOT INDEPENDENT.

    /opt/anaconda3/bin/python tools/s179_event_type_table.py
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))
from culinarystate.evaluation import compiler_vs_gold_pooled as P  # noqa: E402
from s179_compiler_vs_gold_pooled import SETS, load_docs, set_digest  # noqa: E402

TOOL_VERSION = "s179-event-type-table-0.1.0"
OUT = ROOT / "reports" / "del3" / "event_type_table_S179.json"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(OUT))
    ap.add_argument("--n-boot", type=int, default=2000)
    a = ap.parse_args()
    out = Path(a.out)
    if out.exists():
        sys.exit(f"refusing to overwrite {out}")
    reg = {r["canonical_name"] for r in csv.DictReader(
        (ROOT / "registry" / "ingredients" / "ingredient_registry_v1.csv").open(newline=""))}
    result = {"record": "S179_EVENT_TYPE_TABLE", "tool_version": TOOL_VERSION, "status": "AI_DIAGNOSTIC_COUNTS_ONLY",
              "not_independent": True, "sets": {}}
    for name, folder, pattern, basis in SETS:
        paths = sorted(folder.glob(pattern))
        if not paths:
            sys.exit(f"INPUT_MISSING: {name} ({folder})")
        t = P.type_table(load_docs(paths), reg, label_basis=basis, n_boot=a.n_boot, seed=f"s179-type-table-{name}")
        t["input_set_sha256"] = set_digest(paths)
        result["sets"][name] = t
    with out.open("x") as f:
        f.write(json.dumps(result, indent=1, sort_keys=True) + "\n")
    print("wrote", out.relative_to(ROOT), hashlib.sha256(out.read_bytes()).hexdigest())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
