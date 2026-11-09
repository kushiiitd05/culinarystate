# Rung A verb-coverage census, non-BBC families (S178, T3-C05-R1)

Status: AI_DRAFTED / PROPOSED. Counts only; no recipe text. NON_CITABLE. A rule-based coverage count of a rule-based tagger: not an accuracy estimate, not a gold score. Tool `s178-corpus-verb-census-0.1.0-draft`; lexicon `STEP17B_RUNG_A_LEXICON_V1_DRAFT` fingerprint `9678937f6a9a0ff6` (147 ACTION PROC ids).
Sample: full families. See the tool header for the definitions of ACTION event, verb slot, candidate and the closed-class list.

## Table by family

| family | texts with steps | ACTION events | ambiguous (several PROC ids) | PROC lemma guess | verb-slot candidates | mapped | **% mapped** | sentence-initial candidates | **% mapped** | distinct unmapped lemmas (>= 20) | top-200 share of unmapped slot tokens |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| FOODCOM | 522,514 | 8,728,967 | 78,946 (0.904 %) | 1,647 (0.019 %) | 8,995,790 | 7,090,090 | **78.816** | 4,290,419 | **87.355** | 2,775 | 76.493 % |
| GUTENBERG_SEGMENT | 73,778 | 952,392 | 1,757 (0.184 %) | 183 (0.019 %) | 1,049,708 | 651,244 | **62.04** | 340,875 | **68.718** | 2,018 | 54.729 % |
| WIKIBOOKS | 3,676 | 62,527 | 259 (0.414 %) | 33 (0.053 %) | 67,231 | 51,278 | **76.271** | 31,249 | **86.918** | 123 | 72.381 % |
| TASTESET | NOT_AVAILABLE | | | | | | | | | | NO_INSTRUCTION_TEXT |
| A1_BBC_GOOD_FOOD | NOT_ON_THIS_SERVER | | | | | | | | | | D_003_BBC_DATA_NOT_PRESENT |

## FOODCOM

522,514 texts, 5,275,357 sentences, 51,149,384 word tokens; 8,728,967 ACTION events (16.71 per text; 7,090,090 in a verb slot, 3,747,894 sentence-initial; 85 multi-word), 145 distinct PROC ids used.
Verb-slot words excluded: 2,965,940 closed-class, 1,718,402 lexicon food/tool words.
Coverage of the unmapped slot tokens by the top-k lemmas (%): {'top_1': 6.22, 'top_10': 29.25, 'top_50': 54.9, 'top_100': 66.19, 'top_200': 76.49, 'top_500': 86.81, 'top_1000': 92.09}.
ACTION events by PROC family: {'COMBINATION': 2027153, 'MECHANICAL_MIX': 1530133, 'TRANSFER': 1346805, 'HEAT_GENERAL': 734413, 'MECHANICAL_CUT': 574999, 'DRY_HEAT': 376306, 'COOLING': 304514, 'WET_HEAT': 296528, 'FAT_HEAT': 295604, 'SEPARATION': 284251, 'SHAPING': 272501, 'SERVING': 257409, 'HEAT_CONTROL': 140290, 'RESERVATION': 72452, 'PRESERVATION': 70935, 'FERMENT_LEAVEN': 51362, 'RESTING': 14366}.
Top-200 list: `verb_unmapped_top200_FOODCOM.csv` (sha256 `57a674c0cee48a79`), 37 of the 200 rows also in the BBC spaCy list.

## GUTENBERG_SEGMENT

73,778 texts, 680,341 sentences, 9,179,176 word tokens; 952,392 ACTION events (12.91 per text; 651,244 in a verb slot, 234,244 sentence-initial; 0 multi-word), 136 distinct PROC ids used.
Verb-slot words excluded: 894,504 closed-class, 155,633 lexicon food/tool words.
Coverage of the unmapped slot tokens by the top-k lemmas (%): {'top_1': 4.93, 'top_10': 17.58, 'top_50': 34.61, 'top_100': 43.92, 'top_200': 54.73, 'top_500': 68.5, 'top_1000': 77.94}.
ACTION events by PROC family: {'COMBINATION': 206259, 'TRANSFER': 170106, 'MECHANICAL_CUT': 113971, 'MECHANICAL_MIX': 97103, 'WET_HEAT': 78150, 'SEPARATION': 53625, 'HEAT_GENERAL': 47443, 'SHAPING': 41163, 'DRY_HEAT': 34528, 'SERVING': 33853, 'FAT_HEAT': 27656, 'PRESERVATION': 15144, 'COOLING': 12077, 'RESERVATION': 8750, 'FERMENT_LEAVEN': 7123, 'RESTING': 2553, 'HEAT_CONTROL': 1131}.
Top-200 list: `verb_unmapped_top200_GUTENBERG_SEGMENT.csv` (sha256 `3a887bf613b81bf8`), 34 of the 200 rows also in the BBC spaCy list.

## WIKIBOOKS

3,676 texts, 37,754 sentences, 410,075 word tokens; 62,527 ACTION events (17.01 per text; 51,278 in a verb slot, 27,161 sentence-initial; 0 multi-word), 139 distinct PROC ids used.
Verb-slot words excluded: 28,148 closed-class, 10,905 lexicon food/tool words.
Coverage of the unmapped slot tokens by the top-k lemmas (%): {'top_1': 8.49, 'top_10': 34.21, 'top_50': 57.65, 'top_100': 69.05}.
ACTION events by PROC family: {'COMBINATION': 14060, 'TRANSFER': 9966, 'MECHANICAL_MIX': 9783, 'HEAT_GENERAL': 5602, 'MECHANICAL_CUT': 4311, 'WET_HEAT': 2858, 'FAT_HEAT': 2646, 'SEPARATION': 2451, 'SHAPING': 2319, 'SERVING': 2207, 'DRY_HEAT': 1851, 'COOLING': 1615, 'HEAT_CONTROL': 737, 'RESERVATION': 619, 'FERMENT_LEAVEN': 572, 'PRESERVATION': 529, 'RESTING': 142}.
Top-200 list: `verb_unmapped_top200_WIKIBOOKS.csv` (sha256 `54ed92e133d2d87c`), 20 of the 123 rows also in the BBC spaCy list.

## Reading and limits

- 100 % of ACTION events map to PROC by construction; the informative numbers are the share of verb-slot candidates that map and the unmapped list.
- No POS tagger on this server: a candidate is a word in a verb slot that is not a closed-class, food or tool word. Unmapped lemmas include adverbs, nouns and fragments; `slot_share_pct` and `sentence_initial_count` in the CSV help to separate verbs (high) from the rest (low).
- Gutenberg is 19th-century prose: many unmapped slot words are archaic verbs and function words; its sentence-initial share is the least reliable.
- The lists are single words with counts (minimum 20). They are vocabulary, not recipe text; the committed BBC list `registry/processes/unmapped_verbs.csv` is the precedent. Law-6 reviewer to confirm.
- TASTEset has no instruction text; BBC is not on this server (D-003).
