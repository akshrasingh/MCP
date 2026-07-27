"""
server.py
---------
MCP wrapper around provider.search_flights().

Exposes the pure `search_flights` function as an MCP tool over
stdio, using FastMCP - same pattern as weather_server/server.py.

Run it standalone to sanity-check it starts and just sits there
listening on stdio (Ctrl+C to stop):

    python server.py
"""

from mcp.server.fastmcp import FastMCP

from provider import search_flights

# The name shows up when a client lists connected servers.
mcp = FastMCP("flight_server")


@mcp.tool()
def flight_search_flights(origin: str, destination: str, date: str) -> dict:
    """Search mocked flight options between two locations on a date.

    Args:
        origin: Departure city, e.g. "NYC".
        destination: Arrival city, e.g. "Tokyo".
        date: ISO date string, e.g. "2026-08-01".

    Returns:
        A dict with origin, destination, date, options (a list of
        airline/price_usd/duration_hours/stops), source, and
        destination_known.
    """
    return search_flights(origin, destination, date)


if __name__ == "__main__":
    # Runs the server over stdio - this is what config.py's MCP_SERVERS
    # entry for "flight" spawns as a subprocess.
    mcp.run(transport="stdio")
