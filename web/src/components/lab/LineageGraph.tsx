"use client";
import { Background, Handle, Position, ReactFlow, type Edge, type Node, type NodeProps } from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { useMemo } from "react";
import { entityLabel } from "@/lib/lab";
import type { Scenario } from "@/lib/types";

type LgData = { title: string; sub: string; kind: "entity" | "event"; alt: boolean; active: boolean; dim: boolean };
type LgNode = Node<LgData, "lg">;

function LgNodeView({ data }: NodeProps<LgNode>) {
  const cls = ["lg-node", data.kind === "event" ? "ev" : "", data.alt ? "alt" : "", data.active ? "active" : "", data.dim ? "dim" : ""].join(" ");
  return (
    <div className={cls}>
      <Handle type="target" position={Position.Left} />
      <div className="mono font-semibold">{data.title}</div>
      <div className="break-words">{data.sub}</div>
      {data.active && <div className="caption">active step</div>}
      <Handle type="source" position={Position.Right} />
    </div>
  );
}
const nodeTypes = { lg: LgNodeView };

// Layout is computed ONCE per scenario: position encodes lineage and never changes with the step.
function layout(s: Scenario): { nodes: Omit<LgNode, "data">[]; meta: Map<string, Omit<LgData, "active" | "dim">>; edges: Edge[] } {
  const ents = new Map(s.graph.entities.map((e) => [e.entity_id, e]));
  const evs = new Map(s.graph.events.map((e) => [e.event_id, e]));
  const depth = new Map<string, number>();
  const dEnt = (id: string, seen: Set<string>): number => {
    if (depth.has(id)) return depth.get(id) as number;
    const e = ents.get(id);
    const d = e?.created_by_event_id && evs.has(e.created_by_event_id) && !seen.has(id) ? dEv(e.created_by_event_id, new Set(seen).add(id)) + 1 : 0;
    depth.set(id, d);
    return d;
  };
  const dEv = (id: string, seen: Set<string>): number => {
    if (depth.has(id)) return depth.get(id) as number;
    const ev = evs.get(id);
    const d = Math.max(0, ...(ev?.consumes ?? []).filter((c) => ents.has(c) && !seen.has(c)).map((c) => dEnt(c, new Set(seen).add(id)))) + 1;
    depth.set(id, d);
    return d;
  };
  s.graph.events.forEach((e) => dEv(e.event_id, new Set()));
  s.graph.entities.forEach((e) => dEnt(e.entity_id, new Set()));

  const rows = new Map<number, number>();
  const place = (id: string) => {
    const d = depth.get(id) ?? 0;
    const r = rows.get(d) ?? 0;
    rows.set(d, r + 1);
    return { x: d * 170, y: r * 80 };
  };
  const meta = new Map<string, Omit<LgData, "active" | "dim">>();
  const nodes: Omit<LgNode, "data">[] = [];
  for (const e of s.graph.entities) {
    meta.set(e.entity_id, { title: e.entity_id, sub: `${entityLabel(e) || e.entity_type} · ${e.lifecycle}`, kind: "entity", alt: false });
    nodes.push({ id: e.entity_id, type: "lg", position: place(e.entity_id), draggable: false });
  }
  for (const e of s.graph.events) {
    meta.set(e.event_id, { title: e.event_id, sub: (e.span?.texts ?? []).join(" ") || "event", kind: "event", alt: e.alternative_group !== null });
    nodes.push({ id: e.event_id, type: "lg", position: place(e.event_id), draggable: false });
  }
  const edges: Edge[] = s.graph.events.flatMap((e) => [
    ...e.consumes.filter((c) => ents.has(c)).map((c) => ({ id: `${c}>${e.event_id}`, source: c, target: e.event_id })),
    ...e.produces.filter((c) => ents.has(c)).map((c) => ({ id: `${e.event_id}>${c}`, source: e.event_id, target: c })),
    ...e.discards.filter((c) => ents.has(c)).map((c) => ({ id: `${e.event_id}x${c}`, source: e.event_id, target: c, style: { strokeDasharray: "4 3" } })),
  ]);
  return { nodes, meta, edges };
}

export function LineageGraph({ scenario, activeEventId, onPickEvent }: { scenario: Scenario; activeEventId: string; onPickEvent: (id: string) => void }) {
  const base = useMemo(() => layout(scenario), [scenario]);
  const active = scenario.graph.events.find((e) => e.event_id === activeEventId);
  const near = useMemo(() => new Set([activeEventId, ...(active?.consumes ?? []), ...(active?.produces ?? []), ...(active?.discards ?? [])]), [active, activeEventId]);
  const nodes: LgNode[] = useMemo(
    () => base.nodes.map((n) => ({ ...n, data: { ...(base.meta.get(n.id) as Omit<LgData, "active" | "dim">), active: n.id === activeEventId, dim: !near.has(n.id) } })),
    [base, activeEventId, near],
  );
  return (
    <section aria-label="Lot lineage graph">
      <div className="flex items-baseline justify-between">
        <h2 className="label-sc">Lot lineage</h2>
        <span className="caption">rounded = lot / intermediate · square = event · dashed square = alternative_group · dashed edge = discards · drag to pan</span>
      </div>
      <div className="mt-1 h-[300px] border border-line-2 bg-canvas" style={{ borderRadius: 0 }}>
        <ReactFlow nodes={nodes} edges={base.edges} nodeTypes={nodeTypes} fitView fitViewOptions={{ minZoom: 0.7, padding: 0.08 }} nodesDraggable={false} nodesConnectable={false}
          elementsSelectable={false} minZoom={0.3}
          onNodeClick={(_, n) => { if (n.data.kind === "event") onPickEvent(n.id); }}>
          <Background gap={24} size={1} color="var(--cs-border-subtle)" />
        </ReactFlow>
      </div>
      <details className="mt-1">
        <summary className="caption cursor-pointer">Show lineage as a table</summary>
        <table className="tbl dense">
          <thead><tr><th>Event</th><th>Text</th><th>Consumes</th><th>Produces</th><th>Discards</th></tr></thead>
          <tbody>
            {scenario.graph.events.map((e) => (
              <tr key={e.event_id} className={e.event_id === activeEventId ? "row-delta" : undefined}>
                <td className="mono">{e.event_id}{e.event_id === activeEventId ? " (active)" : ""}</td>
                <td>{(e.span?.texts ?? []).join(" ")}</td>
                <td className="mono">{e.consumes.join(", ") || "none"}</td>
                <td className="mono">{e.produces.join(", ") || "none"}</td>
                <td className="mono">{e.discards.join(", ") || "none"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </details>
    </section>
  );
}
