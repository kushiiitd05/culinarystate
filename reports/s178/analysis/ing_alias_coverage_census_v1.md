# ING / ALIAS coverage census (S178, T3-C03-R2)

Status: AI_DRAFTED / PROPOSED. Counts only, no recipe text. NON_CITABLE. Deterministic lexicon lookup, not a model and not a gold score.
Tool `s178-ing-alias-coverage-0.1.0-draft`; rule MENTION_RULE_V1; lexicon fingerprint `9678937f6a9a0ff6`.

A mention is an ingredient phrase (rule above). EXACT = the whole phrase is an ING canonical name or an ALIAS surface. PARTIAL = only a sub-span is, so the lexicon finds *a* food in the phrase but the phrase itself is not a concept. MISS = nothing matches.

## Headline

| family | mentions | distinct phrases | EXACT (ING+ALIAS) | PARTIAL | MISS | any lexicon hit | lines with no lexicon food match |
|---|---:|---:|---:|---:|---:|---:|---:|
| FOODCOM | 4,129,433 | 7,198 | 82.19 % | 16.69 % | 1.11 % | 98.89 % | 45,825 (1.11 %) |
| WIKIBOOKS | 31,966 | 8,255 | 63.71 % | 33.7 % | 2.59 % | 97.41 % | 538 (1.68 %) |
| TASTESET | 3,779 | 1,665 | 58.48 % | 37.66 % | 3.86 % | 96.14 % | 129 (3.41 %) |
| GUTENBERG_SEGMENT | NOT_AVAILABLE | | | | | | 0 ingredient lines (corpus iterator sets them empty, S177 F6); NER FOOD spans not persisted |
| TASTESET_GOLD_FOOD_SPANS | 4,020 | 1,096 | 81.52 % | 13.21 % | 5.27 % | 94.73 % | n/a (span level) |

## FOODCOM

4,129,433 mentions, 7,198 distinct phrases, 1,539 seen once (21.38 % of phrases).

Decile by mention mass (decile 1 = the most frequent phrases that together hold the first 10 % of mentions):

| decile | phrases | mentions | EXACT % | any hit % |
|---:|---:|---:|---:|---:|
| 1 | 3 | 451,713 | 100.0 | 100.0 |
| 2 | 5 | 392,243 | 100.0 | 100.0 |
| 3 | 9 | 405,229 | 100.0 | 100.0 |
| 4 | 15 | 405,407 | 100.0 | 100.0 |
| 5 | 25 | 419,168 | 100.0 | 100.0 |
| 6 | 41 | 405,732 | 86.22 | 100.0 |
| 7 | 76 | 414,144 | 79.23 | 98.6 |
| 8 | 150 | 410,721 | 70.6 | 98.0 |
| 9 | 375 | 412,333 | 57.38 | 97.1 |
| 10 | 6,499 | 412,743 | 28.09 | 95.17 |

Decile by phrase rank (decile 1 = the most frequent 10 % of distinct phrases):

| decile | phrases | count range | mentions | EXACT % | any hit % |
|---:|---:|---|---:|---:|---:|
| 1 | 719 | 622..199781 | 3,729,423 | 88.02 | 99.3 |
| 2 | 720 | 181..622 | 246,821 | 34.64 | 95.98 |
| 3 | 720 | 74..181 | 85,446 | 22.69 | 94.99 |
| 4 | 720 | 34..74 | 36,767 | 12.87 | 92.36 |
| 5 | 720 | 16..34 | 17,010 | 7.48 | 91.0 |
| 6 | 719 | 7..16 | 7,604 | 5.38 | 91.28 |
| 7 | 720 | 3..7 | 3,433 | 2.68 | 90.3 |
| 8 | 720 | 1..3 | 1,489 | 3.36 | 86.84 |
| 9 | 720 | 1..1 | 720 | 2.22 | 85.97 |
| 10 | 720 | 1..1 | 720 | 0.97 | 86.11 |

Coverage curve (top-k most frequent phrases):

| k | % of all mentions | % of non-EXACT mentions inside top-k |
|---:|---:|---:|
| 10 | 23.37 | 0.0 |
| 50 | 47.73 | 0.0 |
| 100 | 60.4 | 7.6 |
| 300 | 78.92 | 33.94 |
| 500 | 86.05 | 48.53 |
| 1,000 | 93.53 | 72.31 |
| 2,000 | 98.05 | 90.22 |
| 5,000 | 99.93 | 99.6 |

Phrases needed to hold X % of mentions: {'50': 57, '80': 324, '90': 699, '95': 1198, '99': 2614}. Non-EXACT phrases needed to hold X % of the non-EXACT mentions: {'50': 146, '80': 633, '90': 1144, '95': 1723, '99': 3120} (of 6,086 non-EXACT phrases).

