"""SSOT §257B module contracts: the 12 mandatory unit-test cases, per runtime module.

clean · missing optional · missing critical · ambiguous surface form · contradictory upstream · source/locale
variation · near-duplicate · OOD concept/process · explicit UNKNOWN · malformed id/reference · version stamp ·
round-trip/replay. Plus the obligations: typed contract (reject malformed, no silent coercion), raw form preserved,
machine-readable reasons, deterministic replay.
"""
from fractions import Fraction

import pytest

from culinarystate.decision import feasibility as F
from culinarystate.decision import ood as O
from culinarystate.decision import policy as P
from culinarystate.decision import relevance as R
from culinarystate.decision.pipeline import Lexicon, parse_query
from culinarystate.retrieval.compatibility import Query, compatibility
from culinarystate.retrieval.retriever import EvidencePacket
from culinarystate.state_graph.engine import Add, Merge, Observe, Predict, Reserve, Split, Transform, replay
from culinarystate.state_graph.symqty import Base
from culinarystate.vocab.line_link import LineLinker

# ------------------------------------------------------------------ C11 feasibility
REQ = F.Requirements({"PROC-000001": "bake", "PROC-000002": "chop"}, {"PROC-000001": frozenset({"TOOL-000001"})},
                     {"PROC-000001": (20.0, 30.0, 60.0)}, {"ING-000007": frozenset({"ALLERGEN-000001"})})


class TestC11Feasibility:
    def test_clean(self):
        assert F.check(F.Action("PROC-000002"), F.Constraints(), REQ)["decision"] == "ALLOW"

    def test_missing_optional_fields_are_not_applicable(self):
        r = F.check(F.Action("PROC-000001"), F.Constraints(), REQ)
        assert r["checks"]["tool"]["status"] == r["checks"]["time"]["status"] == "NOT_APPLICABLE"

    def test_missing_critical_field(self):
        assert F.check(F.Action(""), F.Constraints(), REQ)["checks"]["input"]["reason"] == "MALFORMED_PROCESS_ID"

    def test_contradictory_constraints_reject_with_every_reason(self):
        r = F.check(F.Action("PROC-000001", ("ING-000007",), 90.0),
                    F.Constraints(frozenset(), 10.0, frozenset({"ALLERGEN-000001"})), REQ)
        assert r["decision"] == "REJECT"
        assert {c["reason"] for c in r["checks"].values() if c["status"] == "FAIL"} == \
            {"MISSING_REQUIRED_TOOL", "DURATION_EXCEEDS_BUDGET", "EXCLUDED_ALLERGEN"}

    def test_ood_process_is_unknown_not_allowed(self):
        assert F.check(F.Action("PROC-999999"), F.Constraints(), REQ)["decision"] == "UNKNOWN"

    @pytest.mark.parametrize("pid", ["bake", "PROC-1", "proc-000001", "PROC-0000001", "ING-000001", None])
    def test_malformed_identifier(self, pid):
        assert F.check(F.Action(pid), F.Constraints(), REQ)["decision"] == "REJECT"

    def test_version_stamped_and_replay_deterministic(self):
        a = F.check(F.Action("PROC-000001", ("ING-000007",)), F.Constraints(time_budget_min=5), REQ)
        assert a["version"] == F.VERSION and a == F.check(F.Action("PROC-000001", ("ING-000007",)),
                                                          F.Constraints(time_budget_min=5), REQ)

    def test_zero_budget_and_zero_duration_edges(self):
        assert F.check(F.Action("PROC-000002", (), 0.0), F.Constraints(time_budget_min=0.0), REQ)["decision"] == "ALLOW"


# ------------------------------------------------------------------ C13 relevance gate / C1 intent
class TestC13RelevanceAndC1Intent:
    def test_clean(self):
        assert R.relevance_gate("Can I steam instead of boiling?")["relevant"] is True

    def test_missing_critical_empty(self):
        assert R.relevance_gate("")["reason"] == "MALFORMED_EMPTY"

    @pytest.mark.parametrize("q", ["CAN I BOIL THIS INSTEAD OF FRYING IT?", "can i boil this instead of frying it",
                                   "Can I boil this  instead  of frying it ?!"])
    def test_surface_variation_same_decision(self, q):
        assert R.relevance_gate(q)["relevant"] is True and R.intent(q) == "COMPARE"

    def test_explicit_unknown_is_none(self):
        assert R.relevance_gate("paneer")["relevant"] is None

    def test_raw_form_preserved_and_version(self):
        g = R.relevance_gate("  Why do I need to brown the onions?  ")
        assert g["raw"] == "  Why do I need to brown the onions?  " and g["version"] == R.VERSION

    def test_contradictory_cues_high_relevance_wins(self):
        # navigation words + a substitution: process reasoning is needed (fail safe toward reasoning)
        assert R.relevance_gate("What is the next step if I steam instead of boil?")["relevant"] is True

    def test_count_question_about_loss_is_not_low(self):
        assert R.relevance_gate("How many vitamins do I lose when boiling?")["relevant"] is not False


