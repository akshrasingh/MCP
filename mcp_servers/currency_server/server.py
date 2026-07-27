"""
server.py
---------
MCP wrapper around provider.convert_currency().

Exposes the pure `convert_currency` function as an MCP tool over
stdio, using FastMCP - same pattern as weather_server/server.py.

Run it standalone to sanity-check it starts and just sits there
listening on stdio (Ctrl+C to stop):

    python server.py
"""

from mcp.server.fastmcp import FastMCP

from provider import convert_currency

# The name shows up when a client lists connected servers.
mcp = FastMCP("currency_server")


@mcp.tool()
def currency_convert_currency(amount: float, from_currency: str, to_currency: str) -> dict:
    """Convert an amount from one currency to another using mocked rates.

    Args:
        amount: The amount to convert, e.g. 500.
        from_currency: Source currency code, e.g. "USD".
        to_currency: Target currency code, e.g. "JPY".

    Returns:
        A dict with amount, from_currency, to_currency, converted_amount,
        rate_used, source, from_currency_known, and to_currency_known.
    """
    return convert_currency(amount, from_currency, to_currency)


if __name__ == "__main__":
    # Runs the server over stdio - this is what config.py's MCP_SERVERS
    # entry for "currency" spawns as a subprocess.
    mcp.run(transport="stdio")
