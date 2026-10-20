#!/usr/bin/env python3
"""Matched reproduction + clean re-evaluation of the RecipeDB3 ingredient NER (DeBERTa-base).

  python repro.py --data Ingredient_Annotated_Dataset.csv --protocol theirs --seed 48
  python repro.py --data Ingredient_Annotated_Dataset.csv --protocol clean  --seed 1

theirs: their notebook protocol — random 80/20 row split (random_state=seed), model selected on the TEST set,
        deberta-base, 15 epochs, lr 5e-5, bs 16, max_len 128, SIZE not in the label map (-> O).
clean:  80/10/10 split grouped by masked-sentence family (numbers masked), select on DEV, report TEST once.
Both report seqeval entity macro/micro F1, plus the theirs-test split broken into rows whose masked family also occurs
in train ("leaked") and rows that do not. Assumption: tags -> BIO by starting a new entity when a tag differs from
the previous word's tag (their BIO file is not released; consecutive identical tags are one entity).
"""
from __future__ import annotations

import argparse
import json
import os
import random
import re
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from seqeval.metrics import classification_report, f1_score
from sklearn.model_selection import GroupShuffleSplit, train_test_split
from torch.utils.data import DataLoader, Dataset
from transformers import AutoModelForTokenClassification, AutoTokenizer

def _jsonable(o):
    """numpy scalars/arrays -> plain python (a run lost its result to int64 at the final dump)."""
    if hasattr(o, "tolist"):
        return o.tolist()
    raise TypeError(f"not JSON serializable: {type(o)}")


TAGS = ["NAME", "QUANTITY", "UNIT", "STATE", "TEMP", "DF"]            # SIZE absent in their label_dict
LABELS = ["O"] + [f"{p}-{t}" for t in TAGS for p in "BI"]
L2I = {l: i for i, l in enumerate(LABELS)}
NUM = re.compile(r"\d+(?:[./]\d+)?|[¼½¾⅓⅔⅛]")


def family(sentence: str) -> str:
    return re.sub(r"\s+", " ", NUM.sub("#", sentence.lower())).strip()


def to_bio(tags: list[str]) -> list[str]:
    out, prev = [], None
    for t in tags:
        if t == "O" or t not in TAGS:
            out.append("O")
            prev = None
        else:
            out.append(("I-" if t == prev else "B-") + t)
            prev = t
    return out


class DS(Dataset):
    def __init__(self, df, tok, max_len):
        self.rows = [(s.split(), b) for s, b in zip(df.sentence, df.bio)]
        self.tok, self.max_len = tok, max_len

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, i):
        words, bio = self.rows[i]
        enc = self.tok(words, is_split_into_words=True, truncation=True, max_length=self.max_len,
                       padding="max_length", return_tensors="pt")
        lab, prev = [], None
        for w in enc.word_ids():
            lab.append(-100 if w is None or w == prev else L2I[bio[w]])
            prev = w
        return {**{k: v.squeeze(0) for k, v in enc.items()}, "labels": torch.tensor(lab)}


@torch.no_grad()
def predict(model, loader, dev, df):
    model.eval()
    preds, golds = [], []
    for b in loader:
        lab = b.pop("labels")
        logits = model(**{k: v.to(dev) for k, v in b.items()}).logits.argmax(-1).cpu()
        for p, l in zip(logits, lab):
            keep = l != -100
            preds.append([LABELS[i] for i in p[keep]])
            golds.append([LABELS[i] for i in l[keep]])
    for i, (p, g) in enumerate(zip(preds, golds)):          # truncation guard: pad to gold length
        preds[i] = p + ["O"] * (len(g) - len(p))
    return golds, preds