## WIKIBOOKS

31,966 mentions, 8,255 distinct phrases, 6,173 seen once (74.78 % of phrases).

Decile by mention mass (decile 1 = the most frequent phrases that together hold the first 10 % of mentions):

| decile | phrases | mentions | EXACT % | any hit % |
|---:|---:|---:|---:|---:|
| 1 | 4 | 3,556 | 100.0 | 100.0 |
| 2 | 8 | 3,082 | 88.71 | 100.0 |
| 3 | 16 | 3,026 | 95.44 | 100.0 |
| 4 | 36 | 3,141 | 91.53 | 100.0 |
| 5 | 79 | 3,200 | 83.44 | 100.0 |
| 6 | 169 | 3,177 | 77.43 | 100.0 |
| 7 | 429 | 3,199 | 55.42 | 97.16 |
| 8 | 1,231 | 3,192 | 30.45 | 94.77 |
| 9 | 3,087 | 3,197 | 7.26 | 91.18 |
| 10 | 3,196 | 3,196 | 6.48 | 90.99 |

Decile by phrase rank (decile 1 = the most frequent 10 % of distinct phrases):

| decile | phrases | count range | mentions | EXACT % | any hit % |
|---:|---:|---|---:|---:|---:|
| 1 | 825 | 4..1748 | 22,728 | 83.98 | 99.58 |
| 2 | 826 | 2..4 | 2,203 | 30.78 | 94.78 |
| 3 | 825 | 1..2 | 1,256 | 21.18 | 91.48 |
| 4 | 826 | 1..1 | 826 | 8.11 | 92.37 |
| 5 | 825 | 1..1 | 825 | 2.67 | 91.39 |
| 6 | 826 | 1..1 | 826 | 4.36 | 90.56 |
| 7 | 825 | 1..1 | 825 | 5.21 | 88.12 |
| 8 | 826 | 1..1 | 826 | 6.66 | 89.59 |
| 9 | 825 | 1..1 | 825 | 5.94 | 93.82 |
| 10 | 826 | 1..1 | 826 | 7.87 | 92.25 |

Coverage curve (top-k most frequent phrases):

| k | % of all mentions | % of non-EXACT mentions inside top-k |
|---:|---:|---:|
| 10 | 18.82 | 3.0 |
| 50 | 37.04 | 5.91 |
| 100 | 45.57 | 8.16 |
| 300 | 59.52 | 16.9 |
| 500 | 65.71 | 23.46 |
| 1,000 | 73.1 | 34.4 |
| 2,000 | 80.18 | 49.03 |
| 5,000 | 89.82 | 73.74 |

Phrases needed to hold X % of mentions: {'50': 143, '80': 1972, '90': 5059, '95': 6657, '99': 7936}. Non-EXACT phrases needed to hold X % of the non-EXACT mentions: {'50': 1219, '80': 4698, '90': 5858, '95': 6438, '99': 6902} (of 7,017 non-EXACT phrases).

## TASTESET

3,779 mentions, 1,665 distinct phrases, 1,191 seen once (71.53 % of phrases).

Decile by mention mass (decile 1 = the most frequent phrases that together hold the first 10 % of mentions):

| decile | phrases | mentions | EXACT % | any hit % |
|---:|---:|---:|---:|---:|
| 1 | 6 | 429 | 100.0 | 100.0 |
| 2 | 13 | 342 | 100.0 | 100.0 |
| 3 | 27 | 370 | 85.14 | 100.0 |
| 4 | 46 | 371 | 81.4 | 100.0 |
| 5 | 82 | 381 | 66.93 | 96.85 |
| 6 | 140 | 375 | 55.2 | 92.53 |
| 7 | 218 | 378 | 42.86 | 94.71 |
| 8 | 378 | 378 | 11.9 | 93.65 |
| 9 | 378 | 378 | 17.99 | 91.53 |
| 10 | 377 | 377 | 22.55 | 92.04 |

Decile by phrase rank (decile 1 = the most frequent 10 % of distinct phrases):

| decile | phrases | count range | mentions | EXACT % | any hit % |
|---:|---:|---|---:|---:|---:|
| 1 | 166 | 4..108 | 1,861 | 87.21 | 99.36 |
| 2 | 167 | 2..4 | 445 | 53.26 | 93.71 |
| 3 | 166 | 1..2 | 307 | 45.93 | 93.81 |
| 4 | 167 | 1..1 | 167 | 20.36 | 92.22 |
| 5 | 166 | 1..1 | 166 | 10.84 | 95.18 |
| 6 | 167 | 1..1 | 167 | 11.98 | 92.22 |
| 7 | 166 | 1..1 | 166 | 22.89 | 91.57 |
| 8 | 167 | 1..1 | 167 | 14.37 | 91.02 |
| 9 | 166 | 1..1 | 166 | 27.71 | 93.37 |
| 10 | 167 | 1..1 | 167 | 17.37 | 92.22 |

