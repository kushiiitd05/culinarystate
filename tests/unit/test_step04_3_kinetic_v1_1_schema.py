"""Record-level contract tests for the 04.3 KIN / KINPT v1.1 DRAFT schemas (S158, DRAFT_PENDING_H4).

The v1.1 drafts are new files beside the unchanged v1 drafts. Fixtures are SYNTHETIC SCHEMA FIXTURES
(tests/fixtures/kinetic_v1_1_fixtures.py): placeholder strings and dummy numbers, never data. A passing
test is evidence about the drafts' logic only; it is not H4 approval and signs no threshold.
"""
from __future__ import annotations

import copy
import json
import re
from collections.abc import Callable, Iterator
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft202012Validator

from tests.fixtures import kinetic_v1_1_fixtures as F

ROOT = Path(__file__).resolve().parents[2]
SCHEMAS = ROOT / "registry" / "schemas"
FILES = {"KIN": "KIN.draft_v1_1.schema.json", "KINPT": "KINPT.draft_v1_1.schema.json"}
V1 = {"KIN": "KIN.draft_v1.schema.json", "KINPT": "KINPT.draft_v1.schema.json"}

# Every path at which v1.1 may differ from v1 (the change list of kinetic_trajectory_contract_v1_1_DRAFT.md).
DECLARED_CHANGES = {
    "KIN": {"/$id", "/title", "/description", "/$comment", "/required", "/allOf", "/properties/digitisation_summary",
            "/$defs/analyte_form/required", "/$defs/analyte_form/properties/token",
            "/$defs/analyte_form/properties/token_status", "/$defs/analyte_form/allOf",
            "/$defs/analyte_form/description", "/properties/censoring_summary/allOf",
            "/properties/censoring_summary/description"},
    "KINPT": {"/$id", "/title", "/description", "/$comment", "/allOf", "/properties/digitized/required",
              "/properties/digitized/properties/read_independence", "/properties/digitized/allOf",
              "/properties/digitized/description", "/properties/tau/allOf"},
}


def load(name: str, files: dict[str, str] = FILES) -> dict[str, Any]:
    return json.loads((SCHEMAS / files[name]).read_text(encoding="utf-8"))


def validator(name: str) -> Draft202012Validator:
    return Draft202012Validator({k: v for k, v in load(name).items() if k != "$id"})


def flat_errors(name: str, inst: dict[str, Any]) -> list[str]:
    out: list[str] = []

    def walk(e: Any) -> None:
        out.append("/".join(map(str, e.absolute_path)) + " :: " + "/".join(map(str, e.absolute_schema_path))
                   + " :: " + e.message)
        for c in e.context or []:
            walk(c)

    for e in validator(name).iter_errors(inst):
        walk(e)
    return out


