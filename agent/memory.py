"""
memory.py
---------
Short-term "scratchpad" memory for the ReAct agent.

Stores every Thought / Action / Action Input / Observation the agent
has produced so far and can render them back into the exact text
format the LLM expects on the next turn.

Ported near-verbatim from Day 3's memory.py - no MCP-specific changes
needed here, since memory just stores strings regardless of where the
observation actually came from.
"""

from config import MAX_HISTORY


class Memory:

    def __init__(self):
        self.history = []

    def add_step(
        self,
        thought: str,
        action: str,
        action_input: str,
        observation: str
    ):
        """
        Store one complete ReAct step.
        """

        self.history.append({
            "thought": thought,
            "action": action,
            "action_input": action_input,
            "observation": observation
        })

        # Keep only the latest steps
        if len(self.history) > MAX_HISTORY:
            self.history.pop(0)

    def get_history(self):
        return self.history

    def clear(self):
        self.history.clear()

    def format_for_prompt(self):
        """
        Convert memory into text that can be sent to the LLM.
        """

        if not self.history:
            return ""

        prompt = ""

        for i, step in enumerate(self.history, start=1):

            prompt += f"""
Step {i}

Thought: {step['thought']}
Action: {step['action']}
Action Input: {step['action_input']}
Observation: {step['observation']}

"""

        return prompt.strip()
