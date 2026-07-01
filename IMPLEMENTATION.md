# Golden Hour — Implementation Guide
**How we built this, mapped to the 5-Day AI Agents: Intensive Vibe Coding Course with Google**

This document explains the technical implementation of Golden Hour. Each section maps directly to one day of the course, showing how the concepts learned were applied to build a real disaster-response AI agent system.

---

## Day 1 — Project Setup + First Deployment
**Course concepts used: Google Antigravity, AI Studio, Cloud Run**

### What we did for Golden Hour

Everything started here. We used Google Antigravity to create the project workspace and set up the foundation for all agent work that followed.

**Project folder created:**
```bash
$HOME/agy2-projects/golden-hour
```

**Steps followed:**
1. Installed Google Antigravity
2. Created a new project in Antigravity pointing to the `golden-hour` folder
3. Used AI Studio to generate a simple landing page for the project — a plain dashboard showing disaster alert status
4. Deployed that initial UI to Cloud Run to verify the deployment pipeline was working before writing any agent code

**Why this matters for our project:**
Before building any agents, we needed to confirm the full path — from local Antigravity workspace to a live deployed URL — was working. This landing page became the foundation for the final dashboard that shows flood forecasts and earthquake situation reports.

**What was deployed in Day 1:**
A simple static frontend showing:
- Project name: Golden Hour
- Two mode labels: Anticipate Mode (Floods) and Respond Mode (Earthquakes)
- Placeholder cards for upcoming agent output

---

## Day 2 — Connecting Data Sources via MCP
**Course concepts used: MCP Server, Antigravity CLI, Developer Knowledge**

### What we did for Golden Hour

This is where the project's data backbone was built. Instead of connecting to Google Developer Knowledge (the course example), we configured our own MCP server setup to connect Golden Hour's agents to real disaster data APIs.

**MCP configuration file:**
```
~/.gemini/config/mcp_config.json
```

**Data sources connected as MCP tools:**

| Tool Name | Data Source | What it fetches |
|---|---|---|
| `noaa_flood_forecast` | NOAA National Water Prediction Service API | River level forecasts, flood thresholds, up to 10 days ahead |
| `glofas_flood` | Open-Meteo Flood API (GloFAS wrapper) | Global river discharge forecasts, no key required |
| `usgs_earthquake` | USGS Earthquake GeoJSON feed | Live earthquake data, PAGER alert level, magnitude, location |
| `noaa_tsunami` | NOAA Tsunami Warning Center CAP/ATOM feed | Coastal tsunami alerts |
| `gdacs_events` | GDACS multi-hazard API | Unified global disaster event list |

**Antigravity CLI used for:**
- Testing each data source connection interactively before writing agent code
- Verifying that raw API responses were structured correctly
- Running quick one-line prompts to check data flow

```bash
agy -p "Fetch the latest USGS earthquake feed and tell me the highest alert level event in the last 24 hours"
```

**Key learning applied:**
Never hardcode API keys. NOAA, USGS, Open-Meteo, and GDACS are all keyless — no credentials needed. This was confirmed before the project started, so no secrets management was needed for these sources.

---

## Day 3 — Building the Agent Pipeline with ADK + Skills
**Course concepts used: ADK 2.0 multi-agent system, Agents CLI, Antigravity Skills**

### What we did for Golden Hour

This is where the actual agent architecture was built. We used ADK 2.0 graph workflows to create two separate multi-agent pipelines — one for Anticipate Mode (floods) and one for Respond Mode (earthquakes).

### Setup

```bash
uvx google-agents-cli setup
```

Authentication:
```bash
export GEMINI_API_KEY="your_key_here"
export GOOGLE_GENAI_USE_ENTERPRISE=FALSE
```

### Anticipate Mode Pipeline (Floods)

Scaffolded using Agents CLI as a graph workflow agent called `flood-anticipation-agent`:

```
Prompt used in Antigravity:
"Use ADK 2.0 to create a graph workflow agent called flood-anticipation-agent.
The workflow should:
1. Fetch flood forecast data from NOAA NWPS for a given river gauge ID
2. Check if any forecast values exceed the flood stage threshold
3. If yes, estimate the likely affected population using nearby area data
4. Draft a pre-event action plan with recommended actions and timeline
5. If no threshold is exceeded, return a clear-status report"
```

**Agents in this pipeline:**
- `WatcherAgent` — fetches NOAA forecast data (LlmAgent calling `noaa_flood_forecast` tool)
- `ThresholdAgent` — pure Python function node checking forecast vs. flood stage (deterministic, no LLM)
- `PlannerAgent` — LlmAgent drafting the action plan when threshold is exceeded
- `ReportAgent` — LlmAgent writing the final clear-status or alert report

