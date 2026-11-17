import type { InventoryRow, Json } from "./types";

export const MAIN_COLS = ["Component", "Label", "Input → internal processing → output", "Current result (source)", "Limitation"] as const;
export const SHORT: Record<string, string> = { "Input → internal processing → output": "What it does", "Current result (source)": "Current result (source)", Label: "Status" };
export const STATUSES = ["BUILT", "PARTIAL", "PLANNED_ONLY", "CUT", "DEFERRED"] as const;

// Strip markdown emphasis/code markers only; keep every word and source tag.
export const clean = (s: string) => s.replace(/\*\*/g, "").replace(/`/g, "");
export const statusOf = (r: InventoryRow) => {
  const t = clean(r.Label);
  return STATUSES.find((s) => t.startsWith(s)) ?? STATUSES.find((s) => t.includes(s)) ?? "OTHER";
};
export type InvValue = { kind: "text"; text: string } | { kind: "unknown"; reason: string };
export function invValue(v: Json | undefined): InvValue {
  if (v === undefined || v === null) return { kind: "unknown", reason: "NOT_GIVEN_IN_INVENTORY" };
  const s = typeof v === "string" ? v : JSON.stringify(v);
  if (s.trim() === "NOT_EVIDENCED") return { kind: "unknown", reason: "NOT_EVIDENCED" };
  return { kind: "text", text: clean(s) };
}
export const extraKeys = (r: InventoryRow) => Object.keys(r).filter((k) => !["n", "in_live_demo", ...MAIN_COLS].includes(k));
