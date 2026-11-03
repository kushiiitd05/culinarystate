"""Read-only, counts-only dry-run of the opt-in rc2 grounding pipeline (S154).

Consumes recipe records ({recipe_id, source_family, ingredient_lines}) from an
iterator, grounds every nonblank ingredient line with ``ground_quantity_rc2``
and aggregates integer counts by status/flag/issue code. Nothing per line or
per recipe is kept: no recipe text, recipe id, unit token or exception message
can reach the report, and ``assert_counts_only`` rejects any free-text string.

Locale comes from the legacy source-family map used to build the recipe base
(``recipes.ledgers.LOCALE``: BBC=UK, Food.com=US, others unknown). No POR
records and no ingredient links are supplied, so every volume/count line stays
without grams by construction; the report says so instead of implying a gap.
This is engineering coverage evidence, not a human-verified quality estimate.
"""
from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from multiprocessing import get_context
from pathlib import Path
from typing import Iterable, Mapping

from culinarystate.recipes.ledgers import LOCALE

from .parse_adapter import ADAPTER_VERSION
from .rc2_grounding import PIPELINE_VERSION, GroundingContext, ground_quantity_rc2
from .versioned_normalizer import NORMALIZER_VERSION

REPORT_VERSION = "STEP16_RC2_GROUNDING_DRYRUN_V1"
SOURCE_META = {"origin": "EXPLICIT_SOURCE", "status": "KNOWN", "claim_route": "EXPLICIT"}
LOCALE_META = {"origin": "DERIVED_DETERMINISTIC", "status": "KNOWN", "claim_route": "INFERRED_RULE",
               "evidence_refs": ["LEGACY_SOURCE_FAMILY_LOCALE_MAP"]}
_KNOWN_LOWER_FLAGS = {"locale_ambiguous", "contradictory_stated_mass", "alt_unit_disagrees",
                      "non_standard_vessel", "qualitative", "second_unit_ignored"}
_CODE = re.compile(r"^[A-Za-z0-9_]{1,80}$")
_VALUE = re.compile(r"^[A-Za-z0-9_.:/|-]{1,120}$")
_AXES = ("mass_route", "unit_resolution", "ast_root", "arithmetic_status", "q_level", "flags",
         "issue_codes", "legacy_vs_rc2_mass", "exceptions")
_PROTECTED = (("ledgers",), ("data",), ("exports",), ("annotation", "gold"))


class DryRunError(RuntimeError):
    """Unsafe output destination or a report that is not counts-only."""


def flag_code(flag: str) -> str:
    head = str(flag).split(":", 1)[0]
    if re.fullmatch(r"[A-Z0-9_]{1,80}", head) or head in _KNOWN_LOWER_FLAGS:
        return head
    return "OTHER_FLAG"


def _empty():
    return {"recipes": 0, "recipes_without_ingredient_lines": 0, "lines_total": 0, "lines_blank": 0,
            "lines_grounded": 0, "lines_contract_valid": 0, "lines_with_rc2_mass": 0,
            "lines_with_rc2_volume": 0, "lines_with_rc2_count": 0, "lines_flagged": 0,
            **{axis: Counter() for axis in _AXES}}


def _merge(into, other):
    for key, value in other.items():
        if isinstance(value, Counter):
            into[key].update(value)
        else:
            into[key] += value


_SCHEMA = None


def _init(schema):
    global _SCHEMA
    _SCHEMA = schema


def _count_recipe(item):
    family, lines = item
    out = _empty()
    out["recipes"] = 1
    if not lines:
        out["recipes_without_ingredient_lines"] = 1
    locale = LOCALE.get(family)
    context = GroundingContext(source_metadata=SOURCE_META, locale=locale,
                               locale_metadata=LOCALE_META if locale else None)
    for line in lines:
        out["lines_total"] += 1
        if not isinstance(line, str) or not line.strip():
            out["lines_blank"] += 1
            continue
        try:
            r = ground_quantity_rc2(line, context, schema=_SCHEMA)
        except Exception as exc:  # counted by class name only; message may contain text
            out["exceptions"][type(exc).__name__] += 1
            continue
        out["lines_grounded"] += 1
        out["mass_route"][r.mass_route] += 1
        out["unit_resolution"][r.unit_resolution] += 1
        out["ast_root"][r.ast_root] += 1
        out["arithmetic_status"][r.arithmetic_status] += 1
        out["q_level"][r.record["q_level"]] += 1
        for code in dict.fromkeys(flag_code(f) for f in r.flags):
            out["flags"][code] += 1
        for code in dict.fromkeys(i.code for i in r.issues):
            out["issue_codes"][flag_code(code)] += 1
        rc2 = r.record["mass_g"]["status"]
        out["legacy_vs_rc2_mass"][f"legacy_{r.compatibility_mass_status}__rc2_{rc2}"] += 1
        out["lines_contract_valid"] += not r.issues
        out["lines_flagged"] += bool(r.flags)
        out["lines_with_rc2_mass"] += rc2 != "UNKNOWN"
        out["lines_with_rc2_volume"] += r.record["volume_ml"]["status"] != "UNKNOWN"
        out["lines_with_rc2_count"] += r.record["count"]["status"] != "UNKNOWN"
    return family, out


