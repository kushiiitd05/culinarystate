// Import only from server code (layout, pages, route handlers). In a browser bundle the variable is
// undefined, so the flag can only ever fail closed there.
//
// The live console needs the Python engine on the presenter's Mac (127.0.0.1:8770). A public build
// (Vercel) has no engine, so /live, its API routes and its nav link exist only when this server-side
// flag is set. It is deliberately not NEXT_PUBLIC_: the decision is made on the server and never
// shipped to the browser. tools/live_demo.sh sets CS_LIVE_ENABLED=1.
export function liveEnabled(): boolean {
  return process.env.CS_LIVE_ENABLED === "1";
}

export function liveDisabledResponse(): Response {
  return Response.json({ error: "not found" }, { status: 404, headers: { "Cache-Control": "no-store" } });
}
