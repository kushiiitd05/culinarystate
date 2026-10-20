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
