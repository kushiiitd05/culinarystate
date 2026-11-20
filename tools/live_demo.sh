#!/usr/bin/env bash
# Start the live RAG console: Python engine (127.0.0.1:8770) + Next.js app (localhost:3000), then open /live.
# Ctrl-C (or closing the Terminal window) stops everything this script started.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# Python with the engine's dependencies: $CS_PYTHON if set, else the first of these that exists.
PY="${CS_PYTHON:-}"
if [ -z "$PY" ]; then
  for cand in /opt/anaconda3/bin/python "$ROOT/../.venvs/s179-py311/bin/python"; do
    [ -x "$cand" ] && { PY="$cand"; break; }
  done
fi
[ -n "$PY" ] && [ -x "$PY" ] || { echo "✗ no Python found; set CS_PYTHON=/path/to/python"; exit 1; }
export CS_LIVE_ENABLED=1   # /live and its API routes exist only with this server-side flag (public builds omit it)
KEY_FILE="$HOME/.config/culinarystate/nvidia.env"
ENGINE_URL=http://127.0.0.1:8770/api/health
WEB_URL=http://localhost:3000
LOG_DIR="${TMPDIR:-/tmp}/culinarystate-live"
mkdir -p "$LOG_DIR"
PIDS=()

cleanup() {
  trap - EXIT INT TERM
  echo; echo "Stopping live demo…"
  for p in "${PIDS[@]:-}"; do
    [ -n "$p" ] || continue
    pkill -TERM -P "$p" 2>/dev/null || true   # children (next dev's worker)
    kill -TERM "$p" 2>/dev/null || true
  done
}
trap cleanup EXIT INT TERM

wait_for() {  # url, seconds, name
  for _ in $(seq 1 "$2"); do curl -s -m 2 -o /dev/null "$1" && return 0; sleep 1; done
  echo "✗ $3 did not start. Log: $LOG_DIR"; exit 1
}

[ -f "$KEY_FILE" ] || { echo "✗ NVIDIA key file missing: $KEY_FILE"; exit 1; }

caffeinate -dimsu & PIDS+=($!)   # keep the Mac awake during the talk

if curl -s -m 2 -o /dev/null "$ENGINE_URL"; then
  echo "• engine already running"
else
  echo "• starting engine (loads in ~5 s)…"
  "$PY" "$ROOT/tools/s182_live_rag_server.py" > "$LOG_DIR/engine.log" 2>&1 & PIDS+=($!)
  wait_for "$ENGINE_URL" 60 "engine"
fi
echo "✓ engine: $(curl -s "$ENGINE_URL")"

if curl -s -m 2 -o /dev/null "$WEB_URL"; then
  echo "• web app already running"
else
  echo "• starting web app…"
  (cd "$ROOT/web" && exec ./node_modules/.bin/next dev > "$LOG_DIR/web.log" 2>&1) & PIDS+=($!)
  wait_for "$WEB_URL" 90 "web app"
fi
echo "✓ web app: $WEB_URL"

curl -s -m 60 -o /dev/null "$WEB_URL/live" || true   # compile the page before the browser asks for it
open "$WEB_URL/live"
echo
echo "Live demo open at $WEB_URL/live   (logs: $LOG_DIR)"
echo "Press Ctrl-C to stop."
wait
