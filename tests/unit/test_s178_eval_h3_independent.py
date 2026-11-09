"""S178 / T8-C12-R1: independent H3 scorer (claim extraction + EVD-id lookup), coverage with UCR, sign test."""
from __future__ import annotations

import ast
import math
from pathlib import Path

import pytest

from culinarystate.evaluation import h3_independent as H3
from culinarystate.evaluation import paired_stats as PS
from culinarystate.generation.claims import check_claims
from culinarystate.generation.enforce import enforce
from culinarystate.retrieval.compatibility import Query
from culinarystate.retrieval.retriever import EvidencePacket, Hit


def row(i, rf, *, ing="ING-1", raw="broccoli", proc="PROC-19", steps=("boil",), svar="SVAR-9", status="MEASURED",
        unit="fraction", direction=None):
    rf_d = {"status": status, "unit": unit}
    if status == "MEASURED":
        rf_d["value"] = rf
    elif status == "CENSORED":
        rf_d["censor"] = {"kind": "GT_CAP", "limit": rf}
    return {"id": f"EVD-{i:06d}", "status": "ACTIVE", "matrix": {"ingredient_id": ing, "raw_name": raw},
            "process": {"process_id": proc, "steps": list(steps), "raw_name": steps[0]},
            "target": {"state_variable_id": svar, "raw_name": "Vitamin C"},
            "derived": {"retention_factor": rf_d, **({"direction": direction} if direction else {})}}


EVD = {r["id"]: r for r in [
    row(1, 0.65), row(2, 0.80), row(3, 0.65, ing="ING-9", raw="spinach"),
    row(4, 0.65, ing=None, raw="stem, flower, fruit vegetables, such as asparagus, broccoli, cauliflower"),
    row(5, 0.40), row(6, 1.0), row(7, 0.975, status="CENSORED"), row(8, None, status="UNKNOWN"),
    row(9, 65, unit="%"), row(10, 0.65, proc="PROC-11", steps=("fry",)), row(11, 0.65, svar="SVAR-14"),
    row(12, None, status="UNKNOWN", direction="DECREASE")]}
CELL = {"ingredient_ids": ["ING-1"], "ingredient_names": ["broccoli"], "process_ids": ["PROC-19"],
        "process_names": ["boil"], "target_svars": ["SVAR-9", "SVAR-215"]}


def score(text, cell=CELL, **kw):
    return H3.score_answer(text, evd=EVD, cell=cell, **kw)


def verdicts(res, kind="NUMERIC"):
    return [c["verdict"] for c in res["claims"] if c["kind"] == kind]


# ---------------------------------------------------------------- independence of the code path

def test_module_does_not_import_the_enforcer_or_the_claim_checker():
    tree = ast.parse(Path(H3.__file__).read_text(encoding="utf-8"))
    mods = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.ImportFrom):
            mods.add(n.module or "")
            mods.update(f"{n.module}.{a.name}" for a in n.names)
        elif isinstance(n, ast.Import):
            mods.update(a.name for a in n.names)
    assert not [m for m in mods if "generation" in m or "claims" in m or "enforce" in m], mods


def test_enforced_answer_has_ucr_zero_by_construction_but_the_independent_scorer_still_flags_it():
    """The S173 tautology: enforce() keeps what check_claims accepts, so check_claims(B7) is clean. A value that matches
    a cited row of a different food passes both; the independent scorer calls it WRONG_CELL."""
    pk = {"boil": EvidencePacket("q", Query(), "DIRECT", [Hit("EVD-000003", .8, 1., {}, EVD["EVD-000003"])], [])}
    d = {"mode": "ANSWER", "route": "PROCESS_EFFECT", "precision": "INTERVAL"}
    text = "Boiled broccoli keeps 65% of its vitamin C [EVD-000003]."
    b7 = enforce(text, d, pk)["text"]
    assert b7 == text                                                          # the enforcer keeps it
    assert check_claims(b7, pk["boil"])["unsupported"] == 0                    # the same checker scores UCR = 0
    res = score(b7)
    assert verdicts(res) == ["WRONG_CELL"] and res["n_numeric_unsupported"] == 1


# ---------------------------------------------------------------- extraction

