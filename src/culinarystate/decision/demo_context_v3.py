"""Separate strict-v3 demo adapter; legacy benchmark behavior remains unchanged.

Question linking supplies identities. Optional explicit context supplies only
conditions/state/basis and cannot replace those identities. Missing context refuses
numeric application rather than upgrading a retrieval MATCH or calling old fallback.
"""
from __future__ import annotations

import re
from collections.abc import Mapping

from culinarystate.decision import demo_context as legacy
from culinarystate.decision import front_door
from culinarystate.generation.strict_v3 import VERSION, render
from culinarystate.decision.strict_display_v3 import recipe_display


def unique_target(target, registry):
    if not isinstance(target, str) or not target.strip():
        return None
    expression = r"(?<![a-z])" + re.escape(target.strip().lower()) + r"(?![a-z])"
    ids = {r["state_variable_id"] for r in registry
           if re.search(expression, str(r.get("name", "")).lower())}
    return next(iter(ids)) if len(ids) == 1 else None


class StrictDemoContext(legacy.DemoContext):
    def mode_info(self):
        return {**super().mode_info(), "emission_policy": VERSION}

    def _transform(self, q, recipe_text=None, *, source_contexts=None):
        from culinarystate.decision.pipeline import answer
        result = answer(q, self.lex, self.retriever, self.req, self.family,
                        support_index=self.sup, troubleshoot=self.ts)
        decision, slots, packets = result["decision"], result["slots"], result["packets"]
        target_id = unique_target(slots.target, self.registry)
        source_contexts = source_contexts if isinstance(source_contexts, Mapping) else {}
        contexts = {}
        linked_processes = dict(slots.processes)
        for key, packet in packets.items():
            supplied = source_contexts.get(key)
            contexts[key] = dict(supplied) if isinstance(supplied, Mapping) else {}
            linked_process = linked_processes.get(key)
            packet_process = getattr(getattr(packet, "query", None), "process_id", None)
            contexts[key].update(ingredient_id=slots.ingredient_id,
                                 process_id=linked_process if linked_process == packet_process else None,
                                 target_id=target_id)
        presence = None
        gates = getattr(self, "gates", None)
        if legacy.target_absent(gates, target_id, slots.ingredient_id):
            decision = {**decision, "mode": "ABSTAIN"}
            presence = {"state": "ABSENT", "svar": target_id}
        guarded = render(decision, packets, contexts, getattr(self.retriever, "cond", {}))
        numbers = guarded["numbers"]
        cited = list(dict.fromkeys(n["evd_id"] for n in numbers))
        evidence = None
        if numbers:
            evidence = {"code": "TABLE_REPORTED_UNVERIFIED", "badge": "Unverified source table",
                        "from_data": False, "detail": "Source reports only; applicability is not certified.",
                        "evd_ids_asked_food": cited, "evd_ids_other": []}
        recipe = None
        if isinstance(recipe_text, str) and recipe_text.strip():
            from culinarystate.decision.physics_summary_v2 import physics_summary_v2
            from culinarystate.mechanism import router_demo
            recipe = legacy.recipe_summary(router_demo.route_text(
                recipe_text, index=self.index, target_svar=target_id, rung=self.rung,
                hierarchy=self.hierarchy, schema=self.schema, gates=gates)) if target_id else {
                    "target_svar": None, "reason": "NO_UNIQUE_TARGET", "routes": {}, "steps": []}
            recipe["physics"] = physics_summary_v2(recipe_text, self.binder, self.layer)
        return {"mode": guarded["mode"], "answer": guarded["text"], "cited": cited,
                "reason": guarded["reason"], "precision": "TABLE_REPORT_ONLY" if numbers else None,
                "intent": decision.get("intent"), "slots": {"ingredient": slots.ingredient_id,
                "ingredient_name": slots.ingredient_name, "processes": [n for n, _ in slots.processes],
                "target": slots.target}, "options": {k: p.evidence_class for k, p in packets.items()},
                "evidence": evidence, "target_presence": presence, "recipe": recipe,
                "numeric_provenance": numbers, "recipe_display": recipe_display(recipe) if recipe is not None else None,
                "emission_guard": {k: v for k, v in guarded.items() if k not in ("text", "numbers")}}

    def _relationship(self, q):
        old = super()._relationship(q)
        candidates = [{"id": r["id"], "name": r["name"], "basis": "CORPUS_PATTERN_DESCRIPTOR"}
                      for r in old.get("candidates", [])]
        if not candidates:
            return {**old, "pattern_basis": "CORPUS_PATTERN_UNVERIFIED"}
        names = ", ".join(r["name"] for r in candidates)
        return {"mode": "ANSWER_CORPUS_PATTERN", "answer": "The recipe corpus contains substitution patterns "
                f"involving {names}. Their equivalence and suitability for your recipe are unknown.",
                "cited": [], "candidates": candidates, "pattern_basis": "CORPUS_PATTERN_UNVERIFIED"}

    def respond_with_context(self, query, *, source_contexts=None, recipe_text=None):
        def transform(q, recipe_text=None):
            return self._transform(q, recipe_text, source_contexts=source_contexts)
        out = front_door.respond(query, handlers={"TRANSFORMATION": transform, "RELATIONSHIP": self._relationship},
                                 recipe_text=recipe_text)
        return {**out, "demo_mode": self.mode_info(), "emission_policy": VERSION}

    def respond(self, query, recipe_text=None):
        return self.respond_with_context(query, recipe_text=recipe_text)
