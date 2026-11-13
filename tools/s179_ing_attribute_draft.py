#!/usr/bin/env python
"""D-100 L6b: AI-drafted ING attributes (physical form, acidity, vitamin-C bearing) by frozen qwen2.5:7b-instruct
(845dbda0) for every ACTIVE ING row. Used only as labelled AI_DRAFTED input to the D-108 lot gate until Kush/Parv
review it. Temperature 0, seed 7, JSON format; every value validated against ENUMS, anything else -> UNKNOWN.

    python tools/s179_ing_attribute_draft.py --host http://127.0.0.1:11500 --out registry/ing_attributes_ai_draft_v1.csv
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL = "qwen2.5:7b-instruct"
MODEL_DIGEST_PREFIX = "845dbda0"
ENUMS = {"form": ["LIQUID", "PASTE", "SOLID", "POWDER", "GRANULAR", "UNKNOWN"],
         "acidic": ["YES", "NO", "UNKNOWN"], "vitamin_c": ["YES", "NO", "UNKNOWN"]}
TEMPLATE = (
    "You label cooking ingredients as they are usually sold or used in recipes. For each item give:\n"
    "- form: one of {form}\n"
    "- acidic: YES if its typical pH is below 4.6 (e.g. citrus juice, vinegar, tomato), NO if clearly above, else UNKNOWN\n"
    "- vitamin_c: YES if it is a meaningful natural source of vitamin C (ascorbic acid) as used, NO if not, else UNKNOWN\n"
    "Use UNKNOWN whenever unsure. Do not explain. Return JSON exactly as "
    '{{"items": [{{"id": "...", "form": "...", "acidic": "...", "vitamin_c": "..."}}]}} with one entry per id.\n\n'
    "Items:\n{items}\n")
FIELDS = ("id", "canonical_name", "form", "acidic", "vitamin_c", "parse", "model", "model_digest_prefix", "prompt_sha256",
          "label")


def prompt_sha() -> str:
    return hashlib.sha256(TEMPLATE.encode("utf-8")).hexdigest()


def build_prompt(batch) -> str:
    items = "\n".join(f'- id: {x["id"]} | name: {x["name"]}' for x in batch)
    return TEMPLATE.format(form=", ".join(ENUMS["form"]), items=items)


def _norm(field: str, v) -> str:
    s = str(v or "").strip().upper()
    return s if s in ENUMS[field] else "UNKNOWN"


def parse_response(text: str, batch) -> list[dict]:
    want = [x["id"] for x in batch]
    try:
        items = json.loads(text)["items"]
        got = {str(i.get("id")): i for i in items if isinstance(i, dict)}
        status = None
    except Exception:
        got, status = {}, "INVALID_JSON"
    rows = []
    for i in want:
        it = got.get(i)
        if it is None:
            rows.append({"id": i, "form": "UNKNOWN", "acidic": "UNKNOWN", "vitamin_c": "UNKNOWN",
                         "parse": status or "MISSING_FROM_RESPONSE"})
        else:
            rows.append({"id": i, **{f: _norm(f, it.get(f)) for f in ENUMS}, "parse": "OK"})
    return rows


def _call(host: str, prompt: str) -> str:
    body = json.dumps({"model": MODEL, "prompt": prompt, "stream": False, "format": "json",
                       "options": {"temperature": 0, "seed": 7, "num_ctx": 8192}}).encode()
    req = urllib.request.Request(host.rstrip("/") + "/api/generate", data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=600) as r:
        return json.loads(r.read())["response"]


def _active_ing() -> list[dict]:
    last = {}
    for line in (ROOT / "ledgers/data/ING.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            last[r["id"]] = r
    return [{"id": k, "name": v["canonical_name"]} for k, v in sorted(last.items()) if v.get("status", "ACTIVE") == "ACTIVE"]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--batch", type=int, default=25)
    a = ap.parse_args(argv)
    out = Path(a.out)
    if out.exists():
        sys.exit(f"refusing to overwrite {out}")
    ing = _active_ing()
    names = {x["id"]: x["name"] for x in ing}
    t0, rows = time.time(), []
    for i in range(0, len(ing), a.batch):
        batch = ing[i:i + a.batch]
        try:
            text = _call(a.host, build_prompt(batch))
        except Exception as exc:  # recorded per row, never hidden
            text = ""
            print("call failed", i, exc, file=sys.stderr)
        rows.extend(parse_response(text, batch))
        if i % (a.batch * 20) == 0:
            print(i, len(ing), round(time.time() - t0, 1), "s", flush=True)
    with out.open("x", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({**r, "canonical_name": names[r["id"]], "model": MODEL, "model_digest_prefix": MODEL_DIGEST_PREFIX,
                        "prompt_sha256": prompt_sha(), "label": "AI_DRAFTED_NOT_REVIEWED"})
    print("rows", len(rows), "seconds", round(time.time() - t0, 1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
