import json
from pathlib import Path
from jsonschema import Draft202012Validator
from tests.fixtures.mech_v1_1_fixtures import entry

ROOT=Path(__file__).parents[2]


def test_frozen_reference_is_identical_to_reviewed_draft_contract():
    frozen=json.loads((ROOT/'ledgers/schemas/MECH.schema.json').read_text())
    draft=json.loads((ROOT/'registry/schemas/MECH.draft_v1_1.schema.json').read_text())
    assert frozen==draft


def test_reference_accepts_synthetic_shape_but_never_claims_it_is_evidence():
    schema=json.loads((ROOT/'ledgers/schemas/MECH.schema.json').read_text())
    validator=Draft202012Validator({k:v for k,v in schema.items() if k!='$id'})
    row=entry();assert list(validator.iter_errors(row))==[]
    row['is_evidence']=True
    assert list(validator.iter_errors(row))
