"""Raw/cooked description pairs in USDA SR Legacy (X15, SSOT §198.7 "FoodData Central raw/cooked entries").

A pair is (`X, raw`, `X, cooked[, method][, drained][, with/without salt]`) with the same remaining description
segments. The comparable quantity is the dry-basis ratio
    R = (N_cooked / (100 - water_cooked)) / (N_raw / (100 - water_raw)),
which equals USDA true retention exactly when cooking conserves total solids; leaching of solids biases it.
Not matched samples (SSOT: "often not matched samples/interventions"), so pairs are candidates, never evidence.
"""
from __future__ import annotations

import pandas as pd

METHOD = {"boiled": "boil", "simmered": "simmer", "steamed": "steam", "stewed": "stew", "braised": "braise",
          "roasted": "roast", "baked": "bake", "broiled": "broil", "grilled": "grill", "fried": "fry",
          "pan-fried": "fry", "pan-browned": "fry", "stir-fried": "fry", "microwaved": "microwave",
          "poached": "poach", "scrambled": "fry"}
DROP = {"drained", "unheated", "heated"}
SALT = {"with salt": True, "without salt": False}


def split_state(desc: str) -> tuple[str, str | None, str | None, bool | None]:
    """(base key, RAW/COOKED/None, method, salted). Segments are comma-separated, lower-cased."""
    segs = [s.strip().lower() for s in desc.split(",")]
    base, state, method, salt = [], None, None, None
    for s in segs:
        if s == "raw":
            state = "RAW"
        elif s == "cooked":
            state = "COOKED"
        elif s in METHOD:
            state, method = "COOKED", method or METHOD[s]
        elif s in SALT:
            salt = SALT[s]
        elif s not in DROP:
            base.append(s)
    return "|".join(base), state, method, salt


def pair_foods(food: pd.DataFrame) -> pd.DataFrame:
    """One raw partner per cooked variant; among salted/unsalted twins keep the unsalted one (salt shifts Na)."""
    rows = [(r.fdc_id, *split_state(r.description)) for r in food.itertuples()]
    df = pd.DataFrame(rows, columns=["fdc_id", "base", "state", "method", "salt"])
    raw = df[df.state == "RAW"].drop_duplicates("base").set_index("base").fdc_id
    ck = df[(df.state == "COOKED") & df.base.isin(raw.index)].copy()
    ck["salt_rank"] = ck.salt.map({False: 0, None: 1, True: 2})
    ck = ck.sort_values(["base", "method", "salt_rank"], na_position="last").drop_duplicates(["base", "method"])
    return pd.DataFrame({"base": ck.base, "raw_id": ck.base.map(raw), "cooked_id": ck.fdc_id,
                         "method": ck.method, "salted": ck.salt}).reset_index(drop=True)


def dry_basis_ratio(n_raw: float, water_raw: float, n_cooked: float, water_cooked: float) -> float | None:
    if not n_raw or water_raw >= 100 or water_cooked >= 100:
        return None
    return round((n_cooked / (100 - water_cooked)) / (n_raw / (100 - water_raw)), 4)
