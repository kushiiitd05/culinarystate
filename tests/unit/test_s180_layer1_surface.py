"""S180: the Layer-1 proposable surface narrows to one field (P1 + P2).

``condition_profile_id`` is a reference field: the 36-step plan defines it as a pointer to a 07H COND
record, nothing in ``src/`` reads it, and no COND records are minted on the recipe side. A model
cannot mint a reference, and a non-blank string check cannot tell a reference from a noun lifted out
of the sentence - which is exactly what step 7 recorded ("pan", "chicken", "bowl_content").

So the field stops being proposable, and the refusal says why. ``VNEXT_FAT_STAYS`` stops licensing
anything because the rule has already committed the merge before the flag is raised.

Net licensed surface: ``alternative_group`` on ``VNEXT_ALTERNATIVE_SKIPPED``. Reviews:
``reports/s180/layer1_surface_review_2026-11-15/{ksh,prv}_review.md``.
"""
from __future__ import annotations

from culinarystate.composition import layer1_proposer as LP


def test_only_alternative_group_is_proposable():
    assert LP.PROPOSABLE_FIELDS == ("alternative_group",)


def test_condition_profile_id_is_declared_a_reference_field():
    assert "condition_profile_id" in LP.REFERENCE_FIELDS
    assert "condition_profile_id" not in LP.PROPOSABLE_FIELDS


def test_reference_field_is_refused_with_its_own_reason():
    """Not FIELD_NOT_PROPOSABLE: that would imply some trigger could license it, and none can."""
    assert "FIELD_REQUIRES_EXISTING_REFERENT" in LP.REJECTION_CODES


def test_only_the_alternatives_trigger_licenses_anything():
    licensing = {t: f for t, f in LP.TRIGGER_FIELDS.items() if f}
    assert licensing == {"VNEXT_ALTERNATIVE_SKIPPED": ("alternative_group",)}


def test_fat_stays_licenses_nothing_but_stays_a_known_trigger():
    """The rule already merged fat into the lot, so there is no open question - but the flag is real."""
    assert LP.TRIGGER_FIELDS["VNEXT_FAT_STAYS"] == ()
    assert "VNEXT_FAT_STAYS" in LP.TRIGGERS


def test_every_detected_trigger_still_has_a_licensing_entry():
    """A closed trigger and an unknown trigger must stay distinguishable."""
    assert set(LP.TRIGGER_FIELDS) == set(LP.TRIGGERS)


def test_coreference_triggers_license_nothing():
    for trigger in ("AMBIGUOUS_REFERENCE", "VNEXT_MIXTURE_COREF", "UNRESOLVED_LOT"):
        assert LP.TRIGGER_FIELDS[trigger] == ()


def test_no_condition_kind_vocabulary_was_introduced():
    """Both reviews refused a flat {OVEN_BAKE, OIL_FRY, ...} vocabulary: it would be a second,
    unsourced opinion on cells the rules already fill with a basis, and it would collapse the
    per-axis UNKNOWN that makes the representation worth having."""
    names = [n for n in dir(LP) if "VOCAB" in n.upper() or "CONDITION_KIND" in n.upper()]
    assert names == []
