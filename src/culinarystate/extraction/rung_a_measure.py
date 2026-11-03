"""Step 17b Rung A counts-only measurement (DRAFT_PENDING_16c).

Runs Rung A, the 17a validators V1-V4 and the invented-value auditor (with Rung A's
registered recomputers) and aggregates integer counts by code only: mention labels,
link / grounding / reference outcomes and failure codes, validator issue / unknown /
not-checked codes, invented values, rule-fired flags and the ambiguity count. No
text, recipe id, span or value can reach a report: every key is a fixed code and
``rc2_dryrun.assert_counts_only`` is applied to every report.

Two inputs exist: (1) ``synthetic_report`` over ``SYNTHETIC_FIXTURES`` and the 17
synthetic hard-case prompts (read-only; their blank outcomes are never filled),
labelled SYNTHETIC_NOT_GOLD; (2) ``summarise_records`` over a seeded sample of
recipe records (rank = sha256(seed || recipe_id), ties by id, as in
``annotation.pilot_real``), used by ``tools/step17b_rung_a_dryrun.py``. Neither is a
quality estimate, a gold score or a human gate.
"""
from __future__ import annotations

import hashlib
import heapq
import json
import re
from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, Mapping

from culinarystate.quantity import rc2_dryrun as D
from culinarystate.recipes.ledgers import LOCALE
from culinarystate.state_graph.rule_compiler import compile_recipe

from .auditor import AUDITOR_VERSION, audit_outputs
from .interfaces import INTERFACE_SCHEMA_VERSION, SourceText
from .invariants import run_validators
from .rung_a import RULES_VERSION, RUNG_A_LABELS, RungA
from .rung_a_lexicon import LEXICON_VERSION
from .validators import load_draft_vocabularies

STATUS = "DRAFT_PENDING_16c"
REPORT_VERSION = "STEP17B_RUNG_A_COUNTS_V1_DRAFT"
CATALOG = Path("annotation") / "hard_case_catalog_v2_DRAFT.jsonl"
VALIDATORS = ("V1", "V2", "V3", "V4")
FAILURE_STAGES = ("extract_mentions", "link", "ground_quantity", "build_events", "resolve_refs")
_CODE = re.compile(r"[^A-Za-z0-9_]")

SYNTHETIC_FIXTURES: tuple[str, ...] = (
    "Heat the oil in a frying pan over medium heat. Add 200 g onion and fry for 5-6 minutes until golden. "
    "Stir in the garlic, then pour in 2 tbsp water. Bake at 180°C for 20 minutes.",
    "Mix the flour with the butter into a dough. Divide the dough into 4 balls.",
    "Reserve half of the stock. Stir it into the sauce.",
    "Place the chicken beside the potatoes. Roast them for 1-2 hours at 200°C.",
    "Add the salt if desired. Discard the bay leaf.",
    "Simmer for 1 1/2 hours, then rest for 10 mins.",
    "Hold at 20 C for 2 min.",
    "Whisk the eggs gently until frothy. Fold in the sugar.",
    "Do not stir the caramel. Pour it over the cake.",
    "Freeze at -18°C for 3 days.",
    "Bring 500 ml water to the boil. Add 2 x 400g cans tomatoes.",
    "Place the bread beside the cheese. Slice it.",
    "",
)


def code(token: Any) -> str:
    """A report key: a fixed code with separators folded to ``__`` (never free text)."""
    out = _CODE.sub("__", str(token))[:80]
    return out if out else "EMPTY"


def empty() -> dict:
    return {"texts": 0, "texts_empty": 0, "texts_with_events": 0, "texts_with_invented": 0, "events": 0,
            "invented_count": 0, "values_checked": 0, "ambiguity_count": 0, "mentions": Counter(),
            "links": Counter(), "quantities": Counter(), "references": Counter(), "entities": Counter(),
            "allocations": Counter(), "invented_by_code": Counter(), "diagnostics": Counter(),
            "exceptions": Counter(),
            "failures": {s: Counter() for s in FAILURE_STAGES},
            "validators": {v: {"issues": Counter(), "unknown": Counter(), "not_checked": Counter(),
                               "texts_failed": 0} for v in VALIDATORS}}


def merge(into: dict, other: Mapping) -> dict:
    for key, value in other.items():
        if isinstance(value, Counter):
            into[key].update(value)
        elif isinstance(value, dict):
            merge(into[key], value)
        else:
            into[key] += value
    return into