def test_extracts_percent_fraction_range_and_skips_times_and_counts():
    res = score("Boiled broccoli keeps 65% [EVD-000001]. It keeps 0.8 [EVD-000002] after 20 minutes at 100 °C from "
                "10 rows and 2 sources, 1.5 cups, step 3.")
    nums = [c for c in res["claims"] if c["kind"] == "NUMERIC"]
    assert [c["raw_value"] for c in nums] == [0.65, 0.8] and verdicts(res) == ["SUPPORTED", "SUPPORTED"]
    rng = [c for c in score("Boiling can retain between 25% and 80% of its vitamin C [EVD-000001, EVD-000002].")["claims"]]
    assert [c["part"] for c in rng] == ["lo", "hi"] and [c["raw_value"] for c in rng] == [0.25, 0.8]


def test_loss_phrasing_flips_to_retention_and_reduced_to_does_not():
    assert verdicts(score("Boiling loses 35% of the vitamin C [EVD-000001].")) == ["SUPPORTED"]     # 1 - 0.35 = 0.65
    assert verdicts(score("A 20% loss of vitamin C was measured [EVD-000002].")) == ["SUPPORTED"]   # 0.80
    assert verdicts(score("Boiling reduces vitamin C to 65% [EVD-000001].")) == ["SUPPORTED"]       # level, not loss
    assert verdicts(score("It loses up to 35% [EVD-000001].")) == ["SUPPORTED"]
    res = score("Boiling loses 65% [EVD-000001].")                                                  # retention 0.35 != 0.65
    assert verdicts(res) == ["VALUE_MISMATCH"] and res["claims"][0]["semantics"] == "LOSS"
    assert score("Boiling retains 65% [EVD-000001].")["claims"][0]["semantics"] == "RETENTION"
    assert score("About 65% [EVD-000001].")["claims"][0]["semantics"] == "ASSUMED_RETENTION"


def test_citation_binding_is_positional_not_any_id_in_the_sentence():
    # S173 checker: any id in the sentence may support any number. Here 0.40 follows [EVD-000001] (0.65): mismatch.
    res = score("Broccoli keeps 65% [EVD-000001] and 40% [EVD-000005].")
    assert [c["cites"] for c in res["claims"]] == [["EVD-000001"], ["EVD-000005"]]
    assert verdicts(res) == ["SUPPORTED", "SUPPORTED"]
    swapped = score("Broccoli keeps 40% [EVD-000001] and 65% [EVD-000005].")
    assert verdicts(swapped) == ["VALUE_MISMATCH", "VALUE_MISMATCH"]
    pk = EvidencePacket("q", Query(), "DIRECT", [Hit("EVD-000001", 1, 1, {}, EVD["EVD-000001"]),
                                                 Hit("EVD-000005", 1, 1, {}, EVD["EVD-000005"])], [])
    assert check_claims("Broccoli keeps 40% [EVD-000001] and 65% [EVD-000005].", pk)["unsupported"] == 0   # S173 accepts


def test_citation_only_fragment_attaches_and_preceding_group_is_the_fallback():
    assert verdicts(score("Broccoli keeps 65%. [EVD-000001]")) == ["SUPPORTED"]
    res = score("According to [EVD-000001] about 65% remains.")
    assert res["claims"][0]["binding"] == "PRECEDING" and verdicts(res) == ["SUPPORTED"]
    assert score("Broccoli keeps 65% remains.")["claims"][0]["binding"] == "NONE"


# ---------------------------------------------------------------- ledger lookup and relevance

def test_every_verdict_class():
    assert verdicts(score("Keeps 65%.")) == ["UNCITED"]
    assert verdicts(score("Keeps 65% [EVD-999999].")) == ["NONEXISTENT_ID"]
    assert verdicts(score("Keeps 65% [EVD-000008].")) == ["ROW_NO_VALUE"]
    assert verdicts(score("Keeps 50% [EVD-000001].")) == ["VALUE_MISMATCH"]
    assert verdicts(score("Keeps 65% [EVD-000001].")) == ["SUPPORTED"]
    assert verdicts(score("Keeps 65% [EVD-000009].")) == ["SUPPORTED"]                # row stored as 65 % -> 0.65
    assert set(H3.VERDICTS) >= {"SUPPORTED", "UNCITED", "NONEXISTENT_ID", "ROW_NO_VALUE", "VALUE_MISMATCH", "WRONG_CELL"}


