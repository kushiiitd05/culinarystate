"""STEP 07H-R: recipe EXPRESSION PROBE. Finds candidate surface expressions (deterministic syntax only) in recipe text and normalises each with the FROZEN condition parser/normalizer.
Recipe text is a PROCEDURAL OBSERVATION (source_plane=RECIPE, observation_class=TEXT_STATED): 'bake at 180 C' may be an equipment SETPOINT candidate; it never establishes core/surface temperature,
boiling is never 100 C, 'medium heat' is never a number. No E1-E7 tier, no chemistry, no inference."""
from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

from culinarystate.evidence import condition_normalizer as N
from culinarystate.evidence import condition_parser as P
from culinarystate.evidence import condition_units as U

ROOT = Path(__file__).resolve().parents[3]
PROBE_VERSION = "recipe_probe@1.0.0"
FRAC = "¼½¾⅐⅑⅒⅓⅔⅕⅖⅗⅘⅙⅚⅛⅜⅝⅞"
NUM = rf"(?:\d+\s+\d+/\d+|\d+/\d+|\d+(?:[.,]\d+)?[{FRAC}]?|[{FRAC}])"
SEP = r"(?:\s*(?:-|–|—|to)\s*)"
RANGE = rf"{NUM}(?:{SEP}{NUM})?"
DEG = r"(?:\s*(?:°|º|º|deg(?:rees?)?)\s*)"
TEMP_UNIT = r"(?:C|F|celsius|fahrenheit)"

with open(ROOT / "registry/recipe_location_cues_v1.csv", newline="", encoding="utf-8") as _f:
    LOC_CUES = [(re.compile(r["cue_regex"], re.I), r["location"], int(r["window_chars_before"]), r["cue_id"]) for r in csv.DictReader(_f)]

TIME_UNITS = r"(?:seconds?|secs?|minutes?|mins?|hours?|hrs?|days?|weeks?|months?|years?|h)"
_ui = lambda: None
RX = {
    "TEMPERATURE": re.compile(rf"(?P<x>{RANGE}{DEG}?\s*{TEMP_UNIT}\b(?:\s*(?:fan|conventional|gas))?|{RANGE}{DEG}(?=\W|$)(?![\d]))", re.I),
    "GAS_MARK": re.compile(rf"\b(?P<x>gas\s*(?:mark\s*)?{NUM})\b", re.I),
    "QUALITATIVE_HEAT": re.compile(r"\b(?P<x>(?:very\s+|medium[- ]|moderately\s+)?(?:low|medium|high|moderate|gentle|hot|slow|brisk|fierce)(?:[- ](?:high|low))?\s+(?:heat|oven|fire|flame|temperature))\b", re.I),
    "TIME": re.compile(rf"(?<![\w/])(?P<x>{RANGE}\s*(?:{TIME_UNITS})\b(?:\s+(?:and\s+)?{NUM}\s*(?:{TIME_UNITS})\b)?)", re.I),
    "TIME_QUALITATIVE": re.compile(r"\b(?P<x>overnight|a\s+few\s+(?:seconds|minutes|hours|days)|a\s+couple\s+of\s+(?:seconds|minutes|hours|days)|a\s+(?:little|short)\s+while|several\s+(?:minutes|hours))\b", re.I),
    "ENDPOINT": re.compile(r"\b(?P<x>(?:until|till)\s+[^,.;:()]{3,60})", re.I),
    "PRESSURE": re.compile(rf"(?<![\w/])(?P<x>{NUM}\s*(?:psi[ag]?|bar[ag]?|kpa|mpa|atm|mmhg|torr)\b)", re.I),
    "POWER": re.compile(rf"(?<![\w/])(?P<x>{NUM}\s*(?:watts?|kw|w)\b)", re.I),
    "MEDIUM": re.compile(r"\b(?:in|into|with|over)\s+(?:a\s+(?:large\s+|small\s+)?(?:pan|pot|saucepan|bowl)\s+of\s+)?(?P<x>(?:boiling|simmering|cold|hot|warm|salted|iced|ice|lightly\s+salted)?\s*(?:water|oil|stock|broth|milk|wine|vinegar|steam)\b)", re.I),
    "GEOMETRY": re.compile(rf"(?<![\w/])(?P<x>{NUM}(?:\s*(?:x|×|by)\s*{NUM})?\s*(?:cm|mm|inch(?:es)?|in|\"|″)(?![A-Za-z]))", re.I),
}
QTY_UNIT_WORDS = None  # filled lazily from the UNIT ledger
QUAL_QTY = re.compile(r"\b(?P<x>to taste|a pinch(?: of)?|pinch(?:es)?|a handful(?: of)?|handful|a dash(?: of)?|dash|a knob(?: of)?|knob|a drizzle|drizzle|a splash(?: of)?|splash|a little|a bit|some|plenty of|as needed|as required)\b", re.I)
SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9])")


