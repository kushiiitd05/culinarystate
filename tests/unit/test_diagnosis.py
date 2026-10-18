from culinarystate.decision.diagnosis import TroubleshootIndex, diagnose, failure_of

ROWS = [
    {"relation": "CAUSE", "failure": "CURDLE", "key": "boiled", "text": "boiled", "support_sources": 6},
    {"relation": "CAUSE", "failure": "CURDLE", "key": "acid added too fast", "text": "acid added too fast", "support_sources": 2},
    {"relation": "CAUSE", "failure": "CURDLE", "key": "not stirred", "text": "not stirred", "support_sources": 3},
    {"relation": "RECOVERY", "failure": "CURDLE", "key": "beat in cold milk", "text": "beat in cold milk", "support_sources": 4},
    {"relation": "RECOVERY", "failure": "CURDLE", "key": "strain", "text": "strain", "support_sources": 1},
    {"relation": "PREVENTION", "failure": "CURDLE", "key": "stir constantly", "text": "stir constantly", "support_sources": 9},
    {"relation": "RECOVERY", "failure": "BURN", "key": "scrape off burnt parts", "text": "scrape off burnt parts", "support_sources": 2},
]
IDX = TroubleshootIndex(ROWS)


def test_failure_from_symptom_text():
    assert failure_of("Why did my custard curdle?") == "CURDLE"
    assert failure_of("my sauce split") == "SPLIT"
    assert failure_of("why is my cake heavy") == "HEAVY"
    assert failure_of("tell me about paneer") is None


def test_proposer_ranks_by_support_and_verifier_uses_history():
    d = diagnose("Why did my custard curdle?", history=["whisk", "boil"], idx=IDX)
    causes = {c["cause"]: c for c in d["causes"]}
    assert d["failure"] == "CURDLE" and list(causes)[0] == "boiled"
    assert causes["boiled"]["verdict"] == "CONSISTENT"                    # boil is in the history
    assert causes["acid added too fast"]["verdict"] == "UNVERIFIABLE"
    assert d["causal_language"] == "QUALIFIED"


def test_cause_naming_absent_process_is_inconsistent():
    d = diagnose("Why did my custard curdle?", history=["whisk", "bake"], idx=IDX)
    assert {c["cause"]: c["verdict"] for c in d["causes"]}["boiled"] == "INCONSISTENT"


def test_recovery_comes_from_separate_index_not_inverted_causes():
    d = diagnose("It curdled, how can I recover?", history=["boil"], idx=IDX, min_support=1)
    assert [r["action"] for r in d["recovery"]] == ["beat in cold milk", "strain"]
    assert [r["action"] for r in diagnose("It curdled", ["boil"], IDX)["recovery"]] == ["beat in cold milk"]  # default ≥2
    assert all("boil" not in r["action"] for r in d["recovery"])
    assert d["prevention"][0]["action"] == "stir constantly"


def test_unknown_failure_or_no_candidates():
    assert diagnose("why is it purple?", history=[], idx=IDX)["failure"] is None
    d = diagnose("why did it crack?", history=[], idx=IDX)
    assert d["failure"] == "CRACK" and d["causes"] == [] and d["recoverability"] == "UNKNOWN"


def test_negated_cause_flips_verification():
    d = diagnose("Why did my custard curdle?", history=["boil"], idx=IDX)
    assert {c["cause"]: c["verdict"] for c in d["causes"]}["not stirred"] == "CONSISTENT"      # stir absent
    d = diagnose("Why did my custard curdle?", history=["boil", "stir"], idx=IDX)
    assert {c["cause"]: c["verdict"] for c in d["causes"]}["not stirred"] == "INCONSISTENT"


def test_no_history_means_unverifiable_not_inconsistent():
    d = diagnose("Why did my custard curdle?", history=[], idx=IDX)
    assert {c["verdict"] for c in d["causes"]} == {"UNVERIFIABLE"}
