"use client";
import Link from "next/link";
import { CellView } from "@/components/CellView";
import { RouteChip } from "@/components/RouteChip";
import { WhyRoute } from "@/components/WhyRoute";
import { sameJson } from "@/lib/format";
import { useScenarios } from "@/lib/snapshot";
import { BLOCKS, decodeCell, type Scenario } from "@/lib/types";
import { BaselinePanel, HowToRead } from "./BaselinePanel";

const IDS = ["tomato-a", "tomato-b", "tomato-c", "tomato-d"];
const finalState = (s: Scenario) => s.states[s.states.length - 1];

function DiffTable({ scs }: { scs: Scenario[] }) {
  const rows = BLOCKS.flatMap((b) => {
    const fields = [...new Set(scs.flatMap((s) => Object.keys(finalState(s)[b] ?? {})))];
    return fields.filter((f) => !scs.every((s) => sameJson(finalState(s)[b]?.[f], finalState(scs[0])[b]?.[f]))).map((f) => ({ b, f }));
  });
  return (
    <div className="overflow-x-auto">
      <table className="tbl dense min-w-[760px]">
        <thead><tr><th>Field (final step)</th>{scs.map((s) => <th key={s.id}>{s.title}</th>)}</tr></thead>
        <tbody>
          {rows.map(({ b, f }) => (
            <tr key={`${b}.${f}`}>
              <td className="mono">{b}.{f}</td>
              {scs.map((s) => <td key={s.id}><CellView cell={decodeCell(finalState(s)[b]?.[f])} /></td>)}
            </tr>
          ))}
        </tbody>
      </table>
      <p className="caption mt-1">{rows.length} fields differ across the four final states; fields identical in all four are omitted.</p>
    </div>
  );
}

export function CompareView() {
  const res = useScenarios(IDS);
  if (res.status === "loading") return <p role="status" className="caption">Loading Tomato A–D from the snapshot…</p>;
  if (res.status === "failed") return <p role="status">Snapshot scenarios could not be loaded: <span className="mono">{res.error}</span></p>;
  const scs = res.data;
  return (
    <div className="flex flex-col gap-8">
      <section aria-label="Recipes and vitamin C route">
        <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          {scs.map((s) => {
            const q = s.questions.find((x) => x.id === "vitc-retention");
            const st = q ? s.states[q.state_index] : finalState(s);
            return (
              <article key={s.id} className="panel p-3 flex flex-col gap-2 min-w-0">
                <h2 className="h-section">{s.title}</h2>
                <p className="text-[14px]">{s.recipe_text}</p>
                <Link href={`/lab?s=${s.id}`} className="caption underline">Open in Lab</Link>
                <p className="label-sc mt-1">Vitamin C route</p>
                {q ? <RouteChip route={q.system.route} /> : <span className="caption">no vitamin C question in this scenario</span>}
                {q && <p className="text-[13px]">{q.system.answer}</p>}
                <WhyRoute state={st} target="vitc" />
              </article>
            );
          })}
        </div>
      </section>
      <section aria-label="What differs in state">
        <h2 className="h-section mb-2">What differs in state at the final step</h2>
        <DiffTable scs={scs} />
      </section>
      <section aria-label="Plain LLM versus CulinaryState" className="flex flex-col gap-3">
        <div className="flex flex-wrap items-center gap-2">
          <h2 className="h-section">Plain LLM vs CulinaryState</h2>
          <span className="chip border border-line-3 mono">DIAGNOSTIC</span>
        </div>
        <HowToRead />
        {scs.map((s) => (
          <div key={s.id} className="flex flex-col gap-2">
            <h3 className="label-sc">{s.title}</h3>
            {s.questions.map((q) => (
              <div key={q.id}><p className="text-[13px] font-semibold mb-1">{q.text}</p><BaselinePanel q={q} /></div>
            ))}
          </div>
        ))}
      </section>
    </div>
  );
}
