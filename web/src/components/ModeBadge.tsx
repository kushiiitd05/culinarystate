"use client";
import { usePathname } from "next/navigation";
import { dateOnly } from "@/lib/format";
import { useManifest, useSignature } from "@/lib/snapshot";

// Persistent, non-dismissable. Every page is the signed snapshot except /live, which never fakes being recorded.
export function ModeBadge() {
  const live = usePathname() === "/live";
  const m = useManifest();
  const sig = useSignature();
  const date = m.status === "ready" ? dateOnly(m.data.generated_at) : m.status === "failed" ? "manifest not loaded" : "…";
  const sigText = sig === "checking" ? "checking" : sig;
  if (live) {
    return (
      <div role="status" className="mono inline-flex items-center gap-1.5 border border-line-3 bg-canvas px-2 py-1 text-ink" style={{ borderRadius: 2 }}>
        <span className="font-semibold">LIVE</span><span aria-hidden="true">·</span><span>answers generated now · not signed</span>
      </div>
    );
  }
  return (
    <div role="status" aria-live="polite" className="mono inline-flex items-center gap-1.5 border border-line-3 bg-canvas px-2 py-1 text-ink" style={{ borderRadius: 2 }}>
      <span className="font-semibold">PRECOMPUTED SNAPSHOT</span>
      <span aria-hidden="true">·</span><span>{date}</span>
      <span aria-hidden="true">·</span>
      <span>signature <span className={sig === "verified" ? "font-semibold" : "underline decoration-dashed"}>{sigText}</span></span>
    </div>
  );
}
