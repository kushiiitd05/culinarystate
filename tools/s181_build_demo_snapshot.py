#!/usr/bin/env python3
"""S181: signed, precomputed demo snapshot for CulinaryState Explorer (deployment architecture section 4).

Everything in the snapshot is what the frozen engine returns; nothing is hand-edited. The whole
snapshot is built in memory, passed through the licence gate, and only then written. Labels:
DIAGNOSTIC_ONLY, AI_DRAFTED_SCENARIOS, SELF_WRITTEN_RECIPE_TEXT_ONLY, NO_HUMAN_SIGNOFF_D085.

  build:   s181_build_demo_snapshot.py --generated-at 2026-11-17T00:00:00Z
  verify:  s181_build_demo_snapshot.py --verify
  check:   s181_build_demo_snapshot.py --check     (rebuild in memory, non-zero exit if stale)
  baseline s181_build_demo_snapshot.py --run-baseline   (fill demo/baseline_cache_v1.json over ssh)
"""
from __future__ import annotations

import argparse
import base64
import dataclasses
import enum
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import unicodedata
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Mapping

ROOT = Path(__file__).resolve().parents[1]
BUILDER_VERSION = "s181-snapshot-1.0.0"
SCENARIOS = ROOT / "demo/scenarios_v1.json"
BASELINE_CACHE = ROOT / "demo/baseline_cache_v1.json"
OUT_DIR = ROOT / "web/public/snapshot"
PRIVATE_KEY = Path.home() / ".culinarystate_private/explorer_snapshot_ed25519.pem"
LABELS = ["DIAGNOSTIC_ONLY", "AI_DRAFTED_SCENARIOS", "SELF_WRITTEN_RECIPE_TEXT_ONLY", "NO_HUMAN_SIGNOFF_D085"]
BBC_MARKERS = ("BBCGF-A1", "SRC-000002")       # public_mode.BBC_CORPUS_ID / BBC_SOURCE_ID (asserted at build)
BLOCKS = ("G", "C", "Q", "Y")
DELTA_KINDS = ("ADDED", "CHANGED", "REMOVED", "BECAME_UNKNOWN", "RESOLVED")
RUNG_CONFIG = {"coord_food_guard": True, "lineage_vnext": True, "basis": "D-134"}
BASELINE_ARM = "B0_LLM_ONLY"
BASELINE_LABELS = ["NOT_SYSTEM_OUTPUT", "UNVERIFIED", "NO_EVIDENCE_IDS"]
BASELINE_TIMEOUT_S = 120
_EVD = re.compile(r"EVD-\d+")
_SHA_KEYS = ("recipe_sha256", "raw_sha256")


class LicenceGateError(RuntimeError):
    """The snapshot would carry third-party-derived content. Nothing is written."""


# ---------------------------------------------------------------- pure helpers
def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def canonical_json(obj: Any) -> bytes:
    """Sorted keys, no whitespace, UTF-8, NaN refused."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def jsonable(obj: Any) -> Any:
    """Engine objects (frozen dataclasses, enums, tuples, sets) to plain JSON values. No renaming."""
    if obj is None or isinstance(obj, (str, bool, int, float)):
        return obj
    if isinstance(obj, enum.Enum):
        return jsonable(obj.value)
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return {f.name: jsonable(getattr(obj, f.name)) for f in dataclasses.fields(obj)}
    if isinstance(obj, Mapping):
        return {str(k): jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (set, frozenset)):
        return sorted((jsonable(v) for v in obj), key=lambda v: json.dumps(v, sort_keys=True))
    if isinstance(obj, (list, tuple)):
        return [jsonable(v) for v in obj]
    if isinstance(obj, Fraction):
        return str(obj)
    raise TypeError(f"{type(obj).__name__} is not serialisable into the snapshot")


def lookup_key(question: str, recipe_sha256: str | None) -> str:
    """sha256(nfkc(lower(collapse_ws(q))) + "|" + (recipe_sha256 or "")) so typed questions still hit."""
    q = unicodedata.normalize("NFKC", " ".join(question.split()).lower())
    return sha256_text(q + "|" + (recipe_sha256 or ""))


def _is_unknown(cell: Any) -> bool:
    return isinstance(cell, Mapping) and cell.get("v") is None and "u" in cell


def classify_delta(before: Any, after: Any) -> str | None:
    """Kind of change between two State v2 cells; None when nothing changed."""
    if before == after:
        return None
    if before is None:
        return "ADDED"
    if after is None:
        return "REMOVED"
    if not _is_unknown(before) and _is_unknown(after):
        return "BECAME_UNKNOWN"
    if _is_unknown(before) and not _is_unknown(after):
        return "RESOLVED"
    return "CHANGED"


def state_deltas(prev: Mapping[str, Any], cur: Mapping[str, Any]) -> list[dict[str, Any]]:
    out = []
    for block in BLOCKS:
        a, b = prev.get(block) or {}, cur.get(block) or {}
        for field in sorted(set(a) | set(b)):
            kind = classify_delta(a.get(field), b.get(field))
            if kind:
                out.append({"block": block, "field": field, "kind": kind, "before": a.get(field), "after": b.get(field)})
    return out


def transitions(states: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Deltas between consecutive states of the same food_id, in order of the later state."""
    last: dict[str, int] = {}
    out = []
    for i, s in enumerate(states):
        j = last.get(s["food_id"])
        if j is not None:
            out.append({"food_id": s["food_id"], "from_state_index": j, "to_state_index": i,
                        "from_step": states[j]["step"], "to_step": s["step"], "deltas": state_deltas(states[j], s)})
        last[s["food_id"]] = i
    return out


