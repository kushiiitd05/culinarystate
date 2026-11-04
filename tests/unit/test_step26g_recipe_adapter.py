"""Step 26g recipe-event -> simulation-input adapter, SIMLINK records, census (DRAFT_PENDING_16c_23a_26b).

Status: DRAFT_PENDING_16c_23a_26b. Hard dependencies 18 (draft only), 23a (applicability
engine) and 26b (sim_aa_1 / sim_chl_1) are not built. Synthetic replayed graphs only;
nothing is gold, no simulator runs, no estimate is produced, no sim_run_id is minted and
no ledger row is read or written.

Card (Plan Step 26g, D-027 R-15, R-20): per recipe event a route, the missing inputs and
``sim_run_id`` or NULL; any UNKNOWN required input or UNKNOWN / NOT_APPLICABLE
applicability => SIM_PROHIBITED, never defaulted; no literature or default value enters.
"""
from __future__ import annotations

import ast
import json
from fractions import Fraction
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from culinarystate.state_graph.event_log import EngineEvent, EventLogError
from culinarystate.state_graph.replay import ReplayConfig, replay_events
from culinarystate.state_graph.source_class import SourceClass
from culinarystate.simulation import recipe_adapter as ra
from culinarystate.simulation.recipe_adapter import (
    ApplicabilityBinding, ConditionBinding, ProfileSegment, SimInputError, SimLinkRecord, build_simulation_inputs,
    census_sha256, link_records, simulability_census, write_simlink_jsonl,
)

F = Fraction
REC = "SYN-26G"
AA, CHL = "sim_aa_1", "sim_chl_1"


# ---------------------------------------------------------------- synthetic replayed graphs
def intro(lot: str, k: int) -> EngineEvent:
    return EngineEvent(f"INTRO/{lot}", (-1, k), kind="INTRODUCE_LOT", produces=(lot,),
                       produced_types=((lot, "INGREDIENT_LOT"),))


def ev(eid: str, i: int, consumes=(), produces=(), **kw) -> EngineEvent:
    return EngineEvent(eid, (i, 0), consumes=tuple(consumes), produces=tuple(produces),
                       produced_types=tuple((p, "INTERMEDIATE") for p in produces), **kw)


def replay_ok(**kw):
    """INTRO/N1 -> E1 heat N1 -> N2 ; E2 consumes N2 -> N3. All synthetic."""
    return replay_events([intro("N1", 0), ev("E1", 0, ["N1"], ["N2"]), ev("E2", 1, ["N2"], ["N3"])], **kw)


def seg(a, b, lo, hi=None) -> ProfileSegment:
    return ProfileSegment(F(a), F(b), F(lo), F(hi if hi is not None else lo))


def b(event: str, name: str, value, unit=None, ref="COND-000001", kind="COND",
      cls=SourceClass.STRUCTURAL_RECIPE) -> ConditionBinding:
    return ConditionBinding(event, name, value, kind, ref, cls, unit)


def full_aa(event: str = "E1", ranged: bool = False) -> list[ConditionBinding]:
    # Synthetic placeholder magnitudes for structure tests only (SYNTHETIC_NOT_GOLD); not scientific values.
    dur = (F(5), F(7)) if ranged else F(6)
    return [b(event, "temperature_profile", (seg(0, 6, 90),), "min|degC"),
            b(event, "duration", dur, "min", ref="QNT-000001", kind="QNT"),
            b(event, "medium", "WATER", kind="EVT", ref="EVT-000001"),
            b(event, "water_ratio", F(4), "mL/g", ref="QNT-000002", kind="QNT"),
            b(event, "start_mode", "COLD_START", kind="EVT", ref="EVT-000001"),
            b(event, "lid_state", "OPEN", kind="EVT", ref="EVT-000001"),
            b(event, "piece_size_class", "SIZE_CLASS_A", kind="EVT", ref="EVT-000001"),
            b(event, "matrix_class", "MATRIX_X", kind="ING", ref="ING-000001")]


def app(event: str = "E1", system: str = AA, status: str = "APPLICABLE", ref: str | None = "APPDEC-SYN-1"):
    return ApplicabilityBinding(event, system, status, ref)


def by_event(s) -> dict:
    return {r.event_id: r for r in s.records}


