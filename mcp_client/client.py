"""
client.py
---------
MCPClient: connects to one or more MCP servers (each spawned as a
subprocess over stdio) and exposes a single, synchronous facade -
connect(), list_tools(), call_tool(), close() - that the rest of the
app (agent.py, planner.py) can use without knowing anything about
asyncio.

Why a background thread + its own event loop?
The `mcp` SDK's session objects (see transport.py) are async context
managers meant to stay open for the lifetime of the connection, so the
subprocess isn't respawned on every tool call. Day 3's Agent loop is
plain synchronous code, so this class runs one persistent asyncio
event loop on a background thread, and every public method blocks the
calling (sync) thread until its coroutine finishes on that loop.
"""

import asyncio
import threading
from contextlib import AsyncExitStack

from mcp_client.transport import connect_stdio_server


class MCPClient:
    def __init__(self):
        # tool_name -> ClientSession, built up in connect(). Lets
        # call_tool() route each request to the server that actually
        # registered that tool, without the caller needing to know
        # which server owns which tool.
        self._tool_to_session: dict = {}

        # server_name -> ClientSession, kept around so list_tools() can
        # re-query every connected server for its current tool list.
        self._server_sessions: dict = {}

        # Owns the lifetime of every subprocess + session opened via
        # transport.connect_stdio_server(). Closed all at once in
        # close().
        self._exit_stack = AsyncExitStack()

        # A dedicated event loop running forever on a background
        # thread, so async MCP calls have somewhere to run without
        # requiring the rest of the app to become async.
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._loop.run_forever, daemon=True)
        self._thread.start()

    def _run(self, coroutine):
        """Run an async coroutine on the background loop and block for its result.

        This is the bridge between the outside world's synchronous
        calls and the mcp SDK's async-only API.
        """
        future = asyncio.run_coroutine_threadsafe(coroutine, self._loop)
        return future.result()

    def connect(self, server_configs: dict) -> None:
        """Start every configured server and register its tools.

        Args:
            server_configs: dict shaped like config.enabled_servers(),
                e.g. {"weather": {"command": "python", "args": [...]}}.
        """
        self._run(self._connect_all(server_configs))

    async def _connect_all(self, server_configs: dict) -> None:
        for server_name, server_config in server_configs.items():
            session = await connect_stdio_server(
                server_config["command"], server_config["args"], self._exit_stack
            )
            self._server_sessions[server_name] = session

            tools_result = await session.list_tools()
            for tool in tools_result.tools:
                self._tool_to_session[tool.name] = session

    def list_tools(self) -> list:
        """Return the aggregated list of MCP Tool objects from all connected servers."""
        return self._run(self._list_tools_all())

    async def _list_tools_all(self) -> list:
        all_tools = []
        for session in self._server_sessions.values():
            tools_result = await session.list_tools()
            all_tools.extend(tools_result.tools)
        return all_tools

    def call_tool(self, name: str, arguments: dict):
        """Call a tool by name, routing to whichever server registered it.

        Args:
            name: The MCP tool name, e.g. "weather_get_weather".
            arguments: Keyword arguments for the tool, e.g.
                {"location": "Tokyo", "date": "2026-08-01"}.

        Returns:
            The tool's result as a plain Python dict/value (unwrapped
            from the MCP CallToolResult envelope).
        """
        if name not in self._tool_to_session:
            raise ValueError(f"Unknown tool: {name}")

        return self._run(self._call_tool(name, arguments))

    async def _call_tool(self, name: str, arguments: dict):
        session = self._tool_to_session[name]
        result = await session.call_tool(name, arguments)

        # FastMCP tools that return a dict populate structuredContent
        # with that dict directly - prefer it when present. Fall back
        # to the first text content block for tools that only return
        # plain text.
        if result.structuredContent is not None:
            return result.structuredContent

        for content_block in result.content:
            if hasattr(content_block, "text"):
                return content_block.text

        return None

    def close(self) -> None:
        """Tear down all subprocess connections and stop the background loop."""
        self._run(self._exit_stack.aclose())
        self._loop.call_soon_threadsafe(self._loop.stop)
        self._thread.join(timeout=5)
