#!/usr/bin/env python3
"""V2-DM client (python 3.8 safe, stdlib only): asks a LOCAL Ollama /v1/systemone decision model bounded questions about a proposed NER span.
  python v2dm_client.py --spans tasteset_spans.jsonl --model tev1:4b --parts dev --routes REVIEW,REJECT --out dm_tev1_4b_dev.jsonl [--limit 50] [--port 11500]
Questions: q3_exact (noul, primary) | q1_boundary (noul, diagnostic) | q2_label (choice, diagnostic). Raw responses are stored; parsing happens in analysis. Resumable (skips ids already in --out).
Prompt wording PROMPT_VERSION is frozen on OOF TRAIN rows before DEV is scored (protocol section 4). Never point this at ollama.com / :cloud models."""
import argparse
import json
import time
import urllib.request

PROMPT_VERSION = "p1"   # overridden by --prompt; pre-listed variants: p1 text+label glossary | p2 = p1 + train-gold exemplars per label | p3 = p2 + CRF confidence band
GLOSS = {"FOOD": "a food or ingredient name", "NAME": "an ingredient name", "QUANTITY": "an amount (number or fraction)", "UNIT": "a measurement unit", "PROCESS": "a cooking action",
         "PHYSICAL_QUALITY": "a physical property such as size, texture or form", "COLOR": "a colour", "TASTE": "a taste", "PURPOSE": "the purpose of an ingredient", "PART": "a part of a food",
         "STATE": "a preparation or processing state of the ingredient (e.g. chopped, ground)", "TEMP": "a temperature or temperature state (e.g. hot, frozen)", "DF": "dry or fresh state", "OTHER": "none of the labels"}


def band(c):
    return "very high" if c >= 0.99 else "high" if c >= 0.9 else "medium" if c >= 0.7 else "low"


def render(row, prompt="p1"):
    t = row["text"]
    s = f'Text: {t[:row["s"]]}[[{t[row["s"]:row["e"]]}]]{t[row["e"]:]}\nProposed label for the marked span: {row["label"]}'
    if prompt == "p3":
        s += f'\nThe tagging model\'s confidence in this span: {band(row["conf"])}'
    return s


def questions(row, labels, prompt="p1", exemplars=None):
    lab = row["label"]
    ex = ""
    if prompt in ("p2", "p3") and exemplars and exemplars.get(lab):
        ex = f" Typical correct {lab} spans in this annotation scheme: " + ", ".join(exemplars[lab][:6]) + "."
    return {
        "q3_exact": {"type": "noul", "instructions": "Is the marked span exactly right, meaning its boundaries cover the whole entity and nothing more, AND the proposed label is correct?",
                     "criteria": {"true": f"The marked span is exactly one complete {lab} ({GLOSS.get(lab, lab)}) with correct boundaries.{ex}", "false": "The boundaries are too short, too long, or the label is wrong, or the span is not an entity."}},
        "q1_boundary": {"type": "noul", "instructions": "Ignoring the label, do the marked boundaries cover exactly one complete entity (no missing words, no extra words)?",
                        "criteria": {"true": "The boundaries are exactly right.", "false": "Words are missing or extra."}},
        "q2_label": {"type": "choice", "instructions": "Which label best describes the marked span?",
                     "criteria": {**{l: GLOSS.get(l, l) for l in labels}, "OTHER": GLOSS["OTHER"]}},
    }


def post(port, payload, timeout=120):
    req = urllib.request.Request(f"http://127.0.0.1:{port}/v1/systemone", data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spans", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--parts", default="dev")
    ap.add_argument("--routes", default="REVIEW,REJECT")
    ap.add_argument("--out", required=True)
    ap.add_argument("--port", type=int, default=11500)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--sample", type=int, default=0, help="random subset of n rows (seed 0) instead of the first n")
    ap.add_argument("--prompt", default="p1", choices=["p1", "p2", "p3"])
    ap.add_argument("--exemplars", default="")
    ap.add_argument("--repeat", type=int, default=1, help="repeat each request n times (determinism check)")
    a = ap.parse_args()
    EX = json.load(open(a.exemplars)) if a.exemplars else None
    parts, routes = set(a.parts.split(",")), set(a.routes.split(","))
    rows = [json.loads(l) for l in open(a.spans)]
    labels = sorted({r["label"] for r in rows})
    done = set()
    try:
        done = {json.loads(l)["id"] for l in open(a.out)}
    except FileNotFoundError:
        pass
    todo = [r for r in rows if r["part"] in parts and r["route"] in routes and r["id"] not in done]
    if a.sample:
        import random
        todo = random.Random(0).sample(todo, min(a.sample, len(todo)))
    if a.limit:
        todo = todo[:a.limit]
    with open(a.out, "a") as f:
        for i, r in enumerate(todo):
            for rep in range(a.repeat):
                t0 = time.time()
                try:
                    resp, err = post(a.port, {"model": a.model, "state": render(r, a.prompt), "questions": questions(r, labels, a.prompt, EX)}), None
                except Exception as e:  # noqa: BLE001 -- recorded as a malformed/failed call, not hidden
                    resp, err = None, repr(e)[:200]
                f.write(json.dumps({"id": r["id"], "model": a.model, "prompt": a.prompt, "rep": rep, "ms": round(1000 * (time.time() - t0), 1), "resp": resp, "error": err}) + "\n")
            if i % 200 == 0:
                f.flush()
                print(i, len(todo), flush=True)


if __name__ == "__main__":
    main()
