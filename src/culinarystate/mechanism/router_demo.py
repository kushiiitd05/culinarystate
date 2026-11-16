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

S178 (aa-fit-sim, T5-C11-R4): an optional ``simulate`` argument (``simulate_branch.SimulateBranch``, duck-typed here so
nothing is imported) runs the AA SIMULATE branch per item AFTER the gates. Without it nothing changes (byte-identical).
With it every item gets a ``simulate`` block (status, reason codes, guard reasons) and the route becomes SIMULATE only
when the branch completed a run through guard, domain gate, the unchanged 23a engine and ``sim_core``; otherwise the
route is left exactly as it was (never downgraded, never invented). The branch refuses on real data today.

S178 (FIX-ROUTER, SCI-B R2 / R3 / R5 / R6; all narrowing, only with ``gates``): each item also carries ``event_role``
(``PROCESS_STEP`` / ``ATTRIBUTIVE_STATE`` / ``SERVING_SUGGESTION``: an attributive participle or a serving suggestion is
not a performed process and never gets DIRECT; the SIMULATE branch is not run for it), ``prior_basis`` (where a prior
kind came from), ``prior_presupposed`` and ``member_sr_basis`` (SR derivation code and data points of the member's
plausible identities, R4). ``ingredient_lines`` (optional): the recipe's ingredient lines, read only for processed-state
cues ("1 can ...", "2 boiled ...", "leftover ..."); a food whose line states a processed form carries that prior state
(basis ``INGREDIENT_LINE``). The lines are not routed as events: they describe foods, not process steps.
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
DEMO_VERSION = "router-demo-0.4.0-draft"


class DemoRefused(RuntimeError):
    """A demo output was offered for citation."""


def _summary(r: Mapping[str, Any]) -> dict:
    rf = (r.get("derived") or {}).get("retention_factor") or {}
    proc = r.get("process") or {}
    return {"evd_id": r["id"], "svar_id": r["target"]["state_variable_id"], "target": r["target"].get("raw_name"),
            "status": rf.get("status"), "value": rf.get("value"), "raw": rf.get("raw"), "unit": rf.get("unit"),
            "source_id": r.get("source_id"), "tier": r.get("tier"),
            "verification": (r.get("verification") or {}).get("status"),
            "presupposes_prior_heat": EG.presupposes_prior_heat(proc.get("process_id"), proc.get("raw_name"))}


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


def ingredient_line_states(lines: Iterable[str] | None, rung: RungA, locale: str | None = None,
                           counts: dict | None = None) -> dict[str, frozenset]:
    """ING id -> prior kinds stated in the recipe's ingredient lines (S178 R2; Layer 1 TEXT_STATED). Only a line with a
    registered state cue (``evidence_gates.state_cues``) is read with Rung A's mention tagger and linker; each uniquely
    linked food of the line gets the kinds of the cues outside its own surface. ``counts`` (optional) gains integer
    counters only."""
    out: dict[str, set] = {}
    c = counts if counts is not None else {}
    cfg = None
    for k, line in enumerate(lines or ()):
        if not isinstance(line, str) or not line.strip():
            continue
        c["ingredient_lines_seen"] = c.get("ingredient_lines_seen", 0) + 1
        cues = EG.state_cues(line)
        if not cues:
            continue
        c["ingredient_lines_with_state_cue"] = c.get("ingredient_lines_with_state_cue", 0) + 1
        cfg = cfg or rung.config(locale=locale)
        src = SourceText.from_raw(f"LINE{k}", line)
        ms = rung.extract_mentions(src, cfg)
        for m in ms.mentions:
            if m.label != "FOOD_MENTION":
                continue
            lr = rung.link(src, m, cfg)
            if not lr.selected_id:
                continue
            kinds = {kk for s, e, kk in cues if not (m.span.char_start <= s and e <= m.span.char_end)}
            if kinds:
                out.setdefault(lr.selected_id, set()).update(kinds)
    c["ingredient_line_ing_states"] = c.get("ingredient_line_ing_states", 0) + len(out)
    return {i: frozenset(v) for i, v in out.items()}


def _not_a_step_simulate(role: str) -> dict:
    """The SIMULATE block of an item whose event is not a performed process (S178 R3): never evaluated."""
    return {"record": "AA_SIMULATE_BRANCH", "status": "NOT_EVALUATED_NOT_A_PROCESS_STEP", "simulated": False,
            "engine_route": None, "reasons": [EG.ROLE_REASON[role]], "guard_reasons": [], "domain_gate": None,
            "section141_class": "unsupported", "labels": list(LABELS)}


