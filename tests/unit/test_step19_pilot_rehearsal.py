"""Fixture-only Step19 workflow checks: never human or real-pilot evidence."""
import copy
import json

import pytest

from culinarystate.annotation.pilot_rehearsal import (
    RehearsalError, build_report, draw_frame, fixture_frame, make_packets,
    make_commitment, check_provenance, simulated_labels, write_report,
)


def setup_pair():
    draw = draw_frame(fixture_frame(), count=2, nonce="synthetic-demo")
    packets = make_packets(draw)
    labels = simulated_labels(packets)
    commitments = {k: make_commitment(k, packets[k], labels[k]) for k in ("A", "B")}
    return packets, labels, commitments


def test_reproducible_six_stage_report_is_never_a_human_gate():
    report = build_report()
    assert report == build_report()
    assert report["status"] == "REHEARSAL_ONLY"
    assert report["counts_as_human_gate"] is False
    assert len(report["stages"]) == 6
    assert report["stages"][3]["result"]["synthetic_checks_pass"] is True
    assert report["planted_controls"]["all_detected"] is True
    assert report["stages"][4]["result"]["interpretation"] == "SYNTHETIC_EQUALITY_ONLY_NOT_IAA"
    assert report["unfulfilled_real_pilot_requirements"]


def test_draw_is_order_invariant_and_never_selects_same_group():
    frame = fixture_frame()
    a = draw_frame(frame, count=3, nonce="demo")
    assert a == draw_frame(list(reversed(frame)), count=3, nonce="demo")
    assert len({r["group_id"] for r in a["selected"]}) == 3
    with pytest.raises(RehearsalError):
        draw_frame(frame, count=4, nonce="demo")


@pytest.mark.parametrize("mutation", [
    lambda r: r.update(recipe_id="REC-000001"),
    lambda r: r.update(source="FOODCOM"),
    lambda r: r.update(group_id="SPLITGRP-REC-1"),
    lambda r: r.update(text="a real or arbitrary text field"),
    lambda r: r.update(human_verdict="approved"),
])
def test_frame_refuses_non_fixture_fields_and_markers(mutation):
    frame = fixture_frame()
    mutation(frame[0])
    with pytest.raises(RehearsalError):
        draw_frame(frame, count=1, nonce="demo")


def test_duplicate_recipe_ids_rejected():
    frame = fixture_frame()
    frame.append(copy.deepcopy(frame[0]))
    with pytest.raises(RehearsalError):
        draw_frame(frame, count=1, nonce="demo")


@pytest.mark.parametrize("kind", ["tamper", "missing", "wrong_packet", "wrong_hash", "group_leak", "snapshot"])
def test_planted_integrity_errors_cannot_pass(kind):
    packets, labels, commitments = setup_pair()
    if kind == "tamper":
        labels["A"][0]["codes"] = ["changed"]
    elif kind == "missing":
        commitments["A"]["files"].pop()
    elif kind == "wrong_packet":
        commitments["A"]["files"][0]["packet_id"] = "SYNTHETIC-NOT-ISSUED"
    elif kind == "wrong_hash":
        commitments["A"]["files"][0]["sha256"] = "0" * 64
    elif kind == "group_leak":
        packets["A"][1]["group_id"] = packets["A"][0]["group_id"]
    else:
        commitments["A"]["files"][0]["snapshots"] = []
    result = check_provenance(packets, labels, commitments)
    assert result["synthetic_checks_pass"] is False
    assert result["counts_as_human_gate"] is False
    assert result["issues"]


def test_blank_packets_are_unfilled_and_independent_of_frame_order():
    packets, _, _ = setup_pair()
    for letter, entries in packets.items():
        for p in entries:
            assert p["packet_id"].startswith(f"SYNTHETIC-{letter}-")
            assert p["annotations"] == []
            assert p["human_verdict"] is None
            assert p["counts_as_human_gate"] is False


def test_missing_or_unmarked_packet_is_rejected_not_counted():
    packets, labels, commitments = setup_pair()
    packets["B"][0]["source"] = "BBC"
    with pytest.raises(RehearsalError):
        check_provenance(packets, labels, commitments)


@pytest.mark.parametrize("field,value", [("commitment_time", 1), ("tracked_in_git", True),
                                       ("timestamp_kind", "REAL_UTC"), ("human_verdict", "approved")])
def test_commitments_cannot_masquerade_as_real_provenance(field, value):
    packets, labels, commitments = setup_pair()
    commitments["A"][field] = value
    assert not check_provenance(packets, labels, commitments)["synthetic_checks_pass"]


def test_writer_protects_existing_human_content_and_frozen_paths(tmp_path):
    target = tmp_path / "SYNTHETIC-report.json"
    target.write_text(json.dumps({"human_verdict": "do not overwrite"}))
    with pytest.raises(RehearsalError):
        write_report(target, build_report())
    assert "do not overwrite" in target.read_text()
    with pytest.raises(RehearsalError):
        write_report(tmp_path / "report.json", build_report())
    with pytest.raises(RehearsalError):
        write_report(tmp_path / "annotation" / "gold" / "SYNTHETIC-report.json", build_report())


def test_new_synthetic_artifact_is_written_once(tmp_path):
    path = tmp_path / "SYNTHETIC-report.json"
    write_report(path, build_report())
    assert json.loads(path.read_text())["counts_as_human_gate"] is False
