#!/usr/bin/env bash
# Preflight for the CulinaryState Explorer demo (handover B4). Exits 0 only if every check passes.
#
#   tools/preflight.sh          snapshot + public build + engine-down path. No network to any model.
#   tools/preflight.sh --live   also runs the ten /live presets through the running engine
#                               (start it first with tools/live_demo.sh; uses your NVIDIA key).
#
# Browser checks use the local Google Chrome in headless mode (no Playwright dependency added at freeze).
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WEB="$ROOT/web"
LIVE=0; [ "${1:-}" = "--live" ] && LIVE=1
PORT=3077
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
LOG="${TMPDIR:-/tmp}/culinarystate-preflight"; mkdir -p "$LOG"
FAILS=0; SERVER_PID=""

PY="${CS_PYTHON:-}"
if [ -z "$PY" ]; then
  for cand in /opt/anaconda3/bin/python "$ROOT/../.venvs/s179-py311/bin/python"; do [ -x "$cand" ] && { PY="$cand"; break; }; done
fi

ok()   { printf '  \033[32m✓\033[0m %s\n' "$1"; }
bad()  { printf '  \033[31m✗\033[0m %s\n' "$1"; FAILS=$((FAILS + 1)); }
check() { if eval "$2"; then ok "$1"; else bad "$1"; fi; }   # name, shell condition
code()  { curl -s -o /dev/null -w '%{http_code}' -m 10 "http://localhost:$PORT$1"; }
dom()   { "$CHROME" --headless=new --disable-gpu --virtual-time-budget=8000 --dump-dom "http://localhost:$PORT$1" 2>/dev/null; }

stop_server() { [ -n "$SERVER_PID" ] && { pkill -TERM -P "$SERVER_PID" 2>/dev/null; kill "$SERVER_PID" 2>/dev/null; wait "$SERVER_PID" 2>/dev/null; }; SERVER_PID=""; }
start_server() {  # extra env assignments, e.g. CS_LIVE_ENABLED=1
  stop_server
  (cd "$WEB" && exec env NEXT_TELEMETRY_DISABLED=1 "$@" ./node_modules/.bin/next start -p "$PORT") > "$LOG/web.log" 2>&1 &
  SERVER_PID=$!
  for _ in $(seq 1 40); do curl -s -o /dev/null -m 2 "http://localhost:$PORT/" && return 0; sleep 0.5; done
  bad "web server did not start (log: $LOG/web.log)"; return 1
}
trap stop_server EXIT INT TERM

echo "CulinaryState preflight · $(date '+%Y-%m-%d %H:%M') · $(git -C "$ROOT" rev-parse --short HEAD)"
[ -x "$PY" ] || { echo "✗ no Python found; set CS_PYTHON"; exit 1; }
[ -x "$CHROME" ] || { echo "✗ Google Chrome not found at $CHROME"; exit 1; }
[ -x "$WEB/node_modules/.bin/next" ] || { echo "✗ run: (cd web && npm ci)"; exit 1; }
lsof -i ":$PORT" -sTCP:LISTEN >/dev/null 2>&1 && { echo "✗ port $PORT is busy"; exit 1; }

echo "1 · Snapshot"
v="$("$PY" "$ROOT/tools/s181_build_demo_snapshot.py" --verify 2>&1 | tail -1)"
check "signature and file hashes verify ($(echo "$v" | grep -o '"manifest_sha256": "[0-9a-f]\{12\}' | cut -d'"' -f4)…)" '[[ "$v" == *"\"verify\": \"OK\""* ]]'
c="$("$PY" "$ROOT/tools/s181_build_demo_snapshot.py" --check 2>&1 | tail -1)"
check "in-memory rebuild matches disk (--check FRESH)" '[[ "$c" == *"\"check\": \"FRESH\""* ]]'

echo "2 · Secrets and licence markers"
check "no NVIDIA key in tracked files" '! git -C "$ROOT" grep -qI "nvapi-[A-Za-z0-9_-]\{20,\}" -- . ":!tools/preflight.sh"'
check "no private key in tracked files" '! git -C "$ROOT" grep -qI "BEGIN [A-Z ]*PRIVATE KEY" -- .'
check "public key committed" 'git -C "$ROOT" ls-files --error-unmatch web/public/snapshot/public_key.pem >/dev/null 2>&1'

