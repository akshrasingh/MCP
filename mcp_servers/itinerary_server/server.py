"""
server.py
---------
MCP wrapper around composer.build_itinerary().

Exposes the pure `build_itinerary` function as an MCP tool over
stdio, using FastMCP - same pattern as weather_server/server.py.

Run it standalone to sanity-check it starts and just sits there
listening on stdio (Ctrl+C to stop):

    python server.py
"""

from mcp.server.fastmcp import FastMCP

from composer import build_itinerary

# The name shows up when a client lists connected servers.
mcp = FastMCP("itinerary_server")


@mcp.tool()
def itinerary_generate_itinerary(weather: dict, flights: dict, hotels: dict, places: dict, days: int = 3) -> dict:
    """Compose a day-by-day itinerary from other tools' results.

    Args:
        weather: Result dict from the weather tool.
        flights: Result dict from the flight tool.
        hotels: Result dict from the hotel tool.
        places: Result dict from the maps tool.
        days: How many days the itinerary should cover, defaults to 3.

    Returns:
        A dict with a single "itinerary" key holding the markdown text.
    """
    itinerary_text = build_itinerary(weather, flights, hotels, places, days)
    return {"itinerary": itinerary_text}


if __name__ == "__main__":
    # Runs the server over stdio - this is what config.py's MCP_SERVERS
    # entry for "itinerary" spawns as a subprocess.
    mcp.run(transport="stdio")