def _units():
    global QTY_UNIT_WORDS
    if QTY_UNIT_WORDS is None:
        words = set()
        for line in open(ROOT / "ledgers/data/UNIT.jsonl", encoding="utf-8"):
            r = json.loads(line)
            if r.get("status") == "ACTIVE" and r.get("dimension") in ("MASS", "VOLUME", "COUNT"):
                words.add(r["canonical_name"].lower())
                words.update(a.lower() for a in r.get("aliases") or [])
        words |= {"g", "kg", "mg", "ml", "l", "cl", "dl", "oz", "lb", "lbs", "tsp", "tbsp", "cup", "cups", "pint", "pints", "tin", "tins", "can", "cans", "clove", "cloves", "slice", "slices", "stick", "sticks"}
        words = sorted((w for w in words if re.fullmatch(r"[a-z_ ]{1,14}", w) and w not in {"a", "an", "the"}), key=lambda w: -len(w))
        QTY_UNIT_WORDS = re.compile(rf"^\s*(?P<x>{RANGE}(?:\s*(?:x|×)\s*{NUM})?\s*(?:(?:{'|'.join(re.escape(w.replace('_', ' ')) for w in words)})\b\.?)?)", re.I)
    return QTY_UNIT_WORDS


def _eid(*parts) -> str:
    return "EXPR-" + hashlib.sha1("|".join(map(str, parts)).encode()).hexdigest()[:14]


def location_for(text: str, start: int):
    """-> (location, cue_id) from the registry cues in the window before the expression; first matching cue by registry order (SETPOINT wording beats MEDIUM)"""
    for rx, loc, win, cid in LOC_CUES:
        if rx.search(text[max(0, start - win): start + 12]):
            return loc, cid
    return "UNSPECIFIED", None


def _norm(var, raw, **kw):
    r = N.normalize_text(var, raw, **kw)
    return r


def _fields(res: dict) -> dict:
    return {"parser_candidate_type": res.get("_ptype"), "normalized_value_type": res["value_type"], "normalized_status": res["status"], "canonical_value": res.get("canonical_value"), "canonical_low": res.get("canonical_low"), "canonical_high": res.get("canonical_high"),
            "canonical_unit": res.get("canonical_unit"), "open_low": bool(res.get("open_low")) if res["value_type"] == "INTERVAL" else None, "open_high": bool(res.get("open_high")) if res["value_type"] == "INTERVAL" else None,
            "measurement_location": res.get("location"), "pressure_reference": res.get("pressure_reference"), "basis": res.get("basis"), "qualitative_value": res.get("qualitative"), "reason_codes": ",".join(res["reasons"]),
            "approximate": bool(res.get("approximate"))}


def _qual(raw):
    return {"parser_candidate_type": "QUALITATIVE", "normalized_value_type": "QUALITATIVE", "normalized_status": "VALID", "canonical_value": None, "canonical_low": None, "canonical_high": None, "canonical_unit": None, "open_low": None, "open_high": None,
            "measurement_location": None, "pressure_reference": None, "basis": None, "qualitative_value": raw, "reason_codes": "QUALITATIVE_NOT_NUMERIC,NO_SOURCED_NUMERIC_MAPPING", "approximate": False}


