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


# ------------------------------------------------ ksh review KS2 / KS6
def test_key_packets_must_equal_the_committed_files(tmp_path):
    da, ca = _write(tmp_path, "A", _docs("A", "Kush"))
    db, cb = _write(tmp_path, "B", _docs("B", "Parv"))
    ka, kb = _keys()
    cb_short = {**cb, "files": cb["files"][:1]}
    with pytest.raises(S.ScoreError, match="KEY_VS_COMMITMENT"):
        S.score(ka, kb, labels_a=da, labels_b=db, commitment_a=ca, commitment_b=cb_short)


def test_missing_label_file_is_refused(tmp_path):
    da, ca = _write(tmp_path, "A", _docs("A", "Kush"))
    (da / "DGP-A-0002.json").unlink()
    assert any("MISSING_LABEL_FILE" in p for p in S.commitment_problems(ca, letter="A", label_dir=da))


def test_score_uses_the_key_pairing_not_packet_numbers(tmp_path):
    a = _docs("A", "Kush")
    b = _docs("B", "Parv", perturb=True)  # B-0002 is the perturbed one
    da, ca = _write(tmp_path, "A", a)
    db, cb = _write(tmp_path, "B", b)
    ka, kb = _keys(swap=True)  # A-0001 <-> B-0002 (perturbed), A-0002 <-> B-0001 (identical)
    rep = S.score(ka, kb, labels_a=da, labels_b=db, commitment_a=ca, commitment_b=cb)
    assert rep["per_pair"][0]["event_f1_strict"] < 1.0 and rep["per_pair"][1]["event_f1_strict"] == 1.0


def test_sealed_key_is_checked_against_its_salted_commitment():
    from culinarystate.annotation import pilot_packets as pp
    salt = "3f9c1e7a5b2d8064c1a9e3f75b0d2c8e6a4f1b9d7c3e5a0f8b2d6c4e1a7f9b3d"
    ka, _ = _keys()
    good = pp.key_commitment(ka, salt_hex=salt) + "  sealed_key_P1_A.json (salted)\n"
    assert S.key_problems(ka, salt_hex=salt, tracked_line=good, letter="A") == []
    assert S.key_problems({**ka, "DGP-A-0001": "X"}, salt_hex=salt, tracked_line=good, letter="A")


# ------------------------------------------------ block M4: THR-19P-16 / -31 rates (D-067)
def _tool_module():
    import importlib.util
    from pathlib import Path
    spec = importlib.util.spec_from_file_location("gpa_tool", Path(__file__).resolve().parents[2] / "tools/gold_pilot_agreement.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_denominators_equal_the_existing_tool(tmp_path):
    a, b = white_sauce("Kush"), white_sauce("Parv")
    b["steps"][0]["events"] = b["steps"][0]["events"][:-1]
    tool = _tool_module()
    want = tool.denominators({("Kush", "R"): a, ("Parv", "R"): b}, ["R"])
    assert dict(S.unit_counts(a, b)) == dict(want)


def test_gate_uses_the_max_of_tool_and_per_pair_rates(tmp_path):
    da, ca = _write(tmp_path, "A", _docs("A", "Kush"))
    db, cb = _write(tmp_path, "B", _docs("B", "Parv", perturb=True))
    ka, kb = _keys()
    rep = S.score(ka, kb, labels_a=da, labels_b=db, commitment_a=ca, commitment_b=cb)
    g = rep["handbook_gate"]
    den, cats = rep["denominators"], rep["disagreement_categories"]
    ev = cats["event_type"] + 0
    assert g["tool_rate"]["event_type"] == round(ev / den["events"], 4)
    assert g["per_pair_rate"]["event_type"] == round(ev / (den["events"] / 2), 4)
    assert g["threshold"] == 0.2 and g["verdict"] in ("HANDBOOK_REVISION_REQUIRED", "NO_MECHANICAL_FLAG")
    flagged = sorted(c for c in cats if max(g["tool_rate"][c] or 0, g["per_pair_rate"][c] or 0) > 0.2)
    assert g["flagged_categories"] == flagged
    D.assert_counts_only(rep)


# ------------------------------------------------ block N7: SP-002 sensitivity column (D-069)
def test_sp002_normalisation_keeps_offsets_and_only_touches_fraction_slashes():
    doc = white_sauce("Kush")
    doc["ingredient_lines"][0]["text"] = doc["ingredient_lines"][0]["text"].replace("50", "1⁄2", 1)
    out = S.sp002_normalised(doc)
    assert out is not doc and "⁄" in doc["ingredient_lines"][0]["text"]
    assert out["ingredient_lines"][0]["text"] == doc["ingredient_lines"][0]["text"].replace("⁄", "/")
    assert [len(x["text"]) for x in out["ingredient_lines"]] == [len(x["text"]) for x in doc["ingredient_lines"]]
    assert out["steps"] == doc["steps"]


def test_report_carries_a_sensitivity_block_beside_the_headline(tmp_path):
    da, ca = _write(tmp_path, "A", _docs("A", "Kush"))
    db, cb = _write(tmp_path, "B", _docs("B", "Parv", perturb=True))
    ka, kb = _keys()
    rep = S.score(ka, kb, labels_a=da, labels_b=db, commitment_a=ca, commitment_b=cb)
    sens = rep["sensitivity_sp002"]
    assert sens["basis"] == "U2044_NORMALISED_AT_SCORING_LABELS_UNCHANGED"
    assert sens["mean"] == rep["mean"] and sens["disagreement_categories"] == rep["disagreement_categories"]  # no U+2044
    D.assert_counts_only(rep)
