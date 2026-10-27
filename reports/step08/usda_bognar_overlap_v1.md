# USDA R6 vs Bognar 2002: bibliography overlap (08a.4, G08-9)

Verdict (AGENT, pending expert reading; THR-08A-11 vocabulary): **NO_OVERLAP_FOUND_IN_BIBLIOGRAPHY**

## Method
Extract each reference list, normalise (lowercase, accent-fold, strip punctuation) to surname|year|first 3 title words. Exact = equal key. Fuzzy = same surname, year within 1, title-word Jaccard >= 0.5. NOT_DETERMINABLE if a list is empty or any entry lacks surname or year.

## Counts
- USDA R6 references extracted: 8
- Bognar 2002 references extracted: 11
- Exact matches: 0
- Fuzzy matches (separate): 0

Exact matches (surname, year, journal):
- (none)

Fuzzy matches (surname, year, journal):
- (none)

## Compilation-to-compilation citation (separate from the primary-source verdict)
Bognar entries citing the USDA retention table (surname, year): ['usda|1998'].
This is a direct citation of an earlier release of the same table family, not a shared primary
source, so it does not change the mechanical verdict, but the expert should weigh it for independence.

## Cells affected if overlap were real
L1 USDA-vs-Bognar cells: 67; L2 cells: 249
(all cells of the pair; cross_source_v1.json counts only).

## Limitations
- Only the two printed reference lists were compared; neither names the primary papers behind individual retention values.
- Bibliography overlap is a necessary-not-sufficient signal: shared underlying data without shared citations is not detectable here.
- USDA R6 retn06.txt is the data table; its bibliography comes from retn06.pdf via pdftotext (layout text, in memory).
- Fuzzy matching is deliberately conservative (surname, year +-1, title overlap) and may miss differently transliterated or untitled entries.
- Bognar [4] (online database) and [11] (unpublished data) are keyed like any other entry.
