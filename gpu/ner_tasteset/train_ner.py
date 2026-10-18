#!/usr/bin/env python3
"""X8 / P5: encoder NER on TASTEset (token classification, BIO), protocol from handoff/NER_RUNBOOK.md.

  python train_ner.py --data TASTEset.csv --model bert-base-cased --seed 1 --out runs/
Split: recipes 70/15/15 with split seed 7 (same split for every model/seed; written to split.json). Model selection on
dev micro exact F1 only; test is scored once with the selected epoch. Scorer: scoring/metrics.py (copied next to this
file) — the programme's common span scorer; CI = grouped bootstrap over recipes.
Self-contained: torch + transformers only.
"""
from __future__ import annotations

import argparse
import json
import random
import re
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from crf import CRF, compact
from metrics import corpus_span_scores, grouped_bootstrap
from transformers import AutoModelForTokenClassification, AutoTokenizer, get_linear_schedule_with_warmup

SPLIT_SEED = 7


def split_ids(n: int) -> dict:
    ids = list(range(n))
    random.Random(SPLIT_SEED).shuffle(ids)
    a, b = int(0.7 * n), int(0.85 * n)
    return {"train": sorted(ids[:a]), "dev": sorted(ids[a:b]), "test": sorted(ids[b:])}


def load(path: str):
    d = pd.read_csv(path)
    docs = [(r.ingredients, [(e["start"], e["end"], e["type"]) for e in json.loads(r.ingredients_entities)])
            for r in d.itertuples()]
    labels = sorted({lab for _, spans in docs for *_, lab in spans})
    tags = ["O"] + [f"{p}-{lab}" for lab in labels for p in ("B", "I")]
    return docs, tags


WORD = re.compile(r"\w+|[^\w\s]")                       # words and single punctuation marks


def encode(tok, text: str, spans, tag2id: dict, max_len: int):
    """Pre-split into words/punctuation so every tokenizer sees the same boundaries (BPE glues 'lb.,' otherwise).
    Label = first sub-token of each word; offsets returned are word offsets (one per labelled position)."""
    words = [(m.start(), m.end()) for m in WORD.finditer(text)]
    enc = tok([text[a:b] for a, b in words], is_split_into_words=True, truncation=True, max_length=max_len)
    y, offs, prev = [], [], None
    for w in enc.word_ids():
        if w is None or w == prev:
            y.append(-100)
            offs.append((0, 0))
        else:
            s, e = words[w]
            lab = next(((a, lab) for a, b, lab in spans if a <= s < b), None)
            y.append(tag2id["O"] if lab is None else tag2id[("B-" if s == lab[0] else "I-") + lab[1]])
            offs.append((s, e))
        prev = w
    return enc["input_ids"], enc["attention_mask"], offs, y


def decode(pred_ids, offsets, id2tag: dict, text: str):
    """BIO over words -> char spans; an I- without a matching open span starts a new one (lenient)."""
    spans, cur = [], None
    for p, (s, e) in zip(pred_ids, offsets):
        if s == e:
            continue
        tag = id2tag[p]
        kind, lab = tag.split("-", 1) if tag != "O" else ("O", None)
        if kind == "I" and cur and lab == cur[2]:
            cur = (cur[0], e, lab)                           # continue the open span
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
        yield ids, att, y, [idx[j] for j in range(i, min(i + bs, len(idx)))]


@torch.no_grad()
def predict(model, items, docs, id2tag, bs, dev, crf=None):
    model.eval()
    out = []
    for ids, att, y, order in batches(items, bs, False, None):
        em = model(input_ids=ids.to(dev), attention_mask=att.to(dev)).logits
        if crf is None:
            logits = em.argmax(-1).cpu().tolist()
        else:                                   # word positions come from tokenization (y == -100 elsewhere)
            e, cm, idx = compact(em, (y != -100).to(dev))
            logits = []
            for b, path in enumerate(crf.decode(e, cm)):
                row = [0] * em.size(1)
                for j, tag in enumerate(path):
                    row[int(idx[b, j])] = tag
                logits.append(row)
        for row, k in zip(logits, order):
            text, gold = docs[k]
            out.append((gold, decode(row[:len(items[k][0])], items[k][2], id2tag, text)))
    return out