# ---------------------------------------------------------------- module
def test_module_header_status_and_no_pandas_numpy():
    assert ra.STATUS == "DRAFT_PENDING_16c_23a_26b"
    src = Path(ra.__file__).read_text(encoding="utf-8")
    assert "DRAFT_PENDING_16c_23a_26b" in src.splitlines()[0]
    assert "import pandas" not in src and "import numpy" not in src
    pkg = Path(ra.__file__).with_name("__init__.py").read_text(encoding="utf-8")
    assert "DRAFT_PENDING_16c_23a_26b" in pkg.splitlines()[0]


def test_module_holds_no_float_literal_so_no_default_or_literature_value():
    tree = ast.parse(Path(ra.__file__).read_text(encoding="utf-8"))
    floats = [n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, (float, complex))]
    ints = {n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and type(n.value) is int}
    assert floats == [] and ints <= {0, 1, 2, -1}


def test_required_inputs_are_declared_per_system_with_card_references():
    assert set(ra.SYSTEM_REQUIREMENTS) == {AA, CHL}
    assert "water_ratio" in ra.SYSTEM_REQUIREMENTS[AA] and "medium_ph" in ra.SYSTEM_REQUIREMENTS[CHL]
    for names in ra.SYSTEM_REQUIREMENTS.values():
        assert {"temperature_profile", "duration"} <= set(names)
        assert all(n in ra.INPUT_SPECS for n in names)
    assert all(spec.card_ref for spec in ra.INPUT_SPECS.values())
    assert ra.REQUIREMENTS_STATUS == "PROPOSED_PENDING_26b"


def test_reason_codes_are_a_closed_vocabulary():
    for name in ra.INPUT_SPECS:
        assert {f"MISSING_{name.upper()}", f"CONFLICTING_{name.upper()}",
                f"SOURCE_NOT_PERMITTED_{name.upper()}"} <= ra.REASON_CODES
    assert {"APPLICABILITY_UNKNOWN", "APPLICABILITY_NOT_APPLICABLE", "EVENT_REJECTED_IN_REPLAY",
            "EVENT_SKIPPED_SCOPE", "NO_CONSUMED_ENTITY", "REPLAY_HAS_ISSUES"} <= ra.REASON_CODES


# ---------------------------------------------------------------- binding contract (structural refusals)
def test_bindings_refuse_floats_unit_conversion_text_and_untraced_values():
    with pytest.raises(SimInputError):
        b("E1", "duration", 6.0, "min")                                   # float, not exact
    with pytest.raises(SimInputError):
        b("E1", "duration", F(360), "s")                                  # no unit conversion
    with pytest.raises(SimInputError):
        b("E1", "medium", "boiling salted water")                          # raw text, not a code
    with pytest.raises(SimInputError):
        b("E1", "duration", F(6), "min", ref="")                           # untraced
    with pytest.raises(SimInputError):
        b("E1", "duration", F(6), "min", kind="PAPER")                     # provenance kind outside EVT/COND/QNT/ING
    with pytest.raises(SimInputError):
        b("E1", "not_an_input", F(1), "min")
    with pytest.raises(SimInputError):
        b("E1", "duration", (F(7), F(5)), "min")                           # inverted range
    with pytest.raises(SimInputError):
        b("E1", "duration", F(-1), "min")                                  # negative duration
    with pytest.raises(SimInputError):
        b("E1", "medium", "WATER", cls="STRUCTURAL_RECIPE")                # must be a SourceClass member


def test_profile_segments_must_be_exact_contiguous_and_start_at_zero():
    with pytest.raises(SimInputError):
        ProfileSegment(F(0), F(5), 90.0, F(90))                           # float
    with pytest.raises(SimInputError):
        ProfileSegment(F(5), F(5), F(90), F(90))                           # empty segment
    with pytest.raises(SimInputError):
        b("E1", "temperature_profile", (seg(1, 6, 90),), "min|degC")       # does not start at 0
    with pytest.raises(SimInputError):
        b("E1", "temperature_profile", (seg(0, 3, 90), seg(4, 6, 90)), "min|degC")  # gap
    with pytest.raises(SimInputError):
        b("E1", "temperature_profile", (), "min|degC")


def test_input_status_is_derived_from_the_value_not_declared():
    assert b("E1", "duration", F(6), "min").status == "MEASURED"
    assert b("E1", "duration", (F(5), F(7)), "min").status == "RANGE"
    assert b("E1", "duration", (F(6), F(6)), "min").status == "MEASURED"
    assert b("E1", "temperature_profile", (seg(0, 3, 90), seg(3, 6, 80, 95)), "min|degC").status == "RANGE"
    assert b("E1", "medium", "WATER").status == "MEASURED"


