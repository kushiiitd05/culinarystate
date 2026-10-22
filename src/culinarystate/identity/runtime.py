"""STEP 07I-R runtime: atomic parquet writes, content hashes, the resumable run manifest and the memory watchdog.
Python 3.8 compatible (the A100 server runs 3.8). No recipe text lives here."""
from __future__ import annotations

import hashlib
import json
import os
import threading
import time
from pathlib import Path

import numpy as np
import pyarrow as pa
import pyarrow.parquet as pq

try:
    import psutil
except ImportError:  # watchdog degrades to RSS via resource
    psutil = None

MEMORY_GUARD_EXIT = 75  # EX_TEMPFAIL: checkpoint written, safe to resume


class MemoryGuardTriggered(RuntimeError):
    pass


def rss_gb(tree: bool = False) -> float:
    if psutil is None:
        import resource
        return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e9
    p = psutil.Process()
    total = p.memory_info().rss
    if tree:
        for c in p.children(recursive=True):
            try:
                total += c.memory_info().rss
            except psutil.Error:
                pass
    return total / 1e9


def swap_used_gb() -> float:
    return psutil.swap_memory().used / 1e9 if psutil else float("nan")


def sha256_file(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def table_content_hash(t: pa.Table) -> str:
    """layout-independent hash of table content (schema names/types + values + nulls); stable across machines for identical values"""
    h = hashlib.sha256()
    for name in t.column_names:
        col = t.column(name).combine_chunks()
        h.update(("%s|%s|%d;" % (name, col.type, len(col))).encode())
        if pa.types.is_boolean(col.type) or pa.types.is_integer(col.type) or pa.types.is_floating(col.type):
            h.update(np.asarray(col.is_null()).tobytes())
            vals = col.fill_null(0) if not pa.types.is_boolean(col.type) else col.fill_null(False)
            h.update(np.ascontiguousarray(np.asarray(vals)).tobytes())
        else:
            for v in col.to_pylist():
                h.update(b"\x00" if v is None else (v if isinstance(v, bytes) else json.dumps(v, sort_keys=True).encode()))
                h.update(b"\x1f")
    return h.hexdigest()


def arrays_hash(*arrs) -> str:
    h = hashlib.sha256()
    for a in arrs:
        h.update(np.ascontiguousarray(a).tobytes())
    return h.hexdigest()


def atomic_write_parquet(table: pa.Table, path, compression="zstd") -> dict:
    """write tmp -> fsync -> read back -> verify rows/hash -> atomic rename. Returns {rows, content_hash, bytes}"""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp.%d" % os.getpid())
    try:
        pq.write_table(table, tmp, compression=compression)
        with open(tmp, "rb") as f:
            os.fsync(f.fileno())
        back = pq.read_table(tmp)
        want = table_content_hash(table)
        if back.num_rows != table.num_rows or table_content_hash(back) != want:
            raise IOError("atomic write verification failed for %s" % path)
        os.replace(tmp, path)
    finally:
        if tmp.exists():
            tmp.unlink()
    return {"rows": table.num_rows, "content_hash": want, "bytes": path.stat().st_size}


def verify_parquet(path, rows: int, content_hash: str) -> bool:
    try:
        path = Path(path)
        if not path.exists():
            return False
        if pq.ParquetFile(path).metadata.num_rows != rows:
            return False
        return table_content_hash(pq.read_table(path)) == content_hash
    except Exception:
        return False


class Manifest:
    """JSON run manifest; single writer (parent process); every update is an atomic replace"""

    def __init__(self, path):
        self.path = Path(path)
        self.d = json.loads(self.path.read_text()) if self.path.exists() else {"schema": "step07i_identity_run_v1", "phases": {}, "partitions": {}, "config": {}}

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_name(self.path.name + ".tmp")
        tmp.write_text(json.dumps(self.d, indent=1, sort_keys=True, default=str))
        with open(tmp, "rb") as f:
            os.fsync(f.fileno())
        os.replace(tmp, self.path)

    def phase(self, name: str) -> dict:
        return self.d["phases"].setdefault(name, {})

    def set_phase(self, name: str, **kw):
        self.phase(name).update(kw)
        self.save()

    def part(self, kind: str, pid: str) -> dict:
        return self.d["partitions"].setdefault(kind, {}).get(pid, {})

    def set_part(self, kind: str, pid: str, **kw):
        self.d["partitions"].setdefault(kind, {}).setdefault(pid, {}).update(kw)


class Watchdog(threading.Thread):
    """samples process-tree RSS / swap / progress every `period` s into a jsonl log; sets `stop_event` when the tree exceeds the ceiling"""

    def __init__(self, log_path, ceiling_gb: float, stop_event, progress=None, period: float = 10.0):
        super().__init__(daemon=True)
        self.log_path, self.ceiling, self.stop_event, self.progress, self.period = Path(log_path), ceiling_gb, stop_event, progress, period
        self.peak_gb = 0.0
        self.triggered = False
        self._halt = threading.Event()
        self.t0 = time.time()

    def run(self):
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.log_path, "a") as f:
            while not self._halt.wait(self.period):
                r = rss_gb(tree=True)
                self.peak_gb = max(self.peak_gb, r)
                rec = {"t": round(time.time() - self.t0, 1), "rss_tree_gb": round(r, 3), "swap_used_gb": round(swap_used_gb(), 2)}
                if self.progress:
                    rec.update(self.progress())
                f.write(json.dumps(rec) + "\n")
                f.flush()
                if r > self.ceiling and not self.triggered:
                    self.triggered = True
                    self.stop_event.set()
                    f.write(json.dumps({"event": "MEMORY_GUARD_TRIGGERED", "rss_tree_gb": round(r, 3), "ceiling_gb": self.ceiling}) + "\n")
                    f.flush()

    def halt(self):
        self._halt.set()
