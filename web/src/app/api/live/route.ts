// Proxy to the local live RAG server (tools/s182_live_rag_server.py, 127.0.0.1 only).
// The browser never talks to Python or to NVIDIA directly; the key never leaves the Python process.
import { liveDisabledResponse, liveEnabled } from "@/lib/liveFlag";

const LIVE_URL = process.env.CS_LIVE_URL ?? "http://127.0.0.1:8770";
const HEALTH_TIMEOUT_MS = 1500;
const ASK_TIMEOUT_MS = 150_000;

function offline(reason: string, status = 503) {
  return Response.json({ status: "offline", reason }, { status, headers: { "Cache-Control": "no-store" } });
}

export async function GET() {
  if (!liveEnabled()) return liveDisabledResponse();
  try {
    const r = await fetch(`${LIVE_URL}/api/health`, { cache: "no-store", signal: AbortSignal.timeout(HEALTH_TIMEOUT_MS) });
    if (!r.ok) return offline(`health HTTP ${r.status}`);
    return Response.json(await r.json(), { headers: { "Cache-Control": "no-store" } });
  } catch {
    return offline("live server not running");
  }
}

export async function POST(request: Request) {
  if (!liveEnabled()) return liveDisabledResponse();
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return Response.json({ error: "invalid JSON" }, { status: 400 });
  }
  try {
    const r = await fetch(`${LIVE_URL}/api/live`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      cache: "no-store",
      signal: AbortSignal.timeout(ASK_TIMEOUT_MS),
    });
    return Response.json(await r.json(), { status: r.status, headers: { "Cache-Control": "no-store" } });
  } catch (e) {
    const timedOut = e instanceof DOMException && e.name === "TimeoutError";
    return offline(timedOut ? "live server timed out" : "live server not running", timedOut ? 504 : 503);
  }
}
