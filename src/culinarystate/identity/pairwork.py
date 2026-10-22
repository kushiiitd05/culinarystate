"""STEP 07I-R phases `features` and `score`: per-partition, memory-bounded, resumable pair work.
A worker reads ONE input partition (<= chunk_size pairs), materialises only the representatives that partition touches from the memory-mapped view, computes the interpretable
components (features) or the pre-registered ranking score / provisional family edge / keep flag (score), and writes its own output atomically. Only a tiny status dict returns to the parent."""
from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

from .pairs import MIN_ING, T_IDF, T_PROC, T_SHINGLE, T_TITLE, W, Store
from .runtime import MemoryGuardTriggered, arrays_hash, atomic_write_parquet, rss_gb, table_content_hash, verify_parquet

_STOP = None
_CEIL = None

FLOAT_COLS = ["title_token", "title_trigram", "ingredient_id", "ingredient_token", "ingredient_idf", "multiset", "instruction_shingle", "process_set", "process_seq", "condition",
              "quantity_profile", "scale_ratio"]
BOOL_COLS = ["same_source", "cross_source_family", "locale_agree", "cuisine_agree", "min_tok_ok", "proc3_ok"]
GUARD_EVERY = 2000


def init_worker(stop_event, per_worker_ceiling_gb):
    global _STOP, _CEIL
    _STOP, _CEIL = stop_event, per_worker_ceiling_gb


def _guard():
    if (_STOP is not None and _STOP.is_set()) or (_CEIL is not None and rss_gb() > _CEIL):
        raise MemoryGuardTriggered("rss %.2f GB (ceiling %s) or stop requested" % (rss_gb(), _CEIL))


def local_store(view_path, idf, ii, jj):
    """Store over the unique representatives touched by (ii, jj); returns (store, local_i, local_j)"""
    U = np.unique(np.concatenate([ii, jj]))
    v = pq.read_table(view_path, memory_map=True).take(pa.array(U))
    li, lj = np.searchsorted(U, ii), np.searchsorted(U, jj)
    toks = v.column("toks").to_pylist()
    mass = [dict(zip(a, b)) if len(a) else {} for a, b in zip(v.column("mass_ing").to_pylist(), v.column("mass_g").to_pylist())]
    tokset = [frozenset(t) for t in toks]
    need = set().union(*tokset) if tokset else set()
    st = Store.from_lists(
        id=v.column("rep_id").to_pylist(), src=v.column("source_family").to_pylist(), sid=v.column("source_id").to_pylist(), locale=v.column("locale").to_pylist(),
        cuisine=v.column("cuisine").to_pylist(), title_norm=v.column("title_norm").to_pylist(), twords=[frozenset(str(t).split()) for t in v.column("title_key").to_pylist()],
        ids=[frozenset(x) for x in v.column("ing").to_pylist()], toks=toks, tokset=tokset, proc=v.column("proc").to_pylist(), mh_steps=v.column("mh_steps").to_pylist(),
        cond=[frozenset(x) for x in v.column("cond").to_pylist()], mass=mass, idf={t: float(idf[t]) for t in need}, n_steps=v.column("n_steps").to_pylist(), n_ing=v.column("n_ing").to_pylist())
    return st, li, lj


def input_arrays(path):
    t = pq.read_table(path)
    return t.column("i").to_numpy().astype(np.int32), t.column("j").to_numpy().astype(np.int32), t.column("mask").to_numpy().astype(np.uint8)


def features_table(st, li, lj, ii, jj, mm):
    cols = {c: [] for c in FLOAT_COLS + BOOL_COLS + ["hint"]}
    for k in range(len(li)):
        if k % GUARD_EVERY == 0:
            _guard()
        f = st.components(int(li[k]), int(lj[k]))
        for c in cols:
            cols[c].append(f.get(c))
    out = {"i": pa.array(ii, type=pa.int32()), "j": pa.array(jj, type=pa.int32()), "mask": pa.array(mm, type=pa.uint8())}
    for c in FLOAT_COLS:
        out[c] = pa.array(cols[c], type=pa.float64())
    for c in BOOL_COLS:
        out[c] = pa.array(cols[c], type=pa.bool_())
    out["hint"] = pa.array(cols["hint"], type=pa.string())
    return pa.table(out)


