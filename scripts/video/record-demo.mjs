// Drives the live GUARDIAN Ops Center and records a 1920x1080 video of the
// multimodal_pipeline scenario end-to-end. Output: video-assets/footage/ops-center-<timestamp>.webm
//
// Usage: node scripts/video/record-demo.mjs
//
// Notes:
// - Uses Playwright's built-in `recordVideo` context option (page-level capture).
// - Headed by default so the browser is visible; flip HEADLESS=1 to hide.
// - Does NOT need DOM auth (the dashboard runs anonymously when Firebase Auth is unconfigured).

import { chromium } from "playwright";
import path from "node:path";
import fs from "node:fs";
import url from "node:url";

const __dirname = path.dirname(url.fileURLToPath(import.meta.url));
const REPO = path.resolve(__dirname, "..", "..");
const FOOTAGE_DIR = path.join(REPO, "video-assets", "footage");
// Default to localhost (V2 recording — needs Mapbox token in ops-center/.env.local).
// Override with OPS_CENTER_URL=... env var to record against Cloud Run.
const OPS_CENTER = process.env.OPS_CENTER_URL ?? "http://localhost:3000/";

fs.mkdirSync(FOOTAGE_DIR, { recursive: true });

const HEADLESS = process.env.HEADLESS === "1";
const SCENARIO_BUTTON_TEXT = process.env.SCENARIO ?? "Full Multimodal Chain";
const HOLD_AFTER_CLICK_MS = Number(process.env.HOLD_MS ?? 55_000); // let chain play + ack cards land

const stamp = new Date().toISOString().replace(/[:.]/g, "-").slice(0, 19);
const targetWebm = path.join(FOOTAGE_DIR, `ops-center-${stamp}.webm`);

console.log("→ launching chromium (headed)");
const browser = await chromium.launch({ headless: HEADLESS });
const context = await browser.newContext({
  viewport: { width: 1920, height: 1080 },
  deviceScaleFactor: 1,
  recordVideo: {
    dir: FOOTAGE_DIR,
    size: { width: 1920, height: 1080 },
  },
});
const page = await context.newPage();

console.log("→ navigating to Ops Center");
await page.goto(OPS_CENTER, { waitUntil: "load", timeout: 60_000 });

// Give the dashboard 6s to settle: WebSocket connect, map tiles, scenario tray render.
console.log("→ holding 6s for dashboard to settle");
await page.waitForTimeout(6_000);

console.log(`→ clicking scenario button: "${SCENARIO_BUTTON_TEXT}"`);
const button = page.getByRole("button", { name: SCENARIO_BUTTON_TEXT, exact: false });
await button.waitFor({ state: "visible", timeout: 15_000 });
await button.click();

console.log(`→ holding ${HOLD_AFTER_CLICK_MS / 1000}s for chain + peer acks to play out`);
await page.waitForTimeout(HOLD_AFTER_CLICK_MS);

// Final 3s of idle so the cut has a clean tail
await page.waitForTimeout(3_000);

console.log("→ closing context (flushes video)");
const video = page.video();
await context.close();
await browser.close();

// Playwright writes the WebM with an auto-generated name; rename to our timestamped one.
if (video) {
  const rawPath = await video.path();
  fs.renameSync(rawPath, targetWebm);
  const stats = fs.statSync(targetWebm);
  console.log(`✓ recorded ${(stats.size / 1024 / 1024).toFixed(1)} MB → ${targetWebm}`);
} else {
  console.error("× no video object returned");
  process.exit(1);
}
