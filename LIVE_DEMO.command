#!/usr/bin/env bash
# Double-click in Finder: opens Terminal, starts the live demo, opens the /live page.
exec "$(cd "$(dirname "$0")" && pwd)/tools/live_demo.sh"
