"""Pipeline status stages and heat-step summaries for the S182 live console. Pure functions, no engine calls."""
from __future__ import annotations

from typing import Any, Mapping

STAGES = (("parse", "Read recipe"), ("state", "Build state"), ("simulate", "Physics simulation"),
          ("evidence", "Evidence lookup"), ("similar", "Similar recipes"), ("model", "Ask model"),
          ("verify", "Verify"))
HEAT_FIELDS = ("medium", "duration_min", "temperature_C", "lid_state", "food_T_typical_C", "thermal_dose_typical_min")


def _v(cell: Any) -> Any:
    return cell.get("v") if isinstance(cell, Mapping) else None


def heat_steps(states: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """One row per heat step (first food at that step), with the conditions the engine filled."""
    out, seen = [], set()
    for s in states:
        g, q = s.get("G") or {}, s.get("Q") or {}
        if _v(g.get("is_heat_step")) is not True or s.get("step") in seen:
            continue
        seen.add(s.get("step"))
        out.append({"step": s.get("step"), "action": s.get("action"), "food": s.get("food"),
                    "process": str(_v(g.get("process")) or ""), "family": _v(g.get("family")),
                    **{k: _v(q.get(k)) for k in HEAT_FIELDS}})
    return out


def process_names(states: list[Mapping[str, Any]]) -> list[str]:
    """'PROC-000019 boil' -> 'boil', in order, unique."""
    names = [h["process"].split(" ", 1)[-1] for h in heat_steps(states)]
    return list(dict.fromkeys(n for n in names if n))


def stage(sid: str, status: str, detail: str, ms: int | None = None) -> dict[str, Any]:
    label = dict(STAGES)[sid]
    return {"id": sid, "label": label, "status": status, "detail": detail, "ms": ms}


def _fmt(x: Any) -> str:
    return f"{x:g}" if isinstance(x, float) else str(x)


def simulate_detail(heats: list[Mapping[str, Any]]) -> str:
    parts = []
    for h in heats[:3]:
        bits = []
        if h.get("food_T_typical_C") is not None:
            bits.append(f"food {_fmt(h['food_T_typical_C'])} °C simulated")
        if h.get("thermal_dose_typical_min") is not None:
            bits.append(f"thermal dose {_fmt(h['thermal_dose_typical_min'])} min simulated")
        if h.get("duration_min") is not None:
            bits.append(f"{h['duration_min']} min stated")
        if h.get("lid_state"):
            bits.append(f"lid {h['lid_state']}")
        parts.append(f"{h['action']} (step {h['step']}, {h['food']}): " + (", ".join(bits) or "scenario unknown"))
    return "; ".join(parts)


def pre_model_stages(*, states: list, foods: list[str], mode: str, packet: Mapping | None, cards: list,
                     context: Mapping | None, similar: Mapping | None, ms: Mapping[str, int]) -> list[dict[str, Any]]:
    n_steps = len({s.get("step") for s in states})
    heats = heat_steps(states)
    out = [stage("parse", "done" if states else "error",
                 f"{n_steps} steps recognised" if states else "no cooking step recognised", ms.get("build")),
           stage("state", "done" if states else "skipped",
                 f"{len(states)} food states · foods: {', '.join(foods)}" if states else "no state", None)]
    out.append(stage("simulate", "done", simulate_detail(heats)) if heats else
               stage("simulate", "skipped", "no heat step, so the physics simulation does not apply"))
    if mode == "SAFETY":
        out.append(stage("evidence", "skipped", "food-safety question: refused, nothing looked up"))
    elif packet is not None:
        out.append(stage("evidence", "done", f"route {packet['route']} · {len(packet.get('evidence_ids') or [])} applied, "
                                             f"{len(packet.get('near_evidence_ids') or [])} near · claim packet built"))
    elif context is not None:
        found = sum(len(t.get("evidence_found") or []) for t in (context.get("evidence_match_current_step") or {}).values())
        out.append(stage("evidence", "done", f"{found} evidence rows found for the current step (axis match checked)"))
    else:
        out.append(stage("evidence", "skipped", "nothing to look up for this question"))
    out.append(_similar_stage(similar, ms.get("similar")))
    out.append(stage("model", "pending" if mode != "SAFETY" else "skipped",
                     "waiting" if mode != "SAFETY" else "refused before the model"))
    out.append(stage("verify", "pending" if mode != "SAFETY" else "skipped", "waiting" if mode != "SAFETY" else "—"))
    return out


def _similar_stage(similar: Mapping | None, ms: int | None) -> dict[str, Any]:
    if not similar:
        return stage("similar", "skipped", "similar-recipe index not loaded", ms)
    s = similar["search"]
    total = sum(s["counts"].values())
    ref = similar.get("reference")
    detail = f"{total} similar of {s['searched']:,} recipes"
    if ref:
        detail += f" · reference: “{ref['title']}” (Wikibooks{', same process' if ref.get('same_process') else ''})"
    return stage("similar", "done", detail, ms)


def finish_stages(stages: list[dict[str, Any]], *, model: Mapping | None, verify: tuple[str, str] | None) -> list[dict]:
    """New list with the model and verify stages resolved."""
    out = []
    for s in stages:
        if s["id"] == "model" and model is not None:
            ok = model.get("status") == "OK"
            s = {**s, "status": "done" if ok else "error", "ms": model.get("ms"),
                 "detail": "answered" if ok else str(model.get("reason"))}
        elif s["id"] == "verify" and verify is not None:
            s = {**s, "status": verify[0], "detail": verify[1]}
        out.append(s)
    return out
