import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { LiveConsole } from "@/components/live/LiveConsole";
import { liveEnabled } from "@/lib/liveFlag";

export const metadata: Metadata = { title: "Live" };
// Decide per request from the server environment, so a public build can never serve this page.
export const dynamic = "force-dynamic";

export default function LivePage() {
  if (!liveEnabled()) notFound();
  return (
    <div className="px-4 pt-4 pb-8 flex flex-col gap-4">
      <h1 className="h-display2">Live · ask the system</h1>
      <p className="prose-body text-ink-2">
        Type a recipe and a question. The same hosted model answers twice: once through CulinaryState
        (state, evidence, claim packet, verifier) and once on its own with no evidence.
      </p>
      <LiveConsole />
    </div>
  );
}
