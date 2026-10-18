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


def test_recovery_sample_noise_regressions():
    assert rel("If you have cinnamon stick, break it into four pieces.") == []
    assert rel("If it falls in heavy drops, the jam is sufficiently cooked.") == []
    assert rel("If you don't mind soggy nori, you can wrap the balls in nori beforehand.") == []
    assert rel("If the dough sticks to the board, dust with a little flour.")[0][:2] == ("RECOVERY", "STICK")


def test_fire_and_water_level_are_not_food_failures():
    assert rel("If this burns well, change the dampers to make an indirect draft.") == []
    assert rel("Should the water sink below two-thirds, replenish from the boiling kettle.") == []


def test_separately_and_preferences_are_not_failures():
    assert rel("If boiled separately from the meat, have ready some melted butter to eat with it.") == []
    assert rel("Dressing may be passed separately if preferred.") == []
    assert rel("The rice should be soft and each grain standing out separate when done.") == []
    assert rel("The bones will be more easily separated when they come to table.") == []
    assert rel("The sauce will separate if it is boiled.")[0][:2] == ("CAUSE", "SPLIT")


def test_doneness_signals_are_not_causes():
    assert rel("The cracklins will sink to the bottom when done.") == []
    assert rel("Cook until it feels sticky when tried between fingers; spread on a wet pan.") == []
    assert rel("Cook rather rare, as they will be tough if well done.")[0][:2] == ("CAUSE", "TOUGH")


def test_unless_and_less_liable_are_prevention():
    r = rel("The cake will be less liable to burn if the pans are lined with white buttered paper.")
    assert r[0][:2] == ("PREVENTION", "BURN") and r[0][2].startswith("the pans are lined")
    assert rel("The jam will burn unless it is stirred constantly.")[0][:2] == ("PREVENTION", "BURN")


def test_cause_span_stops_at_clause_and_recovery_allows_short_prefix():
    r = rel("In hot weather, if the paste sticks when being rolled down, put it on a tin sheet and place on ice.")
    assert r[0][:2] == ("RECOVERY", "STICK") and r[0][2].startswith("put it on a tin sheet")
    assert rel("Eggs and milk curdle if boiled, so keep the heat low.")[0][2] == "boiled"


def test_medical_text_is_not_kitchen_failure():
    assert rel("If the burn or scald is serious, send immediately for a physician.") == []
    assert rel("Should one of his patients be seized with a violent cholic, he prescribed boiled cabbage.") == []
