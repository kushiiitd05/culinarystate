from culinarystate.decision.constraints import parse_constraints
from culinarystate.decision.feasibility import Action, Requirements, check

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
