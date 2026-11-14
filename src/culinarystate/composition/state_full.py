"""State v2: per (food, step) explicit state S_t = (G, C, Q, Y, P) assembled from EXISTING producers only.

G  lineage/structure: process, family, merge/split, lot members, ordered process history, cell integrity (from cut
   history), heat-step count
C  composition: C_t v1.2.1 context axes + co-member and own USDA SR composition, prior salt/acid exposure (earlier steps)
Q  physics: physics v06 L1 (medium, temperature, duration, lid, start mode, piece size, matrix class; each with basis)
   + L2 scenario (food T typical, moisture cap, thermal dose) + history sums (cumulative dose, hot-aqueous minutes,
   hot-fat minutes) + oxygen-exposure proxy from lid state
Y  chemistry: composition-aware route for vitamin C / lycopene with evidence or near evidence; vitamin C Model A
   formula retention (FORMULA_RESEARCH_ONLY, NOT_VALIDATED) where its gate passes
P  provenance: every cell carries its basis or an UNKNOWN reason; cumulative sums say when they are partial
Nothing here estimates a value that no producer gives. Labels: DERIVED_VIEW, SCENARIO where L2, RESEARCH_ONLY formula.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

from culinarystate.composition.state import U, V

ROOT = Path(__file__).resolve().parents[3]
TARGETS = {"vitc": "SVAR-000009", "lycopene": "SVAR-000025"}
CRUSH_WORDS = ("mash", "puree", "purée", "blend", "crush", "grate", "mince", "pound", "pulp", "liquidi")
AQ, LIP = {"AQUEOUS", "AQUEOUS+LIPID"}, {"LIPID", "AQUEOUS+LIPID"}


def _tool(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class StateBuilder:
    """Loads every producer once; `build(text)` returns the per-(food, step) states in step order."""

    def __init__(self) -> None:
        import json
        from culinarystate.composition import context_v12 as CV, state as CS
        from culinarystate.extraction.rung_a import RungA
        from culinarystate.ledgers.store import LedgerStore
        from culinarystate.mechanism import evidence_gates as EG, process_signatures as PS, router_demo as RD
        from culinarystate.quantity.rc2_dryrun import load_schema
        from culinarystate.simulation.condition_binding import Binder
        from culinarystate.simulation.scenario_layer import ScenarioLayer, volume_avg_dose
        self.rung, self.schema = RungA(coord_food_guard=True), load_schema()
        self.binder = Binder.load()
        self.binder.rung = self.rung                      # same parse -> same event ids as the state graph
        self.l2, self.dose = ScenarioLayer.load(), volume_avg_dose
        self.fill = _tool("s179_state_dataset_fill")
        self.fit = json.loads((ROOT / self.fill.FC.FIT).read_text())["fit"]
        self.marks, self.roles = CS.load_markers_v2(ROOT / "registry/composition_markers_v2.csv")
        self.sr = CV.load_sr_composition(ROOT / "registry/ing_sr_composition_v1.csv")
        rows = LedgerStore().all_latest("EVD")
        self.evd = {r["id"]: r for r in rows}
        self.env = dict(index=RD.EvidenceIndex.from_rows(rows), gates=EG.EvidenceGates.load(),
                        hierarchy=PS.read_process_hierarchy())
        self.names, self.proc = {}, {}
        for line in (ROOT / "ledgers/data/ING.jsonl").read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                self.names[r["id"]] = r["canonical_name"]
        for line in (ROOT / "ledgers/data/PROC.jsonl").read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                self.proc[r["id"]] = (r.get("family"), r.get("canonical_name") or r["id"])
        self.CS, self.CV, self.RD = CS, CV, RD

    # ------------------------------------------------------------------ helpers
    def _routes(self, text: str) -> dict[str, list]:
        return {t: self.RD.route_text(text, target_svar=s, rung=self.rung, schema=self.schema, **self.env)["items"]
                for t, s in TARGETS.items()}

    def _q(self, r1: dict | None) -> dict[str, Any]:
        q = {k: self.fill.l1_cell(r1, ax) for k, ax in self.fill.L1_AXES.items()}
        q["start_mode"] = self.fill.l1_cell(r1, "start_mode")
        r2 = self.l2.run(r1) if r1 and r1.get("heat") and (r1.get("inputs") or {}).get("medium") else None
        q.update(self.fill.l2_cells(r1, r2, self.fit))
        sc = ((r2 or {}).get("scenarios") or {}).get("TYPICAL") or {}
        d = self.dose(sc) if sc else None
        q["thermal_dose_typical_min"] = V(round(float(d), 3), "SCENARIO_DEFAULT") if d is not None else \
            U("NOT_A_HEAT_EVENT" if r2 is None else "DOSE_NOT_COMPUTED")
        lid = str(q["lid_state"].get("v") or "").upper()
        q["oxygen_exposure_proxy"] = (V("LIMITED_LID", "LID_STATE_PROXY") if ("COVER" in lid and "UN" not in lid) or lid in
                                      ("LID_ON", "ON", "CLOSED") else V("OPEN", "LID_STATE_PROXY") if lid else
                                      U("NO_LID_CUE"))
        return q

    @staticmethod
    def _num(cell) -> float | None:
        v = cell.get("v")
        try:
            return None if v is None else float(v)
        except (TypeError, ValueError):
            return None

    # ------------------------------------------------------------------ main
    def build(self, text: str) -> list[dict[str, Any]]:
        from culinarystate.composition import router_v12 as RV
        from culinarystate.extraction.interfaces import SourceText
        parsed = self.rung.run(SourceText.from_raw("S2", text), self.rung.config(), schema=self.schema)
        mem = self.CS.lot_members_v11(parsed.graph.entities)
        l1 = {r["event_id"]: r for r in self.binder.bind_text(text)["events"]}
        routed = self._routes(text)
        events = list(parsed.graph.events)
        hist: dict[str, dict] = {}                      # per food: running history
        out = []
        for k, e in enumerate(events):
            pid = next((a.value for a in e.attributes if a.field == "proc_id"), None)
            fam, pname = self.proc.get(pid, (None, pid))
            ings = set()
            for c in e.consumes:
                ings |= mem.get(c, (frozenset(), False))[0]
            foods = sorted(i for i in ings if not (self.marks.get(i) and self.roles.get(i) == "MEDIUM"))
            r1 = l1.get(e.event_id)
            is_heat = bool((r1 or {}).get("heat"))           # physics v06 heat flag (family COMBINATION mixes add/braise)
            q = self._q(r1)
            formula = q.pop("aa_retention_typical", U("NOT_A_HEAT_EVENT"))
            kind = ("MERGE" if len(e.consumes) > 1 and len(e.produces) == 1 else
                    "SPLIT" if len(e.consumes) == 1 and len(e.produces) > 1 else "TRANSFORM")
            for food in foods:
                h = hist.setdefault(food, {"procs": [], "dose": 0.0, "dose_partial": False, "aq_min": 0.0, "fat_min": 0.0,
                                           "time_partial": False, "heat_steps": 0, "salt_before": False,
                                           "acid_before": False, "integrity": "NO_CUT_RECORDED"})
                ctx = self.CV.context_v12(food, list(e.consumes), mem, self.marks, self.roles, self.sr,
                                          medium_type=q["medium"].get("v"))
                phase = ctx["contact_phase"].get("v")
                if fam == "MECHANICAL_CUT":
                    h["integrity"] = "CRUSHED_PUREED" if any(w in str(pname).lower() for w in CRUSH_WORDS) else \
                        ("CUT" if h["integrity"] != "CRUSHED_PUREED" else h["integrity"])
                if is_heat:
                    h["heat_steps"] += 1
                    dose, dur = self._num(q["thermal_dose_typical_min"]), self._num(q["duration_min"])
                    h["dose"] += dose or 0.0
                    h["dose_partial"] |= dose is None
                    if phase in AQ or phase in LIP:
                        if dur is None:
                            h["time_partial"] = True
                        else:
                            h["aq_min"] += dur if phase in AQ else 0.0
                            h["fat_min"] += dur if phase in LIP else 0.0
                y = {}
                for t in TARGETS:
                    it = next((i for i in routed[t] if i["event_id"] == e.event_id and i["ingredient_id"] == food), None)
                    if it is None:
                        y[f"{t}_route"] = U("NO_ROUTER_ITEM")
                        continue
                    r = RV.composition_route(it, ctx, self.evd)
                    ev = r.get("evidence") or []
                    near = r.get("near_evidence") or it.get("evidence_not_applied") or []
                    y[f"{t}_route"] = V(r["route"], "; ".join(r.get("composition_reasons") or []) or "ROUTER_0.4.1")
                    y[f"{t}_evidence"] = V([f"{x['evd_id']}={x.get('value')}{x.get('unit') or ''}" for x in ev], "APPLIED") \
                        if ev else (V([x["evd_id"] for x in near], "FOUND_NOT_APPLIED") if near else U("NO_EVIDENCE_ROW"))
                y["vitc_formula_retention_typical"] = formula
                s = {"step": k + 1, "event_id": e.event_id, "action": " ".join(e.span.texts), "food_id": food,
                     "food": self.names.get(food, food),
                     "G": {"process": V(f"{pid} {pname}", "RUNG_A"), "family": V(fam, "PROC_LEDGER") if fam else U("NO_PROC"),
                           "event_kind": V(kind, "RUNG_A"), "lot_members": V(sorted(self.names.get(i, i) for i in ings), "RUNG_A_LOT"),
                           "history": V(list(h["procs"]), "LINEAGE"), "cell_integrity": V(h["integrity"], "CUT_HISTORY"),
                           "heat_steps_so_far": V(h["heat_steps"], "LINEAGE+PHYSICS_V06_HEAT_FLAG"),
                           "is_heat_step": V(is_heat, "PHYSICS_V06_L1")},
                     "C": {**{k2: ctx[k2] for k2 in ("salt_present", "acid_present", "lipid_present", "aqueous_present",
                                                        "contact_phase", "member_composition", "nacl_equiv_fraction_as_added",
                                                        "fat_fraction_as_added", "lot_acidity_band")},
                           "own_composition": V({k2: v[0] for k2, v in self.sr.get(food, {}).items()}, "USDA_SR_LEGACY_2018_04")
                           if self.sr.get(food) else U("NO_SR_MATCH"),
                           "salt_exposure_before": V(h["salt_before"], "LINEAGE_C_T"),
                           "acid_exposure_before": V(h["acid_before"], "LINEAGE_C_T")},
                     "Q": {**q,
                           "cumulative_thermal_dose_min": (U("NOT_HEATED_YET") if not h["heat_steps"] else
                                                           U("DOSE_NOT_COMPUTED") if h["dose_partial"] and not h["dose"] else
                                                           V(round(h["dose"], 3), "SUM_SCENARIO" + ("_PARTIAL" if h["dose_partial"] else ""))),
                           "hot_aqueous_minutes": V(h["aq_min"], "SUM_TEXT_STATED" + ("_PARTIAL" if h["time_partial"] else "")),
                           "hot_fat_minutes": V(h["fat_min"], "SUM_TEXT_STATED" + ("_PARTIAL" if h["time_partial"] else ""))},
                     "Y": y}
                out.append(s)
                h["procs"].append(pname)
                h["salt_before"] |= ctx["salt_present"].get("v") is True
                h["acid_before"] |= ctx["acid_present"].get("v") is True
        return out
