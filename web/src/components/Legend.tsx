import type { Sem } from "@/lib/types";
import { SemChip } from "./StateMark";

const ORDER: Sem[] = ["match", "mismatch", "unknown-source", "unknown-query", "scenario", "ai", "error"];

// Persistent legend: all seven glyph + marker + label triples, always on screen.
export function Legend() {
  return (
    <footer aria-label="Legend of epistemic states" className="border-t border-line-2 bg-s1 px-4 py-2 flex flex-wrap items-center gap-x-3 gap-y-1.5">
      <span className="label-sc">Legend</span>
      {ORDER.map((s) => <SemChip key={s} sem={s} />)}
      <span className="chip st st-nomarker"><span className="marker" aria-hidden="true">·</span>No marker found (not confirmed absent)</span>
    </footer>
  );
}
