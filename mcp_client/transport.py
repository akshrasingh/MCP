"""
transport.py
------------
Thin wrapper around the mcp SDK's stdio transport for spawning a single
MCP server as a subprocess and handing back an initialized
ClientSession.

This hides the async context-manager plumbing (stdio_client +
ClientSession) behind one async function, so client.py can just await
`connect_stdio_server(...)` and get back a ready-to-use session,
without needing to know how the connection was actually made.
"""

from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def connect_stdio_server(
    command: str, args: list[str], exit_stack: AsyncExitStack
) -> ClientSession:
    """Spawn an MCP server over stdio and return an initialized session.

    Args:
        command: Executable to run, e.g. "python".
        args: Arguments to that executable, e.g. ["server.py"].
        exit_stack: Shared AsyncExitStack that owns the subprocess and
            session lifetime. The caller (client.py) decides when to
            close this stack, keeping the subprocess alive across many
            tool calls instead of respawning it each time.

    Returns:
        A ClientSession that has already completed the MCP `initialize`
        handshake and is ready for list_tools()/call_tool().
    """

    server_params = StdioServerParameters(command=command, args=args)

    # Entering these via the shared exit_stack (instead of `async with`)
    # is what lets the subprocess + session outlive this function call.
    read_stream, write_stream = await exit_stack.enter_async_context(
        stdio_client(server_params)
    )
    session = await exit_stack.enter_async_context(
        ClientSession(read_stream, write_stream)
    )

    # The MCP handshake: negotiates protocol version and capabilities
    # with the server before any list_tools()/call_tool() will work.
    await session.initialize()

    return session
