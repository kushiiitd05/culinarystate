import type { Metadata } from "next";
import { InventoryTable } from "@/components/method/InventoryTable";
import { Limitations } from "@/components/method/Limitations";
import { PipelineDiagram } from "@/components/method/PipelineDiagram";

export const metadata: Metadata = { title: "Method" };

export default function MethodPage() {
  return (
    <div className="px-4 pt-4 pb-10 flex flex-col gap-10 max-w-[1240px] mx-auto">
      <section className="flex flex-col gap-3">
        <h1 className="h-display2">Method</h1>
        <p className="prose-body text-ink-2">From recipe text to a typed event record, a lot-aware cooking state, and a claim packet that decides what may be said.</p>
        <PipelineDiagram />
      </section>
      <section aria-label="Everything behind this demo" className="flex flex-col gap-3">
        <h2 className="h-section">Everything behind this demo</h2>
        <InventoryTable />
      </section>
      <Limitations />
    </div>
  );
}
