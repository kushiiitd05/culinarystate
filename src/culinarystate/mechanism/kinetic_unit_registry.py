"""Kinetic unit rows and exact conversions (S178 aa-fit-sim, T5-C07-R5). AI_DRAFTED rows, IN the UNIT ledger (D-079).

Draft of the additive UNIT contract for kinetic units (R-02, CHG-24-4): rate constants (s^-1, min^-1, h^-1, d^-1),
activation energy per amount (J/mol, kJ/mol, kcal/mol with its calorie convention) and absolute temperature (K, degC).
Rows live in ``registry/kinetic_units_v1_DRAFT.csv``. Since D-079 (2026-11-10) they are also minted into the UNIT
ledger by ``tools/s179_mint_kinetic_units.py`` (this module never writes the ledger; ``ledger_unit_ids`` reads it).
Each conversion factor is an exact ``Fraction``; there is no rounding and no default.

Rules kept here
- "kcal/mol" is AMBIGUOUS: the thermochemical calorie (4184 J) and the International Table calorie (4186.8 J) differ by
  about 0.07 %. The plain alias resolves to UNKNOWN until the caller declares ``calorie="TH"`` or ``"IT"``; it is never
  defaulted (project law: UNKNOWN is not a default). Both factors are SOURCE_UNVERIFIED_AGENT_RECALLED.
- Time factors (min = 60 s, h = 3600 s, d = 86400 s) and kJ = 1000 J are the ones already in the repo
  (``lineage.kinetic_contract.SECONDS_PER_UNIT``, ``kinetics.units``); a test cross-checks every row ``units.py`` can parse.
- degC is affine (K = degC + 273.15 exactly); it is never multiplied or raised, and an Arrhenius term needs Kelvin (G24.3).
- A PARAM unit "resolves" when its raw string is a registry name or alias (or a coherent SI string of ``units.py``)
  AND its dimension matches the FORM slot; ``param_unit_issues`` is the check wired to a PARAM record.

``units.py`` has no ``kcal`` token and is not edited by this lane; the registry carries the calorie factors instead.
Before D-079 the ledger schema ``ledgers/schemas/UNIT.schema.json`` could not hold these rows (no rate or
energy-per-amount dimension, no KINETIC unit_type). ``SCHEMA_DELTA`` states the additive enum change D-079 applied.
"""
from __future__ import annotations

import csv
import io
import json
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping

from culinarystate.simulation.kinetics import units as U

STATUS = "AI_DRAFTED_IN_LEDGER_D079"
VERSION = "kinetic-unit-registry-0.1.0-draft"
ROOT = Path(__file__).resolve().parents[3]
CSV_PATH = ROOT / "registry" / "kinetic_units_v1_DRAFT.csv"
LEDGER_PATH = ROOT / "ledgers" / "data" / "UNIT.jsonl"
COLUMNS = ("proposed_key", "canonical_name", "aliases", "unit_type", "dimension_expr", "si_unit", "si_factor_exact",
           "si_factor_float", "convention", "needs_source", "source_status", "units_py_parses", "notes")
CALORIES = ("TH", "IT")
SCHEMA_DELTA = {"unit_type": ["KINETIC"], "dimension": ["RATE_PER_TIME", "ENERGY_PER_AMOUNT"],
                "reason": "UNIT.schema.json v1.0.0 dimension enum = MASS VOLUME COUNT TEMPERATURE TIME LENGTH NONE; "
                          "unit_type enum has no KINETIC (additive change, H4)"}
_SRC_REPO = "REPO_CODE (kinetics.units tokens; kinetic_contract.SECONDS_PER_UNIT for time)"
_SRC_RECALL = "SOURCE_UNVERIFIED_AGENT_RECALLED"


def _row(key: str, name: str, aliases: str, utype: str, dim: str, si_unit: str, factor: Fraction | None,
         convention: str, needs_source: bool, source_status: str, notes: str) -> dict[str, str]:
    return {"proposed_key": key, "canonical_name": name, "aliases": aliases, "unit_type": utype, "dimension_expr": dim,
            "si_unit": si_unit, "si_factor_exact": "" if factor is None else f"{factor.numerator}/{factor.denominator}",
            "si_factor_float": "" if factor is None else repr(float(factor)), "convention": convention,
            "needs_source": str(needs_source), "source_status": source_status,
            "units_py_parses": "", "notes": notes}


