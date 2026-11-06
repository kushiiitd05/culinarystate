"""S166: Step 19 P1 scoring after both commitments exist (D-066).

Pairs A and B packets through both sealed keys, refuses label files that differ from their commitment (PV-6/PV-9),
and writes a counts-only agreement report: numeric metrics and disagreement-category counts per pair index, never
recipe ids, packet-to-recipe keys, entity names or text. Labelled as human-accepted AI drafts (D-045 W2, D-060).
Synthetic fixtures only.
"""
import copy
import hashlib
import json

import pytest

from culinarystate.annotation import pilot_p1_score as S
from culinarystate.annotation.examples import white_sauce
from culinarystate.quantity import rc2_dryrun as D

SENTINEL = "ZQXRECIPE"


def _write(tmp, letter, docs):
    d = tmp / letter
    d.mkdir()
    rows = []
    for pid, doc in docs.items():
        body = (json.dumps(doc, indent=2, ensure_ascii=False) + "\n").encode()
        (d / f"{pid}.json").write_bytes(body)
        rows.append({"packet_id": pid, "sha256": hashlib.sha256(body).hexdigest()})
    return d, {"annotator_letter": letter, "wave": "P1", "files": rows}


def _docs(letter, annot, n=2, perturb=False):
    out = {}
    for i in range(1, n + 1):
        doc = white_sauce(annot)
        doc["recipe_id"] = f"DGP-{letter}-{i:04d}"
        if perturb and i == 2:
            doc = copy.deepcopy(doc)
            doc["steps"][0]["events"] = doc["steps"][0]["events"][:-1]
        out[doc["recipe_id"]] = doc
    return out


def _keys(n=2, swap=False):
    rids = [f"{SENTINEL}-{i}" for i in range(1, n + 1)]
    ka = {f"DGP-A-{i:04d}": rid for i, rid in enumerate(rids, 1)}
    kb = {f"DGP-B-{i:04d}": rid for i, rid in enumerate(reversed(rids) if swap else rids, 1)}
    return ka, kb


def test_pairs_follow_the_keys_not_the_packet_numbers():
    ka, kb = _keys(swap=True)
    assert S.pair_packets(ka, kb) == [("DGP-A-0001", "DGP-B-0002"), ("DGP-A-0002", "DGP-B-0001")]


def test_pairing_refuses_different_recipe_sets():
    ka, kb = _keys()
    kb["DGP-B-0002"] = "OTHER"
    with pytest.raises(S.ScoreError):
        S.pair_packets(ka, kb)


def test_label_files_must_match_their_commitment(tmp_path):
    d, com = _write(tmp_path, "A", _docs("A", "Kush"))
    assert S.commitment_problems(com, letter="A", label_dir=d) == []
    (d / "DGP-A-0001.json").write_text("{}\n")
    assert any("CHANGED_SINCE_COMMITMENT" in p for p in S.commitment_problems(com, letter="A", label_dir=d))
    assert any("WRONG_LETTER" in p for p in S.commitment_problems(com, letter="B", label_dir=d))


def test_identical_labels_score_perfectly_and_report_is_counts_only(tmp_path):
    da, ca = _write(tmp_path, "A", _docs("A", "Kush"))
    db, cb = _write(tmp_path, "B", _docs("B", "Parv"))
    ka, kb = _keys()
    rep = S.score(ka, kb, labels_a=da, labels_b=db, commitment_a=ca, commitment_b=cb)
    text = json.dumps(rep)
    assert SENTINEL not in text and "DGP-" not in text and "white" not in text.lower()
    D.assert_counts_only(rep)
    assert rep["pairs"] == 2 and rep["label_basis"] == "HUMAN_ACCEPTED_AI_DRAFTS_NOT_BLIND"
    assert rep["mean"]["event_f1_strict"] == 1.0 and sum(rep["disagreement_categories"].values()) == 0
    assert [p["pair"] for p in rep["per_pair"]] == ["pair_01", "pair_02"]


def test_a_dropped_event_shows_up_as_a_disagreement(tmp_path):
    da, ca = _write(tmp_path, "A", _docs("A", "Kush"))
    db, cb = _write(tmp_path, "B", _docs("B", "Parv", perturb=True))
    ka, kb = _keys()
    rep = S.score(ka, kb, labels_a=da, labels_b=db, commitment_a=ca, commitment_b=cb)
    assert rep["mean"]["event_f1_strict"] < 1.0 and sum(rep["disagreement_categories"].values()) > 0


def test_score_refuses_when_a_commitment_does_not_match(tmp_path):
    da, ca = _write(tmp_path, "A", _docs("A", "Kush"))
    db, cb = _write(tmp_path, "B", _docs("B", "Parv"))
    (db / "DGP-B-0001.json").write_text("{}\n")
    ka, kb = _keys()
    with pytest.raises(S.ScoreError):
        S.score(ka, kb, labels_a=da, labels_b=db, commitment_a=ca, commitment_b=cb)


def test_cli_writes_once_and_refuses_overwrite(tmp_path):
    import importlib.util
    from pathlib import Path
    root = Path(__file__).resolve().parents[2]
    spec = importlib.util.spec_from_file_location("p1score", root / "tools/step19_p1_score.py")
    tool = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tool)
    da, ca = _write(tmp_path, "A", _docs("A", "Kush"))
    db, cb = _write(tmp_path, "B", _docs("B", "Parv"))
    ka, kb = _keys()
    paths = {}
    for name, obj in (("ka", ka), ("kb", kb), ("ca", ca), ("cb", cb)):
        paths[name] = tmp_path / f"{name}.json"
        paths[name].write_text(json.dumps(obj))
    out = tmp_path / "score.json"
    args = ["--key-a", str(paths["ka"]), "--key-b", str(paths["kb"]), "--labels-a", str(da), "--labels-b", str(db),
            "--commitment-a", str(paths["ca"]), "--commitment-b", str(paths["cb"]), "--out", str(out),
            "--root", str(tmp_path)]
    assert tool.main(args) == 0 and json.loads(out.read_text())["pairs"] == 2
    with pytest.raises(SystemExit):
        tool.main(args)
