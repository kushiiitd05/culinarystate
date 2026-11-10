# Entries Kush commits himself (freeze approvals and SIGN entries; D-071, A4)

Ready-made text from the ops pack (#8, #9, A4), OK'd by Kush in D-084. **Kush appends and commits them from his own
session.** The agent does not. One command, run by Kush (the `!` prefix runs it in the Claude Code session as Kush):

```
! cd ~/Desktop/CGAS/culinarystate && /opt/anaconda3/bin/python - <<'PY'
import re
src = open('handoff/S179_KUSH_OWN_COMMIT_BLOCK.md', encoding='utf-8').read()
block = src.split('<!-- BEGIN ENTRIES -->')[1].split('<!-- END ENTRIES -->')[0].strip('\n')
nums = [int(n) for n in re.findall(r'^### D-(\d{3})', open('DECISIONS.md', encoding='utf-8').read(), re.M)]
n = max(nums) + 1
for tag in ('NN1', 'NN2', 'NN3'):
    block = block.replace(f'D-{tag}', f'D-{n:03d}'); n += 1
open('DECISIONS.md', 'a', encoding='utf-8').write('\n' + block + '\n')
print('appended; now commit')
PY
! cd ~/Desktop/CGAS/culinarystate && git -c user.name="Kush Tokas" commit -m "docs(decisions): crosswalk freeze, FORM schema freeze, D-071 addendum (Kush, own session)" -- DECISIONS.md
```

<!-- BEGIN ENTRIES -->
### D-NN1 · 2026-11-10 · Freeze the mode-to-§141 crosswalk (decided and committed by Kush)
- Mode-to-§141 crosswalk frozen as written: DIRECT/INTERPOLATE -> evidence_supported (tagged E3_UNVERIFIED + COND_UNAUDITED_07A, with an EVD id); SIMULATE/SCENARIO/QUALITATIVE -> physically_possible; UNKNOWN/ASK/ABSTAIN -> unsupported. Caveat in force until the TARGET_ABSENT and CONTEXT_MISMATCH gates land (A2, D-084): DIRECT means "a table row exists for this pair", not "the value applies to this food in this context". Source: consensus 6.2 #8, REV-A V5/N5; ksh/prv verdict OK (S179 verdict sheet item 2).
- **Approver:** Kush.

### D-NN2 · 2026-11-10 · Formula id prefix FORM-; FORM, PARAM and VAL schemas frozen (decided and committed by Kush)
- Formula ids use the prefix FORM- (not MODEL-); the FORM, PARAM and VAL schemas (`registry/schemas/{FORM,PARAM,VAL}.draft_v1.schema.json`) are frozen before PARAM minting on 16 Nov. Reason: keeps formula records out of the ML model-card namespace. Source: consensus 6.2 #9; ksh/prv verdict OK (item 3).
- **Approver:** Kush.

### D-NN3 · 2026-11-10 · D-071 addendum: the AI-persona line (decided and committed by Kush)
- D-071 addendum (adds a limit; does not remove delegation): AI personas (ksh, prv) may tighten, defer, withdraw or refuse. They may not loosen, close or sign. Human-only: signatures, freeze approvals, seals, nonces, amendments to signed records and to rulings, independent-labelling gates (07.A labels, 07I-C, G08-H, G21.6, G23 case labels, Step 10/11 row verification, Step 19 annotation, D5 review) and facts only a person knows. Agreement between ksh and prv is not inter-rater evidence. A file written by an AI and not signed by a human is called a "dated AI draft". Source: REV-B B2.1/B2.3/G-03; ksh/prv verdict OK (item 9).
- **Approver:** Kush.
<!-- END ENTRIES -->
