"""Make and verify the local submission review archive from explicit file lists."""
from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess
import tarfile
import tempfile
import zipfile

import fitz

ROOT = Path(__file__).resolve().parents[2]
SUBMISSION = ROOT / "submission"
FREEZE = "freeze-2026-11-20"
NAME = "CulinaryState_Group17_2026-11-20_REVIEW"
SCREEN_DIR = "reports/final/screens/"
FROZEN_ROOTS = (
    "web",
    "src",
    "docs/final",
    "docs/EVENT_IR_CONTRACT.md",
    "design",
    "deployment",
    "registry/rag/compatibility_axes_v1.csv",
    "registry/food_ph_fda2003_v1.csv",
    "tests/unit/test_s179_gate_provenance_report.py",
    "tools/live_demo.sh",
    "tools/s182_similar.py",
    "tools/s179_d5_run_rungs.py",
    "tools/s179_gate_provenance_report.py",
    "pyproject.toml",
    "CLAUDE.md",
    "DECISIONS.md",
    "STATUS.md",
    "WORKLOG.md",
    "reports/final/RELEASE_CARD.md",
    "reports/final/DELIVERABLE_COMPLIANCE_MATRIX_2026-11-16.md",
    "reports/step26/simulability_census_full_corpus_S166.json",
    "reports/step10/aa_pilot_model_a_fit_D085.json",
    "reports/step10/aa_SIMVAL_diagnostic_2026-11-11_v2.json",
    "reports/del3/compiler_vs_gold_pooled_S179.md",
    "reports/s179/state_inventory_FINAL_2026-11-15.md",
    "reports/s179/CAL_paired_AI_closeout_2026-11-13.json",
    "reports/s180/step7_FINAL_COMPARISON_2026-11-16.md",
    "reports/s181/d4_contract_metrics.json",
    "reports/s181/d4_contract_metrics.md",
    "reports/s181/snapshot_findings.md",
    "reports/s181/human_audit/D3_gold_status.md",
    "reports/s181/human_audit/REPORT_WORDING.md",
    "reports/ner/culinaryner_kf_final_report.md",
)
LOCAL_FILES = (
    "handoff/REHEARSAL_SCRIPT_2026-11-24.md",
    "handoff/KUSH_SUBMISSION_TAKEOVER_2026-11-20.md",
    "reports/final/FINAL_REPORT_DRAFT_S179_2026-11-11.md",
    "reports/final/sections/S180_freeze_results_DRAFT.md",
    "reports/final/REPORT_EVIDENCE_REVIEW_2026-11-20.json",
    "reports/final/deck/BUSINESS_PROPOSAL_OPTIONAL_2026-11-20.md",
    "reports/final/deck/NUMBER_SOURCES.md",
    "reports/final/CulinaryState_final_report.pdf",
    "reports/final/CulinaryState_final.pptx",
    "reports/final/CulinaryState_final.pdf",
    SCREEN_DIR + "MANIFEST.json",
    SCREEN_DIR + "STORIES.md",
    SCREEN_DIR + "answer_panels.json",
    SCREEN_DIR + "runs/tomato-a-d.json",
    SCREEN_DIR + "runs/RUN_MANIFEST.json",
    SCREEN_DIR + "runs/carrots.json",
    SCREEN_DIR + "runs/tomatoes.json",
    SCREEN_DIR + "runs/potatoes.json",
    SCREEN_DIR + "runs/safety.json",
    SCREEN_DIR + "runs/preflight_live_2026-11-20.txt",
)
MARKERS = {
    "source or credential marker": re.compile(rb"nvapi-|PRIVATE KEY|BBCGF|SRC-000002"),
    "private absolute path": re.compile(rb"/Users/"),
}


def command(*args, cwd=ROOT):
    return subprocess.run(args, cwd=cwd, capture_output=True, check=True, text=True).stdout


