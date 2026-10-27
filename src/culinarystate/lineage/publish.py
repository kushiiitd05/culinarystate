"""08a real run: copy a verified scratch result into the real ledgers (D-032).

Allowed: new ledger files, and appends to STUDY.jsonl and _ids.jsonl whose existing bytes are unchanged.
Everything else must be byte-identical between the real and the scratch data directories.
"""
from __future__ import annotations

from pathlib import Path

APPEND_ONLY = ("STUDY.jsonl", "_ids.jsonl")


class PublishRefused(RuntimeError):
    """Scratch result does not fit the D-032 write rules."""


def plan_publish(real: Path, scratch: Path) -> dict[str, list[str]]:
    real, scratch = Path(real), Path(scratch)
    plan: dict[str, list[str]] = {"new": [], "append": []}
    real_names = {p.name for p in real.iterdir() if p.is_file()}
    scr_names = {p.name for p in scratch.iterdir() if p.is_file()}
    if real_names - scr_names:
        raise PublishRefused(f"scratch lacks real files: {sorted(real_names - scr_names)}")
    for name in sorted(scr_names):
        s = (scratch / name).read_bytes()
        if name not in real_names:
            plan["new"].append(name)
            continue
        r = (real / name).read_bytes()
        if s == r:
            continue
        if name in APPEND_ONLY and s.startswith(r):
            plan["append"].append(name)
        else:
            raise PublishRefused(f"{name}: differs and is not an allowed append")
    for name in plan["new"]:
        if (real / name).exists():
            raise PublishRefused(f"{name}: would overwrite")
    return plan


def apply_publish(real: Path, scratch: Path, plan: dict[str, list[str]]) -> None:
    real, scratch = Path(real), Path(scratch)
    for name in plan["new"]:
        (real / name).write_bytes((scratch / name).read_bytes())
    for name in plan["append"]:
        have = (real / name).stat().st_size
        with (real / name).open("ab") as f:
            f.write((scratch / name).read_bytes()[have:])
