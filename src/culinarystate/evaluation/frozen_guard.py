"""Frozen-input guard for the D5 scoring harness (S178 lane H1H3H; board T8-C20-R3 consumer). AI_DRAFTED, DRAFT.

The D5 items (router accuracy, H1, H3, D4, ablations) may run only on the frozen benchmark, never on drafts, and the
scorer may not change after the freeze. This module enforces that before any number is computed. It only reads,
hashes and compares: it never writes, proposes or completes a freeze record (a test checks that the module has no
file-writing call), and an AI output is never an approval (D-071).

REAL mode (``check_real_inputs`` / ``require_real_inputs``). The scorer runs only if a freeze record exists with

- ``record`` = ``FREEZE_D5_BENCHMARK`` and ``status`` = ``FROZEN``;
- approvals by named humans: each approver string is exactly one of ``freeze_records.HUMANS``, carries an ISO date,
  and no approval entry contains an AI marker (agent, AI, Claude, the ksh / prv personas, ...), except the D-085
  delegate ``ksh+prv (AI, D-085)`` with ``decision`` D-085 and ``label`` NO_HUMAN_SIGNOFF_D085, which stands for
  both humans and makes the run ``signoff`` AI_DELEGATED_D085 (S179). By default BOTH
  humans must approve (the conservative reading of the S178 amendment C8, "both humans confirm");
- ``files``: relative path -> sha256 for every benchmark and reference file the scorer reads; each listed file must
  exist and match its bytes, and every file the scorer is given must be listed;
- ``code_sha256``: relative path -> sha256 for every scorer module (``scorer_code_paths``), so that "no code change
  after freeze" (T8-C01-R1 acceptance) is checked, not assumed;
- ``prereg_sha256``: the sha256 of the pre-registration text the benchmark was frozen under.

Record shape (documented here; the humans or the Mac scribe write it, never this code)::

    {"record": "FREEZE_D5_BENCHMARK", "freeze_id": "D5-BENCH-<date>", "status": "FROZEN",
     "files": {"benchmark/d5/<frozen>.csv": "<sha256>", "ledgers/data/EVD.jsonl": "<sha256>", ...},
     "code_sha256": {"src/culinarystate/evaluation/d5_scoring.py": "<sha256>", ...},
     "prereg_sha256": "<sha256 of reports/del5/d5_benchmark_preregistration_DRAFT.md as signed>",
     "approvals": [{"approved_by": "Kush Tokas", "approved_date": "YYYY-MM-DD"},
                   {"approved_by": "Parv Goyal", "approved_date": "YYYY-MM-DD"}]}

The ``freeze_records`` single-approver shape (``approved_by`` + ``approved_date``) is read too; with the default
policy it fails unless every required human is named.

FIXTURE mode (``check_fixture_inputs`` / ``require_fixture_inputs``). Inputs must sit inside the synthetic fixture
directory, be listed with a matching sha256 in its ``manifest.json`` (``synthetic: true``, ``stamp`` = ``STAMP``), and
must not live under ``benchmark/``, ``annotation/``, ``ledgers/`` or ``data/``. Row-level checks (``SYN-`` qids,
synthetic EVD ids) are in ``assert_synthetic_rows`` / ``assert_synthetic_evd``. Every output of a fixture run is
stamped ``SYNTHETIC_FIXTURE_NOT_A_RESULT`` (``stamp``; ``assert_stamped``).
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import date
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

from culinarystate.evaluation.freeze_records import AI_DELEGATE, HUMANS

D085_DECISION, D085_LABEL = "D-085", "NO_HUMAN_SIGNOFF_D085"

VERSION = "frozen_guard@0.1"
STAMP = "SYNTHETIC_FIXTURE_NOT_A_RESULT"
FREEZE_RECORD_TYPE = "FREEZE_D5_BENCHMARK"
ROOT = Path(__file__).resolve().parents[3]
FIXTURE_DIR = "tests/fixtures/d5_synthetic"
PREREG = "reports/del5/d5_benchmark_preregistration_DRAFT.md"
FORBIDDEN_FIXTURE_PREFIXES = ("benchmark/", "annotation/", "ledgers/", "data/")
SYNTHETIC_QID = re.compile(r"^SYN-[A-Z0-9]+-\d{3}$")
REAL_QID = re.compile(r"^D5-")
SYNTHETIC_EVD_MIN = 990000                      # synthetic EVD ids are EVD-990000 .. EVD-999999
# AI markers in approval fields: worker labels, model / vendor names and the D-071 personas (they decide review
# blocks, they never sign). Matched as whole tokens; "_" and digits count as separators, so AI_AGENT matches.
AI_MARKER = re.compile(r"(?<![a-z])(ai|ksh|prv|claude|anthropic|agent|assistant|bot|gpt|llm|codex|copilot|gemini|"
                       r"openai|qwen|model)(?![a-z])", re.I)
SCORER_CODE = (
    "src/culinarystate/evaluation/frozen_guard.py",
    "src/culinarystate/evaluation/d5_scoring.py",
    "src/culinarystate/evaluation/d4_metrics.py",
    "src/culinarystate/evaluation/ablation.py",
    "src/culinarystate/evaluation/h3_independent.py",
    "src/culinarystate/evaluation/claim_audit.py",
    "src/culinarystate/evaluation/paired_stats.py",
    "src/culinarystate/evaluation/mcnemar_power.py",
    "src/culinarystate/evaluation/h1_independence.py",
    "src/culinarystate/evaluation/freeze_records.py",
    "src/culinarystate/decision/query_router.py",
    "src/culinarystate/retrieval/compatibility.py",
    "tools/s178_d5_score.py",
)


class GuardRefused(RuntimeError):
    """The scorer may not run on these inputs; ``problems`` lists every reason."""

    def __init__(self, problems: Iterable[str]):
        self.problems = list(problems)
        super().__init__("frozen-input guard refused: " + "; ".join(self.problems))


def sha256_file(path: Path | str) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def scorer_code_paths() -> tuple[str, ...]:
    """Relative paths whose sha256 a D5 freeze record must pin."""
    return SCORER_CODE


def _rel(root: Path, p: Path | str) -> str:
    q = Path(p)
    q = (root / q) if not q.is_absolute() else q
    try:
        return q.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return q.resolve().as_posix()


def _approvals(rec: Mapping[str, Any]) -> list[dict]:
    """Normalise ``approvals`` (list) or the single ``approved_by`` / ``approved_date`` shape into a list."""
    out: list[dict] = []
    raw = rec.get("approvals")
    if isinstance(raw, list):
        out += [a if isinstance(a, dict) else {"approved_by": a} for a in raw]
    by = rec.get("approved_by")
    if isinstance(by, str) and by.strip():
        out.append({"approved_by": by, "approved_date": rec.get("approved_date")})
    elif isinstance(by, list):
        out += [{"approved_by": b, "approved_date": rec.get("approved_date")} for b in by]
    return out


def _strings(x: Any) -> list[str]:
    if isinstance(x, str):
        return [x]
    if isinstance(x, Mapping):
        return [s for k, v in x.items() for s in _strings(k) + _strings(v)]
    if isinstance(x, (list, tuple)):
        return [s for v in x for s in _strings(v)]
    return []


def approval_problems(rec: Mapping[str, Any], required: Sequence[str] = HUMANS) -> list[str]:
    """Problems with the approval fields only. Every required human must approve with a date; no AI marker."""
    probs: list[str] = []
    apps = _approvals(rec)
    if not apps:
        return ["NO_HUMAN_APPROVAL"]
    named: set[str] = set()
    for a in apps:
        who = a.get("approved_by")
        if who == AI_DELEGATE:                       # D-085: the AI delegate acts for both humans, under its own name
            probs += _delegate_problems(a)
            if not _delegate_problems(a):
                named |= set(HUMANS)
            continue
        markers = sorted({m.group(0).lower() for s in _strings(a) for m in AI_MARKER.finditer(s)})
        if markers:
            probs.append(f"AI_APPROVAL: approval entry carries AI marker(s) {markers}")
            continue
        if not isinstance(who, str) or who not in HUMANS:
            probs.append(f"APPROVER_NOT_HUMAN: {who!r} is not one of {list(HUMANS)}")
            continue
        try:
            date.fromisoformat(str(a.get("approved_date")))
        except ValueError:
            probs.append(f"APPROVAL_DATE_INVALID: {who}")
            continue
        named.add(who)
    for h in required:
        if h not in named:
            probs.append(f"MISSING_APPROVER: {h}")
    return probs


def _delegate_problems(a: Mapping[str, Any]) -> list[str]:
    probs = []
    if a.get("decision") != D085_DECISION or a.get("label") != D085_LABEL:
        probs.append(f"DELEGATE_WITHOUT_D085: an {AI_DELEGATE!r} approval must name {D085_DECISION} and {D085_LABEL}")
    try:
        date.fromisoformat(str(a.get("approved_date")))
    except ValueError:
        probs.append(f"APPROVAL_DATE_INVALID: {AI_DELEGATE}")
    return probs


def signoff_kind(rec: Mapping[str, Any]) -> str | None:
    """HUMAN when every approval is a named human; AI_DELEGATED_D085 when any is the D-085 delegate; else None."""
    who = [a.get("approved_by") for a in _approvals(rec)]
    if not who:
        return None
    return "AI_DELEGATED_D085" if AI_DELEGATE in who else ("HUMAN" if all(w in HUMANS for w in who) else None)


def check_real_inputs(root: Path | str, freeze_record: Path | str, inputs: Sequence[Path | str], *,
                      code_paths: Sequence[str] | None = None, prereg_path: str = PREREG,
                      required_approvers: Sequence[str] = HUMANS,
                      committed_check: Callable[[Path], bool] | None = None) -> dict:
    """Read-only check of a REAL scoring run. Returns ``{"ok", "problems", ...}``; never raises on bad input."""
    root = Path(root)
    code_paths = SCORER_CODE if code_paths is None else tuple(code_paths)
    fr = Path(freeze_record)
    fr = fr if fr.is_absolute() else root / fr
    out: dict[str, Any] = {"version": VERSION, "mode": "REAL", "freeze_record": _rel(root, fr), "problems": [],
                           "files_sha256": {}, "code_sha256": {}, "freeze_id": None}
    probs: list[str] = out["problems"]
    for p in inputs:
        r = _rel(root, p)
        if r.startswith(FIXTURE_DIR + "/") or r == FIXTURE_DIR:
            probs.append(f"FIXTURE_INPUT_IN_REAL_MODE: {r}")
    if _rel(root, fr).startswith(FIXTURE_DIR):
        probs.append("FREEZE_RECORD_IN_FIXTURE_DIR")
    if not fr.is_file():
        probs.append("NO_FREEZE_RECORD")
        out["ok"] = False
        return out
    try:
        rec = json.loads(fr.read_text(encoding="utf-8"))
        if not isinstance(rec, dict):
            raise ValueError("not an object")
    except (OSError, ValueError):
        probs.append("FREEZE_RECORD_UNREADABLE")
        out["ok"] = False
        return out
    out["freeze_id"] = rec.get("freeze_id")
    if rec.get("record") != FREEZE_RECORD_TYPE:
        probs.append(f"WRONG_RECORD_TYPE: {rec.get('record')!r}")
    if rec.get("status") != "FROZEN":
        probs.append(f"NOT_FROZEN: status {rec.get('status')!r}")
    probs += approval_problems(rec, required_approvers)
    files = rec.get("files") if isinstance(rec.get("files"), dict) else {}
    if not files:
        probs.append("NO_FILES_IN_FREEZE")
    for rel, sha in sorted(files.items()):
        f = root / rel
        if not f.is_file():
            probs.append(f"FILE_MISSING: {rel}")
            continue
        now = sha256_file(f)
        if now != sha:
            probs.append(f"HASH_MISMATCH: {rel}")
        else:
            out["files_sha256"][rel] = now
    for p in inputs:
        r = _rel(root, p)
        if r not in files:
            probs.append(f"FILE_NOT_IN_FREEZE: {r}")
    code = rec.get("code_sha256") if isinstance(rec.get("code_sha256"), dict) else {}
    for rel in code_paths:
        f = root / rel
        if rel not in code:
            probs.append(f"CODE_NOT_PINNED: {rel}")
        elif not f.is_file() or sha256_file(f) != code[rel]:
            probs.append(f"CODE_CHANGED_AFTER_FREEZE: {rel}")
        else:
            out["code_sha256"][rel] = code[rel]
    pre = root / prereg_path
    if not rec.get("prereg_sha256"):
        probs.append("PREREG_NOT_PINNED")
    elif not pre.is_file() or sha256_file(pre) != rec["prereg_sha256"]:
        probs.append("PREREG_CHANGED_AFTER_FREEZE")
    if committed_check is not None and not committed_check(fr):
        probs.append("FREEZE_RECORD_NOT_COMMITTED")
    out["signoff"] = signoff_kind(rec)
    if out["signoff"] == "AI_DELEGATED_D085":
        out["label"] = D085_LABEL
    out["freeze_record_sha256"] = sha256_file(fr)
    out["ok"] = not probs
    return out


def require_real_inputs(root: Path | str, freeze_record: Path | str, inputs: Sequence[Path | str], **kw: Any) -> dict:
    res = check_real_inputs(root, freeze_record, inputs, **kw)
    if not res["ok"]:
        raise GuardRefused(res["problems"])
    return res


# ------------------------------------------------------------------ fixture mode

def check_fixture_inputs(fixture_dir: Path | str, inputs: Sequence[Path | str], *, root: Path | str = ROOT) -> dict:
    """Fixture inputs: inside ``fixture_dir``, listed in its manifest with matching sha256, never a benchmark path."""
    root, fdir = Path(root), Path(fixture_dir)
    fdir = fdir if fdir.is_absolute() else root / fdir
    probs: list[str] = []
    out: dict[str, Any] = {"version": VERSION, "mode": "FIXTURE", "stamp": STAMP, "problems": probs, "files_sha256": {}}
    frel = _rel(root, fdir)
    if any(frel.startswith(p) or frel == p.rstrip("/") for p in FORBIDDEN_FIXTURE_PREFIXES):
        probs.append(f"FIXTURE_DIR_IN_FORBIDDEN_PATH: {frel}")
    man_path = fdir / "manifest.json"
    try:
        man = json.loads(man_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        probs.append("NO_FIXTURE_MANIFEST")
        out["ok"] = False
        return out
    if man.get("synthetic") is not True or man.get("stamp") != STAMP:
        probs.append("MANIFEST_NOT_SYNTHETIC")
    listed = man.get("files") if isinstance(man.get("files"), dict) else {}
    for p in inputs:
        q = Path(p)
        q = q if q.is_absolute() else fdir / q
        try:
            name = q.resolve().relative_to(fdir.resolve()).as_posix()
        except ValueError:
            probs.append(f"INPUT_OUTSIDE_FIXTURE_DIR: {_rel(root, q)}")
            continue
        rel_root = _rel(root, q)
        if any(rel_root.startswith(x) for x in FORBIDDEN_FIXTURE_PREFIXES):
            probs.append(f"INPUT_IN_FORBIDDEN_PATH: {rel_root}")
        if name not in listed:
            probs.append(f"INPUT_NOT_IN_MANIFEST: {name}")
        elif not q.is_file() or sha256_file(q) != listed[name]:
            probs.append(f"FIXTURE_HASH_MISMATCH: {name}")
        else:
            out["files_sha256"][name] = listed[name]
    out["ok"] = not probs
    return out


def require_fixture_inputs(fixture_dir: Path | str, inputs: Sequence[Path | str], **kw: Any) -> dict:
    res = check_fixture_inputs(fixture_dir, inputs, **kw)
    if not res["ok"]:
        raise GuardRefused(res["problems"])
    return res


def assert_synthetic_rows(rows: Sequence[Mapping[str, Any]]) -> None:
    """Every benchmark row of a fixture run is synthetic (``SYN-`` qid, synthetic drafter); a ``D5-`` qid refuses."""
    bad = [str(r.get("qid")) for r in rows
           if not SYNTHETIC_QID.match(str(r.get("qid") or "")) or REAL_QID.match(str(r.get("qid") or ""))
           or r.get("drafted_by") != "SYNTHETIC_FIXTURE"]
    if bad:
        raise GuardRefused([f"NON_SYNTHETIC_ROW: {q}" for q in bad[:10]])


def assert_synthetic_evd(evd: Mapping[str, Any]) -> None:
    """Every EVD row of a fixture run has a synthetic id (EVD-990000 or above), so no ledger row can enter."""
    bad = [i for i in evd if not re.fullmatch(r"EVD-\d{6}", str(i)) or int(str(i)[4:]) < SYNTHETIC_EVD_MIN]
    if bad:
        raise GuardRefused([f"NON_SYNTHETIC_EVD_ID: {i}" for i in bad[:10]])


def assert_real_rows(rows: Sequence[Mapping[str, Any]]) -> None:
    """A real run never contains a synthetic row (no fixture mixed into a benchmark)."""
    bad = [str(r.get("qid")) for r in rows if SYNTHETIC_QID.match(str(r.get("qid") or ""))
           or r.get("drafted_by") == "SYNTHETIC_FIXTURE"]
    if bad:
        raise GuardRefused([f"SYNTHETIC_ROW_IN_REAL_RUN: {q}" for q in bad[:10]])


def stamp(obj: Any) -> Any:
    """Stamp a fixture output: the top level and every mapping value of the top level carry ``stamp``."""
    if not isinstance(obj, dict):
        return {"stamp": STAMP, "value": obj}
    out = {"stamp": STAMP}
    for k, v in obj.items():
        out[k] = {"stamp": STAMP, **v} if isinstance(v, dict) and k != "stamp" else v
    return out


def assert_stamped(obj: Mapping[str, Any]) -> None:
    if obj.get("stamp") != STAMP or any(isinstance(v, dict) and v.get("stamp") != STAMP for v in obj.values()):
        raise GuardRefused(["OUTPUT_NOT_STAMPED"])
