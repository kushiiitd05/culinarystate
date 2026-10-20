#!/usr/bin/env python3
"""S119 Part XI prep (laptop): ING-family-grouped data for the contrastive ingredient linker.

  nice -n 10 /opt/anaconda3/bin/python tools/build_linker_data.py   # -> features/linker_data_v1.json (local, built from the ledgers)
Surfaces = ING canonical names + ACTIVE aliases (norm()). Split BY ING (hash bucket, concept-grouped): train 70% / dev 10% / test 20% of concepts.
Two test regimes, both leakage-controlled:
  unseen_concept : every surface of a TEST concept is a query and the concept is REMOVED from the gallery -> gold = NIL (tests NIL / novel handling);
  unseen_alias   : 20% of aliases (hash bucket) of TRAIN concepts are held out as queries; gallery keeps the concept's other surfaces.
Train queries never include held-out aliases. Hard negatives per train surface: lexical (char TF-IDF top neighbours of OTHER concepts), same category,
shared head token (form / compound variants). Embedding neighbours are mined on the A100 from the first-round model."""
import hashlib
import json
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.ledgers.store import LedgerStore  # noqa: E402


def norm(s):
    s = "".join(c for c in unicodedata.normalize("NFKD", (s or "").lower()) if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]+", " ", s)).strip()


def bucket(key):
    return int(hashlib.sha256(f"LINK-v1|{key}".encode()).hexdigest()[:12], 16) / 16 ** 12


def main():
    st = LedgerStore()
    ings = {i["id"]: i for i in st.all_latest("ING") if i["status"] == "ACTIVE"}
    surf = {}
    for iid, i in ings.items():
        surf[(norm(i["canonical_name"]), iid)] = ("canon", "en")
    for a in st.all_latest("ALIAS"):
        if a["status"] == "ACTIVE" and a.get("ingredient_id") in ings and norm(a["normalized"]):
            surf.setdefault((norm(a["normalized"]), a["ingredient_id"]), ("alias", a["language"]))
    by = defaultdict(list)
    for (s, iid), (kind, lang) in surf.items():
        by[iid].append({"s": s, "kind": kind, "lang": lang})
    multi = {i for i, v in by.items() if len(v) >= 2}                     # need >= 2 surfaces for alias queries
    cb = {i: bucket(i) for i in by}
    split = {i: ("test" if cb[i] >= 0.8 else "dev" if cb[i] >= 0.7 else "train") for i in by}
    # surface-level: ambiguous surfaces (same normalised string for two concepts) are dropped from queries
    count = defaultdict(set)
    for (s, iid) in surf:
        count[s].add(iid)
    amb = {s for s, v in count.items() if len(v) > 1}
    queries = {"train": [], "unseen_alias": [], "dev_alias": [], "dev": [], "unseen_concept": []}
    for iid, items in by.items():
        for it in items:
            if it["s"] in amb:
                continue
            row = {"s": it["s"], "ing": iid, "lang": it["lang"], "kind": it["kind"], "cat": ings[iid]["category"], "n_surf": len(items)}
            if split[iid] == "test":
                queries["unseen_concept"].append({**row, "gold": "NIL"})
            elif split[iid] == "dev":
                queries["dev"].append({**row, "gold": "NIL"})
            elif it["kind"] == "alias" and iid in multi and bucket("A|" + it["s"] + iid) < 0.2:
                queries["unseen_alias"].append({**row, "gold": iid})
            elif it["kind"] == "alias" and iid in multi and bucket("A|" + it["s"] + iid) < 0.3:
                queries["dev_alias"].append({**row, "gold": iid})
            else:
                queries["train"].append({**row, "gold": iid})
    held = {(q["s"], q["ing"]) for k in ("unseen_alias", "dev_alias") for q in queries[k]}
    gallery = {"train_gallery": sorted({(it["s"], iid) for iid, v in by.items() if split[iid] == "train" for it in v if (it["s"], iid) not in held}),
               "full_gallery_seen_concepts": sorted({(it["s"], iid) for iid, v in by.items() if split[iid] != "test" for it in v if (it["s"], iid) not in held})}
    # hard negatives for train queries (lexical + category + head token), other concepts only
    tg = gallery["train_gallery"]
    texts = [s for s, _ in tg]
    vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4)).fit(texts)
    G = vec.transform(texts)
    head = defaultdict(list)
    for k, (s, iid) in enumerate(tg):
        head[s.split()[-1]].append(k)
    bycat = defaultdict(list)
    for k, (s, iid) in enumerate(tg):
        bycat[ings[iid]["category"]].append(k)
    rng = np.random.RandomState(0)
    for q in queries["train"]:
        sims = (vec.transform([q["s"]]) @ G.T).toarray()[0]
        lex = [tg[k][1] for k in np.argsort(-sims)[:40] if tg[k][1] != q["ing"]][:8]
        hd = [tg[k][1] for k in head.get(q["s"].split()[-1], []) if tg[k][1] != q["ing"]][:4]
        cat = [tg[k][1] for k in rng.choice(bycat[q["cat"]], min(4, len(bycat[q["cat"]])), replace=False) if tg[k][1] != q["ing"]]
        q["hard_neg"] = {"lexical": lex, "head_token": hd, "category": cat}
    out = {"n_ing": len(by), "split_counts": {k: sum(v == k for v in split.values()) for k in ("train", "dev", "test")},
           "queries": queries, **{k: [list(x) for x in v] for k, v in gallery.items()}, "ambiguous_surfaces_dropped": len(amb)}
    (ROOT / "features").mkdir(exist_ok=True)
    (ROOT / "features" / "linker_data_v1.json").write_text(json.dumps(out))
    print({k: len(v) for k, v in queries.items()}, out["split_counts"], "gallery", {k: len(v) for k, v in gallery.items()}, "amb", len(amb))


if __name__ == "__main__":
    main()
