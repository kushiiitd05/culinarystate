#!/usr/bin/env python
"""Lot-state step 1 (S176, L-LOT): ING -> USDA SR Legacy match draft + human verification queue. AI_DRAFTED.

    python tools/lotstate_match_ing.py            # writes registry/ing_sr_legacy_match_draft_v1.csv,
                                                  #        registry/ing_sr_legacy_verification_queue_v1.csv,
                                                  #        reports/lotstate/ing_sr_match_summary_S176.json
Never writes a ledger. Refuses to overwrite existing outputs unless --overwrite. Nothing is auto-ACCEPTED: every row is
status AI_DRAFTED with an empty human_decision column. The queue is ordered by corpus mention frequency (sources and
columns documented in culinarystate.lotstate.mention_freq) with cumulative coverage so a human can stop at 80 %.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from culinarystate.lotstate import ing_match as M  # noqa: E402
from culinarystate.lotstate import mention_freq as F  # noqa: E402
from culinarystate.lotstate import sr_legacy as S  # noqa: E402
from culinarystate.lotstate.linker import LineLinker, names_map  # noqa: E402
from culinarystate.quantity import rc2_dryrun as D  # noqa: E402

DRAFT = "registry/ing_sr_legacy_match_draft_v1.csv"
QUEUE = "registry/ing_sr_legacy_verification_queue_v1.csv"
SUMMARY = "reports/lotstate/ing_sr_match_summary_S176.json"
DRAFT_COLS = ["ing_id", "canonical_name", "ing_status", "ing_category", "ledger_corpus_frequency", "rank", "fdc_id",
              "sr_description", "sr_category", "score", "confidence_band", "via", "reason", "status", "human_decision"]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write_csv(path: Path, cols: list[str], rows: list[dict], overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise SystemExit(f"refusing to overwrite {path} (use --overwrite)")
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=str(ROOT))
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--no-foodcom-scan", action="store_true", help="skip the Food.com parts scan (tests)")
    a = ap.parse_args(argv)
    root = Path(a.root)
    led = root / "ledgers" / "data"
    sr = S.load_sr(S.default_dir(root))
    matcher = M.Matcher(sr)
    ing_all = M.latest_ing(led / "ING.jsonl", active_only=False)
    ing = [r for r in ing_all if r["status"] == "ACTIVE"]
    draft = M.match_ing_rows(matcher, ing)
    top1 = {r["ing_id"]: r for r in draft if r["rank"] == 1}

    linker = LineLinker(names_map(led))
    src: dict[str, Counter] = {s: Counter() for s in F.SOURCES}
    unlinked: dict[str, int] = {}
    scan: dict = {}
    for r in ing:
        if r.get("corpus_frequency"):
            src["bbc_ledger"][r["id"]] = int(r["corpus_frequency"])
    if not a.no_foodcom_scan:
        parts, n_rec = F.foodcom_part_counts(root / "data/external/foodcom/recipes.parquet")
        c, linked, unl = F.link_counts(parts, linker)
        src["foodcom_parts"] = c
        unlinked["foodcom_parts"] = unl
        scan.update(foodcom_recipes_read=n_rec, foodcom_unique_parts=len(parts), foodcom_part_mentions=linked + unl)
    ts = root / "data/raw/tasteset/TASTEset.csv"
    if ts.exists():
        c, _, unl = F.tasteset_counts(ts, linker)
        src["tasteset_lines"], unlinked["tasteset_lines"] = c, unl
    wb = root / "registry/recipes/wikibooks_ingredient_links_v1.csv"
    if wb.exists():
        src["wikibooks_lines"] = F.csv_id_counts(wb)
    gt = root / "registry/recipes/gutenberg_ingredient_links_v1.csv"
    if gt.exists():
        src["gutenberg_recipes"] = F.csv_id_counts(gt)
    active_ids = {r["id"] for r in ing}
    total = {i: sum(src[s].get(i, 0) for s in F.SOURCES) for i in active_ids}
    order = sorted(active_ids, key=lambda i: (-total[i], i))
    cum, need_all = F.cumulative(((i, total[i]) for i in order), 0.8)

    def need(cols: tuple[str, ...]) -> int:
        tot = {i: sum(src[s].get(i, 0) for s in cols) for i in active_ids}
        return F.cumulative(((i, tot[i]) for i in sorted(active_ids, key=lambda i: (-tot[i], i))), 0.8)[1]

    names = {r["id"]: r for r in ing}
    full: dict[str, list[dict]] = {}
    for x in draft:
        full.setdefault(x["ing_id"], []).append(x)
    qrows = []
    for rank, (i, m, share) in enumerate(cum, 1):
        t = top1.get(i)
        cands = full.get(i, [])
        qrows.append({
            "priority_rank": rank, "ing_id": i, "canonical_name": names[i]["canonical_name"],
            "mentions_total": m, **{f"mentions_{s}": src[s].get(i, 0) for s in F.SOURCES},
            "cum_mentions_share": f"{share:.4f}", "within_80pct": "YES" if rank <= need_all else "NO",
            "proposed_fdc_id": t["fdc_id"] if t else "", "proposed_sr_description": t["sr_description"] if t else "",
            "proposed_band": t["confidence_band"] if t else "NONE", "proposed_score": t["score"] if t else "",
            "alt2_fdc_id": cands[1]["fdc_id"] if len(cands) > 1 else "", "alt3_fdc_id": cands[2]["fdc_id"] if len(cands) > 2 else "",
            "reason": t["reason"] if t else "NO_CANDIDATE", "status": "AI_DRAFTED", "human_decision": ""})
    qcols = ["priority_rank", "ing_id", "canonical_name", "mentions_total", *[f"mentions_{s}" for s in F.SOURCES],
             "cum_mentions_share", "within_80pct", "proposed_fdc_id", "proposed_sr_description", "proposed_band",
             "proposed_score", "alt2_fdc_id", "alt3_fdc_id", "reason", "status", "human_decision"]
    write_csv(root / DRAFT, DRAFT_COLS, draft, a.overwrite)
    write_csv(root / QUEUE, qcols, qrows, a.overwrite)

    bands = Counter(r["confidence_band"] for r in top1.values())
    mention_by_band = Counter()
    for i in active_ids:
        mention_by_band[top1[i]["confidence_band"] if i in top1 else "NONE"] += total[i]
    q80 = [r for r in qrows if r["within_80pct"] == "YES"]
    top_bands = Counter(r["proposed_band"] for r in q80)
    rep = {
        "record": "ING_SR_MATCH_SUMMARY_S176", "status": "AI_DRAFTED_COUNTS_ONLY", "matcher_version": M.MATCHER_VERSION,
        "contains_ids": False, "contains_text": False, "counts_as_human_gate": False,
        "ing_ledger_lines": sum(1 for _ in open(led / "ING.jsonl", encoding="utf-8")),
        "ing_unique_ids": len(ing_all), "ing_active": len(ing), "ing_not_active": len(ing_all) - len(ing),
        "sr_foods": len(sr.foods), "ing_with_candidate": len(top1), "ing_no_candidate": len(ing) - len(top1),
        "top1_band_counts": dict(sorted(bands.items())),
        "mentions_total": sum(total.values()), "mentions_by_top1_band": dict(sorted(mention_by_band.items())),
        "mentions_by_source": {s: sum(src[s].get(i, 0) for i in active_ids) for s in F.SOURCES},
        "unlinked_mentions_by_source": dict(unlinked), **scan,
        "ing_rows_for_80pct_all_sources": need_all,
        "ing_rows_for_80pct_nonbbc_lines": need(("foodcom_parts", "wikibooks_lines", "tasteset_lines")),
        "ing_rows_for_80pct_foodcom_only": need(("foodcom_parts",)),
        "ing_rows_for_80pct_bbc_ledger_only": need(("bbc_ledger",)),
        "queue_80pct_top1_band_counts": dict(sorted(top_bands.items())),
        "ing_with_zero_mentions": sum(1 for i in active_ids if total[i] == 0),
        "ordering": "MENTIONS_TOTAL_DESC_THEN_ING_ID",
        "sr_dir_sha256_food_csv": sha(Path(sr.source_dir) / "food.csv"),
        "draft_sha256": sha(root / DRAFT), "queue_sha256": sha(root / QUEUE),
    }
    D.assert_counts_only(rep)
    out = root / SUMMARY
    if out.exists() and not a.overwrite:
        raise SystemExit(f"refusing to overwrite {out}")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rep, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: rep[k] for k in ("ing_active", "ing_with_candidate", "top1_band_counts",
                                           "ing_rows_for_80pct_all_sources", "ing_rows_for_80pct_nonbbc_lines")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
