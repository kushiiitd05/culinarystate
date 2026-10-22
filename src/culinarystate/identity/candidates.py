"""STEP 07I-R phase `candidates`: bounded-memory candidate-pair generation over the representative view.
Same retrieval rules as the pre-registration (+ amendment A1): (a) equal normalised title blocks, (b) instruction-shingle MinHash LSH, (c) ingredient-token MinHash LSH (>=4 tokens, bucket cap 50),
(d) existing REC family co-membership. Pairs are never held as Python objects: every generator emits numpy int64 keys to disk shards bucketed by the smaller index, then each bucket is
de-duplicated independently and finally packed into fixed-size input partitions (<= chunk_size pairs)."""
from __future__ import annotations

import shutil
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq

from .runtime import arrays_hash, atomic_write_parquet

BITS = {"title": 1, "steps": 2, "ing": 4, "family": 8}
TITLE_MIN, TITLE_BLOCK_MAX = 6, 60
STEPS_ROWS, STEPS_BANDS, STEPS_CAP = 4, 16, 200
ING_ROWS, ING_BANDS, ING_CAP, ING_MIN_TOKS = 4, 8, 50, 4
FAMILY_MAX = 30
EMIT_FLUSH = 2_000_000


class Emitter:
    def __init__(self, raw_dir: Path, n: int, n_buckets: int):
        self.raw, self.n = Path(raw_dir), n
        self.bsize = max(1, -(-n // n_buckets))
        self.n_buckets = -(-n // self.bsize)
        self.counts = {}  # source -> raw pairs emitted
        self.buf, self.nbuf, self.seq = [], 0, 0

    def add(self, a, b, source: str):
        a, b = np.asarray(a, dtype=np.int64), np.asarray(b, dtype=np.int64)
        lo, hi = np.minimum(a, b), np.maximum(a, b)
        m = lo != hi
        lo, hi = lo[m], hi[m]
        if len(lo):
            self.buf.append((source, (lo << 32) | hi))
            self.nbuf += len(lo)
            self.counts[source] = self.counts.get(source, 0) + len(lo)
        if self.nbuf >= EMIT_FLUSH:
            self.flush()

    def flush(self):
        for source, keys in self.buf:
            bk = (keys >> 32) // self.bsize
            for b in np.unique(bk):
                d = self.raw / ("b%03d" % b)
                d.mkdir(parents=True, exist_ok=True)
                np.save(d / ("s%d_%06d.npy" % (BITS[source], self.seq)), keys[bk == b])
                self.seq += 1
        self.buf, self.nbuf = [], 0


def _title_pairs(em: Emitter, title, toks_off, toks_flat, dfc, diag):
    n = len(title)
    ok = np.array([len(t) >= TITLE_MIN for t in title])
    rows = np.nonzero(ok)[0]
    # rarest token per row (min (df, id)) for sub-blocking
    cnt = np.diff(toks_off)
    r_row = np.repeat(np.arange(n), cnt)
    order = np.lexsort((toks_flat, dfc[toks_flat], r_row))
    first = np.r_[True, r_row[order][1:] != r_row[order][:-1]] if len(order) else np.array([], dtype=bool)
    rare = np.full(n, -1, dtype=np.int64)
    if len(order):
        rare[r_row[order][first]] = toks_flat[order][first]
    groups = {}
    for i in rows:
        groups.setdefault(title[i], []).append(i)
    pa_, pb_, nb = [], [], 0

    def emit_block(b):
        nonlocal nb
        ti, tj = np.triu_indices(len(b), 1)
        b = np.asarray(b)
        pa_.append(b[ti]), pb_.append(b[tj])
        nb += len(ti)
        if nb >= 500_000:
            em.add(np.concatenate(pa_), np.concatenate(pb_), "title")
            pa_.clear(), pb_.clear()
            nb = 0
    for lst in groups.values():
        if len(lst) < 2:
            continue
        if len(lst) <= TITLE_BLOCK_MAX:
            emit_block(lst)
            continue
        diag["title_blocks_subblocked"] = diag.get("title_blocks_subblocked", 0) + 1
        sub = {}
        for i in lst:
            if rare[i] >= 0:
                sub.setdefault(rare[i], []).append(i)
        for s in sub.values():
            if len(s) < 2:
                continue
            if len(s) > TITLE_BLOCK_MAX:
                diag["title_subblocks_skipped_over_60"] = diag.get("title_subblocks_skipped_over_60", 0) + 1
                continue
            emit_block(s)
    if pa_:
        em.add(np.concatenate(pa_), np.concatenate(pb_), "title")


def _lsh(em: Emitter, sig_col: pa.ChunkedArray, rows_per_band: int, n_bands: int, source: str, cap: int, name: str, diag, allow=None):
    """sig_col: binary column of uint32 signatures (None allowed). Bucket-size-capped banding; skipped buckets are counted (recall diagnostic)."""
    n = len(sig_col)
    valid = np.asarray(pc.is_valid(sig_col))
    if allow is not None:
        valid &= allow
    idx = np.nonzero(valid)[0]
    if not len(idx):
        return
    sigs = sig_col.combine_chunks().filter(pa.array(valid))
    width = len(sigs[0].as_py()) // 4
    M = np.frombuffer(b"".join(sigs.to_pylist()), dtype=np.uint32).reshape(len(idx), width)
    tri = {}
    for b in range(n_bands):
        blk = M[:, b * rows_per_band:(b + 1) * rows_per_band].astype(np.uint64)
        key = np.zeros(len(blk), dtype=np.uint64)
        with np.errstate(over="ignore"):
            for c in range(rows_per_band):
                key = key * np.uint64(1000003) ^ blk[:, c]
        o = np.argsort(key, kind="stable")
        ks = key[o]
        starts = np.nonzero(np.r_[True, ks[1:] != ks[:-1]])[0]
        sizes = np.diff(np.r_[starts, len(ks)])
        big = sizes > cap
        diag[name + "_buckets_skipped_over_cap"] = diag.get(name + "_buckets_skipped_over_cap", 0) + int(big.sum())
        diag[name + "_records_in_skipped_buckets"] = diag.get(name + "_records_in_skipped_buckets", 0) + int(sizes[big].sum())
        for s in np.unique(sizes[(sizes >= 2) & (sizes <= cap)]):
            st = starts[sizes == s]
            if s not in tri:
                tri[s] = np.triu_indices(s, 1)
            ti, tj = tri[s]
            step = max(1, 1_000_000 // len(ti))
            for k in range(0, len(st), step):
                mem = idx[o[st[k:k + step, None] + np.arange(s)[None, :]]]
                em.add(mem[:, ti].ravel(), mem[:, tj].ravel(), source)


def _family_pairs(em: Emitter, fam_col):
    fams = fam_col.to_pylist()
    g = {}
    for i, f in enumerate(fams):
        if isinstance(f, str) and not f.startswith("FAM-FC") and not f.startswith("FAM-TS"):
            g.setdefault(f, []).append(i)
    for lst in g.values():
        if 2 <= len(lst) <= FAMILY_MAX:
            ti, tj = np.triu_indices(len(lst), 1)
            b = np.asarray(lst)
            em.add(b[ti], b[tj], "family")


def generate(view_path, work_dir, chunk_size: int, n_buckets: int = 128, max_pairs: int = 0, log=print):
    """Returns (stats, partitions) ; partitions = list of {pid, path, rows, input_hash, content_hash}. Deterministic for a given view and chunk_size."""
    work = Path(work_dir)
    raw, parts = work / "raw_shards", work / "parts"
    for d in (raw, parts):
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True)
    view = pq.read_table(view_path, columns=["title_norm", "toks", "mh_steps", "mh_ing", "existing_family_id"], memory_map=True)
    n = view.num_rows
    toks = view.column("toks").combine_chunks()
    toff = np.asarray(toks.offsets).astype(np.int64)
    tflat = np.asarray(pc.list_flatten(toks)).astype(np.int64)
    ntok_vocab = int(tflat.max()) + 1 if len(tflat) else 1
    trow = np.repeat(np.arange(n), np.diff(toff))
    uniq = np.unique(trow * ntok_vocab + tflat)
    dfc = np.bincount(uniq % ntok_vocab, minlength=ntok_vocab)
    uniq_per_row = np.bincount(uniq // ntok_vocab, minlength=n)
    em = Emitter(raw, n, n_buckets)
    diag = {}
    title = view.column("title_norm").to_pylist()
    _title_pairs(em, title, toff, tflat, dfc, diag)
    em.flush()
    _lsh(em, view.column("mh_steps"), STEPS_ROWS, STEPS_BANDS, "steps", STEPS_CAP, "steps_lsh", diag)
    em.flush()
    _lsh(em, view.column("mh_ing"), ING_ROWS, ING_BANDS, "ing", ING_CAP, "ing_lsh", diag, allow=uniq_per_row >= ING_MIN_TOKS)
    em.flush()
    _family_pairs(em, view.column("existing_family_id"))
    em.flush()
    diag["raw_pairs_by_source"] = dict(em.counts)
    # per-bucket de-duplication (OR of source bits), then fixed-size packing
    partitions, cur_i, cur_j, cur_m, cur_n, total = [], [], [], [], 0, 0
    by_bit = {b: 0 for b in BITS.values()}

    def close_part():
        nonlocal cur_i, cur_j, cur_m, cur_n
        if not cur_n:
            return
        i, j, m = np.concatenate(cur_i), np.concatenate(cur_j), np.concatenate(cur_m)
        pid = "P%05d" % len(partitions)
        t = pa.table({"i": pa.array(i, type=pa.int32()), "j": pa.array(j, type=pa.int32()), "mask": pa.array(m, type=pa.uint8())})
        w = atomic_write_parquet(t, parts / (pid + ".in.parquet"), compression="NONE")
        partitions.append({"pid": pid, "path": "parts/%s.in.parquet" % pid, "rows": int(len(i)), "input_hash": arrays_hash(i.astype(np.int32), j.astype(np.int32), m.astype(np.uint8)), "content_hash": w["content_hash"]})
        cur_i, cur_j, cur_m, cur_n = [], [], [], 0

    for bdir in sorted(raw.iterdir()):
        ks, ms = [], []
        for f in sorted(bdir.iterdir()):
            k = np.load(f)
            ks.append(k)
            ms.append(np.full(len(k), int(f.name.split("_")[0][1:]), dtype=np.uint8))
        k, m = np.concatenate(ks), np.concatenate(ms)
        o = np.argsort(k, kind="stable")
        k, m = k[o], m[o]
        st = np.nonzero(np.r_[True, k[1:] != k[:-1]])[0]
        uk, um = k[st], np.bitwise_or.reduceat(m, st)
        if max_pairs and total + len(uk) > max_pairs:
            uk, um = uk[:max_pairs - total], um[:max_pairs - total]
        ui, uj = (uk >> 32).astype(np.int32), (uk & 0xFFFFFFFF).astype(np.int32)
        total += len(uk)
        for b in by_bit:
            by_bit[b] += int(((um & b) > 0).sum())
        s = 0
        while s < len(ui):
            take = min(len(ui) - s, chunk_size - cur_n)
            cur_i.append(ui[s:s + take]), cur_j.append(uj[s:s + take]), cur_m.append(um[s:s + take])
            cur_n += take
            s += take
            if cur_n >= chunk_size:
                close_part()
        if max_pairs and total >= max_pairs:
            break
    close_part()
    shutil.rmtree(raw)
    diag["pairs_total_candidates"] = total
    diag["pairs_by_source_bit"] = {str(b): c for b, c in by_bit.items()}
    diag["partitions"] = len(partitions)
    return diag, partitions
