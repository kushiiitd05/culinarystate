import { SquareDashed } from "lucide-react";
import { fmt } from "@/lib/format";
import type { Cell } from "@/lib/types";

// Exhaustive over the Cell union: an unknown cell has no `value` to render.
export function CellView({ cell, showBasis = false }: { cell: Cell; showBasis?: boolean }) {
  switch (cell.kind) {
    case "known":
      return (
        <span className="st st-plain inline-block">
          <span className="st-val break-words">{fmt(cell.value)}</span>
          {showBasis && cell.basis && <span className="mono block text-ink-3 break-all">basis: {cell.basis}</span>}
        </span>
      );
    case "no_marker":
      return (
        <span className="st st-nomarker inline-block px-1.5" aria-label="No recognised marker found; not confirmed absent">
          <span className="marker" aria-hidden="true">·</span> no marker found
          <span className="caption"> (not confirmed absent)</span>
          {showBasis && cell.basis && <span className="mono block text-ink-3 break-all">basis: {cell.basis}</span>}
        </span>
      );
    case "unknown":
      return (
        <span className="st st-unknown-source inline-flex flex-wrap items-center gap-x-1.5 pr-1.5 py-px max-w-full" aria-label={`Unknown. Reason: ${cell.reason}`}>
          <SquareDashed size={12} aria-hidden="true" />
          <span className="marker" aria-hidden="true">—</span>
          <span className="font-medium">UNKNOWN</span>
          <span className="mono [overflow-wrap:anywhere]">{cell.reason}</span>
        </span>
      );
  }
}
