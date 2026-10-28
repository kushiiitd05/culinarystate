# Step 35 protocol corrections proposed by AI review — DRAFT, UNSIGNED

This document is a proposed amendment for expert/human review. It does not alter
the currently hashed protocol, Parv's recorded answers, signed threshold rows,
ledger labels or G35-PRE. Any accepted amendment must be integrated into a new
protocol version and signed before execution. D1's approval of the old draft
must not be misrepresented as approval of these later corrections.

## Confirmed negatives: s4.4 and THR-35P-36

Replace the database-assays-class alternative with:

> A molecule is a negative for class c only when the reviewed source provides
> an explicit negative label for that molecule/class, or a documented assay
> outcome on that molecule which meets the preregistered negative criterion.
> Database-level class coverage alone is insufficient. Absence of a positive
> edge remains unlabelled. Unreviewed/unknown outcomes are excluded. Conflicting
> positive/negative evidence is retained as CONFLICTING and excluded pending
> adjudication, never resolved by file order or source preference.

The expert must define assay outcome/threshold/conditions and review whether
source semantics support such negatives. Do not infer absence of one taste from
membership in another taste class. Keep the existing >=30-negative support gate;
if it cannot be met, report NEED_DATA rather than manufacturing negatives.

Evidence: the existing protocol calls its data positive-unlabelled and forbids
missing-edge negatives, but its database-level alternative does not establish a
negative observation for each molecule. See the primary-source discussion and
limitations in `AI_REVIEW_2026-10-28.md`.

## Deprecated taste edges: s2 / s4.4 / D35-18

Replace the blanket "underlying cause unknown/unexamined" statement in the next
protocol version with the dated evidence status:

> A read-only AI audit links all 204 deprecated ChemTastesDB edges to unique
> active replacements for the same molecule/source locator. Old objects match
> source Taste text, replacements match Class taste, and source PubChem CID
> matches the molecule, 204/204. This explains the edge migration, not the
> validity of the taste measurements. Human chemistry review remains pending.

Do not reactivate deprecated edges or count old and replacement edges together.
The historical unexamined state remains true of the older protocol version.

## Cuisine conflicts and definitions

Integrate D-040: REGION includes the explicitly reviewed subnational terms;
CONFLICTING cuisine recipes are excluded from single-cuisine scoring with flag
and count retained; MIXED never becomes a guessed continent. American's class
scope and cultural interpretation still need expert review. Parv's lookup
choices are single-reviewer; M49 validates geographic grouping, not cultural
equivalence or annotation reliability.

## Triplet NPMI

The implemented direct triplet generalisation can exceed 1. Choose and register
one of: retain it with an explicit formula/name/range caveat, normalise it using
a reviewed multi-variable definition, or demote it to descriptive reporting.
Do not change the existing formula silently or compare it as if it shared the
pairwise [-1,1] scale. This is an expert decision; no new value is adopted here.

## Environment and signature binding

Carry the D-039 RDKit pin and current Mac availability into the next document,
without erasing the historical server census. Attach the reviewed lookup and
accepted amendment bytes (or explicit cryptographic hashes) to the final signed
package. The current guard hashes only the supplied document: a later edit to an
unhashed lookup/addendum would otherwise not invalidate that document's hash.
The guard now implements bound-file hashes and explicit required-file checks;
synthetic tamper, omission and relocation controls pass. Every future runner
must declare its actual companion inputs. An unsigned review packet is not an
evaluation authorisation.