def test_applicability_needs_a_reference_unless_unknown():
    with pytest.raises(SimInputError):
        ApplicabilityBinding("E1", AA, "APPLICABLE", None)
    with pytest.raises(SimInputError):
        ApplicabilityBinding("E1", AA, "MAYBE", "APPDEC-1")
    with pytest.raises(SimInputError):
        ApplicabilityBinding("E1", "sim_other", "APPLICABLE", "APPDEC-1")
    assert ApplicabilityBinding("E1", AA, "UNKNOWN", None).status == "UNKNOWN"


# ---------------------------------------------------------------- adapter: three-valued, never defaulted
def test_no_bindings_gives_all_unknown_and_sim_prohibited_for_every_event():
    s = build_simulation_inputs(replay_ok(), recipe_id=REC, system_id=AA)
    assert [r.event_id for r in s.records] == ["INTRO/N1", "E1", "E2"]
    for r in s.records:
        assert r.route == "SIM_PROHIBITED" and r.applicability == "UNKNOWN"
        assert all(i.status == "UNKNOWN" and i.value is None and i.provenance == () for i in r.inputs)
        assert "APPLICABILITY_UNKNOWN" in r.reasons
        assert {f"MISSING_{n.upper()}" for n in ra.SYSTEM_REQUIREMENTS[AA]} <= set(r.reasons)
    assert "NO_CONSUMED_ENTITY" in by_event(s)["INTRO/N1"].reasons


def test_complete_inputs_and_applicable_give_simulate_with_provenance_and_null_sim_run():
    s = build_simulation_inputs(replay_ok(), recipe_id=REC, system_id=AA, bindings=full_aa(), applicability=[app()])
    r = by_event(s)["E1"]
    assert r.route == "SIMULATE" and r.reasons == () and r.all_inputs_present
    assert [i.name for i in r.inputs] == list(ra.SYSTEM_REQUIREMENTS[AA])
    assert all(i.status == "MEASURED" and i.provenance for i in r.inputs)
    assert dict((i.name, i.provenance) for i in r.inputs)["duration"] == (("QNT", "QNT-000001"),)
    assert r.targets == (("N1", 1, "INGREDIENT_LOT"),)
    assert r.recipe_event_id == f"{REC}#E1" and r.simulator_status == "NOT_BUILT_PENDING_26b"
    (link,) = [x for x in link_records(s) if x.event_id == "E1"]
    assert link.sim_run_id is None and link.route == "SIMULATE"


def test_range_inputs_are_simulable_and_keep_their_interval():
    s = build_simulation_inputs(replay_ok(), recipe_id=REC, system_id=AA, bindings=full_aa(ranged=True),
                                applicability=[app()])
    r = by_event(s)["E1"]
    dur = next(i for i in r.inputs if i.name == "duration")
    assert r.route == "SIMULATE" and dur.status == "RANGE" and dur.value == (F(5), F(7))


@pytest.mark.parametrize("status,code", [("UNKNOWN", "APPLICABILITY_UNKNOWN"),
                                         ("NOT_APPLICABLE", "APPLICABILITY_NOT_APPLICABLE")])
def test_complete_inputs_without_applicable_never_simulate(status, code):
    a = app(status=status, ref=None if status == "UNKNOWN" else "APPDEC-SYN-2")
    s = build_simulation_inputs(replay_ok(), recipe_id=REC, system_id=AA, bindings=full_aa(), applicability=[a])
    r = by_event(s)["E1"]
    assert r.all_inputs_present and r.route == "SIM_PROHIBITED" and r.reasons == (code,)


def test_one_missing_input_is_named_and_prohibits():
    bs = [x for x in full_aa() if x.input_name != "lid_state"]
    r = by_event(build_simulation_inputs(replay_ok(), recipe_id=REC, system_id=AA, bindings=bs,
                                         applicability=[app()]))["E1"]
    assert r.route == "SIM_PROHIBITED" and r.reasons == ("MISSING_LID_STATE",) and not r.all_inputs_present


