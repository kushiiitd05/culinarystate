"""USDA Table of Nutrient Retention Factors, Release 6 (2007) -> parsed rows.

File: caret-delimited, tilde-quoted; fields Retn_Code, FdGrp_CD, RetnDesc, Nutr_No, NutrDesc, Retn_Factor, date.
Documentation facts used here (retn06.pdf, p.1–3):
  * factors are mostly True Retention (%TR), some Apparent Retention (%AR) -> basis RETENTION_TR_OR_AR;
  * reported to the nearest 5 % -> uncertainty ±2.5;
  * values computed above 100 are reported as 100 -> 100 is right-censored (GT_CAP, ≥97.5).
The description parser is deterministic; every output keeps the raw description.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

CAP_LOWER_BOUND = 97.5
ROUNDING_HALF_WIDTH = 2.5

# abbreviation -> canonical step (order matters only for multi-word keys, matched first)
STEP_WORDS: dict[str, str] = {
    "STIR FRY": "stir-fry", "HARD COOKED": "hard-boil", "FRENCH FRY": "deep-fry", "HASH BROWN": "pan-fry",
    "BAKED STUFFD": "bake", "BOILED+BAKED": "boil+bake", "BOILED+FRIED": "boil+fry",
    "SAUTEED+SIMMERED": "saute+simmer", "BOILED/BAKED": "boil|bake", "FRIED/BROILED": "fry|broil",
    "BROILED/FRIED": "broil|fry", "BKD/SIMMRD": "bake|simmer",
    "BAKED": "bake", "BKD": "bake", "BROILED": "broil", "BRLD": "broil", "BOILED": "boil", "BLD": "boil",
    "BOILD": "boil", "SIMMERED": "simmer", "SIMMER": "simmer", "SIMR": "simmer", "SIMMR": "simmer",
    "SIMMRD": "simmer", "SIMM": "simmer", "SIMRD": "simmer", "FRIED": "fry", "FRYD": "fry",
    "SCRAMBLED": "scramble", "POACHED": "poach", "REHEATED": "reheat", "HEATED": "heat", "ROASTED": "roast",
    "BRAISED": "braise", "BRAIS": "braise", "BRSD": "braise", "BROWN": "brown", "BRWN": "brown",
    "BROWNED": "brown", "STEWED": "stew", "SAUTEED": "saute", "STEAMED": "steam", "TOASTED": "toast",
    "FLAMED": "flame", "MASHED": "mash", "DRAINED": "drain", "DRAIN": "drain", "DRAIND": "drain",
    "DRND": "drain", "CKD": "cook", "COOKED": "cook", "STORED": "store", "STIRRED": "stir",
}
FORM_WORDS = {"CANNED": "canned", "FROZEN": "frozen", "FRZN": "frozen", "FRN": "frozen", "DRIED": "dried",
              "FRESH": "fresh", "FRSH": "fresh", "CURED": "cured", "INST": "instant", "REG/QUICK": "regular/quick",
              "RTE": "ready-to-eat", "RAW": "raw", "GROUND": "ground", "SLICES": "sliced", "SLICE": "sliced",
              "CHOPS": "chops", "ROAST": "roast-cut", "CUT": "cut"}
PRESERVATION = {"canned": "can", "dried": "dry", "frozen": "freeze"}
DUR_RE = re.compile(r"(\d+(?:\.\d+)?)(?:/(\d+(?:\.\d+)?))?\s*(MIN|HRS|HR|HOUR)\b")


@dataclass(frozen=True)
class ParsedDesc:
    raw: str
    matrix_raw: str
    steps: tuple[str, ...]
    forms: tuple[str, ...]
    modifiers: dict = field(default_factory=dict)
    duration_min: tuple[float, float] | None = None   # (low, high) minutes
    unparsed: tuple[str, ...] = ()


def _duration(desc: str) -> tuple[float, float] | None:
    m = DUR_RE.search(desc)
    if not m:
        return None
    lo, hi, unit = float(m.group(1)), float(m.group(2) or m.group(1)), m.group(3)
    k = 1.0 if unit == "MIN" else 60.0
    return (lo * k, hi * k)


def _modifiers(desc: str) -> dict:
    d = desc.upper()
    mods: dict = {}
    if re.search(r"\bW/\s?DRIP", d):
        mods["drippings_included"] = True
    elif re.search(r"\bWO/\s?DRIP", d):
        mods["drippings_included"] = False
    if re.search(r"\bW/\s?COAT", d):
        mods["coating"] = True
    elif re.search(r"\b(WO|W/O)/?\s?COAT", d):
        mods["coating"] = False
    if "WATER USED" in d or "WATER USED" in d.replace("WTR", "WATER"):
        mods["cooking_water"] = "CONSUMED"
    elif re.search(r"LITTLE (WATER|WTR)", d):
        mods["cooking_water"] = "LITTLE_DRAINED"
    elif re.search(r"(WATER|WTR) COVER", d):
        mods["cooking_water"] = "COVER_DRAINED"
    elif "NOT DRAINED" in d:
        mods["cooking_water"] = "NOT_DRAINED"
    if "IN SKIN" in d:
        mods["skin"] = "ON"
    elif "PARED" in d:
        mods["skin"] = "PARED"
    if re.search(r"\bW/\s?LIQUID", d):
        mods["medium"] = "liquid"
    if re.search(r"\bW/\s?SHELL", d):
        mods["shell"] = "ON"
    elif re.search(r"\bWO/\s?SHELL", d):
        mods["shell"] = "OFF"
    if "CASSEROLE" in d:
        mods["vessel"] = "casserole"
    if "NOT STIRRED IN" in d:
        mods["alcohol_mixing"] = "NOT_STIRRED"
    elif "STIRRED" in d:
        mods["alcohol_mixing"] = "STIRRED"
    if "NO HEAT" in d:
        mods["heat"] = "NONE"
    if "OVERNIGHT" in d:
        mods["hold"] = "overnight"
    if "HOT LIQ" in d:
        mods["added_to"] = "hot liquid"
    if "FROM FRZN" in d or "FROM FRN" in d or "FROM FROZEN" in d:
        mods["start_state"] = "frozen"
    if "STORED" in d and "BROWNED" in d:
        mods["stored_before"] = True
    return mods


_NOISE = re.compile(r"\b(W/O|WO/|W/)\s?\S+|\bWATER USED\b|\bLITTLE (WATER|WTR)\b|\b(WATER|WTR) COVER\b|"
                    r"\bNOT DRAINED\b|\bIN SKIN\b|\bIN CASSEROLE\b|\(PARED\)|\bPARED\b|\bAPPROX\b|"
                    r"\bNOT STIRRED IN\b|\bINTO HOT LIQ\b|\bNO HEAT\b|\bOVERNIGHT\b|\bFROM\b|\bETC\b|"
                    + DUR_RE.pattern)


def parse_desc(desc: str) -> ParsedDesc:
    raw = desc
    d = desc.upper().replace("VEAL.SLICES", "VEAL,SLICES").replace("SWEETPOTAOTES", "SWEETPOTATOES")
    tokens = [t.strip() for t in re.split(r",", d) if t.strip()]
    matrix: list[str] = []
    steps: list[str] = []
    forms: list[str] = []
    unparsed: list[str] = []
    seen_step = False
    for tok in tokens:
        step_before_token = seen_step
        clean = _NOISE.sub(" ", tok).replace("(", " ").replace(")", " ")
        clean = re.sub(r"\s+", " ", clean).strip()
        tok_steps: list[str] = []
        rest = clean
        for key in sorted(STEP_WORDS, key=len, reverse=True):
            if re.search(rf"(?<![A-Z/]){re.escape(key)}(?![A-Z])", rest):
                tok_steps.append((rest.find(key), STEP_WORDS[key]))
                rest = re.sub(rf"(?<![A-Z/]){re.escape(key)}(?![A-Z])", " ", rest)
        tok_steps = [s for _, s in sorted(tok_steps)]
        rest_words = rest.split()
        tok_forms = [FORM_WORDS[w] for w in rest_words if w in FORM_WORDS]
        leftover = [w for w in rest_words if w not in FORM_WORDS]
        if tok_steps:
            seen_step = True
            steps.extend(tok_steps)
        forms.extend(tok_forms)
        if leftover:
            # words before the first step describe the matrix; after it, they are unparsed qualifiers
            (unparsed if step_before_token else matrix).append(" ".join(leftover))
    steps = [part for s in steps for part in s.split("+")]          # boil+bake -> boil, bake
    if not steps:                                                      # preservation is the process
        steps = [PRESERVATION[f] for f in forms if f in PRESERVATION]
    # "cook" is generic: drop it when a specific step is present
    if len(steps) > 1:
        steps = [s for s in steps if s != "cook"] or steps
    return ParsedDesc(raw=raw, matrix_raw=",".join(matrix), steps=tuple(dict.fromkeys(steps)),
                      forms=tuple(dict.fromkeys(forms)), modifiers=_modifiers(d), duration_min=_duration(d),
                      unparsed=tuple(unparsed))


@dataclass(frozen=True)
class R6Row:
    line_no: int
    retn_code: str
    food_group: str
    desc: str
    nutr_no: str
    nutr_desc: str
    factor_raw: str
    date_raw: str


def read_rows(path: Path) -> list[R6Row]:
    rows = []
    with Path(path).open(encoding="latin-1") as fh:
        for n, line in enumerate(fh, 1):
            f = [c.strip("~") for c in line.rstrip("\r\n").split("^")]
            if len(f) != 7:
                raise ValueError(f"line {n}: expected 7 fields, got {len(f)}")
            rows.append(R6Row(n, *f))
    return rows


def factor_qvalue(raw: str) -> dict:
    """Retention factor (%) as QVALUE: blank -> UNKNOWN; 100 -> CENSORED (≥97.5); else MEASURED ±2.5."""
    if raw.strip() == "":
        return {"status": "UNKNOWN", "unit": "%", "raw": raw}
    v = float(raw)
    if v >= 100:
        return {"status": "CENSORED", "unit": "%", "raw": raw,
                "censor": {"kind": "GT_CAP", "limit": CAP_LOWER_BOUND}}
    return {"status": "MEASURED", "value": v, "unit": "%", "uncertainty": ROUNDING_HALF_WIDTH, "raw": raw}
