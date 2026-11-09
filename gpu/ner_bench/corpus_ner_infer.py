#!/usr/bin/env python3
"""Corpus NER inference with a saved DeBERTa-CRF checkpoint (S173, D-077). GPU, data plane only.

Reads tools/export_ingredient_lines.py output (one JSONL row per recipe: recipe_id, source_family, lines), groups each
recipe's lines into newline-joined chunks (the TASTEset training format) of at most --max-lines lines, predicts spans
with the checkpoint's encoder + CRF (bench_train_v2.predict), and writes one row per line:
{"recipe_id", "line_index", "text", "spans": [[start, end, label, surface], ...], "model": <ckpt sha256 prefix>}.
Never sees BBC text on a server (the exporter refuses it). MODEL_DERIVED, not gold.

    python corpus_ner_infer.py --ckpt <best.pt> --lines <FAMILY.jsonl> --out <FAMILY.ner.jsonl> [--bs 64]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def chunk_lines(lines: list[str], max_lines: int) -> list[tuple[int, str, list[tuple[int, int]]]]:
    """[(first_line_index, text, [(line_start, line_end) offsets in text])] with text = lines joined by '\\n' + '\\n'."""
    out = []
    for i in range(0, len(lines), max_lines):
        part = lines[i:i + max_lines]
        offs, pos = [], 0
        for s in part:
            offs.append((pos, pos + len(s)))
            pos += len(s) + 1
        out.append((i, "\n".join(part) + "\n", offs))
    return out


def spans_by_line(spans, offs, text, first):
    rows = {first + j: [] for j in range(len(offs))}
    for s, e, lab in spans:
        for j, (a, b) in enumerate(offs):
            if a <= s < b + 1:
                rows[first + j].append([s - a, min(e, b) - a, lab, text[s:min(e, b)]])
                break
    return rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True, type=Path)
    ap.add_argument("--lines", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--bs", type=int, default=64)
    ap.add_argument("--max-lines", type=int, default=12)
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args(argv)
    if a.out.exists():
        sys.exit("refusing to overwrite")
    import torch
    from transformers import AutoModelForTokenClassification, AutoTokenizer
    sys.path.insert(0, str(HERE))
    import bench_train_v2 as BT
    from crf import CRF
    ck = torch.load(a.ckpt, map_location="cpu")
    tags = ck["tags"]
    tag2id = {t: i for i, t in enumerate(tags)}
    id2tag = {i: t for t, i in tag2id.items()}
    name = ck["args"]["model"]
    need_prefix = "roberta" in name or ("deberta" in name and "v3" not in name)
    tok = AutoTokenizer.from_pretrained(name, add_prefix_space=True) if need_prefix else AutoTokenizer.from_pretrained(name)
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    model = AutoModelForTokenClassification.from_pretrained(name, num_labels=len(tags), id2label=id2tag,
                                                            label2id=tag2id)
    model.load_state_dict(ck["model"])
    model.to(dev).eval()
    crf = None
    if ck.get("crf") is not None:
        crf = CRF(len(tags))
        crf.load_state_dict(ck["crf"])
        crf.to(dev)
    sha = hashlib.sha256(a.ckpt.read_bytes()).hexdigest()[:16]
    max_len = ck["args"].get("max_len") or 256
    n_rec = 0
    with open(a.lines, encoding="utf-8") as fi, open(a.out, "x", encoding="utf-8") as fo:
        buf = []

        def flush():
            items = [BT.encode(tok, text, [], tag2id, max_len) for _, _, text, _ in buf]
            preds = BT.predict(model, items, None, id2tag, dev, crf=crf, bs=a.bs)
            for (rid, first, text, offs), sp in zip(buf, preds):
                for li, spans in spans_by_line(sp, offs, text, first).items():
                    a_, b_ = offs[li - first]
                    fo.write(json.dumps({"recipe_id": rid, "line_index": li, "text": text[a_:b_], "spans": spans,
                                         "model": sha}, ensure_ascii=False) + "\n")
            buf.clear()

        for line in fi:
            r = json.loads(line)
            for first, text, offs in chunk_lines(r["lines"], a.max_lines):
                buf.append((r["recipe_id"], first, text, offs))
            n_rec += 1
            if len(buf) >= a.bs * 16:
                flush()
            if a.limit and n_rec >= a.limit:
                break
        if buf:
            flush()
    print(json.dumps({"recipes": n_rec, "model": sha, "device": dev}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
