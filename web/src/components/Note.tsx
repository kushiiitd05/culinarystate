import { Info } from "lucide-react";
import type { ReactNode } from "react";

export function Note({ title, children }: { title: string; children: ReactNode }) {
  return (
    <aside className="border border-line-3 border-l-[3px] bg-canvas px-3 py-2 text-[13px] leading-snug" style={{ borderRadius: 2 }}>
      <p className="flex items-center gap-1.5 font-semibold"><Info size={13} aria-hidden="true" />{title}</p>
      <div className="mt-1 text-ink-2">{children}</div>
    </aside>
  );
}
