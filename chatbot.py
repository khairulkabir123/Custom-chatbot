import os
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

# LangChain and OpenRouter
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

# Global memory saver to keep conversation history in RAM
memory = MemorySaver()

# Import for MCP client (we will use stdio client to talk to the local mcp_server.py)
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()

app = FastAPI(title="AI Outing Chatbot API")

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default_session"

# Initialize OpenRouter via LangChain ChatOpenAI
# You can change the model string to any model supported by OpenRouter
llm = ChatOpenAI(
    model="google/gemini-2.5-flash", # Using a fast model from OpenRouter
    max_tokens=1000,
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1"
)

import sys
# Configuration to run our local MCP server via stdio
server_params = StdioServerParameters(
    command=sys.executable,
    args=["mcp_server.py"],
    env=os.environ.copy()
)

SYSTEM_PROMPT = """You are a helpful and polite virtual outing planner. 
Your job is to recommend places to go (cafes, events, parks) based on user requests.
You have access to a tool that queries the live database for outings. 
This tool returns detailed information including Cancellation Policies, Guest Requirements, Ratings, and Notes.
ALWAYS use the tool when the user asks for a recommendation, price, place to visit, or ANY details about an event.
If the user asks to talk to a human, politely inform them that you are transferring the chat to customer support.
Do not hallucinate places. Base your recommendations ONLY on the data returned by your search tool."""

async def get_chatbot_response(user_message: str, session_id: str = "default_session"):
    # Connect to the MCP Server
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the MCP connection
            await session.initialize()
            
            # Create a LangChain tool that delegates the call to the MCP server
            @tool
            async def search_outings_tool(query: str, max_price: float = None) -> str:
                """Search the database for outings, cafes, and experiences. Returns details like cancellation policies, guest requirements, and ratings."""
                # Construct arguments dynamically to avoid passing None
                args = {"query": query}
                if max_price is not None:
                    args["max_price"] = max_price
                # Call the tool over the MCP protocol
                result = await session.call_tool("search_outings", arguments=args)
                # MCP results are usually an array of content objects
                if result.content and len(result.content) > 0:
                    return str(result.content[0].text)
                return "No data found."
            
            tools = [search_outings_tool]
            
            # Create the ReAct agent with memory checkpointer and system prompt
            agent_executor = create_react_agent(llm, tools, checkpointer=memory, prompt=SYSTEM_PROMPT)
            
            messages = [
                HumanMessage(content=user_message)
            ]
            
            # Run the agent with thread_id to track conversation history
            config = {"configurable": {"thread_id": session_id}}
            response = await agent_executor.ainvoke({"messages": messages}, config=config)
            
            # Return the final message content
            return response["messages"][-1].content

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    try:
        reply = await get_chatbot_response(req.message, req.session_id)
        return {"reply": reply}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    # Start FastAPI server
    uvicorn.run(app, host="127.0.0.1", port=8080)
