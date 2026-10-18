"""Runtime encoder NER (plan Part K layer 2): DeBERTa-v3 ± CRF trained by gpu/ner_tasteset/train_ner.py --save.

EncoderTagger(model_dir).tag(text) -> [(start, end, LABEL)] in TASTEset's label set. Words are pre-split exactly as
in training (\\w+ | single punctuation), labels sit on the first sub-token, CRF (Viterbi) when the model has one.
torch/transformers are imported lazily (ML env: /opt/anaconda3/envs/recsys_env); bio_to_spans is dependency-free.
Model choice: deberta-v3-large_crf (test 0.933) for server batch; deberta-v3-base_crf (0.927) for the 8 GB Mac.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

VERSION = "encoder_tagger@0.1"
WORD = re.compile(r"\w+|[^\w\s]")


def bio_to_spans(tags: list[str], offsets: list[tuple[int, int]]) -> list[tuple[int, int, str]]:
    """Word-level BIO -> char spans; an I- without a matching open span starts a new one (as in training decode)."""
    spans, cur = [], None
    for tag, (s, e) in zip(tags, offsets):
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


class EncoderTagger:
    def __init__(self, model_dir: str | Path, device: str | None = None):
        import torch
        from transformers import AutoModelForTokenClassification, AutoTokenizer

        from .crf import CRF
        d = Path(model_dir)
        self.meta = json.loads((d / "tagger.json").read_text())
        self.tags = self.meta["tags"]
        self.dev = device or ("mps" if torch.backends.mps.is_available() else "cpu")
        self.tok = AutoTokenizer.from_pretrained(d)
        self.model = AutoModelForTokenClassification.from_pretrained(d).to(self.dev).eval()
        self.crf = None
        if self.meta["crf"]:
            self.crf = CRF(len(self.tags))
            self.crf.load_state_dict(torch.load(d / "crf.pt", map_location="cpu"))
            self.crf = self.crf.to(self.dev).eval()
        self.torch = torch

    def tag(self, text: str) -> list[tuple[int, int, str]]:
        words = [(m.start(), m.end()) for m in WORD.finditer(text or "")]
        if not words:
            return []
        enc = self.tok([text[a:b] for a, b in words], is_split_into_words=True, truncation=True,
                       max_length=self.meta["max_len"], return_tensors="pt")
        firsts, prev = [], None
        for i, w in enumerate(enc.word_ids()):
            if w is not None and w != prev:
                firsts.append((i, w))
            prev = w
        with self.torch.no_grad():
            em = self.model(**{k: v.to(self.dev) for k, v in enc.items()}).logits[0]
            pos = self.torch.tensor([i for i, _ in firsts], device=self.dev)
            e = em.index_select(0, pos).unsqueeze(0)
            ids = self.crf.decode(e, self.torch.ones(1, len(firsts), dtype=self.torch.bool, device=self.dev))[0] \
                if self.crf else e[0].argmax(-1).tolist()
        return bio_to_spans([self.tags[i] for i in ids], [words[w] for _, w in firsts])
