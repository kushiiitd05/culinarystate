#!/usr/bin/env python3
"""S119 Part XI selector: cross-encoder RERANKER for the canonical linker (design contract: mention -> bi-encoder top-K -> hard-negative selector -> calibrated link score).
Candidates come from the ZERO-SHOT e5 retriever (top-K concepts), so the reranker is trained on the retriever's real mistakes (hard negatives by construction).
Cross-encoder = BAAI/bge-reranker-large (open weights, cached on the server), fine-tuned with listwise CE (1 positive + K-1 negatives per query) on TRAIN queries only.
Setting selection uses dev_alias (positives) + dev (NIL) only; unseen_alias / unseen_concept are reported for the frozen setting. Saves top-5 score tables for the router.

  python rerank_train.py --seed 1 --epochs 2 [--zero-shot]      (python 3.8 safe)"""
from __future__ import annotations

import argparse
import json
import random
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModel, AutoModelForSequenceClassification, AutoTokenizer

RET = "intfloat/e5-large-v2"
K = 10


@torch.no_grad()
def embed(model, tok, texts, dev, bs=256):
    outs = []
    for i in range(0, len(texts), bs):
        b = tok(["query: " + t for t in texts[i:i + bs]], padding=True, truncation=True, max_length=32, return_tensors="pt").to(dev)
        with torch.autocast("cuda", dtype=torch.bfloat16, enabled=dev == "cuda"):
            h = model(**b).last_hidden_state
        m = b["attention_mask"].unsqueeze(-1)
        outs.append(torch.nn.functional.normalize(((h * m).sum(1) / m.sum(1)).float(), dim=-1))
    return torch.cat(outs)


def candidates(Q, G, gid, k=K):
    """top-k distinct concepts per query: list of [(concept, best_surface_idx, cosine)]."""
    S = (Q @ G.T).cpu().numpy()
    out = []
    for s in S:
        seen, row = set(), []
        for j in np.argsort(-s)[:60]:
            if gid[j] not in seen:
                seen.add(gid[j])
                row.append((gid[j], int(j), float(s[j])))
            if len(row) == k:
                break
        out.append(row)
    return out


