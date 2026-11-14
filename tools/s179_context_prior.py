#!/usr/bin/env python3
"""D-116: full-corpus composition context per (food, heat process) -> corpus prior + naive-lookup headline.

Per heat event (PROC family in HEAT_FAMILIES) and per food member of its consumed lots, C_t v1.2 context is computed
(markers v2 + USDA SR composition). Tallies, counts and ids only (no text):
- prior[food|proc]: n events, k events with salt / acid / lipid stated TRUE, unknown (any axis UNKNOWN)
- naive: events whose (food, proc) pair has any ACTIVE EVD row (what a pair lookup would answer), split into
  added context TRUE (-> CONTEXT_MISMATCH), UNKNOWN, plain
- unplaced_list[axis]: events where the axis is not TRUE but the recipe lists an ingredient with that marker that no
  step uses (INGREDIENT_LIST_UNPLACED suggestion)
Refuses to overwrite. Shard with --shard i/n; merge with --merge.

    python tools/s179_context_prior.py --families FOODCOM --shard 0/16 --out runs/prior_FOODCOM_0of16.json
    python tools/s179_context_prior.py --merge runs/prior_*.json --out reports/s179/context_prior_full.json
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

HEAT_FAMILIES = frozenset({"WET_HEAT", "DRY_HEAT", "FAT_HEAT", "HEAT_GENERAL", "COMBINATION"})
AXES = ("salt", "acid", "lipid")
LABELS = ["DERIVED_VIEW_NOT_LEDGER", "CORPUS_PRIOR_NOT_FACT", "MARKERS_AI_DELEGATED_D085", "SR_MATCH_AI_DRAFTED",
          "NAIVE_PAIR_LOOKUP_PROXY_NO_OTHER_GATES"]


def _ings(entities) -> set[str]:
    return {a.value for e in entities for a in (e.attributes or ()) if a.field == "ingredient_id" and a.value}


def tally_recipe(rec, S, acc) -> None:
    from culinarystate.composition import context_v12 as CV, router_v12 as RV, state as CS
    from culinarystate.extraction.interfaces import SourceText
    raw = "\n".join(str(s) for s in (rec.get("steps") or []))
    if not raw.strip():
        acc["no_steps"] += 1
        return
    rung, schema = S["rung"], S["schema"]
    parsed = rung.run(SourceText.from_raw("CP", raw), rung.config(), schema=schema)
    mem = CS.lot_members_v11(parsed.graph.entities)
    step_ings = set().union(*(m[0] for m in mem.values())) if mem else set()
    lines = [str(x) for x in (rec.get("ingredient_lines") or []) if str(x).strip()]
    list_ings = _ings(rung.run(SourceText.from_raw("CPL", "\n".join(lines)), rung.config(), schema=schema)
                      .graph.entities) if lines else set()
    unplaced = RV.unplaced_from_list(list_ings, step_ings, S["marks"])
    for e in parsed.graph.events:
        proc = next((a.value for a in e.attributes if a.field == "proc_id"), None)
        if S["family"].get(proc) not in HEAT_FAMILIES:
            continue
        ings, _ = set(), False
        for c in e.consumes:
            ings |= mem.get(c, (frozenset(), False))[0]
        foods = [i for i in ings if not (S["marks"].get(i) and S["roles"].get(i) == "MEDIUM")]
        for food in foods:
            ctx = CV.context_v12(food, list(e.consumes), mem, S["marks"], S["roles"], S["sr"], medium_type=None)
            vals = {a: ctx[f"{a}_present"].get("v") for a in AXES}
            p = acc["prior"][f"{food}|{proc}"]
            p["n"] += 1
            for a in AXES:
                p[a] += vals[a] is True
            p["unknown"] += any(v is None for v in vals.values())
            acc["food_events"] += 1
            if (food, proc) in S["evd_pairs"]:
                added = any(v is True for v in vals.values())
                acc["naive"]["evd_pair_events"] += 1
                acc["naive"]["added_context_true"] += added
                acc["naive"]["unknown_no_true"] += (not added) and any(v is None for v in vals.values())
            for a in AXES:
                if vals[a] is not True and unplaced[a]:
                    acc["unplaced_list"][a] += 1


def _acc():
    return {"recipes": 0, "no_steps": 0, "exceptions": 0, "food_events": 0, "naive": Counter(),
            "unplaced_list": Counter(), "prior": defaultdict(Counter)}


def merge(parts: list[dict]) -> dict:
    acc = _acc()
    for p in parts:
        for k in ("recipes", "no_steps", "exceptions", "food_events"):
            acc[k] += p[k]
        acc["naive"].update(p["naive"])
        acc["unplaced_list"].update(p["unplaced_list"])
        for key, c in p["prior"].items():
            acc["prior"][key].update(c)
    return acc


def _dump(acc, extra) -> dict:
    return {**extra, "labels": LABELS, "contains_text": False, "recipes": acc["recipes"], "no_steps": acc["no_steps"],
            "exceptions": acc["exceptions"], "food_events": acc["food_events"], "naive": dict(acc["naive"]),
            "unplaced_list": dict(acc["unplaced_list"]),
            "prior": {k: dict(v) for k, v in sorted(acc["prior"].items())}}


def _setup() -> dict:
    from culinarystate.composition import context_v12 as CV, state as CS
    from culinarystate.extraction.rung_a import RungA
    from culinarystate.ledgers.store import LedgerStore
    from culinarystate.quantity.rc2_dryrun import load_schema
    marks, roles = CS.load_markers_v2(ROOT / "registry/composition_markers_v2.csv")
    family = {}
    for line in (ROOT / "ledgers/data/PROC.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            family[r["id"]] = r.get("family")
    pairs = {((r.get("matrix") or {}).get("ingredient_id"), (r.get("process") or {}).get("process_id"))
             for r in LedgerStore().all_latest("EVD") if r.get("status") == "ACTIVE"}
    return {"rung": RungA(coord_food_guard=True), "schema": load_schema(), "marks": marks, "roles": roles,
            "sr": CV.load_sr_composition(ROOT / "registry/ing_sr_composition_v1.csv"), "family": family,
            "evd_pairs": pairs}


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
        acc = merge([json.loads(Path(p).read_text()) for p in a.merge])
        out.write_text(json.dumps(_dump(acc, {"parts": len(a.merge)}), indent=1))
        print(acc["recipes"], acc["exceptions"], dict(acc["naive"]))
        return 0
    from culinarystate.lotstate import corpus as C
    S, acc, t0 = _setup(), _acc(), time.time()
    si, sn = (int(x) for x in a.shard.split("/"))
    for k, rec in enumerate(C.stream(tuple(a.families), ROOT)):
        if a.limit and k >= a.limit:
            break
        if k % sn != si:
            continue
        acc["recipes"] += 1
        try:
            tally_recipe(rec, S, acc)
        except Exception:
            acc["exceptions"] += 1
    out.write_text(json.dumps(_dump(acc, {"families": a.families, "shard": a.shard,
                                          "wall_seconds": round(time.time() - t0, 1)})))
    print(acc["recipes"], acc["exceptions"], dict(acc["naive"]), dict(acc["unplaced_list"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
