"""C14 uncertainty/OOD gate: evidence-support profile per axis (SSOT §257B C14, §243.4 support distance, G16-OOD).

Support = ACTIVE retention-bearing EVD rows. An axis is cold when the query states it and no row supports it;
pair support counts rows for the ingredient (id, parent id, or named inside a group row) AND the process.
OOD = pair unsupported and at least one stated axis cold. OOD caps output precision at QUALITATIVE: no extrapolated
numbers into unsupported regions (SSOT: "not allowed to search unsupported/OOD regions"). Unstated slots are
UNKNOWN (ood=None), never cold.
"""
from __future__ import annotations

import re
from collections import defaultdict

NUMERIC = ("QUANTITATIVE", "INTERVAL")


class SupportIndex:
    def __init__(self, evd: list[dict]):
        self.rows = [e for e in evd if e["status"] == "ACTIVE" and "retention_factor" in (e.get("derived") or {})]
        self.by_ing, self.by_proc = defaultdict(set), defaultdict(set)
        self.group_rows = []
        for i, e in enumerate(self.rows):
            if e["matrix"].get("ingredient_id"):
                self.by_ing[e["matrix"]["ingredient_id"]].add(i)
            else:
                self.group_rows.append((i, (e["matrix"].get("raw_name") or "").lower()))
            if e["process"].get("process_id"):
                self.by_proc[e["process"]["process_id"]].add(i)

    def _ingredient_rows(self, ing: str | None, parents: tuple, name: str | None) -> tuple[set, set]:
        direct = set().union(*(self.by_ing.get(x, set()) for x in (ing, *parents) if x)) if ing else set()
        group = {i for i, raw in self.group_rows if re.search(rf"(?<!\w){re.escape(name.lower())}(?!\w)", raw)} if name else set()
        return direct, group

    def support(self, ing: str | None, parents: tuple, name: str | None, process_id: str | None) -> dict:
        direct, group = self._ingredient_rows(ing, parents, name)
        stated_ing = bool(ing or name)
        proc = self.by_proc.get(process_id, set()) if process_id else set()
        pair_direct, pair_group = direct & proc, group & proc
        cold = [a for a, stated, n in (("ingredient", stated_ing, len(direct | group)),
                                       ("process", bool(process_id), len(proc))) if stated and n == 0]
        pair = len(pair_direct | pair_group)
        ood = None if not (stated_ing and process_id) else (pair == 0 and bool(cold))
        return {"ingredient": len(direct | group), "process": len(proc), "pair": pair,
                "pair_level": "INGREDIENT" if pair_direct else "GROUP" if pair_group else None,
                "cold_axes": cold, "ood": ood}


def cap_precision(precision: str, support: dict) -> tuple[str, str | None]:
    if support.get("ood") and precision in NUMERIC:
        return "QUALITATIVE", "OOD_SUPPORT_CAP"
    return precision, None
