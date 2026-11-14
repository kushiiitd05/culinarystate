"""Strict-v2 authorization retained; display finite source points without rounding to zero.

The frozen v2 policy is unchanged. This separately versioned renderer never broadens
its admissibility set, and checks the final v3 text after any adapter/fallback.
"""
from __future__ import annotations

from copy import deepcopy
from culinarystate.generation import strict_v2

VERSION = "strict-emission-v3.0.0"


def render(decision, packets, contexts, conditions, *, renderer=None, fallback=None):
    authorized = strict_v2.render(decision, packets, contexts, conditions)
    out = deepcopy(authorized)
    out["upstream_authorization_policy"] = authorized["policy"]
    out["policy"] = VERSION
    if not out["numbers"]:
        return out
    lines = []
    for number in out["numbers"]:
        display = repr(number["value"])
        number["display_value"] = display
        number["display_rule"] = "PYTHON_FINITE_FLOAT_REPR_NO_FIXED_DECIMAL_ROUNDING"
        lines.append(f"An unverified table row reports retention factor {display} [{number['evd_id']}].")
    lines.append("These are source reports, not validated predictions for your food.")
    canonical = "\n".join(lines)

    def attempt(function):
        try:
            return function(tuple(lines)) if function else canonical
        except Exception:
            return None

    text = attempt(renderer)
    if text != canonical:
        text = attempt(fallback) if fallback else None
    if text != canonical:
        refused = strict_v2._refuse("FINAL_RENDER_NOT_AUTHORIZED", out["excluded"])
        refused.update(policy=VERSION, upstream_authorization_policy=authorized["policy"])
        return refused
    out["text"] = text
    return out
