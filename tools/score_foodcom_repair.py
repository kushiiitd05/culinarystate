#!/usr/bin/env python3
"""S118: add v1.1 outcome columns to the dropped-event audit (RESTORED / REJECTED_BY_POLICY / SUPERSEDED / UNRESOLVED) + summary.

An S117-dropped event is RESTORED when the v1.1 step holds an event with the same canonical process; REJECTED_BY_POLICY when its class is
medium-only water, serving suggestion or alternative branch, or its action only heats/prepares a vessel; SUPERSEDED when v1.1 re-authored the
step without that AI-mechanical event (cascade noise); else UNRESOLVED. Deterministic; reads local gold files.
"""
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.state_graph.rule_compiler import step_processes  # noqa: E402

A = ROOT / "reports" / "gold" / "foodcom_dropped_event_audit.csv"
V1 = ROOT / "annotation" / "gold" / "foodcom_ai_assisted_v1_1" / "Kush"
POLICY = {"CONVERTER_LIMITATION", "OPTIONAL_BRANCH", "ALTERNATIVE_BRANCH"}
VESSEL = re.compile(r"^(heat|reduce|preheat|boil)$")


def canon(a):
    n = [x for _, x in step_processes(a or "")]
    return n[0] if n else (a or "").lower()


def main():
    docs = {json.loads(p.read_text())["recipe_id"]: json.loads(p.read_text()) for p in V1.glob("*.json")}
    rows = list(csv.DictReader(open(A)))
    for r in rows:
        steps = {s["step_index"]: s for s in docs[r["recipe_id"]]["steps"]}
        evs = steps[int(r["step_index"])]["events"]
        want = canon(r["process_action"])
        hit = [i for i, e in enumerate(evs) if canon(e.get("process", e["type"])) == want or e["type"].lower() == want]
        if hit:
            r["v1_1_outcome"], r["v1_1_ref"] = "RESTORED", f"s{r['step_index']}e{hit[0]}"
        elif r["repair_class"] in POLICY or (r["repair_class"] == "OPTIONAL_BRANCH"):
            r["v1_1_outcome"], r["v1_1_ref"] = "REJECTED_BY_POLICY", ""
        elif r["event_type"] in ("SERVE", "WAIT") or VESSEL.match(r["process_action"]):
            r["v1_1_outcome"], r["v1_1_ref"] = "REJECTED_BY_POLICY", "no tracked food entity / serving"
        elif not evs and re.match(r"\s*note\b", steps[int(r["step_index"])]["text"], re.I):
            r["v1_1_outcome"], r["v1_1_ref"] = "REJECTED_BY_POLICY", "note step: alternative/serving remark, no state event"
        elif evs:
            r["v1_1_outcome"], r["v1_1_ref"] = "SUPERSEDED", f"step re-authored ({len(evs)} events)"
        else:
            r["v1_1_outcome"], r["v1_1_ref"] = "UNRESOLVED", "step has no event in v1.1"
    with A.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    c = Counter(r["v1_1_outcome"] for r in rows)
    print(c, "of", len(rows))
    print(Counter((r["repair_class"], r["v1_1_outcome"]) for r in rows))
    for r in rows:
        if r["v1_1_outcome"] == "UNRESOLVED":
            print(r["recipe_id"], r["step_index"], r["process_action"], r["repair_class"])


if __name__ == "__main__":
    main()