def plain(obj: Any) -> Any:
    if isinstance(obj, Counter):
        return {k: int(v) for k, v in sorted(obj.items())}
    if isinstance(obj, dict):
        return {k: plain(v) for k, v in obj.items()}
    return obj


def _fail(out: dict, stage: str, failure: Any) -> None:
    out["failures"][stage][code(failure.code.value)] += 1


@lru_cache(maxsize=1)
def _vocabularies() -> Mapping:
    return load_draft_vocabularies()


def count_text(rung: RungA, raw: str, *, schema: Mapping, locale: str | None = None) -> dict:
    """Counts for one instruction text (an exception is counted by class name only)."""
    out = empty()
    out["texts"] = 1
    out["texts_empty"] = int(not raw.strip())
    try:
        source = SourceText.from_raw("COUNTS", raw)
        res = rung.run(source, rung.config(locale=locale), schema=schema)
        outputs = res.all()
        reports = run_validators(source, outputs, qnt_schema=schema, vocabularies=_vocabularies(),
                                 mention_labels=RUNG_A_LABELS, id_sets=rung.lexicon.id_sets())
        audit = audit_outputs(source, outputs, recomputers=rung.recomputers())
    except Exception as exc:  # noqa: BLE001 - counted by class name; the message may contain text
        out["exceptions"][code(type(exc).__name__)] += 1
        return out
    out["mentions"].update(code(m.label) for m in res.mentions.mentions)
    if res.mentions.failure is not None:
        _fail(out, "extract_mentions", res.mentions.failure)
    for lr in res.links:
        out["links"]["SELECTED" if lr.failure is None else code(lr.failure.reason)] += 1
        if lr.failure is not None:
            _fail(out, "link", lr.failure)
    for q in res.quantities:
        out["quantities"]["MASS_GROUNDED" if q.failure is None else code(q.failure.reason)] += 1
        if q.failure is not None:
            _fail(out, "ground_quantity", q.failure)
    for r in res.refs:
        out["references"]["RESOLVED" if r.failure is None else code(r.failure.reason)] += 1
        if r.failure is not None:
            _fail(out, "resolve_refs", r.failure)
    g = res.graph
    if g.failure is not None:
        _fail(out, "build_events", g.failure)
    out["events"] = len(g.events)
    out["texts_with_events"] = int(bool(g.events))
    out["entities"].update(code(n.entity_type) for n in g.entities)
    out["allocations"].update(code(a.kind) for a in g.allocations)
    flags = [*res.mentions.diagnostics, *g.diagnostics]
    out["diagnostics"].update(code(f) for f in flags)
    out["ambiguity_count"] = (sum(1 for f in flags if f.startswith("AMBIGUOUS_") or f == "IMPLICIT_ARG_AMBIGUOUS")
                              + sum(1 for lr in res.links if lr.failure is not None
                                    and lr.failure.reason == "AMBIGUOUS_CANDIDATES"))
    for v, rep in reports.items():
        slot = out["validators"][v]
        slot["issues"].update(code(i.code) for i in rep.issues)
        slot["unknown"].update(code(i.code) for i in rep.unknown)
        slot["not_checked"].update(code(n) for n in rep.not_checked)
        slot["texts_failed"] = int(bool(rep.issues))
    out["invented_count"] = audit.invented_count
    out["values_checked"] = audit.values_checked
    out["texts_with_invented"] = int(audit.invented_count > 0)
    out["invented_by_code"].update({code(k): v for k, v in audit.invented_by_code.items()})
    return out


def summarise_texts(texts: Iterable[str], *, rung: RungA | None = None, schema: Mapping | None = None,
                    locale: str | None = None) -> dict:
    rung = rung or RungA()
    schema = schema or D.load_schema()
    total = empty()
    for raw in texts:
        merge(total, count_text(rung, raw, schema=schema, locale=locale))
    return plain(total)


def _header(rung: RungA, schema: Mapping) -> dict:
    return {"report_version": REPORT_VERSION, "rules_version": RULES_VERSION, "lexicon_version": LEXICON_VERSION,
            "lexicon_fingerprint": rung.lexicon.fingerprint, "interface_schema_version": INTERFACE_SCHEMA_VERSION,
            "auditor_version": AUDITOR_VERSION,
            "schema_sha256": hashlib.sha256(json.dumps(schema, sort_keys=True).encode()).hexdigest(),
            "contains_text": False, "contains_ids": False, "counts_as_human_gate": False}