MASS_VOL = {"g": ("mass", 1e-3, "kg"), "gram": ("mass", 1e-3, "kg"), "grams": ("mass", 1e-3, "kg"), "kg": ("mass", 1.0, "kg"), "mg": ("mass", 1e-6, "kg"), "ml": ("volume", 1e-3, "L"), "l": ("volume", 1.0, "L"), "litre": ("volume", 1.0, "L"),
            "litres": ("volume", 1.0, "L"), "liter": ("volume", 1.0, "L"), "liters": ("volume", 1.0, "L"), "cl": ("volume", 1e-2, "L"), "dl": ("volume", 1e-1, "L"),
            "mm": ("length", 1e-3, "m"), "cm": ("length", 1e-2, "m"), "m": ("length", 1.0, "m"), "inch": ("length", 0.0254, "m"), "inches": ("length", 0.0254, "m"), "in": ("length", 0.0254, "m"), '"': ("length", 0.0254, "m"), "\u2033": ("length", 0.0254, "m")}
_FRAC_MIXED = re.compile(r"(?<![\d/])(\d+)\s+(\d+)/(\d+)(?![\d/])")
_FRAC_SIMPLE = re.compile(r"(?<![\d/])(\d+)/(\d+)(?![\d/])")
_MULT = re.compile(rf"^\s*(?P<n>{NUM})\s*(?:x|\u00d7)\s*(?P<rest>.+)$", re.I)


def _quantity_fractions(raw: str) -> str:
    """QUANTITY context only: '1 1/2' -> 1.5 and '1/2' -> 0.5 (in condition strings '15/20 min' stays AMBIGUOUS slash notation)."""
    raw = _FRAC_MIXED.sub(lambda m: format(int(m.group(1)) + int(m.group(2)) / int(m.group(3)), "g"), raw)
    return _FRAC_SIMPLE.sub(lambda m: format(int(m.group(1)) / int(m.group(2)), "g"), raw)


def amount_fields(raw: str, family: str = "QUANTITY"):
    """QUANTITY/GEOMETRY syntax only: number/range/unit/multiplier. Conversion ONLY for SI mass (-> kg), SI volume (-> L), length (-> m); tsp/tbsp/cup/oz/lb/count units are recognised but NOT converted (regional/density ambiguity; CQPO later).
    A bare number with no unit is a UNITLESS_NUMBER (a count or an amount; not asserted)."""
    mult, txt = 1.0, _quantity_fractions(P._fractions(raw))
    m = _MULT.match(txt)
    if m and not re.match(r"^\s*\d+\s*x\s*\d+\s*(?:cm|mm|inch|in)\b", txt, re.I):
        mult, txt = float(m.group("n").replace(",", ".").replace(" ", "")), m.group("rest")
    txt = re.sub(r"\bfl\.?\s*oz\b", "floz", txt, flags=re.I)
    p = P.parse_raw(txt)
    base = {"normalized_value_type": "UNKNOWN", "normalized_status": "AMBIGUOUS", "canonical_value": None, "canonical_low": None, "canonical_high": None, "canonical_unit": None, "open_low": None, "open_high": None, "measurement_location": None,
            "pressure_reference": None, "basis": None, "qualitative_value": None, "reason_codes": "", "approximate": bool(p["approximate"]), "parser_candidate_type": p["kind"]}
    if p["kind"] not in ("NUMBER", "RANGE", "SLASH_PAIR"):
        base["reason_codes"] = "RAW_TEXT_PRESENT_BUT_NOT_PARSED"
        return base
    unit = (p["unit_text"] or "").lower().strip(". ")
    vals = [p["value"] * mult] if p["kind"] == "NUMBER" else [p["low"] * mult, p["high"] * mult]
    base["normalized_value_type"] = "POINT" if p["kind"] == "NUMBER" else "INTERVAL"
    rc = ["MULTIPLIER_EXPANDED"] if mult != 1.0 else []
    conv = MASS_VOL.get(unit)
    if unit == "":
        base.update(normalized_status="VALID", canonical_unit="1", reason_codes=",".join(rc + ["UNITLESS_NUMBER"]))
        if p["kind"] == "NUMBER":
            base["canonical_value"] = vals[0]
        else:
            base["canonical_low"], base["canonical_high"], base["open_low"], base["open_high"] = vals[0], vals[1], False, False
        return base
    if conv:
        f = conv[1]
        base.update(normalized_status="VALID", canonical_unit=conv[2])
        if p["kind"] == "NUMBER":
            base["canonical_value"] = vals[0] * f
        else:
            base["canonical_low"], base["canonical_high"] = vals[0] * f, vals[1] * f
            base["open_low"] = base["open_high"] = False
            if vals[0] > vals[1]:
                base["normalized_status"] = "INVALID"
                rc.append("INTERVAL_REVERSED")
        if p["kind"] == "SLASH_PAIR":
            base["normalized_status"] = "AMBIGUOUS"
            rc.append("SLASH_NOTATION_RANGE_OR_ALTERNATIVES")
        base["reason_codes"] = ",".join(rc)
        return base
    base["reason_codes"] = ",".join(rc + ["UNIT_RECOGNISED_NO_CONVERSION"])
    return base


