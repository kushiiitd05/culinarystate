import type { Metadata } from "next";
import { IBM_Plex_Sans, JetBrains_Mono, Source_Serif_4 } from "next/font/google";
import { Legend } from "@/components/Legend";
import { MotionRoot } from "@/components/MotionRoot";
import { TopNav } from "@/components/TopNav";
import "./globals.css";

const serif = Source_Serif_4({ subsets: ["latin"], variable: "--font-serif4", display: "swap" });
const plex = IBM_Plex_Sans({ subsets: ["latin"], weight: ["400", "500", "600"], variable: "--font-plex", display: "swap" });
const mono = JetBrains_Mono({ subsets: ["latin"], variable: "--font-jbmono", display: "swap" });

export const metadata: Metadata = {
  title: { default: "CulinaryState Explorer", template: "%s · CulinaryState Explorer" },
  description: "From recipe text to evidence-grounded cooking state. Precomputed snapshot; diagnostic only.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${serif.variable} ${plex.variable} ${mono.variable}`} suppressHydrationWarning>
      <body className="min-h-screen flex flex-col">
        <a href="#main" className="sr-only focus:not-sr-only focus:absolute focus:z-50 focus:bg-canvas focus:p-2">Skip to content</a>
        <TopNav />
        <main id="main" className="flex-1 min-h-0"><MotionRoot>{children}</MotionRoot></main>
        <Legend />
      </body>
    </html>
  );
}
