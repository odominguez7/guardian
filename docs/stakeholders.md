# GUARDIAN stakeholders — name-aligned map

_Locked 2026-05-17. Source of truth for who's who in the demo, PLAN.md, and the Marketplace listing. Use these names verbatim. Don't invent new variants._

_Companion: `docs/stakeholder_lingo_2026.md` is the demo-voice lingo guide (audience-facing labels + first-mention acronym spell-outs). Read both._

---

---

## The two stakeholder rings

GUARDIAN serves two distinct rings of stakeholders. The product story changes depending on who you're talking to.

### Ring 1 — Customers (the money)

Fortune 500 corporate sustainability buyers. They pay the bills. Compliance pressure is the forcing function.

| Canonical name | Aka / persona | What they want | What GUARDIAN gives them |
|---|---|---|---|
| **F500 sustainability buyer** | "Maya Chen, CSO at a top-10 consumer goods F500" | TNFD/CSRD filings their Big-4 auditor will sign off on; board-deck slides; ESG rating uplift; litigation defense | The Sponsor Sustainability A2A peer files TNFD entries on their behalf, auto-generates the board slide, anchors evidence with SHA-256 chain of custody. Court-Evidence bundle survives auditor scrutiny. |

### Ring 2 — Field operators (the impact)

Conservation operators who use the system to actually protect wildlife. They don't pay (yet); they validate the technology works.

| Canonical name | Aka / persona | What they want | What GUARDIAN gives them |
|---|---|---|---|
| **Park Authority** | National park / reserve operator (e.g., Tanzania Parks for Selous; KWS for Maasai Mara) | Faster ranger dispatch; lower false-positive rate; coordination with adjacent parks; audit trail of incidents | Park Service A2A peer takes orchestrator dispatch, returns ranger unit ID + ETA. Audit log goes back to the funder + sponsor. |
| **Funder Reporter** | A program officer / impact lead / reporting lead inside a conservation funder, wildlife NGO, or philanthropic program (e.g., WWF / IUCN — examples only, not canonical) | Quarterly impact reports without raw access to park data; receipts proving their money produced outcomes | Funder Reporter A2A peer auto-emits per-incident impact entries tagged by funder program. |
| **Neighbor Park** | Adjacent reserve (e.g., Maasai Mara when Selous is the origin) | Mutual-aid handoff during chase events; cross-border coordination | Neighbor Park A2A peer accepts handoff requests with corridor + species + window. |

### Ring 3 — Judges (the prize evaluators)

Not paying customers — but they're the audience for this submission. Their rubric defines what "winning" looks like.

| Canonical name | What they care about |
|---|---|
| **Google for Startups AI Agents Challenge judges** | Technical 30% / Business Case 30% / Innovation 20% / Demo 20%. Track 3: A2A interop is mandatory. Marketplace-ready is mandatory. |

---

## The agent ↔ stakeholder map

Which agent serves which stakeholder? This is the alignment that the demo needs to make legible.

