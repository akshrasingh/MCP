"""
server.py
---------
MCP wrapper around provider.get_weather().

Phase 1, Step 1.2 of the build plan: expose the pure `get_weather`
function as an MCP tool over stdio, using the `FastMCP` helper from the
`mcp` SDK (this handles `initialize`, `list_tools`, and `call_tool`
for us, instead of us implementing the low-level protocol by hand).

Run it standalone to sanity-check it starts and just sits there
listening on stdio (Ctrl+C to stop):

    python server.py
"""

from mcp.server.fastmcp import FastMCP

from provider import get_weather

# The name shows up when a client lists connected servers.
mcp = FastMCP("weather_server")


@mcp.tool()
def weather_get_weather(location: str, date: str) -> dict:
    """Get the mocked weather forecast for a location on a given date.

    Args:
        location: City name, e.g. "Tokyo".
        date: ISO date string, e.g. "2026-08-01".

    Returns:
        A dict with location, date, condition, temp_c, humidity_percent,
        source, and location_known.
    """
    return get_weather(location, date)


if __name__ == "__main__":
    # Runs the server over stdio - this is what config.py's MCP_SERVERS
    # entry for "weather" spawns as a subprocess.
    mcp.run(transport="stdio")
