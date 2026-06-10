import os
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

# LangChain and OpenRouter
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

# Import for MCP client (we will use stdio client to talk to the local mcp_server.py)
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()

app = FastAPI(title="AI Outing Chatbot API")

class ChatRequest(BaseModel):
    message: str

# Initialize OpenRouter via LangChain ChatOpenAI
# You can change the model string to any model supported by OpenRouter
llm = ChatOpenAI(
    model="google/gemini-2.5-flash", # Using a fast model from OpenRouter
    max_tokens=1000,
    openai_api_key=os.getenv("OPENROUTER_API_KEY"),
    openai_api_base="https://openrouter.ai/api/v1"
)

# Configuration to run our local MCP server via stdio
server_params = StdioServerParameters(
    command="python",
    args=["mcp_server.py"],
    env=os.environ.copy()
)

SYSTEM_PROMPT = """You are a helpful and polite virtual outing planner. 
Your job is to recommend places to go (cafes, events, parks) based on user requests.
You have access to a tool that queries the live database for outings. 
ALWAYS use the tool when the user asks for a recommendation, price, or place to visit.
If the user asks to talk to a human, politely inform them that you are transferring the chat to customer support (Human Handoff triggered).
Do not hallucinate places. Base your recommendations ONLY on the data returned by your search tool."""

async def get_chatbot_response(user_message: str):
    # Connect to the MCP Server
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the MCP connection
            await session.initialize()
            
            # Create a LangChain tool that delegates the call to the MCP server
            @tool
            async def search_outings_tool(query: str, max_price: float = None) -> str:
                """Search the database for outings, cafes, and experiences."""
                # Call the tool over the MCP protocol
                result = await session.call_tool("search_outings", arguments={"query": query, "max_price": max_price})
                # MCP results are usually an array of content objects
                if result.content and len(result.content) > 0:
                    return str(result.content[0].text)
                return "No data found."
            
            tools = [search_outings_tool]
            
            # Create the ReAct agent
            agent_executor = create_react_agent(llm, tools)
            
            messages = [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=user_message)
            ]
            
            # Run the agent
            response = await agent_executor.ainvoke({"messages": messages})
            
            # Return the final message content
            return response["messages"][-1].content

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    try:
        reply = await get_chatbot_response(req.message)
        return {"reply": reply}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    # Start FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8000)
