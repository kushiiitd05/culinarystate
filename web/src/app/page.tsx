import Link from "next/link";
import { LandingFigures } from "@/components/LandingFigures";
import { Glyph } from "@/components/Logo";

const TOMATOES = [["tomato-a", "Tomato A"], ["tomato-b", "Tomato B"], ["tomato-c", "Tomato C"], ["tomato-d", "Tomato D"]];

export default function Home() {
  return (
    <div className="px-4 py-14 max-w-[1080px] mx-auto flex flex-col gap-10">
      <section className="flex flex-col gap-5">
        <span className="text-ink"><Glyph size={40} /></span>
        <h1 className="serif" style={{ fontSize: "clamp(34px,4.2vw,48px)", lineHeight: 1.06, fontWeight: 400 }}>
          From recipe text to evidence-grounded cooking state
        </h1>
        <p className="prose-body text-ink-2">Precomputed snapshot of the engine&apos;s output on self-written recipes. Diagnostic only.</p>
        <div className="flex flex-wrap gap-2">
          <Link href="/lab?s=tomato-a" className="btn btn-solid">Open the Lab</Link>
          {TOMATOES.map(([id, t]) => <Link key={id} href={`/lab?s=${id}`} className="btn">{t}</Link>)}
          <Link href="/compare" className="btn">Compare A–D</Link>
        </div>
      </section>
      <LandingFigures />
    </div>
  );
}
