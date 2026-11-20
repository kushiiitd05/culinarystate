import { whyRouteFields } from "@/lib/lab";
import { decodeCell, type RawState } from "@/lib/types";
import { CellView } from "./CellView";

// "Why this route": the engine's own strings from the state, not a paraphrase.
export function WhyRoute({ state, target }: { state: RawState; target: string }) {
  return (
    <section aria-label="Why this route">
      <h4 className="label-sc mb-1">Why this route</h4>
      <p className="caption mb-1">Read from the state at this step, as the engine wrote it.</p>
      <table className="tbl dense">
        <tbody>
          {whyRouteFields(state, target).map((f) => (
            <tr key={f.path}>
              <th scope="row" className="!border-b-line w-[38%] !font-normal">
                <span className="block text-ink">{f.label}</span>
                <span className="mono text-ink-3">{f.path}</span>
              </th>
              <td><CellView cell={decodeCell(f.cell)} showBasis /></td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
