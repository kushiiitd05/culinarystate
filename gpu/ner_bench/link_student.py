#!/usr/bin/env python3
"""CulinaryLinkDecision-v1 students CD-L1 (gold only) / CD-L2 (gold + Tev distillation) (python 3.8). Cross-encoder over (mention, candidate text) + a NONE option; softmax over K+1 options.
  python link_student.py --k 5 --lam 0 --seed 1 --out res.json        (lam 0 = CD-L1; lam > 0 = CD-L2)
Train: link_oof.jsonl + teacher_oof_k<K>.jsonl (TRAIN/OOF only). Eval: DEV sets dev_alias / dev from linker_tasks_k10.jsonl (viewed unseen sets and the 441 gold are never read)."""
import argparse
import json
import random
import string
import time

import numpy as np
import torch
from transformers import AutoModel, AutoTokenizer

ENC = "BAAI/bge-small-en-v1.5"


def cand_text(c):
    return c["name"] + (" (also called: " + ", ".join(c["aliases"]) + ")" if c["aliases"] else "")


class Student(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.enc = AutoModel.from_pretrained(ENC)
        self.head = torch.nn.Linear(self.enc.config.hidden_size, 1)

    def forward(self, **b):
        return self.head(self.enc(**b).last_hidden_state[:, 0]).squeeze(-1)


def options(ex, K):
    return [cand_text(c) for c in ex["cands"][:K]] + ["no matching ingredient in the ledger"]


def logits(model, tok, exs, K, dev="cuda"):
    pairs = [(e["mention"], t) for e in exs for t in options(e, K)]
    b = tok([p[0] for p in pairs], [p[1] for p in pairs], padding=True, truncation=True, max_length=64, return_tensors="pt").to(dev)
    with torch.autocast("cuda", dtype=torch.bfloat16):
        s = model(**b)
    return s.float().view(len(exs), K + 1)


def gold_idx(e, K):
    if e["gold"] == "NIL":
        return K
    for i, c in enumerate(e["cands"][:K]):
        if c["id"] == e["gold"]:
            return i
    return -1                                                     # gold not in the K candidates: forced-choice impossible -> ignored in the gold loss


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--k", type=int, default=5)
    ap.add_argument("--lam", type=float, default=0.0)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--epochs", type=int, default=6)
    ap.add_argument("--lr", type=float, default=5e-5)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    random.seed(a.seed), np.random.seed(a.seed), torch.manual_seed(a.seed)
    K = a.k
    keys = list(string.ascii_uppercase[:K]) + ["NONE"]
    tr = [json.loads(l) for l in open("link_oof.jsonl")]
    teach = {}
    for l in open(f"teacher_oof_k{K}.jsonl"):
        r = json.loads(l)
        if r["resp"]:
            p = r["resp"]["answers"]["link"]["probabilities"]
            v = np.array([p.get(k_, 0.0) for k_ in keys]) + 1e-6
            teach[r["id"]] = v / v.sum()
    tr = [e for e in tr if e["id"] in teach]
    dev = [json.loads(l) for l in open("linker_tasks_k10.jsonl")]
    dev = [e for e in dev if e["set"] in ("dev_alias", "dev")]
    tok = AutoTokenizer.from_pretrained(ENC)
    model = Student().cuda()
    opt = torch.optim.AdamW(model.parameters(), lr=a.lr, weight_decay=0.01)
    t0 = time.time()
    for ep in range(a.epochs):
        model.train()
        random.shuffle(tr)
        for i in range(0, len(tr), 16):
            bt = tr[i:i + 16]
            lg = logits(model, tok, bt, K)
            gi = torch.tensor([gold_idx(e, K) for e in bt], device="cuda")
            ce = torch.nn.functional.cross_entropy(lg, gi.clamp(min=0), reduction="none")
            loss = (ce * (gi >= 0).float()).sum() / max((gi >= 0).sum().item(), 1)
            if a.lam > 0:
                T = torch.tensor(np.stack([teach[e["id"]] for e in bt]), device="cuda", dtype=torch.float32)
                loss = loss + a.lam * torch.nn.functional.kl_div(lg.log_softmax(-1), T, reduction="batchmean")
            loss.backward(), torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0), opt.step(), opt.zero_grad()
    model.eval()
    res, lat = {"dev_alias": [], "dev": []}, []
    with torch.no_grad():
        for e in dev:
            t1 = time.time()
            lg = logits(model, tok, [e], K)[0].softmax(-1).cpu().numpy()
            lat.append(1000 * (time.time() - t1))
            forced = int(np.argmax(lg[:K]))
            res[e["set"]].append({"id": e["id"], "gold": e["gold"], "forced": e["cands"][forced]["id"], "pnone": float(lg[K]), "default_none": bool(np.argmax(lg) == K), "default": ("NONE" if np.argmax(lg) == K else e["cands"][int(np.argmax(lg))]["id"]),
                                  "in_pool": any(c["id"] == e["gold"] for c in e["cands"][:K])})
    pos, nil = res["dev_alias"], res["dev"]
    from sklearn.metrics import roc_auc_score, average_precision_score
    y = [0] * len(pos) + [1] * len(nil)
    s = [r["pnone"] for r in pos + nil]
    out = {"k": K, "lam": a.lam, "seed": a.seed, "dev_alias_forced_acc": float(np.mean([r["forced"] == r["gold"] for r in pos])), "dev_alias_default_acc": float(np.mean([r["default"] == r["gold"] for r in pos])),
           "oracle": float(np.mean([r["in_pool"] for r in pos])), "NIL_AUROC": float(roc_auc_score(y, s)), "NIL_AUPRC": float(average_precision_score(y, s)), "NIL_recall_default": float(np.mean([r["default_none"] for r in nil])),
           "false_NONE_on_aliases": float(np.mean([r["default_none"] for r in pos])), "latency_ms_median_gpu_bs1": float(np.median(lat)), "params_M": round(sum(p.numel() for p in model.parameters()) / 1e6, 1), "train_min": round((time.time() - t0) / 60, 2),
           "forced_correct_ids": [r["id"] for r in pos if r["forced"] == r["gold"]]}
    json.dump(out, open(a.out, "w"))
    print({k_: v for k_, v in out.items() if k_ != "forced_correct_ids"})


if __name__ == "__main__":
    main()
