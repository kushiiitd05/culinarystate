#!/usr/bin/env python3
"""EXP-000007 amendment A1 (S114): enumerate every Gold-v1.1 cut with a compatible evidence cell, then select slots.

  /opt/anaconda3/bin/python tools/build_hstate_r_candidates.py
Selection uses ONLY Gold-v1.1 state, EVD ledger coverage and deterministic rules (no B3/B4 output exists or is read):
  H_STATE-R: one slot = (cut, ingredient+process cell). Per recipe the cells must be distinct; round-robin over recipes in
             recipe_id order, per round take each recipe's next unused cell (earliest cut that carries it, ties by entity
             name), cap 6 per recipe, until 40 slots or candidates run out (no forcing).
  H_STATE-A: one slot per recipe at a cut with NO compatible cell (the S112 cut if uncovered, else the uncovered cut
             maximising min(n, N-n)); recipes with no uncovered cut are skipped. Target 20.
  CONTROL:   one per recipe at the S112 cut.
Writes benchmark/h_state/evidence_cut_candidates.csv, questions_to_write.csv (blank, Kush writes text) and local packs.
"""
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))
from build_hstate_authoring_pack import GOLD, OUT, choose_cut  # noqa: E402
from culinarystate.annotation.gold import to_events  # noqa: E402
from culinarystate.ledgers.store import LedgerStore  # noqa: E402
from culinarystate.state_graph.engine import Add, replay  # noqa: E402
from culinarystate.vocab.foodon import norm  # noqa: E402

CAP_PER_RECIPE, TARGET_R, TARGET_A = 6, 40, 20
CAND_FIELDS = ["recipe_id", "family_id", "cut_event_index", "cut_step", "gold_state_hash", "ingredient_entity", "ingredient_id",
               "process", "conditions_available", "compatible_evidence_ids", "compatibility_reason", "candidate_question_types"]
SLOT_FIELDS = ["question_id", "stratum", "recipe_id", "family_id", "cut_event", "cut_step", "gold_state_hash", "target_entity",
               "eligible_evidence_cells", "suggested_mode_category", "state_fields_available", "candidate_question_types",
               "question_text", "state_information_required", "gold_mode", "gold_evidence_cell", "why_state_is_required",
               "author", "review_status"]


def prefix_state(ev, k, concept):
    """Alive entities, base-ingredient ancestry and processes applied along the prefix ev[:k]."""
    adds = {e.label for e in ev if isinstance(e, Add)}
    anc = {a: {a} for a in adds}
    procs, reserved, prior = defaultdict(set), set(), defaultdict(list)
    for e in ev[:k]:
        nm = type(e).__name__
        if nm == "Merge":
            anc[e.output] = set().union(*[anc.get(x, {x}) for x in e.inputs])
            for x in e.inputs:
                procs[e.output] |= procs.get(x, set())
                prior[e.output] += prior.get(x, [])
            procs[e.output].add(e.process)
            prior[e.output].append("Merge")
        elif nm in ("Split", "Reserve"):
            outs = [o for o, _ in e.outputs] if nm == "Split" else [e.output]
            src = e.source
            for o in outs:
                anc[o] = set(anc.get(src, {src}))
                procs[o] = set(procs.get(src, set()))
                prior[o] = list(prior.get(src, [])) + [nm]
                if nm == "Reserve":
                    reserved.add(o)
        elif nm == "Transform":
            procs[e.target].add(e.process)
            prior[e.target].append("Transform")
    return anc, procs, reserved, prior


