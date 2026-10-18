"""§257B.15 C15 multi-objective selector — 12 mandatory unit tests."""
from culinarystate.decision.selector import Option, Selection, VERSION, select, _dominates


# 1. clean in-domain case
def test_clean_pareto():
    opts = [Option("boil", retention=0.50, time_minutes=10.0, feasibility="ALLOWED"),
            Option("steam", retention=0.85, time_minutes=20.0, feasibility="ALLOWED")]
    r = select(opts)
    # steam better retention, boil better time → both on front
    assert len(r.front) == 2
    assert len(r.dominated) == 0


# 2. missing optional fields (UNKNOWN retention/time)
def test_missing_optional():
    opts = [Option("boil", retention=0.50, feasibility="ALLOWED"),
            Option("steam", feasibility="ALLOWED")]  # no retention or time
    r = select(opts)
    # can't compare retention → both on front
    assert len(r.front) == 2


# 3. missing critical field (empty options)
def test_empty_options():
    r = select([])
    assert r.front == ()
    assert r.dominated == ()
    assert r.rejected == ()


# 4. ambiguous surface form (two options with same retention)
def test_tied_retention():
    opts = [Option("boil", retention=0.50, time_minutes=10.0, feasibility="ALLOWED"),
            Option("steam", retention=0.50, time_minutes=15.0, feasibility="ALLOWED")]
    r = select(opts)
    # boil dominates steam (same retention, faster time)
    assert len(r.front) == 1
    assert r.front[0].name == "boil"
    assert len(r.dominated) == 1


# 5. contradictory upstream (one option REJECTED)
def test_rejected_excluded():
    opts = [Option("boil", retention=0.50, feasibility="ALLOWED"),
            Option("fry", retention=0.90, feasibility="REJECTED")]
    r = select(opts)
    assert len(r.front) == 1
    assert r.front[0].name == "boil"
    assert len(r.rejected) == 1
    assert r.rejected[0].name == "fry"


# 6. source/locale variation (different feasibility levels)
def test_constrained_vs_allowed():
    opts = [Option("boil", retention=0.50, feasibility="ALLOWED"),
            Option("microwave", retention=0.60, feasibility="CONSTRAINED")]
    r = select(opts)
    # microwave better retention but constrained → neither dominates → both on front
    assert len(r.front) == 2


# 7. near-duplicate input (same option twice)
def test_duplicate_options():
    o = Option("boil", retention=0.50, time_minutes=10.0, feasibility="ALLOWED")
    r = select([o, o])
    # neither dominates the other (identical) → both on front
    assert len(r.front) == 2


# 8. OOD (single option)
def test_single_option():
    r = select([Option("sous_vide", retention=0.95, feasibility="ALLOWED")])
    assert len(r.front) == 1
    assert r.front[0].name == "sous_vide"


# 9. explicit UNKNOWN
def test_all_unknown():
    opts = [Option("x", feasibility="UNKNOWN"), Option("y", feasibility="UNKNOWN")]
    r = select(opts)
    assert len(r.front) == 2  # can't compare anything


# 10. malformed (all REJECTED)
def test_all_rejected():
    opts = [Option("a", feasibility="REJECTED"), Option("b", feasibility="REJECTED")]
    r = select(opts)
    assert r.front == ()
    assert len(r.rejected) == 2


# 11. version
def test_version():
    r = select([Option("x")])
    assert r.version == VERSION


# 12. dominance: strict domination
def test_strict_dominance():
    a = Option("steam", retention=0.85, time_minutes=10.0, feasibility="ALLOWED")
    b = Option("boil", retention=0.50, time_minutes=20.0, feasibility="ALLOWED")
    assert _dominates(a, b)
    assert not _dominates(b, a)
    r = select([a, b])
    assert len(r.front) == 1
    assert r.front[0].name == "steam"
    assert len(r.dominated) == 1


# -- extra: front sorted by retention descending
def test_front_sorted():
    opts = [Option("boil", retention=0.50, time_minutes=5.0, feasibility="ALLOWED"),
            Option("steam", retention=0.85, time_minutes=20.0, feasibility="ALLOWED"),
            Option("braise", retention=0.70, time_minutes=40.0, feasibility="ALLOWED")]
    r = select(opts)
    # steam dominates braise (better retention AND faster) → braise dominated
    assert len(r.front) == 2
    assert r.front[0].name == "steam"  # highest retention first
    assert len(r.dominated) == 1
    assert r.dominated[0].name == "braise"


# -- extra: three objectives mix
def test_three_way():
    opts = [Option("A", retention=0.90, time_minutes=30.0, feasibility="ALLOWED"),
            Option("B", retention=0.80, time_minutes=15.0, feasibility="ALLOWED"),
            Option("C", retention=0.70, time_minutes=10.0, feasibility="CONSTRAINED")]
    r = select(opts)
    # A best retention, B middle, C fastest but constrained
    # A doesn't dominate B (B faster), B doesn't dominate C (C faster+CONSTRAINED unclear)
    assert len(r.front) == 3
