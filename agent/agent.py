"""
agent.py
---------
Implements the ReAct execution loop, ported from Day 3's agent.py.

The structural change from Day 3: tools are no longer a static dict
built at import time - they live behind an MCPClient, and the tool
catalogue shown to the LLM is built dynamically from whatever tools
the connected MCP servers currently report.

Responsibilities:
1. Ask the planner for the next step.
2. Execute tools via the MCP client.
3. Store observations in memory.
4. Repeat until a final answer or max steps.
"""

import json

from config import MAX_STEPS
from agent.planner import Planner
from agent.memory import Memory
from mcp_client.tool_catalogue import ToolCatalogue


def _parse_action_input(raw):
    """Best-effort parse of the LLM's `Action Input` into a kwargs dict.

    The prompt asks the model to emit a single-line JSON object, but small
    models sometimes emit a bare string. We handle both:
        - Valid JSON object  -> return the dict as-is.
        - Anything else      -> wrap it as {"query": <string>} so single-arg
                                tools still work.
    """
    if raw is None:
        return {}

    text = str(raw).strip()

    # Strip accidental ``` fences the model may add.
    if text.startswith("```"):
        text = text.strip("`").strip()
        if text.lower().startswith("json"):
            text = text[4:].strip()

    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict):
            return parsed
    except (json.JSONDecodeError, TypeError):
        pass

    return {"query": text}


class Agent:

    def __init__(self, mcp_client):
        self.mcp_client = mcp_client
        self.planner = Planner()
        self.memory = Memory()

        # Formats whatever tools mcp_client currently knows about into
        # the plain-text block injected into the system prompt.
        self.tool_catalogue = ToolCatalogue(mcp_client)

    def run(self, user_query: str):

        # Start fresh for every query
        self.memory.clear()

        print("=" * 60)
        print("Starting ReAct Agent")
        print("=" * 60)

        # Built once per run - the tool list doesn't change mid-run.
        tool_catalogue_text = self.tool_catalogue.describe_all()

        for step in range(1, MAX_STEPS + 1):

            print(f"\nStep {step}")
            print("-" * 60)

            # -------------------------
            # Ask planner what to do
            # -------------------------

            decision = self.planner.plan(
                user_query=user_query,
                memory=self.memory.format_for_prompt(),
                tool_catalogue=tool_catalogue_text
            )

            print(f"Thought : {decision['thought']}")

            # -------------------------
            # Stop if planner is done
            # -------------------------

            if decision["final_answer"]:

                print("\nAgent Finished!\n")

                return decision["final_answer"]

            # -------------------------
            # Execute tool via MCP
            # -------------------------

            tool_name = decision["action"]
            tool_input = decision["action_input"]

            print(f"Action : {tool_name}")
            print(f"Input  : {tool_input}")

            kwargs = _parse_action_input(tool_input)

            try:
                observation = self.mcp_client.call_tool(tool_name, kwargs)
            except ValueError as exc:
                # Raised by MCPClient.call_tool() for an unregistered
                # tool name - same role as Day 3's "Unknown tool" check.
                observation = f"{exc}. Please choose a valid tool."
            except TypeError as exc:
                observation = (
                    f"Tool '{tool_name}' rejected arguments {kwargs}: {exc}. "
                    "Please emit Action Input as a JSON object whose keys "
                    "match the tool's parameters."
                )

            print(f"\nObservation:\n{observation}")

            # -------------------------
            # Save trajectory
            # -------------------------

            self.memory.add_step(
                thought=decision["thought"],
                action=tool_name,
                action_input=tool_input,
                observation=observation
            )

        return (
            "Maximum reasoning steps reached before "
            "the agent could answer."
        )
