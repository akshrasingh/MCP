"""
main.py
-------
Entry point for the AI Travel Planner.

Wires everything together:
    1. Build an MCPClient and connect it to every server marked
       enabled=True in config.MCP_SERVERS.
    2. Build an Agent around that MCPClient.
    3. Run a simple REPL, same shape as Day 3's main.py.
"""

import config
from mcp_client.client import MCPClient
from agent.agent import Agent


def main():
    mcp_client = MCPClient()
    mcp_client.connect(config.enabled_servers())

    agent = Agent(mcp_client)

    try:
        while True:

            query = input("\nAsk something (or 'exit'): ")

            if query.lower() == "exit":
                break

            answer = agent.run(query)

            print("\n==============================")
            print("Final Answer")
            print("==============================")
            print(answer)
    finally:
        # Always tear down subprocess connections, even if the REPL
        # loop exits via an exception.
        mcp_client.close()


if __name__ == "__main__":
    main()