Coverage curve (top-k most frequent phrases):

| k | % of all mentions | % of non-EXACT mentions inside top-k |
|---:|---:|---:|
| 10 | 15.11 | 0.0 |
| 50 | 31.25 | 4.14 |
| 100 | 41.28 | 9.05 |
| 300 | 59.27 | 26.0 |
| 500 | 69.17 | 39.07 |
| 1,000 | 82.4 | 66.35 |

Phrases needed to hold X % of mentions: {'50': 174, '80': 910, '90': 1288, '95': 1477, '99': 1628}. Non-EXACT phrases needed to hold X % of the non-EXACT mentions: {'50': 381, '80': 852, '90': 1009, '95': 1087, '99': 1150} (of 1,165 non-EXACT phrases).

## TASTESET_GOLD_FOOD_SPANS

4,020 mentions, 1,096 distinct phrases, 683 seen once (62.32 % of phrases).

Decile by mention mass (decile 1 = the most frequent phrases that together hold the first 10 % of mentions):

| decile | phrases | mentions | EXACT % | any hit % |
|---:|---:|---:|---:|---:|
| 1 | 3 | 427 | 100.0 | 100.0 |
| 2 | 4 | 387 | 100.0 | 100.0 |
| 3 | 9 | 408 | 100.0 | 100.0 |
| 4 | 15 | 389 | 100.0 | 100.0 |
| 5 | 29 | 408 | 100.0 | 100.0 |
| 6 | 48 | 399 | 91.48 | 98.25 |
| 7 | 83 | 397 | 78.34 | 90.68 |
| 8 | 162 | 402 | 69.15 | 89.05 |
| 9 | 341 | 401 | 42.14 | 86.03 |
| 10 | 402 | 402 | 33.58 | 83.08 |

Decile by phrase rank (decile 1 = the most frequent 10 % of distinct phrases):

| decile | phrases | count range | mentions | EXACT % | any hit % |
|---:|---:|---|---:|---:|---:|
| 1 | 109 | 6..150 | 2,424 | 98.6 | 99.71 |
| 2 | 110 | 3..6 | 484 | 76.24 | 90.5 |
| 3 | 109 | 2..3 | 259 | 71.81 | 91.89 |
| 4 | 110 | 1..2 | 195 | 55.38 | 86.67 |
| 5 | 110 | 1..1 | 110 | 33.64 | 87.27 |
| 6 | 109 | 1..1 | 109 | 34.86 | 81.65 |
| 7 | 110 | 1..1 | 110 | 34.55 | 80.91 |
| 8 | 109 | 1..1 | 109 | 33.03 | 79.82 |
| 9 | 110 | 1..1 | 110 | 33.64 | 86.36 |
| 10 | 110 | 1..1 | 110 | 34.55 | 81.82 |

Coverage curve (top-k most frequent phrases):

| k | % of all mentions | % of non-EXACT mentions inside top-k |
|---:|---:|---:|
| 10 | 24.78 | 0.0 |
| 50 | 47.44 | 0.0 |
| 100 | 58.76 | 3.63 |
| 300 | 77.39 | 26.92 |
| 500 | 85.17 | 47.24 |
| 1,000 | 97.61 | 91.39 |

Phrases needed to hold X % of mentions: {'50': 60, '80': 353, '90': 694, '95': 895, '99': 1056}. Non-EXACT phrases needed to hold X % of the non-EXACT mentions: {'50': 179, '80': 402, '90': 476, '95': 513, '99': 543} (of 550 non-EXACT phrases).

## Notes

- EXACT is the strict reading of 'hits ING/ALIAS'; PARTIAL + EXACT is the Rung A reading (a food is found in the phrase, which is what the S175/S177 line census calls a food mention).
- Phrase-level EXACT is conservative: modifiers (fresh, large, chopped, brand words) keep a phrase from matching even when its head noun is a known concept; the PARTIAL class holds those.
- FOODCOM mentions come from the name field only. No quantity is used, so the 79.5 % quantity/part misalignment does not affect this census.
- WIKIBOOKS / TASTESET mentions pass through the legacy quantity grammar, which mis-reads U+2044 (SP-002); the affected lines lose their quantity but their food phrase is unaffected, because the quantity is cut before the lexicon lookup.
- ING / ALIAS are UNVERIFIED registries (AI-drafted); a hit means 'the registry has this surface', not 'the identity is verified'.
- The top-500 non-EXACT lists are written under data/derived/s178_analysis/ (git-ignored). The committed files hold counts only.
