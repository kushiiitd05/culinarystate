import { Asterisk, CircleCheck, CircleQuestionMark, CircleSlash, GitBranch, OctagonX, SquareDashed } from "lucide-react";
import type { ReactNode } from "react";
import type { Sem } from "@/lib/types";

// Design system §3: every state = glyph + text marker + border/bar/fill treatment.
export const SEM: Record<Sem, { Icon: typeof CircleCheck; marker: string; label: string; cls: string }> = {
  match: { Icon: CircleCheck, marker: "=", label: "Evidence applies", cls: "st-match" },
  mismatch: { Icon: CircleSlash, marker: "×", label: "Does not apply", cls: "st-mismatch" },
  "unknown-source": { Icon: SquareDashed, marker: "—", label: "Not stated in recipe", cls: "st-unknown-source" },
  "unknown-query": { Icon: CircleQuestionMark, marker: "?", label: "No evidence available", cls: "st-unknown-query" },
  scenario: { Icon: GitBranch, marker: "Δ", label: "Scenario value", cls: "st-scenario" },
  ai: { Icon: Asterisk, marker: "*", label: "Suggested, unverified", cls: "st-ai" },
  error: { Icon: OctagonX, marker: "!", label: "Validator rejected", cls: "st-error" },
};

export function SemChip({ sem, children, title }: { sem: Sem; children?: ReactNode; title?: string }) {
  const s = SEM[sem];
  return (
    <span className={`chip st ${s.cls}`} title={title}>
      <s.Icon size={12} aria-hidden="true" />
      <span className="marker" aria-hidden="true">{s.marker}</span>
      <span>{children ?? s.label}</span>
    </span>
  );
}

// "derived" is a route colour family in the token set but not one of the seven states;
// it is shown as a plain bordered chip with its own text.
export function DerivedChip({ children }: { children: ReactNode }) {
  return <span className="chip st st-derived"><span className="marker" aria-hidden="true">≈</span>{children}</span>;
}
