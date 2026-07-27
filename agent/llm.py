"""
llm.py
------
Thin wrapper around the local Ollama chat API.

Isolating the LLM call here lets us swap Ollama for Azure OpenAI /
OpenAI / Anthropic later by changing exactly one function. Ported
near-verbatim from Day 3's llm.py.
"""

from ollama import chat

from config import MODEL_NAME, TEMPERATURE


def call_llm(system_prompt: str, user_prompt: str) -> str:
    """Send a single Chat Completion request and return the raw text.

    Args:
        system_prompt: The ReAct protocol + the live tool catalogue.
        user_prompt:   The question + running trajectory.

    Returns:
        The model's raw string output (usually a Thought/Action/Action Input).
    """
    response = chat(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        options={
            "temperature": TEMPERATURE
        },
    )

    # `response.message.content` is where Ollama's SDK puts the assistant text.
    return response.message.content.strip()
