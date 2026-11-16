"""S178 lane MECH: run the Kleene mechanism screen over recipes with their physical-layer records (counts-only report).

    # 1,000-recipe sample (all non-BBC families, the v04 sample records)
    nice -n 10 python tools/s178_mech_screen_run.py --seed 20261104 --sample-size 1000 --workers 8 \
        --families FOODCOM GUTENBERG_SEGMENT WIKIBOOKS TASTESET \
        --l1 data/derived/physical_L1_1000_S178v04 --l2 data/derived/physical_L2_1000_S178v04 \
        --nh-l1 data/derived/physical_NH_L1_1000_S178v04 --nh-l2 data/derived/physical_NH_L2_1000_S178v04 \
        --tag 1000_S178_v04 --out reports/s178/mech/screen_census_1000_S178_v04.json \
        --rows-dir data/derived/mech_screen_1000_S178v04

    # one full family (repeat per family; the record directories are parameters, e.g. the v05 records later)
    nice -n 10 python tools/s178_mech_screen_run.py --seed 20261104 --sample-size 600000 --workers 24 --families FOODCOM \
        --l1 data/derived/physical_L1_full_S178v04/FOODCOM --l2 data/derived/physical_L2_full_S178v04/FOODCOM \
        --nh-l1 data/derived/physical_NH_L1_FOODCOM_full_S178v04 --nh-l2 data/derived/physical_NH_L2_FOODCOM_full_S178v04 \
        --tag FOODCOM_full_S178_v04 --out reports/s178/mech/screen_census_FOODCOM_full_S178_v04.json \
        --rows-dir data/derived/mech_screen_FOODCOM_full_S178v04

The sample is the Step 17b rule (smallest sha256(seed || recipe_id)), and chunk i of ``workers * 8`` chunks holds sample
positions i, i + n, ...; that is exactly how the physical-layer runs wrote ``part-<i>.jsonl``, so chunk i reads part
``i mod (parts in that directory)`` and every record found there is checked to belong to that part (``record_alignment``).
The number of chunks must be a multiple of the number of parts of every directory. Rung A is re-run on the joined step text
(as the binders do) to get the event graph; every screened event's process id must equal its record's. Output: counts-only
JSON (``rc2_dryrun.assert_counts_only``); per-(event, lot) verdict rows under ``--rows-dir`` (git-ignored ``data/derived``).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))

from culinarystate.extraction.interfaces import SourceText  # noqa: E402
from culinarystate.extraction.rung_a import RungA  # noqa: E402
from culinarystate.extraction.rung_a_measure import code, rank, seeded_sample  # noqa: E402
from culinarystate.mechanism import evidence_gates as EG  # noqa: E402
from culinarystate.mechanism import mech_entries as ME  # noqa: E402
from culinarystate.mechanism import mech_inputs as MI  # noqa: E402
from culinarystate.mechanism import mech_k3 as K  # noqa: E402
from culinarystate.mechanism import screen as S  # noqa: E402
from culinarystate.quantity import rc2_dryrun as D  # noqa: E402
from culinarystate.recipes.ledgers import LOCALE  # noqa: E402

RUN_VERSION = "s178-mech-screen-run-0.1.0-draft"
LAYERS = ("L1", "L2", "NH_L1", "NH_L2")
_CTX: dict = {}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _steps(rec) -> list[str]:
    return [str(s) for s in rec.get("steps") or [] if isinstance(s, str) and s.strip()]


def _chunk(idx: int) -> Counter:
    """Chunk ``idx`` = sample positions idx, idx + n, ... (recipes without steps are skipped); reads part idx mod parts."""
    c = _CTX
    texts = [t for t in c["texts"][idx::c["n"]] if t is not None]
    want = {t[0] for t in texts}
    cnt: Counter = Counter()
    records: dict[str, dict] = {}
    for layer in LAYERS:
        d, parts = c["dirs"].get(layer), c["parts"].get(layer, 0)
        if d is None or not parts:
            records[layer] = {}
            continue
        p = idx % parts
        recmap, seen = S.read_part(Path(d) / f"part-{p:05d}.jsonl", want)
        pos = c["pos"]
        cnt[("record_alignment", layer, "foreign_recipe_in_part")] += sum(
            1 for rid in seen if rid not in pos or pos[rid] % parts != p)
        cnt[("record_alignment", layer, "recipes_with_records")] += len(recmap)
        records[layer] = recmap
    rows_fh = open(Path(c["rows_dir"]) / f"part-{idx:05d}.jsonl", "w", encoding="utf-8") if c["rows_dir"] else None
    rung, schema = c["rung"], c["schema"]
    try:
        for rid, fam, raw, locale in texts:
            cnt[("recipes", fam, "with_steps")] += 1
            try:
                g = rung.run(SourceText.from_raw("BIND", raw), rung.config(locale=locale), schema=schema).graph
                res = S.screen_graph(rid, fam, g, screen=c["screen"], catalog=c["catalog"], families=c["families"],
                                     records={k: v.get(rid, {}) for k, v in records.items()},
                                     hierarchy=c["hierarchy"], rows=rows_fh is not None)
            except Exception as e:  # noqa: BLE001 - counted by class name only (a message may hold text)
                cnt[("exceptions", code(type(e).__name__))] += 1
                continue
            cnt.update(res.counts)
            if rows_fh is not None:
                for r in res.rows:
                    rows_fh.write(json.dumps(r, sort_keys=True, separators=(",", ":")) + "\n")
    finally:
        if rows_fh is not None:
            rows_fh.close()
    return cnt


def _stream(families, status):
    from step17b_rung_a_dryrun import corpus_records
    for fam in families:
        n = 0
        try:
            for rec in corpus_records((fam,), ROOT):
                if rec.get("source_family") != fam:
                    continue
                n += 1
                yield rec
        except (FileNotFoundError, OSError, ImportError):
            status[fam] = "INPUT_ERROR_PARTIAL" if n else "INPUT_MISSING"
            continue
        status[fam] = "READ"


def _sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(a) -> dict:
    t0 = time.time()
    start = _now()
    status: dict[str, str] = {}
    seen = 0

    def counted(it):
        nonlocal seen
        for rec in it:
            seen += 1
            yield rec
    sample = seeded_sample(counted(_stream(tuple(a.families), status)), a.seed, a.sample_size)
    texts = []
    for rec in sample:
        st = _steps(rec)
        if st:
            texts.append((rec["recipe_id"], rec.get("source_family"), "\n".join(st), LOCALE.get(rec.get("source_family"))))
    pos = {rec["recipe_id"]: i for i, rec in enumerate(sample)}
    n = a.workers * 8 if a.workers > 1 else 1
    dirs = {"L1": a.l1, "L2": a.l2, "NH_L1": a.nh_l1, "NH_L2": a.nh_l2}
    parts = {k: S.n_parts(Path(v)) if v else 0 for k, v in dirs.items()}
    for k, p in parts.items():
        if dirs[k] and (p == 0 or n % p):
            raise SystemExit(f"{k}: {p} parts in {dirs[k]} do not divide {n} chunks (use --workers matching that run)")
    # texts keep sample positions: chunk i must see positions i, i+n, ... (parts were written from the full sample)
    texts_by_pos = [None] * len(sample)
    for t in texts:
        texts_by_pos[pos[t[0]]] = t
    entries = ME.load(Path(a.entries))
    screen = S.MechScreen(entries)
    catalog = MI.MemberCatalog.load(ROOT)
    _CTX.clear()
    _CTX.update(texts=texts_by_pos, n=n, dirs=dirs, parts=parts, pos=pos,
                rows_dir=a.rows_dir, rung=RungA(), schema=D.load_schema(ROOT), screen=screen, catalog=catalog,
                families=MI.read_proc_families(), hierarchy=EG._default_hierarchy())
    if a.rows_dir:
        Path(a.rows_dir).mkdir(parents=True, exist_ok=True)
    setup_s = time.time() - t0
    try:
        if n == 1:
            parts_out = [_chunk(0)]
        else:
            import multiprocessing as mp
            with mp.get_context("fork").Pool(a.workers) as pool:
                parts_out = pool.map(_chunk, range(n), chunksize=1)
    finally:
        _CTX.clear()
    acc: Counter = Counter()
    for p in parts_out:
        acc.update(p)
    end = _now()
    report = {
        "record": "MECH_SCREEN_CENSUS", "status": S.STATUS, "label": "COUNTS_ONLY_T6_AI_DRAFTED_NOT_A_RESULT_ABOUT_FOOD",
        "citable": False, "contains_ids": False, "contains_text": False, "counts_as_human_gate": False,
        "screen_version": S.SCREEN_VERSION, "run_version": RUN_VERSION, "k3_semantics": "KLEENE_STRONG",
        "views": [S.view_key(v) for v in K.VIEWS], "mechanisms": list(screen.keys), "tag": a.tag,
        "seed_sha256": hashlib.sha256(a.seed.encode()).hexdigest(), "sample_rule": "SHA256_SEED_CONCAT_RECIPE_ID_ASC",
        "sample_size_requested": int(a.sample_size), "recipes_seen": seen, "recipes_sampled": len(sample),
        "recipes_with_steps": len(texts), "family_status": {code(k): v for k, v in sorted(status.items())},
        "chunks": n, "workers": a.workers,
        "inputs": {"entries_sha256": _sha(Path(a.entries)), "inputs_version": MI.VERSION,
                   "record_parts": {k: v for k, v in parts.items()},
                   "record_dirs": {k: (str(Path(v)) if v else "NOT_USED") for k, v in dirs.items()},
                   "record_dir_manifest_sha256": {k: S.dir_manifest_sha256(Path(v)) if v and a.manifest else "NOT_COMPUTED"
                                                  for k, v in dirs.items()},
                   "catalog": {k: v for k, v in catalog.describe().items()}},
        "totals": S.nest(acc, "events") | {"lots": S.nest(acc, "lots")},
        "recipes": S.nest(acc, "recipes"),
        "events_not_screened_family": S.nest(acc, "events_not_screened_family"),
        "events_physical_record_missing": S.nest(acc, "events_physical_record_missing"),
        "record_alignment": S.nest(acc, "record_alignment"),
        "l2_record_status": S.nest(acc, "l2_status"),
        "verdicts": S.nest(acc, "verdict"),
        "verdicts_by_event_class": S.nest(acc, "verdict_by_event_class"),
        "reasons": S.nest(acc, "reason"),
        "possible_support_layer": S.nest(acc, "possible_support_layer"),
        "not_possible_deciding_item": S.nest(acc, "not_possible_item"),
        "l1_to_l2_changes": S.nest(acc, "l1_to_l2_change"),
        "bracket_disagreement": S.nest(acc, "bracket_disagreement"),
        "by_process_family_l1": S.nest(acc, "by_process_family"),
        "edges": S.nest(acc, "edge"),
        "invariant_violations": S.nest(acc, "invariant_violation"),
        "exceptions_by_class": S.nest(acc, "exceptions"),
        "exceptions_total": int(sum(v for k, v in acc.items() if k[0] == "exceptions")),
    }
    D.assert_counts_only(report)
    timing = {"start": start, "end": end, "wall_s": round(time.time() - t0, 1), "setup_s": round(setup_s, 1)}
    return report, timing


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", default="20261104")
    ap.add_argument("--sample-size", type=int, default=1000)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--families", nargs="+", required=True)
    ap.add_argument("--l1", required=True)
    ap.add_argument("--l2")
    ap.add_argument("--nh-l1", required=True)
    ap.add_argument("--nh-l2")
    ap.add_argument("--entries", default=str(ME.OUT_PATH))
    ap.add_argument("--tag", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--rows-dir")
    ap.add_argument("--timing-out", help="sidecar JSON with start / end / wall time (kept out of the report: replay)")
    ap.add_argument("--no-manifest", dest="manifest", action="store_false")
    a = ap.parse_args(argv)
    if os.path.exists(a.out):
        raise SystemExit(f"refusing to overwrite {a.out}")
    rep, timing = run(a)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(rep, indent=1, sort_keys=True) + "\n"
    Path(a.out).write_text(text, encoding="utf-8")
    sha = hashlib.sha256(text.encode()).hexdigest()
    if a.timing_out:
        Path(a.timing_out).write_text(json.dumps({**timing, "report": Path(a.out).name, "report_sha256": sha},
                                                 indent=1, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"out": a.out, "sha256": sha, "exceptions_total": rep["exceptions_total"],
                      "invariant_violations": rep["invariant_violations"], "timing": timing, "totals": rep["totals"]}))
    return 0 if rep["exceptions_total"] == 0 and not rep["invariant_violations"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
