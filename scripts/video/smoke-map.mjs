// Smoke-test the local Ops Center: load page, click multimodal scenario,
// wait for fan-out, screenshot the result.
//
// Usage: node scripts/video/smoke-map.mjs

import { chromium } from "playwright";
import path from "node:path";
import url from "node:url";

const __dirname = path.dirname(url.fileURLToPath(import.meta.url));
const REPO = path.resolve(__dirname, "..", "..");
const OUT_DIR = path.join(REPO, "video-assets", "verification");

const browser = await chromium.launch({ headless: true });
const ctx = await browser.newContext({
  viewport: { width: 1920, height: 1080 },
  deviceScaleFactor: 1,
});
const page = await ctx.newPage();

const errors = [];
const logs = [];
page.on("console", (msg) => {
  if (msg.type() === "error") errors.push("[console.error] " + msg.text());
  else logs.push(`[${msg.type()}] ${msg.text()}`);
});
page.on("pageerror", (e) => errors.push("[pageerror] " + e.message));
page.on("requestfailed", (r) => errors.push(`[reqfail] ${r.method()} ${r.url()} -- ${r.failure()?.errorText}`));

console.log("→ loading http://localhost:3000");
await page.goto("http://localhost:3000", { waitUntil: "load", timeout: 30_000 });
await page.waitForTimeout(10_000); // map tiles + scenario tray render + WS connect
await page.screenshot({ path: path.join(OUT_DIR, "map-idle.png") });
console.log("  idle screenshot → video-assets/verification/map-idle.png");

console.log("→ clicking 'Full Multimodal Chain' scenario");
const btn = page.getByRole("button", { name: /Full Multimodal Chain/i });
const btnCount = await btn.count();
console.log(`  scenario button count: ${btnCount}`);
if (btnCount === 0) {
  console.warn("WARN: scenario button not found — taking what we have");
  console.log("errors so far:", errors);
  await browser.close();
  process.exit(2);
}
await btn.first().click();

// Watch fan-out
await page.waitForTimeout(3_000);
await page.screenshot({ path: path.join(OUT_DIR, "map-flyto.png") });
console.log("  flyTo screenshot → video-assets/verification/map-flyto.png");

await page.waitForTimeout(8_000); // let A2A peers ack and arrows draw
await page.screenshot({ path: path.join(OUT_DIR, "map-fanout.png") });
console.log("  fan-out screenshot → video-assets/verification/map-fanout.png");

await page.waitForTimeout(10_000); // full chain resolves
await page.screenshot({ path: path.join(OUT_DIR, "map-full.png") });
console.log("  full screenshot → video-assets/verification/map-full.png");

if (errors.length) {
  console.log("\nERRORS captured:");
  for (const e of errors) console.log(" ", e);
}
console.log("\nlast logs:");
for (const l of logs.slice(-20)) console.log(" ", l);

// Probe active state via window globals (page exposes some hooks via __NEXT_DATA__? Use evaluate)
const state = await page.evaluate(() => {
  const incidents = document.querySelectorAll('[data-incident-id], .incident');
  const peerMarkers = document.querySelectorAll('.mapboxgl-marker');
  const markerData = Array.from(peerMarkers).map(el => ({
    opacity: getComputedStyle(el).opacity,
    innerHTML: el.innerHTML.slice(0, 80),
  }));
  return {
    incidentNodes: incidents.length,
    peerMarkerCount: peerMarkers.length,
    markerData,
    bodyText: document.body.innerText.slice(0, 600),
  };
});
console.log("\nDOM probe:", JSON.stringify(state, null, 2));

await browser.close();
console.log("\n✓ smoke test complete");
