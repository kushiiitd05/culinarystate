"""k-best Viterbi for the v1 CRF class (python 3.8 safe). Kept in a new module: gpu/ner_bench/crf.py is part of the immutable v1 archive."""
import torch


@torch.no_grad()
def decode_nbest(crf, e, mask, k=5):
    """e [B,M,T] emissions, mask [B,M] prefix-contiguous. Returns, per sequence, a list of (score, path) sorted best-first (up to k distinct tag paths)."""
    out = []
    T = e.size(2)
    for b in range(e.size(0)):
        n = int(mask[b].sum().item())
        if n == 0:
            out.append([])
            continue
        sc = (crf.start + e[b, 0]).unsqueeze(1)                 # [T,1]  best scores per tag, rank-ordered
        back = []
        for t in range(1, n):
            kk = sc.size(1)
            cand = sc.unsqueeze(2) + crf.trans.unsqueeze(1) + e[b, t].view(1, 1, T)    # [prev tag, rank, cur tag]
            flat = cand.permute(2, 0, 1).reshape(T, T * kk)     # [cur tag, prev*rank]
            top = flat.topk(min(k, T * kk), dim=1)
            back.append((top.indices // kk, top.indices % kk))   # prev tag, prev rank
            sc = top.values
        fin = (sc + crf.end.unsqueeze(1)).reshape(-1)
        best = fin.topk(min(k, fin.numel()))
        res = []
        for val, idx in zip(best.values.tolist(), best.indices.tolist()):
            tag, rank = idx // sc.size(1), idx % sc.size(1)
            path = [tag]
            for pt, pr in reversed(back):
                tag, rank = int(pt[tag, rank]), int(pr[tag, rank])
                path.append(tag)
            res.append((val, path[::-1]))
        out.append(res)
    return out
