"""D-100 L6b: qwen-7B ING attribute drafts are validated against fixed enumerations; anything else -> UNKNOWN."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("iad", ROOT / "tools" / "s179_ing_attribute_draft.py")
iad = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(iad)

BATCH = [{"id": "ING-1", "name": "lemon juice"}, {"id": "ING-2", "name": "flour"}, {"id": "ING-3", "name": "tomato"}]


def test_prompt_lists_every_id_and_enums():
    p = iad.build_prompt(BATCH)
    for x in BATCH:
        assert x["id"] in p and x["name"] in p
    for e in iad.ENUMS["form"] + iad.ENUMS["acidic"]:
        assert e in p


def test_parse_valid_and_coerce_invalid_to_unknown():
    resp = json.dumps({"items": [
        {"id": "ING-1", "form": "LIQUID", "acidic": "YES", "vitamin_c": "YES"},
        {"id": "ING-2", "form": "powder", "acidic": "NO", "vitamin_c": "maybe"},
        {"id": "ING-9", "form": "SOLID", "acidic": "NO", "vitamin_c": "NO"}]})
    rows = iad.parse_response(resp, BATCH)
    by = {r["id"]: r for r in rows}
    assert by["ING-1"] == {"id": "ING-1", "form": "LIQUID", "acidic": "YES", "vitamin_c": "YES", "parse": "OK"}
    assert by["ING-2"]["form"] == "POWDER" and by["ING-2"]["vitamin_c"] == "UNKNOWN"
    assert by["ING-3"]["parse"] == "MISSING_FROM_RESPONSE" and by["ING-3"]["form"] == "UNKNOWN"
    assert "ING-9" not in by                                   # ids not asked for are dropped


def test_unparseable_response_gives_unknown_rows():
    rows = iad.parse_response("not json", BATCH)
    assert [r["parse"] for r in rows] == ["INVALID_JSON"] * 3
    assert all(r["acidic"] == "UNKNOWN" for r in rows)


def test_prompt_sha_is_stable():
    assert iad.prompt_sha() == iad.prompt_sha() and len(iad.prompt_sha()) == 64
