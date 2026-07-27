"""
config.py
---------
Central configuration for the AI Travel Planner.

Everything that might change between environments/runs (model name,
step budget, MCP server launch commands, timeouts) lives here so the
rest of the code stays clean and environment-agnostic.
"""

import os
from dotenv import load_dotenv

load_dotenv()


# ---------------------------------------------------------------------------
# LLM Settings
# ---------------------------------------------------------------------------

# Which local Ollama model to send every LLM call to.
MODEL_NAME = os.getenv("MODEL_NAME", "llama3:latest")

# Deterministic output for stable, reproducible reasoning.
TEMPERATURE = float(os.getenv("TEMPERATURE", "0"))

# Timeout (seconds) for a single LLM call.
LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "60"))


# -------------------\--------------------------------------------------------
# Agent Loop Settings
# ---------------------------------------------------------------------------

# Hard cap on Think -> Act -> Observe cycles per user query.
MAX_STEPS = int(os.getenv("MAX_STEPS", "10"))

# How many past ReAct steps to keep in the prompt context.
MAX_HISTORY = int(os.getenv("MAX_HISTORY", "20"))


# ---------------------------------------------------------------------------
# MCP Server Settings
# ---------------------------------------------------------------------------
# Each entry describes how the MCP Client should launch / connect to a
# given MCP server. `command` + `args` are used for stdio-based servers
# (the server is spawned as a subprocess and communicates over stdin/stdout).
#
# Add a new server by:
#   1. Building mcp_servers/<name>_server/server.py
#   2. Adding an entry below.
#   3. No changes needed in agent.py / planner.py / mcp_client.py.

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MCP_SERVERS = {
    "weather": {
        "command": "python",
        "args": [os.path.join(BASE_DIR, "mcp_servers", "weather_server", "server.py")],
        "enabled": True,
    },
    "flight": {
        "command": "python",
        "args": [os.path.join(BASE_DIR, "mcp_servers", "flight_server", "server.py")],
        "enabled": True,
    },
    "hotel": {
        "command": "python",
        "args": [os.path.join(BASE_DIR, "mcp_servers", "hotel_server", "server.py")],
        "enabled": True,
    },
    "currency": {
        "command": "python",
        "args": [os.path.join(BASE_DIR, "mcp_servers", "currency_server", "server.py")],
        "enabled": True,
    },
    "maps": {
        "command": "python",
        "args": [os.path.join(BASE_DIR, "mcp_servers", "maps_server", "server.py")],
        "enabled": True,
    },
    "itinerary": {
        "command": "python",
        "args": [os.path.join(BASE_DIR, "mcp_servers", "itinerary_server", "server.py")],
        "enabled": True,
    },
}


def enabled_servers() -> dict:
    """Return only the MCP server configs currently marked enabled=True.

    Lets you build/test servers incrementally (Phase 4 of the build plan)
    without touching main.py each time.
    """
    return {name: cfg for name, cfg in MCP_SERVERS.items() if cfg.get("enabled")}


# ---------------------------------------------------------------------------
# MCP Client Settings
# ---------------------------------------------------------------------------

# Timeout (seconds) for a single MCP tool call.
MCP_CALL_TIMEOUT = int(os.getenv("MCP_CALL_TIMEOUT", "30"))

# Timeout (seconds) to wait for a server subprocess to start and respond
# to the MCP `initialize` handshake.
MCP_CONNECT_TIMEOUT = int(os.getenv("MCP_CONNECT_TIMEOUT", "15"))


# ---------------------------------------------------------------------------
# Session Settings
# ---------------------------------------------------------------------------

# Default session id used by the CLI REPL (single-user, single-session demo).
DEFAULT_SESSION_ID = "default"