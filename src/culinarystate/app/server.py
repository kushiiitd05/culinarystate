"""Demo web server, standard library only (S173, D-075 M6). DEMO_ONLY, NON_CITABLE.

GET /            static page (src/culinarystate/app/static/index.html)
GET /api/health  {"status": "ok", "mode": {"mode": "public" | "local", ...}}  (S177: which mode is active)
POST /api/ask    {"question": str <= 500, "recipe_text": str <= 6000 | null} -> DemoContext.respond(...) as JSON

Safety: body <= 20 KB, JSON only, per-IP rate limit (default 30 requests/minute), strict CSP, no stack traces or
handler messages in responses (errors are logged server-side). The page renders every string with textContent.

    python -m culinarystate.app.server --host 127.0.0.1 --port 8765 [--public | --local]

S177: public mode (BBC-derived recipe-corpus edges and carbon figures left out) is ON by default for a hosted build and
for a server bound to a non-loopback address, OFF for local use; override with --public / --local or env CS_DEMO_PUBLIC
(see culinarystate.decision.public_mode). The page shows which mode is active.

S178 (FIX-GOV, GOV-4): behind a tunnel the server is still bound to 127.0.0.1 and resolves to local mode, so every
request is checked first: one that carries a forwarding header (X-Forwarded-For, Forwarded, X-Forwarded-Host,
CF-Connecting-IP, ...), a non-loopback or missing Host header, or comes from a non-loopback peer is treated as public.
When the context is not in public mode (or its mode is unknown) such a request gets 503 with a short reason on every
path (page, health, ask), and the context is never called. Start a tunnelled demo with CS_DEMO_PUBLIC=1 or --public.
"""
from __future__ import annotations

import argparse
import json
import logging
import threading
import time
from collections import deque
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from culinarystate.decision.public_mode import refusal_for_request

LOG = logging.getLogger("culinarystate.app")
STATIC = Path(__file__).resolve().parent / "static" / "index.html"
MAX_BODY, MAX_Q, MAX_RECIPE = 20_000, 500, 6000
CSP = ("default-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
       "font-src https://fonts.gstatic.com; script-src 'self' 'unsafe-inline'; connect-src 'self'; "
       "frame-ancestors 'none'; base-uri 'none'; form-action 'self'")


class BadRequest(ValueError):
    """Client error with a user-facing message."""


def validate(payload: Any) -> tuple[str, str | None]:
    if not isinstance(payload, dict):
        raise BadRequest("Send a JSON object with a question.")
    q = payload.get("question")
    if not isinstance(q, str):
        raise BadRequest("The question must be text.")
    q = q.strip()
    if len(q) > MAX_Q:
        raise BadRequest(f"Keep the question under {MAX_Q} characters.")
    r = payload.get("recipe_text")
    if r is not None and not isinstance(r, str):
        raise BadRequest("Recipe steps must be text.")
    if r is not None and len(r) > MAX_RECIPE:
        raise BadRequest(f"Keep the recipe steps under {MAX_RECIPE} characters.")
    return q, (r.strip() or None) if r else None


class RateLimiter:
    def __init__(self, per_minute: int = 30) -> None:
        self.per_minute, self._hits, self._lock = per_minute, {}, threading.Lock()

    def allow(self, key: str, now: float | None = None) -> bool:
        now = time.monotonic() if now is None else now
        with self._lock:
            q = self._hits.setdefault(key, deque())
            while q and now - q[0] >= 60.0:
                q.popleft()
            if len(q) >= self.per_minute:
                return False
            q.append(now)
            return True


def _mode_info(ctx: Any) -> dict | None:
    info = getattr(ctx, "mode_info", None)
    if not callable(info):
        return None
    try:
        out = info()
    except Exception:  # noqa: BLE001 - an unreadable mode is treated as not public
        LOG.exception("mode_info failed")
        return None
    return out if isinstance(out, dict) else None