def test_conflicting_bindings_become_unknown_never_picked():
    bs = full_aa() + [b("E1", "duration", F(9), "min", ref="QNT-000009", kind="QNT")]
    r = by_event(build_simulation_inputs(replay_ok(), recipe_id=REC, system_id=AA, bindings=bs,
                                         applicability=[app()]))["E1"]
    dur = next(i for i in r.inputs if i.name == "duration")
    assert dur.status == "UNKNOWN" and dur.value is None and r.reasons == ("CONFLICTING_DURATION",)
    assert dur.provenance == (("QNT", "QNT-000001"), ("QNT", "QNT-000009"))


def test_agreeing_bindings_merge_provenance():
    bs = full_aa() + [b("E1", "duration", F(6), "min", ref="COND-000007")]
    r = by_event(build_simulation_inputs(replay_ok(), recipe_id=REC, system_id=AA, bindings=bs,
                                         applicability=[app()]))["E1"]
    dur = next(i for i in r.inputs if i.name == "duration")
    assert r.route == "SIMULATE" and dur.provenance == (("COND", "COND-000007"), ("QNT", "QNT-000001"))


@pytest.mark.parametrize("cls", [SourceClass.COMPILED_RETENTION, SourceClass.KINETIC, SourceClass.MEASURED_TRANSITION,
                                 SourceClass.MODEL_GENERATED, SourceClass.MOLECULAR_PRIOR, SourceClass.COMPOSITION])
def test_literature_or_model_sourced_inputs_are_not_used_for_a_recipe_event(cls):
    bs = [x for x in full_aa() if x.input_name != "medium_ph"]
    bs = [x if x.input_name != "duration" else b("E1", "duration", F(6), "min", cls=cls) for x in bs]
    s = build_simulation_inputs(replay_ok(), recipe_id=REC, system_id=AA, bindings=bs, applicability=[app()])
    r = by_event(s)["E1"]
    assert r.route == "SIM_PROHIBITED" and r.reasons == ("SOURCE_NOT_PERMITTED_DURATION",)
    assert s.binding_counts["SOURCE_CLASS_NOT_PERMITTED"] == 1


def test_synthetic_inputs_are_flagged():
    bs = [x if x.input_name != "duration" else b("E1", "duration", F(6), "min", cls=SourceClass.SYNTHETIC)
          for x in full_aa()]
    r = by_event(build_simulation_inputs(replay_ok(), recipe_id=REC, system_id=AA, bindings=bs,
                                         applicability=[app()]))["E1"]
    assert r.synthetic_inputs is True and r.route == "SIMULATE"


def test_chl_requires_ph_and_not_water_ratio():
    bs = full_aa()
    s = build_simulation_inputs(replay_ok(), recipe_id=REC, system_id=CHL, bindings=bs,
                                applicability=[app(system=CHL)])
    r = by_event(s)["E1"]
    assert r.reasons == ("MISSING_MEDIUM_PH",)
    assert s.binding_counts["BINDING_INPUT_NOT_REQUIRED"] == 3              # water_ratio, start_mode, lid_state
    s2 = build_simulation_inputs(replay_ok(), recipe_id=REC, system_id=CHL,
                                 bindings=bs + [b("E1", "medium_ph", (F(5), F(6)), "pH")],
                                 applicability=[app(system=CHL)])
    assert by_event(s2)["E1"].route == "SIMULATE"


def test_rejected_and_skipped_events_are_prohibited_with_replay_reasons():
    bad = replay_events([intro("N1", 0), ev("E1", 0, ["N9"], ["N2"])])           # N9 unknown -> REJECTED
    r = by_event(build_simulation_inputs(bad, recipe_id=REC, system_id=AA, bindings=full_aa(),
                                         applicability=[app()]))["E1"]
    assert r.transaction_status == "REJECTED" and r.route == "SIM_PROHIBITED"
    assert {"EVENT_REJECTED_IN_REPLAY", "REPLAY_HAS_ISSUES"} <= set(r.reasons) and r.targets == ()
    sk = replay_ok(config=ReplayConfig(scope="EXPLICIT_ONLY"))
    r2 = by_event(build_simulation_inputs(sk, recipe_id=REC, system_id=AA, bindings=full_aa(),
                                          applicability=[app()]))["E1"]
    assert r2.transaction_status == "SKIPPED_SCOPE" and "EVENT_SKIPPED_SCOPE" in r2.reasons


def test_replay_with_any_issue_blocks_every_event():
    rp = replay_events([intro("N1", 0), ev("E1", 0, ["N1"], ["N2"]), ev("E2", 1, ["N1"], ["N3"])])
    assert rp.status == "FAIL"
    r = by_event(build_simulation_inputs(rp, recipe_id=REC, system_id=AA, bindings=full_aa(),
                                         applicability=[app()]))["E1"]
    assert r.transaction_status == "APPLIED" and r.reasons == ("REPLAY_HAS_ISSUES",)