def build_rows() -> list[dict[str, str]]:
    """The draft rows, deterministic. ``units_py_parses`` is filled from ``units.parse_unit`` (a fact, not an input)."""
    rate = "TIME^-1"
    en = "ENERGY*AMOUNT^-1"
    rows = [
        _row("KU-001", "s^-1", "1/s|s-1|per s|per second|sec^-1", "KINETIC", rate, "1/s", Fraction(1), "", False,
             _SRC_REPO, "first-order rate constant, coherent SI"),
        _row("KU-002", "min^-1", "1/min|min-1|per min|per minute", "KINETIC", rate, "1/s", Fraction(1, 60), "", False,
             _SRC_REPO, "1 min^-1 = 1/60 s^-1 exactly (60 s per min)"),
        _row("KU-003", "h^-1", "1/h|h-1|per h|per hour|hr^-1|1/hr", "KINETIC", rate, "1/s", Fraction(1, 3600), "", False,
             _SRC_REPO, "1 h^-1 = 1/3600 s^-1 exactly"),
        _row("KU-004", "d^-1", "1/d|d-1|per day|day^-1|1/day", "KINETIC", rate, "1/s", Fraction(1, 86400), "", False,
             _SRC_REPO, "1 d^-1 = 1/86400 s^-1 exactly (storage studies)"),
        _row("KU-005", "J/mol", "J mol-1|J.mol-1|J mol^-1|J*mol^-1", "KINETIC", en, "J/mol", Fraction(1), "", False,
             _SRC_REPO, "activation energy, coherent SI"),
        _row("KU-006", "kJ/mol", "kJ mol-1|kJ.mol-1|kJ mol^-1|kJ*mol^-1", "KINETIC", en, "J/mol", Fraction(1000), "",
             False, _SRC_REPO, "1 kJ/mol = 1000 J/mol exactly"),
        _row("KU-007", "kcal_th/mol", "kcal_TH/mol|kcal(th)/mol", "KINETIC", en, "J/mol", Fraction(4184),
             "CALORIE=TH: 1 cal = 4.184 J (thermochemical), exact by definition", True, _SRC_RECALL,
             "1 kcal_th/mol = 4184 J/mol exactly; the usual convention in chemical-kinetics papers but not proven for "
             "any one paper"),
        _row("KU-008", "kcal_IT/mol", "kcal_IT/mol|kcal(IT)/mol", "KINETIC", en, "J/mol", Fraction(41868, 10),
             "CALORIE=IT: 1 cal = 4.1868 J (International Table), exact by definition", True, _SRC_RECALL,
             "1 kcal_IT/mol = 4186.8 J/mol exactly"),
        _row("KU-009", "kcal/mol", "kcal mol-1|kcal.mol-1|kcal mol^-1|kcal*mol^-1", "KINETIC", en, "J/mol", None,
             "AMBIGUOUS_CALORIE: TH 4184 J or IT 4186.8 J; resolve only with a declared calorie", True,
             _SRC_RECALL, "UNKNOWN factor until the calorie convention is declared (never defaulted)"),
        _row("KU-010", "K", "kelvin", "KINETIC", "TEMPERATURE", "K", Fraction(1), "", False, _SRC_REPO,
             "absolute temperature; the only scale allowed inside an Arrhenius term (G24.3)"),
        _row("KU-011", "degC", "°C|deg C|celsius", "KINETIC", "TEMPERATURE", "K", None,
             "AFFINE: K = degC + 273.15 exactly (offset 27315/100)", False, _SRC_REPO,
             "affine scale: no multiplicative factor; convert with to_kelvin"),
    ]
    for r in rows:
        try:
            U.parse_unit(r["canonical_name"])
            r["units_py_parses"] = "YES"
        except U.UnitError:
            r["units_py_parses"] = "NO"
    return rows


def csv_text(rows: list[dict[str, str]] | None = None) -> str:
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=COLUMNS, lineterminator="\n")
    w.writeheader()
    w.writerows(rows if rows is not None else build_rows())
    return buf.getvalue()


def write_csv(path: Path = CSV_PATH) -> str:
    text = csv_text()
    path.write_text(text, encoding="utf-8")
    return text


def read_rows(path: Path = CSV_PATH) -> list[dict[str, str]]:
    with Path(path).open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


# ----------------------------------------------------------------------------- resolution
@dataclass(frozen=True)
class Resolution:
    verdict: str                    # CONSISTENT | UNKNOWN | INCONSISTENT
    unit: str | None                # canonical name
    dimension: U.Dimension | None
    factor_to_si: Fraction | None   # exact; None when affine or ambiguous
    affine: bool
    detail: str = ""


