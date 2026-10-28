"""Step 16a batch 2: DRAFT v1-rc schemas. v0 files are read-only; drafts live in reports/step16/schema_drafts."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from tests.fixtures.ledger_examples import EXAMPLES, base, i, m

ROOT = Path(__file__).resolve().parents[2]
V0 = ROOT / "ledgers" / "schemas"
DRAFTS = ROOT / "reports" / "step16" / "schema_drafts"
NAMES = ["EVT", "ENTITY", "STATE", "QNT", "POR", "INST", "ALLOC", "REF", "GRAPH", "SPLIT"]
V0_SHA256 = {  # pinned at draft time (v0 files must never change)
    "EVT": "b666bca63b481d44703049e9586553a59fd7acbf1504efa081201bf3cf56cc61",
    "ENTITY": "9c1474b2024352361b8e56b1831a4b68a5fb04d5095ac3cb42d7e4ae46b45165",
    "STATE": "b3a2f0db4df0181db8ef45e6e45d7a9d9274c633fc596e78bba29e48f2373b86",
    "QNT": "c98870c01cbd23279b5c8992dd3219348cdb2fb0221afd7c0c7e351afd14ced0",
    "POR": "1e867ba4e92767d51bb8850f88b188805d01e4431b9c8cdfd8d3197defe451e3",
    "INST": "91e322de2cf3717e75b4890d4f8c12d64077288628e55b4104c18ab5b52eb7c3",
    "ALLOC": "e1d78d4c92c7b11390c0900ef1a728ea9476e348d20288a4933cd5304c4870f0",
    "REF": "f7aff1ac5fe579847024489a80796d1d52fa8171339078210644ee8e95a42865",
    "GRAPH": "9340e2bafdd704a1de4a3138fa8ce7f93638b45f17a3e17adfda24d6fe9da33a",
    "SPLIT": "eb66d1f63f78da564fee72118a7132cda524c9f9b53d8285949d411cd4d10f23",
}


def _load(p: Path) -> dict:
    return json.loads(p.read_text())


def _draft(n: str) -> dict:
    return _load(DRAFTS / f"{n}.draft_v1.schema.json")


def _val(n: str) -> Draft202012Validator:
    return Draft202012Validator(_draft(n))


def ok(n, rec):
    return not list(_val(n).iter_errors(rec))


def walk(o):
    if isinstance(o, dict):
        for k, v in o.items():
            yield k, v
            yield from walk(v)
    elif isinstance(o, list):
        for v in o:
            yield from walk(v)


@pytest.mark.parametrize("n", NAMES)
def test_draft_is_valid_2020_12_and_rc(n):
    d = _draft(n)
    Draft202012Validator.check_schema(d)
    assert d["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    assert "1.0.0-rc" in d["description"]


@pytest.mark.parametrize("n", NAMES)
def test_no_default_keyword_anywhere(n):
    # a 'default' key as a *schema keyword* would imply UNKNOWN == 0; property names are not checked here
    def bad(o, in_props=False):
        if isinstance(o, dict):
            for k, v in o.items():
                if k == "default" and not in_props:
                    return True
                if bad(v, in_props=(k == "properties")):
                    return True
        elif isinstance(o, list):
            return any(bad(v) for v in o)
        return False
    assert not bad(_draft(n))


@pytest.mark.parametrize("n", NAMES)
def test_additive_over_v0(n):
    v0, v1 = _load(V0 / f"{n}.schema.json"), _draft(n)
    assert v0["required"] == v1["required"]
    assert set(v0["properties"]) <= set(v1["properties"])
    assert v0["$id"] == v1["$id"] and v0["additionalProperties"] is False


@pytest.mark.parametrize("n", NAMES)
def test_v0_example_still_validates(n):
    assert ok(n, EXAMPLES[n])


def test_v0_example_validates_for_every_example_with_a_draft():
    assert {k for k in EXAMPLES} >= set(NAMES)


def test_v0_files_untouched():
    for n in NAMES:
        assert hashlib.sha256((V0 / f"{n}.schema.json").read_bytes()).hexdigest() == V0_SHA256[n]


# ---- EVT
def evt(**kw):
    return base("EVT", recipe_id=i("REC"), step_index=0, ordinal=0, trajectory="PLANNED", **kw)


def test_evt_positive():
    assert ok("EVT", evt(event_kind="ACTION", process_id=i("PROC"), process_family_id="FAM:DRY_HEAT",
                         transformation_mode="THERMAL", modality="REQUIRED", temporal_relation="UNTIL",
                         clock="TAU_PROCESS", depends_on=[i("EVT", 2)], endpoint_leakage_flag=False,
                         tool_roles=[{"tool_id": i("TOOL"), "role": "HEAT_SOURCE"}],
                         process_modifiers={"lid_state": {"status": "UNKNOWN", "value": None},
                                            "intensity": {"status": "KNOWN", "value": "high"}}))


@pytest.mark.parametrize("bad", [
    {"event_kind": "SAUTE"}, {"transformation_mode": "BAKING"}, {"temporal_relation": "AFTER"},
    {"modality": "MAYBE"}, {"clock": "WALL"},
    {"tool_roles": [{"tool_id": i("TOOL"), "role": "FUEL"}]},
    {"process_modifiers": {"colour": {"status": "UNKNOWN"}}},
    {"process_modifiers": {"lid_state": {"status": "KNOWN", "value": None}}},
    {"process_modifiers": {"lid_state": {"status": "UNKNOWN", "value": "on"}}},
])
def test_evt_negative(bad):
    assert not ok("EVT", evt(**bad))


def test_evt_unmapped_action_requires_raw_verb():
    assert not ok("EVT", evt(event_kind="ACTION", process_id=None))
    assert ok("EVT", evt(event_kind="ACTION", process_id=None, action_raw="spatchcock"))
    assert ok("EVT", evt(event_kind="OBSERVATION", process_id=None))


def test_evt_family_reference_uses_existing_draft_hierarchy_namespace():
    assert ok("EVT", evt(process_family_id="FAM:DRY_HEAT"))
    assert ok("EVT", evt(process_family_id=None))
    assert not ok("EVT", evt(process_family_id=i("PROC")))


# ---- ENTITY
def ent(**kw):
    return base("ENTITY", recipe_id=i("REC"), label="the sauce", kind="INTERMEDIATE", **kw)


def test_entity():
    assert ok("ENTITY", ent(entity_type="MIXTURE", lifecycle="RESERVED", parent_entity_ids=[i("ENTITY", 2)],
                            created_by_event_id=i("EVT"), consumed_by_event_id=None,
                            facets={"V_FORM": {"value": "OTHER", "raw": "spatchcocked"}, "size_class": {"value": "large"}}))
    assert not ok("ENTITY", ent(lifecycle="VANISHED"))
    assert not ok("ENTITY", ent(entity_type="DISH"))
    assert not ok("ENTITY", ent(facets={"V_FORM": {"value": "OTHER"}}))  # OTHER needs raw
    assert not ok("ENTITY", ent(facets={"V_COLOUR": {"value": "red"}}))
    assert not ok("ENTITY", ent(parent_entity_ids=[i("ENTITY"), i("ENTITY")]))


# ---- STATE
def st(**kw):
    return base("STATE", entity_id=i("ENTITY"), state_version=0, belief="PLANNED", **kw)


def meta(status="KNOWN", origin="EXPLICIT_SOURCE", route="EXPLICIT"):
    return {"origin": origin, "status": status, "claim_route": route}


def test_state_meta_triple():
    assert ok("STATE", st(variables={"temp": {**m(180, "C"), "meta": meta()}}))
    assert ok("STATE", st(variables={"temp": {"status": "UNKNOWN", "meta": meta("UNKNOWN", "UNKNOWN", "MODEL")}}))
    for status in ["KNOWN", "UNKNOWN", "NOT_APPLICABLE", "CONFLICTING", "CENSORED"]:
        assert ok("STATE", st(variables={"x": {"status": "UNKNOWN", "meta": meta(status)}}))
    assert not ok("STATE", st(variables={"x": {"status": "UNKNOWN", "meta": meta("MEASURED")}}))
    assert not ok("STATE", st(variables={"x": {"status": "UNKNOWN", "meta": meta(route="GUESS")}}))
    assert not ok("STATE", st(variables={"x": {"status": "UNKNOWN", "meta": meta(origin="VIBES")}}))
    assert not ok("STATE", st(variables={"x": {"status": "UNKNOWN", "meta": {"origin": "UNKNOWN"}}}))


def test_state_unknown_is_not_zero():
    assert not ok("STATE", st(variables={"x": {"status": "MEASURED", "value": 0, "unit": "g",
                                              "meta": meta("UNKNOWN")}}))
    assert not ok("STATE", st(quantity={"status": "RANGE", "low": 0, "high": 0, "unit": "g",
                                       "meta": meta("NOT_APPLICABLE")}))


def test_state_history_fields_never_from_recipe_text():
    h = lambda route: st(variables={"enzyme_activity_state": {"status": "QUALITATIVE", "qualitative": "active",
                                                              "meta": meta(route=route)}})
    assert not ok("STATE", h("EXPLICIT"))
    assert not ok("STATE", h("INFERRED_LLM"))
    assert ok("STATE", h("SIMULATED"))
    assert ok("STATE", st(variables={"thermal_dose": {"status": "UNKNOWN"}}))
    assert not ok("STATE", st(variables={"thermal_dose": {"status": "MEASURED", "value": 3, "unit": "min"}}))


def test_state_layers():
    assert ok("STATE", st(existence={"value": "PRESENT", "meta": meta()}, container={"value": None, "meta": meta("UNKNOWN")}))
    assert not ok("STATE", st(container={"value": "bowl", "meta": meta("UNKNOWN")}))
    assert not ok("STATE", st(container={"value": "OTHER", "meta": meta()}))
    assert ok("STATE", st(container={"value": "OTHER", "raw": "dutch oven", "meta": meta()}))


# ---- QNT
def qnt(**kw):
    return base("QNT", raw="1 cup flour", parsed={"kind": "NUMBER", "value": 1, "unit_raw": "cup"},
                normalized={"status": "UNKNOWN"}, q_level="Q0", **kw)


def test_qnt_positive():
    assert ok("QNT", qnt(normalized_mass_low_g=100, normalized_mass_high_g=130,
                         intervals=[{"kind": "SOURCE_RANGE", "low": 100, "high": 130, "unit": "g"},
                                    {"kind": "EMPIRICAL_QUANTILES", "low": None, "high": None}],
                         quantity_scope="INGREDIENT_LINE", measured_state="cooked", multiplier=2,
                         dual_expression_check={"conflict": False}, unit_variant="US", locale="IN",
                         locale_evidence="katori", unit_system_era=None, as_purchased_vs_edible=None,
                         ast={"node_type": "ALTERNATIVE", "children": [
                             {"node_type": "RANGE", "low": 1, "high": 2},
                             {"node_type": "QUALITATIVE", "raw": "a pinch"}]}))
    assert ok("QNT", qnt(normalized_mass_low_g=None, normalized_mass_high_g=None))  # UNKNOWN allowed


@pytest.mark.parametrize("bad", [
    {"intervals": [{"kind": "MIDPOINT", "low": 1, "high": 2}]},
    {"quantity_scope": "RECIPE"},
    {"normalized_mass_low_g": -1},
    {"ast": {"node_type": "AVERAGE"}},
    {"ast": {"node_type": "QUALITATIVE", "value": 0}},
    {"ast": {"node_type": "UNKNOWN", "low": 0}},
    {"ast": {"node_type": "ADD", "children": [{"node_type": "NOPE"}]}},
    {"mass_g": {"status": "MEASURED", "value": 0, "unit": "g", "meta": meta("UNKNOWN")}},
    {"mass_g": {"status": "MEASURED", "value": 120, "unit": "g"}, "q_level": "Q6"},
    {"mass_g": {"status": "MEASURED", "value": 120, "unit": "g"}, "q_level": "Q2"},  # no portion_id
])
def test_qnt_negative(bad):
    assert not ok("QNT", {**qnt(), **bad})


def test_qnt_gram_traces_to_por_and_qlevel():
    g = {"status": "MEASURED", "value": 120, "unit": "g"}
    assert ok("QNT", {**qnt(), "mass_g": g, "q_level": "Q2", "portion_id": i("POR")})
    assert ok("QNT", {**qnt(), "mass_g": g, "q_level": "Q0"})
    assert ok("QNT", {**qnt(), "mass_g": {"status": "UNKNOWN"}, "q_level": "Q6"})
    rec = {**qnt(), "mass_g": g}
    del rec["q_level"]
    assert not ok("QNT", rec)  # Q-level mandatory
    for q in ["Q0", "Q1", "Q2", "Q3", "Q4", "Q5", "Q6"]:
        assert ok("QNT", {**qnt(), "q_level": q})
    assert not ok("QNT", {**qnt(), "q_level": "Q7"})


def test_qnt_ast_node_types():
    for t in ["RATIONAL", "RANGE", "ADD", "MULTIPLY", "FRACTION_OF", "REMAINDER_OF", "PACKAGE_CONTENT",
              "ALTERNATIVE", "QUALITATIVE", "OPEN_AMOUNT", "UNKNOWN"]:
        assert ok("QNT", {**qnt(), "ast": {"node_type": t}})


# ---- POR
def por(**kw):
    return base("POR", ingredient_id=i("ING"), from_unit_id=i("UNIT"), grams_per_unit=m(125, "g"), basis="DATABASE", **kw)


def test_por():
    assert ok("POR", por(state="raw", size_class="medium", mass_low_g=100, mass_high_g=150, sample_count=12,
                         source_diversity=3, source_record="FNDDS-123", licence="US public domain"))
    assert ok("POR", por(mass_low_g=None, mass_high_g=None, sample_count=None, source_diversity=None))
    assert not ok("POR", por(mass_low_g=-5))
    assert not ok("POR", por(sample_count=-1))
    assert not ok("POR", por(sample_count=1.5))
    assert not ok("POR", por(unknown_field=1))
    assert not ok("POR", {k: v for k, v in por().items() if k != "verification"})  # v0 verification still required


# ---- SPLIT and copy-forward
def test_split_strategy():
    rec = lambda s: base("SPLIT", dataset_id=i("DATASET"), strategy=s)
    assert ok("SPLIT", rec("split-group-disjoint"))
    assert ok("SPLIT", rec("STUDY_DISJOINT"))
    assert not ok("SPLIT", rec("GROUP_DISJOINT"))


@pytest.mark.parametrize("n", ["INST", "ALLOC", "REF", "GRAPH"])
def test_copy_forward_unchanged(n):
    a, b = _load(V0 / f"{n}.schema.json"), _draft(n)
    a["description"] = b["description"] = None
    assert a == b
