"""
server.py
---------
MCP wrapper around provider.get_places().

Exposes the pure `get_places` function as an MCP tool over
stdio, using FastMCP - same pattern as weather_server/server.py.

Run it standalone to sanity-check it starts and just sits there
listening on stdio (Ctrl+C to stop):

    python server.py
"""

from mcp.server.fastmcp import FastMCP

from provider import get_places

# The name shows up when a client lists connected servers.
mcp = FastMCP("maps_server")


@mcp.tool()
def maps_get_places(location: str, category: str = "attractions") -> dict:
    """Get mocked points of interest for a location and category.

    Args:
        location: City name, e.g. "Tokyo".
        category: "attractions" or "restaurants", defaults to "attractions".

    Returns:
        A dict with location, category, places (a list of name/rating),
        source, location_known, and category_known.
    """
    return get_places(location, category)


if __name__ == "__main__":
    # Runs the server over stdio - this is what config.py's MCP_SERVERS
    # entry for "maps" spawns as a subprocess.
    mcp.run(transport="stdio")
