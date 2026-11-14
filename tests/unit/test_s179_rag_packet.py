"""RAG packet v2: allowed claim decided deterministically from State v2 (tomato A vs D)."""
import pytest

from culinarystate.composition import rag_packet as RP
from culinarystate.composition.state_full import StateBuilder


@pytest.fixture(scope="module")
def B():
    return StateBuilder()


def _p(B, text, step):
    s = next(x for x in B.build(text) if x["food"] == "tomato" and x["step"] == step)
    return RP.packet(s, "vitc")


def test_tomato_a_direct_numeric(B):
    p = _p(B, "Boil the tomatoes in water for 20 minutes.", 1)
    assert p["route"] == "DIRECT" and p["evidence_applied"] == ["EVD-002765=95.0%"]
    assert p["allowed_claim"] == "NUMERIC_FROM_CITED_EVIDENCE_ONLY"


def test_tomato_d_no_numeric_transfer(B):
    p = _p(B, "Mix the tomatoes, water, salt, vinegar and oil.\nBoil the mixture for 20 minutes.", 2)
    assert p["route"] == "UNKNOWN" and p["near_evidence"] == ["EVD-002765"] and p["evidence_applied"] == []
    assert p["compatibility"]["salt"] == p["compatibility"]["acid"] == "UNCONFIRMED"
    assert p["allowed_claim"] == "QUALITATIVE_ONLY_NO_NUMERIC_TRANSFER"
    assert "95" not in RP.render(p).split("NEAR EVIDENCE")[1].split("\n")[0]
