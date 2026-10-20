#!/usr/bin/env python3
"""S119 E3/E4: encoder + span-knowledge metadata fusion -> CRF on the frozen benchmark (python 3.8 safe).

  python fusion_train.py --dataset tasteset --model microsoft/deberta-base --mode gated --feats tasteset_span_feats_v1.npz --seed 1
Metadata m_i comes from the Mac-built, cross-fitted span tables (features/<ds>_span_feats_v1.npz). Fusion: 'concat' z=LN([h;m']) or 'gated'
z = g*h + (1-g)*P m', g = sigmoid(W[h;m'] + b), b init +3 (g ~ 1). Whole-sentence metadata dropout p=0.3 in training. Encoder confidence / entropy are
NOT inputs (calibrator-only). --feats-eval swaps the table for calibration/test (alias-swap and coverage stress tests). --zero-meta = ablation.
Checkpoint = dev exact micro F1 (benchmark rule). Trains from the pretrained encoder with the same budget as E0 (no E0 weights are stored)."""
from __future__ import annotations

import argparse
import json
import random
import time
from pathlib import Path

import numpy as np
import torch
from torch import nn
from transformers import AutoModel, AutoTokenizer, get_linear_schedule_with_warmup

import bench_train as T
from bench_train import B, M, CRF, compact

D_META_DROP = 0.3


class Fused(nn.Module):
    def __init__(self, name, n_tags, d_meta, mode):
        super().__init__()
        self.enc, self.mode = AutoModel.from_pretrained(name), mode
        H = self.enc.config.hidden_size
        self.meta = nn.Sequential(nn.Linear(d_meta, H), nn.GELU(), nn.Dropout(0.1))
        if mode == "gated":
            self.gate, self.proj, self.cls = nn.Linear(2 * H, H), nn.Linear(H, H), nn.Linear(H, n_tags)
            nn.init.constant_(self.gate.bias, 3.0)
        else:
            self.ln, self.cls = nn.LayerNorm(2 * H), nn.Linear(2 * H, n_tags)
        self.last_gate = None

    def forward(self, ids, att, meta, keep):
        h = self.enc(input_ids=ids, attention_mask=att).last_hidden_state
        m = self.meta(meta * keep.view(-1, 1, 1))
        if self.mode == "gated":
            g = torch.sigmoid(self.gate(torch.cat([h, m], -1)))
            self.last_gate = g.detach()
            return self.cls(g * h + (1 - g) * self.proj(m))
        return self.cls(self.ln(torch.cat([h, m], -1)))


def item_meta(items, widx, table, off, doc_ids, d):
    out = []
    for it, wi, k in zip(items, widx, doc_ids):
        rows = table[off[k]:off[k + 1]]
        m = np.zeros((len(it[0]), d), np.float16)
        for p, w in enumerate(wi):
            if 0 <= w < len(rows):
                m[p] = rows[w]
        out.append(m)
    return out


def collate(order, metas, d, L):
    return torch.tensor(np.stack([np.pad(metas[j], ((0, L - len(metas[j])), (0, 0))) for j in order]), dtype=torch.float32)


