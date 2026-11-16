#!/usr/bin/env python3
"""D-100 Lane C / plan L4: full-corpus process x ingredient x target effect map for all ACTIVE EVD targets.

Unchanged router (`router_demo.route_text`) per recipe and target, with the parity-tested grouping of
s179_all_target_router_v2 (targets with no ING/PROC source hit and no presence screen share one evaluation).
Tallies, counts only: per target route/reason counts; per (target, ingredient, process) DIRECT items by EVD id
(EVD values are looked up from the ledger at the end, so the map carries evidence values, not text).
BBC only on the Mac (D-003). Refuses to overwrite.

    python tools/s179_effect_map_224.py --families FOODCOM WIKIBOOKS GUTENBERG_SEGMENT TASTESET --workers 120 \
        --out reports/s179/effect_map_224_nonBBC_2026-11-13.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import sys
import time
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))

TOOL_VERSION = "s179-effect-map-224-0.1.0"
LABELS = ["DIAGNOSTIC", "E3_AI_PRECHECKED_EVIDENCE", "NON_CITABLE", "NO_HUMAN_SIGNOFF_D085"]
_S: dict = {}


def _init() -> None:
    from culinarystate.ledgers.store import LedgerStore
    from culinarystate.extraction.rung_a import RungA
    from culinarystate.mechanism import router_demo as RD, evidence_gates as EG, process_signatures as PS
    from culinarystate.quantity import rc2_dryrun as D
    from culinarystate.recipes.ledgers import LOCALE
    import s179_all_target_router_v2 as V2
    evd = LedgerStore().all_latest("EVD")
    targets = sorted({r["target"]["state_variable_id"] for r in evd
                      if r["status"] == "ACTIVE" and r.get("target", {}).get("state_variable_id")})
    _S.update(RD=RD, V2=V2, LOCALE=LOCALE, targets=targets, index=RD.EvidenceIndex.from_rows(evd),
              gates=EG.EvidenceGates.load(), hierarchy=PS.read_process_hierarchy(), schema=D.load_schema(), rung=RungA())


def _empty() -> dict:
    return {"recipes": Counter(), "no_steps": Counter(), "exceptions": Counter(),
            "route": defaultdict(Counter), "reason": defaultdict(Counter), "items": Counter(),
            "recipes_with_direct": Counter(), "direct": defaultdict(Counter)}


def tally(records) -> dict:
    if not _S:
        _init()
    RD, V2, t = _S["RD"], _S["V2"], _empty()
    targets = _S["targets"]
    for rec in records:
        fam = rec.get("source_family", "UNKNOWN")
        t["recipes"][fam] += 1
        raw = "\n".join(str(s) for s in (rec.get("steps") or []))
        if not raw.strip():
            t["no_steps"][fam] += 1
            continue
        try:
            cached = V2.CachedRung(_S["rung"])

            def route(target):
                return RD.route_text(raw, index=_S["index"], target_svar=target, locale=_S["LOCALE"].get(fam), rung=cached,
                                     hierarchy=_S["hierarchy"], schema=_S["schema"], gates=_S["gates"],
                                     ingredient_lines=rec.get("ingredient_lines"))
            first = route(targets[0])
            pairs = {(i["ingredient_id"], i["process_id"]) for i in first["items"]}
            specific, generic = V2.partition_targets(targets, pairs, _S["index"], _S["gates"])
            outs = {targets[0]: first}
            shared = None
            if generic:
                rep = generic[0]
                shared = outs.get(rep) or route(rep)
            for tg in specific:
                if tg not in outs:
                    outs[tg] = route(tg)
            for tg in targets:
                o = outs.get(tg) or shared
                if o is None:
                    continue
                items = o["items"]
                t["items"][tg] += len(items)
                has_direct = False
                for it in items:
                    t["route"][tg][it["route"]] += 1
                    t["reason"][tg].update(it["reasons"])
                    if it["route"] == "DIRECT" and tg in outs:          # DIRECT only from a real per-target evaluation
                        has_direct = True
                        for ev in it.get("evidence") or []:
                            t["direct"][f'{tg}|{it["ingredient_id"]}|{it["process_id"]}'][ev["evd_id"]] += 1
                t["recipes_with_direct"][tg] += has_direct
        except Exception:
            t["exceptions"][fam] += 1
    return t


def merge(parts) -> dict:
    out = _empty()
    for p in parts:
        for k in ("recipes", "no_steps", "exceptions", "items", "recipes_with_direct"):
            out[k].update(p[k])
        for k in ("route", "reason", "direct"):
            for a, c in p[k].items():
                out[k][a].update(c)
    return out


def _chunks(it, n):
    buf = []
    for x in it:
        buf.append(x)
        if len(buf) == n:
            yield buf
            buf = []
    if buf:
        yield buf


def effect_rows(direct: dict, evd_by_id: dict) -> list[dict]:
    """One row per (target, ingredient, process): item count, EVD ids, value summary from the ledger."""
    rows = []
    for key, ids in direct.items():
        tg, ing, proc = key.split("|")
        vals = [evd_by_id[e]["value"] for e in ids if isinstance(evd_by_id.get(e, {}).get("value"), (int, float))]
        rows.append({"target": tg, "ingredient_id": ing, "process_id": proc, "direct_items": int(sum(ids.values())),
                     "evd_ids": sorted(ids), "n_evd": len(ids),
                     "value_median": round(statistics.median(vals), 4) if vals else None,
                     "value_min": round(min(vals), 4) if vals else None, "value_max": round(max(vals), 4) if vals else None,
                     "unit": next((evd_by_id[e].get("unit") for e in ids if e in evd_by_id), None)})
    return sorted(rows, key=lambda r: -r["direct_items"])


def main(argv=None) -> int:
    from culinarystate.lotstate import corpus as C
    ap = argparse.ArgumentParser()
    ap.add_argument("--families", nargs="+", required=True)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--chunk", type=int, default=200)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    out = Path(a.out)
    if out.exists():
        sys.exit(f"refusing to overwrite {out}")
    code = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in ROOT.glob("src/**/*.py")}
    t0, start = time.time(), time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    recs = C.stream(tuple(a.families), ROOT)
    if a.limit:
        recs = (r for i, r in enumerate(recs) if i < a.limit)
    with Pool(a.workers, initializer=_init) as pool:
        parts = list(pool.imap_unordered(tally, _chunks(recs, a.chunk)))
    if code != {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in code}:
        sys.exit("source changed during run")
    m = merge(parts)
    from culinarystate.ledgers.store import LedgerStore
    evd_by_id = {}
    for r in LedgerStore().all_latest("EVD"):                       # same field the router reports (router_demo._summary)
        rf = (r.get("derived") or {}).get("retention_factor") or {}
        evd_by_id[r["id"]] = {"value": rf.get("value"), "unit": rf.get("unit")}
    rows = effect_rows(m["direct"], evd_by_id)
    rec = {"record": "EFFECT_MAP_224", "decision": "D-100 Lane C / plan L4", "tool_version": TOOL_VERSION, "labels": LABELS,
           "approver": "ksh+prv (AI, D-085)", "families_requested": a.families, "started_at_utc": start,
           "wall_seconds": round(time.time() - t0, 1), "workers": a.workers, "limit": a.limit or None,
           "code_sha256_digest": hashlib.sha256(json.dumps(code, sort_keys=True).encode()).hexdigest(),
           "recipes_by_family": dict(m["recipes"]), "no_steps": dict(m["no_steps"]), "exceptions": dict(m["exceptions"]),
           "targets": {tg: {"items": m["items"][tg], "recipes_with_direct": m["recipes_with_direct"][tg],
                            "route": dict(m["route"][tg]), "reason": dict(m["reason"][tg])} for tg in sorted(m["items"])},
           "effect_rows": rows, "n_effect_rows": len(rows), "contains_text": False, "contains_ids": False,
           "notes": ["Values are EVD rows (E3, AI_PRECHECKED) matched by the unchanged router; not simulator output.",
                     "DIRECT is counted only from per-target evaluations; grouped no-hit targets contribute counts only."],
           "scientific_gate_pass": False}
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("x") as f:
        f.write(json.dumps(rec, indent=1, sort_keys=True) + "\n")
    print(json.dumps({"recipes": sum(m["recipes"].values()), "effect_rows": len(rows), "exceptions": dict(m["exceptions"])}),
          round(time.time() - t0, 1), "s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
