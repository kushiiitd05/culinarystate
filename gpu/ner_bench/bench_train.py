#!/usr/bin/env python3
"""S119 E0: encoder (+CRF) on the frozen semantic NER benchmark v1 (benchmark/ner/*). Python 3.8 / transformers 4.45 safe.

  python bench_train.py --dataset tasteset --model microsoft/deberta-base --seed 1 [--crf] --out runs/
Splits come from splits/<dataset>_split_v1.json (train / calibration / dev / test). Training sees ONLY train. Checkpoint = max dev exact
micro F1 on the primary view (ties -> earlier epoch); test is scored once with that checkpoint. Calibration and dev predictions are also
saved (spans only) for the later calibrator. Metrics: benchmark.evaluate (exact/relaxed/per-label/boundary/strata) + grouped bootstrap CI.
"""
from __future__ import annotations

import argparse
import json
import random
import re
import sys
import time
import types
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from transformers import AutoModelForTokenClassification, AutoTokenizer, get_linear_schedule_with_warmup

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import metrics as M  # noqa: E402  (copy of src/culinarystate/scoring/metrics.py)

_pkg, _sc = types.ModuleType("culinarystate"), types.ModuleType("culinarystate.scoring")
sys.modules.update({"culinarystate": _pkg, "culinarystate.scoring": _sc, "culinarystate.scoring.metrics": M})
import benchmark as B  # noqa: E402
from crf import CRF, compact  # noqa: E402

WORD = re.compile(r"\w+|[^\w\s]")
PRIMARY = {"recipedb3": "recipedb3_published", "tasteset": "tasteset_native"}
KNOWN_RDB3 = B.VIEWS["recipedb3_published"]


def load_docs(dataset: str, data: str):
    if dataset == "tasteset":
        d = pd.read_csv(data)
        return [(r.ingredients, [(e["start"], e["end"], e["type"]) for e in json.loads(r.ingredients_entities)]) for r in d.itertuples()]
    df = pd.read_csv(data).dropna()
    df = df[df.sentence.astype(str).str.strip() != ""].reset_index(drop=True)
    df["tags"] = df.tags.astype(str)
    df = df[df.apply(lambda r: len(r.sentence.split()) == len(r.tags.split()), axis=1)].reset_index(drop=True)
    return [B.words_to_spans(s.split(), B.tags_to_bio(t.split(), set(KNOWN_RDB3))) for s, t in zip(df.sentence, df.tags)]


def encode(tok, text, spans, tag2id, max_len, prefix=None):
    words = [(m.start(), m.end()) for m in WORD.finditer(text)]
    wl = [text[a:b] for a, b in words]
    enc = tok(prefix, wl, is_split_into_words=True, truncation=True, max_length=max_len) if prefix else tok(wl, is_split_into_words=True, truncation=True, max_length=max_len)
    seq = enc.sequence_ids() if prefix else [0] * len(enc["input_ids"])
    y, offs, prev = [], [], None
    for w, sq in zip(enc.word_ids(), seq):
        if w is None or w == prev or sq != (1 if prefix else 0):
            y.append(-100)
            offs.append((0, 0))
        else:
            s, e = words[w]
            lab = next(((a, lab) for a, b, lab in spans if a <= s < b), None)
            y.append(tag2id["O"] if lab is None else tag2id[("B-" if s == lab[0] else "I-") + lab[1]])
            offs.append((s, e))
        prev = w
    return enc["input_ids"], enc["attention_mask"], offs, y


def decode(pred_ids, offsets, id2tag):
    spans, cur = [], None
    for p, (s, e) in zip(pred_ids, offsets):
        if s == e:
            continue
        tag = id2tag[p]
        kind, lab = tag.split("-", 1) if tag != "O" else ("O", None)
        if kind == "I" and cur and lab == cur[2]:
            cur = (cur[0], e, lab)
            continue
        if cur:
            spans.append(cur)
        cur = (s, e, lab) if kind != "O" else None
    if cur:
        spans.append(cur)
    return spans


