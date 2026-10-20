"""Semantic NER benchmark v1 (S118 Part III): frozen splits, label views, strata and metrics.

Everything here is deterministic and library-version independent (hash bucketing, no sklearn). Group = the unit that must not cross
splits: RecipeDB3 = masked-sentence family (numbers masked); TASTEset = recipe, plus byte-identical recipe texts kept in one group.
Splits: test 10% / dev 10% / CALIBRATION 10% / train 70% (RecipeDB3); TASTEset keeps the legacy recipe split (seed 7, 70/15/15)
and carves a 12.5% grouped CALIBRATION set out of train. CALIBRATION is never used to fit encoders, calibrators, aliases or gazetteers.
Dev is for checkpoint/model selection only. All corpus-derived statistics (surface counts, strata) come from TRAIN only.
"""
from __future__ import annotations

import hashlib
import random
import re
from collections import Counter, defaultdict
from typing import Iterable, Sequence

from culinarystate.scoring.metrics import corpus_span_scores

SALT = "CSNER-v1"
NUM = re.compile(r"\d+(?:[./]\d+)?|[¼½¾⅓⅔⅛]")
HEAD_MIN, TAIL_MAX = 20, 4                      # train surface count: head >= 20, mid 5-19, tail 1-4, unseen 0
SEEDS = (1, 2, 3, 4, 5)
TASTESET_LEGACY_SEED = 7
VIEWS = {
    "recipedb3_full": {"NAME", "QUANTITY", "UNIT", "STATE", "TEMP", "DF", "SIZE"},
    "recipedb3_published": {"NAME", "QUANTITY", "UNIT", "STATE", "TEMP", "DF"},      # SIZE excluded (their label_dict)
    "recipedb3_form_state": {"STATE", "DF"},
    "tasteset_native": {"FOOD", "QUANTITY", "UNIT", "PROCESS", "PHYSICAL_QUALITY", "COLOR", "TASTE", "PURPOSE", "PART"},
    "unified_core": {"FOOD", "QUANTITY", "UNIT"},                                    # adapter: NAME -> FOOD
}
ADAPTER_TO_CORE = {"NAME": "FOOD", "FOOD": "FOOD", "QUANTITY": "QUANTITY", "UNIT": "UNIT"}
CHECKPOINT_RULE = "max dev exact micro F1 on the primary view; ties -> earlier epoch; test never read during selection"
STATS_RULE = {"min_effect_delta_micro_f1": 0.003, "ci": "paired grouped bootstrap 95% (groups = split groups), CI must exclude 0",
              "multiplicity": "Holm across the ablation ladder", "n_boot": 1000}
PARETO_RULE = {  # fixed before the first candidate run; a rung is promoted only if ALL hold vs the previous promoted rung
    "gain": "delta exact micro F1 >= 0.003 and Holm-adjusted CI excludes 0 (or delta >= 0 with strictly lower cost and better calibration)",
    "macro_robustness": "exact macro F1 must not fall by more than 0.003",
    "tail_unseen": "tail and unseen-surface F1 must not fall by more than 0.005",
    "calibration": "ECE must not rise by more than 0.01 (when a confidence is produced)",
    "cost": "inference latency <= 2x previous rung unless delta exact micro F1 >= 0.01",
    "reproducibility": "gain present in >= 4 of 5 seeds"}


def bucket(key: str) -> float:
    return int(hashlib.sha256(f"{SALT}|{key}".encode()).hexdigest()[:12], 16) / 16 ** 12


def family(sentence: str) -> str:
    return re.sub(r"\s+", " ", NUM.sub("#", sentence.lower())).strip()


def _part(b: float) -> str:
    return "test" if b < 0.10 else "dev" if b < 0.20 else "calibration" if b < 0.30 else "train"


def split_recipedb3(sentences: Sequence[str]) -> dict[str, list[int]]:
    out: dict[str, list[int]] = defaultdict(list)
    for i, s in enumerate(sentences):
        out[_part(bucket(family(s)))].append(i)
    return {k: out[k] for k in ("train", "calibration", "dev", "test")}


def split_tasteset(texts: Sequence[str]) -> dict[str, list[int]]:
    n = len(texts)
    ids = list(range(n))
    random.Random(TASTESET_LEGACY_SEED).shuffle(ids)
    a, b = int(0.7 * n), int(0.85 * n)
    train, dev, test = sorted(ids[:a]), sorted(ids[a:b]), sorted(ids[b:])
    norm = lambda t: re.sub(r"\s+", " ", t.lower()).strip()
    held = {norm(texts[i]) for i in dev + test}
    quarantined = [i for i in train if norm(texts[i]) in held]          # byte-identical to a dev/test recipe: removed from train
    train = [i for i in train if i not in set(quarantined)]
    cal = [i for i in train if bucket(f"T{i}") < 0.125]
    train = [i for i in train if i not in set(cal)]
    return {"train": train, "calibration": cal, "dev": dev, "test": test, "quarantined_duplicates": quarantined}


