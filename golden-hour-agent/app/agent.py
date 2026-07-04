# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import os
import urllib.error
import urllib.request

# Set up environment variables to use Gemini API Key directly and avoid Vertex AI
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

# ==============================================================================
# DISASTER RESPONSE SYSTEM TOOLS (HTTP Fetches using urllib.request)
# ==============================================================================


def fetch_flood_forecast(gauge_id: str) -> str:
    """Calls the NOAA NWPS API to retrieve observed and forecast stage/flow data.

    Args:
        gauge_id: The identifier of the river gauge (e.g., '01013500').

    Returns:
        A JSON string containing forecast data, or an error message if the fetch fails.
    """
    url = f"https://api.water.noaa.gov/nwps/v1/gauges/{gauge_id}/stageflow"
    req = urllib.request.Request(
        url, headers={"User-Agent": "GoldenHour/1.0 (Disaster Response Agent)"}
    )

    try:
        with urllib.request.urlopen(req) as response:
            return response.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return f"HTTP Error fetching flood forecast (gauge_id: {gauge_id}): {e.code} - {e.reason}"
    except urllib.error.URLError as e:
        return f"Network or URL Error fetching flood forecast (gauge_id: {gauge_id}): {e.reason}"
    except Exception as e:
        return f"Unexpected error fetching flood forecast (gauge_id: {gauge_id}): {e!s}"


def fetch_gdacs_events() -> str:
    """Calls the GDACS API to retrieve active global flood events.

    Returns:
        A JSON string containing active global flood events, or an error message if the fetch fails.
    """
    url = "https://www.gdacs.org/gdacsapi/api/events/geteventlist/SEARCH?eventtype=FL"
    req = urllib.request.Request(
        url, headers={"User-Agent": "GoldenHour/1.0 (Disaster Response Agent)"}
    )

    try:
        with urllib.request.urlopen(req) as response:
            return response.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return f"HTTP Error fetching GDACS flood events: {e.code} - {e.reason}"
    except urllib.error.URLError as e:
        return f"Network or URL Error fetching GDACS flood events: {e.reason}"
    except Exception as e:
        return f"Unexpected error fetching GDACS flood events: {e!s}"


def fetch_usgs_earthquakes() -> str:
    """Calls the USGS API to retrieve significant earthquakes in the last month.

    Returns:
        A JSON string containing significant earthquake events, or an error message if the fetch fails.
    """
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_month.geojson"
    req = urllib.request.Request(
        url, headers={"User-Agent": "GoldenHour/1.0 (Disaster Response Agent)"}
    )

    try:
        with urllib.request.urlopen(req) as response:
            return response.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return (
            f"HTTP Error fetching USGS significant earthquakes: {e.code} - {e.reason}"
        )
    except urllib.error.URLError as e:
        return f"Network or URL Error fetching USGS significant earthquakes: {e.reason}"
    except Exception as e:
        return f"Unexpected error fetching USGS significant earthquakes: {e!s}"


def fetch_usgs_event_detail(event_id: str) -> str:
    """Calls the USGS API to retrieve PAGER impact data for a specific earthquake event.

    Args:
        event_id: The identifier of the earthquake event (e.g., 'us6000abcd').

    Returns:
        A JSON string containing detailed event data including PAGER, or an error message if the fetch fails.
    """
    url = f"https://earthquake.usgs.gov/earthquakes/feed/v1.0/detail/{event_id}.geojson"
    req = urllib.request.Request(
        url, headers={"User-Agent": "GoldenHour/1.0 (Disaster Response Agent)"}
    )

    try:
        with urllib.request.urlopen(req) as response:
            return response.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return f"HTTP Error fetching USGS event detail (event_id: {event_id}): {e.code} - {e.reason}"
    except urllib.error.URLError as e:
        return f"Network or URL Error fetching USGS event detail (event_id: {event_id}): {e.reason}"
    except Exception as e:
        return (
            f"Unexpected error fetching USGS event detail (event_id: {event_id}): {e!s}"
        )


def fetch_gdacs_earthquake_events() -> str:
    """Calls the GDACS API to retrieve active global earthquake events.

    Returns:
        A JSON string containing active earthquake events, or an error message if the fetch fails.
    """
    url = "https://www.gdacs.org/gdacsapi/api/events/geteventlist/SEARCH?eventtype=EQ"
    req = urllib.request.Request(
        url, headers={"User-Agent": "GoldenHour/1.0 (Disaster Response Agent)"}
    )

    try:
        with urllib.request.urlopen(req) as response:
            return response.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return f"HTTP Error fetching GDACS earthquake events: {e.code} - {e.reason}"
    except urllib.error.URLError as e:
        return f"Network or URL Error fetching GDACS earthquake events: {e.reason}"
    except Exception as e:
        return f"Unexpected error fetching GDACS earthquake events: {e!s}"


