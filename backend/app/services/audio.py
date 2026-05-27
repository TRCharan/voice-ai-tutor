import os
from groq import AsyncGroq
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()
client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

async def transcribe_audio(file_bytes: bytes, filename: str) -> str:
    """
    Sends raw audio bytes to Groq's Whisper-large-v3 API for transcription.
    """
    try:
        # Groq (and OpenAI) APIs expect files as a tuple: (filename, file_bytes)
        transcription = await client.audio.transcriptions.create(
            file=(filename, file_bytes),
            model="whisper-large-v3",
            response_format="json",
            language="en", # We force English to help the AI understand accents better
            prompt="The user's name is Charan. They are practicing conversational English."
        )
        return transcription.text
    except Exception as e:
        print(f"Whisper API Error: {e}")
        return ""