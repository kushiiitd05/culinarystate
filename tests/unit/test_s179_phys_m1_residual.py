"""S179 SCI re-review #1 (M1 residual): a food target temperature must never be bound as the medium temperature."""
from __future__ import annotations

from fractions import Fraction

import pytest

from culinarystate.simulation import condition_binding as CB

B = CB.Binder.load()


def _temps(text: str) -> list:
    out = []
    for e in B.bind_text(text)["events"]:
        tp = e["inputs"].get("temperature_profile", {})
        v = tp.get("value")
        if tp.get("basis") == "TEXT_STATED" and v is not None:
            out.append((e["process_id"], [float(Fraction(str(x))) for x in (v if isinstance(v, (tuple, list)) else (v,))]))
    return out


@pytest.mark.parametrize("text,leak_c", [
    ("Fry the chicken until the juices run clear and the meat is 165 F.", 73.9),
    ("Simmer the sauce until it thickens and reaches 160 F.", 71.1),
    ("Roast the beef until done (140 F for rare).", 60.0),
    ("Bake the bread until it sounds hollow, about 200 F inside.", 93.3),
])
def test_m1r_food_target_is_not_bound_as_medium(text, leak_c):
    for _, vals in _temps(text):
        assert all(abs(v - leak_c) > 0.2 for v in vals), (text, vals)


@pytest.mark.parametrize("text,kept_c", [
    ("Fry the chicken in oil at 350 F until golden.", 176.7),                   # medium setting stays bound
    ("Bake at 400 F until golden and crisp.", 204.4),
    ("Boil the syrup until it reaches 240 F.", 115.6),                         # candy stage: the liquid's temperature
])
def test_m1r_controls_keep_the_medium_temperature(text, kept_c):
    vals = [v for _, vs in _temps(text) for v in vs]
    assert any(abs(v - kept_c) < 0.2 for v in vals), (text, vals)
