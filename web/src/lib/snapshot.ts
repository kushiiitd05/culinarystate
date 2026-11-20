"use client";
import { useEffect, useState } from "react";
import type { Inventory, Manifest, Scenario } from "./types";

const BASE = "/snapshot";
const cache = new Map<string, Promise<unknown>>();

function getJson<T>(path: string): Promise<T> {
  const url = path.startsWith("/") ? path : `${BASE}/${path}`;
  let p = cache.get(url);
  if (!p) {
    p = fetch(url).then((r) => {
      if (!r.ok) throw new Error(`${url}: HTTP ${r.status}`);
      return r.json();
    });
    p.catch(() => cache.delete(url));
    cache.set(url, p);
  }
  return p as Promise<T>;
}

export type Loaded<T> = { status: "loading" } | { status: "ready"; data: T } | { status: "failed"; error: string };

function useJson<T>(path: string | null): Loaded<T> {
  const [state, setState] = useState<{ path: string | null; res: Loaded<T> }>({ path, res: { status: "loading" } });
  useEffect(() => {
    if (!path) return;
    let live = true;
    getJson<T>(path).then(
      (data) => live && setState({ path, res: { status: "ready", data } }),
      (e: unknown) => live && setState({ path, res: { status: "failed", error: e instanceof Error ? e.message : String(e) } }),
    );
    return () => { live = false; };
  }, [path]);
  return state.path === path ? state.res : { status: "loading" };
}

export const useManifest = () => useJson<Manifest>("manifest.json");
export const useScenario = (id: string | null) => useJson<Scenario>(id ? `scenarios/${id}.json` : null);
export const useInventory = () => useJson<Inventory>("/data/inventory.json");

export function useScenarios(ids: string[]): Loaded<Scenario[]> {
  const key = ids.join(",");
  const [state, setState] = useState<Loaded<Scenario[]>>({ status: "loading" });
  useEffect(() => {
    let live = true;
    Promise.all(key.split(",").map((id) => getJson<Scenario>(`scenarios/${id}.json`))).then(
      (data) => live && setState({ status: "ready", data }),
      (e: unknown) => live && setState({ status: "failed", error: e instanceof Error ? e.message : String(e) }),
    );
    return () => { live = false; };
  }, [key]);
  return state;
}

export type SigStatus = "checking" | "verified" | "unverified";

// Verifies manifest.json bytes against manifest.sig (Ed25519, base64) with public_key.pem,
// in the browser. Any failure — including a browser without Ed25519 — is "unverified".
async function verifyManifest(): Promise<boolean> {
  const [m, s, k] = await Promise.all(
    ["manifest.json", "manifest.sig", "public_key.pem"].map((f) => fetch(`${BASE}/${f}`, { cache: "no-store" })),
  );
  if (!m.ok || !s.ok || !k.ok) return false;
  const bytes = await m.arrayBuffer();
  const b64 = (t: string) => Uint8Array.from(atob(t), (c) => c.charCodeAt(0));
  const sig = b64((await s.text()).trim());
  const pem = (await k.text()).replace(/-----[A-Z ]+-----/g, "").replace(/\s+/g, "");
  const key = await crypto.subtle.importKey("spki", b64(pem), { name: "Ed25519" }, false, ["verify"]);
  return crypto.subtle.verify({ name: "Ed25519" }, key, sig, bytes);
}

export function useSignature(): SigStatus {
  const [s, setS] = useState<SigStatus>("checking");
  useEffect(() => {
    let live = true;
    verifyManifest().then((ok) => live && setS(ok ? "verified" : "unverified"), () => live && setS("unverified"));
    return () => { live = false; };
  }, []);
  return s;
}