### Respond Mode Pipeline (Earthquakes)

Scaffolded as `earthquake-response-agent`:

```
Prompt used in Antigravity:
"Use ADK 2.0 to create a graph workflow agent called earthquake-response-agent.
The workflow should:
1. Fetch the latest significant earthquake from the USGS feed
2. Extract the PAGER alert level, magnitude, and estimated impact
3. Draft a situation report in plain language
4. Include recommended immediate response actions based on alert level
5. Be honest that this is post-event estimation, not prediction"
```

**Agents in this pipeline:**
- `DetectorAgent` — fetches USGS GeoJSON feed (LlmAgent calling `usgs_earthquake` tool)
- `ImpactAgent` — extracts PAGER data and structures it (function node, deterministic)
- `SitRepAgent` — LlmAgent writing the situation report and response plan

### Skills created for Golden Hour

Two custom Antigravity Skills were built to package reusable instructions:

**Skill 1: `disaster-report-formatter`**
```
golden-hour/.agents/skills/disaster-report-formatter/
├── SKILL.md          ← instructions for consistent report structure
└── resources/
    └── REPORT_TEMPLATE.md   ← standard situation report format
```
This skill ensures every SitRep Agent output follows a consistent structure: Event Summary → Estimated Impact → Recommended Actions → Data Sources → Uncertainty Disclaimer.

**Skill 2: `data-source-verifier`**
```
golden-hour/.agents/skills/data-source-verifier/
├── SKILL.md          ← instructions to always cite data source and timestamp
└── examples/
    ├── good_citation.md
    └── bad_citation.md
```
This skill enforces that every number the agent produces is grounded in actual fetched data, not hallucinated.

### Linting and local testing

```bash
agents-cli lint
agents-cli playground
```

Test prompts used:
```text
Run the flood anticipation agent for river gauge USGS-03290500
```
```text
Run the earthquake response agent for the most recent red-alert event
```

---

## Day 4 — Security, Human-in-the-Loop, and Evaluation
**Course concepts used: Security features, STRIDE threat modeling, human-in-the-loop, local evaluation**

### What we did for Golden Hour

Disaster response is a sensitive domain. A wrong number, a hallucinated casualty estimate, or a leaked data source could cause real harm. Day 4's security concepts were applied directly to Golden Hour.

### Secure project context

```
golden-hour/.agents/CONTEXT.md
```

Rules added:
- Every report must cite its exact data source and fetch timestamp
- No numbers may be stated without a fetched source backing them
- Every situation report must include an explicit uncertainty disclaimer
- The words "predict" and "forecast" must only be used for flood/weather data, never for earthquakes

### Static analysis with Semgrep

```
golden-hour/.semgrep/rules.yaml
```

Custom rule added: flag any hardcoded string starting with `AIzaSy` (Google API key prefix). Since our data sources are keyless, any key appearing in code is a mistake.

```
golden-hour/.pre-commit-config.yaml
```
Pre-commit hook configured to run the Semgrep scan before every commit.

### Agent execution hook

```
golden-hour/.agents/hooks.json
```

`PreToolUse` hook configured to intercept any tool call that would write to an external system — since Golden Hour only reads from public APIs, any write operation is unexpected and should be blocked.

### STRIDE threat model

Local skill created:
```
golden-hour/.agents/skills/stride-threat-model/SKILL.md
```

Running this skill generated `threat_model.md` covering:
- **Spoofing:** fake USGS/NOAA responses injected via network
- **Tampering:** modified disaster data between API and agent
- **Repudiation:** agent producing reports with no audit trail
- **Information disclosure:** sensitive location data in prompts
- **Denial of service:** API rate limits blocking time-critical fetches
- **Elevation of privilege:** agent gaining unintended write access

### Human-in-the-loop

For Red alert level earthquakes (PAGER orange or red), a `RequestInput` node was added before the SitRep is finalized:

```
Expected behavior:
- Green/Yellow PAGER alerts: agent auto-completes the situation report
- Orange/Red PAGER alerts: agent drafts the report but pauses for human review before output
```

This prevents a hallucinated high-severity report from being published without a human check.

### Local evaluation

Evaluation dataset created at:
```
golden-hour/tests/eval/datasets/basic-dataset.json
```

Scenarios scored by LLM-as-judge:
- Does the flood report correctly identify threshold breaches?
- Does the earthquake report correctly reflect the PAGER alert level?
- Is the uncertainty disclaimer present in every report?
- Are all numbers grounded in cited data?
- Does the agent refuse to use the word "predict" for earthquake events?

