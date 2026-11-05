"""S164 (review block J7): secret per-annotator packet salt, independence guards and the Step 19 commit step.

ksh (S163 review K3) showed the "sealed" P1 key could be rebuilt from public data: packet order was
sha256(public seed | letter | recipe_id) and the recipe ids are in the tracked manifest. Kush and Parv accepted
the fix (block J7): a secret per-annotator salt committed by hash, a git-ignore check, a one-letter-per-machine
guard, and the design's commit step (section 5.4; PV-6, PV-9, PV-10). Synthetic fixtures only.
"""
import hashlib
import json
from pathlib import Path

import pytest

from culinarystate.annotation import pilot_commit as pc
from culinarystate.annotation import pilot_packets as pp
from culinarystate.annotation.examples import white_sauce

IDS = [f"R{i}" for i in range(1, 8)]
RECS = {rid: {"source_family": "FOODCOM", "ingredient_lines": [f"{i} cup flour"], "steps": ["Mix."]}
        for i, rid in enumerate(IDS, 1)}
SEED = "9fa0008602a39537"
SALT1, SALT2 = "0123456789abcdef" * 4, "fedcba9876543210" * 4


def order(letter, salt):
    packets, key = pp.build_packets(IDS, RECS, letter=letter, seed_hex=SEED, salt_hex=salt)
    return [key[p["packet_id"]] for p in packets]


# --- salt -------------------------------------------------------------------------------------------------

def test_salt_is_required_and_must_be_long_hex():
    with pytest.raises(TypeError):
        pp.build_packets(IDS, RECS, letter="A", seed_hex=SEED)  # no salt argument
    for bad in ("", "abc", "z" * 64, "A" * 64):
        with pytest.raises(pp.PacketError):
            pp.build_packets(IDS, RECS, letter="A", seed_hex=SEED, salt_hex=bad)


def test_order_depends_on_the_secret_salt_not_only_on_public_data():
    unsalted = sorted(IDS, key=lambda rid: (hashlib.sha256(f"{SEED}|A|{rid}".encode()).hexdigest(), rid))
    assert order("A", SALT1) != unsalted
    assert order("A", SALT1) != order("A", SALT2)
    assert order("A", SALT1) == order("A", SALT1)  # deterministic given the salt


def test_orders_differ_between_annotators():
    assert order("A", SALT1) != order("B", SALT1)


def test_salt_commitment_is_sha256_of_the_salt():
    assert pp.salt_commitment(SALT1) == hashlib.sha256(SALT1.encode("utf-8")).hexdigest()


