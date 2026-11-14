#!/usr/bin/env python3
"""D-110: merge sharded state-dataset fill outputs into one fill-rate table (counts summed; rates recomputed)."""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path


def merge(parts: list[dict]) -> dict:
    fill = defaultdict(lambda: defaultdict(Counter))
    heat = defaultdict(lambda: defaultdict(Counter))
    tot = Counter()
    joined = Counter()
    for p in parts:
        for k in ("recipes", "rows", "exceptions"):
            tot[k] += p[k]
        joined.update(p.get("heat_rows_joined_to_physics", {}))
        for fam, cols in p["fill_by_basis_or_reason"].items():
            for col, cnt in cols.items():
                fill[fam][col].update(cnt)
    rate = {fam: {col: round(100 * sum(v for k, v in c.items() if k.startswith("VALUE:")) / max(1, sum(c.values())), 2)
                  for col, c in cols.items()} for fam, cols in fill.items()}
    return {"recipes": tot["recipes"], "rows": tot["rows"], "exceptions": tot["exceptions"],
            "heat_rows_joined_to_physics": dict(joined), "value_rate_pct": rate,
            "fill_by_basis_or_reason": {f: {c: dict(v) for c, v in cols.items()} for f, cols in fill.items()},
            "shards": sorted(p.get("shard", "0/1") for p in parts)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("parts", nargs="+")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    out = Path(a.out)
    if out.exists():
        sys.exit(f"refusing to overwrite {out}")
    parts = [json.loads(Path(p).read_text()) for p in a.parts]
    m = merge(parts)
    m.update({"record": "STATE_DATASET_FILL_MERGED", "decision": "D-110", "labels": parts[0]["labels"],
              "columns": parts[0]["columns"], "approver": "ksh+prv (AI, D-085)", "contains_text": False, "contains_ids": False,
              "scientific_gate_pass": False})
    out.write_text(json.dumps(m, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: m[k] for k in ("recipes", "rows", "exceptions")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
