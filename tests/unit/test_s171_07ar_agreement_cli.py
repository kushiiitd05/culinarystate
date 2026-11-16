"""S171 / M2: 07.A-R1 scoring CLI (issued-file hash check, returned-file hashes, write once). Synthetic."""
from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

from culinarystate.evidence import condition_agreement as CA
from culinarystate.evidence import condition_audit_packet as P

ROOT = Path(__file__).resolve().parents[2]


def _tool():
    spec = importlib.util.spec_from_file_location("step07ar_agreement", ROOT / "tools/step07ar_agreement.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _write(path, rows):
    with open(path, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=P.COLS + P.REV)
        w.writeheader()
        w.writerows(rows)


@pytest.fixture
def world(tmp_path):
    base = [{**{c: f"v{i}" for c in P.COLS}, "audit_id": f"CA-{i:03d}", "normalizer_fingerprint_12": "e7d589136275",
             **{c: "" for c in P.REV}} for i in range(1, 11)]
    issued = tmp_path / "issued.csv"
    _write(issued, base)
    man = tmp_path / "manifest.json"
    man.write_text(json.dumps({"sha256_packet_Kush": hashlib.sha256(issued.read_bytes()).hexdigest()}))
    lab = lambda over: [{**r, **{f: "CORRECT" for f in CA.FIELDS}, "overall_judgement": "ACCEPT",  # noqa: E731
                         **over.get(r["audit_id"], {})} for r in base]
    a, b = tmp_path / "a.csv", tmp_path / "b.csv"
    _write(a, lab({}))
    _write(b, lab({"CA-001": {"duration_judgement": "INFERRED"}}))
    return {"issued": issued, "man": man, "a": a, "b": b, "out": tmp_path / "gate.json"}


def _argv(w):
    return ["--issued", str(w["issued"]), "--manifest", str(w["man"]), "--kush", str(w["a"]), "--parv", str(w["b"]),
            "--out", str(w["out"])]


def test_scores_once_and_records_returned_hashes(world):
    tool = _tool()
    assert tool.main(_argv(world)) == 0
    out = json.loads(world["out"].read_text())
    assert out["gate"] == "PASS" and out["returned_sha256"]["Kush"] == hashlib.sha256(
        world["a"].read_bytes()).hexdigest()
    with pytest.raises(SystemExit):
        tool.main(_argv(world))


def test_refuses_when_issued_packet_changed(world):
    world["issued"].write_text(world["issued"].read_text() + "\n")
    with pytest.raises(SystemExit):
        _tool().main(_argv(world))
