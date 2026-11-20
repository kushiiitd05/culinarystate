// Quoted verbatim from reports/final/DELIVERABLE_COMPLIANCE_MATRIX_2026-11-16.md (markdown emphasis removed).
const ROWS = [
  ["D1", "PARTIAL", "≥40 hand-verified literature rows. The ledger records 0 human-verified rows — all 17,978 are tier E3.", "human only"],
  ["D2", "PARTIAL", "not every prescribed statistical treatment demonstrated", "agent, if scoped"],
  ["D3", "STRONG CORE, EVALUATION PARTIAL", "The 40-gold-recipe evaluation. State-field accuracy, replay consistency and merge/split F1 against a gold set are not demonstrated", "human (gold) + agent (scoring)"],
  ["D4", "STRONG CORE, METRICS PARTIAL", "The full prescribed metric set — condition-compatible Recall@K, risk–coverage curves and ECE — is not all reported", "agent"],
  ["D5", "PARTIAL", "(a) chef/peer review — not performed. (b) The demo is a backend scenario runner, not the \"8-scenario Streamlit demo\" the contract names.", "human; agent"],
];

export function Limitations() {
  return (
    <section aria-label="What this does not show" className="flex flex-col gap-3">
      <h2 className="h-section">What this does not show</h2>
      <p className="prose-body text-ink-2">No deliverable is complete. Each row below is quoted from the compliance matrix.</p>
      <div className="overflow-x-auto">
        <table className="tbl min-w-[720px]">
          <thead><tr><th>Deliverable</th><th>Status</th><th>Not met / not demonstrated</th><th>Who can close it</th></tr></thead>
          <tbody>{ROWS.map(([d, s, g, w]) => (
            <tr key={d}><td className="font-semibold">{d}</td><td><span className="chip border-2 border-dashed border-line-3 mono">{s}</span></td><td>{g}</td><td>{w}</td></tr>
          ))}</tbody>
        </table>
      </div>
      <ul className="prose-body list-disc pl-5 flex flex-col gap-1">
        <li>&ldquo;Three gaps are human-only and none can be closed by building a UI. A deployed app does not substitute for hand-verified rows, a gold recipe set, or a chef review.&rdquo;</li>
        <li>&ldquo;Forty rows of literature verification cannot be delegated to an AI under D-085.&rdquo; AI-delegated reviews are not human verification.</li>
        <li>&ldquo;The proposal specified an 8-scenario Streamlit demo; we built an interactive web application covering the same eight scenarios.&rdquo; This app is that substitution.</li>
        <li>The matrix itself is &ldquo;AI_DRAFTED — not a human attestation of compliance.&rdquo;</li>
      </ul>
      <p className="caption">Source: <span className="mono">reports/final/DELIVERABLE_COMPLIANCE_MATRIX_2026-11-16.md</span></p>
    </section>
  );
}
