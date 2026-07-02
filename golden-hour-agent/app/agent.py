# ruff: noqa
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

import os

# Set up environment variables to use Gemini API Key directly and avoid Vertex AI
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"

import urllib.request
import urllib.error

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
    # Format URL for NOAA National Water Prediction Service stageflow endpoint
    url = f"https://api.water.noaa.gov/nwps/v1/gauges/{gauge_id}/stageflow"

    # Define a standard user agent to prevent request blockage
    req = urllib.request.Request(
        url, headers={"User-Agent": "GoldenHour/1.0 (Disaster Response Agent)"}
    )

    try:
        # Perform the HTTP GET request
        with urllib.request.urlopen(req) as response:
            return response.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return f"HTTP Error fetching flood forecast (gauge_id: {gauge_id}): {e.code} - {e.reason}"
    except urllib.error.URLError as e:
        return f"Network or URL Error fetching flood forecast (gauge_id: {gauge_id}): {e.reason}"
    except Exception as e:
        return (
            f"Unexpected error fetching flood forecast (gauge_id: {gauge_id}): {str(e)}"
        )


def fetch_gdacs_events() -> str:
    """Calls the GDACS API to retrieve active global flood events.

    Returns:
        A JSON string containing active global flood events, or an error message if the fetch fails.
    """
    # GDACS API endpoint for fetching disaster event list filtered by flood event type (FL)
    url = "https://www.gdacs.org/gdacsapi/api/events/geteventlist/SEARCH?eventtype=FL"

    # Define a standard user agent to prevent request blockage
    req = urllib.request.Request(
        url, headers={"User-Agent": "GoldenHour/1.0 (Disaster Response Agent)"}
    )

    try:
        # Perform the HTTP GET request
        with urllib.request.urlopen(req) as response:
            return response.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return f"HTTP Error fetching GDACS flood events: {e.code} - {e.reason}"
    except urllib.error.URLError as e:
        return f"Network or URL Error fetching GDACS flood events: {e.reason}"
    except Exception as e:
        return f"Unexpected error fetching GDACS flood events: {str(e)}"


def fetch_usgs_earthquakes() -> str:
    """Calls the USGS API to retrieve significant earthquakes in the last month.

    Returns:
        A JSON string containing significant earthquake events, or an error message if the fetch fails.
    """
    # USGS API endpoint for significant earthquakes in the last month
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_month.geojson"

    # Define a standard user agent to prevent request blockage
    req = urllib.request.Request(
        url, headers={"User-Agent": "GoldenHour/1.0 (Disaster Response Agent)"}
    )

    try:
        # Perform the HTTP GET request
        with urllib.request.urlopen(req) as response:
            return response.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return (
            f"HTTP Error fetching USGS significant earthquakes: {e.code} - {e.reason}"
        )
    except urllib.error.URLError as e:
        return f"Network or URL Error fetching USGS significant earthquakes: {e.reason}"
    except Exception as e:
        return f"Unexpected error fetching USGS significant earthquakes: {str(e)}"


def fetch_usgs_event_detail(event_id: str) -> str:
    """Calls the USGS API to retrieve PAGER impact data for a specific earthquake event.

    Args:
        event_id: The identifier of the earthquake event (e.g., 'us6000abcd').

    Returns:
        A JSON string containing detailed event data including PAGER, or an error message if the fetch fails.
    """
    # USGS API endpoint for specific event detail
    url = f"https://earthquake.usgs.gov/earthquakes/feed/v1.0/detail/{event_id}.geojson"

    # Define a standard user agent to prevent request blockage
    req = urllib.request.Request(
        url, headers={"User-Agent": "GoldenHour/1.0 (Disaster Response Agent)"}
    )

    try:
        # Perform the HTTP GET request
        with urllib.request.urlopen(req) as response:
            return response.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return f"HTTP Error fetching USGS event detail (event_id: {event_id}): {e.code} - {e.reason}"
    except urllib.error.URLError as e:
        return f"Network or URL Error fetching USGS event detail (event_id: {event_id}): {e.reason}"
    except Exception as e:
        return f"Unexpected error fetching USGS event detail (event_id: {event_id}): {str(e)}"


