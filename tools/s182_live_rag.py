"""S182 live RAG console engine: one question, the same hosted LLM twice, side by side.

* **System arm (RAG):** recipe -> State v2 (lineage vNext on, D-134) -> evidence compiler ->
  Claim Packet -> the LLM verbalises the packet only -> claim verifier -> template on failure.
* **Plain arm:** the same LLM gets the recipe text and the question, no packet, no contract.
  Its reply is checked against the same packet so the difference is measurable, not asserted.

Nothing here edits ``src/``. The frozen core is called exactly as the S181 snapshot calls it.

Rules carried over from the project:
* Only public or self-written text may leave the machine. The caller must assert
  ``self_written=True``; otherwise no LLM call is made and the system answers by template.
* Any BBC marker in the packet or evidence cards blocks the request before anything is sent.
* The NVIDIA key is read from ``~/.config/culinarystate/nvidia.env`` at call time and is never
  logged, returned or passed on a command line.

Labels: DIAGNOSTIC_ONLY · NO_GOLD · LIVE_LLM_OUTPUT_UNVERIFIED_EXCEPT_BY_CLAIM_VERIFIER.
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Callable, Mapping

ROOT = Path(__file__).resolve().parents[1]
NIM_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
NIM_ENV = Path.home() / ".config/culinarystate/nvidia.env"
DEFAULT_MODEL = "nvidia/nemotron-3-ultra-550b-a55b"
LLM_TIMEOUT_S = 90
LLM_MAX_TOKENS = 2000  # reasoning models spend part of this on hidden reasoning before the answer
MAX_QUESTION = 500
MAX_RECIPE = 6000
BBC_MARKERS = ("BBCGF-A1", "SRC-000002")
LABELS = ["DIAGNOSTIC_ONLY", "NO_GOLD", "LIVE_LLM_OUTPUT_UNVERIFIED_EXCEPT_BY_CLAIM_VERIFIER"]
PACKET_FIELDS = ("food", "step", "action", "target", "question_kind", "route", "allowed_claims",
                 "forbidden_claims", "required_caveats", "evidence_ids", "evidence_values",
                 "near_evidence_ids", "max_allowed_precision")
CARD_FIELDS = ("source_family_id", "source_id", "matrix", "process", "target", "tier", "design")

_TARGETS = (("vitc", re.compile(r"\bvit(?:amin)?\.?\s*c\b|\bascorb", re.I)),
            ("lycopene", re.compile(r"\blycopene\b", re.I)))
_KINDS = (("LEACHING", re.compile(r"\bleach|\binto the (?:cooking )?water\b|\bwater\b", re.I)),
          ("FLAVOUR", re.compile(r"\bflavou?r|\btaste|\baroma", re.I)),
          ("RETENTION_NUMERIC", re.compile(r"\bhow much\b|\bremain|\bretain|\bretention|\bleft\b|\blost\b"
                                           r"|\bloss\b|\bpercent|%|\bamount\b", re.I)),
          ("PROCESS_EFFECT", re.compile(r"\baffect|\beffect|\bhappen|\bchange|\bimpact|\bdestroy|\bdegrad", re.I)),
          ("COMPOSITION", re.compile(r"\bcontain|\bcomposition|\bpresent\b", re.I)))
_THINK = re.compile(r"<think>.*?</think>", re.S | re.I)
_SAFETY = re.compile(r"\bsafe\b|\bunsafe\b|\bbacteri|\bfood poisoning|\bspoil|\bgone bad\b|\bgo bad\b"
                     r"|\bundercooked\b|\bdoneness\b|\bhow long\b.*\bkeep|\bkeep\b.*\bfridge\b|\bexpire", re.I)
_NUTRIENT = re.compile(r"\bvitamin|\bnutrient|\bmineral|\biron\b|\bcalcium\b|\bprotein\b|\bfib(?:re|er)\b"
                       r"|\bfolate\b|\bpotassium\b|\bcarotenoid|\bantioxidant", re.I)
_CITE = re.compile(r"step\s+(\d+)\s*:\s*([^)\n]*)", re.I)
_PAIR = re.compile(r"\s*([A-Za-z_]+)\s*=\s*(.+?)\s*$")
_PERCENT = re.compile(r"(\d+(?:\.\d+)?)\s*(?:%|percent\b)", re.I)
TRACE_FIELDS = {
    "G": ("process", "family", "lot_members", "cell_integrity", "is_heat_step", "heat_steps_so_far"),
    "C": ("salt_present", "acid_present", "lipid_present", "aqueous_present", "contact_phase",
          "salt_exposure_before", "acid_exposure_before", "lot_acidity_band"),
    "Q": ("medium", "temperature_C", "duration_min", "lid_state", "piece_size_class", "matrix_class", "start_mode",
          "hot_aqueous_minutes", "hot_fat_minutes",
          # physics simulation (L2 TYPICAL scenario): labelled SCENARIO_DEFAULT, not measurements
          "thermal_state", "food_T_typical_C", "moisture_cap_C", "thermal_dose_typical_min",
          "cumulative_thermal_dose_min", "oxygen_exposure_proxy"),
}
SIM_FIELDS = frozenset({"thermal_state", "food_T_typical_C", "moisture_cap_C", "thermal_dose_typical_min",
                        "cumulative_thermal_dose_min", "oxygen_exposure_proxy"})
#: Reasons that mean "this field does not apply to this step", not "we could not find it".
NOT_APPLICABLE = frozenset({"NOT_A_HEAT_EVENT", "NOT_HEATED_YET"})
SAFETY_TEXT = ("I can't answer food-safety questions (safe temperatures, doneness, bacteria, or how long food "
               "keeps), so I won't guess.")

LLM = Callable[[str], str]


class RequestError(ValueError):
    """A request that fails validation. The message names the offending field."""


# ------------------------------------------------------------------ pure helpers
def _tool(name: str):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def parse_target(question: str) -> str | None:
    return next((t for t, rx in _TARGETS if rx.search(question)), None)


def parse_kind(question: str) -> str:
    return next((k for k, rx in _KINDS if rx.search(question)), "RETENTION_NUMERIC")


def pick_food(question: str, foods: list[str]) -> str | None:
    low = question.lower()
    named = [f for f in foods if re.search(rf"\b{re.escape(f.lower())}(?:e?s)?\b", low)]
    if len(named) == 1:
        return named[0]
    return foods[0] if len(foods) == 1 else None


def strip_think(text: str) -> str:
    return _THINK.sub("", text or "").strip()


def readable_reasons(packet: Mapping[str, Any]) -> list[str]:
    """The same wording the template uses, so a verbalised reason names the axis the verifier checks."""
    return [f"{k.split('_', 1)[-1].replace('_', ' ')}: {v}" for k, v in (packet.get("unknown_reasons") or {}).items()]


def verbaliser_prompt(question: str, packet: Mapping[str, Any]) -> str:
    view = {k: packet.get(k) for k in PACKET_FIELDS}
    view["unknown_reasons_readable"] = readable_reasons(packet)
    return (
        "You are the verbaliser of an evidence-bounded system. Answer the QUESTION using ONLY the "
        "CLAIM PACKET below.\n"
        "Rules:\n"
        "1. If route is DIRECT, state the evidence value exactly as written (no rounding, no extra "
        "decimals) and cite its evidence id in square brackets, e.g. [EVD-000000].\n"
        "2. If route is not DIRECT, say plainly that it is not known from the available evidence, "
        "and give the reason using the axis names in unknown_reasons_readable (e.g. matrix, process, "
        "measurement method). Give no numbers about the nutrient.\n"
        "3. Never call anything a direct measurement unless route is DIRECT.\n"
        "4. If you mention a near_evidence id, say its number cannot be transferred to this context.\n"
        "5. No other facts, mechanisms or numbers. Two or three sentences. Plain text only.\n\n"
        f"QUESTION: {question}\n\nCLAIM PACKET (JSON):\n{json.dumps(view, indent=1, ensure_ascii=False)}\n"
    )


def question_mode(question: str) -> str:
    """SAFETY (refused, as the core refuses it) · NUTRIENT (claim packet) · ADVICE (state trace)."""
    if _SAFETY.search(question):
        return "SAFETY"
    return "NUTRIENT" if parse_target(question) or _NUTRIENT.search(question) else "ADVICE"


def _cell_known(cell: Any) -> bool:
    return isinstance(cell, Mapping) and cell.get("v") is not None and cell.get("v") != "NO_RECOGNIZED_MARKER"


def state_trace(states: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Per step: the engine's known facts and its UNKNOWNs (with reason), for the fields a cook acts on."""
    out = []
    for s in states:
        known, unknown = {}, {}
        for block, fields in TRACE_FIELDS.items():
            for f in fields:
                cell = (s.get(block) or {}).get(f)
                if cell is None:
                    continue
                if _cell_known(cell):
                    known[f] = cell["v"]
                else:
                    unknown[f] = cell.get("u") or cell.get("v") or "UNKNOWN"
        out.append({"step": s.get("step"), "action": s.get("action"), "food": s.get("food"),
                    "known": known, "unknown": unknown})
    return out


