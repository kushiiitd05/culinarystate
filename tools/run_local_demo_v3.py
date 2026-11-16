#!/usr/bin/env python3
"""Strict-v3 local demo, offline assets, declared provenance beside every display number."""
from pathlib import Path
import argparse
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--local-data", action="store_true")
    args = parser.parse_args(argv)
    from culinarystate.app.strict_server_v3 import make_server
    from culinarystate.decision.demo_context_v3 import StrictDemoContext
    context = StrictDemoContext.load(public=not args.local_data, host="127.0.0.1")
    server = make_server(("127.0.0.1", args.port), context)
    print(f"Local strict-v3 demo: http://127.0.0.1:{server.server_address[1]}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
