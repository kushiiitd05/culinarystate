"""Router demo mode on real recipe text (S170, D-075 M1). NON_CITABLE, DEMO_ONLY.

Runs the UNCHANGED Step 23a engine (``applicability.evaluate``, mode "23a") on queries built from real recipe events:
Rung A gives each event its process id and the ingredient ids of the lots it consumes; the G0 evidence pre-check is
an exact (ingredient_id, process_id, target svar) lookup in the ACTIVE EVD rows. No condition value is consumed
(no axes, no states), so the engine's "no COND consumed" contract and R-05 hold; ``23b`` stays BLOCKED until 07.A
validly passes and 15b is frozen. With no reviewed MECH entry, signature, FORM or PARAM row, an event routes DIRECT
when measured evidence exists and UNKNOWN otherwise, with the engine's reasons (what is missing). The envelope is
labelled NON_CITABLE / DEMO_ONLY: nothing here can feed a claim. EVD rows are tier E3 and UNVERIFIED.

S176 (L-ROUTER): an optional ``gates`` argument (``evidence_gates.EvidenceGates``) screens each item BEFORE G0: a
target-presence screen (``TARGET_ABSENT`` -> route NOT_APPLICABLE; ``TARGET_PRESENCE_UNKNOWN`` keeps routing) and a
lot-context gate (``MERGED_LOT_CONTEXT``: DIRECT is withheld when the process acts on a merged lot). The gates only
narrow routes; without ``gates`` the behaviour is exactly the S170 / S171 one.

S177 (SCIFIX-ROUTER, FINAL-SCI #6 / #7): ABSENT needs a HIGH rank-1 identity, every plausible candidate (any band) known
below the floor and a confirmed ING category; DIRECT is also withheld (``PRIOR_PROCESS_CONTEXT``) when the single-member
lot was already produced by a heat or leach (SEPARATION / SOAK) event, read from the replay graph's ``produces``.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from culinarystate.extraction.interfaces import SourceText
from culinarystate.extraction.rung_a import RungA
from culinarystate.mechanism import applicability as AP
from culinarystate.mechanism import evidence_gates as EG
from culinarystate.mechanism import process_signatures as PS
from culinarystate.quantity import rc2_dryrun as D

ROOT = Path(__file__).resolve().parents[3]
EVD_PATH = ROOT / "ledgers" / "data" / "EVD.jsonl"
LABELS = ("NON_CITABLE", "DEMO_ONLY", "EVIDENCE_E3_UNVERIFIED", "NO_REVIEWED_MECHANISM", "NO_CONDITIONS_CONSUMED")
EVIDENCE_STATUSES = ("MEASURED", "CENSORED")
DEMO_VERSION = "router-demo-0.3.0-draft"


class DemoRefused(RuntimeError):
    """A demo output was offered for citation."""


def _summary(r: Mapping[str, Any]) -> dict:
    rf = (r.get("derived") or {}).get("retention_factor") or {}
    return {"evd_id": r["id"], "svar_id": r["target"]["state_variable_id"], "target": r["target"].get("raw_name"),
            "status": rf.get("status"), "value": rf.get("value"), "raw": rf.get("raw"), "unit": rf.get("unit"),
            "source_id": r.get("source_id"), "tier": r.get("tier"),
            "verification": (r.get("verification") or {}).get("status")}


class EvidenceIndex:
    """ACTIVE EVD rows (latest version per id) keyed by (ingredient_id, process_id)."""

    def __init__(self, by_key: Mapping[tuple[str, str], tuple[dict, ...]]) -> None:
        self._by_key = dict(by_key)

    @classmethod
    def from_rows(cls, rows: Iterable[Mapping[str, Any]]) -> "EvidenceIndex":
        latest: dict[str, Mapping[str, Any]] = {}
        for r in rows:
            if r["id"] not in latest or r["version"] > latest[r["id"]]["version"]:
                latest[r["id"]] = r
        by_key: dict[tuple[str, str], list[dict]] = {}
        for r in latest.values():
            ing, proc = (r.get("matrix") or {}).get("ingredient_id"), (r.get("process") or {}).get("process_id")
            if r.get("status") == "ACTIVE" and ing and proc:
                by_key.setdefault((ing, proc), []).append(_summary(r))
        return cls({k: tuple(sorted(v, key=lambda s: s["evd_id"])) for k, v in by_key.items()})

    @classmethod
    def from_ledger(cls, path: Path = EVD_PATH) -> "EvidenceIndex":
        with Path(path).open(encoding="utf-8") as fh:
            return cls.from_rows(json.loads(line) for line in fh if line.strip())

    def lookup(self, ingredient_id: str | None, process_id: str | None, svar_id: str) -> list[dict]:
        if not ingredient_id or not process_id:
            return []
        return [s for s in self._by_key.get((ingredient_id, process_id), ()) if s["svar_id"] == svar_id]

    def pairs(self, svar_id: str) -> set[tuple[str, str]]:
        """(ingredient_id, process_id) keys holding a MEASURED or CENSORED row for ``svar_id``."""
        return {k for k, rows in self._by_key.items()
                if any(s["svar_id"] == svar_id and s["status"] in EVIDENCE_STATUSES for s in rows)}

    def ingredients(self, svar_id: str) -> set[str]:
        return {ing for ing, _ in self.pairs(svar_id)}


def precheck(hits: Iterable[Mapping[str, Any]]) -> str:
    """G0: DIRECT when a measured or censored row matches exactly; no bracketing in the demo (conservative)."""
    return "DIRECT" if any(h.get("status") in EVIDENCE_STATUSES for h in hits) else "NONE"


def _attr(claims, name: str):
    return next((c.value for c in claims if c.field == name), None)


def _lot_ingredients(graph, entity_ids: Iterable[str]) -> list[str]:
    ents = {e.entity_id: e for e in graph.entities}
    out, stack, seen = [], list(entity_ids), set()
    while stack:
        eid = stack.pop()
        if eid in seen or eid not in ents:
            continue
        seen.add(eid)
        e = ents[eid]
        ing = _attr(e.attributes, "ingredient_id")
        if ing:
            out.append(ing)
        stack.extend(e.parent_entity_ids)
    return sorted(set(out))


def route_text(raw: str, *, index: EvidenceIndex, target_svar: str, locale: str | None = None,
               rung: RungA | None = None, hierarchy: PS.ProcessHierarchy | None = None,
               schema: Mapping[str, Any] | None = None, gates: EG.EvidenceGates | None = None) -> dict:
    """Per (event, linked ingredient): the 23a route for ``target_svar``, its reasons and the matching EVD rows.

    ``gates`` (optional, S176): target-presence screen + lot-context gate before G0; see module docstring. Each item
    then also carries ``route_ungated`` (what S171 would have said), ``gates`` (presence / lot_context codes) and
    ``evidence_not_applied`` (EVD rows found but not allowed to stand)."""
    if not isinstance(target_svar, str) or not target_svar.strip():
        raise ValueError("target_svar is required (e.g. SVAR-000009, vitamin C)")
    rung, hierarchy = rung or RungA(), hierarchy or PS.read_process_hierarchy()
    source = SourceText.from_raw("DEMO", raw)
    graph = rung.run(source, rung.config(locale=locale), schema=schema or D.load_schema()).graph
    members = EG.lot_members(graph, hierarchy) if gates is not None else {}
    items = []
    for ev in graph.events:
        proc = _attr(ev.attributes, "proc_id")
        consumed = (*ev.consumes, *ev.discards)
        for ing in _lot_ingredients(graph, consumed) or [None]:
            hits = index.lookup(ing, proc, target_svar)
            raw_pre = precheck(hits)
            gate = (gates.evaluate(svar_id=target_svar, ing=ing, raw_precheck=raw_pre,
                                   lots=EG.lots_of(members, consumed, ing)) if gates is not None else None)
            q = AP.ApplicabilityQuery(case_id=f"DEMO-{ev.event_id}-{ing or 'UNLINKED'}",
                                      entity_version_id=ing or f"UNLINKED-{ev.event_id}", event_id=ev.event_id,
                                      target_svar_id=target_svar, target_state_key=None, process_id=proc,
                                      event_resolved=proc is not None,
                                      evidence_precheck=gate.final_precheck if gate else raw_pre)
            rec = AP.evaluate(q, (), (), hierarchy)
            reasons = sorted({r for g in rec["gates"].values() for r in g["reasons"]}
                             | ({"NO_LINKED_INGREDIENT"} if ing is None else set()))
            item = {"event_id": ev.event_id, "action": ev.span.surface, "offset": ev.span.char_start,
                    "process_id": proc, "ingredient_id": ing, "route": rec["route"], "reasons": reasons,
                    "evidence": hits, "appdec_id": rec["appdec_id"]}
            if gate is not None:
                item["route_ungated"] = "DIRECT" if raw_pre == "DIRECT" else (
                    "INTERPOLATE" if raw_pre == "BRACKETING" else rec["route"])
                item["gates"] = gate.as_item()
                item["prior_process"] = list(gate.prior_kinds)
                item["member_presence"] = gates.member_presence(target_svar, ing)
                item["member_blocker"] = gates.member_blocker(target_svar, ing)
                item["reasons"] = [*gate.reasons, *reasons]
                if gate.not_applicable:
                    item["route"] = EG.NOT_APPLICABLE
                if gate.not_applicable or gate.withheld:
                    item["evidence"], item["evidence_not_applied"] = [], hits
                else:
                    item["evidence_not_applied"] = []
            items.append(item)
    return {"record": "ROUTER_DEMO", "version": DEMO_VERSION, "labels": list(LABELS), "citable": False,
            "engine_mode": AP.MODE_23A, "engine_version": AP.ENGINE_VERSION, "conditions_consumed": False,
            "target_svar": target_svar, "gates": gates.describe() if gates is not None else {"enabled": False},
            "items": items}


def assert_citable(output: Mapping[str, Any]) -> None:
    if output.get("citable") is not True or "NON_CITABLE" in (output.get("labels") or []):
        raise DemoRefused("router demo output is NON_CITABLE and can never be cited")
