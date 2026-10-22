"""STEP 07I-R: compact, integer-encoded per-representative view used by candidate generation and pair scoring.
Built by streaming the identity-features parquet row-group by row-group (vectorised Arrow/numpy; no per-recipe Python objects), written UNCOMPRESSED so every worker can memory-map it
(shared, evictable page cache instead of one private copy per worker)."""
from __future__ import annotations

import math

import numpy as np
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq

LIST_STR = ("ing_ids", "ing_toks", "proc_seq", "mass_ing")
STR_VOCAB = {"tok": ("ing_toks",), "ing": ("ing_ids", "mass_ing"), "proc": ("proc_seq",)}
COND_FAMILIES = ["TEMPERATURE", "TIME"]


def _vocabs(feat_path, keep_arr):
    """sorted unique strings per vocabulary kind, one streaming pass, restricted to representative rows"""
    seen = {k: set() for k in STR_VOCAB}
    pf = pq.ParquetFile(feat_path)
    cols = ["recipe_id"] + [c for cs in STR_VOCAB.values() for c in cs]
    for rg in range(pf.num_row_groups):
        t = pf.read_row_group(rg, columns=cols)
        t = t.filter(pc.is_in(t.column("recipe_id"), value_set=keep_arr))
        for kind, cs in STR_VOCAB.items():
            for c in cs:
                seen[kind].update(pc.unique(pc.list_flatten(t.column(c))).to_pylist())
    return {k: pa.array(sorted(x for x in v if x is not None)) for k, v in seen.items()}


def _encode_list(col: pa.ChunkedArray, vocab_arr: pa.Array, sort_within: bool, unique_within: bool):
    """list<string> -> (flat int32 ids, int64 offsets) ; vocab-indexed"""
    col = col.combine_chunks()
    offs = np.asarray(col.offsets).astype(np.int64)
    offs = offs - offs[0]
    flat = pc.index_in(pc.list_flatten(col), value_set=vocab_arr)
    ids = np.asarray(flat.fill_null(-1)).astype(np.int32)
    rows = np.repeat(np.arange(len(col)), np.diff(offs))
    if sort_within or unique_within:
        order = np.lexsort((ids, rows))
        ids, rows = ids[order], rows[order]
        if unique_within and len(ids):
            keep = np.r_[True, (ids[1:] != ids[:-1]) | (rows[1:] != rows[:-1])]
            ids, rows = ids[keep], rows[keep]
            offs = np.r_[0, np.cumsum(np.bincount(rows, minlength=len(col)))].astype(np.int64)
    return ids, offs


def _list_array(ids, offs, typ=pa.int32()):
    return pa.ListArray.from_arrays(pa.array(offs.astype(np.int32)), pa.array(ids, type=typ))