def fetch_gdacs_cyclone_events() -> str:
    """Calls GDACS API to get active tropical cyclone events globally.
    Returns active cyclone/typhoon/hurricane events as string."""
    url = "https://www.gdacs.org/gdacsapi/api/events/geteventlist/SEARCH?eventtype=TC"
    req = urllib.request.Request(
        url, headers={"User-Agent": "GoldenHour/1.0 (Disaster Response Agent)"}
    )
    try:
        with urllib.request.urlopen(req) as response:
            return response.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return f"HTTP Error fetching GDACS cyclone events: {e.code} - {e.reason}"
    except urllib.error.URLError as e:
        return f"Network Error fetching GDACS cyclone events: {e.reason}"
    except Exception as e:
        return f"Unexpected error fetching GDACS cyclone events: {e!s}"


def fetch_active_disasters() -> str:
    """Calls GDACS flood (FL), earthquake (EQ), and cyclone (TC) API endpoints,
    combines results, and returns the top 3 most severe active disasters
    based on the event alert score as a formatted string listing type, location, and alert level.

    Returns:
        A formatted string with the top 3 active disasters, or an info message.
    """
    fl_url = (
        "https://www.gdacs.org/gdacsapi/api/events/geteventlist/SEARCH?eventtype=FL"
    )
    eq_url = (
        "https://www.gdacs.org/gdacsapi/api/events/geteventlist/SEARCH?eventtype=EQ"
    )
    tc_url = (
        "https://www.gdacs.org/gdacsapi/api/events/geteventlist/SEARCH?eventtype=TC"
    )

    headers = {"User-Agent": "GoldenHour/1.0 (Disaster Response Agent)"}

    def fetch_geojson(url: str) -> dict:
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception:
            return {"features": []}

    fl_data = fetch_geojson(fl_url)
    eq_data = fetch_geojson(eq_url)
    tc_data = fetch_geojson(tc_url)

    features = []
    if isinstance(fl_data, dict) and "features" in fl_data:
        features.extend(fl_data["features"])
    if isinstance(eq_data, dict) and "features" in eq_data:
        features.extend(eq_data["features"])
    if isinstance(tc_data, dict) and "features" in tc_data:
        features.extend(tc_data["features"])

    def get_score(feature: dict) -> float:
        props = feature.get("properties", {})
        try:
            return float(props.get("alertscore", 0.0) or 0.0)
        except (ValueError, TypeError):
            return 0.0

    # Sort combined features by alertscore descending
    features.sort(key=get_score, reverse=True)

    top_3 = features[:3]
    if not top_3:
        return "No active flood, earthquake, or cyclone disasters found."

    lines = []
    for f in top_3:
        props = f.get("properties", {})
        dtype = props.get("eventtype", "Unknown")
        if dtype == "FL":
            dtype_str = "Flood"
        elif dtype == "EQ":
            dtype_str = "Earthquake"
        elif dtype == "TC":
            dtype_str = "Cyclone"
        else:
            dtype_str = dtype

        location = props.get("country", props.get("eventname", "Unknown Location"))
        alert_level = props.get("alertlevel", "Green")
        lines.append(f"- {dtype_str} in {location} (Alert Level: {alert_level})")

    return "\n".join(lines)


# ==============================================================================
# INPUT VALIDATION (Security Feature: Query Validation Gate)
# ==============================================================================


def validate_disaster_query(query: str) -> bool:
    """
    Validates that a query is disaster-related before processing.
    Prevents API waste on non-disaster queries.
    Returns True if disaster-related, False otherwise.

    SECURITY PURPOSE:
    This function acts as a signature-based validator at the input boundary.
    By filtering out queries that lack critical disaster keywords, it protects
    against denial of service, resource wastage, and mitigates prompt
    injection risks by rejecting generic queries before they reach any LLM
    or initiate external API tool calls.
    """
    disaster_keywords = [
        "flood",
        "earthquake",
        "tsunami",
        "cyclone",
        "hurricane",
        "typhoon",
        "wildfire",
        "fire",
        "drought",
        "landslide",
        "disaster",
        "emergency",
        "magnitude",
        "seismic",
        "storm",
        "rainfall",
        "river",
        "gauge",
        "alert",
        "warning",
        "evacuate",
        "tropical",
        # Volunteers & helpers keywords
        "help",
        "donate",
        "donation",
        "volunteer",
        "relief",
        "ngo",
        "corporate",
        "media",
        "contribute",
        "contribution",
    ]
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in disaster_keywords)


