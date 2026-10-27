# G35-PRE guard: how to sign and what it refuses

Code: `src/culinarystate/representation/prereg_guard.py`. Tests: `tests/unit/test_representation_prereg_guard.py`.
Status: the control is built; **nothing is signed**. The agent never signs; only Kush and Parv do.

## What is hashed
The sha256 of the exact bytes of the pre-registration document (after approval: `reports/step35/preregistration_v1.md`, which should include the signed 01.6 rows; the draft itself is `preregistration_35_0_v1_draft.md`). Any edit, even one character or a trailing newline, changes the hash. The guard does not hash the registry CSV: if the 01.6 rows must be covered, keep them inside the hashed document (Appendix A) or sign a second record the same way.

## How to sign (human steps)
1. Finalise and freeze the document (no more edits after step 3).
2. Produce the unsigned template (writes nothing signed; signers and date are empty):
```
/opt/anaconda3/bin/python - <<'EOF'
import json
from culinarystate.representation.prereg_guard import sign_record_template
rec = sign_record_template("reports/step35/preregistration_v1.md")
open("reports/step35/preregistration_v1.sha256.json", "w").write(json.dumps(rec, indent=2) + "\n")
EOF
```
(run from the repo root with `PYTHONPATH=src` if the package is not installed).
3. Independently check the hash: `shasum -a 256 reports/step35/preregistration_v1.md` must equal the `sha256` field.
4. Each human edits the JSON by hand: add their name to `signers` (for example `["Kush", "Parv"]`), set `date` to `YYYY-MM-DD`, and delete or change `status` (any value other than `UNSIGNED_TEMPLATE`, for example `SIGNED`).
5. Commit the JSON by the human whose session did it. Never touch the document afterwards; a change requires a new document version and a new signature.

## What the guard refuses (raises `PreregNotSigned`)
- hash file missing, unreadable, or not a JSON object;
- document missing;
- no valid 64-char `sha256` recorded;
- recorded sha256 differs from the document's current sha256 (edited after signing);
- `status` is `UNSIGNED_TEMPLATE`, or `signers` is empty, not a list, or has a blank or `<placeholder>` name;
- `date` is not a valid ISO date.

Note: the guard checks that names and a date are present, not that the people are who they claim; it enforces process, not identity. Two signers are the intended practice but the code requires at least one.

## Using it in evaluation code
```python
from culinarystate.representation.prereg_guard import evaluation_entry

@evaluation_entry
def run_rung(...): ...

run_rung(..., prereg_path=PREREG, hash_file=HASH)   # raises before any metric if not signed
```
The decorator consumes `prereg_path` and `hash_file` keyword arguments and runs the guard first. `require_signed_prereg(prereg_path, hash_file)` returns the verified sha256 for logging into result files.

## Two signers (review change)
The guard requires two distinct signer names (Kush and Parv). If one author cannot sign, the hash record must carry `"single_signer_override": {"reason": "<why>", "by": "<who accepted it>"}`; an empty reason or name is refused. The guard still cannot check who the signers really are, only that the record names them.
