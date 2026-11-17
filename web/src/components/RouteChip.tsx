import { routeSem, type Route } from "@/lib/types";
import { DerivedChip, SemChip } from "./StateMark";

const ROUTE_TEXT: Record<Route, string> = {
  DIRECT: "DIRECT · evidence applies",
  SCENARIO: "SCENARIO · scenario value",
  QUALITATIVE: "QUALITATIVE · no number",
  CONTEXT_MISMATCH: "CONTEXT_MISMATCH · does not apply",
  UNKNOWN: "UNKNOWN · abstains",
};
export function RouteChip({ route }: { route: Route }) {
  const sem = routeSem(route);
  if (sem === "derived") return <DerivedChip>{ROUTE_TEXT[route]}</DerivedChip>;
  return <SemChip sem={sem}>{ROUTE_TEXT[route]}</SemChip>;
}
