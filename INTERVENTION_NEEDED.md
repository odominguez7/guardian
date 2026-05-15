# Intervention needed — Ops Center secrets

When you're back, two tokens unlock the full Ops Center experience. Without them, the page deploys + the event firehose + demo scenarios work, but:

- **Map shows a "MAPBOX_TOKEN needed" placeholder** instead of the live map
- **Toolbar shows "Anonymous demo · Firebase Auth not configured"** instead of Google sign-in

Paste two values + run one command + everything lights up.

---

## 1. Mapbox token (5 min)

The actually-fast path:

1. Open https://account.mapbox.com/access-tokens/ in your browser
2. Sign in with Google (no Mapbox account needed; OAuth works)
3. The default public token is already there. Copy it (starts with `pk.`)
4. Tell me the token in chat OR run this yourself:

```bash
export MAPBOX_TOKEN="pk.your-token-here"
```

That's it for Mapbox. Free tier = 50k map loads/month, more than enough for the demo + a week of judge clicks.

---

## 2. Firebase project + Google sign-in (15 min)

The actually-fast path:

1. Open https://console.firebase.google.com/project/guardian-gfs-2026/overview
   (this auto-attaches Firebase to our existing GCP project — no new project needed)
2. If it asks "Add Firebase to your existing Google Cloud project" → click it through
3. In the left sidebar, click **Build → Authentication**
4. Click **Get started** → enable the **Google** sign-in provider (one toggle + a support email)
5. In the Firebase console settings (gear icon top-left, then Project Settings), scroll to **Your apps**
6. Click the web icon `</>` → register app name `guardian-ops-center` → copy the config snippet

You'll get something like:

```js
const firebaseConfig = {
  apiKey: "AIzaSy...",
  authDomain: "guardian-gfs-2026.firebaseapp.com",
  projectId: "guardian-gfs-2026",
  appId: "1:180171737110:web:abc123...",
};
```

Tell me the 4 values in chat OR set them yourself:

```bash
export FIREBASE_API_KEY="AIzaSy..."
export FIREBASE_AUTH_DOMAIN="guardian-gfs-2026.firebaseapp.com"
export FIREBASE_PROJECT_ID="guardian-gfs-2026"
export FIREBASE_APP_ID="1:180171737110:web:abc123..."
```

---

## 3. Re-deploy the Ops Center with the values baked in

After the env vars are set:

```bash
cd ~/Desktop/GFS\ -\ Agents\ Hackathon
make deploy-ops-center
```

That's it. Page now has the live Mapbox map + working Google sign-in.

---

## What you can do RIGHT NOW without these secrets

Even without Mapbox/Firebase, the demo works. The flow:

1. Open the Ops Center URL (printed after `make deploy-ops-center` finishes)
2. You'll see toolbar + event stream + incident panel + "MAPBOX_TOKEN needed" placeholder where the map would be
3. Click any scenario button in the toolbar
4. The event stream + incident panel light up in real time
5. The ranger dispatch card + TNFD filing card appear when the peers ack

The map is the cherry on top; the real demo cinema works without it.
