"""S179 (T5-C07-R5, D-079): kinetic units in the UNIT ledger, additive schema change, append-only, ambiguity kept."""
from __future__ import annotations

import hashlib
import json
import subprocess
from fractions import Fraction
from pathlib import Path

from culinarystate.ledgers import validate as V
from culinarystate.ledgers.registry import R
from culinarystate.mechanism import kinetic_unit_registry as K

ROOT = Path(__file__).resolve().parents[2]
LEDGER = ROOT / "ledgers" / "data" / "UNIT.jsonl"
SCHEMA = ROOT / "ledgers" / "schemas" / "UNIT.schema.json"
PRE_S179_LINES = 74
PRE_S179_SHA = "c7b317ae32c6c03bada10f381ef5a3e657acabd00bd0424882ffe2548dfe18c7"


def _rows():
    return [json.loads(line) for line in LEDGER.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_schema_change_is_additive_and_committed_json_matches_registry():
    props = R["UNIT"]["properties"]
    assert set(K.SCHEMA_DELTA["unit_type"]) <= set(props["unit_type"]["enum"])
    assert set(K.SCHEMA_DELTA["dimension"]) <= set(props["dimension"]["enum"])
    for old in ("PHYSICAL", "CULINARY_VOLUME", "COUNT_PORTION", "PACKAGE", "VERBAL_QUALITATIVE", "ENDPOINT_DESCRIPTOR"):
        assert old in props["unit_type"]["enum"]
    for old in ("MASS", "VOLUME", "COUNT", "TEMPERATURE", "TIME", "LENGTH", "NONE"):
        assert old in props["dimension"]["enum"]
    assert json.loads(SCHEMA.read_text(encoding="utf-8")) == R["UNIT"]


def test_ledger_is_append_only_first_74_rows_byte_identical():
    head = b"".join(LEDGER.read_bytes().splitlines(keepends=True)[:PRE_S179_LINES])
    assert hashlib.sha256(head).hexdigest() == PRE_S179_SHA


def test_every_draft_kinetic_unit_is_an_active_valid_ledger_row():
    rows = {r["canonical_name"]: r for r in _rows() if r.get("unit_type") == "KINETIC"}
    draft = {d["canonical_name"]: d for d in K.build_rows()}
    assert set(rows) == set(draft)
    for name, r in rows.items():
        assert r["status"] == "ACTIVE" and not V.errors(r), (name, V.errors(r))
        d = draft[name]
        assert set(r["aliases"]) == {a for a in d["aliases"].split("|") if a}
        refs = [x for x in r["external_refs"] if x.startswith("si_factor_exact:")]
        if d["si_factor_exact"]:
            assert refs == [f"si_factor_exact:{d['si_factor_exact']}"]
        else:
            assert refs == []


def test_ambiguous_calorie_stays_unknown_and_unsourced_rows_say_so():
    rows = {r["canonical_name"]: r for r in _rows() if r.get("unit_type") == "KINETIC"}
    amb = rows["kcal/mol"]
    assert amb["ambiguity_notes"] and amb["verification"]["status"] == "NEEDS_SOURCE"
    assert not any(x.startswith("si_factor") for x in amb["external_refs"])
    for name in ("kcal_th/mol", "kcal_IT/mol"):
        assert rows[name]["verification"]["status"] == "NEEDS_SOURCE"
    assert K.resolve("kcal/mol").factor_to_si is None


def test_registry_reads_ledger_ids_and_factors_agree():
    ids = K.ledger_unit_ids()
    assert set(ids) == {d["canonical_name"] for d in K.build_rows()}
    assert all(v.startswith("UNIT-") for v in ids.values())
    for d in K.build_rows():
        if d["si_factor_exact"]:
            assert K.resolve(d["canonical_name"]).factor_to_si == Fraction(d["si_factor_exact"])


def test_rung_a_quantity_units_are_unchanged_by_kinetic_rows():
    from culinarystate.extraction import rung_a_lexicon as L
    units = L.read_tables(ROOT)["units"]
    assert not ({"s^-1", "kJ/mol", "K", "degC"} & set(units))


def test_no_id_reused():
    ids = [r["id"] for r in _rows()]
    out = subprocess.run(["git", "show", "HEAD:ledgers/data/UNIT.jsonl"], cwd=ROOT, capture_output=True, text=True).stdout
    old = {json.loads(line)["id"] for line in out.splitlines() if line.strip()}
    new = [i for i in ids if i not in old]
    assert len(new) == len(set(new))
