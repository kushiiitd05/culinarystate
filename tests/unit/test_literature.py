from culinarystate.evidence.literature import Candidate, abstract_text, precheck


def cand(title, abstract, oa=True):
    return Candidate("10.1/x", title, 2020, "J", oa, None, 3, abstract, "q", "boil", "vitamin c", "vegetables")


def test_abstract_reconstruction():
    assert abstract_text({"heat": [1], "We": [0], "vegetables": [2]}) == "We heat vegetables"
    assert abstract_text(None) == ""


def test_precheck_classes():
    cls, score, _ = precheck(cand("Effect of boiling on vitamin C retention in vegetables",
                                  "Vitamin C decreased by 40% after boiling at 100 °C for 10 min."))
    assert cls == "VERIFY_NOW" and score >= 0.8
    assert precheck(cand("A review of vitamin C in cooking", "We review."))[0] == "NEEDS_SOURCE"
    assert precheck(cand("Parasite activity of plant extracts", "In vitro assay."))[0] == "REJECT"


def test_float_threshold_regression():
    # 0.3 + 0.3 + 0.1 + 0.1 must count as 0.8 (VERIFY_NOW), not 0.7999…
    cls, score, _ = precheck(cand("Effect of boiling on vitamin C", "Changes in vitamin C were determined."))
    assert score == 0.8 and cls == "VERIFY_NOW"
