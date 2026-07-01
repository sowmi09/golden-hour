# Golden Hour
**Racing disaster response with anticipatory AI**

> When a major disaster strikes, the first hours are the most critical — and also the most chaotic. Rescue teams don't always know where to go first, aid agencies don't know what's needed or where, and by the time a clear picture forms, valuable time has already been lost. This pattern has repeated across major earthquakes, floods, and storms in recent years — from Turkey-Syria in 2023 to Venezuela in 2026 — different places, same struggle: response that reacts instead of anticipates. This project explores whether an AI agent can change that — fusing live hazard data with population and infrastructure information to predict impact and draft an action plan before the full picture is even confirmed.

**Track:** Agents for Good
**Built for:** Kaggle AI Agents — Intensive Vibe Coding Capstone (2026)

---

## The Problem

Every major disaster follows the same painful pattern. The ground shakes, the river overflows, the fire spreads — and then begins the scramble. Who is affected? How many people? What do they need? Where should help go first?

These questions take hours to answer manually. Aid agencies are still gathering information while the most critical window — the "golden hour" of emergency response — is already slipping away.

This is not a new problem. It happened in the 2023 Turkey-Syria earthquakes, where fragmented coordination slowed aid to millions. It happened in the 2026 Venezuela earthquakes, where a reactive response scrambled to catch up with an event that had already caused widespread destruction. Different places, different disasters — same gap between when something happens and when a real plan gets made.

**Golden Hour asks: what if an AI agent could close that gap?**

---

## The Key Insight — Not All Disasters Are the Same

Here is something most "AI disaster" projects get wrong: they treat all disasters as if they can be predicted. They cannot.

- **Floods, droughts, and wildfire danger** — these CAN be seen coming. Rivers rise slowly. Weather models forecast heavy rainfall days ahead. Drought builds over weeks. There is real, usable lead time here.

- **Earthquakes and tsunamis** — these CANNOT be predicted. No scientist, no government, no AI system on Earth can tell you when or where an earthquake will strike. The only thing technology can do is detect one the second it starts, and react within minutes.

Golden Hour is built around this honest distinction. Instead of pretending all disasters are the same, it operates in two clearly different modes:

### Anticipate Mode — for Floods
When forecast data shows a river is expected to breach danger levels in the next few days, the agent acts immediately — drafting evacuation advisories, resource pre-positioning recommendations, and a response plan *before* the flood even arrives. This is genuine anticipation, days ahead.

### Respond Mode — for Earthquakes and Tsunamis
The moment a significant earthquake is detected, the agent pulls in publicly available impact data — estimated affected population, likely severity, geographic exposure — and drafts a situation report within minutes. Not a prediction. A rapid, structured response to something that has just happened.

**This honesty is our biggest strength.** Existing systems either warn you seconds before shaking (ShakeAlert, JMA) or give you raw numbers for institutions (USGS PAGER). Golden Hour fills the gap in between: it turns those numbers into a readable, actionable written plan — fast, and for anyone, not just licensed institutional subscribers.

---

## Who Is This For?

The people who currently do not get fast, structured response plans:

- Local responders and civil defense teams who are not on USGS/OCHA subscriber lists
- Smaller NGOs coordinating on the ground without access to institutional tools
- Journalists and communicators trying to rapidly understand and report on impact
- Government departments that need a first draft they can refine — not raw data they have to interpret

---

## Where the Data Comes From

Everything Golden Hour uses is free, public, and requires no special access or paid accounts:

| Data | Source | What it provides |
|---|---|---|
| Flood forecasts | NOAA National Water Prediction Service | River level forecasts up to 10 days ahead |
| Global flood forecasts | GloFAS / Open-Meteo | Global river discharge forecasts, no key needed |
| Earthquake impact data | USGS Earthquake GeoJSON + PAGER | Magnitude, location, estimated fatalities/losses, alert level |
| Tsunami alerts | NOAA Tsunami Warning Centers | CAP/ATOM alert feeds, coastal warnings |
| Multi-hazard overview | GDACS (UN/EU) | Unified global disaster alerts, free and keyless |

No private data. No personal information. No paid APIs.

---

## How It Is Different from What Already Exists

| Existing system | What it does | What Golden Hour does differently |
|---|---|---|
| ShakeAlert / JMA / SASMEX | Warns seconds before shaking (after quake starts) | Starts *after* the shaking — drafts the response plan |
| USGS PAGER | Estimates fatalities/losses in numbers for institutions | Converts those numbers into written sitreps and action plans |
| GDACS | Scores disasters for humanitarian coordination teams | Open to anyone; generates readable plans, not just scores |
| UNDAC / OCHA teams | Write rich sitreps manually, over hours | Same output, drafted in minutes as a starting point |
| DisasterResponseGPT (research) | Generates plans from typed scenario descriptions | Automatically grounded in real live data, event-triggered |

**The specific gap we fill:** as of mid-2026, no deployed product or published system takes USGS PAGER/ShakeMap data and uses an AI agent to automatically produce a written situation report and staged action plan. That niche is what Golden Hour occupies.

---

## What This Project Is NOT

Being honest matters more than sounding impressive:

- This does **not** predict earthquakes — nobody can
- This is **not** a certified early-warning system connected to real emergency services
- This is **not** claimed to have saved or improved outcomes in any real disaster
- This is a **working prototype** demonstrating what an agentic architecture can do — built to be extended, not deployed as-is into live operations

The Venezuela and Turkey-Syria disasters are cited as motivation and context, sourced from public reporting. No private or victim data is used. The demo replays a documented past event, not a live crisis.

---

## The Name

The "golden hour" is a term used in emergency medicine — the critical window after a traumatic event when rapid action has the greatest chance of improving outcomes. It is also used by disaster responders to describe the first hours after a sudden-onset event, when the difference between a coordinated response and a chaotic one is most felt.

That window is what this project is designed to protect.
