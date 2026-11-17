"use client";
import { dateOnly } from "@/lib/format";
import { useManifest, useSignature } from "@/lib/snapshot";

// Persistent, non-dismissable. This build is snapshot-only.
export function ModeBadge() {
  const m = useManifest();
  const sig = useSignature();
  const date = m.status === "ready" ? dateOnly(m.data.generated_at) : m.status === "failed" ? "manifest not loaded" : "…";
  const sigText = sig === "checking" ? "checking" : sig;
  return (
    <div role="status" aria-live="polite" className="mono inline-flex items-center gap-1.5 border border-line-3 bg-canvas px-2 py-1 text-ink" style={{ borderRadius: 2 }}>
      <span className="font-semibold">PRECOMPUTED SNAPSHOT</span>
      <span aria-hidden="true">·</span><span>{date}</span>
      <span aria-hidden="true">·</span>
      <span>signature <span className={sig === "verified" ? "font-semibold" : "underline decoration-dashed"}>{sigText}</span></span>
    </div>
  );
}
