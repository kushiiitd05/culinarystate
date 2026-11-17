import type { Claim, GraphEntity, RawCell, RawState, Scenario, Transition } from "./types";

export const transitionTo = (s: Scenario, idx: number): Transition | undefined =>
  s.transitions.find((t) => t.to_state_index === idx);

export const claimFor = (s: Scenario, idx: number, target: string, kind: string): Claim | undefined =>
  s.claims.find((c) => c.state_index === idx && c.target === target && c.question_kind === kind);

export const targetsOf = (s: Scenario) => [...new Set(s.claims.map((c) => c.target))];
export const kindsOf = (s: Scenario) => [...new Set(s.claims.map((c) => c.question_kind))];

export function entityLabel(e: GraphEntity): string {
  const texts = e.span?.texts ?? e.attributes.flatMap((a) => a.span?.texts ?? []);
  return texts.length ? [...new Set(texts)].join(" ") : "";
}

// The fields the engine itself records as the cause of a route (shown verbatim).
export type WhyRouteFields = { label: string; path: string; cell: RawCell | undefined }[];
export function whyRouteFields(state: RawState, target: string): WhyRouteFields {
  return [
    { label: "Route cell", path: `Y.${target}_route`, cell: state.Y[`${target}_route`] },
    { label: "Frozen router reasons", path: `Y.${target}_frozen_reasons`, cell: state.Y[`${target}_frozen_reasons`] },
    { label: "Salt in context", path: "C.salt_present", cell: state.C.salt_present },
    { label: "Acid in context", path: "C.acid_present", cell: state.C.acid_present },
    { label: "Lipid in context", path: "C.lipid_present", cell: state.C.lipid_present },
  ];
}

export type Seg = { text: string; eventId: string | null };
export function recipeSegments(s: Scenario): Seg[] {
  const marks = s.graph.events
    .flatMap((e) => (e.span?.segments ?? []).map(([a, b]) => ({ a, b, id: e.event_id })))
    .sort((x, y) => x.a - y.a);
  const chars = Array.from(s.recipe_text); // offsets are code points
  const out: Seg[] = [];
  let pos = 0;
  for (const m of marks) {
    if (m.a < pos) continue;
    if (m.a > pos) out.push({ text: chars.slice(pos, m.a).join(""), eventId: null });
    out.push({ text: chars.slice(m.a, m.b).join(""), eventId: m.id });
    pos = m.b;
  }
  if (pos < chars.length) out.push({ text: chars.slice(pos).join(""), eventId: null });
  return out;
}
