"use client";
import { CircleCheck, CircleDashed, CircleMinus, CircleX, Loader2 } from "lucide-react";
import type { Stage } from "./types";

const ICON = {
  done: { Icon: CircleCheck, cls: "text-[var(--state-evidence-match-fg)]", word: "done" },
  running: { Icon: Loader2, cls: "animate-spin text-[var(--state-derived-fg)]", word: "running" },
  pending: { Icon: CircleDashed, cls: "text-ink-3", word: "waiting" },
  skipped: { Icon: CircleMinus, cls: "text-ink-3", word: "skipped" },
  error: { Icon: CircleX, cls: "text-[var(--state-error-fg)]", word: "error" },
} as const;

export const WAITING_STAGES: Stage[] = [
  ["parse", "Read recipe"], ["state", "Build state"], ["simulate", "Physics simulation"], ["evidence", "Evidence lookup"],
  ["similar", "Similar recipes"], ["model", "Ask model"], ["verify", "Verify"],
].map(([id, label], i) => ({ id, label, status: i === 0 ? "running" : "pending", detail: "", ms: null }));

/** Live status of the pipeline: each stage's real status and what it did, as reported by the engine. */
export function PipelineStatus({ stages }: { stages: Stage[] }) {
  return (
    <ol className="panel p-3 flex flex-col gap-1.5" aria-label="Pipeline status" aria-live="polite">
      {stages.map((s, i) => {
        const { Icon, cls, word } = ICON[s.status] ?? ICON.pending;
        return (
          <li key={s.id} className="grid grid-cols-[20px_150px_1fr_auto] items-start gap-2 text-[13px]">
            <Icon size={16} className={`mt-0.5 ${cls}`} aria-label={word} />
            <span className={s.status === "skipped" ? "text-ink-3" : "font-semibold"}>{i + 1}. {s.label}</span>
            <span className={s.status === "skipped" ? "text-ink-3" : "text-ink-2"}>{s.detail || (s.status === "running" ? "working…" : "")}</span>
            <span className="caption mono">{s.ms != null ? `${s.ms} ms` : ""}</span>
          </li>
        );
      })}
    </ol>
  );
}
