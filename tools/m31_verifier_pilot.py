#!/usr/bin/env python3
"""EXP-M3.1-AUX task 1: MiniMax M3.1 Flash as a constrained verifier on TASTEset DEV disagreements (design contract: verifier only, never primary NER).

  python tools/m31_verifier_pilot.py build               # offline: build cases from E0 DEV predictions (no network), write reports/ner/m31_cases_tasteset_dev.json
  python tools/m31_verifier_pilot.py smoke               # 10 prompt-dev cases: reliability / latency / format
  python tools/m31_verifier_pilot.py run [--n 100]       # frozen-prompt evaluation on EVAL cases, then score
Data: TASTEset (MIT) DEV only; TEST never touched; no Food.com / RecipeDB3 / BBC text is ever sent. Key from env OLLAMA_API_KEY (never printed or stored).
Primary = deberta-base+CRF, Alternative = deberta-v3-large+CRF (same seed). A case = a span proposed by exactly one of them (or the same text with different type/boundary).
Gold verdict: PRIMARY if only the primary span is gold; ALTERNATIVE if only the alternative span is gold; NEITHER if neither is gold. The model must answer one of
ACCEPT_PRIMARY / ACCEPT_ALTERNATIVE / AMBIGUOUS / UNKNOWN (NEITHER is correct only for AMBIGUOUS or UNKNOWN).
Prompt-dev/eval separation: docs are split by hash; the prompt may be iterated ONLY on PROMPT_DEV docs, then frozen before EVAL is scored."""
import hashlib
import json
import os
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))
RAW = ROOT / "reports" / "ner" / "_raw_e0"
CASES = ROOT / "reports" / "ner" / "m31_cases_tasteset_dev.json"
LEDGER = ROOT / "reports" / "ner" / "m31_aux_ledger.jsonl"
MODEL, URL = "minimax-m3.1-flash", "https://ollama.com/api/chat"
PROMPT_VERSION = "v1"
SYSTEM = ("You verify ingredient-text annotations. You are given one recipe ingredient text and TWO candidate annotations of the SAME text, A and B, "
          "each a span with an entity type. Entity types: FOOD (ingredient), QUANTITY (amount), UNIT (measure unit), PROCESS (preparation action), "
          "PHYSICAL_QUALITY (size/texture/form such as fresh, large), COLOR, TASTE, PURPOSE (intended use), PART (part of an ingredient). "
          "A span is correct only if both its boundaries AND its type are right. Decide using the text only. Do not invent facts. "
          'Answer with JSON only: {"verdict": "ACCEPT_A" | "ACCEPT_B" | "AMBIGUOUS" | "UNKNOWN", "reason": "<max 15 words>"}. '
          "Use ACCEPT_A / ACCEPT_B when exactly one candidate is clearly correct; AMBIGUOUS when both could be defended; UNKNOWN when neither is correct or you cannot tell.")


def bucket(s):
    return int(hashlib.sha256(f"M31|{s}".encode()).hexdigest()[:8], 16) / 16 ** 8


def build():
    import pandas as pd
    import freeze_ner_benchmark as F
    sp = json.loads((ROOT / "benchmark/ner/splits/tasteset_split_v1.json").read_text())["indices"]["dev"]
    docs = F.docs_taste(pd.read_csv(F.TASTE), sp)
    cases = []
    for seed in range(1, 6):
        a = json.load(open(RAW / f"tasteset__deberta-base_crf__seed{seed}.pred.json"))["dev"]
        b = json.load(open(RAW / f"tasteset__deberta-v3-large_crf__seed{seed}.pred.json"))["dev"]
        for k, ((text, gold), pa, pb) in enumerate(zip(docs, a, b)):
            g, A, Bs = {tuple(x) for x in gold}, {tuple(x[:3]) for x in pa}, {tuple(x[:3]) for x in pb}
            onlyA, onlyB = sorted(A - Bs), sorted(Bs - A)
            for sa in onlyA + [None] * 0:                      # pair each exclusive span with the overlapping counterpart if any, else None
                ov = next((x for x in onlyB if min(x[1], sa[1]) > max(x[0], sa[0])), None)
                cases.append({"seed": seed, "doc": sp[k], "text": text, "A": list(sa), "B": list(ov) if ov else None, "A_gold": sa in g, "B_gold": (ov in g) if ov else False})
            for sb in onlyB:
                if not any(min(x[1], sb[1]) > max(x[0], sb[0]) for x in onlyA):
                    cases.append({"seed": seed, "doc": sp[k], "text": text, "A": None, "B": list(sb), "A_gold": False, "B_gold": sb in g})
    seen, uniq = set(), []
    for c in cases:                                              # one case per (doc, spans), seeds merged (a case seen in several seeds counts once)
        key = (c["doc"], tuple(c["A"] or ()), tuple(c["B"] or ()))
        if key not in seen:
            seen.add(key)
            c["gold_verdict"] = "ACCEPT_A" if c["A_gold"] and not c["B_gold"] else "ACCEPT_B" if c["B_gold"] and not c["A_gold"] else "NEITHER" if not (c["A_gold"] or c["B_gold"]) else "BOTH"
            c["split"] = "PROMPT_DEV" if bucket(c["doc"]) < 0.3 else "EVAL"
            uniq.append(c)
    CASES.write_text(json.dumps(uniq))
    print(len(uniq), "cases;", dict(Counter((c["split"], c["gold_verdict"]) for c in uniq)))
    base = Counter()
    for c in uniq:
        if c["gold_verdict"] in ("ACCEPT_A", "ACCEPT_B"):
            base["always_A_correct" if c["gold_verdict"] == "ACCEPT_A" else "always_B_correct"] += 1
    print("decisive cases:", sum(base.values()), dict(base))


