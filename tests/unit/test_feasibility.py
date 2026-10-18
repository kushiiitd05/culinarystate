from culinarystate.decision.feasibility import Action, Constraints, Requirements, check

REQ = Requirements(processes={"PROC-000001": "bake", "PROC-000002": "chop"},
                   required_tools={"PROC-000001": frozenset({"TOOL-000001"})},       # bake -> oven
                   typical_minutes={"PROC-000001": (20.0, 30.0, 60.0)},
                   allergen_of={"ING-000007": frozenset({"ALLERGEN-000001"})})


def test_clean_case_allowed():
    r = check(Action("PROC-000001", ("ING-000009",), 25.0), Constraints(frozenset({"TOOL-000001"}), 40.0), REQ)
    assert r["decision"] == "ALLOW" and r["checks"]["tool"]["status"] == "PASS"


def test_missing_tool_time_and_allergen_reject_with_reasons():
    r = check(Action("PROC-000001", ("ING-000007",), None),
              Constraints(frozenset({"TOOL-000099"}), 10.0, frozenset({"ALLERGEN-000001"})), REQ)
    assert r["decision"] == "REJECT"
    assert r["checks"]["tool"]["reason"] == "MISSING_REQUIRED_TOOL"
    assert r["checks"]["time"]["reason"] == "TYPICAL_MEDIAN_EXCEEDS_BUDGET"     # p50 20 min > 10 min budget
    assert r["checks"]["allergen"]["reason"] == "EXCLUDED_ALLERGEN" and "ING-000007" in r["checks"]["allergen"]["detail"]


def test_absent_constraints_not_applicable_and_unknowns_explicit():
    r = check(Action("PROC-000002", ("ING-000009",), None), Constraints(), REQ)
    assert r["decision"] == "ALLOW" and {c["status"] for c in r["checks"].values()} <= {"PASS", "NOT_APPLICABLE"}
    r = check(Action("PROC-000002", (), None), Constraints(time_budget_min=5.0), REQ)
    assert r["decision"] == "UNKNOWN" and r["checks"]["time"]["reason"] == "DURATION_UNKNOWN"


def test_ood_and_malformed():
    assert check(Action("PROC-000777", (), None), Constraints(), REQ)["checks"]["process"]["reason"] == "OOD_PROCESS"
    assert check(Action("bake", (), None), Constraints(), REQ)["decision"] == "REJECT"
    assert check(Action("PROC-000001", (), -5.0), Constraints(), REQ)["checks"]["input"]["reason"] == "NEGATIVE_DURATION"