def sha256(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def scan(path):
    blobs = [path.read_bytes()]
    if path.suffix == ".pdf":
        with fitz.open(path) as pdf:
            blobs.extend(page.get_text().encode() for page in pdf)
    elif path.suffix == ".pptx":
        with zipfile.ZipFile(path) as deck:
            blobs.extend(deck.read(name) for name in deck.namelist() if name.endswith((".xml", ".rels")))
    return [reason for reason, marker in MARKERS.items() if any(marker.search(blob) for blob in blobs)]


def main():
    out = SUBMISSION / (NAME + ".zip")
    check = SUBMISSION / (NAME + "_CHECKS.txt")
    with tempfile.TemporaryDirectory() as work:
        work = Path(work)
        archive = work / "freeze.tar"
        present = command("git", "ls-tree", "-r", "--name-only", FREEZE, "--", *FROZEN_ROOTS).splitlines()
        command("git", "archive", "--format=tar", f"--output={archive}", FREEZE, "--", *present)
        staging = work / "package"
        staging.mkdir()
        with tarfile.open(archive) as frozen:
            for member in frozen:
                if member.isdir():
                    continue
                if not member.isfile() or member.name not in present:
                    raise ValueError(f"Unexpected archive member {member.name}")
                path = staging / member.name
                path.parent.mkdir(parents=True, exist_ok=True)
                with frozen.extractfile(member) as stream:
                    path.write_bytes(stream.read())
                path.chmod(member.mode & 0o777)

        excluded = []
        for path in sorted(staging.rglob("*")):
            if path.is_file() and (reasons := scan(path)):
                excluded.append(f"{path.relative_to(staging)} — {', '.join(reasons)}")
                path.unlink()

        shots = json.loads((ROOT / SCREEN_DIR / "MANIFEST.json").read_text())
        optional = []
        for shot in shots["images"]:
            name = SCREEN_DIR + shot["file"]
            if sha256(ROOT / name) != shot["sha256"]:
                raise ValueError(f"Screenshot hash mismatch: {name}")
            optional.append(name)
        for name in LOCAL_FILES + tuple(optional):
            source = ROOT / name
            if not source.is_file():
                continue
            if reasons := scan(source):
                raise ValueError(f"Refusing to add {name}. {', '.join(reasons)}")
            target = staging / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.read_bytes())
        readme = SUBMISSION / "README_SUBMISSION.md"
        (staging / readme.name).write_bytes(readme.read_bytes())
        payload = sorted(path for path in staging.rglob("*") if path.is_file())
        sums = staging / "SHA256SUMS"
        sums.write_text("".join(f"{sha256(path)}  {path.relative_to(staging)}\n" for path in payload))
        draft = work / out.name
        with zipfile.ZipFile(draft, "w", compression=zipfile.ZIP_DEFLATED) as package:
            for path in payload + [sums]:
                package.write(path, path.relative_to(staging))
        integrity = command("unzip", "-tq", draft.name, cwd=work)
        extract = work / "extract"
        command("unzip", "-q", str(draft), "-d", str(extract))
        verified = command("shasum", "-a", "256", "-c", "SHA256SUMS", cwd=extract).splitlines()
        hits = [str(path.relative_to(extract)) for path in extract.rglob("*") if path.is_file() and scan(path)]
        if hits:
            raise ValueError("Fresh extraction scan failed: " + ", ".join(hits))
        with draft.open("rb") as stream, out.open("wb") as target:
            shutil.copyfileobj(stream, target)

    check.write_text(
        f"Review archive {out.name}\nFreeze {command('git', 'rev-list', '-n', '1', FREEZE).strip()}\n"
        f"Size {out.stat().st_size:,} bytes\nSHA256 {sha256(out)}\n"
        f"{integrity.strip()}\nFresh extract: {len(verified)} file checksums OK\n"
        "Fresh extract: zero source/key markers or private paths in byte, PDF-text and PPTX-XML scans.\n"
        f"Screenshot checksums: {len(shots['images'])} OK. Visual review is recorded in STATUS.\n"
        "Review candidate. Final-deck approval, live captures, production URL, fallback recording and the "
        "private-path disposition are tracked in STATUS.\n"
        "Omitted from otherwise selected frozen files\n"
        + "\n".join(excluded) + "\n\nFresh-extract checksums\n" + "\n".join(verified) + "\n",
    )
    print(f"{out.name}: {out.stat().st_size:,} bytes, {len(verified)} checksums OK")


if __name__ == "__main__":
    main()
