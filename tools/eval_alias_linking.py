#!/usr/bin/env python3
"""Mention -> ING linking, leave-one-alias-out (Part K.6 / RQ16-28 baseline). Runs in recsys_env (torch+transformers, MPS).

  /opt/anaconda3/envs/recsys_env/bin/python tools/eval_alias_linking.py [--model intfloat/e5-large-v2] [--lang en]
Query = one held-out ALIAS surface of an ING; gallery = every other surface (canonical names + remaining aliases),
the held-out string removed. Hit = the nearest gallery surfaces belong to the same ING. Only ING with >=2 surfaces
after removal are evaluated. Methods: char n-gram TF-IDF (baseline), bi-encoder zero-shot, and their rank fusion (RRF).
Caveat: aliases are ledger-built, so this measures surface-form generalisation, not mention-in-context linking;
mention-level gold stays human-gated (Gold). Buckets: query token count and ING surface-count (frequency proxy).
"""
import argparse
import json
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch
from sklearn.feature_extraction.text import TfidfVectorizer
from transformers import AutoModel, AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.ledgers.store import LedgerStore  # noqa: E402


def norm(s: str) -> str:
    """Copy of vocab.foodon.norm (that module imports lxml, absent from recsys_env); keep in sync."""
    s = "".join(c for c in unicodedata.normalize("NFKD", (s or "").lower()) if not unicodedata.combining(c))
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    words = [w[:-3] + "y" if w.endswith("ies") and len(w) > 4 else
             (w[:-2] if re.search(r"(oes|ches|shes|sses|xes)$", w) else
              (w[:-1] if w.endswith("s") and not w.endswith("ss") and len(w) > 3 else w)) for w in s.split()]
    return " ".join(words)


@torch.no_grad()
def embed(texts, model, tok, dev, prefix, bs=64):
    out = []
    for i in range(0, len(texts), bs):
        b = tok([prefix + t for t in texts[i:i + bs]], padding=True, truncation=True, max_length=32, return_tensors="pt").to(dev)
        h = model(**b).last_hidden_state
        m = b["attention_mask"].unsqueeze(-1)
        v = (h * m).sum(1) / m.sum(1)
        out.append(torch.nn.functional.normalize(v, dim=-1).cpu())
    return torch.cat(out).numpy()


def rank_metrics(sim, gal_ing, q_ing, mask):
    """sim: (nq, ng); mask: (nq, ng) bool, True = excluded gallery item. Returns per-query rank of first same-ING hit."""
    sim = np.where(mask, -9.0, sim)
    order = np.argsort(-sim, axis=1)
    ranks = []
    for i in range(sim.shape[0]):
        hits = np.where(gal_ing[order[i]] == q_ing[i])[0]
        ranks.append(int(hits[0]) + 1 if len(hits) else 10**6)
    return np.array(ranks)


def summarize(r):
    return {"n": int(len(r)), "acc1": float((r == 1).mean()), "r5": float((r <= 5).mean()), "mrr": float((1.0 / r).mean())}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="intfloat/e5-large-v2")
    ap.add_argument("--lang", default="en", help="alias language to evaluate as queries ('all' for every language)")
    ap.add_argument("--out", default=str(ROOT / "reports" / "ner" / "alias_linking_v1.json"))
    a = ap.parse_args()
    st = LedgerStore()
    ing_ids = {i["id"] for i in st.all_latest("ING") if i["status"] == "ACTIVE"}
    surf = []                                    # (surface, ing_id, kind, lang)
    for i in st.all_latest("ING"):
        if i["status"] == "ACTIVE":
            surf.append((norm(i["canonical_name"]), i["id"], "canon", "en"))
    for al in st.all_latest("ALIAS"):
        if al["status"] == "ACTIVE" and al.get("ingredient_id") in ing_ids:
            surf.append((norm(al["normalized"]), al["ingredient_id"], "alias", al["language"]))
    seen, uniq = set(), []
    for s, i, k, l in surf:
        if s and (s, i) not in seen:
            seen.add((s, i)); uniq.append((s, i, k, l))
    texts = [u[0] for u in uniq]
    ing = np.array([u[1] for u in uniq])
    count = defaultdict(int)
    for u in uniq:
        count[u[1]] += 1
    qidx = [j for j, u in enumerate(uniq) if u[2] == "alias" and (a.lang == "all" or u[3] == a.lang) and count[u[1]] >= 2
            and len({v for v in texts if v == u[0]}) == 1]            # surface unique to this ING (unambiguous query)
    print(f"surfaces {len(uniq)}, ING {len(set(ing))}, queries {len(qidx)} (lang={a.lang})", flush=True)
    mask = np.zeros((len(qidx), len(uniq)), bool)
    for r, j in enumerate(qidx):
        mask[r, j] = True
    q_ing = ing[qidx]
    tf = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4), sublinear_tf=True).fit(texts)
    X = tf.transform(texts)
    s_tf = (X[qidx] @ X.T).toarray()
    dev = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    tok = AutoTokenizer.from_pretrained(a.model)
    model = AutoModel.from_pretrained(a.model).to(dev).eval()
    E = embed(texts, model, tok, dev, "query: ")
    s_bi = E[qidx] @ E.T
    def rr(s):
        return np.argsort(np.argsort(-np.where(mask, -9.0, s), axis=1), axis=1) + 1
    s_rrf = 1.0 / (60 + rr(s_tf)) + 1.0 / (60 + rr(s_bi))
    res = {"model": a.model, "lang": a.lang, "n_surfaces": len(uniq), "methods": {}}
    ranks = {"tfidf_char": rank_metrics(s_tf, ing, q_ing, mask), "bi_encoder": rank_metrics(s_bi, ing, q_ing, mask),
             "rrf": rank_metrics(s_rrf, ing, q_ing, mask)}
    ntok = np.array([min(len(texts[j].split()), 3) for j in qidx])
    for m, r in ranks.items():
        res["methods"][m] = {"all": summarize(r), **{f"tokens_{t}{'+' if t == 3 else ''}": summarize(r[ntok == t])
                                                     for t in (1, 2, 3) if (ntok == t).any()}}
    rng = np.random.default_rng(0)
    d = (ranks["bi_encoder"] == 1).astype(float) - (ranks["tfidf_char"] == 1).astype(float)
    boots = [d[rng.integers(0, len(d), len(d))].mean() for _ in range(1000)]
    res["paired_acc1_bi_minus_tfidf"] = {"mean": float(d.mean()), "ci95": [float(np.percentile(boots, 2.5)), float(np.percentile(boots, 97.5))]}
    Path(a.out).write_text(json.dumps(res, indent=1))
    print(json.dumps({m: v["all"] for m, v in res["methods"].items()}, indent=1), res["paired_acc1_bi_minus_tfidf"])


if __name__ == "__main__":
    main()
