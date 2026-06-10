import asyncio
from chatbot import get_chatbot_response

async def main():
    print("Testing Chatbot...")
    response = await get_chatbot_response("Can you recommend a romantic event in Dhaka under 2500?")
    print("Chatbot Response:", response)

if __name__ == "__main__":
    asyncio.run(main())
