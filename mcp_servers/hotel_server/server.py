"""
server.py
---------
MCP wrapper around provider.search_hotels().

Exposes the pure `search_hotels` function as an MCP tool over
stdio, using FastMCP - same pattern as weather_server/server.py.

Run it standalone to sanity-check it starts and just sits there
listening on stdio (Ctrl+C to stop):

    python server.py
"""

from mcp.server.fastmcp import FastMCP

from provider import search_hotels

# The name shows up when a client lists connected servers.
mcp = FastMCP("hotel_server")


@mcp.tool()
def hotel_search_hotels(location: str, checkin: str, checkout: str, guests: int = 1) -> dict:
    """Search mocked hotel options in a location for a date range.

    Args:
        location: City name, e.g. "Tokyo".
        checkin: ISO check-in date string, e.g. "2026-08-01".
        checkout: ISO check-out date string, e.g. "2026-08-04".
        guests: Number of guests, defaults to 1.

    Returns:
        A dict with location, checkin, checkout, nights, guests,
        options (a list of name/price_per_night_usd/rating/stars/
        total_price_usd), source, and location_known.
    """
    return search_hotels(location, checkin, checkout, guests)


if __name__ == "__main__":
    # Runs the server over stdio - this is what config.py's MCP_SERVERS
    # entry for "hotel" spawns as a subprocess.
    mcp.run(transport="stdio")
