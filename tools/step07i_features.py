#!/usr/bin/env python3
"""STEP 07I part 2: single deterministic pass over every recipe corpus -> identity features parquet + tool mention ledger.
  -> ledgers/recipe_identity/recipe_identity_features_v1.parquet, ledgers/recipe_semantics/recipe_tool_mentions_v1.parquet"""
import json
import multiprocessing as mp
import sys
import time
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.identity import features as F  # noqa: E402
from culinarystate.identity.tools_extract import tool_mentions  # noqa: E402
from culinarystate.recipes import corpus as C, ledgers as LG, probe as PR  # noqa: E402

CHUNK = 500
S, I, B = pa.string(), pa.int64(), pa.binary()
FEAT = [("recipe_id", S), ("source_family", S), ("title_norm", S), ("title_key", S), ("norm_text_hash", S), ("raw_hash", S), ("rec_content_sha256", S), ("ing_ids", pa.list_(S)), ("ing_toks", pa.list_(S)), ("n_ing_lines", I), ("n_steps", I),
        ("proc_seq", pa.list_(S)), ("tool_ids", pa.list_(S)), ("mass_ing", pa.list_(S)), ("mass_g", pa.list_(pa.float64())), ("mh_steps", B), ("mh_ing", B), ("n_chars", I), ("cuisine", S), ("existing_family_id", S)]
TOOL = [("recipe_id", S), ("step_index", I), ("char_start", I), ("char_end", I), ("raw_tool", S), ("tool_id", S), ("tool_category", S), ("source_plane", S)]


def init():
    PR._units()
    LG.vocab()


def work(chunk):
    units_rx = PR._units()
    out, tools = [], []
    for rec in chunk:
        ing = LG.ingredient_mentions(rec, units_rx)
        ids = sorted({m["candidate_ingredient_id"] for m in ing if m["candidate_ingredient_id"] and m["link_status"] in ("ACCEPT", "REVIEW")})
        toks = sorted(t for t in ((m["candidate_ingredient_id"] if m["candidate_ingredient_id"] and m["link_status"] in ("ACCEPT", "REVIEW") else "x:" + F.norm_alnum(m["raw_span"] or "")) for m in ing if (m["candidate_ingredient_id"] or m["raw_span"])) if t != "x:")  # multiset (repeats kept)
        pm = [m for m in LG.process_mentions(rec, {}) if m["candidate_proc_id"]]
        pm.sort(key=lambda m: (m["instruction_index"], m["char_start"]))
        by_idx = {m["ingredient_index"]: m["candidate_ingredient_id"] for m in ing if m["ingredient_index"] is not None and m["candidate_ingredient_id"]}
        mi, mg = [], []
        for q in LG.quantity_mentions(rec):
            if q["mass_status"] == "MEASURED" and q["mass_value"] and by_idx.get(q["ingredient_index"]):
                mi.append(by_idx[q["ingredient_index"]])
                mg.append(float(q["mass_value"]))
        tm = tool_mentions(rec)
        tools.extend(tm)
        words = []
        for s in rec["steps"]:
            words.extend(F.norm_words(s))
        r = rec.get("rec") or {}
        out.append({"recipe_id": rec["recipe_id"], "source_family": rec["source_family"], "title_norm": F.norm_alnum(rec.get("title")), "title_key": F.title_key(rec.get("title") or ""),
                    "norm_text_hash": F.text_hash(rec.get("title") or "", rec["ingredient_lines"], rec["steps"]), "raw_hash": C.raw_hash(rec), "rec_content_sha256": r.get("content_sha256"), "ing_ids": ids, "ing_toks": toks,
                    "n_ing_lines": len(rec["ingredient_lines"]), "n_steps": len(rec["steps"]), "proc_seq": [m["candidate_proc_id"] for m in pm], "tool_ids": sorted({t["tool_id"] for t in tm}), "mass_ing": mi, "mass_g": mg,
                    "mh_steps": F.minhash(F.shingles(words, 4), 64), "mh_ing": F.minhash([__import__("zlib").crc32(t.encode()) for t in set(toks)], 32), "n_chars": sum(len(s) for s in rec["steps"]) + sum(len(s) for s in rec["ingredient_lines"]),
                    "cuisine": (rec.get("extra") or {}).get("cuisine"), "existing_family_id": rec.get("family_id")})
    return out, tools


def chunks():
    rec_all = C.rec_latest()
    buf = []

    def feed(it, fam_fn):
        nonlocal buf
        for rec in it:
            rec["family_id"] = fam_fn(rec)
            buf.append(rec)
            if len(buf) >= CHUNK:
                yield buf
                buf = []
    yield from feed(C.iter_rec_corpora(rec_all, ("A1_BBC_GOOD_FOOD", "WIKIBOOKS", "GUTENBERG_SEGMENT")), lambda r: r["rec"]["family_id"])
    yield from feed(C.iter_foodcom(), lambda r: "FAM-" + r["recipe_id"])
    yield from feed(C.iter_tasteset(), lambda r: "FAM-" + r["recipe_id"])
    if buf:
        yield buf


def table(rows, sch):
    return pa.table({n: pa.array([r.get(n) for r in rows], type=t) for n, t in sch})


def main():
    t0 = time.time()
    (ROOT / "ledgers/recipe_identity").mkdir(parents=True, exist_ok=True)
    pool = mp.get_context("spawn").Pool(4, initializer=init)
    wf = wt = None
    nf = nt = 0
    for i, (rows, trows) in enumerate(pool.imap(work, chunks(), chunksize=1)):
        t = table(rows, FEAT)
        wf = wf or pq.ParquetWriter(ROOT / "ledgers/recipe_identity/recipe_identity_features_v1.parquet", t.schema, compression="zstd")
        wf.write_table(t)
        nf += len(rows)
        if trows:
            tt = table(trows, TOOL)
            wt = wt or pq.ParquetWriter(ROOT / "ledgers/recipe_semantics/recipe_tool_mentions_v1.parquet", tt.schema, compression="zstd")
            wt.write_table(tt)
            nt += len(trows)
        if i % 100 == 0:
            print(f"chunk {i} recipes={nf} tools={nt} t={time.time() - t0:.0f}s", flush=True)
    pool.close()
    pool.join()
    wf.close()
    wt and wt.close()
    print(json.dumps({"recipes": nf, "tool_mentions": nt, "elapsed_s": round(time.time() - t0)}))


if __name__ == "__main__":
    main()
