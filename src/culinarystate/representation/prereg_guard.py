"""G35-PRE engineering control (THR-35P-01).

Refuses to run any evaluation unless the pre-registration document has been
hashed (sha256) and signed by humans. This module never signs anything: it can
only produce an UNSIGNED template and verify records humans completed.
"""
from __future__ import annotations

import functools
import hashlib
import json
from datetime import date as _date
from pathlib import Path
from typing import Any, Callable, TypeVar

F = TypeVar("F", bound=Callable[..., Any])

UNSIGNED_STATUS = "UNSIGNED_TEMPLATE"


class PreregNotSigned(RuntimeError):
    """Raised when the G35-PRE gate is not satisfied."""


MIN_SIGNERS = 2  # 35.0 card: Kush and Parv both sign; a recorded override covers an absent second author


def sha256_file(path: Path | str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sign_record_template(prereg_path: Path | str) -> dict[str, Any]:
    """Return an UNSIGNED record: current sha256, empty signers, empty date."""
    p = Path(prereg_path)
    if not p.is_file():
        raise PreregNotSigned(f"pre-registration document not found: {p}")
    return {
        "status": UNSIGNED_STATUS,
        "document": p.name,
        "sha256": sha256_file(p),
        "signers": [],
        "date": "",
    }


def _valid_signers(signers: Any) -> bool:
    if not isinstance(signers, list) or not signers:
        return False
    for s in signers:
        if not isinstance(s, str) or not s.strip() or s.strip().startswith("<"):
            return False
    return True


def _valid_override(value: Any) -> bool:
    """A single signer is allowed only with a written reason and the name of who accepted it."""
    return (isinstance(value, dict) and isinstance(value.get("reason"), str) and bool(value["reason"].strip())
            and isinstance(value.get("by"), str) and bool(value["by"].strip()))


def _valid_date(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        _date.fromisoformat(value)
    except ValueError:
        return False
    return True


def require_signed_prereg(prereg_path: Path | str, hash_file: Path | str) -> str:
    """Return the verified sha256 or raise PreregNotSigned."""
    doc, hf = Path(prereg_path), Path(hash_file)
    if not hf.is_file():
        raise PreregNotSigned(f"hash file missing: {hf}")
    if not doc.is_file():
        raise PreregNotSigned(f"pre-registration document missing: {doc}")
    try:
        rec = json.loads(hf.read_text(encoding="utf-8"))
    except (ValueError, OSError) as exc:
        raise PreregNotSigned(f"hash file unreadable: {hf} ({exc})") from exc
    if not isinstance(rec, dict):
        raise PreregNotSigned("hash file is not a JSON object")
    recorded = rec.get("sha256")
    if not isinstance(recorded, str) or len(recorded) != 64:
        raise PreregNotSigned("hash file records no valid sha256")
    current = sha256_file(doc)
    if recorded.lower() != current:
        raise PreregNotSigned(
            f"document sha256 differs from signed record (signed {recorded}, now {current})"
        )
    if rec.get("status") == UNSIGNED_STATUS or not _valid_signers(rec.get("signers")):
        raise PreregNotSigned("no valid signer names recorded (unsigned template?)")
    if len({n.strip().lower() for n in rec["signers"]}) < MIN_SIGNERS and not _valid_override(rec.get("single_signer_override")):
        raise PreregNotSigned(
            f"{MIN_SIGNERS} distinct signers required (Kush and Parv), or a single_signer_override with a reason"
        )
    if not _valid_date(rec.get("date")):
        raise PreregNotSigned("no valid ISO signing date recorded")
    return current


def evaluation_entry(fn: F) -> F:
    """Decorator: run the guard before `fn`. `fn` must be called with
    keyword args `prereg_path` and `hash_file`, which are consumed here."""

    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            prereg_path = kwargs.pop("prereg_path")
            hash_file = kwargs.pop("hash_file")
        except KeyError as exc:
            raise PreregNotSigned(f"missing required argument {exc}") from exc
        require_signed_prereg(prereg_path, hash_file)
        return fn(*args, **kwargs)

    return wrapper  # type: ignore[return-value]
