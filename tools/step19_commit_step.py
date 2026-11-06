#!/usr/bin/env python3
"""Step 19 commit step for ONE annotator (design section 5.4; PV-6, PV-9, PV-10). DRAFT_PENDING_H4.

Run on the annotator's own machine, in this order:
  python tools/step19_commit_step.py snapshot --letter A --packet DGP-A-0001 --event FIRST_VALIDATE
      (right after the first `gold_cli.py validate` of that file)
  python tools/step19_commit_step.py snapshot --letter A --packet DGP-A-0001 --event DONE
      (after `validate` prints OK and status is DONE)
  python tools/step19_commit_step.py commit --letter A --wave P1 --handbook-version "v1+AddendumA" \\
      --question-log <private log> --representability <private checklist>

Snapshots are appended to the git-ignored annotation/gold/deep_gold_pilot_v1/<letter>/_snapshots.jsonl (hashes and
times only). `commit` writes the tracked, text-free registry/recipe_semantics/deep_gold_pilot_v1/commitments_<letter>_<wave>.json
and refuses to overwrite it, or to run while the other annotator's packets or key are on this machine. The annotator
then commits that file to git from their own session BEFORE anyone opens a sealed key (PV-6, PV-9).
"""
import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from culinarystate.annotation import pilot_commit as pc  # noqa: E402
from culinarystate.annotation import pilot_packets as pp  # noqa: E402

TRACKED = ROOT / "registry/recipe_semantics/deep_gold_pilot_v1"
LOCAL = ROOT / "annotation/gold/deep_gold_pilot_v1"


def _paths(letter: str, wave: str = "P1") -> dict:
    return pp.wave_paths(wave, letter, tracked=TRACKED, local=LOCAL)  # S168: P1 paths unchanged


def _log(letter: str, wave: str = "P1") -> Path:
    return _paths(letter, wave)["snapshots"]


def _guard(letter: str, wave: str = "P1") -> None:
    w = _paths(letter, wave)
    problems = pp.independence_problems(w["local_dir"].parent, letter)
    for probe in (w["snapshots"], w["local_dir"] / "probe.json", w["key"]):
        if subprocess.run(["git", "-C", str(ROOT), "check-ignore", "-q", str(probe)]).returncode != 0:
            problems.append(f"NOT_GIT_IGNORED: {probe.relative_to(ROOT)}")
    if problems:
        raise SystemExit("refusing: " + "; ".join(problems))


def snapshot(a) -> None:
    if not pc.valid_wave(a.wave):
        raise SystemExit("invalid wave name")
    if not pc.valid_packet_id(a.packet, a.letter):
        raise SystemExit(f"invalid packet id for letter {a.letter}")
    _guard(a.letter, a.wave)
    f = _paths(a.letter, a.wave)["local_dir"] / f"{a.packet}.json"
    if not f.is_file():
        raise SystemExit(f"no label file {a.packet}.json for letter {a.letter}")
    if a.event == "DONE":
        try:
            problems = pc.label_problems(json.loads(f.read_text(encoding="utf-8")), letter=a.letter, packet_id=a.packet)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            problems = [f"LABEL_UNREADABLE: {a.packet}"]
        if problems:
            raise SystemExit("refusing DONE snapshot: " + "; ".join(problems))
    entry = {"packet_id": a.packet, **pc.snapshot_entry(f, a.event, pc.utc_now())}
    with _log(a.letter, a.wave).open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry) + "\n")
    print(json.dumps({"snapshot": a.event, "packet_id": a.packet}))


def commit(a) -> None:
    if not pc.valid_wave(a.wave):
        raise SystemExit("invalid wave name (expected P<number>)")
    _guard(a.letter, a.wave)
    w = _paths(a.letter, a.wave)
    out, issued = w["commitment"], w["packets_csv"]
    if not issued.is_file():
        raise SystemExit(f"refusing: no issued packet list {issued.name}")
    expected = [r["packet_id"] for r in csv.DictReader(issued.open(encoding="utf-8"))]
    snaps: dict[str, list] = {}
    try:
        if w["snapshots"].is_file():
            for line in w["snapshots"].read_text(encoding="utf-8").splitlines():
                e = json.loads(line)
                snaps.setdefault(e.pop("packet_id"), []).append(e)
    except (OSError, json.JSONDecodeError, KeyError, AttributeError):
        raise SystemExit("refusing: snapshot log is unreadable or corrupt")
    files = [(p.stem, p, snaps.get(p.stem, [])) for p in sorted(w["local_dir"].glob(f"DGP-{a.letter}-*.json"))]
    try:
        c = pc.build_commitment(files, letter=a.letter, wave=a.wave, handbook_version=a.handbook_version,
                                question_log=a.question_log, representability=a.representability, now=pc.utc_now(),
                                expected_ids=expected)
    except (OSError, pc.CommitError) as exc:
        raise SystemExit(f"refusing: {exc}")
    try:
        with out.open("x", encoding="utf-8") as fh:
            fh.write(json.dumps(c, indent=1, sort_keys=True) + "\n")
    except FileExistsError:
        raise SystemExit(f"refusing to overwrite {out.name}")
    print(json.dumps({"commitment": str(out.relative_to(ROOT)) if out.is_relative_to(ROOT) else str(out), "files": len(c["files"]),
                      "next": "git add + commit this file from your own session before any key is opened"}))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("snapshot")
    s.add_argument("--letter", required=True, choices=sorted(pp.ANNOTATOR))
    s.add_argument("--packet", required=True)
    s.add_argument("--event", required=True, choices=pc.EVENTS)
    s.add_argument("--wave", default="P1", help="wave name (P1 keeps its original paths)")
    c = sub.add_parser("commit")
    c.add_argument("--letter", required=True, choices=sorted(pp.ANNOTATOR))
    c.add_argument("--wave", required=True)
    c.add_argument("--handbook-version", required=True)
    c.add_argument("--question-log", required=True, type=Path)
    c.add_argument("--representability", required=True, type=Path)
    a = ap.parse_args()
    snapshot(a) if a.cmd == "snapshot" else commit(a)


if __name__ == "__main__":
    main()
