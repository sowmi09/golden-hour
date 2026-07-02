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

import urllib.error
from unittest.mock import MagicMock, patch

from app.agent import (
    fetch_flood_forecast,
    fetch_gdacs_earthquake_events,
    fetch_gdacs_events,
    fetch_usgs_earthquakes,
    fetch_usgs_event_detail,
    validate_disaster_query,
)


@patch("urllib.request.urlopen")
def test_fetch_flood_forecast_success(mock_urlopen) -> None:
    # Mocking successful HTTP response
    mock_response = MagicMock()
    mock_response.read.return_value = b'{"status": "success"}'
    mock_urlopen.return_value.__enter__.return_value = mock_response

    result = fetch_flood_forecast("12345")
    assert result == '{"status": "success"}'

    # Verify the correct URL was requested
    args, _kwargs = mock_urlopen.call_args
    req = args[0]
    assert req.full_url == "https://api.water.noaa.gov/nwps/v1/gauges/12345/stageflow"
    assert req.headers["User-agent"] == "GoldenHour/1.0 (Disaster Response Agent)"


@patch("urllib.request.urlopen")
def test_fetch_flood_forecast_http_error(mock_urlopen) -> None:
    # Mocking HTTPError
    mock_urlopen.side_effect = urllib.error.HTTPError(
        "https://api.water.noaa.gov/nwps/v1/gauges/12345/stageflow",
        404,
        "Not Found",
        None,
        None,
    )

    result = fetch_flood_forecast("12345")
    assert (
        "HTTP Error fetching flood forecast (gauge_id: 12345): 404 - Not Found"
        in result
    )


@patch("urllib.request.urlopen")
def test_fetch_gdacs_events_success(mock_urlopen) -> None:
    mock_response = MagicMock()
    mock_response.read.return_value = b'{"events": []}'
    mock_urlopen.return_value.__enter__.return_value = mock_response

    result = fetch_gdacs_events()
    assert result == '{"events": []}'

    args, _kwargs = mock_urlopen.call_args
    req = args[0]
    assert (
        req.full_url
        == "https://www.gdacs.org/gdacsapi/api/events/geteventlist/SEARCH?eventtype=FL"
    )


@patch("urllib.request.urlopen")
def test_fetch_usgs_earthquakes_success(mock_urlopen) -> None:
    mock_response = MagicMock()
    mock_response.read.return_value = b'{"features": []}'
    mock_urlopen.return_value.__enter__.return_value = mock_response

    result = fetch_usgs_earthquakes()
    assert result == '{"features": []}'

    args, _kwargs = mock_urlopen.call_args
    req = args[0]
    assert (
        req.full_url
        == "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_month.geojson"
    )


@patch("urllib.request.urlopen")
def test_fetch_usgs_event_detail_success(mock_urlopen) -> None:
    mock_response = MagicMock()
    mock_response.read.return_value = b'{"properties": {}}'
    mock_urlopen.return_value.__enter__.return_value = mock_response

    result = fetch_usgs_event_detail("us6000abcd")
    assert result == '{"properties": {}}'

    args, _kwargs = mock_urlopen.call_args
    req = args[0]
    assert (
        req.full_url
        == "https://earthquake.usgs.gov/earthquakes/feed/v1.0/detail/us6000abcd.geojson"
    )


@patch("urllib.request.urlopen")
def test_fetch_gdacs_earthquake_events_success(mock_urlopen) -> None:
    mock_response = MagicMock()
    mock_response.read.return_value = b'{"events": []}'
    mock_urlopen.return_value.__enter__.return_value = mock_response

    result = fetch_gdacs_earthquake_events()
    assert result == '{"events": []}'

    args, _kwargs = mock_urlopen.call_args
    req = args[0]
    assert (
        req.full_url
        == "https://www.gdacs.org/gdacsapi/api/events/geteventlist/SEARCH?eventtype=EQ"
    )


def test_validate_disaster_query() -> None:
    # Valid queries containing keywords
    assert validate_disaster_query("What is the flood situation in Kerala?") is True
    assert validate_disaster_query("Tell me about the latest earthquake in India") is True
    assert validate_disaster_query("Are there any tsunami warnings for Japan?") is True
    assert validate_disaster_query("What's the wildfire alert status?") is True

    # Invalid queries containing no disaster keywords
    assert validate_disaster_query("Why is the sky blue?") is False
    assert validate_disaster_query("How do I cook a chocolate cake?") is False
    assert validate_disaster_query("Hello there, nice to meet you!") is False

