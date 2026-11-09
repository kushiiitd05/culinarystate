"""D-073 R1 precision check (S170): draw the labelled sample, then score it. DRAFT; not a human gate.

    python tools/d073_precision_sample.py draw --seed d073-precision-2026-11-07-r1 \
        --exclude-seed d073-exploration-2026-11-07 --exclude-size 400 --recipes 400 \
        --out-private data/interim/d073/d073_r1_sample_private.csv \
        --out reports/step17/d073_r1_sample_counts_S170.json
    python tools/d073_precision_sample.py score --private data/interim/d073/d073_r1_sample_private.csv \
        --out reports/step17/d073_r1_precision_S170.json

Pre-registration: reports/step17/d073_implicit_binding_precision_PREREG.md. The private csv (recipe ids, excerpts,
an empty ``label`` column) must be git-ignored or outside the repository; the tracked outputs hold counts only.
Refuses to overwrite any output.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))
from culinarystate.extraction import d073_current_sample as S  # noqa: E402
from culinarystate.extraction.rung_a import RungA  # noqa: E402
from culinarystate.extraction.rung_a_measure import seeded_sample  # noqa: E402
from culinarystate.recipes.ledgers import LOCALE  # noqa: E402
import step17b_rung_a_dryrun as T17  # noqa: E402

PREREG = "reports/step17/d073_implicit_binding_precision_PREREG.md"
N_ITEMS, CONTEXT = 60, 400
COLS = ("item", "recipe_id", "family", "offset", "action", "tier_size", "current_leaves", "before", "action_and_after",
        "label", "note")


def _tracked_by_git(path: Path) -> bool:
    p = path.resolve()
    try:
        p.relative_to(ROOT.resolve())
    except ValueError:
        return False
    return subprocess.run(["git", "-C", str(ROOT), "check-ignore", "-q", str(p)]).returncode != 0


def _sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _text(rec) -> str:
    return "\n".join(s for s in rec.get("steps") or [] if isinstance(s, str) and s.strip())


def _write_json(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2, sort_keys=True)
        fh.write("\n")


def draw(a, record_source) -> int:
    fams = list(a.families)
    excluded = {r["recipe_id"] for r in seeded_sample(T17._stream(fams, ROOT, record_source, {}),
                                                         a.exclude_seed, a.exclude_size)} if a.exclude_size else set()
    status: dict = {}
    sample = seeded_sample(T17._stream(fams, ROOT, record_source, status), a.seed, a.recipes)
    rung, cands, texts, fam_of = RungA(), {}, {}, {}
    with_steps = events = 0
    for rec in sample:
        rid, raw = rec["recipe_id"], _text(rec)
        if not raw:
            continue
        with_steps += 1
        found = S.r1_candidates(raw, locale=LOCALE.get(rec.get("source_family")), rung=rung)
        events += len(found)
        if found:
            cands[rid], texts[rid], fam_of[rid] = found, raw, rec.get("source_family")
    picked = S.pick_sample(cands, seed=a.seed, n=N_ITEMS, excluded=excluded)
    a.out_private.parent.mkdir(parents=True, exist_ok=True)
    with a.out_private.open("x", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS)
        w.writeheader()
        for i, p in enumerate(picked, 1):
            raw, off = texts[p["recipe_id"]], p["offset"]
            w.writerow({"item": i, "recipe_id": p["recipe_id"], "family": fam_of[p["recipe_id"]], "offset": off,
                        "action": p["surface"], "tier_size": p["tier_size"],
                        "current_leaves": " | ".join(p["current_leaves"]), "before": raw[max(0, off - CONTEXT):off],
                        "action_and_after": raw[off:off + 160], "label": "", "note": ""})
    _write_json(a.out, {
        "record": "D073_R1_PRECISION_SAMPLE", "rule_id": S.RULE_ID, "prereg": PREREG, "status": "AI_ENGINEERING_COUNTS_ONLY",
        "contains_ids": False, "contains_text": False, "counts_as_human_gate": False,
        "seed_sha256": _sha(a.seed), "exclude_seed_sha256": _sha(a.exclude_seed), "exclude_size": a.exclude_size,
        "recipes_requested": a.recipes, "recipes_sampled": len(sample), "texts_with_steps": with_steps,
        "r1_events": events, "recipes_with_r1": len(cands),
        "recipes_with_r1_after_exclusion": sum(1 for r in cands if r not in excluded),
        "sample_items": len(picked), "family_status": dict(sorted(status.items()))})
    print(json.dumps({"sample_items": len(picked), "r1_events": events, "texts_with_steps": with_steps}))
    return 0


def score(a) -> int:
    with a.private.open(newline="", encoding="utf-8") as fh:
        labels = [row["label"].strip() for row in csv.DictReader(fh)]
    try:
        out = S.score(labels)
    except ValueError as exc:
        raise SystemExit(f"score refused: {exc}")
    out.update(record="D073_R1_PRECISION_SCORE", prereg=PREREG, status="AI_ENGINEERING_COUNTS_ONLY",
               contains_ids=False, contains_text=False, counts_as_human_gate=False, labeller="ksh (AI) under D-071",
               private_sha256=hashlib.sha256(a.private.read_bytes()).hexdigest())
    _write_json(a.out, out)
    print(json.dumps({k: out[k] for k in ("n", "label_counts", "precision", "wilson95_lower", "verdict")}))
    return 0


def main(argv=None, record_source=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("draw")
    d.add_argument("--seed", required=True)
    d.add_argument("--recipes", type=int, default=400)
    d.add_argument("--exclude-seed", required=True)
    d.add_argument("--exclude-size", type=int, default=400)
    d.add_argument("--families", nargs="+", choices=T17.FAMILIES, default=list(T17.FAMILIES))
    d.add_argument("--out-private", required=True, type=Path)
    d.add_argument("--out", required=True, type=Path)
    s = sub.add_parser("score")
    s.add_argument("--private", required=True, type=Path)
    s.add_argument("--out", required=True, type=Path)
    a = ap.parse_args(argv)
    if a.cmd == "score":
        if a.out.exists():
            ap.error(f"refusing to overwrite {a.out}")
        return score(a)
    if _tracked_by_git(a.out_private):
        ap.error("the private sample file must be git-ignored or outside the repository")
    for p in (a.out_private, a.out):
        if p.exists():
            ap.error(f"refusing to overwrite {p}")
    if a.recipes < 1 or a.exclude_size < 0:
        ap.error("--recipes must be positive and --exclude-size non-negative")
    return draw(a, record_source or T17.corpus_records)


if __name__ == "__main__":
    sys.exit(main())
