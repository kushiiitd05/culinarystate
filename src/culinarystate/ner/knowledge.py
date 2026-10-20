"""S119 Part VII: compact entity-type knowledge context (K0-K3), built from TRAIN docs only (no dev/calibration/test text, no test examples).
K0 none | K1 definitions | K2 + frequent train aliases per type | K3 + train boundary cases (short positive spans, common non-entity neighbours).
The context is ONE fixed string per dataset, prepended as the first segment of a sentence pair; its tokens carry no labels."""
from __future__ import annotations

from collections import Counter, defaultdict
from typing import Dict, Sequence

DEFS: Dict[str, str] = {
    "FOOD": "ingredient or food item", "NAME": "ingredient name", "QUANTITY": "amount or number", "UNIT": "unit of measure",
    "PROCESS": "preparation action", "PHYSICAL_QUALITY": "size texture or form", "COLOR": "colour", "TASTE": "taste", "PURPOSE": "intended use",
    "PART": "part of an ingredient", "STATE": "processed state such as chopped", "TEMP": "temperature such as hot or frozen", "DF": "dry or fresh",
    "SIZE": "size such as large"}


def _k4(train_docs: Sequence[tuple], labels: Sequence[str], budget: int) -> str:
    """K4: compact CONTRASTIVE few-shot context, TRAIN only, word-budgeted so it fits the encoder window next to short recipe lines.
    Parts in priority order: (1) one whole-phrase example per type (most frequent multi-word span, else most frequent span: teaches boundaries),
    (2) contrast pairs from real train ambiguity: surfaces seen under >1 type, 'surface: major type not minor type' (ranked by evidence),
    (3) type definitions are used only as short labels. Stops adding items when the word budget is reached."""
    surf, lab_of = defaultdict(Counter), defaultdict(Counter)
    for text, spans in train_docs:
        for s_, e_, lab in spans:
            if lab in labels:
                w = text[s_:e_].lower()
                surf[lab][w] += 1
                lab_of[w][lab] += 1
    parts, used = [], 0

    def add(piece: str) -> bool:
        nonlocal used
        n = len(piece.split()) + (1 if parts else 0)          # the " ;" separator counts as a word
        if used + n > budget:
            return False
        parts.append(piece)
        used += n
        return True
    for l in sorted(labels):
        multi = [(c, w) for w, c in surf[l].items() if " " in w and c >= 3]
        ex = max(multi)[1] if multi else (surf[l].most_common(1)[0][0] if surf[l] else "")
        if ex and not add(f"{l.lower()} {ex}"):
            break
    pairs = []
    for w, c in lab_of.items():
        if len(c) > 1 and sum(c.values()) >= 5:
            (a, na), (b, nb) = c.most_common(2)
            if nb / (na + nb) >= 0.02:
                pairs.append((nb * (na + nb) ** 0.5, w, a, b))
    for _, w, a, b in sorted(pairs, reverse=True):
        if not add(f"{w} is {a.lower()} not {b.lower()}"):
            break
    return " ; ".join(parts)


def build_context(train_docs: Sequence[tuple], labels: Sequence[str], kind: str, top_k: int = 5, budget: int = 40) -> str:
    if kind == "K0":
        return ""
    if kind == "K4":
        return _k4(train_docs, labels, budget)
    parts = [f"{l.lower()}: {DEFS.get(l, l.lower())}" for l in sorted(labels)]
    if kind == "K1":
        return " ; ".join(parts)
    surf = defaultdict(Counter)
    for text, spans in train_docs:
        for s_, e_, lab in spans:
            if lab in labels:
                surf[lab][text[s_:e_].lower()] += 1
    if kind == "K2":
        return " ; ".join(f"{p} ({', '.join(w for w, _ in surf[l].most_common(top_k))})" for p, l in zip(parts, sorted(labels)))
    # K3: add words that are frequent in train but almost never inside an entity (boundary negatives), taken from train text only
    freq, ent = Counter(), Counter()
    for text, spans in train_docs:
        cov = set()
        for s, e, lab in spans:
            if lab in labels:
                cov |= set(range(s, e))
        pos = 0
        for w in text.split():
            i = text.find(w, pos)
            pos = i + len(w)
            freq[w.lower()] += 1
            ent[w.lower()] += int(any(j in cov for j in range(i, i + len(w))))
    neg = [w for w, n in freq.most_common(200) if n >= 5 and ent[w] / n < 0.1 and w.isalpha()][:top_k * 2]
    base = build_context(train_docs, labels, "K2", top_k)
    return base + " ; not entities: " + ", ".join(neg)


def type_context(train_docs: Sequence[tuple], label: str, labels: Sequence[str], budget: int = 30) -> str:
    """Entity-TYPE-SPECIFIC knowledge context (RecipeBERT-KA-style, our own implementation): definition of ONE type, its most informative train examples (whole phrases first),
    and the real train ambiguities involving that type ('surface is X not Y'). TRAIN only, word-budgeted."""
    surf, lab_of = Counter(), defaultdict(Counter)
    for text, spans in train_docs:
        for s_, e_, lab in spans:
            if lab in labels:
                w = text[s_:e_].lower()
                lab_of[w][lab] += 1
                if lab == label:
                    surf[w] += 1
    parts, used = [f"{label.lower()} means {DEFS.get(label, label.lower())}"], 0
    used = len(parts[0].split())

    def add(piece):
        nonlocal used
        n = len(piece.split()) + 1
        if used + n > budget:
            return False
        parts.append(piece)
        used += n
        return True
    multi = [(c, w) for w, c in surf.items() if " " in w and c >= 2]
    singles = surf.most_common(12)
    ex = [w for _, w in sorted(multi, reverse=True)[:2]] + [w for w, _ in singles if w not in {m for _, m in multi}][:3]
    if ex:
        add("e.g. " + ", ".join(ex[:5]))
    pairs = []
    for w, c in lab_of.items():
        if label in c and len(c) > 1 and sum(c.values()) >= 5:
            (a, na), (b, nb) = c.most_common(2)
            if nb / (na + nb) >= 0.02:
                pairs.append((nb * (na + nb) ** 0.5, w, a, b))
    for _, w, a, b in sorted(pairs, reverse=True):
        if not add(f"{w} is {a.lower()} not {b.lower()}"):
            break
    return " ; ".join(parts)
