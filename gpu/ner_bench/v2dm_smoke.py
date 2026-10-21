#!/usr/bin/env python3
"""V2-DM smoke test (stdlib, py3.8): Choice + Noul on toy recipe sentences; records response schema, repeatability, latency, malformed rate. Local Ollama only."""
import json
import sys
import time
import urllib.request

PORT, MODEL = int(sys.argv[2]) if len(sys.argv) > 2 else 11500, sys.argv[1]
CASES = [("Add 2 cups finely chopped onions.", "[[onions]]", True), ("Add 2 cups finely chopped onions.", "[[finely]]", False), ("Bake at 350 degrees for 20 minutes.", "[[350 degrees]]", True)]


def post(p):
    req = urllib.request.Request(f"http://127.0.0.1:{PORT}/v1/systemone", data=json.dumps(p).encode(), headers={"Content-Type": "application/json"})
    t = time.time()
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.loads(r.read().decode()), 1000 * (time.time() - t)


out = {"model": MODEL, "cases": []}
bad = 0
for text, marked, expect in CASES:
    state = f"Sentence: {text}\nMarked span: {marked}"
    q = {"is_entity": {"type": "noul", "instructions": "Is the marked span a complete ingredient, quantity, unit, preparation or temperature entity?", "criteria": {"true": "Yes, a complete entity.", "false": "No, not an entity or incomplete."}},
         "label": {"type": "choice", "instructions": "Which label fits the marked span?", "criteria": {"FOOD": "an ingredient", "QUANTITY": "an amount", "UNIT": "a measurement unit", "STATE": "a preparation state", "TEMP": "a temperature", "OTHER": "none of these"}}}
    reps = []
    for _ in range(3):
        try:
            r, ms = post({"model": MODEL, "state": state, "questions": q})
            reps.append({"ms": round(ms, 1), "resp": r})
        except Exception as e:  # noqa: BLE001
            bad += 1
            reps.append({"error": repr(e)[:200]})
    out["cases"].append({"state": state, "expect_entity": expect, "reps": reps})
out["malformed_or_failed"] = bad
print(json.dumps(out, indent=1))