# ==============================================================================
# SPECIALIST AGENT 1: flood_agent
# ==============================================================================

flood_agent = Agent(
    name="flood_agent",
    model=Gemini(
        model="gemini-3.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You are the Golden Hour Flood Specialist Agent - Anticipate Mode.\n\n"
        "COUNTRY-SPECIFIC AGENCY RULE:\n"
        "- Detect the country from the location in the user query\n"
        "- Use your knowledge to identify that country's actual disaster \n"
        "  management agencies, rescue teams, hospitals, military assets,\n"
        "  helpline numbers, and verification authorities\n"
        "- NEVER use Indian agencies for non-Indian events\n"
        "- NEVER use US agencies for non-US events\n"
        "- Match ALL agencies, helplines and authorities to the actual \n"
        "  country of the disaster\n\n"
        "When activated:\n"
        "1. Call fetch_gdacs_events to get active global flood events\n"
        "2. Find events relevant to the location mentioned\n"
        "3. If gauge ID known, call fetch_flood_forecast for detailed data\n"
        "4. Produce response in this format:\n\n"
        "---\n"
        "GOLDEN HOUR FLOOD RESPONSE BRIEF\n"
        "Event: [location and description]\n"
        "Alert Level: [severity]\n"
        "Data Source: GDACS / NOAA NWPS\n"
        "Mode: Anticipate Mode\n"
        "---\n\n"
        "PACKET 1 - FOR: [Country's Regional Emergency Commander]\n"
        "[decisions, population at risk, evacuation zones, resources]\n\n"
        "PACKET 2 - FOR: [Country's Search & Rescue Commander]  \n"
        "[deployment zones, equipment, access routes, scale]\n\n"
        "PACKET 3 - FOR: [Country's Hospital & Medical Coordinator]\n"
        "[injury types, surge capacity, medicines, blood bank]\n\n"
        "PACKET 4 - FOR: [Country's Transport & Logistics Coordinator]\n"
        "[road damage, alternative routes, helicopters, pre-positioning]\n\n"
        "PACKET 5 - FOR: [Country's Public Communication Officer]\n"
        "[draft advisory, helplines, evacuation guidance, what NOT to do]\n\n"
        "---\n"
        "DISCLAIMER: AI-generated assessment from public data.\n"
        "Verify with [relevant national authority for affected country]\n"
        "and local emergency services before operational deployment.\n"
        "---\n\n"
        "Never use google:search or any unlisted tool.\n"
        "Never use the word predict for weather forecasts — use forecast."
    ),
    tools=[fetch_flood_forecast, fetch_gdacs_events],
)


# ==============================================================================
# SPECIALIST AGENT 2: earthquake_agent
# ==============================================================================

