"""DRAFT_PENDING_S160_REVIEW -- regressions for the S160 A-C AI cross-review (worker prv).

R1  15a.R seal: an Approver line that names Kush but is pending, or names an AI, was accepted.
R1b 15a.R seal: marker lines inside a fenced code block of the entry were read as rulings.
R2  Step 35 runner: any two strings (e.g. the AI worker labels "ksh"/"prv") counted as signatures.
R3  15.0 draft: quoted plan text cited to plan lines that do not contain it.
R4  35.0 v2: the D1 row's coverage list differs from the sign-off sheet's own D1 mapping.
All signed records here are synthetic and live in tmp_path.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import pytest

from culinarystate.lineage import reserved_seal as rs
from culinarystate.representation import explicit_runner as er
from culinarystate.representation.prereg_guard import PreregNotSigned

REPO = Path(__file__).resolve().parents[2]
SEED_SHA = hashlib.sha256(b"synthetic").hexdigest()


def _entry(approver: str, *, fenced: bool = False) -> str:
    markers = ("- **15.0 RESERVED_FRACTION:** 1/4\n- **15.0 RESERVED_UNIT:** CELL\n"
               "- **15.0 RESERVED_STRATIFY:** NONE\n"
               f"- **15a.R SEED_SHA256:** {SEED_SHA}\n")
    body = f"```text\n{markers}```\n" if fenced else markers
    return f"# DECISIONS\n\n### D-901 · 2026-01-02 · 15.0 pre-freeze rulings (synthetic)\n{body}- **Approver:** {approver}\n"


def _codes(exc) -> set[str]:
    return {b.split(":", 1)[0] for b in exc.value.blockers}


# ---------------------------------------------------------------- R1 / R1b

@pytest.mark.parametrize("approver", [
    "Kush (pending confirmation).",                       # DECISIONS.md L18 style
    "Claude (reversible; flag for Kush/Parv review).",    # DECISIONS.md L13 style
    "Kush + Parv to confirm before authoring starts.",    # DECISIONS.md L45 style
    "ksh for Kush",
    "Kush (DRAFT)",
])
def test_r1_pending_or_ai_approver_is_refused(approver):
    with pytest.raises(rs.SealRefused) as exc:
        rs.find_ruling(_entry(approver), "D-901")
    assert _codes(exc) & {"APPROVER_NOT_KUSH", "APPROVER_PENDING", "APPROVER_NOT_HUMAN"}


@pytest.mark.parametrize("approver", ["Kush.", "Kush (message of 2026-10-27).", "Kush and Parv (Parv relayed by Kush).",
                                      "Kush (synthetic test entry)"])
def test_r1_signed_human_approver_still_accepted(approver):
    assert rs.find_ruling(_entry(approver), "D-901").decision_id == "D-901"


def test_r1b_markers_inside_a_code_fence_are_not_rulings():
    with pytest.raises(rs.SealRefused) as exc:
        rs.find_ruling(_entry("Kush.", fenced=True), "D-901")
    assert {"FRACTION_MISSING", "UNIT_MISSING", "STRATIFY_MISSING", "SEED_COMMITMENT_MISSING"} <= _codes(exc)


# ---------------------------------------------------------------- R2

def _synthetic_root(tmp_path: Path) -> Path:
    root = tmp_path / "pkg"
    for rel in set(er.package_inputs()) | {er.PACKAGE_DOCUMENT}:
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(f"synthetic bytes for {rel}\n", encoding="utf-8")
    return root


def _sign(root: Path, signers, **extra) -> None:
    rec = dict(er.build_unsigned_record(root), signers=list(signers), date="2026-11-03", status="SIGNED", **extra)
    (root / er.SIGNED_RECORD).write_text(json.dumps(rec), encoding="utf-8")


@pytest.mark.parametrize("signers", [
    ("ksh", "prv"),
    ("Claude", "Parv Goyal"),
    ("Kush Tokas", "Kush T."),
    ("Kush Tokas", "Someone Else"),
    ("Kush and Parv", "Parv Goyal"),
])
def test_r2_runner_refuses_non_human_or_incomplete_signers(tmp_path, signers):
    root = _synthetic_root(tmp_path)
    _sign(root, signers)
    with pytest.raises(PreregNotSigned, match="signer"):
        er.authorise_explicit_run("35e", root=root)


def test_r2_runner_accepts_kush_and_parv(tmp_path):
    root = _synthetic_root(tmp_path)
    _sign(root, ("Kush Tokas", "Parv Goyal"))
    assert er.authorise_explicit_run("35e", root=root).task == "35e"


def test_r2_single_signer_override_still_needs_a_human_signer(tmp_path):
    root = _synthetic_root(tmp_path)
    override = {"single_signer_override": {"reason": "synthetic", "by": "Kush Tokas"}}
    _sign(root, ("Kush Tokas",), **override)
    assert er.authorise_explicit_run("35e", root=root).task == "35e"
    _sign(root, ("prv",), **override)
    with pytest.raises(PreregNotSigned, match="signer"):
        er.authorise_explicit_run("35e", root=root)


# ---------------------------------------------------------------- R3

def _norm(text: str) -> str:
    return " ".join(text.replace("|", " ").replace(":", " ").replace("'", '"').split())


def test_r3_quotes_in_the_15_0_draft_are_on_the_cited_plan_lines():
    doc = (REPO / "reports/step15/pre_freeze_rulings_DRAFT.md").read_text(encoding="utf-8")
    plan = (REPO / "docs/plan/CulinaryState_36_Step_Execution_Plan_v2.md").read_text(encoding="utf-8").splitlines()
    pairs = [(m.group(1), m.group(2)) for m in
             re.finditer(r'"([^"]{8,}?)"\s*\(Plan (L\d+(?:\s*/\s*L\d+)*)\)', doc)]
    pairs += [(m.group(2), m.group(1)) for m in
              re.finditer(r'Plan (L\d+(?:\s*/\s*L\d+)*)\)?:\s*"([^"]{8,}?)"', doc)]
    assert len(pairs) >= 5
    for quote, refs in pairs:
        frags = [f.strip(" .") for f in re.split(r"\.\.\.|…", quote) if f.strip(" .")]
        for line in (int(x) for x in re.findall(r"L(\d+)", refs)):
            for frag in frags:
                assert _norm(frag) in _norm(plan[line - 1]), (line, frag)


# ---------------------------------------------------------------- R4

def test_r4_v2_d1_row_uses_the_sign_off_sheet_mapping():
    sheet = (REPO / "reports/step35/35_0_signoff_sheet_DRAFT.md").read_text(encoding="utf-8")
    mapping = re.search(r"\*\*D1\. [^*]*\((D35-[0-9, ]+)\)\.\*\*", sheet).group(1)
    v2 = (REPO / er.PACKAGE_DOCUMENT).read_text(encoding="utf-8")
    row = next(line for line in v2.splitlines() if line.startswith("| D1 |"))
    assert f"({mapping})" in row
    assert "covers D35-1, 3, 5" not in row
