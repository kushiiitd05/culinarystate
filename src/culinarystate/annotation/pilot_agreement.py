"""S101 pilot Gold agreement: Kush vs Parv on the same recipe, with a categorised disagreement table.

Entity labels are free text, so B's labels are mapped onto A's with `align_entities` (ingredient Adds by order, derived
entities by ancestor overlap) before events, coreference and state are compared; label choice alone is never a disagreement.
Categories (the S101 grouping): boundary, entity_type, canonical_identity, event_type, event_argument, coref,
intermediate_identity, quantity, final_state. A span present in only one file is `entity_type`; a QUANTITY/UNIT span in any
mismatch is `quantity`.
"""
from __future__ import annotations

import copy

from culinarystate.scoring.metrics import b_cubed, corpus_span_scores, relation_scores, tuple_prf
from culinarystate.scoring.state_metrics import edge_tuples, final_fields, STRUCTURAL
from culinarystate.state_graph.engine import Add, replay

from .gold import to_events

CATEGORIES = ("boundary", "entity_type", "canonical_identity", "event_type", "event_argument", "coref",
              "intermediate_identity", "quantity", "final_state")
ARG_KEYS = ("inputs", "output", "outputs", "process", "tool", "medium", "time", "temperature", "endpoint", "portion",
            "fraction", "location", "field", "value", "sets")
QTY_LABELS = {"QUANTITY", "UNIT"}


def _align(doc_a: dict, doc_b: dict) -> dict[str, str]:
    from culinarystate.scoring.state_metrics import align_entities
    return align_entities(to_events(doc_a), to_events(doc_b))


def relabel_doc(doc: dict, mapping: dict[str, str]) -> dict:
    """Copy of `doc` with entity labels renamed (unmapped labels get '~' so they cannot collide)."""
    m = lambda x: mapping.get(x, f"~{x}")  # noqa: E731
    out = copy.deepcopy(doc)
    for li in out["ingredient_lines"]:
        li["entity"] = m(li["entity"])
    for st in out["steps"]:
        for c in st.get("coref", []):
            c["entity"] = m(c["entity"]) if c["entity"] != "UNKNOWN" else c["entity"]
        for ev in st["events"]:
            for k in ("target", "output"):
                if k in ev:
                    ev[k] = m(ev[k])
            if "inputs" in ev:
                ev["inputs"] = [m(x) for x in ev["inputs"]]
            if "outputs" in ev:
                ev["outputs"] = [{**o, "label": m(o["label"])} for o in ev["outputs"]]
    return out


def _ek(ev: dict) -> tuple:
    return (ev["type"], ev.get("target", ""), tuple(ev.get("inputs", [])), ev.get("output", ""),
            tuple(sorted(o["label"] for o in ev.get("outputs", []))), ev.get("process", ""))


def _evkey_loose(ev: dict) -> tuple:
    return (ev["type"], ev.get("target") or "+".join(ev.get("inputs", [])))


def _units(doc: dict) -> list[tuple[str, dict]]:
    return [(f"line {x['line_index']}", x) for x in doc["ingredient_lines"]] + \
           [(f"step {x['step_index']}", x) for x in doc["steps"]]


def _span_cat(sa: dict | None, sb: dict | None) -> str:
    labs = {s["label"] for s in (sa, sb) if s}
    if labs & QTY_LABELS:
        return "quantity"
    if sa and sb:
        return "boundary" if sa["label"] == sb["label"] else "entity_type"
    return "entity_type"


def disagreements(doc_a: dict, doc_b: dict, mapping: dict[str, str]) -> list[dict]:
    rid, b = doc_a["recipe_id"], relabel_doc(doc_b, mapping)
    rows: list[dict] = []

    def add(cat, where, field, ka, kb):
        rows.append({"recipe_id": rid, "category": cat, "where": where, "field": field, "kush": str(ka), "parv": str(kb),
                     "adjudicated": "", "rationale": "", "handbook_rule": ""})
    ub = dict(_units(b))
    for where, ua in _units(doc_a):
        x = ub.get(where)
        if x is None:
            continue
        txt = ua["text"]
        sa, sb = list(ua["spans"]), list(x["spans"])
        matched_b = set()
        for s in sa:
            hit = next((j for j, t in enumerate(sb) if j not in matched_b and (t["start"], t["end"], t["label"]) ==
                        (s["start"], s["end"], s["label"])), None)
            if hit is not None:
                matched_b.add(hit)
                continue
            ov = next((j for j, t in enumerate(sb) if j not in matched_b and t["start"] < s["end"] and s["start"] < t["end"]), None)
            if ov is not None:
                matched_b.add(ov)
                add(_span_cat(s, sb[ov]), where, "span", f"{s['label']}:{txt[s['start']:s['end']]}",
                    f"{sb[ov]['label']}:{txt[sb[ov]['start']:sb[ov]['end']]}")
            else:
                add(_span_cat(s, None), where, "span", f"{s['label']}:{txt[s['start']:s['end']]}", "")
        for j, t in enumerate(sb):
            if j not in matched_b:
                add(_span_cat(None, t), where, "span", "", f"{t['label']}:{txt[t['start']:t['end']]}")
        if "concept" in ua and ua["concept"] != x["concept"]:
            add("canonical_identity", where, "concept", ua["concept"], x["concept"])
        if ua.get("quantity_override") != x.get("quantity_override"):
            add("quantity", where, "quantity_override", ua.get("quantity_override"), x.get("quantity_override"))
        if "events" in ua:
            ea, eb = list(ua["events"]), list(x["events"])
            used = set()
            for e in ea:
                j = next((j for j, f in enumerate(eb) if j not in used and _ek(f) == _ek(e)), None)
                if j is not None:
                    used.add(j)
                    diff = [k for k in ARG_KEYS if e.get(k) != eb[j].get(k)]
                    if diff:
                        add("event_argument", where, e["type"] + ":" + ",".join(diff),  # S166: was 6 args
                            {k: e.get(k) for k in diff}, {k: eb[j].get(k) for k in diff})
                    continue
                j = next((j for j, f in enumerate(eb) if j not in used and _evkey_loose(f) == _evkey_loose(e)), None)
                if j is not None:
                    used.add(j)
                    f = eb[j]
                    cat = "intermediate_identity" if (e.get("output") and f.get("output") and e.get("output") != f.get("output")) \
                        else "event_argument"
                    add(cat, where, "event", _ek(e), _ek(f))
                else:
                    add("event_type", where, "event", e["type"] + ":" + str(_evkey_loose(e)), "")
            for j, f in enumerate(eb):
                if j not in used:
                    add("event_type", where, "event", "", f["type"] + ":" + str(_evkey_loose(f)))
            ca = {(c["start"], c["entity"]) for c in ua.get("coref", [])}
            cb = {(c["start"], c["entity"]) for c in x.get("coref", [])}
            for s in sorted(ca ^ cb):
                add("coref", where, "coref", s if s in ca else "", s if s in cb else "")
    fa, fb = final_fields(replay(to_events(doc_a))), final_fields(replay(to_events(b)))
    for k in sorted(set(fa) | set(fb)):
        if fa.get(k) != fb.get(k):
            add("quantity" if k[1] == "qty" else "final_state", "final", f"{k[0]}.{k[1]}", fa.get(k), fb.get(k))
    return rows


