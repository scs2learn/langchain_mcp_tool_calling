import os
import asyncio
import gradio as gr
import json
import pandas as pd
from dotenv import load_dotenv
from typing import List, AsyncGenerator

from langchain.chat_models import init_chat_model
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import BaseTool

# --- Configuration & Initialization ---
load_dotenv()

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

# Global variables for the agent and memory to persist across chatbot turns
AGENT_EXECUTOR = None


async def initialize_agent():
    """Initializes and returns the AgentExecutor instance."""
    global AGENT_EXECUTOR
    if AGENT_EXECUTOR:
        return AGENT_EXECUTOR

    print("Initializing MultiServerMCPClient...")
    client = MultiServerMCPClient(mcp_servers_config)

    print("Loading tools from all connected MCP servers...")
    tools: List[BaseTool] = await client.get_tools()
    print(f"Successfully loaded {len(tools)} tools: {[tool.name for tool in tools]}")

    llm = init_chat_model("gemini-2.0-flash", model_provider="google_genai", temperature=0)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", (
                "You are a helpful and proactive AI assistant. "
                "You have access to a variety of tools provided by different services, "
                "including arithmetic, database queries, user management, and weather information. "
                "When a user asks a question that requires information from a tool, "
                "you MUST use the appropriate tool(s) to get the necessary information "
                "before responding. "
                "If a query requires multiple steps, you should chain the tool calls automatically. "
                "Always provide a direct and concise answer to the user's original question after using tools. "
                "For requests to list users or query data, your final response must be in a structured, tabular format."
            )),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    )

    agent = create_tool_calling_agent(llm, tools, prompt)
    AGENT_EXECUTOR = AgentExecutor(agent=agent, tools=tools, verbose=True)

    return AGENT_EXECUTOR


# --- Gradio Chatbot Logic ---

def is_json_string(s: str) -> bool:
    """Checks if a string is valid JSON."""
    try:
        json.loads(s)
        return True
    except (json.JSONDecodeError, TypeError):
        return False


def format_json_as_table(json_data: str) -> str:
    """Converts a JSON string to a Markdown table."""
    try:
        data = json.loads(json_data)

        if isinstance(data, list) and all(isinstance(item, dict) for item in data):
            df = pd.DataFrame(data)
            return df.to_markdown(index=False)

        elif isinstance(data, dict):
            df = pd.DataFrame(list(data.items()), columns=['Attribute', 'Value'])
            return df.to_markdown(index=False)

    except (json.JSONDecodeError, ValueError) as e:
        print(f"Failed to format JSON as table: {e}")
        return json_data

    return json_data


async def respond(message: str, history: List[List[str]]) -> AsyncGenerator[str, None]:
    """
    Asynchronous function to handle user messages, invoke the agent,
    and stream the response to Gradio using the corrected history format.
    """
    agent_executor = await initialize_agent()

    # Correctly parse Gradio's history format
    chat_history_lc = []
    for chat_entry in history:
        if chat_entry and len(chat_entry) == 2:
            user_message, bot_response = chat_entry
            if user_message:
                chat_history_lc.append(("human", user_message))
            if bot_response:
                chat_history_lc.append(("ai", bot_response))

    full_response = ""
    async for chunk in agent_executor.astream(
            {"input": message, "chat_history": chat_history_lc}
    ):
        if "output" in chunk:
            full_response += chunk["output"]
            yield full_response
        else:
            yield full_response

    # Post-process the final output
    final_output = full_response

    # --- THIS IS THE CRITICAL FIX ---
    # We strip any leading/trailing whitespace before checking if it's JSON.
    trimmed_output = final_output.strip()

    if is_json_string(trimmed_output):
        final_output = format_json_as_table(trimmed_output)

    yield final_output


if __name__ == "__main__":
    demo = gr.ChatInterface(
        fn=respond,
        title="MCP-Powered Conversational Agent",
        description="Ask me questions about arithmetic, user data, Northwind database, or the weather!",
        # examples=[
        #     ["What is the weather of the city associated with the user with user_id 101?"],
        #     ["List all users."],
        #     ["What are the details of user with user_id 969?"],
        #     ["What is 100 divided by 5?"],
        #     ["What is the weather in London?"],
        #     [
        #         "Add a new user named Bob Smith with ID 300, born 1995-10-20, living at 123 Pine St, Anytown, IL 60601, phone 555-111-2222, email bob@example.com."]
        # ],
        chatbot=gr.Chatbot(height=500),
        theme="soft",
        type="messages",
    )

    print("Launching Gradio interface. Please open http://127.0.0.1:7860 in your browser.")
    demo.launch(share=False)