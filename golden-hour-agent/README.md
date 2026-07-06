# Golden Hour: Racing Disaster Response with Anticipatory AI

**Track:** Agents for Good
**GitHub:** https://github.com/sowmi09/golden-hour

---

## The Problem

When a major disaster strikes, the first hours are the most critical — and also the most chaotic. Rescue teams do not always know where to go first. Aid agencies do not know what is needed or where. Hospitals do not know how many casualties to expect. Transport coordinators do not know which roads are blocked. Public communication officers are scrambling while misinformation spreads on social media.

These questions take hours to answer manually. And by the time a clear picture forms, the most critical window — the golden hour — has already slipped away.

This pattern has repeated across every major disaster in recent years. In the 2023 Turkey-Syria earthquakes, fragmented coordination slowed aid to millions. In the 2026 Venezuela earthquakes, a magnitude 7.5 event struck with no pre-positioned response plan. Different places, different disasters — the same gap between when something happens and when a real coordinated plan gets made.

But Golden Hour is not just for response teams. After every disaster, millions of people want to help — the general public, NGOs, companies, news channels, and government departments — but don't know how to contribute effectively. That gap is equally painful and equally unsolved.

**Golden Hour asks: what if one AI system could serve everyone at once?**

---

## The Key Insight: Not All Disasters Are the Same

Most AI disaster projects make one critical mistake — they treat all disasters as if they can be predicted. They cannot.

Floods, cyclones, and wildfire danger are genuinely forecastable. Rivers rise slowly. Weather models predict storms days ahead. But earthquakes and tsunamis cannot be predicted — no scientist, no government, no AI system on Earth can tell you when or where one will strike.

Golden Hour is built around this honest distinction and operates in two modes:

**Anticipate Mode** — for floods and cyclones. The agent acts on forecast data days before the disaster arrives, drafting pre-event response plans and resource pre-positioning guidance.

**Respond Mode** — for earthquakes and tsunamis. The moment a significant earthquake is detected, the agent pulls USGS PAGER impact data and drafts a situation report within minutes — not a prediction, but a rapid structured response.

This honesty is our biggest differentiator. Existing systems either warn seconds before shaking (ShakeAlert, JMA) or give raw numbers to institutional subscribers (USGS PAGER). Golden Hour fills the gap: turning those numbers into readable, actionable plans — fast, and for anyone.

---

## Who Is This For?

Golden Hour serves five types of users from a single platform:

- **Government Officials and Emergency Managers** — get role-specific action packets with correct local agencies, helplines, and resource activation guidance
- **NDRF/Search & Rescue Commanders** — get deployment priorities, equipment lists, and access route status
- **Hospital and Medical Coordinators** — get expected injury types, casualty estimates, and surge capacity guidance
- **NGOs, Companies, and Volunteers** — get tailored guidance on how to contribute effectively without duplicating government effort
- **News Channels and Media** — get verified facts, correct helplines to broadcast, and misinformation to counter

---

## The Solution: Golden Hour Multi-Agent System

Golden Hour is a multi-agent AI system built using Google's Agent Development Kit (ADK), developed entirely using Antigravity IDE and Antigravity CLI throughout the 5-Day AI Agents Intensive course.

### Agent Architecture

The system has five agents working together:

**root_agent (Orchestrator)**
The entry point for all queries. It collects user registration details (name, country, role) on first interaction, then acts as a security gate rejecting non-disaster queries, and routes to the correct specialist agent based on query type and user role.

**flood_agent (Anticipate Mode)**
Activated for floods, rainfall, and river-related queries. Calls GDACS flood events API and NOAA NWPS for detailed river gauge forecast data. Produces 5 role-specific action packets using correct country-appropriate agencies.

**earthquake_agent (Respond Mode)**
Activated for earthquakes, seismic events, and tsunamis. Calls USGS significant earthquake feed, USGS event detail API for PAGER impact data, and GDACS earthquake events. Never uses the word "predict" — always states post-event estimation.

**cyclone_agent (Anticipate Mode)**
Activated for cyclones, typhoons, hurricanes, and severe storms. Calls GDACS cyclone events API. Produces 5 role-specific packets with meteorological guidance specific to the affected country.

**helper_agent (Public Help Connector)**
Activated when users want to help, donate, volunteer, or coordinate relief. Provides tailored guidance for General Public, NGOs, Companies, News Channels, and Government Officials — connecting helpers with the right channels in the affected country.

### The Five-Packet Output

Every disaster query produces five simultaneous role-specific action packets:

- **Packet 1:** Regional Emergency Commander — decisions, population at risk, resource activation
- **Packet 2:** Search & Rescue Commander — deployment zones, equipment, access routes
- **Packet 3:** Hospital & Medical Coordinator — injury types, casualty estimates, hospitals to activate
- **Packet 4:** Transport & Logistics Coordinator — road damage, alternative routes, helicopter needs
- **Packet 5:** Public Communication Officer — draft advisory, helplines, evacuation guidance

One plain-language input → five simultaneous role-specific action packets in under 30 seconds.

