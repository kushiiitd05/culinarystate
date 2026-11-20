import type { Metadata } from "next";
import { Suspense } from "react";
import { LabWorkbench } from "@/components/lab/LabWorkbench";

export const metadata: Metadata = { title: "Lab" };

export default function LabPage() {
  return <Suspense fallback={<p role="status" className="p-4 caption">Loading…</p>}><LabWorkbench /></Suspense>;
}
