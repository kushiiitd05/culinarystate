import type { DeltaKind } from "@/lib/types";

export const DELTA: Record<DeltaKind, { marker: string; text: string; cls: string }> = {
  ADDED: { marker: "+", text: "added", cls: "dchip-added" },
  CHANGED: { marker: "~", text: "changed", cls: "dchip-changed" },
  REMOVED: { marker: "−", text: "removed", cls: "dchip-removed" },
  BECAME_UNKNOWN: { marker: "—", text: "became unknown", cls: "dchip-unknown" },
  RESOLVED: { marker: "→", text: "resolved (was unknown)", cls: "dchip-resolved" },
};
export const DELTA_ORDER: DeltaKind[] = ["ADDED", "CHANGED", "REMOVED", "BECAME_UNKNOWN", "RESOLVED"];

export function DeltaChip({ kind, count }: { kind: DeltaKind; count?: number }) {
  const d = DELTA[kind];
  return (
    <span className={`dchip ${d.cls}`}>
      <span className="marker" aria-hidden="true">{d.marker}</span>
      {d.text}{count !== undefined && <span className="tabular-nums"> {count}</span>}
    </span>
  );
}