def batches(items, bs, shuffle, rng):
    idx = list(range(len(items)))
    if shuffle:
        rng.shuffle(idx)
    for i in range(0, len(idx), bs):
        chunk = [items[j] for j in idx[i:i + bs]]
        L = max(len(c[0]) for c in chunk)
        ids = torch.tensor([c[0] + [0] * (L - len(c[0])) for c in chunk])
        att = torch.tensor([c[1] + [0] * (L - len(c[1])) for c in chunk])
        y = torch.tensor([c[3] + [-100] * (L - len(c[3])) for c in chunk])
        yield ids, att, y, idx[i:i + bs]


@torch.no_grad()
def predict(model, items, docs, id2tag, dev, crf=None, bs=64):
    model.eval()
    out = [None] * len(items)
    for ids, att, y, order in batches(items, bs, False, None):
        with torch.autocast("cuda", dtype=torch.bfloat16, enabled=dev == "cuda"):
            em = model(input_ids=ids.to(dev), attention_mask=att.to(dev)).logits
        em = em.float()
        if crf is None:
            rows = em.argmax(-1).cpu().tolist()
        else:
            e, cm, idx = compact(em, (y != -100).to(dev))
            rows = []
            for b, path in enumerate(crf.decode(e, cm)):
                row = [0] * em.size(1)
                for j, tag in enumerate(path):
                    row[int(idx[b, j])] = tag
                rows.append(row)
        for row, k in zip(rows, order):
            out[k] = decode(row[:len(items[k][0])], items[k][2], id2tag)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", choices=["tasteset", "recipedb3"], required=True)
    ap.add_argument("--data", default="")
    ap.add_argument("--splits", default="")
    ap.add_argument("--model", required=True)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--crf", action="store_true")
    ap.add_argument("--epochs", type=int, default=15)
    ap.add_argument("--lr", type=float, default=0.0, help="0 = 5e-5 base / 2e-5 large (benchmark budget)")
    ap.add_argument("--bs", type=int, default=16)
    ap.add_argument("--max-len", type=int, default=0, help="0 = 128 recipedb3 / 256 tasteset")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--knowledge", default="K0", choices=["K0", "K1", "K2", "K3"], help="train-derived entity-type context prefix (Part VII)")
    ap.add_argument("--out", default="runs")
    a = ap.parse_args()
    random.seed(a.seed), np.random.seed(a.seed), torch.manual_seed(a.seed)
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    data = a.data or str(HERE / ("TASTEset.csv" if a.dataset == "tasteset" else "Ingredient_Annotated_Dataset.csv"))
    split = json.loads(Path(a.splits or HERE / f"{a.dataset}_split_v1.json").read_text())["indices"]
    docs = load_docs(a.dataset, data)
    view = PRIMARY[a.dataset]
    labels = sorted(B.VIEWS[view])
    tags = ["O"] + [f"{p}-{l}" for l in labels for p in ("B", "I")]
    tag2id = {t: i for i, t in enumerate(tags)}
    id2tag = {i: t for t, i in tag2id.items()}
    is_large = "large" in a.model
    lr = a.lr or (2e-5 if is_large else 5e-5)
    max_len = a.max_len or (256 if a.dataset == "tasteset" else 128)
    need_prefix = "roberta" in a.model or ("deberta" in a.model and "v3" not in a.model)
    tok = AutoTokenizer.from_pretrained(a.model, add_prefix_space=True) if need_prefix else AutoTokenizer.from_pretrained(a.model)
    prefix = None
    if a.knowledge != "K0":
        import knowledge as K
        ctx = K.build_context([docs[i] for i in split["train"]], sorted(B.VIEWS[view]), a.knowledge)
        prefix = [ctx[m.start():m.end()] for m in WORD.finditer(ctx)]
    enc = [encode(tok, t, [s for s in sp if s[2] in B.VIEWS[view]], tag2id, max_len, prefix) for t, sp in docs]
    model = AutoModelForTokenClassification.from_pretrained(a.model, num_labels=len(tags), id2label=id2tag, label2id=tag2id).to(dev)
    crf = CRF(len(tags)).to(dev) if a.crf else None
    tr_ids = split["train"][:a.limit] if a.limit else split["train"]
    tr = [enc[i] for i in tr_ids]
    groups = [{"params": model.parameters(), "lr": lr}] + ([{"params": crf.parameters(), "lr": 5e-3}] if crf else [])
    opt = torch.optim.AdamW(groups, lr=lr, weight_decay=0.01)
    steps = a.epochs * ((len(tr) + a.bs - 1) // a.bs)
    sch = get_linear_schedule_with_warmup(opt, int(0.1 * steps), steps)
    rng = random.Random(a.seed)
    part = lambda p: ([enc[i] for i in split[p]], [docs[i] for i in split[p]])
    counts = B.surface_counts([docs[i] for i in split["train"]])
    hist, best_state, best_crf, t0 = [], None, None, time.time()
    if dev == "cuda":
        torch.cuda.reset_peak_memory_stats()
    for ep in range(1, a.epochs + 1):
        model.train()
        for ids, att, y, _ in batches(tr, a.bs, True, rng):
            with torch.autocast("cuda", dtype=torch.bfloat16, enabled=dev == "cuda"):
                em = model(input_ids=ids.to(dev), attention_mask=att.to(dev)).logits
            em = em.float()
            if crf is None:
                loss = torch.nn.functional.cross_entropy(em.view(-1, em.size(-1)), y.to(dev).view(-1), ignore_index=-100)
            else:
                e, cm, idx = compact(em, (y != -100).to(dev))
                loss = crf.nll(e, y.to(dev).gather(1, idx), cm)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step(), sch.step(), opt.zero_grad()
        di, dd = part("dev")
        pred = predict(model, di, dd, id2tag, dev, crf)
        f1 = M.corpus_span_scores([(g, p) for (_, g), p in zip(dd, pred)], "exact", labels=B.VIEWS[view])["micro"]["f1"]
        hist.append({"epoch": ep, "dev_micro_f1": f1, "loss": round(loss.item(), 4)})
        print(hist[-1], flush=True)
        if B.select_checkpoint(hist) == ep:
            best_state = {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
            best_crf = {k: v.detach().cpu().clone() for k, v in crf.state_dict().items()} if crf else None
    sel_ep = B.select_checkpoint(hist)
    model.load_state_dict(best_state)
    if crf:
        crf.load_state_dict(best_crf)
    preds = {}
    for p in ("dev", "calibration", "test"):
        it, dd = part(p)
        preds[p] = predict(model, it, dd, id2tag, dev, crf)
    td = part("test")[1]
    ev_docs = [(t, g, pr) for (t, g), pr in zip(td, preds["test"])]
    res = B.evaluate(ev_docs, counts, view)
    boot = M.grouped_bootstrap({i: [(g, p)] for i, (_, g, p) in enumerate(ev_docs)},
                               lambda ds: M.corpus_span_scores([x for x in ds], "exact", labels=B.VIEWS[view])["micro"]["f1"], n_boot=1000)
    name = f"{a.dataset}__{a.model.split('/')[-1]}{'_crf' if a.crf else ''}{'_' + a.knowledge if a.knowledge != 'K0' else ''}__seed{a.seed}"
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{name}.json").write_text(json.dumps({
        "dataset": a.dataset, "model": a.model, "crf": a.crf, "knowledge": a.knowledge, "seed": a.seed, "view": view, "selected_epoch": sel_ep, "selection": "dev exact micro F1",
        "history": hist, "test": res, "test_micro_exact_f1_ci": boot, "hparams": {"lr": lr, "bs": a.bs, "epochs": a.epochs, "max_len": max_len},
        "n": {k: len(v) for k, v in split.items()}, "minutes": round((time.time() - t0) / 60, 2),
        "peak_gpu_gb": round(torch.cuda.max_memory_allocated() / 1e9, 2) if dev == "cuda" else 0,
        "gpu": torch.cuda.get_device_name(0) if dev == "cuda" else "cpu", "torch": torch.__version__}, indent=1, default=lambda o: o.tolist()))
    (out / f"{name}.pred.json").write_text(json.dumps({p: [[list(s) for s in pr] for pr in v] for p, v in preds.items()}))
    print(name, "dev", max(h["dev_micro_f1"] for h in hist), "test exact micro", res["exact"]["micro"]["f1"], "boundary", round(res["boundary_error_rate"], 4), boot)


if __name__ == "__main__":
    main()
