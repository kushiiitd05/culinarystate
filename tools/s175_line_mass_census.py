"""S175: counts-only line -> grams census (Rung A food mention -> ING name -> SR via defaults registry).

    python tools/s175_line_mass_census.py --families A1_BBC_GOOD_FOOD --out reports/s175/line_mass_census_BBC.json

D-003: A1_BBC_GOOD_FOOD runs on the Mac only. Output is counts only (composition.line_census.assert_counts_only).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))

from culinarystate.composition import ing_sr_match as M  # noqa: E402
from culinarystate.composition import line_census as LC  # noqa: E402
from culinarystate.composition import sr_legacy as SR  # noqa: E402
from culinarystate.extraction.rung_a_lexicon import load_lexicon, tokens  # noqa: E402

SR_DIR = ROOT / "data/raw/fdc/sr_legacy/FoodData_Central_sr_legacy_food_csv_2018-04"
REGISTRY = ROOT / "registry/ing_sr_defaults_v1.csv"


def _ing_names() -> tuple[dict[str, str], dict[str, int]]:
    name, freq = {}, {}
    with open(ROOT / "ledgers/data/ING.jsonl", encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            name[r["id"]], freq[r["id"]] = r["canonical_name"], r.get("corpus_frequency") or 0
    return name, freq


def make_find_food(lex, name: dict[str, str], freq: dict[str, int]):
    def find(line: str) -> str | None:
        words = [w for _, _, w in tokens(line)]
        best = None
        for i in range(len(words)):
            m = lex.food_at(words, i)
            if m is not None and (best is None or m.length > best.length):
                best = m
        ids = [i for i in (best.ids if best else ()) if i in name]
        if not ids:
            return None
        return name[sorted(ids, key=lambda i: (-freq[i], i))[0]]
    return find


def make_resolve(foods, registry, index):
    cache: dict[str, LC.Resolved] = {}

    def resolve(n: str) -> LC.Resolved:
        if n not in cache:
            r = M.resolve(n, foods, registry, index=index)
            usable = r.status in ("REGISTRY_MAPPED", "AUTO_MATCH_HIGH")
            cache[n] = LC.Resolved(r.fdc_id if usable else None, r.status)
        return cache[n]
    return resolve


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--families", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    from step17b_rung_a_dryrun import corpus_records
    foods = SR.load_sr(SR_DIR)
    name, freq = _ing_names()
    out = LC.census(corpus_records(tuple(a.families), ROOT),
                    find_food=make_find_food(load_lexicon(), name, freq),
                    resolve=make_resolve(foods, M.load_registry(REGISTRY), M.build_index(foods)), foods=foods)
    out["usable_match_statuses"] = ["REGISTRY_MAPPED", "AUTO_MATCH_HIGH"]
    LC.assert_counts_only({k: v for k, v in out.items() if k != "usable_match_statuses"})
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(out, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({f: {k: v for k, v in d.items() if isinstance(v, int)} for f, d in out["families"].items()}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
