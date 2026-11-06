"""S168: wave-scoped Step 19 paths for P1b (P1b amendment proposal; D-070 O5).

P1's committed paths must not move; any other wave gets its own local folder and wave-named tracked files, so P1b
packets never mix with P1's (the commit step would count them as EXTRA_PACKETS). Synthetic only.
"""
from pathlib import Path

import pytest

from culinarystate.annotation import pilot_commit as pc
from culinarystate.annotation import pilot_packets as pp

T, L = Path("/t"), Path("/l")


def test_p1_paths_are_exactly_the_existing_ones():
    p = pp.wave_paths("P1", "A", tracked=T, local=L)
    assert p == {"local_dir": L / "A", "key": L / "sealed_key_P1_A.json", "snapshots": L / "A" / "_snapshots.jsonl",
                 "manifest": T / "manifest_P1.csv", "manifest_sha": T / "manifest_P1.csv.sha256",
                 "packets_csv": T / "packets_P1_A.csv", "key_sha": T / "sealed_key_P1_A.sha256",
                 "salt_sha": T / "salt_P1_A.sha256", "commitment": T / "commitments_A_P1.json"}


def test_other_waves_get_their_own_folder_and_names():
    p = pp.wave_paths("P1b", "B", tracked=T, local=L)
    assert p["local_dir"] == L / "P1b" / "B" and p["key"] == L / "P1b" / "sealed_key_P1b_B.json"
    assert p["manifest"] == T / "manifest_P1b.csv" and p["packets_csv"] == T / "packets_P1b_B.csv"
    assert p["salt_sha"] == T / "salt_P1b_B.sha256" and p["commitment"] == T / "commitments_B_P1b.json"
    assert p["snapshots"] == L / "P1b" / "B" / "_snapshots.jsonl"


@pytest.mark.parametrize("wave,ok", [("P1", True), ("P1b", True), ("P2", True), ("P10", True), ("P1B", False),
                                     ("P1bb", False), ("p1", False), ("P", False), ("../P1", False)])
def test_wave_names(wave, ok):
    assert pc.valid_wave(wave) is ok


def test_bad_wave_or_letter_is_refused():
    with pytest.raises(pp.PacketError):
        pp.wave_paths("../x", "A", tracked=T, local=L)
    with pytest.raises(pp.PacketError):
        pp.wave_paths("P1b", "C", tracked=T, local=L)


def _commit_tool(tmp, monkeypatch):
    import importlib.util
    import subprocess as sp
    root = Path(__file__).resolve().parents[2]
    spec = importlib.util.spec_from_file_location("commit_tool_s168", root / "tools/step19_commit_step.py")
    tool = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tool)
    monkeypatch.setattr(tool, "TRACKED", tmp / "tracked")
    monkeypatch.setattr(tool, "LOCAL", tmp / "local")
    real = sp.run
    monkeypatch.setattr(tool.subprocess, "run",
                        lambda args, *a, **k: sp.CompletedProcess(args, 0) if "check-ignore" in args else real(args, *a, **k))
    return tool


def test_commit_step_writes_wave_scoped_files_and_leaves_p1_alone(tmp_path, monkeypatch):
    import json
    import sys
    from culinarystate.annotation.examples import white_sauce
    tool = _commit_tool(tmp_path, monkeypatch)
    doc = white_sauce("Kush")
    doc.update(recipe_id="DGP-A-0001", status="DONE")
    d = tmp_path / "local" / "P1b" / "A"
    d.mkdir(parents=True)
    (d / "DGP-A-0001.json").write_text(json.dumps(doc, indent=2) + "\n")
    (tmp_path / "tracked").mkdir()
    (tmp_path / "tracked" / "packets_P1b_A.csv").write_text("packet_id\nDGP-A-0001\n")
    q = tmp_path / "q.txt"
    q.write_text("no questions\n")
    for ev in ("FIRST_VALIDATE", "DONE"):
        monkeypatch.setattr(sys, "argv", ["x", "snapshot", "--letter", "A", "--packet", "DGP-A-0001", "--event", ev,
                                          "--wave", "P1b"])
        tool.main()
    monkeypatch.setattr(sys, "argv", ["x", "commit", "--letter", "A", "--wave", "P1b", "--handbook-version",
                                      "v1+AddendumA+AddendumB", "--question-log", str(q), "--representability", str(q)])
    tool.main()
    c = json.loads((tmp_path / "tracked" / "commitments_A_P1b.json").read_text())
    assert c["wave"] == "P1b" and [f["packet_id"] for f in c["files"]] == ["DGP-A-0001"]
    assert not (tmp_path / "local" / "A").exists() and not (tmp_path / "tracked" / "commitments_A_P1.json").exists()
