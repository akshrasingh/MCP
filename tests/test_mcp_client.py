"""
test_mcp_client.py
-------------------
Phase 2 checkpoint: proves MCPClient can talk to a real MCP server
(weather_server, spawned as a subprocess) end-to-end - not just import
provider.py directly like Phase 1's isolated test did.

Run with:
    pytest tests/test_mcp_client.py -v
"""

import sys
from pathlib import Path

# The project root needs to be on sys.path so `import config` and
# `import mcp_client` (a proper package) both resolve.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import pytest

import config
from mcp_client.client import MCPClient


@pytest.fixture
def weather_client():
    """Connect an MCPClient to only the weather server, and clean up after."""

    # Build a single-server config dict directly from config.py's
    # MCP_SERVERS, regardless of that server's `enabled` flag - this
    # test should stay isolated from whatever's enabled for the real app.
    weather_only_config = {"weather": config.MCP_SERVERS["weather"]}

    client = MCPClient()
    client.connect(weather_only_config)

    yield client

    client.close()


def test_list_tools_includes_weather_tool(weather_client):
    tools = weather_client.list_tools()
    tool_names = [tool.name for tool in tools]

    assert "weather_get_weather" in tool_names


def test_call_tool_returns_weather_data(weather_client):
    result = weather_client.call_tool(
        "weather_get_weather", {"location": "Tokyo", "date": "2026-08-01"}
    )

    assert "temp_c" in result
    assert result["location"] == "Tokyo"
    assert result["date"] == "2026-08-01"


def test_call_tool_raises_for_unknown_tool(weather_client):
    with pytest.raises(ValueError):
        weather_client.call_tool("not_a_real_tool", {})
