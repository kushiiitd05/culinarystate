"""Polite single-file acquisition with snapshot metadata (SNAP- ledger input).

No crawling: one URL -> one file. Re-downloads are skipped when the file exists
unless `force=True`, so raw snapshots stay pinned by hash.
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import requests

USER_AGENT = "CulinaryState-research/0.1 (IIIT Delhi course project; kush23296@iiitd.ac.in)"


@dataclass(frozen=True)
class Snapshot:
    url: str
    local_path: str
    sha256: str
    bytes: int
    retrieved_at: str
    http_status: int | None


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch(url: str, dest: Path, force: bool = False, timeout: int = 60, pause_s: float = 1.0) -> Snapshot:
    dest = Path(dest)
    meta_path = dest.with_suffix(dest.suffix + ".snap.json")
    if dest.exists() and meta_path.exists() and not force:
        return Snapshot(**json.loads(meta_path.read_text()))
    dest.parent.mkdir(parents=True, exist_ok=True)
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=timeout)
    resp.raise_for_status()
    dest.write_bytes(resp.content)
    snap = Snapshot(url=url, local_path=str(dest), sha256=sha256_file(dest), bytes=dest.stat().st_size,
                    retrieved_at=datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
                    http_status=resp.status_code)
    meta_path.write_text(json.dumps(asdict(snap), indent=2))
    time.sleep(pause_s)
    return snap
