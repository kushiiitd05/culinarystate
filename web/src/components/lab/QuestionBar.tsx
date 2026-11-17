"use client";
import { CircleQuestionMark } from "lucide-react";
import { RouteChip } from "@/components/RouteChip";
import { SemChip } from "@/components/StateMark";
import { WhyRoute } from "@/components/WhyRoute";
import type { Question, Scenario } from "@/lib/types";

export function Answer({ q, scenario }: { q: Question; scenario: Scenario }) {
  const s = q.system;
  const abstain = s.route === "UNKNOWN" || s.evidence_ids.length === 0;
  const state = scenario.states[q.state_index];
  return (
    <div role="status" aria-live="polite" className="flex flex-col gap-2">
      <div className="flex flex-wrap items-center gap-2">
        <RouteChip route={s.route} />
        <span className="caption">answered from step {state?.step} · verifier on this answer: {s.verifier.ok ? "no violation" : s.verifier.codes.join(", ")}</span>
      </div>
      {abstain ? (
        <div className="st st-unknown-query p-3" style={{ borderRadius: 0 }}>
          <p className="flex items-center gap-1.5 font-semibold"><CircleQuestionMark size={14} aria-hidden="true" /> <span className="marker">?</span> Abstains — no number is stated</p>
          <p className="mt-1 text-ink">{s.answer}</p>
          {s.near_evidence_ids.length > 0 && <p className="mt-1 text-[13px]">Near evidence (not transferable): <span className="mono">{s.near_evidence_ids.join(", ")}</span></p>}
          {state && <div className="mt-2 text-ink"><WhyRoute state={state} target={q.target} /></div>}
        </div>
      ) : (
        <div className="st st-match p-3" style={{ borderRadius: 0 }}>
          <p className="text-ink">{s.answer}</p>
          <p className="mt-1 flex flex-wrap gap-1">{s.evidence_ids.map((id) => <SemChip key={id} sem="match">{id}</SemChip>)}</p>
        </div>
      )}
    </div>
  );
}

export function QuestionBar({ scenario, selected, onSelect }: { scenario: Scenario; selected: string | null; onSelect: (id: string | null) => void }) {
  const q = scenario.questions.find((x) => x.id === selected);
  return (
    <div className="glass p-3 flex flex-col gap-2 max-h-[46vh] overflow-y-auto">
      <div className="flex flex-wrap items-center gap-2">
        <span className="label-sc">Ask</span>
        {scenario.questions.map((x) => (
          <button key={x.id} type="button" className="btn" aria-pressed={x.id === selected} onClick={() => onSelect(x.id === selected ? null : x.id)}>{x.text}</button>
        ))}
      </div>
      {q && <Answer q={q} scenario={scenario} />}
    </div>
  );
}
