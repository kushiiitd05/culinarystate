"""Inter-annotator agreement (Kush vs Parv) + adjudication rows for one recipe.

Spans: exact/relaxed F1 (A treated as reference; F1 is symmetric) and character-level Cohen's kappa.
Concepts: exact agreement per ingredient line. Coref: B³. State: both docs are compiled and replayed,
then compared with DEL-3 state metrics, so disagreements that change the state graph are visible.
"""
from __future__ import annotations

from collections import Counter

from culinarystate.scoring.metrics import b_cubed, corpus_span_scores
from culinarystate.scoring.state_metrics import state_scores
from culinarystate.state_graph.engine import replay

from .gold import to_events


def _spans(items: list[dict]) -> list[tuple[int, int, str]]:
    return [(s["start"], s["end"], s["label"]) for s in items]


def char_kappa(text: str, a: list[dict], b: list[dict]) -> float | None:
    def labels(spans):
        lab = ["O"] * len(text)
        for s in spans:
            for i in range(s["start"], min(s["end"], len(text))):
                lab[i] = s["label"]
        return lab
    la, lb = labels(a), labels(b)
    n = len(text)
    if n == 0:
        return None
    po = sum(x == y for x, y in zip(la, lb)) / n
    ca, cb = Counter(la), Counter(lb)
    pe = sum(ca[k] * cb.get(k, 0) for k in ca) / (n * n)
    return round((po - pe) / (1 - pe), 4) if pe < 1 else 1.0


def _pairs(doc_a: dict, doc_b: dict, key: str, idx: str) -> list[tuple[dict, dict]]:
    by_b = {x[idx]: x for x in doc_b[key]}
    return [(x, by_b[x[idx]]) for x in doc_a[key] if x[idx] in by_b]


def agreement(doc_a: dict, doc_b: dict) -> dict:
    if doc_a["recipe_id"] != doc_b["recipe_id"]:
        raise ValueError("different recipes")
    lines = _pairs(doc_a, doc_b, "ingredient_lines", "line_index")
    steps = _pairs(doc_a, doc_b, "steps", "step_index")
    span_docs = [(_spans(a["spans"]), _spans(b["spans"])) for a, b in lines + steps]
    kappas = [k for a, b in lines + steps if (k := char_kappa(a["text"], a["spans"], b["spans"])) is not None]
    concept_agree = sum(a["concept"] == b["concept"] for a, b in lines) / len(lines) if lines else None
    ca = [{f"{st['step_index']}:{c['start']}"} | {f"E:{c['entity']}"} for st in doc_a["steps"] for c in st.get("coref", [])]
    cb = [{f"{st['step_index']}:{c['start']}"} | {f"E:{c['entity']}"} for st in doc_b["steps"] for c in st.get("coref", [])]
    ga, gb = replay(to_events(doc_a)), replay(to_events(doc_b))
    return {
        "recipe_id": doc_a["recipe_id"],
        "spans_exact": corpus_span_scores(span_docs, "exact"),
        "spans_relaxed": corpus_span_scores(span_docs, "relaxed")["micro"],
        "char_kappa_mean": round(sum(kappas) / len(kappas), 4) if kappas else None,
        "concept_agreement": round(concept_agree, 4) if concept_agree is not None else None,
        "coref_b_cubed": b_cubed(ca, cb) if ca or cb else None,
        "state": state_scores(ga, gb),
        "issues_a": list(ga.issues), "issues_b": list(gb.issues),
    }


def adjudication_rows(doc_a: dict, doc_b: dict) -> list[dict]:
    """Disagreements for the adjudication sheet (annotation/adjudication_template.csv columns)."""
    rows = []
    for a, b in _pairs(doc_a, doc_b, "ingredient_lines", "line_index"):
        for fld in ("concept", "entity", "optional"):
            if a.get(fld) != b.get(fld):
                rows.append(_row(doc_a, f"line {a['line_index']}", fld, a.get(fld), b.get(fld)))
        sa, sb = set(map(tuple, _spans(a["spans"]))), set(map(tuple, _spans(b["spans"])))
        for s in sorted(sa ^ sb):
            rows.append(_row(doc_a, f"line {a['line_index']}", "span", s if s in sa else "", s if s in sb else ""))
    for a, b in _pairs(doc_a, doc_b, "steps", "step_index"):
        ea = sorted(_event_key(e) for e in a["events"])
        eb = sorted(_event_key(e) for e in b["events"])
        for e in sorted(set(ea) ^ set(eb)):
            rows.append(_row(doc_a, f"step {a['step_index']}", "event", e if e in ea else "", e if e in eb else ""))
        sa, sb = set(_spans(a["spans"])), set(_spans(b["spans"]))
        for s in sorted(sa ^ sb):
            rows.append(_row(doc_a, f"step {a['step_index']}", "span", s if s in sa else "", s if s in sb else ""))
    return rows


def _event_key(e: dict) -> str:
    parts = [e["type"], e.get("target", ""), "+".join(e.get("inputs", [])), e.get("output", ""), e.get("process", "")]
    return "|".join(parts)


def _row(doc: dict, where: str, field: str, a, b) -> dict:
    return {"recipe_id": doc["recipe_id"], "where": where, "field": field, "kush": str(a), "parv": str(b),
            "adjudicated": "", "rationale": "", "handbook_rule": ""}
