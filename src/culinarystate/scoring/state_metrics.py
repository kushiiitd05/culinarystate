"""DEL-3 state-graph metrics on top of the common scorer.

Gold and predicted graphs are replayed engine Graphs. Entities are aligned by label (gold
annotation guidelines require canonical entity labels per recipe); relations are compared as
(src_entity, relation, dst_entity) with version numbers dropped, so a correct edge at a different
version index is not double-penalised.
"""
from __future__ import annotations

from culinarystate.state_graph.engine import Graph, replay

from .metrics import relation_scores, tuple_prf

STRUCTURAL = ("MERGES_INTO", "SPLITS_INTO", "RESERVED_AS", "DISCARDED_FROM", "RECOMBINED_WITH")


def _ent(ref: str) -> str:
    return ref.split("@", 1)[0]


def edge_tuples(g: Graph, relations: tuple[str, ...] | None = None) -> list[tuple[str, str, str]]:
    return [(_ent(e.src), e.relation, _ent(e.dst)) for e in g.edges if relations is None or e.relation in relations]


def final_fields(g: Graph) -> dict[tuple[str, str], str]:
    out = {}
    for ent in g.alive():
        v = g.current(ent)
        for name, b in v.fields:
            out[(ent, name)] = b.value
        out[(ent, "location")] = v.location or ""
        out[(ent, "qty")] = v.qty.render()
    return out


def state_scores(gold: Graph, pred: Graph) -> dict:
    gf, pf = final_fields(gold), final_fields(pred)
    keys = set(gf)
    correct = sum(1 for k in keys if pf.get(k) == gf[k])
    alive = tuple_prf(gold.alive(), pred.alive())
    return {
        "state_field_accuracy": round(correct / len(keys), 4) if keys else None,
        "n_state_fields": len(keys),
        "alive_entities": alive.as_dict(),
        "merge_split_f1": tuple_prf(edge_tuples(gold, STRUCTURAL), edge_tuples(pred, STRUCTURAL)).as_dict(),
        "all_edges": relation_scores(edge_tuples(gold), edge_tuples(pred)),
        "pred_issues": list(pred.issues),
    }


def replay_consistency(events) -> dict:
    a, b = replay(events), replay(list(events))
    return {"deterministic": a.sha256() == b.sha256(), "issues": list(a.issues), "sha256": a.sha256()}


# ------------------------------------------------------------------ entity alignment
def _ancestors(g: Graph) -> dict[str, frozenset[str]]:
    """Ingredient (root) ancestors of every entity, via structural/transform edges."""
    parents: dict[str, set[str]] = {e: set() for e in g.versions}
    for e in g.edges:
        s, d = _ent(e.src), _ent(e.dst)
        if d in parents and s != d and e.relation in ("MERGES_INTO", "SPLITS_INTO", "RESERVED_AS", "RECOMBINED_WITH"):
            parents[d].add(s)
    memo: dict[str, frozenset[str]] = {}

    def anc(x: str, seen=()) -> frozenset[str]:
        if x in memo:
            return memo[x]
        if not parents[x] or x in seen:
            memo[x] = frozenset({x})
            return memo[x]
        out = frozenset().union(*(anc(p, seen + (x,)) for p in parents[x]))
        memo[x] = out
        return out
    return {x: anc(x) for x in g.versions}


def align_entities(gold_events: list, pred_events: list) -> dict[str, str]:
    """Map predicted entity labels -> gold labels. Ingredient Adds align by order; derived entities by
    Jaccard overlap of (aligned) ingredient ancestors, greedy best-first, one-to-one."""
    from culinarystate.state_graph.engine import Add
    g_adds = [e.label for e in gold_events if isinstance(e, Add)]
    p_adds = [e.label for e in pred_events if isinstance(e, Add)]
    mapping = {p: g for p, g in zip(p_adds, g_adds)}
    gg, gp = replay(gold_events), replay(pred_events)
    ga, pa = _ancestors(gg), _ancestors(gp)
    g_derived = [x for x in gg.versions if x not in g_adds]
    p_derived = [x for x in gp.versions if x not in p_adds]
    cands = []
    for p in p_derived:
        pset = frozenset(mapping.get(a, a) for a in pa[p])
        for g in g_derived:
            inter, union = len(pset & ga[g]), len(pset | ga[g])
            if inter:
                cands.append((inter / union, p, g))
    used_g: set[str] = set()
    for score, p, g in sorted(cands, key=lambda t: (-t[0], t[1], t[2])):
        if p not in mapping and g not in used_g:
            mapping[p] = g
            used_g.add(g)
    return mapping


def relabel(events: list, mapping: dict[str, str]) -> list:
    """Rename entity labels inside events (unmapped labels kept, prefixed to avoid accidental matches)."""
    import dataclasses

    def m(x):
        return mapping.get(x, f"~{x}")
    out = []
    for ev in events:
        changes = {}
        for f in dataclasses.fields(ev):
            v = getattr(ev, f.name)
            if f.name in ("label", "target", "output", "source", "reserved"):
                changes[f.name] = m(v)
            elif f.name == "inputs":
                changes[f.name] = tuple(m(x) for x in v)
            elif f.name == "outputs":
                changes[f.name] = tuple((m(lbl), fr) for lbl, fr in v)
        out.append(dataclasses.replace(ev, **changes))
    return out


def aligned_state_scores(gold_events: list, pred_events: list) -> dict:
    mapping = align_entities(gold_events, pred_events)
    res = state_scores(replay(gold_events), replay(relabel(pred_events, mapping)))
    res["alignment"] = mapping
    return res
