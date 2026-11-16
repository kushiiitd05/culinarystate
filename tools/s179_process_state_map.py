#!/usr/bin/env python
"""D-100 Lane T: which state change (D-097 type) each process causes, and where in the recipe it happens.

Runs Rung A on every recipe's steps (families present on the host; BBC only on the Mac, D-003) and tallies, counts only:
  by_family[family][type], proc_type[PROC][type], proc_family_type[PROC family][type],
  position_type[step-position decile][type], position_proc_family[decile][family],
  type_bigrams["A>B"], proc_family_bigrams["A>B"] (consecutive events within a recipe).
Types: D-097 structural mapping (Merge / Split / Transform / Discard / UNMAPPED). No text, no recipe ids.

    python tools/s179_process_state_map.py --families FOODCOM WIKIBOOKS GUTENBERG_SEGMENT TASTESET \
        --workers 100 --out reports/s179/process_state_map_nonBBC_2026-11-13.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.evaluation.runga_typed_vs_gold import map_event  # noqa: E402

TOOL_VERSION = "s179-process-state-map-0.1.0"
LABELS = ["DIAGNOSTIC", "D-097_STRUCTURAL_TYPES", "NON_CITABLE", "NO_HUMAN_SIGNOFF_D085"]
_RUNG = None
_GUARD = False
_PROC_FAMILY: dict = {}


def _init(guard: bool = False) -> None:
    global _RUNG, _SCHEMA, _GUARD
    _GUARD = guard
    from culinarystate.extraction.rung_a import RungA
    from culinarystate.quantity.rc2_dryrun import load_schema
    _RUNG, _SCHEMA = RungA(coord_food_guard=guard), load_schema()
    if not _PROC_FAMILY:
        for line in (ROOT / "ledgers/data/PROC.jsonl").read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                _PROC_FAMILY[r["id"]] = r.get("family") or "UNSPECIFIED"


def decile(i: int, n: int) -> int:
    return min(9, (10 * i) // max(n, 1))


def _empty() -> dict:
    return {"n_recipes": 0, "n_events": 0, "exceptions": 0, "recipes_without_events": 0, "coord_food_guard_triggers": 0,
            "recipes_with_guard_trigger": 0,
            "by_family": defaultdict(Counter), "proc_type": defaultdict(Counter),
            "proc_family_type": defaultdict(Counter), "position_type": defaultdict(Counter),
            "position_proc_family": defaultdict(Counter), "type_bigrams": Counter(), "proc_family_bigrams": Counter()}


def tally_records(records) -> dict:
    if _RUNG is None:
        _init()
    from culinarystate.extraction.interfaces import SourceText
    t = _empty()
    for rec in records:
        t["n_recipes"] += 1
        fam = rec.get("source_family", "UNKNOWN")
        try:
            raw = "\n".join(str(s) for s in (rec.get("steps") or []))
            out = _RUNG.run(SourceText.from_raw("PSM", raw), _RUNG.config(), schema=_SCHEMA) if raw.strip() else None
            events = list(out.graph.events) if out else []
            g = sum(1 for d in (out.mentions.diagnostics if out else ()) if d == "COORD_FOOD_GUARD")
            t["coord_food_guard_triggers"] += g
            t["recipes_with_guard_trigger"] += g > 0
        except Exception:  # counted, never hidden
            t["exceptions"] += 1
            continue
        if not events:
            t["recipes_without_events"] += 1
            continue
        prev_type = prev_fam = None
        for i, e in enumerate(events):
            typ = map_event(e) or "UNMAPPED"
            proc = next((a.value for a in e.attributes if a.field == "proc_id"), "NO_PROC")
            pf = _PROC_FAMILY.get(proc, "NO_PROC")
            d = str(decile(i, len(events)))
            t["n_events"] += 1
            t["by_family"][fam][typ] += 1
            t["proc_type"][proc][typ] += 1
            t["proc_family_type"][pf][typ] += 1
            t["position_type"][d][typ] += 1
            t["position_proc_family"][d][pf] += 1
            if prev_type is not None:
                t["type_bigrams"][f"{prev_type}>{typ}"] += 1
                t["proc_family_bigrams"][f"{prev_fam}>{pf}"] += 1
            prev_type, prev_fam = typ, pf
    return t


def merge(parts) -> dict:
    out = _empty()
    for p in parts:
        for k in ("n_recipes", "n_events", "exceptions", "recipes_without_events", "coord_food_guard_triggers",
                  "recipes_with_guard_trigger"):
            out[k] += p[k]
        for k in ("by_family", "proc_type", "proc_family_type", "position_type", "position_proc_family"):
            for a, c in p[k].items():
                out[k][a].update(c)
        out["type_bigrams"].update(p["type_bigrams"])
        out["proc_family_bigrams"].update(p["proc_family_bigrams"])
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


def _plain(t: dict) -> dict:
    return {k: ({a: dict(c) for a, c in v.items()} if isinstance(v, defaultdict) else dict(v) if isinstance(v, Counter) else v)
            for k, v in t.items()}


def main(argv=None) -> int:
    from culinarystate.lotstate import corpus as C
    ap = argparse.ArgumentParser()
    ap.add_argument("--families", nargs="+", required=True)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--chunk", type=int, default=500)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", required=True)
    ap.add_argument("--coord-food-guard", action="store_true")
    a = ap.parse_args(argv)
    out = Path(a.out)
    if out.exists():
        sys.exit(f"refusing to overwrite {out}")
    t0, start = time.time(), time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    recs = C.stream(tuple(a.families), ROOT)
    if a.limit:
        recs = (r for i, r in enumerate(recs) if i < a.limit)
    with Pool(a.workers, initializer=_init, initargs=(a.coord_food_guard,)) as pool:
        parts = list(pool.imap_unordered(tally_records, _chunks(recs, a.chunk)))
    res = _plain(merge(parts))
    rec = {"record": "PROCESS_STATE_MAP", "decision": "D-100 Lane T", "tool_version": TOOL_VERSION, "labels": LABELS,
           "approver": "ksh+prv (AI, D-085)", "families_requested": a.families, "coord_food_guard": a.coord_food_guard, "started_at_utc": start,
           "wall_seconds": round(time.time() - t0, 1), "workers": a.workers, "limit": a.limit or None,
           "contains_text": False, "contains_ids": False, **res}
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("x") as f:
        f.write(json.dumps(rec, indent=1, sort_keys=True) + "\n")
    print(json.dumps({k: res[k] for k in ("n_recipes", "n_events", "exceptions", "recipes_without_events")}),
          round(time.time() - t0, 1), "s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