```
                  ┌──────────────────────────────────────────────────┐
                  │           GUARDIAN ORCHESTRATOR                  │
                  │   (our service, ADK, Gemini 2.5 Pro)             │
                  └─────┬──────┬──────┬──────┬──────┬──────┬─────────┘
                        │      │      │      │      │      │
            ┌───────────┘      │      │      │      │      └───────────┐
            ▼                  ▼      ▼      ▼      ▼                  ▼
       ┌─────────┐        ┌────────┐ ┌─────┐ ┌──────┐ ┌──────────┐ ┌──────────┐
       │ Stream  │        │ Audio  │ │Spec │ │Court │ │Falsifier │ │Dispatch  │
       │ Watcher │        │ Agent  │ │ ID  │ │Evid. │ │ (NEW)    │ │ (stub)   │
       └─────────┘        └────────┘ └─────┘ └──────┘ └──────────┘ └──────────┘
                                                          │
                                                          │ (dissent record)
                                                          ▼
       ╔══════════════════════════════════════════════════════════════════╗
       ║       A2A PEERS (independent services, own agent.json, mTLS)     ║
       ╚══════════════════════════════════════════════════════════════════╝
            ▲                  ▲                       ▲                  ▲
            │                  │                       │                  │
       ┌────┴─────┐      ┌─────┴────────┐     ┌────────┴──────┐    ┌──────┴─────┐
       │   Park   │      │   Sponsor    │     │    Funder     │    │  Neighbor  │
       │ Service  │      │Sustainability│     │   Reporter    │    │    Park    │
       │  agent   │      │    agent     │     │     agent     │    │    agent   │
       └────┬─────┘      └──────┬───────┘     └──────┬────────┘    └─────┬──────┘
            │                   │                    │                   │
            ▼                   ▼                    ▼                   ▼
       ┌─────────┐        ┌────────────┐      ┌──────────────┐     ┌──────────┐
       │  PARK   │        │    F500    │      │   FUNDER     │     │ NEIGHBOR │
       │AUTHORITY│        │  BUYER     │      │ (NGO/philan- │     │   PARK   │
       │(operator)│       │ (customer) │      │  thropic)    │     │(operator)│
       │ Ring 2  │        │   Ring 1   │      │  (operator)  │     │  Ring 2  │
       │         │        │            │      │   Ring 2     │     │          │
       └─────────┘        └────────────┘      └──────────────┘     └──────────┘
```

---

## Naming rules (must be enforced in PLAN.md, segments.json, marketplace listing, README)

- **Customer ring** ALWAYS called **"F500 sustainability buyer"** or **"Sponsor Sustainability"** in product surfaces. Never "F500 sponsor" alone (ambiguous), never "corporate sustainability officer" (too long for cards).
- **Park ring** ALWAYS called **"Park Authority"** or **"Park Service"** (service = the A2A agent; authority = the human/org). Never "Park Service Operations" except in tool returns.
- **Funder ring** ALWAYS called **"Funder Reporter"**. Never "WWF" or "IUCN" explicitly in card titles (those are example operators, not the canonical role).
- **Neighbor ring** ALWAYS called **"Neighbor Park"**. Never "Mutual Aid" alone (that's the *protocol*, not the *peer*).
- **Adversarial agent** ALWAYS called **"Falsifier"** in product UI / cards / VO. Never "red team," "auditor," "challenger" in the demo (taste / consistency).
- **System name** ALWAYS **"GUARDIAN"** (all caps, no hyphens, no spaces). The product is GUARDIAN; the company is "GuardIAn Wildlife" — that's only used in producer credit on the close card.

---

## Score-relevant story per audience

When writing demo VO / cards / Marketplace copy, mirror these phrasings:

### To a F500 buyer (Chief Sustainability Officer, Head of Sustainability, or ESG Reporting Lead — "Maya CSO" persona for short):
> "GUARDIAN's Sponsor Sustainability agent files your Taskforce on Nature-related Financial Disclosures (TNFD) entry the moment an incident is detected. Mapped to European Sustainability Reporting Standard E4: Biodiversity and Ecosystems (ESRS E4). Anchored to a Secure Hash Algorithm 256-bit (SHA-256) chain of custody that survives a Big Four audit. Your board slide auto-generates."

### To a Google judge (ADK/A2A):
> "GUARDIAN ships four discoverable A2A peers — Park, Sponsor, Funder, Neighbor — each in a separate Cloud Run service with a public agent.json. The orchestrator fans out via A2A protocol v0.3.0. The Falsifier agent challenges every dispatch on Gemini 2.5 Flash; dissent is logged into the Court-Evidence bundle."

### To any human:
> "Cameras and microphones in wildlife reserves catch poaching threats in real time. AI agents confirm what they're seeing, argue about whether to act, and dispatch park rangers. Every action is recorded so the company sponsoring the protection has proof their money is working."
