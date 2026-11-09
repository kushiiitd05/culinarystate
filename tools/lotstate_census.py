#!/usr/bin/env python
"""Lot-state census over a seeded recipe sample (S176, L-LOT): counts-only report + per-lot / per-line records.

    python tools/lotstate_census.py --seed 20261104 --sample-size 1000 --workers 8 \
        --out reports/lotstate/lotstate_census_1000_S176.json --records-dir data/derived/lotstate_1000_S176
Families default to the non-BBC corpora present on this server (FOODCOM, GUTENBERG_SEGMENT, WIKIBOOKS, TASTESET);
BBC Good Food text is never read (D-003). The full corpus is NOT run by this lane: sizes above 5,000 need --allow-large.
The pH registry is a parameter (--ph-registry, optional --ph-crosswalk); without it every pH flag is UNKNOWN.
Water activity stays UNKNOWN unless --allow-unverified-aw-constants is given (constants are SOURCE_UNVERIFIED).
Refuses to overwrite the report or a non-empty records directory; never writes a ledger.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from culinarystate.extraction.rung_a import RungA  # noqa: E402
from culinarystate.lotstate import census as CS  # noqa: E402
from culinarystate.lotstate import corpus as C  # noqa: E402
from culinarystate.lotstate import ing_match as M  # noqa: E402
from culinarystate.lotstate import sr_legacy as S  # noqa: E402
from culinarystate.lotstate.composition import AW_REGISTRY, AwConfig  # noqa: E402
from culinarystate.lotstate.linker import LineLinker, latest_rows, names_map  # noqa: E402
from culinarystate.lotstate.lots import BuilderConfig, LotStateBuilder  # noqa: E402
from culinarystate.lotstate.ph import PhRegistry  # noqa: E402
from culinarystate.quantity import rc2_dryrun as D  # noqa: E402

DRAFT = "registry/ing_sr_legacy_match_draft_v1.csv"
PROTECTED = ("EVD", "COND", "SRC", "MEAS", "SNAP")


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def protected_hashes(root: Path) -> dict:
    return {n: sha(root / "ledgers" / "data" / f"{n}.jsonl") for n in PROTECTED}


def load_top1(path: Path) -> dict:
    rows = list(csv.DictReader(open(path, encoding="utf-8", newline="")))
    return M.top1_table(rows)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed", required=True)
    ap.add_argument("--sample-size", type=int, default=1000)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--families", nargs="+", choices=C.FAMILIES, default=["FOODCOM", "GUTENBERG_SEGMENT", "WIKIBOOKS", "TASTESET"])
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--out", required=True)
    ap.add_argument("--records-dir", default=None)
    ap.add_argument("--units-out", default=None, help="also write the Food.com units check (counts only) for the same sample")
    ap.add_argument("--min-band", choices=("LOW", "MEDIUM", "HIGH"), default="MEDIUM")
    ap.add_argument("--ph-registry", default=None)
    ap.add_argument("--ph-crosswalk", default=None)
    ap.add_argument("--ph-crosswalk-min-band", default="HIGH")
    ap.add_argument("--allow-unverified-aw-constants", action="store_true")
    ap.add_argument("--allow-large", action="store_true")
    a = ap.parse_args(argv)
    root, out = Path(a.root), Path(a.out)
    if a.sample_size < 1 or a.workers < 1:
        ap.error("--sample-size and --workers must be positive")
    if a.sample_size > 5000 and not a.allow_large:
        ap.error("full-corpus sizes are not run by lane L-LOT (use --allow-large after orchestrator approval)")
    if out.exists():
        ap.error("refusing to overwrite an existing report")
    rdir = None
    if a.records_dir:
        rdir = Path(a.records_dir).resolve()
        try:
            inside = rdir.relative_to(ROOT.resolve()).parts
        except ValueError:
            inside = None
        if inside is not None and inside[:1] != ("data",):
            ap.error("--records-dir must be under data/ (git-ignored) or outside the repository")
        if rdir.exists() and any(rdir.iterdir()):
            ap.error("--records-dir must be empty or new")
        rdir.mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    start = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    before = protected_hashes(root)
    led = root / "ledgers" / "data"
    sr = S.load_sr(S.default_dir(root))
    top1 = load_top1(root / DRAFT)
    ing = latest_rows(led / "ING.jsonl")
    ph = PhRegistry.load(Path(a.ph_registry), crosswalk=Path(a.ph_crosswalk) if a.ph_crosswalk else None,
                         crosswalk_min_band=a.ph_crosswalk_min_band) if a.ph_registry else None
    aw = AwConfig(allow_unverified_constants=a.allow_unverified_aw_constants, registry_path=root / AW_REGISTRY)
    builder = LotStateBuilder(sr=sr, top1=top1, ing_names={k: v["canonical_name"] for k, v in ing.items()},
                              linker=LineLinker(names_map(led)), schema=D.load_schema(), rung=RungA(), ph_registry=ph,
                              cfg=BuilderConfig(min_band=a.min_band, aw=aw))
    recs = C.sample_records(tuple(a.families), a.seed, a.sample_size, root)
    if a.units_out:
        uo = Path(a.units_out)
        if uo.exists():
            ap.error("refusing to overwrite the units report")
        from culinarystate.lotstate.units_check import units_check
        ur = units_check(recs)
        ur.update(seed_sha256=hashlib.sha256(a.seed.encode()).hexdigest(), sample_size_requested=a.sample_size,
                  recipes_sampled=len(recs))
        D.assert_counts_only(ur)
        uo.parent.mkdir(parents=True, exist_ok=True)
        uo.write_text(json.dumps(ur, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps({"units_verdict": ur["verdict"]}))
    tally = CS.census(recs, builder, workers=a.workers, records_dir=rdir)
    body = CS.summarise(tally, a.min_band)
    after = protected_hashes(root)
    code_files = sorted((root / "src/culinarystate/lotstate").glob("*.py")) + [Path(__file__).resolve(),
                                                                              root / AW_REGISTRY, root / DRAFT]
    rep = {
        "record": "LOTSTATE_CENSUS_S176", "status": "AI_ENGINEERING_DRY_RUN_COUNTS_ONLY",
        "label": "REAL_BASE_SAMPLE_COUNTS_NOT_GOLD", "census_version": CS.CENSUS_VERSION,
        "contains_ids": False, "contains_text": False, "counts_as_human_gate": False,
        "labels": "MODEL_DERIVED|NON_CITABLE", "layer": "REFERENCE_DATA_MODEL_DERIVED",
        "seed_sha256": hashlib.sha256(a.seed.encode("utf-8")).hexdigest(), "sample_rule": "SHA256_SEED_CONCAT_RECIPE_ID_ASC",
        "sample_size_requested": a.sample_size, "families_requested": list(a.families), "workers": a.workers,
        "bbc_text_read": False, "min_band": a.min_band,
        "ph_registry": "ABSENT" if ph is None else "PRESENT_PROVISIONAL", "ph_registry_rows": 0 if ph is None else len(ph),
        "ph_registry_sha256": sha(Path(a.ph_registry)) if a.ph_registry else "NONE",
        "water_activity_switch": "ON_UNVERIFIED_CONSTANTS" if a.allow_unverified_aw_constants else "OFF",
        "match_draft_sha256": sha(root / DRAFT), "sr_food_csv_sha256": sha(Path(sr.source_dir) / "food.csv"),
        "protected_ledgers_unchanged": before == after,
        "code_sha256": [{"path": p.relative_to(root).as_posix() if p.is_relative_to(root) else p.name, "sha256": sha(p)}
                        for p in code_files],
        "records_written": rdir is not None, "seconds": round(time.time() - t0, 1), "started": start,
        **body,
    }
    D.assert_counts_only(rep)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "x", encoding="utf-8") as fh:
        fh.write(json.dumps(rep, indent=2, sort_keys=True) + "\n")
    if rdir is not None:
        parts = sorted(rdir.glob("*.jsonl"))
        man = {"record": "LOTSTATE_RECORDS_MANIFEST_S176", "census_report": out.as_posix(),
               "files": [{"name": p.name, "bytes": p.stat().st_size, "sha256": sha(p)} for p in parts],
               "contains_text": False, "note": "recipe ids, ING ids, numbers and codes only; git-ignored data plane"}
        (rdir / "MANIFEST.json").write_text(json.dumps(man, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"recipes": rep["recipes_sampled"], "lines": rep["lines"]["total"], "lots": rep["lots"]["total"],
                      "pct_usable_grams": rep["lines"]["pct_usable_grams"],
                      "pct_interval": rep["lots"]["pct_interval_composition"],
                      "pct_presence": rep["lots"]["pct_presence_only"], "seconds": rep["seconds"]}))
    return 0 if rep["protected_ledgers_unchanged"] else 4


if __name__ == "__main__":
    sys.exit(main())
