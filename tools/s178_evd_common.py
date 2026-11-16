"""Shared helpers for the S178 EVD lane tools (tools/s178_evd_*.py). Read-only on ledgers; no timestamps in outputs.

Every EVD-lane tool writes deterministic, counts-only JSON (sorted keys, trailing newline) so that two runs on the same
inputs are byte-identical. Nothing here writes under ledgers/.
"""
from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

PROTECTED = ("EVD", "COND", "SRC", "MEAS", "SNAP")
DEFAULT_OUT = "reports/s178/evd"


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for b in iter(lambda: fh.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def protected_hashes(root: Path = ROOT, names: tuple[str, ...] = PROTECTED) -> dict[str, str]:
    return {n: sha256_file(root / "ledgers" / "data" / f"{n}.jsonl") for n in names}


def read_ledger(path: Path) -> tuple[dict[str, dict], list[dict]]:
    """-> (latest record per id, every version line in file order). Latest = highest version (ties: later line)."""
    latest: dict[str, dict] = {}
    lines: list[dict] = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            r = json.loads(line)
            lines.append(r)
            if r["id"] not in latest or r["version"] >= latest[r["id"]]["version"]:
                latest[r["id"]] = r
    return latest, lines


def counter_dict(c: Counter, top: int | None = None) -> dict:
    items = sorted(c.items(), key=lambda kv: (-kv[1], str(kv[0])))
    return {str(k): v for k, v in (items[:top] if top else items)}


def pct(a: int, b: int) -> float | None:
    return round(100.0 * a / b, 2) if b else None


def dumps(obj) -> str:
    return json.dumps(obj, indent=1, sort_keys=True, ensure_ascii=False) + "\n"


def write_new_or_same(path: Path, text: str) -> str:
    """Write ``text`` to ``path`` (utf-8, LF). Returns the sha256 of the text."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    return sha256_bytes(text.encode("utf-8"))


def md_table(header: list[str], rows: list[list], align_right: tuple[int, ...] = ()) -> str:
    def cell(x):
        if isinstance(x, int) and not isinstance(x, bool):
            return f"{x:,}"
        if isinstance(x, float):
            return f"{x:,.2f}"
        return "" if x is None else str(x)
    sep = ["---:" if i in align_right else "---" for i in range(len(header))]
    out = ["| " + " | ".join(header) + " |", "|" + "|".join(sep) + "|"]
    out += ["| " + " | ".join(cell(x) for x in r) + " |" for r in rows]
    return "\n".join(out)
