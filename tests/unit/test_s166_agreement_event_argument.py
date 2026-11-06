"""S166: pilot_agreement.disagreements crashed when a matched event differed only in an argument (P1 scoring run).

`add()` takes (category, where, field, kush, parv) but the event_argument branch passed six values. Synthetic.
"""
import copy

from culinarystate.annotation.examples import white_sauce
from culinarystate.annotation.pilot_agreement import _align, disagreements


def test_a_matched_event_with_a_different_argument_is_an_event_argument_row():
    a, b = white_sauce("Kush"), copy.deepcopy(white_sauce("Parv"))
    b["steps"][1]["events"][1]["time"] = "99 minutes"  # same event key, different argument
    rows = disagreements(a, b, _align(a, b))
    arg = [r for r in rows if r["category"] == "event_argument"]
    assert len(arg) == 1 and arg[0]["field"].endswith(":time") and arg[0]["parv"] == str({"time": "99 minutes"})
