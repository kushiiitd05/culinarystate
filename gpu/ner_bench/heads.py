"""S119 Part X: span-boundary auxiliary head. Shares the (fused) token representation z with the CRF; the CRF still DECODES (rescoring by this head is a
separate, later ablation). Heads: P(start_i), P(end_j), P(type | i,j). Loss = L_CRF + lambda_span * L_span, lambda fixed on dev, never on test."""
from __future__ import annotations

from typing import List, Sequence, Tuple

import torch
from torch import nn


def bio_to_spans(tag_ids: Sequence[int], id2tag: dict) -> List[Tuple[int, int, str]]:
    """Word-position BIO ids (-100 ignored upstream) -> (start, end_inclusive, label). An orphan I- opens a span (lenient, like decode)."""
    spans, cur = [], None
    for p, t in enumerate(tag_ids):
        tag = id2tag[t]
        if tag == "O":
            cur = None
            continue
        kind, lab = tag.split("-", 1)
        if kind == "I" and cur and cur[2] == lab:
            cur[1] = p
        else:
            cur = [p, p, lab]
            spans.append(cur)
    return [tuple(s) for s in spans]


class SpanHead(nn.Module):
    def __init__(self, hidden: int, n_types: int, max_len: int = 8):
        super().__init__()
        self.start, self.end = nn.Linear(hidden, 1), nn.Linear(hidden, 1)
        self.typ = nn.Sequential(nn.Linear(2 * hidden, hidden), nn.GELU(), nn.Linear(hidden, n_types + 1))   # last class = "not a span"
        self.n_types, self.max_len = n_types, max_len

    def loss(self, z: torch.Tensor, gold: Sequence[Sequence[Tuple[int, int, int]]], lengths: Sequence[int]) -> torch.Tensor:
        """z [B,L,H] at WORD positions (compacted); gold[b] = [(start, end_inclusive, type_id)]. Boundary BCE + type CE over gold spans and sampled negatives."""
        B, L, _ = z.shape
        ys, ye = torch.zeros(B, L, device=z.device), torch.zeros(B, L, device=z.device)
        mask = torch.zeros(B, L, device=z.device)
        pairs, tgt = [], []
        for b in range(B):
            mask[b, :lengths[b]] = 1
            for s, e, t in gold[b]:
                ys[b, s], ye[b, e] = 1, 1
                pairs.append((b, s, e))
                tgt.append(t)
            gs = {(s, e) for s, e, _ in gold[b]}
            for s in range(lengths[b]):                                       # negatives: short spans that are not gold
                for e in range(s, min(lengths[b], s + 3)):
                    if (s, e) not in gs and len(pairs) < 4 * (len(tgt) + 1) + 8:
                        pairs.append((b, s, e))
                        tgt.append(self.n_types)
        bce = nn.functional.binary_cross_entropy_with_logits
        l_b = (bce(self.start(z).squeeze(-1), ys, reduction="none") * mask).sum() / mask.sum() + (bce(self.end(z).squeeze(-1), ye, reduction="none") * mask).sum() / mask.sum()
        if not pairs:
            return l_b
        idx = torch.tensor(pairs, device=z.device)
        feats = torch.cat([z[idx[:, 0], idx[:, 1]], z[idx[:, 0], idx[:, 2]]], dim=-1)
        return l_b + nn.functional.cross_entropy(self.typ(feats), torch.tensor(tgt, device=z.device))

    @torch.no_grad()
    def score_spans(self, z: torch.Tensor, b: int, spans: Sequence[Tuple[int, int]]) -> List[float]:
        """Diagnostic / later rescoring: P(start)*P(end)*P(type!=none) for given spans of item b."""
        out = []
        for s, e in spans:
            f = torch.cat([z[b, s], z[b, e]], dim=-1)
            out.append(float(torch.sigmoid(self.start(z[b, s])) * torch.sigmoid(self.end(z[b, e])) * (1 - self.typ(f).softmax(-1)[-1])))
        return out
