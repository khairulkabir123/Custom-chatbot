import asyncio
from chatbot import get_chatbot_response

async def main():
    print("Testing Chatbot Memory...")
    session_id = "test_user_1"
    
    # Question 1: Setting context
    question1 = "Hi, my budget is 2500 Taka and I'm looking for an event."
    print(f"\nUser: {question1}")
    response1 = await get_chatbot_response(question1, session_id)
    print(f"Chatbot: {response1}")
    
    # Question 2: Testing memory
    question2 = "What are the guest requirements for the event you just recommended?"
    print(f"\nUser: {question2}")
    response2 = await get_chatbot_response(question2, session_id)
    print(f"Chatbot: {response2}")

if __name__ == "__main__":
    asyncio.run(main())
