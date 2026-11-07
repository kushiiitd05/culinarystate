"""Demo context (S171, D-075 M4/M6): load once, answer through the front door. DEMO_ONLY, NON_CITABLE.

TRANSFORMATION handler = the DEL-5 pipeline (slots -> evidence packets -> feasibility -> decision) with the promoted
C16 template verbaliser (B5T: no LLM), plus, when recipe text is supplied, the Step 23a router demo per recipe event
for the question's target state variable. Other §39 branches have no handler yet and abstain (front_door).
"""
from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

from culinarystate.decision import front_door as FD

ROOT = Path(__file__).resolve().parents[3]
SVAR_REGISTRY = ROOT / "registry" / "state_variable_registry_v1.csv"
_CITE = re.compile(r"\bEVD-\d{6}\b")


def svar_for(target: str | None, registry: Sequence[Mapping[str, Any]]) -> str | None:
    """SVAR whose name contains the target phrase; ties broken by most EVD rows, then id. None if no match."""
    if not target or not target.strip():
        return None
    t = re.sub(r"\s+", " ", target.lower()).strip()
    hits = [r for r in registry if re.search(rf"(?<![a-z]){re.escape(t)}(?![a-z])", str(r.get("name", "")).lower())]
    if not hits:
        return None

    def rows(r):
        try:
            return int(r.get("current_row_count") or 0)
        except ValueError:
            return 0
    return sorted(hits, key=lambda r: (-rows(r), r["state_variable_id"]))[0]["state_variable_id"]


def cited_ids(text: str) -> list[str]:
    return list(dict.fromkeys(_CITE.findall(text or "")))


def recipe_summary(out: Mapping[str, Any]) -> dict:
    steps = [{"event_id": i["event_id"], "action": i["action"], "process_id": i["process_id"],
              "ingredient_id": i["ingredient_id"], "route": i["route"], "reasons": list(i["reasons"]),
              "evidence": [e["evd_id"] for e in i["evidence"]]} for i in out["items"]]
    return {"target_svar": out["target_svar"], "routes": dict(sorted(Counter(s["route"] for s in steps).items())),
            "steps": steps}


class DemoContext:
    def __init__(self, **parts: Any) -> None:
        self.__dict__.update(parts)

    @classmethod
    def load(cls) -> "DemoContext":
        from culinarystate.decision.diagnosis import TroubleshootIndex
        from culinarystate.decision.feasibility import load_requirements
        from culinarystate.decision.ood import SupportIndex
        from culinarystate.decision.pipeline import load_lexicon
        from culinarystate.extraction.rung_a import RungA
        from culinarystate.ledgers.store import LedgerStore
        from culinarystate.mechanism import process_signatures as PS
        from culinarystate.mechanism import router_demo as RD
        from culinarystate.quantity import rc2_dryrun as D
        from culinarystate.retrieval.retriever import EvidenceRetriever
        st = LedgerStore()
        lex, family = load_lexicon(st)
        cond = {c["id"]: c for c in st.all_latest("COND")}
        evd = st.all_latest("EVD")
        with open(SVAR_REGISTRY, newline="", encoding="utf-8") as fh:
            registry = list(csv.DictReader(fh))
        return cls(lex=lex, family=family, retriever=EvidenceRetriever(evd, cond, family), sup=SupportIndex(evd),
                   req=load_requirements(st), ts=TroubleshootIndex.from_registry(ROOT), registry=registry,
                   index=RD.EvidenceIndex.from_rows(evd), rung=RungA(), schema=D.load_schema(),
                   hierarchy=PS.read_process_hierarchy())

    def _transform(self, q: str, recipe_text: str | None = None) -> dict:
        from culinarystate.decision.pipeline import answer
        from culinarystate.generation.verbalize import verbalize
        from culinarystate.mechanism import router_demo as RD
        r = answer(q, self.lex, self.retriever, self.req, self.family, support_index=self.sup, troubleshoot=self.ts)
        d, s = r["decision"], r["slots"]
        text = verbalize(q, d, r["packets"])
        recipe = None
        if recipe_text and recipe_text.strip():
            svar = svar_for(s.target, self.registry)
            recipe = recipe_summary(RD.route_text(recipe_text, index=self.index, target_svar=svar, rung=self.rung,
                                                  hierarchy=self.hierarchy, schema=self.schema)) if svar else \
                {"target_svar": None, "reason": "NO_TARGET_STATE_VARIABLE", "routes": {}, "steps": []}
        return {"mode": d["mode"], "answer": text, "cited": cited_ids(text), "reason": d.get("reason"),
                "precision": d.get("precision"), "intent": d.get("intent"),
                "slots": {"ingredient": s.ingredient_id, "ingredient_name": s.ingredient_name,
                          "processes": [n for n, _ in s.processes], "target": s.target},
                "options": {k: p.evidence_class for k, p in r["packets"].items()}, "recipe": recipe}

    def respond(self, query: str, recipe_text: str | None = None) -> dict:
        return FD.respond(query, handlers={"TRANSFORMATION": self._transform}, recipe_text=recipe_text)
