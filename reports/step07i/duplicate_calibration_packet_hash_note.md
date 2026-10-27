# 07I-C 400-pair packet: pre-label state (recorded 2026-10-27 by Claude as scribe, after THR-07IC-01..09 were signed and before any label exists)

- Blank packet sha256 `1cc5ded65cea44afcd6efd44c3b7444bb4c06146cffd4e5809acf380f64698d8` (matches `reports/step07i/duplicate_calibration_packet_manifest.json`), 491,991 bytes, 400 rows, 0 labels filled, in both `duplicate_pairs_v1_Kush.csv` and `duplicate_pairs_v1_Parv.csv` (byte-identical, mtime 2026-10-22 15:56).
- `duplicate_pairs_v1_KEY_SEALED.csv` has not been opened by Claude and must not be opened by either reviewer.
- THR-07IC-01..09 signed by Kush Tokas 2026-10-27 (rows 10-12, the later sealed v2 packet, stay draft).
- Return protocol: each reviewer labels their own file alone, then records the sha256 of the RETURNED file (not the blank packet) in a note before the other file is opened. The 07.A experience applies: save as a real UTF-8 .csv with the same header, use only the six allowed labels (SAME_RECIPE_COPY, SAME_RECIPE_MINOR_VARIANT, SAME_DISH_DIFFERENT_RECIPE, RELATED, DISTINCT, UNCERTAIN); choose UNCERTAIN when unsure.

## Returned files (recorded 2026-10-27, BEFORE any comparison or agreement run)
- Kush: `annotation/duplicate_calibration/duplicate_pairs_v1_kudsh.csv` (file name has a typo; content is Kush's), sha256 `42f2134b297f7aaaeed6eade4b4bf68d1573893a347b4e9c16bf72a4d1711af7`, 519,489 bytes, mtime 2026-10-27 11:51:38 IST.
- Parv: `annotation/duplicate_calibration/duplicate_pairs_v1_Parv_.csv` (trailing underscore in the name), sha256 `1e6c81d99360c481563a40b6bdbf4eaa9415a205ea1a402a579af2295b2b1b48`, 541,517 bytes, mtime 2026-10-27 11:46:43 IST.
- Format check (vocabulary only): each has 400 rows with the six allowed labels only (no cell outside them), 400 of 400 filled. The blank copies `duplicate_pairs_v1_{Kush,Parv}.csv` are unchanged (sha256 `1cc5ded6…`).
- File save-time gap: 295 s (Parv first). No 07I-C minimum-gap rule is registered; disclosed only.
- Not confirmed by anyone yet: that neither reviewer opened the other's file or the sealed key. `duplicate_pairs_v1_KEY_SEALED.csv` mtime is still 2026-10-22 (unchanged), sha256 `f7973d7d…`.
