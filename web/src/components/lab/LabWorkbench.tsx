"use client";
import { useRouter, useSearchParams } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import { Note } from "@/components/Note";
import { transitionTo } from "@/lib/lab";
import { useManifest, useScenario } from "@/lib/snapshot";
import type { Scenario } from "@/lib/types";
import { Inspector } from "./Inspector";
import { LineageGraph } from "./LineageGraph";
import { QuestionBar } from "./QuestionBar";
import { RecipePane } from "./RecipePane";
import { StateBlocks } from "./StateBlocks";
import { Timeline } from "./Timeline";

function Workbench({ scenario, manifest }: { scenario: Scenario; manifest: ReturnType<typeof useManifest> }) {
  const [index, setIndex] = useState(scenario.states.length - 1);
  const [question, setQuestion] = useState<string | null>(null);
  const n = scenario.states.length;
  const state = scenario.states[index];

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const t = e.target as HTMLElement | null;
      if (t && (t.tagName === "SELECT" || t.tagName === "INPUT" || t.tagName === "TEXTAREA")) return;
      if (e.key === "ArrowLeft") { setIndex((i) => Math.max(0, i - 1)); e.preventDefault(); }
      if (e.key === "ArrowRight") { setIndex((i) => Math.min(n - 1, i + 1)); e.preventDefault(); }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [n]);

  const pickEvent = useCallback((eventId: string) => {
    const i = scenario.states.findIndex((s) => s.event_id === eventId);
    if (i >= 0) setIndex(i);
  }, [scenario]);

  return (
    <div className="flex flex-col gap-3 px-3 pb-3">
      {scenario.id === "cut-mixed" && (
        <Note title="Known limitation in this scenario">
          After the diced tomatoes join the sliced carrots, the engine reports the tomato&apos;s <span className="mono">Q.piece_size_class</span> as
          {" "}<span className="mono">SLICED</span> (the carrots&apos; cut). This is an engine quirk, kept visible on purpose; <span className="mono">cut-dice</span> is the clean single-food cut.
          Source: <span className="mono">reports/s181/snapshot_findings.md</span>.
        </Note>
      )}
      <div className="grid gap-4 lg:grid-cols-[minmax(220px,1fr)_minmax(0,2.3fr)_minmax(300px,1.4fr)]">
        <section className="panel p-4 min-w-0" aria-label="Recipe">
          <RecipePane scenario={scenario} activeEventId={state.event_id} onPickEvent={pickEvent} />
        </section>
        <section className="min-w-0 flex flex-col gap-4" aria-label="State">
          <Timeline scenario={scenario} index={index} onSelect={setIndex} />
          <LineageGraph scenario={scenario} activeEventId={state.event_id} onPickEvent={pickEvent} />
          <StateBlocks state={state} index={index} transition={transitionTo(scenario, index)} />
        </section>
        <section className="panel p-3 min-w-0 lg:max-h-[calc(100vh-140px)] lg:overflow-y-auto lg:sticky lg:top-20 self-start" aria-label="Inspector">
          <Inspector key={scenario.id} scenario={scenario} index={index} manifest={manifest.status === "ready" ? manifest.data : null} />
        </section>
      </div>
      <div className="sticky bottom-2 z-30"><QuestionBar scenario={scenario} selected={question} onSelect={setQuestion} /></div>
    </div>
  );
}

export function LabWorkbench() {
  const params = useSearchParams();
  const router = useRouter();
  const manifest = useManifest();
  const list = manifest.status === "ready" ? manifest.data.scenarios : [];
  const id = params.get("s") ?? "tomato-a";
  const sc = useScenario(id);

  return (
    <div className="flex flex-col gap-3 pt-4">
      <div className="px-3 flex flex-wrap items-center gap-2">
        <h1 className="h-display2 mr-3">Lab</h1>
        <nav aria-label="Scenarios" className="flex flex-wrap gap-1">
          {list.map((s) => (
            <button key={s.id} type="button" className="btn" aria-pressed={s.id === id} onClick={() => router.replace(`/lab?s=${s.id}`)}>{s.title}</button>
          ))}
        </nav>
      </div>
      {manifest.status === "failed" && <p role="status" className="px-3">Snapshot manifest could not be loaded: <span className="mono">{manifest.error}</span></p>}
      {sc.status === "loading" && <p role="status" className="px-3 caption">Loading scenario {id} from the snapshot…</p>}
      {sc.status === "failed" && <p role="status" className="px-3">Scenario <span className="mono">{id}</span> is not in the snapshot: <span className="mono">{sc.error}</span></p>}
      {sc.status === "ready" && <Workbench key={sc.data.id} scenario={sc.data} manifest={manifest} />}
    </div>
  );
}
