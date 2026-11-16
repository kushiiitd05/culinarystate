#!/usr/bin/env python3
"""Dry-run trace of the current implementation on one recipe text: per step, lots consumed -> produced (merge/split),
lineage, C_t of each food, router route + evidence found for vitamin C and lycopene, the named state vector and the
change (Δ) since that food's previous state. Physics (Q) is filled only in corpus runs (physics v06); here it is masked.

    python tools/s179_state_trace_demo.py "Chop the tomatoes. ..."
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

TARGETS = {"vitc": "SVAR-000009", "lycopene": "SVAR-000025"}


def main(argv=None) -> int:
    from culinarystate.composition import context_v12 as CV, router_v12 as RV, state as CS, state_vector as SV
    from culinarystate.extraction.interfaces import SourceText
    from culinarystate.extraction.rung_a import RungA
    from culinarystate.ledgers.store import LedgerStore
    from culinarystate.mechanism import evidence_gates as EG, process_signatures as PS, router_demo as RD
    from culinarystate.quantity.rc2_dryrun import load_schema
    text = (argv or sys.argv[1:])[0].replace("\\n", "\n")
    rung, schema = RungA(coord_food_guard=True), load_schema()
    marks, roles = CS.load_markers_v2(ROOT / "registry/composition_markers_v2.csv")
    sr = CV.load_sr_composition(ROOT / "registry/ing_sr_composition_v1.csv")
    rows = LedgerStore().all_latest("EVD")
    evd = {r["id"]: r for r in rows}
    env = dict(index=RD.EvidenceIndex.from_rows(rows), gates=EG.EvidenceGates.load(), hierarchy=PS.read_process_hierarchy())
    names, fam = {}, {}
    for line in (ROOT / "ledgers/data/ING.jsonl").read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            names[r["id"]] = r["canonical_name"]
    for line in (ROOT / "ledgers/data/PROC.jsonl").read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            fam[r["id"]] = (r.get("family"), r.get("canonical_name") or r["id"])
    parsed = rung.run(SourceText.from_raw("DEMO", text), rung.config(), schema=schema)
    mem = CS.lot_members_v11(parsed.graph.entities)
    ents = {e.entity_id: e for e in parsed.graph.entities}
    routed = {t: RD.route_text(text, target_svar=s, rung=rung, schema=schema, **env)["items"] for t, s in TARGETS.items()}
    made_by: dict[str, str] = {}
    events = list(parsed.graph.events)
    prev_vec: dict[str, tuple] = {}

    def lot(eid):
        own = [a.value for a in (ents[eid].attributes or ()) if a.field == "ingredient_id"] if eid in ents else []
        ings = sorted(names.get(i, i) for i in mem.get(eid, (frozenset(),))[0])
        return f"{eid}[{'+'.join(ings) or '?'}]" + ("" if own or eid not in ents else f"<-{','.join(ents[eid].parent_entity_ids)}")

    def history(eid, seen=()):
        out = set()
        for p in (ents[eid].parent_entity_ids if eid in ents else ()):
            f = made_by.get(p)
            if f in SV.HEAT:
                out.add("HEATED")
            if f == "MECHANICAL_CUT":
                out.add("CUT")
            if f == "SEPARATION":
                out.add("SEPARATED")
            if p not in seen:
                out |= history(p, seen + (eid,))
        return out

    for k, e in enumerate(events):
        proc = next((a.value for a in e.attributes if a.field == "proc_id"), None)
        family, pname = fam.get(proc, (None, proc))
        kind = "MERGE" if len(e.consumes) > 1 and len(e.produces) == 1 else \
            "SPLIT" if len(e.consumes) == 1 and len(e.produces) > 1 else "TRANSFORM"
        print(f"\nSTEP {k + 1} {e.event_id} '{' '.join(e.span.texts)}' -> {proc} {pname} ({family}) {kind}")
        print(f"  consumes: {', '.join(lot(c) for c in e.consumes) or '(nothing linked)'}")
        print(f"  produces: {', '.join(e.produces) or '-'}" + (f"  discards: {', '.join(e.discards)}" if e.discards else ""))
        ings = set()
        for c in e.consumes:
            ings |= mem.get(c, (frozenset(), False))[0]
        foods = sorted(i for i in ings if not (marks.get(i) and roles.get(i) == "MEDIUM"))
        hist = set().union(*(history(c) for c in e.consumes)) if e.consumes else set()
        for food in foods:
            ctx = CV.context_v12(food, list(e.consumes), mem, marks, roles, sr, medium_type=None)
            flag = {a: ctx[f"{a}_present"].get("v") for a in ("salt", "acid", "lipid", "aqueous")}
            routes = {}
            for t in TARGETS:
                it = next((i for i in routed[t] if i["event_id"] == e.event_id and i["ingredient_id"] == food), None)
                if it is None:
                    continue
                out = RV.composition_route(it, ctx, evd)
                ev = out.get("evidence") or []
                near = out.get("near_evidence") or it.get("evidence_not_applied") or []
                ret = next((x.get("value") for x in ev), None)
                routes[t] = {"route": out["route"], "retention": ret}
                found = ", ".join(f"{x['evd_id']}={x.get('value')}{x.get('unit') or ''}" for x in (ev or near)) or "none"
                print(f"    [{names.get(food, food)} · {t}] frozen={it['route']} -> composition-aware={out['route']} "
                      f"| evidence {'APPLIED' if ev else 'found but not applied' if near else 'not found'}: {found} "
                      f"| {'; '.join(out.get('composition_reasons') or [])}")
            vec = SV.encode(family=family, step_position=round(k / max(1, len(events) - 1), 3), n_inputs=len(e.consumes),
                            n_members=len(ings), history=hist, ctx=ctx, routes=routes)
            known = sum(vec[1])
            d = SV.delta(prev_vec[food], vec) if food in prev_vec else None
            print(f"  FOOD {names.get(food, food)}: context={flag} phase={ctx['contact_phase'].get('v')} "
                  f"co-members={[names.get(i, i) for i in ctx['context_members']['v']]} history={sorted(hist)}")
            print(f"    vector: {known}/{len(vec[0])} dims known; "
                  + ("first state of this food" if d is None else f"Δ since its last state: {d}"))
            prev_vec[food] = vec
        for p in e.produces:
            made_by[p] = family
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
