import os
from groq import AsyncGroq
from dotenv import load_dotenv

load_dotenv()
client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

async def transcribe_audio(file_bytes: bytes, filename: str) -> str:
    try:
        transcription = await client.audio.transcriptions.create(
            file=(filename, file_bytes),
            model="whisper-large-v3",
            response_format="json",
            # We shorten the prompt so it's less prone to hallucination
            prompt="A bilingual conversation in English and the target language." 
        )
        
        result = transcription.text.strip()
        print(f"🎤 RAW WHISPER OUTPUT: '{result}'")
        
        # --- THE SILENCE FILTER ---
        # If Whisper hears dead air, it hallucinates these phrases. We must block them.
        ghost_phrases = [
            "a bilingual conversation",
            "transcribe exactly what they say",
            "subtitles by",
            "amara.org",
            "thanks for watching",
            "thank you."
        ]
        
        # If the output is just a ghost phrase, return empty to trigger the routing fallback
        for ghost in ghost_phrases:
            if ghost in result.lower():
                print("🚫 SILENCE FILTER TRIGGERED: Blocked Whisper Hallucination")
                return ""
                
        return result

    except Exception as e:
        print(f"Whisper API Error: {e}")
        return ""