def test_relevance_levels_and_minimum_relevance():
    assert verdicts(score("Keeps 65% [EVD-000003].")) == ["WRONG_CELL"]               # right value, spinach row
    assert verdicts(score("Keeps 65% [EVD-000010].")) == ["WRONG_CELL"]               # fry row
    assert verdicts(score("Keeps 65% [EVD-000011].")) == ["WRONG_CELL"]               # folate svar
    agg = score("Keeps 65% [EVD-000004].")                                             # aggregate row that names broccoli
    assert verdicts(agg) == ["SUPPORTED"] and agg["claims"][0]["relevance"] == "SIMILAR"
    assert verdicts(score("Keeps 65% [EVD-000004].", min_relevance="EXACT")) == ["WRONG_CELL"]
    exact = score("Keeps 65% [EVD-000001].")
    assert exact["claims"][0]["relevance"] == "EXACT"
    parent = {"ingredient_ids": ["ING-77"], "process_ids": ["PROC-19"], "target_svars": ["SVAR-9"]}
    assert verdicts(score("Keeps 65% [EVD-000001].", cell=parent, ing_relatives={"ING-77": ["ING-1"]})) == ["SUPPORTED"]
    assert verdicts(score("Keeps 65% [EVD-000001].", cell=parent)) == ["WRONG_CELL"]
    nocell = score("Keeps 65% [EVD-000003].", cell=None)                               # no question cell: value only
    assert verdicts(nocell) == ["SUPPORTED"] and nocell["claims"][0]["relevance"] == "NOT_CHECKED"
    with pytest.raises(ValueError):
        score("Keeps 65% [EVD-000001].", min_relevance="ANY")


def test_censored_row_and_nonexistent_and_outside_packet_flags():
    assert verdicts(score("Keeps 97.5% [EVD-000007].")) == ["SUPPORTED"]
    res = score("Keeps 65% [EVD-000001, EVD-999999, EVD-000003].", packet_ids=["EVD-000001"])
    assert res["nonexistent_ids"] == ["EVD-999999"] and res["outside_packet_ids"] == ["EVD-000003"]
    assert verdicts(res) == ["SUPPORTED"] and res["claims"][0]["supporting_ids"] == ["EVD-000001"]


# ---------------------------------------------------------------- directional claims and abstention

def test_directional_claims_checked_against_the_cited_row():
    assert verdicts(score("Boiling reduces vitamin C [EVD-000005]."), "DIRECTION") == ["SUPPORTED"]      # 0.40 -> DECREASE
    assert verdicts(score("Boiling reduces vitamin C [EVD-000006]."), "DIRECTION") == ["VALUE_MISMATCH"]  # 1.0 -> NO_CHANGE
    assert verdicts(score("Boiling does not reduce vitamin C [EVD-000006]."), "DIRECTION") == ["SUPPORTED"]
    assert verdicts(score("Vitamin C increases [EVD-000012]."), "DIRECTION") == ["VALUE_MISMATCH"]       # direction DECREASE
    assert verdicts(score("Vitamin C drops [EVD-000012]."), "DIRECTION") == ["SUPPORTED"]                # label-only row
    ev = {"EVD-000013": row(13, 0.9500000000000001, direction="DECREASE")}                          # ledger direction wins
    assert verdicts(H3.score_answer("Boiling reduces vitamin C [EVD-000013].", evd=ev), "DIRECTION") == ["SUPPORTED"]
    assert H3.row_direction(row(14, 0.97)) == "NO_CHANGE" and H3.row_direction(row(14, None, status="UNKNOWN")) is None
    assert score("Horseradish may be more stable [EVD-000005].")["n_direction"] == 0                  # hedge, not "no change"
    unc = score("Boiling can reduce the vitamin C content.")
    assert unc["n_direction"] == 0 and unc["n_direction_uncited_sentences"] == 1 and verdicts(unc, "DIRECTION_UNCITED") == ["UNCITED"]
    assert unc["n_numeric"] == 0                                                        # directional claims never enter UCR


def test_abstention_detection_needs_a_cue_and_no_number():
    assert score("There is no measurement for this exact food and process.")["abstained"] is True
    assert score("No evidence for the exact food, but similar foods keep 65% [EVD-000001].")["abstained"] is False
    assert score("Boiling is a cooking method.")["abstained"] is False


# ---------------------------------------------------------------- intervals, coverage, sign test

