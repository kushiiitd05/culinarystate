"""Local HTTP server for the S182 live RAG console. Standard library only.

    /opt/anaconda3/bin/python tools/s182_live_rag_server.py [--port 8770] [--model ...]

GET  /api/health -> {"status": "ok", "model": ..., "loaded_s": ...}
POST /api/analyse {"question", "recipe_text"} -> fast pre-model phase (state, simulation, evidence, similar)
POST /api/live   {"question": str, "recipe_text": str, "self_written": bool} -> LiveEngine.answer(...)

Binds 127.0.0.1 only: the Next.js route handler proxies to it, the browser never reaches it.
Body cap, JSON only, a global rate limit, ``no-store``, and no stack traces in responses.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import threading
import time
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAX_BODY = 16_384


def _load_engine_module():
    spec = importlib.util.spec_from_file_location("s182_live_rag", ROOT / "tools/s182_live_rag.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["s182_live_rag"] = mod
    spec.loader.exec_module(mod)
    return mod


class RateLimit:
    def __init__(self, per_minute: int) -> None:
        self.per_minute, self.hits, self.lock = per_minute, deque(), threading.Lock()

    def allow(self) -> bool:
        now = time.monotonic()
        with self.lock:
            while self.hits and now - self.hits[0] > 60:
                self.hits.popleft()
            if len(self.hits) >= self.per_minute:
                return False
            self.hits.append(now)
            return True


def make_handler(LR, engine, llm, limit: RateLimit, loaded_s: float):
    class Handler(BaseHTTPRequestHandler):
        server_version = "cs-live/1"

        def log_message(self, fmt: str, *args) -> None:  # one line, never the question text
            sys.stderr.write(f"{self.command} {self.path} {args[1] if len(args) > 1 else ''}\n")

        def _send(self, code: int, obj) -> None:
            body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:  # noqa: N802
            if self.path == "/api/health":
                self._send(200, {"status": "ok", "model": llm.model, "loaded_s": loaded_s})
            else:
                self._send(404, {"error": "not found"})

        def do_POST(self) -> None:  # noqa: N802
            if self.path not in ("/api/live", "/api/analyse"):
                return self._send(404, {"error": "not found"})
            if "application/json" not in (self.headers.get("Content-Type") or ""):
                return self._send(415, {"error": "JSON only"})
            n = int(self.headers.get("Content-Length") or 0)
            if n <= 0 or n > MAX_BODY:
                return self._send(413, {"error": f"body must be 1-{MAX_BODY} bytes"})
            if not limit.allow():
                return self._send(429, {"error": "rate limit; try again in a minute"})
            try:
                req = LR.validate(json.loads(self.rfile.read(n).decode("utf-8")))
            except (json.JSONDecodeError, UnicodeDecodeError):
                return self._send(400, {"error": "invalid JSON"})
            except LR.RequestError as exc:
                return self._send(400, {"error": str(exc)})
            try:
                if self.path == "/api/analyse":
                    out = engine.analyse_only(req["question"], req["recipe_text"], model=llm.model)
                else:
                    out = engine.answer(req["question"], req["recipe_text"], llm=llm, self_written=req["self_written"])
            except Exception as exc:  # noqa: BLE001 - logged server side, generic message to client
                sys.stderr.write(f"engine error: {type(exc).__name__}: {exc}\n")
                return self._send(500, {"error": f"The engine could not process this recipe ({type(exc).__name__}). "
                                                 "Nothing was guessed; details are in the server log."})
            self._send(200, out)

    return Handler


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--port", type=int, default=8770)
    ap.add_argument("--per-minute", type=int, default=20)
    ap.add_argument("--model", default=None)
    args = ap.parse_args(argv)
    LR = _load_engine_module()
    LR.read_key()  # fail fast if the key file is missing; the value is not kept
    t = time.perf_counter()
    engine = LR.LiveEngine.load()
    loaded_s = round(time.perf_counter() - t, 1)
    llm = LR.NimLLM(args.model or LR.DEFAULT_MODEL)
    srv = ThreadingHTTPServer(("127.0.0.1", args.port),
                              make_handler(LR, engine, llm, RateLimit(args.per_minute), loaded_s))
    print(f"live RAG console on http://127.0.0.1:{args.port}  model={llm.model}  loaded in {loaded_s}s", flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
