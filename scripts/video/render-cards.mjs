// Render every video-assets/cards/*.html to a matching 1920x1080 PNG via Playwright.
// Usage: node scripts/video/render-cards.mjs                (renders all)
//        ONLY=02-proof-tnfd-id node scripts/video/render-cards.mjs   (renders one)

import { chromium } from "playwright";
import path from "node:path";
import fs from "node:fs";
import url from "node:url";

const __dirname = path.dirname(url.fileURLToPath(import.meta.url));
const CARDS_DIR = path.resolve(__dirname, "..", "..", "video-assets", "cards");
const ONLY = (process.env.ONLY || "").trim();

const htmls = fs.readdirSync(CARDS_DIR).filter(f => f.endsWith(".html"));
const browser = await chromium.launch({ headless: true });
const ctx = await browser.newContext({
  viewport: { width: 1920, height: 1080 },
  deviceScaleFactor: 1,
});
const page = await ctx.newPage();

for (const f of htmls) {
  const base = f.replace(/\.html$/, "");
  if (ONLY && base !== ONLY) continue;
  const src = path.join(CARDS_DIR, f);
  const dst = path.join(CARDS_DIR, `${base}.png`);
  await page.goto("file://" + src, { waitUntil: "networkidle" });
  await page.waitForTimeout(150); // let fonts settle
  await page.screenshot({ path: dst, fullPage: false, omitBackground: false });
  console.log(`[ok] ${base}.png`);
}
await browser.close();
