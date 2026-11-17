import type { Metadata } from "next";
import { CompareView } from "@/components/compare/CompareView";

export const metadata: Metadata = { title: "Compare" };

export default function ComparePage() {
  return (
    <div className="px-4 pt-4 pb-8 flex flex-col gap-4">
      <h1 className="h-display2">Compare · Tomato A–D</h1>
      <p className="prose-body text-ink-2">Four self-written recipes that differ by one ingredient each. The state at the final step, the route each reaches for vitamin C, and the answer.</p>
      <CompareView />
    </div>
  );
}
