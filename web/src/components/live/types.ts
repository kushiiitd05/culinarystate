import type { Route, Verifier } from "@/lib/types";
import type { CoverageRow } from "./CoveragePanel";

export type Health = { status: string; model?: string; reason?: string } | null;
export type EvidenceCard = {
  id: string; role: "applied" | "near"; source_family_id: string | null; source_id: string | null;
  matrix?: { raw_name?: string } | null; process?: { raw_name?: string } | null; target?: { raw_name?: string } | null;
  tier?: string | null; design?: string | null;
};
export type TraceStep = { step: number | null; action: string | null; food: string; known: Record<string, unknown>; unknown: Record<string, string> };
export type Citation = { step: number; field: string; claimed: string; actual: string; ok: boolean };
export type AdviceContext = {
  where_you_are: { food: string; current_step: number | null; action: string | null; total_steps: number;
    hot_aqueous_minutes_so_far: number | null; hot_fat_minutes_so_far: number | null };
  changes: { from_step: number; to_step: number; changes: { field: string; kind: string; before: unknown; after: unknown }[] }[];
};
export type Stage = { id: string; label: string; status: "done" | "pending" | "skipped" | "error" | "running"; detail: string; ms: number | null };
export type HeatStep = {
  step: number; action: string; food: string; process: string; family: string | null; medium: string | null;
  duration_min: string | number | null; temperature_C: string | number | null; lid_state: string | null;
  food_T_typical_C: number | null; thermal_dose_typical_min: number | null;
};
export type Similar = {
  search: {
    query_foods: string[]; query_processes: string[]; counts: Record<string, number>; searched: number; min_score: number;
    shown: { id: string; family: string; title: string; score: number; url: string | null; licence: string; steps_available: boolean }[];
  };
  reference: { id: string; title: string; url: string | null; licence: string; heat_steps: HeatStep[]; same_process: boolean } | null;
} | null;
export type LiveResult = {
  model: string;
  mode: "NUTRIENT" | "ADVICE" | "SAFETY";
  trace: TraceStep[];
  coverage: CoverageRow[];
  context: AdviceContext | null;
  parsed: { target: string | null; question_kind: string; food: string | null; foods: string[] };
  states: { index: number; food: string; step: number | null; action: string | null }[];
  evidence: EvidenceCard[];
  similar: Similar;
  pipeline: Stage[];
  system: {
    status: string; route: Route | null; final: string; draft: string | null; draft_check: Verifier | null;
    used_template: boolean; draft_call?: { status: string; reason?: string; ms: number };
    label?: string; warnings?: string[]; citations?: Citation[];
  };
  plain: {
    status: string; text?: string; reason?: string; ms?: number; check?: Verifier; warnings?: string[];
    claimed_numbers?: { number: string; matches_packet_evidence_value: boolean }[];
  } | null;
  timing_ms: { pipeline: number; similar?: number; total: number };
  error?: string; reason?: string;
};