def fmt(c):
    s = lambda x: "none (this model proposes no span here)" if not x else f'"{c["text"][x[0]:x[1]]}" as {x[2]}'
    return f'Ingredient text:\n"""{c["text"]}"""\nCandidate A: {s(c["A"])}\nCandidate B: {s(c["B"])}'


def call(c, retries=2):
    import urllib.request
    body = json.dumps({"model": MODEL, "stream": False, "options": {"temperature": 0}, "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": fmt(c)}]}).encode()
    for i in range(retries + 1):
        t0 = time.time()
        try:
            r = urllib.request.Request(URL, body, {"Authorization": f"Bearer {os.environ['OLLAMA_API_KEY']}", "Content-Type": "application/json"})
            d = json.load(urllib.request.urlopen(r, timeout=120))
            txt = (d.get("message") or {}).get("content") or ""
            j = json.loads(txt[txt.index("{"):txt.rindex("}") + 1])
            return {"verdict": j.get("verdict"), "reason": j.get("reason"), "sec": round(time.time() - t0, 2), "in": d.get("prompt_eval_count"), "out": d.get("eval_count"), "ok": True}
        except Exception as e:
            err = f"{type(e).__name__}: {str(e)[:80]}"
            if "401" in err or "403" in err:
                return {"ok": False, "error": err, "fatal": True}
            time.sleep(2 * (i + 1))
    return {"ok": False, "error": err}


def run(split, n):
    cases = [c for c in json.loads(CASES.read_text()) if c["split"] == split and c["gold_verdict"] != "BOTH"]
    cases = sorted(cases, key=lambda c: bucket(f"{c['doc']}{c['A']}{c['B']}"))[:n]
    res = []
    for c in cases:
        r = call(c)
        res.append({**{k: c[k] for k in ("doc", "A", "B", "gold_verdict", "split")}, **r})
        with LEDGER.open("a") as fh:
            fh.write(json.dumps({"task": "verifier_tasteset_dev", "model": MODEL, "prompt": PROMPT_VERSION, "split": split, **{k: v for k, v in res[-1].items() if k != "reason"}}) + "\n")
        if r.get("fatal"):
            print("FATAL:", r["error"])
            break
    score(res)


def score(res):
    ok = [r for r in res if r.get("ok")]
    print(f"calls {len(res)}, parsed {len(ok)} ({len(ok) / max(len(res), 1):.0%}), median latency {sorted(r['sec'] for r in ok)[len(ok) // 2] if ok else None}s")
    dec = [r for r in ok if r["gold_verdict"] in ("ACCEPT_A", "ACCEPT_B")]
    acc = [r for r in dec if r["verdict"] == r["gold_verdict"]]
    abst = [r for r in dec if r["verdict"] in ("AMBIGUOUS", "UNKNOWN")]
    wrong = [r for r in dec if r["verdict"] in ("ACCEPT_A", "ACCEPT_B") and r["verdict"] != r["gold_verdict"]]
    nA = sum(r["gold_verdict"] == "ACCEPT_A" for r in dec)
    print(f"decisive cases {len(dec)}: correct {len(acc)}, wrong {len(wrong)}, abstain {len(abst)} | baselines: always-A {nA / max(len(dec), 1):.3f}, always-B {(len(dec) - nA) / max(len(dec), 1):.3f}")
    if dec:
        print(f"verifier accuracy (all) {len(acc) / len(dec):.3f}; selective accuracy when it commits {len(acc) / max(len(acc) + len(wrong), 1):.3f} at coverage {(len(acc) + len(wrong)) / len(dec):.3f}")
    neither = [r for r in ok if r["gold_verdict"] == "NEITHER"]
    if neither:
        print(f"NEITHER cases {len(neither)}: correctly declined {sum(r['verdict'] in ('AMBIGUOUS', 'UNKNOWN') for r in neither)}")


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "build":
        build()
    elif cmd == "smoke":
        run("PROMPT_DEV", 10)
    else:
        run("EVAL", int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else 100)
