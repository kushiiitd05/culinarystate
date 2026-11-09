# Food.com bare-count share and the unit-drop mechanism (S178, T3-C07-R4)

Status: AI_DRAFTED / PROPOSED. Counts only; no recipe text. NON_CITABLE.

Recipes read: 522,517. Tool `s178-corpus-foodcom-bare-count-0.1.0-draft`.

## Verdict

No Food.com quantity string contains a letter, so no unit token exists in the quantity field for a parser to lose: the unit drop is source-level. The parser recognises a unit on 0.198 % of lines, the name field holds a unit word on 4.244 % of strings and the NER finds UNIT spans on 4.161 % of lines: all three are well below 5 % and come from words inside food names, not from a stated unit. The NER's UNIT span count and the number of name strings holding a unit word agree within about 2 %, and its QUANTITY span count equals the number of lines that start with a digit to within 0.01 %.

Every Food.com quantity is a bare count or a bare number (no mass, no volume): grams are UNKNOWN by construction, and no parser change (including SP-002) can create them.

## 1. Source field

4,882,431 quantity strings, 298,706 null, 4,583,725 non-null.

| shape | strings |
|---|---:|
| DECIMAL | 3,130 |
| FRACTION | 1,208,573 |
| INTEGER | 3,023,128 |
| MIXED_NUMBER | 252,344 |
| RANGE | 96,550 |

Strings with any alphabetic character: **0**; strings with U+2044: 1,483,559. Share of non-null strings that are bare numbers: 100.0 %.

## 2. Parser (lines as the corpus iterator builds them)

4,129,433 lines (120,129 unique).

| quantity kind read | legacy parser | with SP-002 pre-normalisation |
|---|---:|---:|
| FRACTION | 0 | 1,031,934 |
| MIXED | 0 | 224,992 |
| NONE | 191,419 | 191,419 |
| NUMBER | 3,875,528 | 2,603,399 |
| PACKAGE | 22 | 22 |
| RANGE | 62,464 | 77,667 |

Lines with a bare numeric quantity at the start: 3,937,952 (95.363 %); lines with no quantity text: 191,481.
Lines where a unit is recognised: legacy 5,790 (0.14 %), with pre-normalisation 8,191 (0.198 %). the parser reads the unit from the PART string (the quantity field has none); 'unit recognised' therefore counts food names that begin with a unit word (e.g. a count noun), not stated units.
Bare-count lines (numeric quantity, no unit recognised anywhere): 3,929,823 (95.166 % of lines).

## 3. Name field

175,237 of 4,129,433 part strings (4.244 %) contain a unit-lexicon word. single-letter t and c excluded by the lexicon; count nouns such as clove or can are unit tokens, so this is an upper bound.

## 4. NER counts (S174)

QUANTITY spans 3,937,650; UNIT spans 171,812 = 4.363 % of QUANTITY, 4.161 % of lines; UNIT spans / name strings with a unit word = 0.9805; QUANTITY spans minus lines starting with a digit = -302. model-derived (DeBERTa-CRF), per-span output not on this server; Wikibooks 82.2 % and TASTEset 83.7 % in the same file.
