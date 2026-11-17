// Fast first phase: engine only (state, simulation, evidence, similar recipes), no model call.
const LIVE_URL = process.env.CS_LIVE_URL ?? "http://127.0.0.1:8770";
const ANALYSE_TIMEOUT_MS = 30_000;

export async function POST(request: Request) {
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return Response.json({ error: "invalid JSON" }, { status: 400 });
  }
  try {
    const r = await fetch(`${LIVE_URL}/api/analyse`, {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body),
      cache: "no-store", signal: AbortSignal.timeout(ANALYSE_TIMEOUT_MS),
    });
    return Response.json(await r.json(), { status: r.status, headers: { "Cache-Control": "no-store" } });
  } catch (e) {
    const timedOut = e instanceof DOMException && e.name === "TimeoutError";
    return Response.json({ status: "offline", error: timedOut ? "engine timed out" : "engine not running" },
      { status: timedOut ? 504 : 503, headers: { "Cache-Control": "no-store" } });
  }
}
