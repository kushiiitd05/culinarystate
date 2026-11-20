"use client";
import { RouteChip } from "@/components/RouteChip";
import { SemChip } from "@/components/StateMark";
import type { Verifier } from "@/lib/types";
import type { Citation, LiveResult } from "./types";

const show = (v: unknown) => (Array.isArray(v) ? v.join(", ") : v === true ? "true" : v === false ? "false" : String(v));
const pct = (w: string, lead: string) => `${w.replace("UNSOURCED_PERCENT: ", lead)}%`;

function VerdictChip({ check, label }: { check: Verifier | null | undefined; label: string }) {
  if (!check) return null;
  return check.ok ? <SemChip sem="match">{label}: passes</SemChip>
    : <SemChip sem="error">{label}: {check.codes.join(", ")}</SemChip>;
}

function CitationList({ rows }: { rows: Citation[] }) {
  if (rows.length === 0) return <p className="caption">The model cited no state facts.</p>;
  const ok = rows.filter((c) => c.ok).length;
  return (
    <div>
      <p className="label-sc">Citations checked against the engine&apos;s state · {ok}/{rows.length} match</p>
      <ul className="mt-1 flex flex-col gap-1 text-[13px]">
        {rows.map((c, i) => (
          <li key={i} className="flex flex-wrap items-center gap-2">
            {c.ok ? <SemChip sem="match">✓ matches</SemChip> : <SemChip sem="error">✗ wrong</SemChip>}
            <span className="mono">step {c.step}: {c.field} = {c.claimed}</span>
            {!c.ok && <span className="text-ink-3">engine says <span className="mono">{c.actual}</span></span>}
          </li>
        ))}
      </ul>
    </div>
  );
}

export function ContextDetails({ r }: { r: LiveResult }) {
  const w = r.context?.where_you_are;
  return (
    <div className="flex flex-col gap-2 text-[13px]">
      {w && <p className="mono">where you are: {w.food} · step {w.current_step} of {w.total_steps} ({w.action}) ·
        hot water {w.hot_aqueous_minutes_so_far ?? "?"} min · hot fat {w.hot_fat_minutes_so_far ?? "?"} min</p>}
      {(r.context?.changes ?? []).map((c, i) => (
        <p key={`${i}-${c.from_step}-${c.to_step}`} className="mono">step {c.from_step}→{c.to_step}: {c.changes.map((d) =>
          `${d.field} ${show(d.before)} → ${show(d.after)}`).join(" · ")}</p>
      ))}
    </div>
  );
}

export function EvidenceTable({ r }: { r: LiveResult }) {
  if (r.evidence.length === 0) {
    return <p className="caption">{r.mode === "NUTRIENT" ? "No evidence row applies to this context, so no number is given."
      : "Evidence rows apply to nutrient questions; this question used the state trace instead."}</p>;
  }
  return (
    <table className="tbl dense"><thead><tr><th>Row</th><th>Use</th><th>Food · process</th><th>Source</th><th>Tier</th></tr></thead>
      <tbody>{r.evidence.map((e) => (
        <tr key={`${e.role}-${e.id}`}>
          <td className="mono">{e.id}</td>
          <td>{e.role === "applied" ? <SemChip sem="match">applied</SemChip> : <SemChip sem="mismatch">near · not transferred</SemChip>}</td>
          <td>{e.process?.raw_name ?? e.matrix?.raw_name ?? "—"}</td>
          <td className="mono">{e.source_family_id ?? "—"}</td>
          <td className="mono">{e.tier ?? "—"}</td>
        </tr>))}
      </tbody></table>
  );
}

export function SystemPanel({ r }: { r: LiveResult }) {
  const s = r.system;
  const advice = s.status === "STATE_AWARE_ADVICE";
  const nutrient = r.mode === "NUTRIENT";
  return (
    <section className="panel p-4 flex flex-col gap-3" aria-label="CulinaryState answer">
      <header className="flex flex-wrap items-center gap-2">
        <h2 className="h-section">CulinaryState {nutrient ? "(claim packet)" : "(state-aware)"}</h2>
        {nutrient && s.route ? <RouteChip route={s.route} />
          : advice ? <SemChip sem="ai">Suggested, unverified · grounded in recipe state</SemChip>
            : <SemChip sem="unknown-query">{s.status}</SemChip>}
      </header>
      <p className="prose-body whitespace-pre-line">{s.final}</p>
      <div className="flex flex-wrap gap-2">
        {s.draft_check && <VerdictChip check={s.draft_check} label="LLM draft" />}
        {nutrient && <SemChip sem={s.used_template ? "scenario" : "ai"}>{s.used_template ? "Shown: deterministic template" : "Shown: LLM draft, verified"}</SemChip>}
        {(s.warnings ?? []).map((w, i) => <SemChip key={`${i}-${w}`} sem="mismatch">{pct(w, "percentage not from the engine: ")}</SemChip>)}
        {s.draft_call?.status === "LLM_ERROR" && <SemChip sem="error">LLM error: {s.draft_call.reason}</SemChip>}
      </div>
      {s.used_template && s.draft && (
        <details className="text-[13px]"><summary className="cursor-pointer text-ink-2">Rejected LLM draft</summary>
          <p className="mt-1 line-through decoration-1 text-ink-3">{s.draft}</p></details>
      )}
      {advice && <CitationList rows={s.citations ?? []} />}
    </section>
  );
}

export function PlainPanel({ r }: { r: LiveResult }) {
  const p = r.plain;
  if (!p) return null;
  const unsourced = (p.claimed_numbers ?? []).filter((n) => !n.matches_packet_evidence_value);
  return (
    <section className="panel p-4 flex flex-col gap-3" aria-label="Plain LLM answer">
      <header className="flex flex-wrap items-center gap-2">
        <h2 className="h-section">Plain LLM, no evidence</h2>
        <SemChip sem="ai">{r.model}</SemChip>
      </header>
      {p.status === "OK" ? <p className="prose-body whitespace-pre-line">{p.text}</p> : <p className="prose-body text-ink-3">{p.status}: {p.reason}</p>}
      <div className="flex flex-wrap gap-2">
        <VerdictChip check={p.check} label="Same verifier" />
        {(p.warnings ?? []).map((w, i) => <SemChip key={`${i}-${w}`} sem="mismatch">{pct(w, "percentage with no source: ")}</SemChip>)}
        {r.mode === "ADVICE" && p.status === "OK" && <SemChip sem="unknown-query">no state, nothing to check citations against</SemChip>}
        {unsourced.length > 0 && <SemChip sem="mismatch">numbers with no evidence: {unsourced.map((n) => n.number).join(", ")}</SemChip>}
      </div>
      <p className="caption">Sees only the recipe text and the question: no state, no simulation, no evidence, no similar recipes.</p>
      {p.ms !== undefined && <p className="caption mono">LLM {p.ms} ms</p>}
    </section>
  );
}
