#!/usr/bin/env python3
"""EXP-M3.1-AUX task 6: KB / ledger audit with MiniMax M3.1 Flash. It only PROPOSES issues; deterministic checks confirm them; nothing in the ledger is changed.

  OLLAMA_API_KEY=... python tools/m31_ledger_audit.py        # -> reports/ner/m31_ledger_audit.json + .md
Sent: ING canonical names, categories and ALIAS surfaces from the project ledgers (project-built vocabulary; no recipe text, no benchmark text).
Issue types: DUPLICATE_CONCEPT, ALIAS_ON_WRONG_CONCEPT, BAD_ALIAS, CATEGORY_INCONSISTENT, NOT_AN_INGREDIENT, BAD_CANONICAL_NAME.
Deterministic confirmation: shared normalised surface across concepts; plural/singular or whitespace duplicates; token-subset canonical names; same-category check."""
import json
import os
import re
import sys
import time
import unicodedata
import urllib.request
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.ledgers.store import LedgerStore  # noqa: E402

URL, MODEL = "https://ollama.com/api/chat", "minimax-m3.1-flash"
SYSTEM = ("You audit a food-ingredient vocabulary. Each line is: ID | canonical name | category | aliases. Find real problems ONLY (precision over recall): "
          "DUPLICATE_CONCEPT (two IDs that are the same ingredient), ALIAS_ON_WRONG_CONCEPT (an alias that names a different ingredient), BAD_ALIAS (not a name for this ingredient), "
          "CATEGORY_INCONSISTENT (category clearly wrong for the ingredient), NOT_AN_INGREDIENT (a cooking process, tool, dish, or brand rather than an ingredient), BAD_CANONICAL_NAME. "
          'Return JSON only: {"issues":[{"type":"...","ids":["ING-..."],"alias":"<optional>","evidence":"<max 20 words>"}]}. If a line is fine, say nothing about it. Maximum 15 issues.')


def norm(s):
    s = "".join(c for c in unicodedata.normalize("NFKD", (s or "").lower()) if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]+", " ", s)).strip()


def call(text):
    body = json.dumps({"model": MODEL, "stream": False, "think": False, "options": {"temperature": 0, "num_predict": 8000}, "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": text}]}).encode()
    for i in range(3):
        try:
            r = urllib.request.Request(URL, body, {"Authorization": f"Bearer {os.environ['OLLAMA_API_KEY']}", "Content-Type": "application/json"})
            d = json.load(urllib.request.urlopen(r, timeout=300))
            t = d["message"]["content"]
            return json.loads(t[t.index("{"):t.rindex("}") + 1]).get("issues", []), d.get("prompt_eval_count"), d.get("eval_count")
        except Exception as e:
            err = f"{type(e).__name__}: {str(e)[:80]}"
            if "401" in err or "403" in err:
                raise
            print("  call failed:", err, flush=True)
            time.sleep(3 * (i + 1))
    return None, 0, 0


def main():
    st = LedgerStore()
    ing = {i["id"]: i for i in st.all_latest("ING") if i["status"] == "ACTIVE"}
    al = defaultdict(list)
    for a in st.all_latest("ALIAS"):
        if a["status"] == "ACTIVE" and a.get("ingredient_id") in ing and a["language"] == "en":
            al[a["ingredient_id"]].append(a["normalized"])
    lines = [f"{i} | {r['canonical_name']} | {r['category']} | {'; '.join(sorted(set(al.get(i, [])))[:8])}" for i, r in sorted(ing.items())]
    chunks = [lines[k:k + 120] for k in range(0, len(lines), 120)]
    issues, usage = [], []
    for n, ch in enumerate(chunks):
        out, pi, po = call("\n".join(ch))
        ok = out is not None
        out = out or []
        for x in out:
            x["chunk"] = n
        issues += out
        usage.append((pi, po))
        with (ROOT / "reports/ner/m31_aux_ledger.jsonl").open("a") as fh:
            fh.write(json.dumps({"task": "ledger_audit", "model": MODEL, "chunk": n, "lines": len(ch), "issues": len(out), "in": pi, "out": po, "ok": ok}) + "\n")
        print("chunk", n, len(ch), "lines ->", len(out), "issues", "" if ok else "(CALL FAILED)", "tokens out", po, flush=True)
    # deterministic confirmation
    surf = defaultdict(set)
    for i, r in ing.items():
        surf[norm(r["canonical_name"])].add(i)
        for a in al.get(i, []):
            surf[norm(a)].add(i)
    shared = {s: v for s, v in surf.items() if len(v) > 1}
    canon = {norm(r["canonical_name"]): i for i, r in ing.items()}
    for x in issues:
        ids = [i for i in x.get("ids", []) if i in ing]
        x["ids_exist"] = len(ids) == len(x.get("ids", [])) and bool(ids)
        c = False
        if x["type"] in ("DUPLICATE_CONCEPT", "ALIAS_ON_WRONG_CONCEPT") and len(ids) >= 1:
            c = any(set(ids) <= v or (len(set(ids) & v) >= 1 and len(v) > 1) for v in shared.values()) or (
                x["type"] == "DUPLICATE_CONCEPT" and len(ids) == 2 and (norm(ing[ids[0]]["canonical_name"]).rstrip("s") == norm(ing[ids[1]]["canonical_name"]).rstrip("s")
                                                                          or set(norm(ing[ids[0]]["canonical_name"]).split()) <= set(norm(ing[ids[1]]["canonical_name"]).split())))
        if x["type"] == "CATEGORY_INCONSISTENT" and len(ids) == 1:
            peers = [j for j, r in ing.items() if j != ids[0] and norm(r["canonical_name"]).split()[-1:] == norm(ing[ids[0]]["canonical_name"]).split()[-1:]]
            c = bool(peers) and all(ing[j]["category"] != ing[ids[0]]["category"] for j in peers)
        x["deterministic_support"] = bool(c)
    rep = {"model": MODEL, "n_ing": len(ing), "chunks": len(chunks), "calls": len(chunks), "tokens_in": sum(u[0] or 0 for u in usage), "tokens_out": sum(u[1] or 0 for u in usage),
           "n_issues": len(issues), "n_ids_exist": sum(x["ids_exist"] for x in issues), "n_deterministically_supported": sum(x["deterministic_support"] for x in issues),
           "by_type": {t: sum(1 for x in issues if x["type"] == t) for t in sorted({x["type"] for x in issues})},
           "deterministic_shared_surface_count": len(shared), "issues": issues}
    (ROOT / "reports/ner/m31_ledger_audit.json").write_text(json.dumps(rep, indent=1))
    print({k: v for k, v in rep.items() if k != "issues"})


if __name__ == "__main__":
    main()
