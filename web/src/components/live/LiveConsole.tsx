"use client";
import { useEffect, useState } from "react";
import { Loader2, Play, Scale } from "lucide-react";
import { Note } from "@/components/Note";
import { SemChip } from "@/components/StateMark";
import { ContextDetails, EvidenceTable, PlainPanel, SystemPanel } from "./AnswerPanels";
import { CoveragePanel } from "./CoveragePanel";
import { PipelineStatus, WAITING_STAGES } from "./PipelineStatus";
import { DEFAULT_PRESET, PRESET_GROUPS, type Preset } from "./presets";
import { SimilarPanel } from "./SimilarPanel";
import type { Health, LiveResult, Stage } from "./types";

const TABS = [["answer", "Answer"], ["pipeline", "Pipeline"], ["state", "State & simulation"],
  ["evidence", "Evidence"], ["similar", "Similar recipes"]] as const;
type Tab = (typeof TABS)[number][0];

function HealthBadge({ health }: { health: Health }) {
  if (!health) return <SemChip sem="unknown-query">checking live server…</SemChip>;
  if (health.status === "ok") return <SemChip sem="match">LIVE · {health.model}</SemChip>;
  return <SemChip sem="error">Engine offline. Double-click LIVE_DEMO.command (starts engine + web)</SemChip>;
}