def test_clopper_pearson_known_values():
    lo, hi = H3.clopper_pearson(0, 10)
    assert lo == 0.0 and hi == pytest.approx(0.3085, abs=1e-3)
    lo, hi = H3.clopper_pearson(5, 10)
    assert (lo, hi) == (pytest.approx(0.1871, abs=1e-3), pytest.approx(0.8129, abs=1e-3))
    lo, hi = H3.clopper_pearson(10, 10)
    assert hi == 1.0 and lo == pytest.approx(0.6915, abs=1e-3)
    assert H3.clopper_pearson(0, 0) == (0.0, 1.0)
    lo, hi = H3.clopper_pearson(19, 20)
    assert lo < PS.wilson(19, 20)[0] and hi == pytest.approx(0.9987, abs=1e-3)           # CP is wider than Wilson


def test_sign_test_one_and_two_sided():
    assert H3.sign_test_exact(6, 0) == pytest.approx(1 / 64)
    assert H3.sign_test_exact(6, 0, alternative="two-sided") == pytest.approx(2 / 64)
    assert H3.sign_test_exact(5, 5) == pytest.approx(0.623046875)                        # P(X >= 5 | n = 10)
    assert H3.sign_test_exact(0, 0) == 1.0
    assert H3.sign_test_exact(0, 6) == 1.0                                               # wrong direction: P(X >= 0)
    assert H3.sign_test_exact(1, 5) == pytest.approx(63 / 64)
    with pytest.raises(ValueError):
        H3.sign_test_exact(1, 1, alternative="less")


def _res(n_num, n_bad, abstained=False):
    return {"n_numeric": n_num, "n_numeric_unsupported": n_bad, "abstained": abstained}


def test_summarize_rung_reports_coverage_next_to_ucr():
    gold = {"q1": "ANSWER", "q2": "ANSWER", "q3": "ANSWER_SIMILAR_ONLY", "q4": "ABSTAIN", "q5": "ABSTAIN", "q6": "COMPARE"}
    empty_b7 = {q: _res(0, 0, abstained=(g == "ABSTAIN")) for q, g in gold.items()}      # UCR "0" by saying nothing
    s = H3.summarize_rung(empty_b7, gold)
    assert s["ucr"] is None and s["coverage_answerable"]["x"] == 0 and s["coverage_answerable"]["n"] == 4
    assert s["abstention_on_abstain_gold"]["x"] == 2 and s["answers_with_no_claim_and_no_abstention"] == 4
    good = {"q1": _res(2, 0), "q2": _res(1, 1), "q3": _res(0, 0, True), "q4": _res(0, 0, True), "q5": _res(3, 2), "q6": _res(2, 0)}
    s = H3.summarize_rung(good, gold)
    assert (s["n_numeric_claims"], s["n_unsupported"], s["ucr"]) == (8, 3, 0.375)
    assert s["selective_risk"]["x"] == 2 and s["selective_risk"]["n"] == 4              # q2, q5 of q1, q2, q5, q6
    assert s["coverage_answerable"]["x"] == 2                                            # q1 and q6 (q2's only claim is bad)
    assert s["false_abstention_answerable"]["x"] == 1 and s["questions_with_numbers_on_abstain_gold"] == 1
    assert s["coverage_answerable"]["cp95"][0] < 0.5 < s["coverage_answerable"]["cp95"][1]


def test_compare_rungs_sign_test_counts_discordant_questions():
    b2 = {f"q{i}": _res(2, 1 if i < 8 else 0) for i in range(10)}
    b7 = {f"q{i}": _res(2, 0) for i in range(10)}
    r = H3.compare_rungs(b2, b7)
    assert (r["b_worse_only_unsupported"], r["c_better_only_unsupported"]) == (8, 0)
    assert r["p_one_sided_exact"] == pytest.approx(1 / 256) and r["can_be_significant"]
    few = H3.compare_rungs({f"q{i}": _res(2, 1 if i < 3 else 0) for i in range(10)}, b7)
    assert few["b_worse_only_unsupported"] == 3 and few["can_be_significant"] is False
    both_bad = H3.compare_rungs({"q": _res(1, 1)}, {"q": _res(1, 1)})
    assert (both_bad["b_worse_only_unsupported"], both_bad["c_better_only_unsupported"]) == (0, 0)
    assert math.isclose(both_bad["p_one_sided_exact"], 1.0)
