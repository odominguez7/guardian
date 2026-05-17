import { chromium } from "playwright";
import path from "node:path";
import fs from "node:fs";
const OUT = "/Users/odominguez7/Desktop/GFS - guardIAn/video-assets/audit-2026-05-17";
fs.mkdirSync(OUT, { recursive: true });
const b = await chromium.launch({ headless: true });
const ctx = await b.newContext({ viewport: { width: 1920, height: 1080 } });
const p = await ctx.newPage();
await p.goto("https://guardian-ops-center-180171737110.us-central1.run.app/", { waitUntil: "networkidle", timeout: 60000 });
await p.waitForTimeout(2500);
await p.screenshot({ path: path.join(OUT, "v32-01-operations.png") });
console.log("✓ operations tab");

// Click Live Cams tab
await p.click('button:has-text("Live Cams")');
await p.waitForTimeout(3000);
await p.screenshot({ path: path.join(OUT, "v32-02-live-cams.png") });
console.log("✓ live cams tab");

// Click Agent Theater tab
await p.click('button:has-text("Agent Theater")');
await p.waitForTimeout(2500);
await p.screenshot({ path: path.join(OUT, "v32-03-agent-theater.png") });
console.log("✓ agent theater tab");

// Click a specialist agent
await p.click('button:has-text("Stream Watcher")').catch(() => {});
await p.waitForTimeout(1500);
await p.screenshot({ path: path.join(OUT, "v32-04-theater-stream-watcher.png") });
console.log("✓ theater with stream_watcher active");

await b.close();
console.log("done");
