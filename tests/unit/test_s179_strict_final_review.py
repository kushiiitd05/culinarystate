"""Independent adversarial controls for the final local strict view; synthetic only."""
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace as NS

from culinarystate.generation import strict_v2
from tests.unit.test_s179_strict_emission_v2 import fixture


def test_frozen_v2_rounding_defect_is_reproducible():
    c, cond, row, packet = fixture()
    row["derived"]["retention_factor"]["value"] = .004
    out = strict_v2.render({"mode": "ANSWER", "precision": "QUANTITATIVE"}, {"boil": packet}, {"boil": c}, {cond["id"]: cond})
    assert "factor 0.00" in out["text"] and out["numbers"][0]["value"] > 0


def test_v3_does_not_round_small_measured_points_to_zero():
    from culinarystate.generation.strict_v3 import render
    c, cond, row, packet = fixture()
    row["derived"]["retention_factor"]["value"] = .004
    out = render({"mode": "ANSWER", "precision": "QUANTITATIVE"}, {"boil": packet}, {"boil": c}, {cond["id"]: cond})
    assert "factor 0.004 " in out["text"] and "factor 0.00 " not in out["text"]
    assert out["numbers"][0]["display_value"] == "0.004"


def test_v3_final_fallback_cannot_replace_canonical_point():
    from culinarystate.generation.strict_v3 import render
    c, cond, _, packet = fixture()
    out = render({"mode": "ANSWER", "precision": "QUANTITATIVE"}, {"boil": packet}, {"boil": c}, {cond["id"]: cond},
                 renderer=lambda lines: "0.00", fallback=lambda lines: "0.55")
    assert out["mode"] == "ABSTAIN" and not out["numbers"]


def test_display_does_not_convert_null_or_unknown_to_a_number():
    from culinarystate.decision.strict_display_v3 import physics_display
    step = {"event_id": "SYN-E1", "action": "boil", "stated": {"duration_min": "5", "temperature_c": None},
            "scenario": {"typical_core_end_c": None, "range_core_end_c": [40., None]},
            "numeric_provenance": {"stated.duration_min": {"basis": "UNKNOWN", "status": "UNKNOWN", "unit": "min"},
                                   "scenario.range_core_end_c.0": {"basis": "MODEL_DERIVED", "status": "MODEL_DERIVED", "unit": "degC", "source_field_refs": ["/synthetic"], "assumed_default_refs": ["SD-001"]}}}
    before = deepcopy(step)
    display = physics_display(step)
    assert step == before
    assert [(r["path"], r["value"]) for r in display["numbers"]] == [("scenario.range_core_end_c.0", 40.)]
    assert "stated.duration_min" in display["unavailable_paths"]
    assert display["numbers"][0]["basis"] == "MODEL_DERIVED"
    assert display["numbers"][0]["assumed_default_refs"] == ["SD-001"]


def test_display_endpoint_metadata_is_required_independently():
    from culinarystate.decision.strict_display_v3 import physics_display
    step = {"stated": {"temperature_c": ["90", "100"]}, "scenario": {}, "numeric_provenance": {
        "stated.temperature_c.0": {"basis": "TEXT_STATED", "status": "RANGE", "unit": "degC", "span_ids": ["SYN-SPAN"]}}}
    display = physics_display(step)
    assert [n["path"] for n in display["numbers"]] == ["stated.temperature_c.0"]
    assert "stated.temperature_c.1" in display["unavailable_paths"]


def test_nan_infinity_boolean_and_nonnumeric_text_are_never_display_numbers():
    from culinarystate.decision.strict_display_v3 import physics_display
    for value in [float("nan"), float("inf"), True, "nan", "1/0", "synthetic"]:
        step = {"stated": {"duration_min": value}, "scenario": {}, "numeric_provenance": {
            "stated.duration_min": {"basis": "TEXT_STATED", "status": "MEASURED", "unit": "min"}}}
        assert not physics_display(step)["numbers"]


def test_strict_view_never_calls_source_row_presence_measured_or_applicable():
    from culinarystate.decision.strict_display_v3 import recipe_display
    source = {"steps": [{"event_id": "SYN-E1", "route": "DIRECT", "action": "boil", "evidence": ["EVD-990001"]}],
              "physics": {"steps": [{"event_id": "SYN-E2", "action": "heat", "stated": {}, "scenario": {}, "numeric_provenance": {}}]}}
    out = recipe_display(source)
    assert len(out["steps"]) == 2  # heat-only output must not vanish
    assert out["steps"][0]["badge"] == "Unverified source row only"
    assert out["steps"][0]["applicability_certified"] is False
    assert out["steps"][1]["badge"] == "Condition applicability unknown"


def test_view_asset_uses_provenance_view_model_and_stays_offline():
    p = Path(__file__).parents[2] / "src/culinarystate/app/static/strict_v3.html"
    text = p.read_text()
    assert "detail.recipe_display" in text
    assert "number.basis" in text and "number.unit" in text
    assert "Math.round" not in text and "fonts.googleapis" not in text
    assert "innerHTML" not in text


def test_v3_adapter_keeps_linked_identity_and_precision_guards(monkeypatch):
    from culinarystate.decision.demo_context_v3 import StrictDemoContext
    from tests.unit.test_s179_strict_demo_v2 import context
    ctx, supplied = context(monkeypatch)
    strict = StrictDemoContext(**ctx.__dict__)
    assert strict._transform("synthetic query")["mode"] == "ABSTAIN"
    out = strict._transform("synthetic query", source_contexts={"boil": supplied})
    assert out["mode"] == "ANSWER" and out["numeric_provenance"][0]["display_value"] == "0.55"
    assert out["emission_guard"]["policy"] == "strict-emission-v3.0.0"
    ctx, supplied = context(monkeypatch, wrong_packet_process=True)
    strict = StrictDemoContext(**ctx.__dict__)
    assert strict._transform("synthetic query", source_contexts={"boil": supplied})["mode"] == "ABSTAIN"


def test_new_server_keeps_forwarding_guard_and_serves_only_new_asset():
    import types
    from culinarystate.app.strict_server_v3 import make_handler
    from tests.unit.test_s178_fixgov_forwarded_public import _Ctx, _FakeSock, LOCAL, PUBLIC

    def call(mode, forwarded=False):
        headers = 'X-Forwarded-For: 203.0.113.5\r\n' if forwarded else ''
        request = ('GET / HTTP/1.1\r\nHost: 127.0.0.1:8765\r\n' + headers + '\r\n').encode()
        sock = _FakeSock(request)
        make_handler(_Ctx(mode))(sock, ('127.0.0.1', 50000), types.SimpleNamespace())
        head, _, body = bytes(sock.out).partition(b'\r\n\r\n')
        return int(head.split(b' ')[1]), body

    status, body = call(PUBLIC)
    assert status == 200 and b'local research demo' in body and b'Math.round' not in body
    assert call(LOCAL, forwarded=True)[0] == 503