@torch.no_grad()
def predict_f(model, crf, items, metas, id2tag, dev, d, zero=False):
    model.eval()
    out, gates = [None] * len(items), []
    for ids, att, y, order in T.batches(items, 32, False, None):
        meta = collate(order, metas, d, ids.size(1)).to(dev)
        with torch.autocast("cuda", dtype=torch.bfloat16, enabled=dev == "cuda"):
            em = model(ids.to(dev), att.to(dev), meta, torch.zeros(len(order), device=dev) if zero else torch.ones(len(order), device=dev))
        e, cm, idx = compact(em.float(), (y != -100).to(dev))
        if model.last_gate is not None:
            gates.append(model.last_gate[(y != -100).to(dev)].float().mean().item())
        for b, path in enumerate(crf.decode(e, cm)):
            row = [0] * em.size(1)
            for j, tag in enumerate(path):
                row[int(idx[b, j])] = tag
            out[order[b]] = T.decode(row[:len(items[order[b]][0])], items[order[b]][2], id2tag)
    return out, (float(np.mean(gates)) if gates else None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True, choices=["tasteset", "recipedb3"])
    ap.add_argument("--model", required=True)
    ap.add_argument("--mode", choices=["concat", "gated"], default="gated")
    ap.add_argument("--feats", required=True)
    ap.add_argument("--feats-eval", default="")
    ap.add_argument("--tag", default="")
    ap.add_argument("--zero-meta", action="store_true")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--epochs", type=int, default=15)
    ap.add_argument("--bs", type=int, default=16)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", default="runs")
    a = ap.parse_args()
    random.seed(a.seed), np.random.seed(a.seed), torch.manual_seed(a.seed)
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    here = T.HERE
    data = str(here / ("TASTEset.csv" if a.dataset == "tasteset" else "Ingredient_Annotated_Dataset.csv"))
    split = json.loads((here / f"{a.dataset}_split_v1.json").read_text())["indices"]
    docs = T.load_docs(a.dataset, data)
    view = T.PRIMARY[a.dataset]
    labels = sorted(B.VIEWS[view])
    tags = ["O"] + [f"{p}-{l}" for l in labels for p in ("B", "I")]
    tag2id = {t: i for i, t in enumerate(tags)}
    id2tag = {i: t for t, i in tag2id.items()}
    lr = 2e-5 if "large" in a.model else 5e-5
    max_len = 256 if a.dataset == "tasteset" else 128
    need_prefix = "roberta" in a.model or ("deberta" in a.model and "v3" not in a.model)
    tok = AutoTokenizer.from_pretrained(a.model, add_prefix_space=True) if need_prefix else AutoTokenizer.from_pretrained(a.model)
    enc = [T.encode(tok, t, [s for s in sp if s[2] in B.VIEWS[view]], tag2id, max_len, None, True) for t, sp in docs]
    z = np.load(here / a.feats)
    ze = np.load(here / a.feats_eval) if a.feats_eval else z
    d = z["M"].shape[1]
    ids_all = list(range(len(docs)))
    metas_tr = item_meta([e[:4] for e in enc], [e[4] for e in enc], z["M"], z["offsets"], ids_all, d)
    metas_ev = item_meta([e[:4] for e in enc], [e[4] for e in enc], ze["M"], ze["offsets"], ids_all, d) if a.feats_eval else metas_tr
    items = [e[:4] for e in enc]
    model = Fused(a.model, len(tags), d, a.mode).to(dev)
    crf = CRF(len(tags)).to(dev)
    tr_ids = split["train"][:a.limit] if a.limit else split["train"]
    tr = [items[i] for i in tr_ids]
    tr_m = [metas_tr[i] for i in tr_ids]
    new = [p for n, p in model.named_parameters() if not n.startswith("enc.")]
    opt = torch.optim.AdamW([{"params": model.enc.parameters(), "lr": lr}, {"params": new, "lr": 1e-3}, {"params": crf.parameters(), "lr": 5e-3}], weight_decay=0.01)
    steps = a.epochs * ((len(tr) + a.bs - 1) // a.bs)
    sch = get_linear_schedule_with_warmup(opt, int(0.1 * steps), steps)
    rng = random.Random(a.seed)
    part = lambda p, mm: ([items[i] for i in split[p]], [mm[i] for i in split[p]], [docs[i] for i in split[p]])
    counts = B.surface_counts([docs[i] for i in split["train"]])
    hist, best_state, best_crf, t0 = [], None, None, time.time()
    for ep in range(1, a.epochs + 1):
        model.train()
        for ids, att, y, order in T.batches(tr, a.bs, True, rng):
            meta = collate(order, tr_m, d, ids.size(1)).to(dev)
            keep = (torch.rand(len(order), device=dev) > D_META_DROP).float()
            if a.zero_meta:
                keep = keep * 0
            with torch.autocast("cuda", dtype=torch.bfloat16, enabled=dev == "cuda"):
                em = model(ids.to(dev), att.to(dev), meta, keep)
            e, cm, idx = compact(em.float(), (y != -100).to(dev))
            loss = crf.nll(e, y.to(dev).gather(1, idx), cm)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step(), sch.step(), opt.zero_grad()
        di, dm, dd = part("dev", metas_tr)
        pred, _ = predict_f(model, crf, di, dm, id2tag, dev, d, a.zero_meta)
        f1 = M.corpus_span_scores([(g, p) for (_, g), p in zip(dd, pred)], "exact", labels=B.VIEWS[view])["micro"]["f1"]
        hist.append({"epoch": ep, "dev_micro_f1": f1, "loss": round(loss.item(), 4)})
        print(hist[-1], flush=True)
        if B.select_checkpoint(hist) == ep:
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
            best_crf = {k: v.detach().cpu().clone() for k, v in crf.state_dict().items()}
    sel = B.select_checkpoint(hist)
    model.load_state_dict(best_state), crf.load_state_dict(best_crf)
    preds, gate = {}, None
    for p in ("dev", "calibration", "test"):
        it, mm, dd = part(p, metas_ev if p != "dev" else metas_tr)
        preds[p], g = predict_f(model, crf, it, mm, id2tag, dev, d, a.zero_meta)
        gate = g if p == "test" else gate
    td = part("test", metas_ev)[2]
    ev = [(t, g, pr) for (t, g), pr in zip(td, preds["test"])]
    res = B.evaluate(ev, counts, view)
    boot = M.grouped_bootstrap({i: [(g, p)] for i, (_, g, p) in enumerate(ev)}, lambda ds: M.corpus_span_scores(ds, "exact", labels=B.VIEWS[view])["micro"]["f1"], n_boot=1000)
    mode = ("zero" if a.zero_meta else a.mode) + a.tag
    name = f"{a.dataset}__{a.model.split('/')[-1]}_fusion-{mode}__seed{a.seed}"
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{name}.json").write_text(json.dumps({"dataset": a.dataset, "model": a.model, "crf": True, "knowledge": "K0", "fusion": mode, "seed": a.seed, "view": view,
                                                  "selected_epoch": sel, "history": hist, "test": res, "test_micro_exact_f1_ci": boot, "mean_gate_test": gate, "feats": a.feats,
                                                  "feats_eval": a.feats_eval or a.feats, "n": {k: len(v) for k, v in split.items()}, "minutes": round((time.time() - t0) / 60, 2),
                                                  "peak_gpu_gb": round(torch.cuda.max_memory_allocated() / 1e9, 2) if dev == "cuda" else 0, "torch": torch.__version__}, indent=1, default=lambda o: o.tolist()))
    (out / f"{name}.pred.json").write_text(json.dumps({p: [[list(s) for s in pr] for pr in v] for p, v in preds.items()}))
    print(name, "dev", max(h["dev_micro_f1"] for h in hist), "test exact micro", res["exact"]["micro"]["f1"], "gate", gate, boot)


if __name__ == "__main__":
    main()
