import json
from fastapi import APIRouter, UploadFile, File, Form
from app.models.schemas import ChatRequest, ChatResponse, Message
from app.services.llm import generate_tutor_response
from app.services.audio import transcribe_audio

router = APIRouter()

# --- Our original text-only endpoint ---
@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    ai_reply = await generate_tutor_response(request.messages)
    return ChatResponse(reply=ai_reply)

# --- Our NEW voice-enabled endpoint ---
@router.post("/chat-audio", response_model=ChatResponse)
async def chat_audio_endpoint(
    file: UploadFile = File(...),
    messages_json: str = Form("[]") # We accept history as a stringified JSON form field
):
    """
    Receives an audio file and optional chat history.
    1. Transcribes audio to text.
    2. Appends user text to history.
    3. Gets AI response.
    """
    # 1. Read the audio into memory and transcribe it
    file_bytes = await file.read()
    print(f"🚨 DEBUG: Received file name: {file.filename}")
    print(f"🚨 DEBUG: Received file size: {len(file_bytes)} bytes")
    user_text = await transcribe_audio(file_bytes, file.filename)
    
    # Fail gracefully if audio was empty or corrupted
    if not user_text:
        return ChatResponse(reply="I couldn't hear that clearly. Could you try speaking a bit louder?")

    # 2. Reconstruct the chat history from the frontend
    try:
        history_dicts = json.loads(messages_json)
        messages = [Message(**msg) for msg in history_dicts]
    except Exception:
        # If frontend sends bad JSON, we just start a new conversation
        messages = []
        
    # 3. Add the newly transcribed message to the end of the history
    messages.append(Message(role="user", content=user_text))
    
    # 4. Pass the full context to Llama 3.1
    ai_reply = await generate_tutor_response(messages)
    
    return ChatResponse(user_text=user_text,reply=ai_reply)