def make_handler(ctx: Any, *, per_minute: int = 30) -> type[BaseHTTPRequestHandler]:
    """The request handler class for ``ctx`` (make_server binds it; tests drive it without a socket)."""
    limiter = RateLimiter(per_minute)

    class Handler(BaseHTTPRequestHandler):
        server_version = "CulinaryStateDemo/0.1"

        def log_message(self, fmt, *args):  # route access logs to logging, not stderr
            LOG.info("%s %s", self.address_string(), fmt % args)

        def _send(self, status: int, body: bytes, ctype: str) -> None:
            self.send_response(status)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Content-Security-Policy", CSP)
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def _json(self, status: int, obj: Any) -> None:
            self._send(status, json.dumps(obj, ensure_ascii=False, default=str).encode("utf-8"),
                       "application/json; charset=utf-8")

        def _refuse_if_public_in_local_mode(self) -> bool:
            """GOV-4: 503 for a tunnelled / proxied / remote request unless public mode is active. True when refused."""
            refusal = refusal_for_request(_mode_info(ctx), self.headers, self.client_address[0] if self.client_address else None)
            if refusal is None:
                return False
            LOG.warning("refused a public-looking request in %s mode (%s)", refusal["mode"], refusal["signal"])
            if self.path.startswith("/api/"):
                self._json(HTTPStatus.SERVICE_UNAVAILABLE, refusal)
            else:
                self._send(HTTPStatus.SERVICE_UNAVAILABLE, (refusal["error"] + "\n").encode("utf-8"), "text/plain; charset=utf-8")
            return True

        def do_GET(self) -> None:  # noqa: N802
            if self._refuse_if_public_in_local_mode():
                return
            if self.path in ("/", "/index.html"):
                self._send(200, STATIC.read_bytes(), "text/html; charset=utf-8")
            elif self.path == "/api/health":
                self._json(200, {"status": "ok", "mode": _mode_info(ctx) or {"mode": "unknown"}})
            else:
                self._json(404, {"error": "Not found."})

        def do_POST(self) -> None:  # noqa: N802
            if self._refuse_if_public_in_local_mode():
                return
            if self.path != "/api/ask":
                return self._json(404, {"error": "Not found."})
            if not limiter.allow(self.client_address[0]):
                return self._json(HTTPStatus.TOO_MANY_REQUESTS, {"error": "Too many questions. Wait a minute."})
            try:
                n = int(self.headers.get("Content-Length") or 0)
            except ValueError:
                n = -1
            if n < 0 or n > MAX_BODY:
                return self._json(413 if n > MAX_BODY else 400, {"error": "The request is too large."})
            try:
                q, recipe = validate(json.loads(self.rfile.read(n) or b"null"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                return self._json(400, {"error": "Send valid JSON."})
            except BadRequest as exc:
                return self._json(400, {"error": str(exc)})
            try:
                out = ctx.respond(q, recipe_text=recipe)
            except Exception:  # noqa: BLE001 - logged here, never sent to the client
                LOG.exception("respond failed")
                return self._json(500, {"error": "Answering failed on the server. Nothing was guessed."})
            self._json(200, out)

    return Handler


def make_server(addr: tuple[str, int], ctx: Any, *, per_minute: int = 30) -> ThreadingHTTPServer:
    """A threading HTTP server on ``addr`` with the handler from make_handler."""
    return ThreadingHTTPServer(addr, make_handler(ctx, per_minute=per_minute))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--per-minute", type=int, default=30)
    grp = ap.add_mutually_exclusive_group()
    grp.add_argument("--public", dest="public", action="store_true", default=None,
                     help="public mode: leave out BBC-derived recipe-corpus edges and carbon figures")
    grp.add_argument("--local", dest="public", action="store_false",
                     help="local mode: keep them (own machine only)")
    a = ap.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    from culinarystate.decision.demo_context import DemoContext
    LOG.info("loading ledgers (about 30-40 s)")
    ctx = DemoContext.load(public=a.public, host=a.host)
    srv = make_server((a.host, a.port), ctx, per_minute=a.per_minute)
    LOG.info("mode: %s (source %s)", ctx.mode_info()["mode"], ctx.mode_info().get("source"))
    LOG.info("serving on http://%s:%d", a.host, a.port)
    srv.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
