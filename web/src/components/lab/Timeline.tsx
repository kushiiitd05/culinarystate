import type { Scenario } from "@/lib/types";

export function Timeline({ scenario, index, onSelect }: { scenario: Scenario; index: number; onSelect: (i: number) => void }) {
  return (
    <div>
      <div className="flex items-baseline justify-between">
        <h2 className="label-sc">Step timeline</h2>
        <span className="caption">← → change step · {index + 1} of {scenario.states.length}</span>
      </div>
      <ol className="mt-1 flex gap-1 overflow-x-auto pb-1" aria-label="States in order">
        {scenario.states.map((st, i) => (
          <li key={i} className="shrink-0">
            <button type="button" onClick={() => onSelect(i)} aria-current={i === index ? "step" : undefined} aria-pressed={i === index} className="btn !items-start flex-col !gap-0 text-left">
              <span className="mono">step {st.step} · {st.event_id}</span>
              <span className="text-[13px]">{st.action} — {st.food}</span>
            </button>
          </li>
        ))}
      </ol>
    </div>
  );
}
