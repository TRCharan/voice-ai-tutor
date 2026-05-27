from pydantic import BaseModel
from typing import List, Optional

class Message(BaseModel):
    role: str       # "user" or "assistant"
    content: str    # The actual text

class ChatRequest(BaseModel):
    messages: List[Message]

class ChatResponse(BaseModel):
    user_text: str
    reply: str
    corrections: Optional[List[str]] = []   # For Future grammar corrections