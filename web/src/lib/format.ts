import type { Json } from "./types";

export function fmt(v: Json): string {
  if (v === null) return "null";
  if (typeof v === "boolean") return v ? "true" : "false";
  if (typeof v === "number" || typeof v === "string") return String(v);
  if (Array.isArray(v)) return v.length === 0 ? "[ ] (empty list)" : v.map(fmt).join(", ");
  const entries = Object.entries(v);
  return entries.length === 0 ? "{ } (empty)" : entries.map(([k, x]) => `${k}: ${fmt(x)}`).join(" · ");
}
export const sameJson = (a: unknown, b: unknown) => JSON.stringify(a) === JSON.stringify(b);
export const shortHash = (h: string | null | undefined) => (h ? `${h.slice(0, 12)}…` : "");
export const dateOnly = (iso: string) => iso.slice(0, 10);
