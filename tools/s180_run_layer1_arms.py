"""Run the pre-registered step-7 Layer-1 arms over the sealed hard-case set.

Arms, all asked for the **same** ``Proposal`` schema and all passed through the **same** gate
(``layer1_proposer.review``):

  * ``D``  deterministic, rules only. Already in the seal manifest; this tool only reports it.
  * ``L``  local Qwen on vinayak via ollama. Stays inside the private network: the request is piped
           to the server over ssh on stdin, so recipe text never touches a shell argument.
  * ``H``  hosted Nemotron-Ultra via NVIDIA NIM. **Metered, external.** Refuses to run without
           ``--i-have-authorisation``, because it sends case text off the machine.

Measures are the six registered in
``reports/s180/step7_sealed_comparison_preregistration.md``. Everything written here is
DIAGNOSTIC_ONLY: there is no gold for Layer-1 proposals on these cases, so arm agreement is not
accuracy and no arm may be called correct on the strength of it.

Usage:
  python tools/s180_run_layer1_arms.py --arm L --out reports/s180/step7_arm_L.json
  python tools/s180_run_layer1_arms.py --arm H --i-have-authorisation --out …
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

SEAL = ROOT / "reports/s180/hardcase_seal_2026-11-15.json"
LABELS = ("DIAGNOSTIC_ONLY", "NO_GOLD_SO_AGREEMENT_IS_NOT_ACCURACY", "WIKIBOOKS_CC_BY_PUBLIC_TEXT_ONLY",
          "SEALED_SET_UNCHANGED")
LOCAL_HOST = "vinayak-server"
LOCAL_MODEL = "qwen2.5:7b-instruct"
HOSTED_MODEL = "nvidia/nemotron-3-ultra-550b-a55b"
NIM_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
NIM_ENV = Path.home() / ".config/culinarystate/nvidia.env"

#: What each trigger is actually asking. A bare token invites a guess; the question does not.
TRIGGER_QUESTIONS = {
    "VNEXT_MIXTURE_COREF": 'the text refers back to a mixture ("the sauce", "the batter") - which '
                           'existing mixture is meant?',
    "VNEXT_ALTERNATIVE_SKIPPED": 'the text offers a choice ("A or B") - which events are the '
                                 'mutually exclusive alternatives?',
    "VNEXT_FAT_STAYS": "a frying fat was added with the food - under what condition profile was "
                       "this step read?",
    "AMBIGUOUS_REFERENCE": "a reference could not be resolved to one food - under what condition "
                           "profile was this step read?",
    "AMBIGUOUS_ANTECEDENT": "a pronoun or implicit argument has more than one antecedent - under "
                            "what condition profile was this step read?",
    "AMBIGUOUS_ACTION": "the action could not be bound to one process - under what condition "
                        "profile was this step read?",
    "AMBIGUOUS_CANDIDATES": "several candidates matched - under what condition profile was this "
                            "step read?",
    "AMBIGUOUS_OR_MISSING": "a required argument is ambiguous or missing - under what condition "
                            "profile was this step read?",
    "UNRESOLVED_LOT": "an ingredient lot was never resolved to a use - under what condition "
                      "profile was this step read?",
}

PROMPT = """You resolve one kind of ambiguity in a recipe's event graph. Rules already parsed it.

WHAT IS BEING ASKED:
{questions}

Return ONLY a JSON array of proposals. Each proposal is an object with exactly these keys:
  "trigger": one of {triggers}
  "field": {fields}
  "value": a short CATEGORICAL label, never a number
  "event_id": an event id from the graph below
  "span_start": integer character offset into the RECIPE TEXT
  "span_end": integer character offset into the RECIPE TEXT, greater than span_start
  "rationale": one short sentence

Hard rules: "field" must be exactly as listed above for the trigger you answer - no other field is \
accepted. Never propose a number. Every proposal must point at a real span of the RECIPE TEXT. \
Return [] if nothing is warranted.

EVENT IDS: {event_ids}

