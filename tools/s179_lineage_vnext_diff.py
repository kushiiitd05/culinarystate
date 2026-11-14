#!/usr/bin/env python3
"""D-132: corpus differential, frozen Rung A (guard on) vs lineage vNext. Counts and ids only (no text).

Per recipe both parsers run; tallies: events, produced lots, vNext flags, recipes whose event/consumes signature
changed, and for heat-family events the C_t v1.2.1 food-context TRUE rates (salt / acid / lipid) in each version.
A seeded sample of changed recipe ids is kept for spot checks. Shard with --shard i/n; merge with --merge.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
HEAT = frozenset({"WET_HEAT", "DRY_HEAT", "FAT_HEAT", "HEAT_GENERAL"})   # COMBINATION excluded (mixes add/season)
AXES = ("salt", "acid", "lipid")


def _setup():
    from culinarystate.composition import context_v12 as CV, state as CS
    from culinarystate.extraction.rung_a import RungA
    from culinarystate.quantity.rc2_dryrun import load_schema
    marks, roles = CS.load_markers_v2(ROOT / "registry/composition_markers_v2.csv")
    fam = {}
    for line in (ROOT / "ledgers/data/PROC.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            fam[r["id"]] = r.get("family")
    return {"old": RungA(coord_food_guard=True), "new": RungA(coord_food_guard=True, lineage_vnext=True),
            "schema": load_schema(), "marks": marks, "roles": roles, "fam": fam,
            "sr": CV.load_sr_composition(ROOT / "registry/ing_sr_composition_v1.csv"), "CS": CS, "CV": CV}


def one(raw, rung, S, acc, tag):
    from culinarystate.extraction.interfaces import SourceText
    out = rung.run(SourceText.from_raw("VD", raw), rung.config(), schema=S["schema"])
    mem = S["CS"].lot_members_v11(out.graph.entities)
    sig = []
    acc[f"{tag}:events"] += len(out.graph.events)
    for e in out.graph.events:
        acc[f"{tag}:produced"] += len(e.produces)
        pid = next((a.value for a in e.attributes if a.field == "proc_id"), None)
        ings = set()
        for c in e.consumes:
            ings |= mem.get(c, (frozenset(), False))[0]
        sig.append((pid, tuple(sorted(ings))))
        if S["fam"].get(pid) not in HEAT:
            continue
        for food in (i for i in ings if not (S["marks"].get(i) and S["roles"].get(i) == "MEDIUM")):
            ctx = S["CV"].context_v12(food, list(e.consumes), mem, S["marks"], S["roles"], S["sr"], medium_type=None)
            acc[f"{tag}:heat_food_events"] += 1
            for a in AXES:
                acc[f"{tag}:{a}_true"] += ctx[f"{a}_present"].get("v") is True
    for f in (out.graph.diagnostics or ()) if tag == "new" else ():
        if str(f).startswith("VNEXT_"):
            acc[f"flag:{f}"] += 1
    return sig, out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--families", nargs="*", default=[])
    ap.add_argument("--shard", default="0/1")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--merge", nargs="*")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    out = Path(a.out)
    if out.exists():
        sys.exit(f"refusing to overwrite {out}")
    if a.merge:
        acc, sample = Counter(), []
        for p in a.merge:
            d = json.loads(Path(p).read_text())
            acc.update(d["counts"])
            sample += d["changed_sample"]
        out.write_text(json.dumps({"parts": len(a.merge), "counts": dict(acc), "contains_text": False,
                                   "changed_sample": sorted(sample)[:200]}, indent=1))
        print(dict(acc))
        return 0
    from culinarystate.lotstate import corpus as C
    S, acc, sample = _setup(), Counter(), []
    si, sn = (int(x) for x in a.shard.split("/"))
    for k, rec in enumerate(C.stream(tuple(a.families), ROOT)):
        if a.limit and k >= a.limit:
            break
        if k % sn != si:
            continue
        raw = "\n".join(str(s) for s in (rec.get("steps") or []))
        if not raw.strip():
            continue
        acc["recipes"] += 1
        try:
            so, _ = one(raw, S["old"], S, acc, "old")
            sn_, onew = one(raw, S["new"], S, acc, "new")
            if so != sn_:
                acc["recipes_changed"] += 1
                h = hashlib.sha256(f"20261114|{rec['recipe_id']}".encode()).hexdigest()
                sample.append(f"{h[:12]}|{rec['recipe_id']}")
        except Exception:
            acc["exceptions"] += 1
    sample = [s.split("|", 1)[1] for s in sorted(sample)[:50]]
    out.write_text(json.dumps({"families": a.families, "shard": a.shard, "counts": dict(acc),
                               "contains_text": False, "changed_sample": sample}))
    print(dict(acc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
