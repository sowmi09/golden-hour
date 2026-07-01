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
import urllib.request
import urllib.error

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

# Set up environment variables to use Gemini API Key directly
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"


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
    """Calls the GDACS API to retrieve active flood events worldwide.

    Returns:
        A JSON string containing active flood events, or an error message if the fetch fails.
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
        return f"HTTP Error fetching GDACS events: {e.code} - {e.reason}"
    except urllib.error.URLError as e:
        return f"Network or URL Error fetching GDACS events: {e.reason}"
    except Exception as e:
        return f"Unexpected error fetching GDACS events: {str(e)}"


# Define the root agent running in Anticipate Mode for floods
root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-flash-latest",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You are Golden Hour, a disaster response AI agent operating in Anticipate Mode for floods.\n"
        "You have exactly two tools available: fetch_flood_forecast and fetch_gdacs_events.\n"
        "Do not use any other tools. Do not attempt google:search or any other tool not listed.\n"
        "\n"
        "When given a river gauge ID:\n"
        "1. Call fetch_flood_forecast with that gauge ID\n"
        "2. Analyse the returned data for any values exceeding normal flood stage\n"
        "3. If threat detected: draft a clear action plan with affected area, estimated timeline, recommended actions, and data source citation\n"
        "4. If no threat: return a clear status report\n"
        "\n"
        "Always end your response with:\n"
        "DISCLAIMER: This is an AI-generated assessment based on public NOAA forecast data. Always verify with official sources before taking action."
    ),
    tools=[fetch_flood_forecast, fetch_gdacs_events],
)

# App wrapper exposing the root agent to the framework
app = App(
    root_agent=root_agent,
    name="app",
)
