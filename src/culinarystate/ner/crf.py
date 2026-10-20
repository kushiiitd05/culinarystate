"""Linear-chain CRF in plain torch (no extra package on the server). Plan Part K: encoder ± CRF.

Operates on the labelled positions only (first sub-token of each word): `compact` gathers them into a contiguous
sequence, so sub-token positions never enter the transition structure.
"""
from __future__ import annotations

import torch
from torch import nn


def compact(emissions: torch.Tensor, mask: torch.Tensor):
    """[B,L,T] + bool [B,L] -> [B,M,T], [B,M] bool, gather index [B,M] (M = max labelled positions)."""
    lengths = mask.sum(1)
    m = int(lengths.max().item()) if lengths.numel() else 0
    idx = torch.zeros(mask.size(0), max(m, 1), dtype=torch.long, device=mask.device)
    cmask = torch.zeros(mask.size(0), max(m, 1), dtype=torch.bool, device=mask.device)
    for b in range(mask.size(0)):
        pos = mask[b].nonzero(as_tuple=True)[0]
        idx[b, :len(pos)], cmask[b, :len(pos)] = pos, True
    e = emissions.gather(1, idx.unsqueeze(-1).expand(-1, -1, emissions.size(-1)))
    return e, cmask, idx


class CRF(nn.Module):
    def __init__(self, num_tags: int):
        super().__init__()
        self.trans = nn.Parameter(torch.zeros(num_tags, num_tags))
        self.start = nn.Parameter(torch.zeros(num_tags))
        self.end = nn.Parameter(torch.zeros(num_tags))

    def nll(self, e: torch.Tensor, tags: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
        """Mean negative log-likelihood; e [B,M,T], tags [B,M], mask [B,M] (prefix-contiguous)."""
        tags = tags.clamp(min=0)
        b = torch.arange(e.size(0), device=e.device)
        score = self.start[tags[:, 0]] + e[b, 0, tags[:, 0]]
        alpha = self.start + e[:, 0]
        for t in range(1, e.size(1)):
            m = mask[:, t]
            score = score + (self.trans[tags[:, t - 1], tags[:, t]] + e[b, t, tags[:, t]]) * m
            nxt = torch.logsumexp(alpha.unsqueeze(2) + self.trans + e[:, t].unsqueeze(1), dim=1)
            alpha = torch.where(m.unsqueeze(1), nxt, alpha)
        last = tags.gather(1, (mask.sum(1) - 1).clamp(min=0).unsqueeze(1)).squeeze(1)
        score = score + self.end[last]
        return (torch.logsumexp(alpha + self.end, dim=1) - score).mean()

    @torch.no_grad()
    def decode(self, e: torch.Tensor, mask: torch.Tensor) -> list[list[int]]:
        out = []
        for b in range(e.size(0)):
            n = int(mask[b].sum().item())
            if n == 0:
                out.append([])
                continue
            v, back = self.start + e[b, 0], []
            for t in range(1, n):
                s = v.unsqueeze(1) + self.trans
                back.append(s.argmax(0))
                v = s.max(0).values + e[b, t]
            best = [int((v + self.end).argmax())]
            for bp in reversed(back):
                best.append(int(bp[best[-1]]))
            out.append(best[::-1])
        return out


def _fb(crf: "CRF", e: torch.Tensor):
    """Forward/backward log-messages for ONE sequence e [M,T] (no mask; slice to its length first). Returns alpha, beta, logZ."""
    M, T = e.shape
    alpha = [crf.start + e[0]]
    for t in range(1, M):
        alpha.append(torch.logsumexp(alpha[-1].unsqueeze(1) + crf.trans, dim=0) + e[t])
    beta = [crf.end]
    for t in range(M - 1, 0, -1):
        beta.append(torch.logsumexp(crf.trans + (e[t] + beta[-1]).unsqueeze(0), dim=1))
    beta = beta[::-1]
    return torch.stack(alpha), torch.stack(beta), torch.logsumexp(alpha[-1] + crf.end, dim=0)


@torch.no_grad()
def marginals(crf: "CRF", e: torch.Tensor) -> torch.Tensor:
    """Per-position tag marginals [M,T] for one sequence (rows sum to 1)."""
    a, b, z = _fb(crf, e)
    return torch.exp(a + b - z)


@torch.no_grad()
def span_prob(crf: "CRF", e: torch.Tensor, start: int, end: int, b_tag: int, i_tag: int, fb=None) -> float:
    """P(exactly the span [start, end] tagged B-X I-X ... I-X, with the next position NOT I-X). This is the span confidence the calibrator uses
    (CRF forward-backward marginal of the span's B...I path, not a token softmax). `end` inclusive."""
    a, b, z = fb if fb is not None else _fb(crf, e)
    M = e.size(0)
    tags = [b_tag] + [i_tag] * (end - start)
    if start == 0:
        s = crf.start[tags[0]] + e[start, tags[0]]
    else:
        s = torch.logsumexp(a[start - 1] + crf.trans[:, tags[0]], dim=0) + e[start, tags[0]]
    for k in range(1, len(tags)):
        s = s + crf.trans[tags[k - 1], tags[k]] + e[start + k, tags[k]]
    if end == M - 1:
        s = s + crf.end[tags[-1]]
    else:
        nxt = torch.ones(e.size(1), dtype=torch.bool)
        nxt[i_tag] = False                                                   # boundary: the following tag must not continue the span
        msg = crf.trans[tags[-1]] + e[end + 1] + b[end + 1]
        s = s + torch.logsumexp(msg[nxt], dim=0)
    return float(torch.exp(s - z))
