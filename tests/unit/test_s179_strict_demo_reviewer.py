"""Independent adapter check: packet query cannot replace the linked requested process."""
from culinarystate.decision import pipeline
from tests.unit.test_s179_strict_demo_v2 import context


def test_packet_process_cannot_override_linked_question_process(monkeypatch):
    ctx, supplied = context(monkeypatch)
    result = pipeline.answer()
    packet = result["packets"]["boil"]
    # Keep the linked question's process unchanged, but introduce a different
    # packet query/source process. An exact row/context pair is insufficient.
    assert result["slots"].processes == [("boil", "PROC-990001")]
    packet.query.process_id = "PROC-990002"
    packet.direct[0].row["process"]["process_id"] = "PROC-990002"
    supplied["process_id"] = "PROC-990002"
    out = ctx._transform("How much vitamin C remains after boiling carrot?", source_contexts={"boil": supplied})
    assert out["mode"] == "ABSTAIN" and not out["numeric_provenance"]
