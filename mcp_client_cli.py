import getpass
import os
import asyncio
from dotenv import load_dotenv
from typing import List

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain.chat_models import init_chat_model
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import BaseTool

# Load environment variables for API keys and other secrets
load_dotenv()

# --- Configuration ---
# Define the connection parameters for each of your MCP servers.
mcp_servers_config = {
    "MathService": {
        "transport": "streamable_http",
        "url": "http://127.0.0.1:8050/mcp",
    },
    "NorthWindService": {
        "transport": "streamable_http",
        "url": "http://127.0.0.1:8060/mcp",
    },
    "WeatherService": {
        "transport": "streamable_http",
        "url": "http://127.0.0.1:8070/mcp",
    },
    "UserAPIService": {
        "transport": "streamable_http",
        "url": "http://127.0.0.1:8080/mcp",
    },
}


async def create_agent_with_mcp_tools() -> AgentExecutor:
    """
    Initializes the MCP client, loads tools from all servers, and creates an agent.
    """
    print("Initializing MultiServerMCPClient...")

    # Create the client instance.
    client = MultiServerMCPClient(mcp_servers_config)

    print("Loading tools from all connected MCP servers...")
    # This is the corrected line. Call get_tools() directly on the client instance.
    tools: List[BaseTool] = await client.get_tools()
    print(f"Successfully loaded {len(tools)} tools: {[tool.name for tool in tools]}")

    # Initialize your LLM
    llm = init_chat_model("gemini-2.0-flash", model_provider="google_genai", temperature=0)

    # The enhanced prompt is still crucial for guiding the agent's behavior.
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", (
                "You are a helpful and proactive AI assistant. "
                "You have access to a variety of tools provided by different services, "
                "including arithmetic, database queries, user management, and weather information. "
                "When a user asks a question that requires information from a tool, "
                "you MUST use the appropriate tool(s) to get the necessary information "
                "before responding. "
                "If a query requires multiple steps (e.g., getting user info then weather), "
                "you should chain the tool calls automatically. "
                "Always provide a direct and concise answer to the user's original question after using tools."
            )),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    )

    # Create the tool-calling agent with the loaded tools and LLM
    agent = create_tool_calling_agent(llm, tools, prompt)

    # Create the AgentExecutor to run the agent
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    return agent_executor


async def main():
    """Main function to run the agent with a sample query."""
    try:
        agent_executor = await create_agent_with_mcp_tools()

        # This is your key test query.
        print("\n--- Testing combination tool calling with MCP servers ---")
        query = "What is the weather of the city associated with the user with user_id 101?"

        # We assume user 969 exists and has a city
        response = await agent_executor.ainvoke({"input": query})

        print(f"\nUser Query: {query}")
        print(f"Agent Answer: {response['output']}")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(main())