def test_orphan_bindings_are_counted_not_attached():
    s = build_simulation_inputs(replay_ok(), recipe_id=REC, system_id=AA,
                                bindings=[b("E99", "duration", F(6), "min")],
                                applicability=[app(event="E99"), app(system=CHL)])
    assert s.binding_counts["BINDING_EVENT_NOT_IN_REPLAY"] == 1
    assert s.binding_counts["APPLICABILITY_EVENT_NOT_IN_REPLAY"] == 1
    assert s.binding_counts["APPLICABILITY_OTHER_SYSTEM"] == 1
    assert all(r.route == "SIM_PROHIBITED" for r in s.records)


def test_conflicting_applicability_is_unknown():
    s = build_simulation_inputs(replay_ok(), recipe_id=REC, system_id=AA, bindings=full_aa(),
                                applicability=[app(), app(status="NOT_APPLICABLE", ref="APPDEC-SYN-3")])
    r = by_event(s)["E1"]
    assert r.applicability == "UNKNOWN" and "APPLICABILITY_UNKNOWN" in r.reasons
    assert s.binding_counts["APPLICABILITY_CONFLICT"] == 1


def test_bad_arguments_are_refused():
    with pytest.raises(SimInputError):
        build_simulation_inputs(replay_ok(), recipe_id=REC, system_id="sim_other")
    with pytest.raises(SimInputError):
        build_simulation_inputs(replay_ok(), recipe_id="", system_id=AA)
    with pytest.raises(SimInputError):
        build_simulation_inputs("not a replay", recipe_id=REC, system_id=AA)  # type: ignore[arg-type]
    dup = replay_events([intro("N1", 0), ev("E1", 0, ["N1"], ["N2"]), ev("E1", 1, ["N2"], ["N3"])])
    with pytest.raises(SimInputError):
        build_simulation_inputs(dup, recipe_id=REC, system_id=AA)          # recipe_event_id must be unique


def test_records_are_deterministic_and_hash_covers_inputs():
    a = build_simulation_inputs(replay_ok(), recipe_id=REC, system_id=AA, bindings=full_aa(), applicability=[app()])
    b2 = build_simulation_inputs(replay_ok(), recipe_id=REC, system_id=AA, bindings=list(reversed(full_aa())),
                                 applicability=[app()])
    assert a.to_jsonl() == b2.to_jsonl() and a.sha256 == b2.sha256
    c = build_simulation_inputs(replay_ok(), recipe_id=REC, system_id=AA, bindings=full_aa(ranged=True),
                                applicability=[app()])
    assert by_event(a)["E1"].sha256 != by_event(c)["E1"].sha256
    rec = json.loads(a.to_jsonl().splitlines()[1])
    assert rec["replay_snapshot_sha256"] == replay_ok().snapshot_sha256


# ---------------------------------------------------------------- link records and writer
def test_link_record_never_carries_a_sim_run_id():
    (link, *_) = link_records(build_simulation_inputs(replay_ok(), recipe_id=REC, system_id=AA))
    assert link.sim_run_id is None
    with pytest.raises(SimInputError):
        SimLinkRecord(**{**link.fields(), "sim_run_id": "SIM-000001"})
    with pytest.raises(SimInputError):
        SimLinkRecord(**{**link.fields(), "route": "SIMULATE"})           # SIMULATE needs empty reasons
    with pytest.raises(SimInputError):
        SimLinkRecord(**{**link.fields(), "reasons": ("MADE_UP",)})
    assert link.to_canonical()["sim_run_id"] is None


