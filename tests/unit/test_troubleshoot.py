from culinarystate.kg.troubleshoot import mine_sentence, sentences


def rel(s):
    return [(r.relation, r.failure, r.text) for r in mine_sentence(s)]


def test_recovery_after_conditional_failure():
    assert rel("If the custard curdles, beat in a little cold milk at once.") == \
        [("RECOVERY", "CURDLE", "beat in a little cold milk at once")]
    assert rel("Should the sauce separate, whisk in a spoonful of hot water.") == \
        [("RECOVERY", "SPLIT", "whisk in a spoonful of hot water")]


def test_cause_from_will_fail_if():
    assert rel("The sauce will curdle if it is allowed to boil.") == [("CAUSE", "CURDLE", "it is allowed to boil")]
    assert rel("Cakes sink if the oven door is opened too soon.") == [("CAUSE", "SINK", "the oven door is opened too soon")]


def test_prevention():
    assert rel("Stir constantly to prevent it from burning.") == [("PREVENTION", "BURN", "Stir constantly")]
    assert rel("Keep the heat low, or the eggs will curdle.") == [("PREVENTION", "CURDLE", "Keep the heat low")]


def test_non_failure_and_noise_ignored():
    assert rel("If liked, add a little nutmeg.") == []
    assert rel("Split the vanilla pod lengthways.") == []         # 'split' as an action, no condition
    assert rel("") == []


def test_sentence_splitter_keeps_abbreviations():
    assert sentences("Boil 5 min. If it curdles, strain it. Serve.") == ["Boil 5 min.", "If it curdles, strain it.", "Serve."]


def test_precision_sample_regressions():
    assert rel("Burn half those rags in the cask, covering the bung-hole so it may have air enough to keep it burning.") == []
    assert rel("Turn the pudding after five minutes, to keep the heavy parts from settling.") == []
    assert rel("When the weather is warm, and it is very difficult to prevent milk from turning sour, scald it.") == []
    assert rel("Put just enough water in the pan to keep them from burning.")[0][:2] == ("PREVENTION", "BURN")
    assert rel("If the cake turns out heavy, the oven was too cool.") != []


def test_grains_noun_is_not_grainy():
    assert rel("If the grains are cooked in a double boiler, they will not need stirring.") == []
    assert rel("If the fudge turns grainy, add a little water and reheat.")[0][:2] == ("RECOVERY", "GRAINY")
