"""S175: ING canonical name -> USDA SR Legacy food matcher (lexical, UNVERIFIED until a human checks)."""
from __future__ import annotations

from types import MappingProxyType

from culinarystate.composition import ing_sr_match as M
from culinarystate.composition.sr_legacy import SRFood


def food(fdc: int, desc: str, cat: int = 11) -> SRFood:
    return SRFood(fdc_id=fdc, description=desc, category_id=cat, nutrients=MappingProxyType({}), portions=())


FOODS = {f.fdc_id: f for f in (
    food(1, "Onions, raw"),
    food(2, "Onions, cooked, boiled, drained, without salt"),
    food(3, "Onions, spring or scallions (includes tops and bulb), raw"),
    food(4, "Sugars, granulated", 19),
    food(5, "Sugars, powdered", 19),
    food(6, "Wheat flour, white, all-purpose, enriched, bleached", 20),
    food(7, "Tomatoes, red, ripe, raw, year round average"),
    food(8, "Soup, onion, dry, mix", 6),
    food(9, "Garlic, raw"),
    food(10, "Cherries, sweet, raw", 9),
    food(11, "Peppers, sweet, red, raw"),
)}

SYN = {"caster sugar": "sugars, granulated", "icing sugar": "sugars, powdered", "plain flour": "wheat flour, white, all-purpose",
       "spring onion": "onions, spring or scallions"}


def test_normalise_lowercases_strips_and_singularises() -> None:
    assert M.normalise("Tomatoes") == ("tomato",)
    assert M.normalise("Red-Onions!") == ("red", "onion")
    assert M.normalise("cherries") == ("cherry",)
    assert M.normalise("glass") == ("glass",)
    assert M.normalise("  ") == ()


def test_plain_name_prefers_head_in_first_segment_and_raw() -> None:
    r = M.match("onion", FOODS, SYN)
    assert r.fdc_id == 1 and r.status == "AUTO_MATCH_HIGH" and r.verification == "UNVERIFIED"
    assert M.match("tomatoes", FOODS, SYN).fdc_id == 7


def test_synonym_registry_maps_uk_names() -> None:
    assert M.match("caster sugar", FOODS, SYN).fdc_id == 4
    assert M.match("icing sugar", FOODS, SYN).fdc_id == 5
    assert M.match("plain flour", FOODS, SYN).fdc_id == 6
    r = M.match("spring onions", FOODS, SYN)
    assert r.fdc_id == 3 and r.via_synonym == "spring onion"
    assert M.match("caster sugar", FOODS, SYN).status == "AUTO_MATCH_HIGH"


def test_no_candidate_is_no_match_not_a_guess() -> None:
    r = M.match("saffron", FOODS, SYN)
    assert r.status == "NO_MATCH" and r.fdc_id is None and r.score is None


def test_head_only_outside_first_segment_is_low() -> None:
    # "onion" soup mix: head is not in the first segment
    only_soup = {8: FOODS[8]}
    r = M.match("onion", only_soup, SYN)
    assert r.fdc_id == 8 and r.status == "AUTO_MATCH_LOW"


def test_close_runner_up_is_low() -> None:
    two = {1: FOODS[1], 99: food(99, "Onions, raw, sweet")}
    r = M.match("onion", two, SYN)
    assert r.status in ("AUTO_MATCH_HIGH", "AUTO_MATCH_LOW") and r.fdc_id == 1
    assert r.runner_up_fdc_id == 99


def test_match_is_deterministic_and_ties_break_on_fdc_id() -> None:
    twins = {20: food(20, "Garlic, raw"), 9: FOODS[9]}
    a, b = M.match("garlic", twins, SYN), M.match("garlic", dict(reversed(list(twins.items()))), SYN)
    assert a == b and a.fdc_id == 9 and a.status == "AUTO_MATCH_LOW"


def test_red_pepper_needs_all_tokens() -> None:
    assert M.match("red pepper", FOODS, SYN).fdc_id == 11
    assert M.match("green pepper", FOODS, SYN).status == "NO_MATCH"


def test_exact_first_segment_beats_compound_first_segment() -> None:
    foods = {1: food(1, "Sugar-apples, (sweetsop), raw", 9), 2: food(2, "Sugars, granulated", 19),
             3: food(3, "Water convolvulus,raw"), 4: food(4, "Beverages, water, tap, drinking", 14)}
    assert M.match("sugar", foods, {}).fdc_id == 2
    # "water convolvulus" has head noun convolvulus: no head bonus, so at best a LOW match
    assert M.match("water", foods, {}).status == "AUTO_MATCH_LOW"


def test_synonym_csv_loader(tmp_path) -> None:
    p = tmp_path / "syn.csv"
    p.write_text("term,sr_query,kind,rationale,status\ncaster sugar,sugars granulated,UK_US,UK name,AGENT_PROPOSED\n"
                 "milk,milk whole 3.25 milkfat,DEFAULT_FORM,generic milk -> whole,AGENT_PROPOSED\n", encoding="utf-8")
    syn = M.load_synonyms(p)
    assert syn == {"caster sugar": "sugars granulated", "milk": "milk whole 3.25 milkfat"}


REG_CSV = ("term,sr_description,fdc_id,kind,rationale,status,verification\n"
           "caster sugar,\"Sugars, granulated\",4,UK_US,fine sucrose,AGENT_PROPOSED,UNVERIFIED\n"
           "crème fraîche,,,NO_SR_EQUIVALENT,,AGENT_PROPOSED,UNVERIFIED\n"
           "chif,,,NOT_A_FOOD,NER artefact,AGENT_PROPOSED,UNVERIFIED\n")


def test_registry_hit_wins_over_lexical(tmp_path) -> None:
    p = tmp_path / "reg.csv"
    p.write_text(REG_CSV, encoding="utf-8")
    reg = M.load_registry(p)
    r = M.resolve("Caster Sugar", FOODS, reg)
    assert (r.status, r.fdc_id, r.kind, r.verification) == ("REGISTRY_MAPPED", 4, "UK_US", "UNVERIFIED")
    u = M.resolve("crème fraîche", FOODS, reg)
    assert (u.status, u.fdc_id, u.kind) == ("REGISTRY_UNMAPPABLE", None, "NO_SR_EQUIVALENT")
    assert M.resolve("garlic", FOODS, reg).status in ("AUTO_MATCH_HIGH", "AUTO_MATCH_LOW")


def test_registry_rejects_stale_fdc_and_bad_kind(tmp_path) -> None:
    p = tmp_path / "reg.csv"
    p.write_text(REG_CSV.replace(",4,UK_US", ",999,UK_US"), encoding="utf-8")
    import pytest
    with pytest.raises(ValueError, match="999"):
        M.resolve("caster sugar", FOODS, M.load_registry(p))
    p.write_text(REG_CSV.replace("NOT_A_FOOD", "GUESS"), encoding="utf-8")
    with pytest.raises(ValueError, match="GUESS"):
        M.load_registry(p)
    p.write_text(REG_CSV.replace("NO_SR_EQUIVALENT", "DIRECT"), encoding="utf-8")
    with pytest.raises(ValueError, match="fdc_id"):
        M.load_registry(p)


def test_real_defaults_registry_is_well_formed() -> None:
    from pathlib import Path
    reg = M.load_registry(Path(__file__).resolve().parents[2] / "registry/ing_sr_defaults_v1.csv")
    assert len(reg) >= 290
    assert {e.kind for e in reg.values()} <= M.MAPPED_KINDS | M.UNMAPPABLE_KINDS