def _index(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    idx: dict[str, dict[str, str]] = {}
    for r in rows:
        for name in [r["canonical_name"], *[a for a in r["aliases"].split("|") if a]]:
            if idx.setdefault(name, r) is not r:
                raise ValueError(f"alias {name!r} is claimed by two rows")
    return idx


def resolve(unit: str | None, *, calorie: str | None = None, rows: list[dict[str, str]] | None = None) -> Resolution:
    """Registry resolution of a raw unit string. Missing / unknown strings are UNKNOWN, never a default unit."""
    if calorie is not None and calorie not in CALORIES:
        raise ValueError(f"calorie must be one of {CALORIES} or None")
    if unit is None or not str(unit).strip() or unit == "UNKNOWN":
        return Resolution(U.UNKNOWN, None, None, None, False, "UNIT_MISSING")
    idx = _index(rows if rows is not None else read_rows())
    row = idx.get(str(unit).strip())
    if row is None:
        return Resolution(U.UNKNOWN, None, None, None, False, f"UNIT_NOT_IN_KINETIC_REGISTRY {unit!r}")
    if row["canonical_name"] == "kcal/mol":
        if calorie is None:
            return Resolution(U.UNKNOWN, "kcal/mol", U.dimension(row["dimension_expr"]), None, False,
                              "CALORIE_CONVENTION_UNDECLARED")
        row = idx[f"kcal_{'th' if calorie == 'TH' else 'IT'}/mol"]
    dim = U.dimension(row["dimension_expr"])
    if row["si_factor_exact"] == "":
        return Resolution(U.CONSISTENT, row["canonical_name"], dim, None, True, "AFFINE")
    num, den = row["si_factor_exact"].split("/")
    return Resolution(U.CONSISTENT, row["canonical_name"], dim, Fraction(int(num), int(den)), False)


def to_kelvin(value: float | Fraction, unit: str) -> Fraction:
    """Exact: K = degC + 273.15 (offset 27315/100); K stays K. Anything else is refused."""
    v = Fraction(value)
    if unit in ("K", "kelvin"):
        return v
    if unit in ("degC", "°C", "deg C", "celsius"):
        return v + Fraction(27315, 100)
    raise ValueError(f"not a temperature unit: {unit!r}")


def to_si(value: float | Fraction, unit: str, *, calorie: str | None = None) -> Fraction | None:
    """Exact SI value (Fraction) of a kinetic quantity, or None when no exact factor exists (UNKNOWN calorie, affine)."""
    r = resolve(unit, calorie=calorie)
    if r.verdict != U.CONSISTENT or r.factor_to_si is None:
        return None
    return Fraction(value) * r.factor_to_si


def check_rows(rows: list[dict[str, str]] | None = None) -> list[str]:
    """Self-consistency problems: factors agree with ``units.py`` wherever it can parse the unit, ids unique."""
    rows = rows if rows is not None else read_rows()
    out: list[str] = []
    keys = [r["proposed_key"] for r in rows]
    if len(set(keys)) != len(keys):
        out.append("DUPLICATE_KEY")
    try:
        _index(rows)
    except ValueError as exc:
        out.append(f"ALIAS_CLAIMED_TWICE {exc}")
    for r in rows:
        dim = U.dimension(r["dimension_expr"])
        if r["si_factor_exact"]:
            num, den = r["si_factor_exact"].split("/")
            exact = Fraction(int(num), int(den))
            if r["si_factor_float"] != repr(float(exact)):
                out.append(f"{r['proposed_key']}:FLOAT_NOT_FROM_EXACT")
        else:
            exact = None
        try:
            p = U.parse_unit(r["canonical_name"])
        except U.UnitError:
            continue
        if p.dimension != dim:
            out.append(f"{r['proposed_key']}:DIMENSION_DISAGREES_WITH_UNITS_PY")
        if not p.affine and exact is not None and p.factor_to_si != exact:
            out.append(f"{r['proposed_key']}:FACTOR_DISAGREES_WITH_UNITS_PY {p.factor_to_si} vs {exact}")
    return out


# ----------------------------------------------------------------------------- PARAM wiring
def param_unit_issues(param: Mapping[str, Any], slot_dimension: str | U.Dimension, *,
                      calorie: str | None = None) -> list[str]:
    """Codes for a PARAM record whose unit does not resolve in the registry (or units.py) with the slot's dimension.

    Checked: ``value.unit`` (when the value is numeric) against ``slot_dimension`` and ``T_ref.unit`` against TEMPERATURE
    (Kelvin only: PARAM_T_REF_NOT_KELVIN). An UNKNOWN value has no unit to resolve and raises no issue here.
    """
    want = slot_dimension if isinstance(slot_dimension, U.Dimension) else U.dimension(slot_dimension)
    out: list[str] = []
    value = param.get("value") or {}
    if value.get("status") in ("MEASURED", "RANGE"):
        unit = value.get("unit")
        r = resolve(unit, calorie=calorie)
        if r.verdict != U.CONSISTENT:
            chk = U.check_unit(unit, want)
            undeclared = U.undeclared_concentration_tokens(unit)     # S159 R1: "mg/g/min" must not pass as a rate unit
            if chk.verdict == U.CONSISTENT and undeclared and not ({"MASS", "AMOUNT", "LENGTH"}
                                                                   & {k for k, _ in want.exponents}):
                r = Resolution(U.UNKNOWN, None, None, None, False, f"CONCENTRATION_TOKENS_UNDECLARED {list(undeclared)}")
            elif chk.verdict == U.CONSISTENT:
                r = Resolution(U.CONSISTENT, unit, want, None, False, "UNITS_PY_GRAMMAR")
        if r.verdict != U.CONSISTENT:
            out.append(f"PARAM_UNIT_UNRESOLVED:{r.detail}")
        elif r.dimension != want:
            out.append(f"PARAM_UNIT_DIMENSION:{unit!r} is {r.dimension}, slot wants {want}")
    t_ref = param.get("T_ref")
    if isinstance(t_ref, Mapping) and t_ref.get("status") in ("MEASURED", "RANGE"):
        r = resolve(t_ref.get("unit"))
        if r.verdict != U.CONSISTENT or r.affine or r.dimension != U.dimension("TEMPERATURE"):
            out.append("PARAM_T_REF_NOT_KELVIN")
    return out


# ----------------------------------------------------------------------------- UNIT-ledger projection (not written)
def unit_records(start_number: int, *, rows: list[dict[str, str]] | None = None,
                 created_at: str = "2026-11-09T00:00:00+00:00", created_by: str = "AI_AGENT:aa-fit-sim:S178",
                 ids: list[str] | None = None) -> list[dict[str, Any]]:
    """UNIT-schema records for the kinetic rows; ids start at UNIT-<start_number> unless ``ids`` gives minted ids.

    A defined conversion factor is not a measurement, so it is carried only as ``external_refs`` ``si_factor_exact``
    (never as a MEASURED QVALUE). Rows whose factor is agent-recalled (the calorie rows) are NEEDS_SOURCE; the plain
    ``kcal/mol`` row has no factor at all. Nothing is appended anywhere by this function."""
    dim_map = {"TIME^-1": "RATE_PER_TIME", "ENERGY*AMOUNT^-1": "ENERGY_PER_AMOUNT", "TEMPERATURE": "TEMPERATURE"}
    src = rows if rows is not None else read_rows()
    if ids is not None and len(ids) != len(src):
        raise ValueError("one id per row")
    out = []
    for i, r in enumerate(src):
        needs = r["needs_source"] == "True"
        out.append({
            "id": ids[i] if ids is not None else f"UNIT-{start_number + i:06d}", "record_type": "UNIT",
            "schema_version": "1.0.0", "version": 1, "status": "ACTIVE", "created_at": created_at,
            "created_by": created_by,
            "provenance": {"method": "DERIVED", "source_ids": [], "agent": "kinetic_unit_registry@0.2",
                           "locator": r["proposed_key"], "notes": r["source_status"]},
            "verification": {"status": "NEEDS_SOURCE" if needs else "UNVERIFIED"},
            "canonical_name": r["canonical_name"],
            "aliases": [a for a in r["aliases"].split("|") if a], "unit_type": "KINETIC",
            "dimension": dim_map[r["dimension_expr"]], "si_unit": r["si_unit"], "conventions": [],
            "external_refs": [f"si_factor_exact:{r['si_factor_exact']}"] if r["si_factor_exact"] else [],
            "ambiguity_notes": r["convention"] or None})
    return out


def ledger_unit_ids(path: Path = LEDGER_PATH) -> dict[str, str]:
    """canonical_name -> UNIT id for the ACTIVE KINETIC rows of the UNIT ledger (latest version per id)."""
    latest: dict[str, dict[str, Any]] = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.strip():
            rec = json.loads(line)
            latest[rec["id"]] = rec
    return {r["canonical_name"]: rid for rid, r in latest.items()
            if r.get("unit_type") == "KINETIC" and r.get("status") == "ACTIVE"}
