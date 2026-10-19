from types import SimpleNamespace as NS

from culinarystate.decision.pipeline import pareto_view


def _pk(vals):
    rows = [NS(row={"derived": {"retention_factor": {"status": "MEASURED", "value": v}}}) for v in vals]
    return NS(direct=rows, near=[])


def test_single_option_no_view():
    assert pareto_view({"boil": _pk([0.5])}, {}, {}) is None


def test_higher_retention_dominates_and_reject_excluded():
    pk = {"boil": _pk([0.4, 0.5, 0.6]), "steam": _pk([0.8]), "fry": _pk([0.9])}
    feas = {"boil": {"decision": "ALLOW"}, "steam": {"decision": "ALLOW"}, "fry": {"decision": "REJECT"}}
    sel = pareto_view(pk, feas, {"boil": "PROC-1", "steam": "PROC-2", "fry": "PROC-3"})
    assert [o.name for o in sel.front] == ["steam"]
    assert [o.name for o in sel.dominated] == ["boil"]
    assert [o.name for o in sel.rejected] == ["fry"]
    assert sel.front[0].retention == 0.8 and sel.front[0].process_id == "PROC-2"


def test_unmeasured_is_neutral():
    sel = pareto_view({"a": _pk([]), "b": _pk([0.7])}, {}, {})
    assert {o.name for o in sel.front} == {"a", "b"}