def run_features(task):
    """task: dict(pid, in_path, out_path, view_path, idf_path, input_hash, rows) -> status dict"""
    t0 = time.time()
    ii, jj, mm = input_arrays(task["in_path"])
    if arrays_hash(ii, jj, mm) != task["input_hash"] or len(ii) != task["rows"]:
        return {"pid": task["pid"], "status": "INPUT_HASH_MISMATCH"}
    try:
        st, li, lj = local_store(task["view_path"], np.load(task["idf_path"]), ii.astype(np.int64), jj.astype(np.int64))
        t = features_table(st, li, lj, ii, jj, mm)
        w = atomic_write_parquet(t, task["out_path"])
    except MemoryGuardTriggered as e:
        return {"pid": task["pid"], "status": "MEMORY_GUARD_TRIGGERED", "detail": str(e), "peak_rss_gb": rss_gb()}
    return {"pid": task["pid"], "status": "DONE", "rows": w["rows"], "output_hash": w["content_hash"], "bytes": w["bytes"], "seconds": round(time.time() - t0, 2), "peak_rss_gb": round(rss_gb(), 3)}


def _col(t, name):
    a = t.column(name).combine_chunks()
    return np.asarray(a.fill_null(np.nan)).astype(np.float64)


def score_table(ft: pa.Table) -> pa.Table:
    """vectorised ranking score / provisional family edge / keep flag; arithmetic order identical to Store.finalize (sequential weighted accumulation)"""
    n = ft.num_rows
    num, den, navail = np.zeros(n), np.zeros(n), np.zeros(n, dtype=np.int8)
    for k, w in W.items():
        v = _col(ft, k)
        a = ~np.isnan(v)
        num = num + np.where(a, w * np.where(a, v, 0.0), 0.0)
        den = den + np.where(a, w, 0.0)
        navail = navail + a.astype(np.int8)
    with np.errstate(invalid="ignore", divide="ignore"):
        score = np.where(den > 0, num / np.where(den > 0, den, 1.0), np.nan)
    idf, tt, sh, ps = _col(ft, "ingredient_idf"), _col(ft, "title_token"), _col(ft, "instruction_shingle"), _col(ft, "process_seq")
    boolv = lambda c: ft.column(c).combine_chunks()
    min_ok = np.asarray(boolv("min_tok_ok").fill_null(False))
    p3 = np.asarray(boolv("proc3_ok").fill_null(False))
    cu = boolv("cuisine_agree")
    cu_false = np.asarray(cu.is_valid()) & ~np.asarray(cu.fill_null(True))
    sup = (sh >= T_SHINGLE) | ((ps >= T_PROC) & p3)  # NaN compares False
    edge = min_ok & (idf >= T_IDF) & (tt >= T_TITLE) & sup & ~cu_false
    mask = ft.column("mask").combine_chunks().to_numpy(zero_copy_only=False).astype(np.uint8)
    keep = (score >= 0.50) | edge | ((mask & 8) > 0) | (((mask & 1) > 0) & (tt >= 0.8))
    return pa.table({"i": ft.column("i"), "j": ft.column("j"), "mask": ft.column("mask"), "score": pa.array(score, type=pa.float64(), from_pandas=True),
                     "features_available": pa.array(navail, type=pa.int8()), "family_edge": pa.array(edge), "keep": pa.array(keep)})


def run_score(task):
    """task: dict(pid, feat_path, out_path, feat_hash, rows)"""
    t0 = time.time()
    if not verify_parquet(task["feat_path"], task["rows"], task["feat_hash"]):
        return {"pid": task["pid"], "status": "FEATURE_PARTITION_INVALID"}
    t = score_table(pq.read_table(task["feat_path"]))
    w = atomic_write_parquet(t, task["out_path"])
    return {"pid": task["pid"], "status": "DONE", "rows": w["rows"], "output_hash": w["content_hash"], "bytes": w["bytes"], "seconds": round(time.time() - t0, 2), "peak_rss_gb": round(rss_gb(), 3),
            "kept": int(np.asarray(t.column("keep")).sum()), "edges": int(np.asarray(t.column("family_edge")).sum())}
