# CulinaryState — agent pointer

Read in order: `STATUS.md` → tail of `WORKLOG.md` → `DECISIONS.md` → relevant `docs/SSOT_INDEX.md` ranges.
Never load the whole SSOT; use `sed -n 'A,Bp'` on ranges from the index.

- Log every step: `python tools/log_step.py --block <B/DEL> --title ... --did ... --files ... --verify ...`
- Python: `/opt/anaconda3/bin/python` (base). ML: `/opt/anaconda3/envs/recsys_env/bin/python`. No new venvs.
- Tests: `/opt/anaconda3/bin/python -m pytest -q`
- Laws: no invented scientific values; UNKNOWN is a valid answer; AI review ≠ human verification;
  raw text preserved, normalization is a new column; ledgers append-only; IDs never reused.
- Third-party raw text (BBC recipes, papers) stays in `data/raw/` (git-ignored).
- Humans: Kush, Parv. Commits authored by the human whose session did the work.
