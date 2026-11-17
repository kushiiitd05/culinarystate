import type { Metadata } from "next";
import { LiveConsole } from "@/components/live/LiveConsole";

export const metadata: Metadata = { title: "Live" };

export default function LivePage() {
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
