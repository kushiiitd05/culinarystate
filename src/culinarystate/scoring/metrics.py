"""One common scorer for the programme (plan P5-B).

All functions are pure and take plain Python structures so the same code scores NER, linking,
events/relations, coreference, quantities and state graphs. Grouped bootstrap gives CIs over the
unit of independence (recipe family / source family / study), never over individual rows.
"""
from __future__ import annotations

import random
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Callable, Hashable, Iterable, Sequence

Span = tuple[int, int, str]          # (start, end, label), end exclusive


@dataclass(frozen=True)
class PRF:
    tp: float
    fp: float
    fn: float

    @property
    def precision(self) -> float:
        return self.tp / (self.tp + self.fp) if self.tp + self.fp else 0.0

    @property
    def recall(self) -> float:
        return self.tp / (self.tp + self.fn) if self.tp + self.fn else 0.0

    @property
    def f1(self) -> float:
        p, r = self.precision, self.recall
        return 2 * p * r / (p + r) if p + r else 0.0

    def __add__(self, o: "PRF") -> "PRF":
        return PRF(self.tp + o.tp, self.fp + o.fp, self.fn + o.fn)

    def as_dict(self) -> dict:
        return {"tp": self.tp, "fp": self.fp, "fn": self.fn, "precision": round(self.precision, 4),
                "recall": round(self.recall, 4), "f1": round(self.f1, 4)}


# ------------------------------------------------------------------ spans (NER)
def _overlap(a: Span, b: Span) -> int:
    return max(0, min(a[1], b[1]) - max(a[0], b[0]))


def span_prf(gold: Sequence[Span], pred: Sequence[Span], mode: str = "exact",
             labels: set[str] | None = None) -> dict[str, PRF]:
    """Per-label PRF for one document. mode: exact | relaxed (any overlap, same label, 1:1 greedy)."""
    g = [s for s in gold if labels is None or s[2] in labels]
    p = [s for s in pred if labels is None or s[2] in labels]
    out: dict[str, PRF] = defaultdict(lambda: PRF(0, 0, 0))
    used: set[int] = set()
    for ps in p:
        match = None
        for j, gs in enumerate(g):
            if j in used or gs[2] != ps[2]:
                continue
            if (mode == "exact" and gs[:2] == ps[:2]) or (mode == "relaxed" and _overlap(gs, ps) > 0):
                match = j
                break
        if match is None:
            out[ps[2]] += PRF(0, 1, 0)
        else:
            used.add(match)
            out[ps[2]] += PRF(1, 0, 0)
    for j, gs in enumerate(g):
        if j not in used:
            out[gs[2]] += PRF(0, 0, 1)
    return dict(out)


def corpus_span_scores(docs: Iterable[tuple[Sequence[Span], Sequence[Span]]], mode: str = "exact",
                       labels: set[str] | None = None) -> dict:
    per: dict[str, PRF] = defaultdict(lambda: PRF(0, 0, 0))
    for gold, pred in docs:
        for lab, prf in span_prf(gold, pred, mode, labels).items():
            per[lab] += prf
    micro = sum(per.values(), PRF(0, 0, 0))
    macro_f1 = sum(x.f1 for x in per.values()) / len(per) if per else 0.0
    return {"micro": micro.as_dict(), "macro_f1": round(macro_f1, 4),
            "per_label": {k: v.as_dict() for k, v in sorted(per.items())}}


# ------------------------------------------------------------------ entity linking
NIL = "NIL"


def linking_scores(items: Iterable[tuple[str, Sequence[str]]], ks: Sequence[int] = (1, 5)) -> dict:
    """items: (gold_id or NIL, ranked predictions). A NIL gold is correct at k iff the top-1 is NIL
    (abstaining correctly); predicting an id for a NIL gold is an over-link."""
    n, hits, rr, over_link, nil_gold = 0, Counter(), 0.0, 0, 0
    for gold, ranked in items:
        n += 1
        ranked = list(ranked)
        if gold == NIL:
            nil_gold += 1
            ok = bool(ranked) and ranked[0] == NIL or not ranked
            for k in ks:
                hits[k] += ok
            rr += 1.0 if ok else 0.0
            over_link += 0 if ok else 1
            continue
        for k in ks:
            hits[k] += gold in ranked[:k]
        rr += 1.0 / (ranked.index(gold) + 1) if gold in ranked else 0.0
    return {"n": n, **{f"acc@{k}" if k == 1 else f"recall@{k}": round(hits[k] / n, 4) if n else 0.0 for k in ks},
            "mrr": round(rr / n, 4) if n else 0.0, "nil_gold": nil_gold,
            "over_link_rate_on_nil": round(over_link / nil_gold, 4) if nil_gold else None}


# ------------------------------------------------------------------ relations / events / edges
def tuple_prf(gold: Iterable[Hashable], pred: Iterable[Hashable]) -> PRF:
    gc, pc = Counter(gold), Counter(pred)
    tp = sum((gc & pc).values())
    return PRF(tp, sum(pc.values()) - tp, sum(gc.values()) - tp)