def score_pairs(model, tok, pairs, dev, bs=128):
    out = []
    for i in range(0, len(pairs), bs):
        b = tok([p[0] for p in pairs[i:i + bs]], [p[1] for p in pairs[i:i + bs]], padding=True, truncation=True, max_length=48, return_tensors="pt").to(dev)
        with torch.no_grad(), torch.autocast("cuda", dtype=torch.bfloat16, enabled=dev == "cuda"):
            out.append(model(**b).logits.squeeze(-1).float().cpu())
    return torch.cat(out).numpy() if out else np.zeros(0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="linker_data_v1.json")
    ap.add_argument("--model", default="BAAI/bge-reranker-large")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--epochs", type=int, default=2)
    ap.add_argument("--lr", type=float, default=1e-5)
    ap.add_argument("--bs", type=int, default=8)
    ap.add_argument("--zero-shot", action="store_true", help="evaluate without fine-tuning")
    ap.add_argument("--tag", default="")
    ap.add_argument("--out", default="runs")
    a = ap.parse_args()
    random.seed(a.seed), np.random.seed(a.seed), torch.manual_seed(a.seed)
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    D = json.loads(Path(a.data).read_text())
    rt, rm = AutoTokenizer.from_pretrained(RET), AutoModel.from_pretrained(RET).to(dev).eval()
    gal = D["full_gallery_seen_concepts"]
    G, gid = embed(rm, rt, [s for s, _ in gal], dev), [i for _, i in gal]
    tgal = D["train_gallery"]
    TG, tid = embed(rm, rt, [s for s, _ in tgal], dev), [i for _, i in tgal]
    tr_by = defaultdict(list)
    for s, i in tgal:
        tr_by[i].append(s)
    ct = AutoTokenizer.from_pretrained(a.model)
    ce = AutoModelForSequenceClassification.from_pretrained(a.model, num_labels=1).to(dev)
    t0, hist = time.time(), []
    if not a.zero_shot:
        trq = [q for q in D["queries"]["train"] if len(tr_by[q["ing"]]) >= 2]
        Qt = embed(rm, rt, [q["s"] for q in trq], dev)
        cand = candidates(Qt, TG, tid, K + 1)
        opt = torch.optim.AdamW(ce.parameters(), lr=a.lr, weight_decay=0.01)
        rng = random.Random(a.seed)
        order = list(range(len(trq)))
        for ep in range(1, a.epochs + 1):
            ce.train()
            rng.shuffle(order)
            for i in range(0, len(order) - a.bs + 1, a.bs):
                pairs, groups = [], []
                for n in order[i:i + a.bs]:
                    q = trq[n]
                    pos = rng.choice([s for s in tr_by[q["ing"]] if s != q["s"]] or [q["s"]])
                    neg = [(c, tgal[j][0]) for c, j, _ in cand[n] if c != q["ing"]][:K - 1]
                    items = [pos] + [s for _, s in neg]
                    pairs += [(q["s"], s) for s in items]
                    groups.append(len(items))
                b = ct([p[0] for p in pairs], [p[1] for p in pairs], padding=True, truncation=True, max_length=48, return_tensors="pt").to(dev)
                with torch.autocast("cuda", dtype=torch.bfloat16, enabled=dev == "cuda"):
                    sc = ce(**b).logits.squeeze(-1).float()
                loss, pos_i = 0.0, 0
                for g in groups:
                    loss = loss + torch.nn.functional.cross_entropy(sc[pos_i:pos_i + g].unsqueeze(0), torch.zeros(1, dtype=torch.long, device=sc.device))
                    pos_i += g
                (loss / len(groups)).backward(), opt.step(), opt.zero_grad()
            hist.append({"epoch": ep, "loss": round(float(loss) / len(groups), 4)})
            print(hist[-1], flush=True)
    ce.eval()
    tables, res = {}, {}
    for name in ("unseen_alias", "dev_alias", "dev", "unseen_concept"):
        qs = D["queries"][name]
        cand = candidates(embed(rm, rt, [q["s"] for q in qs], dev), G, gid, K)
        pairs, meta = [], []
        for n, (q, row) in enumerate(zip(qs, cand)):
            for c, j, cos in row:
                pairs.append((q["s"], gal[j][0]))
                meta.append((n, c, cos))
        sc = score_pairs(ce, ct, pairs, dev)
        per = defaultdict(list)
        for (n, c, cos), s in zip(meta, sc):
            per[n].append((c, float(s), cos))
        rows = []
        for n, q in enumerate(qs):
            ranked = sorted(per[n], key=lambda x: -x[1])[:5]
            rows.append({"gold": q["gold"], "top": [(c, s) for c, s, _ in ranked], "retr_top": [(c, cos) for c, _, cos in sorted(per[n], key=lambda x: -x[2])[:5]], "lang": q["lang"], "n_surf": q["n_surf"], "ntok": len(q["s"].split())})
        tables[name] = rows

    def metrics(rows, key):
        rk = np.array([next((i + 1 for i, (c, _) in enumerate(r[key]) if c == r["gold"]), 10**6) for r in rows])
        return {"n": int(len(rk)), "acc1": float((rk == 1).mean()), "r5": float((rk <= 5).mean()), "mrr": float((1.0 / rk).mean())}
    dev_m = {"reranked": metrics(tables["dev_alias"], "top"), "retriever": metrics(tables["dev_alias"], "retr_top")}
    pos_s, neg_s = [r["top"][0][1] for r in tables["dev_alias"]], [r["top"][0][1] for r in tables["dev"]]
    cands_tau = np.linspace(min(pos_s + neg_s), max(pos_s + neg_s), 200)
    tau = max(cands_tau, key=lambda c: 0.5 * (np.mean([p >= c for p in pos_s]) + np.mean([n < c for n in neg_s])))
    tp = sum(r["top"][0][1] < tau for r in tables["unseen_concept"])
    fp = sum(r["top"][0][1] < tau for r in tables["unseen_alias"])
    out = {"dev_alias_selection": dev_m, "unseen_alias": {"reranked": metrics(tables["unseen_alias"], "top"), "retriever": metrics(tables["unseen_alias"], "retr_top")},
           "tau_on_dev": float(tau), "nil": {"precision": tp / max(tp + fp, 1), "recall": tp / max(len(tables["unseen_concept"]), 1)}, "history": hist, "minutes": round((time.time() - t0) / 60, 2), "hparams": vars(a)}
    out_dir = Path(a.out)
    out_dir.mkdir(exist_ok=True)
    name = f"rerank__{a.model.split('/')[-1]}{'_zs' if a.zero_shot else ''}{a.tag}__seed{a.seed}"
    (out_dir / f"{name}.json").write_text(json.dumps(out, indent=1))
    (out_dir / f"{name}.tables.json").write_text(json.dumps(tables))
    print(name, "dev_alias acc1 reranked", round(dev_m["reranked"]["acc1"], 3), "retriever", round(dev_m["retriever"]["acc1"], 3), "| unseen_alias", round(out["unseen_alias"]["reranked"]["acc1"], 3), "nil", out["nil"])


if __name__ == "__main__":
    main()
