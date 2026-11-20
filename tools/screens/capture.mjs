import { chromium } from "playwright-core";
import { createHash } from "node:crypto";
import { execFileSync } from "node:child_process";
import { mkdir, readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = fileURLToPath(new URL("../../", import.meta.url));
const output = resolve(root, "reports/final/screens");
const snapshotURL = process.env.CS_SNAPSHOT_CAPTURE_URL || "http://localhost:3001";
const liveURL = process.env.CS_LIVE_CAPTURE_URL || "http://localhost:3000";
const freeze = execFileSync("git", ["rev-list", "-n", "1", "freeze-2026-11-20"], { cwd: root, encoding: "utf8" }).trim();
const mode = process.argv[2] || "snapshot";
if (!["snapshot", "live", "local"].includes(mode)) throw new Error("Select snapshot, live or local.");
const sha256 = bytes => createHash("sha256").update(bytes).digest("hex");
const captures = [];
const runs = [];
await mkdir(resolve(output, "runs"), { recursive: true });

const browser = await chromium.launch({
  executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  headless: true,
  args: ["--disable-background-networking"],
});
const context = await browser.newContext({
  viewport: { width: 1600, height: 1000 },
  deviceScaleFactor: 1,
  colorScheme: "light",
  reducedMotion: "reduce",
});
const page = await context.newPage();
async function shot(name, route) {
  await page.evaluate(() => document.fonts.ready);
  const styled = await page.evaluate(() => getComputedStyle(document.body).backgroundColor !== "rgba(0, 0, 0, 0)");
  if (!styled) throw new Error("The page stylesheet did not load.");
  const body = await page.locator("body").innerText();
  if (/\/Users\/|nvapi-|BBCGF|SRC-000002/.test(body)) throw new Error("Restricted text on screen.");
  if (mode !== "snapshot" && /engine offline/i.test(body)) throw new Error("The live engine is offline.");
  const file = name + ".png";
  const bytes = await page.screenshot({ animations: "disabled" });
  await writeFile(resolve(output, file), bytes);
  captures.push({ file, route, commit: freeze, timestamp_utc: new Date().toISOString(), sha256: sha256(bytes), viewport: [1600, 1000],
    ...(mode === "local" ? { hosted_model_sent: false } : {}) });
}
async function snapshot(route) {
  const response = await page.goto(snapshotURL + route);
  if (response?.status() !== 200) throw new Error("Snapshot route failed: " + route);
  await page.getByText("verified", { exact: true }).first().waitFor();
  if (await page.getByRole("link", { name: "Live", exact: true }).count()) throw new Error("Public navigation exposes Live.");
}
async function ask(preset, id, capturePipeline = false) {
  await page.getByRole("button", { name: preset }).click();
  if (mode === "local") await page.getByRole("checkbox", { name: /I wrote this recipe text/ }).uncheck();
  const responsePromise = page.waitForResponse(res => new URL(res.url()).pathname === "/api/live" && res.request().method() === "POST", { timeout: 180000 });
  await page.getByRole("button", { name: "Ask live" }).click();
  if (capturePipeline) {
    await page.getByText("asking the model…", { exact: false }).first().waitFor({ timeout: 20000 });
    await shot("06_live_pipeline_ticking", "/live");
  }
  const response = await responsePromise;
  const data = await response.json();
  const serialized = JSON.stringify(data, null, 2) + "\n";
  if (/\/Users\/|nvapi-|BBCGF|SRC-000002/.test(serialized)) throw new Error("Restricted marker in live response.");
  const file = id + ".json";
  await writeFile(resolve(output, "runs", file), serialized);
  runs.push({ file, route: "/api/live", commit: freeze, timestamp_utc: new Date().toISOString(),
    sha256: sha256(serialized), model: data.model ?? null, http_status: response.status() });
  if (!response.ok() || data.error) throw new Error("Live request failed for " + id + " (HTTP " + response.status() + ")");
  await page.getByRole("region", { name: "CulinaryState answer" }).waitFor({ timeout: 15000 });
  return data;
}

async function similarShot() {
  const data = await ask("Roast potatoes soggy", "potatoes");
  if (mode === "local" && data.plain?.status !== "NOT_SENT_TEXT_NOT_SELF_WRITTEN") {
    throw new Error("Expected the ordinary no-send result.");
  }
  if (!data.similar?.search?.searched) throw new Error("The local similar-recipe index was unavailable.");
  await page.getByRole("tab", { name: "Similar recipes" }).click();
  await page.getByText(/Searched all/).scrollIntoViewIfNeeded();
  await shot("10_live_similar_recipes", "/live");
}

async function safetyShot() {
  const data = await ask("Chicken · is it safe?", "safety");
  if (data.system?.status !== "ABSTAIN_SAFETY") throw new Error("Safety refusal was absent.");
  if (mode === "local" && data.plain?.status !== "NOT_SENT_TEXT_NOT_SELF_WRITTEN") {
    throw new Error("Expected the ordinary no-send result.");
  }
  await page.getByRole("region", { name: "CulinaryState answer" }).scrollIntoViewIfNeeded();
  await shot("11_live_safety_refusal", "/live");
}

try {
  if (mode === "snapshot") {
    await snapshot("/");
    await shot("01_landing", "/");
    await snapshot("/lab?s=tomato-a");
    await page.getByRole("list", { name: "States in order" }).getByRole("button").last().click();
    await shot("02_lab_tomato_state", "/lab?s=tomato-a");
    await snapshot("/lab?s=tomato-c");
    await page.getByRole("list", { name: "States in order" }).getByRole("button").last().click();
    await page.getByRole("tab", { name: "Compatibility", exact: true }).click();
    await page.getByRole("tabpanel", { name: "Compatibility" }).getByRole("table").waitFor();
    await shot("03_lab_unknown_axis", "/lab?s=tomato-c");
    await snapshot("/compare");
    await page.getByRole("heading", { name: "What differs in state at the final step" }).waitFor();
    await shot("04_compare_A-D", "/compare");
    await snapshot("/method");
    await shot("05_method_pipeline", "/method");
    await snapshot("/lab?s=banana-abstain");
    await shot("12_snapshot_signature_badge", "/lab?s=banana-abstain");
  } else if (mode === "local") {
    await page.route(/\/api\/live(\/analyse)?$/, route => {
      const method = route.request().method();
      if (method === "POST" && route.request().postDataJSON().self_written !== false) return route.abort();
      return route.continue();
    });
    await page.goto(liveURL + "/live");
    await similarShot();
    await safetyShot();
  } else {
    await page.goto(liveURL + "/live");
    await page.getByRole("button", { name: "Ask live" }).waitFor();
    const carrots = await ask(/Carrots came out mushy/, "carrots", true);
    await page.getByRole("region", { name: "CulinaryState answer" }).scrollIntoViewIfNeeded();
    await shot("07_live_answer_carrots", "/live");
    if (carrots.plain?.status === "OK") {
      await page.getByRole("button", { name: "Compare with plain LLM" }).click();
      await page.getByRole("region", { name: "Plain LLM answer" }).waitFor();
      await shot("08_live_compare_plain_carrots", "/live");
    }
    const tomatoes = await ask("Tomatoes · vitamin C", "tomatoes");
    if (tomatoes.plain?.status === "OK") {
      await page.getByRole("button", { name: "Compare with plain LLM" }).click();
      await page.getByRole("region", { name: "Plain LLM answer" }).scrollIntoViewIfNeeded();
      await shot("09_live_vitc_compare", "/live");
    }
    await similarShot();
    await safetyShot();
  }
} finally {
  const file = resolve(output, "MANIFEST.json");
  let previous = [];
  try { previous = JSON.parse(await readFile(file, "utf8")).images; }
  catch (error) { if (error.code !== "ENOENT") throw error; }
  const images = new Map(previous.map(row => [row.file, row]));
  for (const row of captures) images.set(row.file, row);
  await writeFile(file, JSON.stringify({
    freeze: "freeze-2026-11-20",
    images: [...images.values()].sort((a, b) => a.file.localeCompare(b.file)),
    colour_vision_variant: "NOT_IMPLEMENTED",
  }, null, 2) + "\n");
  if (runs.length) {
    const file = resolve(output, "runs", "RUN_MANIFEST.json");
    let previousRuns = [];
    try { previousRuns = JSON.parse(await readFile(file, "utf8")).responses; }
    catch (error) { if (error.code !== "ENOENT") throw error; }
    const responses = new Map(previousRuns.map(row => [row.file, row]));
    for (const row of runs) responses.set(row.file, row);
    await writeFile(file, JSON.stringify({ responses: [...responses.values()] }, null, 2) + "\n");
  }
  await browser.close();
}