def _group(block: str, field: str) -> str:
    if field in SIM_FIELDS:
        return "simulation"
    return {"G": "process", "C": "composition", "Q": "conditions"}[block]


def coverage(states: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Per step: every tracked field as FILLED (value + source), NOT_APPLICABLE, or UNKNOWN (reason)."""
    out = []
    for s in states:
        cells = []
        for block, fields in TRACE_FIELDS.items():
            for f in fields:
                cell = (s.get(block) or {}).get(f)
                if not isinstance(cell, Mapping):
                    continue
                if _cell_known(cell):
                    status, value, source = "FILLED", cell["v"], cell.get("b")
                else:
                    reason = cell.get("u") or cell.get("v") or "UNKNOWN"
                    status = "NOT_APPLICABLE" if reason in NOT_APPLICABLE else "UNKNOWN"
                    value, source = None, reason
                cells.append({"field": f, "group": _group(block, f), "status": status, "value": value, "source": source})
        counts = {k: sum(c["status"] == k for c in cells) for k in ("FILLED", "NOT_APPLICABLE", "UNKNOWN")}
        out.append({"step": s.get("step"), "action": s.get("action"), "food": s.get("food"), "counts": counts,
                    "cells": cells})
    return out


def advice_prompt(question: str, context: Any) -> str:
    return (
        "You are a cooking assistant inside a state-tracking system. The engine parsed the user's recipe "
        "step by step. The STATE TRACE below has four parts: where_you_are (the cook's current step and "
        "heat time so far); state_trace (per step, what the engine established about each food, and what "
        "it could not establish, with the reason); changes (what changed from one step to the next); and "
        "evidence_match_current_step (evidence rows found for this food and process, and whether salt, "
        "acid and lipid match the evidence context). Treat it as the ground truth about what happened "
        "in this kitchen, and answer for the cook's current step. If similar_public_recipe_reference is present, "
        "it is a DIFFERENT public recipe found by similarity search: you may compare against its stated conditions "
        "and name it, but never present its values as facts about this kitchen.\n"
        "Answer the QUESTION with 3-5 short, practical suggestions. For each suggestion, name the state "
        "fact it responds to, e.g. (step 1: acid_present = true, lot_members includes vinegar). "
        "If an unknown fact would change the advice, say so and say what the cook should check. "
        "food_T_typical_C, moisture_cap_C, thermal_dose_typical_min, cumulative_thermal_dose_min, thermal_state "
        "and oxygen_exposure_proxy come from the engine's physics simulation (typical scenario), not from a "
        "measurement: when you use one, call it simulated. Use them where they explain the outcome.\n"
        "Give no nutrient retention numbers or percentages. Plain text, no headings.\n\n"
        f"QUESTION: {question}\n\nSTATE TRACE (JSON):\n{json.dumps(context, indent=1, ensure_ascii=False)}\n"
    )


def advice_warnings(text: str) -> list[str]:
    return [f"UNSOURCED_PERCENT: {m}" for m in _PERCENT.findall(text)]


def _norm(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (list, tuple)):
        return ", ".join(str(v) for v in value)
    return str(value)


def _same(claimed: str, actual: str) -> bool:
    """Exact match, or the claimed number equals the engine value rounded to the claimed precision, or the
    claimed leading word equals the value. Trailing words ("simulated", a unit) are ignored."""
    c, a = claimed.strip().lower(), actual.strip().lower()
    if c == a:
        return True
    num = re.match(r"^(-?\d+(?:\.(\d+))?)(?![\d.])", c)
    if num:
        try:
            return round(float(a), len(num.group(2) or "")) == float(num.group(1))
        except ValueError:
            return False
    word = re.match(r"^([a-z_]+)", c)
    return bool(word) and word.group(1) == a


def citation_check(text: str, trace: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Every '(step N: field = value)' the model cites, compared with the engine's trace. Never edits text."""
    by_step: dict[Any, dict[str, Any]] = {}
    for t in trace:
        merged = by_step.setdefault(t.get("step"), {"known": {}, "unknown": {}})
        merged["known"].update(t.get("known") or {})
        merged["unknown"].update(t.get("unknown") or {})
    rows = []
    for m in _CITE.finditer(text):
        step = int(m.group(1))
        for part in re.split(r"[,;]", m.group(2)):
            pm = _PAIR.match(part)
            if not pm:
                continue
            field, claimed = pm.group(1), re.split(r"\s+[—–-]\s+|\s+\(", pm.group(2))[0].strip()
            row = {"step": step, "field": field, "claimed": claimed}
            s = by_step.get(step)
            if s is None:
                rows.append({**row, "actual": "NO_SUCH_STEP", "ok": False})
            elif field in s["known"]:
                actual = _norm(s["known"][field])
                rows.append({**row, "actual": actual, "ok": _same(claimed, actual)})
            elif field in s["unknown"]:
                actual = str(s["unknown"][field])
                rows.append({**row, "actual": actual, "ok": _same(claimed, actual) or _same(claimed, "unknown")})
            else:
                rows.append({**row, "actual": "NOT_IN_TRACE", "ok": False})
    return rows


def plain_prompt(recipe_text: str, question: str) -> str:
    """Identical to the S181 baseline prompt: no system contract."""
    return _tool("s181_build_demo_snapshot").baseline_prompt(recipe_text, question)


def licence_hits(obj: Any) -> list[str]:
    blob = json.dumps(obj, ensure_ascii=False, default=str)
    return [m for m in BBC_MARKERS if m in blob]


def validate(body: Any) -> dict[str, Any]:
    """Return a new, cleaned request dict or raise RequestError. Never mutates ``body``."""
    if not isinstance(body, Mapping):
        raise RequestError("question: body must be a JSON object")
    q, r, sw = body.get("question"), body.get("recipe_text"), body.get("self_written", False)
    if not isinstance(q, str) or not q.strip() or len(q) > MAX_QUESTION:
        raise RequestError(f"question: required string, 1-{MAX_QUESTION} chars")
    if not isinstance(r, str) or not r.strip() or len(r) > MAX_RECIPE:
        raise RequestError(f"recipe_text: required string, 1-{MAX_RECIPE} chars")
    if not isinstance(sw, bool):
        raise RequestError("self_written: must be true or false")
    return {"question": q.strip(), "recipe_text": r.strip(), "self_written": sw}


# ------------------------------------------------------------------ hosted LLM
def read_key(path: Path = NIM_ENV) -> str:
    for line in path.read_text(encoding="utf-8").splitlines():
        name, _, value = line.partition("=")
        if "KEY" in name.upper() and value.strip():
            return value.strip().strip("\"'")
    raise RuntimeError(f"no API key in {path}")


class NimLLM:
    """NVIDIA NIM chat completion, temperature 0. The key is held only inside the request header."""

    def __init__(self, model: str = DEFAULT_MODEL, timeout: int = LLM_TIMEOUT_S) -> None:
        self.model, self.timeout = model, timeout

    def __call__(self, prompt: str) -> str:
        payload = json.dumps({"model": self.model, "temperature": 0, "max_tokens": LLM_MAX_TOKENS,
                              "messages": [{"role": "user", "content": prompt}]}).encode()
        req = urllib.request.Request(NIM_URL, data=payload, method="POST", headers={
            "Content-Type": "application/json", "Authorization": f"Bearer {read_key()}"})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                body = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            raise RuntimeError(f"HTTP {exc.code}: {exc.read().decode('utf-8', 'replace')[:160]}") from None
        except urllib.error.URLError as exc:
            raise RuntimeError(f"network: {exc.reason}") from None
        try:
            text = strip_think(body["choices"][0]["message"].get("content") or "")
        except (KeyError, IndexError, TypeError):
            raise RuntimeError(f"unexpected reply: {json.dumps(body)[:160]}") from None
        if not text:
            raise RuntimeError("EMPTY_CONTENT (model returned reasoning only)")
        return text


def _timed(llm: LLM, prompt: str) -> dict[str, Any]:
    t = time.perf_counter()
    try:
        return {"status": "OK", "text": llm(prompt), "ms": round((time.perf_counter() - t) * 1000)}
    except Exception as exc:  # noqa: BLE001 - the real error is shown, never replaced by text
        return {"status": "LLM_ERROR", "reason": f"{type(exc).__name__}: {exc}"[:300],
                "ms": round((time.perf_counter() - t) * 1000)}


def _report(report) -> dict[str, Any]:
    return _tool("s181_build_demo_snapshot").report_dict(report)


def _lists(obj: Any) -> Any:
    """New copy with every tuple turned into a list, as a JSON round trip would. Never mutates ``obj``."""
    if isinstance(obj, Mapping):
        return {k: _lists(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_lists(v) for v in obj]
    return obj


class RangeSafeScenarioLayer:
    """Adapter for the frozen ``ScenarioLayer`` on the in-memory path.

    The full-corpus L2 runs read L1 rows from JSON, where a duration range ("2-5 min") is a list, which
    ``scenario_layer._triple`` handles. In memory the binder hands over a tuple, which ``_triple`` reads
    as a scalar and crashes on. Converting tuples to lists reproduces the batch input exactly; ``src/``
    is not edited (architecture freeze). A one-line core fix (``isinstance(v, (list, tuple))``) is the
    proper repair and needs a human decision.
    """

    def __init__(self, inner) -> None:
        self._inner = inner

    def run(self, rec):
        return self._inner.run(_lists(rec) if rec is not None else rec)

    def __getattr__(self, name: str):
        return getattr(self._inner, name)


def load_similar():
    """The 612k similar-recipe index, or None when its git-ignored inputs (ledgers/recipe_base,
    data/interim/wikibooks) are not on this machine. The rest of the engine works without it."""
    try:
        return _tool("s182_similar").SimilarIndex.load()
    except (FileNotFoundError, OSError, ImportError, ValueError) as exc:
        sys.stderr.write(f"similar-recipe search disabled: {type(exc).__name__}: {exc}\n")
        return None


# ------------------------------------------------------------------ engine
class LiveEngine:
    """Loads the frozen StateBuilder once (~6 s) and answers in ~30 ms plus LLM time."""

    def __init__(self, builder, similar=None) -> None:
        self.builder = builder
        self.similar = similar
        self.snap = _tool("s181_build_demo_snapshot")
        self.st = _tool("s182_live_stages")
        self.snap._set_rung(builder, True)
        if not isinstance(builder.l2, RangeSafeScenarioLayer):
            builder.l2 = RangeSafeScenarioLayer(builder.l2)

    @classmethod
    def load(cls, *, similar: bool = True) -> "LiveEngine":
        sys.path.insert(0, str(ROOT / "src"))
        from culinarystate.composition.state_full import StateBuilder
        return cls(StateBuilder(), load_similar() if similar else None)

    def similar_for(self, states: list[Mapping[str, Any]], recipe_text: str) -> dict[str, Any] | None:
        """Search all 612k recipes locally; run the engine on the best public (Wikibooks) candidates and keep
        the first whose heat steps share a process family with this recipe. Only public text is built."""
        if self.similar is None:
            return None
        foods = list(dict.fromkeys(s["food"] for s in states))
        result = self.similar.search(recipe_text, foods, self.st.process_names(states))
        mine = {h["family"] for h in self.st.heat_steps(states)}
        ref = None
        for rid in result.get("reference_candidates") or ():
            doc = self.similar.public_steps(rid)
            if not doc:
                continue
            try:
                heats = self.st.heat_steps(self.snap.jsonable(self.builder.build(doc["steps"][:MAX_RECIPE])))
            except Exception:  # noqa: BLE001 - a public recipe the frozen parser cannot read is skipped, not fatal
                continue
            if not heats:
                continue
            cand = {**{k: doc[k] for k in ("id", "title", "url", "licence")}, "heat_steps": heats[:6],
                    "same_process": bool(mine & {h["family"] for h in heats})}
            if cand["same_process"]:
                ref = cand
                break
            ref = ref or cand
        return {"search": result, "reference": ref}

    def evidence_cards(self, packet: Mapping[str, Any]) -> list[dict[str, Any]]:
        cards = []
        for role, ids in (("applied", packet.get("evidence_ids") or ()), ("near", packet.get("near_evidence_ids") or ())):
            for eid in ids:
                row = self.builder.evd.get(eid) or {}
                cards.append({"id": eid, "role": role,
                              **{k: self.snap.jsonable(row.get(k)) for k in CARD_FIELDS}})
        return cards

    def _stub(self, status: str, final: str, **extra: Any) -> dict[str, Any]:
        return {"status": status, "route": None, "packet": None, "draft": None, "draft_check": None,
                "final": final, "used_template": True, **extra}

    def changes(self, states: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
        """Step-to-step deltas on the cook-relevant fields only, before/after as plain values."""
        wanted = {f for fields in TRACE_FIELDS.values() for f in fields}
        out = []
        for t in self.snap.transitions(states):
            rows = [{"field": d["field"], "kind": d["kind"],
                     "before": (d["before"] or {}).get("v"), "after": (d["after"] or {}).get("v")}
                    for d in t["deltas"] if d["field"] in wanted]
            if rows:
                out.append({"from_step": t["from_step"], "to_step": t["to_step"], "changes": rows})
        return out

    def matches(self, state: Mapping[str, Any]) -> dict[str, Any]:
        """Per target: route, axis match values, and the evidence rows the engine found for this state."""
        y = state.get("Y") or {}
        out = {}
        for target in ("vitc", "lycopene"):
            ids = (y.get(f"{target}_evidence") or {}).get("v") or []
            out[target] = {"route": (y.get(f"{target}_route") or {}).get("v"),
                           "route_basis": (y.get(f"{target}_route") or {}).get("b"),
                           "axis_match": (y.get(f"{target}_compat") or {}).get("v"),
                           "evidence_found": self.evidence_cards({"near_evidence_ids": ids})}
        return out

    def advice_context(self, states: list[Mapping[str, Any]], food: str | None) -> dict[str, Any]:
        mine = [s for s in states if food is None or s["food"] == food] or states
        cur = mine[-1]
        q = cur.get("Q") or {}
        return {"where_you_are": {"food": cur["food"], "current_step": cur.get("step"), "action": cur.get("action"),
                                  "total_steps": max((s.get("step") or 0) for s in states),
                                  "hot_aqueous_minutes_so_far": (q.get("hot_aqueous_minutes") or {}).get("v"),
                                  "hot_fat_minutes_so_far": (q.get("hot_fat_minutes") or {}).get("v")},
                "state_trace": state_trace(states), "changes": self.changes(states),
                "evidence_match_current_step": self.matches(cur)}

    def _nutrient(self, question: str, states: list, foods: list[str], food: str | None) -> tuple[dict, dict | None]:
        from culinarystate.composition import claim_packet as CP, claim_verifier as CV
        target, kind = parse_target(question), parse_kind(question)
        if target is None:
            return self._stub("ABSTAIN_TARGET_NOT_WIRED", "Only vitamin C and lycopene are wired in this build, so "
                              "I won't give a number for this nutrient."), None
        if not states:
            return self._stub("ABSTAIN_NO_STATE", "I couldn't build a food state from this recipe text."), None
        if food is None:
            return self._stub("ASK_WHICH_FOOD", f"Which food do you mean: {', '.join(foods)}?"), None
        idx = max(i for i, s in enumerate(states) if s["food"] == food)
        packet = self.snap.jsonable(CP.claim_packet(states[idx], target, kind))
        return {"status": "PACKET", "route": packet["route"], "packet": packet, "state_index": idx, "draft": None,
                "draft_check": None, "final": CV.template_answer(packet), "used_template": True}, packet

    def analyse(self, question: str, recipe_text: str) -> dict[str, Any]:
        """Everything before the model: state, simulation, evidence, similar recipes, pipeline status. ~0.1-1 s."""
        t0 = time.perf_counter()
        states = self.snap.jsonable(self.builder.build(recipe_text))
        build_ms = round((time.perf_counter() - t0) * 1000)
        foods = list(dict.fromkeys(s["food"] for s in states))
        food, mode = pick_food(question, foods), question_mode(question)
        t1 = time.perf_counter()
        similar = self.similar_for(states, recipe_text) if states else None
        similar_ms = round((time.perf_counter() - t1) * 1000)
        packet, context = None, None
        if mode == "SAFETY":
            system = self._stub("ABSTAIN_SAFETY", SAFETY_TEXT)
        elif mode == "NUTRIENT":
            system, packet = self._nutrient(question, states, foods, food)
        elif not states:
            system = self._stub("ABSTAIN_NO_STATE", "I couldn't build a food state from this recipe text.")
        else:
            context = self.advice_context(states, food)
            ref = (similar or {}).get("reference")
            if ref:
                context["similar_public_recipe_reference"] = {
                    "note": "A DIFFERENT recipe (public, Wikibooks) found by similarity search; its conditions are "
                            "typical values for comparison, not facts about this kitchen.",
                    **{k: ref[k] for k in ("title", "licence", "heat_steps")}}
                context["similar_recipes_found_in_corpus"] = sum(similar["search"]["counts"].values())
            system = self._stub("ADVICE_NOT_SENT", "State-aware advice needs the hosted model, and this text was "
                                "not marked self-written or public, so nothing was sent.")
        cards = self.evidence_cards(packet) if packet else []
        public_similar = {"search": {k: v for k, v in (similar or {}).get("search", {}).items() if k != "hidden"},
                          "reference": (similar or {}).get("reference")} if similar else None
        stages = self.st.pre_model_stages(states=states, foods=foods, mode=mode, packet=packet, cards=cards,
                                          context=context, similar=similar, ms={"build": build_ms, "similar": similar_ms})
        return {"t0": t0, "question": question, "mode": mode, "states_full": states, "foods": foods, "food": food,
                "packet": packet, "context": context, "system": system, "cards": cards, "similar": public_similar,
                "hits": licence_hits([packet, cards, context, public_similar]), "pipeline": stages,
                "ms": {"pipeline": build_ms, "similar": similar_ms}}

    def response(self, a: Mapping[str, Any], *, model: str, plain: Any) -> dict[str, Any]:
        states, q = a["states_full"], a["question"]
        return {"labels": list(LABELS), "model": model, "question": q, "mode": a["mode"],
                "parsed": {"target": parse_target(q), "question_kind": parse_kind(q), "food": a["food"],
                           "foods": a["foods"]},
                "states": [{"index": i, "food": s["food"], "step": s.get("step"), "action": s.get("action")}
                           for i, s in enumerate(states)],
                "trace": state_trace(states), "coverage": coverage(states), "context": a["context"],
                "evidence": a["cards"], "similar": a["similar"], "pipeline": a["pipeline"], "system": a["system"],
                "plain": plain, "licence_hits": a["hits"],
                "timing_ms": {**a["ms"], "total": round((time.perf_counter() - a["t0"]) * 1000)}}

    def answer(self, question: str, recipe_text: str, *, llm: LLM, self_written: bool) -> dict[str, Any]:
        from culinarystate.composition import claim_verifier as CV
        a = self.analyse(question, recipe_text)
        packet, context, system, hits = a["packet"], a["context"], a["system"], a["hits"]
        send = self_written and not hits
        with ThreadPoolExecutor(max_workers=2) as pool:
            plain_job = pool.submit(_timed, llm, plain_prompt(recipe_text, question)) if send else None
            sys_job = None
            if send and packet is not None:
                sys_job = pool.submit(_timed, llm, verbaliser_prompt(question, packet))
            elif send and context is not None:
                sys_job = pool.submit(_timed, llm, advice_prompt(question, context))
            d = sys_job.result() if sys_job else None
            plain = plain_job.result() if plain_job else None
        verify = None
        if d is not None:
            system["draft_call"] = {k: v for k, v in d.items() if k != "text"}
            if d["status"] == "OK" and packet is not None:
                final, used_template, rep = CV.answer_or_template(d["text"], packet)
                system.update(draft=d["text"], draft_check=self.snap.report_dict(rep), final=final,
                              used_template=used_template)
                verify = ("done", "claim verifier passed: LLM answer shown" if rep.ok else
                          f"claim verifier failed ({', '.join(sorted(rep.codes))}): deterministic template shown")
            elif d["status"] == "OK":
                cites = citation_check(d["text"], context["state_trace"])
                system.update(status="STATE_AWARE_ADVICE", label="AI_SUGGESTED_STATE_GROUNDED", draft=d["text"],
                              final=d["text"], used_template=False, warnings=advice_warnings(d["text"]),
                              citations=cites)
                verify = ("done", f"{sum(c['ok'] for c in cites)}/{len(cites)} cited state facts match the engine")
            elif context is not None:
                system.update(status="ADVICE_LLM_ERROR", final=f"The model call failed ({d['reason']}); no advice shown.")
        elif a["mode"] != "SAFETY":
            verify = ("skipped", "nothing was sent to the model")
        stages = self.st.finish_stages(a["pipeline"], model=d if d is not None else
                                       ({"status": "SKIPPED", "reason": "not sent"} if a["mode"] != "SAFETY" else None),
                                       verify=verify)
        if d is None and a["mode"] != "SAFETY":
            stages = [{**s, "status": "skipped"} if s["id"] == "model" else s for s in stages]

        if hits:
            plain = {"status": "REFUSED_LICENCE", "reason": f"licence markers {hits} in context; nothing sent"}
        elif not self_written:
            plain = {"status": "NOT_SENT_TEXT_NOT_SELF_WRITTEN",
                     "reason": "Only public or self-written text may go to the hosted model."}
        elif plain["status"] == "OK" and packet is not None:
            plain["check"] = self.snap.report_dict(CV.verify(plain["text"], packet))
            ev = CV._evidence_numbers(packet)
            plain["claimed_numbers"] = [{"number": n, "matches_packet_evidence_value": CV._canon(n) in ev}
                                        for n, _ in CV.claimed_numbers(plain["text"])]
        elif plain["status"] == "OK":
            plain["warnings"] = advice_warnings(plain["text"])
        return self.response({**a, "pipeline": stages}, model=getattr(llm, "model", "unknown"), plain=plain)

    def analyse_only(self, question: str, recipe_text: str, *, model: str) -> dict[str, Any]:
        """The fast first phase for the UI's live pipeline display. No model call."""
        return self.response(self.analyse(question, recipe_text), model=model, plain=None)
