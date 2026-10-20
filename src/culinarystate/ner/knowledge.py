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


def build_context(train_docs: Sequence[tuple], labels: Sequence[str], kind: str, top_k: int = 5) -> str:
    if kind == "K0":
        return ""
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
