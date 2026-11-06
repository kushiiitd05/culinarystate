"""Step 26g simulability census over real recipes, counts only (S166; review block J8). DRAFT_PENDING_16c_23a_26b.

Chain per recipe: Rung A -> event adapter -> replay -> ``build_simulation_inputs`` (no condition or
applicability bindings exist yet, so every event stays SIM_PROHIBITED) -> ``simulability_census``.
Recipes are sampled exactly as the Step 17b dry-run does (smallest sha256(seed || recipe_id)). Recipe ids
and text stay in memory; the report holds integer counts, codes and hashes only. Not a gold score and not a
human gate. Replaces the ad hoc chain behind reports/step26/simulability_census_real_sample_counts.json.
"""
from __future__ import annotations

import hashlib
from collections import Counter
from typing import Iterable, Iterator, Mapping

from culinarystate.extraction.interfaces import SourceText
from culinarystate.extraction.rung_a import RungA
from culinarystate.extraction.rung_a_measure import code, seeded_sample
from culinarystate.quantity import rc2_dryrun as D
from culinarystate.recipes.ledgers import LOCALE
from culinarystate.simulation.recipe_adapter import (SYSTEM_REQUIREMENTS, build_simulation_inputs, census_sha256,
                                                      simulability_census)
from culinarystate.state_graph.event_adapter import adapt_event_graph

CHAIN_VERSION = "step26g-census-chain-0.1.0-draft"


def _steps(rec: Mapping) -> list[str]:
    return [str(s) for s in rec.get("steps") or [] if isinstance(s, str) and s.strip()]


def census_from_records(records: Iterable[Mapping], *, seed: str, size: int = 1000, system_id: str = "sim_aa_1",
                        rung: RungA | None = None, schema: Mapping | None = None) -> dict:
    """Counts-only census report for the seeded sample (one SimulationInputSet per recipe with steps)."""
    if system_id not in SYSTEM_REQUIREMENTS:
        raise ValueError(f"system_id must be one of {tuple(SYSTEM_REQUIREMENTS)}")
    rung = rung or RungA()
    schema = schema or D.load_schema()
    seen = 0

    def counted(it: Iterable[Mapping]) -> Iterator[Mapping]:
        nonlocal seen
        for rec in it:
            seen += 1
            yield rec

    sample = seeded_sample(counted(records), seed, size)
    totals = Counter()
    issues: Counter = Counter()
    exceptions: Counter = Counter()

    def sets():
        for rec in sample:
            steps = _steps(rec)
            if not steps:
                continue
            totals["texts_with_steps"] += 1
            try:
                source = SourceText.from_raw("COUNTS", "\n".join(steps))
                res = rung.run(source, rung.config(locale=LOCALE.get(rec.get("source_family"))), schema=schema)
                adapted = adapt_event_graph(source, res.graph, groundings=res.quantities,
                                            recomputers=rung.recomputers())
                built = build_simulation_inputs(adapted.replay(), recipe_id=rec["recipe_id"], system_id=system_id)
            except Exception as exc:  # noqa: BLE001 - counted by class name; the message may contain text
                exceptions[code(type(exc).__name__)] += 1
                continue
            totals["engine_events"] += len(adapted.events)
            totals["adapter_invented_excluded"] += adapted.invented_count
            issues.update(code(i.code) for i in adapted.issues)
            yield built

    census = simulability_census(sets())
    report = {
        "status": "AI_ENGINEERING_DRY_RUN_COUNTS_ONLY", "label": "REAL_BASE_SAMPLE_COUNTS_NOT_GOLD",
        # Parv's ad hoc file wrote "RungA->event_adapter->replay->26g(sim_aa_1)", which fails the counts-only guard
        "chain": f"RUNG_A|EVENT_ADAPTER|REPLAY|STEP26G:{system_id}", "chain_version": CHAIN_VERSION,
        "contains_ids": False, "contains_text": False, "counts_as_human_gate": False,
        "seed_sha256": hashlib.sha256(seed.encode("utf-8")).hexdigest(),
        "sample_rule": "SHA256_SEED_CONCAT_RECIPE_ID_ASC", "sample_size_requested": int(size),
        "recipes_seen": seen, "recipes_sampled": len(sample), "texts_with_steps": totals["texts_with_steps"],
        "engine_events": totals["engine_events"], "adapter_invented_excluded": totals["adapter_invented_excluded"],
        "adapter_issue_codes": dict(sorted(issues.items())), "exceptions_by_class": dict(sorted(exceptions.items())),
        # ksh review K7: the all-SIM_PROHIBITED result is structural, not a finding about the corpus
        "bindings_supplied": 0, "applicability_supplied": 0, "prohibited_by_construction": True,
        "reading": "NO_CONDITION_OR_APPLICABILITY_BINDINGS_YET_ALL_EVENTS_SIM_PROHIBITED_BY_CONSTRUCTION",
        "census": census, "census_sha256": census_sha256(census),
    }
    D.assert_counts_only(report)
    return report