def test_writer_writes_new_file_and_refuses_overwrite_protected_paths_and_ledger_names(tmp_path):
    links = link_records(build_simulation_inputs(replay_ok(), recipe_id=REC, system_id=AA, bindings=full_aa(),
                                                 applicability=[app()]))
    out = write_simlink_jsonl(links, tmp_path / "reports" / "simlink_draft.jsonl", root=tmp_path)
    lines = out.read_text(encoding="utf-8").splitlines()
    head = json.loads(lines[0])
    assert head["record"] == "SIMLINK_HEADER" and head["draft_status"] == ra.STATUS and head["count"] == 3
    assert all(json.loads(x)["sim_run_id"] is None for x in lines[1:])
    with pytest.raises(EventLogError):
        write_simlink_jsonl(links, out, root=tmp_path)                    # never overwrite
    for bad in ("ledgers/sim/x.jsonl", "data/x.jsonl", "exports/x.jsonl", "annotation/gold/x.jsonl"):
        with pytest.raises(EventLogError):
            write_simlink_jsonl(links, tmp_path / bad, root=tmp_path)
    for name in ("SIMLINK_v1.jsonl", "simlink_v2.JSONL", "SIM.jsonl"):
        with pytest.raises(SimInputError):
            write_simlink_jsonl(links, tmp_path / "reports" / name, root=tmp_path)
    with pytest.raises(SimInputError):
        write_simlink_jsonl(links + links, tmp_path / "reports" / "dup.jsonl", root=tmp_path)
    with pytest.raises(SimInputError):
        write_simlink_jsonl(["x"], tmp_path / "reports" / "bad.jsonl", root=tmp_path)  # type: ignore[list-item]


# ---------------------------------------------------------------- census
def _census_sets():
    full = build_simulation_inputs(replay_ok(), recipe_id="SYN-A", system_id=AA, bindings=full_aa(),
                                   applicability=[app()])
    part = build_simulation_inputs(replay_ok(), recipe_id="SYN-B", system_id=AA,
                                   bindings=[x for x in full_aa() if x.input_name not in ("lid_state", "water_ratio")],
                                   applicability=[app()])
    return full, part


def test_census_counts_routes_reasons_and_inputs_only():
    full, part = _census_sets()
    c = simulability_census([full, part])
    s = c["systems"][AA]
    assert c["draft_status"] == ra.STATUS and c["sets"] == 2 and s["events"] == 6
    assert s["route"] == {"SIMULATE": 1, "SIM_PROHIBITED": 5}
    assert s["all_inputs_present"] == 1
    assert s["reasons"]["MISSING_LID_STATE"] == 5 and s["reasons"]["MISSING_WATER_RATIO"] == 5
    assert s["reasons"]["APPLICABILITY_UNKNOWN"] == 4 and s["reasons"]["NO_CONSUMED_ENTITY"] == 2
    assert s["input_status"]["duration"] == {"MEASURED": 2, "RANGE": 0, "UNKNOWN": 4}
    assert s["missing_input_count"]["0"] == 1 and s["missing_input_count"]["2"] == 1
    assert s["applicability"] == {"APPLICABLE": 2, "NOT_APPLICABLE": 0, "UNKNOWN": 4}
    assert c["sim_run_ids_minted"] == 0 and c["estimates_emitted"] == 0


def test_census_holds_no_ids_or_text_and_is_deterministic():
    full, part = _census_sets()
    c1, c2 = simulability_census([full, part]), simulability_census([part, full])
    assert census_sha256(c1) == census_sha256(c2)
    blob = json.dumps(c1)
    for token in ("SYN-A", "SYN-B", "E1", "N1", "COND-", "QNT-", "EVT-", "\"WATER\"", "MATRIX_X", "APPDEC"):
        assert token not in blob
    with pytest.raises(SimInputError):
        simulability_census([full, full])                                  # same recipe twice


def test_empty_census_is_valid_and_zero():
    c = simulability_census([])
    assert c["sets"] == 0 and c["systems"] == {}


# ---------------------------------------------------------------- property: UNKNOWN never becomes SIMULATE
@settings(max_examples=60, deadline=None)
@given(keep=st.lists(st.booleans(), min_size=8, max_size=8),
       applicability=st.sampled_from(["APPLICABLE", "NOT_APPLICABLE", "UNKNOWN", None]))
def test_property_unknown_never_becomes_simulate(keep, applicability):
    bs = [x for x, k in zip(full_aa(), keep) if k]
    apps = [] if applicability is None else [app(status=applicability,
                                                 ref=None if applicability == "UNKNOWN" else "APPDEC-SYN-9")]
    for r in build_simulation_inputs(replay_ok(), recipe_id=REC, system_id=AA, bindings=bs, applicability=apps).records:
        unknown = any(i.status == "UNKNOWN" for i in r.inputs) or r.applicability != "APPLICABLE"
        if unknown:
            assert r.route == "SIM_PROHIBITED" and r.reasons
        assert (r.route == "SIMULATE") == (r.reasons == ())
        assert all(i.value is None for i in r.inputs if i.status == "UNKNOWN")