# ---------------------------------------------------------------- licence gate
def check_mode(info: Mapping[str, Any]) -> None:
    if not (info.get("public") is True and info.get("bbc_derived_edges") == "EXCLUDED"
            and info.get("carbon_figures") == "EXCLUDED"):
        raise LicenceGateError(f"MODE_NOT_PUBLIC_EXCLUDED: {dict(info)}")


def _walk(node: Any) -> Iterable[tuple[str, Any]]:
    if isinstance(node, Mapping):
        for k, v in node.items():
            yield k, v
            yield from _walk(v)
    elif isinstance(node, list):
        for v in node:
            yield from _walk(v)


def licence_gate(files: Mapping[str, bytes], self_written_sha256: set[str]) -> None:
    """Fail on any BBC marker, and on any recipe text or recipe sha that is not self-written."""
    for path, data in sorted(files.items()):
        for marker in BBC_MARKERS:
            if marker.encode() in data:
                raise LicenceGateError(f"BBC_MARKER {marker} in {path}")
        if not path.endswith(".json"):
            continue
        for key, value in _walk(json.loads(data)):
            if key in _SHA_KEYS and value is not None and value not in self_written_sha256:
                raise LicenceGateError(f"NOT_SELF_WRITTEN {key}={value} in {path}")
            if key == "recipe_text" and value is not None and sha256_text(str(value)) not in self_written_sha256:
                raise LicenceGateError(f"NOT_SELF_WRITTEN recipe_text in {path}")


def evidence_ids(files: Mapping[str, bytes]) -> list[str]:
    return sorted({m for data in files.values() for m in _EVD.findall(data.decode("utf-8", "replace"))})