def build(feat_path, base_cols_df, rep_ids_sorted, cond_path, out_view, out_idf, progress=None):
    """base_cols_df: pandas frame indexed like rep_ids_sorted with source_id, locale, cuisine_if_explicit. Returns stats dict."""
    keep_arr = pa.array(rep_ids_sorted)
    voc = _vocabs(feat_path, keep_arr)
    pf = pq.ParquetFile(feat_path)
    pieces = []
    cols = ["recipe_id", "source_family", "title_norm", "title_key", "n_steps", "n_ing_lines", "existing_family_id", "ing_ids", "ing_toks", "proc_seq", "mass_ing", "mass_g", "mh_steps", "mh_ing"]
    for rg in range(pf.num_row_groups):
        t = pf.read_row_group(rg, columns=cols)
        t = t.filter(pc.is_in(t.column("recipe_id"), value_set=keep_arr))
        if t.num_rows == 0:
            continue
        ing, io = _encode_list(t.column("ing_ids"), voc["ing"], False, True)
        tok, to = _encode_list(t.column("ing_toks"), voc["tok"], True, False)
        prc, po = _encode_list(t.column("proc_seq"), voc["proc"], False, False)
        mi, mo = _encode_list(t.column("mass_ing"), voc["ing"], False, False)
        mg = t.column("mass_g").combine_chunks()
        pieces.append(pa.table({
            "rep_id": t.column("recipe_id"), "source_family": t.column("source_family"),
            "title_norm": pc.fill_null(t.column("title_norm"), ""), "title_key": pc.fill_null(t.column("title_key"), ""),
            "n_steps": t.column("n_steps"), "n_ing": t.column("n_ing_lines"), "existing_family_id": t.column("existing_family_id"),
            "ing": _list_array(ing, io), "toks": _list_array(tok, to), "proc": _list_array(prc, po), "mass_ing": _list_array(mi, mo),
            "mass_g": pa.ListArray.from_arrays(pa.array(np.asarray(mg.offsets).astype(np.int32) - np.int32(np.asarray(mg.offsets)[0])), pc.list_flatten(mg).cast(pa.float64())),
            "mh_steps": t.column("mh_steps"), "mh_ing": t.column("mh_ing")}))
    view = pa.concat_tables(pieces).combine_chunks()
    order = pc.sort_indices(view, sort_keys=[("rep_id", "ascending")])
    view = view.take(order)
    n = view.num_rows
    assert view.column("rep_id").to_pylist() == list(rep_ids_sorted), "representative set mismatch"
    # base-derived scalars (aligned to sorted rep ids)
    for c in ("source_id", "locale", "cuisine_if_explicit"):
        view = view.append_column(c if c != "cuisine_if_explicit" else "cuisine", pa.array(base_cols_df[c].tolist(), type=pa.string()))
    # condition signature (T = round(K), t = round(minutes)); codes are a bijection of the old string tags
    cidx = {r: i for i, r in enumerate(rep_ids_sorted)}
    cpf = pq.ParquetFile(cond_path)
    rows_l, code_l = [], []
    for b in cpf.iter_batches(batch_size=500000, columns=["recipe_id", "expression_family", "canonical_value"]):
        d = b.to_pandas()
        d = d[d.expression_family.isin(COND_FAMILIES) & d.canonical_value.notna()]
        r = d.recipe_id.map(cidx)
        d, r = d[r.notna()], r[r.notna()]
        if not len(d):
            continue
        v = d.canonical_value.to_numpy(dtype=float)
        is_t = (d.expression_family == "TEMPERATURE").to_numpy()
        code = np.where(is_t, (np.rint(v).astype(np.int64) + 10_000_000) * 2, (np.rint(v / 60).astype(np.int64) + 10_000_000) * 2 + 1)
        rows_l.append(r.to_numpy(dtype=np.int64))
        code_l.append(code)
    if rows_l:
        rr, cc = np.concatenate(rows_l), np.concatenate(code_l)
        order = np.lexsort((cc, rr))
        rr, cc = rr[order], cc[order]
        keep = np.r_[True, (cc[1:] != cc[:-1]) | (rr[1:] != rr[:-1])]
        rr, cc = rr[keep], cc[keep]
    else:
        rr, cc = np.array([], dtype=np.int64), np.array([], dtype=np.int64)
    offs = np.r_[0, np.cumsum(np.bincount(rr, minlength=n))].astype(np.int32)
    view = view.append_column("cond", pa.ListArray.from_arrays(pa.array(offs), pa.array(cc, type=pa.int64())))
    # idf over representatives (document frequency of unique tokens)
    tk = view.column("toks").combine_chunks()
    tflat = np.asarray(pc.list_flatten(tk)).astype(np.int64)
    trow = np.repeat(np.arange(n), np.diff(np.asarray(tk.offsets).astype(np.int64)))
    pair = np.unique(trow * (len(voc["tok"]) + 1) + tflat)
    dfc = np.bincount(pair % (len(voc["tok"]) + 1), minlength=len(voc["tok"])).astype(np.float64)
    idf = np.array([math.log((n + 1) / (c + 1)) + 1.0 for c in dfc])  # math.log (not np.log): bit-identical to the original scalar implementation
    np.save(out_idf, idf)
    pq.write_table(view, out_view, compression="NONE")
    return {"reps": n, "token_vocab": len(voc["tok"]), "ing_vocab": len(voc["ing"]), "proc_vocab": len(voc["proc"]), "cond_pairs": int(len(rr))}
