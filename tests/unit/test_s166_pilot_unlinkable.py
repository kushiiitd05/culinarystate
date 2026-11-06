"""S166 (prv review P1/P2/P5 of PR #8): nothing tracked may link a packet id to a recipe from public data.

prv mapped 7 of 7 superseded B packets to recipes: the tracked csv kept content_sha256 = sha256(public recipe
content), and the recipe ids are public in manifest_P1.csv. The main session found two more links of the same
kind: file_sha256 (the blank packet is fully determined by the public packet id and the public recipe) and the
sealed-key hash (the key is one of 7! = 5,040 mappings). Per-packet line and step counts can single out a
recipe too. Tracked values are now salted commitments sha256(salt | hash), checkable once the salt is revealed.
Synthetic fixtures only.
"""
import hashlib
import itertools
import json
import secrets

import pytest

from culinarystate.annotation import pilot_commit as pc
from culinarystate.annotation import pilot_packets as pp

IDS = [f"R{i}" for i in range(1, 8)]
RECS = {rid: {"source_family": "FOODCOM", "ingredient_lines": [f"{i} cup flour"] * i, "steps": ["Mix."] * (8 - i)}
        for i, rid in enumerate(IDS, 1)}
SEED = "9fa0008602a39537"
SALT_A = "3f9c1e7a5b2d8064c1a9e3f75b0d2c8e6a4f1b9d7c3e5a0f8b2d6c4e1a7f9b3d"
SALT_B = "b8e2d4f6a1c3e5079d2b4f6a8c0e1d3f5b7a9c2e4d6f8a0b1c3d5e7f9a2b4c6d"
TRACKED_COLUMNS = {"packet_id", "file_sha256_salted", "content_sha256_salted", "ai_prefill",
                   "model_outputs_embedded", "status"}


def _file_sha(doc):
    return hashlib.sha256((json.dumps(doc, indent=2, ensure_ascii=False) + "\n").encode()).hexdigest()


def _public_attack_values(packets):
    """Everything an outsider can compute from public ids, public recipes and the public packet-id pattern."""
    vals = {pp.content_hash(r) for r in RECS.values()}
    for p in packets:  # the blank doc depends only on (packet id, recipe): rebuild every pairing
        for rid in IDS:
            one, _ = pp.build_packets([rid], RECS, letter="B", seed_hex=SEED, salt_hex=SALT_B)
            doc = dict(one[0]["doc"], recipe_id=p["packet_id"],
                       source_ref=p["doc"]["source_ref"])
            vals.add(_file_sha(doc))
    for r in RECS.values():
        vals |= {str(len(r["ingredient_lines"])), str(len(r["steps"]))}
    return vals


def test_tracked_rows_hold_no_value_derivable_from_public_data():
    packets, _ = pp.build_packets(IDS, RECS, letter="B", seed_hex=SEED, salt_hex=SALT_B)
    rows = pp.manifest_rows(packets, salt_hex=SALT_B)
    assert set(rows[0]) == TRACKED_COLUMNS
    attack = _public_attack_values(packets)
    assert {_file_sha(p["doc"]) for p in packets} <= attack  # the attack does reach the unsalted hashes
    for row in rows:
        assert not {str(v) for k, v in row.items() if k != "packet_id"} & attack


def test_salted_commitments_check_out_once_the_salt_is_revealed():
    packets, _ = pp.build_packets(IDS, RECS, letter="B", seed_hex=SEED, salt_hex=SALT_B)
    rows = {r["packet_id"]: r for r in pp.manifest_rows(packets, salt_hex=SALT_B)}
    for p in packets:
        assert rows[p["packet_id"]]["file_sha256_salted"] == pp.salted(SALT_B, _file_sha(p["doc"]))
        assert rows[p["packet_id"]]["content_sha256_salted"] == pp.salted(SALT_B, p["content_sha256"])
    assert pp.salted(SALT_A, "x") != pp.salted(SALT_B, "x")


def test_sealed_key_commitment_cannot_be_found_by_trying_every_mapping():
    packets, key = pp.build_packets(IDS, RECS, letter="B", seed_hex=SEED, salt_hex=SALT_B)
    commitment = pp.key_commitment(key, salt_hex=SALT_B)
    pids = sorted(key)

    def key_bytes(mapping):
        return (json.dumps(mapping, indent=1, sort_keys=True) + "\n").encode("utf-8")

    tried = {hashlib.sha256(key_bytes(dict(zip(pids, perm)))).hexdigest()
             for perm in itertools.permutations(IDS)}
    assert len(tried) == 5040 and commitment not in tried
    assert commitment == pp.salted(SALT_B, hashlib.sha256(key_bytes(key)).hexdigest())


@pytest.mark.parametrize("salt", ["0123456789abcdef" * 4, "fedcba9876543210" * 4, ("0123456789ab" * 6)[:64],
                                  "abcdef01" * 8])
def test_patterned_salts_are_refused(salt):
    assert not pp.salt_ok(salt)


def test_generated_salts_are_accepted():
    assert all(pp.salt_ok(secrets.token_hex(32)) for _ in range(500))


def test_the_other_annotators_salt_is_refused(tmp_path):
    (tmp_path / "salt_P1_A.sha256").write_text(pp.salt_commitment(SALT_A) + "  salt_P1_A (secret, outside git)\n")
    assert pp.salt_reuse_problems(SALT_A, tracked_dir=tmp_path, letter="B", wave="P1")
    assert pp.salt_reuse_problems(SALT_B, tracked_dir=tmp_path, letter="B", wave="P1") == []


def test_commitment_requires_the_issued_packet_list(tmp_path):
    q = tmp_path / "q.txt"
    q.write_text("q\n")
    with pytest.raises(TypeError):
        pc.build_commitment([], letter="A", wave="P1", handbook_version="v1", question_log=q, representability=q,
                            now="2026-11-06T00:00:00Z")
