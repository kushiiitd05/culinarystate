"""Step 09 field classes, locators, extractor proposals and deterministic validators (S157).

Status: PROVISIONAL_PENDING_09_GATE. Imported and re-exported by ``culinarystate.evidence.machinery``,
which owns the verification queue; this module holds no review or verification status at all.
Validators only FLAG (raw text preserved, normalisation in a new column); they never correct,
default or invent a value. Registries are read-only: measurement basis / location names, the
PHYSICAL rows of the unit registry plus a PROPOSED scientific unit list, and the temperature
bounds of ``condition_variable_bounds_registry_v1.csv``.
"""
from __future__ import annotations

import csv
import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from fractions import Fraction
from functools import cache
from pathlib import Path
from typing import Any

from culinarystate.ledgers.common import HUMANS

STATUS = "PROVISIONAL_PENDING_09_GATE"
CRITICAL_STATUS = "PROPOSED_PENDING_09_GATE"
MACHINERY_VERSION = "evidence_machinery@0.1-provisional"
ROOT = Path(__file__).resolve().parents[3]
REGISTRY = ROOT / "registry"


class MachineryError(ValueError):
    """Contract violation or refused write."""

# ---------------------------------------------------------------- field classes (09.2)
@dataclass(frozen=True)
class FieldClassSpec:
    name: str
    critical: bool
    description: str


_CLASSES = (
    ("numeric_value", True, "reported number of an observation"),
    ("unit", True, "unit string as printed"),
    ("basis", True, "measurement basis (measurement_basis_registry_v1 name or NOT_REPORTED)"),
    ("n", False, "number of samples / replicates"),
    ("dispersion", False, "dispersion value with dispersion_type attribute"),
    ("censoring", True, "censoring token (<LOD, ND, tr, <x, >x) or a detected value"),
    ("temperature", True, "temperature with unit"),
    ("time", True, "time with unit"),
    ("temperature_location", False, "measurement_location_registry_v1 name"),
    ("medium_water_ratio", False, "food:medium ratio such as 1:10"),
    ("matrix_identity", True, "food matrix as named in the document"),
    ("process", True, "process as named in the document"),
    ("method_platform", False, "analytical method / platform"),
    ("k_level", False, "K0..K4 or UNKNOWN (kinetic contract section 8)"),
    ("kinetic_parameter", True, "AUTHOR_REPORTED kinetic parameter (09.5)"),
)
FIELD_CLASSES: Mapping[str, FieldClassSpec] = {n: FieldClassSpec(n, c, d) for n, c, d in _CLASSES}
CRITICAL_FIELD_CLASSES = frozenset(n for n, c, _ in _CLASSES if c)

LOCATOR_KINDS = ("SPAN", "TABLE_CELL", "FIGURE")
EXTRACTOR_KINDS = ("AI_MODEL", "RULE", "HUMAN_EXTRACTOR")
DISPERSION_TYPES = ("SD", "SE", "CI95", "RANGE", "IQR", "NOT_REPORTED")
K_LEVELS = ("K0", "K1", "K2", "K3", "K4", "UNKNOWN")
KINETIC_PARAMETERS = ("k", "order", "Ea", "A", "T_ref", "D", "z", "half_life", "Q10")
ABSENT_TOKENS = ("NOT_REPORTED", "UNKNOWN")
RESERVED_ATTRIBUTES = frozenset({"reviewer", "verifier", "verified_at", "verification_status", "human_decision",
                                 "reviewed_at", "verification"})
SCIENTIFIC_UNITS = frozenset({"%", "g", "mg", "µg", "ug", "mcg", "ng", "kg", "l", "ml", "µl", "ul", "dl", "mol",
                              "mmol", "µmol", "umol", "nmol", "ppm", "ppb", "kj", "kcal", "j", "°c", "k", "°f",
                              "s", "min", "h", "d", "fw", "dw", "dm", "iu", "re", "rae", "te", "mol/l", "pa", "kpa"})