# ------------------------------------------------------------------ C1 slot parser
LEX = Lexicon(LineLinker({"broccoli": "ING-1", "spinach": "ING-2", "green beans": "ING-3", "bean": "ING-4"}, set()),
              {"boil": "PROC-1", "steam": "PROC-2", "fry": "PROC-3"}, {"ING-1": ("ING-9",)}, {}, frozenset())


class TestC1SlotParser:
    def test_longest_mention_wins_over_substring(self):
        assert parse_query("How much folate do boiled green beans keep?", LEX).ingredient_id == "ING-3"

    def test_ood_ingredient_stays_unknown(self):
        assert parse_query("How much vitamin C does boiled romanesco keep?", LEX).ingredient_id is None

    def test_repeated_process_is_deduplicated(self):
        s = parse_query("Boil it, then boil again: how much vitamin C does boiled broccoli keep?", LEX)
        assert [p for _, p in s.processes] == ["PROC-1"]

    def test_no_target_is_none_not_guessed(self):
        assert parse_query("What happens when I boil broccoli?", LEX).target is None


# ------------------------------------------------------------------ C7 compatibility
FAM = {"PROC-1": "WET_HEAT", "PROC-2": "WET_HEAT", "PROC-3": "FAT_HEAT"}


def _evd(**over):
    e = {"matrix": {"ingredient_id": "ING-1", "raw_name": "broccoli", "initial_state": "raw", "food_group": "veg"},
         "process": {"process_id": "PROC-1", "step_process_ids": ["PROC-1"], "medium": "water"},
         "target": {"raw_name": "Vitamin C", "basis": "FRESH_WEIGHT"}, "tier": "E3"}
    for k, v in over.items():
        e[k] = {**e[k], **v} if isinstance(v, dict) else v
    return e


class TestC7Compatibility:
    def test_unknown_on_both_sides_is_neutral_not_mismatch(self):
        r = compatibility(Query(), _evd(matrix={"ingredient_id": None, "raw_name": ""}), None, FAM)
        assert not r["hard_mismatch"] and set(r["vector"].values()) <= {"UNKNOWN", "E3"}

    def test_missing_condition_record_is_unknown(self):
        r = compatibility(Query(ingredient_id="ING-1", time_min=(5, 10), temperature_c=(100, 100)), _evd(), None, FAM)
        assert r["vector"]["time"] == r["vector"]["temperature"] == "UNKNOWN"

    def test_censored_temperature_bound_is_unknown_not_match(self):
        cond = {"temperatures": [{"location": "CORE", "value": {"status": "CENSORED", "unit": "degC", "raw": "> 75 °C",
                                                               "censor": {"kind": "GT_STATED", "limit": 75.0}}}]}
        r = compatibility(Query(ingredient_id="ING-1", temperature_c=(80, 80)), _evd(), cond, FAM)
        assert r["vector"]["temperature"] == "UNKNOWN"

    def test_target_case_and_substring_variation(self):
        for t in ("vitamin c", "VITAMIN C", "Vitamin C, total ascorbic acid"):
            assert compatibility(Query(target=t), _evd(), None, FAM)["vector"]["target"] == "MATCH"

    def test_regex_special_chars_in_ingredient_name_are_literal(self):
        r = compatibility(Query(ingredient_name="c++ (beta)"), _evd(matrix={"ingredient_id": None,
                                                                             "raw_name": "c++ (beta) stew"}), None, FAM)
        assert r["vector"]["matrix"] == "NEAR"

    def test_score_bounded(self):
        r = compatibility(Query(ingredient_id="ING-1", process_id="PROC-1", target="vitamin c", medium="water",
                                basis="FRESH_WEIGHT", state="raw"), _evd(), None, FAM)
        assert 0.0 <= r["score"] <= 1.0