def tags_to_bio(tags: Sequence[str], known: set[str]) -> list[str]:
    """RecipeDB3 word tags -> BIO: a new entity starts when a tag differs from the previous word's tag (their BIO file is not released)."""
    out, prev = [], None
    for t in tags:
        if t == "O" or t not in known:
            out.append("O")
            prev = None
        else:
            out.append(("I-" if t == prev else "B-") + t)
            prev = t
    return out


def words_to_spans(words: Sequence[str], bio: Sequence[str]) -> tuple[str, list[tuple[int, int, str]]]:
    """Whitespace-joined text and (start, end, label) spans from word-level BIO tags."""
    text, pos, spans, cur = " ".join(words), 0, [], None
    for w, t in zip(words, bio):
        s, e = pos, pos + len(w)
        pos = e + 1
        if t == "O":
            cur = None
        elif t.startswith("B-") or cur is None or cur[2] != t[2:]:
            cur = [s, e, t[2:]]
            spans.append(cur)
        else:
            cur[1] = e
    return text, [tuple(s) for s in spans]


def surface_counts(docs: Iterable[tuple[str, Sequence[tuple[int, int, str]]]]) -> Counter:
    """(label, lower-cased surface) -> count. Build from the TRAIN split only."""
    c: Counter = Counter()
    for text, spans in docs:
        for s, e, lab in spans:
            c[(lab, text[s:e].lower())] += 1
    return c


def stratum(label: str, surface: str, counts: Counter) -> str:
    n = counts.get((label, surface.lower()), 0)
    return "unseen" if n == 0 else "tail" if n <= TAIL_MAX else "head" if n >= HEAD_MIN else "mid"


def select_checkpoint(log: Sequence[dict], key: str = "dev_micro_f1") -> int:
    """Epoch index (1-based) maximising the DEV score; ties -> earlier. Refuses logs without a dev key."""
    if not log or any(key not in e for e in log):
        raise ValueError(f"checkpoint selection needs '{key}' in every log entry (dev only)")
    best = max(range(len(log)), key=lambda i: (log[i][key], -i))
    return best + 1


def boundary_error_rate(gold: Sequence[tuple], pred: Sequence[tuple]) -> dict:
    """Gold spans with no exact match but an overlapping same-label prediction (boundary error) / type error (overlap, other label)."""
    exact = set(pred)
    n = be = te = 0
    for g in gold:
        n += 1
        if g in exact:
            continue
        if any(p[2] == g[2] and min(p[1], g[1]) > max(p[0], g[0]) for p in pred):
            be += 1
        elif any(min(p[1], g[1]) > max(p[0], g[0]) for p in pred):
            te += 1
    return {"n_gold": n, "boundary_errors": be, "type_errors": te, "boundary_error_rate": be / n if n else 0.0}


def _f1(tp, fp, fn):
    p, r = tp / (tp + fp) if tp + fp else 0.0, tp / (tp + fn) if tp + fn else 0.0
    return 2 * p * r / (p + r) if p + r else 0.0


def strata_f1(docs: Sequence[tuple[str, Sequence, Sequence]], counts: Counter, labels: set[str]) -> dict:
    """Exact F1 by train-surface stratum: gold side stratified by gold surface, prediction side by predicted surface."""
    tp, fp, fn = Counter(), Counter(), Counter()
    for text, gold, pred in docs:
        g = {x for x in gold if x[2] in labels}
        p = {x for x in pred if x[2] in labels}
        for x in g:
            (tp if x in p else fn)[stratum(x[2], text[x[0]:x[1]], counts)] += 1
        for x in p - g:
            fp[stratum(x[2], text[x[0]:x[1]], counts)] += 1
    out = {k: {"f1": round(_f1(tp[k], fp[k], fn[k]), 4), "tp": tp[k], "fp": fp[k], "fn": fn[k]} for k in ("head", "mid", "tail", "unseen")}
    seen_tp, seen_fp, seen_fn = (sum(c[k] for k in ("head", "mid", "tail")) for c in (tp, fp, fn))
    out["seen_alias"] = {"f1": round(_f1(seen_tp, seen_fp, seen_fn), 4)}
    out["unseen_alias"] = out["unseen"]
    return out


def evaluate(docs: Sequence[tuple[str, Sequence, Sequence]], counts: Counter, view: str) -> dict:
    """docs = (text, gold_spans, pred_spans). Returns exact micro/macro, per-label, relaxed, boundary error, strata for a label view."""
    labels = VIEWS[view]
    pairs = [(g, p) for _, g, p in docs]
    exact = corpus_span_scores(pairs, mode="exact", labels=labels)
    relaxed = corpus_span_scores(pairs, mode="relaxed", labels=labels)
    gold = [[x for x in g if x[2] in labels] for _, g, _ in docs]
    pred = [[x for x in p if x[2] in labels] for _, _, p in docs]
    be = [boundary_error_rate(g, p) for g, p in zip(gold, pred)]
    n = sum(b["n_gold"] for b in be)
    return {"view": view, "exact": exact, "relaxed": relaxed,
            "boundary_error_rate": sum(b["boundary_errors"] for b in be) / n if n else 0.0,
            "type_error_rate": sum(b["type_errors"] for b in be) / n if n else 0.0, "strata": strata_f1(docs, counts, labels)}
