from fractions import Fraction as F

import pytest

from culinarystate.lotstate import values as V
from culinarystate.lotstate.line_grams import normalise_text, resolve_line
from culinarystate.quantity import rc2_dryrun as D
from culinarystate.quantity.rc2_grounding import GroundingContext
from tests.unit._lotstate_fx import make_sr

SR = make_sr()
SCHEMA = D.load_schema()
CTX = GroundingContext(source_metadata=D.SOURCE_META, locale="US", locale_metadata=D.LOCALE_META)
CTX_NOLOC = GroundingContext(source_metadata=D.SOURCE_META)


def go(text, fdc=1, band="HIGH", ctx=CTX, **kw):
    return resolve_line(text, schema=SCHEMA, context=ctx, sr=SR, fdc_id=fdc, band=band, **kw)


def test_stated_mass_is_q0_exact():
    r = go("100 g butter", fdc=2)
    assert (r.basis, r.q_level, r.reason) == (V.BASIS_STATED_MASS, "Q0", "STATED_MASS")
    assert r.grams == (F(100), F(100))
    r = go("1 lb butter", fdc=2)
    assert r.grams == (F("453.59237"), F("453.59237"))


def test_count_without_size_is_an_interval_over_sr_item_weights():
    r = go("1 onion")
    assert r.basis == V.BASIS_SR_PORTION and r.q_level == "Q2_PROPOSED"
    assert r.grams == (F(70), F(150)) and r.ambiguous
    r3 = go("3 onions")
    assert r3.grams == (F(210), F(450))


def test_stated_size_narrows_to_that_portion():
    r = go("1 large onion, chopped")
    assert r.grams == (F(150), F(150)) and not r.ambiguous


def test_volume_uses_sr_density_range_and_named_prep_state():
    r = go("1/2 cup chopped onion")
    assert r.basis == V.BASIS_SR_PORTION and r.grams == (F(80), F(80))      # cup, chopped = 160 g
    r = go("1 cup onion")                                                   # prep state not named: chopped AND sliced
    assert r.ambiguous and r.grams == (F(115), F(160))          # one US cup x the sliced and chopped SR densities


def test_stick_count_unit_and_fraction_slash():
    assert go("1 stick butter", fdc=2).grams == (F(113), F(113))
    assert normalise_text("1⁄2 cup") == "1/2 cup"
    r = go("1⁄4 cup sugar", fdc=3)                                     # Food.com style fraction slash
    assert r.grams == (F(50), F(252, 5))                                    # cup = 200 g, tbsp = 12.6 g: two densities


def test_nothing_is_invented_for_qualitative_or_missing_quantity():
    for text, reason in [("salt", "NO_QUANTITY"), ("1 pinch salt", "QUALITATIVE"), ("to taste salt", "QUALITATIVE")]:
        r = go(text, fdc=4)
        assert (r.basis, r.grams, r.q_level, r.reason) == (V.BASIS_UNKNOWN, None, "Q6", reason)


def test_no_sr_match_or_portion_stays_unknown():
    assert go("1 onion", fdc=None).reason == "NO_SR_MATCH"
    assert go("1 cup butter", fdc=6).reason == "NO_SR_PORTION" or go("1 cup butter", fdc=6).grams is None
    assert go("2 stalks celery", fdc=1).grams is None


def test_locale_ambiguous_cup_is_unknown_without_locale():
    r = go("1 cup onion", ctx=CTX_NOLOC)
    assert r.basis == V.BASIS_UNKNOWN and r.reason == "LOCALE_AMBIGUOUS"


def test_foodcom_bare_number_is_not_a_count():
    r = go("2 sugar", fdc=3, unit_stripped_source=True)
    assert (r.basis, r.reason) == (V.BASIS_UNKNOWN, "FOODCOM_UNIT_STRIPPED")
    # a unit that is present in the text is still honoured
    r = go("2 tbsp sugar", fdc=3, unit_stripped_source=True)
    assert r.basis == V.BASIS_SR_PORTION
    r = go("100 g sugar", fdc=3, unit_stripped_source=True)
    assert r.basis == V.BASIS_STATED_MASS


def test_foodcom_length_mismatch_pairs_no_quantity():
    r = go("2 sugar", fdc=3, unit_stripped_source=True, qp_mismatch=True)
    assert r.reason == "FOODCOM_QP_LENGTH_MISMATCH" and r.grams is None


def test_band_floor_applies_to_sr_portion_only():
    low = go("1 onion", band="LOW")
    assert low.grams is not None and low.usable_grams("MEDIUM") is None
    stated = go("100 g butter", fdc=2, band="LOW")
    assert stated.usable_grams("HIGH") == (F(100), F(100))
