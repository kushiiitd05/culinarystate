# Prompt for the Mac Claude session — merge the manjot orchestration branch (2026-11-08)

Copy everything below the line into the Mac Claude session in `~/Desktop/CGAS/culinarystate`.

---

You are taking back the baton from the server orchestrator that ran on manjot-server on 2026-11-08 (S175). It
worked on branch `max/s176-orchestration`, created from GitHub `kush/s169-seal-p1b` @ `07fc0d2`. Do the following
in order and stop to ask Kush only where a step says so.

## 0. Notice / disclaimer (read first, keep it in every report and slide)
- Everything on `max/s176-orchestration` is **AI_DRAFTED by agents**; none of it is human-verified, signed or
  approved. No D-071 human-only item (signatures, nonces, approvals of preregs/freeze records, human facts) was
  done or simulated. SSOT v16 is a **DRAFT pending Kush's approval; v15 stays authoritative**.
- Numbers in committed outputs are counts/aggregates only; third-party text stays git-ignored; no BBC data exists
  on manjot (D-003); BBC-dependent re-runs below must be done on the Mac.
- Personal calendar details were deliberately removed from the plans; do not add them back to committed files
  (the GitHub repo is public).

## 1. Get the branch
```bash
cd ~/Desktop/CGAS/culinarystate
git status                      # commit or stash your own work first
scp manjot23309@192.168.3.19:~/kush_work/culinarystate_s176_orchestration.bundle ~/Desktop/CGAS/
git bundle verify ~/Desktop/CGAS/culinarystate_s176_orchestration.bundle
git fetch ~/Desktop/CGAS/culinarystate_s176_orchestration.bundle max/s176-orchestration:max/s176-orchestration
git log --oneline 07fc0d2..max/s176-orchestration
```

## 2. Merge into your current line of work
- If your local branch is still `kush/s169-seal-p1b` at `07fc0d2`, fast-forward: `git merge --ff-only max/s176-orchestration`.
- If you committed after `07fc0d2`, merge normally. Expected conflicts only in `WORKLOG.md`, `DECISIONS.md`,
  `registry/compute_runs_v1.csv`, `handoff/FINISH_PLAN_2026-11-07.md`: keep both sides; renumber the server's
  WORKLOG ids (S175+) and decision proposals (D-078+) after yours (ids are never reused).
- Run the full test suite on the Mac (`python -m pytest -q`); fix only merge breakage; report anything else.

## 3. Mac-only follow-ups (BBC stays on the Mac, D-003)
1. If the server's physics fix landed (`physics_drivers` evaporation/phase-change version bump — see
   `reports/orchestration/S176_L-PHYS_report.md`), re-run Layer 2 for the BBC family on the Mac with the new version
   and log the run in `registry/compute_runs_v1.csv`; the old S173/S174 L2 outputs are superseded (keep them on
   record, mark SUPERSEDED).
2. If the router fix landed (`reports/orchestration/S176_L-ROUTER_report.md`), re-run the router census for the BBC
   family and publish the full-corpus total = non-BBC (manjot, S176) + BBC (Mac).
3. Non-heat family layers (`reports/orchestration/S176_L-NH_report.md`): run the BBC family on the Mac.

## 4. Push, PR and merge
```bash
git push origin max/s176-orchestration          # or your merged branch
gh pr create --base main --head max/s176-orchestration \
  --title "Gather the stack: s169-seal-p1b + manjot orchestration (S175)" \
  --body-file handoff/MAC_CLAUDE_MERGE_PROMPT_2026-11-08.md
```
`main` is 165+ commits behind `kush/s169-seal-p1b`; every other GitHub branch is already contained in it, so this
one PR gathers the whole stack. **Ask Kush before merging into `main`.** After merge, log a WORKLOG step.

## 5. Then hand the humans their pack
Open `handoff/HUMAN_OPERATIONS_PACK_2026-11-09.md` with Kush and Parv: the decision sitting (9–10 Nov), the
signature checklist (10–11 Nov), the blind labelling/verification tasks (13, 15, 16 Nov), fallbacks L0–L3 and the
"cannot claim" sheet. Record each human decision in `DECISIONS.md` as the human's own words (scribe).

## 6. Key files on the branch
- Plan: `reports/orchestration/ssot_consensus/CONSENSUS_PLAN_2026-11-08.md`, `registry/component_ledger_v1.csv`
- Reviews: `reports/orchestration/review/S176_REV-A_science.md`, `S176_REV-B_eval_governance.md`
- SSOT v16 draft: `docs/SSOT/computational_gastronomy_master_ssot_v16_0_DRAFT.md` (+ `docs/SSOT/ssot_v16_INDEX_ADDENDUM.md`)
- Deployment: `handoff/DEPLOYMENT_AND_PRESENTATION_PLAN_2026-11-08.md`
- Lane reports: `reports/orchestration/S176_*_report.md`; resume anchor: `handoff/RESUME_ANCHOR_2026-11-08_ORCH.md`