def walk_schema(node: Any, path: str = "") -> Iterator[tuple[str, dict[str, Any]]]:
    if isinstance(node, dict):
        yield path, node
        for k, v in node.items():
            yield from walk_schema(v, f"{path}/{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk_schema(v, f"{path}/{i}")


def diff_paths(a: Any, b: Any, path: str = "") -> set[str]:
    """JSON-pointer paths where a and b differ (dicts recurse; any other difference is reported whole)."""
    if isinstance(a, dict) and isinstance(b, dict):
        out: set[str] = set()
        for k in set(a) | set(b):
            if k not in a or k not in b:
                out.add(f"{path}/{k}")
            else:
                out |= diff_paths(a[k], b[k], f"{path}/{k}")
        return out
    return set() if a == b else {path}


# ----------------------------------------------------------------------------- structure
@pytest.mark.parametrize("name", ["KIN", "KINPT"])
def test_v1_1_schema_is_valid_draft_2020_12_and_marked_draft(name: str) -> None:
    s = load(name)
    Draft202012Validator.check_schema(s)
    assert s["$schema"].endswith("2020-12/schema")
    assert s["$id"] == f"culinarystate/draft/{FILES[name]}"
    assert "DRAFT_PENDING_H4" in s["title"]
    assert s["description"].startswith("schema_version 1.1.0-draft. STATUS DRAFT_PENDING_H4")
    for r in (n["$ref"] for _, n in walk_schema(s) if isinstance(n.get("$ref"), str)):
        assert r.startswith("#/$defs/") and r.split("/")[-1] in s["$defs"], r


@pytest.mark.parametrize("name", ["KIN", "KINPT"])
def test_no_open_object_and_no_default_keyword(name: str) -> None:
    for p, n in walk_schema(load(name)):
        matcher = re.search(r"/(if|contains|not)(/|$)", p)
        if "properties" in n and n.get("type") == "object" and not matcher:
            assert n.get("additionalProperties") is False, f"open object at {p}"
        assert "default" not in n, f"'default' keyword at {p}"


@pytest.mark.parametrize("name", ["KIN", "KINPT"])
def test_v1_1_differs_from_v1_only_at_the_declared_paths(name: str) -> None:
    v1, v11 = load(name, V1), load(name)
    assert v1["description"].startswith("schema_version 1.0.0-draft"), "the v1 draft must stay as it was"
    assert diff_paths(v1, v11) == DECLARED_CHANGES[name]
    assert set(v1["required"]) <= set(v11["required"])


def test_new_required_keys_and_threshold_reference() -> None:
    k = load("KIN")
    assert set(k["required"]) - set(load("KIN", V1)["required"]) == {"digitisation_summary"}
    ds = k["properties"]["digitisation_summary"]
    assert ds["properties"]["rule_ref"] == {"const": "THR-04K-03"}
    assert {"token", "token_status"} <= set(k["$defs"]["analyte_form"]["required"])
    p = load("KINPT")
    assert "read_independence" in p["properties"]["digitized"]["required"]


# ----------------------------------------------------------------------------- accepted variants
def _variants() -> Iterator[tuple[str, str, dict[str, Any]]]:
    k, pts, _ = F.series()
    yield "KIN", "plain three-point table series", k
    for p in pts:
        yield "KINPT", f"plain point {p['id']}", p
    kd, pd, _ = F.series(digitised=True)
    yield "KIN", "figure-digitised series with two independent reads", kd
    yield "KINPT", "digitised point", pd[1]
    kw = copy.deepcopy(k)
    kw["time_base"].update(unit="week", unit_raw="wk")
    yield "KIN", "raw weeks kept", kw
    yield "KINPT", "weeks converted exactly", F.kinpt(t=F.tau(2.0, "week", seconds=F.exact_seconds(2.0, "week")))
    yield "KINPT", "month kept raw, NOT_CONVERTED", F.kinpt(t=F.tau(3.0, "month"))
    yield "KINPT", "month by a stated convention", F.kinpt(t=F.tau(1.0, "month", seconds={
        "status": "CONVERTED_BY_STATED_CONVENTION", "value": 1.0, "convention": "synthetic convention text"}))
    yield "KINPT", "definitional zero converted to exactly 0 s", F.kinpt(t=F.tau(0, "min", "DEFINITIONAL_ZERO", seconds={
        "status": "CONVERTED_EXACT", "value": 0, "convention": None}))
    ref = F.tau(None, "UNKNOWN", "NOT_APPLICABLE_REFERENCE")
    yield "KINPT", "untreated reference without a tau, not converted", F.kinpt(t=ref)
    rng = F.tau(None, "min", "RANGE")
    rng.update(low=10.0, high=12.0)
    yield "KINPT", "interval tau kept as an interval", F.kinpt(t=rng)
    yield "KINPT", "same-reader repeat recorded (meaning open, H4)", F.kinpt(digitized="YES", reads="SAME_READER_REPEATED",
                                                                          t=F.tau(1.0, derivation="DIGITIZED"))
    yield "KINPT", "digitised, reads not reported", F.kinpt(digitized="YES", reads="NOT_REPORTED", t=F.tau(1.0, derivation="DIGITIZED"))
    yield "KINPT", "digitisation status UNKNOWN", F.kinpt(digitized="UNKNOWN")
    kt = copy.deepcopy(k)
    kt["target"]["analyte_form"] = {"status": "STATED", "text": "synthetic form text", "token": None,
                                    "token_status": "NO_APPROVED_REGISTRY"}
    yield "KIN", "stated analyte form, no approved token registry", kt
    kr = copy.deepcopy(kt)
    kr["target"]["analyte_form"].update(token="SYNTH_FORM_A", token_status="REGISTRY_TOKEN")
    yield "KIN", "registry token (the token list itself is an expert question)", kr
    kc = copy.deepcopy(k)
    kc["censoring_summary"].update(any_censored="YES", kinds_present=["DETECTED", "ND"])
    yield "KIN", "censored series", kc
    ku = copy.deepcopy(k)
    ku["lineage"].update(lab_group_id=None, lab_group_status="UNKNOWN", lab_group_basis="UNKNOWN")
    yield "KIN", "lab group UNKNOWN is a valid answer", ku
    kdu = copy.deepcopy(k)
    kdu["digitisation_summary"].update(any_digitised="UNKNOWN", two_read_status="NOT_ASSESSED")
    yield "KIN", "digitisation not assessed", kdu
    krel = copy.deepcopy(k)
    krel["target"].update(value_scale="RELATIVE_TO_C0", c0_reference="T0_SAMPLE", c0_obs_id="OBS-000001")
    yield "KIN", "relative-scale series with its C0 sample", krel


@pytest.mark.parametrize("name,label,inst", list(_variants()), ids=lambda x: x if isinstance(x, str) else "")
def test_accepted_variants_validate(name: str, label: str, inst: dict[str, Any]) -> None:
    assert flat_errors(name, inst) == [], label


# ----------------------------------------------------------------------------- negative controls
def _k(fn: Callable[[dict[str, Any]], Any]) -> dict[str, Any]:
    k = F.series()[0]
    fn(k)
    return k


def _p(fn: Callable[[dict[str, Any]], Any], base: dict[str, Any] | None = None) -> dict[str, Any]:
    p = copy.deepcopy(base or F.kinpt())
    fn(p)
    return p


def _af(**kw: Any) -> Callable[[dict[str, Any]], None]:
    return lambda k: k["target"]["analyte_form"].update(kw)


DIG_PT = F.kinpt(digitized="YES", t=F.tau(1.0, derivation="DIGITIZED"))
NEGATIVES: list[tuple[str, str, dict[str, Any], str]] = [
    # v1.1 additions on KIN
    ("KIN", "digitisation_summary missing", _k(lambda k: k.pop("digitisation_summary")), r"digitisation_summary"),
    ("KIN", "two-read rule pointing at another threshold", _k(lambda k: k["digitisation_summary"].update(rule_ref="THR-04K-01")), r"rule_ref"),
    ("KIN", "no digitised point but a two-read claim", _k(lambda k: k["digitisation_summary"].update(
        two_read_status="ALL_DIGITISED_POINTS_TWO_INDEPENDENT_READS")), r"two_read_status"),
    ("KIN", "digitised series with two_read_status NOT_APPLICABLE", _k(lambda k: k["digitisation_summary"].update(
        any_digitised="YES")), r"two_read_status"),
    ("KIN", "figure-digitised series that claims no digitised point", _k(lambda k: (
        k.update(series_origin_form="FIGURE_DIGITIZED"), k["provenance"].update(locator="x"))), r"any_digitised"),
    ("KIN", "token given without an approved registry", _k(_af(status="STATED", text="x", token="SYNTH_A",
                                                                token_status="NO_APPROVED_REGISTRY")), r"token"),
    ("KIN", "REGISTRY_TOKEN without a token", _k(_af(status="STATED", text="x", token_status="REGISTRY_TOKEN")), r"token"),
    ("KIN", "UNKNOWN spelled as a token", _k(_af(status="STATED", text="x", token="UNKNOWN", token_status="REGISTRY_TOKEN")), r"token"),
    ("KIN", "lower-case token", _k(_af(status="STATED", text="x", token="synth_a", token_status="REGISTRY_TOKEN")), r"token"),
    ("KIN", "token on an analyte form that was not reported", _k(_af(token="SYNTH_A", token_status="REGISTRY_TOKEN")), r"token"),
    ("KIN", "stated form with token_status NOT_APPLICABLE", _k(_af(status="STATED", text="x")), r"token_status"),
    ("KIN", "censored YES listing only uncensored kinds", _k(lambda k: k["censoring_summary"].update(
        any_censored="YES", kinds_present=["DETECTED", "TRUE_ZERO"])), r"kinds_present|contains"),
    # v1 rules that must survive
    ("KIN", "single time point", _k(lambda k: k.update(n_timepoints=1)), r"n_timepoints"),
    ("KIN", "historical clock", _k(lambda k: k["time_base"].update(clock="HISTORICAL_T")), r"clock"),
    ("KIN", "E4 without HUMAN_VERIFIED", _k(lambda k: k.update(evidence_tier="E4")), r"verification"),
    ("KIN", "recipe-plane split group", _k(lambda k: k["lineage"].update(split_group_id="SPLITGRP-REC-000001")), r"split_group_id"),
    ("KIN", "lab group key missing", _k(lambda k: k["lineage"].pop("lab_group_status")), r"lab_group_status"),
    ("KIN", "C0 from the t0 sample without its OBS", _k(lambda k: k["target"].update(c0_reference="T0_SAMPLE")), r"c0_obs_id"),
    ("KIN", "temperature REPORTED without a profile", _k(lambda k: k["condition_profile"].update(temperature_status="REPORTED")), r"temperature_profiles"),
    ("KIN", "profile without a clock tag", _k(lambda k: k["condition_profile"].update(temperature_status="REPORTED",
        temperature_profiles=[{x: y for x, y in F.PROFILE_ISO.items() if x != "clock"}])), r"clock"),
    # v1.1 additions on KINPT
    ("KINPT", "read_independence missing", _p(lambda p: p["digitized"].pop("read_independence")), r"read_independence"),
    ("KINPT", "not digitised but independent reads claimed", _p(lambda p: p["digitized"].update(
        read_independence="INDEPENDENT_READERS")), r"read_independence"),
    ("KINPT", "digitised with read_independence NOT_APPLICABLE", _p(lambda p: p["digitized"].update(
        read_independence="NOT_APPLICABLE"), DIG_PT), r"read_independence"),
    ("KINPT", "digitisation UNKNOWN but reads claimed", _p(lambda p: p["digitized"].update(
        status="UNKNOWN", read_independence="INDEPENDENT_READERS")), r"read_independence"),
    ("KINPT", "digitised tau on a point flagged not digitised", _p(lambda p: p.update(tau=F.tau(1.0, derivation="DIGITIZED"))), r"digitized"),
    ("KINPT", "reference without tau converted to seconds", _p(lambda p: p.update(tau=F.tau(
        None, "UNKNOWN", "NOT_APPLICABLE_REFERENCE", seconds={"status": "CONVERTED_EXACT", "value": 0, "convention": None}))), r"normalised_seconds"),
    ("KINPT", "interval tau collapsed to one seconds value (an invented midpoint)", _p(lambda p: p.update(tau={
        **F.tau(None, "min", "RANGE"), "low": 10.0, "high": 12.0,
        "normalised_seconds": {"status": "CONVERTED_EXACT", "value": 660, "convention": None}})), r"normalised_seconds"),
    ("KINPT", "definitional zero converted to a non-zero number of seconds", _p(lambda p: p.update(tau=F.tau(
        0, "min", "DEFINITIONAL_ZERO", seconds={"status": "CONVERTED_EXACT", "value": 5, "convention": None}))), r"normalised_seconds|value"),
    # v1 rules that must survive
    ("KINPT", "tau without clock", _p(lambda p: p["tau"].pop("clock")), r"clock"),
    ("KINPT", "month converted EXACTLY", _p(lambda p: p.update(tau=F.tau(1.0, "month", seconds={
        "status": "CONVERTED_EXACT", "value": 1.0, "convention": None}))), r"normalised_seconds|status"),
    ("KINPT", "digitised YES without tool", _p(lambda p: p["digitized"].update(tool=None), DIG_PT), r"tool"),
]


@pytest.mark.parametrize("name,label,inst,why", NEGATIVES, ids=[n[1] for n in NEGATIVES])
def test_negative_controls_rejected_for_the_intended_reason(name: str, label: str, inst: dict[str, Any], why: str) -> None:
    errs = flat_errors(name, inst)
    assert errs, f"{label} was ACCEPTED but must be rejected"
    assert any(re.search(why, e) for e in errs), f"{label}: rejected, but not for /{why}/: {errs[:4]}"


def test_r14_and_no_kinetic_value_in_the_new_text() -> None:
    """The v1.1 additions name no analyte system and carry no numeric scientific value."""
    for name in FILES:
        added = {p: n for p, n in walk_schema(load(name))
                 if any(p.startswith(c) for c in DECLARED_CHANGES[name] if c not in ("/$id", "/required"))}
        text = json.dumps(added)
        assert not re.search(r"ascorb|chlorophyll|pheoph|vitamin", text, re.I), name
        numbers = re.findall(r'"(?:const|minimum|maximum|exclusiveMinimum)":\s*(-?\d+(?:\.\d+)?)', text)
        assert set(numbers) <= {"0", "1"}, (name, numbers)
