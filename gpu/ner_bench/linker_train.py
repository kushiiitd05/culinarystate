#!/usr/bin/env python3
"""S119 Part XI: contrastive ingredient linker (e5 bi-encoder, InfoNCE with mined hard negatives) on features/linker_data_v1.json (python 3.8 safe).

  python linker_train.py --data linker_data_v1.json --seed 1 [--epochs 4]
Round 0 = zero-shot e5 (and a char TF-IDF baseline). Train queries/gallery never contain held-out aliases or test/dev concepts.
Eval: unseen_alias (gold = concept) + unseen_concept (concept removed from gallery, gold = NIL). NIL threshold tau on top-1 cosine is chosen on
dev_alias (positives) + dev (NIL) only. Reports Acc@1/@5/MRR, NIL P/R, by head/tail, en/regional, token length. Saves top-5 tables for the router."""
from __future__ import annotations

import argparse
import json
import random
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModel, AutoTokenizer

MODEL = "intfloat/e5-large-v2"


FMT = {"plain": "query: ", "ing": "query: ingredient name: "}
PREFIX = FMT["plain"]


def embed(model, tok, texts, dev, bs=256, grad=False):
    outs = []
    for i in range(0, len(texts), bs):
        b = tok([PREFIX + t for t in texts[i:i + bs]], padding=True, truncation=True, max_length=32, return_tensors="pt").to(dev)
        with torch.set_grad_enabled(grad), torch.autocast("cuda", dtype=torch.bfloat16, enabled=dev == "cuda"):
            h = model(**b).last_hidden_state
        m = b["attention_mask"].unsqueeze(-1)
        outs.append(torch.nn.functional.normalize(((h * m).sum(1) / m.sum(1)).float(), dim=-1))
    return torch.cat(outs)


def evaluate(model, tok, D, dev, tau=None):
    gal = D["full_gallery_seen_concepts"]
    G = embed(model, tok, [s for s, _ in gal], dev)
    gid = np.array([i for _, i in gal])

    def run(qs):
        Q = embed(model, tok, [q["s"] for q in qs], dev)
        S = (Q @ G.T).cpu().numpy()
        top = np.argsort(-S, axis=1)[:, :50]
        return S, top

    res = {}
    for name in ("unseen_alias", "dev_alias", "dev", "unseen_concept"):
        qs = D["queries"][name]
        S, top = run(qs)
        rows = []
        for q, s, t in zip(qs, S, top):
            ids, seen = [], set()
            for k in t:                                                    # rank concepts, not surfaces
                if gid[k] not in seen:
                    seen.add(gid[k])
                    ids.append((gid[k], float(s[k])))
                if len(ids) == 5:
                    break
            rows.append({"gold": q["gold"], "top": ids, "lang": q["lang"], "n_surf": q["n_surf"], "ntok": len(q["s"].split())})
        res[name] = rows
    if tau is None:                                                        # choose tau on dev only: positives = dev_alias, NIL = dev
        cand = np.linspace(0.5, 1.0, 101)
        best, tau = -1, 0.8
        pos, neg = [r["top"][0][1] for r in res["dev_alias"]], [r["top"][0][1] for r in res["dev"]]
        for c in cand:
            bal = 0.5 * (np.mean([p >= c for p in pos]) + np.mean([n < c for n in neg]))
            if bal > best:
                best, tau = bal, float(c)
    rd = np.array([next((i + 1 for i, (c, _) in enumerate(r["top"]) if c == r["gold"]), 10**6) for r in res["dev_alias"]])
    dev_metrics = {"n": int(len(rd)), "acc1": float((rd == 1).mean()), "r5": float((rd <= 5).mean()), "mrr": float((1.0 / rd).mean())}   # SELECTION metric (dev_alias), not the held-out test queries
    pos = res["unseen_alias"]
    rk = np.array([next((i + 1 for i, (c, _) in enumerate(r["top"]) if c == r["gold"]), 10**6) for r in pos])
    bucket = lambda f: {"n": int(f.sum()), "acc1": float((rk[f] == 1).mean()) if f.any() else None, "r5": float((rk[f] <= 5).mean()) if f.any() else None}
    en = np.array([r["lang"] == "en" for r in pos])
    nsf = np.array([r["n_surf"] for r in pos])
    ntok = np.array([r["ntok"] for r in pos])
    nil_neg = res["unseen_concept"]
    tp = sum(r["top"][0][1] < tau for r in nil_neg)                       # NIL correctly flagged
    fp_nil = sum(r["top"][0][1] < tau for r in pos)                       # real concept wrongly flagged NIL
    out = {"tau": tau, "dev_alias_selection": dev_metrics, "unseen_alias": {**bucket(np.ones(len(rk), bool)), "mrr": float((1.0 / rk).mean())},
           "by_lang": {"en": bucket(en), "regional": bucket(~en)}, "by_concept_surfaces": {"head_ge6": bucket(nsf >= 6), "tail_le3": bucket(nsf <= 3)},
           "by_tokens": {"1": bucket(ntok == 1), "2": bucket(ntok == 2), "3plus": bucket(ntok >= 3)},
           "nil": {"precision": tp / max(tp + fp_nil, 1), "recall": tp / max(len(nil_neg), 1), "n_nil": len(nil_neg), "n_pos": len(pos)}}
    return out, res


