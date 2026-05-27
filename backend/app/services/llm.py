import os
from groq import AsyncGroq
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

# Initialize the Groq async client
client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """
You are a friendly, encouraging, and highly skilled English language tutor.
The user is practicing conversational English.
Response converssationally, keep your answers concise (1-3 sentences), and naturally keep the conversation going.
If the user makes a major grammatical error, subtly correct them in your response.
"""

async def generate_tutor_response(messages: list) -> str:
    """
    Takes a list of message history and returns the AI tutor's response using Llama 3.
    """
    api_messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for msg in messages:
        api_messages.append({"role": msg.role, "content": msg.content})

    try:
        response = await client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=api_messages,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Groq API Error: {e}")
        return "I'm having a little trouble hearing you right now. Could you try again?"