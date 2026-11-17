"use client";
import { CellView } from "@/components/CellView";
import { clean, invValue } from "@/lib/inventory";
import { useInventory, useManifest } from "@/lib/snapshot";

// Figures are read from files, never typed in: inventory rows by number, plus the manifest.
const ROWS = [14, 1, 27];

export function LandingFigures() {
  const inv = useInventory();
  const m = useManifest();
  if (inv.status !== "ready") return <p role="status" className="caption">{inv.status === "failed" ? `Inventory not loaded: ${inv.error}` : "Loading figures…"}</p>;
  return (
    <div className="grid gap-3 md:grid-cols-3">
      {ROWS.map((n) => {
        const r = inv.data.components.find((c) => c.n === n);
        if (!r) return null;
        const v = invValue(r["Current result (source)"]);
        return (
          <figure key={n} className="border-t-2 border-ink pt-2 flex flex-col gap-1">
            <figcaption className="label-sc">{clean(r.Component)}</figcaption>
            <p className="mono text-ink-2">{clean(r.Label)}</p>
            {v.kind === "text" ? <p className="text-[15px] tabular-nums">{v.text}</p> : <CellView cell={{ kind: "unknown", reason: v.reason }} />}
            <p className="caption">source: <span className="mono">data/inventory.json</span> row {n} (status, current result) · tags as written</p>
          </figure>
        );
      })}
      {m.status === "ready" && (
        <p className="caption md:col-span-3">
          Snapshot: {m.data.scenarios.length} scenarios · builder <span className="mono">{m.data.builder_version}</span> · {m.data.labels.join(" · ")} (source: <span className="mono">snapshot/manifest.json</span>)
        </p>
      )}
    </div>
  );
}