def _items(records: Iterable[Mapping], limit):
    for n, rec in enumerate(records):
        if limit is not None and n >= limit:
            return
        yield str(rec.get("source_family")), list(rec.get("ingredient_lines") or [])


def _plain(acc):
    return {k: dict(sorted(v.items())) if isinstance(v, Counter) else v for k, v in acc.items()}


def summarise(records: Iterable[Mapping], *, schema: Mapping | None = None, workers: int = 1,
              chunk_size: int = 200, limit: int | None = None) -> dict:
    """Aggregate counts for the given records; the iterator is consumed once, read-only."""
    if schema is None:
        schema = load_schema()
    totals, by_family = _empty(), {}
    items = _items(records, limit)
    if workers <= 1:
        _init(schema)
        results = map(_count_recipe, items)
        pool = None
    else:
        pool = get_context("spawn").Pool(workers, initializer=_init, initargs=(schema,))
        results = pool.imap(_count_recipe, items, chunksize=chunk_size)
    try:
        for family, counts in results:
            _merge(totals, counts)
            _merge(by_family.setdefault(family, _empty()), counts)
    finally:
        if pool is not None:
            pool.close()
            pool.join()
    report = {
        "report_version": REPORT_VERSION, "pipeline_version": PIPELINE_VERSION,
        "adapter_version": ADAPTER_VERSION, "normalizer_version": NORMALIZER_VERSION,
        "schema_sha256": hashlib.sha256(json.dumps(schema, sort_keys=True).encode()).hexdigest(),
        "status": "AI_ENGINEERING_DRY_RUN_COUNTS_ONLY", "contains_recipe_text": False,
        "contains_recipe_ids": False, "counts_as_human_gate": False, "por_records_supplied": 0,
        "ingredient_links_supplied": False, "locale_source": "LEGACY_SOURCE_FAMILY_LOCALE_MAP",
        "totals": _plain(totals), "by_family": {k: _plain(v) for k, v in sorted(by_family.items())},
    }
    assert_counts_only(report)
    return report


def load_schema(root: Path | None = None) -> dict:
    root = root or Path(__file__).resolve().parents[3]
    return json.loads((root / "reports/step16/schema_drafts/QNT.draft_v2.schema.json").read_text(encoding="utf-8"))


def assert_counts_only(obj, path="") -> None:
    """Raise DryRunError unless every key is a code and every string a short code-like token."""
    if isinstance(obj, Mapping):
        for key, value in obj.items():
            if not isinstance(key, str) or not _CODE.match(key):
                raise DryRunError(f"non-code key at {path or '/'}")
            assert_counts_only(value, f"{path}/{key}")
    elif isinstance(obj, (list, tuple)):
        for i, value in enumerate(obj):
            assert_counts_only(value, f"{path}/{i}")
    elif isinstance(obj, str):
        if not _VALUE.match(obj):
            raise DryRunError(f"non-code string at {path}")
    elif obj is not None and not isinstance(obj, (bool, int, float)):
        raise DryRunError(f"unsupported value type at {path}")


def write_report(path: Path, report: Mapping, *, root: Path) -> None:
    """Write a new counts-only JSON file outside protected/raw-data areas; never overwrite."""
    assert_counts_only(report)
    target, base = Path(path).resolve(), Path(root).resolve()
    try:
        parts = target.relative_to(base).parts
    except ValueError:
        parts = ()
    if any(parts[:len(p)] == p for p in _PROTECTED):
        raise DryRunError("refusing to write inside ledgers/, data/, exports/ or annotation/gold/")
    if target.exists():
        raise DryRunError("refusing to overwrite an existing report")
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "x", encoding="utf-8") as fh:
        fh.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
