"""STEP 07I-R phased, resumable, memory-bounded identity pipeline orchestrator (Python 3.8+).
phases: audit -> exact -> candidates -> features -> score -> family-candidates   (review-sample / statistics call the existing 07I tools)
Crash policy: every unit of work is a partition; a unit counts as done only if its manifest entry, input hash, row count and content hash all validate."""
from __future__ import annotations

import hashlib
import json
import multiprocessing as mp
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq

from . import candidates as CAND
from . import exact as EX
from . import families as FAM
from . import pairwork as PW
from . import reps_view as RV
from .runtime import MEMORY_GUARD_EXIT, Manifest, Watchdog, atomic_write_parquet, rss_gb, sha256_file, table_content_hash, verify_parquet


class MemoryGuardExit(SystemExit):
    pass


class Run:
    def __init__(self, root, name="main", sample=0, chunk_size=150_000, n_buckets=128, max_memory_gb=4.5, threads=3, max_pairs=0, log=print):
        self.root, self.name, self.sample, self.log = Path(root), name, sample, log
        self.ID = self.root / "ledgers/recipe_identity"
        self.run = self.ID / "run" / name
        self.run.mkdir(parents=True, exist_ok=True)
        mname = "step07i_identity_run_v1.json" if name == "main" else "_run_%s.json" % name
        self.man = Manifest(self.ID / "run_manifests" / mname)
        self.cfg = dict(chunk_size=chunk_size, n_buckets=n_buckets, max_memory_gb=max_memory_gb, threads=threads, max_pairs=max_pairs, sample=sample)
        self.man.d["config"] = self.cfg
        self.suf = "" if name == "main" else "_" + name
        self.feat = self.ID / "recipe_identity_features_v1.parquet"
        self.base = self.root / "ledgers/recipe_base/recipe_base_v1.parquet"
        self.usage = self.root / "registry/recipe_source_usage_registry_v1.csv"
        self.a1 = self.root.parent / "a1" / "A1 3" / "data" / "processed" / "recipes_processed.jsonl"
        self.cond = self.root / "ledgers/recipe_semantics/recipe_condition_mentions_v1.parquet"
        self.stop = None
        self.watch_period = 10.0

    # ------------------------------------------------------------------ audit
    def audit(self):
        t0 = time.time()
        pf = pq.ParquetFile(self.feat)
        base_ids = pq.read_table(self.base, columns=["recipe_id"]).column("recipe_id")
        ids, nulls, empties, short = [], {n: 0 for n in pf.schema_arrow.names}, {k: 0 for k in ("title_norm", "title_key")}, 0
        for rg in range(pf.num_row_groups):
            t = pf.read_row_group(rg)
            ids.extend(t.column("recipe_id").to_pylist())
            for c in t.column_names:
                nulls[c] += t.column(c).null_count
            for c in empties:
                empties[c] += int(pc.sum(pc.equal(pc.fill_null(t.column(c), "x"), "")).as_py() or 0)
            short += int(pc.sum(pc.less(t.column("n_chars"), 60)).as_py())
        bset, fset = set(base_ids.to_pylist()), set(ids)
        res = {"file_sha256": sha256_file(self.feat), "bytes": self.feat.stat().st_size, "rows": pf.metadata.num_rows, "row_groups": pf.num_row_groups, "created_by": pf.metadata.created_by,
               "unique_recipe_ids": len(fset), "duplicate_recipe_ids": len(ids) - len(fset), "base_rows": len(bset), "missing_from_features": len(bset - fset), "extra_in_features": len(fset - bset),
               "invalid_ids": sum(1 for r in ids if not isinstance(r, str) or not r), "sorted_by_recipe_id": ids == sorted(ids), "null_counts": {k: v for k, v in nulls.items() if v},
               "empty_strings": empties, "records_n_chars_lt_60": short, "schema": [str(f) for f in pf.schema_arrow], "seconds": round(time.time() - t0, 1)}
        res["verdict"] = "COMPLETE_REUSABLE" if (res["rows"] == res["base_rows"] and not res["duplicate_recipe_ids"] and not res["missing_from_features"] and not res["extra_in_features"] and not res["invalid_ids"]) else "PARTIAL_UNKNOWN"
        self.man.set_phase("audit", **res)
        return res

    # ------------------------------------------------------------------ exact
    def _input_key(self, *parts):
        return hashlib.sha256(json.dumps(parts, sort_keys=True, default=str).encode()).hexdigest()

    def exact(self, resume=True):
        key = self._input_key(sha256_file(self.feat), sha256_file(self.base), sha256_file(self.usage), self.sample)
        out = self.run / "exact.parquet"
        ph = self.man.phase("exact")
        if resume and ph.get("input_key") == key and verify_parquet(out, ph.get("rows", -1), ph.get("content_hash", "")):
            self.log("exact: valid, skipped")
            return pq.read_table(out).to_pandas()
        df = EX.load_frame(self.feat, self.base, self.usage, self.a1, self.sample)
        tbl, stats = EX.build_exact(df)
        w = atomic_write_parquet(pa.Table.from_pandas(tbl, preserve_index=False), out)
        reps = tbl[tbl.recipe_id == tbl.group_representative_id]
        self.man.set_phase("exact", input_key=key, rows=w["rows"], content_hash=w["content_hash"], stats=stats, groups=int(tbl.duplicate_group_id.nunique()), representatives=int(len(reps)),
                           multi_member_groups=int((tbl.groupby("duplicate_group_id").size() > 1).sum()), records_in_multi_member_groups=int((tbl.group_size > 1).sum()))
        self.log("exact: %d recipes -> %d groups" % (len(tbl), len(reps)))
        return tbl

    # ------------------------------------------------------------------ candidates (+ compact view)
    def candidates(self, resume=True, dry=False):
        ex = self.man.phase("exact")
        key = self._input_key(ex["content_hash"], self.cfg["chunk_size"], self.cfg["n_buckets"], self.cfg["max_pairs"])
        ph = self.man.phase("candidates")
        view, idf = self.run / "reps_view.parquet", self.run / "idf.npy"
        parts = self.man.d.get("candidate_partitions", [])
        if resume and ph.get("input_key") == key and view.exists() and parts and all((self.run / p["path"]).exists() and verify_parquet(self.run / p["path"], p["rows"], p["content_hash"]) for p in parts):
            self.log("candidates: %d partitions valid, skipped" % len(parts))
            return parts
        if dry:
            self.log("candidates: would (re)generate")
            return parts
        tbl = pq.read_table(self.run / "exact.parquet").to_pandas()
        reps = tbl[tbl.recipe_id == tbl.group_representative_id].sort_values("recipe_id").reset_index(drop=True)
        t0 = time.time()
        vstats = RV.build(self.feat, reps.set_index("recipe_id", drop=False)[["source_id", "locale", "cuisine_if_explicit"]], reps.recipe_id.tolist(), self.cond, view, idf)
        self.log("reps view built %.0fs rss=%.2fGB" % (time.time() - t0, rss_gb()))
        diag, parts = CAND.generate(view, self.run, self.cfg["chunk_size"], self.cfg["n_buckets"], self.cfg["max_pairs"])
        self.man.d["candidate_partitions"] = parts
        self.man.d["partitions"] = {}  # downstream partition status is invalid when the candidate set changes
        self.man.set_phase("candidates", input_key=key, view=vstats, diag=diag, peak_rss_gb=round(rss_gb(), 3), seconds=round(time.time() - t0), view_sha256=sha256_file(view),
                           candidate_set_hash=hashlib.sha256("".join(p["input_hash"] for p in parts).encode()).hexdigest())
        self.log("candidates: %d pairs in %d partitions (%.0fs, rss %.2fGB)" % (diag["pairs_total_candidates"], len(parts), time.time() - t0, rss_gb()))
        return parts

    # ------------------------------------------------------------------ partition engine
    def _valid(self, kind, p, out_name, in_key, in_val):
        e = self.man.part(kind, p["pid"])
        return e.get("status") == "DONE" and e.get(in_key) == in_val and e.get("rows") == p["rows"] and verify_parquet(self.run / "parts" / out_name, p["rows"], e.get("output_hash", ""))

    def _execute(self, kind, fn, tasks, only=None):
        todo = [t for t in tasks if only is None or t["pid"] == only]
        if not todo:
            return 0
        ctx = mp.get_context("spawn")
        stop = ctx.Event()
        done = {"n": 0, "pairs": 0}
        t0 = time.time()
        wd = Watchdog(self.run / ("watchdog_%s.jsonl" % kind), self.cfg["max_memory_gb"], stop, lambda: {"phase": kind, "partitions_done": done["n"], "pairs": done["pairs"], "pairs_per_s": round(done["pairs"] / max(1e-9, time.time() - t0))}, period=self.watch_period)
        wd.start()
        per_worker = max(0.5, (self.cfg["max_memory_gb"] - 0.6) / self.cfg["threads"])
        tripped = False
        with ctx.Pool(self.cfg["threads"], initializer=PW.init_worker, initargs=(stop, per_worker)) as pool:
            for r in pool.imap_unordered(fn, todo):
                if r["status"] == "DONE":
                    done["n"] += 1
                    done["pairs"] += r["rows"]
                    e = {k: v for k, v in r.items() if k not in ("pid",)}
                    ik = "input_hash" if kind == "features" else "feat_hash"
                    e[ik] = next(t for t in todo if t["pid"] == r["pid"])[ik]
                    self.man.set_part(kind, r["pid"], **e)
                    self.man.save()
                    self.log("%s %s rows=%d %.1fs rss=%.2fGB" % (kind, r["pid"], r["rows"], r["seconds"], r["peak_rss_gb"]))
                else:
                    self.man.set_part(kind, r["pid"], status=r["status"], detail=r.get("detail"))
                    self.man.save()
                    self.log("%s %s %s" % (kind, r["pid"], r["status"]))
                    if r["status"] == "MEMORY_GUARD_TRIGGERED":
                        tripped = True
                        stop.set()
        wd.halt()
        peak = max(wd.peak_gb, 0.0)
        self.man.set_phase(kind, peak_tree_rss_gb=round(peak, 3), last_run_seconds=round(time.time() - t0), last_run_partitions=done["n"], last_run_pairs=done["pairs"])
        if tripped or wd.triggered:
            self.man.set_phase(kind, status="MEMORY_GUARD_TRIGGERED")
            self.log("MEMORY_GUARD_TRIGGERED (checkpoint written; rerun with --resume)")
            raise MemoryGuardExit(MEMORY_GUARD_EXIT)
        return done["n"]

    def features(self, resume=True, only=None, dry=False, limit=0):
        parts = self.man.d["candidate_partitions"]
        tasks = []
        for p in parts:
            out = "%s.feat.parquet" % p["pid"]
            if resume and self._valid("features", p, out, "input_hash", p["input_hash"]):
                continue
            tasks.append({"pid": p["pid"], "in_path": str(self.run / p["path"]), "out_path": str(self.run / "parts" / out), "view_path": str(self.run / "reps_view.parquet"), "idf_path": str(self.run / "idf.npy"),
                          "input_hash": p["input_hash"], "rows": p["rows"]})
        self.log("features: %d/%d partitions to run" % (len(tasks), len(parts)))
        if dry:
            return len(tasks)
        tasks = tasks[:limit] if limit else tasks
        n = self._execute("features", PW.run_features, tasks, only)
        bad = [p["pid"] for p in parts if not self._valid("features", p, "%s.feat.parquet" % p["pid"], "input_hash", p["input_hash"])]
        self.man.set_phase("features", status="DONE" if not bad else "INCOMPLETE", invalid_partitions=bad)
        return n

    def score(self, resume=True, only=None, dry=False, limit=0):
        parts = self.man.d["candidate_partitions"]
        tasks = []
        for p in parts:
            fe = self.man.part("features", p["pid"])
            if fe.get("status") != "DONE":
                raise RuntimeError("features partition %s not DONE" % p["pid"])
            out = "%s.score.parquet" % p["pid"]
            if resume and self._valid("score", p, out, "feat_hash", fe["output_hash"]):
                continue
            tasks.append({"pid": p["pid"], "feat_path": str(self.run / "parts" / ("%s.feat.parquet" % p["pid"])), "out_path": str(self.run / "parts" / out), "feat_hash": fe["output_hash"], "rows": p["rows"]})
        self.log("score: %d/%d partitions to run" % (len(tasks), len(parts)))
        if dry:
            return len(tasks)
        tasks = tasks[:limit] if limit else tasks
        n = self._execute("score", PW.run_score, tasks, only)
        bad = [p["pid"] for p in parts if not self._valid("score", p, "%s.score.parquet" % p["pid"], "feat_hash", self.man.part("features", p["pid"]).get("output_hash"))]
        self.man.set_phase("score", status="DONE" if not bad else "INCOMPLETE", invalid_partitions=bad,
                           kept_pairs=sum(self.man.part("score", p["pid"]).get("kept", 0) for p in parts), family_edges=sum(self.man.part("score", p["pid"]).get("edges", 0) for p in parts))
        return n

    # ------------------------------------------------------------------ family candidates + final tables
    def family(self):
        t0 = time.time()
        parts = self.man.d["candidate_partitions"]
        exact = pq.read_table(self.run / "exact.parquet").to_pandas()
        view = pq.read_table(self.run / "reps_view.parquet", columns=["rep_id", "title_key"], memory_map=True)
        rep_ids, title_key = view.column("rep_id").to_pylist(), view.column("title_key").to_pylist()
        kept = FAM.collect_kept(self.run, [p["pid"] for p in parts], rep_ids)
        out = FAM.build(exact, rep_ids, title_key, kept, self.run / "reps_view.parquet", np.load(self.run / "idf.npy"))
        m, reps = out["members"], out["reps"]
        dg = m[["duplicate_group_id", "recipe_id", "source_family", "source_id", "group_representative_id", "duplicate_relation", "duplicate_status", "group_size", "group_cross_source"]].sort_values(["duplicate_group_id", "recipe_id"])
        fm = m[["recipe_family_id", "recipe_id", "duplicate_group_id", "source_family", "source_id", "family_role", "edge_confidence", "representative_recipe_id", "dish_family_candidate_id"]].assign(
            family_method="PROVISIONAL_STAR_V1", calibrated=False).sort_values(["recipe_family_id", "recipe_id"])
        tables = {"duplicate_group_members_v1": dg, "recipe_family_members_v1": fm, "dish_family_candidates_v1": out["dish"], "candidate_pairs_v1": kept, "recipe_family_consistency_v1": out["consistency"]}
        hashes = {}
        for k, d in tables.items():
            hashes[k] = atomic_write_parquet(pa.Table.from_pandas(d.reset_index(drop=True), preserve_index=False), self.ID / ("%s%s.parquet" % (k, self.suf)))["content_hash"]
        have = set(pq.ParquetFile(self.base).schema_arrow.names)
        bcols = pq.read_table(self.base, columns=[c for c in EX.BASE_COLS + ["title_raw"] if c in have]).to_pandas().rename(columns={"recipe_family_id": "legacy_family_id"})
        bcols = bcols[[c for c in bcols.columns if c == "recipe_id" or c not in m.columns]]
        m = m.merge(bcols, on="recipe_id", how="left", validate="1:1")  # downstream 07I tools expect the base columns next to the identity columns
        m.to_pickle(self.ID / ("_identity_work%s.pkl" % self.suf))
        reps.merge(exact[["recipe_id", "source_family", "source_id", "usage_class", "quality_tier", "group_representative_id", "locale", "cuisine_if_explicit"]], on="recipe_id", how="left").to_pickle(self.ID / ("_reps_work%s.pkl" % self.suf))
        ex = self.man.phase("exact")
        cd = self.man.phase("candidates")["diag"]
        sc = self.man.phase("score")
        summary = {"recipes": int(len(exact)), "exact_duplicate_groups": ex["multi_member_groups"], "records_in_multi_member_groups": ex["records_in_multi_member_groups"], "logical_recipes_exact_dedup": ex["representatives"],
                   "exact_stats": ex["stats"], "candidate_pairs": cd["pairs_total_candidates"], "candidate_diag": cd, "diagnostics": cd, "scored_kept_pairs": int(len(kept)), "provisional_family_edges": int(kept.family_edge.sum()),
                   "families": out["n_families"], "multi_member_families_over_reps": int((reps.groupby("recipe_family_id").size() > 1).sum()), "dish_family_candidates": int(len(out["dish"])),
                   "family_review_status": out["consistency"].family_review_status.value_counts().to_dict() if len(out["consistency"]) else {}, "output_hashes": hashes, "seconds": round(time.time() - t0)}
        summary["final_hash"] = hashlib.sha256(json.dumps(hashes, sort_keys=True).encode()).hexdigest()
        (self.root / "reports/step07i" / ("_identity_summary%s.json" % self.suf)).write_text(json.dumps(summary, indent=1, default=str))
        self.man.set_phase("family-candidates", status="DONE", summary=summary)
        self.log(json.dumps({k: summary[k] for k in ("recipes", "logical_recipes_exact_dedup", "candidate_pairs", "scored_kept_pairs", "provisional_family_edges", "families", "final_hash")}))
        return summary