RECIPE TEXT:
{raw}"""


def build_prompt(case: dict, event_ids: str) -> str:
    """Offer only the fields the fired triggers license, and state what each trigger asks."""
    from culinarystate.composition.layer1_proposer import TRIGGER_FIELDS
    triggers = list(case["triggers"])
    questions = "\n".join(f'  - {t}: {TRIGGER_QUESTIONS.get(t, "resolve this ambiguity")}'
                           for t in triggers)
    licensed = sorted({f for t in triggers for f in TRIGGER_FIELDS.get(t, ())})
    fields = " or ".join(f'"{f}"' for f in licensed) + " (and nothing else)"
    return PROMPT.format(questions=questions, triggers=", ".join(triggers), fields=fields,
                         event_ids=event_ids, raw=case["raw"])


_JSON_ARRAY = re.compile(r"\[.*\]", re.DOTALL)


def load_cases() -> list[dict]:
    manifest = json.loads(SEAL.read_text(encoding="utf-8"))
    packet = ROOT / manifest["packet_path"]
    import hashlib
    digest = hashlib.sha256(packet.read_bytes()).hexdigest()
    if digest != manifest["packet_sha256"]:
        raise SystemExit(f"SEAL BROKEN: packet sha256 {digest} != manifest {manifest['packet_sha256']}")
    with packet.open(encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def parse_graph(raw: str, case_id: str):
    from culinarystate.extraction.interfaces import SourceText
    from culinarystate.extraction.rung_a import RungA
    from culinarystate.quantity.rc2_dryrun import load_schema
    rung = RungA(coord_food_guard=True, lineage_vnext=True)
    return rung.run(SourceText.from_raw(case_id, raw), rung.config(), schema=load_schema()).graph


#: A VPN blip should not void a 60-case run, so a transient ssh failure is retried.
SSH_RETRIES = 4
SSH_BACKOFF_S = 20


def ask_local(prompt: str, timeout: int) -> str:
    """Pipe the request to ollama on the server over ssh stdin; text is never a shell argument."""
    payload = json.dumps({"model": LOCAL_MODEL, "stream": False,
                          "messages": [{"role": "user", "content": prompt}],
                          "options": {"temperature": 0}})
    cmd = ["ssh", "-o", "ConnectTimeout=15", "-o", "ServerAliveInterval=10", LOCAL_HOST,
           'curl -s --max-time %d -X POST http://127.0.0.1:11434/api/chat '
           '-H "Content-Type: application/json" -d @-' % timeout]
    last = ""
    for attempt in range(SSH_RETRIES):
        done = subprocess.run(cmd, input=payload, capture_output=True, text=True,
                              timeout=timeout + 30)
        if done.returncode == 0:
            return json.loads(done.stdout)["message"]["content"]
        last = done.stderr.strip()[:200] or "ssh failed"
        if attempt < SSH_RETRIES - 1:
            print(f"  ssh attempt {attempt + 1} failed ({last[:60]}); retrying in {SSH_BACKOFF_S}s",
                  flush=True)
            time.sleep(SSH_BACKOFF_S)
    raise RuntimeError(last)


def ask_hosted(prompt: str, timeout: int) -> str:
    """NVIDIA NIM. Key is read from outside the repo and never logged."""
    import os
    key = None
    for line in NIM_ENV.read_text(encoding="utf-8").splitlines():
        if "=" in line and "KEY" in line.split("=")[0].upper():
            key = line.split("=", 1)[1].strip().strip('"\'')
    if not key:
        raise SystemExit(f"no API key found in {NIM_ENV}")
    payload = json.dumps({"model": HOSTED_MODEL, "temperature": 0,
                          "messages": [{"role": "user", "content": prompt}]})
    cmd = ["curl", "-s", "--max-time", str(timeout), NIM_URL,
           "-H", "Content-Type: application/json", "-H", f"Authorization: Bearer {key}", "-d", "@-"]
    env = dict(os.environ)
    done = subprocess.run(cmd, input=payload, capture_output=True, text=True,
                          timeout=timeout + 30, env=env)
    if done.returncode != 0:
        raise RuntimeError(done.stderr.strip()[:200] or "curl failed")
    return json.loads(done.stdout)["choices"][0]["message"]["content"]


def to_proposals(text: str):
    """Model text -> Proposal objects. Anything unparseable is returned as a raw dict for the gate."""
    from culinarystate.composition.layer1_proposer import Proposal, ProposalError
    m = _JSON_ARRAY.search(text or "")
    if not m:
        return [{"unparseable": (text or "")[:200]}], 0
    try:
        rows = json.loads(m.group(0))
    except json.JSONDecodeError:
        return [{"unparseable": m.group(0)[:200]}], 0
    if not isinstance(rows, list):
        return [{"unparseable": str(rows)[:200]}], 0
    out, parsed = [], 0
    for r in rows:
        if not isinstance(r, dict):
            out.append({"unparseable": str(r)[:120]})
            continue
        try:
            out.append(Proposal(
                trigger=str(r.get("trigger", "")), field=str(r.get("field", "")),
                value=str(r.get("value", "")), event_id=str(r.get("event_id", "")),
                span_start=r.get("span_start"), span_end=r.get("span_end"),
                rationale=str(r.get("rationale", ""))[:200]))
            parsed += 1
        except (ProposalError, TypeError):
            out.append(dict(r))
    return out, parsed


def run_arm(arm: str, cases: list[dict], timeout: int, limit: int) -> dict:
    from culinarystate.composition import layer1_proposer as L1
    ask = {"L": ask_local, "H": ask_hosted}[arm]
    rows, reasons, latencies = [], Counter(), []
    returned = accepted = parsed_total = span_ok = failures = 0

    for case in cases[: limit or None]:
        graph = parse_graph(case["raw"], f"WB-{case['pageid']}")
        prompt = build_prompt(case, ", ".join(e.event_id for e in graph.events[:40]))
        t0 = time.time()
        try:
            text = ask(prompt, timeout)
        except Exception as exc:
            failures += 1
            rows.append({"pageid": case["pageid"], "error": str(exc)[:160]})
            continue
        latencies.append(round(time.time() - t0, 2))

        proposals, parsed = to_proposals(text)
        returned += len(proposals)
        parsed_total += parsed
        decisions = L1.review(proposals, graph, triggers=tuple(case["triggers"]), raw=case["raw"])
        accepted += len(decisions.accepted)
        span_ok += sum(1 for p in decisions.accepted if 0 <= p.span_start < p.span_end <= len(case["raw"]))
        for _, why in decisions.rejected:
            reasons[why] += 1
        rows.append({
            "pageid": case["pageid"], "triggers": case["triggers"],
            "n_returned": len(proposals), "n_parsed": parsed,
            "n_accepted": len(decisions.accepted),
            "accepted": [{"event_id": p.event_id, "field": p.field, "value": p.value,
                          "span": [p.span_start, p.span_end]} for p in decisions.accepted],
            "rejected_reasons": [why for _, why in decisions.rejected],
            "latency_s": latencies[-1],
        })

    n = len([r for r in rows if "error" not in r])
    return {
        "labels": list(LABELS),
        "arm": arm,
        "model": {"L": LOCAL_MODEL, "H": HOSTED_MODEL}[arm],
        "cases_attempted": len(cases[: limit or None]),
        "cases_answered": n,
        "failures": failures,
        "proposals_returned": returned,
        "proposals_parsed_into_schema": parsed_total,
        "schema_compliance": round(parsed_total / returned, 4) if returned else None,
        "proposals_accepted": accepted,
        "gate_acceptance_rate": round(accepted / returned, 4) if returned else None,
        "accepted_span_valid": span_ok,
        "rejection_reasons": dict(reasons),
        "latency_s": {"mean": round(sum(latencies) / len(latencies), 2) if latencies else None,
                      "max": max(latencies) if latencies else None},
        "per_case": rows,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", choices=("L", "H"), required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--timeout", type=int, default=120)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--i-have-authorisation", action="store_true",
                    help="required for arm H: it sends case text to an external, metered API")
    args = ap.parse_args(argv)

    if args.arm == "H" and not args.i_have_authorisation:
        raise SystemExit("arm H sends case text to an external metered API; rerun with "
                         "--i-have-authorisation once Kush has approved it")

    cases = load_cases()
    print(f"seal verified | {len(cases)} cases | arm {args.arm}")
    result = run_arm(args.arm, cases, args.timeout, args.limit)
    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=1, sort_keys=True), encoding="utf-8")
    print(f"answered {result['cases_answered']}/{result['cases_attempted']} | returned "
          f"{result['proposals_returned']} | accepted {result['proposals_accepted']} | "
          f"schema {result['schema_compliance']} | gate {result['gate_acceptance_rate']}")
    print(f"rejections: {result['rejection_reasons']}")
    print(f"-> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
