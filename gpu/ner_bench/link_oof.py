#!/usr/bin/env python3
"""CulinaryLinkDecision-v1 step 3 (python 3.8): concept- and alias-grouped 5-fold OOF candidate generation with the frozen BGE v2 recipe. See reports/ner_v2/culinary_link_decision_v1_protocol.md section 2.
  python link_oof.py --data linker_data_v2.json --names ledger_names.json --out link_oof.jsonl"""
import argparse
import hashlib
import json
import random
from collections import defaultdict

import numpy as np
import torch
from transformers import AutoModel, AutoTokenizer

MODEL = "BAAI/bge-large-en-v1.5"
H = lambda s: int(hashlib.sha256(s.encode()).hexdigest()[:8], 16) % 5


def embed(model, tok, texts, grad=False, bs=256):
    outs = []
    for i in range(0, len(texts), bs):
        b = tok(texts[i:i + bs], padding=True, truncation=True, max_length=32, return_tensors="pt").to("cuda")
        with torch.set_grad_enabled(grad), torch.autocast("cuda", dtype=torch.bfloat16):
            h = model(**b).last_hidden_state[:, 0]
        outs.append(torch.nn.functional.normalize(h.float(), dim=-1))
    return torch.cat(outs)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--names", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    D = json.load(open(a.data))
    names = json.load(open(a.names))
    train_q, gallery = D["queries"]["train"], [tuple(x) for x in D["train_gallery"]]
    tok = AutoTokenizer.from_pretrained(MODEL)
    out = open(a.out, "w")
    for k in range(5):
        random.seed(1), np.random.seed(1), torch.manual_seed(1)
        held = {i for _, i in gallery if H("LD1|c|" + i) == k} | {q["ing"] for q in train_q if H("LD1|c|" + q["ing"]) == k}
        cnt = defaultdict(list)
        for s_, i_ in gallery:
            cnt[i_].append(s_)
        al_held = {(q["s"], q["ing"]) for q in train_q if q["ing"] not in held and len(cnt[q["ing"]]) >= 2 and H("LD1|a|" + q["s"] + q["ing"]) == k}   # any surface (canonical or alias) of a multi-surface concept
        for i_ in {i for _, i in al_held}:                                                                                                    # a concept must keep >= 1 surface in the gallery
            if all((s_, i_) in al_held for s_ in cnt[i_]):
                al_held.discard(sorted((s_, i_) for s_ in cnt[i_])[0])
        G = [(s, i) for s, i in gallery if i not in held and (s, i) not in al_held]
        by = defaultdict(list)
        for s, i in G:
            by[i].append(s)
        trq = [q for q in train_q if q["ing"] not in held and (q["s"], q["ing"]) not in al_held and len(by[q["ing"]]) >= 2]
        model = AutoModel.from_pretrained(MODEL).cuda()
        opt = torch.optim.AdamW(model.parameters(), lr=1e-5, weight_decay=0.01)
        rng = random.Random(1)
        for ep in range(4):
            model.train()
            rng.shuffle(trq)
            for i in range(0, len(trq) - 64 + 1, 64):
                qs = trq[i:i + 64]
                pos = [rng.choice([x for x in by[q["ing"]] if x != q["s"]] or [q["s"]]) for q in qs]
                neg = []
                for q in qs:
                    hn = [c for kk in ("lexical", "head_token", "category") for c in q["hard_neg"].get(kk, []) if by.get(c)]
                    neg.append(rng.choice(by[rng.choice(hn)]) if hn else rng.choice(G)[0])
                Q, P, N = embed(model, tok, [q["s"] for q in qs], True), embed(model, tok, pos, True), embed(model, tok, neg, True)
                logits = (Q @ torch.cat([P, N]).T) / 0.05
                idl = [q["ing"] for q in qs]
                same = torch.tensor([[x == y for y in idl + [None] * len(neg)] for x in idl], device=logits.device)
                same[:, :len(qs)] &= ~torch.eye(len(qs), dtype=torch.bool, device=logits.device)
                loss = torch.nn.functional.cross_entropy(logits.masked_fill(same, -1e4), torch.arange(len(qs), device=logits.device))
                loss.backward(), opt.step(), opt.zero_grad()
        model.eval()
        Gm = embed(model, tok, [s for s, _ in G])
        gid = [i for _, i in G]
        items = [("pos", q) for q in train_q if (q["s"], q["ing"]) in al_held] + [("nil", q) for q in train_q if q["ing"] in held]
        S = (embed(model, tok, [q["s"] for _, q in items]) @ Gm.T).cpu().numpy()
        for (kind, q), s in zip(items, S):
            seen, cands = set(), []
            for j in np.argsort(-s)[:80]:
                if gid[j] not in seen:
                    seen.add(gid[j])
                    c = gid[j]
                    cands.append({"id": c, "score": round(float(s[j]), 4), "name": names.get(c, by[c][0]), "aliases": [x for x in by[c] if x != names.get(c)][:3]})
                if len(cands) == 10:
                    break
            out.write(json.dumps({"id": f"oof{k}-{len(cands)}-{abs(hash(q['s'])) % 10**6}-{kind}", "fold": k, "kind": kind, "mention": q["s"], "gold": q["ing"] if kind == "pos" else "NIL", "n_surf": q["n_surf"], "cands": cands}) + "\n")
        out.flush()
        print("fold", k, "gallery surfaces", len(G), "train queries", len(trq), "pos", sum(1 for t, _ in items if t == "pos"), "nil", sum(1 for t, _ in items if t == "nil"), flush=True)
        del model, opt
        torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