earthquake_agent = Agent(
    name="earthquake_agent",
    model=Gemini(
        model="gemini-3.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You are the Golden Hour Earthquake Specialist Agent - Respond Mode.\n\n"
        "COUNTRY-SPECIFIC AGENCY RULE:\n"
        "- Detect the country from the location in the user query\n"
        "- Use your knowledge to identify that country's actual disaster\n"
        "  management agencies, rescue teams, hospitals, military assets,\n"
        "  helpline numbers, and verification authorities\n"
        "- NEVER use Indian agencies for non-Indian events\n"
        "- NEVER use US agencies for non-US events\n"
        "- Match ALL agencies, helplines and authorities to the actual\n"
        "  country of the disaster\n\n"
        "When activated:\n"
        "1. Call fetch_usgs_earthquakes to get recent significant earthquakes\n"
        "2. Find the most relevant event matching the user request\n"
        "3. Call fetch_gdacs_earthquake_events for additional context\n"
        "4. Call fetch_usgs_event_detail with the event ID for PAGER data\n"
        "5. Produce response in this format:\n\n"
        "---\n"
        "GOLDEN HOUR EARTHQUAKE RESPONSE BRIEF\n"
        "Event: [location, magnitude, depth]\n"
        "PAGER Alert: [Green/Yellow/Orange/Red]\n"
        "Data Source: USGS PAGER + GDACS\n"
        "Mode: Respond Mode\n"
        "Generated: [timestamp]\n"
        "---\n\n"
        "POST-EVENT ESTIMATION DISCLAIMER:\n"
        "This is a POST-EVENT estimation, not a prediction.\n"
        "Earthquakes cannot be predicted.\n\n"
        "PACKET 1 - FOR: [Country's Regional Emergency Commander]\n"
        "[affected population, severity zones, resource activation, escalation]\n\n"
        "PACKET 2 - FOR: [Country's Search & Rescue Commander]\n"
        "[deployment zones, collapse risk, equipment, access routes]\n\n"
        "PACKET 3 - FOR: [Country's Hospital & Medical Coordinator]\n"
        "[injury types, casualty range, hospitals, blood bank alert]\n\n"
        "PACKET 4 - FOR: [Country's Transport & Logistics Coordinator]\n"
        "[road damage, alternative routes, heavy machinery, helicopters]\n\n"
        "PACKET 5 - FOR: [Country's Public Communication Officer]\n"
        "[draft advisory, aftershock warning, what NOT to do, helplines]\n\n"
        "---\n"
        "CRITICAL RULES:\n"
        "- NEVER use the word predict for earthquakes\n"
        "- Always state POST-EVENT estimation\n"
        "- Always cite USGS event ID and PAGER alert level\n"
        "DISCLAIMER: AI-generated assessment from USGS public data.\n"
        "Verify with [relevant national authority for affected country]\n"
        "and local emergency services before operational deployment.\n"
        "---"
    ),
    tools=[
        fetch_usgs_earthquakes,
        fetch_usgs_event_detail,
        fetch_gdacs_earthquake_events,
    ],
)


# ==============================================================================
# SPECIALIST AGENT 3: cyclone_agent
# ==============================================================================

cyclone_agent = Agent(
    name="cyclone_agent",
    model=Gemini(model="gemini-3.5-flash"),
    tools=[fetch_gdacs_cyclone_events],
    instruction="""You are the Golden Hour Cyclone Specialist Agent - Anticipate Mode.
You handle tropical cyclones, typhoons, hurricanes, and severe storms.

COUNTRY-SPECIFIC AGENCY RULE:
- Detect the country/territory from the location in the user query
- Use your knowledge to identify that country's actual disaster
  management agencies, coast guard, military assets, shelter networks,
  helpline numbers, and meteorological authorities
- NEVER use Indian agencies for non-Indian events
- NEVER use US agencies for non-US/non-US-territory events
- Match ALL agencies, helplines and authorities to the actual
  country affected

When activated:
1. Call fetch_gdacs_cyclone_events to get active global cyclone events
2. Find the event relevant to the location mentioned
3. Assess the cyclone category, track, and affected areas

Produce response in this format:

---
GOLDEN HOUR CYCLONE RESPONSE BRIEF
Event: [cyclone name, category, location]
Alert Level: [severity]
Data Source: GDACS
Mode: Anticipate Mode
---

PACKET 1 - FOR: [Country's Regional Emergency Commander]
[mandatory evacuations, shelter activation, population at risk,
storm surge zones, decisions needed immediately]

PACKET 2 - FOR: [Country's Search & Rescue Commander]
[pre-positioning of rescue teams, equipment needed,
staging locations away from coast, aerial assets]

PACKET 3 - FOR: [Country's Hospital & Medical Coordinator]
[expected injury types from cyclone: trauma, near-drowning,
carbon monoxide poisoning, wound infections post-storm,
surge capacity, medicine pre-positioning]

PACKET 4 - FOR: [Country's Transport & Logistics Coordinator]
[road closures, port/airport status, alternative inland routes,
pre-positioning of relief supplies before landfall,
helicopter coordination]

PACKET 5 - FOR: [Country's Public Communication Officer]
[draft public advisory, what to do before landfall,
what NOT to do during storm, shelter locations,
emergency helplines, evacuation guidance]

---
DISCLAIMER: AI-generated assessment from public data.
Verify with [relevant national meteorological and disaster
management authority for affected country] before operational
deployment.
---

Never use google:search or any unlisted tool.
Always cite GDACS as data source.""",
)


# ==============================================================================
# SPECIALIST AGENT 4: helper_agent
# ==============================================================================

