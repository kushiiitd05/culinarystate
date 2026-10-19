#!/usr/bin/env python3
"""S109: human review sheet for the Gold-v1 correction queue (local file: contains source text).

  /opt/anaconda3/bin/python tools/make_gold_review_sheet.py   ->  annotation/gold/gold_v1_1_review_sheet.md
Per recipe: source steps, then every proposal row with the reason, current vs proposed events, and the recipe-level effect on the
replayed state (alive entities and event counts, v1 -> proposed). Kush records APPROVE / REJECT / MODIFY / NEEDS_DISCUSSION + a
short rationale per item_id in gold_v1_correction_queue.csv (decision, reviewer columns) or tells the coding agent per id.
"""
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.annotation.gold import to_events  # noqa: E402
from culinarystate.state_graph.engine import replay  # noqa: E402

G = ROOT / "annotation" / "gold"


def compact(evs):
    out = []
    for e in evs:
        a = e.get("target") or "+".join(e.get("inputs", []))
        o = e.get("output") or ",".join(x["label"] for x in e.get("outputs", [])) or e.get("location") or e.get("portion") or ""
        out.append(f"{e['type']}({a}{' -> ' + o if o else ''}{', ' + e['process'] if e.get('process') else ''})")
    return "; ".join(out) if out else "(no events)"


def main():
    v1 = {p.name.split(".")[0]: json.loads(p.read_text()) for p in sorted((G / "pilot_20_adjudicated").glob("*.json"))}
    pr = {p.name.split(".")[0]: json.loads(p.read_text()) for p in sorted((G / "pilot_20_adjudicated_v1_1_proposed").glob("*.json"))}
    rows = list(csv.DictReader((G / "gold_v1_correction_queue.csv").open()))
    L = ["# Gold-v1 -> v1.1 review sheet (S109)", "",
         "Every item is `AI_PROPOSED_CORRECTION`. Nothing is applied until you record a decision. Options per item id: "
         "APPROVE / REJECT / MODIFY (say what to change) / NEEDS_DISCUSSION, with a short rationale. 'approve all proposals' is a valid answer; "
         "AUDIT_FLAG rows are information (their fixes are separate proposal rows) and need no decision. Source text is third-party: local only.", ""]
    for rid in sorted(v1):
        mine = [r for r in rows if r["recipe_id"] == rid and r["item_type"] != "AUDIT_FLAG"
                and json.loads(r["patch_json"]).get("op") != "none"]
        flags = [r for r in rows if r["recipe_id"] == rid and r["item_type"] == "AUDIT_FLAG"]
        if not mine and not flags:
            L += [f"## {rid}: PASS (no proposals)", ""]
            continue
        a, b = replay(to_events(v1[rid])), replay(to_events(pr[rid]))
        av, bv = set(a.alive()), set(b.alive())
        L += [f"## {rid}", f"State effect if ALL its items are accepted: alive entities {len(av)} -> {len(bv)}; events "
              f"{sum(len(s['events']) for s in v1[rid]['steps'])} -> {sum(len(s['events']) for s in pr[rid]['steps'])}. "
              f"Removed from alive: {sorted(av - bv)}. Newly alive: {sorted(bv - av)}.", ""]
        for r in mine:
            L += [f"### {r['item_id']} · {r['item_type']} · step {r['step_index'] or '-'}",
                  f"- problem: {r['problem']}", f"- reason/source support: {r['reason']}",
                  f"- source: {r['source_text'][:400]}"]
            p = json.loads(r["patch_json"])
            if p["op"] == "replace_events":
                L += [f"- current: {compact(v1[rid]['steps'][p['step']]['events'])}", f"- proposed: {compact(p['events'])}"]
            else:
                L += [f"- current: {r['current_value'][:200]}", f"- proposed: {r['proposed_correction'][:300]}"]
            L += ["- decision: ____  rationale: ____", ""]
        for r in flags:
            L += [f"- flag {r['item_id']}: {r['current_value']} - {r['problem']}"]
        L.append("")
    (G / "gold_v1_1_review_sheet.md").write_text("\n".join(L) + "\n")
    print(len(L), "lines; rows needing a decision:", sum(1 for r in rows if r["item_type"] != "AUDIT_FLAG" and json.loads(r["patch_json"]).get("op") != "none"))


if __name__ == "__main__":
    main()
