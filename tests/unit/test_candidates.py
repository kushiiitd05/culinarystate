"""§257B.10 C10 candidate action generator — 12 mandatory unit tests."""
import pytest
from culinarystate.decision.candidates import (
    Candidate, CandidateSet, VERSION,
    process_candidates, substitution_candidates, sequence_candidates,
    generate_candidates,
)

# shared fixtures
PROC_NAMES = {"PROC-001": "boil", "PROC-002": "fry", "PROC-003": "steam",
              "PROC-004": "roast", "PROC-010": "chop"}
HEAT = frozenset({"PROC-001", "PROC-002", "PROC-003", "PROC-004"})
PROCESSED_BY = {
    "ING-100": ["PROC-001", "PROC-002", "PROC-003", "PROC-010"],  # chop is not heat
    "ING-200": ["PROC-004"],
}
KGE_CONF = {
    ("ING-100", "ING_PROCESSED_BY", "PROC-001"): 0.8,
    ("ING-100", "ING_PROCESSED_BY", "PROC-002"): 0.5,
    ("ING-100", "ING_PROCESSED_BY", "PROC-003"): 0.3,
    ("ING-200", "ING_PROCESSED_BY", "PROC-004"): 0.9,
}
EVD_SUPPORT = {("ING-100", "PROC-001"): 42, ("ING-100", "PROC-002"): 15, ("ING-100", "PROC-003"): 3}
ALTERNATIVES = {
    "ING-100": [("ING-300", 0.7), ("ING-301", 0.4)],
}
ING_NAMES = {"ING-100": "broccoli", "ING-200": "chicken", "ING-300": "cauliflower", "ING-301": "kale"}
FOLLOWED_BY = {
    "PROC-001": [("PROC-003", 0.6), ("PROC-002", 0.3)],
}


# 1. clean in-domain case
def test_clean_process_candidates():
    cands = process_candidates("ING-100", PROCESSED_BY, HEAT, PROC_NAMES, KGE_CONF, EVD_SUPPORT)
    assert len(cands) == 3  # only heat procs (chop excluded)
    assert all(isinstance(c, Candidate) for c in cands)
    assert cands[0].name == "boil"  # most evidence (42)
    assert cands[0].evidence_count == 42
    assert cands[0].type == "PROCESS"


# 2. missing optional fields (no confidence in KGE)
def test_missing_confidence():
    cands = process_candidates("ING-200", PROCESSED_BY, HEAT, PROC_NAMES, {}, {})
    assert len(cands) == 1
    assert cands[0].name == "roast"
    assert cands[0].confidence == 0.0
    assert cands[0].evidence_count == 0


# 3. missing critical field (no ingredient_id)
def test_missing_ingredient():
    cands = process_candidates(None, PROCESSED_BY, HEAT, PROC_NAMES, KGE_CONF, EVD_SUPPORT)
    assert cands == []


# 4. ambiguous surface form (ingredient with many alternatives)
def test_substitution_candidates():
    cands = substitution_candidates("ING-100", ALTERNATIVES, ING_NAMES)
    assert len(cands) == 2
    assert cands[0].name == "cauliflower"
    assert cands[0].type == "SUBSTITUTION"
    assert cands[0].source_predicate == "ING_ALTERNATIVE_TO"


# 5. contradictory upstream fields (process both candidate and excluded)
def test_non_heat_excluded():
    """Chop (PROC-010) is in PROCESSED_BY but not in heat → excluded."""
    cands = process_candidates("ING-100", PROCESSED_BY, HEAT, PROC_NAMES, KGE_CONF, EVD_SUPPORT)
    names = {c.name for c in cands}
    assert "chop" not in names


# 6. source/locale variation (different ingredient)
def test_different_ingredient():
    cands = process_candidates("ING-200", PROCESSED_BY, HEAT, PROC_NAMES, KGE_CONF, EVD_SUPPORT)
    assert len(cands) == 1
    assert cands[0].name == "roast"


# 7. near-duplicate input (same ingredient twice → same candidates)
def test_idempotent():
    c1 = process_candidates("ING-100", PROCESSED_BY, HEAT, PROC_NAMES, KGE_CONF, EVD_SUPPORT)
    c2 = process_candidates("ING-100", PROCESSED_BY, HEAT, PROC_NAMES, KGE_CONF, EVD_SUPPORT)
    assert c1 == c2


# 8. OOD concept (ingredient not in processed_by)
def test_ood_ingredient():
    cands = process_candidates("ING-999", PROCESSED_BY, HEAT, PROC_NAMES, KGE_CONF, EVD_SUPPORT)
    assert cands == []


# 9. explicit UNKNOWN (no substitutions known)
def test_no_substitutions():
    cands = substitution_candidates("ING-200", ALTERNATIVES, ING_NAMES)
    assert cands == []  # ING-200 not in alternatives


# 10. malformed identifier
def test_malformed_id():
    cands = process_candidates("BOGUS", PROCESSED_BY, HEAT, PROC_NAMES, KGE_CONF, EVD_SUPPORT)
    assert cands == []


# 11. version present
def test_version():
    cs = generate_candidates("ING-100", "PROC-001", "vitamin C",
                             PROCESSED_BY, HEAT, PROC_NAMES, KGE_CONF, EVD_SUPPORT,
                             ALTERNATIVES, ING_NAMES, FOLLOWED_BY)
    assert cs.version == VERSION
    assert isinstance(cs, CandidateSet)


# 12. round-trip: full generate includes all families
def test_full_generate():
    cs = generate_candidates("ING-100", "PROC-001", "vitamin C",
                             PROCESSED_BY, HEAT, PROC_NAMES, KGE_CONF, EVD_SUPPORT,
                             ALTERNATIVES, ING_NAMES, FOLLOWED_BY)
    types = {c.type for c in cs.candidates}
    assert "PROCESS" in types
    assert "SUBSTITUTION" in types
    assert "SEQUENCE" in types
    assert cs.ingredient_id == "ING-100"
    assert cs.process_id == "PROC-001"
    assert cs.target == "vitamin C"


# -- extra: sequence candidates
def test_sequence_candidates():
    cands = sequence_candidates("PROC-001", FOLLOWED_BY, PROC_NAMES)
    assert len(cands) == 2
    assert cands[0].name == "steam"
    assert cands[0].type == "SEQUENCE"


def test_sequence_no_process():
    cands = sequence_candidates(None, FOLLOWED_BY, PROC_NAMES)
    assert cands == []


# -- extra: max_k
def test_max_k():
    cands = process_candidates("ING-100", PROCESSED_BY, HEAT, PROC_NAMES, KGE_CONF, EVD_SUPPORT, max_k=2)
    assert len(cands) == 2