def score(golds, preds):
    r = classification_report(golds, preds, output_dict=True, zero_division=0)
    per = {k: {"f1": v["f1-score"], "precision": v["precision"], "recall": v["recall"], "support": v["support"]} for k, v in r.items() if k not in ("micro avg", "macro avg", "weighted avg")}
    return {"macro_f1": r["macro avg"]["f1-score"], "micro_f1": r["micro avg"]["f1-score"], "n_entities": r["micro avg"]["support"], "per_label": per}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--protocol", choices=["theirs", "clean"], required=True)
    ap.add_argument("--seed", type=int, default=48)
    ap.add_argument("--model", default="microsoft/deberta-base")
    ap.add_argument("--epochs", type=int, default=15)
    ap.add_argument("--lr", type=float, default=5e-5)
    ap.add_argument("--bs", type=int, default=16)
    ap.add_argument("--max-len", type=int, default=128)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", default="runs")
    ap.add_argument("--with-size", action="store_true", help="include SIZE in the label map (their notebook drops it)")
    a = ap.parse_args()
    global TAGS, LABELS, L2I
    if a.with_size:
        TAGS = TAGS + ["SIZE"]
        LABELS = ["O"] + [f"{p}-{t}" for t in TAGS for p in "BI"]
        L2I = {l: i for i, l in enumerate(LABELS)}
    t_start = time.time()
    random.seed(a.seed); np.random.seed(a.seed); torch.manual_seed(a.seed)
    df = pd.read_csv(a.data).dropna()
    df = df[df.sentence.astype(str).str.strip() != ""].reset_index(drop=True)
    df["tags"] = df.tags.astype(str)
    ok = df.apply(lambda r: len(r.sentence.split()) == len(r.tags.split()), axis=1)
    skipped = int((~ok).sum())
    df = df[ok].reset_index(drop=True)
    df["bio"] = [to_bio(t.split()) for t in df.tags]
    df["fam"] = df.sentence.map(family)
    if a.limit:
        df = df.sample(a.limit, random_state=0).reset_index(drop=True)
    if a.protocol == "theirs":
        train, test = train_test_split(df, test_size=0.20, random_state=a.seed)
        dev = test                                           # selection on TEST, as in their notebook
    else:
        g = GroupShuffleSplit(1, test_size=0.2, random_state=a.seed)
        tr_i, rest_i = next(g.split(df, groups=df.fam))
        train, rest = df.iloc[tr_i], df.iloc[rest_i].reset_index(drop=True)
        g2 = GroupShuffleSplit(1, test_size=0.5, random_state=a.seed)
        d_i, t_i = next(g2.split(rest, groups=rest.fam))
        dev, test = rest.iloc[d_i], rest.iloc[t_i]
    train_fams = set(train.fam)
    test = test.assign(leaked=test.fam.isin(train_fams))
    tok = AutoTokenizer.from_pretrained(a.model, add_prefix_space=True)
    model = AutoModelForTokenClassification.from_pretrained(a.model, num_labels=len(LABELS))
    dv = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(dv)
    ld = lambda d, sh: DataLoader(DS(d, tok, a.max_len), batch_size=a.bs, shuffle=sh)
    tr_l, dev_l, te_l = ld(train, True), ld(dev, False), ld(test, False)
    opt = torch.optim.AdamW(model.parameters(), lr=a.lr)
    best, best_ep, log, best_pred = -1, 0, [], None
    for ep in range(1, a.epochs + 1):
        model.train()
        tl = 0.0
        for b in tr_l:
            out = model(**{k: v.to(dv) for k, v in b.items()})
            opt.zero_grad(); out.loss.backward(); opt.step(); tl += out.loss.item()
        sel = score(*predict(model, dev_l, dv, dev))
        log.append({"epoch": ep, "train_loss": tl / len(tr_l), **{f"sel_{k}": v for k, v in sel.items()}})
        print(log[-1], flush=True)
        if sel["macro_f1"] > best:
            best, best_ep = sel["macro_f1"], ep
            best_pred = predict(model, te_l, dv, test)
    last_pred = predict(model, te_l, dv, test)
    res = {"protocol": a.protocol, "seed": a.seed, "model": a.model, "n_train": len(train), "n_dev": len(dev),
           "n_test": len(test), "skipped_len_mismatch": skipped, "best_epoch": best_ep,
           "selection_split": "TEST" if a.protocol == "theirs" else "DEV",
           "test_at_best": score(*best_pred), "test_at_last": score(*last_pred), "log": log,
           "leaked_frac_of_test": float(test.leaked.mean()), "with_size": a.with_size, "labels": LABELS,
           "exact_duplicate_frac_of_test": float(test.sentence.isin(set(train.sentence)).mean()), "n_train_families": int(train.fam.nunique()),
           "runtime_s": round(time.time() - t_start), "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "cpu",
           "code_revision": os.environ.get("REV", "unknown"), "torch": torch.__version__, "lr": a.lr, "epochs": a.epochs, "bs": a.bs}
    lk = test.leaked.to_numpy()
    for name, m in (("leaked", lk), ("non_leaked", ~lk)):
        idx = np.where(m)[0]
        if len(idx):
            res[f"test_at_best_{name}"] = {**score([best_pred[0][i] for i in idx], [best_pred[1][i] for i in idx]),
                                           "n_sentences": int(len(idx))}
    Path(a.out).mkdir(exist_ok=True)
    (Path(a.out) / f"{a.protocol}{'_size' if a.with_size else ''}_seed{a.seed}.json").write_text(json.dumps(res, indent=1, default=_jsonable))
    print(json.dumps({k: v for k, v in res.items() if k != "log"}, indent=1, default=_jsonable))


if __name__ == "__main__":
    t = time.time(); main(); print(f"wall {time.time() - t:.0f}s")
