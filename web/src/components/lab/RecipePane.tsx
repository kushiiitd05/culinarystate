import { recipeSegments } from "@/lib/lab";
import type { Scenario } from "@/lib/types";

export function RecipePane({ scenario, activeEventId, onPickEvent }: {
  scenario: Scenario; activeEventId: string; onPickEvent: (eventId: string) => void;
}) {
  const segs = recipeSegments(scenario);
  return (
    <div className="flex flex-col gap-3">
      <h2 className="label-sc">Recipe text</h2>
      <p className="prose-body">
        {segs.map((s, i) =>
          s.eventId === null ? <span key={i}>{s.text}</span> : (
            <button key={i} type="button" onClick={() => onPickEvent(s.eventId as string)}
              aria-current={s.eventId === activeEventId ? "step" : undefined}
              className={s.eventId === activeEventId
                ? "font-semibold underline decoration-2 underline-offset-4 bg-s3 px-0.5"
                : "underline decoration-dotted underline-offset-4 cursor-pointer"}>
              {s.text}<sup className="mono ml-0.5">{s.eventId}</sup>
            </button>
          ))}
      </p>
      <p className="caption">Underlined spans are the text each event was compiled from. The active step is bold with a solid underline.</p>
      <h3 className="label-sc mt-2">Events</h3>
      <ol className="flex flex-col">
        {scenario.graph.events.map((e) => {
          const on = e.event_id === activeEventId;
          return (
            <li key={e.event_id}>
              <button type="button" onClick={() => onPickEvent(e.event_id)} aria-current={on ? "step" : undefined}
                className={`w-full text-left px-2 py-1.5 border-l-[3px] text-[13px] ${on ? "border-ink bg-s3 font-semibold" : "border-line-2"}`}>
                <span className="mono mr-2">{e.event_id}</span>
                {(e.span?.texts ?? []).join(" ") || "—"}
                {on && <span className="caption ml-2">active</span>}
                {e.alternative_group && <span className="mono block text-ink-3">alternative_group: {e.alternative_group}</span>}
              </button>
            </li>
          );
        })}
      </ol>
      <p className="caption">{scenario.teaches}</p>
      <p className="mono text-ink-3 break-all">{scenario.labels.join(" · ")}</p>
    </div>
  );
}
