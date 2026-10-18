"""Minimal Ollama client (A100 via SSH tunnel: ssh -f -N -L 11435:localhost:11434 vinayak-server).
Deterministic decoding (temperature 0, fixed seed) for replay (§257B C16 obligation)."""
from __future__ import annotations

import json
import os
import urllib.request

URL = os.environ.get("OLLAMA_URL", "http://localhost:11435")


def generate(prompt: str, model: str = "qwen2.5:7b-instruct", seed: int = 7, timeout: int = 300) -> str:
    body = json.dumps({"model": model, "prompt": prompt, "stream": False,
                       "options": {"temperature": 0, "seed": seed, "num_predict": 200, "num_ctx": 4096}}).encode()
    req = urllib.request.Request(f"{URL}/api/generate", body, {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())["response"].strip()
