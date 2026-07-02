# Golden Hour Disaster Response Agent

Golden Hour is an upgraded multi-agent disaster response system designed to serve disaster management teams, NDRF/first responder field commanders, hospital/medical coordinators, transport and logistics teams, and public communication officers. It processes plain-language user queries to produce structured, role-specific action briefs during floods and earthquakes.

---

## How the AI agents work together

Golden Hour uses a three-agent system to coordinate information routing and specialize in disaster types:

- **root_agent**: Acts as the initial security gate and orchestrator. It inspects all incoming plain-language user requests. If the request is not related to a supported natural disaster, it rejects it immediately. Otherwise, it routes the query to the correct specialist agent. It also determines the country context to use the appropriate emergency management authorities.
- **flood_agent**: Operating in *Anticipate Mode*, it queries GDACS and NOAA NWPS tools to assess active flood events and river stage levels, producing a detailed 5-packet disaster brief.
- **earthquake_agent**: Operating in *Respond Mode*, it fetches significant earthquake events from the USGS and active GDACS earthquake feeds, retrieves PAGER details, and produces a structured 5-packet situation assessment.

---

## What the agent actually produces

Whenever a disaster query is processed, the system produces five role-specific, actionable packets:

- **Packet 1 - District / Regional Commander (DDMA / FEMA / NDRRMC)**: Decisions to make, population at risk, priority areas, and evacuation zone resources.
- **Packet 2 - Search & Rescue Field Commander (NDRF / Search & Rescue)**: Deployment priorities, building collapse risks, required search and rescue gear, and access routes.
- **Packet 3 - Hospital & Medical Coordinator**: Expected injuries (waterborne disease, crush syndrome, hypothermia), casualty range estimates, hospital surge activations, and blood bank reserve alerts.
- **Packet 4 - Transport & Logistics Coordinator**: Infrastructure damage assessments, alternative route suggestions, heavy debris removal equipment, and helicopter landing zones.
- **Packet 5 - Public Communication Officer**: Clean public advisories, crucial warnings (such as aftershocks or water safety rules), emergency help numbers, and shelter directions.

---

## Where the data comes from

Golden Hour pulls live information keylessly from five primary, public endpoints:

- **NOAA NWPS**: River stage flow data and forecasts (up to 10 days ahead) for specific gauges.
- **Open-Meteo GloFAS**: Global flood and discharge forecasts.
- **USGS GeoJSON + PAGER**: Significant earthquakes details, magnitude, depth, location, and shaking impact estimations.
- **GDACS Floods**: Active global flood events and alert severity categories.
- **GDACS Earthquakes**: Active global earthquake and seismic events.

---

## Security features

To safeguard disaster response environments, Golden Hour incorporates several security layers:

- **Non-disaster queries are rejected immediately**: Any query not matching disaster topics is caught at the front door.
- **Country detection uses correct local teams**: The system detects the country from the query location to map response briefs to appropriate native agencies (e.g. NDRF in India, FEMA in the USA, NDRRMC in the Philippines), preventing incorrect emergency instructions or phone numbers.
- **No API keys stored in code**: All tool integrations use public, keyless APIs, avoiding credentials leaking.
- **Input validation on all queries**: An input validation gate verifies keywords before initiating any LLM calls or tool lookups.
- **Audit hooks on all tool calls**: Built-in PreToolUse hooks log all tool invocations for compliance and audit trails.

---

## Project Structure

```
golden-hour-agent/
├── .agents/               # Security context policies and event hooks
│   ├── CONTEXT.md             # Security and scope guidelines
│   ├── hooks.json             # Pre-tool audit logs
│   └── skills/                # Custom Antigravity skills
├── app/                   # Core agent code
│   ├── agent.py               # Multi-agent layout, tools, and app wrapper
│   └── app_utils/             # telemetry and typings
├── tests/                 # Unit and integration tests
├── pyproject.toml         # Python environment configuration
└── README.md              # Project documentation
```

---

## Setup Instructions

Run the following commands in your terminal to set up the environment and launch the local web server:

```bash
# Clone the repository
git clone https://github.com/sowmi09/golden-hour
cd golden-hour/golden-hour-agent

# Install dependencies and sync virtualenv
uv sync

# Configure environment variables
set GOOGLE_GENAI_USE_VERTEXAI=False
set GEMINI_API_KEY=your_key_here

# Launch local ADK web server
uv run adk web app --host 127.0.0.1 --port 8080
```