INJECTION = re.compile(r"ignore (all |any )?(the )?(previous|prior|above) (instructions|prompts?)|"
                       r"disregard (all |the )?"
                       r"(previous|prior|above)|system prompt|you are (now )?(an?|the) (assistant|ai|model|helpful)|"
                       r"mark (this|the|all) (row|rows|item|items|record|records|value|values)( as)? verified|"
                       r"<\|im_start\|>|\bassistant:", re.IGNORECASE)


# ---------------------------------------------------------------- registries (read-only)
def _csv_column(path: Path, column: str) -> frozenset[str]:
    with path.open(newline="", encoding="utf-8") as fh:
        return frozenset(r[column].strip() for r in csv.DictReader(fh) if r.get(column, "").strip())


@cache
def _registry(name: str) -> frozenset[str]:
    if name == "basis":
        return _csv_column(REGISTRY / "measurement_basis_registry_v1.csv", "name")
    if name == "location":
        return _csv_column(REGISTRY / "measurement_location_registry_v1.csv", "name")
    if name == "units":
        out: set[str] = set(SCIENTIFIC_UNITS)
        with (REGISTRY / "units" / "unit_registry_v1.csv").open(newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                if r.get("type") == "PHYSICAL":
                    out |= {a.strip().lower() for a in [r["unit"], *r["aliases"].split("|")] if a.strip()}
        return frozenset(out)
    raise KeyError(name)


@cache
def _temperature_bounds() -> tuple[Fraction, Fraction | None]:
    with (REGISTRY / "condition_variable_bounds_registry_v1.csv").open(newline="", encoding="utf-8") as fh:
        row = next(r for r in csv.DictReader(fh) if r["variable"] == "temp_unspecified")
    return Fraction(row["hard_min"]), (Fraction(row["plaus_max"]) if row["plaus_max"] else None)


# ---------------------------------------------------------------- locators and proposals
@dataclass(frozen=True)
class Locator:
    document_id: str
    kind: str
    page: int | None = None
    table: str | None = None
    row: str | None = None
    column: str | None = None
    char_start: int | None = None
    char_end: int | None = None
    figure: str | None = None

    def __post_init__(self) -> None:
        if not str(self.document_id or "").strip():
            raise MachineryError("locator needs a document_id")
        if self.kind not in LOCATOR_KINDS:
            raise MachineryError(f"locator kind must be one of {LOCATOR_KINDS}")
        if self.kind == "SPAN":
            s, e = self.char_start, self.char_end
            if not (isinstance(s, int) and isinstance(e, int) and 0 <= s < e):
                raise MachineryError("SPAN locator needs 0 <= char_start < char_end")
        if self.kind == "TABLE_CELL" and not all(str(x or "").strip() for x in (self.table, self.row, self.column)):
            raise MachineryError("TABLE_CELL locator needs table, row and column")
        if self.kind == "FIGURE" and not str(self.figure or "").strip():
            raise MachineryError("FIGURE locator needs a figure id")

    def to_dict(self) -> dict:
        return {k: getattr(self, k) for k in ("document_id", "kind", "page", "table", "row", "column",
                                              "char_start", "char_end", "figure")}


@dataclass(frozen=True)
class Proposal:
    """One extractor's reading of one field. A proposal is never a verification."""
    field_class: str
    raw_value: str
    extractor_id: str
    extractor_kind: str
    locator: Locator
    attributes: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.field_class not in FIELD_CLASSES:
            raise MachineryError(f"unknown field class {self.field_class!r}")
        if not isinstance(self.raw_value, str):
            raise MachineryError("raw_value must be the string as printed")
        if self.extractor_kind not in EXTRACTOR_KINDS:
            raise MachineryError(f"extractor_kind must be one of {EXTRACTOR_KINDS}")
        who = str(self.extractor_id or "").strip()
        if not who:
            raise MachineryError("extractor_id is required")
        if (self.extractor_kind == "HUMAN_EXTRACTOR") != (who in HUMANS):
            raise MachineryError("HUMAN_EXTRACTOR iff extractor_id names Kush or Parv")
        if not isinstance(self.locator, Locator):
            raise MachineryError("locator must be a Locator")
        attrs = dict(self.attributes)
        bad = RESERVED_ATTRIBUTES & {k.lower() for k in attrs}
        if bad:
            raise MachineryError(f"a proposal cannot carry review fields {sorted(bad)}")
        if not all(isinstance(k, str) and isinstance(v, str) for k, v in attrs.items()):
            raise MachineryError("attributes are str -> str")
        object.__setattr__(self, "attributes", dict(sorted(attrs.items())))

    @property
    def family(self) -> str:
        """Extractor family: the id before ``@version``, whitespace-trimmed and casefolded (review R1)."""
        return self.extractor_id.split("@", 1)[0].strip().casefold()

    def to_dict(self) -> dict:
        return {"field_class": self.field_class, "raw_value": self.raw_value, "extractor_id": self.extractor_id,
                "extractor_kind": self.extractor_kind, "locator": self.locator.to_dict(),
                "attributes": dict(self.attributes)}


# ---------------------------------------------------------------- parsing helpers
_NUM = re.compile(r"^\s*([+-]?\d+(?:\.\d+)?)\s*$")
_QTY = re.compile(r"^\s*([+-]?\d+(?:\.\d+)?)\s*(.*?)\s*$")
_TEMP_UNITS = {"°c": "C", "ºc": "C", "° c": "C", "c": "C", "°f": "F", "ºf": "F", "° f": "F", "f": "F", "k": "K"}
_TIME_S = {"s": 1, "sec": 1, "secs": 1, "second": 1, "seconds": 1, "min": 60, "mins": 60, "minute": 60,
           "minutes": 60, "h": 3600, "hr": 3600, "hrs": 3600, "hour": 3600, "hours": 3600, "d": 86400,
           "day": 86400, "days": 86400, "week": 604800, "weeks": 604800}
_TIME_RAW_ONLY = {"month", "months", "year", "years"}


def _dec(s: str) -> Decimal | None:
    m = _NUM.match(s or "")
    if not m:
        return None
    try:
        return Decimal(m.group(1))
    except InvalidOperation:
        return None


def _fs(x: Fraction) -> str:
    """Exact decimal string of a fraction with a terminating expansion, else n/d."""
    d = Decimal(x.numerator) / Decimal(x.denominator)
    if Fraction(d) == x:
        return format(d.normalize(), "f")
    return f"{x.numerator}/{x.denominator}"


def _temperature_K(raw: str) -> tuple[Fraction | None, str | None]:
    m = _QTY.match(raw or "")
    if not m:
        return None, None
    unit = _TEMP_UNITS.get(m.group(2).strip().lower())
    if unit is None:
        return None, m.group(2).strip() or None
    v = Fraction(m.group(1))
    return {"C": v + Fraction(27315, 100), "F": (v - 32) * Fraction(5, 9) + Fraction(27315, 100), "K": v}[unit], unit


def _censoring(raw: str) -> tuple[str, str | None]:
    t = (raw or "").strip()
    low = t.lower().replace(" ", "")
    if low in ("nd", "n.d.", "n.d", "notdetected", "<nd"):
        return "NON_DETECT", None
    if low in ("<lod", "<dl", "belowlod"):
        return "BELOW_LOD", None
    if low in ("<loq", "belowloq"):
        return "BELOW_LOQ", None
    if low in ("tr", "tr.", "trace", "traces"):
        return "CENSORED_UNKNOWN", None
    m = re.fullmatch(r"([<>])\s*(\d+(?:\.\d+)?)", t)
    if m:
        return ("LT_STATED" if m.group(1) == "<" else "GT_STATED"), m.group(2)
    if _dec(t) is not None:
        return "DETECTED", None
    if t in ABSENT_TOKENS:
        return "NOT_REPORTED", None
    return "UNPARSED", None


def normalise_value(p: Proposal) -> dict:
    """New-column normalisation; the raw string is always kept and never replaced."""
    raw, fc = p.raw_value, p.field_class
    out: dict[str, Any] = {"raw": raw, "status": "RAW_ONLY"}
    if raw.strip() in ABSENT_TOKENS:
        return {"raw": raw, "status": raw.strip()}
    if fc in ("numeric_value", "dispersion", "kinetic_parameter", "n"):
        d = _dec(raw)
        if d is not None:
            out.update(status="NORMALISED", value=format(d, "f"))
    elif fc == "temperature":
        k, _ = _temperature_K(raw)
        if k is not None:
            out.update(status="NORMALISED", value_K=_fs(k), normalizer=MACHINERY_VERSION)
    elif fc == "time":
        m = _QTY.match(raw)
        unit = m.group(2).strip().lower() if m else ""
        if m and unit in _TIME_S:
            out.update(status="NORMALISED", value_s=_fs(Fraction(m.group(1)) * _TIME_S[unit]),
                       normalizer=MACHINERY_VERSION)
        elif m and unit in _TIME_RAW_ONLY:
            out.update(status="NOT_CONVERTED")
    elif fc == "censoring":
        kind, limit = _censoring(raw)
        out.update(status="NORMALISED" if kind != "UNPARSED" else "RAW_ONLY", censoring=kind)
        if limit is not None:
            out["limit"] = limit
    return out


def _in_span(value: str, span: str) -> bool:
    v, s = " ".join(value.split()), " ".join(span.split())
    if not v:
        return False
    return re.search(r"(?<![0-9A-Za-z.])" + re.escape(v) + r"(?![0-9A-Za-z])", s) is not None


def prompt_injection_flags(text: str | None) -> tuple[str, ...]:
    return ("PROMPT_INJECTION_SUSPECTED",) if text and INJECTION.search(text) else ()


# ---------------------------------------------------------------- validators (09.3)
def _check_class(p: Proposal) -> list[str]:
    raw, fc, a = p.raw_value.strip(), p.field_class, p.attributes
    flags: list[str] = []
    if raw in ABSENT_TOKENS:
        return flags
    if fc == "numeric_value":
        d = _dec(raw)
        if d is None:
            flags.append("NOT_NUMERIC")
            if re.fullmatch(r"[+-]?\d+,\d+", raw):
                flags.append("DECIMAL_COMMA_AMBIGUOUS")
        elif d == 0 and a.get("censoring") != "TRUE_ZERO":
            flags.append("ZERO_REQUIRES_TRUE_ZERO")
    elif fc == "unit":
        parts = [x for x in re.split(r"[\s/]+", raw.lower()) if x and not re.fullmatch(r"\d+(\.\d+)?", x)]
        if not parts or any(x not in _registry("units") for x in parts):
            flags.append("UNIT_NOT_IN_REGISTRY")
    elif fc == "basis" and raw not in _registry("basis"):
        flags.append("BASIS_NOT_IN_REGISTRY")
    elif fc == "temperature_location" and raw not in _registry("location"):
        flags.append("LOCATION_NOT_IN_REGISTRY")
    elif fc == "n":
        if not re.fullmatch(r"\d+", raw) or int(raw) < 1:
            flags.append("N_INVALID")
    elif fc == "dispersion":
        dt = a.get("dispersion_type")
        if not dt:
            flags.append("DISPERSION_TYPE_MISSING")
        elif dt not in DISPERSION_TYPES:
            flags.append("DISPERSION_TYPE_INVALID")
        d = _dec(raw)
        if d is None:
            flags.append("NOT_NUMERIC")
        elif d < 0:
            flags.append("DISPERSION_NEGATIVE")
    elif fc == "censoring" and _censoring(raw)[0] == "UNPARSED":
        flags.append("CENSORING_UNPARSED")
    elif fc == "temperature":
        k, unit = _temperature_K(raw)
        if k is None:
            flags.append("UNIT_MISSING" if unit is None and _QTY.match(raw) else "TEMPERATURE_UNPARSED")
        else:
            lo, hi = _temperature_bounds()
            if k < lo:
                flags.append("TEMPERATURE_BELOW_ABSOLUTE_ZERO")
            elif hi is not None and k > hi:
                flags.append("ABOVE_PLAUSIBLE_BOUND")
    elif fc == "time":
        m = _QTY.match(raw)
        unit = m.group(2).strip().lower() if m else ""
        if not m or not unit:
            flags.append("UNIT_MISSING" if m else "TIME_UNPARSED")
        elif unit not in _TIME_S and unit not in _TIME_RAW_ONLY:
            flags.append("TIME_UNIT_UNKNOWN")
        elif Fraction(m.group(1)) < 0:
            flags.append("TIME_NEGATIVE")
    elif fc == "medium_water_ratio":
        m = re.fullmatch(r"(\d+(?:\.\d+)?)\s*:\s*(\d+(?:\.\d+)?)", raw)
        d = _dec(raw)
        if m:
            if Decimal(m.group(1)) <= 0 or Decimal(m.group(2)) <= 0:
                flags.append("RATIO_INVALID")
        elif d is None or d <= 0:
            flags.append("RATIO_INVALID")
    elif fc == "k_level" and raw not in K_LEVELS:
        flags.append("K_LEVEL_INVALID")
    elif fc == "kinetic_parameter":
        if a.get("parameter") not in KINETIC_PARAMETERS:
            flags.append("KINETIC_PARAMETER_UNKNOWN")
        if a.get("value_status") != "AUTHOR_REPORTED":
            flags.append("KINETIC_NOT_AUTHOR_REPORTED")
        if _dec(raw) is None:
            flags.append("NOT_NUMERIC")
    elif fc in ("matrix_identity", "process", "method_platform") and not raw:
        flags.append("EMPTY_VALUE")
    return flags


def validate_proposal(p: Proposal, span_text: str | None) -> tuple[str, ...]:
    """Flag codes for one proposal against the cited span text. Flags only: nothing is corrected."""
    flags = _check_class(p)
    if p.raw_value.strip() not in ABSENT_TOKENS:
        if span_text is None:
            flags.append("NO_SPAN_TEXT")
        elif not _in_span(p.raw_value, span_text):
            flags.append("VALUE_NOT_IN_SPAN")
    digitised = p.attributes.get("digitisation_tool") and p.attributes.get("digitisation_version")
    if p.locator.kind == "FIGURE" and not digitised:
        flags.append("FIGURE_REQUIRES_DIGITISATION_RECORD")
    flags += prompt_injection_flags(span_text)
    return tuple(dict.fromkeys(flags))


def _interval(s: str, decimals: int | None) -> tuple[Fraction, Fraction] | None:
    d = _dec(s)
    if d is None:
        return None
    places = decimals if decimals is not None else max(0, -d.as_tuple().exponent)
    half = Fraction(1, 2 * 10 ** places)
    return Fraction(d) - half, Fraction(d) + half


def check_retention_arithmetic(before: str, after: str, yield_factor: str | None, reported: str, *,
                               decimals: int) -> tuple[str, ...]:
    """Reported retention vs after/before x yield, every displayed value taken as a rounding interval."""
    b, a, r = _interval(before, decimals), _interval(after, decimals), _interval(reported, None)
    y = _interval(yield_factor, None) if yield_factor else (Fraction(1), Fraction(1))
    if None in (b, a, r, y) or b[0] <= 0:
        return ("ARITHMETIC_UNPARSED",)
    lo, hi = a[0] / b[1] * y[0], a[1] / b[0] * y[1]
    return () if r[1] >= lo and r[0] <= hi else ("ARITHMETIC_INCONSISTENT",)


def check_percent_change(before: str, after: str, reported_pct: str, *, decimals: int) -> tuple[str, ...]:
    """Reported percent change vs (after - before) / before x 100 under rounding intervals."""
    b, a, r = _interval(before, decimals), _interval(after, decimals), _interval(reported_pct, None)
    if None in (b, a, r) or b[0] <= 0:
        return ("ARITHMETIC_UNPARSED",)
    lo, hi = (a[0] - b[1]) / b[1] * 100, (a[1] - b[0]) / b[0] * 100
    return () if r[1] >= lo and r[0] <= hi else ("ARITHMETIC_INCONSISTENT",)