### Country Intelligence

The system automatically detects the country from the location mentioned and uses correct local agencies for every country — NDRF and ASDMA for India, FEMA for USA, NDRRMC for Philippines, FANB and Civil Protection for Venezuela, BASARNAS and BNPB for Indonesia. No hardcoded country lists — the LLM's built-in knowledge is used to identify the right agencies for any of the 196 countries on Earth.

---

## Data Sources

All data sources are free, public, and require no API keys:

| Source | What it provides |
|---|---|
| NOAA National Water Prediction Service | River level forecasts up to 10 days ahead |
| GDACS Flood Events API | Active global flood alerts |
| GDACS Cyclone Events API | Active global tropical cyclone alerts |
| USGS Earthquake GeoJSON Feed | Significant earthquakes, updated in real time |
| USGS Event Detail API | PAGER alert level, estimated fatalities, shaking intensity |
| GDACS Earthquake Events API | Global earthquake coordination data |

---

## Course Concepts Demonstrated

Golden Hour demonstrates four of the six required course concepts:

**1. Multi-Agent System (ADK) — Code**
Five ADK agents: root_agent orchestrates, four specialists handle flood, earthquake, cyclone, and public help. Agent transfer verified in ADK dev-ui trace with routing diagram.

**2. Security Features — Code**
- CONTEXT.md with strict scope and country-detection rules
- Input validation function rejecting non-disaster queries before any API call
- PreToolUse hooks.json for tool execution audit trail
- No API keys stored anywhere in code
- Country-appropriate response teams for every country

**3. Antigravity — Video**
Entire project built using Antigravity IDE and Antigravity CLI — from scaffolding the ADK project with agents-cli, to writing and refining all agent code, to creating the custom skill.

**4. Agent Skills (CLI) — Code**
Custom Antigravity Agent Skill called disaster-report-formatter created at .agents/skills/disaster-report-formatter/SKILL.md, following the progressive disclosure pattern from Day 3. agents-cli used for scaffolding, linting, and testing throughout.

---

## Verified Demo Results

**Demo 1 — Registration Flow**
User says "Hi" → root_agent asks for name, country, role → User provides details → System personalises all subsequent responses based on role and country.

**Demo 2 — Assam Flood (India)**
Query: "What is the flood situation in Assam right now?"
Result: Routed to flood_agent → called GDACS API → produced 5 packets with Indian agencies (ASDMA, NDRF, SDRF), specific districts, correct helplines (1070, 1077). Total latency: under 30 seconds.

**Demo 3 — Venezuela Earthquake**
Query: "Tell me about the Venezuela earthquake June 2026"
Result: Routed to earthquake_agent → autonomously resolved USGS event ID us6000t7zp → fetched PAGER Red alert → produced 5 packets with Venezuelan agencies (FANB, PAHO, Civil Protection, Ven 911). Never used the word "predict."

**Demo 4 — Public Help (NGO)**
Query: "Our NGO wants to help flood victims"
Result: Routed to helper_agent → provided NGO-specific guidance on coordination, approved relief camp zones, inter-agency contacts, what is most needed.

**Demo 5 — Security Gate**
Query: "Why is the sky blue?"
Result: Immediately rejected — "Golden Hour only handles disaster response and relief coordination." No API calls made, zero cost wasted.

---

## What This Project Is NOT

- Does not predict earthquakes — nobody can
- Is not a certified emergency system connected to real response teams
- Is not claimed to have improved any real disaster outcome
- Is a working prototype demonstrating agentic architecture for disaster response and public coordination

---

## Future Roadmap

**Phase 2:** User analytics via Google Sheets — track who uses Golden Hour, from which countries, for which disaster types, to improve the system over time.

**Phase 3:** Public help connector embedded in news channel websites — readers see live disaster status and can directly contribute via verified channels.

**Phase 4:** Government dashboard — real-time supply tracking, damage assessment status, and resource gap identification.

**Phase 5:** India-specific river data integration — once CWC (Central Water Commission) opens their public API, replace NOAA NWPS with granular Indian river gauge data.

---

## The Build Journey

Built entirely using the 5-Day AI Agents Intensive course tools:

- **Day 1:** Antigravity IDE project setup, initial Cloud Run exploration
- **Day 2:** MCP server configuration, Antigravity CLI for all API connections
- **Day 3:** Multi-agent ADK project scaffolded using agents-cli, custom disaster-report-formatter skill created
- **Day 4:** Security features added — CONTEXT.md, hooks.json, input validation, 10 unit tests passing
- **Day 5:** Frontend built, full integration testing, demo verification across 5 disaster scenarios

The key lesson: genuine agentic engineering is not about monitor-and-summarize. It is about autonomous multi-step reasoning — detecting an event, routing to the right specialist, fetching real data, producing role-specific action packets, and connecting helpers — all from a single plain-language input.

---

## GitHub Repository

**https://github.com/sowmi09/golden-hour**

Setup instructions, architecture diagrams, and full implementation documentation in the repository README and IMPLEMENTATION.md files.
