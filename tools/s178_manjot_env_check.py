#!/usr/bin/env python
"""S178 (T7-C01-R5, T8-C15-R3): which packages, Step 35 bound inputs and Ollama models are visible on THIS host.

Read-only. Writes ``reports/s178/manjot_env_inputs_check.json`` (counts, names, versions, sha256 matches; no recipe text,
no private address). Three checks:

1. third-party packages: importable or not (``importlib``), with version;
2. Step 35 v2 bound inputs (``reports/step35/preregistration_35_0_v2_package.sha256.UNSIGNED.json``): present here? sha256
   equal to the template? plus the three files the template lists as ``not_bound_absent_here``, with the frozen hashes
   found in committed freeze manifests;
3. Ollama on this host (``GET /api/tags`` on localhost only, metadata only, never ``/api/generate``): is a server there and
   which qwen models does it list. This is NOT the D5 run host (vinayak through a tunnel); a digest seen here is a
   reference, not a pin.

    python tools/s178_manjot_env_check.py
"""
from __future__ import annotations

import hashlib
import importlib
import importlib.util
import json
import os
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
OUT = ROOT / "reports/s178/manjot_env_inputs_check.json"
PACKAGES = ["numpy", "pandas", "pyarrow", "scipy", "sklearn", "torch", "rdkit", "lightgbm", "xgboost", "hypothesis",
            "lxml", "requests", "networkx", "transformers", "sentence_transformers", "statsmodels", "matplotlib", "yaml",
            "tqdm", "jsonschema", "pytest", "faiss", "rank_bm25", "tabpfn"]
PROJECT_MODULES = ["culinarystate.representation.cuisine_rungs", "culinarystate.representation.explicit_runner",
                   "culinarystate.representation.prereg_guard", "culinarystate.representation.recipe_rungs",
                   "culinarystate.representation.similarity_registry", "culinarystate.molecules.pubchem",
                   "culinarystate.transition.baselines", "culinarystate.generation.llm",
                   "culinarystate.retrieval.retriever", "culinarystate.evaluation.h3_independent"]
FROZEN_IN = {  # frozen hashes recorded in committed manifests (path inside the manifest -> manifest file)
    "ledgers/recipe_base/recipe_base_v1.parquet": "reports/step07/step07hr_freeze_manifest.json",
    "ledgers/recipe_identity/gold_firewall_v1.parquet": "ledgers/recipe_identity_v2/op_selection_report_v1.json",
    "ledgers/recipe_semantics/recipe_ingredient_mentions_v1.parquet": "reports/step07/step07hr_freeze_manifest.json",
}


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def pkg_status(name: str) -> dict:
    try:
        spec = importlib.util.find_spec(name)
    except Exception:
        spec = None
    if spec is None:
        return {"importable": False, "reason": "not installed"}
    try:
        m = importlib.import_module(name)
        if name == "jsonschema":
            from importlib.metadata import version
            v = version("jsonschema")
        else:
            v = getattr(m, "__version__", None)
        return {"importable": True, "version": v}
    except Exception as e:  # pragma: no cover
        return {"importable": False, "reason": f"{type(e).__name__}: {str(e)[:80]}"}


def step35_inputs() -> dict:
    tmpl = json.loads((ROOT / "reports/step35/preregistration_35_0_v2_package.sha256.UNSIGNED.json").read_text())
    base = ROOT / "reports/step35"
    bound = []
    for b in tmpl["bound_files"]:
        p = (base / b["path"]).resolve()
        rel = os.path.relpath(p, ROOT)
        bound.append({"path": rel, "present": p.exists(), "sha256_matches_template": (sha(p) == b["sha256"]) if p.exists() else None})
    extra = []
    for rel in tmpl["not_bound_absent_here"]:
        p = ROOT / rel
        frozen = None
        mf = ROOT / FROZEN_IN[rel]
        if mf.exists():
            txt = mf.read_text()
            import re
            m = re.search(re.escape(rel) + r'"?\s*:\s*"([0-9a-f]{64})"', txt)
            frozen = m.group(1) if m else None
        row = {"path": rel, "present_here": p.exists(), "frozen_sha256_in_repo": frozen, "frozen_sha256_source": FROZEN_IN[rel]}
        if p.exists():
            row["sha256_here"] = sha(p)
            row["sha256_matches_frozen"] = (row["sha256_here"] == frozen) if frozen else None
        extra.append(row)
    return {"template_document_sha256": tmpl["sha256"], "n_bound": len(bound),
            "n_bound_present": sum(b["present"] for b in bound),
            "n_bound_sha_match": sum(bool(b["sha256_matches_template"]) for b in bound), "bound": bound,
            "listed_absent_in_template": extra}


def ollama_local(timeout: int = 3) -> dict:
    try:
        with urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=timeout) as r:
            models = json.loads(r.read()).get("models", [])
        q = [{"name": m["name"], "digest_prefix12": m["digest"][:12]} for m in models if m["name"].startswith("qwen")]
        return {"server_on_localhost": True, "n_models": len(models), "qwen_models": q,
                "has_tag_qwen2.5:7b-instruct": any(m["name"] == "qwen2.5:7b-instruct" for m in models),
                "note": "metadata only (GET /api/tags); no generation; not the D5 run host, so a digest here is a reference, not a pin"}
    except Exception as e:
        return {"server_on_localhost": False, "reason": f"{type(e).__name__}"}


def main() -> int:
    mods = {}
    for m in PROJECT_MODULES:
        try:
            importlib.import_module(m)
            mods[m] = "OK"
        except Exception as e:
            mods[m] = f"FAIL {type(e).__name__}: {str(e)[:60]}"
    out = {"label": "S178 T7-C01-R5 / T8-C15-R3 host check", "python": sys.version.split()[0],
           "packages": {p: pkg_status(p) for p in PACKAGES}, "project_modules": mods,
           "step35_inputs": step35_inputs(), "ollama_local": ollama_local()}
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print("wrote", OUT.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
