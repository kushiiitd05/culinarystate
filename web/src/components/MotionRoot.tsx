"use client";
import { MotionConfig } from "motion/react";
import type { ReactNode } from "react";

// Motion honours prefers-reduced-motion itself; markup is identical on server and client.
export function MotionRoot({ children }: { children: ReactNode }) {
  return <MotionConfig reducedMotion="user">{children}</MotionConfig>;
}
