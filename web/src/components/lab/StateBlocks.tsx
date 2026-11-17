"use client";
import { motion, useReducedMotion } from "motion/react";
import { useMemo, useState } from "react";
import { CellView } from "@/components/CellView";
import { BLOCKS, BLOCK_NAMES, decodeCell, type Delta, type RawState, type Transition } from "@/lib/types";
import { DELTA_ORDER, DeltaChip } from "./DeltaChip";

type Row = { field: string; delta?: Delta; present: boolean };

export function StateBlocks({ state, index, transition }: { state: RawState; index: number; transition?: Transition }) {
  const reduce = useReducedMotion();
  const [onlyDelta, setOnlyDelta] = useState(false);
  const deltas = useMemo(() => new Map((transition?.deltas ?? []).map((d) => [`${d.block}.${d.field}`, d])), [transition]);
  const counts = useMemo(() => {
    const c = new Map<string, number>();
    for (const d of transition?.deltas ?? []) c.set(d.kind, (c.get(d.kind) ?? 0) + 1);
    return c;
  }, [transition]);

  return (
    <div className="flex flex-col gap-3">
      <div className="flex flex-wrap items-center gap-2" role="status" aria-live="polite">
        <h2 className="label-sc">Delta from previous step</h2>
        {!transition && <span className="caption">No earlier state for this lot in the snapshot — nothing to compare against.</span>}
        {transition && <span className="caption">step {transition.from_step} → step {transition.to_step}</span>}
        {transition && DELTA_ORDER.filter((k) => counts.has(k)).map((k) => <DeltaChip key={k} kind={k} count={counts.get(k)} />)}
        {transition && transition.deltas.length === 0 && <span className="caption">no field differs</span>}
        {transition && (
          <button type="button" className="btn ml-auto" aria-pressed={onlyDelta} onClick={() => setOnlyDelta((v) => !v)}>
            Only fields that differ
          </button>
        )}
      </div>
      {BLOCKS.map((b) => {
        const present = Object.keys(state[b] ?? {});
        const removed = [...deltas.values()].filter((d) => d.block === b && !present.includes(d.field)).map((d) => d.field);
        const rows: Row[] = [
          ...present.map((field) => ({ field, delta: deltas.get(`${b}.${field}`), present: true })),
          ...removed.map((field) => ({ field, delta: deltas.get(`${b}.${field}`), present: false })),
        ].filter((r) => !onlyDelta || r.delta);
        return (
          <section key={b} aria-label={BLOCK_NAMES[b]}>
            <h3 className="h-section !text-[15px] mb-0.5">{BLOCK_NAMES[b]}</h3>
            <table className="tbl dense">
              <thead><tr><th className="w-[30%]">Field</th><th>Value at this step</th><th className="w-[36%]">Delta</th></tr></thead>
              <tbody>
                {rows.length === 0 && <tr><td colSpan={3} className="caption">No field in this block differs from the previous step.</td></tr>}
                {rows.map((r) => (
                  <tr key={r.field} className={r.delta ? "row-delta" : undefined}>
                    <td className="mono">{r.field}</td>
                    <td>{r.present ? <CellView cell={decodeCell(state[b][r.field])} /> : <span className="caption">not present at this step</span>}</td>
                    <td>
                      {r.delta ? (
                        <motion.div key={`${index}-${r.field}`} initial={reduce ? false : { opacity: 0, x: -6 }} animate={{ opacity: 1, x: 0 }}
                          transition={{ duration: 0.2, ease: [0.2, 0, 0, 1] }} className="flex flex-col items-start gap-0.5">
                          <DeltaChip kind={r.delta.kind} />
                          <span className="was">was: <CellView cell={decodeCell(r.delta.before)} /></span>
                        </motion.div>
                      ) : <span className="caption" aria-label="unchanged">unchanged</span>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        );
      })}
    </div>
  );
}
