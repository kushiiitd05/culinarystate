"""R4 graph expansion over the food hierarchy (SSOT §241.1 R4, §241.3 categorical match types).

Edges: ING.parent_ids (FORM_OF / VARIANT_OF) and the Open Food Facts taxonomy (ODbL) via ING external_refs
"OFF:en:…". related(ing) -> {other ING id: PARENT | CHILD | SIBLING | ANCESTOR}. Siblings share a direct parent
with at most `max_siblings` children (broad groups like "vegetable" would make everything a sibling); ANCESTOR is a
grandparent-or-higher OFF group. Relations are match types for the compatibility vector, never equivalence.
Siblings are off by default: leave-cell-out evaluation (reports/del4/graph_expansion_v1.md) found sibling evidence
worse than the global process×target median, while parent/child/ancestor evidence beats it.
"""
from __future__ import annotations

from collections import defaultdict

VERSION = "food_graph@0.1"
RANK = {"PARENT": 0, "CHILD": 1, "SIBLING": 2, "ANCESTOR": 3}


class FoodGraph:
    def __init__(self, ings: list[dict], off_parents: dict[str, list[str]], max_siblings: int = 40):
        self.parents: dict[str, set] = defaultdict(set)              # node -> parent nodes (ING ids and OFF ids)
        self.ing_of: dict[str, set] = defaultdict(set)               # OFF id -> ING ids
        self.node_of: dict[str, set] = defaultdict(set)              # ING id -> its nodes (itself + OFF ids)
        for i in ings:
            self.node_of[i["id"]].add(i["id"])
            self.parents[i["id"]] |= set(i.get("parent_ids") or ())
            for r in i.get("external_refs") or ():
                if r.startswith("OFF:"):
                    self.node_of[i["id"]].add(r[4:])
                    self.ing_of[r[4:]].add(i["id"])
        for o, ps in off_parents.items():
            self.parents[o] |= set(ps)
        self.children: dict[str, set] = defaultdict(set)
        for n, ps in list(self.parents.items()):
            for p in ps:
                self.children[p].add(n)
        self.max_siblings = max_siblings

    def _ings(self, nodes) -> set:
        return {i for n in nodes for i in ({n} if n.startswith("ING-") else self.ing_of.get(n, ()))}

    def _ancestors(self, nodes: set) -> set:
        seen, todo = set(), list(nodes)
        while todo:
            for p in self.parents.get(todo.pop(), ()):
                if p not in seen:
                    seen.add(p)
                    todo.append(p)
        return seen

    def related(self, ing_id: str | None, siblings: bool = False) -> dict[str, str]:
        if not ing_id or ing_id not in self.node_of:
            return {}
        nodes = self.node_of[ing_id]
        direct = {p for n in nodes for p in self.parents.get(n, ())}
        rel: dict[str, str] = {}

        def put(ids, kind):
            for i in ids:
                if i != ing_id and RANK[kind] < RANK.get(rel.get(i), 9):
                    rel[i] = kind
        put(self._ings(direct), "PARENT")
        put(self._ings({c for n in nodes for c in self.children.get(n, ())}), "CHILD")
        if siblings:
            put(self._ings({s for p in direct if len(self.children.get(p, ())) <= self.max_siblings
                            for s in self.children[p]} - nodes), "SIBLING")
        put(self._ings(self._ancestors(direct)), "ANCESTOR")
        return dict(sorted(rel.items()))
