// Wordmark: a small lot-lineage glyph (two lots merging into one) beside the name.
export function Glyph({ size = 22 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" aria-hidden="true" focusable="false">
      <g fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round">
        <path d="M8 8 L16 16 M8 24 L16 16 M16 16 H24" />
      </g>
      <circle cx="8" cy="8" r="3.2" fill="var(--cs-canvas)" stroke="currentColor" strokeWidth="2.4" />
      <circle cx="8" cy="24" r="3.2" fill="var(--cs-canvas)" stroke="currentColor" strokeWidth="2.4" />
      <circle cx="24" cy="16" r="3.6" fill="currentColor" />
    </svg>
  );
}
export function Logo({ size = 22 }: { size?: number }) {
  return (
    <span className="inline-flex items-center gap-2 text-ink" aria-label="CulinaryState">
      <Glyph size={size} />
      <span className="serif" style={{ fontSize: size * 0.86, fontWeight: 500, letterSpacing: "-0.01em", lineHeight: 1 }}>
        CulinaryState
      </span>
    </span>
  );
}