def _spans(items):
    return [(s["start"], s["end"], s["label"]) for s in items]


def recipe_metrics(doc_a: dict, doc_b: dict) -> dict:
    mapping = _align(doc_a, doc_b)
    b = relabel_doc(doc_b, mapping)
    ga, gb = replay(to_events(doc_a)), replay(to_events(b))
    units_b = dict(_units(b))
    pairs = [(_spans(ua["spans"]), _spans(units_b[w]["spans"])) for w, ua in _units(doc_a) if w in units_b]
    ev_a = [_ek(e) for s in doc_a["steps"] for e in s["events"]]
    ev_b = [_ek(e) for s in b["steps"] for e in s["events"]]
    lines = [(x, y) for x, y in zip(doc_a["ingredient_lines"], b["ingredient_lines"])]
    unk = [(x["concept"] == "UNKNOWN") != (y["concept"] == "UNKNOWN") for x, y in lines]
    ca = [{f"{s['step_index']}:{c['start']}", f"E:{c['entity']}"} for s in doc_a["steps"] for c in s.get("coref", [])]
    cb = [{f"{s['step_index']}:{c['start']}", f"E:{c['entity']}"} for s in b["steps"] for c in s.get("coref", [])]
    adds_a = {e.label for e in to_events(doc_a) if isinstance(e, Add)}
    der_a = {x for x in ga.versions if x not in adds_a}
    der_b = {x for x in gb.versions if x not in {e.label for e in to_events(b) if isinstance(e, Add)}}
    proc_a = sorted(e.get("process", "") for s in doc_a["steps"] for e in s["events"] if e.get("process"))
    proc_b = sorted(e.get("process", "") for s in b["steps"] for e in s["events"] if e.get("process"))
    return {
        "recipe_id": doc_a["recipe_id"], "alignment": mapping,
        "spans_exact": corpus_span_scores(pairs, "exact"), "spans_relaxed": corpus_span_scores(pairs, "relaxed"),
        "concept_agreement": sum(x["concept"] == y["concept"] for x, y in lines) / len(lines) if lines else None,
        "unknown_disagreement_rate": sum(unk) / len(unk) if unk else None,
        "process_link_f1": tuple_prf(proc_a, proc_b).as_dict(),
        "event_f1_strict": tuple_prf(ev_a, ev_b).as_dict(),
        "event_f1_loose": tuple_prf([_evkey_loose(e) for s in doc_a["steps"] for e in s["events"]],
                                    [_evkey_loose(e) for s in b["steps"] for e in s["events"]]).as_dict(),
        "relation": relation_scores(edge_tuples(ga), edge_tuples(gb)),
        "structural_relation_f1": tuple_prf(edge_tuples(ga, STRUCTURAL), edge_tuples(gb, STRUCTURAL)).as_dict(),
        "coref_b_cubed": b_cubed(ca, cb) if ca or cb else None,
        "intermediate_entity_f1": tuple_prf(der_a, der_b).as_dict(),
        "alive_entity_f1": tuple_prf(ga.alive(), gb.alive()).as_dict(),
        "state_field_agreement": _field_agree(final_fields(ga), final_fields(gb)),
        "replay_consistent": {"a_issues": list(ga.issues), "b_issues": list(gb.issues),
                              "ok": not ga.issues and not gb.issues},
    }


def _field_agree(fa: dict, fb: dict) -> dict:
    keys = set(fa) | set(fb)
    return {"n": len(keys), "agree": round(sum(fa.get(k) == fb.get(k) for k in keys) / len(keys), 4) if keys else None}
