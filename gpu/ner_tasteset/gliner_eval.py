"""Plan Part K / P1: GLiNER zero-shot vs fine-tuned on TASTEset, same recipe split as train_ner.py (seed 7).

  PYTHONPATH=pylib $PY gliner_eval.py --data TASTEset.csv --model urchade/gliner_large-v2.1 --mode zeroshot
  PYTHONPATH=pylib $PY gliner_eval.py --data TASTEset.csv --model urchade/gliner_large-v2.1 --mode finetune --epochs 8
Zero-shot: natural-language label names, threshold chosen on DEV. Fine-tune: GLiNER trainer on TRAIN, checkpoint per
epoch, checkpoint + threshold chosen on DEV, TEST reported once. Same exact/relaxed span metrics and grouped bootstrap
CI as the encoder runs. Writes runs/gliner_<model>_<mode>.json (+ .pred.jsonl).
"""
from __future__ import annotations

import argparse
import json
import random
import re
import time
from pathlib import Path

import numpy as np
import torch
from metrics import corpus_span_scores, grouped_bootstrap
from train_ner import load, split_ids, SPLIT_SEED

NAMES = {"FOOD": "food ingredient", "QUANTITY": "quantity", "UNIT": "unit of measurement", "PROCESS": "cooking process",
         "PHYSICAL_QUALITY": "physical quality", "COLOR": "color", "TASTE": "taste", "PURPOSE": "purpose",
         "PART": "part of food", "DIET": "diet", "TRADE_NAME": "brand name", "EXAMPLE": "example"}
WORD = re.compile(r"\w+|[^\w\s]")
GRID = (0.2, 0.3, 0.4, 0.5, 0.6)


def predict(model, docs, labels, thr):
    back = {NAMES.get(l, l.lower()): l for l in labels}
    out = []
    for text, gold in docs:
        ents = model.predict_entities(text, list(back), threshold=thr, flat_ner=True)
        out.append((gold, sorted((e["start"], e["end"], back[e["label"]]) for e in ents)))
    return out


def to_train(text: str, spans) -> dict:
    words = [(m.start(), m.end()) for m in WORD.finditer(text)]
    ner = []
    for s, e, lab in spans:
        idx = [i for i, (a, b) in enumerate(words) if a >= s and b <= e]
        if idx:
            ner.append([idx[0], idx[-1], NAMES.get(lab, lab.lower())])
    return {"tokenized_text": [text[a:b] for a, b in words], "ner": ner}


def best_threshold(model, dev, labels):
    f1 = {t: corpus_span_scores(predict(model, dev, labels, t), "exact")["micro"]["f1"] for t in GRID}
    t = max(f1, key=f1.get)
    return t, f1[t], f1


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--model", default="urchade/gliner_large-v2.1")
    ap.add_argument("--mode", choices=("zeroshot", "finetune"), default="zeroshot")
    ap.add_argument("--epochs", type=int, default=8)
    ap.add_argument("--lr", type=float, default=5e-6)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--out", default="runs")
    a = ap.parse_args()
    random.seed(a.seed), np.random.seed(a.seed), torch.manual_seed(a.seed)
    from gliner import GLiNER
    docs, tags = load(a.data)
    labels = sorted({t.split("-", 1)[1] for t in tags if t != "O"})
    split = split_ids(len(docs))
    part = {k: [docs[i] for i in v] for k, v in split.items()}
    dev_name = "cuda" if torch.cuda.is_available() else "cpu"
    model = GLiNER.from_pretrained(a.model).to(dev_name)
    t0, extra = time.time(), {}
    if a.mode == "finetune":
        from gliner.data_processing.collator import DataCollator
        from gliner.training import Trainer, TrainingArguments
        ck = Path(a.out) / f"gliner_ck_{a.model.split('/')[-1]}"
        args = TrainingArguments(output_dir=str(ck), learning_rate=a.lr, weight_decay=0.01, others_lr=1e-5,
                                 others_weight_decay=0.01, lr_scheduler_type="linear", warmup_ratio=0.1,
                                 per_device_train_batch_size=8, focal_loss_alpha=0.75, focal_loss_gamma=2,
                                 num_train_epochs=a.epochs, save_strategy="epoch", save_total_limit=a.epochs,
                                 dataloader_num_workers=0, report_to="none", seed=a.seed)
        Trainer(model=model, args=args, train_dataset=[to_train(t, s) for t, s in part["train"]],
                tokenizer=model.data_processor.transformer_tokenizer,
                data_collator=DataCollator(model.config, data_processor=model.data_processor, prepare_labels=True)).train()
        scores = {}
        for c in sorted(ck.glob("checkpoint-*"), key=lambda p: int(p.name.split("-")[1])):
            m = GLiNER.from_pretrained(str(c)).to(dev_name)
            scores[c.name] = (best_threshold(m, part["dev"], labels), m)
        name = max(scores, key=lambda k: scores[k][0][1])
        (thr, dev_f1, grid), model = scores[name]
        extra = {"checkpoint": name, "dev_by_checkpoint": {k: v[0][1] for k, v in scores.items()}}
    else:
        thr, dev_f1, grid = best_threshold(model, part["dev"], labels)
    test = predict(model, part["test"], labels, thr)
    res = {m: corpus_span_scores(test, m) for m in ("exact", "relaxed")}
    ci = grouped_bootstrap({i: [d] for i, d in enumerate(test)},
                           lambda ds: corpus_span_scores(ds, "exact")["micro"]["f1"], n_boot=1000)
    name = f"gliner_{a.model.split('/')[-1]}_{a.mode}_seed{a.seed}"
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{name}.json").write_text(json.dumps({
        "model": a.model, "mode": a.mode, "seed": a.seed, "split_seed": SPLIT_SEED, "selected_on": "DEV",
        "threshold": thr, "best_dev_micro_exact_f1": dev_f1, "dev_threshold_grid": grid, "test": res,
        "test_micro_exact_f1_ci": ci, "label_names": NAMES, "minutes": round((time.time() - t0) / 60, 2), **extra},
        indent=1))
    (out / f"{name}.pred.jsonl").write_text("\n".join(json.dumps({"recipe": split["test"][i], "gold": g, "pred": p})
                                                      for i, (g, p) in enumerate(test)) + "\n")
    print(name, "thr", thr, "dev", dev_f1, "test exact", res["exact"]["micro"]["f1"], "relaxed",
          res["relaxed"]["micro"]["f1"], ci)


if __name__ == "__main__":
    main()
