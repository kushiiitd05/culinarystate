# Step 08b: questions for Kush (draft, answer one at a time, most important first)

1. Does a G08-3 FAIL (D-034) count as the "detector precision/recall evidence" that releases 08b v1? Recommended: no; keep 08b v1 NOT authorised until B2 / B3 pass a re-audit or you write a different release rule.
2. Do you sign D-035 to authorise 08b-v0 only (new files, Mac, no 08a code edits)? Recommended: yes, with the not-authorised list as drafted.
3. Which of G08b-1..4 apply to v0? Recommended: G08b-1, 2, 4 fully, and G08b-3 as a fixture unit test only (no recall claim), all four again for v1.
4. Which exact threshold is "the 08a-registered threshold" for G08b-3: the frozen B3 cut 0.75 in `detectors.py` (D-034)? Recommended: yes, 0.75 unchanged.
5. May 08b-v0 wrap the existing 08a detector modules without editing them? Recommended: yes; any needed change comes back to you as a separate request.
6. Do you want to give numbers the card leaves open (fixture size and perturbation classes, test or coverage floor, `rule_version` hash, memory bound)? Recommended: leave UNKNOWN now; set only the fixture classes before coding, reusing the seven THR-08A-17 classes.