def fetch_gdacs_earthquake_events() -> str:
    """Calls the GDACS API to retrieve active global earthquake events.

    Returns:
        A JSON string containing active earthquake events, or an error message if the fetch fails.
    """
    # GDACS API endpoint for fetching disaster event list filtered by earthquake event type (EQ)
    url = "https://www.gdacs.org/gdacsapi/api/events/geteventlist/SEARCH?eventtype=EQ"

    # Define a standard user agent to prevent request blockage
    req = urllib.request.Request(
        url, headers={"User-Agent": "GoldenHour/1.0 (Disaster Response Agent)"}
    )

    try:
        # Perform the HTTP GET request
        with urllib.request.urlopen(req) as response:
            return response.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        return f"HTTP Error fetching GDACS earthquake events: {e.code} - {e.reason}"
    except urllib.error.URLError as e:
        return f"Network or URL Error fetching GDACS earthquake events: {e.reason}"
    except Exception as e:
        return f"Unexpected error fetching GDACS earthquake events: {str(e)}"


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
        'flood', 'earthquake', 'tsunami', 'cyclone', 'hurricane',
        'typhoon', 'wildfire', 'fire', 'drought', 'landslide',
        'disaster', 'emergency', 'magnitude', 'seismic', 'storm',
        'rainfall', 'river', 'gauge', 'alert', 'warning', 'evacuate'
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
        "You are the Golden Hour Flood Specialist Agent operating in Anticipate Mode.\n"
        "You accept plain language questions like 'What is the flood situation in Kerala?'\n\n"
        "When activated:\n"
        "1. Call fetch_gdacs_events to get active global flood events\n"
        "2. Find events relevant to the location mentioned by the user\n"
        "3. If a gauge ID is mentioned or known, call fetch_flood_forecast for detailed data\n\n"
        "Then produce FIVE role-specific action packets in this exact format:\n\n"
        "---\n"
        "GOLDEN HOUR FLOOD RESPONSE BRIEF\n"
        "Event: [location and event description]\n"
        "Alert Level: [severity]\n"
        "Data Source: GDACS / NOAA NWPS\n"
        "Generated: [current time estimate]\n"
        "---\n\n"
        "PACKET 1 - FOR: District Collector / DDMA Commander\n"
        "[What decisions need to be made right now. Population at risk. \n"
        "Areas to prioritize. Resources to activate. Evacuation zones.]\n\n"
        "PACKET 2 - FOR: NDRF / Rescue Field Commander  \n"
        "[Where to deploy first. Access routes likely to be flooded. \n"
        "Equipment needed. Estimated rescue operations scale.]\n\n"
        "PACKET 3 - FOR: Hospital & Medical Coordinator\n"
        "[Expected casualty types from flooding: drowning, waterborne disease risk, \n"
        "hypothermia. Surge capacity needed. Medical supplies to pre-position.]\n\n"
        "PACKET 4 - FOR: Transport & Logistics Coordinator\n"
        "[Which roads/bridges likely affected. Alternative routes. \n"
        "Relief materials to pre-position. Helicopter landing zones if needed.]\n\n"
        "PACKET 5 - FOR: Public Communication Officer\n"
        "[Draft public advisory in simple language. What people in affected \n"
        "areas should do RIGHT NOW. Evacuation instructions if needed.]\n\n"
        "---\n"
        "DISCLAIMER: AI-generated assessment from public data. \n"
        "Verify with IMD, CWC, and NDMA before operational deployment.\n"
        "---\n\n"
        "Never use google:search or any unlisted tool.\n"
        "Always end with the disclaimer."
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
        "You are the Golden Hour Earthquake Specialist Agent operating in Respond Mode.\n"
        "You accept plain language questions like 'Tell me about the latest earthquake in India'\n\n"
        "When activated:\n"
        "1. Call fetch_usgs_earthquakes to get recent significant earthquakes\n"
        "2. Find the most relevant event matching the user's question\n"
        "3. Call fetch_usgs_event_detail with the event ID for PAGER data\n"
        "4. Also call fetch_gdacs_earthquake_events for additional context\n\n"
        "Then produce FIVE role-specific action packets in this exact format:\n\n"
        "---\n"
        "GOLDEN HOUR EARTHQUAKE RESPONSE BRIEF\n"
        "Event: [location, magnitude, depth]\n"
        "PAGER Alert: [Green/Yellow/Orange/Red]\n"
        "Data Source: USGS PAGER + GDACS\n"
        "Generated: [current time estimate]\n"
        "---\n\n"
        "PACKET 1 - FOR: District Collector / DDMA Commander\n"
        "[Estimated affected population. Severity zones. \n"
        "Immediate resource activation needed. State/national escalation required?]\n\n"
        "PACKET 2 - FOR: NDRF / Search & Rescue Field Commander\n"
        "[Priority deployment zones based on shaking intensity. \n"
        "Building collapse risk areas. Equipment needed: USAR tools, canine units. \n"
        "Access route status.]\n\n"
        "PACKET 3 - FOR: Hospital & Medical Coordinator\n"
        "[Expected injury types: crush syndrome, trauma, fractures. \n"
        "Estimated casualty range from PAGER. Which hospitals to activate. \n"
        "Blood bank alert level. Field medical post locations.]\n\n"
        "PACKET 4 - FOR: Transport & Logistics Coordinator\n"
        "[Road/bridge damage risk zones. Alternative supply routes. \n"
        "Heavy machinery needs for debris clearance. \n"
        "Helicopter requirement for cut-off areas.]\n\n"
        "PACKET 5 - FOR: Public Communication Officer\n"
        "[Draft public advisory. Aftershock warning. \n"
        "What NOT to do (re-enter damaged buildings). \n"
        "Helpline numbers to broadcast. Evacuation guidance if needed.]\n\n"
        "---\n"
        "CRITICAL RULES:\n"
        "- NEVER use the word 'predict' for earthquakes\n"
        "- Always state this is POST-EVENT estimation, not prediction\n"
        "- Always cite USGS event ID and PAGER alert level\n"
        "- DISCLAIMER: AI-generated assessment from USGS public data. \n"
        "  Verify with IMD Seismology Division and NDMA before operational deployment.\n"
        "---\n\n"
        "Never use google:search or any unlisted tool."
    ),
    tools=[
        fetch_usgs_earthquakes,
        fetch_usgs_event_detail,
        fetch_gdacs_earthquake_events,
    ],
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
        "SECURITY GATE: Before routing to any specialist agent, check if the query \n"
        "is about a natural disaster (flood, earthquake, tsunami, cyclone, wildfire, \n"
        "drought). If NOT disaster-related, immediately respond: 'Golden Hour only \n"
        "handles natural disaster response queries. Please ask about floods, \n"
        "earthquakes, cyclones, tsunamis, wildfires or droughts.' Do not call any \n"
        "tools or route to any agent for non-disaster queries.\n\n"
        "COUNTRY DETECTION: Detect the country from the location in the query.\n"
        "Use appropriate local response teams for that country, not generic Indian \n"
        "teams for non-Indian events.\n\n"
        "You are Golden Hour - an AI disaster response coordination system.\n"
        "You serve disaster management teams, NDRF commanders, hospital coordinators,\n"
        "logistics teams, and public communication officers.\n\n"
        "You have two specialist agents:\n"
        "- flood_agent: handles floods, river flooding, flash floods, rainfall alerts\n"
        "- earthquake_agent: handles earthquakes, tremors, seismic events, tsunamis\n\n"
        "When user asks about any disaster:\n"
        "1. Identify the disaster type\n"
        "2. Route to the correct specialist agent\n"
        "3. The specialist will produce five role-specific action packets\n\n"
        "Accept plain language inputs. Users should never need to know gauge IDs or event codes.\n"
        "Never answer disaster questions yourself - always route to the specialist."
    ),
    sub_agents=[flood_agent, earthquake_agent],
)


# ==============================================================================
# APP WRAPPER (Exposing the root agent to the framework)
# ==============================================================================

app = App(
    root_agent=root_agent,
    name="app",
)
