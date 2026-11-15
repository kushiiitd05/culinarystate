"""D-116 item 5 / T6: named, masked state vector derived from the explicit state (retrieval only, never a decision).

Every dimension has a name. UNKNOWN is mask = 0 (value 0 means "known zero", never "unknown"). The vector is a pure
function of explicit cells, so it can always be traced back to them. Δ between two vectors is taken only on
dimensions known in both. Block weights are fixed for retrieval and listed in BLOCK_WEIGHTS; nothing is learned.
"""
from __future__ import annotations

import math
from typing import Any, Mapping, Optional

FAMILIES = ("COMBINATION", "COOLING", "DRY_HEAT", "ENDPOINT", "FAT_HEAT", "FERMENT_LEAVEN", "HEAT_CONTROL",
            "HEAT_GENERAL", "MECHANICAL_CUT", "MECHANICAL_MIX", "PRESERVATION", "RESERVATION", "RESTING", "SEPARATION",
            "SERVING", "SHAPING", "TRANSFER", "WET_HEAT")
HEAT = {"WET_HEAT", "DRY_HEAT", "FAT_HEAT", "HEAT_GENERAL", "COMBINATION"}
PHASES = ("AQUEOUS", "LIPID", "AQUEOUS+LIPID", "AIR")
SR_KEYS = ("fat_g_per_100g", "water_g_per_100g", "sodium_mg_per_100g", "protein_g_per_100g", "sugars_g_per_100g")
SR_SCALE = {"sodium_mg_per_100g": 1000.0}
ROUTES = ("DIRECT", "SCENARIO", "QUALITATIVE", "CONTEXT_MISMATCH", "UNKNOWN")
BLOCK_WEIGHTS = {"G": 1.0, "C": 1.0, "Q": 1.0, "Y": 0.5}     # fixed, documented; retrieval only


def dims() -> list[tuple[str, str]]:
    """(block, name) for every dimension, in order."""
    out = [("G", f"family={f}") for f in FAMILIES]
    out += [("G", "step_position"), ("G", "log_n_inputs"), ("G", "log_n_members"),
            ("G", "history_heated"), ("G", "history_cut"), ("G", "history_separated")]
    out += [("C", f"{a}_present") for a in ("salt", "acid", "lipid", "aqueous")]
    out += [("C", f"phase={p}") for p in PHASES]
    out += [("C", f"comember_mean_{k}") for k in SR_KEYS]
    out += [("Q", "temperature_C/100"), ("Q", "duration_min/60")]
    out += [("Y", f"{t}_route={r}") for t in ("vitc", "lycopene") for r in ROUTES]
    out += [("Y", f"{t}_retention") for t in ("vitc", "lycopene")]
    return out


def encode(*, family: Optional[str], step_position: float, n_inputs: int, n_members: int, history: set[str],
           ctx: Mapping[str, Any], temperature_c: Optional[float] = None, duration_min: Optional[float] = None,
           routes: Optional[Mapping[str, Mapping[str, Any]]] = None) -> tuple[list[float], list[int]]:
    """Returns (values, mask) aligned with dims()."""
    v: list[float] = []
    m: list[int] = []

    def put(x: Optional[float]):
        v.append(0.0 if x is None else float(x))
        m.append(0 if x is None else 1)

    for f in FAMILIES:
        put(None if family is None else float(family == f))
    put(step_position)
    put(math.log1p(n_inputs))
    put(math.log1p(n_members))
    for h in ("HEATED", "CUT", "SEPARATED"):
        put(float(h in history))
    for a in ("salt", "acid", "lipid", "aqueous"):
        x = ctx[f"{a}_present"].get("v")
        put(None if x is None else float(x is True))
    phase = ctx["contact_phase"].get("v")
    for p in PHASES:
        put(None if phase is None else float(phase == p))
    comp = (ctx.get("member_composition") or {}).get("v") or {}
    for k in SR_KEYS:
        xs = [c[k] for c in comp.values() if k in c]
        put(sum(xs) / len(xs) / SR_SCALE.get(k, 100.0) if xs else None)
    put(None if temperature_c is None else temperature_c / 100.0)
    put(None if duration_min is None else duration_min / 60.0)
    for t in ("vitc", "lycopene"):
        r = (routes or {}).get(t)
        for name in ROUTES:
            put(None if r is None else float(r.get("route") == name))
    for t in ("vitc", "lycopene"):
        r = (routes or {}).get(t) or {}
        put(r.get("retention") / 100.0 if r.get("route") == "DIRECT" and r.get("retention") is not None else None)
    return v, m


def _dims_for(n: int) -> list[tuple[str, str]]:
    """The dim list matching a vector's length, so V0 and V1 vectors both read correctly."""
    for candidate in (dims(), dims_v1()):
        if len(candidate) == n:
            return candidate
    raise ValueError(f"vector length {n} matches no known STATE_VECTOR version")


