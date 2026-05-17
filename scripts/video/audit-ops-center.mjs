// Headless audit capture of the live Ops Center.
// Takes screenshots at 5 states:
//   1. initial-load — empty, before any user gesture
//   2. after-click — user clicked, ambient bed should start
//   3. scenario-mid-firing — scenario in progress, fan-out arrows + ack cards
//   4. scenario-complete — all 4 peers ack'd
//   5. auto-cycle-active — idle for 12s, AUTO DEMO should fire

import { chromium } from "playwright";
import path from "node:path";
import fs from "node:fs";
import url from "node:url";

const __dirname = path.dirname(url.fileURLToPath(import.meta.url));
const REPO = path.resolve(__dirname, "..", "..");
const OUT_DIR = path.join(REPO, "video-assets", "audit-2026-05-17");
fs.mkdirSync(OUT_DIR, { recursive: true });

const URL = process.env.OPS_CENTER_URL ?? "https://guardian-ops-center-180171737110.us-central1.run.app/";

console.log(`→ launching headless chromium against ${URL}`);
const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({
  viewport: { width: 1920, height: 1080 },
  deviceScaleFactor: 1,
});
const page = await context.newPage();
page.on("console", (msg) => console.log(`  [browser-${msg.type()}]`, msg.text().slice(0, 200)));
page.on("pageerror", (err) => console.error("  [page-error]", err.message.slice(0, 200)));

console.log("→ goto + wait for network idle");
await page.goto(URL, { waitUntil: "networkidle", timeout: 60_000 });
await page.waitForTimeout(2_000);
const p1 = path.join(OUT_DIR, "01-initial-load.png");
await page.screenshot({ path: p1, fullPage: false });
console.log(`✓ ${p1}`);

console.log("→ click somewhere (triggers ambient bed)");
await page.mouse.click(960, 540);
await page.waitForTimeout(1_500);
const p2 = path.join(OUT_DIR, "02-after-first-click.png");
await page.screenshot({ path: p2, fullPage: false });
console.log(`✓ ${p2}`);

console.log("→ click 'Full Multimodal Chain' scenario");
const scenarioBtn = page.locator('button:has-text("Full Multimodal Chain")').first();
await scenarioBtn.click({ timeout: 15_000 });
await page.waitForTimeout(8_000);  // fan-out starts
const p3 = path.join(OUT_DIR, "03-scenario-mid-firing.png");
await page.screenshot({ path: p3, fullPage: false });
console.log(`✓ ${p3}`);

console.log("→ wait for scenario complete (4 peers ack)");
await page.waitForTimeout(25_000);
const p4 = path.join(OUT_DIR, "04-scenario-complete.png");
await page.screenshot({ path: p4, fullPage: false });
console.log(`✓ ${p4}`);

console.log("→ idle 15s, check for AUTO DEMO trigger");
await page.waitForTimeout(15_000);
const p5 = path.join(OUT_DIR, "05-auto-cycle-active.png");
await page.screenshot({ path: p5, fullPage: false });
console.log(`✓ ${p5}`);

// Also capture the right-rail (activity stream) zoomed for "talks in code" critique
console.log("→ zoom right-rail (activity stream code-language audit)");
const rail = page.locator('h2:has-text("Agent Activity Stream"), [class*="AGENT ACTIVITY STREAM"]').first().or(page.locator('text=AGENT ACTIVITY STREAM').first());
try {
  const box = await rail.boundingBox({ timeout: 3000 });
  if (box) {
    await page.screenshot({
      path: path.join(OUT_DIR, "06-activity-stream-detail.png"),
      clip: { x: 1560, y: 0, width: 360, height: 1080 },
    });
    console.log(`✓ 06-activity-stream-detail.png`);
  }
} catch (e) {
  await page.screenshot({
    path: path.join(OUT_DIR, "06-activity-stream-detail.png"),
    clip: { x: 1560, y: 0, width: 360, height: 1080 },
  });
  console.log(`✓ 06-activity-stream-detail.png (fallback crop)`);
}

// Also capture the incident panel (left rail)
await page.screenshot({
  path: path.join(OUT_DIR, "07-incident-panel-detail.png"),
  clip: { x: 0, y: 0, width: 320, height: 1080 },
});
console.log(`✓ 07-incident-panel-detail.png`);

console.log("→ board-slide endpoint audit");
const slidePage = await context.newPage();
await slidePage.goto("https://guardian-180171737110.us-central1.run.app/board-slide/TNFD-2026-A0192B2A32", { waitUntil: "networkidle", timeout: 60_000 });
await slidePage.waitForTimeout(2_000);
await slidePage.screenshot({ path: path.join(OUT_DIR, "08-board-slide.png"), fullPage: false });
console.log(`✓ 08-board-slide.png`);

await browser.close();
console.log("");
console.log(`done. ${fs.readdirSync(OUT_DIR).length} captures written to ${OUT_DIR}`);
