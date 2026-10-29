"""Six-stage synthetic rehearsal, deliberately incapable of opening real pilot inputs.

This is a software integrity demonstration, not the real Step19 draw, PV1..10
implementation, human independence check, alpha/F1 estimator or approval gate.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path


class RehearsalError(ValueError):
    """Invalid synthetic input or unsafe output destination."""


MARKERS = {"status": "REHEARSAL_ONLY", "source": "AI_DRAFT_SYNTHETIC",
           "counts_as_human_gate": False}
FRAME_KEYS = set(MARKERS) | {"recipe_id", "group_id"}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode("utf-8")).hexdigest()


def _tag(**kwargs):
    return {**MARKERS, **kwargs}


def _marked(record):
    if any(record.get(k) != v or type(record.get(k)) is not type(v) for k, v in MARKERS.items()):
        raise RehearsalError("Only explicitly marked synthetic rehearsal records are accepted")


def _sid(value):
    if not isinstance(value, str) or not value.startswith("SYNTHETIC-") or len(value) <= 10:
        raise RehearsalError("Only SYNTHETIC- IDs are accepted")


def fixture_frame():
    """Four wholly artificial IDs in three groups; no text or source recipe IDs."""
    return [_tag(recipe_id=f"SYNTHETIC-RECIPE-{i}", group_id=f"SYNTHETIC-GROUP-{g}")
            for i, g in ((1, 1), (2, 1), (3, 2), (4, 3))]


def draw_frame(frame, *, count, nonce):
    """Fixture-only SHA256 ranking, not the preregistered pilot algorithm."""
    if type(count) is not int or count < 1 or not isinstance(nonce, str) or not nonce:
        raise RehearsalError("Positive integer count and explicit synthetic nonce required")
    if not isinstance(frame, list) or not frame:
        raise RehearsalError("Explicit nonempty synthetic frame required")
    ids = set()
    for row in frame:
        _marked(row)
        if set(row) != FRAME_KEYS:
            raise RehearsalError("Synthetic frame cannot contain recipe text or additional fields")
        _sid(row["recipe_id"])
        _sid(row["group_id"])
        if row["recipe_id"] in ids:
            raise RehearsalError("Duplicate recipe ID")
        ids.add(row["recipe_id"])
    canonical = sorted(frame, key=lambda r: r["recipe_id"])
    frame_hash = digest(canonical)
    ranked = sorted(canonical, key=lambda r: (digest([frame_hash, nonce, r["recipe_id"]]), r["recipe_id"]))
    selected, groups = [], set()
    for row in ranked:
        if row["group_id"] not in groups:
            selected.append(copy.deepcopy(row))
            groups.add(row["group_id"])
        if len(selected) == count:
            break
    if len(selected) != count:
        raise RehearsalError("Insufficient distinct synthetic groups")
    return _tag(algorithm="synthetic-sha256-ranking-v1-not-real-pilot-draw",
                frame_sha256=frame_hash, nonce=nonce, selected=selected)


def make_packets(draw):
    _marked(draw)
    result = {"A": [], "B": []}
    for letter in result:
        for index, row in enumerate(draw["selected"], 1):
            _marked(row)
            _sid(row["recipe_id"])
            _sid(row["group_id"])
            result[letter].append(_tag(packet_id=f"SYNTHETIC-{letter}-{index:04d}",
                                      recipe_id=row["recipe_id"], group_id=row["group_id"],
                                      annotations=[], human_verdict=None,
                                      fixture_content_sha256=digest(["SYNTHETIC-CONTENT", row["recipe_id"]])))
    return result


def simulated_labels(packets):
    """Controlled algorithmic codes; deliberately different from blank packets.

    No simulated code is a proposed Gold annotation; A/B are software fixture
    channels, never identities or accounts of human annotators.
    """
    return {letter: [_tag(packet_id=p["packet_id"], recipe_id=p["recipe_id"],
                         codes=["SYNTHETIC-CODE-1", "SYNTHETIC-CODE-2" if letter == "A" else "SYNTHETIC-CODE-3"])
                     for p in entries] for letter, entries in packets.items()}


def make_commitment(letter, packets, labels):
    if letter not in {"A", "B"} or len(packets) != len(labels):
        raise RehearsalError("Synthetic channels and complete file list required")
    files = []
    for packet, label in zip(packets, labels):
        _marked(packet)
        _marked(label)
        if label["packet_id"] != packet["packet_id"] or not packet["packet_id"].startswith(f"SYNTHETIC-{letter}-"):
            raise RehearsalError("Packet/channel mismatch")
        _sid(packet["packet_id"])
        # Fixed fixture timestamps are explicitly simulated, not attestations.
        files.append(_tag(packet_id=packet["packet_id"], sha256=digest(label),
                          packet_sha256=digest(packet),
                          snapshots=[{"sha256": digest({"synthetic_interim": packet["packet_id"]}), "time": 10},
                                     {"sha256": digest(label), "time": 20}]))
    return _tag(channel=letter, timestamp_kind="SIMULATED_TICKS_NOT_UTC", commitment_time=30,
                tracked_in_git=False, human_verdict=None, files=files)


def check_provenance(packets, labels, commitments):
    """Check synthetic content binding only; no independent human claim allowed."""
    issues = []
    if any(set(obj) != {"A", "B"} for obj in (packets, labels, commitments)):
        raise RehearsalError("Exactly synthetic software channels A and B required")
    for letter in ("A", "B"):
        commitment = commitments[letter]
        _marked(commitment)
        if (commitment.get("commitment_time") != 30
                or type(commitment.get("commitment_time")) is not int
                or commitment.get("timestamp_kind") != "SIMULATED_TICKS_NOT_UTC"
                or commitment.get("tracked_in_git") is not False
                or commitment.get("human_verdict") is not None):
            issues.append(f"{letter}:INVALID_SIMULATED_COMMITMENT")
        if commitment.get("channel") != letter:
            issues.append(f"{letter}:CHANNEL_MISMATCH")
        entries = packets[letter]
        by_packet, by_label, by_file = {}, {}, {}
        groups = set()
        for packet in entries:
            _marked(packet)
            for field in ("packet_id", "recipe_id", "group_id"):
                _sid(packet[field])
            pid = packet["packet_id"]
            if pid in by_packet or not pid.startswith(f"SYNTHETIC-{letter}-"):
                issues.append(f"{letter}:DUPLICATE_OR_WRONG_PACKET")
            if packet["group_id"] in groups:
                issues.append(f"{letter}:GROUP_LEAKAGE")
            groups.add(packet["group_id"])
            by_packet[pid] = packet
        for label in labels[letter]:
            _marked(label)
            _sid(label["packet_id"])
            if label["packet_id"] in by_label:
                issues.append(f"{letter}:DUPLICATE_LABEL")
            by_label[label["packet_id"]] = label
        for entry in commitment.get("files", []):
            _marked(entry)
            _sid(entry["packet_id"])
            if entry["packet_id"] in by_file:
                issues.append(f"{letter}:DUPLICATE_COMMITMENT")
            by_file[entry["packet_id"]] = entry
        if not by_packet or set(by_packet) != set(by_label) or set(by_packet) != set(by_file):
            issues.append(f"{letter}:MISSING_OR_WRONG_PACKET")
        for pid in set(by_packet) & set(by_label) & set(by_file):
            p, label, entry = by_packet[pid], by_label[pid], by_file[pid]
            if label.get("recipe_id") != p["recipe_id"]:
                issues.append(f"{letter}:RECIPE_MISMATCH")
            if entry.get("sha256") != digest(label) or entry.get("packet_sha256") != digest(p):
                issues.append(f"{letter}:HASH_MISMATCH")
            snapshots = entry.get("snapshots", [])
            if (len(snapshots) < 2 or snapshots[-1].get("sha256") != entry.get("sha256")
                    or any(type(s.get("time")) is not int or not 0 <= s["time"] < 30 for s in snapshots)
                    or [s.get("time") for s in snapshots] != sorted({s.get("time") for s in snapshots})):
                issues.append(f"{letter}:SNAPSHOT_INVALID")
    a = {(p["recipe_id"], p["group_id"], p["fixture_content_sha256"]) for p in packets["A"]}
    b = {(p["recipe_id"], p["group_id"], p["fixture_content_sha256"]) for p in packets["B"]}
    if a != b:
        issues.append("CROSS_CHANNEL_CONTENT_MISMATCH")
    return _tag(synthetic_checks_pass=not issues, issues=issues,
                counts_as_pilot_provenance=False,
                scope="HASH_PACKET_GROUP_SNAPSHOT_FIXTURES_ONLY_NOT_PV1_TO_PV10")


def _agreement(labels, provenance):
    if not provenance["synthetic_checks_pass"]:
        raise RehearsalError("No synthetic equality summary after integrity failure")
    a = {r["recipe_id"]: r["codes"] for r in labels["A"]}
    b = {r["recipe_id"]: r["codes"] for r in labels["B"]}
    if set(a) != set(b) or any(len(a[k]) != len(b[k]) for k in a):
        raise RehearsalError("Unmatched fixture vectors")
    matches = sum(x == y for k in a for x, y in zip(a[k], b[k]))
    total = sum(len(v) for v in a.values())
    return _tag(equal_cells=matches, total_cells=total,
                interpretation="SYNTHETIC_EQUALITY_ONLY_NOT_IAA")


def build_report():
    draw = draw_frame(fixture_frame(), count=2, nonce="SYNTHETIC-DEMO-NONCE-NOT-KUSH")
    packets = make_packets(draw)
    labels = simulated_labels(packets)
    commitments = {k: make_commitment(k, packets[k], labels[k]) for k in ("A", "B")}
    provenance = check_provenance(packets, labels, commitments)
    controls = {}
    for name in ("tampered_label", "missing_file", "wrong_packet", "wrong_hash", "group_leak", "missing_snapshot"):
        p, lab, c = copy.deepcopy((packets, labels, commitments))
        if name == "tampered_label":
            lab["A"][0]["codes"] = ["SYNTHETIC-TAMPERED"]
        elif name == "missing_file":
            c["A"]["files"].pop()
        elif name == "wrong_packet":
            c["A"]["files"][0]["packet_id"] = "SYNTHETIC-WRONG-PACKET"
        elif name == "wrong_hash":
            c["A"]["files"][0]["sha256"] = "0" * 64
        elif name == "group_leak":
            p["A"][1]["group_id"] = p["A"][0]["group_id"]
        else:
            c["A"]["files"][0]["snapshots"] = []
        verdict = check_provenance(p, lab, c)
        controls[name] = _tag(detected=not verdict["synthetic_checks_pass"], issues=verdict["issues"])
    return _tag(
        rehearsal_version="synthetic-six-stage-v1",
        stages=[_tag(stage=1, name="synthetic_frame_group_draw", result=draw),
                _tag(stage=2, name="blank_fixture_packets", result=packets),
                _tag(stage=3, name="simulated_hash_commitments", result=commitments),
                _tag(stage=4, name="fixture_integrity_checks", result=provenance),
                _tag(stage=5, name="simulated_agreement_summary", result=_agreement(labels, provenance)),
                _tag(stage=6, name="report", result=_tag(input_sha256=digest(fixture_frame()),
                                                       observations_sha256=digest(labels)))],
        simulated_observations=labels,
        planted_controls=_tag(all_detected=all(v["detected"] for v in controls.values()), controls=controls),
        unfulfilled_real_pilot_requirements=["H4_H5_AND_SIGNED_THR19P_ROWS", "KUSH_PRE_FRAME_NONCE",
            "APPROVED_REAL_FRAME_AND_DRAW_SPEC", "SOURCE_ELIGIBILITY_AND_LOCAL_TEXT",
            "TWO_BLIND_HUMAN_ANNOTATORS_AND_CAPACITY", "PRIVATE_MACHINES_AND_REAL_TIMING",
            "REAL_SNAPSHOTS_AND_TRACKED_COMMITMENTS_BEFORE_KEY", "COMPLETE_PV1_TO_PV10",
            "HUMAN_ADJUDICATION_AND_WAVE_SPECIFIC_IAA"])


def write_report(path, report):
    """Write new synthetic-named artifact only; never replace any existing file."""
    _marked(report)
    path = Path(path)
    resolved = path.resolve()
    if (not path.name.startswith("SYNTHETIC-") or path.suffix != ".json"
            or any(p in {"gold", "ledgers", "registry", "schemas", "schema_drafts", ".git"} for p in resolved.parts)
            or path.is_symlink()):
        raise RehearsalError("Use a new SYNTHETIC-*.json outside protected paths")
    if path.exists():
        raise RehearsalError("Never overwrite an existing artifact or human fields")
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n")
    except FileExistsError as exc:
        raise RehearsalError("Existing artifacts cannot be overwritten") from exc