async function post(path: string, body: unknown): Promise<LiveResult> {
  const r = await fetch(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  const data = (await r.json()) as LiveResult;
  if (!r.ok) throw new Error(data.error ?? data.reason ?? `HTTP ${r.status}`);
  return data;
}

function Presets({ recipe, question, pick }: { recipe: string; question: string; pick: (p: Preset) => void }) {
  return (
    <div className="flex flex-col gap-2">
      {PRESET_GROUPS.map((g) => (
        <div key={g.group} className="flex flex-wrap items-center gap-1.5" role="group" aria-label={g.group}>
          <span className="label-sc w-28 shrink-0" title={g.hint}>{g.group}</span>
          {g.presets.map((p) => (
            <button key={p.label} type="button" className="btn" title={p.shows}
              aria-pressed={recipe === p.text && question === p.question} onClick={() => pick(p)}>{p.label}</button>
          ))}
        </div>
      ))}
    </div>
  );
}

function Tabs({ tab, setTab, ready }: { tab: Tab; setTab: (t: Tab) => void; ready: boolean }) {
  return (
    <div role="tablist" aria-label="Result views" className="flex flex-wrap gap-1 border-b border-line-2">
      {TABS.map(([id, label]) => (
        <button key={id} role="tab" type="button" aria-selected={tab === id} disabled={!ready && id !== "pipeline"}
          onClick={() => setTab(id)}
          className={`px-3 py-1.5 text-[14px] border-b-2 -mb-px ${tab === id ? "border-ink font-semibold text-ink" : "border-transparent text-ink-2"} disabled:opacity-40`}>
          {label}
        </button>
      ))}
    </div>
  );
}

export function LiveConsole() {
  const [health, setHealth] = useState<Health>(null);
  const [recipe, setRecipe] = useState(DEFAULT_PRESET.text);
  const [question, setQuestion] = useState(DEFAULT_PRESET.question);
  const [selfWritten, setSelfWritten] = useState(true);
  const [busy, setBusy] = useState(false);
  const [stages, setStages] = useState<Stage[] | null>(null);
  const [analysis, setAnalysis] = useState<LiveResult | null>(null);
  const [result, setResult] = useState<LiveResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [compare, setCompare] = useState(false);
  const [tab, setTab] = useState<Tab>("answer");

  useEffect(() => {
    let alive = true;
    const probe = () => fetch("/api/live", { cache: "no-store" }).then((r) => r.json())
      .then((h) => { if (alive) setHealth(h); })
      .catch(() => { if (alive) setHealth({ status: "offline" }); });
    probe();
    const id = setInterval(probe, 10_000);
    return () => { alive = false; clearInterval(id); };
  }, []);

  function pick(p: Preset) {
    setRecipe(p.text); setQuestion(p.question); setSelfWritten(true);
    setResult(null); setAnalysis(null); setStages(null); setError(null);
  }

  async function ask() {
    const body = { question, recipe_text: recipe, self_written: selfWritten };
    setBusy(true); setError(null); setResult(null); setAnalysis(null); setCompare(false); setTab("pipeline");
    setStages(WAITING_STAGES);
    try {
      const a = await post("/api/live/analyse", body);          // phase 1: engine only, ~0.1-1 s
      setAnalysis(a);
      setStages(a.pipeline.map((s) => (s.id === "model" && s.status === "pending" ? { ...s, status: "running", detail: "asking the model…" } : s)));
      const r = await post("/api/live", body);                  // phase 2: model + verifier
      setResult(r); setStages(r.pipeline); setTab("answer");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not reach the live server.");
      setStages((st) => st?.map((s) => (s.status === "running" ? { ...s, status: "error", detail: "failed" } : s)) ?? null);
    } finally {
      setBusy(false);
    }
  }

  const live = health?.status === "ok";
  const view = result ?? analysis;
  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap items-center gap-2"><HealthBadge health={health} /></div>

      <div className="panel p-4 flex flex-col gap-3">
        <Presets recipe={recipe} question={question} pick={pick} />
        <label className="flex flex-col gap-1">
          <span className="label-sc">Recipe</span>
          <textarea value={recipe} onChange={(e) => setRecipe(e.target.value)} rows={3} maxLength={6000}
            className="border border-line-2 bg-canvas p-2 text-[15px]" style={{ borderRadius: 4 }} />
        </label>
        <label className="flex flex-col gap-1">
          <span className="label-sc">Question</span>
          <input value={question} onChange={(e) => setQuestion(e.target.value)} maxLength={500}
            className="border border-line-2 bg-canvas p-2 text-[15px]" style={{ borderRadius: 4 }} />
        </label>
        <label className="flex items-start gap-2 text-[13px] text-ink-2">
          <input type="checkbox" checked={selfWritten} onChange={(e) => setSelfWritten(e.target.checked)} className="mt-0.5" />
          <span>I wrote this recipe text myself, or it is public. It will be sent to NVIDIA&apos;s hosted model. If unticked,
            nothing is sent and the system answers from its template only.</span>
        </label>
        <div className="flex flex-wrap gap-2">
          <button type="button" className="btn btn-solid" onClick={ask} disabled={!live || busy || !recipe.trim() || !question.trim()}>
            {busy ? <Loader2 size={14} className="animate-spin" aria-hidden="true" /> : <Play size={14} aria-hidden="true" />}
            <span>{busy ? "Running pipeline…" : "Ask live"}</span>
          </button>
          {result?.plain && (
            <button type="button" className="btn" aria-pressed={compare} onClick={() => { setCompare(!compare); setTab("answer"); }}>
              <Scale size={14} aria-hidden="true" /><span>{compare ? "Hide comparison" : "Compare with plain LLM"}</span>
            </button>
          )}
        </div>
      </div>

      {error && <SemChip sem="error">{error}</SemChip>}
      {stages && (
        <div className="flex flex-col gap-3">
          <Tabs tab={tab} setTab={setTab} ready={!!view} />
          {tab === "pipeline" && <PipelineStatus stages={stages} />}
          {tab === "answer" && (result ? (
            <div className={`grid gap-4 ${compare ? "md:grid-cols-2" : ""}`}>
              <SystemPanel r={result} />
              {compare && <PlainPanel r={result} />}
            </div>
          ) : <PipelineStatus stages={stages} />)}
          {tab === "state" && view && (
            <div className="panel p-4 flex flex-col gap-3"><CoveragePanel rows={view.coverage} /><ContextDetails r={view} /></div>
          )}
          {tab === "evidence" && view && <div className="panel p-4"><EvidenceTable r={view} /></div>}
          {tab === "similar" && view && <div className="panel p-4"><SimilarPanel similar={view.similar} /></div>}
        </div>
      )}

      <Note title="Reading this honestly">
        Live output, DIAGNOSTIC_ONLY, no gold. Both answers come from the same model at temperature 0; only the context
        differs. Nutrient questions: the verifier checks both answers against the same claim packet. It is a wording and
        number check, not a judge of truth. Cooking-fix questions: the advice is the model&apos;s own suggestion; the engine
        checks only that the state facts it cites are true. Similar recipes are matched by shared words; only public
        (Wikibooks, Gutenberg) recipes are shown or sent. Food-safety questions are refused.
      </Note>
    </div>
  );
}