# ------------------------------------------------------------------ C14 OOD
class TestC14OOD:
    IDX = O.SupportIndex([{"status": "ACTIVE", "matrix": {"ingredient_id": "ING-1", "raw_name": "broccoli"},
                           "process": {"process_id": "PROC-1"}, "derived": {"retention_factor": {}}},
                          {"status": "DEPRECATED", "matrix": {"ingredient_id": "ING-2", "raw_name": "kale"},
                           "process": {"process_id": "PROC-1"}, "derived": {"retention_factor": {}}}])

    def test_deprecated_rows_give_no_support(self):
        assert self.IDX.support("ING-2", (), "kale", "PROC-1")["ood"] is True

    def test_parent_concept_gives_support(self):
        assert self.IDX.support("ING-5", ("ING-1",), None, "PROC-1")["pair"] == 1

    def test_cold_process_named(self):
        s = self.IDX.support("ING-1", (), "broccoli", "PROC-7")
        assert s["ood"] and s["cold_axes"] == ["process"]

    def test_name_with_regex_chars(self):
        assert self.IDX.support(None, (), "(?:.*)", "PROC-1")["ingredient"] == 0


# ------------------------------------------------------------------ C3 engine (replay, contradictions)
def _b(text):
    return Base.from_channels({"status": "UNKNOWN"}, {"status": "UNKNOWN"}, {"status": "UNKNOWN"}, text)


class TestC3Engine:
    EV = [Add("a", None, _b("2 eggs")), Add("b", None, _b("100g sugar")), Merge(("a", "b"), "mix", "whisk"),
          Transform("mix", "bake", sets=(("colour", "golden"),)), Observe("mix", "colour", "pale")]

    def test_replay_is_deterministic_and_order_sensitive(self):
        assert replay(self.EV).sha256() == replay(list(self.EV)).sha256()
        swapped = self.EV[:3] + [self.EV[4], self.EV[3]]
        assert replay(swapped).sha256() != replay(self.EV).sha256()

    def test_observation_overrides_plan_and_prediction_cannot_override_observation(self):
        g = replay(self.EV + [Predict("mix", "colour", "golden", "model-x")])
        assert g.current("mix").get("colour").value == "pale"
        assert any(a.get("ignored_prediction") == "golden" for a in g.audit)

    def test_contradictory_split_fractions_rejected(self):
        g = replay(self.EV[:3] + [Split("mix", (("p", Fraction(2, 3)), ("q", Fraction(2, 3))))])
        assert any("sum to" in i for i in g.issues) and "p" not in g.versions

    def test_operations_on_unknown_or_consumed_entities_are_issues_not_crashes(self):
        g = replay([Transform("ghost", "fry"), Reserve("ghost", "x", fraction=Fraction(1, 2))] + self.EV
                   + [Merge(("a",), "again")])
        assert "ghost" not in g.versions and "again" not in g.versions and g.issues

    def test_duplicate_add_is_flagged(self):
        assert any("added twice" in i for i in replay(self.EV[:1] * 2).issues)


# ------------------------------------------------------------------ policy (cascade, never over-claims)
def _pk(cls):
    return EvidencePacket("q", Query(), cls)


class TestPolicy:
    SLOTS = {"ingredient": "ING-1", "process": "PROC-1"}

    @pytest.mark.parametrize("cls", ["UNSUPPORTED", "IRRELEVANT"])
    def test_no_evidence_never_answers(self, cls):
        assert P.decide("How much vitamin C does boiled broccoli keep?", {"m": _pk(cls)}, self.SLOTS)["mode"] == "ABSTAIN"

    def test_empty_packets_abstain_not_crash(self):
        assert P.decide("How much vitamin C does boiled broccoli keep?", {}, self.SLOTS)["mode"] == "ABSTAIN"

    def test_all_options_infeasible_for_compare(self):
        d = P.decide("roast vs steam?", {"roast": _pk("DIRECT"), "steam": _pk("DIRECT")}, self.SLOTS,
                     feasibility={"roast": {"decision": "REJECT"}, "steam": {"decision": "REJECT"}})
        assert d["mode"] == "ABSTAIN" and d["rejected"] == ["roast", "steam"]

    def test_non_numeric_target_never_quantitative(self):
        d = P.decide("How much colour does boiled broccoli keep?", {"m": _pk("DIRECT")}, self.SLOTS, numeric_target=False)
        assert d["precision"] == "QUALITATIVE"

    def test_version_and_raw_query_stamped(self):
        q = "  what IS the next step?  "
        d = P.decide(q, {}, self.SLOTS)
        assert d["version"] == P.VERSION and d["query"] == q
