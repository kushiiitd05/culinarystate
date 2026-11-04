"""DRAFT_PENDING_29diag_PREREG -- 29-diag TRANSITION_BOOTSTRAP_V0 diagnostic runner entry (NON_CITABLE).

Spine row 29-diag (``registry/execution_spine_v2.csv``) and the plan's Step 29 card: an early
diagnostic on FROZEN bootstrap data only (R-12), HARD on the 15.0 rulings and the 15a.R
RESERVED seal "recorded before any 29-diag read", with Kush's pre-registration sign-off.
It has no pass gate and its output can never be cited (G15-1/2/3 cannot be met by it).

``run_bootstrap_diag`` refuses, listing every blocker, unless all of these hold:

* ``SNAPSHOT_NOT_FROZEN``: ``snapshot_id`` is a frozen bootstrap snapshot. No 15a freeze
  exists and no freeze-record format is defined, so ``frozen_bootstrap_snapshot_ids``
  returns the empty set: every id (including the live ledger or "ES-1.1") is refused.
* ``NO_SIGNED_15_0``: DECISIONS.md holds a complete signed 15.0 ruling (the seal's parser).
* ``SEAL_COMMITMENT_MISSING`` / ``SEAL_DECISION_NOT_SIGNED``: the 15a.R commitment exists
  and names a signed 15.0 decision.
* ``SEALED_LIST_MISSING`` / ``SEAL_VERIFY_FAILED``: the sealed list is supplied and verifies.
* ``DIAG_PREREG_UNSIGNED``: a signed 29-diag pre-registration exists (none; format undefined).

The runner callable gets a ``DiagContext`` that only offers reserved-group exclusion and the
DIAGNOSTIC mode; its return value is wrapped, so it cannot relabel the output as citable.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Optional, Sequence

from culinarystate.evaluation import leakage as lk

STATUS = "DRAFT_PENDING_29diag_PREREG"
DIAG_LABELS = ("NON_CITABLE", "DIAGNOSTIC_ONLY", "BOOTSTRAP_UNVERIFIED", "COND_UNAUDITED",
               "PRIOR_EXPOSURE_REANALYSIS", "PROVISIONAL_08A")


class DiagRefused(RuntimeError):
    """29-diag may not run (or an output may not be cited); ``blockers`` lists every reason."""

    def __init__(self, blockers: Iterable[str]):
        self.blockers = list(blockers)
        super().__init__("29-diag refused: " + "; ".join(self.blockers))


def frozen_bootstrap_snapshot_ids(root: Path | str) -> frozenset[str]:
    """Ids of frozen 15a bootstrap snapshots. Empty: no 15a freeze or freeze-record format exists."""
    return frozenset()


def diag_preregistration_signed(root: Path | str) -> bool:
    """Whether Kush has signed the 29-diag pre-registration. False: no record or format exists."""
    return False


def _read_commitment(path: Path) -> tuple[Optional[dict], list[str]]:
    if not path.is_file():
        return None, [f"SEAL_COMMITMENT_MISSING: no 15a.R commitment at {path.name}"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return None, [f"SEAL_COMMITMENT_UNREADABLE: {type(exc).__name__}"]
    if not isinstance(data, dict):
        return None, ["SEAL_COMMITMENT_UNREADABLE: not a JSON object"]
    return data, []


def _check(root: Path, snapshot_id: str, commitment_path: Optional[Path],
           sealed_list_path: Optional[Path]) -> tuple[list[str], Optional[dict], Optional[frozenset[str]]]:
    from culinarystate.lineage import reserved_seal as rs  # lazy: the seal module pulls in pandas

    blockers: list[str] = []
    if snapshot_id not in frozen_bootstrap_snapshot_ids(root):
        blockers.append(f"SNAPSHOT_NOT_FROZEN: {snapshot_id!r} is not a frozen 15a bootstrap snapshot")
    try:
        signed = rs.find_15_0_rulings((root / "DECISIONS.md").read_text(encoding="utf-8"))
    except OSError:
        signed = []
        blockers.append("DECISIONS_UNREADABLE: DECISIONS.md missing")
    if not signed:
        blockers.append("NO_SIGNED_15_0: no complete signed 15.0 ruling in DECISIONS.md")
    commitment, errs = _read_commitment(Path(commitment_path) if commitment_path else root / rs.COMMITMENT_PATH)
    blockers.extend(errs)
    if commitment is not None and commitment.get("decision_id") not in signed:
        blockers.append("SEAL_DECISION_NOT_SIGNED: the commitment's decision is not a signed 15.0 ruling")
    reserved: Optional[frozenset[str]] = None
    if sealed_list_path is None or not Path(sealed_list_path).is_file():
        blockers.append("SEALED_LIST_MISSING: pass the sealed list (kept outside git)")
    elif commitment is not None:
        try:
            reserved = lk.load_sealed_reserved(commitment, Path(sealed_list_path).read_bytes())
        except lk.LeakageRefused as exc:
            blockers.append("SEAL_VERIFY_FAILED: " + "; ".join(exc.blockers))
    if not diag_preregistration_signed(root):
        blockers.append("DIAG_PREREG_UNSIGNED: no signed 29-diag pre-registration (Kush) exists")
    return blockers, commitment, reserved


def collect_diag_blockers(*, root: Path | str, snapshot_id: str, commitment_path: Optional[Path | str] = None,
                          sealed_list_path: Optional[Path | str] = None) -> list[str]:
    """Every reason 29-diag would refuse now (empty list = it could run)."""
    blockers, _, _ = _check(Path(root), snapshot_id, Path(commitment_path) if commitment_path else None,
                            Path(sealed_list_path) if sealed_list_path else None)
    return blockers


@dataclass
class DiagContext:
    """What a 29-diag runner may use: DEV-row filtering against the seal and the DIAGNOSTIC mode."""
    snapshot_id: str
    unit: str
    root: Path
    _reserved: frozenset[str] = field(repr=False)
    exclusions: list[dict[str, Any]] = field(default_factory=list)

    def filter_dev_rows(self, rows: Sequence[Mapping[str, Any]], *, id_column: str,
                        group_columns: Sequence[str]) -> list[Mapping[str, Any]]:
        """Rows outside every RESERVED component (EVD-shaped rows; seal unit from the commitment)."""
        seal = {str(r.get(id_column)): lk.seal_group_id(r, self.unit) for r in rows}
        out = lk.exclude_reserved(rows, id_column=id_column, group_columns=group_columns,
                                  row_seal_group=seal, reserved=self._reserved)
        lk.assert_reserved_excluded([str(r.get(id_column)) for r in out.kept_rows], row_seal_group=seal,
                                    reserved=self._reserved)
        self.exclusions.append(out.report())
        return list(out.kept_rows)

    def require_mode(self, mode: str) -> tuple[str, ...]:
        return lk.require_mode(mode, root=self.root)


def run_bootstrap_diag(snapshot_id: str, runner: Callable[[DiagContext], Any], *, root: Path | str,
                       commitment_path: Optional[Path | str] = None,
                       sealed_list_path: Optional[Path | str] = None) -> dict[str, Any]:
    """The only 29-diag entry: every check first, then ``runner(context)``; output is NON_CITABLE."""
    base = Path(root)
    blockers, commitment, reserved = _check(base, snapshot_id, Path(commitment_path) if commitment_path else None,
                                            Path(sealed_list_path) if sealed_list_path else None)
    if blockers:
        raise DiagRefused(blockers)
    assert commitment is not None and reserved is not None
    ctx = DiagContext(snapshot_id=snapshot_id, unit=str(commitment.get("unit")), root=base, _reserved=reserved)
    result = runner(ctx)
    return {"status": STATUS, "labels": list(DIAG_LABELS), "citable": False, "snapshot_id": snapshot_id,
            "seal_payload_sha256": commitment.get("payload_sha256"), "exclusions": list(ctx.exclusions),
            "result": result}


def assert_citable(output: Mapping[str, Any]) -> None:
    """Refuse to cite a 29-diag (or any NON_CITABLE) output."""
    if output.get("citable") is not True or "NON_CITABLE" in (output.get("labels") or []):
        raise DiagRefused(["NON_CITABLE: 29-diag output is diagnostic only and can never be cited"])
