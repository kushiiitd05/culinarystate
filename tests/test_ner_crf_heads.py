"""S119 Part XX: CRF decode legality, forward-backward marginals, span probability, span-head offsets/loss. Needs torch (recsys_env); skipped otherwise."""
import itertools

import pytest

torch = pytest.importorskip("torch")
from culinarystate.ner.crf import CRF, marginals, span_prob  # noqa: E402
from culinarystate.ner.heads import SpanHead, bio_to_spans  # noqa: E402

T = 5            # O, B-X, I-X, B-Y, I-Y


def _crf(seed=0):
    torch.manual_seed(seed)
    c = CRF(T)
    for p in (c.trans, c.start, c.end):
        torch.nn.init.normal_(p, std=0.5)
    return c


def _brute(c, e):
    M = e.size(0)
    out = {}
    for path in itertools.product(range(T), repeat=M):
        s = c.start[path[0]] + e[0, path[0]] + sum(c.trans[path[t - 1], path[t]] + e[t, path[t]] for t in range(1, M)) + c.end[path[-1]]
        out[path] = float(s)
    z = torch.logsumexp(torch.tensor(list(out.values())), 0)
    return {p: float(torch.exp(torch.tensor(s) - z)) for p, s in out.items()}


def test_marginals_and_span_prob_match_brute_force():
    c, e = _crf(), torch.randn(4, T)
    pr = _brute(c, e)
    m = marginals(c, e)
    for t in range(4):
        for k in range(T):
            assert abs(float(m[t, k]) - sum(p for path, p in pr.items() if path[t] == k)) < 1e-4
    got = span_prob(c, e, 1, 2, 1, 2)                                   # B-X I-X at positions 1-2, next position not I-X
    want = sum(p for path, p in pr.items() if path[1] == 1 and path[2] == 2 and (path[3] != 2))
    assert abs(got - want) < 1e-4
    assert abs(span_prob(c, e, 0, 0, 1, 2) - sum(p for path, p in pr.items() if path[0] == 1 and path[1] != 2)) < 1e-4
    assert abs(span_prob(c, e, 2, 3, 1, 2) - sum(p for path, p in pr.items() if path[2] == 1 and path[3] == 2)) < 1e-4      # span at the end


def test_decode_is_the_argmax_path():
    c, e = _crf(1), torch.randn(1, 4, T)
    path = c.decode(e, torch.ones(1, 4, dtype=torch.bool))[0]
    best = max(_brute(c, e[0]).items(), key=lambda kv: kv[1])[0]
    assert tuple(path) == best


def test_bio_to_spans_offsets_and_orphan_i():
    id2 = {0: "O", 1: "B-X", 2: "I-X", 3: "B-Y", 4: "I-Y"}
    assert bio_to_spans([1, 2, 0, 3, 4, 4, 2], id2) == [(0, 1, "X"), (3, 5, "Y"), (6, 6, "X")]


def test_span_head_loss_decreases_and_scores_in_unit_interval():
    torch.manual_seed(0)
    z = torch.randn(2, 6, 16)
    head = SpanHead(16, 2)
    gold = [[(0, 1, 0), (3, 3, 1)], [(2, 4, 1)]]
    opt = torch.optim.Adam(head.parameters(), lr=1e-2)
    first = float(head.loss(z, gold, [6, 6]))
    for _ in range(60):
        loss = head.loss(z, gold, [6, 6])
        opt.zero_grad(), loss.backward(), opt.step()
    assert float(loss) < first
    sc = head.score_spans(z, 0, [(0, 1), (4, 5)])
    assert all(0 <= s <= 1 for s in sc) and sc[0] > sc[1]
