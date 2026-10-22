"""STEP 07I-R tests: resumable, memory-bounded identity pipeline on a tiny synthetic corpus (no real recipe text)."""
import csv
import hashlib
import json
import os
import random

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from culinarystate.identity import exact as EX
from culinarystate.identity import families as FAM
from culinarystate.identity import pairwork as PW
from culinarystate.identity.features import minhash
from culinarystate.identity.pairs import W, Store
from culinarystate.identity.pipeline import MemoryGuardExit, Run
from culinarystate.identity.runtime import atomic_write_parquet, table_content_hash, verify_parquet

TOKENS = ["tok%02d" % k for k in range(40)]
PROCS = ["PROC-%06d" % k for k in range(8)]


def _sig(words, n):
    sh = [hash_i(" ".join(words[i:i + 2])) for i in range(max(1, len(words) - 1))]
    return minhash(sh, n)


def hash_i(s):
    return int(hashlib.md5(s.encode()).hexdigest()[:8], 16)


def make_corpus(root, n=70, seed=3):
    rng = random.Random(seed)
    rows, base = [], []
    templates = []
    for t in range(n // 5):
        templates.append(rng.sample(TOKENS, 8))
    for k in range(n):
        tpl = templates[k % len(templates)]
        toks = sorted(set(tpl[: 8 - (k // len(templates)) % 2]))  # family-like near copies
        steps = ["mix %s then bake %d" % (" ".join(toks[:3]), k % len(templates))]
        rid = "R%04d" % k
        text = "|".join(toks) + "|" + "|".join(steps)
        raw_hash = hashlib.sha256((text if k % 13 else "SAME").encode()).hexdigest() if k % 13 == 0 else hashlib.sha256((text + str(k)).encode()).hexdigest()
        rows.append({"recipe_id": rid, "source_family": "SRC_A" if k % 2 else "SRC_B", "title_norm": "dish %d number" % (k % len(templates)), "title_key": "dish %d" % (k % len(templates)),
                     "norm_text_hash": hashlib.sha256((text + "n%d" % k).encode()).hexdigest(), "raw_hash": raw_hash, "rec_content_sha256": None, "ing_ids": ["ING-%06d" % (hash_i(t) % 50) for t in toks],
                     "ing_toks": toks, "n_ing_lines": len(toks), "n_steps": 1, "proc_seq": PROCS[: 3 + k % 3], "tool_ids": [], "mass_ing": [], "mass_g": [],
                     "mh_steps": _sig(" ".join(steps).split(), 64), "mh_ing": _sig(toks, 32), "n_chars": 200, "cuisine": None, "existing_family_id": None})
        base.append({"recipe_id": rid, "source_id": "SRC-%d" % (k % 2), "source_record_id": rid, "locale": "en", "cuisine_if_explicit": None, "quality_tier": "GOLD_PENDING_INDEPENDENT_IAA" if k == 13 else "SOURCE_RAW",
                     "has_instructions": True, "has_ingredients": True, "has_quantities": False, "has_conditions": False, "has_gold_annotations": k == 13, "recipe_family_id": "FAM-%s" % rid, "raw_recipe_pointer": rid})
    (root / "ledgers/recipe_identity").mkdir(parents=True, exist_ok=True)
    (root / "ledgers/recipe_base").mkdir(parents=True, exist_ok=True)
    (root / "ledgers/recipe_semantics").mkdir(parents=True, exist_ok=True)
    (root / "registry").mkdir(parents=True, exist_ok=True)
    (root / "reports/step07i").mkdir(parents=True, exist_ok=True)
    ls, ld = pa.list_(pa.string()), pa.list_(pa.float64())
    sch = pa.schema([("recipe_id", pa.string()), ("source_family", pa.string()), ("title_norm", pa.string()), ("title_key", pa.string()), ("norm_text_hash", pa.string()), ("raw_hash", pa.string()),
                     ("rec_content_sha256", pa.string()), ("ing_ids", ls), ("ing_toks", ls), ("n_ing_lines", pa.int64()), ("n_steps", pa.int64()), ("proc_seq", ls), ("tool_ids", ls), ("mass_ing", ls),
                     ("mass_g", ld), ("mh_steps", pa.binary()), ("mh_ing", pa.binary()), ("n_chars", pa.int64()), ("cuisine", pa.string()), ("existing_family_id", pa.string())])
    pq.write_table(pa.Table.from_pylist(rows, schema=sch), root / "ledgers/recipe_identity/recipe_identity_features_v1.parquet")
    pq.write_table(pa.Table.from_pylist(base), root / "ledgers/recipe_base/recipe_base_v1.parquet")
    pq.write_table(pa.table({"recipe_id": ["R0001"], "expression_family": ["TEMPERATURE"], "canonical_value": [450.0], "normalized_status": ["OK"]}), root / "ledgers/recipe_semantics/recipe_condition_mentions_v1.parquet")
    with open(root / "registry/recipe_source_usage_registry_v1.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["source_id", "usage_class"])
        w.writerow(["SRC-0", "PUBLIC_OPEN"])
        w.writerow(["SRC-1", "LICENCE_UNVERIFIED"])
    return rows


@pytest.fixture()
def corpus(tmp_path):
    root = tmp_path / "culinarystate"
    make_corpus(root)
    return root


def run_to_candidates(root, chunk=300, name="t"):
    r = Run(root, name, 0, chunk, 8, 4.5, 1, 0, log=lambda s: None)
    r.audit()
    r.exact()
    r.candidates()
    return r


def test_exact_groups_reproducible_and_order_independent(corpus):
    f = lambda: EX.load_frame(corpus / "ledgers/recipe_identity/recipe_identity_features_v1.parquet", corpus / "ledgers/recipe_base/recipe_base_v1.parquet", corpus / "registry/recipe_source_usage_registry_v1.csv")
    t1, s1 = EX.build_exact(f())
    t2, s2 = EX.build_exact(f().sample(frac=1, random_state=1).sort_values("recipe_id").reset_index(drop=True))
    assert t1.equals(t2) and s1 == s2
    assert t1.duplicate_group_id.nunique() < len(t1)  # SAME-hash copies merged
    assert len(t1) == 70  # no member is deleted


def test_gold_and_licence_survive_exact_grouping(corpus):
    df = EX.load_frame(corpus / "ledgers/recipe_identity/recipe_identity_features_v1.parquet", corpus / "ledgers/recipe_base/recipe_base_v1.parquet", corpus / "registry/recipe_source_usage_registry_v1.csv")
    t, _ = EX.build_exact(df)
    g13 = t[t.recipe_id == "R0013"].iloc[0]
    assert g13.quality_tier == "GOLD_PENDING_INDEPENDENT_IAA"
    grp = t[t.duplicate_group_id == g13.duplicate_group_id]
    assert (grp.group_representative_id == "R0013").all()  # Gold member represents its group, never demoted
    assert dict(zip(t.recipe_id, t.usage_class)) == {r: ("PUBLIC_OPEN" if int(r[1:]) % 2 == 0 else "LICENCE_UNVERIFIED") for r in t.recipe_id}  # licence class carried unchanged
    assert t.source_id.notna().all() and t.source_family.notna().all()  # provenance preserved


def test_chunk_size_bounds_partitions_and_pairs_unique(corpus):
    r = run_to_candidates(corpus, chunk=25)
    parts = r.man.d["candidate_partitions"]
    assert parts and all(p["rows"] <= 25 for p in parts)
    assert len({p["pid"] for p in parts}) == len(parts)
    keys = set()
    for p in parts:
        t = pq.read_table(r.run / p["path"])
        i, j = t.column("i").to_numpy(), t.column("j").to_numpy()
        assert (i < j).all()
        ks = set(zip(i.tolist(), j.tolist()))
        assert not (ks & keys), "pair appears in two partitions"
        keys |= ks
    assert len(keys) == r.man.phase("candidates")["diag"]["pairs_total_candidates"]


def test_resume_skips_valid_partitions_and_is_deterministic(corpus):
    r = run_to_candidates(corpus, chunk=25)
    pid0 = r.man.d["candidate_partitions"][0]["pid"]
    r.features(only=pid0)  # interrupted: only one partition finished
    assert r.man.part("features", pid0)["status"] == "DONE"
    f0 = r.run / "parts" / (pid0 + ".feat.parquet")
    m0 = os.stat(f0).st_mtime_ns
    r.features(resume=True)
    assert os.stat(f0).st_mtime_ns == m0  # valid partition was not rescored
    r.score()
    r.family()
    h1 = r.man.phase("family-candidates")["summary"]["final_hash"]
    r2 = Run(corpus, "t", 0, 25, 8, 4.5, 1, 0, log=lambda s: None)  # fresh process object, same manifest
    r2.exact(), r2.candidates(), r2.features(), r2.score()
    r2.family()
    assert r2.man.phase("family-candidates")["summary"]["final_hash"] == h1


def test_corrupt_and_missing_partitions_are_recomputed(corpus):
    r = run_to_candidates(corpus, chunk=25)
    r.features()
    parts = r.man.d["candidate_partitions"]
    a, b = parts[0]["pid"], parts[1]["pid"]
    good = r.man.part("features", a)["output_hash"]
    fa, fb = r.run / "parts" / (a + ".feat.parquet"), r.run / "parts" / (b + ".feat.parquet")
    with open(fa, "r+b") as f:  # partial corruption: truncate mid-file
        f.truncate(os.path.getsize(fa) // 2)
    fb.unlink()  # missing partition
    assert not verify_parquet(fa, parts[0]["rows"], good)
    r.features()
    assert verify_parquet(fa, parts[0]["rows"], good) and fb.exists()
    assert r.man.part("features", a)["output_hash"] == good


def test_input_hash_change_is_rejected(corpus):
    r = run_to_candidates(corpus, chunk=25)
    p = r.man.d["candidate_partitions"][0]
    task = {"pid": p["pid"], "in_path": str(r.run / p["path"]), "out_path": str(r.run / "parts" / "x.feat.parquet"), "view_path": str(r.run / "reps_view.parquet"), "idf_path": str(r.run / "idf.npy"),
            "input_hash": "0" * 64, "rows": p["rows"]}
    assert PW.run_features(task)["status"] == "INPUT_HASH_MISMATCH"
    assert not (r.run / "parts" / "x.feat.parquet").exists()


def test_atomic_write_leaves_no_partial_file(tmp_path, monkeypatch):
    t = pa.table({"a": [1, 2, 3]})
    import culinarystate.identity.runtime as RT
    monkeypatch.setattr(RT, "table_content_hash", lambda x: "bad" if x.num_rows == 3 and getattr(RT, "_n", 0) else "ok")
    RT._n = 1
    calls = {"n": 0}

    def flaky(x):
        calls["n"] += 1
        return "h%d" % calls["n"]  # write-side hash != read-back hash
    monkeypatch.setattr(RT, "table_content_hash", flaky)
    with pytest.raises(IOError):
        atomic_write_parquet(t, tmp_path / "o.parquet")
    assert list(tmp_path.iterdir()) == []


def test_memory_guard_trips_in_worker(corpus):
    r = run_to_candidates(corpus, chunk=25)
    p = r.man.d["candidate_partitions"][0]
    PW.init_worker(None, 1e-6)
    try:
        res = PW.run_features({"pid": p["pid"], "in_path": str(r.run / p["path"]), "out_path": str(r.run / "parts" / "g.feat.parquet"), "view_path": str(r.run / "reps_view.parquet"),
                               "idf_path": str(r.run / "idf.npy"), "input_hash": p["input_hash"], "rows": p["rows"]})
    finally:
        PW.init_worker(None, None)
    assert res["status"] == "MEMORY_GUARD_TRIGGERED" and not (r.run / "parts" / "g.feat.parquet").exists()


def test_vectorised_score_matches_scalar_finalize():
    rng = np.random.RandomState(0)
    n = 400
    cols = {k: rng.rand(n) for k in list(W) + ["title_trigram", "ingredient_token", "process_set", "scale_ratio"]}
    for k in cols:
        cols[k][rng.rand(n) < 0.3] = np.nan
    ft = {"i": pa.array(np.arange(n, dtype=np.int32)), "j": pa.array(np.arange(n, dtype=np.int32) + 1), "mask": pa.array(rng.randint(1, 16, n).astype(np.uint8))}
    for k in PW.FLOAT_COLS:
        ft[k] = pa.array(cols.get(k, np.full(n, np.nan)), type=pa.float64(), from_pandas=True)
    mt, p3 = rng.rand(n) < 0.8, rng.rand(n) < 0.7
    cu = [None if x < 0.4 else bool(x < 0.7) for x in rng.rand(n)]
    for k in ("same_source", "cross_source_family", "locale_agree"):
        ft[k] = pa.array([True] * n)
    ft["cuisine_agree"], ft["min_tok_ok"], ft["proc3_ok"] = pa.array(cu, type=pa.bool_()), pa.array(mt), pa.array(p3)
    ft["hint"] = pa.array([None] * n, type=pa.string())
    out = PW.score_table(pa.table(ft)).to_pandas()
    st = Store.from_lists(id=[])
    for k in range(n):
        f = {c: (None if np.isnan(cols[c][k]) else float(cols[c][k])) for c in W}
        f.update(title_token=f["title_token"], min_tok_ok=bool(mt[k]), proc3_ok=bool(p3[k]), cuisine_agree=cu[k])
        g = st.finalize(f)
        assert (g["score"] is None and np.isnan(out.score[k])) or g["score"] == out.score[k]
        assert g["family_edge"] == out.family_edge[k] and g["features_available"] == out.features_available[k]


def test_star_clustering_does_not_chain():
    # path A-B-C-D (indices 0-1-2-3): B has degree 2 and becomes centre; D only touches C, so D must NOT be pulled in transitively
    ei, ej, es = np.array([0, 1, 2]), np.array([1, 2, 3]), np.array([0.9, 0.9, 0.9])
    center, conf = FAM.star_cluster(4, ei, ej, es)
    assert center[0] == center[1] == center[2] == 1 and center[3] == 3


def test_family_phase_preserves_every_recipe_and_flags_consistency(corpus):
    r = run_to_candidates(corpus, chunk=40)
    r.features(), r.score()
    s = r.family()
    fm = pd.read_parquet(r.ID / "recipe_family_members_v1_t.parquet")
    dg = pd.read_parquet(r.ID / "duplicate_group_members_v1_t.parquet")
    assert len(fm) == 70 and fm.recipe_id.nunique() == 70 and len(dg) == 70  # nothing deleted or merged away
    assert fm.source_id.notna().all() and fm.source_family.notna().all()
    assert (fm.calibrated == False).all() and (fm.family_method == "PROVISIONAL_STAR_V1").all()  # noqa: E712
    cons = pd.read_parquet(r.ID / "recipe_family_consistency_v1_t.parquet")
    if len(cons):
        assert cons.family_review_status.isin(["FAMILY_CANDIDATE_REVIEW", "FAMILY_CANDIDATE_CONSISTENT"]).all()
        assert (cons.min_internal_score.dropna() <= cons.mean_internal_score.dropna() + 1e-12).all()
    assert s["recipes"] == 70
