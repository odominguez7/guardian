import { chromium } from "playwright";
const br = await chromium.launch({ headless: true });
const ctx = await br.newContext({ viewport: { width: 1920, height: 1080 } });
const p = await ctx.newPage();
await p.goto("http://localhost:3000", { waitUntil: "load" });
await p.waitForTimeout(8_000);
const info = await p.evaluate(() => {
  const all = document.querySelectorAll("*");
  const matches = [];
  for (const el of all) {
    const tag = el.tagName.toLowerCase();
    if (tag.startsWith("next") || (el.id || "").includes("nextjs") || /next.*portal|toast|dev/i.test(String(el.className))) {
      matches.push({tag: el.tagName, id: el.id, cls: String(el.className).slice(0,100), shadow: !!el.shadowRoot});
    }
  }
  return matches;
});
console.log(JSON.stringify(info, null, 2));
await br.close();
