"""SSOT §257B.16 C16 grounded generator (verbaliser + enforcement) and §257B.17 C17 citation layer: 12 cases each."""
import pytest

from culinarystate.generation import claims as C
from culinarystate.generation import enforce as E
from culinarystate.generation import verbalize as V
from culinarystate.retrieval.compatibility import Query
from culinarystate.retrieval.retriever import EvidencePacket, Hit


def _hit(i, rf=0.55, unit=None, name="broccoli", group=None, derived=True):
    row = {"id": f"EVD-{i:06d}", "matrix": {"raw_name": name} if name else {}, "process": {},
           "target": {"raw_name": "Vitamin C"}}
    if group:
        row["independence_group"] = group
    if derived:
        rfv = {"status": "MEASURED", "value": rf, **({"unit": unit} if unit else {})}
        row["derived"] = {"retention_factor": rfv, "direction": "DECREASE"}
    return Hit(row["id"], 0.8, 1.0, {}, row)


def _pk(*hits, cls="DIRECT", near=False):
    return EvidencePacket("q", Query(), cls, [] if near else list(hits), list(hits) if near else [])


ANS = {"mode": "ANSWER", "route": "PROCESS_EFFECT", "precision": "INTERVAL"}


class TestC16Generator:
    def test_clean(self):
        pk = {"boil": _pk(_hit(1), _hit(2, 0.62))}
        assert C.check_claims(V.verbalize("q", ANS, pk), pk["boil"])["unsupported"] == 0

    def test_missing_optional_fields(self):
        assert "UNKNOWN" not in V.verbalize("q", ANS, {"boil": _pk(_hit(1, name=None), near=True, cls="INTERPOLATED")})

    def test_missing_critical_field_rejected(self):
        with pytest.raises(ValueError, match="MISSING_MODE"):
            V.facts({"route": "PROCESS_EFFECT"}, {})

    def test_ambiguous_question_becomes_ask(self):
        assert V.verbalize("q", {"mode": "ASK", "ask_for": ["ingredient"]}, {}).endswith("?")

    def test_contradictory_upstream_conflict_packet_beats_numeric_cap(self):
        pk = {"boil": _pk(_hit(1, 0.4), _hit(2, 1.3), cls="CONFLICT")}
        t = V.verbalize("q", {**ANS, "precision": "QUANTITATIVE"}, pk)
        assert "disagree" in t and C.check_claims(t, pk["boil"])["numeric_claims"] == 0

    def test_source_locale_percent_and_fraction_rows_share_scale(self):
        pk = {"boil": _pk(_hit(1, 0.55), _hit(2, 70, "%"))}
        t = V.verbalize("q", ANS, pk)
        assert "0.55" in t and "0.70" in t and "70" not in t.replace("0.70", "")

    def test_near_duplicate_rows_give_single_value(self):
        t = V.verbalize("q", ANS, {"boil": _pk(_hit(1), _hit(2))})
        assert "from" not in t and t.count("0.55") == 1

    def test_ood_empty_packet_is_unknown(self):
        assert "UNKNOWN" in V.verbalize("q", ANS, {"boil": _pk(cls="UNSUPPORTED")})

    def test_explicit_unknown_abstain_has_no_numbers(self):
        t = V.verbalize("q", {"mode": "ABSTAIN", "reason": "X"}, {"boil": _pk(_hit(1))})
        assert C.check_claims(t, _pk(_hit(1)))["numeric_claims"] == 0

    def test_malformed_reference_sentence_removed(self):
        r = E.enforce("It keeps 0.55 [EVD-12]. Vitamin C decreases [EVD-000001].", ANS, {"boil": _pk(_hit(1))})
        assert r["text"] == "Vitamin C decreases [EVD-000001]." and r["removed"][0]["reason"] == "NON_EVIDENCE_CITATION"

    def test_version_stamped(self):
        assert V.facts(ANS, {})["version"] == V.VERSION and E.enforce("x.", ANS, {})["version"] == E.VERSION

    def test_replay_deterministic(self):
        pk = {"boil": _pk(_hit(1), _hit(2, 0.62))}
        assert V.verbalize("q", ANS, pk) == V.verbalize("q", ANS, pk)
        assert E.enforce("Keeps 0.9 [EVD-000001].", ANS, pk) == E.enforce("Keeps 0.9 [EVD-000001].", ANS, pk)


class TestC17Citations:
    PK = _pk(_hit(1), _hit(2, 62, "%"))

    def test_clean(self):
        assert C.check_claims("Keeps 55% [EVD-000001].", self.PK)["ucr"] == 0.0

    def test_missing_optional_unit_defaults_to_fraction(self):
        assert C.check_claims("Keeps 0.55 [EVD-000001].", _pk(_hit(1)))["unsupported"] == 0

    def test_missing_critical_value_is_unsupported(self):
        r = C.check_claims("Keeps 0.55 [EVD-000003].", _pk(_hit(3, derived=False)))
        assert r["claims"][0]["reason"] == "VALUE_NOT_IN_CITED_EVIDENCE"

    def test_ambiguous_scale_fraction_or_percent_both_match(self):
        assert C.check_claims("Keeps 0.62 or 62% [EVD-000002].", self.PK)["unsupported"] == 0

    def test_contradictory_cites_any_match_supports(self):
        assert C.check_claims("Keeps 0.62 [EVD-000001, EVD-000002].", self.PK)["unsupported"] == 0

    def test_locale_percent_word(self):
        assert C.check_claims("Keeps 55 percent [EVD-000001].", self.PK)["unsupported"] == 0

    def test_near_duplicate_citations(self):
        r = C.check_claims("Keeps 0.55 [EVD-000001][EVD-000001].", self.PK)
        assert r["unsupported"] == 0 and r["fabricated_citations"] == []

    def test_ood_number_without_rows_is_unsupported(self):
        assert C.check_claims("Keeps 0.55 [EVD-000001].", _pk(cls="UNSUPPORTED"))["unsupported"] == 1

    def test_explicit_unknown_no_numbers_gives_undefined_ucr(self):
        assert C.check_claims("Evidence is insufficient.", self.PK)["ucr"] is None

    @pytest.mark.parametrize("bad", ["EVD-0000011", "EVD-12", "evd-000001"])
    def test_malformed_ids_are_not_citations(self, bad):
        r = C.check_claims(f"Keeps 0.55 [{bad}].", self.PK)
        assert r["claims"][0]["reason"] == "UNCITED" and r["fabricated_citations"] == []

    def test_version_stamped(self):
        assert C.check_claims("x", self.PK)["version"] == C.VERSION

    def test_replay_deterministic(self):
        assert C.check_claims("Keeps 0.9 [EVD-000001].", self.PK) == C.check_claims("Keeps 0.9 [EVD-000001].", self.PK)
