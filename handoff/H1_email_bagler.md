# H1 draft — email to Prof. Ganesh Bagler (Kush sends; Claude does not send)

**To:** bagler@iiitd.ac.in (listed as the RecipeDB Team contact in the RecipeDB 3.0 API documentation)
**From:** kush23296@iiitd.ac.in · **Cc:** Parv Goyal
**Subject:** CGAS Group 17 — request for RecipeDB 3.0 API access and permission to use the RecipeDB3 NER annotations

Dear Prof. Bagler,

We are Kush Tokas and Parv Goyal (Group 17, Computational Gastronomy). Our course project, CulinaryState, tracks
how ingredients change state through a recipe and answers cooking questions only from cited evidence
(retention-factor tables, recipe corpora), abstaining when evidence is insufficient.

We would like to build on CoSyLab's resources and compare against your lab's work properly, and would be grateful
for help with four things:

1. **RecipeDB 3.0 API.** The Postman documentation lists the endpoints but the base URL is a local address.
   Could we get the API host and a key (or the access procedure), and the terms of use for a course project?
2. **RecipeDB3 NER annotations** (github.com/cosylabiiit/RecipeDB3_NER_Research_Paper). The repository has no
   licence file. May we use the ingredient and instruction annotations to reproduce the published DeBERTa and spaCy
   results and to evaluate our own taggers on the same data? We would keep the data local, cite the work, and not
   redistribute it.
3. **FlavorDB bulk data**, if a download is available for academic use.
4. **Other public CoSyLab datasets without a licence file.** We came across RecipeDB2 (ingredient categories),
   spice-disease-associations, SweetpredDB and SustainableFoodDB. May we use them for the course project (local
   use, cited, not redistributed), for example to link ingredient categories and taste or health associations to
   our evidence ledgers? We have not used them in our repository pending your reply.

What we have so far, in case it is useful: a DeBERTa-v3-large + CRF ingredient tagger at 0.933 exact entity F1 on
TASTEset (5 seeds, dev-selected), evidence ledgers built from USDA, Bognár and Phenol-Explorer, and recipe corpora
from Project Gutenberg and Wikibooks. On your data we plan a matched reproduction first (same split, seeds and
scorer), then a re-evaluation with a separate dev set for checkpoint selection and a split grouped by
augmentation family. We would gladly share the scripts and results with your lab.

Thank you for your time.

Best regards,
Kush Tokas (2023296) and Parv Goyal
IIIT-Delhi

---
Notes for Kush (not part of the email):
- Check the roll number and add Parv's email before sending.
- Approval of this draft = plan item "approve H1 email" (Final Master Plan line 3011).
- Do NOT mention the NER methodology findings in this email (H6 gate; share only after permission and review).
- Until a reply: RecipeDB stays UNRESOLVED_EXTERNAL (AH2); the RecipeDB3 annotations are not downloaded (no licence); RecipeDB2 / spice-disease / SweetpredDB / SustainableFoodDB stay local-only, not in ledgers (S088).
