// Render a single HTML file to a transparent PNG (for video overlay use).
// Usage: node scripts/video/render-overlay.mjs <html-path> <png-out>

import { chromium } from "playwright";
import path from "node:path";

const src = path.resolve(process.argv[2]);
const dst = path.resolve(process.argv[3]);

const browser = await chromium.launch({ headless: true });
const ctx = await browser.newContext({
  viewport: { width: 1920, height: 1080 },
  deviceScaleFactor: 1,
});
const page = await ctx.newPage();
await page.goto("file://" + src, { waitUntil: "networkidle" });
await page.waitForTimeout(150);
await page.screenshot({ path: dst, omitBackground: true });
await browser.close();
console.log(`[ok] ${dst}`);
