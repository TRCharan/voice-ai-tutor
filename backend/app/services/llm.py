import os
import json
from groq import AsyncGroq
from dotenv import load_dotenv
from app.services.database import search_memory

load_dotenv()
client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

async def generate_tutor_response(messages: list, target_language: str, proficiency_level: str) -> dict:
    latest_user_text = messages[-1].content if messages else ""
    relevant_memories = search_memory(latest_user_text, n_results=2)
    
    if relevant_memories:
        memory_string = "\n- ".join(relevant_memories)
        context_block = f"Past Context:\n- {memory_string}"
    else:
        context_block = ""

    dynamic_system_prompt = f"""
    You are the curriculum engine and evaluator for a {target_language} learning application.
    The user is a native English speaker currently learning {target_language} at the {proficiency_level} level.

    CONTEXT ABOUT THE USER:
    {context_block}

    LANGUAGE ROUTING (STRICT HARD RULES):
    Classify the user's input into one of three categories and respond EXACTLY as instructed. DO NOT overthink or invent translations.

    CATEGORY 1: THE USER SPOKE ENGLISH
    - Score: 100
    - Feedback: Provide the EXACT translation in {target_language}, followed by a simple phonetic English pronunciation guide. (e.g., "Translation: Ich bin... Pronunciation: Ick bin...")
    - Next Exercise: "Now, tap the microphone and try saying that in {target_language}."

    CATEGORY 2: THE USER SPOKE {target_language}
    - Score: 0 to 100 based on grammatical accuracy. 
    - Feedback: Praise them if correct. If they made a mistake, explain it strictly in English. 
    - Next Exercise: Give them a brand NEW English phrase to translate to keep the lesson moving forward.

    CATEGORY 3: UNRECOGNIZED ALPHABETS OR GIBBERISH
    - If the input contains non-Latin scripts (Korean, Japanese, Arabic, Hindi, etc.) or is completely unrecognizable (Turkish, random static), DO NOT attempt to translate it.
    - Score: 0
    - Feedback: EXACTLY "Microphone error: Please speak clearly in English or {target_language}."
    - Next Exercise: EXACTLY "Tap the microphone to try again."

    OUTPUT SCHEMA:
    You MUST output ONLY a valid JSON object matching this exact structure. Do not add conversational filler.
    {{
      "recognized_user_text": "The exact text you evaluated.",
      "feedback": "<Apply the exact rule from the Category above>",
      "score": <Apply the exact score from the Category above>,
      "next_exercise": "<Apply the exact rule from the Category above>",
      "english_audio": "A short English script to be spoken out loud. (e.g., 'Here is the translation:')",
      "target_audio": "ONLY output {target_language}. NEVER include English words here."
    }}
    """
    
    api_messages = [{"role": "system", "content": dynamic_system_prompt}]
    for msg in messages:
        api_messages.append({"role": msg.role, "content": msg.content})

    try:
        response = await client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=api_messages,
            temperature=0.3,
            response_format={"type": "json_object"} 
        )
        
        raw_json_string = response.choices[0].message.content
        return json.loads(raw_json_string)
        
    except Exception as e:
        print(f"Groq API Error: {e}")
        return {
            "feedback": "I had trouble processing that.",
            "score": 0,
            "next_exercise": "Please repeat your last sentence.",
            "english_audio": "I had trouble processing that. Please try again.",
            "target_audio": ""
        }