@torch.no_grad()
def word_states(model, items, bs, dev):
    """Last-layer states + model probabilities at word positions: list per item of ([n,H], [n,T], positions)."""
    model.eval()
    out = []
    for ids, att, y, order in batches(items, bs, False, None):
        o = model(input_ids=ids.to(dev), attention_mask=att.to(dev), output_hidden_states=True)
        h, pr = o.hidden_states[-1], o.logits.softmax(-1)
        for b, k in enumerate(order):
            pos = (y[b] != -100).nonzero(as_tuple=True)[0].to(dev)
            out.append((k, h[b, pos], pr[b, pos], pos.cpu().tolist()))
    return sorted(out, key=lambda x: x[0])


@torch.no_grad()
def knn_predict(states, store_h, store_y, n_tags, k, lam, temp, length):
    """kNN-NER: interpolate model probs with a label distribution from the k nearest train word states."""
    preds = []
    for item, h, pr, pos in states:
        hn = torch.nn.functional.normalize(h, dim=-1)
        sim = hn @ store_h.T
        top, ix = sim.topk(k, dim=-1)
        w = (top / temp).softmax(-1)
        pk = torch.zeros(h.size(0), n_tags, device=h.device).scatter_add_(1, store_y[ix], w)
        tags = ((1 - lam) * pr + lam * pk).argmax(-1).tolist()
        row = [0] * length[item]
        for p_, t in zip(pos, tags):
            row[p_] = t
        preds.append(row)
    return preds

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--epochs", type=int, default=10)
    ap.add_argument("--lr", type=float, default=3e-5)
    ap.add_argument("--bs", type=int, default=16)
    ap.add_argument("--max-len", type=int, default=192)
    ap.add_argument("--limit", type=int, default=0, help="smoke test: use first N recipes")
    ap.add_argument("--crf", action="store_true", help="linear-chain CRF over word positions (plan Part K)")
    ap.add_argument("--knn", action="store_true", help="kNN-NER over a train-only datastore, lambda/k tuned on dev")
    ap.add_argument("--out", default="runs")
    a = ap.parse_args()
    random.seed(a.seed), np.random.seed(a.seed), torch.manual_seed(a.seed)
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    docs, tags = load(a.data)
    if a.limit:
        docs = docs[:a.limit]
    split = split_ids(len(docs))
    tag2id = {t: i for i, t in enumerate(tags)}
    id2tag = {i: t for t, i in tag2id.items()}
    tok = AutoTokenizer.from_pretrained(a.model, add_prefix_space=True) if "roberta" in a.model else \
        AutoTokenizer.from_pretrained(a.model)
    enc = [encode(tok, t, s, tag2id, a.max_len) for t, s in docs]
    model = AutoModelForTokenClassification.from_pretrained(a.model, num_labels=len(tags), id2label=id2tag,
                                                            label2id=tag2id).to(dev)
    crf = CRF(len(tags)).to(dev) if a.crf else None
    tr = [enc[i] for i in split["train"]]
    groups = [{"params": model.parameters(), "lr": a.lr}] + ([{"params": crf.parameters(), "lr": 5e-3}] if crf else [])
    opt = torch.optim.AdamW(groups, lr=a.lr, weight_decay=0.01)
    steps = a.epochs * ((len(tr) + a.bs - 1) // a.bs)
    sch = get_linear_schedule_with_warmup(opt, int(0.1 * steps), steps)
    rng = random.Random(a.seed)

    def scored(part):
        items = [enc[i] for i in split[part]]
        sub = [docs[i] for i in split[part]]
        return predict(model, items, sub, id2tag, 64, dev, crf)

    best, best_state, hist, t0 = -1.0, None, [], time.time()
    for ep in range(1, a.epochs + 1):
        model.train()
        for ids, att, y, _ in batches(tr, a.bs, True, rng):
            if crf is None:
                loss = model(input_ids=ids.to(dev), attention_mask=att.to(dev), labels=y.to(dev)).loss
            else:
                em = model(input_ids=ids.to(dev), attention_mask=att.to(dev)).logits
                e, cm, idx = compact(em, (y != -100).to(dev))
                loss = crf.nll(e, y.to(dev).gather(1, idx), cm)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step(), sch.step(), opt.zero_grad()
        f1 = corpus_span_scores(scored("dev"), "exact")["micro"]["f1"]
        hist.append({"epoch": ep, "dev_micro_exact_f1": f1, "loss": round(loss.item(), 4)})
        if f1 > best:
            best, best_state = f1, {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}
            best_crf = {k: v.detach().cpu().clone() for k, v in crf.state_dict().items()} if crf else None
    model.load_state_dict(best_state)
    if crf:
        crf.load_state_dict(best_crf)
    test = scored("test")
    res = {m: corpus_span_scores(test, m) for m in ("exact", "relaxed")}
    knn = None
    if a.knn and crf is None:
        parts = {pt: [enc[i] for i in split[pt]] for pt in ("train", "dev", "test")}
        st = {pt: word_states(model, parts[pt], 64, dev) for pt in parts}
        store_h = torch.nn.functional.normalize(torch.cat([h for _, h, _, _ in st["train"]]), dim=-1)
        store_y = torch.tensor([t for i in split["train"] for t in enc[i][3] if t != -100], device=dev)
        lens = {pt: {j: len(parts[pt][j][0]) for j in range(len(parts[pt]))} for pt in parts}

        def knn_docs(pt, k, lam, temp):
            pr = knn_predict(st[pt], store_h, store_y, len(tags), k, lam, temp, lens[pt])
            return [(docs[i][1], decode(row[:len(enc[i][0])], enc[i][2], id2tag, docs[i][0]))
                    for i, row in zip(split[pt], pr)]
        grid = [(k, lam, temp) for k in (8, 32) for lam in (0.1, 0.25, 0.4) for temp in (0.05, 0.1)]
        dev_f1 = {g: corpus_span_scores(knn_docs("dev", *g), "exact")["micro"]["f1"] for g in grid}
        g = max(dev_f1, key=dev_f1.get)
        ktest = knn_docs("test", *g)
        knn = {"selected_on_dev": {"k": g[0], "lambda": g[1], "temp": g[2], "dev_f1": dev_f1[g]},
               "dev_grid": {f"k{k}_l{l}_t{t}": v for (k, l, t), v in dev_f1.items()},
               "test": {m: corpus_span_scores(ktest, m) for m in ("exact", "relaxed")},
               "test_micro_exact_f1_ci": grouped_bootstrap({i: [d] for i, d in enumerate(ktest)},
                                                           lambda ds: corpus_span_scores(ds, "exact")["micro"]["f1"])}
    ci = grouped_bootstrap({i: [d] for i, d in enumerate(test)},
                           lambda ds: corpus_span_scores(ds, "exact")["micro"]["f1"], n_boot=1000)
    name = f"{a.model.split('/')[-1]}{'_crf' if a.crf else ''}{'_knn' if a.knn and not a.crf else ''}_seed{a.seed}"
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "split.json").write_text(json.dumps(split))
    (out / f"{name}.json").write_text(json.dumps({
        "model": a.model + ("+crf" if a.crf else ""), "seed": a.seed, "split_seed": SPLIT_SEED, "n": {k: len(v) for k, v in split.items()},
        "selected_on": "DEV", "best_dev_micro_exact_f1": best, "history": hist, "test": res,
        "test_micro_exact_f1_ci": ci, "knn": knn, "hparams": vars(a), "device": dev, "minutes": round((time.time() - t0) / 60, 2),
        "torch": torch.__version__}, indent=1))
    (out / f"{name}.pred.jsonl").write_text("\n".join(json.dumps({"recipe": split["test"][i], "gold": g, "pred": p})
                                                      for i, (g, p) in enumerate(test)) + "\n")
    print(name, "dev", best, "test exact", res["exact"]["micro"]["f1"], "relaxed", res["relaxed"]["micro"]["f1"], ci)


if __name__ == "__main__":
    main()
