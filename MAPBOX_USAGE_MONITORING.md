# Mapbox usage monitoring — how to NOT get billed

Quick summary of how Mapbox bills us + what to do to stay in the free tier.

## Free tier limits (Mapbox GL JS web maps)

- **50,000 map loads / month**, then pay-as-you-go.
- A "map load" = one initialization of a `mapboxgl.Map` object on a page. Page reload = new load. Single browsing session caps at 12 hours.
- Tiered overage pricing once you cross 50k:
  - 50,001–100,000 loads: **$5.00 per 1,000**
  - 100,001–200,000: $4.00 per 1,000
  - 200,001–1M: $3.00 per 1,000

For our hackathon judges (~50-200 unique clicks total), we're nowhere near 50k. The risk is if the token leaks and someone embeds it on their high-traffic site.

## What Mapbox does NOT offer

- ❌ Hard spending cap. Once over 50k, billing is automatic.
- ❌ Configurable usage alerts (e.g. "email me at 50% of free tier"). They do NOT send threshold warnings.
- ❌ Wildcard URL restrictions. Each domain must be listed explicitly.
- ✅ One automatic email the first time you exceed free tier in a billing period.

So the only real safeguards are: (a) restrict the token so leaks can't be abused, and (b) check the dashboard manually.

## The token we deployed tonight

The token in env is `pk.eyJ1Ijoib2RvbWluZ3VlejA3...` — this is your **default public token**. It works, but **it cannot be URL-restricted**. The default token is universally usable; anyone who pulls it out of the JS bundle can use it from anywhere.

For a hackathon demo with limited audience this is acceptable risk. But: see "Polish step" below.

## Polish step — create a URL-restricted custom token (15 min, do when back)

The default token can't be locked down. We need a **custom public token** with URL restrictions. Steps:

1. Open https://console.mapbox.com/account/access-tokens/
2. Click **+ Create a token** (top)
3. Settings:
   - **Name:** `guardian-ops-center-prod`
   - **Scopes:** leave all "Public Scopes" checked (default). Do not enable any secret scopes.
   - **URL Restrictions** (the important part) — add these one at a time:
     - `https://guardian-ops-center-180171737110.us-central1.run.app`
     - (if you add a custom domain later, add it here too)
4. Click **Create token**. Copy it.
5. Paste in chat OR run:
   ```bash
   export MAPBOX_TOKEN="pk.<your-new-restricted-token>"
   cd ~/Desktop/GFS\ -\ Agents\ Hackathon
   make deploy-ops-center
   ```
6. Optional — create a second token `guardian-ops-center-dev` with `http://localhost:3000` for local dev. Wildcards aren't supported, so explicit.

Mapbox blocks requests from non-listed origins with 403; leaking the token in the public JS bundle no longer matters.

## How to monitor usage day-to-day

### Mapbox console

- **Statistics page:** https://console.mapbox.com/statistics/
- Shows your map loads by day/week/month, broken down by domain + country.
- **~24-hour delay** — usage doesn't show up immediately. Don't panic if it's empty right after the demo.
- Bookmark this. Check it once a week + the day before submission.

### Invoices page

- https://console.mapbox.com/invoices/
- If you're under the 50k free tier, this page shows "$0.00" all month.
- If you cross it, you'll see the daily breakdown of charges accruing.

### Our own monitoring (cheap insurance, optional)

I can add a tiny client-side counter to the Ops Center that:
1. Listens to mapbox-gl `load` events
2. Posts the count to `/events/load-counter` on the orchestrator
3. Renders a "Map loads this session" widget in the toolbar
4. Hard-caps at 40,000 (safety buffer below 50k) → switches to placeholder

If you want me to build that next session, say so. ~30 min of work.

## If something does start billing

- Mapbox emails the account address the first time you cross free tier in a billing period.
- You will not get a second email until the next billing cycle.
- The default account has no payment method by default. Without a card on file, Mapbox would block service rather than auto-bill into a debt — but verify your account state at https://console.mapbox.com/account/billing/.
- Cheapest defense if usage spikes: just delete the leaked token at https://console.mapbox.com/account/access-tokens/. The page goes blank until you redeploy with a new token, no charges accumulate.

## TL;DR

| Action | Why |
|---|---|
| Bookmark https://console.mapbox.com/statistics/ | Weekly visual check on usage |
| Bookmark https://console.mapbox.com/invoices/ | Confirms $0.00 is still the monthly bill |
| Create a URL-restricted token (see polish step above) | Default token has no leak protection |
| Verify no payment method on file | Belt-and-suspenders: even if the URL restrictions fail, no money moves |
| Optional: ask Claude to wire the client-side load counter | Self-monitoring + auto cap below 40k |

---

Sources:
- [Mapbox pricing](https://www.mapbox.com/pricing)
- [Map loads glossary](https://docs.mapbox.com/help/glossary/map-loads)
- [Token management](https://docs.mapbox.com/accounts/guides/tokens/)
- [URL restrictions blog](https://blog.mapbox.com/url-restrictions-for-access-tokens-5f7f7eb90092)
- [Statistics page docs](https://docs.mapbox.com/accounts/guides/statistics/)