def relation_scores(gold: Iterable[tuple], pred: Iterable[tuple], key: Callable[[tuple], str] = lambda t: t[1]) -> dict:
    gold, pred = list(gold), list(pred)
    overall = tuple_prf(gold, pred)
    per = {}
    for lab in sorted({key(t) for t in gold} | {key(t) for t in pred}):
        per[lab] = tuple_prf([t for t in gold if key(t) == lab], [t for t in pred if key(t) == lab]).as_dict()
    return {"overall": overall.as_dict(), "per_relation": per}


# ------------------------------------------------------------------ coreference
def b_cubed(gold_clusters: Sequence[set], pred_clusters: Sequence[set]) -> PRF | dict:
    gmap = {m: frozenset(c) for c in gold_clusters for m in c}
    pmap = {m: frozenset(c) for c in pred_clusters for m in c}
    mentions = set(gmap) | set(pmap)
    if not mentions:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}
    p = sum(len(gmap.get(m, {m}) & pmap.get(m, {m})) / len(pmap.get(m, {m})) for m in mentions) / len(mentions)
    r = sum(len(gmap.get(m, {m}) & pmap.get(m, {m})) / len(gmap.get(m, {m})) for m in mentions) / len(mentions)
    f = 2 * p * r / (p + r) if p + r else 0.0
    return {"precision": round(p, 4), "recall": round(r, 4), "f1": round(f, 4)}


def pairwise_links(clusters: Sequence[set]) -> set[frozenset]:
    out = set()
    for c in clusters:
        items = sorted(c, key=str)
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                out.add(frozenset((items[i], items[j])))
    return out


def coref_scores(gold_clusters: Sequence[set], pred_clusters: Sequence[set]) -> dict:
    return {"b_cubed": b_cubed(gold_clusters, pred_clusters),
            "pairwise": tuple_prf(pairwise_links(gold_clusters), pairwise_links(pred_clusters)).as_dict()}


# ------------------------------------------------------------------ quantities
def quantity_scores(pairs: Iterable[tuple[dict, dict]], rel_tol: float = 0.05) -> dict:
    """pairs of (gold QVALUE, pred QVALUE) for one channel. Reports exact-status agreement, numeric
    accuracy within tolerance, and the invented-value rate (pred numeric where gold is UNKNOWN/QUALITATIVE)."""
    n = status_ok = num_ok = num_n = invented = abstain_wrong = 0
    for g, p in pairs:
        n += 1
        gs, ps = g.get("status"), p.get("status")
        status_ok += gs == ps
        g_num, p_num = gs in ("MEASURED", "RANGE"), ps in ("MEASURED", "RANGE")
        if not g_num and p_num:
            invented += 1
        if g_num and not p_num:
            abstain_wrong += 1
        if g_num and p_num:
            num_n += 1
            gv = g.get("value", None if gs == "RANGE" else 0)
            pv = p.get("value", None if ps == "RANGE" else 0)
            if gs == ps == "MEASURED":
                num_ok += abs(gv - pv) <= rel_tol * max(abs(gv), 1e-9)
            else:
                glo, ghi = (g["low"], g["high"]) if gs == "RANGE" else (gv, gv)
                plo, phi = (p["low"], p["high"]) if ps == "RANGE" else (pv, pv)
                num_ok += plo <= ghi and glo <= phi            # intervals overlap
    return {"n": n, "status_accuracy": round(status_ok / n, 4) if n else 0.0,
            "numeric_accuracy": round(num_ok / num_n, 4) if num_n else None,
            "invented_value_rate": round(invented / n, 4) if n else 0.0,
            "missed_value_rate": round(abstain_wrong / n, 4) if n else 0.0}


# ------------------------------------------------------------------ grouped bootstrap
def grouped_bootstrap(groups: dict[Hashable, list], statistic: Callable[[list], float], n_boot: int = 1000,
                      seed: int = 20261018, alpha: float = 0.05) -> dict:
    """Resample whole groups (recipe family / source / study) with replacement."""
    keys = sorted(groups, key=str)
    if not keys:
        return {"estimate": None, "low": None, "high": None, "n_groups": 0}
    rng = random.Random(seed)
    point = statistic([x for k in keys for x in groups[k]])
    stats = []
    for _ in range(n_boot):
        sample = [x for _ in keys for x in groups[keys[rng.randrange(len(keys))]]]
        stats.append(statistic(sample))
    stats.sort()
    lo = stats[int((alpha / 2) * n_boot)]
    hi = stats[min(n_boot - 1, int((1 - alpha / 2) * n_boot))]
    return {"estimate": round(point, 4), "low": round(lo, 4), "high": round(hi, 4), "n_groups": len(keys),
            "n_boot": n_boot, "seed": seed}
