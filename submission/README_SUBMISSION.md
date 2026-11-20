# CulinaryState · Group 17

Freeze `freeze-2026-11-20` at `0a41d62`. The freeze suite recorded 8,578 tests passed, five skipped, zero failed and 44 deselected. The signature and freshness checks passed on the frozen snapshot.

## Open the results

- Start with `reports/final/CulinaryState_final_report.pdf` and the slide exports when present.
- Review the signed and local screenshot captures and their manifest in `reports/final/screens/`. `STORIES.md` links the answers to the saved JSON.
- See `reports/final/RELEASE_CARD.md` and `reports/final/DELIVERABLE_COMPLIANCE_MATRIX_2026-11-16.md` for scope. D1–D5 remain partial.

## Run the demos

- Public Explorer at [culinarystate-group17.vercel.app](https://culinarystate-group17.vercel.app). To run the signed snapshot locally, go to `web/`, run `npm ci`, then `npm run build` and `npm run start`. The browser verifies the snapshot with the included public key. Open Lab or Compare.
- From a full project checkout and with authorised local inputs set up, run `./tools/live_demo.sh` and open `http://localhost:3000/live`. Follow the source-use rules and use your own configured credential.
- The rehearsal and recording shot list are in `handoff/REHEARSAL_SCRIPT_2026-11-24.md`. The fallback video is pending. Both hosted comparison runs and the live preflight are in the archive. The signed snapshot and saved screenshots remain available.

## Reproduce and verify

Run `shasum -a 256 -c SHA256SUMS` from the extracted package. The source and methods excerpts in this archive support inspection. For the complete frozen test and local backend environment, use the repository freeze tag and authorised local assets. The archive excludes local research corpora, raw per-record artifacts, private packets, ledger data and confidential paths. The packaging check record lists exclusions and gate status.