def extract(text: str, kind: str):
    """-> list of (family, start, end, raw) for one text unit. kind in {'ingredient','step'}"""
    out, taken = [], []
    free = lambda a, b: not any(a < e and s < b for s, e in taken)
    if kind == "ingredient":
        m = _units().match(text)
        if m and m.group("x").strip() and re.search(r"\d|[" + FRAC + "]", m.group("x")):
            rx_ = m.group("x").rstrip()
            out.append(("QUANTITY", m.start("x"), m.start("x") + len(rx_), rx_))
            taken.append((m.start("x"), m.end("x")))
        for m in QUAL_QTY.finditer(text):
            if free(m.start(), m.end()):
                out.append(("QUANTITY", m.start("x"), m.end("x"), m.group("x")))
                taken.append((m.start(), m.end()))
    for fam in ("TEMPERATURE", "GAS_MARK", "PRESSURE", "POWER", "GEOMETRY", "TIME", "TIME_QUALITATIVE", "QUALITATIVE_HEAT", "ENDPOINT", "MEDIUM"):
        if kind == "ingredient" and fam not in ("GEOMETRY", "TIME", "TEMPERATURE", "GAS_MARK"):
            continue
        for m in RX[fam].finditer(text):
            a, b = m.start("x"), m.end("x")
            if fam == "TEMPERATURE" and not re.search(r"°|º|deg", m.group("x"), re.I):
                mm = re.match(rf"\s*({NUM})", m.group("x"))   # bare 'C'/'F' unit: '1/2 c.' is a cup, not 0.5 C -> need a plausible temperature number and no abbreviation dot
                try:
                    v = float(P._fractions(mm.group(1)).replace(",", "."))
                except ValueError:
                    v = 0.0
                if v < 30 or text[b:b + 1] == ".":
                    continue
            if fam == "ENDPOINT" or free(a, b):
                out.append((fam, a, b, text[a:b]))
                if fam != "ENDPOINT":
                    taken.append((a, b))
    if kind == "step":
        for m in QUAL_QTY.finditer(text):
            if free(m.start(), m.end()) and m.group("x").lower() in ("to taste", "as needed", "as required"):
                out.append(("QUANTITY", m.start("x"), m.end("x"), m.group("x")))
    return sorted(out, key=lambda t: (t[1], t[2]))


