"use client";
import { useState } from "react";
import { CellView } from "@/components/CellView";
import { RouteChip } from "@/components/RouteChip";
import { SemChip } from "@/components/StateMark";
import { WhyRoute } from "@/components/WhyRoute";
import { fmt } from "@/lib/format";
import { claimFor, kindsOf, targetsOf } from "@/lib/lab";
import { BLOCKS, decodeCell, type ClaimPacket, type Manifest, type Scenario } from "@/lib/types";

const TABS = ["State", "Evidence", "Compatibility", "Claim packet", "Provenance"] as const;
type Tab = (typeof TABS)[number];

function List({ items, mono = true }: { items: string[]; mono?: boolean }) {
  if (items.length === 0) return <span className="caption">none</span>;
  return <ul className="flex flex-col gap-0.5">{items.map((x) => <li key={x} className={mono ? "mono break-all" : ""}>{x}</li>)}</ul>;
}

function compatSem(status: string) {
  if (status === "EVALUABLE") return null;
  if (status === "UNKNOWN") return "unknown-query" as const;
  if (status === "MISMATCH" || status === "INCOMPATIBLE") return "mismatch" as const;
  return "unknown-source" as const;
}

export function CompatTable({ p }: { p: ClaimPacket }) {
  return (
    <table className="tbl dense">
      <thead><tr><th>Axis</th><th>Status</th><th>Reason</th></tr></thead>
      <tbody>
        {Object.entries(p.compatibility).map(([k, c]) => {
          const sem = compatSem(c.status);
          return (
            <tr key={k}>
              <td><span className="mono block">{k}</span><span className="caption">{c.axis}{c.hard_exclusion ? " · hard exclusion" : ""}</span></td>
              <td>{sem ? <SemChip sem={sem}>{c.status}</SemChip> : <span className="chip st st-plain">{c.status}</span>}</td>
              <td className="mono break-all">{c.reason ?? "—"}</td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}

export function PacketView({ p }: { p: ClaimPacket }) {
  const rows: [string, React.ReactNode][] = [
    ["route", <RouteChip key="r" route={p.route} />],
    ["allowed_claims", <List key="a" items={p.allowed_claims} />],
    ["forbidden_claims", <List key="f" items={p.forbidden_claims} />],
    ["required_caveats", <List key="c" items={p.required_caveats} />],
    ["evidence_ids", <List key="e" items={p.evidence_ids} />],
    ["evidence_values", <List key="v" items={p.evidence_values} />],
    ["near_evidence_ids", <List key="n" items={p.near_evidence_ids} />],
    ["unknown_reasons", <List key="u" items={Object.entries(p.unknown_reasons).map(([k, v]) => `${k}: ${v}`)} />],
    ["max_allowed_precision", p.max_allowed_precision === null
      ? <CellView key="m" cell={{ kind: "unknown", reason: "NO_NUMBER_ALLOWED (null in packet)" }} />
      : <span key="m" className="tabular-nums">{p.max_allowed_precision}</span>],
    ["selected_axes", <span key="s" className="mono">{p.selected_axes.join(", ")}</span>],
  ];
  return (
    <table className="tbl dense"><tbody>
      {rows.map(([k, v]) => <tr key={k}><th scope="row" className="mono !font-normal w-[34%]">{k}</th><td>{v}</td></tr>)}
    </tbody></table>
  );
}

export function Inspector({ scenario, index, manifest }: { scenario: Scenario; index: number; manifest: Manifest | null }) {
  const [tab, setTab] = useState<Tab>("State");
  const targets = targetsOf(scenario);
  const kinds = kindsOf(scenario);
  const [target, setTarget] = useState(targets[0] ?? "");
  const [kind, setKind] = useState(kinds.includes("RETENTION_NUMERIC") ? "RETENTION_NUMERIC" : kinds[0] ?? "");
  const state = scenario.states[index];
  const claim = claimFor(scenario, index, target, kind);

  return (
    <div className="flex flex-col gap-2">
      <div role="tablist" aria-label="Inspector" className="flex flex-wrap gap-1">
        {TABS.map((t) => (
          <button key={t} role="tab" type="button" aria-selected={tab === t} className="btn !min-h-7 !px-2" onClick={() => setTab(t)}>{t}</button>
        ))}
      </div>
      {tab !== "State" && tab !== "Provenance" && (
        <div className="flex flex-wrap gap-2 items-center text-[13px]">
          <label>target <select className="btn !min-h-7" value={target} onChange={(e) => setTarget(e.target.value)}>{targets.map((t) => <option key={t}>{t}</option>)}</select></label>
          <label>question kind <select className="btn !min-h-7" value={kind} onChange={(e) => setKind(e.target.value)}>{kinds.map((t) => <option key={t}>{t}</option>)}</select></label>
          <span className="caption">step {state.step}</span>
        </div>
      )}
      <div role="tabpanel" aria-label={tab} className="min-w-0">
        {tab === "State" && (
          <div className="flex flex-col gap-2">
            <p className="caption">Every cell with its basis (<span className="mono">b</span>) or its UNKNOWN reason (<span className="mono">u</span>). Step {state.step}, {state.action}, {state.food} <span className="mono">{state.food_id}</span>.</p>
            {BLOCKS.map((b) => (
              <table key={b} className="tbl dense">
                <thead><tr><th colSpan={2}>{b}</th></tr></thead>
                <tbody>{Object.entries(state[b]).map(([f, c]) => (
                  <tr key={f}><td className="mono w-[36%]">{f}</td><td><CellView cell={decodeCell(c)} showBasis /></td></tr>
                ))}</tbody>
              </table>
            ))}
          </div>
        )}
        {tab === "Evidence" && (claim ? (
          <div className="flex flex-col gap-2">
            <RouteChip route={claim.packet.route} />
            <table className="tbl dense">
              <thead><tr><th>Evidence id</th><th>Value</th><th>Source family</th></tr></thead>
              <tbody>
                {claim.packet.evidence_ids.length === 0 && claim.packet.near_evidence_ids.length === 0 && (
                  <tr><td colSpan={3}><CellView cell={{ kind: "unknown", reason: "NO_EVIDENCE_ID_IN_PACKET" }} /></td></tr>
                )}
                {claim.packet.evidence_ids.map((id) => (
                  <tr key={id}>
                    <td><SemChip sem="match">{id}</SemChip></td>
                    <td className="tabular-nums">{claim.packet.evidence_values.find((v) => v.startsWith(`${id}=`))?.slice(id.length + 1) ?? "—"}</td>
                    <td className="mono">{manifest?.evidence_sources[id]?.source_family_id ?? "not listed in manifest"}</td>
                  </tr>
                ))}
                {claim.packet.near_evidence_ids.map((id) => (
                  <tr key={id}>
                    <td><SemChip sem="mismatch">{id} · near, not transferable</SemChip></td>
                    <td className="caption">number not transferred to this context</td>
                    <td className="mono">{manifest?.evidence_sources[id]?.source_family_id ?? "not listed in manifest"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : <p className="caption">No claim packet for this target and kind at this step.</p>)}
        {tab === "Compatibility" && (claim ? <CompatTable p={claim.packet} /> : <p className="caption">No claim packet for this target and kind at this step.</p>)}
        {tab === "Claim packet" && (claim ? (
          <div className="flex flex-col gap-3">
            <WhyRoute state={state} target={target} />
            <PacketView p={claim.packet} />
            <div>
              <h4 className="label-sc">Template answer</h4>
              <p className="text-[13px]">{claim.template_answer}</p>
              <p className="caption">Verifier on template answer: {claim.verifier.ok ? "no violation" : claim.verifier.codes.join(", ")}</p>
            </div>
          </div>
        ) : <p className="caption">No claim packet for this target and kind at this step.</p>)}
        {tab === "Provenance" && (
          <table className="tbl dense"><tbody>
            {[
              ...Object.entries(scenario.graph.provenance).map(([k, v]) => [`graph.provenance.${k}`, fmt(v)]),
              ["graph.diagnostics", scenario.graph.diagnostics.join(", ") || "none"],
              ["recipe_sha256", scenario.recipe_sha256],
              ["scenario labels", scenario.labels.join(", ")],
              ...(manifest ? [["manifest.builder_version", manifest.builder_version], ["manifest.git_head", manifest.git_head], ["manifest.generated_at", manifest.generated_at],
                ["manifest.rung_config", fmt(manifest.rung_config)]] : []),
              ...(scenario.vnext_comparison ? [["vnext_comparison", fmt(scenario.vnext_comparison)]] : []),
            ].map(([k, v]) => <tr key={k}><th scope="row" className="mono !font-normal w-[40%] break-all">{k}</th><td className="mono break-all">{v}</td></tr>)}
          </tbody></table>
        )}
      </div>
    </div>
  );
}
