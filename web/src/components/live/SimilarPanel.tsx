"use client";
import { SemChip } from "@/components/StateMark";
import type { Similar } from "./types";

const FAMILY: Record<string, { name: string; rule: string }> = {
  WIKIBOOKS: { name: "Wikibooks", rule: "public · shown and sent" },
  GUTENBERG_SEGMENT: { name: "Project Gutenberg", rule: "public domain · title shown" },
  FOODCOM: { name: "Food.com", rule: "local only · counted, never shown or sent" },
  A1_BBC_GOOD_FOOD: { name: "BBC Good Food", rule: "local only (D-003) · counted, never shown or sent" },
  TASTESET: { name: "TASTEset", rule: "local only · counted, never shown or sent" },
};
const fmt = (v: unknown): string => (v == null ? "—" : Array.isArray(v) ? v.map(fmt).join("–")
  : typeof v === "number" ? `${Math.round(v * 100) / 100}` : String(v));

export function SimilarPanel({ similar }: { similar: Similar }) {
  if (!similar) return <p className="caption">Similar-recipe index not loaded.</p>;
  const { search, reference } = similar;
  const total = Object.values(search.counts).reduce((a, b) => a + b, 0);
  return (
    <div className="flex flex-col gap-4 text-[14px]">
      <p className="text-ink-2">
        Searched all <b>{search.searched.toLocaleString()}</b> recipes on this machine for{" "}
        <span className="mono">{[...search.query_foods, ...search.query_processes].join(", ") || "the recipe text"}</span>.{" "}
        <b>{total.toLocaleString()}</b> are similar (shared food words, score ≥ {search.min_score}). Similar means shared
        words, not a judged equivalence.
      </p>
      <table className="tbl dense"><thead><tr><th>Corpus</th><th>Similar</th><th>What may leave this machine</th></tr></thead>
        <tbody>{Object.entries(search.counts).sort((a, b) => b[1] - a[1]).map(([fam, n]) => (
          <tr key={fam}><td>{FAMILY[fam]?.name ?? fam}</td><td className="mono">{n.toLocaleString()}</td>
            <td className="text-ink-3">{FAMILY[fam]?.rule ?? "local only · counted"}</td></tr>))}
        </tbody></table>

      {reference ? (
        <div className="flex flex-col gap-2">
          <p className="label-sc">Reference recipe given to the model</p>
          <p>
            <b>{reference.title}</b>{" "}
            {reference.same_process && <SemChip sem="match">same cooking process</SemChip>}{" "}
            <span className="caption">{reference.licence}{reference.url && <> · <a className="underline" href={reference.url} target="_blank" rel="noreferrer">source</a></>}</span>
          </p>
          <p className="caption">The engine parsed this public recipe live and ran the same simulation on it. It is a different recipe:
            its values are typical conditions for comparison, never facts about your kitchen.</p>
          <table className="tbl dense"><thead><tr><th>Step</th><th>Process</th><th>Stated time</th><th>Stated temp</th><th>Lid</th><th>Food temp (sim.)</th><th>Dose (sim.)</th></tr></thead>
            <tbody>{reference.heat_steps.map((h) => (
              <tr key={h.step}><td className="mono">{h.step} · {h.action} · {h.food}</td><td>{h.process.split(" ").slice(1).join(" ")}</td>
                <td className="mono">{fmt(h.duration_min)}</td><td className="mono">{fmt(h.temperature_C)}</td><td>{fmt(h.lid_state)}</td>
                <td className="mono">{fmt(h.food_T_typical_C)}</td><td className="mono">{fmt(h.thermal_dose_typical_min)}</td></tr>))}
            </tbody></table>
        </div>
      ) : <p className="caption">No public recipe with a readable heat step matched, so the model got no reference.</p>}

      {search.shown.length > 0 && (
        <div>
          <p className="label-sc">Closest public matches</p>
          <ul className="mt-1 flex flex-col gap-1">{search.shown.map((s) => (
            <li key={s.id} className="flex flex-wrap items-baseline gap-2">
              <span className="mono caption">{s.score.toFixed(2)}</span>
              {s.url ? <a className="underline" href={s.url} target="_blank" rel="noreferrer">{s.title}</a> : <span>{s.title}</span>}
              <span className="caption">{FAMILY[s.family]?.name ?? s.family}</span>
            </li>))}
          </ul>
        </div>
      )}
    </div>
  );
}