def probe_recipe(rec: dict) -> list[dict]:
    """all expression rows for one recipe (dict from corpus.py)"""
    rows = []
    base = {"recipe_id": rec["recipe_id"], "recipe_family_id": rec.get("family_id"), "source_id": rec["source_id"], "source_family": rec["source_family"], "source_record_id": rec["source_record_id"]}

    def add(fam, kind, idx, sidx, a, b, raw, text, extra=None):
        row = dict(base)
        row.update({"expression_id": _eid(rec["recipe_id"], kind, idx, a, b, raw), "ingredient_index": idx if kind == "ingredient" else None, "step_index": idx if kind == "step" else None, "sentence_index": sidx, "char_start": a, "char_end": b,
                    "expression_family": fam, "raw_expression": raw, "raw_context_hash": hashlib.sha256(text.encode()).hexdigest()[:16], "text_unit": kind, "source_plane": "RECIPE", "observation_class": "TEXT_STATED", "probe_version": PROBE_VERSION, "compound_group_id": None})
        row.update(extra or {})
        rows.append(row)

    def handle(text, kind, idx):
        sents = [(0, text)] if kind == "ingredient" else None
        if sents is None:
            pos, sents = 0, []
            for s in SENT_SPLIT.split(text):
                j = text.find(s, pos)
                sents.append((j, s))
                pos = j + len(s)
        for si, (off, s) in enumerate(sents):
            n0 = len(rows)
            for fam, a, b, raw in extract(s.replace("\u2044", "/"), kind):
                a0, b0 = a + off, b + off
                raw_orig = s[a:b]
                role, ex = None, {"mapping_id": None, "mapping_status": None, "normalized_variable_id": None, "normalized_variable": None}
                if fam == "TEMPERATURE":
                    loc, cue = location_for(s, a)
                    var = N.temperature_variable_for(loc)
                    res = N.normalize_text(var, re.sub(r"\s*(?:fan|conventional|gas)\s*$", "", raw, flags=re.I).replace("º", "°"), location=loc)
                    ex = dict(_fields(res), normalized_variable=var, normalized_variable_id=res.get("variable_id"), mapping_id=cue, mapping_status="VERIFIED_DETERMINISTIC" if cue and loc == "SETPOINT" else ("CANDIDATE" if cue else "UNSPECIFIED"))
                    ex["measurement_location"] = loc
                    role = f"{loc}_CANDIDATE" + ("|FAN" if re.search(r"fan\s*$", raw, re.I) else "")
                elif fam == "GAS_MARK":
                    ex = dict(_qual(raw), mapping_id="GAS_MARK", mapping_status="UNSUPPORTED_NO_SOURCED_MAPPING", normalized_variable="temp_equipment_setpoint", normalized_variable_id=N.VARS["temp_equipment_setpoint"]["condition_variable_id"])
                    role = "SETPOINT_CANDIDATE|GAS_MARK"
                elif fam == "QUALITATIVE_HEAT":
                    ex = dict(_qual(raw), mapping_id=None, mapping_status="QUALITATIVE", normalized_variable=None, normalized_variable_id=None)
                    role = "HEAT_LEVEL"
                elif fam in ("TIME", "TIME_QUALITATIVE"):
                    if fam == "TIME_QUALITATIVE":
                        ex = dict(_qual(raw), mapping_id=None, mapping_status="QUALITATIVE", normalized_variable="time_duration", normalized_variable_id=N.VARS["time_duration"]["condition_variable_id"])
                    else:
                        res = N.normalize_text("time_duration", _timeraw(raw))
                        ex = dict(_fields(res), normalized_variable="time_duration", normalized_variable_id=res.get("variable_id"), mapping_id=None, mapping_status="VERIFIED_DETERMINISTIC" if res["status"] == "VALID" else "AMBIGUOUS")
                    role = "DURATION_CANDIDATE"
                elif fam == "ENDPOINT":
                    ex = dict(_qual(raw), mapping_id=None, mapping_status="QUALITATIVE", normalized_variable=None, normalized_variable_id=None)
                    role = "ENDPOINT_PHRASE"
                elif fam == "MEDIUM":
                    ex = dict(_qual(raw.strip()), mapping_id=None, mapping_status="CANDIDATE", normalized_variable="solvent_medium", normalized_variable_id=N.VARS["solvent_medium"]["condition_variable_id"])
                    role = "MEDIUM_CANDIDATE"
                elif fam == "PRESSURE":
                    res = N.normalize_text("pressure", raw)
                    ex = dict(_fields(res), normalized_variable="pressure", normalized_variable_id=res.get("variable_id"), mapping_id=None, mapping_status="VERIFIED_DETERMINISTIC" if res["status"] == "VALID" else "AMBIGUOUS")
                    role = "PRESSURE_CANDIDATE"
                elif fam == "POWER":
                    res = N.normalize_text("microwave_power", raw)
                    ex = dict(_fields(res), normalized_variable="microwave_power", normalized_variable_id=res.get("variable_id"), mapping_id=None, mapping_status="VERIFIED_DETERMINISTIC" if res["status"] == "VALID" else "AMBIGUOUS")
                    role = "POWER_CANDIDATE"
                elif fam == "GEOMETRY" and re.search(r"\d\s*(?:x|\u00d7|by)\s*\d", raw, re.I):
                    ex = dict(_qual(raw), parser_candidate_type="MULTI_DIMENSION", normalized_value_type="UNKNOWN", normalized_status="AMBIGUOUS", qualitative_value=None, reason_codes="MULTI_DIMENSION_EXPRESSION", normalized_variable=None, normalized_variable_id=None, mapping_id=None, mapping_status="SYNTAX_ONLY")
                    role = "SIZE_OR_DIMENSION"
                elif fam == "GEOMETRY":
                    ex = dict(amount_fields(raw.replace("×", "x") if "x" not in raw.lower() and "×" not in raw else raw.split("x")[0].split("×")[0]), normalized_variable=None, normalized_variable_id=None, mapping_id=None, mapping_status="SYNTAX_ONLY")
                    role = "SIZE_OR_DIMENSION"
                elif fam == "QUANTITY":
                    if QUAL_QTY.fullmatch(raw.strip()):
                        ex = dict(_qual(raw), mapping_id=None, mapping_status="QUALITATIVE", normalized_variable=None, normalized_variable_id=None)
                    else:
                        ex = dict(amount_fields(raw), normalized_variable=None, normalized_variable_id=None, mapping_id=None, mapping_status="SYNTAX_ONLY")
                    role = "INGREDIENT_AMOUNT" if kind == "ingredient" else "STEP_AMOUNT"
                add(fam, kind, idx, si, a0, b0, raw_orig, text, dict(ex, candidate_semantic_role=role))
            _group_oven(rows[n0:], s, off)

    for i, line in enumerate(rec["ingredient_lines"]):
        handle(line, "ingredient", i)
    for i, step in enumerate(rec["steps"]):
        handle(step, "step", i)
    for k, v in (rec.get("structured_times") or {}).items():
        if v and re.match(r"^P", str(v)):
            m = re.fullmatch(r"P(?:(\d+)D)?(?:T(?:(\d+)H)?(?:(\d+)M)?)?", str(v))
            if m and any(m.groups()):
                d, h, mi = (int(x) if x else 0 for x in m.groups())
                secs = d * 86400 + h * 3600 + mi * 60
                res = N.normalize_value("time_duration", value=secs, unit="s", raw=str(v))
                row = dict(base)
                row.update({"expression_id": _eid(rec["recipe_id"], "field", k, v), "ingredient_index": None, "step_index": None, "sentence_index": None, "char_start": None, "char_end": None, "expression_family": "TIME_STRUCTURED_FIELD", "raw_expression": str(v),
                            "raw_context_hash": hashlib.sha256(f"{k}={v}".encode()).hexdigest()[:16], "text_unit": "field:" + k, "source_plane": "RECIPE", "observation_class": "TEXT_STATED", "probe_version": PROBE_VERSION, "compound_group_id": None, "candidate_semantic_role": "TOTAL_OR_PREP_OR_COOK_TIME",
                            "normalized_variable": "time_duration", "normalized_variable_id": res.get("variable_id"), "mapping_id": None, "mapping_status": "ISO8601_DURATION_FIELD"})
                row.update(_fields(res))
                rows.append(row)
    return rows


_GAP = re.compile(r"^[\s/,;()]*(?:or|and)?[\s/,;()]*(?:fan|conventional|gas|mark)?[\s/,;()]*$", re.I)


def _group_oven(sent_rows, s, off):
    """oven compound 'A C / B C fan / gas N': adjacent TEMPERATURE/GAS_MARK components separated only by '/', ',', 'fan', 'gas' share a compound_group_id (components stay separate; nothing is converted or merged)"""
    comp = [r for r in sent_rows if r["expression_family"] in ("TEMPERATURE", "GAS_MARK")]
    gid = None
    for prev, cur in zip(comp, comp[1:]):
        gap = s[prev["char_end"] - off: cur["char_start"] - off]
        if len(gap) <= 14 and _GAP.match(gap):
            gid = gid or "OVEN-" + prev["expression_id"][5:]
            prev["compound_group_id"] = cur["compound_group_id"] = gid
        else:
            gid = None


def _timeraw(raw: str) -> str:
    """'1 hour 30 minutes' -> kept whole is unparsable by the single-value parser; first component is used only if the second is absent. Compound handled by caller as separate normalisation of the sum."""
    return raw
