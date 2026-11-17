"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Moon, Sun } from "lucide-react";
import { useEffect, useState } from "react";
import { Logo } from "./Logo";
import { ModeBadge } from "./ModeBadge";

const LINKS = [["/lab", "Lab"], ["/compare", "Compare"], ["/method", "Method"]] as const;

function ThemeToggle() {
  const [dark, setDark] = useState(false);
  useEffect(() => {
    let stored: string | null = null;
    try { stored = localStorage.getItem("cs-theme"); } catch { /* storage unavailable: stay light */ }
    if (stored === "dark") { document.documentElement.classList.add("dark"); setDark(true); }
  }, []);
  const toggle = () => {
    const next = !dark;
    setDark(next);
    document.documentElement.classList.toggle("dark", next);
    try { localStorage.setItem("cs-theme", next ? "dark" : "light"); } catch { /* not persisted */ }
  };
  return (
    <button type="button" className="btn" onClick={toggle} aria-pressed={dark} aria-label="Dark mode">
      {dark ? <Moon size={14} aria-hidden="true" /> : <Sun size={14} aria-hidden="true" />}
      <span>{dark ? "Dark" : "Light"}</span>
    </button>
  );
}

export function TopNav() {
  const path = usePathname();
  return (
    <header className="sticky top-2 z-40 mx-2 mt-2">
      <nav aria-label="Primary" className="glass flex flex-wrap items-center gap-x-4 gap-y-2 px-4 py-2">
        <Link href="/" aria-label="CulinaryState home"><Logo /></Link>
        <ul className="flex items-center gap-1">
          {LINKS.map(([href, label]) => {
            const on = path === href || path.startsWith(`${href}/`);
            return (
              <li key={href}>
                <Link href={href} aria-current={on ? "page" : undefined}
                  className={`px-2.5 py-1 text-[14px] ${on ? "font-semibold text-ink border-b-2 border-ink" : "text-ink-2 border-b-2 border-transparent"}`}>
                  {label}
                </Link>
              </li>
            );
          })}
        </ul>
        <div className="ml-auto flex flex-wrap items-center gap-2">
          <ModeBadge />
          <ThemeToggle />
        </div>
      </nav>
    </header>
  );
}
