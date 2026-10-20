#!/usr/bin/env python3
"""EXP-M3.1-AUX task 5: TRAIN-only synthetic data for the contrastive linker, generated with MiniMax M3.1 Flash.

  OLLAMA_API_KEY=... python tools/m31_linker_augment.py      # -> features/linker_aug_v1.json (+ ledger rows)
Source: only TRAIN concepts and their TRAIN surfaces from features/linker_data_v1.json (held-out aliases, dev and test concepts are never shown to the model).
Per concept the model proposes: new surface forms (spelling/plural/abbreviation/regional names), and confusable DIFFERENT ingredients (hard negatives).
Deterministic filters: drop a generated surface that (a) equals any existing surface of ANY concept, (b) equals any dev_alias / unseen_alias / dev / unseen_concept query surface
(counted as 'collisions' to show whether the model reproduces held-out strings), (c) is empty, > 4 tokens, or contains digits. Everything is flagged synthetic=true."""
import json
import os
import re
import sys
import time
import unicodedata
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
URL, MODEL = "https://ollama.com/api/chat", "minimax-m3.1-flash"
SYSTEM = ("You help build an ingredient-name dictionary for recipes. For each ingredient line 'ID | canonical name | category | known names' propose: "
          "'new': up to 5 DIFFERENT names a recipe might use for the SAME ingredient (spelling variants, plural/singular, abbreviations, regional or language-of-origin names used in English recipes); "
          "'confusable': up to 3 DIFFERENT ingredients (names) that are easily confused with it but are not the same ingredient. Names only, lower case, no quantities or preparation words, no brands. "
          'Return JSON only: {"items":[{"id":"ING-...","new":["..."],"confusable":["..."]}]}. Be conservative: omit a name if unsure.')


def norm(s):
    s = "".join(c for c in unicodedata.normalize("NFKD", (s or "").lower()) if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]+", " ", s)).strip()


def call(text):
    body = json.dumps({"model": MODEL, "stream": False, "think": False, "options": {"temperature": 0, "num_predict": 8000}, "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": text}]}).encode()
    for i in range(2):
        try:
            r = urllib.request.Request(URL, body, {"Authorization": f"Bearer {os.environ['OLLAMA_API_KEY']}", "Content-Type": "application/json"})
            d = json.load(urllib.request.urlopen(r, timeout=300))
            t = d["message"]["content"]
            return json.loads(t[t.index("{"):t.rindex("}") + 1]).get("items", []), d.get("prompt_eval_count"), d.get("eval_count")
        except Exception as e:
            err = f"{type(e).__name__}: {str(e)[:80]}"
            if "401" in err or "403" in err:
                raise
            print("  call failed:", err, flush=True)
            time.sleep(3)
    return [], 0, 0


def main():
    D = json.loads((ROOT / "features/linker_data_v1.json").read_text())
    train_by, canon = {}, {}
    for s, i in D["train_gallery"]:
        train_by.setdefault(i, []).append(s)
    for q in D["queries"]["train"]:
        canon.setdefault(q["ing"], q["cat"])
    held = {q["s"] for k in ("dev_alias", "unseen_alias", "dev", "unseen_concept") for q in D["queries"][k]}
    existing = {s for s, _ in D["train_gallery"]} | {s for s, _ in D["full_gallery_seen_concepts"]}
    name_to_id = {}
    for s, i in D["train_gallery"]:
        name_to_id.setdefault(s, i)
    ids = sorted(train_by)
    aug, negs, stats = {}, {}, {"concepts": len(ids), "calls": 0, "proposed": 0, "kept": 0, "collide_existing": 0, "collide_heldout": 0, "bad_form": 0, "neg_resolved": 0, "neg_total": 0}
    for k in range(0, len(ids), 25):
        batch = ids[k:k + 25]
        txt = "\n".join(f"{i} | {sorted(train_by[i], key=len)[0]} | {canon.get(i, '?')} | {'; '.join(sorted(train_by[i])[:6])}" for i in batch)
        items, pi, po = call(txt)
        stats["calls"] += 1
        with (ROOT / "reports/ner/m31_aux_ledger.jsonl").open("a") as fh:
            fh.write(json.dumps({"task": "linker_augment", "model": MODEL, "batch": k // 25, "concepts": len(batch), "items": len(items), "in": pi, "out": po, "ok": bool(items)}) + "\n")
        for it in items:
            i = it.get("id")
            if i not in train_by:
                continue
            for n in it.get("new", []):
                n2 = norm(n)
                stats["proposed"] += 1
                if not n2 or len(n2.split()) > 4 or re.search(r"\d", n2):
                    stats["bad_form"] += 1
                elif n2 in held:
                    stats["collide_heldout"] += 1
                elif n2 in existing:
                    stats["collide_existing"] += 1
                else:
                    aug.setdefault(i, []).append(n2)
                    stats["kept"] += 1
            for c in it.get("confusable", []):
                stats["neg_total"] += 1
                j = name_to_id.get(norm(c))
                if j and j != i:
                    negs.setdefault(i, []).append(j)
                    stats["neg_resolved"] += 1
        print("batch", k // 25, "of", (len(ids) + 24) // 25, "kept so far", stats["kept"], flush=True)
    (ROOT / "features/linker_aug_v1.json").write_text(json.dumps({"synthetic": True, "model": MODEL, "source": "TRAIN concepts only", "aug": aug, "hard_neg": negs, "stats": stats}))
    print(stats)


if __name__ == "__main__":
    main()
