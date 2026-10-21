#!/usr/bin/env python3
"""Track C runner (stdlib, py3.8): choice among top-5 candidates + NONE with a local decision model. python v2dm_linker_run.py tasks.jsonl MODEL out.jsonl [port]"""
import json
import sys
import time
import urllib.request

tasks, MODEL, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
PORT = int(sys.argv[4]) if len(sys.argv) > 4 else 11500
import string
K = int(sys.argv[5]) if len(sys.argv) > 5 else 5
KEYS = list(string.ascii_uppercase[:K])      # K = number of candidates shown (default 5 = TEV-LINK-v0)
with open(OUT, "w") as f:
    for l in open(tasks):
        r = json.loads(l)
        crit = {KEYS[i]: f'{c["name"]}' + (f' (also called: {", ".join(c["aliases"])})' if c["aliases"] else "") for i, c in enumerate(r["cands"][:K])}
        crit["NONE"] = "None of the candidates is the same ingredient as the mention."
        q = {"link": {"type": "choice", "instructions": f'Which ingredient from the ledger is the same ingredient as the recipe mention "{r["mention"]}"? Choose NONE if no candidate is the same ingredient.', "criteria": crit}}
        t0 = time.time()
        try:
            req = urllib.request.Request(f"http://127.0.0.1:{PORT}/v1/systemone", data=json.dumps({"model": MODEL, "state": f'Recipe ingredient mention: {r["mention"]}', "questions": q}).encode(), headers={"Content-Type": "application/json"})
            resp, err = json.loads(urllib.request.urlopen(req, timeout=120).read().decode()), None
        except Exception as e:  # noqa: BLE001
            resp, err = None, repr(e)[:200]
        f.write(json.dumps({"id": r["id"], "ms": round(1000 * (time.time() - t0), 1), "resp": resp, "error": err}) + "\n")