def hard_case_prompts(root: Path | None = None) -> list[str]:
    """Prompts of the synthetic hard-case catalog (read-only; outcomes are never read or filled)."""
    path = Path(root or Path(__file__).resolve().parents[3]) / CATALOG
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line)["prompt"] for line in fh if line.strip()]


def synthetic_report(root: Path | None = None, *, rung: RungA | None = None) -> dict:
    """SYNTHETIC_NOT_GOLD counts over the synthetic fixtures and the 17 hard-case prompts."""
    rung = rung or RungA()
    schema = D.load_schema(root)
    report = {**_header(rung, schema), "label": "SYNTHETIC_NOT_GOLD", "status": "AI_ENGINEERING_SYNTHETIC_COUNTS",
              "fixtures": summarise_texts(SYNTHETIC_FIXTURES, rung=rung, schema=schema),
              "hard_cases": summarise_texts(hard_case_prompts(root), rung=rung, schema=schema)}
    D.assert_counts_only(report)
    return report


# ------------------------------------------------------------------ seeded real-base sample
def rank(seed: str, recipe_id: str) -> str:
    return hashlib.sha256(seed.encode("utf-8") + recipe_id.encode("utf-8")).hexdigest()


def seeded_sample(records: Iterable[Mapping], seed: str, size: int = 1000) -> list[Mapping]:
    """The ``size`` records with the smallest sha256(seed || recipe_id) (ties by id); O(size) memory."""
    keyed = ((rank(seed, rec["recipe_id"]), rec["recipe_id"], n, rec) for n, rec in enumerate(records)
             if isinstance(rec.get("recipe_id"), str) and rec["recipe_id"])
    return [item[3] for item in heapq.nsmallest(size, keyed, key=lambda item: item[:3])]


def _floor(rec: Mapping, out: Counter) -> None:
    """Retained negative floor: the existing rule compiler over the same record (event counts by type)."""
    try:
        events = compile_recipe(list(rec.get("ingredient_lines") or []), [str(s) for s in rec.get("steps") or []])
    except Exception as exc:  # noqa: BLE001 - counted by class name only
        out[f"exception_{code(type(exc).__name__)}"] += 1
        return
    out["events"] += len(events)
    out.update(f"event_{code(type(e).__name__)}" for e in events)


def summarise_records(records: Iterable[Mapping], *, seed: str, size: int = 1000, rung: RungA | None = None,
                      schema: Mapping | None = None) -> dict:
    """Counts-only summary of Rung A over a seeded sample (read-only; nothing per recipe is kept)."""
    rung = rung or RungA()
    schema = schema or D.load_schema()
    seen = 0

    def counted(it: Iterable[Mapping]) -> Iterable[Mapping]:
        nonlocal seen
        for rec in it:
            seen += 1
            yield rec

    sample = seeded_sample(counted(records), seed, size)
    totals = {**empty(), "recipes_sampled": 0, "recipes_with_steps": 0, "recipes_without_steps": 0,
              "rule_compiler_floor": Counter({"events": 0})}
    by_family: dict[str, dict] = {}
    for rec in sample:
        family = code(rec.get("source_family"))
        steps = [str(s) for s in rec.get("steps") or [] if isinstance(s, str) and s.strip()]
        part = {**empty(), "recipes_sampled": 1, "recipes_with_steps": int(bool(steps)),
                "recipes_without_steps": int(not steps), "rule_compiler_floor": Counter({"events": 0})}
        if steps:
            merge(part, count_text(rung, "\n".join(steps), schema=schema, locale=LOCALE.get(rec.get("source_family"))))
        _floor(rec, part["rule_compiler_floor"])
        merge(totals, part)
        merge(by_family.setdefault(family, {**empty(), "recipes_sampled": 0, "recipes_with_steps": 0,
                                            "recipes_without_steps": 0,
                                            "rule_compiler_floor": Counter({"events": 0})}), part)
    totals["recipes_seen"] = seen
    report = {**_header(rung, schema), "status": "AI_ENGINEERING_DRY_RUN_COUNTS_ONLY",
              "label": "REAL_BASE_SAMPLE_COUNTS_NOT_GOLD", "sample_size_requested": int(size),
              "sample_seed_sha256": hashlib.sha256(seed.encode("utf-8")).hexdigest(),
              "sample_rule": "SHA256_SEED_CONCAT_RECIPE_ID_ASC", "locale_source": "LEGACY_SOURCE_FAMILY_LOCALE_MAP",
              "totals": plain(totals), "by_family": {k: plain(v) for k, v in sorted(by_family.items())}}
    D.assert_counts_only(report)
    return report
