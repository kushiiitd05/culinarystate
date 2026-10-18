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