def test_read_salt_refuses_a_file_inside_the_repository(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    inside = repo / "salt.txt"
    inside.write_text(SALT1 + "\n")
    with pytest.raises(pp.PacketError):
        pp.read_salt(inside, repo_root=repo)
    outside = tmp_path / "private" / "salt.txt"
    outside.parent.mkdir()
    outside.write_text(SALT1 + "\n")
    outside.chmod(0o600)
    assert pp.read_salt(outside, repo_root=repo) == SALT1


# --- independence guards ----------------------------------------------------------------------------------

def test_other_annotators_material_on_this_machine_is_a_problem(tmp_path):
    assert pp.independence_problems(tmp_path, "A") == []
    (tmp_path / "B").mkdir()
    assert any("B" in p for p in pp.independence_problems(tmp_path, "A"))
    (tmp_path / "B").rmdir()
    (tmp_path / "sealed_key_P1_B.json").write_text("{}")
    assert pp.independence_problems(tmp_path, "A")


# --- commit step ------------------------------------------------------------------------------------------

def done_doc(annotator="Kush", pid="DGP-A-0001"):
    doc = white_sauce(annotator)
    doc["recipe_id"] = pid
    doc["status"] = "DONE"
    return doc


def write(path, doc):
    path.write_text(json.dumps(doc, indent=2) + "\n")
    return path


def snaps(path):
    return [pc.snapshot_entry(path, "FIRST_VALIDATE", "2026-11-06T10:00:00Z"),
            pc.snapshot_entry(path, "DONE", "2026-11-06T10:30:00Z")]


def build(tmp_path, files, **kw):
    ql = tmp_path / "questions.txt"
    ql.write_text("no questions\n")
    rep = tmp_path / "representability.csv"
    rep.write_text("item,answer\n")
    args = dict(letter="A", wave="P1", handbook_version="v1+AddendumA", question_log=ql, representability=rep,
                now="2026-11-06T11:00:00Z")
    args.update(kw)
    return pc.build_commitment(files, **args)


def test_snapshot_entry_records_hash_time_and_event(tmp_path):
    f = write(tmp_path / "DGP-A-0001.json", done_doc())
    e = pc.snapshot_entry(f, "DONE", "2026-11-06T10:30:00Z")
    assert e == {"sha256": hashlib.sha256(f.read_bytes()).hexdigest(), "utc": "2026-11-06T10:30:00Z", "event": "DONE"}
    with pytest.raises(pc.CommitError):
        pc.snapshot_entry(f, "LATER", "2026-11-06T10:30:00Z")


def test_commitment_has_the_design_shape_and_no_text(tmp_path):
    f = write(tmp_path / "DGP-A-0001.json", done_doc())
    c = build(tmp_path, [("DGP-A-0001", f, snaps(f))])
    assert set(c) == {"annotator_letter", "wave", "handbook_version", "created_utc", "question_log_sha256",
                      "representability_sha256", "files"}
    row = c["files"][0]
    assert set(row) == {"packet_id", "sha256", "size_bytes", "mtime_utc", "committed_utc", "snapshots"}
    assert row["sha256"] == hashlib.sha256(f.read_bytes()).hexdigest() and row["size_bytes"] == f.stat().st_size
    blob = json.dumps(c)
    assert "flour" not in blob and "milk" not in blob and "butter" not in blob


@pytest.mark.parametrize("mutate,code", [
    (lambda d: d.update(status="DRAFT"), "NOT_DONE"),
    (lambda d: d.update(annotator="Parv"), "ANNOTATOR_MISMATCH"),
    (lambda d: d["ingredient_lines"][0].update(entity="TODO"), "INVALID"),
])
def test_commitment_refuses_unfinished_or_wrong_files(tmp_path, mutate, code):
    doc = done_doc()
    mutate(doc)
    f = write(tmp_path / "DGP-A-0001.json", doc)
    with pytest.raises(pc.CommitError, match=code):
        build(tmp_path, [("DGP-A-0001", f, snaps(f))])


def test_commitment_refuses_missing_or_stale_snapshots(tmp_path):
    f = write(tmp_path / "DGP-A-0001.json", done_doc())
    with pytest.raises(pc.CommitError, match="SNAPSHOTS"):
        build(tmp_path, [("DGP-A-0001", f, snaps(f)[:1])])
    s = snaps(f)
    write(f, {**done_doc(), "notes": "edited after DONE"})
    with pytest.raises(pc.CommitError, match="LAST_SNAPSHOT"):
        build(tmp_path, [("DGP-A-0001", f, s)])


def test_commitment_refuses_a_packet_id_of_the_other_letter(tmp_path):
    f = write(tmp_path / "DGP-B-0001.json", done_doc(pid="DGP-B-0001"))
    with pytest.raises(pc.CommitError, match="PACKET_LETTER"):
        build(tmp_path, [("DGP-B-0001", f, snaps(f))])


# --- S164 code-review fixes (python-reviewer: 2 HIGH, 5 MEDIUM) ---------------------------------------------

def test_last_snapshot_must_be_done_and_follow_first_validate_in_log_order(tmp_path):
    f = write(tmp_path / "DGP-A-0001.json", done_doc())
    first = pc.snapshot_entry(f, "FIRST_VALIDATE", "2026-11-06T10:00:00Z")
    done = pc.snapshot_entry(f, "DONE", "2026-11-06T10:00:00Z")  # same second: order comes from the log
    with pytest.raises(pc.CommitError, match="SNAPSHOT_ORDER"):
        build(tmp_path, [("DGP-A-0001", f, [done, first])])
    assert build(tmp_path, [("DGP-A-0001", f, [first, done])])["files"][0]["snapshots"][-1]["event"] == "DONE"


def test_committed_files_must_equal_the_issued_packet_ids(tmp_path):
    f = write(tmp_path / "DGP-A-0001.json", done_doc())
    with pytest.raises(pc.CommitError, match="MISSING_PACKETS"):
        build(tmp_path, [("DGP-A-0001", f, snaps(f))], expected_ids=["DGP-A-0001", "DGP-A-0002"])
    with pytest.raises(pc.CommitError, match="EXTRA_PACKETS"):
        build(tmp_path, [("DGP-A-0001", f, snaps(f))], expected_ids=[])


def test_question_log_and_checklist_must_be_non_empty_files(tmp_path):
    f = write(tmp_path / "DGP-A-0001.json", done_doc())
    empty = tmp_path / "empty.txt"
    empty.write_text("")
    with pytest.raises(pc.CommitError, match="QUESTION_LOG"):
        build(tmp_path, [("DGP-A-0001", f, snaps(f))], question_log=empty)


def test_unreadable_label_file_is_a_commit_error_not_a_crash(tmp_path):
    f = tmp_path / "DGP-A-0001.json"
    f.write_text("{not json")
    with pytest.raises(pc.CommitError, match="LABEL_UNREADABLE"):
        build(tmp_path, [("DGP-A-0001", f, [])])


@pytest.mark.parametrize("value,ok", [("P1", True), ("P12", True), ("../x", False), ("P1/../x", False), ("", False)])
def test_wave_names_are_validated(value, ok):
    assert pc.valid_wave(value) is ok


def test_packet_ids_are_validated_per_letter():
    assert pc.valid_packet_id("DGP-A-0001", "A")
    for bad in ("DGP-B-0001", "DGP-A-1", "../DGP-A-0001", "DGP-A-0001/x"):
        assert not pc.valid_packet_id(bad, "A")


@pytest.mark.parametrize("salt", ["0" * 64, "ab" * 32, "a" * 63, "a1" * 16])
def test_low_entropy_or_short_salts_are_refused(salt):
    with pytest.raises(pp.PacketError):
        pp.build_packets(IDS, RECS, letter="A", seed_hex=SEED, salt_hex=salt)


def test_read_salt_refuses_symlink_into_repo_case_variants_and_open_permissions(tmp_path):
    good = "0123456789abcdef" * 4
    repo = tmp_path / "Repo"
    repo.mkdir()
    (repo / "salt.txt").write_text(good + "\n")
    link = tmp_path / "link.txt"
    link.symlink_to(repo / "salt.txt")
    with pytest.raises(pp.PacketError):
        pp.read_salt(link, repo_root=repo)
    with pytest.raises(pp.PacketError):
        pp.read_salt(Path(str(repo).replace("Repo", "repo")) / "salt.txt", repo_root=repo)
    priv = tmp_path / "private.txt"
    priv.write_text(good + "\n")
    priv.chmod(0o644)
    with pytest.raises(pp.PacketError, match="0600"):
        pp.read_salt(priv, repo_root=repo)
    priv.chmod(0o600)
    assert pp.read_salt(priv, repo_root=repo) == good
