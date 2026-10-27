# Edge audit packet (blind)
For each row, judge whether the two records really are linked as the edge_type says. Use exactly one of: CORRECT_EDGE, WRONG_EDGE, UNCERTAIN.
Fill the `edge_judgement` column only; optionally explain in `reason_if_not_correct`. Do not edit any other cell.
Judge only the texts shown. Do not look up the detector, do not look at the other reviewer's file, do not open the sealed key file.
A false merge is worse than a missed duplicate: when unsure choose UNCERTAIN. Detector, score and stratum are hidden on purpose.
