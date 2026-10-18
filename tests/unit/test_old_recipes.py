from culinarystate.ingest.old_recipes import fields, is_heading, segment

TEXT = """CHAPTER IV.

SOUPS.

1001. ONION SOUP.

INGREDIENTS.--6 large onions, 2 oz. of butter, salt and pepper to taste, 2 quarts of
stock. Mode.--Slice the onions and fry them in the butter; add the stock and simmer
for 1 hour. Time.--1-1/2 hour. Sufficient for 8 persons.

Boiled Potatoes.

Wash the potatoes, put them into boiling water with salt, and boil for 20 minutes.
"""


def test_headings():
    assert is_heading("1001. ONION SOUP.") and is_heading("Boiled Potatoes.")
    assert not is_heading("CHAPTER IV.") and not is_heading("Wash the potatoes, put them into boiling water.")


def test_segment_and_fields():
    recs = segment(TEXT)
    assert [r["title"] for r in recs] == ["ONION SOUP", "Boiled Potatoes"]
    assert recs[0]["ingredients"].startswith("6 large onions") and recs[0]["method"].startswith("Slice")
    assert recs[0]["time"] == "1-1/2 hour" and recs[0]["servings"].startswith("for 8")
    assert "boil for 20 minutes" in recs[1]["body"] and fields("no fields here") == {}
