// Pipeline as a clean inline SVG. Each box links to its inventory row(s) below.
type Box = { label: string; sub?: string; inv: number[]; llm?: boolean };
const BOXES: Box[] = [
  { label: "Recipe", sub: "text", inv: [1, 28] },
  { label: "Semantic compiler", sub: "process recognition", inv: [5, 2, 3, 4] },
  { label: "Ambiguity trigger", inv: [24] },
  { label: "LLM proposal", sub: "alternative_group only", inv: [24], llm: true },
  { label: "Typed Event IR", inv: [6] },
  { label: "Invariant validator", sub: "V1–V4", inv: [7] },
  { label: "S_t = (G,C,Q,Y,P)", sub: "lot graph · replay", inv: [8, 9, 10, 11, 12] },
  { label: "Evidence compiler", sub: "ledger · router", inv: [14, 18, 22] },
  { label: "Compatibility", sub: "axes · pH bands", inv: [15, 16, 17] },
  { label: "Claim packet", inv: [23] },
  { label: "Verbaliser", sub: "template", inv: [25] },
  { label: "Claim verifier", inv: [26] },
  { label: "Answer or abstention", inv: [26, 28] },
];
const W = 170, H = 62, GX = 34, GY = 46, PER = 5;

function pos(i: number) {
  const row = Math.floor(i / PER);
  const col = row % 2 === 0 ? i % PER : PER - 1 - (i % PER); // snake, so arrows stay short
  return { x: 10 + col * (W + GX), y: 10 + row * (H + GY), row };
}

export function PipelineDiagram() {
  const rows = Math.ceil(BOXES.length / PER);
  const vw = 20 + PER * W + (PER - 1) * GX, vh = 20 + rows * H + (rows - 1) * GY;
  return (
    <figure className="flex flex-col gap-2">
      <svg viewBox={`0 0 ${vw} ${vh}`} className="w-full h-auto" aria-labelledby="pipe-title">
        <title id="pipe-title">{`Pipeline: ${BOXES.map((b) => b.label).join(" → ")}`}</title>
        <defs>
          <marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
            <path d="M0 0 L10 5 L0 10 z" fill="var(--cs-border-strong)" />
          </marker>
        </defs>
        {BOXES.slice(1).map((_, k) => {
          const a = pos(k), b = pos(k + 1);
          const [x1, y1, x2, y2] = a.row === b.row
            ? (b.x > a.x ? [a.x + W, a.y + H / 2, b.x - 3, b.y + H / 2] : [a.x, a.y + H / 2, b.x + W + 3, b.y + H / 2])
            : [a.x + W / 2, a.y + H, b.x + W / 2, b.y - 3];
          return <line key={k} x1={x1} y1={y1} x2={x2} y2={y2} stroke="var(--cs-border-strong)" strokeWidth={1.5} markerEnd="url(#arr)" />;
        })}
        {BOXES.map((b, i) => {
          const p = pos(i);
          return (
            <a key={b.label} href={`#inv-${b.inv[0]}`} aria-label={`${b.label}: inventory rows ${b.inv.join(", ")}`}>
              <rect x={p.x} y={p.y} width={W} height={H} rx={b.llm ? 0 : 4} fill="var(--cs-surface-2)"
                stroke={b.llm ? "var(--viz-ai-suggested)" : "var(--cs-border-strong)"} strokeWidth={2} strokeDasharray={b.llm ? "5 3" : undefined} />
              <text x={p.x + 10} y={p.y + 22} fontSize="14" fontWeight={600} fill="var(--cs-text-primary)" fontFamily="var(--font-sans)">
                {b.llm ? "* " : ""}{b.label}
              </text>
              {b.sub && <text x={p.x + 10} y={p.y + 39} fontSize="12" fill="var(--cs-text-secondary)" fontFamily="var(--font-sans)">{b.sub}</text>}
              <text x={p.x + 10} y={p.y + 54} fontSize="11" fill="var(--cs-text-muted)" fontFamily="var(--font-mono)" style={{ fontFeatureSettings: '"calt" 0, "zero" 1' }}>
                {b.inv.length > 4 ? `inv #${b.inv[0]}–#${b.inv[b.inv.length - 1]}` : `inv #${b.inv.join(", #")}`}
              </text>
            </a>
          );
        })}
      </svg>
      <figcaption className="caption">
        Read left to right, then snake down. The dashed square with <span className="marker">*</span> is the only LLM step; it may propose an
        {" "}<span className="mono">alternative_group</span> and nothing else, and its proposal passes the invariant validator like any other event.
        Each box links to its rows in the inventory below (<span className="mono">inv #n</span>).
      </figcaption>
      <ul className="flex flex-wrap gap-x-3 gap-y-1 text-[13px]">
        {BOXES.map((b) => (
          <li key={b.label}>{b.label}: {b.inv.map((n, j) => <a key={n} href={`#inv-${n}`} className="underline mono">{j ? ", " : ""}#{n}</a>)}</li>
        ))}
      </ul>
    </figure>
  );
}
