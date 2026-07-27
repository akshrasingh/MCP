"""
planner.py
----------
The Planner is the "brain" of the agent.

Responsibilities:
1. Build the prompt using:
    - System Prompt (with the live tool catalogue injected)
    - User Question
    - Previous Memory
2. Send it to the LLM.
3. Parse the response into a structured decision.

The planner NEVER executes tools. Ported from Day 3's planner.py, with
one change: plan() now takes `tool_catalogue` as a parameter instead
of importing a static SYSTEM_PROMPT, since the tool list is discovered
dynamically from the connected MCP servers.
"""

import re

from agent.llm import call_llm
from agent.prompts.system_prompt import build_system_prompt


class Planner:

    def __init__(self):
        pass

    def build_prompt(self, user_query: str, memory: str) -> str:
        """
        Builds the user prompt that is sent to the LLM.
        """

        prompt = f"""
========================
Conversation History
========================

{memory}

========================
User Question
========================

{user_query}

Think carefully.

If you need a tool, return:

Thought:
Action:
Action Input:

If you know the answer, return:

Thought:
Final Answer:
"""

        return prompt.strip()

    def plan(self, user_query: str, memory: str, tool_catalogue: str) -> dict:
        """
        Generate the next planning step.
        """

        system_prompt = build_system_prompt(tool_catalogue)

        user_prompt = self.build_prompt(
            user_query=user_query,
            memory=memory
        )

        response = call_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt
        )

        return self.parse_response(response)

    def parse_response(self, response: str) -> dict:
        """
        Convert the LLM response into a structured dictionary.
        """

        result = {
            "thought": None,
            "action": None,
            "action_input": None,
            "final_answer": None,
            "raw_output": response
        }

        thought = re.search(
            r"Thought:\s*(.*)",
            response,
            re.IGNORECASE
        )

        action = re.search(
            r"Action:\s*(.*)",
            response,
            re.IGNORECASE
        )

        action_input = re.search(
            r"Action Input:\s*(.*)",
            response,
            re.IGNORECASE
        )

        final_answer = re.search(
            r"Final Answer:\s*(.*)",
            response,
            re.IGNORECASE | re.DOTALL
        )

        if thought:
            result["thought"] = thought.group(1).strip()

        if action:
            result["action"] = action.group(1).strip()

        if action_input:
            result["action_input"] = action_input.group(1).strip()

        if final_answer:
            result["final_answer"] = final_answer.group(1).strip()

        return result