---

## Day 5 — Cloud Deployment and Full Pipeline
**Course concepts used: Agent Runtime deployment, Cloud Run frontend, Pub/Sub event pipeline, deployability**

### What we did for Golden Hour

The final step was taking the locally-tested agents and deploying them to Google Cloud so the full end-to-end pipeline runs in the cloud.

### Dependency lock and dry-run

```bash
uv lock
agents-cli deploy --dry-run
```

### Deployment to Agent Runtime

```bash
agents-cli deploy --project YOUR_PROJECT_ID --region us-west1
```

Both pipelines deployed:
- `flood-anticipation-agent` → Agent Runtime
- `earthquake-response-agent` → Agent Runtime

### Frontend dashboard on Cloud Run

A FastAPI dashboard was built and deployed to Cloud Run:

**Endpoints:**
- `GET /` — main dashboard showing latest flood forecasts and recent earthquake situation reports
- `GET /api/flood-status` — latest Anticipate Mode output
- `GET /api/earthquake-status` — latest Respond Mode output
- `POST /api/review/{session_id}` — human approval endpoint for orange/red PAGER events

### Event pipeline via Pub/Sub

A Pub/Sub topic `disaster-events` was created. External triggers (or a scheduled job) publish events to this topic, which pushes directly to the Agent Runtime agents — no intermediate service needed.

**Low-severity flood event (auto-completes):**
```json
{"type": "flood", "gauge_id": "USGS-03290500", "mode": "anticipate"}
```

**High-severity earthquake event (pauses for human review):**
```json
{"type": "earthquake", "alert_level": "red", "mode": "respond"}
```

### Final deployed architecture

```
[Pub/Sub Topic: disaster-events]
        ↓ push
[Agent Runtime]
   ├── flood-anticipation-agent  →  auto-completes  →  dashboard
   └── earthquake-response-agent
           ├── green/yellow  →  auto-completes  →  dashboard
           └── orange/red    →  pauses → human review via dashboard → resumes
        ↓
[Cloud Run: Golden Hour Dashboard]
        ↓
[Public HTTPS URL for judges to access]
```

### APIs enabled in Google Cloud

- `aiplatform.googleapis.com`
- `run.googleapis.com`
- `pubsub.googleapis.com`
- `cloudbuild.googleapis.com`
- `cloudtrace.googleapis.com`

---

## Course Concepts Demonstrated — Summary

| Concept | Where | How |
|---|---|---|
| **Multi-agent system (ADK)** | Code | Two ADK graph workflow pipelines: `flood-anticipation-agent` and `earthquake-response-agent`, each with 3-4 specialist agents |
| **MCP Server** | Code | Five disaster data APIs wrapped as MCP tools in `mcp_config.json` |
| **Antigravity** | Video | Used throughout — project creation, agent scaffolding, skills, CLI testing |
| **Security features** | Code | `CONTEXT.md` rules, Semgrep, pre-commit hooks, agent execution hooks, STRIDE threat model, human-in-the-loop for high-severity events |
| **Deployability** | Video | Agent Runtime deployment, Cloud Run dashboard, Pub/Sub event pipeline |
| **Agent skills** | Code | Two custom skills: `disaster-report-formatter` and `data-source-verifier` |

All six course concepts are demonstrated. Minimum requirement was three.

---

## Setup Instructions

### Prerequisites
- Python 3.11+
- `uv` installed
- Google Antigravity installed
- A Google Cloud project (for deployment only — local testing needs no cloud)
- No paid API keys needed for data sources

### Run locally

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/golden-hour
cd golden-hour

# 2. Install dependencies
uv sync

# 3. Set up authentication
export GEMINI_API_KEY="your_key_here"
export GOOGLE_GENAI_USE_ENTERPRISE=FALSE

# 4. Install agents-cli
uvx google-agents-cli setup

# 5. Run the flood agent locally
agents-cli playground

# 6. Test with a sample prompt
agents-cli run "Run flood anticipation for gauge USGS-03290500"
```

### Deploy to cloud

```bash
uv lock
agents-cli deploy --dry-run
agents-cli deploy --project YOUR_PROJECT_ID --region us-west1
```

---

## Important Notes

- No API keys or secrets are stored in this repository
- All disaster data sources (NOAA, USGS, Open-Meteo, GDACS) are free and keyless
- Orange/Red PAGER earthquake events always require human review before a situation report is published
- All agent outputs include a data source citation and uncertainty disclaimer
- The word "predict" is never used for earthquake events — only for floods where genuine forecast data exists