def evidence_sources(ids: Iterable[str], evd: Mapping[str, Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
    """Source ids of every cited EVD row, from the ledger. Fails on a BBC-derived or missing row."""
    out = {}
    for eid in ids:
        row = evd.get(eid)
        if row is None:
            raise LicenceGateError(f"EVIDENCE_ID_NOT_IN_LEDGER {eid}")
        srcs = sorted({s for s in [row.get("source_id"), *((row.get("provenance") or {}).get("source_ids") or ())] if s})
        family = row.get("source_family_id")
        if any(s in BBC_MARKERS for s in srcs) or family in BBC_MARKERS:
            raise LicenceGateError(f"BBC_DERIVED_EVIDENCE {eid}")
        out[eid] = {"source_ids": srcs, "source_family_id": family}
    return out


# ---------------------------------------------------------------- signing
def load_or_create_private_key(path: Path):
    from cryptography.hazmat.primitives import serialization as ser
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    path = Path(path).expanduser().resolve()
    if path == ROOT or ROOT in path.parents:
        raise ValueError("the private key must never live inside the repository")
    if path.exists():
        return ser.load_pem_private_key(path.read_bytes(), password=None)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    key = Ed25519PrivateKey.generate()
    pem = key.private_bytes(ser.Encoding.PEM, ser.PrivateFormat.PKCS8, ser.NoEncryption())
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "wb") as fh:
        fh.write(pem)
    os.chmod(path, 0o600)
    return key


def public_key_pem(key) -> bytes:
    from cryptography.hazmat.primitives import serialization as ser
    return key.public_key().public_bytes(ser.Encoding.PEM, ser.PublicFormat.SubjectPublicKeyInfo)


def sign(manifest: bytes, key) -> bytes:
    return base64.b64encode(key.sign(manifest))


def verify_signature(manifest: bytes, signature_b64: bytes, public_pem: bytes) -> bool:
    from cryptography.hazmat.primitives import serialization as ser
    try:
        ser.load_pem_public_key(public_pem).verify(base64.b64decode(signature_b64, validate=True), manifest)
        return True
    except Exception:  # noqa: BLE001 - any failure (bad base64, bad key, bad signature) is "not verified"
        return False


# ---------------------------------------------------------------- assembly
def assemble(payloads: Mapping[str, Any], *, git_head: str, generated_at: str, rung_config: Mapping[str, Any],
             evidence_sources_map: Mapping[str, Any], inputs: Mapping[str, Any],
             extra: Mapping[str, Any] | None = None) -> dict[str, bytes]:
    """{relative path: bytes} for every data file plus manifest.json, in sorted path order."""
    files = {p: canonical_json(payloads[p]) for p in sorted(payloads)}
    manifest = {**(extra or {}), "snapshot": "CULINARYSTATE_EXPLORER_DEMO_SNAPSHOT", "builder_version": BUILDER_VERSION,
                "git_head": git_head, "generated_at": generated_at, "rung_config": dict(rung_config),
                "labels": list(LABELS), "evidence_sources": dict(evidence_sources_map), "inputs": dict(inputs),
                "files": {p: {"sha256": sha256_bytes(b), "bytes": len(b)} for p, b in files.items()}}
    files["manifest.json"] = canonical_json(manifest)
    return dict(sorted(files.items()))


def diff_snapshot(expected: Mapping[str, bytes], on_disk: Mapping[str, bytes]) -> list[str]:
    out = [f"CHANGED {p}" for p in expected if p in on_disk and on_disk[p] != expected[p]]
    out += [f"MISSING_ON_DISK {p}" for p in expected if p not in on_disk]
    out += [f"EXTRA_ON_DISK {p}" for p in on_disk if p not in expected]
    return sorted(out)


# ---------------------------------------------------------------- baseline (plain LLM, arm B0)
def baseline_prompt(recipe_text: str, question: str) -> str:
    """No system contract: the self-written recipe text plus the question."""
    return f"Recipe: {recipe_text}\n\nQuestion: {question} Answer in two sentences."


def baseline_key(model: str, prompt: str) -> str:
    return sha256_text(model + "|" + prompt)


def _tool(name: str):
    sys.path.insert(0, str(ROOT / "tools"))
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def run_baseline(scenarios: list[dict], cache_path: Path) -> dict[str, int]:
    """Ask the local model each scenario question; store replies verbatim in the cache. Failures are
    recorded as NOT_RUN with the real error and retried on the next run. Nothing is fabricated."""
    arms = _tool("s180_run_layer1_arms")
    cache = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {"entries": {}}
    entries, counts = dict(cache.get("entries") or {}), {"asked": 0, "ok": 0, "not_run": 0, "cached": 0}
    for sc in scenarios:
        for q in sc["questions"]:
            prompt = baseline_prompt(sc["recipe_text"], q["text"])
            key = baseline_key(arms.LOCAL_MODEL, prompt)
            if (entries.get(key) or {}).get("status") == "OK":
                counts["cached"] += 1
                continue
            counts["asked"] += 1
            try:
                text = arms.ask_local(prompt, BASELINE_TIMEOUT_S)
                entries[key] = {"status": "OK", "model": arms.LOCAL_MODEL, "temperature": 0, "prompt": prompt,
                                "text": text, "scenario_id": sc["id"], "question_id": q["id"]}
                counts["ok"] += 1
            except Exception as exc:  # noqa: BLE001 - the real error is recorded, never replaced by text
                entries[key] = {"status": "NOT_RUN", "model": arms.LOCAL_MODEL, "prompt": prompt,
                                "reason": f"{type(exc).__name__}: {exc}"[:300], "scenario_id": sc["id"],
                                "question_id": q["id"]}
                counts["not_run"] += 1
            body = {"record": "B0_LLM_ONLY_BASELINE_CACHE", "labels": ["DIAGNOSTIC_ONLY", *BASELINE_LABELS],
                    "note": "One model, one prompt, temperature 0, no gold. Replies verbatim.", "entries": entries}
            cache_path.write_text(json.dumps(body, indent=1, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    return counts


def baseline_block(entry: Mapping[str, Any] | None, packet: Mapping[str, Any], CV, model: str) -> dict[str, Any]:
    if not entry or entry.get("status") != "OK":
        reason = (entry or {}).get("reason") or "NO_CACHE_ENTRY_RUN_--run-baseline"
        return {"baseline": {"arm": BASELINE_ARM, "status": "NOT_RUN", "reason": reason}}
    text = entry["text"]
    evidence = CV._evidence_numbers(packet)
    return {"baseline": {"arm": BASELINE_ARM, "model": entry.get("model", model), "temperature": 0,
                         "labels": list(BASELINE_LABELS), "prompt": entry["prompt"], "text": text},
            "baseline_check": report_dict(CV.verify(text, packet)),
            "baseline_claimed_numbers": [{"number": n, "decimals": d, "matches_packet_evidence_value": CV._canon(n) in evidence}
                                         for n, d in CV.claimed_numbers(text)]}


def report_dict(report) -> dict[str, Any]:
    return {"ok": report.ok, "codes": sorted(report.codes),
            "violations": [{"code": v.code, "detail": v.detail} for v in report.violations]}


# ---------------------------------------------------------------- engine
def _set_rung(builder, vnext: bool) -> None:
    from culinarystate.extraction.rung_a import RungA
    builder.rung = RungA(coord_food_guard=True, lineage_vnext=vnext)
    builder.binder.rung = builder.rung


def scenario_payload(sc: Mapping[str, Any], builder, baseline_entries: Mapping[str, Any], model: str) -> dict[str, Any]:
    from culinarystate.composition import claim_packet as CP, claim_verifier as CV, evidence_compiler as EC
    from culinarystate.extraction.interfaces import SourceText
    text = sc["recipe_text"]
    _set_rung(builder, False)
    default_states = jsonable(builder.build(text))
    _set_rung(builder, True)
    states = jsonable(builder.build(text))
    graph = builder.rung.run(SourceText.from_raw("S2", text), builder.rung.config(), schema=builder.schema).graph
    claims = []
    for i, s in enumerate(states):
        for target in ("vitc", "lycopene"):
            for kind in sorted(EC.QUESTION_AXES):
                pk = jsonable(CP.claim_packet(s, target, kind))
                answer = CV.template_answer(pk)
                claims.append({"state_index": i, "target": target, "question_kind": kind, "packet": pk,
                               "template_answer": answer, "verifier": report_dict(CV.verify(answer, pk))})
    questions = []
    for q in sc["questions"]:
        idx = max((i for i, s in enumerate(states) if s["food"] == q["food"]), default=None)
        row = {**q, "lookup_key": lookup_key(q["text"], sha256_text(text)), "state_index": idx}
        if idx is None:
            row["system"] = {"status": "NO_STATE_FOR_FOOD"}
            row["baseline"] = {"arm": BASELINE_ARM, "status": "NOT_RUN", "reason": "NO_STATE_FOR_FOOD_SO_NO_PACKET"}
        else:
            c = next(c for c in claims if (c["state_index"], c["target"], c["question_kind"]) ==
                     (idx, q["target"], q["question_kind"]))
            row["system"] = {"route": c["packet"]["route"], "answer": c["template_answer"], "verifier": c["verifier"],
                             "evidence_ids": c["packet"]["evidence_ids"], "near_evidence_ids": c["packet"]["near_evidence_ids"]}
            entry = baseline_entries.get(baseline_key(model, baseline_prompt(text, q["text"])))
            row.update(baseline_block(entry, c["packet"], CV, model))
        questions.append(row)
    differs = [i for i in range(max(len(states), len(default_states)))
               if i >= len(states) or i >= len(default_states) or states[i] != default_states[i]]
    return {"id": sc["id"], "title": sc["title"], "kind": sc["kind"], "teaches": sc["teaches"],
            "recipe_text": text, "recipe_sha256": sha256_text(text), "labels": list(LABELS),
            "graph": jsonable(graph), "states": states, "transitions": transitions(states), "claims": claims,
            "questions": questions,
            "vnext_comparison": {"default_config": {"coord_food_guard": True, "lineage_vnext": False},
                                 "states_identical": states == default_states, "state_count": len(states),
                                 "default_state_count": len(default_states), "differing_state_indexes": differs}}


def build(generated_at: str, git_head: str, baseline_cache: Path) -> tuple[dict[str, bytes], dict[str, Any]]:
    """The whole snapshot in memory, gated. Raises LicenceGateError before anything can be written."""
    sys.path.insert(0, str(ROOT / "src"))
    from culinarystate.composition.state_full import StateBuilder
    from culinarystate.decision import public_mode as PM
    assert (PM.BBC_CORPUS_ID, PM.BBC_SOURCE_ID) == BBC_MARKERS
    spec = json.loads(SCENARIOS.read_text(encoding="utf-8"))
    cache = json.loads(baseline_cache.read_text(encoding="utf-8")) if baseline_cache.exists() else {}
    cases = _tool("s179_submission_demo").CASES
    model = "qwen2.5:7b-instruct"
    self_written = {sha256_text(s["recipe_text"]) for s in spec["scenarios"]}
    authored_case_texts = {sha256_text(c["recipe_text"]) for c in cases if c.get("recipe_text")}

    builder = StateBuilder()
    rung_config = dict(RUNG_CONFIG)
    payloads: dict[str, Any] = {}
    for sc in spec["scenarios"]:
        payloads[f"scenarios/{sc['id']}.json"] = scenario_payload(sc, builder, cache.get("entries") or {}, model)
    evd = builder.evd
    del builder

    from culinarystate.decision.demo_context_v3 import StrictDemoContext
    ctx = StrictDemoContext.load(public=True, host="127.0.0.1")
    mode = jsonable(ctx.mode_info())
    check_mode(mode)
    ask_index = {}
    for c in cases:
        rt = c.get("recipe_text")
        rsha = sha256_text(rt) if rt else None
        path = f"ask/{c['id']}.json"
        payloads[path] = {"id": c["id"], "query": c["query"], "expected_branch": c["expected_branch"],
                          "recipe_text": rt, "recipe_sha256": rsha, "lookup_key": lookup_key(c["query"], rsha),
                          "labels": list(LABELS), "response": jsonable(ctx.respond(c["query"], recipe_text=rt))}
        ask_index[payloads[path]["lookup_key"]] = path
    check_mode(jsonable(ctx.mode_info()))

    data_files = {p: canonical_json(v) for p, v in payloads.items()}
    sources = evidence_sources(evidence_ids(data_files), evd)
    inputs = {"scenarios_sha256": sha256_bytes(SCENARIOS.read_bytes()),
              "builder_sha256": sha256_bytes(Path(__file__).read_bytes()),
              "baseline_cache_sha256": sha256_bytes(baseline_cache.read_bytes()) if baseline_cache.exists() else None,
              "contractual_cases_from": "tools/s179_submission_demo.py"}
    extra = {"demo_mode": mode, "ask_index": dict(sorted(ask_index.items())),
             "scenarios": [{"id": s["id"], "title": s["title"], "kind": s["kind"], "path": f"scenarios/{s['id']}.json",
                            "recipe_sha256": sha256_text(s["recipe_text"])} for s in spec["scenarios"]],
             "self_written_recipe_sha256": sorted(self_written),
             "authored_contractual_case_recipe_sha256": sorted(authored_case_texts)}
    files = assemble(payloads, git_head=git_head, generated_at=generated_at, rung_config=rung_config,
                     evidence_sources_map=sources, inputs=inputs, extra=extra)
    licence_gate(files, self_written | authored_case_texts)
    return files, payloads


# ---------------------------------------------------------------- disk
def read_snapshot(out_dir: Path) -> dict[str, bytes]:
    return {str(p.relative_to(out_dir)): p.read_bytes() for p in sorted(out_dir.rglob("*.json"))} if out_dir.exists() else {}


def write_snapshot(files: Mapping[str, bytes], out_dir: Path, key) -> None:
    signed = {**files, "manifest.sig": sign(files["manifest.json"], key) + b"\n", "public_key.pem": public_key_pem(key)}
    licence_gate({p: b for p, b in signed.items() if not p.endswith(".json")}, set())
    for stale in set(read_snapshot(out_dir)) - set(files):
        (out_dir / stale).unlink()
    for rel, data in signed.items():
        path = out_dir / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)


def verify_snapshot(out_dir: Path) -> list[str]:
    problems = []
    try:
        manifest_bytes = (out_dir / "manifest.json").read_bytes()
        sig, pub = (out_dir / "manifest.sig").read_bytes().strip(), (out_dir / "public_key.pem").read_bytes()
    except OSError as exc:
        return [f"MISSING {exc}"]
    manifest = json.loads(manifest_bytes)
    if canonical_json(manifest) != manifest_bytes:
        problems.append("MANIFEST_NOT_CANONICAL")
    if not verify_signature(manifest_bytes, sig, pub):
        problems.append("SIGNATURE_INVALID")
    disk = {p: b for p, b in read_snapshot(out_dir).items() if p != "manifest.json"}
    for rel, meta in manifest["files"].items():
        if rel not in disk:
            problems.append(f"MISSING_ON_DISK {rel}")
        elif sha256_bytes(disk[rel]) != meta["sha256"]:
            problems.append(f"SHA256_MISMATCH {rel}")
    problems += [f"UNLISTED_FILE {rel}" for rel in disk if rel not in manifest["files"]]
    return problems


def git_head() -> str:
    return subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--generated-at", help="ISO time recorded in the manifest (required to build; no wall clock is read)")
    ap.add_argument("--out", type=Path, default=OUT_DIR)
    ap.add_argument("--baseline-cache", type=Path, default=BASELINE_CACHE)
    ap.add_argument("--private-key", type=Path, default=PRIVATE_KEY)
    ap.add_argument("--run-baseline", action="store_true", help="fill the baseline cache over ssh, then exit")
    ap.add_argument("--verify", action="store_true", help="check signature and file hashes of an existing snapshot")
    ap.add_argument("--check", action="store_true", help="rebuild in memory; non-zero exit if the snapshot on disk differs")
    a = ap.parse_args(argv)
    if a.run_baseline:
        print(json.dumps(run_baseline(json.loads(SCENARIOS.read_text(encoding="utf-8"))["scenarios"], a.baseline_cache)))
        return 0
    if a.verify:
        problems = verify_snapshot(a.out)
        print(json.dumps({"verify": "FAIL" if problems else "OK", "problems": problems,
                          "manifest_sha256": sha256_bytes((a.out / "manifest.json").read_bytes()) if not problems else None}))
        return 1 if problems else 0
    try:
        if a.check:
            # git_head and generated_at are taken from the committed manifest: committing the snapshot moves
            # HEAD, so the gate compares content (engine output, inputs, builder) and not the commit it sits in.
            old = json.loads((a.out / "manifest.json").read_bytes())
            files, _ = build(old["generated_at"], old["git_head"], a.baseline_cache)
            problems = diff_snapshot(files, read_snapshot(a.out)) + verify_snapshot(a.out)
            print(json.dumps({"check": "STALE" if problems else "FRESH", "problems": problems, "files": len(files)}))
            return 1 if problems else 0
        if not a.generated_at:
            ap.error("--generated-at is required to build")
        files, _ = build(a.generated_at, git_head(), a.baseline_cache)
    except LicenceGateError as exc:
        print(f"LICENCE GATE FAILED, nothing written: {exc}", file=sys.stderr)
        return 2
    write_snapshot(files, a.out, load_or_create_private_key(a.private_key))
    total = sum(p.stat().st_size for p in a.out.rglob("*") if p.is_file())
    print(json.dumps({"written": len(files) + 2, "bytes": total, "manifest_sha256": sha256_bytes(files["manifest.json"]),
                      "problems_on_verify": verify_snapshot(a.out)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