def delta(a: tuple[list[float], list[int]], b: tuple[list[float], list[int]]) -> dict[str, float]:
    """Named changes b - a on dimensions known in both (zero changes omitted)."""
    names = [n for _, n in _dims_for(len(a[0]))]
    return {n: round(vb - va, 3) for n, va, ma, vb, mb in zip(names, a[0], a[1], b[0], b[1])
            if ma and mb and abs(vb - va) > 1e-9}


def similarity(a: tuple[list[float], list[int]], b: tuple[list[float], list[int]]) -> float:
    """Block-weighted cosine over dimensions known in both (retrieval only)."""
    blocks = [blk for blk, _ in _dims_for(len(a[0]))]
    num = na = nb = 0.0
    for blk, va, ma, vb, mb in zip(blocks, a[0], a[1], b[0], b[1]):
        if ma and mb:
            w = BLOCK_WEIGHTS[blk]
            num += w * va * vb
            na += w * va * va
            nb += w * vb * vb
    return 0.0 if not na or not nb else round(num / math.sqrt(na * nb), 4)


# --------------------------------------------------------------------------- V1
# V1 exposes the physics history State v2 already computes. V0 carried only temperature and
# duration in Q (2 of 51 dims) while thermal dose, cumulative dose, hot-aqueous and hot-fat
# minutes, food temperature, moisture cap, lid state and the oxygen proxy sat unused, so V0's
# notion of "time" was step position plus a raw stated duration, not accumulated dose.
#
# V0 is left untouched: the committed step-9 retrieval diagnostic was measured on it. V1 extends
# V0's dim order, so V0's names are a prefix of V1's. Nothing is learned and nothing is estimated:
# every added dim is a cell State v2 produces, and an absent cell stays mask 0 (UNKNOWN), which
# remains distinct from a known zero.
V1_STATUS = "DIAGNOSTIC_RETRIEVAL_ONLY_WEIGHTS_NOT_VALIDATED"
_V1_EXTRA = (
    ("G", "log_heat_steps_so_far"),
    ("Q", "thermal_dose_typical_min/60"),
    ("Q", "cumulative_thermal_dose_min/60"),
    ("Q", "hot_aqueous_minutes/60"),
    ("Q", "hot_fat_minutes/60"),
    ("Q", "food_T_typical_C/100"),
    ("Q", "moisture_cap_C/100"),
    ("Q", "lid_covered"),
    ("Q", "oxygen_limited"),
)


def dims_v1() -> list[tuple[str, str]]:
    """(block, name) for every V1 dimension. V0's dims come first, in V0 order."""
    return dims() + list(_V1_EXTRA)


def encode_v1(*, family: Optional[str], step_position: float, n_inputs: int, n_members: int,
              history: set[str], ctx: Mapping[str, Any], temperature_c: Optional[float] = None,
              duration_min: Optional[float] = None,
              routes: Optional[Mapping[str, Mapping[str, Any]]] = None,
              heat_steps_so_far: Optional[int] = None,
              thermal_dose_min: Optional[float] = None,
              cumulative_dose_min: Optional[float] = None,
              hot_aqueous_minutes: Optional[float] = None,
              hot_fat_minutes: Optional[float] = None,
              food_t_typical_c: Optional[float] = None,
              moisture_cap_c: Optional[float] = None,
              lid_covered: Optional[bool] = None,
              oxygen_limited: Optional[bool] = None) -> tuple[list[float], list[int]]:
    """Returns (values, mask) aligned with dims_v1(). Absent cells are mask 0, never a guess."""
    v, m = encode(family=family, step_position=step_position, n_inputs=n_inputs,
                  n_members=n_members, history=history, ctx=ctx, temperature_c=temperature_c,
                  duration_min=duration_min, routes=routes)
    v, m = list(v), list(m)

    def put(x: Optional[float]):
        v.append(0.0 if x is None else float(x))
        m.append(0 if x is None else 1)

    put(None if heat_steps_so_far is None else math.log1p(heat_steps_so_far))
    put(None if thermal_dose_min is None else thermal_dose_min / 60.0)
    put(None if cumulative_dose_min is None else cumulative_dose_min / 60.0)
    put(None if hot_aqueous_minutes is None else hot_aqueous_minutes / 60.0)
    put(None if hot_fat_minutes is None else hot_fat_minutes / 60.0)
    put(None if food_t_typical_c is None else food_t_typical_c / 100.0)
    put(None if moisture_cap_c is None else moisture_cap_c / 100.0)
    put(None if lid_covered is None else float(bool(lid_covered)))
    put(None if oxygen_limited is None else float(bool(oxygen_limited)))
    return v, m
