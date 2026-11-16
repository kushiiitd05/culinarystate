"""Seal the step-7 hard-case set and record the deterministic baseline (freeze step 7, part 1).

Selects recipes where a Layer-1 ambiguity trigger fires, stratified by trigger, ranked inside each
stratum by ``sha256(seed || pageid)`` so the choice is reproducible and fixed before any model runs.

Source is **Wikibooks only** (CC-BY, public, citable by pageid/revid/url). No BBC or other
third-party raw text enters this set, because the hosted comparison sends the case text to an
external API and only public or self-written text may go there.

Two outputs:
  * the packet (``data/interim/s180_hardcases/…jsonl``, git-ignored) — holds the case text;
  * the manifest (``reports/s180/…json``, committed) — counts, seed, quotas, per-case pageid /
    revid / url / triggers, the deterministic baseline, and the packet's SHA-256. No step text.

The manifest is committed **before** any model is run. After that, nothing in the selection may
change: a change is a dated amendment committed before the first model result, or the attempt is void.

Usage:
  python tools/s180_seal_hardcases.py --n 60 --out reports/s180/hardcase_seal_2026-11-15.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
RECIPES = ROOT / "data/interim/wikibooks/recipes.jsonl"
PACKET_DIR = ROOT / "data/interim/s180_hardcases"
SEED = "s180-layer1-hardcases-2026-11-15"
#: Quota per primary trigger. Shares sum to 1.0; the last stratum absorbs the rounding remainder.
QUOTAS = {
    "VNEXT_MIXTURE_COREF": 0.25,
    "VNEXT_ALTERNATIVE_SKIPPED": 0.25,
    "AMBIGUOUS_REFERENCE": 0.20,
    "VNEXT_FAT_STAYS": 0.15,
    "UNRESOLVED_LOT": 0.15,
}
LABELS = ("DETERMINISTIC_BASELINE_RULES_ONLY", "WIKIBOOKS_CC_BY_PUBLIC_TEXT_ONLY",
          "SEALED_BEFORE_ANY_MODEL_RUN", "NO_GOLD_SO_AGREEMENT_IS_DIAGNOSTIC")


def rank_key(pageid: str) -> str:
    return hashlib.sha256(f"{SEED}‖{pageid}".encode()).hexdigest()


def steps_text(record: dict) -> str:
    steps = record.get("steps") or []
    if isinstance(steps, str):
        steps = json.loads(steps.replace("'", '"')) if steps.startswith("[") else []
    out = [s.get("text", "") for s in steps if isinstance(s, dict) and s.get("text")]
    return "\n".join(out)


def load_recipes() -> list[dict]:
    with RECIPES.open(encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def build_env():
    from culinarystate.extraction.rung_a import RungA
    from culinarystate.quantity.rc2_dryrun import load_schema
    return RungA(coord_food_guard=True, lineage_vnext=True), load_schema()


def scan(record: dict, rung, schema) -> dict | None:
    """Parse one recipe with rules only. Returns a case when a trigger fires, else None."""
    from culinarystate.composition import layer1_proposer as L1
    from culinarystate.extraction.interfaces import SourceText

    raw = steps_text(record)
    if not raw.strip():
        return None
    out = rung.run(SourceText.from_raw(f"WB-{record['pageid']}", raw), rung.config(), schema=schema)
    graph = out.graph
    flags = tuple(str(f) for f in (graph.diagnostics or ()))
    triggers = L1.triggers_for(flags=flags, lot_accounting=graph.lot_accounting or {})
    if not triggers:
        return None
    return {
        "pageid": str(record["pageid"]),
        "revid": str(record.get("revid", "")),
        "url": record.get("url", ""),
        "title": record.get("title", ""),
        "triggers": list(triggers),
        "primary_trigger": triggers[0],
        "raw": raw,
        # deterministic baseline: what the rules alone produce, recorded before any model runs
        "baseline": {
            "n_events": len(graph.events),
            "n_entities": len(graph.entities),
            "n_produced": sum(len(e.produces) for e in graph.events),
            "n_allocations": len(graph.allocations),
            "flags": sorted(set(flags)),
            "lot_statuses": sorted(set((graph.lot_accounting or {}).values())),
            "n_proposable_slots": sum(1 for e in graph.events
                                      if e.alternative_group is None and e.condition_profile_id is None),
        },
    }


def select(cases: list[dict], n: int) -> list[dict]:
    """Stratify by primary trigger, then take the top of each stratum by the seeded rank."""
    by_trigger: dict[str, list[dict]] = {}
    for c in cases:
        by_trigger.setdefault(c["primary_trigger"], []).append(c)
    for rows in by_trigger.values():
        rows.sort(key=lambda c: rank_key(c["pageid"]))

    wanted = {t: int(n * share) for t, share in QUOTAS.items()}
    chosen: list[dict] = []
    for trigger, want in wanted.items():
        chosen.extend(by_trigger.get(trigger, [])[:want])
    # fill any shortfall from the remaining cases, still by seeded rank, so n is met where possible
    if len(chosen) < n:
        taken = {c["pageid"] for c in chosen}
        rest = sorted((c for c in cases if c["pageid"] not in taken), key=lambda c: rank_key(c["pageid"]))
        chosen.extend(rest[: n - len(chosen)])
    chosen.sort(key=lambda c: rank_key(c["pageid"]))
    return chosen[:n]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=60)
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=0, help="scan only the first N recipes (debug)")
    args = ap.parse_args(argv)

    rung, schema = build_env()
    recipes = load_recipes()
    if args.limit:
        recipes = recipes[: args.limit]

    cases, failures = [], 0
    for record in recipes:
        try:
            case = scan(record, rung, schema)
        except Exception:
            failures += 1
            continue
        if case:
            cases.append(case)

    chosen = select(cases, args.n)
    PACKET_DIR.mkdir(parents=True, exist_ok=True)
    packet_path = PACKET_DIR / f"hardcases_{len(chosen)}_{SEED}.jsonl"
    packet_path.write_text("".join(json.dumps(c, ensure_ascii=False) + "\n" for c in chosen),
                           encoding="utf-8")

    manifest = {
        "labels": list(LABELS),
        "seed": SEED,
        "quotas": QUOTAS,
        "requested_n": args.n,
        "selected_n": len(chosen),
        "scanned_recipes": len(recipes),
        "parse_failures": failures,
        "eligible_pool": len(cases),
        "pool_by_primary_trigger": dict(Counter(c["primary_trigger"] for c in cases)),
        "selected_by_primary_trigger": dict(Counter(c["primary_trigger"] for c in chosen)),
        "packet_path": str(packet_path.relative_to(ROOT)),
        "packet_sha256": hashlib.sha256(packet_path.read_bytes()).hexdigest(),
        "contains_text": False,
        "cases": [
            {k: c[k] for k in ("pageid", "revid", "url", "title", "triggers", "primary_trigger", "baseline")}
            for c in chosen
        ],
    }
    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, indent=1, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    print(f"scanned {len(recipes)} | eligible {len(cases)} | selected {len(chosen)} | failures {failures}")
    print(f"packet  {packet_path.relative_to(ROOT)}  sha256 {manifest['packet_sha256'][:16]}")
    print(f"manifest {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
