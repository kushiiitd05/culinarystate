// Snapshot types. Cells are decoded into a discriminated union so that an
// UNKNOWN cell can never be rendered through the "known value" code path.
export type Json = string | number | boolean | null | Json[] | { [k: string]: Json };

export type RawCell = { v: Json; b?: string; u?: string };

export type Cell =
  | { kind: "known"; value: Exclude<Json, null>; basis: string }
  | { kind: "no_marker"; basis: string } // "NO_RECOGNIZED_MARKER": no marker found, NOT confirmed absence
  | { kind: "unknown"; reason: string };

export const NO_MARKER = "NO_RECOGNIZED_MARKER";

export function decodeCell(raw: RawCell | undefined | null): Cell {
  if (!raw || raw.v === null || raw.v === undefined) {
    return { kind: "unknown", reason: raw?.u ?? "REASON_NOT_STATED_IN_SNAPSHOT" };
  }
  if (raw.v === NO_MARKER) return { kind: "no_marker", basis: raw.b ?? "" };
  return { kind: "known", value: raw.v as Exclude<Json, null>, basis: raw.b ?? "" };
}

export const BLOCKS = ["G", "C", "Q", "Y"] as const;
export type Block = (typeof BLOCKS)[number];
export const BLOCK_NAMES: Record<Block, string> = {
  G: "G · graph / lineage",
  C: "C · composition context",
  Q: "Q · process quantities",
  Y: "Y · evidence and route",
};

export type RawState = {
  step: number; event_id: string; action: string; food: string; food_id: string;
} & Record<Block, Record<string, RawCell>>;

export type DeltaKind = "ADDED" | "CHANGED" | "REMOVED" | "BECAME_UNKNOWN" | "RESOLVED";
export type Delta = { block: Block; field: string; kind: DeltaKind; before?: RawCell | null; after?: RawCell | null };
export type Transition = {
  food_id: string; from_state_index: number; to_state_index: number; from_step: number; to_step: number; deltas: Delta[];
};

export type Route = "DIRECT" | "SCENARIO" | "QUALITATIVE" | "CONTEXT_MISMATCH" | "UNKNOWN";
export type CompatCell = { axis: string; status: string; reason: string | null; hard_exclusion?: boolean; owner_step?: string };
export type ClaimPacket = {
  route: Route; action: string; food: string; step: number; target: string; question_kind: string;
  allowed_claims: string[]; forbidden_claims: string[]; required_caveats: string[];
  evidence_ids: string[]; evidence_values: string[]; near_evidence_ids: string[];
  compatibility: Record<string, CompatCell>; unknown_reasons: Record<string, string>;
  max_allowed_precision: number | null; selected_axes: number[];
};
export type Verifier = { ok: boolean; codes: string[]; violations: { code: string; detail: string }[] };
export type Claim = {
  state_index: number; target: string; question_kind: string; packet: ClaimPacket; template_answer: string; verifier: Verifier;
};
export type ClaimedNumber = { number: string; decimals: number; matches_packet_evidence_value: boolean };
export type Question = {
  id: string; text: string; target: string; question_kind: string; food: string; state_index: number; lookup_key: string;
  system: { answer: string; route: Route; evidence_ids: string[]; near_evidence_ids: string[]; verifier: Verifier };
  baseline: { arm: string; model: string; prompt: string; temperature: number; text: string; labels: string[] };
  baseline_check: Verifier;
  baseline_claimed_numbers: ClaimedNumber[];
};
export type Span = { segments: [number, number][]; texts: string[] } | null;
export type GraphAttr = { field: string; value: Json; status: string; origin?: string; claim_route?: string; span?: Span };
export type GraphEntity = {
  entity_id: string; entity_type: string; lifecycle: string; parent_entity_ids: string[];
  created_by_event_id: string | null; attributes: GraphAttr[]; span: Span;
};
export type GraphEvent = {
  event_id: string; consumes: string[]; produces: string[]; discards: string[]; depends_on: string[];
  alternative_group: string | null; claim_route: string; order: number[]; attributes: GraphAttr[]; span: Span;
};
export type Scenario = {
  id: string; title: string; kind: string; teaches: string; labels: string[];
  recipe_text: string; recipe_sha256: string;
  states: RawState[]; transitions: Transition[]; claims: Claim[]; questions: Question[];
  graph: {
    entities: GraphEntity[]; events: GraphEvent[]; diagnostics: string[]; failure: Json;
    lot_accounting: Record<string, string>; provenance: Record<string, Json>; allocations: Json[];
  };
  vnext_comparison?: Record<string, Json>;
};
export type Manifest = {
  snapshot: string; builder_version: string; generated_at: string; git_head: string; labels: string[];
  scenarios: { id: string; title: string; kind: string; path: string; recipe_sha256: string }[];
  files: Record<string, { bytes: number; sha256: string }>;
  evidence_sources: Record<string, { source_family_id: string; source_ids: string[] }>;
  demo_mode: Record<string, Json>; rung_config: Record<string, Json>; inputs: Record<string, Json>;
};
export type InventoryRow = { n: number; Component: string; Label: string; in_live_demo: boolean } & Record<string, Json | undefined>;
export type Inventory = { source: string; source_sha256: string; labels: string[]; note: string; components: InventoryRow[] };

// The seven semantic states of the design system (§3).
export type Sem = "match" | "mismatch" | "unknown-source" | "unknown-query" | "scenario" | "ai" | "error";
export function routeSem(r: Route): Sem | "derived" {
  switch (r) {
    case "DIRECT": return "match";
    case "SCENARIO": return "scenario";
    case "QUALITATIVE": return "derived";
    case "CONTEXT_MISMATCH": return "mismatch";
    case "UNKNOWN": return "unknown-query";
  }
}