def main():
    st = LedgerStore()
    ing = {norm(i["canonical_name"]): i["id"] for i in st.all_latest("ING") if i["status"] == "ACTIVE"}
    proc = {p["canonical_name"]: p["id"] for p in st.all_latest("PROC") if p["status"] == "ACTIVE"}
    cells = defaultdict(list)
    for e in st.all_latest("EVD"):
        rf = (e.get("derived") or {}).get("retention_factor")
        i, p = e["matrix"].get("ingredient_id"), e["process"].get("process_id")
        if e["status"] == "ACTIVE" and rf and i and p:
            cells[(i, p)].append(e["id"])
    cand, per_recipe, a_pool, base = [], defaultdict(dict), {}, {}
    for f in sorted(GOLD.glob("*.ADJUDICATED.json")):
        d = json.loads(f.read_text())
        rid, fam = d["recipe_id"], f"FAM-{d['recipe_id']}"
        ev = to_events(d)
        concept = {l["entity"]: l["concept"] for l in d["ingredient_lines"]}
        idx = [i for i, e in enumerate(ev) if not isinstance(e, Add)]
        N = len(idx)
        s112 = choose_cut(ev)[1]
        adds = {e.label for e in ev if isinstance(e, Add)}
        uncovered = []
        for n in range(1, N):
            k = idx[n - 1] + 1
            g = replay(ev[:k])
            alive_d = [a for a in g.alive() if a not in adds]
            if not alive_d:
                continue
            anc, procs, reserved, prior = prefix_state(ev, k, concept)
            step = getattr(ev[k - 1], "step", None)
            h = g.sha256()
            hit = False
            for ent in alive_d:
                v = g.current(ent)
                conds = {a for a, _ in v.fields} | {"ENTITY"}
                if v.location:
                    conds.add("LOCATION")
                if ent in reserved:
                    conds.add("RESERVED_STATUS")
                if prior.get(ent):
                    conds.add("PRIOR_EVENT")
                if len(anc.get(ent, {ent})) > 1:
                    conds.add("COMPOSITION")
                conds = sorted(conds)
                for b in sorted(anc.get(ent, {ent})):
                    iid = ing.get(norm(concept.get(b, "")))
                    for pr in sorted(procs.get(ent, set()) | procs.get(b, set())):
                        pid = proc.get(pr)
                        ids = cells.get((iid, pid)) if iid and pid else None
                        if not ids:
                            continue
                        hit = True
                        types = sorted(set(conds) | {"PROCESS"})
                        row = {"recipe_id": rid, "family_id": fam, "cut_event_index": k, "cut_step": step, "gold_state_hash": h,
                               "ingredient_entity": ent, "ingredient_id": iid, "process": pid, "conditions_available": "|".join(conds),
                               "compatible_evidence_ids": "|".join(ids[:5]),
                               "compatibility_reason": f"{ent} derives from base {b} ({iid}) and {pr} applied before cut; EVD retention cell ({iid},{pid}) n={len(ids)}",
                               "candidate_question_types": "|".join(types)}
                        cand.append(row)
                        per_recipe[rid].setdefault((iid, pid), []).append(row)
            if not hit:
                uncovered.append((min(n, N - n), -n, k, step, h, sorted(alive_d)))
        base[rid] = (fam, s112, ev, d)
        a_pool[rid] = uncovered
    with (OUT / "evidence_cut_candidates.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=CAND_FIELDS)
        w.writeheader()
        w.writerows(cand)
    # --- H_STATE-R selection
    chosen = []
    ordered = {rid: sorted(cs.items(), key=lambda kv: (min(r["cut_event_index"] for r in kv[1]), kv[0])) for rid, cs in per_recipe.items()}
    max_supported = sum(len(v) for v in ordered.values())
    ptr = Counter()
    while len(chosen) < TARGET_R:
        progressed = False
        for rid in sorted(ordered):
            if len(chosen) >= TARGET_R:
                break
            if ptr[rid] < min(len(ordered[rid]), CAP_PER_RECIPE):
                (iid, pid), rows = ordered[rid][ptr[rid]]
                ptr[rid] += 1
                r = min(rows, key=lambda x: (x["cut_event_index"], x["ingredient_entity"]))
                chosen.append(("H_STATE-R", r))
                progressed = True
        if not progressed:
            break
    # --- H_STATE-A and CONTROL
    slots, count = [], Counter()
    def add(stratum, rid, k, step, h, ent, cellids, mode, fields, types):
        count[(rid, stratum)] += 1
        fam = base[rid][0]
        tag = {"H_STATE-R": "R", "H_STATE-A": "A", "CONTROL": "C"}[stratum]
        slots.append({"question_id": f"{rid}-{tag}{count[(rid, stratum)]}", "stratum": stratum, "recipe_id": rid, "family_id": fam,
                      "cut_event": k, "cut_step": step, "gold_state_hash": h, "target_entity": ent, "eligible_evidence_cells": cellids,
                      "suggested_mode_category": mode, "state_fields_available": fields, "candidate_question_types": types,
                      "author": "", "review_status": "UNWRITTEN"})
    for _, r in chosen:
        add("H_STATE-R", r["recipe_id"], r["cut_event_index"], r["cut_step"], r["gold_state_hash"], r["ingredient_entity"],
            f'{r["ingredient_id"]}+{r["process"]}:{r["compatible_evidence_ids"]}', "ANSWER_WITH_EVIDENCE", r["conditions_available"], r["candidate_question_types"])
    a_chosen = []
    for rid in sorted(a_pool):
        fam, s112, ev, d = base[rid]
        pool = a_pool[rid]
        if not pool:
            continue
        hit = [p for p in pool if p[2] == s112]
        p = hit[0] if hit else max(pool)
        a_chosen.append((rid, p))
    for rid, p in a_chosen[:TARGET_A]:
        add("H_STATE-A", rid, p[2], p[3], p[4], "|".join(p[5]), "UNSUPPORTED", "ASK_OR_ABSTAIN", "", "ENTITY|PROCESS|FORM|TIME|TEMPERATURE|LOCATION|PRIOR_EVENT")
    for rid in sorted(base):
        fam, s112, ev, d = base[rid]
        g = replay(ev[:s112])
        h = g.sha256()
        add("CONTROL", rid, s112, getattr(ev[s112 - 1], "step", None), h, "", "", "SAME_MODE_AS_PAIRED_STATE_DEPENDENT", "", "fully specified (states the omitted condition)")
    with (OUT / "questions_to_write.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=SLOT_FIELDS)
        w.writeheader()
        w.writerows({k: r.get(k, "") for k in SLOT_FIELDS} for r in slots)
    n = Counter(s["stratum"] for s in slots)
    rc = Counter(s["recipe_id"] for s in slots if s["stratum"] == "H_STATE-R")
    print(json.dumps({"candidate_rows": len(cand), "recipes_with_supported_cut": len(per_recipe), "max_distinct_cells_total": max_supported,
                      "slots": dict(n), "R_per_recipe": dict(rc), "A_available_recipes": len(a_chosen),
                      "cells_distribution": dict(Counter(r["process"] for _, r in chosen))}, indent=1))


if __name__ == "__main__":
    main()
