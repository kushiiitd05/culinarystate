"""Separate strict-v3 static view with the unchanged request validation/GOV-4 guard."""
from pathlib import Path
from http.server import ThreadingHTTPServer
from culinarystate.app import server as legacy

STATIC = Path(__file__).resolve().parent / "static" / "strict_v3.html"


def make_handler(ctx, *, per_minute=30):
    base = legacy.make_handler(ctx, per_minute=per_minute)

    class StrictHandler(base):
        def do_GET(self):
            if self.path in ("/", "/index.html"):
                if self._refuse_if_public_in_local_mode():
                    return
                self._send(200, STATIC.read_bytes(), "text/html; charset=utf-8")
                return
            super().do_GET()

    return StrictHandler


def make_server(addr, ctx, *, per_minute=30):
    return ThreadingHTTPServer(addr, make_handler(ctx, per_minute=per_minute))
