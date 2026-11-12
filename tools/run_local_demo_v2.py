#!/usr/bin/env python3
"""Run the separately versioned strict demo on loopback; no hosting or model call."""
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--local-data", action="store_true", help="include local-only corpus patterns on this machine")
    args = parser.parse_args(argv)
    from culinarystate.app.server import make_server
    from culinarystate.decision.demo_context_v2 import StrictDemoContext
    context = StrictDemoContext.load(public=not args.local_data, host="127.0.0.1")
    server = make_server(("127.0.0.1", args.port), context)
    print(f"Local strict-v2 demo: http://127.0.0.1:{server.server_address[1]}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
