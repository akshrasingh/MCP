"""
tool_catalogue.py
-----------------
Formats the tools discovered by MCPClient into a single, plain-text
block that the ReAct system prompt can inject directly - e.g.:

    - weather_get_weather(location: str, date: str): Get the mocked
      weather forecast for a location on a given date.
    - hotel_search_hotels(location: str, checkin: str, checkout: str,
      guests: int): Search mocked hotel options in a location for a
      date range.

Unlike Day 3's static tool_descriptions() (a hardcoded string), this is
built dynamically from whatever tools the connected MCP servers report
having right now, so adding a new server (Phase 4) never requires
touching this file.
"""


class ToolCatalogue:
    def __init__(self, mcp_client):
        self._mcp_client = mcp_client

    def describe_all(self) -> str:
        """Return a formatted string describing every available tool.

        Each tool is rendered as its name, its parameters (with types
        pulled from the tool's JSON schema), and its description.
        """

        tools = self._mcp_client.list_tools()

        if not tools:
            return "(no tools available)"

        lines = []
        for tool in tools:
            # tool.inputSchema is a JSON Schema dict, e.g.
            # {"properties": {"location": {"type": "string"}, ...}}.
            # Pull out just the parameter names + types for a compact
            # one-line signature - the LLM doesn't need the full
            # schema, just enough to know what to pass.
            properties = {}
            if tool.inputSchema:
                properties = tool.inputSchema.get("properties", {})

            param_parts = []
            for param_name, param_schema in properties.items():
                param_type = param_schema.get("type", "any")
                param_parts.append(f"{param_name}: {param_type}")

            params_str = ", ".join(param_parts)
            description = (tool.description or "").strip()

            lines.append(f"- {tool.name}({params_str}): {description}")

        return "\n".join(lines)