echo "3 · Public build (no CS_LIVE_ENABLED)"
if (cd "$WEB" && rm -rf .next && env -u CS_LIVE_ENABLED NEXT_TELEMETRY_DISABLED=1 ./node_modules/.bin/next build > "$LOG/build.log" 2>&1); then
  ok "next build"
  check "no BBC marker in shipped files" '! grep -rlq -e "BBCGF-A1" -e "SRC-000002" "$WEB/public" "$WEB/.next/static" 2>/dev/null'
  if start_server env -u CS_LIVE_ENABLED; then
    for p in / /lab /compare /method /snapshot/manifest.json /snapshot/manifest.sig /snapshot/public_key.pem; do
      check "GET $p → 200" '[ "$(code "$p")" = 200 ]'
    done
    for p in /live /api/live; do check "GET $p → 404 (live hidden)" '[ "$(code "$p")" = 404 ]'; done
    check "POST /api/live/analyse → 404" '[ "$(curl -s -o /dev/null -w "%{http_code}" -X POST -H "content-type: application/json" -d "{}" "http://localhost:$PORT/api/live/analyse")" = 404 ]'
    for p in / /lab /compare /method; do
      d="$(dom "$p")"
      check "$p: badge says signature verified" '[[ "$d" == *">verified</span>"* ]]'
      check "$p: no link to /live" '[[ "$d" != *"href=\"/live\""* ]]'
    done
  fi
else
  bad "next build failed (log: $LOG/build.log)"
fi

echo "4 · Engine-down path (CS_LIVE_ENABLED=1, engine unreachable)"
if start_server CS_LIVE_ENABLED=1 CS_LIVE_URL=http://127.0.0.1:9; then
  check "GET /live → 200" '[ "$(code /live)" = 200 ]'
  h="$(curl -s -m 10 "http://localhost:$PORT/api/live")"
  check "GET /api/live reports offline" '[[ "$h" == *"\"status\":\"offline\""* ]]'
  check "/live shows the engine-offline chip" '[[ "$(dom /live)" == *"Engine offline"* ]]'
fi
stop_server

if [ "$LIVE" = 1 ]; then
  echo "5 · Live presets through the running engine (127.0.0.1:8770)"
  if curl -s -m 3 http://127.0.0.1:8770/api/health | grep -q '"status": "ok"'; then
    "$PY" - "$WEB/src/components/live/presets.ts" <<'EOF' || FAILS=$((FAILS + 1))
import json, re, sys, urllib.request
src = open(sys.argv[1], encoding="utf-8").read()
groups = re.findall(r'group: "([^"]+)".*?presets: \[(.*?)\n    \],', src, re.S)
expect = {"Fix my dish": "ADVICE", "Nutrients": "NUTRIENT", "Safety": "SAFETY"}
n_bad = n = 0
for group, body in groups:
    for label, text, question in re.findall(r'label: "([^"]+)".*?text: "([^"]+)",\s*question: "([^"]+)"', body, re.S):
        n += 1
        req = urllib.request.Request("http://127.0.0.1:8770/api/live", method="POST",
                                     data=json.dumps({"question": question, "recipe_text": text, "self_written": True}).encode(),
                                     headers={"Content-Type": "application/json"})
        try:
            out = json.load(urllib.request.urlopen(req, timeout=180))
        except Exception as exc:  # noqa: BLE001
            print(f"  ✗ {label}: {type(exc).__name__}: {exc}"); n_bad += 1; continue
        stages = {s["id"]: s["status"] for s in out.get("pipeline", [])}
        problems = [p for p in (
            out.get("error") and f"error {out['error']}",
            out.get("mode") != expect[group] and f"mode {out.get('mode')} (expected {expect[group]})",
            "verify" not in stages and "no verify stage",
            stages.get("verify") == "error" and "verify stage errored",
            any(v == "error" for v in stages.values()) and f"stage errors {stages}",
        ) if p]
        print(f"  {'✗' if problems else '✓'} {label}: mode {out.get('mode')}, verify {stages.get('verify')}, {out.get('timing_ms', {}).get('total')} ms"
              + (f" — {'; '.join(problems)}" if problems else ""))
        n_bad += bool(problems)
print(f"  {n - n_bad}/{n} presets reached Verify without error")
sys.exit(1 if n_bad or n != 10 else 0)
EOF
  else
    bad "engine not running on 127.0.0.1:8770 (start it with tools/live_demo.sh)"
  fi
fi

echo
if [ "$FAILS" = 0 ]; then echo "PREFLIGHT PASS"; exit 0; else echo "PREFLIGHT FAIL: $FAILS check(s)"; exit 1; fi
