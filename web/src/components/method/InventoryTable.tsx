"use client";
import { ChevronDown, ChevronRight } from "lucide-react";
import { Fragment, useState } from "react";
import { CellView } from "@/components/CellView";
import { clean, extraKeys, invValue, MAIN_COLS, SHORT, statusOf, STATUSES } from "@/lib/inventory";
import { useInventory } from "@/lib/snapshot";
import type { InventoryRow, Json } from "@/lib/types";

function V({ v }: { v: Json | undefined }) {
  const x = invValue(v);
  return x.kind === "unknown" ? <CellView cell={{ kind: "unknown", reason: x.reason }} /> : <span className="break-words">{x.text}</span>;
}

function Status({ r }: { r: InventoryRow }) {
  const s = statusOf(r);
  const style = s === "BUILT" ? "border-solid" : s === "PARTIAL" ? "border-dashed" : "border-dotted";
  return (
    <span className="flex flex-col gap-0.5">
      <span className={`chip border-2 ${style} border-line-3 mono w-fit`}>{s}</span>
      <span className="caption">{clean(r.Label)}</span>
    </span>
  );
}

function Group({ title, rows }: { title: string; rows: InventoryRow[] }) {
  const [open, setOpen] = useState<Set<number>>(new Set());
  const toggle = (n: number) => setOpen((o) => { const x = new Set(o); if (x.has(n)) x.delete(n); else x.add(n); return x; });
  return (
    <section aria-label={title} className="flex flex-col gap-1">
      <h3 className="h-section">{title} <span className="caption">({rows.length})</span></h3>
      <div className="overflow-x-auto">
        <table className="tbl min-w-[900px]">
          <thead><tr><th className="w-8">#</th>{MAIN_COLS.map((c) => <th key={c}>{SHORT[c] ?? c}</th>)}</tr></thead>
          <tbody>
            {rows.length === 0 && <tr><td colSpan={6} className="caption">No component matches the filter.</td></tr>}
            {rows.map((r) => (
              <Fragment key={r.n}>
                <tr id={`inv-${r.n}`} className="scroll-mt-24 target:bg-s3">
                  <td className="tabular-nums">{r.n}</td>
                  <td>
                    <button type="button" onClick={() => toggle(r.n)} aria-expanded={open.has(r.n)} className="flex items-start gap-1 text-left font-semibold">
                      {open.has(r.n) ? <ChevronDown size={14} aria-hidden="true" className="mt-0.5 shrink-0" /> : <ChevronRight size={14} aria-hidden="true" className="mt-0.5 shrink-0" />}
                      {clean(r.Component)}
                    </button>
                  </td>
                  <td><Status r={r} /></td>
                  <td><V v={r["Input → internal processing → output"]} /></td>
                  <td><V v={r["Current result (source)"]} /></td>
                  <td><V v={r.Limitation} /></td>
                </tr>
                {open.has(r.n) && (
                  <tr className="bg-s1">
                    <td />
                    <td colSpan={5}>
                      <dl className="grid gap-x-4 gap-y-1 md:grid-cols-[200px_1fr] text-[13px]">
                        {extraKeys(r).map((k) => (
                          <Fragment key={k}><dt className="text-ink-2 font-semibold">{k}</dt><dd><V v={r[k]} /></dd></Fragment>
                        ))}
                        <dt className="text-ink-2 font-semibold">Runs live in this demo</dt><dd>{r.in_live_demo ? "yes" : "no"}</dd>
                      </dl>
                    </td>
                  </tr>
                )}
              </Fragment>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}

export function InventoryTable() {
  const inv = useInventory();
  const [q, setQ] = useState("");
  const [status, setStatus] = useState<string>("ALL");
  if (inv.status === "loading") return <p role="status" className="caption">Loading component inventory…</p>;
  if (inv.status === "failed") return <p role="status">Component inventory could not be loaded: <span className="mono">{inv.error}</span></p>;
  const needle = q.trim().toLowerCase();
  const rows = inv.data.components.filter((r) =>
    (status === "ALL" || statusOf(r) === status) && (!needle || JSON.stringify(r).toLowerCase().includes(needle)));
  return (
    <div className="flex flex-col gap-4">
      <p className="caption">
        {inv.data.components.length} components from <span className="mono">{inv.data.source}</span> (sha256 <span className="mono">{inv.data.source_sha256.slice(0, 12)}…</span>) · {inv.data.labels.join(" · ")}. {inv.data.note}
      </p>
      <div className="flex flex-wrap items-center gap-3 text-[13px]">
        <label className="flex items-center gap-1.5">Filter
          <input type="search" value={q} onChange={(e) => setQ(e.target.value)} placeholder="component, result, limitation…" className="btn !cursor-text w-64" />
        </label>
        <label className="flex items-center gap-1.5">Status
          <select value={status} onChange={(e) => setStatus(e.target.value)} className="btn">
            <option value="ALL">all</option>{STATUSES.map((s) => <option key={s}>{s}</option>)}
          </select>
        </label>
        <span className="caption">Status chip border: solid = BUILT, dashed = PARTIAL, dotted = planned / cut / deferred. Click a component to expand all fields.</span>
      </div>
      <Group title="Runs live in this demo" rows={rows.filter((r) => r.in_live_demo)} />
      <Group title="Offline and corpus-scale work" rows={rows.filter((r) => !r.in_live_demo)} />
    </div>
  );
}