def route_text(raw: str, *, index: EvidenceIndex, target_svar: str, locale: str | None = None,
               rung: RungA | None = None, hierarchy: PS.ProcessHierarchy | None = None,
               schema: Mapping[str, Any] | None = None, gates: EG.EvidenceGates | None = None,
               simulate: Any = None, ingredient_lines: Iterable[str] | None = None,
               counts: dict | None = None) -> dict:
    """Per (event, linked ingredient): the 23a route for ``target_svar``, its reasons and the matching EVD rows.

    ``gates`` (optional, S176): target-presence screen + lot-context gate before G0; see module docstring. Each item
    then also carries ``route_ungated`` (what S171 would have said), ``gates`` (presence / lot_context codes) and
    ``evidence_not_applied`` (EVD rows found but not allowed to stand)."""
    if not isinstance(target_svar, str) or not target_svar.strip():
        raise ValueError("target_svar is required (e.g. SVAR-000009, vitamin C)")
    rung, hierarchy = rung or RungA(), hierarchy or PS.read_process_hierarchy()
    source = SourceText.from_raw("DEMO", raw)
    res = rung.run(source, rung.config(locale=locale), schema=schema or D.load_schema())
    graph = res.graph
    text = line_states = None
    if gates is not None:
        text = EG.text_context(raw, res.mentions.mentions, res.links)
        line_states = ingredient_line_states(ingredient_lines, rung, locale, counts)
    members = EG.lot_members(graph, hierarchy, text=text, ingredient_states=line_states) if gates is not None else {}
    sim_l1 = simulate.layer1(raw, locale) if simulate is not None else {}
    items = []
    for ev in graph.events:
        proc = _attr(ev.attributes, "proc_id")
        consumed = (*ev.consumes, *ev.discards)
        span = (ev.span.char_start, ev.span.char_end) if ev.span is not None else None
        role = text.role(span) if text is not None else EG.PROCESS_STEP
        for ing in _lot_ingredients(graph, consumed) or [None]:
            hits = index.lookup(ing, proc, target_svar)
            raw_pre = precheck(hits)
            gate = (gates.evaluate(svar_id=target_svar, ing=ing, raw_precheck=raw_pre,
                                   lots=EG.lots_of(members, consumed, ing), event_role=role,
                                   stated=text.window_states(span, ing), hits=hits) if gates is not None else None)
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
                item["prior_basis"] = list(gate.prior_basis)
                item["prior_presupposed"] = gate.presupposed
                item["event_role"] = gate.event_role
                item["member_presence"] = gates.member_presence(target_svar, ing)
                item["member_blocker"] = gates.member_blocker(target_svar, ing)
                item["member_sr_basis"] = gates.member_basis(target_svar, ing)
                if gate.event_role != EG.PROCESS_STEP and raw_pre == "DIRECT":
                    # counts only (S178 R3 share): would every other gate have let DIRECT stand for a real step?
                    alt = gates.evaluate(svar_id=target_svar, ing=ing, raw_precheck=raw_pre,
                                         lots=EG.lots_of(members, consumed, ing), stated=text.window_states(span, ing),
                                         hits=hits)
                    item["direct_if_process_step"] = alt.final_precheck == "DIRECT" and not alt.not_applicable
                item["reasons"] = [*gate.reasons, *reasons]
                if gate.not_applicable:
                    item["route"] = EG.NOT_APPLICABLE
                else:
                    item["route"] = gates.context_route(gate, item["route"])     # S179 A2 (opt-in)
                if gate.not_applicable or gate.withheld:
                    item["evidence"], item["evidence_not_applied"] = [], hits
                else:
                    item["evidence_not_applied"] = []
            if simulate is not None and gate is not None and gate.event_role != EG.PROCESS_STEP:
                item["simulate"] = _not_a_step_simulate(gate.event_role)     # S178 R3: never simulate a non-event
            elif simulate is not None:
                out = simulate.evaluate_item(item, layer1=sim_l1.get(ev.event_id), precheck=q.evidence_precheck,
                                             hierarchy=hierarchy, target_svar=target_svar)
                item["simulate"] = out.as_item()
                if out.simulated:
                    item["reasons_demo_engine"] = item["reasons"]
                    item["route"], item["reasons"] = "SIMULATE", ["SIMULATE_RESEARCH_ONLY_PILOT"]
                    item["appdec_id"] = (out.record or {}).get("appdec_id", item["appdec_id"])
            items.append(item)
    env = {"record": "ROUTER_DEMO", "version": DEMO_VERSION, "labels": list(LABELS), "citable": False,
           "engine_mode": AP.MODE_23A, "engine_version": AP.ENGINE_VERSION, "conditions_consumed": False,
           "target_svar": target_svar, "gates": gates.describe() if gates is not None else {"enabled": False},
           "items": items}
    if simulate is not None:
        env["simulate"] = {"enabled": True, "mode": simulate.guard.mode, "guard_allowed": simulate.guard.allowed,
                           "guard_reasons": list(simulate.guard.reasons), "layer1_text_inputs_used": True}
    return env


def assert_citable(output: Mapping[str, Any]) -> None:
    if output.get("citable") is not True or "NON_CITABLE" in (output.get("labels") or []):
        raise DemoRefused("router demo output is NON_CITABLE and can never be cited")
