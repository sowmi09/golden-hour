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
    """Fetches top 3 active disasters from GDACS combining
    floods, earthquakes and cyclones."""
    results = []

    endpoints = [
        (
            "FL",
            "https://www.gdacs.org/gdacsapi/api/events/geteventlist/SEARCH?eventtype=FL",
        ),
        (
            "EQ",
            "https://www.gdacs.org/gdacsapi/api/events/geteventlist/SEARCH?eventtype=EQ",
        ),
        (
            "TC",
            "https://www.gdacs.org/gdacsapi/api/events/geteventlist/SEARCH?eventtype=TC",
        ),
    ]

    for event_type, url in endpoints:
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "GoldenHour/1.0 (Disaster Response Agent)"},
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
                features = data.get("features", [])
                for feature in features[:2]:
                    props = feature.get("properties", {})
                    country = props.get("country", "Unknown location")
                    alert = props.get("alertlevel", "Unknown")
                    name = props.get("name", event_type)
                    results.append(
                        f"{event_type}: {name} in {country} - Alert: {alert}"
                    )
        except Exception as e:
            results.append(f"{event_type}: Could not fetch data - {e!s}")

    if not results:
        return "No active disaster data available at this time."

    return "Active disasters right now:\n" + "\n".join(results[:3])


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
        model="gemini-2.5-flash",
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
        model="gemini-2.5-flash",
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
    model=Gemini(model="gemini-2.5-flash"),
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
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="""You are the Golden Hour Public Helper Agent.
You connect people wanting to help disaster victims with the right channels.

When activated, immediately provide help guidance in ALL these sections without asking any questions:

SECTION 1 - FOR GENERAL PUBLIC:
How to donate, volunteer, give blood, what items needed,
where to drop donations, what NOT to send.

SECTION 2 - FOR NGOs:
How to coordinate with government, approved zones for relief camps, inter-agency coordination contacts,
what is most needed right now.

SECTION 3 - FOR COMPANIES/CORPORATES:
CSR contribution channels, logistics support options,
official financial donation portals, how to get official acknowledgment.

SECTION 4 - FOR NEWS CHANNELS/MEDIA:
Key verified facts to broadcast, correct helplines to share,
misinformation to counter, how to direct viewers to help.

SECTION 5 - FOR GOVERNMENT OFFICIALS:
Supply gap analysis, public resource mobilization guidance,
inter-department coordination, official collection drives.

Use country-appropriate channels based on disaster location.
Always end with disclaimer about verifying with official sources.""",
)


# ==============================================================================
# ROOT AGENT (Orchestrator Routing Agent)
# ==============================================================================

root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction="""You are Golden Hour — AI disaster response and relief coordination system.

STEP 1 - GREETING AND REGISTRATION:
When user says hi, hello, hey, or any greeting:
Respond with exactly this:
'Welcome to Golden Hour! I help disaster response teams, NGOs, government officials, and the public with real-time disaster information and relief coordination.

To serve you better, please tell me:
1. Your Name
2. Your Country
3. Your Role:
   - General Public
   - Government Official / NDRF / Emergency Manager
   - NGO / Relief Organization
   - News Channel / Media
   - Company / Corporate
   - Researcher / Student

This helps me tailor disaster information specifically for you.'

STEP 2 - AFTER REGISTRATION:
When user provides their details (name, country, role):
- Acknowledge them warmly
- Remember their role for this session
- Tell them what they can ask

STEP 3 - ROUTING BASED ON QUERY AND ROLE:
Once registered, route queries to specialists:
- Flood/rainfall/river queries → flood_agent
- Earthquake/seismic/tsunami → earthquake_agent
- Cyclone/typhoon/hurricane/storm → cyclone_agent
- Help/donate/volunteer/NGO/corporate/media → helper_agent
- 'What disasters are happening' → call fetch_active_disasters tool

ROLE-BASED CONTEXT:
Pass the user's role to specialist agents so they emphasize the most relevant packet:
- Government Official → emphasize Packet 1 (Commander)
- NGO → emphasize Packet 2 (Rescue) and helper guidance
- General Public → emphasize Packet 5 (Public Advisory)
- Media → emphasize Packet 5 and connect to helper_agent
- Company/Corporate → connect to helper_agent

SECURITY GATE:
Reject non-disaster queries politely:
'Golden Hour only handles disaster response and relief coordination. Please ask about floods, earthquakes, cyclones, or how to help disaster victims.'""",
    sub_agents=[flood_agent, earthquake_agent, cyclone_agent, helper_agent],
    tools=[fetch_active_disasters],
)


# ==============================================================================
# APP WRAPPER (Exposing the root agent to the framework)
# ==============================================================================

app = App(
    root_agent=root_agent,
    name="app",
)
