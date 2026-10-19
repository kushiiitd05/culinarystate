#!/usr/bin/env python3
"""EXP-000007 H_STATE authoring pack: one cut point per Gold-v1.1 recipe + eligible evidence cells + question template.

  /opt/anaconda3/bin/python tools/build_hstate_authoring_pack.py
Cut rule (fixed before looking at any system output): cut after n of the N non-Add Gold events, n in [1, N-1], maximising
min(n, N-n) (the middle), ties to the smaller n, and at least one derived (non-ingredient) entity alive. Never chosen by
pronouns or difficulty. Writes per-recipe packs (local: contain recipe text), a text-free manifest, and a blank question
template for Kush (question_text is HIS: nothing here writes a question). No system (B3/B4) is run.
"""
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.annotation.gold import to_events  # noqa: E402
from culinarystate.ledgers.store import LedgerStore  # noqa: E402
from culinarystate.state_graph.engine import Add, replay  # noqa: E402
from culinarystate.vocab.foodon import norm  # noqa: E402

GOLD = ROOT / "annotation" / "gold" / "pilot_20_adjudicated_v1_1"
OUT = ROOT / "benchmark" / "h_state"
FIELDS = ["question_id", "recipe_id", "family_id", "cut_event", "cut_step", "gold_state_hash", "question_text", "question_class",
          "state_information_required", "gold_mode", "gold_evidence_cell", "acceptable_answer_semantics", "why_state_is_required",
          "author", "review_status"]


def choose_cut(events):
    idx = [i for i, e in enumerate(events) if not isinstance(e, Add)]
    N = len(idx)
    adds = {e.label for e in events if isinstance(e, Add)}
    best = None
    for n in range(1, N):                                          # leave at least one event after the cut
        g = replay(events[: idx[n - 1] + 1])
        if not [a for a in g.alive() if a not in adds]:
            continue
        key = (min(n, N - n), -n)
        if best is None or key > best[0]:
            best = (key, n, idx[n - 1] + 1)
    return best[1:] if best else (None, None)


def main():
    st = LedgerStore()
    ing = {norm(i["canonical_name"]): i["id"] for i in st.all_latest("ING") if i["status"] == "ACTIVE"}
    proc = {p["canonical_name"]: p["id"] for p in st.all_latest("PROC") if p["status"] == "ACTIVE"}
    cells = defaultdict(lambda: defaultdict(list))
    for e in st.all_latest("EVD"):
        if e["status"] != "ACTIVE":
            continue
        rf = (e.get("derived") or {}).get("retention_factor")
        i, p = e["matrix"].get("ingredient_id"), e["process"].get("process_id")
        if rf and i and p:
            cells[(i, p)][e["target"].get("raw_name", "")].append(e["id"])
    manifest, template = [], []
    for f in sorted(GOLD.glob("*.ADJUDICATED.json")):
        d = json.loads(f.read_text())
        rid = d["recipe_id"]
        ev = to_events(d)
        n, k = choose_cut(ev)
        if n is None:
            raise SystemExit(f"{rid}: no valid cut point")
        g = replay(ev[:k])
        adds = {e.label: e for e in ev if isinstance(e, Add)}
        anc = {a: {a} for a in adds}                                   # base-ingredient ancestry along the prefix
        procs = defaultdict(set)
        for e in ev[:k]:
            nm = type(e).__name__
            if nm == "Merge":
                anc[e.output] = set().union(*[anc.get(x, {x}) for x in e.inputs])
                for x in e.inputs:
                    procs[e.output] |= procs.get(x, set())
                procs[e.output].add(e.process)
            elif nm == "Split":
                for o, _ in e.outputs:
                    anc[o] = set(anc.get(e.source, {e.source}))
                    procs[o] = set(procs.get(e.source, set()))
            elif nm == "Reserve":
                anc[e.output] = set(anc.get(e.source, {e.source}))
                procs[e.output] = set(procs.get(e.source, set()))
            elif nm == "Transform":
                procs[e.target].add(e.process)
        concept = {l["entity"]: l["concept"] for l in d["ingredient_lines"]}
        elig = []
        for ent in g.alive():
            for b in anc.get(ent, {ent}):
                iid = ing.get(norm(concept.get(b, "")))
                for pr in procs.get(ent, set()) | procs.get(b, set()):
                    pid = proc.get(pr)
                    for tgt, ids in cells.get((iid, pid), {}).items() if iid and pid else []:
                        elig.append({"entity": ent, "ingredient": iid, "process": pid, "target": tgt, "evd_ids": ids[:5], "n_rows": len(ids)})
        state = {}
        for ent in g.alive():
            v = g.current(ent)
            state[ent] = {"qty": v.qty.render(), "location": v.location, "fields": {a: b.value for a, b in v.fields},
                          "ingredients": sorted(anc.get(ent, {ent}))}
        h = g.sha256()
        step = ev[k - 1].step if hasattr(ev[k - 1], "step") else None
        done = [{"type": type(e).__name__, "target": getattr(e, "target", None) or getattr(e, "source", None) or getattr(e, "output", None)} for e in ev[:k] if not isinstance(e, Add)]
        pack = {"recipe_id": rid, "family_id": f"FAM-{rid}", "cut_event_count": n, "cut_event_index": k, "cut_step": step,
                "gold_state_hash": h, "events_applied": len(done), "events_remaining": sum(1 for e in ev[k:] if not isinstance(e, Add)),
                "alive_state": state, "eligible_evidence_cells": elig[:12], "n_eligible_cells": len(elig),
                "steps_up_to_cut": [s["text"] for s in d["steps"] if s["step_index"] <= (step or 0)],
                "full_steps_for_context": [s["text"] for s in d["steps"]]}
        (OUT / "authoring_pack" / f"{rid}.json").write_text(json.dumps(pack, indent=1, ensure_ascii=False))
        manifest.append({"recipe_id": rid, "family_id": pack["family_id"], "cut_event_index": k, "cut_step": step, "gold_state_hash": h,
                         "events_applied": len(done), "events_remaining": pack["events_remaining"], "n_alive": len(state),
                         "n_eligible_evidence_cells": len(elig)})
        for q, cls in (("Q1", "STATE_DEPENDENT"), ("Q2", "STATE_DEPENDENT"), ("Q3", "STATE_DEPENDENT"), ("Q4", "CONTROL")):
            template.append({"question_id": f"{rid}-{q}", "recipe_id": rid, "family_id": pack["family_id"], "cut_event": k, "cut_step": step,
                             "gold_state_hash": h, "question_class": cls, "author": "", "review_status": "UNWRITTEN"})
    with (OUT / "authoring_manifest.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(manifest[0]))
        w.writeheader()
        w.writerows(manifest)
    with (OUT / "questions_to_write.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows({k: r.get(k, "") for k in FIELDS} for r in template)
    print(len(manifest), "recipes;", len(template), "question slots; eligible-cell counts:", Counter(m["n_eligible_evidence_cells"] > 0 for m in manifest))


if __name__ == "__main__":
    main()
