#!/usr/bin/env python3
"""Step 08a.8 driver: blind edge-audit packets (B2, B3, STRONG; 50 each) and the 200 unlinked-pair recall packets.

  python tools/step08a_audit_packets.py --edges exports/lineage/step08a_v1/edge_candidates.jsonl --out-dir annotation/lineage_audit

Reads EVD and the edge candidates; writes only under --out-dir (per-reviewer blind files plus a sealed key). Never
fills a judgement column. Blocking for the unlinked pairs = same normalised analyte and matrix tokens (the B3 block).
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from culinarystate.lineage import audit_packet as ap_  # noqa: E402
from culinarystate.lineage import detectors as det  # noqa: E402

SEED = 20261027


def _load_active_evd(path: Path) -> dict[str, dict]:
    latest: dict[str, dict] = {}
    for line in path.open(encoding="utf-8"):
        if line.strip():
            r = json.loads(line)
            latest[r["id"]] = r
    return {k: v for k, v in latest.items() if v.get("status", "ACTIVE") == "ACTIVE"}


def summary(it: dict) -> str:
    vals = "; ".join(f"{v['role']}={v['value']:g} {v['unit']}" for v in it["values"]) or "no numeric value"
    return (f"source={it['source_id']} | ref={it['doc_ref'] or 'none'} | locator={it['locator'] or 'none'} | "
            f"analyte={it['analyte']} | matrix={it['matrix']} | process={it['process']} | {vals}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--edges", required=True, type=Path)
    ap.add_argument("--out-dir", required=True, type=Path)
    ap.add_argument("--evd", type=Path, default=ROOT / "ledgers" / "data" / "EVD.jsonl")
    a = ap.parse_args()
    items = {r["id"]: det.item_from_evd(r) for r in _load_active_evd(a.evd).values()}
    edges = [json.loads(l) for l in a.edges.read_text().splitlines() if l.strip()]
    for e in edges:
        e["edge_id"] = e["edge_key"]
        e["from_summary"], e["to_summary"] = summary(items[e["from_id"]]), summary(items[e["to_id"]])
    res = ap_.build_edge_audit_packets(edges, SEED, a.out_dir, "edge_audit_v1")

    blocks: dict[tuple, list[str]] = defaultdict(list)
    for i, it in items.items():
        blocks[(det.normalise_text(it["analyte"]), tuple(sorted(set(det._matrix_tokens(it["matrix"])))))].append(i)
    blocked = (p for g in blocks.values() if len(g) > 1 for p in itertools.combinations(sorted(g), 2))
    pairs = ap_.draw_unlinked_pairs(blocked, ((e["from_id"], e["to_id"]) for e in edges), SEED)
    mp = [{"pair_id": f"{x}|{y}", "from_id": x, "to_id": y, "from_summary": summary(items[x]),
           "to_summary": summary(items[y])} for x, y in pairs]
    res2 = ap_.build_missed_pair_packets(mp, SEED, a.out_dir, "missed_pair_v1")
    print(json.dumps({"edge": res, "missed_pairs": {"n": len(mp), **{k: v for k, v in res2.items() if k != "items"}}},
                     indent=2, default=str)[:3000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