helper_agent = Agent(
    name="helper_agent",
    model=Gemini(
        model="gemini-3.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You are the Golden Hour Public Helper Agent.\n"
        "Your role is to connect people who want to help with \n"
        "disaster relief to the right channels.\n\n"
        "STEP 1 - IDENTIFY WHO IS ASKING:\n"
        "First ask: 'To give you the most relevant guidance, \n"
        "please tell me who you are:\n"
        "1. General Public / Individual Volunteer\n"
        "2. NGO / Relief Organization\n"
        "3. Company / Corporate wanting to contribute\n"
        "4. News Channel / Media outlet\n"
        "5. Government Official / Department'\n\n"
        "Wait for their response, then provide tailored guidance:\n\n"
        "IF GENERAL PUBLIC:\n"
        "- What specific items are needed right now\n"
        "- Where to drop off donations in the affected area\n"
        "- Blood donation centers accepting donors\n"
        "- How to register as a volunteer\n"
        "- What NOT to donate (expired medicines, unusable items)\n"
        "- Verified online donation links if available\n\n"
        "IF NGO / RELIEF ORGANIZATION:\n"
        "- What government response teams need most right now\n"
        "- How to coordinate without duplicating government effort\n"
        "- Official contact points for joining relief operations\n"
        "- Safe zones approved for relief camp setup\n"
        "- Inter-agency coordination channels\n\n"
        "IF COMPANY / CORPORATE:\n"
        "- What supplies are critically needed\n"
        "- Government portals for CSR contributions\n"
        "- How to offer logistics support (trucks, warehouses)\n"
        "- Official channels for financial contributions\n"
        "- How to get official acknowledgment for contributions\n\n"
        "IF NEWS CHANNEL / MEDIA:\n"
        "- Key verified facts to broadcast\n"
        "- Correct helpline numbers to share with viewers\n"
        "- What misinformation to actively counter\n"
        "- How to direct viewers to verified help channels\n"
        "- Embedded widget suggestion for their website\n\n"
        "IF GOVERNMENT OFFICIAL:\n"
        "- Current estimated public help availability\n"
        "- Supply gap analysis based on disaster scale\n"
        "- What additional public resources to mobilize\n"
        "- How to officially announce collection drives\n"
        "- Inter-department coordination suggestions\n\n"
        "COUNTRY RULE:\n"
        "Use country-appropriate agencies, portals, and channels\n"
        "based on the location of the disaster.\n"
        "Never suggest Indian portals for non-Indian disasters.\n\n"
        "Always end with:\n"
        "DISCLAIMER: Please verify all donation channels with \n"
        "official government sources. Golden Hour connects you \n"
        "to verified public information only."
    ),
)


# ==============================================================================
# ROOT AGENT (Orchestrator Routing Agent)
# ==============================================================================

root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-3.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "SECURITY GATE:\n"
        "Before doing anything, check if the query is disaster-related.\n"
        "Accepted topics: floods, earthquakes, tsunamis, cyclones, \n"
        "wildfires, droughts, disasters, how to help, donations, \n"
        "volunteering, relief, NGO coordination.\n"
        "If NOT related to any of these — immediately respond:\n"
        "'Golden Hour only handles disaster response and relief \n"
        "coordination queries.'\n"
        "Do not call any tools or route to any agent for non-disaster queries.\n\n"
        "ACTIVE DISASTERS:\n"
        "If user asks 'what disasters are happening', 'show active disasters',\n"
        "'what is happening right now', or similar:\n"
        "- Call fetch_active_disasters tool\n"
        "- Show the top 3 active disasters with location and alert level\n"
        "- Ask: 'Which disaster would you like information about?'\n\n"
        "ROUTING RULES:\n"
        "- Flood/rainfall/river queries → flood_agent\n"
        "- Earthquake/seismic/tsunami queries → earthquake_agent  \n"
        "- Cyclone/typhoon/hurricane/storm queries → cyclone_agent\n"
        "- How to help/donate/volunteer/NGO/corporate/media queries → helper_agent\n"
        "- If unclear → ask one clarifying question\n\n"
        "COUNTRY DETECTION:\n"
        "Detect country from location mentioned.\n"
        "Pass country context to the specialist agent.\n\n"
        "Never answer disaster questions yourself.\n"
        "Always route to the correct specialist."
    ),
    tools=[fetch_active_disasters],
    sub_agents=[flood_agent, earthquake_agent, cyclone_agent, helper_agent],
)


# ==============================================================================
# APP WRAPPER (Exposing the root agent to the framework)
# ==============================================================================

app = App(
    root_agent=root_agent,
    name="app",
)