def tfidf_baseline(D):
    from sklearn.feature_extraction.text import TfidfVectorizer
    gal = D["full_gallery_seen_concepts"]
    vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4)).fit([s for s, _ in gal])
    G = vec.transform([s for s, _ in gal])
    gid = np.array([i for _, i in gal])
    qs = D["queries"]["unseen_alias"]
    S = (vec.transform([q["s"] for q in qs]) @ G.T).toarray()
    acc = np.mean([gid[int(np.argmax(s))] == q["gold"] for q, s in zip(qs, S)])
    return float(acc)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="linker_data_v1.json")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--epochs", type=int, default=4)
    ap.add_argument("--bs", type=int, default=64)
    ap.add_argument("--lr", type=float, default=1e-5)
    ap.add_argument("--temp", type=float, default=0.05)
    ap.add_argument("--fmt", choices=["plain", "ing"], default="plain", help="input prompt format for query/passage text")
    ap.add_argument("--tag", default="")
    ap.add_argument("--round2", type=int, default=0, help="extra epochs after mining EMBEDDING-neighbour hard negatives from the round-1 model (contract: nearest embedding candidates)")
    ap.add_argument("--out", default="runs")
    a = ap.parse_args()
    global PREFIX
    PREFIX = FMT[a.fmt]
    random.seed(a.seed), np.random.seed(a.seed), torch.manual_seed(a.seed)
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    D = json.loads(Path(a.data).read_text())
    tok = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModel.from_pretrained(MODEL).to(dev)
    by = defaultdict(list)
    for s, i in D["train_gallery"]:
        by[i].append(s)
    zero, _ = evaluate(model, tok, D, dev)
    rng = random.Random(a.seed)
    opt = torch.optim.AdamW(model.parameters(), lr=a.lr, weight_decay=0.01)
    trq = [q for q in D["queries"]["train"] if len(by[q["ing"]]) >= 2]
    t0, hist = time.time(), []
    sur2ing = {sv: i for sv, i in D["train_gallery"]}

    def run_epochs(n, offset):
        for ep in range(1, n + 1):
            model.train()
            rng.shuffle(trq)
            for i in range(0, len(trq) - a.bs + 1, a.bs):
                qs = trq[i:i + a.bs]
                pos = [rng.choice([s_ for s_ in by[q["ing"]] if s_ != q["s"]] or [q["s"]]) for q in qs]
                neg = []
                for q in qs:
                    hn = [c for k in ("lexical", "head_token", "category", "embed") for c in q["hard_neg"].get(k, []) if by.get(c)]
                    neg.append(rng.choice(by[rng.choice(hn)]) if hn else rng.choice(D["train_gallery"])[0])
                Q = embed(model, tok, [q["s"] for q in qs], dev, grad=True)
                P = embed(model, tok, pos, dev, grad=True)
                N = embed(model, tok, neg, dev, grad=True)
                logits = (Q @ torch.cat([P, N]).T) / a.temp
                idl = [q["ing"] for q in qs]
                same = torch.tensor([[x == y for y in idl + [None] * len(neg)] for x in idl], device=logits.device)
                same[:, :len(qs)] &= ~torch.eye(len(qs), dtype=torch.bool, device=logits.device)
                logits = logits.masked_fill(same, -1e4)
                loss = torch.nn.functional.cross_entropy(logits, torch.arange(len(qs), device=logits.device))
                loss.backward(), opt.step(), opt.zero_grad()
            hist.append({"epoch": offset + ep, "loss": round(loss.item(), 4)})
            print(hist[-1], flush=True)

    run_epochs(a.epochs, 0)
    if a.round2 > 0:                                   # mine embedding-neighbour hard negatives (other concepts) from the round-1 model, train more
        model.eval()
        G = embed(model, tok, [s_ for s_, _ in D["train_gallery"]], dev)
        gid = [i for _, i in D["train_gallery"]]
        Qe = embed(model, tok, [q["s"] for q in trq], dev)
        top = (Qe @ G.T).topk(12, dim=1).indices.cpu().tolist()
        for q, t in zip(trq, top):
            q["hard_neg"]["embed"] = [gid[k] for k in t if gid[k] != q["ing"]][:6]
        run_epochs(a.round2, a.epochs)
    model.eval()
    final, res = evaluate(model, tok, D, dev)
    out = Path(a.out)
    out.mkdir(exist_ok=True)
    (out / f"linker__e5-large-v2{a.tag}__seed{a.seed}.json").write_text(json.dumps({"zero_shot_e5": zero, "contrastive": final, "tfidf_char_acc1_unseen_alias": tfidf_baseline(D), "history": hist,
                                                                           "minutes": round((time.time() - t0) / 60, 2), "hparams": vars(a), "fmt": a.fmt}, indent=1))
    (out / f"linker__e5-large-v2{a.tag}__seed{a.seed}.tables.json").write_text(json.dumps({k: res[k] for k in ("unseen_alias", "unseen_concept", "dev_alias", "dev")}))
    print("zero-shot acc1", zero["unseen_alias"]["acc1"], "contrastive acc1", final["unseen_alias"]["acc1"], "nil", final["nil"])


if __name__ == "__main__":
    main()
