"""S181 demo snapshot builder: pure-function tests only (no engine load)."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import stat
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("s181_build_demo_snapshot", ROOT / "tools/s181_build_demo_snapshot.py")
S = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = S
_spec.loader.exec_module(S)

K = {"v": 1, "b": "X"}
UNK = {"v": None, "u": "NO_CUE"}


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------- deltas
@pytest.mark.parametrize("before,after,kind", [
    (None, K, "ADDED"),
    (K, None, "REMOVED"),
    (K, {"v": 2, "b": "X"}, "CHANGED"),
    (K, {"v": 1, "b": "OTHER_BASIS"}, "CHANGED"),
    (UNK, {"v": None, "u": "OTHER_REASON"}, "CHANGED"),
    (K, UNK, "BECAME_UNKNOWN"),
    (UNK, K, "RESOLVED"),
    (K, dict(K), None),
    (UNK, dict(UNK), None),
    (None, None, None),
])
def test_classify_delta(before, after, kind):
    assert S.classify_delta(before, after) == kind


def test_added_unknown_cell_is_added_not_became_unknown():
    assert S.classify_delta(None, UNK) == "ADDED"


def test_state_deltas_cover_blocks_and_skip_unchanged():
    prev = {"G": {"a": K, "gone": K}, "C": {"s": UNK}, "Q": {"same": K}, "Y": {"r": K}}
    cur = {"G": {"a": {"v": 2, "b": "X"}}, "C": {"s": K}, "Q": {"same": dict(K), "new": K}, "Y": {"r": UNK}}
    got = {(d["block"], d["field"]): d for d in S.state_deltas(prev, cur)}
    assert {k: d["kind"] for k, d in got.items()} == {
        ("G", "a"): "CHANGED", ("G", "gone"): "REMOVED", ("C", "s"): "RESOLVED",
        ("Q", "new"): "ADDED", ("Y", "r"): "BECAME_UNKNOWN"}
    assert got[("G", "a")]["before"] == K and got[("G", "a")]["after"] == {"v": 2, "b": "X"}
    assert got[("Q", "new")]["before"] is None and got[("G", "gone")]["after"] is None


def test_identical_states_produce_no_delta():
    s = {"G": {"a": K}, "C": {}, "Q": {"q": UNK}, "Y": {}}
    assert S.state_deltas(s, json.loads(json.dumps(s))) == []


def test_transitions_pair_consecutive_states_of_same_food_only():
    def st(step, food, v):
        return {"step": step, "event_id": f"E{step}", "food_id": food, "G": {"x": {"v": v, "b": "B"}}, "C": {}, "Q": {}, "Y": {}}
    states = [st(1, "ING-1", 1), st(1, "ING-2", 1), st(2, "ING-2", 1), st(3, "ING-1", 5)]
    tr = S.transitions(states)
    assert [(t["food_id"], t["from_state_index"], t["to_state_index"]) for t in tr] == [("ING-2", 1, 2), ("ING-1", 0, 3)]
    assert tr[0]["deltas"] == [] and tr[1]["deltas"][0]["kind"] == "CHANGED"


# ---------------------------------------------------------------- licence gate
def _files(text: str = "Chop the tomatoes.") -> dict[str, bytes]:
    return {"scenarios/x.json": S.canonical_json({"recipe_text": text, "recipe_sha256": sha(text)})}


def test_licence_gate_accepts_clean_output():
    S.licence_gate(_files(), {sha("Chop the tomatoes.")})


@pytest.mark.parametrize("marker", ["BBCGF-A1", "SRC-000002"])
def test_licence_gate_rejects_bbc_marker(marker):
    files = {**_files(), "ask/y.json": S.canonical_json({"corpus_ids": [marker]})}
    with pytest.raises(S.LicenceGateError, match=marker):
        S.licence_gate(files, {sha("Chop the tomatoes.")})


def test_licence_gate_rejects_recipe_sha_that_is_not_self_written():
    with pytest.raises(S.LicenceGateError, match="NOT_SELF_WRITTEN"):
        S.licence_gate(_files("Somebody else's recipe."), {sha("Chop the tomatoes.")})


def test_licence_gate_rejects_recipe_text_whose_declared_sha_is_wrong():
    files = {"scenarios/x.json": S.canonical_json({"recipe_text": "Other text.", "recipe_sha256": sha("Chop the tomatoes.")})}
    with pytest.raises(S.LicenceGateError, match="NOT_SELF_WRITTEN"):
        S.licence_gate(files, {sha("Chop the tomatoes.")})


def test_licence_gate_checks_raw_sha_inside_graph():
    files = {"scenarios/x.json": S.canonical_json({"graph": {"raw_sha256": "f" * 64}})}
    with pytest.raises(S.LicenceGateError, match="NOT_SELF_WRITTEN"):
        S.licence_gate(files, {sha("Chop the tomatoes.")})


@pytest.mark.parametrize("info", [
    {"public": False, "bbc_derived_edges": "INCLUDED_LOCAL_ONLY", "carbon_figures": "INCLUDED_LOCAL_ONLY"},
    {"public": True, "bbc_derived_edges": "INCLUDED_LOCAL_ONLY", "carbon_figures": "EXCLUDED"},
    {"public": True, "bbc_derived_edges": "EXCLUDED", "carbon_figures": "INCLUDED_LOCAL_ONLY"},
    {"public": "yes", "bbc_derived_edges": "EXCLUDED", "carbon_figures": "EXCLUDED"},
    {},
])
def test_mode_gate_rejects_anything_but_public_excluded(info):
    with pytest.raises(S.LicenceGateError):
        S.check_mode(info)


def test_mode_gate_accepts_public_excluded():
    S.check_mode({"public": True, "bbc_derived_edges": "EXCLUDED", "carbon_figures": "EXCLUDED"})


# ---------------------------------------------------------------- evidence sources
EVD = {"EVD-000001": {"id": "EVD-000001", "source_id": "SRC-000001", "source_family_id": "USDA-RETN-R6",
                      "provenance": {"source_ids": ["SRC-000001"]}},
       "EVD-000002": {"id": "EVD-000002", "source_id": "SRC-000009", "provenance": {"source_ids": ["SRC-000002"]}}}


def test_evidence_ids_found_anywhere_in_output():
    files = {"a.json": b'{"x":["EVD-000001=95.0%"],"t":"see [EVD-000007]"}', "b.json": b'"EVD-000001"'}
    assert S.evidence_ids(files) == ["EVD-000001", "EVD-000007"]


def test_evidence_sources_records_source_ids():
    assert S.evidence_sources(["EVD-000001"], EVD) == {
        "EVD-000001": {"source_ids": ["SRC-000001"], "source_family_id": "USDA-RETN-R6"}}


def test_evidence_sources_rejects_bbc_derived_row():
    with pytest.raises(S.LicenceGateError, match="EVD-000002"):
        S.evidence_sources(["EVD-000002"], EVD)


def test_evidence_sources_rejects_id_missing_from_ledger():
    with pytest.raises(S.LicenceGateError, match="EVD-999999"):
        S.evidence_sources(["EVD-999999"], EVD)


# ---------------------------------------------------------------- canonical JSON, signing
def test_canonical_json_is_sorted_and_has_no_whitespace():
    assert S.canonical_json({"b": [1, 2], "a": {"z": None, "y": "é"}}) == '{"a":{"y":"é","z":null},"b":[1,2]}'.encode("utf-8")


def test_canonical_json_refuses_nan():
    with pytest.raises(ValueError):
        S.canonical_json({"x": float("nan")})


def test_signature_round_trips_and_one_byte_change_fails(tmp_path):
    key = S.load_or_create_private_key(tmp_path / "priv" / "k.pem")
    manifest = S.canonical_json({"files": {"a.json": "00"}, "labels": ["DIAGNOSTIC_ONLY"]})
    sig, pub = S.sign(manifest, key), S.public_key_pem(key)
    assert S.verify_signature(manifest, sig, pub)
    tampered = manifest.replace(b'"00"', b'"01"')
    assert len(tampered) == len(manifest) and not S.verify_signature(tampered, sig, pub)
    assert not S.verify_signature(manifest, sig[:-4] + b"AAA=", pub)


def test_private_key_is_created_0600_and_reused(tmp_path):
    path = tmp_path / "priv" / "k.pem"
    k1 = S.load_or_create_private_key(path)
    assert stat.S_IMODE(path.stat().st_mode) == 0o600
    assert S.public_key_pem(S.load_or_create_private_key(path)) == S.public_key_pem(k1)


def test_private_key_path_inside_repo_is_refused():
    with pytest.raises(ValueError):
        S.load_or_create_private_key(ROOT / "web/public/snapshot/k.pem")


# ---------------------------------------------------------------- determinism
def _assemble(payloads):
    return S.assemble(payloads, git_head="a" * 40, generated_at="2026-11-17T00:00:00Z",
                      rung_config={"coord_food_guard": True, "lineage_vnext": True, "basis": "D-134"},
                      evidence_sources_map={}, inputs={"scenarios_sha256": "0" * 64})


def test_rebuild_is_byte_identical_and_independent_of_key_order():
    a = _assemble({"scenarios/x.json": {"b": 1, "a": [1, 2]}, "ask/y.json": {"q": "?"}})
    b = _assemble({"ask/y.json": {"q": "?"}, "scenarios/x.json": {"a": [1, 2], "b": 1}})
    assert a == b and list(a) == sorted(a)


def test_manifest_lists_every_file_with_its_sha256_and_labels():
    files = _assemble({"scenarios/x.json": {"a": 1}})
    m = json.loads(files["manifest.json"])
    assert files["manifest.json"] == S.canonical_json(m)
    assert m["files"] == {"scenarios/x.json": {"sha256": hashlib.sha256(files["scenarios/x.json"]).hexdigest(),
                                               "bytes": len(files["scenarios/x.json"])}}
    assert m["labels"] == ["DIAGNOSTIC_ONLY", "AI_DRAFTED_SCENARIOS", "SELF_WRITTEN_RECIPE_TEXT_ONLY", "NO_HUMAN_SIGNOFF_D085"]
    assert m["generated_at"] == "2026-11-17T00:00:00Z" and m["git_head"] == "a" * 40
    assert m["builder_version"] == S.BUILDER_VERSION and m["rung_config"]["basis"] == "D-134"


def test_changed_generation_time_changes_only_the_manifest():
    a = _assemble({"scenarios/x.json": {"a": 1}})
    b = S.assemble({"scenarios/x.json": {"a": 1}}, git_head="a" * 40, generated_at="2026-11-21T00:00:00Z",
                   rung_config={"coord_food_guard": True, "lineage_vnext": True, "basis": "D-134"},
                   evidence_sources_map={}, inputs={"scenarios_sha256": "0" * 64})
    assert a["scenarios/x.json"] == b["scenarios/x.json"] and a["manifest.json"] != b["manifest.json"]


def test_diff_snapshot_reports_changed_missing_and_extra():
    assert S.diff_snapshot({"a": b"1", "b": b"2", "c": b"3"}, {"a": b"1", "b": b"X", "d": b"4"}) == [
        "CHANGED b", "EXTRA_ON_DISK d", "MISSING_ON_DISK c"]


# ---------------------------------------------------------------- misc
def test_lookup_key_normalises_case_whitespace_and_nfkc():
    r = sha("Boil.")
    assert S.lookup_key("  How  MUCH\tvitamin C? ", r) == S.lookup_key("how much vitamin c?", r)
    assert S.lookup_key("q", None) == hashlib.sha256(b"q|").hexdigest()
    assert S.lookup_key("q", r) != S.lookup_key("q", None)


def test_jsonable_handles_dataclasses_enums_tuples_and_sets():
    import dataclasses
    import enum
    from fractions import Fraction

    class Kind(enum.Enum):
        A = "A"

    @dataclasses.dataclass(frozen=True)
    class D:
        k: Kind
        t: tuple
        s: frozenset
        f: Fraction

    assert S.jsonable(D(Kind.A, (1, (2, 3)), frozenset({"b", "a"}), Fraction(1, 3))) == {
        "k": "A", "t": [1, [2, 3]], "s": ["a", "b"], "f": "1/3"}
