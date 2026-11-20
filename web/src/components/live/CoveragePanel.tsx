"use client";
import { useState } from "react";
import { SemChip } from "@/components/StateMark";

export type CoverageCell = {
  field: string; group: "process" | "composition" | "conditions" | "simulation";
  status: "FILLED" | "NOT_APPLICABLE" | "UNKNOWN"; value: unknown; source: string | null;
};
export type CoverageRow = {
  step: number | null; action: string | null; food: string;
  counts: { FILLED: number; NOT_APPLICABLE: number; UNKNOWN: number }; cells: CoverageCell[];
};

const GROUPS = ["simulation", "conditions", "composition", "process"] as const;
const GROUP_LABEL: Record<(typeof GROUPS)[number], string> = {
  simulation: "Physics simulation (typical scenario)", conditions: "Cooking conditions from text",
  composition: "Composition", process: "Process & lineage",
};
const show = (v: unknown) => (Array.isArray(v) ? v.join(", ") : typeof v === "boolean" ? String(v) : String(v ?? ""));

function Bar({ counts }: { counts: CoverageRow["counts"] }) {
  const total = counts.FILLED + counts.NOT_APPLICABLE + counts.UNKNOWN || 1;
  const seg = (n: number, cls: string, label: string) => n > 0 && (
    <span className={`st ${cls} block h-full`} style={{ width: `${(100 * n) / total}%`, paddingLeft: 0 }} title={`${n} ${label}`} />
  );
  return (
    <span className="flex h-3 w-40 overflow-hidden border border-line-2" style={{ borderRadius: 2 }} aria-hidden="true">
      {seg(counts.FILLED, "st-match", "filled")}{seg(counts.NOT_APPLICABLE, "st-nomarker", "does not apply")}
      {seg(counts.UNKNOWN, "st-unknown-source", "unknown")}
    </span>
  );
}

function Cell({ c }: { c: CoverageCell }) {
  if (c.status === "FILLED") {
    return (
      <li className="flex flex-wrap items-baseline gap-1.5">
        <SemChip sem={c.group === "simulation" ? "scenario" : "match"}>{c.group === "simulation" ? "simulated" : "filled"}</SemChip>
        <span className="mono">{c.field} = {show(c.value)}</span>
        <span className="caption mono">{c.source}</span>
      </li>
    );
  }
  return (
    <li className="flex flex-wrap items-baseline gap-1.5 text-ink-3">
      {c.status === "NOT_APPLICABLE" ? <span className="chip st st-nomarker">does not apply</span>
        : <SemChip sem="unknown-source">unknown</SemChip>}
      <span className="mono">{c.field}</span><span className="caption mono">{c.source}</span>
    </li>
  );
}

export function CoveragePanel({ rows }: { rows: CoverageRow[] }) {
  const heat = rows.findIndex((r) => r.cells.some((c) => c.group === "simulation" && c.status === "FILLED"));
  const [open, setOpen] = useState<number>(heat >= 0 ? heat : rows.length - 1);
  if (rows.length === 0) return null;
  const row = rows[Math.min(open, rows.length - 1)];
  return (
    <div className="flex flex-col gap-2">
      <p className="label-sc">State the engine built · what is known, what does not apply, what is unknown and why</p>
      <ul className="flex flex-col gap-1">
        {rows.map((r, i) => (
          <li key={i}>
            <button type="button" className="btn w-full justify-start gap-3" aria-pressed={i === open} onClick={() => setOpen(i)}>
              <span className="mono w-56 shrink-0 text-left truncate">step {r.step} · {r.action} · {r.food}</span>
              <Bar counts={r.counts} />
              <span className="mono text-[12px]">{r.counts.FILLED} filled · {r.counts.NOT_APPLICABLE} n/a · {r.counts.UNKNOWN} unknown</span>
            </button>
          </li>
        ))}
      </ul>
      <div className="grid gap-3 md:grid-cols-2 text-[13px]">
        {GROUPS.map((g) => {
          const cells = row.cells.filter((c) => c.group === g);
          if (cells.length === 0) return null;
          return (
            <div key={g}>
              <p className="font-semibold">{GROUP_LABEL[g]}</p>
              <ul className="mt-1 flex flex-col gap-1">{cells.map((c) => <Cell key={c.field} c={c} />)}</ul>
            </div>
          );
        })}
      </div>
    </div>
  );
}
