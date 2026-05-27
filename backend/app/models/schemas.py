from pydantic import BaseModel
from typing import List, Optional

class Message(BaseModel):
    role: str
    content: str
    # Making these optional so the incoming chat history doesn't crash FastAPI
    feedback: Optional[str] = None
    score: Optional[int] = None
    next_exercise: Optional[str] = None
    english_audio: Optional[str] = None
    target_audio: Optional[str] = None

class ChatRequest(BaseModel):
    messages: List[Message]
    target_language: str
    proficiency_level: str

class ChatResponse(BaseModel):
    user_text: str
    # --- FIXED: Replaced tutor_audio_reply with our two new bilingual fields ---
    english_audio: str
    target_audio: str
    feedback: str
    score: int
    next_exercise: str