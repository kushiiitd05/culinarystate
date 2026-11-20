import { Note } from "@/components/Note";
import { RouteChip } from "@/components/RouteChip";
import { SemChip } from "@/components/StateMark";
import type { Question } from "@/lib/types";

export function HowToRead() {
  return (
    <Note title="How to read this">
      <ul className="list-disc pl-4 flex flex-col gap-0.5">
        <li>One model (<span className="mono">qwen2.5:7b-instruct</span>), one prompt, temperature 0, no system contract, no gold. This is a description of two outputs, not a score.</li>
        <li>On the 5 questions where the system routes DIRECT, the plain model gave no number and hedged, while the system stated the cited 95.0%. There the plain model was the more cautious side.</li>
        <li>The narrower finding: in 3 of 19 replies the plain model wrote an unsourced &ldquo;20-30%&rdquo;, once as lost and once as remaining.</li>
        <li>Two FORBIDDEN_NUMERIC_CLAIM verdicts are verifier false positives on durations (&ldquo;15-minute&rdquo;, &ldquo;10-15 minutes&rdquo;). REQUIRED_CAVEAT_MISSING is a wording check that fails some replies which do decline to quantify.</li>
      </ul>
      <p className="mt-1 caption">Source: <span className="mono">reports/s181/snapshot_findings.md</span></p>
    </Note>
  );
}

export function BaselinePanel({ q }: { q: Question }) {
  const b = q.baseline;
  return (
    <section aria-label={`Plain LLM versus CulinaryState: ${q.text}`} className="grid gap-3 md:grid-cols-2">
      <div className="border border-line-2 p-3 flex flex-col gap-2" style={{ borderRadius: 0 }}>
        <p className="label-sc">Plain LLM · <span className="mono">{b.arm}</span></p>
        <p className="caption"><span className="mono">{b.model}</span> · temperature {b.temperature} · {b.labels.join(" · ")}</p>
        <blockquote className="border-l-2 border-line-3 pl-3 text-[14px]">{b.text}</blockquote>
        <div>
          <p className="text-[13px] font-semibold">Numbers it asserted</p>
          {q.baseline_claimed_numbers.length === 0 ? <p className="caption">none detected by the verifier</p> : (
            <ul className="flex flex-col gap-1">
              {q.baseline_claimed_numbers.map((n, i) => (
                <li key={i} className="flex items-center gap-2 text-[13px]">
                  <span className="tabular-nums font-semibold">{n.number}</span>
                  {n.matches_packet_evidence_value ? <SemChip sem="match">matches packet evidence value</SemChip> : <SemChip sem="mismatch">no match to any packet evidence value</SemChip>}
                </li>
              ))}
            </ul>
          )}
        </div>
        <div className="text-[13px]">
          <span className="font-semibold">Claim verifier on this reply: </span>
          {q.baseline_check.ok ? "no violation" : q.baseline_check.violations.map((v) => <span key={v.code} className="block"><span className="mono">{v.code}</span> — {v.detail}</span>)}
        </div>
      </div>
      <div className="border border-line-2 p-3 flex flex-col gap-2" style={{ borderRadius: 0 }}>
        <p className="label-sc">CulinaryState</p>
        <RouteChip route={q.system.route} />
        <p className="text-[14px]">{q.system.answer}</p>
        <p className="text-[13px]">Evidence ids: {q.system.evidence_ids.length ? <span className="mono">{q.system.evidence_ids.join(", ")}</span> : <span className="caption">none (abstains)</span>}</p>
        <p className="text-[13px]">Claim verifier on this answer: {q.system.verifier.ok ? "no violation" : q.system.verifier.codes.join(", ")}</p>
      </div>
    </section>
  );
}
