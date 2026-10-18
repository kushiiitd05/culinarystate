from culinarystate.decision.constraints import parse_constraints
from culinarystate.decision.feasibility import Action, Constraints, Requirements, check

TOOLS = {"oven": "TOOL-000001", "hob": "TOOL-000002", "frying pan": "TOOL-000003", "microwave": "TOOL-000004",
         "saucepan": "TOOL-000005"}
ALLERGENS = {"gluten": "ALLERGEN-000001", "milk": "ALLERGEN-000003", "egg": "ALLERGEN-000004", "nut": "ALLERGEN-000006"}


def P(t):
    return parse_constraints(t, TOOLS, ALLERGENS)


def test_only_have_is_closed_world_and_no_x_is_unavailable():
    c, info = P("I only have a frying pan and a microwave, no oven")
    assert c.available_tools == frozenset({"TOOL-000003", "TOOL-000004"})
    assert c.unavailable_tools == frozenset({"TOOL-000001"})


def test_plain_have_stays_open_world():
    c, _ = P("I have a saucepan")
    assert c.available_tools is None


def test_time_budget_variants():
    assert P("dinner in 15 minutes")[0].time_budget_min == 15
    assert P("I have half an hour")[0].time_budget_min == 30
    assert P("needs to be done within 1 hour")[0].time_budget_min == 60
    assert P("20-30 mins max")[0].time_budget_min == 20                       # conservative: lower end
    assert P("make it tasty")[0].time_budget_min is None


def test_allergens_and_unresolved_diets():
    c, info = P("gluten-free please, my son is allergic to nuts; we are vegan and lactose intolerant")
    assert c.excluded_allergens == frozenset({"ALLERGEN-000001", "ALLERGEN-000006"})
    assert set(info["unresolved"]) == {"vegan", "lactose"}


def test_no_eggs_and_dairy_free():
    assert P("no eggs, dairy-free")[0].excluded_allergens == frozenset({"ALLERGEN-000004", "ALLERGEN-000003"})


def test_empty_and_raw_preserved():
    c, info = P("")
    assert (c.available_tools, c.time_budget_min, c.excluded_allergens, c.unavailable_tools) == \
        (None, None, frozenset(), frozenset()) and info["raw"] == ""


def test_unavailable_required_tool_rejects_action():
    req = Requirements({"PROC-000001": "bake"}, {"PROC-000001": frozenset({"TOOL-000001"})}, {}, {})
    c, _ = P("no oven at home")
    r = check(Action("PROC-000001"), c, req)
    assert r["decision"] == "REJECT" and r["checks"]["tool"]["reason"] == "REQUIRED_TOOL_UNAVAILABLE"


ING = {"onion": "ING-000010", "red onion": "ING-000011", "garlic": "ING-000012", "egg": "ING-000013",
       "coconut milk": "ING-000014", "milk": "ING-000015"}


def _pi(t):
    return parse_constraints(t, TOOLS, ALLERGENS, ING)


def test_ingredient_exclusions_resolve_longest_name():
    c, info = _pi("No onion, without garlic and I'm out of coconut milk")
    assert c.excluded_ingredients == frozenset({"ING-000010", "ING-000012", "ING-000014"})
    assert "ING-000015" not in c.excluded_ingredients and info["unresolved_exclusions"] == []


def test_plural_and_tools_are_not_ingredients():
    c, info = _pi("no onions and no oven")
    assert c.excluded_ingredients == frozenset({"ING-000010"}) and c.unavailable_tools == frozenset({"TOOL-000001"})


def test_unknown_exclusion_is_unresolved_not_guessed():
    c, info = _pi("no blorpfruit please")
    assert c.excluded_ingredients == frozenset() and info["unresolved_exclusions"] == ["blorpfruit"]


def test_function_words_after_cue_are_ignored():
    c, info = _pi("no more than 20 minutes, no time for chopping")
    assert c.excluded_ingredients == frozenset() and info["unresolved_exclusions"] == []


def test_excluded_ingredient_or_its_parent_rejects_action():
    req = Requirements({"PROC-000001": "bake"}, {}, {}, {}, {"ING-000011": ("ING-000010",)})
    c, _ = _pi("no onion")
    r = check(Action("PROC-000001", ("ING-000011",)), c, req)
    assert r["decision"] == "REJECT" and r["checks"]["ingredient"]["reason"] == "EXCLUDED_INGREDIENT"
    assert check(Action("PROC-000001", ("ING-000012",)), c, req)["checks"]["ingredient"]["status"] == "PASS"
    assert check(Action("PROC-000001", ("ING-000012",)), Constraints(), req)["checks"]["ingredient"]["status"] == "NOT_APPLICABLE"


def test_weak_tool_alias_counts_after_a_constraint_cue():
    c, info = _pi("no microwave, I have no grill, and no onion")
    assert c.unavailable_tools == frozenset({"TOOL-000004"}) and c.excluded_ingredients == frozenset({"ING-000010"})
    assert info["unresolved_exclusions"] == []                     # "grill" is a tool, not an unknown food
    c, _ = _pi("I only have a hob and microwave")
    assert c.available_tools == frozenset({"TOOL-000002", "TOOL-000004"})
