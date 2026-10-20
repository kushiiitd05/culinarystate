#!/usr/bin/env python3
"""S119 Part VII variant K-TS: ENTITY-TYPE-SPECIFIC knowledge-augmented token classification (our reimplementation of the RecipeBERT-KA idea; no external weights/code).
One shared encoder+CRF with 3 tags (O / B / I). For every document and every entity type T the input is  [type-T knowledge context] [SEP] [recipe text]  and only type-T spans are labelled;
predictions of all types are merged per document by span confidence (CRF forward-backward marginal), greedy non-overlapping. Contexts are TRAIN-only (knowledge.type_context).
Checkpoint = dev exact micro F1 of the MERGED output (benchmark rule). Python 3.8 safe.

  python typespec_train.py --dataset tasteset --model microsoft/deberta-base --seed 1 --out runs"""
from __future__ import annotations

import argparse
import json
import random
import time
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForTokenClassification, AutoTokenizer, get_linear_schedule_with_warmup

import bench_train as T
import knowledge as K
from bench_train import B, M, CRF, compact

TAGS = ["O", "B-X", "I-X"]
T2I = {t: i for i, t in enumerate(TAGS)}
I2T = {i: t for t, i in T2I.items()}


def merge(per_type, text_len=None):
    """per_type: list of (s, e, label, conf). Greedy by confidence, no overlaps."""
    out, taken = [], []
    for s, e, lab, c in sorted(per_type, key=lambda x: -x[3]):
        if all(e <= a or s >= b for a, b in taken):
            out.append((s, e, lab))
            taken.append((s, e))
    return sorted(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", choices=["tasteset", "recipedb3"], required=True)
    ap.add_argument("--model", required=True)
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
    lr = 2e-5 if "large" in a.model else 5e-5
    max_len = 256 if a.dataset == "tasteset" else 128
    need_prefix = "roberta" in a.model or ("deberta" in a.model and "v3" not in a.model)
    tok = AutoTokenizer.from_pretrained(a.model, add_prefix_space=True) if need_prefix else AutoTokenizer.from_pretrained(a.model)
    train_docs = [docs[i] for i in split["train"]]
    ctx = {l: K.type_context(train_docs, l, labels, budget=min(40, int(0.18 * max_len))) for l in labels}
    pre = {l: [c[m.start():m.end()] for m in T.WORD.finditer(c)] for l, c in ctx.items()}
    print({l: len(c.split()) for l, c in ctx.items()}, flush=True)

    def inst(idx):
        """items for documents idx: list over docs of list over labels of encoded instance."""
        return [[T.encode(tok, docs[i][0], [(s, e, "X") for s, e, l in docs[i][1] if l == lab], T2I, max_len, pre[lab]) for lab in labels] for i in idx]
    enc_train = inst(split["train"][:a.limit] if a.limit else split["train"])
    flat_train = [it for d in enc_train for it in d]
    model = AutoModelForTokenClassification.from_pretrained(a.model, num_labels=3, id2label=I2T, label2id=T2I).to(dev)
    crf = CRF(3).to(dev)
    opt = torch.optim.AdamW([{"params": model.parameters(), "lr": lr}, {"params": crf.parameters(), "lr": 5e-3}], weight_decay=0.01)
    steps = a.epochs * ((len(flat_train) + a.bs - 1) // a.bs)
    sch = get_linear_schedule_with_warmup(opt, int(0.1 * steps), steps)
    rng = random.Random(a.seed)

    def predict_split(name):
        idx = split[name]
        encs = inst(idx)
        flat = [it for d in encs for it in d]
        dd = [docs[i] for i in idx for _ in labels]
        spans, confs = T.predict(model, flat, dd, I2T, dev, crf, conf=True, tag2id=T2I)
        res = []
        for k in range(len(idx)):
            per = []
            for j, lab in enumerate(labels):
                n = k * len(labels) + j
                per += [(s, e, lab, c) for (s, e, _), c in zip(spans[n], confs[n])]
            res.append(merge(per))
        return res

    hist, best_state, best_crf, t0 = [], None, None, time.time()
    if dev == "cuda":
        torch.cuda.reset_peak_memory_stats()
    for ep in range(1, a.epochs + 1):
        model.train()
        for ids, att, y, _ in T.batches(flat_train, a.bs, True, rng):
            with torch.autocast("cuda", dtype=torch.bfloat16, enabled=dev == "cuda"):
                em = model(input_ids=ids.to(dev), attention_mask=att.to(dev)).logits
            e, cm, idx = compact(em.float(), (y != -100).to(dev))
            loss = crf.nll(e, y.to(dev).gather(1, idx), cm)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step(), sch.step(), opt.zero_grad()
        pred = predict_split("dev")
        f1 = M.corpus_span_scores([(docs[i][1], p) for i, p in zip(split["dev"], pred)], "exact", labels=B.VIEWS[view])["micro"]["f1"]
        hist.append({"epoch": ep, "dev_micro_f1": f1, "loss": round(loss.item(), 4)})
        print(hist[-1], flush=True)
        if B.select_checkpoint(hist) == ep:
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
            best_crf = {k: v.detach().cpu().clone() for k, v in crf.state_dict().items()}
    sel = B.select_checkpoint(hist)
    model.load_state_dict(best_state), crf.load_state_dict(best_crf)
    preds = {p: predict_split(p) for p in ("dev", "calibration", "test")}
    counts = B.surface_counts(train_docs)
    ev = [(docs[i][0], docs[i][1], p) for i, p in zip(split["test"], preds["test"])]
    res = B.evaluate(ev, counts, view)
    boot = M.grouped_bootstrap({i: [(g, p)] for i, (_, g, p) in enumerate(ev)}, lambda ds: M.corpus_span_scores(ds, "exact", labels=B.VIEWS[view])["micro"]["f1"], n_boot=1000)
    name = f"{a.dataset}__{a.model.split('/')[-1]}_typespec__seed{a.seed}"
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{name}.json").write_text(json.dumps({"dataset": a.dataset, "model": a.model, "crf": True, "knowledge": "TS", "seed": a.seed, "view": view, "selected_epoch": sel, "history": hist,
                                                  "test": res, "test_micro_exact_f1_ci": boot, "contexts": ctx, "n": {k: len(v) for k, v in split.items()}, "minutes": round((time.time() - t0) / 60, 2),
                                                  "peak_gpu_gb": round(torch.cuda.max_memory_allocated() / 1e9, 2) if dev == "cuda" else 0, "torch": torch.__version__}, indent=1, default=lambda o: o.tolist()))
    (out / f"{name}.pred.json").write_text(json.dumps({p: [[list(s) for s in pr] for pr in v] for p, v in preds.items()}))
    print(name, "dev", max(h["dev_micro_f1"] for h in hist), "test exact micro", res["exact"]["micro"]["f1"], boot)


if __name__ == "__main__":
    main()
